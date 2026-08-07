# Harness derivation — mac-terminal — round 18

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent health and authorization** — Local agent v0.5.0 is healthy on 127.0.0.1:8000; token is configured and required for protected routes; FULL_CONTROL_MODE, LLM planner, and full-control planner are enabled. All listed macOS automation permissions report granted and requiredMissing/optionalMissing are empty.
  - evidence: GET /health and GET /ops/status returned 200 with these fields.
- **Mac observability surface** — Read-only /observe, /ops/status, /ops/snapshot, /jobs, /logs, /routing, and receipt/journal routes are live. Execution receipts now expose duration, touched shell reference, reversibility, and irreversible reason; however one current execute job remains processing with no receipts.
  - evidence: GET /capabilities enumerated the routes; GET /observe, /ops/status, /ops/snapshot, /jobs, and /logs returned live JSON.
- **UI input trust** — Accessibility and Screen Recording are TCC-granted, but synthesized input reachability is explicitly unverified; /observe says a no-op probe is needed and UI actions may report success while doing nothing if the grant is for the wrong bundle.
  - evidence: GET /observe returned accessibility.trusted=true, uiActionsWillReachTheScreen=null, and consequence text.
- **Browser bridge** — Browser extension is configured but currently offline with zero devices; there are 3 durable browser sessions/tabs visible through observation and one pending browser command.
  - evidence: GET /ops/status and GET /observe returned browser online=false/devices=[]/pendingCommands=1 and sessions=3.
- **Diagnostic tool availability** — The newly granted mac_read_diagnostics and mac_readonly_diagnostics_impl tools have schemas but no backend implementation, so direct fixed-command diagnostics cannot currently run. HTTP observation/status remains usable.
  - evidence: Calls returned 'This tool was granted a schema but has no implementation yet'.
- **Execution journal retention** — Execution journal is read-only and derives from the durable job store, receipts, undo verdicts, routing stats, and action-risk labels. It currently retains 120 jobs, returns 25 by default, and oldest retained job is about one hour old; older history is evicted.
  - evidence: GET /journal returned jobsInStore=120, returned=25, storePath=/Users/evanliu/AI-Pendant-Workspace/pendant-jobs.json and retention note.
- **Current job anomaly** — At least one local execute job has remained processing since 07:09:44 with no receipts, while prior long run_shell jobs complete successfully and are marked irreversible. This is the main recovery/observability issue to investigate.
  - evidence: GET /jobs returned local_c88256b7... status=processing, receipts=[]; completed triage jobs show duration and irreversible run_shell receipts.
- **Routing telemetry** — Routing telemetry is live but currently only has two deterministic requests, no planner/background samples, and no priced token data; it cannot yet characterize planner cost or latency.
  - evidence: GET /routing returned totalRequests=2, deterministic requests=2, planner/background requests=0, priced=false.

## What it asked for

_Nothing._
## Its own summary

Reconnaissance continued. The Mac local agent is healthy (v0.5.0, 127.0.0.1:8000), bearer-authenticated, FULL_CONTROL_MODE/LLM planner enabled, relay reachable, and all reported macOS automation permissions granted. Read-only observability is substantially available: /observe, /ops/status, /ops/snapshot, /jobs, /logs, /journal, /routing, and receipts. Receipts now include duration, touched shell, reversibility, and irreversible reason. Important findings: UI input reachability remains unverified despite TCC Accessibility/Screen Recording grants; browser extension is offline with zero devices, three durable browser sessions, and one pending command; the job store retains only the newest 120 jobs; routing telemetry has only two deterministic samples and no planner cost data; one execute job is currently stuck in processing with no receipts. The newly granted fixed diagnostic tools (mac_read_diagnostics and mac_readonly_diagnostics_impl) exist only as schemas and return 'no implementation yet', so HTTP observation is the usable status path. I sent these findings to the orchestrator record and asked relay/mac-planner/mac-vision peers for cross-checks.

**Biggest unknown:** Why local_c88256b7-6efb-4123-b5eb-c57c26b3e9ae remains processing with no receipts, and whether synthesized UI input actually reaches the screen. The pending diagnostic-tool implementation and the outstanding job-control/route-lifecycle capability would make these directly verifiable, but I did not re-request previously denied or pending grants.

