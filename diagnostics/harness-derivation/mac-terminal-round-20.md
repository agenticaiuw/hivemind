# Harness derivation — mac-terminal — round 20

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac local-agent health and relay** — Local agent v0.5.0 is healthy and ready with FULL_CONTROL_MODE and required macOS permissions; relay is configured/reachable and bridge online as of 2026-08-07T07:21:57Z.
  - evidence: GET /health returned 200; GET /ops/status via probe_http returned ok:true, fullControlMode:true, permissions.requiredMissing:[], ready:true, relay.reachable:true.
- **Mac observability** — Read-only /observe exposes foreground/running apps, browser sessions, permission confidence, and configured directory roots. It explicitly says accessibility is trusted but input delivery is unverified; browser extension is offline and has 2 pending commands.
  - evidence: GET /observe returned readOnly:true, accessibility consequence 'Unverified', browser sessions:3; GET /ops/status returned browser online:false and pendingCommands:2.
- **Job receipts and reversibility** — Job receipts now capture action type, effect, timing, touched shell reference, reversibility, and irreversible reason. run_shell jobs are marked effect:write and irreversible because they leave no reversible trace; at least one job remains processing.
  - evidence: GET /jobs returned completed run_shell receipts with durationMs and irreversibleReason 'run_shell leaves no reversible trace', plus local_2751... status processing.
- **Diagnostic tool implementation** — The newly granted mac_read_diagnostics tool is present but unimplemented, so structured host diagnostics cannot be obtained through it; HTTP observation endpoints are currently the working read-only path.
  - evidence: Calling mac_read_diagnostics with OS/hardware/user/uptime/battery/network/audio/local-agent checks returned 'has no implementation yet'.

## What it asked for

_Nothing._
