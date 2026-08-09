# Harness derivation — faculty-judgement — round 269

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make sure my morning brief actually reaches me. If I didn’t hear it, give me the missed version—not a duplicate—and tell me exactly what was delivered.”"
- **useful because:** Today a routine can be marked completed when the relay/Mac generated audio, even if the pendant never downloaded or played it; duplicate 07:00 routines can also produce competing briefs. Delivery ACKs let the system distinguish generated, downloaded, started, finished, interrupted, checksum-failed, and no-audio, then recover with one concise replay. This is the single most useful daily capability: a briefing is not complete until the owner actually received it.
- **path:** relay → Mac → pendant → dashboard
- **model tier:** Cheap background model deduplicates and compresses brief items; deterministic policy handles ACK state and retry; realtime model is used only when the owner asks for a spoken catch-up or clarification.
- **latency:** No added latency to generation. ACK reconciliation runs within 30 seconds of an event; a missed-brief alert is queued on reconnect and should be audible on the next deliberate play press.
- **cost:** Near-zero incremental model cost for ACK/state transitions; roughly one short background summarization call only when a replay must be compressed. Storage is small event metadata per artifact.
- **security:** Store opaque artifact IDs, hashes, timestamps, and playback positions—not raw audio in the relay event. Do not replay private content automatically while the owner may be in public; route through the owner’s configured speak policy and attention arbiter. A checksum error or ambiguous ACK must produce a reviewable 'not confirmed' state, never claim success.
- **missing:** Wire record_pendant_delivery_event into the briefing/routine completion path and make event IDs idempotent end to end.; A durable mapping from routine/briefing item to artifact ID and a dedupe key across the duplicate 07:00 routines.; A delivery-aware replay scheduler that feeds attention_arbitrate and expires stale items.; A fix for relay job leases so a failed reconciliation cannot strand the source job.

### "“The Mac died or the browser disconnected halfway through that task. Recover it safely, show me what is still pending, and never repeat an external action just because the connection dropped.”"
- **useful because:** An in-flight job currently has no lease and can remain processing for up to 24 hours; relay and Mac IDs are not joinable, and a reconnect has no trustworthy checkpoint. The owner needs a recovery experience, not a dead job record: identify the exact step, revalidate current browser/Mac state, cancel stale work, and present only reversible or physically confirmed next steps.
- **path:** relay → Mac → browser → pendant → dashboard
- **model tier:** Deterministic lease/revalidation/policy machinery first; a cheap model summarizes the recovery packet. Realtime is used only if the owner asks what happened.
- **latency:** Detect an orphan within 1 minute; produce a recovery packet within 3 seconds after a surface reconnects. No automatic mutation during recovery.
- **cost:** Negligible model cost for ordinary recovery; one short summary call for complex multi-step jobs. Main cost is durable metadata: one checkpoint and join record per active job.
- **security:** Fail closed when the checkpoint is missing, stale, or sensitive. Revalidate before any retry; never replay a mutation from a pre-crash plan. Require the existing physical transaction approval latch for irreversible actions. Explanations must link evidence, plan, and effect, with secrets excluded.
- **missing:** Add lease_until and a requeue/orphan sweep to relay_jobs, using the working routine-lease pattern.; Persist relay-job-id ↔ Mac-job-id ↔ browser-command-id and the current step/checkpoint.; Have the Mac write a durable checkpoint before and after every action, including whether an external side effect was committed.; A recovery packet route/UI that invokes revalidate_pending_plan, cross_surface_preflight, autonomy_policy_evaluate, and explain_action_provenance without executing.; A pendant inbox item for 'recovery needs your decision', reusing the existing physical approval primitive.

### "“When two parts of my life disagree, don’t silently choose. Tell me what conflicts, which source is stale or unreliable, and ask me the smallest question that resolves it.”"
- **useful because:** The system already has separate readers and a reconciliation tool, but the owner still receives confident all-clear answers when EventKit is unauthorized, and source disagreement is not turned into a durable, actionable question. This capability turns uncertainty into a short, evidence-linked decision instead of a fabricated conclusion: calendar/mail/browser/device state are compared, confidence is explicit, and the question can be answered from the pendant or dashboard.
- **path:** relay → Mac → browser → pendant → dashboard
- **model tier:** Deterministic source health and conflict rules classify freshness, permission ambiguity, and contradictions; a cheap model writes the one-sentence question. Realtime answers only follow-up conversation.
- **latency:** Read-only scan under 5 seconds when sources are online; question appears in the next attention arbitration cycle. No external mutation until the owner answers and policy evaluates it.
- **cost:** Usually zero model calls; one small synthesis call for multi-source conflicts. Tiny durable records for conflict ID, source refs, and resolution status.
- **security:** Return provenance and confidence, not raw private snippets by default. Treat empty EventKit reads as unreadable unless corroborated; never infer the owner’s location from the Mac timezone. Resolution must be scoped and revocable, and a low-confidence answer cannot authorize an external action.
- **missing:** Extend reconcile_personal_state with source freshness/permission provenance, changed-only output, and explicit question objects.; Fix GET /notifications and GET /day-plan so unauthorized EventKit emptiness is not reported as all-clear.; Persist conflict/resolution links in fleet memory or the context graph with a writer and TTL; retract them when the source is revoked.; Add a pendant-safe question envelope and an idempotent answer path that feeds the existing policy and provenance tools.

