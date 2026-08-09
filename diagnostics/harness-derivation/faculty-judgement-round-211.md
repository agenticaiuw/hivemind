# Harness derivation — faculty-judgement — round 211

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **owner morning briefing reliability** — Owner has repeatedly requested a three-sentence world/US news brief; live owner state contains multiple daily brief routines at 07:00/07:30, including a research brief and a calendar/mail/files brief. Any new morning-brief feature must deduplicate these rather than add another routine.
  - evidence: discover(owner) returned 10+ identical news requests and scheduled routines rtn_2f7c2300, rtn_9c1f06d4, rtn_835c3d97.

## Capabilities it proposed

### "Give me one trustworthy three-sentence world-and-US news brief each morning, and make sure I can actually hear it or know why I missed it."
- **useful because:** The owner has asked for this repeatedly, yet scheduled research and brief jobs can complete without proving that the audio reached or was played. This turns a nominal 'completed' routine into a dependable morning experience with freshness, deduplication, and an honest fallback.
- **path:** mac-planner → browser-extension → relay → pendant → dashboard
- **model tier:** background for source collection and ranking; realtime only for a spoken fallback or owner follow-up
- **latency:** Collect within 2 minutes of the scheduled run; spoken fallback under 5 seconds after a missed-delivery decision.
- **cost:** Low: one background synthesis plus 3-6 browser reads; dominant cost is source retrieval and TTS, not realtime inference.
- **security:** Read-only public news by default; retain source URLs and short claims, not full articles. Never silently broaden to authenticated pages. Require owner confirmation before any non-news action.
- **missing:** A durable routine-to-artifact-to-pendant correlation ID; A scheduler policy that waits for record_pendant_delivery_event playback_finished or playback_interrupted; A compact fallback route that puts the same artifact into the existing alert inbox without duplicating it; A freshness/duplicate detector over source URLs and headlines

### "When I mark something on the pendant, turn that moment into a useful next step: capture what was happening, identify the relevant page or conversation, and leave me a reviewable note or reminder."
- **useful because:** A physical moment marker is available even when the owner cannot dictate. Today it is disconnected from the Mac/browser context, so the owner must reconstruct the moment later. Joining the marker to the nearest browser tab, focused app, active job, and recent audio item makes a one-press gesture materially useful without storing raw microphone audio.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Cheap deterministic join first; background model only to summarize the joined evidence into a draft.
- **latency:** Acknowledge the marker locally immediately; assemble context within 10 seconds when the Mac/browser are reachable; never block the pendant on model work.
- **cost:** Very low for deterministic joins; occasional background summarization is the dominant cost.
- **security:** The marker must carry no audio or page contents. Attach only least-privilege IDs, timestamps, app/domain and provenance references; redact secrets before any model prompt. Creating a reminder/note is reversible and allowed by owner policy, but external sends remain confirmation-gated.
- **missing:** A cross-surface marker correlation contract linking the existing offline_moment_bookmark payload to Mac/browser observations; A time-window join endpoint that returns provenance references rather than copied content; A durable reviewable draft record and idempotent marker processing; A pendant-to-relay path for the existing marker when LTE reconnects

### "If an action or briefing becomes stale while I am away, don't execute it blindly: tell me exactly what changed, preserve my place, and offer the smallest safe next step."
- **useful because:** The system can prepare plans and now has typed revalidation, policy evaluation, provenance, and playback delivery events, but these are separate. A user-facing stale-plan sentinel would prevent browser/Mac actions from acting on yesterday's page while making recovery comprehensible rather than simply failing.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Deterministic revalidation and autonomy policy; realtime model only when the changed state needs a short spoken explanation.
- **latency:** Revalidate in under 1 second for known sources; spoken explanation under 3 seconds; no action commits until the verdict is stable.
- **cost:** Near-zero for typed checks; model cost only for an ambiguity explanation or alternative wording.
- **security:** Fail closed on missing or sensitive evidence. Return changed fields and provenance, not page bodies or credentials. A stale plan can be discarded or re-prepared automatically only if reversible and policy permits; external or destructive actions require the existing physical approval path.
- **missing:** A watcher that invokes revalidate_pending_plan at lease expiry, browser navigation, or resumed playback; A durable link from plan ID to browser/Mac source fingerprints and owner-facing recovery options; A small reprepare operation that preserves the original intent but never reuses stale parameters; A pendant envelope that explains stale/prepared/awaiting-approval state without exposing sensitive content

