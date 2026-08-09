# Harness derivation — faculty-judgement — round 236

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What materially changed in my life since yesterday, and what is the one thing I should do next?”"
- **useful because:** This would be the system's single most useful daily behavior: not another inbox dump, but a short, source-linked change judgment across calendar/mail/browser/page watches/routines and completed actions. It would distinguish genuinely new obligations from repeated noise, say when a source was unreadable, and offer one reversible next step. The pendant gives the answer; the Mac and browser establish the facts; the relay arbitrates when to speak.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Background model composes the change set and candidate actions; realtime model only speaks the final one-sentence answer or handles a follow-up. Deterministic policy and provenance checks decide whether it may interrupt.
- **latency:** Under 10 seconds for an on-demand query; under 30 seconds for a scheduled morning run. One short spoken sentence by default, with a dashboard drill-down.
- **cost:** Roughly $0.01–$0.05 per run depending on mail/page volume; most cost is evidence summarization, not arbitration.
- **security:** Never claim a quiet day when EventKit is unauthorized: require the briefingTriage/meetingPrep empty-pair corroboration. Mail and authenticated browser content stay local unless the configured model boundary allows it. Every delta and recommendation carries evidence refs and an explainable policy verdict; external actions remain draft/confirm.
- **missing:** A durable yesterday/current baseline and cross-source diff writer (fleet memory has schema and routes but no production writer).; A real scheduled briefing invocation for runBriefingTriage; currently routines run commands but no briefing scheduler exists.; Owner-set policy for what counts as materially changed and whether a recommendation may be spoken.

### "“Before you do that, show me what this choice will break, delay, or create—and give me the safest reversible option.”"
- **useful because:** People need help with consequences, not just execution. The system would assemble a compact counterfactual around a proposed action: calendar and reminder collisions, browser/session effects, pending jobs, spend or external-audience exposure, and the undo path. It would let the owner choose deliberately without the Mac silently acting, and it works for ambiguous spoken requests where a normal plan is too shallow.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** A cheaper background model gathers and summarizes read-only evidence; the deterministic autonomy evaluator, stale-plan revalidator, and cross-surface preflight produce the safety verdict. Realtime is used only to clarify the owner's choice and read the result aloud.
- **latency:** Read-only preview in 5–12 seconds; never mutate during preview. After explicit choice, existing execution plus receipt/undo may run.
- **cost:** About $0.02–$0.08 per preview, dominated by browser/mail evidence and the counterfactual summary; policy checks are negligible.
- **security:** The preview must not leak secrets into a third-party model or expose page credentials to the pendant. It must show uncertainty and stale evidence, revalidate immediately before any mutation, and require the existing physical approval latch for high-impact or external actions. No “likely okay” may be treated as consent.
- **missing:** A typed consequence model that maps each action class to affected surfaces and known undo operations.; A durable cross-surface join between relay job IDs, Mac jobs, browser commands, and action receipts; today localJobId is only telemetry.; A real approval decision handoff on the relay; the current approval contract is documented but not wired across bodies.

### "“Keep my conversations intelligible: if the pendant is falling behind or audio is failing, fix the delivery path or tell me before I miss the answer.”"
- **useful because:** This turns device telemetry into a user-visible guarantee rather than a postmortem. The relay correlates pendant download/playback ACKs, UART packet loss and underruns, and pipeline receipts; it detects a degrading link before speech becomes unintelligible, chooses a measured lower-cost audio profile or pauses nonessential work, and gives one honest short alert. It must preserve the owner's current item and never claim playback happened without a pendant ACK.
- **path:** pendant → relay → mac → dashboard
- **model tier:** No expensive model for detection or profile selection: a deterministic quality controller uses measured thresholds and signed device events. A background model can explain trends in plain language; realtime only speaks an urgent user-facing alert.
- **latency:** Detect within one or two delivery artifacts (roughly 1–5 seconds); profile change at an utterance boundary; explanation under 15 seconds. No interruption for transient single-packet noise.
- **cost:** Near-zero model cost for normal operation; occasional explanation is under $0.01. Dominant cost is firmware/relay engineering and small telemetry storage.
- **security:** Telemetry contains opaque artifact/session IDs, not transcript content. Device events must be authenticated, monotonic, and deduplicated. A fallback profile must never silently lower speech privacy or route audio elsewhere. The controller should fail safe to queueing rather than repeatedly retrying or speaking over corrupted output.
- **missing:** A durable quality-controller and profile policy shared by relay and Mac; current pipeline routes expose artifacts/events but no closed-loop controller.; Firmware support for signed quality summaries/profile acknowledgements beyond the accepted delivery ACK queue.; A verified, live route for applying and rolling back audio profiles at utterance boundaries; do not assume per-browser audio control exists.

### "“When I correct you—‘not important’, ‘don’t ask me this again’, or ‘that was the wrong choice’—learn the rule, show me exactly what changed, and use it everywhere.”"
- **useful because:** Today each surface can make a locally reasonable decision, but the owner's correction does not become a durable, inspectable behavioral rule across the pendant, relay, Mac, and browser. This would make the system improve from real feedback instead of repeatedly irritating the owner. The owner could review, narrow, expire, or undo every learned rule.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Realtime model extracts the correction only when the owner explicitly states it; a deterministic compiler turns it into a typed policy delta. Background evaluation tests the delta against recent decisions; no model is needed at runtime to apply it.
- **latency:** Acknowledge the correction in under 2 seconds; show the proposed rule in under 10 seconds; do not apply ambiguous corrections until the owner confirms.
- **cost:** Under $0.01 for an explicit correction and near-zero for enforcement; occasional background conflict analysis is the main cost.
- **security:** A frustrated utterance must not silently alter permissions or disclosure boundaries. Rules need scope, expiry, confidence, provenance, and a visible undo. Never infer a global preference from one correction; default to the narrowest surface/action/topic scope.
- **missing:** A durable cross-surface policy-delta store with versioning and conflict resolution.; A feedback event emitted from spoken barge-in, dashboard review, and action undo, linked to the original decision.; A compiler that maps corrections to existing autonomy and attention policy fields without bypassing physical approval or disclosure policy.

