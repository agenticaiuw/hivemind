# Harness derivation — faculty-judgement — round 196

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When you make a recommendation, let me say whether it was useful or wrong, and learn that without silently changing what you do.”"
- **useful because:** The system currently has hand-tuned urgency and autonomy rules but no owner-facing outcome loop. A single correction such as “that wasn’t urgent,” “you missed the real deadline,” or “never suggest that source again” should improve future judgement while preserving an auditable record of what changed. This is the highest-leverage capability: it makes every other cross-surface feature get better for this particular person instead of merely accumulating more automation.
- **path:** pendant → relay → mac → browser
- **model tier:** Realtime only for the short spoken acknowledgement and ambiguity check; a cheaper background model classifies the correction and proposes a policy delta. The deterministic autonomy_policy_evaluate and attention_arbitrate remain the enforcement path.
- **latency:** Acknowledge in under 1 second; background classification and replay against recent decisions within 30 seconds.
- **cost:** About $0.002–$0.01 per correction, dominated by the background classification and replay; deterministic evaluation is negligible.
- **security:** Corrections may mention private people or sources. Store a redacted, provenance-linked correction by default, not the raw utterance; require explicit confirmation before a correction changes an external-action rule. Never let one correction silently broaden permissions. Show the owner the exact proposed delta, matched policy fields, expiry, and affected surfaces.
- **missing:** A durable policy-delta store and version history (the existing briefing policy endpoint stores interruption policy but has no outcome feedback or diff history).; A correction capture route that links spoken feedback to the action/item receipt and supports accept/reject.; A replay evaluator that measures the proposed delta against recent attention/autonomy decisions before activation.

### "“After you say you did something, check the world and tell me whether it really took effect—not just whether your request was accepted.”"
- **useful because:** A Mac receipt or relay job completion is not proof that the owner's browser, calendar, or file state changed. This capability turns ‘done’ into a verified claim: it re-reads the relevant surface after a bounded delay, compares the observed state with the intended effect, and speaks one short result such as ‘the draft exists but was not sent’ or ‘the page still shows the old value.’ It prevents the most costly kind of trust failure: confidently claiming success when only a command was queued.
- **path:** relay → mac → browser → pendant
- **model tier:** Use deterministic typed checks and revalidate_pending_plan first; use a cheaper background model only to map an intent to a verification predicate. Realtime speaks the final one-sentence verdict.
- **latency:** Immediate acceptance in under 1 second, then verification within 5–20 seconds depending on browser heartbeat and app readback.
- **cost:** Usually under $0.005, dominated by one browser/Mac readback; model use is optional and limited to predicate extraction.
- **security:** Verification must be read-only and least-privilege. Do not read message bodies, form secrets, or unrelated tabs merely to prove an effect. A failed read must be reported as ‘unverified,’ never as success. External effects remain subject to autonomy_policy_evaluate and physical approval; verification cannot trigger a retry automatically.
- **missing:** A typed effect-to-observation predicate in the plan record (expected URL/title/value/reminder identity/file hash, with sensitivity bounds).; A durable verification receipt that distinguishes accepted, observed, contradicted, and unverified, linked to the original relay/Mac/browser IDs.; A scheduler/retry budget for read-only verification that expires rather than re-running a mutation.

### "“Keep track of the things I repeatedly defer, and at a calm moment show me the smallest honest list of what my deferrals are costing me.”"
- **useful because:** Today a deferred briefing item can disappear into separate queues, while repeated snoozes feel like fresh interruptions. This capability treats deferral as a visible state rather than a silent failure: coalesce the same item, increase its ‘attention debt’ only when the owner consciously defers it, expire debt when the source changes or the owner resolves it, and offer a quiet review with the evidence and the reason it was deferred. It helps the owner regain agency without turning every postponed item into an alarm.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic dedupe, aging, expiry, and attention_arbitrate decisions; a cheaper background model may cluster equivalent items across mail, watches, routines, and browser sources. Realtime is used only for the spoken review and explicit choice.
- **latency:** No interruption on each deferral; update state under 100 ms. Generate a review in under 10 seconds when requested or at an owner-configured quiet window.
- **cost:** Near-zero for bookkeeping; under $0.01 for an occasional clustering/review generation.
- **security:** Debt is sensitive behavioral metadata. Keep raw source content behind provenance references and speak only titles/categories unless the owner asks. Never infer moral urgency or escalate merely because a counter is high. The owner must be able to dismiss, snooze, or delete a debt record and revoke its sources.
- **missing:** A durable deferral ledger keyed by normalized source/item identity, with count, last decision, expiry, source references, and owner dismissal.; A coalescer that joins equivalent items across audio briefs, page watches, routines, mail triage, and browser jobs without copying private content.; A quiet-review route that returns ranked debt with evidence and supports resolve/dismiss/snooze transitions.

