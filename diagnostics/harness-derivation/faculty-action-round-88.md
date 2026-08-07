# Harness derivation — faculty-action — round 88

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If I tell you to do something while I’m away, queue it safely, carry it out when the right device comes back, and tell me whether the intended result actually happened—not merely whether a command ran.”"
- **useful because:** Today an intent can be handed to a Mac job, but online/offline transitions, browser failure, and semantic success are separate. This would let the worn voice surface, always-awake relay, Mac/browser hands, and perception/judgement form one reliable action loop: accept a bounded intent, execute only while its lease is valid, verify the postcondition, retry only safe steps, and return a human-readable outcome.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-judgement → faculty-perception
- **model tier:** Use realtime only to capture/acknowledge the owner's short intent; use a cheaper background model for intent normalization, retry classification, and postcondition summarization.
- **latency:** Immediate acknowledgement under 1 second; execution may wait for device return. Verification within 10 seconds after each step, with a hard expiry supplied by the intent.
- **cost:** About $0.01–$0.05 per deferred intent, dominated by background verification/retry reasoning; routine Mac actions and receipts are negligible.
- **security:** Persist only the normalized goal, allowed surfaces, expiry, and redacted evidence pointers. Never replay an expired lease or escalate an irreversible browser/Mac step without explicit approval. Private page content remains on the Mac/browser; relay stores hashes and status. Pendant should announce failure without reading sensitive evidence aloud unless requested.
- **missing:** A first-class intent/lease record shared by relay and Mac jobs, including expiry, allowed actions, and a semantic postcondition; A verifier callback that can ask faculty-perception to inspect the resulting Mac/browser state and classify success, failure, or unknown; Bounded retry and cancellation semantics across reconnects, with an idempotency key spanning relay, /execute, and browser commands; Pendant delivery of final receipt/status when the device is paired again

### "“Pause that job here and let me resume it from the exact next step on whichever device is available, with a compact explanation of what already happened and what will happen next.”"
- **useful because:** Today long-running work is tied to the device and execution job that started it. A sleep, reconnect, or handoff can force the owner to repeat context or guess whether a step already happened. A portable checkpoint would make the hive act like one continuous worker: the Mac can stop after a verified boundary, the relay can preserve the checkpoint, the browser can reattach its session, and the pendant can resume or cancel without replaying completed side effects.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Use a small background model to summarize checkpoints and select the next eligible step; use realtime only for the owner’s resume/pause voice interaction.
- **latency:** Pause acknowledgement under 1 second. Resume briefing under 3 seconds, then execution proceeds asynchronously. Checkpoint writes must be atomic before any next side effect.
- **cost:** Typically under $0.02 per handoff; cost is dominated by one short checkpoint summarization, not the ordinary action calls.
- **security:** Checkpoints must contain opaque references and redacted state, not copied private page contents or credentials. Bind each checkpoint to the owner/session and an expiry. Never resume an irreversible step merely because a checkpoint exists; require the same approval class and fresh confirmation when needed.
- **missing:** A portable, append-only checkpoint schema with completed-step receipts, verified state, next-step preconditions, and browser session affinity; Atomic pause barriers in Mac and browser runners so no step is half-committed when a handoff is made; A resume planner that rejects stale checkpoints and reconciles them against fresh perception before continuing; Pendant-visible checkpoint summaries and explicit resume/cancel controls


## Changes it proposed to its own stack

### `relay` — Add a durable DeferredIntent envelope and state machine shared by relay and Mac: intentId/idempotencyKey, normalized goal, allowed surfaces, explicit postcondition, approval class, lease expiry, retry budget, current job/command IDs, and verification state. On reconnect, resume only unexpired intents; after every completed action invoke faculty-perception through /observe or a typed inspection, then emit a signed success/failure/unknown receipt to the pendant. Keep command receipts as child records rather than treating transport completion as task success.
- **owner gets:** When the owner says “do that later,” they get a trustworthy answer about the result—even if the browser was offline or the Mac slept—instead of silently duplicated work or a misleading “done.”
- effort: Medium: relay D1 schema/state machine, Mac adapter around /execute and browser command IDs, verifier callback, and pendant status rendering; add fault-injection tests for reconnect, expiry, duplicate delivery, and ambiguous verification.  ·  risk: A weak postcondition could falsely report success, and retries could duplicate side effects. Mitigate with explicit postconditions, idempotency keys, no automatic retry for irreversible actions, and an UNKNOWN result requiring review. Recover by cancelling the envelope and using existing job undo where available.
- cost: Low storage and API overhead; roughly one background verification call per completed intent, much cheaper than realtime reasoning.  ·  latency: Adds seconds after action completion for verification; immediate acknowledgement remains unchanged.
- security: Lease and approval class prevent stale or unauthorized replay; evidence should be hashed/redacted in relay and detailed private state retained only on Mac.
- depends on: Owner pairing of a pendant so final receipts can be delivered; Browser extension online for browser-backed intents; A small verifier contract between faculty-perception and action receipts; Existing durable job/receipt and browser command IDs

### `interaction` — Add a pendant-first emergency stop protocol: a long press or two-button gesture emits a locally generated, replay-resistant stop nonce; relay immediately marks all active action leases for that owner as cancelled, forwards cancellation to Mac jobs and queued browser commands, and returns a terse LED/audio acknowledgement. Each affected job records whether it stopped before or after its last committed step. This is a kill switch, not an approval prompt and not dependent on speech, Accessibility, or the browser being online.
- **owner gets:** If the owner hears an unexpected action, loses trust, or simply changes their mind, they can stop the hive from their body instantly—even while the Mac UI is stuck, the browser is unavailable, or the microphone is not open.
- effort: Medium: pendant firmware gesture and signed event, relay cancellation fan-out, Mac/browser cancellation adapters, and race-condition tests around already-committed steps.  ·  risk: A false trigger could cancel useful work; require a deliberate gesture and brief vibration/LED confirmation. Cancellation cannot undo an already-committed external side effect, so receipts must clearly distinguish stopped, completed, and unknown. Recover by allowing explicit resume from a checkpoint.
- cost: Negligible per-action API cost; small firmware and relay implementation cost, with no added model calls.  ·  latency: Relay cancellation should reach online Mac jobs in under 500 ms; offline browser commands are marked cancelled and prevented from later execution.
- security: Use a device-bound key and monotonic nonce to prevent forged or replayed stops. Do not expose job contents in the pendant acknowledgement.
- depends on: A paired pendant with a working button and secure device identity; Relay fan-out cancellation for Mac jobs and browser command queues; An atomic cancelled-before-execution check in each executor


## What it asked for

_Nothing._
