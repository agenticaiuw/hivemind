# Harness derivation — unified — round 173

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What changed on my computer and browser since yesterday, and can you undo any of it?”"
- **useful because:** Gives the owner a trustworthy rewind of cross-surface activity instead of hunting through separate job history, browser commands, and context changes. It reports evidence first and never silently undoes anything.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** background for inventory and clustering; realtime only to explain the ranked result and collect an explicit undo choice
- **latency:** Inventory in 3–8 s; spoken summary under 10 s; each undo has a separate confirmation and receipt
- **cost:** Low: mostly local GETs and receipt hashing; one background model call for grouping ambiguous changes, typically <$0.02
- **security:** Only inspect the owner’s bound Mac jobs, browser sessions, and context graph; redact page contents and secrets from the model. Undo is opt-in per item, and irreversible/browser actions are shown as non-undoable rather than guessed.
- **missing:** A read-only cross-surface change index joining GET /jobs/:jobId/receipts, GET /browser/inspections, context-graph mutation history, and pendant approval/delivery receipts; A preview endpoint that maps each candidate to the existing job undo capability without executing it; Retention and deletion rules for activity history

### "“Make sure the thing you just did actually reached the website, my Mac, and my ears—tell me what is still uncertain.”"
- **useful because:** Separates intent accepted, action completed, browser state changed, audio delivered, and audio heard. Today those are different systems and a green job status can hide a failed final leg; this gives one honest closeout and a targeted retry or human action.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → dashboard → pendant
- **model tier:** deterministic evidence join first; realtime model only verbalizes uncertainty and asks for confirmation when remediation is consequential
- **latency:** Evidence join within 2 s after each leg; spoken closeout within 4 s of playback completion
- **cost:** Very low: receipt correlation and hashes dominate; model cost near zero for deterministic outcomes
- **security:** Bind evidence to job, tab/session, artifact ID, and audio sequence; never infer success from a screenshot alone. Browser page content remains local/redacted. Any retry of a non-idempotent action requires physical_transaction_approval_latch or an explicit owner confirmation.
- **missing:** A durable cross-surface artifact ID propagated from relay job through Mac/browser action and audio artifact; An implementation of the existing audio_delivery_ack_queue's relay-side join with browser and Mac receipts; A final-state verifier for browser mutations that can compare before/after evidence without exposing secrets

### "“Forget this specific piece of information everywhere you can find it, then prove what was removed and what remains.”"
- **useful because:** Turns forgetting into a bounded, auditable operation across context graph, reminders, local captures, relay-held records, browser command results, and queued pendant artifacts. It avoids the dangerous fiction that deleting one memory means deletion everywhere.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard → pendant
- **model tier:** planner/background for candidate discovery and entity resolution; deterministic executor for deletion; realtime only for the owner’s confirmation and final report
- **latency:** Candidate preview in 5–15 s; deletion only after explicit confirmation; convergence report within 10 s after all surfaces respond
- **cost:** Usually <$0.03 for entity resolution; storage scans and cryptographic receipts dominate, not inference
- **security:** Default to preview-only and exact-scope confirmation. Do not delete mail, files, or browser data based on semantic similarity alone. Keep a minimal deletion receipt (IDs, hashes, timestamps), not the deleted content; honor the owner’s still-unspecified retention policy.
- **missing:** Owner-defined retention/deletion policy (still requested and unanswered); A tombstone protocol shared by context graph, relay durable state, browser spool, Mac captures, and pendant OUTBOX/INBOX; A read-only candidate scanner and post-delete convergence checker with per-surface refusal reasons

### "“Give me a safe 20-minute delegation: read my calendar and the named website, prepare drafts, but do not send, purchase, delete, or change settings.”"
- **useful because:** The owner gets useful autonomy without handing the agent a permanent all-or-nothing key. A bounded capability token travels with the job across relay, Mac, browser, and pendant, and expires automatically.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic policy compiler for the capability token; background model for planning within the granted scope; realtime only for spoken setup and status
- **latency:** Token issued in under 2 s after physical confirmation; ordinary actions should feel interactive; expiry and revocation take effect within one polling interval
- **cost:** Low: policy evaluation and signed tokens are local/relay CPU; model cost is ordinary planning only
- **security:** Default deny. Bind token to exact apps/sites, action types, data classes, job/session, expiry, and one-use or repeat limits. The pendant’s physical_transaction_approval_latch authorizes issuance, never arbitrary future actions. Browser secrets and page contents stay inside the bound browser session.
- **missing:** A relay-enforced capability-token format and verifier shared by Mac and browser bridges; Action-level policy checks before every dispatch, not only at plan creation; A pendant status/invalidation event so the owner can revoke the delegation offline; A dashboard view showing scope, remaining time, and attempted denials

