# Harness derivation — faculty-action — round 182

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Do this across my Mac and browser, and only tell me it worked after you independently verify every step; if anything is uncertain, stop and show me exactly where.""
- **useful because:** This is the core dependable action experience: one owner request becomes a correlated transaction across planner, Mac executor, browser sessions, physical approval, and fresh independent verification, instead of a receipt that merely says an attempt was sent.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-judgement → faculty-action → faculty-perception
- **model tier:** Use realtime only to clarify and report; use a cheaper background planner for decomposition, existing Mac/browser executors for steps, and faculty-perception for read-only verification.
- **latency:** Acknowledge in under 1 s; simple actions complete in 5–15 s; multi-step workflows may run asynchronously with wearable progress and a final verified/unknown result.
- **cost:** Usually one planner call plus low-cost verification calls; realtime tokens only for the spoken interaction. Dominant cost is page/app evidence and long workflows, not the physical latch.
- **security:** Never expose secrets to the pendant or relay. Require the existing physical_transaction_approval_latch for risky mutations, bind every step to an operation and attempt ID, expire approvals, and treat missing or contradictory verification as unknown rather than success.
- **missing:** A transaction coordinator that persists step dependencies, attempt IDs, deadlines, and compensation actions; A narrow addition to verify_operation_step accepting operation/attempt correlation and returning signed provenance; A uniform executor receipt schema shared by Mac and browser actions

### ""Stop everything I asked the system to do, including queued browser and Mac work.""
- **useful because:** A true wearable panic stop gives the owner an immediate escape hatch when an action is taking too long, entered the wrong app, or no longer feels right; it is useful even when the Mac screen is unavailable.
- **path:** relay-realtime → faculty-action → mac-planner → mac-vision → browser-extension → unified
- **model tier:** No expensive model is needed: relay performs deterministic cancellation fan-out, while realtime only confirms the scope and outcome.
- **latency:** Transmit the stop intent immediately; cancel queued work within 1 s and request cooperative cancellation of running steps within 3 s, then report any uninterruptible or unknown steps.
- **cost:** Negligible model cost; a few relay and Mac/browser control requests. Cost is dominated by durable audit logging and any required post-stop verification.
- **security:** A stop must be fail-safe and idempotent, never interpreted as approval. It must cancel only the owner's active operation namespace, preserve an immutable audit record, avoid deleting evidence, and surface actions that could not be interrupted.
- **missing:** A relay-wide cancel token checked by Mac and browser workers between steps; A pendant sw1 emergency gesture mapped to cancel-all with a distinct LED/audio acknowledgement; A read-only post-stop sweep to identify steps that reached unknown state

### ""If you aren't sure whether it happened, check the real state and either safely finish it or leave it alone and tell me what I need to decide.""
- **useful because:** Network drops and app crashes routinely create ambiguous outcomes. A reconciliation capability prevents duplicate sends or duplicate purchases while turning an unknown receipt into a concrete, owner-readable decision.
- **path:** faculty-perception → faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Use deterministic state probes first; use a cheap background model to classify discrepancies and propose a repair. Escalate to realtime only when the owner must choose between competing safe repairs.
- **latency:** Probe within 2 s of an unknown result; offer a repair plan within 10 s; never retry a side effect automatically until postconditions establish it did not happen and policy permits retry.
- **cost:** Low-to-moderate: most cases are GET/probe calls; model cost appears only for ambiguous multi-app state. Durable journals and snapshots dominate storage, not inference.
- **security:** Treat unknown as a distinct terminal state. Do not infer success from executor receipts. Redact evidence, require physical approval for any repair mutation, bind repairs to the original operation and a fresh state hash, and retain the failed attempt for audit.
- **missing:** A reconciliation state machine with per-action safe-to-retry predicates and compensation plans; Fresh cross-surface probes that can compare browser state, app state, and file state in one operation; Owner-facing choice records that expire without silently selecting a repair

### ""Before you do anything that could expose my information, show me exactly which data would leave which device, who receives it, how long it is kept, and let me approve a redacted version instead.""
- **useful because:** The owner currently has to trust invisible relay and browser data flows. A live, per-operation privacy manifest would make sensitive automation understandable and let them safely use the system for email, forms, and personal records without handing over more context than necessary.
- **path:** relay-realtime → faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension → unified
- **model tier:** Use deterministic taint and destination analysis for the manifest; use a cheap model only to summarize it in plain language. Realtime is reserved for the owner's spoken approval.
- **latency:** Generate the manifest in under 500 ms for a simple action and under 3 s for a multi-step browser workflow; block execution until approval when policy requires it.
- **cost:** Low inference cost; the main engineering cost is data-flow labeling and encrypted short-lived manifest storage.
- **security:** The manifest itself must not reproduce secrets. Display field categories and hashes or masked previews, enforce destination allowlists, expire approvals, and log the exact approved scope. Any mismatch between planned and actual fields must abort.
- **missing:** End-to-end sensitivity labels for planner inputs, browser fields, Mac files, and relay payloads; A preflight data-flow analyzer that compares planned versus actual outbound fields; A physical approval envelope that binds consent to a privacy-manifest hash, not merely an action hash

