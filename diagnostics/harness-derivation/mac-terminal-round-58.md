# Harness derivation — mac-terminal — round 58

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-bridge live readiness** — At live /ops/status, Mac agent is online with FULL_CONTROL_MODE and llmPlannerEnabled, but computerUse.loopEnabled=false; Accessibility and Screen Recording are ungranted, browser extension home-chrome is offline with 4 pending commands, while relay is reachable and mac bridge online.
  - evidence: GET /ops/status returned HTTP 200 with agent.permissions, computerUse, browserExtension, and relay payload.

## Capabilities it proposed

### "“Handle this logged-in browser task even if the browser is asleep—wake the Mac bridge, reconnect the browser, resume where you left off, and tell me promptly if it cannot be recovered.”"
- **useful because:** Today a browser action can sit for ~45 seconds and fail because the extension is offline, even though the Mac and relay are healthy. The owner gets a fast recovery attempt instead of a silent dead end, while preserving the authenticated browser boundary and never submitting an irreversible step automatically.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use realtime only to acknowledge the pendant request and announce state changes; use a cheaper background planner for health preflight, Safari/bridge recovery, checkpointed resume, and final concise report.
- **latency:** Preflight and health verdict under 2 seconds; attempt bridge wake/reconnect for up to 20 seconds with heartbeat updates; resume from the last completed checkpoint. Never spend 45 seconds on a command known to target an offline surface.
- **cost:** Low per invocation: mostly local status checks and durable job state; one background planner call only when recovery or step reconciliation is needed. Realtime cost is limited to a short acknowledgement and completion/failure announcement.
- **security:** Authenticated page data stays in the browser bridge and local agent; relay receives job state and redacted error reasons, not page contents. Recovery may open Safari and reconnect an extension, but must stop at any irreversible submit/send checkpoint and retain existing receipts and tab affinity.
- **missing:** A fast browser-health preflight/circuit breaker that consults /browser/status before dispatch; A Mac-bridge recovery action to launch/focus Safari and verify extension polling without relying on screen-recording permission; Checkpointed resume semantics that distinguish a definitely-unexecuted step from an unknown-outcome step; Pendant-friendly progress events and dashboard controls for retry, abandon, or inspect the failed checkpoint

### "“While I was away, tell me what the system tried to do, what actually changed, what failed because a device was unavailable, and what still needs my decision—across the pendant, Mac, relay, and browser.”"
- **useful because:** Today the owner can see individual job records and failure receipts, but cannot ask one question and receive a trustworthy, cross-surface causal account. This would turn disconnected logs such as an offline browser command, a healthy relay, and a Mac-side fallback into a short answer that distinguishes completed effects, no-op failures, unknown outcomes, and pending decisions.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheap background model to assemble and classify the event timeline from typed local receipts and health transitions; use realtime only when the owner asks from the pendant, for a short spoken summary and follow-up questions.
- **latency:** A cached summary should start within 2 seconds and finish within 5 seconds; if raw evidence must be fetched from the Mac or browser, announce that and complete within 15 seconds. Never claim an effect without a receipt or explicit device evidence.
- **cost:** Low: event normalization and deterministic correlation dominate; one small background-model call for causal compression. No vision or realtime generation is needed unless the owner asks for a live explanation.
- **security:** Keep page text, shell commands, and private app contents on the Mac/browser. Send the relay only redacted event types, timestamps, target surface, outcome class, and receipt references. The owner must be able to request local evidence, and the system must label inferred causality separately from observed facts.
- **missing:** A shared event schema spanning local jobs, relay pipeline events, browser commands, and pendant notifications; A durable correlation ID that survives retries, handoffs, and reconnects; A local evidence index that can answer completed/no-op/unknown without exposing raw command or page contents; A causal summarizer with strict observed-versus-inferred wording and a pendant-sized output mode


## Changes it proposed to its own stack

