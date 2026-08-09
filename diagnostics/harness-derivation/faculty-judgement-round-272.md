# Harness derivation — faculty-judgement — round 272

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make urgent things reach me reliably. If the pendant is unavailable or I miss the alert, use the safest available surface, and tell me exactly what was delivered and what was not.”"
- **useful because:** Today an attention decision can exist without proof that the owner heard it. This would turn urgency into a delivery contract: retry or downgrade across pendant, Mac, and browser, never silently claim success, and show the owner the last confirmed surface and playback position.
- **path:** relay → pendant → mac → browser
- **model tier:** background for classification and retry planning; realtime only for the owner's spoken status query
- **latency:** Under 2 seconds for a status answer; urgent retry decisions under 10 seconds, with bounded backoff rather than repeated model calls
- **cost:** <$0.01 per alert lifecycle; deterministic policy, delivery ACKs, and preflight dominate, not model tokens
- **security:** Do not copy private alert content to a less-private surface. Route only an opaque alert reference until that surface passes the sensitivity policy; require confirmation for any external side effect. Every attempt, refusal, and ACK must have provenance.
- **missing:** A durable delivery-contract record linking one attention event to all surface attempts and terminal outcome; A policy-defined fallback order and per-surface content allowance; A relay scheduler that consumes record_pendant_delivery_event and coalesces retries

### "“When I correct you on the Mac or in the browser, remember the correction everywhere—without copying the original private text—and let me see or undo the memory later.”"
- **useful because:** The system currently projects memory one-way as a clipped Mac blob; a correction made in one body can vanish when the next body speaks. A typed, short-lived, source-linked memory event would make the pendant feel like the same assistant while preserving revocation and sensitivity boundaries.
- **path:** mac → browser → relay → pendant
- **model tier:** background model only when extracting a candidate preference/task; deterministic normalization, expiry, projection, and retraction thereafter
- **latency:** Under 500 ms to append a correction locally; under 3 seconds for relay projection on the next conversation
- **cost:** <$0.005 per correction; most work is bounded event storage and projection, with model use optional and only for ambiguous wording
- **security:** Never persist raw quotes by default. Classify sensitivity before fan-out, retain source and confidence, use the existing retracted event semantics, and make “forget this” emit a tombstone to every projection. A secret or sensitive fact must not be spoken merely because it is remembered.
- **missing:** A production writer in the Mac bridge and browser-result path to POST /v1/memory/events; The relay_memory_events migration in the actually deployed schema; A source-linked deletion/retraction cascade from local facts/context graph to the fleet event; A projection read integrated into relay context handoff instead of inheritedText alone

### "“When you tell me nothing is waiting, also tell me what you actually checked, what was unreadable, and what you could not see—without making me interrogate the system.”"
- **useful because:** The owner cannot currently distinguish an empty life from an unreadable source: unauthorized EventKit reads become empty arrays, browser absence can mean offline, and pull-only triage can silently omit work. This capability makes negative answers honest and useful by attaching a compact coverage statement to every briefing or status answer, rather than claiming all-clear from missing evidence.
- **path:** relay → mac → browser → pendant
- **model tier:** Deterministic source-coverage evaluator first; use the slower model only to phrase a concise explanation when sources conflict or the owner asks follow-up questions
- **latency:** Add at most 300 ms for local coverage checks and 2 seconds for cross-surface checks; spoken answer should fit one short sentence plus an optional detail on request
- **cost:** <$0.002 per answer when source checks are cached; model cost only for ambiguous explanations
- **security:** Expose source names and freshness, not private contents. Do not reveal whether a sensitive account contains data to a bystander; use a generic “a private source was unavailable” form unless the owner is authenticated and requests detail. Preserve evidence references so the owner can inspect the basis.
- **missing:** A uniform typed coverage envelope for calendar, mail, reminders, browser, jobs, and pendant inputs, distinguishing empty, unreadable, stale, offline, and not-requested; Fix the two all-clear paths that treat unauthorized EventKit emptiness as success, and require corroboration before suppression; A briefing/pendant speech integration that emits coverage alongside conclusions without dumping raw source text