### ""Tell me what changed across my Mac and browser since I last checked, grouped by the thing it affects, and only interrupt me for changes that need a decision.""
- **useful because:** The owner should not need to remember which app, tab, folder, or job contains important changes. A causal, cross-surface change radar turns scattered notifications into a quiet prioritized digest while preserving urgent exceptions.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → unified
- **model tier:** Use scheduled deterministic collectors and a cheap background summarizer; reserve realtime for urgent changes or an on-demand spoken query.
- **latency:** Collect incrementally every few minutes with no foreground delay; answer an on-demand query in under 5 s; urgent policy matches should reach the pendant within 2 s.
- **cost:** Low-to-moderate background model cost proportional to changed items; deduplicated hashes and local summaries keep relay bandwidth and token use bounded.
- **security:** Keep raw content on the Mac/browser where possible, send only redacted change records, respect per-source sensitivity and quiet hours, and require explicit opt-in for monitoring private tabs, messages, or documents.
- **missing:** A durable cross-surface cursor and causal grouping model for file, app, browser, and job changes; Mac/browser collectors that emit redacted diffs rather than full snapshots; Owner-configurable urgency and source privacy policy

### ""When I'm in public or a sensitive app, keep private content off the pendant and out of speech automatically, but still let me know what needs my attention.""
- **useful because:** Today a useful answer can become a privacy incident through spoken playback, pendant prompts, or copied page text. A coordinated confidential mode would let the owner use automation around passwords, health, finance, and other people without broadcasting secrets.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-action → unified
- **model tier:** Use deterministic browser/app sensitivity signals and local policy checks; use no model for redaction decisions. A low-cost summarizer may produce a safe notification such as 'one private approval is waiting.'
- **latency:** Sensitivity transitions under 200 ms; redact before any relay or audio enqueue; safe status cues under 1 s.
- **cost:** Minimal inference cost; implementation cost is sensitivity detection, audio-queue enforcement, and cross-surface policy propagation.
- **security:** Fail closed when sensitivity is unknown, never send raw secrets to relay or pendant, flush queued private audio on mode transition, and require a deliberate local gesture to reveal a masked value. Keep an audit of policy decisions without storing content.
- **missing:** Shared sensitivity signals from browser fields, Mac app/document context, and owner policy; A relay/audio gate that rejects private payloads before playback; A pendant-safe notification vocabulary and local confidential-mode indicator


## Changes it proposed to its own stack

### `interaction` — Add a wearable 'action status card' protocol: every operation emits compact phases (queued, waiting-for-owner, executing step N, verifying, verified/unknown/failed), with monotonic sequence numbers and a final spoken summary generated from the durable ledger. The pendant shows phase-specific LED/audio cues and can request the next status without receiving private page contents.
- **owner gets:** The owner can trust what the system is doing without staring at the Mac: they know whether it is waiting for approval, still working, finished, or unable to prove completion, and stale notifications cannot overwrite newer truth.
- effort: Medium: define event schema, relay fan-out, Mac/browser emission hooks, and small firmware status renderer; test dropped-link replay and out-of-order events.  ·  risk: Dropped links or duplicate events could cause stale cues; monotonic sequence rejection and persisted last-seen state recover safely. An incorrect final status is worse than silence, so unverified states must remain explicit.
- cost: Very low API cost; small relay storage and a few hundred bytes of firmware state.  ·  latency: Immediate local cue; status propagation adds under 200 ms when connected.
- security: Status payloads must contain redacted action labels and hashes, not form values, message bodies, or secrets. Bind events to operation IDs and expire old status streams.
- depends on: Existing physical_transaction_approval_latch semantics; A shared operation/attempt ID added to executor receipts and verify_operation_step; Existing truthful action status beacon must be extended rather than duplicated

### `context` — Create a privacy-preserving cross-surface context capsule: when a conversation moves between pendant, relay, Mac, and browser, each surface contributes only typed claims (intent, entities, pending decisions, evidence hashes, expiry, sensitivity) rather than replaying the full transcript or page contents. The receiving surface can request a narrowly scoped claim and must record why it was released.
- **owner gets:** The owner gets continuity without repeatedly explaining themselves, while private browser pages and spoken history do not automatically follow every request to every machine. This makes the hive feel like one assistant without making every node a copy of the owner's life.
- effort: High: define claim schemas and retention, add redaction and consent checks, implement selective retrieval on relay/Mac/browser, and test expiry and conflicting claims.  ·  risk: A missing claim can make the assistant seem forgetful; conflicting or stale claims could cause a wrong action. Claims need provenance, freshness checks, explicit conflict surfacing, and conservative fallback to asking the owner.
- cost: Reduces repeated context-token cost over time; adds small encrypted metadata storage and occasional summarization calls.  ·  latency: Adds a local lookup, typically under 100 ms; selective retrieval may add 0.5–2 s for a remote surface.
- security: Improves least-privilege materially, but the claim index is sensitive metadata. Encrypt it, minimize retention, bind releases to an operation, and never store raw secrets in capsules.
- depends on: A sensitivity taxonomy shared by relay, Mac, and browser; Per-claim provenance and expiry; Owner policy for when a claim may cross device boundaries


## What it asked for

_Nothing._
## Its own summary

Recorded four distinct deliverables this round: (1) an owner-facing cross-surface action transaction that refuses to claim success without independent postcondition verification, (2) a wearable cancel-all escape hatch, (3) monotonic wearable action-status cards, and (4) unknown-outcome reconciliation that probes before retrying. The recorder noted the first/second are connective work over existing routes, so the missing value is specifically the protocol between them, not another executor.

**Biggest unknown:** I still need the concrete operation/attempt correlation contract added to verify_operation_step and executor receipts; a relay-wide cancellation token observed by Mac/browser workers; and safe-to-retry/compensation predicates per action class. I also still lack the previously queued device diagnostics, replay cursor, and authoritative pendant hardware revision/button-count response, so I cannot honestly specify or test the emergency gesture firmware mapping yet.

