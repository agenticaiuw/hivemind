# Harness derivation — faculty-action — round 29

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **action-execution-readiness** — The live Mac agent is not ready: Accessibility and Screen Recording are untrusted/missing; browser bridge is offline with 3 pending commands. Recent browser_navigate jobs fail after roughly 45 seconds rather than being preflight-blocked. Relay and Mac bridge are reachable.
  - evidence: GET /ops/status returned ready:false, accessibility.trusted:false, screenRecording.granted:false, browserExtension.online:false, pendingCommands:3; GET /jobs showed browser_navigate failures with reason extension offline and ~45s durations.

## Capabilities it proposed

### "“Do this wherever you can; if a device is unavailable, keep going and tell me exactly what is blocked.”"
- **useful because:** Today the mind can decide an action but execution fails late and opaquely: the browser has three pending commands while offline, and the Mac agent reports ready:false because Accessibility and Screen Recording are missing. A cross-surface preflight would test reachability, permissions, session/tab affinity, and relay/pendant connectivity before acting; route safe steps to another surface, durably queue blocked steps, and return a compact owner-facing receipt naming completed, queued, and blocked work. This avoids 45-second dead-end browser attempts and makes unattended work trustworthy.
- **path:** faculty-judgement emits an action graph with required capabilities and reversibility → faculty-action runs a preflight against Mac agent /ops/status, browser heartbeat/status, relay job state, and pendant pipeline → browser-extension executes authenticated browser steps when online; mac-vision or mac-terminal handles equivalent Mac-local work when permitted → relay persists queued steps and wakes the pendant with a short status/receipt → pendant displays or speaks completed/blocked/needs-owner-attention summary
- **model tier:** Background planner for graph validation and recovery; realtime only for the owner's live clarification or confirmation. Deterministic health checks and routing should be code, not model calls.
- **latency:** Preflight under 1 second for local/relay health; if blocked, report immediately rather than waiting 45 seconds. Queue retries with exponential backoff and quiet hours; wake pendant only for urgent or completed outcomes.
- **cost:** Negligible model cost for deterministic preflight; roughly one background planning call only for ambiguous fallback routing. Dominant cost is durable storage and occasional TTS/audio delivery.
- **security:** Health metadata must not include page contents or secrets. Authenticated browser actions remain on the paired extension. Never bypass missing Accessibility/Screen Recording or confirmation gates; irreversible actions stay queued pending owner approval. Persist an audit receipt with required capability, route chosen, evidence, and retry history.
- **missing:** A shared action-graph schema carrying prerequisites, fallback routes, urgency, expiry, and approval state; A single preflight endpoint/SDK aggregating Mac readiness, browser online/session state, relay reachability, and pendant delivery; Durable queue with retry/dead-letter and dependency-aware resume (not just a browser command queue); Owner-visible blocked/queued receipt and pendant notification protocol; Automatic cleanup/reconciliation of the existing three stale browser commands

### "“Make this change everywhere it needs to happen, but leave my world consistent if one part fails.”"
- **useful because:** The mind can currently perform separate actions on the Mac, in authenticated browser sessions, and through the relay, but it cannot guarantee consistency across them. A single request such as updating a local project note, preparing a logged-in form, and recording the resulting reference can leave half-finished state when a surface disappears. The owner should get a cross-surface transaction: preview the complete change set, execute reversible steps under one transaction ID, verify postconditions on every surface, compensate completed steps when a later step fails, and report any genuinely non-compensable residue explicitly.
- **path:** faculty-judgement compiles the intended change into a typed transaction with invariants and compensation rules → faculty-action coordinates Mac file/note/reminder changes, authenticated browser mutations, and relay persistence under one transaction ID → browser-extension supplies before/after evidence and idempotent mutation handles for private pages → mac-vision or mac-terminal performs local changes with snapshots and restores when compensation is safe → relay stores the transaction journal and wakes the pendant with commit, compensated, or partial-failure status → pendant presents a terse completion state and offers owner confirmation for any residual irreversible step
- **model tier:** Use a cheaper background model only to translate an ambiguous goal into candidate steps and compensation plans; use deterministic code for transaction state, invariant checks, idempotency, and rollback. Realtime is only for live approval or clarification.
- **latency:** Preview in under 2 seconds for known actions; execute asynchronously when multi-step. The pendant should receive immediate accepted/running state and a final receipt when committed, compensated, or irreversibly partial.
- **cost:** Low model cost after planning; storage and evidence journaling dominate. A background planner call is needed only when step dependencies or compensations are ambiguous.
- **security:** Never claim atomicity for irreversible external effects such as sent mail, purchases, or submitted forms. Require explicit approval at the irreversible boundary, isolate secrets to their owning surface, encrypt the journal, redact page contents from relay receipts, and make compensation opt-in per action type. The owner must see exactly which effects are and are not reversible.
- **missing:** A cross-surface transaction/saga protocol with typed invariants, idempotency keys, leases, and compensation handlers; Snapshot/restore adapters for Mac files, notes, reminders, and browser fields; Postcondition verification primitives that can cite evidence from each surface; A durable encrypted transaction journal and reconciliation worker on the relay; UI and pendant vocabulary distinguishing committed, compensated, and irreversibly partial outcomes


## Changes it proposed to its own stack

### `relay` — Add a dependency-aware cross-surface action coordinator. Accept an action graph whose nodes declare required surface, reachability/permission prerequisites, reversibility, expiry, and approval. Run deterministic preflight probes before dispatch; execute ready nodes, persist blocked nodes with reason and retry policy, resume when heartbeats/permissions return, and emit one signed receipt containing per-node status and evidence. Reconcile and expire orphaned browser commands instead of leaving pendingCommands stranded.
- **owner gets:** A request will either finish, continue safely while they are away, or explain the exact blocker immediately. The owner no longer has to know whether to open Safari, grant a Mac permission, or repeat a command.
- effort: Medium-high: shared schema, relay D1 state machine, Mac/browser adapters, receipt UI and pendant event mapping; staged rollout can begin with read-only preflight and no new execution powers.  ·  risk: A bad fallback could perform work on an unintended surface or retry twice. Require idempotency keys, tab/session binding, explicit approval inheritance, node-level leases, and dead-letter state; recover by canceling the graph and exposing receipts.
- cost: Low storage and request overhead; deterministic probes dominate, with no extra LLM call for ordinary routing. Optional background planner call only for ambiguous fallback.  ·  latency: Adds <1 s preflight, but removes current long timeout failures; retries happen asynchronously.
- security: Improves security by refusing actions when permissions/session identity are uncertain; receipts must redact URLs, page text, and tokens. Never treat browser-online as authorization for irreversible actions.
- depends on: Shared typed context/action schema; Durable relay job runner; Browser request IDs and session affinity; Mac readiness/permission status endpoint; Pendant event delivery and owner-facing receipt


## What it asked for

_Nothing._
## Its own summary

Discovered a live, distinct execution gap and proposed it: cross-surface action preflight plus durable dependency-aware recovery. The Mac agent currently reports ready:false because Accessibility and Screen Recording are missing; the browser bridge is offline with three pending commands, and browser jobs currently burn about 45 seconds before failing. Proposed coordinator would preflight all surfaces, route safe alternatives, persist blocked work, retry/resume on heartbeats, reconcile stale commands, and give one per-node receipt. Sent this to faculty-judgement and recorded the live evidence.

**Biggest unknown:** Whether the orchestrator will implement the shared action-graph/dependency queue and receipt protocol, versus only the already-requested browser-specific queue. I still need that substrate before I can make cross-surface fallback execution real.