### "“I’m in a conversation—quietly tell me what this unfamiliar term means, using the relevant page or document on my Mac, without recording the conversation.”"
- **useful because:** The pendant becomes useful in the moment: it can resolve a name, acronym, product, or reference while the owner is speaking, without forcing them to stop and operate a screen. The Mac/browser supply private context; the pendant supplies the discreet answer.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** realtime for the short spoken clarification; deterministic local retrieval first, with a background model only when disambiguation or summarization is needed
- **latency:** Candidate lookup under 1 s; spoken answer in 2–4 s; if confidence is low, ask one concise clarification rather than guessing
- **cost:** Usually <$0.01 per clarification; local page/document extraction dominates, with realtime inference reserved for the final short answer
- **security:** Explicitly no audio recording or transcript retention. Search only the currently owner-bound tab/document and user-named scope; redact account numbers, messages, and unrelated page regions. Never click, submit, or alter the source while answering.
- **missing:** A transient, non-persistent audio-to-query handoff from the active pendant turn; A browser/Mac scoped retrieval endpoint that returns snippets with provenance and sensitivity labels; A hard context deadline so stale tabs cannot answer a later question; An owner-configurable rule for whether spoken answers may quote private source text

### "“Before I leave, tell me what I will lose if the Mac and browser disappear, and package only the next actions I can still do from the pendant.”"
- **useful because:** The owner gets graceful degradation instead of discovering offline limitations after a task fails. It inventories active work, identifies which steps require the Mac/browser, and converts the remainder into a compact pendant-resident handoff with explicit expiry.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** deterministic dependency analysis first; background model to compress remaining actions; realtime only to speak the short handoff
- **latency:** Readiness report in 3–6 s while connected; offline handoff must be available locally before disconnect
- **cost:** Low: mostly receipt/job inspection and compact serialization; one small background summarization call
- **security:** Do not copy page contents, credentials, or raw audio to the pendant. Store only opaque task IDs, labels, deadlines, required-surface flags, and owner-approved next actions. Expire stale handoffs and require physical confirmation before any queued external action.
- **missing:** A dependency manifest on each job step declaring required surface and offline-safe alternatives; A bounded pendant INBOX payload type for task handoffs, distinct from alerts but using the existing inbox durability mechanism; A relay reconciliation protocol that marks a handoff stale rather than replaying it after world state changes; A Mac departure/link-loss trigger or owner-invoked preflight


## Changes it proposed to its own stack

### `integration` — Add a proof-carrying artifact envelope shared by relay jobs, Mac/browser commands, pipeline audio, and pendant delivery acknowledgements: artifactId, parentJobId, turnId, idempotency key, producer, byte/hash summary, observed state, and terminal evidence links. Add a deterministic closeout reducer that reports complete, partial, contradicted, or unknown without invoking a model.
- **owner gets:** When the pendant says “done,” the owner can trust that it means the final real-world leg was observed—not merely that a request was queued.
- effort: Medium-high: schema and receipt propagation across relay, Mac agent, browser bridge, and firmware metadata; no raw audio or page secrets need to be stored.  ·  risk: Old jobs lack envelopes and must be labeled legacy/unknown; malformed or conflicting receipts should fail closed and surface uncertainty rather than block unrelated work.
- cost: Negligible storage and CPU overhead per job; no meaningful model cost.  ·  latency: Adds milliseconds to receipt writes and up to one short polling window for final evidence.
- security: Improves provenance, but hashes and cross-surface IDs become sensitive metadata; scope them to the owner and redact values in spoken output.
- depends on: audio_delivery_ack_queue; physical_transaction_approval_latch; relay-side durable receipt implementation; browser command lease sweep and relay job lease/requeue prerequisites

### `context` — Create a capability policy layer that is evaluated at dispatch time across relay, Mac, browser, and pendant—not merely during planning. It should issue short-lived, scope-bound authority tokens, expose denials as evidence, and invalidate tokens on physical privacy latch, session end, world-fingerprint change, or expiry.
- **owner gets:** The owner can safely say “you may do this, here, for this long” and trust that a later plan, stale tab, or compromised bridge cannot silently broaden the permission.
- effort: High: shared schema, relay verification, Mac/browser enforcement middleware, pendant revocation signaling, and dashboard visibility.  ·  risk: Incorrect policy matching could block intended work or, worse, permit too much. Fail closed, provide a dry-run explanation, and retain only hashed scope metadata in receipts.
- cost: Small relay/Mac CPU and metadata storage overhead; no additional model call for enforcement.  ·  latency: A few milliseconds per dispatch plus one signature verification; revocation bounded by bridge polling unless an active link exists.
- security: Substantially reduces blast radius and makes delegation auditable; token metadata itself must avoid revealing sensitive URLs or document names.
- depends on: physical_transaction_approval_latch; relay job leases and requeue; browser command lease supervisor; action-level Mac/browser middleware; owner-defined retention policy


## What it asked for

_Nothing._
