# Harness derivation — faculty-judgement — round 222

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before I send or change anything, tell me what this will affect across my day, what could conflict, and show me a reversible plan."
- **useful because:** This is the system's single most useful judgement capability: it turns a proposed action into an owner-facing consequence map rather than blindly executing or merely checking permissions. It can notice a browser purchase colliding with a calendar commitment, a reminder duplicating an existing one, or a drafted message exposing a private source, then present the smallest reversible next step. No single node can do this: the relay holds intent and policy, the Mac reads local calendar/mail/files, the browser reads authenticated state, and the pendant gives a short spoken decision plus physical approval when needed.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model to extract candidate effects and conflicts; use the realtime model only to explain the final compact consequence map when the owner asks. Deterministic autonomy_policy_evaluate and revalidate_pending_plan must gate the result; never let the model directly authorize a mutation.
- **latency:** 2-5 seconds for a read-only preview; under 1 second for cached policy/evidence. Mutation remains a separate explicitly approved step.
- **cost:** Roughly $0.01-$0.05 per preview, dominated by cross-surface evidence and the occasional model synthesis; zero model cost when deterministic checks find no effects.
- **security:** Read only by default. Do not send mail, buy, delete, or submit forms during preview. Source snippets remain on the Mac/browser unless the owner asks for detail; provenance IDs and sensitivity classes travel to the relay. Any external side effect requires a fresh policy evaluation, stale-plan revalidation, and physical consent for high-impact actions.
- **missing:** A typed consequence/impact graph and preview route that composes calendar/mail/reminder/browser effects without mutating; A durable plan-to-source and plan-to-receipt join (current relay and Mac IDs are not foreign keys); A standard reversible-effect vocabulary for browser and Mac actions; Owner policy values for what counts as an unacceptable conflict

### "Notice the corrections I keep making, turn them into proposed personal rules, and ask me to approve or reject each rule instead of making me repeat myself."
- **useful because:** The owner currently has facts and preferences, but no safe way for the system to learn behavioural rules from corrections such as 'don't read private titles aloud', 'always preview tidy', or 'this source is stale'. This creates a reviewable policy changelog, not silent profiling: each proposed rule cites the exact receipts, utterances, and cross-surface outcomes that motivated it, has an expiry, and can be revoked. The Mac can observe corrections and receipts, the browser contributes authenticated outcomes, the relay aggregates them, and the pendant surfaces one short approval prompt.
- **path:** mac-planner → mac-vision → browser-extension → relay-realtime → pendant → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model to cluster repeated corrections and extract candidate rules; use the realtime tier only when the owner asks why a rule was proposed or approves it by voice. Deterministic policy evaluation must remain the enforcement mechanism.
- **latency:** Background scan once nightly or after 20 new receipts; approval explanation under 2 seconds. No rule changes take effect before owner approval.
- **cost:** About $0.01-$0.03 per nightly scan, dominated by summarizing new receipts; approvals are near-zero when the rule and evidence are already cached.
- **security:** Rules are proposals, never inferred consent. Store only a compact rule, evidence IDs, confidence, scope, expiry, and sensitivity—not raw private content. Conflicting rules fail closed and are shown together. A rule affecting external side effects or spoken disclosure requires explicit confirmation; revocation must fan out to relay, Mac, and browser policy caches.
- **missing:** A durable policy-proposal log distinct from facts and memories; A correction/event normalizer that links an owner utterance to the action receipt it corrected; Cross-surface policy distribution with version and acknowledgement; A dashboard/pendant review queue for approve, reject, edit, and revoke

### "Find the recurring things that keep failing or wasting my time across the pendant, Mac, and browser, explain the pattern in plain language, and suggest one fix I can approve."
- **useful because:** One-off receipts tell the owner what happened; they do not reveal that the same browser login expires every Friday, the same briefing is missed after a link drop, or the same Mac action is retried three times. A friction radar would turn repeated failures into a concrete owner-level intervention: change a routine, add a watch, alter a policy, or stop attempting an unreliable path. It is not a health dashboard—the output is a ranked, human-sized decision with evidence and an undo path. The pendant contributes delivery ACKs and interruptions, the relay joins them, the Mac contributes job/action receipts, and the browser contributes command leases and page-watch outcomes.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic aggregation for counts, recurrence, latency, and failure clusters; use a cheap background model to name the pattern and draft one intervention. Realtime is reserved for the owner's spoken question and never for scanning the corpus.
- **latency:** Daily or weekly background scan; a spoken explanation under 2 seconds from a cached finding. Never interrupt solely because a pattern was detected—attention_arbitrate decides whether it waits for the next briefing.
- **cost:** Approximately $0.01-$0.04 per scan, with most cost in one compact model summary; aggregation itself is local and free.
- **security:** Retain event IDs, categories, timestamps, and bounded metrics rather than page contents, message bodies, or audio. Apply sensitivity redaction before cross-surface aggregation. Never auto-repair a recurring problem: propose a reversible change, run autonomy_policy_evaluate, revalidate its sources, and require confirmation for external effects.
- **missing:** A durable cross-surface event join keyed by relay job, Mac job, browser command, and pendant artifact; A recurrence detector with baseline and confidence, rather than raw receipt listing; A typed intervention proposal linked to evidence and an undo operation; A retention policy for aggregated failure metrics

### "Answer this the way you did last time, but tell me only what changed, what stayed the same, and what you still cannot verify."
- **useful because:** The owner should not have to reread a full briefing or remember the previous answer to detect change. A cross-surface answer-diff would compare the prior cited evidence with fresh calendar, mail, browser, research, and pendant-delivery evidence, preserve unchanged context as a compact checksum, and speak only meaningful deltas. It would prevent both false novelty and false reassurance: unchanged evidence is explicitly marked unchanged, while inaccessible or revoked sources remain unverified. This is a new judgement surface, not another notification triage or memory store.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic source fingerprints, timestamps, and provenance comparisons first; use a cheap background model only to summarize the changed spans. Realtime is used solely for the owner's spoken request and concise explanation.
- **latency:** 2-4 seconds for a cached recurring question; up to 8 seconds when fresh browser and Mac reads are required. No interruption occurs unless the owner asks or an existing attention policy permits it.
- **cost:** About $0.01-$0.04 per uncached comparison, dominated by summarizing changed spans; unchanged-source comparisons are local and nearly free.
- **security:** Persist source IDs, hashes, timestamps, and bounded redacted deltas—not full historical answers or raw private quotes by default. A revoked or expired source must never appear as current evidence. The response must distinguish unchanged, changed, unavailable, and contradicted. No external action is implied by a delta.
- **missing:** A durable answer record containing the exact evidence references and source fingerprints used for the prior answer; A cross-surface diff protocol for calendar, mail, browser, research, and pendant delivery evidence; A contradiction classifier that reports disagreement rather than choosing a winner silently; A compact owner-facing history view showing what changed and why


## What it asked for

_Nothing._
