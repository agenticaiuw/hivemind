# Harness derivation — faculty-judgement — round 199

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Did that actually happen, and if not, make sure it doesn’t happen later?” for an action I approved."
- **useful because:** An approval is not the same as execution. The system would bind the physical approval to a plan, monitor its expiry and execution receipt, and automatically invalidate stale approval rather than silently retrying or leaving an action in limbo. The owner gets one truthful answer: executed, safely cancelled, or needs re-approval.
- **path:** pendant → relay → mac → dashboard
- **model tier:** background for receipt correlation and expiry monitoring; realtime only for the owner's short question
- **latency:** Immediate acknowledgement under 1 s; receipt reconciliation within 5 s of a surface reconnect; no model call for the normal state machine.
- **cost:** <$0.001 per invocation; mostly durable-state reads and receipt joins, with model use only for ambiguous natural-language status questions.
- **security:** Never replay an expired approval. Require the physical approval nonce and plan hash to match; fail closed on unknown outcome. Show target and side-effect class, but do not put secrets or page contents on the pendant. Owner confirmation is required for any re-approval.
- **missing:** Durable relay implementation of the approval-handoff contract; A relay job lease/requeue mechanism so an orphaned execution can be classified; A cross-surface foreign key joining relay job IDs, Mac jobs, plans, and physical approval nonce; A small dashboard status view for expired/unknown approvals

### "“Tell me whether I really heard the important part of that briefing; if not, replay only what I missed.”"
- **useful because:** Generated, downloaded, and played are different facts. The owner should not have to trust a server receipt or guess after a dropped link. The relay would use authenticated pendant delivery/playback events to answer precisely and replay only an interrupted item, preserving position and avoiding duplicate announcements.
- **path:** pendant → relay → mac → dashboard
- **model tier:** No model for delivery state; realtime only to summarize an interrupted item when the owner requests it.
- **latency:** Answer from the event ledger in under 500 ms; replay can begin on the next available audio boundary.
- **cost:** <$0.001 per question; event ingestion and lookup dominate, with optional one short synthesis call for a compact replay.
- **security:** Use opaque artifact IDs and authenticated device sessions; do not expose audio bytes in the status answer. Deduplicate offline ACK replay and refuse to claim playback_finished without a verified event. Expired or revoked artifacts must not be replayed.
- **missing:** Production wiring from the pendant ACK queue to the relay event endpoint; A durable, queryable delivery ledger keyed by artifact and briefing item; A signed semantic link between an audio artifact and its briefing item/cursor; A user-facing status/replay surface on the dashboard and pendant

### "“That recommendation was wrong—mark exactly what was wrong, stop using that evidence for this decision, and tell me what changes.”"
- **useful because:** Correction is currently either a vague conversational signal or a destructive revocation. This would capture the owner's correction against the exact briefing/action item, quarantine the implicated source for that decision, preserve an audit trail, and ask the system to recompute only affected recommendations. The owner gets learning without silent rewriting of history.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Realtime to resolve the owner's utterance to the currently spoken item; background to recompute affected recommendations and produce a diff.
- **latency:** Acknowledge and quarantine in under 2 s; recomputation within 30 s, never blocking the owner’s conversation.
- **cost:** $0.002–$0.02 depending on recomputation; evidence lookup and policy evaluation dominate, not the correction write.
- **security:** A correction must not silently delete evidence or alter completed receipts. Require an item/cursor binding, preserve the original claim, redact sensitive excerpts, and require confirmation before any recomputed recommendation causes an external mutation. Source revocation must be scoped and reversible.
- **missing:** A durable correction record linked to item, evidence, decision, and affected action; A non-destructive source-quarantine scope distinct from global evidence revocation; A recomputation/diff endpoint that can report changed recommendations without executing them; A pendant/dashboard correction UI that can bind speech to the current item

