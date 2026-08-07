# Harness derivation — mac-terminal — round 125

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If something I asked the pendant to do fails, recover it automatically when it is safe, otherwise tell me exactly what broke, what was tried, and what I need to do."
- **useful because:** The system already records failures, but today a failed Mac/browser job is a dead end: the owner has to notice it, diagnose stale tabs or missing permissions, and retry manually. A cross-surface recovery loop would use the relay for durable monitoring, the Mac for local diagnostics/actions, and the browser extension for tab/session repair, then return a short truthful pendant update instead of silently replaying a bad action.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic failure classification and bounded recovery recipes first; gpt-4.1-mini background model for summarizing evidence and choosing among known recovery recipes; realtime only for the final spoken update when the owner is actively listening.
- **latency:** For an interactive failure, diagnose in under 2 seconds and attempt at most one bounded recovery within 10 seconds; background jobs can retry/diagnose for up to 2 minutes. Never block the original action path.
- **cost:** About $0.001–$0.01 per recovered failure, dominated by optional background summarization; deterministic stale-tab, offline-bridge, timeout, and permission checks should be free.
- **security:** Diagnostics may include private URLs, app names, and browser error text; keep evidence on the Mac/relay, redact page contents and secrets before sending to the model, and send only a concise result to the pendant. Recovery must be limited to the same owner-requested goal and be auditable; never blindly replay a browser mutation or submit a form.
- **missing:** A durable failure-classification and recovery state machine that links job/action receipts to browser tab/session state and Mac permission/bridge health.; Typed, idempotent recovery recipes such as select a live tab explicitly, reopen the bridge, refresh machine context, or retry a timed-out read once.; A relay-side completion/failure notification queue and dashboard view showing original error, recovery attempt, outcome, and next owner step.; A redaction layer for command output, URLs, and browser evidence before model summarization.

### "Before you use my Mac or logged-in browser, tell me exactly what information will leave the device, what will stay local, and which model or service will see each piece; let me choose a private-local mode when possible."
- **useful because:** Today the system can act across a trusted Mac, authenticated Safari sessions, relay storage, and cloud models, but the owner cannot see or control the data boundary of a particular task. A per-task data-flow preview would make the hive usable for sensitive mail, documents, and account pages without forcing the owner to understand implementation details. This is distinct from action approval: it governs information disclosure, not whether a trusted action may run.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic data-flow analysis and redaction classification first; use a cheap background model only to explain the resulting policy in plain language. Realtime is needed only to speak the short preview or answer a follow-up.
- **latency:** Render a preview in under 500 ms for known action types; for an unfamiliar workflow, produce a conservative preview within 2 seconds before execution planning continues.
- **cost:** Near-zero for deterministic classification; under $0.001 for occasional background explanation. The dominant cost is engineering a complete inventory, not inference.
- **security:** The preview itself must not reveal private page contents. It should describe categories, destinations, retention, and transformations (for example, “Gmail message body: local Safari only” or “calendar title: sent to relay model after redaction”). A local-only selection must be enforceable and visibly fail closed if a required cloud step cannot be avoided. The policy and actual observed egress should both be journaled for later inspection.
- **missing:** A typed per-action data-flow manifest covering shell output, screenshots, DOM/page text, audio, model prompts, relay persistence, and dashboard access.; A local redaction/tokenization service that can replace sensitive values while preserving task utility.; Execution-time enforcement of the selected privacy mode, including a local-model or local-deterministic fallback and refusal to upload when no fallback exists.; A post-task egress receipt comparing planned versus actual destinations, fields, retention, and model calls.


## Changes it proposed to its own stack

### `model-routing` — Make the planner consume a live capability-readiness matrix before selecting an execution surface. Derive it from /ops/status and /browser/status, explicitly distinguishing configured, permission-ready, online, and currently-targetable. For this Mac, report Accessibility=false and Screen Recording=false as unavailable for mac-vision, while Safari automation and browser-extension are available; attach a short reason and a fallback route to every plan. Recompute after bridge heartbeats and permission changes, and record the matrix version in the job receipt.
- **owner gets:** The owner gets fewer impossible attempts and more honest behavior: GUI work will not be sent to a loop that cannot control or see the Mac, while browser or script alternatives are chosen immediately. If no safe fallback exists, the pendant says that before wasting time rather than reporting a mysterious failure.
- effort: Medium: readiness schema, planner prompt/selector integration, receipt field, and tests for stale browser tabs and missing Accessibility/Screen Recording.  ·  risk: A stale health result could hide a newly available surface or overrule a valid one. Use short TTLs, refresh on failure, and permit the planner to retry once after a fresh status read. This is advisory routing only and does not add approval gates or reduce FULL_CONTROL_MODE.
- cost: Negligible API cost; one small deterministic status read per multi-step plan. Saves planner tokens and failed execution attempts.  ·  latency: Adds roughly 50–150 ms locally; should reduce total latency by avoiding doomed vision/browser retries.
- security: Permission state and app/tab metadata remain local; only coarse readiness labels and failure reasons need enter model context. Do not expose URLs or command output in the matrix.
- depends on: A stable /ops/status and /browser/status response schema with timestamps and explicit permission booleans; Planner support for surface fallback and a readinessVersion field in job receipts

### `relay` — Add bounded live stdout/stderr progress and heartbeat events for run_shell and other long Mac actions. The local agent should emit sequence-numbered chunks (with size caps and secret redaction), phase, elapsed time, and exit status into the existing job/pipeline stream; persist only a compact tail plus hashes in the journal. Relay and pendant can subscribe, while the dashboard reconstructs the full local log when authorized.
- **owner gets:** For a command that takes minutes, the pendant can say “still indexing files, 42 seconds elapsed” instead of appearing dead, and can distinguish a slow job from a crashed Mac bridge. When it finishes, the owner gets the real exit code and the last useful error rather than a vague failure.
- effort: Medium: child-process stream handling, redaction/chunk limits, pipeline event schema, reconnect cursors, and tests for timeout/termination.  ·  risk: Output can contain secrets or huge/binary data; redact known token patterns, cap each chunk and total retained tail, mark truncation, and keep full output local by default. A dropped stream must not affect execution.
- cost: Low storage and relay traffic; no model cost unless the owner asks for a summary. Reduces repeated polling and planner turns.  ·  latency: Near-zero execution impact; first progress event within 250 ms, with 1–2 second coalescing to avoid pendant spam.
- security: Potential leakage of shell output is the main risk. Default to local-only raw output, relay only redacted progress summaries, and require an explicit dashboard fetch for full logs.
- depends on: Existing /jobs, /journal, /pipeline/events, and /pipeline/stream contracts; A redaction utility shared by shell receipts and relay telemetry; A reconnect cursor so clients do not replay duplicate progress events


## What it asked for

_Nothing._
