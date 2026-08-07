# Harness derivation — faculty-action — round 53

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-action-safety** — As of 2026-08-07T11:38Z, the Mac agent is not ready for trustworthy GUI automation: fullControlMode and planner are enabled, but Accessibility trusted=false, Screen Recording=false, input reachability failed, and observe warns UI actions can report success while doing nothing. Computer-use loop is disabled; vision upload consent is false. Browser extension is offline with 4 pending commands.
  - evidence: GET /ops/status and GET /observe live responses

## Capabilities it proposed

### "“Stop everything you’re about to do, right now.”"
- **useful because:** A physical, offline-capable emergency stop is the missing safety hand on a system that can act through the Mac and private browser. One long press on the pendant should revoke pending browser/Mac jobs, cancel relay retries, close any staged transaction leases, and return a spoken receipt. It works even when the owner cannot reach the laptop or voice path.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No model for the stop path; pendant firmware emits a signed stop event, relay performs deterministic cancellation, Mac bridge and browser extension acknowledge. Use a cheap background model only to summarize what was halted afterward; never put an LLM in the stop decision.
- **latency:** Pendant LED/haptic acknowledgment under 150 ms locally; relay fan-out and Mac/browser acknowledgments under 2 s. If a surface is offline, mark it unacknowledged and keep retrying cancellation, but never claim it stopped.
- **cost:** Near-zero inference cost; roughly <1 cent per invocation for storage/events, dominated by durable relay writes and retries.
- **security:** The stop event must be authenticated to the paired pendant, replay-protected, and scoped to this owner's action namespace. It should cancel queued and leased work, revoke browser command tokens, and prevent new execution until explicitly re-armed. It cannot undo an already completed external side effect, so the receipt must distinguish cancelled, in-flight/unknown, and completed. Do not upload audio or screen data.
- **missing:** Pendant firmware emergency-stop event and local LED/haptic acknowledgment; Relay fan-out endpoint with idempotent cancellation and action-lease revocation; Mac executor and browser bridge cancellation checkpoints between every step, with acknowledgments; A re-arm flow requiring an intentional pendant gesture plus spoken/visual status; Dashboard showing per-surface stop receipts and any actions that were already completed

### "“Make sure this happens exactly once, even if I say it again or the connection drops.”"
- **useful because:** Today the pendant, relay, Mac planner, and browser bridge can retry or independently interpret the same request, creating duplicate reminders, purchases, messages, or form submissions. The owner should be able to delegate an intent with exactly-once protection: repeated speech, reconnects, and agent handoffs converge on one transaction and one honest outcome.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a deterministic intent normalizer and durable idempotency ledger on the relay; use a cheaper background model only to resolve genuinely ambiguous natural-language references. No realtime model is needed after the initial intent is formed.
- **latency:** A duplicate request should be recognized locally or by relay in under 300 ms; first execution may take normal task time. After a disconnect, resume from the durable transaction state rather than restarting.
- **cost:** Well under 1 cent per request for relay/database reads and receipts; cost is dominated by any ordinary browser or Mac execution, not deduplication.
- **security:** Idempotency keys must be scoped to the owner, intent, target account, and an explicit expiry so a future legitimate action is not suppressed. Store hashes and outcome metadata rather than sensitive page contents. Ambiguous target changes must create a new transaction and require review; never treat a failed/unknown external result as safe to repeat automatically.
- **missing:** A relay-owned durable intent ledger with states planned, leased, committed, failed, and unknown; Canonical idempotency-key derivation shared by realtime voice, Mac planner, and browser bridge; Commit tokens exchanged only after a verified external postcondition, with a reconciliation path for unknown outcomes; Execution adapters that accept and persist the key across retries and agent handoffs; Dashboard and spoken receipts that identify the single transaction and explain whether a repeated request was coalesced


## Changes it proposed to its own stack

