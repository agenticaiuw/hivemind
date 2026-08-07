# Harness derivation — mac-terminal — round 80

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent health and recovery gap** — At 2026-08-07T12:36Z the Mac agent is full-control and relay-reachable, but computer-use loop is disabled; vision model configured yet Screen Recording is not granted and Accessibility is untrusted. Browser bridge is offline with 5 pending commands. Journal has 120 retained jobs, 147 actions, 14 failures, 0 undoable, and 112 actions without model-tier attribution.
  - evidence: GET /ops/snapshot and GET /journal returned HTTP 200 with these fields.

## Capabilities it proposed

### "“Continue the thing that failed when my browser was offline.”"
- **useful because:** Today relay_job_status can report a failure but cannot turn a transient offline-browser failure into a resumed task. This lets the owner recover hands-free after reopening the browser, without repeating the whole instruction or guessing which step is safe to retry.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Background/cheap model for job classification and resume planning; realtime only for the short spoken acknowledgement and final result.
- **latency:** Immediate acknowledgement under 1 second; health check under 2 seconds; execution continues asynchronously and speaks only on completion or a non-recoverable diagnosis.
- **cost:** Usually one cheap classification call plus local/relay calls; no vision or realtime model unless the failed step specifically needs computer-use.
- **security:** Resume only the failed idempotent action using its stored idempotency key and prior receipt; never replay completed writes. Keep page text and shell arguments out of the spoken acknowledgement unless needed.
- **missing:** A resumable-job endpoint that accepts a job id or natural-language reference and starts from the failed action boundary; Preflight/failure classification and bounded retry described in the proposed Mac harness change; Browser heartbeat/online transition wake-up that releases queued resumptions

### "“Why did that take so long, and what exactly happened on my Mac?”"
- **useful because:** The owner cannot currently get a trustworthy end-to-end explanation of a task: model planning, relay transit, Mac execution, and browser availability are recorded in separate places, and most actions have no model-tier attribution. This gives a concise spoken postmortem with a linked, inspectable timeline rather than another generic failure message.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic aggregation first; use a cheap background model only to turn the structured timeline into a short explanation. Realtime is reserved for the spoken follow-up.
- **latency:** Under 2 seconds for the structured status and under 5 seconds for the optional spoken summary; no re-execution of the task.
- **cost:** Normally no model call; otherwise one small background completion over redacted events. Storage is a few KB per job for correlation metadata.
- **security:** Keep shell arguments, tokens, page contents, and prompt text out of the owner-facing summary by default. Show app/domain names and failure classes, with a dashboard drill-down requiring local authentication. Preserve unknown attribution instead of guessing.
- **missing:** A single immutable correlation ID propagated from pendant request through relay, planner, Mac job, browser command, and action receipts; A read-only timeline joiner that combines /routing, /journal/:jobId, job receipts, and browser heartbeat state; A redaction-and-explanation formatter exposed to the pendant and dashboard; Backfill or explicit unknown markers for the 112 currently unattributed actions

### "“Make the Mac ready so you can use my browser and see the screen.”"
- **useful because:** Today the owner receives opaque failures when Accessibility, Screen Recording, or the browser bridge is unavailable. They cannot ask the pendant to diagnose the complete readiness chain, open the right Mac settings, wake the bridge, verify each prerequisite, and tell them exactly what remains.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic health checks and typed Mac actions; background model only for interpreting an unfamiliar permission dialog. No realtime planning is needed beyond the spoken acknowledgement.
- **latency:** Initial diagnosis under 2 seconds; opening settings and bridge recovery within 10 seconds; wait for owner-granted permissions and recheck automatically when they return.
- **cost:** Mostly local checks and typed actions, with negligible model cost. A small persistent readiness record avoids repeating checks on every request.
- **security:** The system may open settings but must not claim permissions were granted until the OS and extension report them. Never transmit screen pixels merely to diagnose readiness. Require explicit local OS consent where macOS requires it.
- **missing:** A readiness state machine spanning Accessibility, Screen Recording, browser-extension heartbeat, and vision-loop availability; Typed deep links/open-and-verify actions for the relevant macOS Privacy & Security panes; A browser-extension wake/reconnect handshake and owner-facing pending-permission state; Pendant notification when readiness changes from blocked to usable


