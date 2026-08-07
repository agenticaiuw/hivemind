# Harness derivation — faculty-action — round 75

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Carry this out across my Mac and logged-in browser, but if anything changes underneath you, pause safely, keep my place, and tell me exactly what completed and what remains.”"
- **useful because:** Today each surface can queue work and produce receipts, but a multi-surface task can lose its place between the Mac job queue and browser command lease. This gives the owner one resumable operation: the relay coordinates typed checkpoints across pendant, Mac, and browser, automatically stops on stale preconditions or lost leases, and reports a concise spoken state rather than claiming completion or replaying an action.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the realtime tier only to capture the owner's short command and announce state changes; use a cheaper background model for planning/reconciliation and deterministic executors for Mac/browser steps.
- **latency:** Acknowledge in under 2 seconds; individual steps may run asynchronously. On disconnect, checkpoint within 5 seconds and resume only after lease/state reconciliation.
- **cost:** Roughly $0.01–$0.05 per multi-step operation for background planning/reconciliation; dominant cost is model calls for ambiguous recovery, not deterministic Mac/browser execution.
- **security:** Action packets must contain only task-scoped private data, with browser session IDs never exposed to the pendant. Never replay a step whose idempotency key has an unknown outcome. Any send/delete/purchase remains stopped for the existing owner confirmation policy. Log before/after evidence and redact secrets from receipts.
- **missing:** A cross-surface saga coordinator with durable action packets, step dependencies, checkpoint state, and compensating/reconciliation rules; A resumable browser result protocol replacing the current single blocking browser wait with progress events and polling; Mac executor precondition evaluation and lease renewal (the implemented receipts/undo layer currently records outcomes but does not gate stale state); A pendant-visible compact state/lease indicator and a dashboard timeline joining Mac and browser receipts

### "“Stop whatever you’re doing everywhere.” (or double-press the pendant button)"
- **useful because:** A long-running Mac/browser action can outlive the spoken conversation. The owner needs a physical, low-latency stop that cancels queued work across surfaces, prevents a leased browser command from being replayed, and reports which steps could not be stopped. This is an emergency interrupt, not an approval gate: it should work even when the relay is reconnecting and should never silently undo irreversible effects.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** No expensive model on the stop path. The pendant emits a signed stop event; relay, Mac, and browser executors apply deterministic cancellation. Realtime only speaks the resulting receipt if a link is available.
- **latency:** Local LED/button acknowledgement under 100 ms; relay fan-out under 1 second; each executor marks cancellation or unknown outcome within 5 seconds. If disconnected, persist the stop intent and apply it when the link returns before accepting new work.
- **cost:** Negligible model/API cost; implementation and durable event storage dominate.
- **security:** Only a physically authenticated pendant and the active owner session may issue the global stop. Stop events need monotonic sequence numbers and replay protection. Cancel does not delete data or claim rollback; every already-started irreversible step is explicitly reported. Store no page contents in the stop record.
- **missing:** A firmware-local stop-event spool and button gesture handler that survives a dropped relay link; A relay fan-out endpoint that atomically marks an operation cancelled before dispatching cancellation to Mac and browser; Executor cancellation tokens and a terminal unknown-outcome state for in-flight commands; A compact pendant LED/audio acknowledgement and dashboard view of stopped, completed, and unknown steps

