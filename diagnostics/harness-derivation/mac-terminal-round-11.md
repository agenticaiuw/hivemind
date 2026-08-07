# Harness derivation — mac-terminal — round 11

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac local-agent HTTP service** — GET /health returned 200 JSON {ok:true, service:'AI Pendant Mac Local Agent', version:'0.5.0'}. Root, /api, /status, /capabilities, /diagnostics, /actions, /health/details, /version, /browser, /metrics, /openapi.json, /api-docs, /routes, /config, and /healthz returned 404.
  - evidence: probe_http GET responses in round 11
- **Mac local-agent observability endpoints** — GET /jobs, /logs, and /sessions returned 200. Responses contain job IDs, action types/params, statuses, timestamps, stdout/stderr, browser snapshots, and session turns. /jobs/:id was 404, so per-job lookup route is not exposed at that path.
  - evidence: probe_http GET /jobs, /logs, /sessions and /jobs/local_... responses in round 11
- **Mac diagnostics tool availability** — All granted diagnostic tool variants (mac_read_diagnostics, mac_readonly_diagnostics, mac_readonly_diagnostics_impl) currently return an error saying no implementation yet; no host data could be freshly collected through them this round.
  - evidence: parallel tool calls in round 11
- **Mac shell architecture and policy** — Inherited context establishes arbitrary run_shell with 120s default timeout, unrestricted cwd/environment/network, FULL_CONTROL_MODE bypassing actionRisk, no shell authorization or confirmation, and job record as only audit trail; owner deliberately requires maximum capability and does not want gates or narrowing.
  - evidence: orchestrator-provided Mac shell compatibility and authorization context

## What it asked for

### `t15-h93d` (tool) — mac_shell_job_control
- why: The existing arbitrary run_shell can execute unattended but the exposed diagnostics are unimplemented and /jobs lacks per-job lookup. Useful work needs structured observability and recovery for long-running or failed commands without reducing capability: inspect one job, retrieve bounded stdout/stderr, and cancel a still-running job.

```json
{
  "operation": "string enum: inspect|tail|cancel",
  "job_id": "string",
  "max_output_bytes": "integer 1..1048576",
  "stream": "string enum stdout|stderr|both",
  "signal": "string enum INT|TERM|KILL (only for cancel)"
}
```

## Its own summary

Reconnaissance: local Mac agent health is confirmed at GET /health (AI Pendant Mac Local Agent v0.5.0). GET /jobs, /logs, and /sessions expose rich action/job/session records including shell stdout/stderr and browser snapshots; /jobs/:id and common metadata/docs routes are absent. All newly granted diagnostic tool variants are present in schema but return 'no implementation yet', so no fresh host diagnostics were possible. Existing granted context establishes the deliberate unrestricted FULL_CONTROL_MODE shell design, inherited cwd/env/network, 120s default timeout, and job-record-only audit. I recorded these findings, notified mac-planner, relay-realtime, and mac-vision, and requested a structured shell job inspect/tail/cancel capability to improve observability and recovery without narrowing execution.

**Biggest unknown:** The local-agent route and job lifecycle contract remains unavailable (previously requested and still unanswered), including exact POST execution schema, asynchronous behavior, timeout/termination semantics, log retention, and whether any authenticated remote caller can reach these endpoints. The diagnostic implementations also need to be wired before current OS/process/network/audio state can be verified.

