# Harness derivation — mac-terminal — round 12

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent health and control posture** — Local agent v0.5.0 is healthy at /health; /ops/status reports fullControlMode=true, llmPlannerEnabled=true, fullControlPlanner=true. Computer-use loop disabled, vision model configured, vision upload consent false, maxSteps 25.
  - evidence: GET /health returned 200 service AI Pendant Mac Local Agent version 0.5.0; GET /ops/status returned these fields.
- **Mac permissions and connected services** — Agent is ready with Accessibility and Screen Recording granted, all listed automation grants present, browser extension online with one Safari device and zero pending commands. Relay is configured/reachable and macBridgeOnline=true.
  - evidence: GET /ops/status returned permissions.ready=true, requiredMissing=[], browserExtension.online=true/pendingCommands=0, relay.reachable=true and macBridgeOnline=true.
- **Mac agent observability** — Existing GET /logs and GET /jobs expose command/action results, statuses, thinking traces, receipts with effect, touched resources, reversibility and timing; GET /jobs/:jobId/receipts is available. Undo/cancel routes exist for jobs, but shell-specific job control contract is not yet available to me.
  - evidence: Route discovery listed /logs, /jobs, /jobs/:jobId/receipts, /jobs/:jobId/cancel, /jobs/:jobId/undo; live /jobs showed receipt fields including effect, touched, reversible, irreversibleReason.
- **Diagnostic tool availability** — The granted mac_read_diagnostics interface currently returns 'no implementation yet', so it cannot collect host diagnostics. Live HTTP status is usable as a fallback, but a bounded diagnostic implementation remains needed for shell-tier reconnaissance and fast status paths.
  - evidence: Calling mac_read_diagnostics with standard checks returned error: tool was granted a schema but has no implementation yet.
- **Routing telemetry** — GET /routing is live and reports deterministic/background/planner request counts, estimated token and latency metrics, escalations, and recent requests; currently all counters are zero and no baseline samples.
  - evidence: GET /routing returned 200 with totalRequests=0, samples=0, recent=[] across all tiers.

## What it asked for

_Nothing._
## Its own summary

Recon complete for this round. Live probing confirms Mac Local Agent v0.5.0 is healthy and ready, full-control execution is intentionally enabled, all required macOS permissions are granted, Safari browser extension and Cloud relay are online, and existing logs/jobs/receipts provide action-level observability including reversibility and timing. Routing telemetry exists but has zero samples. Every newly granted diagnostic executor (mac_read_diagnostics, mac_readonly_diagnostics_impl) currently returns 'no implementation yet', so no direct host command diagnostics were possible; HTTP /ops/status was used instead. I recorded these findings and informed mac-planner.

**Biggest unknown:** The still-unanswered Mac local-agent route/job lifecycle contract and mac_shell_job_control/mac_readonly_probe grants. I need those implementations/contracts to run bounded shell inventory, inspect shell jobs, capture stdout/stderr/exit code/duration, classify reversible versus permanent effects, and support failure recovery without inventing endpoint behavior. No further request was made because those requests are already pending.