### "“Only interrupt me for a question when the answer will prevent repeated mistakes; group those questions, explain what each answer changes, and let one answer fix every surface.”"
- **useful because:** Today ambiguity is paid for repeatedly: the relay, Mac, browser, and pendant can each make a different reasonable guess about the same person, place, or deadline. The owner should get a small, ranked clarification queue rather than surprise questions or silent assumptions. Each answer would be scoped, expiring when appropriate, and visibly linked to the behaviors it changes.
- **path:** pendant → relay → mac → browser
- **model tier:** Background model ranks and clusters unresolved ambiguities; deterministic storage and policy decide whether a question is worth interrupting for; realtime only asks the selected question
- **latency:** No interruption for low-value ambiguity; generate a batch within 5 seconds after a conflict is detected, then ask one short question at an owner-chosen opportunity
- **cost:** <$0.01 per clustered clarification batch; embedding/model work is limited to genuinely unresolved conflicts
- **security:** Questions must not quote sensitive source material aloud. Show the minimum context needed, record the owner's answer as a scoped preference rather than a universal fact, and require explicit confirmation before it changes external actions.
- **missing:** A durable clarification record with scope, expiry, alternatives, owner answer, and affected behaviors; A ranker that estimates mistake cost and interruption cost instead of treating every conflict equally; A fan-out writer so the accepted answer reaches relay, Mac, browser, and pendant projections with provenance and revocation

### "“When I tell you ‘that’s wrong,’ find the exact claim you used, show me where it came from, stop it from influencing future actions, and ask only for the replacement fact you actually need.”"
- **useful because:** A correction today can fix the current conversation while stale copies remain in facts, context graph, browser findings, or relay projections. The owner should be able to repair one mistaken belief rather than hunt through stores or continue being contradicted by another body.
- **path:** pendant → relay → mac → browser
- **model tier:** Realtime for binding the spoken correction to the current claim; deterministic provenance traversal and retraction for the write path; background model only to propose a replacement when the owner did not provide one
- **latency:** Acknowledge the correction in under 1 second, produce the source chain in under 3 seconds, and finish the scoped retraction before any dependent external action can run
- **cost:** <$0.01 per correction; storage traversal and tombstones dominate, with model use optional
- **security:** Never repeat the mistaken sensitive value aloud. Require owner confirmation before replacing a fact that could affect an external action. Retractions must be durable, idempotent, source-scoped, and visible in receipts; preserve only the minimum audit metadata needed to explain the correction.
- **missing:** A claim-to-source dependency edge on every derived fact, including capsule or browser provenance identifiers; A cross-store retraction transaction covering local facts, context graph, fleet memory, pending plans, and cached projections; A speech-safe claim binder that identifies the active item without trusting free-form text alone


## Changes it proposed to its own stack

### `relay` — Give relay_jobs the same lease semantics already used by relay_routines: add claimed_until and lease_owner, atomically claim with a bounded lease, periodically requeue expired processing jobs, and preserve an attempt number plus the existing idempotency/receipt data. On reconnect, the Mac must resume only from a lease-safe checkpoint or report the job as needing review; it must never blindly repeat a non-idempotent step.
- **owner gets:** A Mac sleep, crash, or dropped link currently leaves work stuck as processing for up to 24 hours. The owner gets either a job that quietly never finishes or is tempted to repeat it. This makes “finish that for me” survive ordinary laptop interruptions without duplicate sends or purchases.
- effort: Medium: schema migration, D1 and memory-store parity, claim/requeue sweep, bridge handling, and tests for crash-after-effect. Reuse the working routine lease implementation rather than inventing a new protocol.  ·  risk: A lease expiry during a slow external action could cause a duplicate. Mitigate with attempt fencing, actionIdFor idempotency, and fail-closed requeue for steps lacking a receipt. Recovery is an explicit review state, not an automatic replay.
- cost: Negligible storage and one periodic database sweep; no model cost.  ·  latency: Normal jobs gain one conditional claim update; reconnect recovery becomes bounded by the sweep interval instead of a 24-hour TTL.
- security: Improves auditability. Lease tokens must be unguessable and never authorize a different job; receipts remain the source of truth for already-applied effects.
- depends on: Persist relay-job-id to Mac-job-id mapping as queryable metadata; Use existing action idempotency keys and POST /jobs/:jobId/receipts; A bridge reconnect path that distinguishes safe retry from owner review


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing advances: (1) a delivery contract that proves an urgent alert was actually downloaded/played and safely falls back across surfaces without leaking private content; (2) relay job leases and fenced requeue so Mac sleep or crashes no longer strand work for 24 hours or invite duplicate side effects; and (3) fleet memory that finally writes the existing typed, expiring, retractable events so a correction made on Mac/browser reaches the pendant as the same mind. The first is the most owner-visible: “did you actually get the urgent thing?” becomes answerable rather than assumed.

**Biggest unknown:** I still need owner-set values, not guessed defaults: the permitted fallback order (pendant/Mac/browser), which sensitivity classes may cross each boundary, and which alert classes are allowed to interrupt. Technically I also need confirmation of the deployed relay schema/migration state and a queryable relay-job↔Mac-job correlation; without those, delivery proof and lease recovery can only be partially implemented.

