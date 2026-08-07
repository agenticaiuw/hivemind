# Harness derivation — mac-terminal — round 85

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac execution observability and readiness** — Live /ops/snapshot shows FULL_CONTROL_MODE and planner enabled, but browser extension is offline with 7 pending commands; accessibility and screen-recording permissions are missing, agent ready=false despite requiredMissing=[]; relay and Mac bridge are reachable. Live /journal reports 120 retained jobs, 146 actions, 77 writes, 16 failures, 0 undoable, and 112 unattributed-tier actions. /routing shows 57% of requests already off planner but planner requests average ~9.7k tokens.
  - evidence: GET /ops/snapshot HTTP 200; GET /journal HTTP 200; GET /routing HTTP 200 on 2026-08-07T12:49Z.

## Capabilities it proposed

### "When I ask you to do something involving my browser, just proceed: use the fastest available route, automatically fall back for public pages when Safari is offline, queue private-page work until the bridge returns, and tell me on the pendant exactly what ran, what was deferred, and why."
- **useful because:** Today a dead extension can burn 45 seconds per navigation and produce repeated opaque failures. This would make the hive resilient: public work still completes through the relay, private work is preserved rather than retried blindly, and the owner gets a concise spoken status instead of discovering failure later.
- **path:** pendant → relay → mac-planner → browser-harness → dashboard
- **model tier:** Deterministic health/preflight and routing first; background model for summarizing deferred/completed work; realtime only for the immediate spoken acknowledgement.
- **latency:** Under 1 second for health classification and pendant acknowledgement; public fallback should begin within 3 seconds; private work waits for a heartbeat or configurable deadline without repeated 45-second attempts.
- **cost:** Negligible for health checks and routing; roughly 1 background-model call per multi-step task (about 2k–4k prompt tokens) only when a human summary is needed. Avoids the current repeated planner calls and browser timeout waste.
- **security:** Never send authenticated/private URLs, DOM, or cookies to the public fallback. Classify a task before routing; private sessions remain on the local bridge. Persist only task metadata and failure reason. Any eventual browser mutation keeps the existing owner policy and receipts; this proposal adds no blocking gate.
- **missing:** A single availability classifier with freshness TTL for Mac bridge, browser extension, and relay browser backends; A resumable task state machine that distinguishes public fallback-safe steps from private steps and records the exact deferred checkpoint; A circuit breaker/backoff keyed by extension/session so an offline bridge cannot consume repeated 45-second attempts; A pendant/relay notification path for completion, deferral, and recovery events

### "When several background tasks finish or fail while I am away, give me one interruption at the right moment that bundles only the decisions I need, lets me ask for any receipt, and otherwise leaves everything quietly queued."
- **useful because:** Today each surface can create its own job, failure, audio, or browser update, but there is no shared attention budget. The owner should not receive five separate pendant alerts for one stalled workflow, nor miss a meaningful failure because it was buried in Mac logs.
- **path:** relay → pendant → mac-planner → browser-harness → dashboard
- **model tier:** Deterministic event aggregation, deduplication, urgency scoring, and quiet-hours handling; background model only to compress a multi-job digest; realtime only when the owner opens the interruption.
- **latency:** Aggregate events within 1 second; deliver immediately only for configured urgent failures, otherwise wait for the next attention window or explicit pendant request. Digest generation under 3 seconds.
- **cost:** Near-zero for aggregation; approximately one background call per digest, typically 1k–3k prompt tokens. No planner call for ordinary receipts.
- **security:** Digest content must inherit each artifact's residency label and avoid putting private page text into relay notifications or durable audio unless permitted. Never infer urgency from sensitive content without a local policy decision. The owner can inspect the underlying receipt before any follow-up action.
- **missing:** A shared attention ledger with deduplication keys, urgency, quiet hours, and delivery state; Cross-surface event emission from Mac jobs, browser commands, relay jobs, and audio completion; A pendant acknowledgement/query protocol that marks a digest read without losing individual receipts; Owner-configurable urgency rules and escalation limits


## Changes it proposed to its own stack

