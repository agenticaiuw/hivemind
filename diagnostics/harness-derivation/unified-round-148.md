# Harness derivation — unified — round 148

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/relay health and pending pipeline** — As of this round the Mac agent, relay, browser extension, Accessibility, Screen Recording, and automation permissions are all live/ready. However /pipeline contains at least two stale runs with status=processing, and a completed run emitted 'Waiting for your approval on the dashboard' despite no approval UI; the relay accepted 24 kHz PCM but there is no physical playback receipt in the event chain.
  - evidence: GET /ops/snapshot returned agent ready, accessibility trusted, screenRecording granted, browser online, relay reachable; GET /pipeline returned processing runs and approval-waiting event followed by relay_result done.

## Capabilities it proposed

### "When I plug the pendant into my Mac, show me a local 'wearable console' that proves the button, mic, speaker, USB audio session, bridge, and firmware are healthy—without LTE or cloud—and let me run a spoken test phrase."
- **useful because:** The hardware is physically here now but LTE is unregistered. This gives the owner an immediate, privacy-preserving way to know whether the thing on their body works before relying on it, and makes USB the useful path rather than a developer-only serial cable.
- **path:** pendant → mac-bridge → mac-planner → dashboard
- **model tier:** deterministic diagnostics; use background model only to summarize failures in plain language
- **latency:** button/status indicators under 500 ms; synthetic audio test under 5 s; summary under 2 s after measurements
- **cost:** near-zero API cost for counters and fixtures; under $0.01 only if a background model summarizes an unusual failure
- **security:** Local USB only by default; never upload microphone samples. Test audio is generated locally and receipts contain counters, firmware version, and hashes only. Require explicit button press to start speaker/mic test.
- **missing:** serial protocol exposing authenticated health snapshot and test commands; Mac serial watcher and a small dashboard panel; bridge acknowledgement correlated to pendant test sequence

### "If you say a reply is ready but I do not hear it, tell me exactly where it stopped—model, relay, USB/LTE transport, bridge, decode, or speaker—and offer one safe retry of only the missing segment."
- **useful because:** A relay receipt is not proof that sound reached the owner's ear. This turns silent failures into a precise, recoverable interaction instead of making the owner repeat themselves or guess whether the pendant is broken.
- **path:** pendant → relay-realtime → mac-bridge → mac-planner
- **model tier:** deterministic event correlation; cheap background summarizer only for owner-facing wording
- **latency:** detect missing playback-start within 2 s; speak diagnosis on the next natural turn in under 1 s
- **cost:** negligible storage for bounded event receipts; no model call for normal paths, <$0.01 for summaries
- **security:** Store opaque turn IDs, hashes, timestamps, and counters—not raw audio. Retry must be idempotent and never duplicate speech; require confirmation before replaying a potentially sensitive response.
- **missing:** bridge-to-speaker playback-start/finish receipt wired through relay; bounded turn-state correlator and stale-audio suppression; a user-visible retry/confirm action

### "When I am speaking through the pendant, keep one conversation alive as it moves between LTE and the Mac's USB link, so a dropped radio does not create a new session or make me repeat the last sentence."
- **useful because:** The pendant and bridge are connected over USB today while LTE is unavailable. A real turn-preserving handoff would make the device dependable in a basement, airplane mode, or at the desk, rather than exposing transport changes as broken conversations.
- **path:** pendant → mac-bridge → relay-realtime → mac-planner
- **model tier:** deterministic transport/session arbiter; realtime model remains only for the active conversation
- **latency:** transport decision under 250 ms; handoff only at turn boundary, with no more than 300 ms added silence
- **cost:** no extra inference cost; bounded session metadata and duplicate suppression in relay storage
- **security:** Bind both transports to the same device/session nonce; encrypt USB framing; discard duplicate frames by monotonic sequence; never silently fall back to a different account or browser session.
- **missing:** cross-transport session lease and monotonic turn journal; firmware/bridge handoff marker at turn boundaries; relay support for USB-origin frames and replay-safe deduplication

### "Tell me the truthful state of anything I asked you to do—even if it is stuck, waiting, or only partly done—and let me say “leave it for later” or “cancel it” from the pendant without pretending an unavailable dashboard action exists."
- **useful because:** Today a pipeline can remain processing or say it is waiting for dashboard approval when no such control exists. The owner needs an honest, wearable answer and a safe disposition, not a misleading completion sentence.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** deterministic state reconciliation; realtime model only phrases the final short spoken status
- **latency:** status under 1 s; cancel/hold receipt under 2 s
- **cost:** negligible metadata and no extra inference on normal paths
- **security:** Cancellation must be bound to an opaque job/turn nonce and never infer permission to undo external effects. Say unknown rather than claim cancellation when a side effect may already have happened.
- **missing:** authoritative terminal-state reconciler for pipeline/jobs; wearable hold/cancel command and receipt; removal of false approval wording when no approval channel exists; stale-processing timeout policy

