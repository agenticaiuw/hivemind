# Harness derivation — mac-terminal — round 15

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent route surface** — Live route discovery lists authenticated Mac-agent endpoints for /health, /capabilities, /execute, sessions, logs, jobs, receipts, cancellation/undo, thinking, pipeline, projects/context, machine context, ops status/snapshot, observe, browser, briefing/research/routines, and more. Discovery metadata says Bearer token required except /health.
  - evidence: functions.discover(category=routes) returned the route list and summaries.
- **Mac-agent reachability from this harness** — The discovery service cannot live-fetch the Mac-agent routes: describing /health, /capabilities, /jobs, /jobs/:jobId/receipts, /ops/snapshot, /observe, and /logs all returned liveStatus 0/liveResponse fetch failed; direct probe_http GET /health also returned status 0 fetch failed.
  - evidence: functions.describe and functions.probe_http responses in this round.
- **Granted Mac diagnostics** — The newly granted mac_read_diagnostics and mac_readonly_diagnostics_impl interfaces are present by schema but have no backend implementation, so they cannot return host facts; both explicitly returned 'tool ... has no implementation yet'.
  - evidence: Calls to mac_read_diagnostics with eight read-only checks and mac_readonly_diagnostics_impl whoami.
- **reachable devices** — Device discovery reports home-macbook-bridge (mac_bridge) offline, last seen 2026-08-07T06:35:40.374Z; cloudflare-contract-test (mobile) also offline, last seen 2026-07-31T23:42:56.525Z. Thus no currently online device is visible through this discovery surface.
  - evidence: functions.discover(category=devices) response.

## What it asked for

_Nothing._
## Its own summary

Continued reconnaissance: route discovery confirms a broad authenticated Mac-agent API, including jobs/receipts, logs, ops status/snapshot, and observe. However, all live route fetches I tested (/health, /capabilities, /jobs, receipts, ops, observe, logs) fail from this harness with status 0/fetch failed. The newly granted diagnostic interfaces are schema-only and return 'no implementation yet'; device discovery likewise shows home-macbook-bridge offline. I recorded these findings and notified mac-planner, mac-vision, and relay-realtime. For useful work I still need: (1) a functioning read-only Mac diagnostic implementation, (2) the local-agent route authentication and job lifecycle/receipt contract (already requested and pending), and (3) working reachability or an equivalent bridge to query/monitor the Mac agent. Given owner policy, I do not need execution gates; the highest-value replacement work remains receipts/structured observability, command stdout/stderr/exit/timeout metadata, and failure recovery.

**Biggest unknown:** Whether the Mac local agent is actually running/reachable now, and the exact authenticated request plus job/receipt schema needed to observe shell execution.