## Changes it proposed to its own stack

### `mac-harness` — Add an execution preflight and adaptive recovery layer that runs before queued Mac/browser work: snapshot bridge/browser/permission health, classify the likely failure (offline extension, missing Accessibility/Screen Recording, timeout, transient app error), attach the preflight and model-tier receipt to the job, and either (a) immediately retry only transient failures with bounded backoff, or (b) return a concrete owner-facing repair instruction and keep the job resumable rather than spending repeated 45-second attempts. Do not block or gate actions; this is observability and recovery only.
- **owner gets:** The pendant can tell the owner why something failed and recover automatically instead of silently burning time on impossible browser actions. Today the agent has 5 queued browser commands while the extension is offline, and recent failures take ~45 seconds each; the owner should get one actionable status and a continuation when Chrome/Safari returns.
- effort: Medium: shared preflight module, failure classifier, resumable job state, and receipt fields across local-agent and relay job status.  ·  risk: A bad classifier could retry a non-transient action or misdiagnose a permission issue. Bound retries, preserve idempotency keys, and expose the exact raw failure and preflight snapshot in the journal; resume only from the failed action boundary.
- cost: Small storage and one cheap local status check per job; reduces wasted realtime/model calls and repeated browser polling.  ·  latency: Adds tens of milliseconds for local preflight, but avoids 45-second offline waits; retries are background and bounded.
- security: Receipts must redact command arguments and page content while retaining health flags. No new privileges or restrictions.
- depends on: Durable job receipts already present (chg-5fc73ce3); Authenticated /ops/snapshot, /journal, and browser status observability; Idempotency-aware job runner and relay_job_status continuation

### `integration` — Propagate a single request/job correlation id and routing receipt from planner through relay → Mac job creation → every action receipt, with a small backfill reconciler for existing jobs. Expose tier, escalation, model, latency, and token estimate on /journal/:jobId and relay_job_status; mark genuinely external jobs as unknown rather than leaving most actions unattributed.
- **owner gets:** When a task is slow or fails, the owner gets an honest explanation of whether the delay came from the model, relay, Mac execution, or a disconnected browser. The live router already reports useful tier data (57% of recent requests avoided planner and one background request escalated), but 112 of 147 retained actions currently have no tier attribution.
- effort: Medium: request-id propagation across relay and local-agent schemas, receipt join, and a read-only migration for retained jobs.  ·  risk: Incorrect joins could report the wrong model or expose internal prompts. Use immutable IDs, confidence/unknown states, and never include prompt text in receipts.
- cost: Negligible storage; enables cheaper routing decisions and avoids redundant diagnostic model calls.  ·  latency: Near-zero metadata overhead; reconciliation can run asynchronously.
- security: Receipts need model metadata only, with argument/page-content redaction preserved.
- depends on: Existing /routing statistics; Existing action receipts and journal; Relay job records and relay_job_status


## What it asked for

_Nothing._
## Its own summary

Round 80 established live Mac-agent facts: relay and agent are healthy, but computer-use is disabled because Screen Recording is missing and Accessibility is untrusted; browser bridge is offline with 5 pending commands. The retained journal has 120 jobs/147 actions, 14 failures, 0 undoable actions, and 112 actions without tier attribution. I recorded these findings and proposed (1) non-blocking preflight, failure classification, bounded retry/resume, (2) a spoken “continue the failed task” flow, and (3) end-to-end routing/job correlation so failures and cost are attributable. I also informed mac-planner.

**Biggest unknown:** The granted read-only diagnostics tool still has no implementation, so I cannot independently verify battery/network/process details beyond the authenticated agent snapshot. To make browser/vision recovery real, the owner or installer still needs to grant Screen Recording and Accessibility and bring the browser extension online; no further permission request is needed from me.