### "“Handle this form using my logged-in information, but keep sensitive fields on my devices—do not send passwords, payment numbers, or identity numbers to the model or relay.”"
- **useful because:** The owner cannot safely delegate many everyday tasks today because the browser may contain secrets that must not enter model context or relay logs. This would let the mind coordinate a private browser-to-Mac action while proving that sensitive values stayed local, rather than forcing the owner to type every protected field themselves.
- **path:** pendant → relay → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** Use a cheap background planner for field classification and deterministic local executors for filling protected fields. The realtime tier should receive only a short status and never the values. A stronger model is needed only for ambiguous field semantics, with a hard deny-by-default policy for protected data.
- **latency:** Classify the page and produce a redacted plan within 2 seconds; local protected-field filling should feel interactive, under 1 second per field. If classification is uncertain, pause rather than transmit.
- **cost:** Low API cost because sensitive values never become prompt tokens; the dominant cost is one planning/classification call for an unfamiliar form and local browser execution.
- **security:** Sensitive values must be represented by device-local opaque handles, never copied into relay requests, model prompts, screenshots, receipts, or spoken output. The browser extension needs a strict field policy, DOM-origin binding, clipboard prevention, and audit hashes rather than plaintext. Require explicit confirmation for any protected value that would leave the local device; default is refusal. Recovery must clear temporary values and invalidate handles after completion.
- **missing:** A browser-local sensitive-field broker that detects password, payment, identity, and private-contact fields and fills them without exposing values; A redacted action-plan schema carrying field labels, origin, constraints, and opaque local handles rather than field contents; End-to-end secret-flow enforcement across relay, Mac logs, browser results, screenshots, receipts, and dashboard; A user-visible privacy receipt proving which fields stayed local and which (if any) crossed a boundary


## Changes it proposed to its own stack

### `integration` — Add a resumable audio-delivery protocol for 24 kHz generated briefings: the Mac/relay emits an operation-scoped manifest (codec, sample rate, duration, chunk hashes), the relay sends numbered chunks with bounded backpressure, and the pendant ACKs the highest contiguous chunk plus a final playback receipt. Persist only the manifest and a short replay window; on reconnect resume from the last ACK instead of restarting or duplicating speech. Surface underruns, codec mismatch, and truncated playback as explicit job/briefing status.
- **owner gets:** A briefing that was generated successfully should actually be listenable later. The owner gets one spoken confirmation that audio was fully delivered and can resume after walking out of range, instead of discovering a silent, partial, or duplicated queue item.
- effort: Medium: protocol and relay integration, a small pendant transport/playback state machine, and end-to-end tests with dropped links, delayed ACKs, and power loss.  ·  risk: A stale ACK could skip audio or replay it. Prevent this with manifest IDs, monotonic chunk sequence numbers, hash checks, and bounded replay; discard an incomplete item rather than presenting it as complete. Recovery is retry from the last verified chunk or regenerate the item.
- cost: No additional model cost; modest relay storage for manifests/replay windows and negligible device flash/RAM for state. Audio generation remains the dominant API cost.  ·  latency: Adds milliseconds of ACK/control overhead and may delay final completion until playback buffering is verified; initial playback can begin as soon as the first safe buffer is filled.
- security: Use opaque briefing IDs and authenticated transport; do not put transcript text in chunk metadata. Expire manifests and replay buffers promptly.
- depends on: The 24 kHz path acceptance criteria already requested from the orchestrator; A firmware-local durable event/queue primitive (offline_intent_spool request is still unanswered); An authenticated relay-to-pendant data channel with delivery acknowledgements; A canonical briefing/job ID shared by /research, /pipeline/audio, and the audio queue


## What it asked for

_Nothing._
## Its own summary

Recorded three forward proposals. (1) A cross-surface resumable action packet joining existing Mac jobs, browser commands, leases, receipts, and undo; the missing work is coordination and stale-state reconciliation between those pieces. (2) A physical pendant emergency stop that fans out cancellation to Mac/browser and reports unknown in-flight outcomes without pretending rollback. (3) A 24 kHz audio-delivery protocol with manifests, chunk hashes, contiguous ACKs, reconnect resume, and honest playback receipts so generated briefings are actually listenable. The owner’s Mac is online, but home Chrome is offline; no new orchestrator grants appeared in this round.

**Biggest unknown:** The 24 kHz acceptance criteria and owner action/approval priorities are still unresolved upstream, as are the requested firmware inspection/build access and audio-path probe. I did not re-request them. Those criteria determine codec, buffering, retention, and what counts as a successful playback receipt; without them, the audio proposal cannot be implemented or verified end to end.

