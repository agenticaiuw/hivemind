# Harness derivation — faculty-action — round 133

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live action surfaces** — Safari bridge is online with 3 tabs and no pending commands, but the active tab is a failed example.com page; Mac agent reports fullControlPlanner enabled while Accessibility and Screen Recording remain ungranted, and automation grants are present.
  - evidence: GET /browser/status and GET /ops/status at 2026-08-07T18:18Z

## Capabilities it proposed

### "“I’m wearing the pendant—take care of the thing I’m looking at.” Have the system capture the active Safari tab, identify the reversible next step, prepare it on the Mac, and return a one-sentence spoken receipt plus a physical ready/failed signal on the pendant; never submit an irreversible action without my explicit confirmation."
- **useful because:** This is the system’s highest-value action loop: the owner does not have to describe a URL, copy text, or choose a surface. The worn button/voice establishes intent, Safari supplies private context, the Mac executes reversible work, and the pendant confirms what actually happened. It turns “I’m looking at it” into useful action while preserving the send/buy/delete boundary.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Realtime model only for the short intent and confirmation exchange; a cheaper background planner performs page extraction and reversible steps, with the browser harness enforcing an explicit irreversible checkpoint.
- **latency:** Acknowledge the button within 300 ms; capture tab and speak a plan within 3 s; reversible execution within 15 s; confirmation and final receipt within 2 s of approval.
- **cost:** About $0.01–$0.08 per invocation depending on page length and whether vision is needed; browser extraction and screenshots dominate, not the short spoken exchange.
- **security:** Private authenticated page contents leave Safari only to the local Mac agent/relay path. Never transmit secrets in the receipt. Before send/buy/delete, show the exact target, fields, and before/after evidence and require a fresh deliberate confirmation from the pendant; expire the prepared transaction after a short TTL.
- **missing:** A pendant-to-Mac intent event and status channel that works over the currently connected USB serial devices; A browser operation that binds the captured active tab to a durable, resumable transaction; A single confirmation protocol shared by pendant, browser, and Mac with postcondition evidence

### "“If that action fails, recover it.” When a browser or Mac action hits a timeout, changed page, or lost connection, have the system diagnose the failure, choose a safe alternate hand (browser bridge, AppleScript/API, or deferred Mac job), retry only idempotent steps, and leave me a concise pendant receipt saying what was recovered and what still needs me."
- **useful because:** Today an action can be planned but a browser heartbeat, tab, network, or UI change can strand it. The owner should not have to understand which surface failed or repeat the request. Cross-surface recovery is where the hive is materially better than a single Mac agent, while the explicit retry policy prevents duplicate side effects.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Cheap background model classifies failure and selects a known-safe fallback; realtime is used only if the owner must answer a recovery question or approve a changed irreversible step.
- **latency:** Detect and acknowledge failure in 1 s; attempt a safe fallback within 10 s; for deferred work, provide a durable status and receipt rather than holding the conversation open.
- **cost:** Roughly $0.005–$0.04 per failed job for classification and receipt; screenshots/page reinspection dominate. Successful jobs incur no additional model call.
- **security:** Fallbacks must have an allowlisted equivalence class and a precondition/postcondition check. Never retry send, purchase, delete, or permission changes automatically. Include the original and fallback target in the receipt, redact page data, and expire recovery leases.
- **missing:** A typed failure taxonomy and idempotency/precondition contract shared by Mac, browser, and relay jobs; A fallback planner that can invoke AppleScript or API routes without treating a different side effect as equivalent; A durable recovery queue with owner-visible receipts and a pendant status event

### "“Arm this only while I’m holding the pendant.” Let the Mac and browser prepare a high-impact action, but require a device-bound physical gesture on the pendant—such as a long press followed by a second press within 10 seconds—to release the final commit token. Show the target and change in the spoken prompt before arming, and give a local LED result afterward."
- **useful because:** This gives the owner a real security boundary that is independent of browser sessions, Mac focus, or a stolen microphone transcript. A prepared action cannot commit merely because an old voice turn, tab, or relay session is still alive; the owner’s hand is the final authorization surface.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** No expensive model is needed for the gesture protocol. Use the realtime model only to explain the proposed change and ask for arming; deterministic firmware/relay logic validates the gesture and transaction binding.
- **latency:** LED arm acknowledgement under 150 ms; commit decision under 500 ms after the second gesture; expire the arm window after 10 seconds.
- **cost:** Near-zero per action after implementation; at most a short realtime turn for the spoken explanation.
- **security:** Bind the token to device identity, transaction hash, target tab, and expiry. Reject replayed sequence numbers and any gesture received after the spoken proposal changes. Never expose the token in UART logs or browser telemetry.
- **missing:** A cryptographically bound pendant gesture protocol; A transaction hash shared by Mac, browser, relay, and pendant; Firmware LED/gesture states beyond the current conversation start/end semantics

