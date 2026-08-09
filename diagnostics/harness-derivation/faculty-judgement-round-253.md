# Harness derivation — faculty-judgement — round 253

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “what did we decide?”, show me the exact decision, the evidence I was looking at, and what happened afterward—without making me remember which app it was in."
- **useful because:** It turns fragmented browser, voice, and Mac actions into a truthful, human-readable decision history. The pendant supplies the moment and spoken question; the browser/Mac supply source and effect receipts; the relay joins them and can explain uncertainty instead of inventing continuity.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background model for nightly indexing and a cheap deterministic joiner for retrieval; realtime only for the spoken answer.
- **latency:** Under 2 seconds for a known decision; up to 30 seconds for a cross-source reconstruction.
- **cost:** <$0.01 for retrieval and join; occasional background indexing dominates, not the spoken response.
- **security:** Decision context may include private page text or names. Default to titles/digests and source links; require explicit dashboard reveal for snippets. Never let a historical decision authorize a new external action. Cross-surface correlation must be durable, not inferred from timestamps alone.
- **missing:** A durable relay-job/Mac-job/browser-command correlation key (the current localJobId telemetry is not queryable); Writers for browser provenance and fleet memory, or a new compact decision index; A semantic decision-event schema linking owner utterance, evidence capsule, action receipt, and outcome; A dashboard timeline view

### "After you do something for me, tell me whether it actually worked—not merely that the Mac accepted the command—and recover gracefully if the result is different."
- **useful because:** Owners care about outcomes (the reminder exists, the page changed, the audio played), not transport success. This closes the dangerous gap between accepted jobs and reality, especially after browser drops or stale Mac state.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic typed verifiers first; background model only to interpret a changed page or ambiguous result. Realtime speaks one short outcome sentence.
- **latency:** 3–10 seconds after reversible actions; 30 seconds for a browser re-check; never block urgent cancellation.
- **cost:** <$0.005 for deterministic checks; $0.01–$0.03 when page interpretation needs a model.
- **security:** Verification reads current private state and may expose it in speech. Speak only status (“worked”, “needs review”, “could not verify”), not page contents. Never auto-retry mutations unless autonomy_policy_evaluate marks them idempotent and reversible; stale plans require revalidate_pending_plan.
- **missing:** A typed postcondition/verifier contract attached to each plan step; A durable operation journal joining relay, Mac, browser, and pendant delivery IDs; Read routes for created reminders/notes and a browser result snapshot with provenance; A recovery executor that can offer inspect/undo/retry rather than silently repeat

### "Make my brief learn how I actually listen: shorten items I skip, resume exactly where I stopped, and surface an important item later if I interrupted it."
- **useful because:** A spoken briefing should adapt to the owner's attention rather than repeatedly wasting it. Pendant playback ACKs and barge-in identify what was heard; the relay ranks unfinished items; Mac/browser provide fresh evidence so resumed items are not stale.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic playback state and ranking; background model summarizes only the deferred item. Realtime handles the immediate stop/resume exchange.
- **latency:** Immediate pause/resume under 300 ms; next-item decision under 1 second; deferred re-summary within 60 seconds.
- **cost:** <$0.01 per briefing item; model cost only for a newly shortened summary.
- **security:** Playback telemetry should store opaque artifact/item IDs and positions, not raw audio. Re-ranking can change urgency but must retain evidence refs and explain why an item was deferred. Sensitive content remains non-spoken by default unless the owner has set a policy.
- **missing:** A durable item-level playback history and learning policy (ACK events now exist but no ranking consumer); A scheduler that invokes briefingTriage; currently the 07:00 policy does not fire anything; A policy field mapping interruption/skip/completion to shortening and defer behavior; Freshness checks before resuming a stale item

### "Before you give me advice, tell me how sure you are—and prove that your confidence improves or worsens based on what happened later."
- **useful because:** The owner would get an assistant that is measurably honest rather than merely fluent: uncertain calendar reads, stale browser state, and inferred preferences would be visibly different from verified facts. Over time, the system could learn which kinds of predictions it routinely gets wrong.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Cheap deterministic calibration over evidence and later outcomes; background model only labels ambiguous outcome matches. Realtime speaks a short confidence-qualified answer.
- **latency:** Under 1 second for an existing claim; nightly calibration can run in the background.
- **cost:** <$0.005 per claim; background aggregation is the dominant cost and can use a small model or no model.
- **security:** Confidence must never become permission to act. Store claim IDs, evidence references, and outcome labels rather than raw private text; allow the owner to inspect and correct a mistaken outcome label.
- **missing:** A durable claim/outcome record spanning voice, Mac, browser, and relay; A calibration report with reliability by source and claim type; A spoken policy for when low confidence means ask, defer, or answer cautiously; Outcome labels from later verification, not just model self-rating

### "When I correct you, make that correction change the right future behavior—and show me exactly what it changed, without turning one correction into a permanent guess about me."
- **useful because:** Today a correction can disappear with the conversation or become an opaque memory. This would let the owner teach the system safely: a correction can be scoped to one task, one source, one surface, or a durable preference, with a visible expiry and undo.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic scope/expiry handling; a small background model may classify whether the correction is preference, task, entity, or one-off instruction.
- **latency:** Immediate acknowledgement under 500 ms; propagation to other surfaces under 5 seconds.
- **cost:** <$0.005 per correction; no model cost for explicit scope selection.
- **security:** Never silently promote a one-off correction into a permanent preference. Sensitive corrections stay local unless explicitly shared. Every propagation must carry a source, expiry, and revocation path.
- **missing:** A first-class correction event distinct from generic memory facts; Owner-selectable scope and expiry in the spoken/dashboard interaction; Cross-surface memory writer and retraction propagation; A before/after explanation showing which future decisions changed

