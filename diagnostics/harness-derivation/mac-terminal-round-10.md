# Harness derivation — mac-terminal — round 10

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac local agent health and scheduler** — GET /health reports AI Pendant Mac Local Agent version 0.5.0. GET /routines exposes a persisted daily routine named Morning brief, enabled, scheduled 07:30, ran once successfully at 2026-08-07T05:29:38Z; scheduler state is observable via HTTP.
  - evidence: GET /health and GET /routines returned 200 JSON.
- **Mac local agent job observability** — GET /jobs and GET /logs expose recent action jobs and detailed action results. Existing records include successful run_shell battery/Wi-Fi and git branch checks, plus failed browser actions due to no matching tab/protected page/invalid URL. Job records include jobId, status, command, actions, stdout/stderr, timestamps, and failure reasons.
  - evidence: GET /jobs and GET /logs returned 200 JSON with detailed records.
- **Mac runtime status** — A recorded successful routine command reported Battery Power at 49%, discharging with 1:35 remaining, and Wi-Fi en0 On. Currentness is tied to the routine's 2026-08-07 execution, not a fresh diagnostic.
  - evidence: GET /jobs response includes successful run_shell stdout.
- **Local agent route surface** — GET / and GET /status, /capabilities, /browser/tabs, /v1/bridge/work return 404; /logs and /jobs are valid read endpoints. Bridge work is not exposed at this local-agent path.
  - evidence: Parallel probe_http GET responses.

## What it asked for

_Nothing._
## Its own summary

Continued reconnaissance via the real local-agent HTTP surface. Confirmed /health (agent v0.5.0), /routines (persisted daily Morning brief, enabled, completed once), /jobs and /logs (detailed action/job observability including stdout/stderr and failure reasons). Confirmed /, /status, /capabilities, /browser/tabs, and /v1/bridge/work are not local-agent GET routes (404). Shared scheduler/observability facts with mac-planner and relay-realtime. The granted diagnostic tools themselves return 'no implementation yet', so no fresh host diagnostics could be collected this round.

**Biggest unknown:** The local-agent route and job lifecycle contract remains unavailable (already requested): exact endpoints/semantics for submitting, polling, cancellation, retries, and bridge-originated work. Also, a functioning read-only diagnostic implementation is still needed for fresh OS/process/permissions/audio/network checks; current status evidence is historical job output rather than a live probe.

