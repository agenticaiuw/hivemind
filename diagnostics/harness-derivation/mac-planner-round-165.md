# Harness derivation — mac-planner — round 165

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-mac-165** — The Mac bridge and Safari extension are online, but the pendant is not relay-registered; Accessibility and Screen Recording are false, computer-use loop disabled, and vision upload consent false. Both prototype boards are physically USB-connected, so a tethered path is testable now but no serial session daemon exists.
  - evidence: GET /ops/status returned macBridgeOnline=true, browserExtension.online=true, accessibility.trusted=false, screenRecording.granted=false, computerUse.loopEnabled=false, relay.pairingRequired=true; hardware specs identify the live USB serial devices.

## Capabilities it proposed

### "“Press the pendant button, say a command, and have my Mac carry it out while I’m wearing headphones; tell me what changed, and keep working if the relay drops.”"
- **useful because:** This is the first genuinely usable end-to-end loop available today: the worn button and microphone provide intent, the Mac has local app/files/browser reach, and the ESP32 returns spoken confirmation. It works even before LTE registration because USB serial is live.
- **path:** pendant → mac-bridge → mac-planner → browser-extension → relay
- **model tier:** Realtime only for the short command/confirmation; use the local planner and cheaper background model for multi-step work.
- **latency:** Button-to-start under 300 ms; first spoken acknowledgement under 2 s; desktop actions may continue asynchronously with a completion cue.
- **cost:** About one realtime turn plus local execution; roughly $0.01–$0.05 depending on audio duration. USB transport and macOS speech dominate neither API cost nor latency.
- **security:** Commands and resulting desktop state stay on the Mac/relay path; authenticated browser content must not be echoed into logs or audio unless requested. Mutations follow the owner's existing maximum-access policy, but every completion needs a truthful receipt.
- **missing:** USB serial daemon that maps pendant button/audio frames to a local session; audio return path from Mac/relay through ESP32 to headphones; reconnect/offline queue and deduplication across USB and LTE; verified action receipt spoken back to the pendant

### "“When I plug in the pendant, run a two-minute health check on the whole system and say exactly what is working, what is stale, and what I should fix.”"
- **useful because:** The current status view can say the bridge and Safari extension are online while Accessibility, Screen Recording, or the pendant are not; a physical tether gives a deterministic test point. This prevents the worst failure mode: claiming an action happened when the UI or audio path did nothing.
- **path:** pendant → mac-bridge → relay → browser-extension → dashboard
- **model tier:** Cheap deterministic checks and rule-based summary; reserve realtime for the spoken result only.
- **latency:** Complete in under 120 seconds, with immediate LED/button feedback and a short spoken report.
- **cost:** Near-zero model cost if checks are structured; one short TTS response, under $0.01.
- **security:** Only device identifiers, permission booleans, and synthetic test results should leave the Mac. Do not scan or upload private browser/page content. A failed check must never auto-change permissions or delete data.
- **missing:** Serial discovery and signed challenge between nRF9160 and Mac; audio loopback test fixture for the 15,625 Hz mic and 24 kHz playback path; permission-aware action probe that distinguishes reported success from actual UI effect; dashboard endpoint storing timestamped health vectors

### "“If I’m in a meeting, let me tap once to make the Mac quietly collect the relevant calendar, mail, and open-tab context; tap again afterward for a private spoken debrief and a list of follow-ups, without sending anything.”"
- **useful because:** The pendant is the only surface that can start and end a capture session without taking over the Mac. Combining its physical boundary with Calendar/Mail reads and authenticated Safari tabs yields a useful meeting capsule rather than a generic transcript or notification dump.
- **path:** pendant → mac-bridge → mac-planner → browser-extension → relay
- **model tier:** Use bounded read models for Calendar/Mail and browser extraction; use a cheaper background model to build the capsule; realtime only for tap acknowledgement and the final short debrief.
- **latency:** Tap acknowledgement under 500 ms; context snapshot within 10 s; debrief ready within 1 minute after the ending tap.
- **cost:** Typically $0.02–$0.10 per meeting depending on extracted page/mail volume; context extraction and summarization dominate.
- **security:** Capture must be visibly indicated by the single LED and physically ended by a second tap. Redact unrelated mail and tabs, encrypt capsule at rest, auto-expire it, and never send follow-up messages without a separate explicit command.
- **missing:** A pendant-local capture boundary event and LED state protocol; meeting capsule storage/API with source-level provenance and expiry; browser-tab selection/extraction bound to the active Safari session; cross-source deduplication and private spoken playback queue

