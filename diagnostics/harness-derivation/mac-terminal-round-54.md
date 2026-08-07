# Harness derivation — mac-terminal — round 54

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When you run something on my Mac, tell me immediately if it is still running, what it produced, and if it failed, recover or explain the exact next step; I can ask the pendant 'what happened?' later."
- **useful because:** Today the Mac can execute unrestricted shell work, but the owner has no dependable, low-latency witness across relay, pendant, and Mac. A durable execution narrative prevents silent hangs, makes failures actionable, and lets the owner resume after a dropped voice link. It also turns the observed 12 failures and 113 unattributed jobs into useful feedback rather than opaque history.
- **path:** pendant → relay → mac-planner → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Cheap background classifier for heartbeat parsing, failure clustering, and retry eligibility; realtime only for the owner's spoken 'what happened?' query and concise alert. Do not send raw stdout to the expensive tier unless requested.
- **latency:** Mac emits an acknowledgement and heartbeat within 1 second; relay forwards a compact event to the pendant within 300 ms when connected. Failure classification under 2 seconds. Full explanation on demand in 3–8 seconds.
- **cost:** Low: one small event per job heartbeat and one cheap summarization call only on failure or owner query. Dominant cost is the optional realtime explanation; normal execution needs no model call.
- **security:** Shell output may contain secrets, tokens, or private file contents. Keep raw stdout/stderr on the Mac; send only redacted status, exit code, command class, paths hashed or user-approved, and short error fingerprints upstream. Never auto-retry non-idempotent or unknown commands. The owner policy still permits unrestricted execution; this is observability and recovery, not a gate.
- **missing:** A Mac job event stream with monotonic sequence numbers, start/heartbeat/stdout-summary/exit events, and durable retention beyond the 120-job ring; Reliable action-to-model tier attribution (currently 113 jobs are unattributed); A retry contract that records idempotency, backoff, attempt lineage, and why a retry was or was not attempted; Relay-to-pendant resumable subscription so a dropped link can replay only unseen events; Cross-surface redaction and failure taxonomy shared by Mac shell and browser actions

### "Start this task on whichever device is available, keep going if I leave the Mac, and hand it between my pendant, browser, and Mac without losing the exact place or making me repeat anything."
- **useful because:** Today a voice request that spans an authenticated browser session and Mac work is effectively tied to one live connection. If the browser disconnects, the Mac sleeps, or the owner walks away with only the pendant, the task becomes an opaque partial completion. The owner should be able to resume a multi-step task from its last verified state, with the system knowing what was completed rather than restarting or guessing.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use a cheap background workflow state machine for checkpoints, preconditions, and deterministic transitions. Use realtime only when the pendant must ask the owner an ambiguity question or report a meaningful state change. Use the expensive model for visual/browser interpretation only when a page has changed unexpectedly.
- **latency:** A checkpoint is written within 500 ms of each completed step. Reconnection and handoff should resume within 3 seconds. Ambiguity prompts reach the pendant within 1 second when the relay is connected.
- **cost:** Low for ordinary steps because checkpointing is deterministic. The dominant cost is occasional mac-vision/browser interpretation after UI drift; avoid model calls when selectors, hashes, or typed results still validate.
- **security:** Checkpoint records may contain authenticated URLs, document names, or task data. Store secrets and raw page content only on the originating device; the relay carries opaque task IDs, redacted state summaries, and encrypted capability-scoped tokens. Never claim a step completed without a receipt and verified postcondition. External submissions, purchases, messages, or deletion remain explicit owner decisions even though routine continuation is automatic.
- **missing:** A common workflow protocol shared by relay, browser, and Mac with step IDs, verified postconditions, leases, and resumable cursors; Device-local encrypted checkpoint stores with conflict resolution and expiry; A browser capability to expose stable semantic state and submit typed receipts rather than only screenshots or tab status; Mac sleep/disconnect detection plus a lease handoff mechanism; A planner that can compute compensating actions for partial workflows and distinguish safe continuation from an irreversible boundary; Pendant prompts that identify the exact unresolved step without replaying private task contents


## Changes it proposed to its own stack

### `mac-harness` — Add an append-only execution event journal beside the existing job store. Every action (including run_shell) gets a generated traceId, parentTraceId, modelTier, intent hash, start/heartbeat/end timestamps, timeout reason, exit code, stderr fingerprint, bounded stdout summary, retry lineage, and an explicit undoability verdict. Expose GET /journal/stream?since=<cursor> (SSE or long-poll) and GET /journal/:traceId, while retaining raw output locally. Add a cheap deterministic failure classifier and idempotency-aware retry metadata, but do not block or require confirmation.
- **owner gets:** The owner can ask the pendant what a command is doing and receive a trustworthy answer even after the voice session ends. Repeated browser failures and shell failures become diagnosable; successful work can be resumed rather than repeated blindly. Existing receipts record results, but the live journal currently reports 113 unattributed jobs and no undoable actions, so it cannot explain execution history well.
- effort: Medium: event schema and writer in executor/jobTracker, stream endpoint, bounded local retention/rotation, and relay adapter; add integration tests for timeout, crash, reconnect, and concurrent jobs.  ·  risk: Journal growth, accidental sensitive output leakage, and event-order races. Keep raw streams local, cap summaries, redact common secret patterns, use monotonic sequence plus fsync checkpoints, and have the relay discard malformed or out-of-order events. If the stream fails, ordinary execution continues and GET /jobs remains the fallback.
- cost: Negligible model/API cost; modest local disk (for example 25–100 MB rotating journal) and small CPU overhead per event. No hardware cost.  ·  latency: Sub-millisecond to a few milliseconds per event locally; SSE delivery under 300 ms when connected. No added model latency to execution.
- security: Improves auditability without narrowing the owner's deliberate unrestricted shell policy. Raw command/output remains on-device; upstream receives redacted metadata and opt-in excerpts only.
- depends on: Stable local-agent authentication for the new stream; Relay resumable cursor protocol; Shared redaction and failure taxonomy across Mac and browser harnesses

### `dashboard-ux` — Build a trace-oriented 'What ran?' view that groups Mac and browser actions by owner request, displays a compact timeline with live/failed/retried states, and lets the owner filter by failure fingerprint or idempotency key. Selecting a failed step shows the exact redacted error, affected surface, attempt lineage, and a one-tap 'resume from here' request to the planner; never silently replays it.
- **owner gets:** Instead of searching 120 jobs or hearing an incomplete voice response, the owner can see whether a long task is alive, what changed, and where it stopped. The repeated browser_list_tabs and browser_navigate failures become visible patterns rather than repeated mystery failures.
- effort: Medium: consume the proposed journal stream, add grouping and cursor persistence, and wire resume requests to planner with explicit owner invocation.  ·  risk: Grouping can mis-associate parallel actions or expose too much detail. Use trace parentage rather than time proximity, redact by default, and show raw output only after an explicit expand action. Resume must create a new trace linked to the old one.
- cost: No recurring model cost; modest dashboard storage for cursors and rendered metadata.  ·  latency: Live updates within one heartbeat; no effect on action execution.
- security: Reduces accidental leakage by making redacted summaries the default. Authenticated Mac-agent access and per-owner dashboard authorization remain required.
- depends on: Mac execution event journal with trace IDs; Relay cursor/replay support; Planner resume API that carries idempotency and attempt lineage


## What it asked for

_Nothing._
