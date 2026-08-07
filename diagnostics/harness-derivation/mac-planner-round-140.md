# Harness derivation — mac-planner — round 140

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac browser bridge recovery defect** — At 2026-08-07T14:52Z the Mac agent reports browser extension offline with 11 pending commands. POST /plan can generate an open_app action with params.appName plus a computer_use_task heartbeat check, but recent /execute jobs failed because executor validators looked in wrong fields. The plan also incorrectly advertises requiresConfirmation=true despite FULL_CONTROL_MODE policy saying no gate runs.
  - evidence: GET /ops/status; GET /browser/status; GET /jobs; POST /plan with a no-replay recovery command

## Capabilities it proposed

### "“Make my browser available, then handle the thing I just asked about.”"
- **useful because:** Today a stopped extension leaves commands queued and the Mac reports misleading validation failures. This gives the owner one reliable spoken recovery path: the pendant starts the recovery, the relay coordinates it, the Mac verifies the bridge, and only then does the browser agent continue with evidence and a final receipt.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only to understand the short spoken request and report status; use a cheap background planner for action normalization, heartbeat polling, and queue reconciliation. Browser extraction can use the existing slower research tier.
- **latency:** A healthy bridge should continue in under 2 seconds. If offline, allow one launch and a 15-second bounded heartbeat wait, then tell the owner it could not recover rather than looping.
- **cost:** Near-zero incremental model cost for healthy requests; one short realtime turn plus inexpensive background orchestration. Dominant cost is any subsequent authenticated-page extraction, not recovery.
- **security:** The browser may hold private authenticated tabs. Relay receives only bridge state, request IDs, and summarized receipts; page contents remain on the Mac/browser path. Never auto-submit or auto-replay stale queued mutations; show the owner which queued reads are safe and require an explicit continuation for writes.
- **missing:** Shared action-contract normalization at the /execute/computerControl boundary; A launch-and-heartbeat recovery endpoint/state machine; Queue reconciliation that classifies pending commands by idempotency and read/write effect; Extension reconnect UX that surfaces the recovered tab/session in the dashboard and pendant status

### "“My browser was disconnected. Tell me exactly what was attempted, what never ran, and let me resume only the safe items.”"
- **useful because:** Today the owner can be left with queued browser commands and failed Mac receipts, but no single cross-device explanation of whether a request was attempted, duplicated, or merely waiting. They need a trustworthy reconnect report before continuing private browser work.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a deterministic background reconciliation service for request/receipt comparison; use the realtime model only to turn the resulting structured report into a short spoken explanation and to interpret the owner's choice of items to resume.
- **latency:** Generate the report within 3 seconds of reconnection; resume selected read-only items immediately and keep writes staged for a later explicit spoken choice.
- **cost:** Minimal model cost: normally one short realtime response, with deterministic reconciliation dominating compute. No page re-reading unless the owner selects an item whose evidence has expired.
- **security:** The report must distinguish attempted versus completed without exposing page contents to the relay. Store hashes, request IDs, timestamps, tab/session IDs, and effect classes; redact URLs and snippets by default. Never resume a mutation solely because it was previously queued. Require an unambiguous item selection and preserve an append-only audit record.
- **missing:** A cross-surface intent ledger linking pendant request IDs to Mac jobs, browser command IDs, and receipts; A disconnect epoch and reconnect watermark so queued work can be classified as pre-disconnect, in-flight, or post-reconnect; A read-only reconciliation endpoint returning item-level resume eligibility and evidence freshness; A dashboard and pendant interaction for selecting individual safe items rather than replaying the whole queue


## Changes it proposed to its own stack

### `mac-harness` — Add a pre-dispatch action-contract adapter and browser-bridge watchdog. Before execution, canonicalize each action from either top-level aliases or nested params into one typed shape (open_app.appName, run_shell.command, run_applescript.script, etc.), reject only when the canonical value is genuinely absent, and emit the canonical key set in the receipt. Add a bounded recovery routine: if browser heartbeat is offline, launch AI Pendant Browser Bridge, poll /browser/heartbeat for up to 15 seconds, then report online/offline and the count of queued commands without silently replaying them.
- **owner gets:** The owner stops seeing false failures for actions that contained the requested value, and a spoken request involving Safari can recover a stopped bridge instead of hanging with 11 invisible pending commands. Failures become diagnosable and queued browser work is not accidentally duplicated.
- effort: Medium: shared normalization module, executor contract tests for the three observed failing payloads, and a heartbeat/launch state machine with timeout and receipt fields.  ·  risk: A bad adapter could map an unintended field or launch an app repeatedly. Constrain aliases to an explicit schema, cap retries to one per request, preserve original payload in audit receipts, and never auto-drain existing commands until their request IDs are checked for idempotency.
- cost: Negligible API cost; one local heartbeat poll loop. No new data leaves the Mac beyond existing authenticated status/receipts.  ·  latency: Adds at most 15 seconds only when a browser task detects the extension offline; normal actions gain a sub-millisecond normalization step.
- security: No new privilege; uses the already-authorized Mac bridge and bearer-protected status routes. Keep page contents out of recovery telemetry.
- depends on: A single documented action schema shared by planner, /execute, and computerControl dispatch; Browser command idempotency/request IDs (existing queue work should be used, not reimplemented)

### `integration` — Introduce an end-to-end causal intent envelope shared by pendant, relay, Mac jobs, and browser commands: every spoken intent gets an immutable intentId, attemptId, disconnectEpoch, parent step, and effect class. Propagate that envelope unchanged through /execute, browser polling/results, receipts, and journal entries; reject mismatched epochs and mark uncertain in-flight work as 'unknown' rather than failed or completed. Add a reconciliation event when the bridge returns, without replaying anything automatically.
- **owner gets:** The owner can finally distinguish “never started,” “started but outcome unknown,” “completed,” and “safe to resume” after a link loss. This prevents duplicate browser actions and makes the pendant’s explanation trustworthy even when the Mac and browser disagree.
- effort: Medium-to-high protocol change across relay, Mac job tracker, browser bridge, and dashboard schemas, followed by simulated disconnect/reconnect tests and migration for existing jobs.  ·  risk: Older clients may omit envelopes or produce orphan records. Treat missing metadata as legacy/unknown, never as successful; retain backward-compatible receipt reads and provide a migration view rather than rewriting history.
- cost: Negligible API cost and small D1/local JSON storage overhead per step; no additional page-content transfer.  ·  latency: A few milliseconds for metadata propagation; reconciliation is asynchronous after reconnect.
- security: Improves privacy and auditability if the envelope contains identifiers only, not page text or secrets. Use opaque IDs, redact URLs in relay logs, and expire detailed correlation metadata according to existing retention policy.
- depends on: A versioned shared envelope schema and correlation-ID generator; Receipt/journal writers accepting propagated metadata; Browser command queue preserving request IDs across reconnects


## What it asked for

_Nothing._