### "“For anything sensitive, let my pendant be the physical key: prepare the action on my Mac or in Safari, show me a compact spoken summary, and require one deliberate tap on the worn device before it can use my account.”"
- **useful because:** Today the Mac runs in FULL_CONTROL_MODE with no confirmation gate, while the pendant is not a trusted authorization factor. This would let the owner keep maximum automation for ordinary work while reserving a physical, unmistakable gesture for purchases, messages, account changes, and other identity-bearing actions.
- **path:** pendant → mac-bridge → browser-extension → relay → dashboard-ux
- **model tier:** Use deterministic policy and cryptographic verification; use a cheap text model to summarize the pending mutation. Realtime is only needed if the owner asks follow-up questions by voice.
- **latency:** Prepare in under 3 seconds; spoken summary under 2 seconds; tap authorization reflected in the executor within 500 ms.
- **cost:** Negligible model cost for structured actions; under $0.01 when summarization is needed. Engineering and secure-key provisioning dominate.
- **security:** The private key must remain on-device and never be sent to the relay. Prevent replay with nonce, expiry, job binding, and cancellation on unplug. Never treat a spoken 'yes' alone as authorization for an identity-bearing action.
- **missing:** Secure pendant key storage and signing firmware; Mac-side authorization broker that binds a tap signature to one exact action hash; Browser bridge support for pending-action display and commit; Recovery/re-pairing flow that cannot silently weaken protection

### "“If my Mac goes to sleep or loses the network halfway through a task, let the system carry the intent across the relay and resume on whichever surface comes back, without starting the task twice.”"
- **useful because:** The owner currently has separate Mac jobs, browser sessions, relay state, and a physical device, but no user-visible continuity contract. A task that spans a private Safari session and local files should survive sleep, USB removal, or relay reconnect rather than silently disappearing or duplicating a mutation.
- **path:** pendant → mac-bridge → browser-extension → relay → dashboard
- **model tier:** Use a deterministic durable state machine and idempotency keys; use a background inexpensive model only to re-plan a failed step. Realtime is limited to status questions and concise announcements.
- **latency:** Immediate local queued acknowledgement; resume within 5 seconds of a surface reconnect; no duplicate side effects.
- **cost:** Low API cost: mostly durable state and local checks, with occasional cheap replanning. Storage and retry orchestration dominate.
- **security:** Persist only the minimum action graph and encrypted references to private data. Expire abandoned intents, bind browser work to its original session, and never resume an irreversible step without the physical authorization policy above.
- **missing:** A durable cross-surface intent state machine with leases and idempotency; Relay-to-Mac reconnect protocol and pending-intent delivery; Browser transaction checkpoints that distinguish read, draft, and commit; User-facing resume/cancel controls on pendant and dashboard

### "“Let me ask the pendant what my computer is doing right now, and have it answer with a live, source-linked explanation—not a guess from old logs.”"
- **useful because:** The owner cannot currently obtain a trustworthy spoken answer about whether an action is actually running, what app or browser session it touched, or why it stopped. This would combine live Mac state, browser state, pipeline state, and job receipts into one current explanation, even when the screen is unavailable.
- **path:** pendant → mac-bridge → browser-extension → relay → dashboard-ux
- **model tier:** Collect structured observations deterministically and use a small summarizer; reserve realtime for the conversational response, not state gathering.
- **latency:** Answer within 2 seconds for status, under 8 seconds for a cross-surface explanation.
- **cost:** Usually below $0.01; structured probes dominate and can be cached for seconds, while the model only verbalizes them.
- **security:** Return only task-relevant metadata by default: app names, job states, and redacted URLs. Require an explicit request for message contents or private page text. Attach timestamps and source identifiers so stale data cannot sound live.
- **missing:** A live observation aggregator with freshness/expiry per field; Correlation from a spoken question to active job, browser tab, and pipeline IDs; A pendant response protocol for short status speech and error tones; Dashboard rendering of the same evidence bundle


## Changes it proposed to its own stack

### `mac-harness` — Add a local USB pendant session daemon that discovers /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, frames button/audio/control packets, assigns a session UUID, forwards commands to /plan and completions to /execute/job receipts, and survives unplug/replug with idempotent sequence numbers.
- **owner gets:** The owner can actually wear and use the prototype while tethered today instead of waiting for LTE registration; spoken commands and confirmations become a continuous experience rather than disconnected firmware and HTTP demos.
- effort: Medium: serial framing, reconnect state machine, launchd service, and integration tests against both boards.  ·  risk: Malformed or duplicated frames could repeat a Mac mutation; sequence IDs and job-id dedupe limit this. On failure, leave the Mac untouched and blink/report a transport error.
- cost: No recurring API cost beyond commands; roughly 1–3 days engineering and negligible CPU/power on Mac.  ·  latency: Adds under 100 ms for local framing; reconnect may take 1–3 s.
- security: USB serial is local but should require the known board identifiers and a pairing secret; never log raw microphone audio or private command text.
- depends on: Pendant/bridge wire protocol specification; A small local serial service or launchd integration; Completion audio transport

