# Harness derivation — mac-planner — round 125

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask you to use a private browser page, recover the connection if needed, do the read-only work, and tell me clearly if the browser is unavailable instead of silently failing."
- **useful because:** Today nine browser commands are stranded because the extension is offline, while the Mac agent reports success-like jobs that ultimately fail. A worn-device request should either complete against the owner's authenticated tab or produce an honest, spoken recovery status and a durable retry—not a dead end.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the cheap background model for bridge health checks, queue reconciliation, and retry scheduling; use realtime only for the owner's live request and one-sentence status; use no model for heartbeat/extension restart logic.
- **latency:** Heartbeat/status decision under 1 s; AppleScript/browser-bridge recovery under 5 s; read-only extraction after the tab responds within the existing 30–45 s bound. If not recovered, speak a short failure and keep a durable retry capsule.
- **cost:** Near-zero for health/retry; one normal extraction model call only when page content needs interpretation. Dominant cost is page extraction context, not watchdog logic.
- **security:** Read-only by default; preserve authenticated content on the Mac/browser and send only the requested extracted fields to relay. Never replay queued writes automatically. Any pending submit/send/delete remains paused for explicit owner review.
- **missing:** A browser-bridge watchdog/recovery worker that can distinguish offline, stale command, and page timeout; An idempotent queue drain with per-command TTL and read-only/write classification; A pendant/relay notification capsule for retry state and exact failure reason; An implementation of the granted mac_readonly_inspect schema (currently schema-only) for verifying Safari/extension state

### "If a task on my Mac gets stuck on a choice or an expired page, ask me on the pendant, let me answer there, and resume from the exact blocked step without starting over or losing the work already done."
- **useful because:** Today a desktop task either fails when the owner walks away or requires them to return to the Mac and explain everything again. This would make the pendant a true remote control for stalled desktop work: the owner can resolve a choice while moving, while the Mac preserves completed steps and the browser keeps its authenticated session.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime tier only to conduct the short clarification exchange and acknowledge the answer. Use a cheaper background model to serialize the paused plan, validate that the answer resolves the ambiguity, and resume/reconcile the remaining steps.
- **latency:** Detect and announce a blocked step within 2 seconds; deliver the clarification prompt to the pendant within 3 seconds; resume within 5 seconds after the answer. If the link is down, persist the question and continue when connectivity returns.
- **cost:** Usually one short realtime turn plus inexpensive state validation; the dominant cost is only the original task planning, not the pause/resume cycle.
- **security:** The prompt must show the exact app, tab, and proposed effect without exposing unrelated page content. Answers from the pendant may authorize only the named blocked step; never broaden them into permission for later destructive actions. Expired or changed pages require revalidation before resume.
- **missing:** A durable pausable execution state machine with a resumable step cursor and completed-step receipts; A relay-to-Mac clarification channel carrying question IDs, bounded answers, expiry, and cancellation; A pendant UI/audio interaction for selecting among a few choices or saying a bounded answer while offline-capable; Browser session revalidation and tab-affinity checks before resuming a paused step; Dashboard visibility for paused, awaiting-owner, resumed, expired, and cancelled states

### "When a Mac or browser task is ready to send, buy, delete, or submit, read me the exact change on the pendant and let me approve or reject it there, even if I am not looking at the Mac."
- **useful because:** The owner wants maximum automation but explicitly does not want accidental sends, deletions, or purchases. Today the Mac path has no live approval gate, and a browser action can be stranded or misreported. A pendant-mediated approval would preserve the owner's control without requiring them to sit at the screen.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheap background model to render a structured, redacted change summary and validate the proposed action. Use realtime only for the brief spoken readout and yes/no answer. The executor must enforce the signed decision without asking a model to reinterpret it.
- **latency:** Generate the approval card in under 2 seconds; spoken approval round trip under 4 seconds; expire unanswered approvals after a configurable window and leave the task paused.
- **cost:** Low: one compact summarization call for complex changes; simple structured actions need no model. Network/audio transport dominates latency, not inference.
- **security:** Approval must be bound to a single job, exact action hash, target tab/app, and short expiry; replayed or altered approvals must fail closed. Redact secrets and unrelated page text. Never treat ambient speech or an unpaired pendant as approval. Owner policy requires confirmation for sending mail, deleting files, and buying.
- **missing:** A cryptographically bound approval token generated by the pendant/relay and verified by the Mac executor; A structured before/after diff format for browser, file, mail, and purchase actions; A real approval gate in the FULL_CONTROL execution path (currently action-risk classification is dead code); A pendant audio/UI protocol for clear affirmative, rejection, and correction responses; Receipt evidence linking the approved hash to the exact executed action


## Changes it proposed to its own stack

### `integration` — Add an ingress validator and causal state machine for Mac jobs. Reject empty action lists before creating a job; attach one correlation ID from pendant request through /execute, browser command, receipt, and spoken response; record terminal reason codes (offline, stale, timeout, permission, no-op) and reconcile orphaned browser commands into the same timeline. Expose a compact incident view in the dashboard and a machine-readable status endpoint.
- **owner gets:** The owner currently sees failed jobs with empty commands and nine browser commands stranded separately from their originating requests. This would make the system tell one truthful story—what was requested, what device was unavailable, whether anything changed, and whether retry is safe—rather than making the owner debug the harness.
- effort: Medium: shared request envelope, ingress validation, job/command linkage, reason-code taxonomy, dashboard grouping, and regression fixtures for offline/timeout/retry paths.  ·  risk: A stricter validator could reject malformed plans that used to limp through; preserve a compatibility path for legacy callers and add tests. Correlation metadata must never include page contents or secrets.
- cost: Negligible API/storage overhead; saves expensive model retries by eliminating no-op and duplicate execution attempts.  ·  latency: Sub-millisecond validation; no added latency to valid actions. Dashboard aggregation can be asynchronous.
- security: Improves auditability without adding access. Keep URLs/DOM snippets redacted by default and use opaque IDs in relay speech.
- depends on: Browser queue and receipt linkage from chg-14accc01 should be reused rather than replaced; The existing /jobs, /jobs/:jobId/receipts, /journal, and /browser/result/:commandId data stores need a shared correlation field; mac_readonly_inspect implementation remains desirable for verifying local recovery, but this change does not depend on it


## What it asked for

_Nothing._
## Its own summary

Recorded two new cross-surface capabilities: resumable Mac/browser work that asks bounded clarification questions on the pendant and resumes at the blocked step; and pendant-mediated, action-hash-bound approval for sends, deletes, purchases, and submissions. Both require new state/protocol/enforcement work not present today.

**Biggest unknown:** Whether the owner prefers spoken-only approval or a small pendant UI for reviewing structured before/after diffs.

