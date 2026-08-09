# Harness derivation — mac-planner — round 213

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “take over from the pendant,” keep the same conversation alive over USB even when LTE is unregistered: route pendant audio through the Mac, show the reply in the ear, and return to cellular automatically when it comes back."
- **useful because:** The hardware is physically on the owner's desk today but the LTE registration is not. This makes the wearable useful now instead of silently failing in the exact state we can test, while preserving one conversation identity across transport changes.
- **path:** pendant → mac-planner → relay-realtime → browser-extension
- **model tier:** Realtime only for the live voice turn; a cheap background state machine handles link selection and reconnection, with no model call for transport changes.
- **latency:** USB audio/control handoff under 250 ms; cellular rejoin may take seconds but must not create a second conversation or lose queued audio.
- **cost:** Negligible model cost for handoffs; roughly one relay websocket and the existing audio path. Dominant cost is implementation/testing of serial framing and reconnection.
- **security:** USB is a local trusted boundary but must pair to the already-authenticated Mac bridge, not accept arbitrary serial peers. Do not persist raw microphone audio; retain only encrypted in-flight buffers and delivery receipts. Transport switching should be observable.
- **missing:** mac_serial_exchange or an equivalent typed USB-serial exchange tool/daemon; relay transport multiplexer that binds USB and LTE to one session; pendant firmware USB control/audio framing compatible with the shipped 24 kHz/60 ms path

### "If a Mac or authenticated browser task is running, let me press the pendant once to hear its current status, twice to pause it, and hold to cancel or undo the last safe step; when I reconnect, tell me exactly what happened."
- **useful because:** The owner cannot watch a screen continuously. A physical, low-attention interrupt makes long browser and desktop jobs safe to leave running and recoverable from a dropped link, using the pendant as the one control surface that is always with him.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** No LLM for pause/cancel/status routing; use deterministic job state and receipts. Use a cheaper background model only to compress a receipt into one spoken sentence; realtime speaks only when the button interaction is live.
- **latency:** Acknowledge button state locally in under 100 ms; relay action under 500 ms; status speech under 2 s. Cancellation must be idempotent and survive reconnect.
- **cost:** Near-zero for control; one short summarization call only when the owner asks for a spoken explanation. Storage is small job receipts plus an event ledger.
- **security:** Cancel/undo must be scoped to the owner's authenticated active job and reject stale command IDs. Sending mail, deleting files, purchases, and irreversible browser mutations remain confirmation-required even if the pendant asks to continue. Redact page contents in receipts.
- **missing:** firmware mapping for a distinct interrupt gesture into the existing alert inbox/bookmark controls; relay command router that can authenticate pendant interrupt events and bind them to a Mac/browser job; a browser-side pause primitive for commands already in flight (cancel exists at job level but not necessarily inside a page transaction)

### "When I press the pendant’s bookmark button while the Mac is connected, make a durable incident card: capture the exact UART/device and relay telemetry around that moment, attach the active Mac/browser job and foreground app, and leave me a short spoken diagnosis plus a file in ~/AI-Pendant-Workspace."
- **useful because:** A physical bookmark is the only reliable way to mark the instant a wearable glitch, distorted reply, or browser failure occurs. Correlating device counters, relay pipeline events, and desktop state turns “it broke” into a reproducible report without recording a conversation by default.
- **path:** pendant → mac-planner → relay-realtime → browser-extension
- **model tier:** Deterministic collection and correlation first; a cheap background model summarizes the bounded telemetry. Realtime is used only if the owner asks immediately for the diagnosis.
- **latency:** Local bookmark acknowledgement under 100 ms; telemetry snapshot and workspace card within 10 s; spoken summary within 3 s after request.
- **cost:** One small summary call per incident, dominated by no-model telemetry collection. A card is a few KB; raw audio remains opt-in and bounded by the existing bookmark policy.
- **security:** Default to counters, timestamps, IDs, app/job metadata—not page text, mail, secrets, or microphone audio. Redact URLs/query strings and browser content. Atomic card creation prevents half-reports; owner can delete the card.
- **missing:** a live USB serial read path (the pendant is connected now, but mac_serial_exchange is still unavailable); relay endpoint to snapshot and correlate pipeline telemetry by bookmark timestamp; a typed read-only Mac snapshot that returns active job, foreground app, and browser command IDs in one record