### "Let me ask the pendant to prepare a browser action as a spoken, minimal diff—what will change, which account/tab it affects, and what data it will send—then approve that exact diff with the physical approval latch before submission."
- **useful because:** The owner can safely use browser sessions that only the Mac can reach without exposing page contents to the relay or approving an opaque “done” promise. The pendant becomes a review surface and the physical latch becomes a real boundary.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic diff/provenance generation; background model may compress text but must not alter the signed diff
- **latency:** spoken preview under 3 s; approval receipt and submit under 5 s
- **cost:** small metadata cost; optional background summarization under $0.01; no raw page upload
- **security:** Bind approval to tab/session, origin, account label, plan digest, expiry, and a redacted field-level diff. Never send passwords, page screenshots, or form secrets to the relay.
- **missing:** browser-side structured dry-run and field diff; relay implementation of the approval handoff contract; pendant delivery of pending preview and approval result; submit endpoint that verifies the exact digest


## Changes it proposed to its own stack

### `integration` — Wire a local USB wearable-console path: the Mac serial watcher reads a versioned health frame from the nRF9160 and ESP32, runs the existing audio fixture on explicit request, correlates bridge acknowledgements, and renders a one-screen HEALTHY/DEGRADED/FAILED result with the failing hop and receipt ID.
- **owner gets:** The owner can plug in the pendant and know in seconds whether it is trustworthy, even with no LTE registration or cloud access.
- effort: Medium: serial framing, watcher, fixture invocation, and a small dashboard view.  ·  risk: Malformed serial input must be ignored; test mode must not open the microphone or speaker without a deliberate local request. Recover by disconnect/reconnect and preserve no raw audio.
- cost: No inference cost; a few KB of local status logs.  ·  latency: Status under 500 ms; fixture under 5 s.
- security: USB-local and authenticated; expose counters/hashes only.
- depends on: authenticated serial health/test frames from both chips; audio_path_diagnostic_fixture firmware hooks

### `relay` — Extend the existing audio delivery acknowledgement queue into a hop-complete state machine: generated, relay-accepted, transport-sent, bridge-accepted, decode-started, playback-started, playback-finished, interrupted. Add a bounded timeout classifier and an idempotent 'replay missing artifact' command that cannot replay an already-started artifact.
- **owner gets:** When audio disappears, the system can say whether the problem was radio, bridge, decoder, or speaker—and recover without making the owner repeat the request or hearing a duplicate answer.
- effort: Medium-high: bridge event format, relay persistence, timeout policy, and replay guard.  ·  risk: False timeout could cause a needless retry; require owner confirmation for replay and expire old artifacts. Recover by marking uncertain rather than guessing completion.
- cost: Small bounded metadata storage; no routine raw-audio retention beyond the existing delivery window.  ·  latency: Failure detection within 2 s; normal playback unchanged.
- security: Opaque artifact IDs and hashes; replay authorization bound to session and artifact.
- depends on: audio_delivery_ack_queue; ESP32 bridge playback start/finish events; relay event persistence

### `firmware` — Add an explicit turn-boundary transport handoff frame to the already accepted usb_fallback_audio_session: pause capture only at a monotonic turn boundary, transfer the session nonce and last acknowledged sequence, and resume on the alternate link with duplicate suppression and a one-frame silence budget.
- **owner gets:** Moving between desk USB and standalone radio would stop feeling like two devices; the owner would not lose a sentence or get the reply twice.
- effort: High: firmware ownership marker, bridge forwarding, relay deduplication, and fault tests.  ·  risk: A crash during handoff could strand a session; use a two-phase boundary marker and conservative timeout, then start a new turn rather than replaying uncertain audio.
- cost: Tiny RAM/state overhead; no model or routine API cost.  ·  latency: Up to 300 ms only during handoff; no added delay in steady state.
- security: Bind handoff to device/session nonce; reject stale or cross-session frames.
- depends on: usb_fallback_audio_session; duplex_audio_congestion_guard; relay job/session lease support

### `context` — Add a cross-surface causal timeline for each conversation turn that links the pendant sequence, relay job, Mac pipeline, browser command, and audio artifact, with explicit unknown gaps rather than synthetic success. Make it queryable by the pendant and dashboard and retain only bounded hashes/labels after the configured retention window.
- **owner gets:** When something goes wrong, the owner can ask “where did that turn go?” and receive one coherent answer instead of separate stale Mac, relay, browser, and audio histories that disagree.
- effort: High: event identity contract, correlator, clock-skew handling, redaction, and retention enforcement.  ·  risk: Bad correlation could merge two turns; require device/session/job bindings and expose confidence/unknown. If clocks disagree, preserve each source timestamp and never invent ordering.
- cost: Bounded metadata storage; no routine raw audio or page content retention. Background model optional only for wording.  ·  latency: Near-real-time updates; query under 1 s for recent turns.
- security: Opaque IDs, per-surface redaction, and owner-configured deletion; browser content remains local.
- depends on: pipeline event schema; audio delivery acknowledgement queue; browser command/result IDs; owner retention/deletion policy


## What it asked for

_Nothing._
