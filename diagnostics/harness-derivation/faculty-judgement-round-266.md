# Harness derivation — faculty-judgement — round 266

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Did I actually get the important things done today, and what is still at risk tomorrow?”"
- **useful because:** The system should distinguish intentions, drafts, completed effects, and merely delivered briefings instead of giving another task list. It would reconcile Mac job receipts, browser evidence, reminders/notes, and pendant playback ACKs into a short, provenance-linked evening answer, then identify only unresolved commitments and offer reversible next steps.
- **path:** relay → mac → browser → pendant
- **model tier:** background for evidence collection and ranking; realtime only for the owner's follow-up conversation
- **latency:** Up to 30 seconds for the first grounded report; under 2 seconds for follow-up questions about one item
- **cost:** One background synthesis call per requested report, dominated by evidence summarization; follow-ups should use cached item evidence and be cheap
- **security:** Never infer completion from an audio download or a prepared plan. Require a receipt or explicit owner statement; redact sensitive snippets from speech and show source links only on the dashboard. Mutations remain drafts or require the existing physical approval latch.
- **missing:** A durable cross-surface join between relay jobs and Mac/browser action IDs; A writer for fleet memory or another durable completion index; A production ingestion path for pendant delivery ACKs into briefing item state; A commitment/obligation view that extends reconcile_personal_state without creating a second ledger

### "“I missed that—repeat only the item I interrupted, in one sentence, and tell me whether it is still actionable.”"
- **useful because:** A delivered audio file is not the same as an understood briefing. This gives the owner precise recovery from dropped attention without replaying a whole digest, and lets the system avoid stale advice by checking the item's current evidence before repeating it.
- **path:** pendant → relay → mac → browser
- **model tier:** Realtime for binding the utterance to the active audio cursor and speaking the short answer; background only when fresh browser or Mac evidence must be gathered
- **latency:** Pause and identify the item within 500 ms; speak a fresh one-sentence answer within 3 seconds
- **cost:** Usually no new model call beyond the live turn; a cheap targeted recheck dominates when the item has aged
- **security:** Bind only to the authenticated active cursor, never to an arbitrary item name from stale context. Re-check expiry/revocation and run autonomy_policy_evaluate before suggesting an external action. Secret or sensitive content stays non-speaking unless the owner has configured it.
- **missing:** A production route that atomically records the spoken utterance against the active cursor and returns an item-level state; Reliable playback_started/interrupted ACK ingestion and deduplication; A stale-item revalidation adapter for briefing evidence, not just prepared browser plans; Owner-configurable speech disclosure policy

### "“If I revoke that website or note, show me everything it influenced, stop anything pending because of it, and tell me what remains.”"
- **useful because:** Today revoking an evidence capsule can leave copied facts, context-graph text, drafts, and prepared actions alive. A source-impact report would make privacy controls trustworthy: the owner sees the complete downstream blast radius before choosing scoped revocation, and stale external actions are blocked rather than silently proceeding.
- **path:** browser → mac → relay → pendant
- **model tier:** Background graph traversal and impact classification; realtime only to read a concise result and collect explicit confirmation for revocation or cancellation
- **latency:** Preview in 5 seconds for a normal source; cancellation/revocation confirmation under 2 seconds after the owner approves
- **cost:** Mostly local indexed traversal and hashing; occasional background model call only to summarize ambiguous dependency edges
- **security:** Default to metadata and hashes, not raw quoted content. Revocation must be idempotent, source-scoped, and fail closed when dependency edges are missing. Never cancel or delete externally without explicit confirmation; the pendant should speak only “N downstream items found” unless detail is approved.
- **missing:** Provenance links from derived facts and context-graph entities to evidence capsule IDs; A durable cross-surface dependency index covering relay jobs, Mac actions, browser drafts, and audio items; A transactional revoke/cancel coordinator with dry-run and idempotent execution; A real cascade from POST /evidence/revoke into facts, graph copies, fleet memory, and pending plans

### "“Before I commit to this, show me the likely consequences of doing it, postponing it, or doing nothing—and tell me which assumptions would make that forecast wrong.”"
- **useful because:** The owner cannot currently ask for a grounded counterfactual about their own day. Plans and previews describe steps, but they do not compare branches against real deadlines, existing commitments, browser state, Mac jobs, or the time required to recover from failure. This would turn the hive into a consequence-aware advisor without silently taking any action.
- **path:** relay → mac → browser → pendant
- **model tier:** Background model for branch synthesis and uncertainty explanation; realtime model only for clarifying one assumption and reading the chosen comparison aloud
- **latency:** A three-branch forecast within 20 seconds; follow-up assumption checks within 3 seconds
- **cost:** One background synthesis per explicit request, with most cost in collecting and compressing branch evidence; no recurring spend or model call for unrequested forecasts
- **security:** Simulation must be read-only and visibly labeled as forecast, not fact. Do not send, purchase, delete, or modify anything while evaluating branches. Sensitive evidence should be reduced to derived facts and source references; any recommendation that becomes an external action must pass autonomy_policy_evaluate and physical approval.
- **missing:** A typed read-only scenario representation with branch assumptions, time horizon, and confidence; A cross-surface temporal dependency graph joining reminders, mail, browser watches, Mac jobs, routines, and pendant-delivery state; A deterministic way to distinguish observed completion from planned or predicted completion; A forecast receipt that records inputs, assumptions, model version, and what changed after the owner chooses a branch

### "“Which things are you currently assuming about me or my devices that are most likely wrong, and what one observation would settle each?”"
- **useful because:** The owner cannot see the system’s dangerous unknowns in one place. A live assumption audit would surface stale timezone, permission, device availability, calendar readability, and goal assumptions before they turn into confident speech or actions, ranking the cheapest observation that would resolve each uncertainty.
- **path:** relay → mac → browser → pendant
- **model tier:** Cheap background evaluator over existing provenance and status records; realtime only to explain the top uncertainty in one sentence
- **latency:** Under 5 seconds for the ranked audit; under 2 seconds to answer one assumption follow-up
- **cost:** Mostly deterministic joins and freshness checks; occasional low-cost synthesis for grouping related uncertainties
- **security:** Expose uncertainty metadata and source identifiers without revealing sensitive values. Never convert a low-confidence assumption into a mutation; require cross_surface_preflight and autonomy_policy_evaluate after the observation changes confidence. Keep owner preferences distinct from machine-derived facts.
- **missing:** A durable assumption record with claim, source, freshness, confidence, and a falsification test; A common freshness/contradiction schema across Mac, browser, relay, and pendant observations; A read-only observation planner that can propose the cheapest resolving probe without executing it; An owner-facing audit route and receipt linking each confidence change to its evidence


## What it asked for

_Nothing._
## Its own summary

Discovered the live device picture: Safari and the Mac bridge are online, the nRF9160 pendant is offline, and iOS probes are mixed. I recorded three new owner-facing capabilities: an evidence-backed end-of-day completion/risk report, exact interrupted-brief recovery with fresh validity checks, and a source-revocation blast-radius preview/cascade. The most valuable is the first: it answers what actually happened rather than what was merely planned or spoken.

**Biggest unknown:** The owner’s explicit morning-brief reliability preference remains unavailable, but these designs intentionally avoid guessing it. The implementation gaps are concrete: cross-surface IDs/dependency edges, durable delivery-ACK ingestion, and real revocation cascades. No additional permission request is needed this round.