### "While I am looking at any authenticated web page, let me say “make this defensible.” Capture the exact visible claim, its surrounding page context, timestamp, source identity, and any linked primary evidence; compare it with my local notes or calendar context, then leave a signed, redacted evidence packet in ~/AI-Pendant-Workspace and speak only the confidence and the one missing fact."
- **useful because:** The owner can currently inspect pages or ask for summaries, but cannot turn a fleeting browser observation into a trustworthy, auditable artifact. This would make the pendant a field notebook for decisions: the browser supplies authenticated context, the relay supplies the conversation, and the Mac preserves provenance without requiring the owner to copy/paste or expose an entire page.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Use deterministic browser capture, URL/title/selection extraction, hashing, and redaction first. Use a cheap background reasoning model to identify the claim, retrieve linked primary evidence, and assign calibrated uncertainty. Realtime only speaks the final one-sentence result.
- **latency:** Acknowledge the command in under 300 ms; capture and durable packet in under 8 s; evidence comparison in under 30 s, with a progressive spoken update if sources are slow.
- **cost:** One bounded reasoning call plus optional source fetches per request; dominant cost is evidence comparison, not capture. Packets should be tens of KB and contain hashes/snippets rather than full pages by default.
- **security:** Authenticated page content and local context are sensitive. Require an explicit spoken command, isolate credentials/cookies from the relay, redact account numbers and secrets before persistence, preserve source hashes and timestamps, and mark claims as unverified when evidence cannot be fetched. Never submit forms or contact anyone as part of verification.
- **missing:** A browser-extension primitive that returns the selected/visible claim and a bounded DOM context with stable element/source identifiers, rather than only a generic inspection; A relay evidence-correlation job with provenance, uncertainty, and redaction policy; A Mac-side signed evidence-packet writer and verifier in the workspace; A pendant command/result protocol that can carry a claim ID and progressive completion state

### "Let me say “delegate this to the browser for 20 minutes” and have the pendant create a temporary, site- and action-scoped delegation: the browser may perform only the named task, the Mac records every step, and the pendant can revoke it instantly; at expiry it must stop and report what remains."
- **useful because:** The owner currently has either manual browser work or broad full-control automation. A short-lived delegation lets him leave a bounded task running without granting an indefinite agent the keys to every authenticated session, and the pendant gives him a revocation control he can reach away from the keyboard.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime interprets the spoken scope once; a deterministic policy engine enforces site, verb, resource, deadline, and revocation. Use a cheap model only to summarize the execution receipt, never to decide whether an action is in scope.
- **latency:** Create delegation and local acknowledgement under 500 ms; revocation reaches browser and Mac under 1 s; expiry is enforced locally even if the relay is unreachable.
- **cost:** Negligible ongoing inference cost; one short summary call at completion. Main work is policy enforcement and durable audit logs.
- **security:** The scope must be unforgeable and bound to the authenticated browser session, with deny-by-default for purchases, deletion, sending messages, credential changes, and downloads of secrets. The relay must not receive cookies or page passwords. Revocation and expiry need fail-closed behavior on each local executor, with a receipt proving the final state.
- **missing:** A signed delegation-token format understood independently by relay, Mac executor, and browser extension; Browser-side action enforcement for every command, including navigation and form submission, not just command queueing; Pendant-local revoke/expiry state that works while LTE is down and then reconciles; A Mac action ledger that records precondition, effect, and terminal state for each delegated step