### `mac-harness` — Add a durable execution-ledger join that attaches routing receipt, planner trace, parent job, action receipt, evidence capsule IDs, and undoability to one immutable record. Backfill links when a job finishes, and expose filters for model tier, command type, failure class, latency, and whether the action was a write. Treat missing joins explicitly as 'unattributed' rather than silently dropping them.
- **owner gets:** The Mac currently reports 146 actions and 77 writes, but 112 actions are unattributed to a model tier; the owner cannot reliably answer which agent spent time, what actually ran, or why a failure happened. A single human-readable history would make the pendant's 'what happened?' answer trustworthy and reveal waste such as repeated browser attempts.
- effort: Medium: define a stable executionId and correlation propagation through planner/router/executor, add a small append-only ledger plus a repair pass over recent jobs, then add dashboard and relay summary queries.  ·  risk: Correlation bugs could duplicate or misjoin records. Preserve existing job and receipt files as source of truth, make the ledger append-only/idempotent, and mark uncertain joins rather than guessing. No action behavior or owner policy changes.
- cost: No model cost; small local JSONL/SQLite storage and negligible CPU. Dashboard queries may add a few milliseconds.  ·  latency: Near-zero on execution if linkage is emitted in-memory; asynchronous persistence after receipt completion.
- security: Keep command text, URLs, and evidence local by default; relay receives only redacted summaries unless explicitly requested. This is observability, not a new permission gate.
- depends on: Existing action receipts and /jobs/:jobId/receipts; Existing /routing and routingStats records; Existing /journal and /journal/:jobId; A stable correlation ID propagated by mac-planner/mac-vision/browser actions

### `browser-harness` — Add lease/TTL semantics and supersession for browser commands: every queued command records session, prerequisite health snapshot, expiry, and supersedes key; when the extension is offline, coalesce repeated idempotent probes, stop dispatching stale work, and emit one deferred receipt. On heartbeat, revalidate the session before releasing only still-valid commands.
- **owner gets:** The live Mac has 7 pending browser commands while offline, and repeated browser navigation attempts have all consumed roughly 45 seconds before failing. This prevents stale clicks or navigations from replaying after the owner has moved on, while preserving useful work and making recovery quick when Safari returns.
- effort: Small-to-medium: extend browser command records, add queue sweeper and dedupe index, validate session/URL before dispatch, and surface deferred/expired states in job receipts.  ·  risk: A legitimate long-running task could expire or a coalescing key could merge commands that were intentionally distinct. Default TTLs by action type, never coalesce writes, and keep an explicit force/continue path for the planner.
- cost: Negligible storage/CPU; saves browser round trips and planner retries. No additional model calls.  ·  latency: Immediate offline classification; recovery dispatch starts on the first healthy heartbeat instead of waiting for timeout.
- security: Improves safety by preventing stale authenticated actions from replaying. Preserve session affinity and do not broaden data access.
- depends on: Existing browser command queue and /browser/poll; GET /browser/status and POST /browser/heartbeat; Existing request IDs/idempotency keys and action receipts; The execution-ledger correlation proposed above

### `context` — Add end-to-end data-residency and sensitivity labels to every cross-surface artifact, not just raw browser pages: classify source fields and derived summaries as device-local, relay-safe, or owner-approved-to-share; propagate the label through Mac jobs, browser evidence capsules, relay notifications, audio queues, and pendant speech. The relay should receive a redacted event or a cryptographic reference when the source is local-only, while the Mac can still perform the full private computation.
- **owner gets:** The owner should be able to ask the pendant for a spoken answer about private browser, Mail, or Mac data without having to wonder whether the underlying content or an audio copy left the Mac. Today there is no consistent guarantee across the Mac agent, browser bridge, relay, and durable audio path; this would make private cross-device assistance trustworthy while retaining the hive's reach.
- effort: Large: define a small label taxonomy and provenance envelope, add propagation and redaction at every serialization boundary, encrypt/localize private artifacts, and expose a per-job residency explanation in the dashboard and completion receipt.  ·  risk: Incorrect classification could leak sensitive content or unnecessarily prevent useful delivery. Default unknown data to local-only, preserve source provenance, make redaction deterministic and testable, and allow the owner to explicitly promote a specific artifact. This is a data-handling safeguard, not an action-approval gate.
- cost: No additional model calls for deterministic labels and redaction; modest local storage and relay metadata overhead. Summaries may require one extra background pass when redaction is semantic rather than structural.  ·  latency: Usually under 100 ms for labels; semantic redaction may add roughly 1–3 seconds. Private Mac computation remains local and does not wait on relay upload.
- security: Substantially reduces accidental exfiltration through relay logs, durable audio, browser evidence, and spoken notifications. Requires encryption at rest and strict rejection of unlabeled cross-surface payloads.
- depends on: Mac job and action receipts; Browser evidence capsules and authenticated session metadata; Relay persistent state and durable audio paths; Pendant notification/speech delivery; A shared provenance envelope carried across planner, Mac, browser, and relay


## What it asked for

_Nothing._
