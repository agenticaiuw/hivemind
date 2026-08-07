# Harness derivation — mac-terminal — round 25

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent live readiness** — Current ops snapshot reports fullControlMode and planner enabled, but agent ready=false because Accessibility and Screen Recording permissions are missing; browser extension home-chrome is offline with 2 pending commands, while relay and Mac bridge are reachable.
  - evidence: GET /ops/snapshot HTTP 200 response at 2026-08-07T09:33Z: accessibility.trusted=false, screenRecording.granted=false, browser.online=false/pendingCommands=2, relay.reachable=true, macBridgeOnline=true.

## Capabilities it proposed

### "If I ask you to do something across my Mac and logged-in browser, just start it; if one part is unavailable, tell me exactly what is blocked, keep the rest moving, and resume automatically when that part comes back."
- **useful because:** Today a browser task can sit in a queue while the extension is offline, and the Mac reports missing Accessibility/Screen Recording permissions only as a generic not-ready state. The owner should get a useful spoken explanation instead of a 45-second failed attempt, while independent Mac/relay work continues and the browser step resumes without repeating completed work.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic capability preflight and job dependency scheduling first; use background gpt-4.1-mini only to summarize the blocked reason and next step, and realtime only for the owner's live spoken interaction.
- **latency:** Preflight and dependency split under 300 ms; pendant hears a blocked/continuing status within 1 s. Browser heartbeat retry every 5–10 s with exponential backoff; no model call on retries.
- **cost:** Near-zero for health checks/retries; roughly one background gpt-4.1-mini call (about 2k input tokens today) only when the user-facing explanation materially changes. Storage is a small durable job/dependency record and event log.
- **security:** Health data stays in the relay/Mac job metadata; do not transmit page contents or credentials in readiness events. Never replay a browser mutation automatically unless its idempotency key and prior receipt prove it did not complete; resume only at the first unacknowledged step.
- **missing:** A shared capability snapshot API consumed by relay and Mac planner, with explicit states for browser online/offline, permission missing, queue depth, and retry-after; A DAG-style job runner that splits Mac/browser/relay steps, persists completed receipt IDs, and reattaches a waiting browser step to the same authenticated session/tab; A browser reconnect handshake that drains or reconciles the 2 currently pending commands instead of allowing stale commands to execute blindly; Pendant event types for blocked, partial-progress, resumed, and permanently-failed jobs, plus a dashboard view of dependency and retry state

### "When I’m in a meeting or focused, keep the pendant silent and collect only genuinely urgent things; when I’m free, give me one short, prioritized catch-up, including anything the Mac or my logged-in browser discovered."
- **useful because:** The owner should not have to manually switch modes or receive fragmented alerts from separate agents. The pendant’s physical presence, Mac focus state/calendar, browser activity, and always-on relay can jointly infer an interruption budget and turn scattered events into one timely catch-up without losing urgent items.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Deterministic event correlation and urgency rules first; use a cheap background model to cluster and rank accumulated events; use realtime only when the owner explicitly asks for the catch-up or an urgent alert must be spoken immediately.
- **latency:** Mode changes reflected within 1–2 seconds; urgent alerts under 5 seconds; normal catch-up generated in under 10 seconds after the owner becomes available. No model call for ordinary mode transitions.
- **cost:** Low relay storage and event traffic; one small background ranking call per catch-up, typically far cheaper than a realtime turn. Retain event summaries and source links, not full page contents or audio.
- **security:** Calendar titles, browser page metadata, and focus state are sensitive and must remain in the owner’s encrypted account scope. Do not infer or announce sensitive meeting details aloud; announce only urgency and a neutral source label. The owner needs a physical pendant override to force quiet or urgent mode.
- **missing:** A shared interruption-state protocol with states such as available, focused, meeting, quiet, and emergency, including source confidence and expiry; A Mac focus/calendar signal adapter and browser event publisher that emit normalized, privacy-minimized events to the relay; Pendant-local quiet/urgent override and a durable on-device unread counter that works across a dropped link; Relay-side event deduplication, urgency policy, and release queue with explicit source links and dismissal state; A dashboard timeline showing why an item was held, surfaced, or suppressed, with per-source quiet rules


## Changes it proposed to its own stack

### `browser-harness` — Add a fail-fast preflight and reconciliation layer before browser actions are dispatched. The Mac bridge publishes a signed capability heartbeat (extension online, session/tab identity, queue depth, last-seen age); the relay planner converts an offline or stale heartbeat into a waiting dependency instead of sending the action. On reconnect, reconcile each queued command by requestId/idempotencyKey against browser receipts, mark completed commands, and execute only unacknowledged steps. Emit blocked/resumed/expired events to the pendant and dashboard.
- **owner gets:** A request will no longer burn 45 seconds and end in a generic browser-offline failure. The owner hears that the Mac portion is continuing, gets a precise recovery instruction, and the browser portion resumes safely after Safari is available without duplicate clicks or submissions.
- effort: Medium-high: bridge heartbeat and reconciliation protocol, relay durable dependency state, planner integration, pendant event plumbing, and tests for disconnects during navigation and submit.  ·  risk: A stale heartbeat could cause either unnecessary waiting or duplicate execution. Use short leases, monotonic command sequence numbers, idempotency keys, and receipt reconciliation; expire commands with an explicit explanation rather than guessing. Roll back by treating the runner as fail-fast as it is now.
- cost: Small D1/relay storage and heartbeat traffic; no additional model calls for retries. One background summarization call only when status needs natural-language explanation.  ·  latency: Adds under 300 ms preflight when healthy; avoids the current ~45 s timeout when offline. Reconnect latency is heartbeat interval plus one reconciliation round.
- security: Heartbeat carries capability/session metadata, never page text or credentials. Bind commands to authenticated extension ID plus tab/session lease; reject commands whose lease or idempotency scope has changed.
- depends on: Shared typed capability snapshot between Mac bridge and relay; Durable job dependency/receipt schema; Browser command request IDs and tab/session affinity (the still-open browser reliability change)


## What it asked for

_Nothing._
## Its own summary

Fresh live discovery found a concrete cross-node failure: the relay and Mac bridge are reachable, but the Mac agent is not ready (Accessibility and Screen Recording missing), the browser extension is offline with 2 queued commands, and browser attempts currently wait ~45 seconds before failing. I recorded this and proposed a new capability plus browser-harness change: health-aware dependency splitting, fail-fast browser preflight, durable receipt reconciliation, safe reconnect/resume, and pendant/dashboard blocked/resumed events. This is additive to the existing durable-job and browser-command proposals, not a restatement.

**Biggest unknown:** The granted Mac diagnostics schemas still have no implementation, so I cannot independently inspect host state through that tool. I still need the bridge/extension heartbeat and queue-reconciliation contract, a shared capability snapshot schema, and durable dependency/receipt primitives; the browser-extension agent has been asked to confirm its side.