### "“Give me a portable, private copy of what you know about my life, with every item’s source, expiry, and deletion effect, so I can move or restore you without trusting one server.”"
- **useful because:** Today the owner's memory is fragmented across Mac files, relay state, browser provenance, context graph, and audio artifacts. They cannot inspect or restore one coherent personal state. An owner-controlled encrypted snapshot would make continuity survivable across relay loss, model changes, and device replacement, while showing exactly what would be restored and what would not.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background model only for human-readable summaries; export/import must be deterministic and never depend on a model.
- **latency:** Export under 10 s for normal state; preview import under 2 s; restore can run in the background with progress and rollback.
- **cost:** <$0.01 per export/import; storage and encryption dominate, not inference.
- **security:** Encrypt with an owner-held key; never send raw secrets to a model or browser. Import is preview-only until physical confirmation, preserves tombstones and provenance, and rejects partial restores that would create duplicate facts or revive revoked data.
- **missing:** A canonical cross-surface state manifest covering facts, graph entities, evidence, approvals, jobs, audio, and browser provenance; Stable IDs linking relay, Mac, browser, and pendant records; Versioned export/import with conflict preview and rollback; An owner-controlled key and recovery process that does not depend on the relay

### "“When you notice I am repeating the same life mistake, show me the pattern and let me choose a small experiment—not another reminder.”"
- **useful because:** The system currently records events, tasks, and actions but cannot turn repeated outcomes into an owner-controlled behavioral experiment. A longitudinal pattern view could connect missed deadlines, abandoned plans, recurring purchases, or repeated browser workflows, then propose one reversible change with a success measure and an expiry date. It would help the owner change course without pretending the model knows their values.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background model for pattern discovery and concise explanations; realtime only when the owner asks about a pattern.
- **latency:** Weekly or on-demand analysis within 60 s; spoken answer under 3 s when a prepared pattern exists.
- **cost:** $0.01–$0.10 per analysis depending on history size; deterministic aggregation should filter candidates before inference.
- **security:** Patterns are sensitive inferences, not facts. Keep them private by default, attach evidence and confidence, allow deletion, never diagnose health or character, and require explicit owner acceptance before storing an experiment or changing routines.
- **missing:** A bounded longitudinal event view joining tasks, reminders, browser activity, jobs, and outcomes; A distinction between observed facts and inferred patterns; An experiment record with owner acceptance, metric, expiry, and opt-out; A dashboard and spoken explanation that can show the supporting evidence without exposing unrelated private material


## Changes it proposed to its own stack

### `new-surface` — Add an owner-controlled “values and tradeoffs” surface: the owner can state ranked principles in plain language, test a proposed action against them, and inspect which principle conflicts drove the recommendation. The evaluator must distinguish an explicitly stated value from a model-inferred preference, expire inferred values, and ask before writing a new durable value.
- **owner gets:** The system can currently optimize for urgency and completion without knowing why the owner would choose one acceptable outcome over another. This gives the owner a way to make decisions consistent with their priorities without silently turning guesses into permanent preferences.
- effort: Medium-high: policy schema, dashboard editor, spoken readback, deterministic matching, provenance, and integration at planning and action gates.  ·  risk: A model may overgeneralize a one-off statement into a life rule. Mitigate with explicit-vs-inferred labels, expiry, confidence, and physical confirmation before an inferred value affects an external action. Recover by deleting or downgrading the value without rewriting historical receipts.
- cost: <$0.01 per evaluation after deterministic filtering; occasional background model call to normalize a newly stated principle.  ·  latency: Under 300 ms for known principles; up to 3 s when interpreting a new statement.
- security: Values are highly personal. Keep them local by default, redact them from third-party prompts, and require explicit consent before relay storage or cross-surface export.
- depends on: A versioned owner-policy store with provenance and expiry; A deterministic policy evaluator that exposes matched rules; A safe distinction between explicit owner statements and inferred preferences; A dashboard and pendant flow for reviewing, correcting, and deleting principles


## What it asked for

_Nothing._