### "When I ask “what happened while I was away?”, give me a tamper-evident, cross-surface activity report: every Mac file/app change, browser navigation or submission, relay job, and pendant event in the interval, including an explicit statement of what was not touched, then let me open the relevant receipt or undoable item from the pendant."
- **useful because:** Receipts exist per subsystem, but the owner cannot currently obtain one coherent answer about everything the hive did during an absence—or distinguish silence from an unobserved failure. A single negative-and-positive activity report restores trust after unattended work and makes recovery practical.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Collect and hash event records deterministically; use a cheap background model only to compress them into a short spoken report. Realtime is only the delivery channel, not the auditor.
- **latency:** Return an initial bounded report in under 3 s and complete reconciliation in under 15 s; pendant should retain the request/result IDs across a dropped link.
- **cost:** No model call for collection; one small summarization call per report. Storage is append-only hashes and compact event metadata, with payloads fetched only on demand.
- **security:** Reports can reveal private URLs, filenames, and messages. Redact content by default, separate metadata from payload, encrypt at rest, and require explicit owner wording before revealing sensitive details. The report must distinguish recorded, inferred, and missing telemetry; missing logs cannot be presented as “nothing happened.”
- **missing:** A shared append-only event envelope and clock/skew reconciliation across pendant, relay, Mac, and browser; Browser hooks that emit submit/navigation/effect receipts rather than only command results; Mac file/app mutation events with before/after hashes and an explicit coverage boundary; A relay query that joins those streams and returns both observed actions and telemetry gaps


## Changes it proposed to its own stack

### `integration` — Ship a local USB pendant companion on the Mac that auto-discovers /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, opens the nRF9160 and ESP32 links with explicit framing/version negotiation, timestamps every device diagnostic/QoS frame against the Mac monotonic clock, and writes atomic incident bundles under ~/AI-Pendant-Workspace. It must reconnect after cable resets, never enable microphone capture by itself, and expose a relay-uploadable receipt rather than raw audio.
- **owner gets:** With the pendant physically attached but LTE unregistered, the owner can run and trust the audio-path diagnostic today, see whether a failure is modem, codec, bridge, or relay, and hand a reproducible report to the system instead of repeating “the voice sounded wrong.”
- effort: Medium: a small launch-agent/daemon, serial framing tests against both live ports, and a bounded incident schema; then wire the existing diagnostic fixture and QoS frames into it.  ·  risk: A bad auto-open could contend with a flashing/debug session or capture data unexpectedly. Require an explicit diagnostic arm from the Mac agent, release ports on malformed frames, cap bundle size, and make every write atomic with a receipt. Recovery is daemon restart and fixture rerun.
- cost: No model cost; a few KB per incident and negligible idle CPU. One-time engineering effort, no hardware purchase.  ·  latency: Port discovery under 2 s; diagnostic receipt under 10 s; reconnect after USB reset under 3 s.
- security: USB serial is local but still authenticate the bridge identity and redact payloads. Store counters and hashes by default; raw PCM only when the owner explicitly arms a test. Do not upload arbitrary serial text.
- depends on: mac_serial_exchange tool or an equivalent real local serial capability (currently still unavailable); firmware diagnostic fixture and duplex congestion QoS frames; relay ingestion route for signed device incident receipts


## What it asked for

_Nothing._
## Its own summary

Round 213 produced three cross-surface capabilities and one concrete integration change: USB fallback for the live conversation, pendant interruption/control of Mac/browser jobs, bookmark-correlated incident cards, and a local dual-serial diagnostic companion. I verified the Mac is online, Safari/browser bridge is online, relay is reachable, and Accessibility plus Screen Recording are now granted and input delivery is verified. The most valuable immediate path is making the physically connected pendant useful without LTE, then turning its bookmark into a reproducible device/Mac/relay incident record.

**Biggest unknown:** I still need a real typed USB-serial exchange capability for the two live ports (/dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA); the queued mac_serial_exchange request remains unavailable. I also need a relay-side correlation/ingestion route for signed bookmark telemetry and a browser in-flight pause primitive. Browser inspection currently fails resolution because action:browser_inspect and POST /browser/inspect tie, so a typed browser-tabs/inspection selector would remove that ambiguity.

