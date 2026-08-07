# Harness derivation — mac-terminal — round 101

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent failure observability** — GET /journal at 2026-08-07T13:44Z reports 120 retained jobs, 146 actions, 18 failures, 79 writes, 0 undoable/undone, and 112 unattributed-tier jobs. Repeated browser_navigate fingerprint act_36a2da2b0b8c ran 8 times and failed 8 times; failures were Safari extension offline or 45-second timeout.
  - evidence: Authenticated GET /journal response and GET /jobs response in Round 101.

## Capabilities it proposed

### "“If something you delegated fails, recover it without making me repeat myself, and tell me only when you need my help.”"
- **useful because:** The live journal shows 18 failed actions, including eight repeated browser navigations with the same idempotency key and 45-second extension timeouts. Today the system records the failure but leaves the owner to diagnose Safari, retry, or choose another surface. A cross-surface recovery coordinator can inspect health, classify the failure, avoid retry storms, switch public work to the server browser, reattach private work to Safari, and return one concise spoken status.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Deterministic failure taxonomy and retry/circuit-breaker first; background gpt-4.1-mini for a short recovery plan; planner gpt-5.6-luna only for ambiguous multi-surface recovery or conflicting evidence. Realtime is used only to speak the final status if the owner is waiting.
- **latency:** Health and duplicate detection under 300 ms; deterministic retry or route switch under 2 s; background diagnosis under 5 s. Do not block the original action longer than its existing timeout. One spoken update on recovery, and one only if owner intervention is required.
- **cost:** Most incidents: $0 model cost via journal/health rules. Routine diagnosis roughly one small gpt-4.1-mini call (about 2–3k prompt tokens, 50–150 completion tokens); planner escalation only for ambiguous cases (about 8–10k prompt tokens). Dominant cost is resending job/error context, so pass compact typed receipts rather than full transcripts.
- **security:** Private Safari failures must remain on the Mac and never be sent to the public browser or relay prompt; classify session scope before fallback. Never replay a write after an unknown outcome; only retry idempotent reads or actions with an explicit receipt showing no effect. Preserve the owner's maximum-access policy—this is observability and recovery, not a new approval gate. Expose the exact failure, route chosen, and whether anything changed.
- **missing:** A read-only browser/Safari health signal with extension polling age, active tab/session, modal/page-load blockage, and a bounded action capability matrix; A durable recovery state machine with per-action idempotency and an unknown-outcome state, plus a circuit breaker keyed by session and action type; A route-switch adapter that can send public tasks to Cloudflare Browser Run while pinning authenticated tasks to the Safari bridge; A compact pendant event/voice status contract for recovered, waiting-for-owner, and permanently-failed outcomes

### "“Why did you do that, and what would have happened if you had chosen differently?”"
- **useful because:** Today the owner can see individual job receipts, but cannot trace one spoken request through relay routing, planner decisions, browser tabs, Mac actions, evidence, and the final outcome—or compare the chosen route with safe alternatives. A cross-surface causal replay would make the hive understandable and let the owner correct bad assumptions without reconstructing events from logs.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Deterministic event graph assembly and counterfactual inventory first. Use background gpt-4.1-mini to summarize the causal chain; use planner gpt-5.6-luna only when the owner asks for a genuine counterfactual involving ambiguous intent or multiple possible workflows.
- **latency:** The event chain should be queryable in under 500 ms from local records. A concise spoken explanation should arrive in under 5 seconds; deeper counterfactual analysis may take 10–20 seconds and should be explicitly requested.
- **cost:** Basic provenance lookup has no model cost. A normal explanation costs one small background call with roughly 2–4k compact event tokens and under 200 completion tokens. Counterfactuals cost one planner call, dominated by reconstructing the relevant decision context rather than by the final response.
- **security:** Authenticated URLs, typed text, shell commands, and page contents must remain local or be represented by redacted hashes and short owner-approved excerpts. Counterfactuals must be labeled as hypothetical, never presented as actions that occurred. The replay must be append-only and tamper-evident so explanations cannot silently rewrite history.
- **missing:** A cross-surface causal event schema linking utterance, routing decision, model call, action, evidence capsule, receipt, and outcome; Immutable correlation IDs propagated from pendant request through relay, Mac jobs, browser commands, and returned audio; A local redacted replay store with retention and owner deletion controls; A counterfactual planner interface that can enumerate alternatives without executing them; Dashboard and pendant views that present a short causal chain first and details on request


## Changes it proposed to its own stack

### `mac-harness` — Extend every Mac/browser action receipt into a compact execution trace: normalized action fingerprint and idempotency key, surface/session/tab, planner tier and model, queue/start/extension-response timestamps, timeout phase, effect certainty (no-effect/changed/unknown), and recovery eligibility. Persist the trace in the existing job record and expose filtered summaries through /journal and /logs; aggregate by fingerprint so repeated failures become one incident instead of dozens of opaque jobs. Redact command arguments, URLs, and typed text by default while retaining hashes and owner-visible labels.
- **owner gets:** When a task fails, the owner can immediately hear or see whether Safari was offline, stuck on a dialog, timed out after execution, or never started—and whether retrying is safe. It also makes the system stop wasting time on the same failing browser navigation and makes model cost and latency attributable instead of reporting 112 unattributed jobs.
- effort: Medium: receipt schema migration, executor instrumentation around local-agent/browserBridge calls, journal aggregation, and a small dashboard/pendant formatter. Existing receipts and journal provide the storage and read-only surface; no action gate is required.  ·  risk: Older jobs will lack fields and must render as unknown. Incorrect effect certainty could cause an unsafe retry, so unknown must remain non-retryable. Hashing must be stable without leaking secrets; retain raw details only in the local job store under existing access. Recover by falling back to legacy receipt rendering if migration fails.
- cost: Negligible API cost; a few hundred bytes per action and modest local JSON/D1 growth. Aggregation reduces future planner prompt tokens by sending one incident summary rather than repeated full errors.  ·  latency: Under 5 ms local instrumentation per action; /journal aggregation may add tens of milliseconds. No extra network round trip on the execution critical path.
- security: Improves auditability without narrowing the owner's deliberate FULL_CONTROL_MODE. Default redaction prevents shell command contents, authenticated URLs, and form text from entering relay/model prompts; exact data remains local for debugging.
- depends on: Existing actionReceipts/jobTracker and /journal implementation; A stable action/session fingerprint convention shared by Mac and browser bridges; Dashboard or pendant status formatter consuming the new typed fields


## What it asked for

_Nothing._
