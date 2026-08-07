# Harness derivation — faculty-perception — round 81

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-registry** — At 2026-08-07T13:17Z, home-macbook-bridge is online; home-chrome is offline with no tab/window and 7 pending browser commands; cloudflare-contract-test is offline. No registered pendant appears.
  - evidence: discover:devices live response; GET /browser/status at 13:17Z; GET /ops/status relay payload
- **mac-input-reachability** — At 2026-08-07T13:17Z, AI Pendant Agent can observe apps but cannot reach UI input: Accessibility trusted=false, screenRecording=false, inputReachability=failed, uiActionsWillReachTheScreen=false. AppleScript automation grants are present.
  - evidence: GET /observe live response observedAt 2026-08-07T13:17:07Z and GET /ops/status
- **relay-state** — At 2026-08-07T13:17Z, relay is configured and reachable, reports mac bridge online, and supports pendant pipeline telemetry, speech, persistent state, and durable audio; this is service capability, not evidence of a connected pendant.
  - evidence: GET /ops/status live relay payload

## Capabilities it proposed

### "“I’m back—tell me exactly what was happening on my computer and let me resume from the pendant without reopening everything.”"
- **useful because:** Today the owner has fragmented state: Mac jobs, browser tabs, relay pipeline events, approvals, and audio are separate, and a disconnected browser or pendant leaves uncertainty about what was merely planned versus actually completed. This capability would provide a compact, spoken, evidence-linked handoff after interruption: current task, last confirmed effect, blocked dependency, pending approval, and one safe resume option. It is not a generic job-status query; it reconstructs a cross-surface interrupted session and preserves the owner’s place.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use the realtime model only to understand the short spoken resume request and speak the result. Use a cheaper background planner to reconcile event logs, browser state, Mac jobs, receipts, and relay delivery state; use deterministic code for ordering and confirmation status.
- **latency:** Spoken acknowledgement under 1 second from the pendant; evidence-backed handoff in 2–5 seconds when Mac and browser are reachable. If a surface is unavailable, return a partial handoff immediately with explicit source age rather than waiting indefinitely.
- **cost:** Approximately $0.01–$0.05 per handoff depending on event volume; most cost is the background reconciliation model and optional speech rendering, not realtime conversation.
- **security:** The handoff may contain private page titles, messages, calendar data, and action details, so relay payloads must use the existing paired/authenticated channel and minimize fields. Never replay an action merely because it was pending. Require explicit confirmation before resuming any write or irreversible step; report unavailable surfaces instead of guessing.
- **missing:** A durable interrupted-session record joining relay pipeline IDs, Mac job IDs, browser session/tab IDs, approvals, receipts, and audio delivery acknowledgements; A typed event reducer that distinguishes planned, started, completed, failed, blocked, expired, and delivered states across surfaces; A resume token bound to the owner’s session and task, with stale-state expiry and a deterministic safe-next-step preview; A connected pendant and online browser bridge for end-to-end verification; current hardware/device absence means this can only be implemented and simulated today

### "“Watch the assumptions behind this plan and tell me the moment one stops being true.”"
- **useful because:** A normal page watch reports changed pages; it does not know which changes invalidate the owner’s active plan. This capability would turn a spoken goal into a dependency set—meeting time, travel status, document version, account state, browser availability, or required approval—and alert only when a dependency crosses a meaningful threshold. The owner gets an early warning and a revised safe option instead of discovering at the last step that the plan was impossible.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheaper background model to extract and periodically reassess dependencies; use deterministic comparisons and schedules for most checks. Use realtime only for a short alert and follow-up conversation when the owner responds.
- **latency:** Dependency checks can run on schedules or event triggers. Deliver an alert within 30 seconds of a source event when online; queue it durably for the next pendant connection if offline.
- **cost:** Roughly $0.005–$0.03 per active plan per day; deterministic calendar/job/status checks dominate, with model calls only when semantic interpretation is needed.
- **security:** Dependency definitions can expose private calendar, mail, work, and authenticated-page context. Keep raw content on the Mac/browser where possible and send only normalized facts and evidence hashes to the relay. Alerts must never execute a replacement action; require confirmation for any changed plan that writes or sends.
- **missing:** A first-class active-plan dependency graph with fact sources, thresholds, expiry, and owner-visible explanations; Event subscriptions from Calendar/Mail/browser watches/job receipts rather than periodic page polling alone; A semantic invalidation evaluator that links a changed fact to a specific planned step and produces alternatives; Pendant notification and acknowledgement delivery with durable deduplication


## Changes it proposed to its own stack

### `integration` — Add a live reachability lease and stale-command quarantine across relay, Mac UI, browser bridge, and pendant delivery. Before enqueueing or reporting any action, snapshot each required surface (bridge heartbeat, /observe inputReachability, /browser/status, and pendant registry). Attach observedAt, a short lease expiry, and required-surface set to the job. If a surface is offline or its lease expires, hold the job as blocked (never execute later silently), collapse duplicate browser commands, and emit a typed blocked receipt naming the missing surface and the owner-facing recovery (for example enable the extension, grant Accessibility, or connect the pendant). Revalidate the lease immediately before execution and before saying completed.
- **owner gets:** The owner would stop hearing that something was done when the browser was offline, UI input was actually rejected, or no pendant existed. In the current live state there are already 7 pending browser commands while the extension is offline, and UI action receipts cannot be trusted; quarantine makes failure immediate, explicit, and recoverable instead of stale work surprising them later.
- effort: Medium: shared job schema, relay/Mac status adapter, browser queue migration, and receipt/dashboard states; preserve existing receipts and provide a one-time migration of pending commands to blocked.  ·  risk: A transient heartbeat loss could delay legitimate work; use short leases only for UI/browser/pendant actions, allow read-only AppleScript/server work independently, and provide explicit retry after a fresh heartbeat. Migration must not drop commands or mark them succeeded.
- cost: Negligible API cost; one small status check per action and fewer wasted model/browser retries. Storage adds a few hundred bytes of metadata per job.  ·  latency: Adds roughly 50–200 ms for local status checks; avoids 45-second browser timeouts observed in failed jobs.
- security: Improves safety by preventing execution after an owner’s context changed and by making missing permissions visible; do not include page contents or secrets in blocked receipts.
- depends on: Implement the claimability ladder / provenance fields proposed by faculty-judgement; Existing GET /ops/status and GET /observe reachability telemetry; Existing GET /browser/status and browser command queue; Existing GET /jobs, GET /jobs/:jobId/receipts, and POST /pipeline/events for typed state propagation; A live pendant registry and delivery acknowledgements when a pendant is connected


## What it asked for

_Nothing._