### "Before I commit to something, show me what my day would look like if I say yes, delay it, or decline—including time, focus, travel, and downstream obligations—without changing anything."
- **useful because:** The owner can receive plans and execute actions, but cannot safely explore consequences across calendar, routines, browser commitments, files, and pendant attention before deciding. A reversible counterfactual would make the system useful as judgement rather than merely as an executor.
- **path:** faculty-judgement → mac-planner → browser-extension → relay → pendant → dashboard
- **model tier:** Background model for synthesis after deterministic collection; realtime only to narrate the selected scenario.
- **latency:** A first scenario in 10 seconds; additional branches in under 5 seconds from cached observations. No mutation during simulation.
- **cost:** Moderate background inference; collection and calendar/browser reads dominate latency, with no TTS cost unless the owner requests audio.
- **security:** Read-only by default. Do not infer or expose other people's private details beyond what is already visible to the owner. Clearly label estimates versus observed commitments. Never create, cancel, or send anything from a scenario.
- **missing:** A typed counterfactual model for time blocks, travel buffers, attention cost, and downstream dependencies; Read adapters for the owner's actual calendar/tasks and authenticated browser obligations with the existing empty-read honesty checks; A scenario cache keyed by evidence versions so stale simulations are visibly invalidated; A pendant summary format that reports tradeoffs without reading sensitive details aloud in public

### "When I am leaving for an appointment, tell me the latest honest departure time and keep updating me if the route, meeting, or my current task changes—without nagging me after I have left."
- **useful because:** The owner has a wearable that can interrupt them, a Mac that can inspect browser and calendar state, and a relay that can remain awake, but no capability currently turns those into a closed-loop departure decision. This is a concrete everyday benefit that no single surface can provide alone.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic deadline and state checks; background model only to resolve ambiguous event/location text; realtime for a short urgent spoken update.
- **latency:** Initial answer under 5 seconds; route/state refresh every 2–5 minutes; urgent change reaches the pendant within 10 seconds when connected.
- **cost:** Low-to-moderate: periodic route and calendar reads dominate; model calls only for ambiguity, not every refresh.
- **security:** Location and appointment details are sensitive. Keep raw location on the Mac when possible, send only departure deadline and coarse reason to the relay/pendant, and expire the state after departure. No external booking or messaging without confirmation.
- **missing:** A location/route provider and a trustworthy current-location source (Mac network/location or owner-provided origin); A typed departure-state machine with arrival deadline, buffer, route confidence, and hysteresis; A relay-to-pendant update envelope with expiry and acknowledgement semantics; A reliable signal that the owner dismissed or completed the departure prompt

### "Teach me what this system has learned about how I work, show the evidence and uncertainty, and let me correct one pattern without having to hunt through settings."
- **useful because:** The system accumulates facts, graph entities, browser observations, routines, action receipts, and delivery outcomes, but the owner cannot inspect the resulting behavioral model as a coherent, editable explanation. Making the model legible would let the owner benefit from adaptation without surrendering control to opaque memory.
- **path:** dashboard → faculty-judgement → relay → mac-planner → browser-extension → pendant
- **model tier:** Background model clusters patterns and writes explanations; deterministic provenance and sensitivity checks decide what may be displayed or spoken.
- **latency:** Dashboard view under 3 seconds from cached projections; corrections applied within 10 seconds; pendant receives only a short confirmation.
- **cost:** Moderate one-time clustering and low-cost incremental updates; provenance joins and graph projection dominate engineering rather than API spend.
- **security:** Behavioral patterns can be more sensitive than their source facts. Show source references, confidence, age, and affected surfaces; do not expose private page contents in spoken form. Corrections must retract or supersede every derived copy, including graph, facts, browser provenance, and fleet memory.
- **missing:** A unified read model joining facts, context graph, browser provenance, routines, receipts, and delivery events; A real derived-claim lineage and deletion cascade across those stores; A dashboard editor for accept, correct, suppress, and forget-pattern operations; A policy-controlled spoken summary that never reveals sensitive learned patterns by default


## What it asked for

### `c22-gawx` (context) — owner's desired morning brief reliability
- why: The owner repeatedly asks for three-sentence news briefs and has duplicate daily briefing routines. I need to know whether they want one canonical morning brief, and what fallback channel they prefer when it is not played.
- would change: I would choose whether to propose a single deduplicated routine with spoken fallback, or avoid assuming a preference and make the policy explicitly owner-configurable.