### `integration` — Add a cross-surface action contract and verifier. Every planned Mac/browser step carries risk class, lease ID, preconditions, typed expected postconditions, observation recipe, timeout, and undo strategy. The executor must re-observe after each mutating step, compare typed fields (not screenshots alone), append before/after evidence to the receipt, and halt with an explicit mismatch state. Relay, Mac bridge, and browser bridge share the same lease and cancellation token so a stale or revoked plan cannot continue.
- **owner gets:** The owner can ask the mind to make real changes without silently drifting when a page, focused app, or UI state changes. They get an honest answer—completed, safely stopped, or uncertain—with evidence and a recovery path instead of a misleading success chime.
- effort: Medium-high: define contract/versioning, implement Mac and browser adapters, add observation recipes and mismatch states, then integration-test crashes, retries, stale tabs, and dropped pendant links.  ·  risk: A strict verifier will stop some actions that would have worked; recover by exposing the mismatch evidence and allowing a fresh re-plan. Never auto-retry an irreversible step after an ambiguous result. Existing legacy actions need an explicit unverified compatibility mode.
- cost: Small per-step storage and observation overhead; background validation can use a cheap model, while deterministic field comparison avoids inference cost. No new hardware required.  ·  latency: Adds roughly 100–500 ms per step for observation; much less than recovering from a silent bad action.
- security: Improves safety: leases, replay protection, scoped cancellation, and provenance. Screenshots/DOM snippets should be redacted and retained only under the existing short evidence TTL.
- depends on: Mac Accessibility and Screen Recording permissions being correctly granted to the running binary; Browser bridge online with request IDs and tab/session affinity; Durable job receipts and undo endpoints; A pendant-originated cancellation/revocation event

### `relay` — Create a relay-owned exactly-once intent ledger spanning voice turns, Mac jobs, browser commands, and reconnects. Normalize each approved intent into a canonical target/action hash, issue one transaction ID and lease, and require every surface to carry it. Retries return the existing receipt; only a verified commit advances the ledger, while ambiguous external outcomes enter reconciliation instead of being replayed. Expiry and explicit target changes create a new transaction.
- **owner gets:** The owner can repeat themselves or lose connectivity without wondering whether a message was sent twice, a form submitted twice, or a reminder duplicated. They receive one durable outcome tied to one request.
- effort: Medium: relay schema/state machine, adapters in Mac and browser executors, commit/reconciliation protocol, and failure-injection tests across dropped links and process restarts.  ·  risk: Over-aggressive normalization could merge two actions the owner intended separately. Mitigate with short intent windows, target/account scoping, and a spoken confirmation when confidence is below threshold. Unknown external outcomes must remain visibly unresolved.
- cost: Tiny D1/storage and hashing overhead; no new model call for ordinary requests.  ·  latency: One durable ledger round trip, typically tens to hundreds of milliseconds; retries become faster because they return the prior receipt.
- security: Reduces duplicate side effects but makes the relay authoritative for transaction metadata. Encrypt sensitive target identifiers, scope keys per paired owner, and enforce retention/erasure.
- depends on: A shared transaction ID accepted by Mac and browser action APIs; Durable relay storage and authenticated pairing; Typed external postcondition/commit reporting from each executor


## What it asked for

_Nothing._
## Its own summary

Discovered the live safety boundary and proposed two gaps beyond the backlog: a physical pendant emergency-stop that revokes relay/Mac/browser leases, and a typed cross-surface postcondition verifier that re-observes every mutation and halts honestly on mismatch. Informed mac-vision and faculty-judgement that current receipts are not trustworthy for GUI work because Accessibility and Screen Recording are absent, input reachability fails, computer-use is disabled, and the browser extension is offline with four queued commands. Recorded the live finding and told unified.

**Biggest unknown:** Whether the orchestrator can grant Accessibility and Screen Recording to the exact running AI Pendant Agent binary (not merely another installed binary), and whether the owner wants the emergency stop to cancel already-in-flight external requests or only prevent further steps.