### "“When I keep failing to start something, tell me what is actually blocking it and offer one small intervention—not another reminder.”"
- **useful because:** The system can currently see fragments of work, browser activity, audio deferrals, and failed jobs, but cannot distinguish lack of time, missing information, access failure, avoidance, or an impossible plan. A cross-surface friction diagnosis would turn repeated stalled behavior into a useful explanation and one reversible next step. This is different from reminders or commitment tracking: it diagnoses the bottleneck rather than escalating the obligation.
- **path:** pendant → relay → mac → browser
- **model tier:** A background model builds a bounded hypothesis from structured events; deterministic rules enforce evidence minimums and prohibit diagnosis from a single signal. Realtime only delivers the concise finding and asks whether to try the proposed intervention.
- **latency:** Collect evidence incrementally; answer a direct request within 10 seconds. Never interrupt merely because a pattern was detected.
- **cost:** $0.01–$0.05 per diagnosis, dominated by cross-surface summarization; structured event filtering should happen locally and cheaply.
- **security:** Behavioral inference is highly sensitive. Store hypotheses separately from facts, retain them briefly, show the evidence and confidence, and never label health, mood, or character. No intervention may mutate external state without the existing approval policy. The owner must be able to reject a hypothesis and prevent reuse of its evidence.
- **missing:** A typed friction-hypothesis record distinct from durable facts or commitments, with evidence_refs, confidence, expiry, and owner rejection.; Cross-surface event normalization for failed, abandoned, blocked, and completed attempts.; An owner-facing hypothesis review and deletion path with no silent promotion into memory.

### "“Occasionally show me the beliefs you rely on that may have gone stale, and let me renew, correct, or retire each one in one sentence.”"
- **useful because:** The system currently projects remembered preferences and entities indefinitely in important cases, while expiration and pruning are largely unscheduled. That means an old preference can silently shape a new judgement long after it stopped being true. A stale-belief audit makes memory corrigible without dumping the entire memory store on the owner: it surfaces only high-impact, aging claims when they are about to influence a decision.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic age, use, provenance, and conflict scoring selects candidates; a cheaper model groups duplicates and writes a short neutral prompt. Realtime handles the owner's renew/correct/retire response.
- **latency:** No unsolicited spoken audit; prepare it in the background and present at a quiet, owner-chosen review. Each response should complete in under 2 seconds.
- **cost:** Usually below $0.01 per audit; most work is local ranking and storage maintenance.
- **security:** Do not speak sensitive values in public or expose raw source text by default. Retirement must create a tombstone that prevents the claim from being reintroduced by projection, while preserving only the minimum audit provenance. Renewal must not extend a claim whose source has been revoked without fresh evidence.
- **missing:** A scheduled, owner-controlled stale-claim review over facts, graph entities, browser claims, and fleet memory.; A cross-store tombstone and reintroduction guard; current deletion and evidence revocation do not propagate consistently.; A compact spoken review format that names the claim and source without revealing sensitive content.

### "“Before I revoke a source or forget something, show me exactly which future answers, reminders, and pending actions would change—and let me preview the safer degraded behavior.”"
- **useful because:** Revocation today is not an impact-aware operation: evidence, derived facts, graph copies, and queued work can diverge, so the owner cannot know what forgetting will actually accomplish. A counterfactual privacy preview would trace dependencies before any deletion, distinguish ‘will disappear,’ ‘will be downgraded,’ and ‘is currently unlinked,’ then show how future judgement changes with that source removed. It gives the owner meaningful control over privacy rather than a misleading success response.
- **path:** relay → mac → browser → pendant
- **model tier:** Use a deterministic dependency traversal and provenance graph first; a cheaper model summarizes the affected answers and proposes conservative degraded behavior. Realtime speaks only the preview summary; all revocation remains explicitly confirmed.
- **latency:** Preview in under 5 seconds for local stores and under 15 seconds when browser/relay state must be checked. No mutation until explicit confirmation.
- **cost:** $0.005–$0.03 per preview, mostly local graph traversal and optional summarization; relay reads dominate network latency.
- **security:** The preview itself must not disclose the sensitive source being revoked. Return hashes, claim labels, sensitivity-safe excerpts, and affected action IDs by default. Never infer that an unlinked copy was deleted. Preserve a tamper-evident audit of the owner's confirmation and the exact incomplete propagation set.
- **missing:** A provenance edge from every derived fact, graph entity, reminder, draft, and pending action back to its source capsule or observation.; A read-only counterfactual evaluator that recomputes projections and autonomy decisions with selected sources removed.; A transactional revocation plan with per-store completion, explicit partial-failure states, and a retryable non-mutating repair path.


## What it asked for

_Nothing._
