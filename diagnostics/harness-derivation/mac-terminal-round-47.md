# Harness derivation — mac-terminal — round 47

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac readiness and browser dispatch** — The newly granted mac_read_diagnostics schema is still unimplemented. Live /ops/status reports fullControlMode=true but agent ready=false because Accessibility trusted=false and Screen Recording granted=false; browser bridge is offline with 3 pending commands. Two recent browser_navigate jobs each waited about 45 seconds before failing.
  - evidence: GET /ops/status HTTP 200; GET /jobs HTTP 200; mac_read_diagnostics returned 'no implementation yet'.

## Capabilities it proposed

### "When something I asked you to do is blocked because a device, permission, or browser session is unavailable, tell me exactly what is missing, leave a recovery card on my Mac and pendant, and continue automatically when the capability returns—without repeating any irreversible step."
- **useful because:** Today a failed request just becomes a delayed error, even when the underlying problem is temporary. The owner should not need to remember which bridge, permission, or tab to restore, nor resubmit the request. A recovery card makes the failure actionable, while automatic resumption turns the hive into a dependable assistant rather than a collection of one-shot tools.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic local readiness checks and a background model for classifying the failure, extracting the minimal owner-facing explanation, and deciding whether a task step is safely resumable. Reserve realtime only for speaking the immediate alert. The relay persists the paused intent and the Mac/browser surfaces emit recovery events.
- **latency:** Immediate readiness explanation under 1 second when the request is dispatched; recovery-card creation under 3 seconds. Resume in the background on the next healthy heartbeat, with no realtime model call unless the owner asks for details.
- **cost:** Usually near-zero model cost for deterministic checks; roughly $0.001–$0.01 per blocked-task explanation depending on context size. The dominant cost is not inference but durable queue/heartbeat storage and occasional background re-planning after recovery.
- **security:** Recovery state may contain private URLs, app names, and task context, so encrypt or redact it in relay storage and expose only the minimum needed on the pendant. Never persist page text, credentials, or form values in the card. Automatic continuation must be limited to explicitly classified idempotent reads and reversible preparation; irreversible or unknown steps remain paused and require a fresh owner instruction. Every resume, skip, and expiration needs an auditable receipt.
- **missing:** A durable paused-intent record shared by relay and Mac agent, including step-level completion state and an expiration time; A signed, short-TTL readiness event stream for Mac permissions, browser bridge/tab availability, and relay connectivity; A step mutability/idempotency contract that distinguishes safe reads and preparation from irreversible actions; Pendant notification and acknowledgement protocol for recovery cards, including a concise spoken summary and a way to defer or cancel; A resume engine that revalidates preconditions and uses request/idempotency keys so recovery cannot duplicate completed work


## Changes it proposed to its own stack

### `integration` — Add a cross-surface capability preflight and circuit breaker before dispatching Mac/browser jobs. The Mac agent should publish a compact, cached readiness vector (bridge heartbeat age, browser online/tab binding, Accessibility and Screen Recording status, app automation grants, disk/battery/network, queue depth) with a short TTL. The relay/planner consults it before dispatch: fail browser work immediately when the extension is offline instead of waiting ~45 seconds, purge or mark stale pending browser commands with an explicit expiry, and select a declared fallback (Mac shell/public web/pendant-only explanation) when one exists. On recovery heartbeat, retry only idempotent read steps with the original request/idempotency key; never replay mutations automatically. Include the preflight snapshot and decision in the job receipt.
- **owner gets:** The owner gets an immediate, truthful answer instead of a minute-long 'failed' job when Safari or permissions are unavailable. When the bridge comes back, safe reads can resume without repeating a form submission, and every failure explains whether the problem was browser, permission, network, or queue health.
- effort: Moderate: readiness endpoint/schema in local-agent, heartbeat and stale-command sweeper in browser bridge, planner dispatch hook, and receipt/dashboard rendering. Add integration tests for offline->online and mutation retry suppression.  ·  risk: A stale readiness cache could incorrectly choose a fallback or miss a newly recovered bridge; use a short TTL and recheck on dispatch. Incorrect idempotency classification could duplicate a mutation, so default unknown actions to non-retryable. Sweeping commands must preserve active leases and audit every expiration.
- cost: Negligible API cost; reduces wasted planner/realtime calls and 45-second local job waits. Small local CPU/storage cost for heartbeat snapshots and queue metadata.  ·  latency: Adds a local sub-100ms preflight when healthy; cuts known-offline browser failures from ~45s to near-instant. Recovery retries remain background.
- security: Readiness exposes permission and device-health metadata only to the authenticated local agent/relay; do not include URLs, page text, tokens, or command payloads. Receipts should redact sensitive paths and browser data.
- depends on: A typed readiness schema shared by local-agent, browser bridge, relay, and planner; Stable request/idempotency keys and action mutability classification in job receipts; A stale-command lease/expiry field in the browser command queue


## What it asked for

_Nothing._
## Its own summary

Discovered that the granted structured Mac diagnostics tool still has no implementation. Live status shows the agent is not ready (Accessibility and Screen Recording missing), the browser bridge is offline with three pending commands, and browser jobs wait roughly 45 seconds before failing. Proposed a new cross-surface readiness preflight/circuit breaker with short-TTL health vectors, immediate offline failures, stale command expiry, idempotent read-only recovery, mutation retry suppression, and receipt evidence. This improves reliability without adding approval gates or reducing FULL_CONTROL_MODE.

**Biggest unknown:** The exact local-agent job/queue and browser-heartbeat contracts remain unavailable, so implementation would need those schemas plus a working read-only diagnostics implementation.