### "“You did the thing—now verify that it actually achieved what I wanted, and tell me if the outcome is still unresolved.”"
- **useful because:** A completion receipt only proves that a command was accepted or a click occurred. The owner needs outcome-level closure: did the calendar state change, did the browser page reflect the update, did the expected file or reminder appear, and did the pendant actually deliver the spoken result? This capability would catch silent partial failures and stop the system from reporting success when the world did not change.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic postconditions handle files, receipts, browser state, calendar/reminder reads, and pendant delivery ACKs. A background model translates the owner's natural-language goal into reviewable postconditions; realtime only reports unresolved outcomes.
- **latency:** Verify fast effects within 5–15 seconds; schedule delayed checks for effects that need time. Speak only a concise unresolved warning, not a noisy success notification.
- **cost:** Usually under $0.02 per goal; browser and mail/calendar reads dominate, with scheduled checks capped by TTL.
- **security:** Verification must be read-only and least-privilege. It must distinguish “not observable” from “failed,” avoid rereading secret page fields, and never perform a compensating mutation without fresh confirmation. Every outcome claim needs before/after evidence and a source timestamp.
- **missing:** A typed postcondition schema and evaluator spanning Mac, browser, relay jobs, and pendant delivery.; A durable goal-to-action-to-observation join; current relay/Mac/browser ID namespaces are not a queryable foreign-key chain.; Read adapters for the owner state that is currently write-only or permission-ambiguous, with honest unreadable results.

### "“If one body of you disappears, keep my place: tell me what was heard, what was decided, and what still needs me—without replaying or repeating work.”"
- **useful because:** The owner currently experiences separate relay jobs, Mac jobs, browser commands, and pendant playback as disconnected histories. A dropped link, restart, or handoff can lose the conversational position even when individual receipts survive. This would provide one compact, source-linked continuity card: last owner utterance, active item, decisions made, pending approval, effects observed, and the safe next step, with idempotent resume rather than blind retry.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic event folding and idempotency decide what can resume; a cheap background model compresses the card. Realtime speaks only when the owner asks “where were we?” or when a safe handoff needs acknowledgment.
- **latency:** Recovery card available within 2 seconds from durable state; reconstruction from stale surfaces under 10 seconds. Never auto-replay a side effect.
- **cost:** Low ongoing model cost; occasional compression under $0.01. Storage and event correlation are the main engineering costs.
- **security:** Continuity cards must redact secrets and preserve source sensitivity. They must distinguish observed, planned, approved, and completed states. Replaying an action requires idempotency proof, stale-plan revalidation, and physical approval for external or irreversible effects.
- **missing:** A single durable event envelope and correlation key spanning relay, Mac, browser, and pendant—not merely telemetry localJobId.; A state-folding service that consumes context handoff, action receipts, browser results, and pendant delivery events.; A real durable relay-side approval decision and resume protocol, with duplicate suppression and explicit owner-visible lifecycle states.


## Changes it proposed to its own stack

### `relay` — Install a closed-loop spoken-audio quality controller that consumes authenticated pendant delivery ACKs and UART-derived metrics, maintains a per-session health state, and emits a signed profile decision (hold, retry once, lower complexity, or defer) at the next utterance boundary. Persist the decision and its evidence beside the pipeline receipt, and require a matching pendant ACK before marking an utterance delivered.
- **owner gets:** The owner stops hearing clipped, late, or missing answers without being told what happened; when quality is genuinely poor, the system degrades deliberately and preserves the current brief item instead of talking over failure.
- effort: Medium-high: relay state machine, firmware profile ACK/status frame, and Mac pipeline adapter; reuse existing event and receipt schemas where possible.  ·  risk: A bad controller could lower quality unnecessarily or loop retries. Bound retries, keep a known-good profile, require hysteresis, and expose a one-tap rollback/diagnostic draft. If telemetry is missing, queue rather than claim success.
- cost: Negligible runtime/API cost; modest D1 telemetry growth capped by per-session retention. Firmware change is engineering cost, not a new hardware bill.  ·  latency: At most one utterance-boundary decision; normal playback is unchanged. Failure detection adds 1–5 seconds of telemetry lag.
- security: Opaque authenticated IDs only; no transcript in telemetry. Signed profile commands and monotonic device sequence numbers prevent stale or forged quality decisions.
- depends on: The accepted audio_delivery_ack_queue must emit authenticated playback events.; The accepted pendant_diagnostics_and_bug_draft parser must expose normalized metrics to the relay.; A typed audio-profile apply/rollback route must be implemented; current pipeline inspection alone cannot change the profile.


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: a cross-surface “what materially changed?” judgment (the highest-value daily behavior), a consequence/undo preview before consequential actions, and a closed-loop audio reliability guardian that detects degraded delivery and preserves truthful playback state. I also specified the relay quality-controller change that makes the third real rather than merely connective.

**Biggest unknown:** The owner still has not supplied the policy values that determine what counts as materially changed, what may interrupt, and what notification content may be spoken. The system should ship conservative, named defaults and surface these as owner decisions—not silently invent them. Technically, the largest remaining blockers are durable cross-surface IDs/baselines, the unwired relay approval handoff, and a typed audio-profile apply/rollback path.

