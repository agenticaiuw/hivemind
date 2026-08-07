# Harness derivation — mac-terminal — round 19

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac local agent live status** — Agent v0.5.0 is healthy on localhost:8000, token configured, FULL_CONTROL_MODE and full-control planner enabled; relay reachable and Mac bridge online.
  - evidence: GET /ops/status returned 200 with fullControlMode:true, fullControlPlanner:true, tokenConfigured:true, relay.reachable:true, macBridgeOnline:true.
- **Mac permissions and UI reliability** — Accessibility and Screen Recording are granted and requiredMissing is empty, but synthesized input reachability is explicitly unverified; /observe says UI action receipts may be untrustworthy until a no-op input probe is run.
  - evidence: GET /observe returned accessibility.trusted:true, screenRecording:true, eventsPost:null, consequence:'Unverified...'.
- **Browser bridge** — Browser extension is currently offline with no devices and one pending command; three durable browser sessions/tabs exist.
  - evidence: GET /ops/status returned browserExtension.online:false, devices:[], pendingCommands:1; GET /observe returned browser.sessions:3.
- **Mac execution observability** — The agent exposes 116 authenticated routes including jobs, receipts, journal, observe, ops snapshot/status, logs, routing, and pipeline traces. Execution journal is derived read-only and records order, touched resources, planner tier, and undoability.
  - evidence: GET /capabilities returned routeCount:116 and route groups; GET /ops/status and /observe returned live state.
- **Granted diagnostics tool availability** — The granted mac_read_diagnostics interface is present but has no implementation, so it cannot provide host facts. Existing authenticated HTTP observability endpoints do work.
  - evidence: Calling mac_read_diagnostics with eight read-only checks returned error: 'tool ... has no implementation yet'; probe_http /ops/status and /observe returned 200.

## What it asked for

_Nothing._
## Its own summary

Continued reconnaissance completed. Live probes confirm Mac local agent v0.5.0 is healthy and authenticated, FULL_CONTROL_MODE/full-control planner are intentionally enabled, relay and Mac bridge are reachable, and 116 routes provide jobs/receipts/journal/observe/ops/pipeline telemetry. Required macOS permissions are present, but synthesized-input reachability is unverified, so UI-action receipts may be false. Browser extension is offline with no devices and one pending command; three durable browser sessions remain. The granted mac_read_diagnostics and mac_readonly_diagnostics_impl tools both exist only as unimplemented schemas, while authenticated HTTP probes work. I informed mac-planner and relay-realtime. For useful future work, the pending local-agent auth/observability access and a functioning read-only diagnostics tool remain the concrete needs; no additional permission or shell policy change is needed.

**Biggest unknown:** Whether Accessibility events actually reach the screen, and the current battery/network/disk/process details, because the granted diagnostic tools have no implementation and /observe intentionally does not perform the no-op input test.

