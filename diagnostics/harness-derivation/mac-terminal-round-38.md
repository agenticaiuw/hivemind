# Harness derivation — mac-terminal — round 38

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac readiness and failure behavior** — The live Mac agent reports fullControlMode=true and token configured, but ready=false because Accessibility and Screen Recording are not granted. Browser bridge is offline with 3 pending commands; browser navigate attempts sit ~45 seconds before failing. Relay is reachable and macBridgeOnline=true. The newly granted mac_read_diagnostics schemas exist but currently return 'no implementation yet'.
  - evidence: GET /ops/status HTTP 200 and GET /jobs HTTP 200 during round 38; mac_read_diagnostics returned tool error 'no implementation yet'.

## Capabilities it proposed

### "“If I leave you working on my Mac or logged-in browser, let me know when it is finished or blocked—without making me check the dashboard.”"
- **useful because:** Long jobs currently can fail after a long timeout while the owner has no indication. A wearable notification turns asynchronous Mac/browser work into something the owner can trust: completion, partial completion, or a precise recovery instruction arrives where they are.
- **path:** mac-planner → browser-extension → relay-realtime → pendant → dashboard
- **model tier:** background for job summarization and deduplication; deterministic state transitions and notifications; realtime only if the owner asks a follow-up by voice.
- **latency:** Emit a short state event within 1 second of each job transition; generate the concise spoken summary within 2–5 seconds after completion. Do not keep realtime open while work runs.
- **cost:** Usually <$0.01 per completed job when one background summary is needed; deterministic success/failure notifications cost no model call. Dominant cost is the optional background summary and audio generation.
- **security:** Notifications must not speak page contents, email text, or command arguments aloud in public. Send only job label, outcome, duration, and a redacted recovery hint; require an explicit owner request on the pendant/dashboard to reveal details. Keep authenticated URLs and shell output on the Mac/dashboard.
- **missing:** Cross-surface durable job-event subscription from local agent to relay; A pendant-safe notification queue with deduplication, quiet hours, and retry after link loss; A readiness preflight/fast-fail contract so blocked browser jobs report immediately instead of timing out; A spoken-summary endpoint that can produce a short audio item and mark it acknowledged

### "“Why is the thing I asked you to do stuck, and fix the blockage if you can?”"
- **useful because:** Today a Mac or browser job can appear to hang, then return a vague failure after a long delay. The owner should be able to ask from the pendant and receive a causal explanation—offline bridge, missing permission, stale tab, network failure, or command error—plus the safest automatic recovery. The system should try local, reversible repairs such as re-polling the bridge or reattaching a stale session, then report exactly what remains blocked.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic diagnostics and recovery selection first; background model only to translate structured causes into a concise explanation. Realtime is used only for the owner's spoken question and answer.
- **latency:** Return the first diagnosis in under 2 seconds from cached job/readiness state; attempt bounded recovery for up to 15 seconds, then report a concrete next step.
- **cost:** Typically <$0.005 per invocation; deterministic state inspection dominates, with an optional small background summarization call. No call is needed for standard known failure codes.
- **security:** Do not read shell output, authenticated page text, URLs, or permission details aloud by default. Speak a redacted cause and recovery status; require an explicit follow-up to expose sensitive diagnostics. Recovery actions must be narrowly scoped, reversible where possible, and recorded in the existing receipt/audit trail.
- **missing:** A causal failure taxonomy shared by local jobs, browser commands, relay delivery, and pendant connectivity; A bounded recovery planner with typed, idempotent repair operations (reattach session, resume polling, retry only after precondition change); A live job/readiness state API queryable by the relay and pendant; Privacy-aware spoken rendering of diagnostic evidence


## Changes it proposed to its own stack

### `integration` — Add a capability-aware preflight and fast-fail layer shared by relay, mac-planner, browser-extension, and mac-terminal. Before dispatch, query a compact readiness contract (Mac agent health/permissions, browser extension heartbeat and pending-command age, active session/tab binding, relay reachability, and pendant link). Classify each planned step as ready, degraded, or unavailable; route ready steps normally, substitute another surface when safe, and return a typed failure immediately when unavailable instead of letting browser commands sit for ~45 seconds. Persist the preflight snapshot and include it in the existing job receipt, with suggested recovery (e.g. open Safari/enable bridge, grant Screen Recording) but no approval gate or capability restriction.
- **owner gets:** Requests finish quickly and explain themselves. The owner stops waiting through repeated browser timeouts and gets an actionable answer about which device or permission is actually missing; multi-surface jobs can still use the parts that are online.
- effort: Medium: define readiness schema, adapters for existing /ops/status and browser heartbeat/session state, planner dispatch hook, receipt/dashboard rendering, and tests for stale heartbeats and partial failures.  ·  risk: A stale or overly strict health signal could incorrectly skip a workable action, or leak permission/device details into receipts. Mitigate with short TTLs, an explicit degraded/unknown state, fallback dispatch for unknown, and local redaction. No mutation is performed by preflight.
- cost: Negligible API cost; a few deterministic JSON reads per job. Saves model and wall-clock cost by preventing doomed retries/timeouts.  ·  latency: Adds roughly 50–200 ms for local checks; avoids 45–120 s failed browser attempts and allows partial execution.
- security: Read-only readiness metadata only; do not include URLs, page text, tokens, or environment secrets in relay-visible snapshots. Keep detailed permission diagnostics local and send only typed reasons.
- depends on: A stable local readiness endpoint aggregating existing /ops/status, /browser/status, and job/session state; Browser heartbeat freshness and command queue timestamps; Receipt schema support for preflight evidence


## What it asked for

_Nothing._
