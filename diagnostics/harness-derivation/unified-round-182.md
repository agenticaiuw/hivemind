# Harness derivation — unified — round 182

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser readiness** — The AI Pendant Agent is fully ready now: accessibility and screen recording are both granted for com.aipendant.agent, browser extension is online with 9 Safari tabs and 0 pending/spooled commands, relay reachable, and pendant pipeline telemetry/durable audio are enabled. Current visible tab is x.com.
  - evidence: GET /ops/status and GET /browser/status returned ok=true, permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser.online=true, pendingCommands=0, spool.spooled=0, relay.reachable=true.

## Capabilities it proposed

### ""Continue what I was doing." Reconstruct the latest interrupted or active task across my pendant conversation, relay job, Mac work, and the exact browser tabs, then tell me the smallest truthful next step before doing anything."
- **useful because:** The owner should never have to remember whether work lives in a voice turn, a queued Mac job, or a Safari tab. This turns the hive's distributed state into one actionable handoff, especially after sleep, USB reconnect, or a dropped relay link.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** background for state joining and summarization; realtime only for the short spoken handoff
- **latency:** Under 3 seconds to speak a state summary; longer work remains queued and receipt-backed.
- **cost:** One small background synthesis per request; dominated by context serialization, not audio generation.
- **security:** Only inspect explicitly bound active sessions, current jobs, and the current conversation; redact page contents and secrets by default. Never infer that a proposed next action was performed. Mutating or sending requires the existing approval path.
- **missing:** A first-class correlated handoff record joining sessionId, jobId, pipelineId, browser session/URL pattern, and last receipt; A stale-state policy that distinguishes completed, failed, and genuinely interrupted work (including closing ordinary ledgers); A spoken owner-facing response route for the joined evidence

### ""Audit what parts of my browser and Mac are currently visible to you, and close the exposure." Return a redacted inventory of bound tabs, pending browser commands, captured artifacts, and active audio/jobs, then let me revoke selected browser sessions or clear captures."
- **useful because:** The owner gets a concrete privacy answer instead of trusting that a latch or browser bridge did everything. It makes accidental exposure visible while preserving the browser's unique authenticated reach.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic inventory and revocation; background model only to summarize the redacted result
- **latency:** Inventory spoken in under 2 seconds; revocation receipt within 5 seconds.
- **cost:** Negligible model cost; mostly bounded metadata reads and explicit deletion calls.
- **security:** Default-deny and metadata-only: show origin/title hash and binding, never page body, cookies, tokens, or audio. Require explicit confirmation for revocation because it can discard pending work. Produce a signed convergence receipt after every change.
- **missing:** A typed cross-surface exposure inventory route with stable redaction; A safe bulk revoke operation for browser sessions/commands and capture artifacts; Integration with privacy_convergence_check so the receipt covers queued jobs and relay persistence, not just local state

### ""Forget everything about [topic/person/project]." Find only the explicitly bound records across conversation context, Mac captures/journal, relay jobs, and browser session artifacts; preview the exact deletion set; after my confirmation, delete what is deletable and return an auditable remainder list."
- **useful because:** A wearable assistant accumulates sensitive context across machines. The owner needs one trustworthy erasure command, not separate guesses about what the relay, Mac, and browser retained. The remainder list makes limits honest instead of claiming deletion that did not happen.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic search, scope calculation, and deletion receipts; background model only to resolve the owner's topic into explicit identifiers, never to choose extra records silently
- **latency:** Preview in under 5 seconds for bounded stores; deletion and receipts within 10 seconds.
- **cost:** Low metadata/search cost; model cost is limited to one short disambiguation if the topic is ambiguous.
- **security:** Require an exact scope preview and confirmation; do not delete by fuzzy semantic match alone. Preserve a minimal tombstone/audit hash without content, honor legal/system immutability, and never expose secrets while listing matches. Physical approval is required if deletion touches browser artifacts or external queued actions.
- **missing:** A cross-surface retention/deletion index with provenance for each stored artifact; Typed, idempotent delete operations and receipts for relay jobs, context graph entities/relations, captures, journals, browser sessions, and pendant inbox/outbox metadata; An owner retention policy and default deletion windows (still an open decision)

