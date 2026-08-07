# Harness derivation — mac-terminal — round 86

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent live reliability** — At 2026-08-07T12:52Z /ops/status reports fullControlMode and planner enabled, but browser extension offline with 7 pending commands; agent ready=false because Accessibility and Screen Recording permissions are missing. /jobs shows repeated browser_navigate failures (6 runs, 6 failed; ~45s timeout), and /journal totals 16 failed actions, 0 undoable, 112 routing receipts unattributed.
  - evidence: GET /ops/status, GET /jobs, GET /journal, GET /routing returned 200.
- **browser queue pathology** — GET /browser/status now says online=true, but GET /browser/poll returns a command created 2026-08-07T09:11:42Z still processing, claimed at 12:52:47, attempts=8, action type navigate with empty params; seven commands remain pending. This is a poisoned/stale queue item, not merely a disconnected extension.
  - evidence: GET /browser/status and GET /browser/poll at 12:52Z; GET /logs shows repeated 45s browser failures.

## Capabilities it proposed

### "“Keep my browser work reliable: if Safari or the bridge drops, preserve my queued requests, tell me what is stuck, and when it comes back reconcile each request and continue only the safe ones.”"
- **useful because:** Today the owner can receive repeated 45-second browser failures and stale commands can remain processing with empty parameters and eight attempts, while seven requests remain pending. No single Mac, browser, pendant, or relay node can both preserve authenticated browser intent, detect bridge recovery, explain what happened on the wearable, and safely resume across the outage. This gives the owner continuity rather than silent loss or blind replay.
- **path:** relay → mac-planner → browser-extension → pendant
- **model tier:** background for heartbeat classification, queue reconciliation, and recovery summaries; deterministic state transitions and idempotency checks do the normal work; realtime only speaks an immediate short alert when the owner is actively waiting.
- **latency:** Heartbeat detection within 15–30 seconds; immediate outage notice within one polling interval; recovery reconciliation under 2 seconds per queued item before producing a concise pendant summary. Do not wait 45 seconds for each known-offline request.
- **cost:** Usually near-zero model cost because health checks, leases, retries, and idempotency are deterministic; occasional gpt-4.1-mini summary at roughly 1–3k prompt tokens per outage, plus a few D1 writes. This saves repeated planner/browser timeout calls.
- **security:** Authenticated URLs, tab/session IDs, and action payloads must remain on the Mac or encrypted relay store; pendant notifications contain only sanitized status and request labels. Never replay non-idempotent browser actions solely because a heartbeat returns: reattach and verify tab/session state, require an existing idempotency key, and classify unsafe or ambiguous items as skipped with an explanation. This is recovery and observability, not a new approval gate or restriction on the owner's unrestricted Mac shell.
- **missing:** Relay durable queue-health state machine with lease expiry, dead-letter records, and recovery events; Mac read adapter exposing normalized browser queue item age, attempts, status, idempotency key, and session affinity; Browser extension handshake that acknowledges command completion or explicit cancellation and reports tab identity/version; Cross-surface notification event from relay to pendant with a compact recovery receipt


## Changes it proposed to its own stack

### `integration` — Add a cross-surface liveness supervisor and dead-letter recovery loop. The relay periodically reads Mac /ops/status, /browser/status, /jobs, and /routing; tracks per-surface heartbeats, pending-command age, timeout/error rates, permission readiness, and attribution completeness. When a browser command is queued but the extension is offline or repeatedly times out, move it to a durable dead-letter record (preserving idempotency key and tab/session affinity), stop blind retries, and issue one compact pendant/Mac notification explaining the exact recovery step. On heartbeat recovery, revalidate the tab/session and offer a bounded resume; classify receipts with the originating tier/model so unattributed work is eliminated. This is telemetry/recovery only and does not gate FULL_CONTROL actions.
- **owner gets:** The owner currently gets 45-second repeated browser failures and seven stranded commands with no proactive explanation. They would instead hear once that Safari/extension is offline or blocked, know which request was preserved, and have it resume safely when the bridge returns—while Mac shell remains maximally capable.
- effort: Medium: relay state machine plus a small Mac observability adapter, dead-letter persistence, heartbeat scheduler, and pendant notification payloads; ~2–3 engineering days including failure-injection tests.  ·  risk: A false offline diagnosis could delay an otherwise recoverable action; mitigate with timestamps, one bounded retry after heartbeat, and explicit queued/failed/resumable states. Never replay a non-idempotent action without its existing idempotency key and session revalidation. No new data beyond existing job/action receipts, URLs, and error metadata leaves the Mac.
- cost: Near-zero model cost: deterministic polling and state transitions; roughly a few D1 writes per incident and small relay egress. Avoids expensive planner retries and repeated 45-second browser calls.  ·  latency: Heartbeat polling adds negligible background load; recovery notification is near real time. It reduces user-visible failure latency by detecting offline state before waiting through a command timeout.
- security: Read-only access to current authenticated observability endpoints; preserves existing unrestricted execution policy. Do not include page contents or secrets in relay telemetry—send status, IDs, timestamps, and sanitized error classes only.
- depends on: Existing authenticated read-only /ops/status, /browser/status, /jobs, /journal, and /routing endpoints; Durable relay D1 state and pendant notification/audio pipeline; Existing job idempotency keys, receipts, and browser tab/session affinity


## What it asked for

_Nothing._
## Its own summary

Discovered and recorded a live reliability defect: the Mac agent is full-control and observable, but the browser queue contains 7 pending commands and a stale `navigate` item processing since 09:11 with 8 attempts and empty params; recent navigations repeatedly waited ~45 seconds and failed. The extension has just reported online, proving this is a poisoned/stale queue problem as well as an offline problem. Proposed a cross-surface relay liveness supervisor with durable dead-lettering, idempotency/session revalidation, bounded resume, sanitized pendant alerts, and routing attribution—telemetry/recovery only, no execution gates. No additional read permission or tool is needed from me this round; implementation needs relay scheduler/D1 state and a small Mac adapter over existing observability routes.

**Biggest unknown:** Whether the stale browser command can be safely cancelled/reaped through the existing browser command lifecycle without dropping a legitimate owner request; the route contract and mutation semantics for queue cleanup were not available, and I did not mutate anything.

