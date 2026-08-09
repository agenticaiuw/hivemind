# Harness derivation — relay-realtime — round 268

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “take care of this,” have the pendant, relay, Mac, and my logged-in browser collaborate until the real-world result is verified—not merely until an action was attempted—and tell me exactly what remains if verification fails."
- **useful because:** Today the owner can hand work to one downstream surface and later ask for a job status, but cannot get a single accountable loop spanning a Mac app and an authenticated browser. This would turn vague spoken delegation into a trustworthy outcome, especially when the owner is away from the Mac.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use relay-realtime only to clarify the initial utterance and narrate concise updates; use the cheaper Mac planner for planning, browser harness for authenticated web state, and a background verification worker for retries and reconciliation.
- **latency:** Acknowledge in under 2 seconds; first plan in 5–10 seconds; completion may take minutes. The owner should be able to stop talking and receive a later pendant alert.
- **cost:** About $0.01–$0.08 per delegated task depending on planner retries and browser verification; verification and retries dominate, not the spoken turn.
- **security:** The browser session may expose private data to the planner and relay. Keep page contents scoped to the task, retain only a redacted receipt, and require an explicit owner policy for irreversible external effects. Never claim success from a click receipt alone.
- **missing:** A durable cross-surface task state machine with plan, execute, verify, retry, and compensating-action states; A browser-side verification contract that returns evidence rather than only action success; A background worker/alarm that continues the loop while the Mac is offline and resumes when it returns; A single pendant-facing completion event containing evidence and an actionable failure reason

### "Save my current work moment when I press the pendant: include what I said, the Mac's open apps and windows, and the browser's logged-in tabs; later say “restore the moment from yesterday” and put me back where I was, without reopening anything that has become unsafe or stale."
- **useful because:** A wearable can mark the instant an interruption happens, but today a spoken note, Mac state, and browser session are separate and not restorable as one unit. This would make the pendant a genuine interruption-and-recovery device for the owner's real work.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime model only for the short spoken label. Use a cheaper background model to summarize and redact the snapshot, and deterministic Mac/browser adapters to capture and restore state.
- **latency:** Capture acknowledgement under 1 second and snapshot completion under 10 seconds. Restore should begin immediately, with a concise report of stale or unavailable items.
- **cost:** Roughly $0.005–$0.03 per snapshot/restore; screenshots, browser metadata, and model summarization dominate storage and cost.
- **security:** Logged-in URLs, window titles, and screenshots can contain secrets. Encrypt snapshots, default to metadata rather than page bodies, apply a per-surface retention period, and show the owner exactly which tabs/apps will be restored before any destructive replacement.
- **missing:** A versioned workspace-snapshot schema shared by Mac and browser adapters; Mac actions to enumerate and restore window/app state, including safe stale-state checks; Browser extension export/import of tab groups and session identifiers without sending page contents; A durable encrypted snapshot store and a pendant gesture/voice command to select snapshots

### "While a delegated task is running, let me press the pendant and say a correction like “skip that site and use the second result”; resume the existing Mac/browser job from its checkpoint, preserving useful work instead of starting over."
- **useful because:** Today the pendant can interrupt speech, and the owner can learn a job's status, but cannot safely steer an in-flight multi-step task. A correction currently means abandoning the context or waiting for a wrong workflow to finish. This gives the owner practical control while away from the Mac.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use relay-realtime for the short correction and intent extraction; use a cheaper planner to compute a delta against the checkpoint; let deterministic adapters execute only the changed suffix.
- **latency:** Acknowledge the correction in under 2 seconds, checkpoint in under 5 seconds, and resume within 15 seconds. The owner should hear whether the old branch was cancelled, preserved, or already irreversible.
- **cost:** About $0.01–$0.06 per correction, mostly planner context and any browser reinspection; materially cheaper than replanning the entire task.
- **security:** Cancellation races can leave partial external changes. Persist an action journal, mark irreversible steps as already committed, never replay them, and include the exact checkpoint and affected surfaces in the spoken receipt. The owner’s correction and page evidence should have bounded retention.
- **missing:** Cooperative pause/cancel/checkpoint semantics in the Mac planner and browser command queue; A job action journal with idempotency keys and a dependency graph of completed steps; Relay routing that can associate a new utterance with the active job without inventing a second protocol; A planner mode that produces a minimal delta plan and explicitly reports irreversible steps


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: a cross-surface delegated task that verifies real-world outcome, restorable Mac+authenticated-browser work moments, and live correction/resumption of an in-flight job. All three require missing connective state machines and adapters rather than another speech feature. The most valuable is verified delegation: the owner should be able to say one thing while away from the Mac and receive evidence of what actually changed, not a click receipt.

**Biggest unknown:** Which existing job/execute routes have authoritative cancellation and idempotency semantics; without those, verification, restoration, and in-flight correction must be implemented as new durable protocols rather than safely composed from today’s APIs.

