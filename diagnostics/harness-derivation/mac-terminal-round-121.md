# Harness derivation — mac-terminal — round 121

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac/browser observability round 121** — Mac agent v0.5.0 and relay are reachable; fullControlMode and planner are enabled, but computer-use loop is disabled because Accessibility is untrusted and Screen Recording is missing. Browser extension home-chrome is offline with 12 pending commands. /journal reports 120 retained jobs, 140 actions, 25 failures, 0 undoable, and 111 unattributed tiers; repeated browser_navigate key has 11/11 failures.
  - evidence: GET /ops/status, GET /browser/status, GET /journal at 2026-08-07T14:54Z

## Capabilities it proposed

### "From the pendant, run the task across my Mac and browser, then tell me whether it really completed; if a transient bridge or command failure occurs, retry safely and show me the exact failed step."
- **useful because:** Today the hive can enqueue and receipt actions, but browser is offline with 12 pending commands and recent browser navigation has failed repeatedly. The owner needs one truthful end-to-end result, not a plan that looks successful while a bridge is stale.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime tier only to interpret the spoken request and narrate status; use a cheaper background worker for polling heartbeats, retry classification, and receipt synthesis.
- **latency:** Acknowledge immediately; first status within 2 seconds; allow up to 30 seconds for bridge recovery and bounded retries, then report blocked with the exact step.
- **cost:** Low per invocation: one realtime turn plus inexpensive background polling; dominant cost is any browser vision/screenshot step, which should only run when DOM/typed actions cannot verify state.
- **security:** Authenticated browser content and local command output must stay on-device or in the authenticated relay; redact secrets from receipts. Never replay stale queued browser commands during recovery; require explicit user intent to discard or replay them.
- **missing:** Browser heartbeat adapter that actually runs and reconciles stale pending commands; Durable cross-surface job state machine with retry classification and terminal verified/blocked states; Correlation IDs and redacted shell/browser receipts; Accessibility and Screen Recording permission for actual AI Pendant Agent if UI/vision fallback is needed

### "When I tell the pendant “handle this when my computer is available,” save the intent, then later continue across my Mac and authenticated browser—even if both are offline now—and tell me what changed, what was skipped, and why."
- **useful because:** Today an unavailable bridge turns a spoken request into a dead end or stale queued commands. The owner should be able to delegate deferred work while away from the desk, without losing the request or having old clicks replay unexpectedly when connectivity returns.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime model only to capture and clarify the intent and announce completion. Use a cheaper background model for deferred planning, readiness polling, conflict detection, and concise result synthesis.
- **latency:** Capture and confirmation in under 2 seconds. Resume automatically when required surfaces are healthy; tolerate hours or days of delay. Notify only on completion, an ambiguity requiring the owner, or an expired/blocked intent.
- **cost:** Low per request: one realtime capture plus inexpensive scheduled readiness checks; background model cost is dominated by replanning after the Mac project or browser page changes. No vision calls unless structured verification fails.
- **security:** The relay must store an encrypted intent envelope, not page contents or shell output. At resume time, re-check browser origin, tab/session identity, Mac project path, and authorization state; never reuse expired login state or blindly replay mutations. Require a fresh spoken confirmation only when the original intent was ambiguous or its risk materially changed.
- **missing:** An encrypted durable intent envelope with owner-approved expiry, prerequisites, and semantic idempotency key; A cross-surface wake/resume scheduler that waits for Mac and browser readiness instead of emitting commands into an offline queue; Conflict-aware replanning that compares the original assumptions with current tabs/files before acting; A pendant notification protocol for deferred completion, blocked state, expiry, and required clarification

