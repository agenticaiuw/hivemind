# Harness derivation — mac-terminal — round 91

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-browser-recovery** — At 2026-08-07T13:05Z the Mac agent is full-control and relay-connected, but browser extension is offline with 7 pending commands. The same browser_navigate idempotency key failed 6 times; one waited 45 seconds before timing out. /journal exposes receipts, but totals show 112 actions unattributed to a routing tier and 0 undoable actions.
  - evidence: Authenticated GET /ops/status, GET /journal, GET /jobs, and GET /routing responses in Round 91.

## Capabilities it proposed

### ""Keep trying that browser task, and tell me on the pendant when it actually succeeds.""
- **useful because:** Today a browser command can sit for 45 seconds, fail while the extension is stale, and leave seven pending commands. This lets the owner delegate the waiting: the Mac observes extension recovery, retries only the safe/idempotent step, and the relay delivers one concise success or an actionable failure to the pendant without another conversation turn.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Background model for retry classification and a final short status; deterministic local logic for heartbeat, queue reconciliation, and idempotent retry. Use realtime only to speak the result when the owner is actively listening.
- **latency:** Immediate acknowledgement under 1 second; heartbeat checks every 5–15 seconds while a task is pending; speak within 2 seconds of a confirmed result. Stop after a bounded deadline set by the owner.
- **cost:** Near-zero when healthy (local status checks). One small background-model call only for ambiguous failure classification or final wording, roughly 2k–4k prompt tokens; realtime/TTS cost only if spoken immediately.
- **security:** Authenticated browser session contents stay on the Mac/browser bridge and are not sent to the relay. Relay receives job id, health state, typed outcome, and a redacted summary. Never retry clicks, submits, purchases, or other non-idempotent writes automatically; expose receipts and require the owner's existing conversational authorization for a new write.
- **missing:** Durable retry/watch state that survives local-agent restart and relay reconnect; Browser command acknowledgement with command age and idempotency classification; A scheduler/heartbeat worker that can wake on browser reconnection; Relay event routing from job completion to the pendant pipeline; A compact owner-facing policy for retry deadline and safe action types

### ""Make this Mac ready for you to control, and tell me exactly what I still need to click.""
- **useful because:** The owner currently cannot tell why the agent is not ready: live status reports Accessibility and Screen Recording missing even though most automation grants are present. A pendant-initiated readiness check would turn a mysterious failure into a guided, verified setup, then confirm when visual and control capabilities are genuinely available.
- **path:** pendant → relay → mac-planner → mac-vision → dashboard-ux
- **model tier:** Deterministic checks and routing for known permission states; background model only to turn the state into a short spoken checklist. Realtime is used only for the live pendant response.
- **latency:** Return the first diagnosis in under 3 seconds; launch the relevant System Settings pane immediately; re-check after the owner returns, with no polling longer than 30 seconds unless explicitly requested.
- **cost:** Usually zero model calls because /ops/status already provides structured permission state. One short background response when the state is ambiguous; dominant cost is local verification and the owner's manual click, not API usage.
- **security:** The agent must not claim permissions were fixed until a fresh local check verifies them. Opening Settings is reversible, but changing privacy permissions remains an explicit owner action inside macOS. Send only boolean permission states and remediation URLs to the relay; never transmit screen contents or permission databases.
- **missing:** A permission-remediation contract mapping each missing capability to an exact macOS System Settings destination and a post-click verification probe; A local verification event emitted when Accessibility or Screen Recording changes, rather than requiring blind refreshes; A readiness capability matrix shared by mac-planner and mac-vision so the planner can select a non-visual fallback honestly; A pendant/dashboard checklist that preserves which steps were completed across relay reconnects


## Changes it proposed to its own stack

### `mac-harness` — Add a non-blocking execution preflight and failure-aware recovery ledger for cross-surface actions. Before dispatching browser_* work, sample the existing browser status/heartbeat state and attach a health snapshot (online, lastSeenAt, pending count, tab/session affinity) to the job. If offline or stale, fail fast with a typed reason instead of waiting 45 seconds; if online but a command times out, record one bounded retry only after a fresh heartbeat, then persist a recovery hint for the relay/pendant. Drain or expire stale queued commands by idempotency key so an extension reconnect cannot replay obsolete work. Keep FULL_CONTROL_MODE and all action permissions unchanged; this is observability, faster failure, and recovery, not a gate.
- **owner gets:** Browser requests would stop hanging for nearly a minute and then silently repeating. The pendant could say immediately whether the browser is disconnected, retry once when it genuinely returns, and avoid acting on stale commands after reconnection.
- effort: Medium: browser health snapshot in jobTracker/executor, typed failure states and bounded retry, plus queue expiry keyed by idempotencyKey; dashboard/relay rendering is a smaller follow-up.  ·  risk: A transient extension stall could be classified as offline or a retry could duplicate a non-idempotent action. Restrict automatic retry to reads and actions explicitly marked idempotent; preserve the existing receipt and expose every retry. Recovery is to rerun from the durable job record.
- cost: Negligible API cost; saves model turns and local wait time. Small persistent metadata increase per job (health snapshot and retry record).  ·  latency: Healthy browser actions add only a local status check; stale/offline actions return in under a second instead of ~45 seconds.
- security: No new authority or data egress. Health metadata contains extension/tab state and should remain in the authenticated local journal; do not include page contents in failure telemetry.
- depends on: Existing GET /browser/status and POST /browser/heartbeat routes; Existing GET /jobs, GET /jobs/:jobId, receipts, journal, and idempotency keys; Browser extension emitting reliable lastSeenAt/command acknowledgement


## What it asked for

_Nothing._
## Its own summary

Round 91 discovery is complete. Live observability confirms the Mac agent is in deliberate FULL_CONTROL_MODE and relay-connected, but it is not operationally ready (Accessibility and Screen Recording are missing), the browser extension is offline with 7 queued commands, and one browser navigation has failed repeatedly with ~45-second waits. I recorded this finding, notified the browser-extension agent, and proposed (1) a non-blocking browser health/preflight and queue reconciler that preserves maximum authority, and (2) a pendant command to keep retrying safe browser work until success with durable relay notifications. The newly granted mac_read_diagnostics tool is still schema-only and returned no implementation.

**Biggest unknown:** Whether the orchestrator will implement durable retry/watch state and reliable browser command acknowledgements, and whether Accessibility/Screen Recording are intentionally unavailable or simply not yet granted. I still need a working read-only Mac diagnostics implementation and the local-agent job lifecycle contract to validate recovery end to end; those requests are already pending and should not be re-issued.

