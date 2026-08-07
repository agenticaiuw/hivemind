# Harness derivation — mac-planner — round 123

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-control-plane** — At 2026-08-07T13:55Z the Mac agent reports browser online with 9 pending commands, but the sole device home-chrome has tabId, tabUrl, tabTitle, tabCount, userAgent, browserName, and extensionVersion all empty/null. The durable journal reports 146 actions, 18 failed, 112 unattributed, and repeated browser_navigate failures including 45-second waits and offline/blocked-dialog errors.
  - evidence: GET /ops/status, GET /browser/status, GET /journal, and GET /jobs probed in Round 123.

## Capabilities it proposed

### "“If you’re checking something in my logged-in browser and it goes offline, keep the task safe, tell me what paused, and resume it when the right tab comes back—without repeating steps.”"
- **useful because:** Today the control plane claims the browser is online while exposing no tab identity, leaves 9 commands pending, and has repeated navigate failures/timeouts. This gives the owner a truthful spoken status and continuation across a sleeping Mac, instead of hangs, lost work, or accidental replay. It only works as a hive feature: the relay/pendant keeps the intent alive, the Mac owns the private session, the browser extension proves the tab, and the server reconciles evidence.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the cheaper background model for queue reconciliation, heartbeat classification, retry planning, and evidence summaries; use realtime only to answer the owner’s immediate “what happened?” question on the pendant.
- **latency:** Immediate pause notice under 2 seconds after a failed heartbeat; resume within one heartbeat (roughly 10–30 seconds) after a valid tab-bearing lease. No 45-second blocking wait.
- **cost:** Usually <$0.01 per paused/resumed task; dominant cost is background summarization only when evidence changes, not heartbeats or receipts.
- **security:** Private page content and session cookies remain in the browser/Mac path; the relay receives status, identifiers, and redacted evidence hashes by default. A stale lease must never run commands, and private work must not fail over to a public browser backend. Mutating steps retain existing owner maximum-access policy, but idempotency and before/after receipts are mandatory.
- **missing:** Browser lease epoch and real-tab heartbeat validation; Stale-command quarantine/requeue state machine; Durable browser job runner with resumable result stream; Pendant notification adapter for pause/resume receipts; Dashboard view for quarantined commands and reconciliation history

### "“Do this in the background without interrupting me; only speak up if it becomes urgent, otherwise leave me a complete review packet when I’m free.”"
- **useful because:** Today a long Mac/browser operation either occupies the conversation with failures or finishes without a consistent owner-ready handoff. The owner should be able to delegate while working, commuting, or sleeping and receive exactly one appropriately timed result: urgent exceptions immediately, routine completion as a cited packet when their attention window opens.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic routing and a cheaper background model for progress classification, urgency scoring, and packet assembly; reserve realtime for an actual urgent interruption or when the owner asks for the result.
- **latency:** Acknowledgement within 2 seconds. Background work may run for hours. Urgent escalation within 10 seconds of a verified blocking or high-impact event; routine results wait for the next declared attention window.
- **cost:** Typically under $0.02 per delegated task; most work is local state and receipts. Model cost is concentrated in the final synthesis or an urgent spoken escalation.
- **security:** The relay stores only task metadata, urgency state, and redacted result references by default. Full private browser/Mac evidence remains local and is revealed only when the owner opens the packet. The system must never infer urgency from sensitive content without an explicit owner policy, and mutating actions retain the owner’s existing maximum-access policy.
- **missing:** Per-task interruption contract (quiet hours, urgency threshold, attention-window source, escalation channel); A cross-surface event severity taxonomy shared by Mac jobs, browser results, and relay; Durable review packets linking action receipts, evidence capsules, failures, and next steps; Attention-window resolver using Calendar/foreground state and pendant availability; One-shot deduplication so retries and reconnects cannot produce repeated spoken alerts


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-device lease and command-reconciliation layer. Treat a heartbeat as valid only when it carries a fresh device epoch plus a real tab/window identity and capability hash; mark the current home-chrome lease stale when tabId/tabUrl/tabCount are null or the heartbeat expires. Move commands claimed by that lease into a quarantined state (never execute them on a later device by accident), then requeue them with the same idempotency key only after a new valid heartbeat. Emit one durable reconciliation record per command with claimed lease, quarantine reason, retry count, and final disposition, and expose a compact status endpoint for the pendant/Mac planner. This is the missing control plane beneath the still-unbuilt durable browser runner—not an approval gate.
- **owner gets:** The owner stops seeing 45-second hangs and silent duplicate browser actions. If Safari/Chrome sleeps or a dialog blocks it, the pendant can say “paused, 9 commands preserved; resumed at 2:14” and continue safely when the real tab returns, rather than treating a ghost device as online.
- effort: Medium: browser bridge heartbeat schema and lease store, queue state transition/reconciliation endpoint, planner notification adapter, and restart tests.  ·  risk: A too-strict heartbeat could pause valid work; recover by allowing an explicit device re-announce and operator-visible requeue reason. Never auto-fail private work to the public relay, which cannot hold the owner’s login session.
- cost: Negligible API cost; a few D1/local JSON writes per heartbeat and command transition.  ·  latency: Heartbeats remain cheap; failed commands return a fast paused/quarantined result instead of waiting 45 seconds. Resume adds only one heartbeat interval.
- security: Improves session safety: stale leases cannot execute, idempotency keys prevent replay, and private URLs/results stay on the authenticated browser path.
- depends on: chg-14accc01’s existing request IDs/idempotency/tab affinity (progressive polling remains unfinished); chg-16bc5dee’s durable browser runner and result stream; browser extension must emit a real tab-bearing heartbeat

