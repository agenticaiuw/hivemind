# Harness derivation — mac-planner — round 108

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“The browser task failed while I was away—resume it safely and tell me exactly what ran.”"
- **useful because:** Today a disconnected bridge leaves seven pending commands and stale authenticated sessions; a reconnect can otherwise replay an old click/type or make the owner wait 45 seconds before learning it failed. This capability turns an interrupted multi-node task into a truthful recovery: reattach only a live tab/session, reconcile each command by idempotency receipt, continue only unapplied steps, and leave a concise result on the Mac/pendant.
- **path:** browser-extension → mac-planner → relay-realtime → unified
- **model tier:** Background/cheaper model for lease reconciliation, receipt matching, and retry classification; realtime only to tell the owner the recovery status on the pendant.
- **latency:** Detect disconnect immediately; reconcile in under 2 seconds after bridge heartbeat returns; retry transient reads with bounded backoff. Never block the voice turn on a 45-second browser wait.
- **cost:** Usually <$0.01 per recovery; dominated by one short planner/background classification call. No model call for straightforward receipt and TTL checks.
- **security:** Authenticated URLs, tab identifiers, and extracted snippets remain on the owner's Mac/relay path and must not be sent to public Browser Run. Expired commands are marked abandoned, not replayed. Session reattachment requires the same browser profile plus a fresh bridge lease; mutation steps use existing idempotency keys and are reported with before/after receipts. Owner policy permits maximum access, so this is observability and replay prevention rather than a new approval gate.
- **missing:** Browser command leases with explicit expiry and heartbeat, plus an abandoned state distinct from failed; Reconnect reconciliation endpoint that compares pending command ids against browser receipts and marks stale sessions detached; Durable per-step job state/result stream so the planner can resume after process restart instead of waiting synchronously

### "“I got interrupted—save where I am now, and when I’m back tell me exactly what to resume.”"
- **useful because:** A wearable can notice the interruption while the Mac has the real work state. One coordinated handoff would capture the foreground app, open browser tabs, relevant calendar/mail context, and a short owner-spoken marker, then later restore the thread without reopening or changing anything. This is different from a morning brief or meeting preparation: it preserves an in-progress cognitive state at the moment it breaks.
- **path:** relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Cheaper background model compiles and ranks the captured state; realtime model only handles the pendant's brief capture/resume exchange.
- **latency:** Capture acknowledgement under 1 second; read-only Mac/browser snapshot under 3 seconds; resume card under 10 seconds after the owner asks.
- **cost:** <$0.02 per handoff, mostly one compact summarization call; inspection and source reads are local/low cost.
- **security:** Capture is explicitly user-triggered by the pendant button or phrase. Store only redacted snippets and metadata by default, with a short TTL; never record microphone continuously. Browser private-page text stays on the Mac/relay memory path, with URLs and source timestamps in the capsule. Resume is read-only by default; any action still goes through the existing Mac executor and its owner-selected maximum-access policy.
- **missing:** A pendant-triggered handoff event that asks the Mac for a bounded snapshot without opening a microphone stream; A typed context capsule schema linking foreground app, browser tab ids, calendar/mail source timestamps, and owner marker with TTL; A resume endpoint that retrieves one capsule and renders a concise spoken card plus optional Mac reopen actions

### "“I was disconnected—what changed everywhere since I last heard from you?”"
- **useful because:** Today the owner must separately ask about Mac jobs, browser failures, messages, and pendant connectivity, and can miss changes that occurred while the wearable or Mac was unreachable. The owner should receive one causally ordered delta across the hive: completed and failed desktop actions, browser/session changes, queued work, and only newly relevant personal notifications, with duplicates removed and each item sourced. This is not a morning brief or a job-status lookup; it is a connection-aware catch-up from the owner's last acknowledged point in time.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** Use a cheap background model to cluster and rank the event delta; use the realtime tier only to answer the spoken request and read the short result.
- **latency:** Return an initial five-item delta within 3 seconds, then stream additional evidence if needed. Local event collection must not wait on an offline surface.
- **cost:** Under $0.02 per catch-up, mostly one compact ranking call; event cursors, deduplication, and receipt joins are deterministic.
- **security:** Private browser contents and mail/calendar details stay on the Mac/relay trusted path; the model receives only selected snippets and provenance. Persist acknowledgements and event hashes, not full sensitive payloads, with short retention. Clearly label events observed before versus after a disconnect, and never infer that an action succeeded merely because its command was queued.
- **missing:** A durable cross-surface event ledger with monotonic per-surface cursors, causal/request IDs, timestamps, sensitivity labels, and retention policies; A per-owner acknowledgement cursor that survives pendant, relay, Mac, and browser reconnects; Adapters that turn Mac receipts, browser lease/session events, relay jobs, and bounded Mail/Calendar reads into a common event shape; A deterministic deduplication and relevance pass before the compact model summary

