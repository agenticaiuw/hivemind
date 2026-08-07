# Harness derivation — relay-realtime — round 77

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Let me talk naturally while I’m walking; keep understanding me and carrying out the request even when LTE quality changes.”"
- **useful because:** Today the pendant uplink is 15,625-Hz mono while TTS is 24-kHz mono, with no demonstrated end-to-end input-rate negotiation. The owner should not have to repeat themselves or silently lose an intent because radio conditions or sample-rate conversion damaged a short spoken command. The relay should negotiate an input profile, preserve chunk boundaries and transcript continuity, and make the downstream Mac/browser action use the final reconciled utterance.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime model handles only live turn-taking, codec/profile selection signals, and concise recovery prompts; downstream planning and browser/Mac work stays on the cheaper planner/action tiers.
- **latency:** Profile selection and stream handoff under 150 ms; ordinary speech remains sub-second to first acknowledgement. A degraded-link reconciliation may add 1–3 seconds, but the pendant should say that it is still processing rather than drop the request.
- **cost:** Small incremental realtime-token cost for an occasional recovery turn; dominant cost is unchanged speech inference. Engineering cost is transport/codec QA and a bounded transcript-reconciliation buffer, not a model call per audio chunk.
- **security:** Audio and transcript continue to leave the pendant over the existing authenticated link. The relay must bind reconciled chunks to the same voice run, reject late/duplicate chunks, and never execute an action from an unverified partial transcript; only the final intent is handed to Mac/browser surfaces.
- **missing:** Authenticated codec/sample-rate negotiation between pendant firmware and /pipeline/audio; Sequence numbers, replay/deduplication, and resumable input chunks for a voice run; A final-transcript barrier before mac-planner/mac-vision/browser-extension execution; Telemetry exposing input-rate conversion loss and radio-induced gaps to the owner-facing receipt

### "“Stop the thing you’re doing right now.”"
- **useful because:** The owner is wearing the only always-present control surface and may be away from the Mac. They need a spoken interrupt that propagates to an in-flight Mac or browser job, stops not-yet-started steps, and tells them exactly which step (if any) already happened. This is an explicit abort, not an approval gate, and is different from discovering a completed job afterward.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** No expensive reasoning model is needed for the stop path: realtime only performs wake-word/intent recognition, while relay and downstream agents use a typed cancellation signal and receipt update.
- **latency:** Acknowledge locally in under 250 ms and deliver cancellation to the active surface under 500 ms when connected. If a physical action is already non-interruptible, report that fact immediately and stop subsequent steps.
- **cost:** Near-zero model cost beyond recognition already being performed; modest relay state and cancellation endpoint implementation.
- **security:** Only the pendant's authenticated active voice session may cancel its own voiceRun/job. Cancellation must be idempotent, auditable, and scoped to the selected job—not a broad kill switch for unrelated work. A late cancel cannot falsely claim that an already-completed mutation was undone.
- **missing:** A relay registry mapping active voice runs to downstream job IDs and cancellation tokens; Cooperative cancellation checkpoints in mac-planner/mac-vision/browser command queues; A typed cancel endpoint and receipt state such as cancel_requested, stopped_before_step, or completed_before_cancel; A short spoken acknowledgement path that does not wait for the full job planner


## Changes it proposed to its own stack

### `integration` — Add a durable VoiceRun Envelope that spans POST /pipeline/audio through intent selection, POST /execute, and job receipts. The envelope carries voiceRunId, monotonically increasing audio sequence numbers, negotiated sample rate, partial/final transcript hashes, selected downstream surface, and completion state. The relay accepts retransmitted chunks idempotently, refuses execution until a final transcript hash is present, and emits one owner-readable receipt linking the spoken request to the actual Mac/browser result.
- **owner gets:** A person wearing the pendant gets one coherent answer instead of a confusing mix of partial recognition, duplicate actions, and later job receipts. If they repeat themselves during a bad LTE moment, the system can recover without running the request twice; if something fails, they can ask what happened and receive a precise answer tied to the original utterance.
- effort: Medium: schema and state-machine work in the Worker, firmware sequence fields, pipeline adapter changes, and contract tests covering reconnect, duplicate chunks, late results, and Mac/browser unavailability.  ·  risk: A bug in the final-transcript barrier could delay legitimate actions or strand a voice run. Recover by expiring incomplete envelopes, exposing an explicit failed/retry state, and retaining the existing direct execution path behind a server-side emergency switch for diagnostics.
- cost: Negligible storage and CPU per voice run; bounded retention (for example, metadata plus hashes rather than raw audio) keeps Worker storage low. No additional model call for normal turns.  ·  latency: No measurable added latency on healthy streams; idempotency checks are local. Reconnect reconciliation can add up to a few seconds, with spoken progress feedback.
- security: Improves auditability and replay resistance. Raw audio need not be persisted; transcript hashes and authenticated run IDs prevent a stale partial utterance from triggering a new action.
- depends on: The input codec/sample-rate negotiation proposed above; A durable or otherwise crash-safe voice-run state store on the relay; A final-transcript signal from the realtime speech pipeline; Receipt metadata support in the existing job/action path


## What it asked for

_Nothing._
## Its own summary

Recorded two new proposals: (1) an adaptive, resumable voice uplink with end-to-end sample-rate negotiation and final-transcript integrity, and (2) an explicit spoken emergency cancellation path that propagates from the worn pendant to in-flight Mac/browser jobs. Both depend on connective state and typed protocols that are not wired today, rather than merely exposing existing routes.

**Biggest unknown:** Whether the live firmware and pipeline can be extended to carry authenticated sequence numbers and a negotiated input profile without replacing the current LTE audio transport.