### "“Before I commit to this, show me the consequences if I say yes, no, or later—across my real calendar, inbox, browser commitments, and current work—without changing anything.”"
- **useful because:** The owner can preview individual Mac actions, but cannot rehearse a consequential choice across all surfaces as competing futures. A counterfactual rehearsal would expose collisions, hidden follow-up work, deadlines, and irreversible effects before the owner commits, turning the pendant from an executor into a decision instrument.
- **path:** pendant → relay → Mac → browser → dashboard
- **model tier:** A cheap planning model builds candidate futures from read-only evidence; deterministic evaluators calculate conflicts, policy violations, and reversibility. Realtime is used only to explain the chosen branch conversationally.
- **latency:** Under 8 seconds for a normal branch comparison; no writes during rehearsal. The owner can request a deeper branch only after seeing the compact result.
- **cost:** One small planning call per rehearsal, with bounded evidence excerpts; most conflict and policy checks are deterministic. No external API spend unless the branch explicitly includes research.
- **security:** Rehearsal must be read-only and clearly labeled hypothetical. Never send, buy, delete, or alter calendar state while simulating. Sensitive snippets remain local or redacted; every predicted consequence carries evidence and a confidence level. A later real action must revalidate because the world may have changed.
- **missing:** A typed counterfactual plan format with branch IDs, assumptions, predicted effects, and expiry.; Read adapters for all participating surfaces, including a truthful calendar/reminder permission result rather than empty success.; A consequence engine that maps one proposed commitment to downstream browser, mail, calendar, and local-job effects.; A dashboard/pendant rendering that lets the owner choose a branch and then creates a fresh, revalidated plan instead of executing the simulation.

### "“When I ask what I know about a person, project, or place, give me the living view: what is established, what is merely inferred, what has gone stale, and what evidence would change my mind.”"
- **useful because:** Current memory can answer from accumulated facts, but it cannot present a calibrated, time-aware belief with supporting and contradicting evidence as one owner-facing object. This would prevent old assumptions from masquerading as current truth and make the AI useful for real decisions without pretending certainty.
- **path:** pendant → relay → Mac → browser → dashboard
- **model tier:** Deterministic projection computes freshness, source status, sensitivity, and contradictions; a cheap model compresses the belief map into a short spoken answer. Realtime is reserved for follow-up reasoning.
- **latency:** Under 5 seconds for a normal topic; evidence expansion is on demand. Spoken output defaults to one sentence with an option to hear the evidence chain.
- **cost:** Usually no model call for projection; one short synthesis call when multiple contradictory sources need language. Storage is bounded by summaries and source references, not raw quotations.
- **security:** Do not expose private evidence by default in audio. Distinguish observed, owner-asserted, and model-inferred claims. A source revocation must immediately remove its claims from the projection, and stale claims must never authorize an external action without fresh confirmation.
- **missing:** A unified belief projection over facts, context graph, browser provenance, evidence capsules, and fleet events.; Explicit claim links from derived facts to source capsules/jobs so revocation can propagate.; Freshness and contradiction semantics with per-kind expiry and a visible inferred-versus-observed distinction.; A topic-scoped owner query and a compact pendant-safe response format.

### "“When I am moving between places or contexts, carry only the right working set with me: what I was doing, what is next, and what must stay behind—then let me resume without repeating or exposing private material.”"
- **useful because:** The owner’s work is split across a browser session, Mac applications, relay context, and a worn device, but context handoff is currently a model handoff rather than an owner-controlled continuity boundary. A context capsule would make transitions intentional: preserve the task state and next action while excluding secrets, stale UI, and irrelevant history.
- **path:** pendant → relay → Mac → browser → dashboard
- **model tier:** Deterministic redaction, expiry, and surface capability checks construct the capsule; a cheap model summarizes the remaining work. Realtime is only needed when the owner asks to resume by voice.
- **latency:** Capture in under 2 seconds at a deliberate bookmark; resume in under 5 seconds after revalidation. No automatic cross-surface mutation merely because a capsule exists.
- **cost:** Small metadata write and bounded summary; one cheap synthesis call on capture or resume for complex work. No raw screen images or page bodies need leave the originating surface.
- **security:** Capsules need explicit audience/surface, expiry, sensitivity, and revocation. Never carry browser secrets, form fields, or private snippets to the pendant. Resuming must revalidate current state and require the existing physical approval boundary for irreversible effects. A dropped link must leave the capsule recoverable without replaying actions.
- **missing:** An owner-triggered capsule API that composes context handoff, browser provenance, job checkpoints, and current project state.; A typed allowlist of fields permitted on pendant, relay, Mac, and browser, rather than relying on prompt clipping alone.; A durable capsule index with expiry, revocation, and source-linked deletion propagation.; A resume planner that distinguishes 'continue reading/drafting' from 'repeat an external action' and refuses the latter without fresh approval.


## What it asked for

_Nothing._
## Its own summary

I discovered the newly granted decision/provenance/attention/delivery primitives and recorded three owner-facing capabilities: delivery-confirmed self-healing briefings, crash-safe cross-surface task recovery, and explicit conflict questions instead of silent source selection. The recorder flagged all three as adjacent to existing backlog clusters, so the important remaining work is wiring and narrowing rather than inventing more names. The first is the highest-value: generation is not delivery, and the pendant’s authenticated playback ACK can finally make the system honest about whether the owner actually heard a brief.

**Biggest unknown:** Implementation status of the newly granted primitives in the live code remains partial: especially the artifact-to-routine mapping, relay job leases/checkpoint joins, and a durable writer for conflict/retraction records. I do not need more owner preferences this round; those were explicitly declined. What is needed from the build is an inventory of the exact /catchup and approval routes before treating them as missing, followed by wiring one end-to-end delivery-confirmed briefing path.

