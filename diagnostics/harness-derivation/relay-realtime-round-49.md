# Harness derivation — relay-realtime — round 49

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep an eye on this delegated task and only interrupt me if you hit a blocker or the result materially changes; otherwise give me a spoken completion or failure summary when it is done.”"
- **useful because:** Today a pendant request is effectively a single turn: once work leaves the realtime relay, the owner cannot rely on a durable, cross-surface conversation that notices a meaningful state change, asks one targeted clarification, and resumes without making them repeat the task. This would make delegation trustworthy while the owner is away from the Mac, without flooding them with progress noise.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard-ux
- **model tier:** Realtime handles the initial utterance, blocker clarification, and concise spoken notification only. mac-planner uses the cheaper planning tier for the task; mac-vision/browser-extension perform the work; a durable relay monitor evaluates typed state transitions and suppresses routine progress.
- **latency:** Immediate acknowledgement in under 1 second. Normal progress is silent. A blocker notification should reach the pendant within roughly 5 seconds of a typed failure/clarification event; completion summary can arrive within 10 seconds of the final receipt.
- **cost:** About $0.01–$0.08 per delegated task depending on planner/vision steps; the dominant cost is existing Mac/browser model calls, not the short realtime interruption. Monitor transitions should be rule-based and nearly free.
- **security:** Task state, action receipts, and any clarification context leave the Mac for the relay; authenticated page contents must remain redacted to the minimum needed for the blocker/result. Notifications must be bound to the paired pendant and never expose secrets in spoken summaries. Mutations follow the owner's existing maximum-access policy, but an explicit confirmation should still be required only where the downstream application itself demands it.
- **missing:** A durable task monitor with typed lifecycle events and a resumable clarification state, surviving Worker restarts; A push channel from relay to the paired pendant, including deduplication and offline retry; A common result/blocker schema emitted by mac-planner, mac-vision, and browser-extension; A small relay policy engine that classifies changes as silent progress, actionable blocker, or completion; A dashboard view showing the task timeline and exactly what context will be spoken


## Changes it proposed to its own stack

### `relay` — Add a durable, priority-aware pendant notification inbox rather than treating relay output as only a response to an active voice turn. Each notification gets a task/event id, urgency, expiry, spoken-safe summary, and delivery/ack state. The relay stores it durably, retries after LTE loss, coalesces repeated updates, and exposes the full receipt to the dashboard; the pendant firmware only needs a tiny push/LED/vibration cue and can fetch the summary on the next connected voice session.
- **owner gets:** The owner can leave the Mac unattended and still trust that a blocked or completed delegated task will reach them, without repeated polling or a noisy stream of progress messages. Expiring stale notices prevents the pendant from surprising them with an irrelevant result days later.
- effort: Medium: define an event envelope and idempotency rules, add a Durable Object or durable queue/outbox, implement authenticated pendant pull/push and retry semantics, then add relay speech summarization and dashboard inspection. Requires a small firmware update for notification cue and acknowledgement.  ·  risk: A retry or reconnect could produce duplicate or stale spoken notifications; mitigate with event ids, expiry, acknowledgement, and coalescing. A compromised session could leak task summaries, so bind delivery to the paired device and keep sensitive content server-side until speech generation. Recovery is replay from the durable outbox and dashboard/manual dismissal.
- cost: Low ongoing API cost (mostly storage and a few tiny Worker operations); roughly a few kilobytes per pending event. Firmware power impact should be negligible if the pendant polls only on its existing LTE wake/connect cycle; push would need measurement. Durable Object/queue/storage charges are the main infrastructure cost.  ·  latency: No impact on ordinary voice turns. A connected pendant can receive an urgent event within seconds; offline delivery is necessarily deferred until the next link opportunity.
- security: Adds a new notification data path and therefore requires device pairing, per-event authorization, replay protection, and redaction before any spoken summary. It should not transmit raw browser pages, mail bodies, or credentials to the pendant.
- depends on: A common typed task lifecycle/blocker/completion event schema across Mac and browser agents; Authenticated paired-pendant identity and replay protection; A Worker Durable Object/queue or equivalent durable outbox; A firmware notification cue and acknowledgement primitive


## What it asked for

_Nothing._
## Its own summary

Recorded two new items: (1) blocker-aware delegated tasks that remain quietly monitored across Mac/browser/relay and interrupt the owner only for a meaningful blocker or completion, with resumable clarification; (2) a durable, priority-aware pendant notification inbox with retry, expiry, deduplication, acknowledgement, and spoken-safe summaries. The owner cannot reliably have either today.

**Biggest unknown:** The exact pendant firmware wake/connect and notification primitives, plus the durable event schema shared by mac-planner, mac-vision, and browser-extension, still need to be specified and implemented. No further discovery was performed this round.

