# Harness derivation — faculty-action — round 30

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current executor availability** — home-macbook-bridge is online, but home-chrome browser bridge is offline with zero tabs. Cross-surface actions therefore need explicit waiting/reconnect semantics rather than assuming browser execution is available.
  - evidence: discover(devices) Round 30 returned home-macbook-bridge online and home-chrome offline/0 tabs.

## Capabilities it proposed

### "When I say “take care of this when you can,” keep the task with you across disconnected devices: capture it on the pendant, do the work on my Mac and logged-in browser when they become available, and tell me on the pendant exactly what happened, what is waiting for approval, and how to undo it."
- **useful because:** Today the mind can decide a task but loses the handoff when the owner walks away, the Mac sleeps, or the browser bridge is offline. This creates one durable action thread spanning the always-on relay, wearable capture, Mac execution, and private browser session—without silently sending irreversible actions.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → mac-vision → dashboard-ux
- **model tier:** Use the realtime tier only to capture/clarify the short spoken intent and announce completion; use a cheaper background model for decomposition, retries, and receipt summarization. The relay persists a typed intent envelope; Mac planner selects the executor; browser extension handles authenticated pages; pendant is the notification/approval endpoint.
- **latency:** Pendant acknowledgement under 1 second, even offline (local queued receipt). Start execution within 30 seconds of Mac/browser availability. Each reversible step may retry in the background; irreversible browser submission pauses for explicit pendant or dashboard approval. Completion announcement should arrive within 2 seconds of a verified receipt.
- **cost:** About $0.01–$0.08 per task for background planning and summarization, plus negligible relay/storage; realtime cost is limited to the initial utterance and final short announcement. Browser and Mac work dominate wall-clock time, not tokens.
- **security:** Private page content must stay on the Mac/browser path and only extracted fields needed for the task may reach the relay. Bind the intent to the owner's device key, target account/session, and an expiry; never treat a reconnect as approval. Show before/after evidence for sends, purchases, deletions, or external submissions; require explicit approval and provide an idempotent undo where possible. If a device disappears, retain the task state but do not broaden permissions.
- **missing:** A durable cross-surface action envelope with idempotency key, expiry, owner approval state, and executor lease; Pendant-local offline intent spool and a reconnect/push protocol for task state and approval prompts; Relay scheduler that resumes jobs when Mac and browser bridge return, with per-step typed receipts and retry policy; Mac/browser executor handshake exposing availability, authenticated session identity, and safe pause points; A unified owner-facing action timeline on the pendant and dashboard, including approve/reject/undo; End-to-end tests for sleep, network loss, duplicate reconnects, stale browser tabs, and partially completed workflows

### "If a condition I care about happens, prepare the whole action and reach me wherever I am: for example, “if this flight drops below $800, check my calendar, hold the best option, and ask me on the pendant before buying.”"
- **useful because:** The owner cannot currently turn an intention about the future into a coordinated, bounded action. A relay can notice a public change, the Mac can reconcile local calendar and preferences, and the authenticated browser can prepare a private transaction—but no single node can safely carry the plan from trigger through a just-in-time approval.
- **path:** relay → mac-planner → mac-vision → browser-extension → pendant → dashboard-ux
- **model tier:** Use a cheaper background model for scheduled/trigger evaluation, option ranking, and preparation. Use realtime only when the pendant asks the owner for a concise final decision. Deterministic code should enforce thresholds, expiry, budget, and approval gates; the model must not be the authority for purchase or submission.
- **latency:** Trigger evaluation can run every 5–15 minutes or on a provider webhook. Prepare an option within 60 seconds of a qualifying event. The pendant approval prompt should arrive within 2 seconds once the private browser transaction is ready; expire the offer after a short owner-defined window.
- **cost:** Roughly $0.01–$0.10 per triggered evaluation depending on option count; public polling/provider webhooks and browser/Mac execution dominate cost. Most non-triggered checks should use deterministic comparisons and no model call.
- **security:** Never grant standing permission to buy or submit. Store the rule, threshold, maximum spend, allowed accounts, and expiry as structured policy; require fresh pendant approval tied to the exact displayed option and amount. Keep calendar and account data on the Mac/browser path, redact it from relay logs, and revoke a prepared hold if approval expires. Handle stale prices, duplicate triggers, timezone changes, and provider errors as safe pauses.
- **missing:** A durable conditional-plan schema with trigger source, predicate, evaluation history, expiry, and bounded action graph; Provider adapters or signed webhook/polling inputs for public conditions, with freshness and anti-spoof checks; A cross-surface planner that can query Mac-local state and prepare—but not submit—an authenticated browser transaction; A pendant push prompt that displays a compact, exact option/price and binds approval to its hash; A reservation/hold lifecycle with timeout cancellation, duplicate-trigger suppression, and clear owner receipts; Dashboard controls for creating, testing, pausing, and deleting conditional plans without exposing private credentials


## Changes it proposed to its own stack

### `relay` — Implement a cross-surface action envelope and lease protocol. Each spoken intent becomes a durable record {intentId, idempotencyKey, sensitivity, requiredCapabilities, approvalState, expiry, currentStep, ownerDevice}; executors (Mac, browser bridge, pendant) claim short leases and heartbeat them. Every step writes a typed receipt with input hash, target surface/session, before/after evidence, retryability, and undo reference. On reconnect, reconcile by idempotency key rather than replaying blindly; on lease expiry, pause steps marked irreversible and resume only after fresh capability/session checks.
- **owner gets:** A task will not vanish or run twice when the Mac sleeps, Wi‑Fi drops, or Safari reconnects. The owner gets an honest answer—done, paused for approval, or safely awaiting a device—instead of a vague failure, and can resume from the pendant without repeating completed work.
- effort: Medium-high: shared schema and D1/R2 persistence, relay scheduler, adapters in Mac and browser harnesses, pendant notification protocol, dashboard timeline, and failure-injection tests.  ·  risk: A bad reconciliation rule could duplicate an external action or falsely report completion. Mitigate with idempotency keys, explicit irreversible checkpoints, lease expiry pauses, append-only receipts, and a kill switch. Recover by marking the envelope conflicted and requiring owner review rather than guessing.
- cost: Small persistent storage and periodic heartbeat traffic; background model calls only for decomposition/receipt compression (~$0.01–$0.08/task). No realtime call during waiting or retries.  ·  latency: Immediate local acknowledgement; 0–30 seconds to resume after a device reconnect depending on polling/heartbeat. Extra preflight checks add roughly 100–500 ms before each external side effect.
- security: Improves security by binding work to device/session identity, limiting data to the executor that needs it, expiring stale approvals, and recording provenance. Requires careful protection of intent records and approval tokens.
- depends on: Pendant offline intent spool; Durable job runner and browser command queue; Typed context projection with sensitivity/TTL; Mac/browser capability and session-health handshake; Owner approval and undo UI


## What it asked for

_Nothing._
## Its own summary

Discovered the live executor state: the Mac bridge is online, while the authenticated browser bridge is offline with zero tabs. I proposed a new cross-device “take care of this when you can” capability and the concrete relay lease/idempotency protocol needed to make it safe: pendant capture and acknowledgement, durable relay job, Mac/browser resumption, explicit approval checkpoints, typed receipts, and undo/reconciliation after reconnects. I also recorded the current browser-offline constraint.

**Biggest unknown:** Whether the orchestrator’s newly granted firmware/build and accessibility permissions are actually active in this surface; the granted category currently reports empty, so I cannot verify implementation or run end-to-end tests. The action envelope still depends on the pendant offline spool, durable runner, executor handshakes, and approval UI.