### "“If the Mac, browser, and relay disagree about whether it happened, tell me what is actually known and what I should verify.”"
- **useful because:** Distributed automation can currently produce a successful-looking queued job, a timed-out browser command, and a stale tab record at the same time. The owner needs a contradiction report rather than a confident but false completion message: distinguish observed effects from attempted effects, identify the strongest evidence, and give one bounded verification step on the correct surface.
- **path:** faculty-perception → faculty-judgement → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Cheap background reconciliation for receipts, timestamps, and tab state; realtime only for the short spoken explanation. Escalate to the expensive tier only when evidence genuinely conflicts or the owner asks for interpretation.
- **latency:** Deterministic evidence join under 2 seconds; spoken answer under 5 seconds; verification can continue asynchronously without blocking the owner.
- **cost:** Usually below $0.01 because most cases are receipt comparisons; model cost occurs only for ambiguous conflicts.
- **security:** Do not treat queued, dispatched, or locally acknowledged events as proof of an external effect. Private page contents remain local to the authenticated browser path. Verification must be read-only unless the owner separately asks for an action; retain evidence hashes and source timestamps with short TTL.
- **missing:** A common evidence ontology separating intent, dispatch, acknowledgement, observed effect, and confirmed external state; Cross-surface correlation IDs propagated from pendant utterance through relay job, Mac action receipt, and browser command; A contradiction detector that refuses to collapse stale or timed-out records into success; A read-only verification planner that selects the least-invasive surface and explains its evidence


## Changes it proposed to its own stack

### `browser-harness` — Replace browserBridge's single 45-second waitForBrowserResult with a leased, event-driven job state machine. On dispatch, persist commandId/action idempotency key/session id and a short lease; emit queued/dispatched/acknowledged/completed/abandoned events; renew the lease on extension heartbeat; on reconnect reconcile command receipts before retrying. Expire commands without a live lease and mark sessions detached when lastSeenAt is older than the lease window. Expose non-blocking GET job progress and a bounded stream for the planner.
- **owner gets:** A browser action will stop hanging for 45 seconds and then possibly replay after the owner has moved on. The owner gets immediate, truthful progress and can safely resume only unapplied work when the bridge returns.
- effort: Medium: browserBridge queue/state persistence, heartbeat endpoint, reconciliation tests across restart and reconnect, and planner polling/stream wiring.  ·  risk: A lease that is too short could abandon a slow but valid page load; use separate dispatch and execution deadlines and preserve the receipt for late completion. A reconnect race could duplicate a mutation; content-addressed idempotency keys and receipt reconciliation must win before retry. Recovery is to surface abandoned state and require a new explicit resume command.
- cost: Negligible storage and request overhead; one heartbeat per active browser job. Reduces wasted model calls and repeated 45-second waits.  ·  latency: Immediate queued/failed status; read actions resume within one heartbeat after reconnect. Slow pages still honor a bounded execution deadline.
- security: Improves safety by preventing stale authenticated commands from executing after an unattended reconnect. Keep private-page payloads on the Safari bridge; persist only hashes, ids, status, and minimal metadata in relay storage.
- depends on: chg-14accc01's existing request IDs/idempotency keys and typed receipts; chg-16bc5dee's existing backend selection; do not fail over owner-private Safari sessions to public relay; A browser extension heartbeat/reconnect signal


## What it asked for

_Nothing._
