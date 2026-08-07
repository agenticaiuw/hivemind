# Harness derivation — mac-terminal — round 17

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent health and policy** — Live localhost agent is version 0.5.0 on port 8000; fullControlMode and fullControlPlanner are true, token configured, required macOS permissions reported ready. Browser extension is online with one Safari device and zero pending commands. Relay is configured/reachable and mac bridge online.
  - evidence: GET /ops/snapshot returned status.agent and relay/browser details at 2026-08-07T06:48Z.
- **Mac capabilities and route surface** — GET /capabilities reports 116 routes, Bearer auth except /health and dashboard paths, plus jobs/receipts, execution journal, observe, pipeline, browser, routines, research, briefing, and machine-context groups. Execute returns per-action receipts; journal is read-only derived observability.
  - evidence: GET /capabilities returned routeCount 116 and group descriptions.
- **Current Mac observation** — Foreground app is Claude. 21 application bundles are running; browser has 3 durable sessions (default time.is/UTC, two probe forms). Accessibility is trusted but input posting was not probed; screenRecording currently reports false and ui action reachability is unverified. FULL_CONTROL means configured directory roots are not enforced.
  - evidence: GET /observe returned observedAt 2026-08-07T06:49:47Z with foregroundApps, accessibility, browser, and directories.
- **Diagnostics tool implementation** — The granted mac_read_diagnostics schema exists but has no implementation, so it cannot currently provide host checks. HTTP /machine-context and /ops/snapshot remain usable for inventory.
  - evidence: mac_read_diagnostics call returned 'tool was granted a schema but has no implementation yet'.
- **Granted diagnostic executors** — Both mac_read_diagnostics and mac_readonly_diagnostics_impl are nonfunctional stubs despite granted schemas; direct diagnostic calls return no implementation. This leaves HTTP agent endpoints as the only working reconnaissance path in this harness.
  - evidence: Calls to mac_read_diagnostics and mac_readonly_diagnostics_impl returned the explicit no-implementation error.

## What it asked for

### `p14-kjq3` (permission) — read-only access to authenticated Mac-agent observability endpoints (/jobs, /logs, /journal, /routing) via the existing local-agent auth context
- why: I need to verify the newly added receipts/journal/undo/recovery behavior and identify whether shell failures are diagnosable, but unauthenticated probe_http calls to these routes fail.
- risk it sees: This exposes local execution metadata (commands, paths, receipts, and possibly session details) to this reconnaissance agent; no mutation would be performed and secrets should be redacted by the endpoint layer.

## Its own summary

Environment is now mapped: this MacBook-Air-6.local runs AI Pendant Mac Local Agent v0.5.0 at localhost:8000 (116 routes), with FULL_CONTROL_MODE/full-control planner enabled, unrestricted configured roots, relay reachable, and Safari browser bridge online. /capabilities documents jobs/receipts, execution journal, observe, pipeline, browser, routines, and other surfaces. /observe shows Claude foreground, 21 running apps, 3 durable browser sessions, Accessibility trusted but actual synthesized-input reachability unverified, and screen recording false. The granted direct diagnostic tools are stubs with no implementation, so HTTP endpoints are the working path. I recorded all findings, informed mac-planner, and queued permission for authenticated read-only /jobs,/logs,/journal,/routing inspection to validate observability and failure recovery. No side effects were performed.

**Biggest unknown:** Whether authenticated job receipts/journal/logs actually capture arbitrary shell argv, cwd, timeout, exit status, stdout/stderr, reversibility, and recovery/cancellation accurately; current probes cannot access those routes without the local auth context.