### `model-routing` — Make execution routing liveness-aware before invoking the expensive realtime tier: consult the browser lease/status and Mac bridge readiness, classify each planned step as ready, wait-for-device, or blocked, and hand wait-for-device work to a durable background lane with a bounded exponential retry schedule. Realtime should answer immediately with the classified state and receipt ID, not sit on a 45-second browser wait. When readiness changes, send only the delta back to the planner and pendant.
- **owner gets:** Requests feel immediate and honest: “I can do this when Chrome reconnects” replaces a long silence, while the owner’s battery and attention are not spent on repeated failed attempts. They also get one completion message rather than multiple duplicate failure notices.
- effort: Medium: a preflight classifier, routing metadata in job records, background wake/retry trigger, and a small event-to-pendant adapter.  ·  risk: A readiness check can be briefly stale; the executor still verifies the lease immediately before each action and records any mismatch. If the background lane is unavailable, the task remains visibly paused rather than being discarded.
- cost: Reduces GPT realtime usage and browser timeout work; background classification can use a low-cost model or deterministic rules. Storage/event costs are small.  ·  latency: Immediate acknowledgement under 1–2 seconds; successful work is unchanged, unavailable work waits without blocking the conversation.
- security: No additional page data needs to leave the Mac. Routing sees only readiness, origin (private/public), and task metadata; private pages remain pinned to the authenticated browser.
- depends on: Browser lease/quarantine change proposed this round; GET /routing and GET /ops/status; GET /browser/status and POST /browser/heartbeat; POST /jobs and GET /jobs/:jobId; POST /pipeline/events

### `interaction` — Add an explicit interruption contract to every delegated task: quiet/until-time, urgent-only, or conversational. Compile that contract once at task creation, propagate it through relay, Mac jobs, browser commands, and receipts, and collapse all retries/reconnects into one owner-visible state machine. At completion, materialize a review packet containing outcome, evidence links, failures, and recommended next action; deliver it through the pendant only when the contract permits, otherwise expose it at the next attention window.
- **owner gets:** The owner can delegate real work without being nagged, lose neither failures nor completions, and review one trustworthy packet instead of reconstructing a task from scattered spoken alerts, browser tabs, and Mac logs.
- effort: Medium-high: shared task contract schema, event severity/deduplication, packet renderer, and attention-window integration across relay and Mac.  ·  risk: Incorrect severity could delay an important alert. Recover with a persistent dashboard badge, an always-available “what’s waiting?” query, and a hard upper bound after which a quiet task becomes a review item rather than an unspoken failure.
- cost: Low storage and event cost; cheaper background synthesis replaces repeated realtime narration. No new per-task realtime call unless escalation occurs.  ·  latency: Delegation acknowledgement remains near-instant; routine narration is suppressed, while urgent events are pushed promptly and completion packets are ready at the next review point.
- security: Contracts and packet metadata may cross the relay, but private evidence remains local or redacted until explicitly requested. The contract controls delivery timing, not authorization to perform actions.
- depends on: Durable task identity shared by relay, Mac jobs, and browser commands; A typed event severity/deduplication stream; Calendar/foreground/pendant attention-window signals; Existing action receipts and evidence capsules


## What it asked for

_Nothing._
