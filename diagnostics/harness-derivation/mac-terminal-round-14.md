# Harness derivation — mac-terminal — round 14

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent audit and rollback** — Jobs and receipts provide per-action audit metadata and typed undo status; receipts distinguish read/write and reversible/irreversible, with touched refs, timing, snapshots, and reasons. Undo endpoints exist, but observed run_applescript/browser navigation were irreversible.
  - evidence: GET /jobs/local_4201b2c5-65da-4a63-8c99-4bda8eaca0ff/receipts returned receiptId/actionId, effect, startedAt/finishedAt/durationMs, touched, snapshot, reversible:false, irreversibleReason; jobs object included undo.canUndo and snapshotVault.
- **Mac agent runtime** — Agent v0.5.0 is healthy on localhost:8000 with fullControlMode=true, planner enabled, browser extension online, accessibility/screen recording/automation permissions ready, relay reachable and paired.
  - evidence: GET /ops/status returned tokenConfigured:true, fullControlMode:true, browserExtension.online:true, permissions.ready:true, relay.reachable:true.
- **Mac agent observability** — Flat activity log and aggregate ops snapshot are available; logs include command, actions, results and receipts. Paths are exposed in ops status.
  - evidence: GET /logs returned executed commands and receipt structures; GET /ops/snapshot returned logPath /Users/evanliu/AI-Pendant-Workspace/mac-agent-activity-log.json and jobsPath /Users/evanliu/AI-Pendant-Workspace/pendant-jobs.json.
- **Route discovery** — Capability manifest reports 98 bearer-authenticated routes, with groups for jobs, logs, ops, machine context, browser, pipeline, sessions, thinking, projects, routines, research, etc.; health and dashboard are public.
  - evidence: GET /capabilities returned routeCount:98, publicPaths [/dashboard, /health], and grouped route manifest.
- **Granted diagnostics tools** — The granted mac_read_diagnostics and mac_readonly_diagnostics interfaces are present but have no implementation, so they cannot provide direct host diagnostics; HTTP ops/machine-context probes are currently the usable source.
  - evidence: Both tool calls returned error: tool was granted a schema but has no implementation yet.

## What it asked for

_Nothing._
## Its own summary

Completed reconnaissance of the Mac agent. Confirmed 98 bearer-authenticated routes, healthy full-control runtime, online Safari bridge and relay, complete automation permissions, machine inventory, and concrete job/log/receipt/undo observability. Communicated to mac-planner that receipts already provide effect, timing, touched refs, snapshots, reversibility and irreversible reasons, and recommended structured command metadata, pre-state capture for known reversible actions, typed restore, correlation and cancellation without adding gates. Recorded all findings.

**Biggest unknown:** The granted direct Mac diagnostic interfaces still have no implementation, and the exact local run_shell job lifecycle/structured receipt contract remains unavailable; HTTP status, machine-context, jobs, logs and ops snapshot are usable substitutes.

