# Harness derivation — faculty-action — round 96

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask “did that happen?”, give me a proof-backed answer across my Mac, browser, relay, and pendant—what was only queued, what executed, what was delivered, and what cannot be verified—then offer the safest next step."
- **useful because:** Current receipts can say a Mac action succeeded even when browser is offline, Mac input is unavailable, or pendant playback was never acknowledged. The owner needs an honest answer about real-world effect, not an optimistic job result. This is uniquely cross-device: the Mac knows execution, the browser knows tab/session delivery, the relay knows accepted audio, and the pendant must provide physical delivery/playback evidence.
- **path:** mac-planner → browser-extension → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action → pendant
- **model tier:** Use the realtime model only for the owner's immediate spoken question; use a cheaper background verifier to join receipts and telemetry, and never infer delivery from missing evidence.
- **latency:** Spoken answer within 2 seconds from cached evidence; refresh Mac/browser/relay evidence asynchronously when stale and follow up when it changes.
- **cost:** Low per query (mostly local D1/JSON joins); occasional background refresh dominates, not model tokens.
- **security:** Evidence may contain private URLs, page text, file paths, and message metadata; retain hashes and minimal snippets, redact secrets, bind every fact to job/action/device identity, and require confirmation before any retry or compensating action.
- **missing:** A shared execution-state schema with queued/accepted/executing/executed/delivered/played/failed/unknown states; Authoritative pendant delivery and playback acknowledgements with device clock/source timestamps; A cross-surface evidence joiner that distinguishes live evidence from historical records and expires stale claims; A retry/repair planner that treats unknown as unknown rather than success

### "Before you carry out a consequential request, show me the likely cross-device state change; afterward, show me the actual state delta attributable to this action, including unexpected side effects, without relying on the app's claim that it succeeded."
- **useful because:** Today the system can report that an action returned successfully, but it cannot establish what changed because of the action across files, browser sessions, messages, calendars, relay jobs, and pendant output. A causal before/after view would let the owner catch wrong-recipient, wrong-account, duplicate, and partial-completion failures even when ordinary receipts look green.
- **path:** faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime → pendant → unified
- **model tier:** Use a cheaper background/read-only observer for snapshots and diffing; reserve the realtime model for explaining the resulting delta to the owner.
- **latency:** Read-only preflight under 3 seconds for common actions; post-action delta within 5 seconds, with slower reconciliation for external services.
- **cost:** Low-to-moderate storage and API cost for compact typed snapshots; model cost is limited to unusual diffs and owner-facing explanations.
- **security:** Snapshots may contain private page text, files, recipients, and account state. Store minimized typed fields and hashes rather than raw content, encrypt retained deltas, enforce job ownership, and require confirmation whenever the predicted delta includes an irreversible or external side effect.
- **missing:** A cross-surface causal snapshot format with field-level hashes and provenance; Read-only observers for external account state and pendant output state; Correlation IDs propagated from intent through every action and resulting event; A delta classifier that separates expected, incidental, and unexplained changes


## Changes it proposed to its own stack

### `integration` — Build an evidence ledger and receipt reducer spanning Mac jobs, browser commands, relay pipeline events, and pendant telemetry. Every event gets a monotonic event ID, source/device identity, source timestamp plus ingestion timestamp, job/action/artifact linkage, and one of queued/accepted/executing/executed/delivered/played/failed/unknown. Reducer rules must never promote state from historical acceptance or timeout; stale or contradictory sources produce unknown with reasons. Expose a per-action timeline and freshness badge through the existing job receipts/ops snapshot, and let faculty-action request a retry only after faculty-judgement sees the explicit unknown state.
- **owner gets:** The owner will stop being told “done” when a command is merely queued, a browser is offline, Mac input cannot reach the UI, or speech was accepted by the relay but never played on the pendant. They get a truthful, actionable status and can safely retry or wait.
- effort: Medium-high: shared event schema and persistence, reducer tests for contradictory/out-of-order events, adapters for four producers, dashboard and spoken summary formatting.  ·  risk: Clock skew, duplicate events, and partial outages can create unknown states; recover by using server ingestion ordering, idempotency keys, bounded reconciliation, and preserving raw evidence for audit. Never auto-retry irreversible actions.
- cost: Small D1/JSON storage and background CPU; negligible model cost because summaries can be generated from typed state, with realtime model only for conversational explanation.  ·  latency: Cached status is immediate; fresh reconciliation typically adds under 1–3 seconds and should not block an already completed local action.
- security: Cross-surface evidence joins private URLs, paths, and audio metadata; encrypt or minimize payloads, hash content where possible, enforce per-owner job access, and redact secrets before relay/dashboard projection.
- depends on: Pendant-side authoritative delivery/playback acknowledgements; A durable browser command/result identity and tab affinity (existing queue is offline with pending commands); Relay pipeline telemetry carrying device identity and source timestamps; Integration hooks in actionReceipts.js and browser result handlers

### `integration` — Add a causal-state layer around each plan: capture a minimal, provenance-tagged read-only baseline immediately before execution; propagate one correlation ID through Mac action receipts, browser command/results, relay pipeline events, and device acknowledgements; capture the same typed fields afterward; and compute an expected-versus-observed delta. Mark fields as expected, incidental, unexplained, or unverifiable. For external services, use field hashes and stable identifiers rather than retaining page contents. Expose the preflight prediction and postflight delta as a signed artifact attached to the job, not as an inferred sentence in the model prompt.
- **owner gets:** The owner can see exactly what changed due to an instruction and spot duplicate sends, wrong targets, partial execution, or unexpected account/file changes—even when an application and the local executor both claim success.
- effort: High: define typed snapshot adapters, correlation propagation, field-level provenance, diff classification, retention limits, and adversarial tests for retries, concurrent changes, and stale browser tabs.  ·  risk: Unrelated changes may occur between snapshots, and external systems may hide state. Preserve uncertainty rather than attributing it; use narrow observation windows, stable IDs, server timestamps, and an explicit 'could not attribute' result. Never block emergency read-only actions on a complete baseline.
- cost: Moderate local storage and API reads; compact hashes keep retention inexpensive. Occasional background reconciliation costs less than realtime inference.  ·  latency: Adds roughly 1–5 seconds around consequential actions; read-only actions can use asynchronous postflight diffing.
- security: Baseline and delta artifacts can reveal sensitive account state. Minimize fields, hash content, encrypt artifacts, enforce per-job access, and automatically expire raw observation material.
- depends on: A shared correlation ID propagated across all surfaces; Read-only state adapters for Mac, browser, relay, and pendant; Authoritative device acknowledgements where physical output is claimed; A typed provenance and freshness policy


## What it asked for

_Nothing._