### "Keep my Mac and authenticated browser in sync after a multi-step request—for example, if you book something in the browser and add it to Calendar—then detect partial completion, repair the missing side, and tell me exactly which sides succeeded."
- **useful because:** The owner cannot reliably ask the hive to perform work spanning a logged-in browser and local Mac today: one side can succeed while the other fails, leaving duplicate bookings, missing calendar entries, or an apparently finished job with no trustworthy reconciliation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles only the spoken request and final explanation. A cheaper background planner maintains the task's intended facts, compares receipts from both surfaces, and performs idempotent reconciliation; reserve the expensive vision model for ambiguous browser state.
- **latency:** Speak an immediate accepted/blocked acknowledgement; complete ordinary reconciliation within 30 seconds after both surfaces respond. If a side remains unavailable, persist a partially-complete state and notify on recovery rather than looping.
- **cost:** Low-to-moderate: background reasoning and receipt polling dominate; browser vision is exceptional. Local fact/receipt storage is small, with no need to resend full page contents.
- **security:** Do not infer success from a click alone. Require typed evidence (URL, event ID, record ID, or local object identifier), scope reconciliation to the intended account and time window, and never undo an externally committed booking automatically. Keep authenticated page data and calendar details encrypted and local/relay-protected.
- **missing:** A cross-surface intent/fact ledger that records expected postconditions and evidence requirements; Adapters that expose stable external identifiers for browser results and Mac Calendar/Reminder mutations; A reconciliation planner with idempotency and non-destructive conflict handling; Dashboard and pendant language for partial, repaired, conflicted, and externally-committed outcomes


## Changes it proposed to its own stack

### `browser-harness` — Add a stale-command quarantine ledger, separate from the pending browser queue: when an extension misses heartbeat, freeze delivery; assign each queued command an enqueue timestamp, originating utterance/job ID, tab/session affinity, and expiry; on reconnect, atomically classify each as safe-to-discard, safe-to-revalidate, or requires explicit replay. Revalidate tab URL/session and idempotency key before any replay, and expose a one-call pendant/dashboard summary plus discard-all-for-job operation. Do not execute or silently replay the current 12 pending commands.
- **owner gets:** The owner will not have yesterday's clicks or navigation suddenly execute when Chrome returns. They can see exactly what is stale, reconnect safely, and choose which unfinished task—if any—should resume.
- effort: Moderate: queue schema migration, heartbeat transition handling, atomic poll claim/release, session revalidation, and dashboard/relay projection.  ·  risk: A legitimate command may expire and need to be reissued; retain the original intent and reason so the agent can reconstruct it. A crash during reconnect could duplicate a command; use leases plus idempotency keys and write-ahead state transitions.
- cost: Negligible API cost; bounded local queue metadata growth. No hardware cost.  ·  latency: Adds one heartbeat/session validation round before replay, typically under 1 second; avoids expensive failed browser actions and vision retries.
- security: Reduces accidental actions in authenticated sessions and keeps stale command contents local; do not send page contents to relay during reconciliation.
- depends on: Existing browser pending queue, /browser/status, /browser/heartbeat, /browser/poll, /browser/result/:commandId; A durable job/receipt correlation ID from the Mac relay


## What it asked for

_Nothing._
## Its own summary

Fresh live discovery: Mac/relay are healthy and reachable, but the browser bridge is offline with 12 pending commands. Computer-use is disabled because the actual AI Pendant Agent lacks Accessibility and Screen Recording; automation grants are present. /journal shows 120 retained jobs, 140 actions, 25 failures, zero undoable, and 111 unattributed tiers; browser_navigate has failed 11/11 for one repeated key. I recorded this and proposed two non-gating improvements: (1) stale browser-command quarantine with leases, expiry, tab/session revalidation, and explicit replay/discard—never silently replay the current queue; (2) a cross-surface capability that gives the pendant a truthful verified/blocked outcome with bounded retries. The earlier generic shell telemetry proposal was rejected as already covered, so I did not duplicate it.

**Biggest unknown:** Whether the browser bridge can be made to emit a real heartbeat without opening the UI, and the exact durable job/receipt correlation contract needed to connect relay utterances to Mac and browser steps. I still need implementation of the heartbeat adapter/queue reconciliation and the durable cross-surface state machine; I do not need another permission request this round.

