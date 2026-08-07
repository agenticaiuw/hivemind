# Harness derivation — mac-planner — round 117

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Handle this logged-in browser task even if my browser is temporarily unavailable; keep me informed and continue when it reconnects."
- **useful because:** Today a browser command can sit in a nine-command pending queue and consume a 45-second timeout, while the pendant/relay has no clear distinction between queued, failed, or safe-to-retry. This gives the owner a truthful answer immediately, preserves private-session work for reconnection, and routes only safe public subtasks elsewhere.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime tier only for the immediate spoken status; use a cheaper background model to checkpoint the task, classify public versus authenticated steps, and resume after the bridge heartbeat returns.
- **latency:** Speak an admission result in under 2 seconds after a bridge health check. Do not wait 45 seconds for a dead extension. Resume within one heartbeat plus 5 seconds after reconnect; require a fresh state check before any mutation.
- **cost:** About $0.001–$0.01 per task depending on background summarization; the dominant cost is any resumed page extraction, not health checks or queue bookkeeping.
- **security:** Authenticated URLs, page text, and cookies stay on the Mac/browser path; only a redacted task state and status go to the relay. Never replay a mutation from a stale tab: resume read steps automatically, but re-plan and surface a before/after preview for any submit/send/purchase step.
- **missing:** A cross-surface admission/router service with a short browser-health TTL and per-step retry policy; Durable task checkpoints that bind each step to tab/session identity and invalidate them on tab change or stale heartbeat; Pendant-readable states for queued, waiting-for-browser, resumed, and abandoned tasks; A queue quarantine/drain operation so the existing nine pending commands cannot all replay after reconnect

### "Answer questions using my private Mac and logged-in browser data without sending the underlying content to the cloud; tell me exactly what crossed between the Mac, browser, relay, and pendant."
- **useful because:** The owner should be able to use the whole hive without choosing between usefulness and privacy. Today the surfaces can collaborate, but there is no end-to-end, task-scoped data-residency contract proving that private page text, mail, calendar details, or files stayed local while only a minimal answer reached the pendant.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a small local model on the Mac for extraction and summarization of private data. Send only a redacted answer or structured facts to the relay; use the realtime tier solely to speak the result. Use a slower background model only when local synthesis is insufficient and the owner has explicitly enabled cloud processing for that task.
- **latency:** For a local-only answer, speak within 3 seconds after the Mac has the relevant source. A data-flow manifest should be available within 1 second and never delay ordinary local execution.
- **cost:** Usually under $0.005 per request when local synthesis is sufficient; cloud escalation, if explicitly enabled, dominates cost.
- **security:** Private source content must remain on the Mac/browser unless the owner grants per-task cloud escalation. Every transfer needs a content class, destination, hash, reason, retention, and redaction record. The pendant should receive only the spoken answer and a short reference token, not raw page text or credentials. A dashboard must let the owner revoke retained capsules and inspect the transfer ledger.
- **missing:** A task-scoped data-residency and cloud-escalation policy enforced across Mac, browser, relay, and audio output; A local redaction/structured-extraction service that can produce answers without forwarding source text; An append-only cross-surface transfer ledger with content hashes, destinations, retention expiry, and revocation; A pendant gesture or spoken command to switch a task to local-only mode and receive a privacy status confirmation


## Changes it proposed to its own stack

### `integration` — Add an execution-policy reconciliation check to the pipeline event writer. Before emitting “Waiting for your approval,” read the effective executor mode and action policy; in FULL_CONTROL_MODE emit “Executing under owner’s maximum-access policy” (or a real failure), and attach the exact policy version to the job receipt. Alert when pipeline metadata and executor behavior disagree.
- **owner gets:** The owner currently hears/ sees an approval gate for a shell-backed news task even though the configured Mac policy says no gates run in FULL_CONTROL_MODE. That makes it impossible to know whether a task is waiting, running, or stuck, and can leave routine work silently incomplete.
- effort: Small-to-medium: centralize policy lookup in pipelineTrace/orchestrator, add a consistency assertion and regression tests for plan→execute→TTS flows.  ·  risk: A strict assertion could mark old jobs unhealthy; recover by treating it as an observability warning and preserving execution. No user data needs to leave the Mac.
- cost: Negligible API cost; one local policy lookup and a few receipt bytes per job.  ·  latency: Under 5 ms in the local pipeline.
- security: Improves audit accuracy without adding a confirmation gate or reducing the owner’s explicitly chosen maximum access.
- depends on: A single authoritative effective-policy endpoint or in-process policy object shared by executor.js and pipelineTrace.js; Receipt schema support for policyVersion/effectiveMode

### `mac-harness` — Make action execution reachability-aware without adding a confirmation gate: consume the existing read-only /observe result before ui_* actions; when synthesized input is not accepted, automatically downgrade those steps to an AppleScript/accessibility-free equivalent when one exists, otherwise return `not_reached` (not success) with the exact TCC cause. Keep non-UI actions executing normally.
- **owner gets:** Right now the Mac reports ui_click/type_text/press_keys as successful while doing nothing because AI Pendant Agent is not trusted by Accessibility. This would stop false completion claims and still let Calendar, Mail, Finder, Safari, and other AppleScript-capable work continue.
- effort: Medium: add a reachability preflight and fallback map in computerControl/executor, plus receipt status and tests for trusted and untrusted hosts.  ·  risk: Some AppleScript fallbacks may target the wrong document; restrict fallback to named-app scripts with explicit object IDs and mark ambiguous cases not_reached. Existing maximum-access behavior is preserved.
- cost: Negligible API cost; one local observation/cache lookup per UI batch.  ·  latency: Typically 10–100 ms for cached reachability; no added delay for non-UI actions.
- security: No new privilege or data egress. It makes the existing TCC boundary visible rather than pretending it was crossed. Screen Recording remains unnecessary for non-vision fallbacks.
- depends on: /observe or an equivalent cached inputReachability state; A typed receipt status distinguishing executed, failed, and not_reached; AppleScript adapters for the small set of supported named-app operations


## What it asked for

_Nothing._