### "“Save this moment so I can resume it later.” From the pendant, capture the active browser tab, the relevant page excerpt, the current Mac application/project, and the last action receipt into one private task capsule. Later, saying “resume that” should reopen the exact tab and present the capsule, but must re-check every precondition before doing anything."
- **useful because:** The owner can leave a task without losing the invisible context that made it meaningful. Unlike a bookmark or reminder, the capsule preserves what was seen, what was attempted, and what remains, while the precondition check prevents stale page state from causing an accidental action.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Use a cheap background summarizer to compress the excerpt and receipt; use realtime only for the short capture/resume exchange.
- **latency:** Capture acknowledgement under 1 s and capsule creation under 5 s; resume should reopen and validate within 5 s.
- **cost:** Approximately $0.002–$0.02 per capsule, dominated by page-text summarization; storage is a small local JSON/SQLite record plus optional redacted excerpt.
- **security:** Capsules may contain authenticated page data. Encrypt or keep them local by default, retain source URL/tab identity and sensitivity labels, redact secrets, and require reauthentication or fresh confirmation if a resumed task would mutate anything.
- **missing:** A first-class capsule schema linking tab, page excerpt, Mac project, pendant intent, and action receipt; Tab/session reattachment with stale-state and authorization checks; A pendant-triggered capture event and spoken capsule index

### "“Tell me whether this is safe before I touch it.” When I point the pendant at an active browser task or ask about the current Mac action, produce a compact risk briefing: who will receive data, what files/accounts will change, what can be undone, and what cannot. Let me ask follow-up questions through the pendant without losing the exact proposed operation."
- **useful because:** The owner currently has to infer risk from scattered browser pages, Mac prompts, and action receipts. A cross-surface preflight makes consequential automation understandable before commitment, especially when the private browser session and Mac-side tools are combined.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A cheaper text model builds the structured risk summary from typed action metadata and evidence; realtime handles only the owner’s spoken questions and final acknowledgment.
- **latency:** Initial risk card and one spoken sentence within 3 s; follow-up answers within 2 s while retaining the same transaction binding.
- **cost:** About $0.005–$0.03 per preflight, with browser inspection and evidence extraction dominating model cost.
- **security:** Risk analysis must not itself mutate state. Redact account identifiers and secrets in spoken output, distinguish verified facts from model inference, and invalidate the briefing if the target tab, fields, or action plan changes.
- **missing:** A typed effect/risk vocabulary covering browser, AppleScript, shell, and relay actions; A provenance reducer that turns receipts and page evidence into a human-readable preflight; A transaction-bound conversational follow-up channel on the pendant


## Changes it proposed to its own stack

### `integration` — Build a USB-tethered pendant action bus on the Mac that treats the nRF9160 serial link as a real input/output surface today: timestamp and authenticate button press/release/long-press frames, attach them to the current Mac/browser session, enqueue an action or cancellation, and drive the pendant LED through a small state machine (queued, inspecting, ready-for-confirmation, succeeded, failed, expired). Persist an append-only event and receipt record so a dropped serial link cannot duplicate an action when it reconnects.
- **owner gets:** The owner can wear the actual prototype and trigger or cancel work without opening an app. They get immediate physical feedback instead of wondering whether the system heard them, and reconnects cannot silently repeat a message, purchase, deletion, or other side effect.
- effort: Medium: serial framing/handshake, local daemon integration, LED command support, idempotent event store, and a Mac/browser session correlation layer; test with the two USB devices without flashing firmware first.  ·  risk: A stale button frame could trigger the wrong task or a reconnect could strand an action. Require monotonic sequence numbers, a short action lease, cancellation on ambiguity, and visible error flashing; recover by replaying only unconsumed telemetry, never action commands.
- cost: Negligible API cost; roughly 1–2 kB per event locally. No hardware cost for the prototype. Firmware work is small but must respect the single LED/button and existing full-duplex I2S.  ·  latency: Under 100 ms for local LED acknowledgement and under 500 ms to enqueue a Mac action; no impact on audio if serial handling remains off the I2S/audio thread.
- security: USB serial is treated as a local privileged control channel: bind it to the known device identity, reject unknown serial numbers, and require a fresh confirmation frame for irreversible work. Keep page contents and action parameters out of LED/UART telemetry.
- depends on: A defined pendant serial frame format and device identity; The pending physical-action confirmation and offline-cancel semantics; A local background process allowed to open /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA


## What it asked for

_Nothing._