### "When I ask “what did you not tell me?”, show me important things you deliberately deferred or suppressed, why, and whether they are still actionable."
- **useful because:** Silence is otherwise unobservable: a briefing can omit an event because of quiet hours, low confidence, deduplication, stale evidence, or a policy rule. The owner should be able to audit missed attention without receiving every suppressed notification in real time.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic suppression ledger and policy explanation; background model only groups related deferred items. Realtime reads a concise audit summary.
- **latency:** Under 2 seconds for the recent suppression ledger; nightly cleanup can be asynchronous.
- **cost:** <$0.005 per audit query; storage and deterministic filtering dominate.
- **security:** The ledger itself can reveal private mail or calendar subjects. Store redacted summaries plus evidence references, apply sensitivity policy before spoken output, expire ordinary suppressed items, and require dashboard reveal for sensitive details.
- **missing:** A durable attention-decision ledger containing every interrupt/defer/suppress result and matched policy rule; An owner-facing query for expired versus still-actionable suppressed items; A retention policy for suppression metadata distinct from content retention; Integration with attention_arbitrate, briefingTriage, and the existing policy explanation surface


## Changes it proposed to its own stack

### `relay` — Give relay_jobs a lease_until and lease_owner, requeue expired processing jobs with an attempt counter, and expose the original relay↔Mac correlation in job status. Claiming must be compare-and-set and retries must be idempotency-aware.
- **owner gets:** If the Mac or link dies halfway through a request, the owner gets a truthful retry or failure instead of a job that silently vanishes for 24 hours. No more “I asked for that—did it happen?” dead ends.
- effort: Medium: schema migration, D1 and memory-store parity, claim/requeue sweep, and receipt semantics.  ·  risk: A crashed worker can be retried after a side effect. Recover only jobs whose step receipts prove no external mutation, or route them to review; never blindly replay unknown mutations.
- cost: Negligible storage and CPU; one periodic relay sweep.  ·  latency: Normal jobs unchanged; recovery waits at most the lease interval.
- security: Preserve owner/job scoping and redact payloads from lease diagnostics.
- depends on: A durable idempotency key crossing relay and Mac (current actionIdFor is Mac-local); A typed retryability classification from autonomy_policy_evaluate

### `memory` — Actually write normalized owner-relevant events from the Mac bridge and browser into shared fleetMemory, including retractions, expiry, surface, confidence, and sensitivity; stop relying on the clipped inherited memory.text blob as the only cross-body memory.
- **owner gets:** A preference or correction made while speaking can be honored by the Mac and browser later, and a revocation can stop old guidance from resurfacing. The owner experiences one mind instead of three bodies forgetting each other.
- effort: Medium: wire POST /v1/memory/events, apply the existing migration, add bridge event mapping and projection tests.  ·  risk: Over-collecting personal data or stale facts. Emit only explicit preferences/tasks/entities, enforce existing byte/TTL budgets, and expose source and retraction in the dashboard.
- cost: Small D1 writes and projection reads; no model cost.  ·  latency: One bounded write per accepted event; prompt projection remains within its existing 800–2000 byte budget.
- security: Use the existing three-class classifier and conservative projection; never send raw quotes or secrets to fleet memory.
- depends on: Apply relay_memory_events migration to the deployed schema; A writer call from local-agent/bridge.js and later browser extension; Owner-visible source/retraction controls

### `memory` — Add provenance links from derived facts and context-graph entities to their originating evidence capsule or capture, then make revoke/delete propagate tombstones across facts, graph, browser provenance, and fleet memory projections.
- **owner gets:** When the owner says “forget that site/person/note,” it would actually stop influencing future answers instead of deleting one visible copy while stale copies continue guiding the agent.
- effort: Large but bounded: schema fields, reverse indexes, cascade transaction/order, and a dry-run purge report before commit.  ·  risk: Over-broad deletion or irreversible loss. Require a dashboard confirmation with the exact affected IDs, preserve non-content tombstones, and make the operation idempotent.
- cost: More local index bytes and a bounded purge pass; no recurring model cost.  ·  latency: Normal reads unchanged; purge may take seconds for large graphs.
- security: This is a privacy boundary: revoke before prompt projection, external action, or spoken delivery; include explain_action_provenance receipts.
- depends on: Add capsuleId/source refs to memoryService fact records; Mount browserProvenance routes or replace them with a durable index; Fleet memory writer and retraction support; A cross-store purge preview route

### `model-routing` — Create a claim-specific uncertainty router that chooses among answer, ask-one-question, gather-more-evidence, or refuse based on calibrated source reliability and action risk—not a single global confidence number. Record the route and the evidence that triggered it.
- **owner gets:** The assistant would stop treating a low-stakes guess about a restaurant like a high-stakes guess about a deadline or purchase. It would ask fewer needless questions for reliable facts and intervene earlier when uncertainty could cost the owner something.
- effort: Large: typed claim classes, calibration store, routing policy, owner-visible explanations, and integration at voice, briefing, planning, and execution boundaries.  ·  risk: Bad calibration could create either annoying hesitation or dangerous overconfidence. Fail closed for external side effects, require fresh evidence for deadlines and permissions, and keep a visible override/appeal path.
- cost: Usually lowers cost by avoiding expensive reasoning for verified claims; adds background aggregation and occasional evidence reads.  ·  latency: Verified read-only answers faster; ambiguous/high-risk requests may add one evidence round trip or one clarifying question.
- security: The router must evaluate sensitivity before selecting a surface; uncertainty metadata may leave the device, raw content should not.
- depends on: A durable claim/outcome ledger; Source-linked memory and evidence revocation; A policy object extending autonomy_policy_evaluate with claim risk and freshness; Outcome verification after Mac/browser actions


## What it asked for

_Nothing._