### `mac-harness` — Add a non-blocking execution journal and preflight circuit breaker around every cross-surface action. Before dispatch, snapshot target health (Mac bridge, browser extension, permissions, session/tab affinity); if unhealthy, emit a typed blocked-before-start receipt immediately, enqueue a recovery plan, and resume only from a checkpoint whose prior outcome is certain. Record monotonic start/deadline/heartbeat timestamps, retry reason, and whether an outcome is unknown. Keep FULL_CONTROL_MODE and unrestricted shell exactly as-is; this is telemetry, routing, and recovery—not a gate.
- **owner gets:** A request will stop wasting nearly a minute on a browser command that could never run, and a dropped connection will not make the agent guess whether it already clicked or submitted something. The pendant can say “browser offline; reconnecting” quickly, while the Mac and relay continue recovery in the background.
- effort: Medium: shared typed journal schema, preflight adapters for Mac/browser/relay, checkpoint state machine, and dashboard/pendant event projection; integration tests for offline, timeout, reconnect, and unknown-outcome cases.  ·  risk: A bad checkpoint classification could skip a needed step or duplicate a reversible one. Default unknown outcome to pause and report, use idempotency keys where supported, and preserve raw receipts for manual recovery. Journal growth is controlled by compaction with immutable summaries.
- cost: Negligible compute/storage overhead on Mac; occasional cheap planner call during recovery. No new model call for healthy actions.  ·  latency: Adds milliseconds to healthy dispatch; removes known-dead waits and enables parallel recovery heartbeats.
- security: Improves auditability without reducing owner-authorized access. Store page-content-free health/error metadata by default; keep sensitive browser evidence local and reference it by receipt ID.
- depends on: A stable typed job/checkpoint contract across local agent and relay; A browser extension heartbeat/status endpoint; A Mac action for opening/focusing Safari and checking bridge polling

### `model-routing` — Compile a live capability matrix into the planner route decision: expose per-surface health, permissions, latency, and action classes with TTLs, then select the least-dependent execution path before planning (for example, use shell/AppleScript or browser DOM actions when vision is unavailable; use relay/pendant for notification only; defer GUI actions until Accessibility/Screen Recording are actually ready). If no path is viable, return a precise reason and recovery action immediately rather than invoking a disabled loop.
- **owner gets:** The owner gets an action that works with the Mac as it is, instead of a vague failure from an unavailable vision loop. It also makes the pendant’s answer honest: “I can do this through Safari, but visual control is unavailable,” rather than burning time trying the wrong body.
- effort: Medium: typed capability snapshots with expiry, planner routing rules, and result explanations; no change to FULL_CONTROL authorization.  ·  risk: Stale health could route to a path that has just disappeared. Require a lightweight execution-time recheck and fall back to the recovery journal; never infer that a permission is granted merely because it was previously observed.
- cost: Saves expensive planner/vision calls and long failed retries; small local status overhead.  ·  latency: Adds one cached matrix lookup and optional quick recheck; should reduce failed-task latency substantially.
- security: No broader access. Permission state and app names are sensitive host metadata, so send only the minimum reason to relay and keep detailed diagnostics local.
- depends on: Typed health/preflight journal; A compact context projection with source timestamps and TTL; Planner adapters that advertise shell, AppleScript, browser, and vision alternatives


## What it asked for

_Nothing._
## Its own summary

Fresh discovery found a concrete live failure mode: /ops/status shows the Mac/relay healthy, but the browser extension is offline with 4 pending commands; /jobs shows browser_navigate waited ~45 seconds before failing. I proposed an end-to-end capability to wake/reconnect/resume authenticated browser work, plus a Mac execution journal/preflight circuit breaker and capability-aware model routing. These preserve FULL_CONTROL_MODE and do not add approval gates. I also recorded the current readiness facts: vision loop disabled, Accessibility and Screen Recording unavailable, relay reachable.

**Biggest unknown:** The newly granted mac_read_diagnostics schema still has no implementation, so I cannot independently verify host diagnostics beyond /ops/status. The requested Mac job-lifecycle contract, read-only observability permission, and shell-job-control tool also remain unanswered; I can proceed with the live HTTP evidence but cannot validate journal/checkpoint behavior end to end yet.