### `integration` — Create a cross-surface truth receipt: after every pendant-originated job, correlate the serial command, planner output, executor result, browser command result, and final observable probe into one signed JSON receipt with states accepted, executed, verified, or failed; speak only the verified state.
- **owner gets:** When Accessibility is false, an action can report success while doing nothing. The owner would hear the difference immediately and stop trusting phantom completions.
- effort: Medium: receipt schema, correlation IDs through /plan,/execute,browser bridge, and a post-action verification adapter for files/apps/tabs.  ·  risk: Verification can be stale or expensive; label timestamps and unverifiable states rather than guessing. Never claim verification from a planner response alone.
- cost: Small storage and one local probe per action; no model cost for structured verification.  ·  latency: Adds 0.2–2 s for verification, with immediate 'working' acknowledgement.
- security: Receipts may expose filenames or URLs; redact content and apply short retention, with sensitive fields stored locally only.
- depends on: macOS permission truth being consumed as a hard fact; Stable request/job IDs across serial, relay, and browser bridge; Read-only verification probes

### `firmware` — Define a physical interaction protocol for the single button and LED: short press starts tethered command capture, second press commits/stops; long press cancels and clears unsent audio; LED patterns distinguish listening, queued, verified, failed, and disconnected. Mirror those events over USB serial and retain only a tiny unsent sequence counter in flash.
- **owner gets:** The owner can control capture and know whether the system heard, queued, completed, or failed without looking at a screen—especially valuable when the Mac has no Accessibility or the relay is unreachable.
- effort: Medium firmware work within existing one-button/one-LED hardware; protocol tests across nRF9160 and ESP32.  ·  risk: Ambiguous press timing or flash wear; use debouncing, bounded long-press windows, and RAM-first state with infrequent counter commits. Audio must be discarded on cancel.
- cost: Well under the 211,608 B application RAM if event metadata is tens of bytes; negligible power impact, no API cost.  ·  latency: Immediate local LED response; serial event delivery under 100 ms.
- security: Do not persist command audio or transcript on the pendant; clear buffers on cancel and expose only opaque session IDs.
- depends on: USB session daemon; A documented serial framing/handshake; Audio buffering path that can be cancelled safely

### `hardware` — Add a small secure element to the production pendant and make the button tap produce device-signed, nonce-bound authorization attestations; keep the prototype path behind a clearly labeled development key rather than pretending the nRF9160 dev board is a trust anchor.
- **owner gets:** The owner gets a real physical authorization key for sensitive Mac and browser actions instead of an easily replayed software confirmation or an always-on unrestricted executor.
- effort: High: board revision, secure-element provisioning, firmware signing protocol, and Mac pairing/recovery UX.  ·  risk: Lost pendant could block the owner; provide explicit recovery with a previously enrolled device or offline recovery code, never an invisible downgrade. Prototype keys must be revocable.
- cost: Roughly $1–$4 per production unit plus engineering/provisioning; negligible power compared with the radio and audio path.  ·  latency: Under 100 ms for local signature generation and verification.
- security: Substantially improves resistance to replay and remote relay compromise; private keys never leave the pendant.
- depends on: Physical authorization capability; Mac-side action hash binding; Documented pendant serial protocol

### `relay` — Implement a lease-based intent journal shared by relay, Mac bridge, browser extension, and pendant: every task has a monotonic step graph, owner, expiry, idempotency key, and explicit handoff state; a reconnecting surface must claim a lease before continuing.
- **owner gets:** Tasks would finish once—not twice or zero times—when the Mac sleeps, Safari reconnects, USB is unplugged, or LTE eventually becomes available.
- effort: High: D1 schema/API, bridge and extension adapters, crash-recovery tests, and visible resume/cancel controls.  ·  risk: A bad lease could strand work or delay completion; leases must expire, expose recovery state, and make uncommitted steps safe to replay.
- cost: Small D1/storage and polling cost; occasional background replanning token usage.  ·  latency: Normal actions gain only a few tens of milliseconds; reconnect resume becomes much faster and predictable.
- security: Encrypt or minimize private payloads, bind leases to authenticated device/session identities, and prohibit cross-account handoff.
- depends on: Cross-surface continuity capability; Stable job/browser request IDs; Relay pairing and device identity


## What it asked for

_Nothing._
