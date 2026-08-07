# Harness derivation — mac-terminal — round 16

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac local agent health** — GET /health previously responded 200 with {ok:true, service:'AI Pendant Mac Local Agent', version:'0.5.0', capabilities:'/capabilities'}, but subsequent probe and route descriptions returned fetch failed; reachability is intermittent or backend-side unavailable.
  - evidence: functions.probe_http GET /health response in this round, followed by five fetch-failed probes and route describe calls.
- **Mac diagnostic grants** — All four granted diagnostic interfaces are currently nonfunctional stubs: mac_read_diagnostics, both mac_readonly_diagnostics variants, and mac_readonly_diagnostics_impl return 'tool was granted a schema but has no implementation yet'.
  - evidence: Parallel calls to each tool returned the identical no-implementation error.
- **Mac agent observability surface** — Discovered route table includes health/capabilities, jobs with receipts/cancel/undo, logs, ops status/snapshot, machine-context, routing, journal, and browser status; all protected routes are described as Bearer-token required.
  - evidence: discover(routes) returned these named routes and auth summary.

## What it asked for

_Nothing._
## Its own summary

Reconnaissance continued. The discovered Mac agent is v0.5.0; /health returned 200 once, but all subsequent local-agent probes and route live-descriptions failed with fetch failed, so connectivity is intermittent/unavailable from this harness. The route table exposes protected observability and lifecycle endpoints including /logs, /jobs, /jobs/:id/receipts, cancel/undo, /ops/status, /ops/snapshot, /journal, and /machine-context. Every newly granted diagnostic tool is only a schema stub and returns no implementation yet. I recorded these findings. To do useful terminal work I need (1) an actually implemented read-only diagnostics path, (2) stable access to the local-agent route/job lifecycle surface, and (3) the already-pending shell job-control/lifecycle contract; no authorization gates are needed or requested.

**Biggest unknown:** Whether the local agent is currently down, unreachable only from the discovery backend, or intermittently failing; without a functioning diagnostic implementation or stable route access I cannot verify host state, running jobs, receipts, or recovery behavior.

