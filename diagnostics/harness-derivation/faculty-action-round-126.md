# Harness derivation — faculty-action — round 126

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’ve approved this on my pendant—carry out the prepared action now, but only if the physical confirmation is fresh.”"
- **useful because:** Turns the worn device into a possession-bound approval key. A prepared browser/Mac action cannot be accidentally triggered by a stale voice transcript, remote replay, or an unattended Mac; the owner gets a fast tactile commit path while the system keeps evidence of exactly what was approved.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Realtime model interprets the short approval and binds it to a pending action; deterministic relay/Mac code validates a nonce, expiry, device identity, and action hash; no expensive model call is needed to execute.
- **latency:** Under 500 ms from button/voice confirmation to relay acknowledgment; execution latency is the underlying Mac/browser operation.
- **cost:** <$0.001 per approval after implementation; dominant cost is any original planning call, not the nonce validation.
- **security:** The approval must be a one-time nonce bound to action hash, account/session, and 10-second expiry; never transmit or log secrets. Require explicit confirmation for irreversible actions and show a compact spoken summary before arming. Missing today: pendant identity/serial approval protocol and a server-side pending-action gate.
- **missing:** pending-action approval ledger with nonce/action hash/expiry; USB-serial pendant confirmation bridge usable today and LTE transport later; irreversible-action policy integration

### "“If that computer task partially succeeded, find out what actually changed, finish only the missing parts, and tell me exactly what you repaired.”"
- **useful because:** Most dangerous automation failures are ambiguous outcomes: a form may have submitted while the receipt timed out, or a calendar event may have been created before the browser crashed. This capability makes the action system outcome-oriented rather than retry-oriented, preventing duplicate submissions and giving the owner a trustworthy final state.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action → unified
- **model tier:** Cheap background reconciliation compares typed receipts and fresh observations; realtime is used only to explain the result to the owner. Deterministic idempotency and state checks precede any repair.
- **latency:** Initial ambiguity notice within 2 seconds; reconciliation within 30 seconds for normal Mac/browser tasks, with a durable job continuing after disconnect.
- **cost:** $0.003–$0.02 per ambiguous task depending on observation/model extraction; most successful tasks incur no extra model call.
- **security:** Never blindly retry mutations. Re-observe the exact account/tab/object, require idempotency keys, preserve before/after evidence, and escalate if identity or destination differs. Data leaving device is limited to necessary page/action metadata. Missing today: a typed postcondition/reconciliation engine and cross-surface receipt ledger.
- **missing:** postcondition declarations per action; cross-surface state reconciliation and repair planner; durable receipt ledger correlating browser tab, Mac job, and resulting object

### "“Walk me through this checklist one step at a time; do the safe computer steps, pause for my pendant confirmation at the risky steps, and let me cancel without touching the Mac.”"
- **useful because:** Makes long real-world workflows usable while the owner is away from the screen: the Mac/browser handles navigation and data gathering, while the pendant provides an unmistakable checkpoint and emergency stop. The owner can complete tasks such as returns, travel changes, or account recovery without surrendering control of the final commits.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → faculty-judgement → faculty-action
- **model tier:** Background/local planner decomposes and executes reversible steps; realtime model speaks only current step and interprets brief responses. Deterministic checkpoint state machine handles pause, timeout, cancel, and resume.
- **latency:** Spoken next-step update under 1 second; safe steps proceed automatically; risky-step confirmation expires after 60 seconds and cancellation takes effect within 1 second.
- **cost:** $0.01–$0.08 per multi-step workflow, dominated by initial planning and occasional browser extraction; checkpoint turns are cheap.
- **security:** Each checkpoint displays action, target, and expected effect in speech/pendant LED pattern; cancel must be local and work through USB even if relay is unreachable. Do not expose page contents on audio unless requested. Missing today: durable workflow state machine, pendant button/LED protocol, and action-specific risk classifier.
- **missing:** checkpointed workflow executor with pause/resume/cancel; local USB pendant cancel/confirm transport; risk-classified action plans and per-step postconditions

