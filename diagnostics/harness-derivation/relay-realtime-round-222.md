# Harness derivation — relay-realtime — round 222

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I change my mind, let me pause, cancel, or reprioritize the thing you are doing on my Mac or in my browser—by speaking to the pendant—and tell me exactly what was stopped and what was already done."
- **useful because:** Today delegation is effectively fire-and-forget: the owner may be away from the Mac and cannot safely steer a long or unexpectedly broad workflow from the wearable. Conversational cancellation would make the hive trustworthy for real work, not just one-shot commands.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime interprets a short control utterance and resolves it against the active job; the existing cheaper planner/vision tiers continue the work or perform the cancellation. No expensive model is needed to summarize a receipt.
- **latency:** Acknowledge pause/cancel within 500 ms from the relay, issue the stop at the next action boundary, and speak a receipt within 2 seconds. If the target is ambiguous, list the active jobs rather than guessing.
- **cost:** Low: one short realtime turn plus a small status/receipt call; the dominant cost remains the already-running planner or browser job, not cancellation.
- **security:** Stopping is reversible in most cases but cannot undo an external side effect already committed. The relay must expose an explicit state machine (queued, running, stopping, stopped, completed, partially_completed) and report the last confirmed action, not claim rollback. Job identifiers and action receipts must remain scoped to the owner.
- **missing:** A first-class cancel/pause/reprioritize endpoint and cooperative cancellation checkpoints in Mac planner, vision loop, and browser command execution; A spoken active-job resolver that maps phrases like 'that one' to recent jobs without inventing a second protocol; A durable partial-completion receipt delivered through the existing pendant inbox/event path

### "When my Mac drops offline halfway through something, keep the job safely paused, tell me on the pendant what remains, and continue it automatically when the Mac returns—without making me restate the task."
- **useful because:** The owner is usually away from the Mac, so a network hiccup currently turns a multi-step request into an uncertain half-completion. Durable handoff would make the wearable and Mac feel like one agent instead of two devices that forget each other.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the realtime tier only for the owner's brief status question and resume command. A durable relay job record and the cheaper Mac planner should serialize and recover the plan; no model should be called merely to retry transport.
- **latency:** Detect a lost Mac lease within 5 seconds, speak a short offline/paused notice within 2 seconds after that, and resume within 10 seconds of a healthy reconnect. Recovery must be idempotent rather than racing a duplicate action.
- **cost:** Low incremental inference cost; most work is durable state and connectivity. A recovery turn should send only the compact plan cursor and receipts, not the full conversation.
- **security:** A replay could duplicate an email, purchase, deletion, or other external mutation. Every action needs an idempotency key and a durable committed/unknown result; automatically retry only actions classified as safe or explicitly marked retryable, and surface unknown external effects to the owner. Do not send full task context to an unpaired Mac.
- **missing:** A durable job lease and reconnect protocol spanning relay and Mac, with cursor, action idempotency keys, and an explicit paused/offline state; Mac agent startup recovery that claims a lease and resumes only after reconciling the last action receipt; Pendant delivery of a paused-state summary and a spoken 'continue that' resolver after reconnect; A network-independent test harness that kills the Mac link between every action and verifies no duplicate side effect


## Changes it proposed to its own stack

### `hardware` — Add a low-power haptic actuator and a second deliberate input (a tactile side button or rotary encoder with press) to the pendant, then reserve them for silent control: acknowledge/dismiss an alert, pause or cancel an active job, and resume the same voice turn after an accidental release. Keep the existing single LED and primary button semantics unchanged.
- **owner gets:** They could control a remote workflow or acknowledge a result without stopping what they are doing or needing to look at the pendant; a second deliberate input also gives a safe way to resume a clipped thought without making the current record button ambiguous.
- effort: New enclosure and PCB revision, one GPIO/driver path, debounce and power-budget work, and firmware gesture/state tests over USB serial before LTE testing. The relay must advertise input capabilities and map them to the active session/job.  ·  risk: Accidental presses, false haptic interpretations, and jewellery-size/power compromises. Recover with long-press/press-confirm gestures, configurable haptic patterns, and a firmware kill switch; never make cancellation or resume depend on the LED.
- cost: Roughly $2–8 in prototype components plus enclosure/PCB revision; a haptic motor adds brief 10–80 mA pulses and the extra input is negligible when idle. It avoids storing audio or adding routine SD writes.  ·  latency: Local acknowledgement/resume can be immediate over the USB/LTE link; haptic feedback is sub-100 ms and removes a spoken round trip for simple controls.
- security: Physical presence becomes a stronger owner signal for pause/resume and alert acknowledgement, but it is not a cryptographic authenticator. Preserve the existing owner policy and log the input event with the job/session receipt.
- depends on: GET /v1/devices/status; GET /pipeline; POST /execute; GET /jobs/:jobId/receipts


## What it asked for

_Nothing._
## Its own summary

Recorded three non-duplicate proposals: (1) pendant-controlled pause/cancel/reprioritize for active Mac/browser jobs with truthful partial receipts; (2) a haptic actuator plus deliberate second input for silent job control, alert acknowledgement, and same-turn resume; and (3) durable relay/Mac job leases that survive Mac disconnects, reconcile the last action, and resume idempotently without making the owner restate the task. The live context-projection wiring was attempted but correctly rejected as already in the backlog.

**Biggest unknown:** The exact cancellation and durable-lease endpoints are not present in the observed route inventory; implementing these needs new relay/Mac protocol and cooperative checkpoints in every executor.