### ""Give me a 30-minute delegation capsule for this one task." Let me define the allowed browser origins, Mac apps, action classes, spending/message limits, and expiry; have the pendant physically approve the capsule, enforce it across every executor, and automatically revoke it with a receipt."
- **useful because:** Today approval is per staged action, which is too brittle for a task that legitimately needs several harmless steps, but broad agent control is too dangerous. A narrow, expiring capability lets the owner delegate a real outcome without handing the system an enduring bearer token or trusting a verbal promise.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic policy enforcement and receipts; realtime model only for conversational setup and concise status
- **latency:** Capsule preview in 3 seconds, activation after one physical approval, enforcement overhead under 50 ms per action.
- **cost:** Low model cost; dominant work is deterministic policy checks and signed receipts.
- **security:** Default deny. Bind capsule to owner/device identity, exact origin/app allowlists, action-type limits, budget, nonce, and expiry. Revoke on privacy latch, link ambiguity, policy violation, or clock uncertainty. Never let a model widen scope; external sends/deletes remain separately confirmable.
- **missing:** A capability-token evaluator shared by Mac and browser executors; Relay persistence and revocation propagation for capsules across USB/LTE reconnects; A user-facing policy editor and per-action denial receipts

### ""Put this Safari tab in agent quarantine." Mark the current tab as private until I physically unlock it; while quarantined, the agent may see only a redacted title/origin, cannot inspect or act, and navigation or window changes automatically relock it."
- **useful because:** The browser is the one surface that can reach the owner’s authenticated private life. A global privacy latch is too coarse when the owner still wants conversation and Mac automation; per-tab quarantine gives a practical boundary without closing every session.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic browser policy and state machine; realtime model only to explain the current lock state
- **latency:** Lock within one heartbeat (under 2 seconds); unlock receipt before any page inspection or command.
- **cost:** Negligible model cost; small persistent browser-policy state and heartbeat checks.
- **security:** Quarantine must fail closed on bridge loss, tab ID reuse, origin change, or stale nonce. Store only opaque tab/session identifiers and redacted metadata. Unlock requires deliberate physical approval and an explicit scope/expiry; never treat a spoken request alone as unlock.
- **missing:** Browser-extension enforcement that gates every inspect, poll, and result by quarantine state; A stable tab identity and navigation observer, not only a URL pattern; Relay-to-pendant lock/unlock receipts that survive USB/LTE handoff


## Changes it proposed to its own stack

### `integration` — Add a cross-surface capability ledger that records, for each delegated action, the exact authorization capsule, executor, browser tab/app binding, precondition hash, postcondition evidence, and expiry; make the relay reject actions whose capsule is missing, expired, widened, or not acknowledged by the target surface.
- **owner gets:** When the owner says "what did you do under my delegation?" they get a complete, bounded answer rather than scattered Mac job and browser receipts, and a reconnect cannot accidentally continue an old delegation.
- effort: Medium-high: shared schema, relay enforcement, Mac/browser middleware, migration tests, and failure-injection across USB/LTE loss.  ·  risk: A stale or malformed ledger could block legitimate work; fail closed and provide an explicit owner revocation/recovery path. Do not infer completion from dispatch—require target receipts.
- cost: Small storage and read overhead; no meaningful model cost.  ·  latency: One local authorization lookup per action; target under 50 ms with cached capsule, slower only on revocation checks.
- security: Materially improves least privilege, replay resistance, and auditability; creates sensitive metadata about owner activity, so apply bounded retention and redacted exports.
- depends on: A first-class delegation capsule format and evaluator; Stable browser tab identity/navigation binding; Relay job lease/revocation propagation; Owner retention policy


## What it asked for

_Nothing._
## Its own summary

Recorded three distinct capabilities: cross-surface task handoff, privacy exposure audit/revocation, and owner-directed cross-surface erasure. The browser-form approval idea was correctly rejected as an existing capability. Fresh live discovery also shows the Mac agent is now fully ready: Accessibility and Screen Recording are granted, Safari bridge is online with 9 tabs and no pending/spooled commands, and the relay is reachable.

**Biggest unknown:** The owner’s retention/deletion policy and personal timezone are still unanswered. Engineering still needs a correlated handoff index, a real approval relay/delivery loop, and typed cross-surface deletion receipts; these are implementation gaps, not permissions blockers.