### "“Move this appointment to the best available time, but don’t cancel the current one unless the replacement is confirmed.”"
- **useful because:** The owner gets safe multi-system transactions instead of brittle sequences that can leave them with no appointment, duplicate bookings, or a missing reservation. The system can negotiate a replacement, hold it, and commit only when the complete transition is evidenced.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception → faculty-action
- **model tier:** A cheaper background planner searches and compares options; deterministic transaction orchestration handles holds, commit ordering, compensation, and timeouts. Realtime is used only for presenting the choice and receiving a final preference.
- **latency:** Show viable options within 60 seconds where the site permits; commit confirmation within 2 seconds after the owner’s pendant approval; retain the old booking until the replacement has a durable confirmation.
- **cost:** $0.02–$0.15 per transaction, dominated by authenticated-page extraction and any negotiation/planning calls.
- **security:** Never expose booking credentials or commit without explicit approval. Bind every hold and commit to the exact account, appointment, timezone, and expiry. If a site cannot guarantee holds, stop rather than simulate atomicity. Missing today: a saga/compensation coordinator, reservation-hold abstraction, and cross-site transaction policy.
- **missing:** cross-service transaction coordinator with compensation steps; reservation/hold and expiry model; commit proof requirements for each supported service

### "“When I leave my desk, keep the task alive and tell me on the pendant only when I need to make a decision that cannot wait.”"
- **useful because:** The owner can hand off long tasks without keeping a Mac screen open or listening continuously. The relay filters routine progress, while the pendant delivers only deadline-bearing decisions with enough context to act from anywhere.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Background model summarizes progress and classifies urgency; a cheap deterministic scheduler handles deadlines and quiet hours; realtime is reserved for the brief spoken interruption and response.
- **latency:** Decision alerts delivered within 3 seconds of detection; routine work may continue for minutes or hours without conversation turns.
- **cost:** $0.005–$0.03 per task-hour depending on polling and summarization; most idle time uses no model calls.
- **security:** Only send minimum necessary information to the pendant; redact private page content and require a physical confirmation for consequential decisions. Offline delivery needs a bounded local queue and expiry so stale prompts cannot commit anything. Missing today: urgency/deadline policy, durable decision inbox, and pendant notification protocol.
- **missing:** durable decision inbox with deadline and escalation semantics; quiet-hours and urgency policy; pendant notification/acknowledgment transport

### "“Give me a private, spoken handoff when I arrive home: what changed while I was away, what decisions are waiting, and what I can safely approve now.”"
- **useful because:** This creates a useful boundary between unattended work and owner control. Instead of a noisy stream of alerts or a generic morning briefing, the owner receives a compact, current handoff that separates completed work, blocked work, and actions ready for approval.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** A background model compiles the handoff from receipts, deadlines, and pending decisions; realtime speaks it when the owner requests it. Deterministic filtering excludes stale, already-resolved, or low-priority items.
- **latency:** Generate within 5 seconds on request; spoken handoff under 60 seconds by default, with drill-down on demand.
- **cost:** $0.005–$0.04 per handoff, mostly summarization; receipt collection and filtering are deterministic.
- **security:** Require owner presence/physical pendant acknowledgment before reading sensitive titles aloud; support a silent LED/vibration summary and explicit “details” command. Never infer completion from absence of an error. Missing today: a cross-surface handoff compiler, privacy-aware audio policy, and presence/arrival signal.
- **missing:** handoff compiler over jobs, browser sessions, and decisions; privacy-aware spoken disclosure policy; arrival/presence trigger or explicit pendant request path


## Changes it proposed to its own stack

### `interaction` — Add a visible and audible 'armed action' state spanning relay, Mac, browser, and pendant: the system publishes the pending action hash, target, expiry countdown, and required confirmation; the pendant LED/button and Mac dashboard show the same state, and any mismatch automatically disarms it.
- **owner gets:** The owner can know at a glance—or by touching the pendant—whether the system is waiting for approval, executing, or safely disarmed, instead of wondering whether saying 'yes' will trigger an old or different task.
- effort: Medium: shared action-state schema, relay fan-out, Mac dashboard rendering, and USB serial firmware integration; no flash until separately approved.  ·  risk: A lost serial link could leave stale UI; short expiries and relay-side truth recover safely. Never treat a displayed state as proof of execution; receipts remain authoritative.
- cost: Negligible runtime/API cost; modest engineering cost.  ·  latency: One small state update per action and sub-second propagation on LAN/USB.
- security: Improves replay resistance and reduces accidental authorization; action hashes should avoid embedding secrets and logs should retain only redacted targets.
- depends on: pending-action approval ledger; cross-surface receipt ledger; USB serial pendant bridge


## What it asked for

_Nothing._
