# Harness derivation — faculty-judgement — round 212

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me my morning brief only once, and tell me whether I actually heard it.”"
- **useful because:** Today duplicate 07:00 routines can generate multiple briefs, and server receipts stop before the pendant has downloaded or played audio. This makes the brief a delivery contract: coalesce duplicate runs, produce one source-linked artifact, and recover visibly if playback never happened.
- **path:** relay-realtime → relay → mac-planner → pendant
- **model tier:** Use the cheap background model for gathering and compression; use realtime only for the owner's follow-up. Deterministic policy and ACK reconciliation should not call a model.
- **latency:** Generate within 2 minutes of the scheduled time; delivery state should be visible within 10 seconds of each pendant ACK, with no extra spoken interruption unless policy marks an item urgent.
- **cost:** Roughly $0.01–$0.05 per brief depending on source count; the dominant cost is background summarization/TTS, not arbitration or ACK storage.
- **security:** Never speak a permission failure as an empty calendar or mail result. Carry source IDs and sensitivity through the artifact, redact before TTS, and require owner confirmation before any follow-up mutation. Duplicate routine IDs must be coalesced idempotently.
- **missing:** A durable routine-run dedupe key and one canonical brief artifact ID shared by relay and Mac; A consumer that turns record_pendant_delivery_event into delivered/not-heard status and retries or queues a compact fallback; A scheduler hook that invokes attention_arbitrate before speaking

### "“If I miss something important, rescue it without nagging me: try the pendant, then my Mac, then leave me one reviewable draft.”"
- **useful because:** An urgent item currently either interrupts or waits in a queue; there is no end-to-end notion of an owner not receiving it. This would make missed delivery recoverable while preserving attention and confirmation boundaries: one attempt per channel, then a durable draft rather than repeated alerts.
- **path:** relay-realtime → relay → pendant → mac-planner → browser-extension
- **model tier:** Use deterministic attention_arbitrate and delivery ACK state for routing; use a cheap background model only to compress the item and draft wording. Realtime is reserved for an owner-initiated rescue question.
- **latency:** At most one channel transition per 15 minutes; a hard deadline may bypass the delay only under the owner policy. Draft creation should complete within 30 seconds after a confirmed missed delivery.
- **cost:** Usually under $0.02 per rescue; browser/Mac reads and TTS dominate, while the policy and ACK checks are negligible.
- **security:** A missed ACK is not proof the owner did not hear (offline playback ACKs can arrive later), so use expiry and provenance rather than guessing. Never send mail or submit a form; create only a reviewable local draft and require physical approval for external effects.
- **missing:** A durable rescue state machine keyed by artifact/item ID with idempotent channel attempts; An attention-arbitrate outcome that can schedule a later channel rather than merely suppressing; A trusted mapping from an audio item to a Mac/browser draft target, with stale-plan revalidation

### "“For the news you brief me on, tell me what is solid, what is disputed, and let me ask ‘why?’ without repeating the whole story.”"
- **useful because:** The owner has repeatedly asked for three short world/US headlines, but a short spoken headline hides source disagreement and freshness. This adds an epistemic layer: each sentence has a compact confidence and source trail, and a follow-up can expand only the selected item instead of replaying the entire brief.
- **path:** relay-realtime → relay → browser-extension → mac-planner → pendant
- **model tier:** Use a cheap background model for retrieval clustering and source comparison; use realtime only for the owner's “why?” or “what changed?” follow-up. Deterministic freshness and provenance checks run without a model.
- **latency:** Initial three-sentence brief in 60 seconds; source disagreement lookup in 3 seconds from stored evidence, otherwise a background refresh with an honest pending response.
- **cost:** About $0.02–$0.08 per brief, dominated by web retrieval and summarization; follow-ups are cheap if evidence capsules are retained.
- **security:** Store source URLs, timestamps, and short redacted digests rather than unbounded article text. Do not present model consensus as fact; speak “one source says” when sources conflict. Browser pages may contain secrets, so enforce existing redaction and origin policy before evidence leaves the Mac.
- **missing:** A reachable, durable cross-source comparison route (the existing crossCheck module is currently unmounted and in-memory); A source-linked news item schema shared with audio_brief_item_action and explain_action_provenance; A freshness/conflict policy surfaced to the owner rather than hidden in a score

### "“When I say ‘this morning’, use the right time zone, and warn me before a reminder or briefing lands at the wrong local time.”"
- **useful because:** The system currently has an authoritative Mac routine zone of America/New_York, an owner-memory sample of America/Chicago, and no pendant zone. Silent substitution can fire routines or create reminders at the wrong hour. This feature makes temporal interpretation explicit: resolve machine-local scheduling separately from uncertain owner-local intent, ask one concise clarification when they diverge, and preserve the chosen interpretation on the action receipt.
- **path:** pendant → relay-realtime → relay → mac-planner
- **model tier:** Use deterministic timezone parsing and policy for routine execution; use realtime only to ask the one clarification question. Background models are unnecessary.
- **latency:** Resolve unambiguous requests immediately; if the zones conflict, ask within one utterance and do not schedule until answered. Existing routines should continue using the authoritative Mac zone without pretending it is the owner's location.
- **cost:** Below $0.005 per request; almost all work is local parsing and a small durable preference write.
- **security:** A timezone is personal location metadata. Keep it out of spoken logs and third-party prompts unless needed. Never infer physical location from the Mac zone or zoneless pendant clock; preserve null/unknown rather than fabricate an instant.
- **missing:** A durable owner choice distinct from the Mac routine timezone, with provenance and expiry/change history; A temporal-intent parser that returns local date, zone source, confidence, and unresolved ambiguity; A confirmation path that binds the chosen zone to the resulting reminder/briefing receipt

### "“Notice how I actually listen, then make future answers fit me—shorter when I interrupt, fuller when I finish—and let me undo that adaptation.”"
- **useful because:** The system can record playback started, finished, and interrupted, but today those events only describe delivery. It does not learn the owner's real listening pattern. A bounded, reversible hearing-profile would reduce repeated interruptions and make the pendant feel conversational rather than mechanically verbose.
- **path:** pendant → relay-realtime → relay → mac-planner
- **model tier:** Use deterministic rolling statistics for interruption/completion patterns; use realtime only for the current conversation. No background model is needed.
- **latency:** Adapt on the next response; profile updates should take under 100 ms after an ACK. Never delay an urgent response while learning.
- **cost:** Negligible API cost; this is local statistics plus existing audio events. Occasional model savings are likely because responses become shorter.
- **security:** Listening behavior is personal telemetry. Store coarse aggregates, not raw audio or transcripts; make the profile inspectable, expiring, and explicitly resettable. Do not infer attention, consent, or comprehension from a single interrupted playback.
- **missing:** A durable hearing-profile record with decay, confidence, and a reset operation; A response-length/style policy that consumes playback outcomes without changing factual content; An owner-facing explanation showing which aggregate caused an adaptation

### "“Before I commit to a plan, let me hear the consequences of each option in the context of the rest of my day—not just a list of tasks.”"
- **useful because:** Existing planning can rank a day and preview individual actions, but it does not narrate trade-offs between competing choices: what becomes late, what attention is consumed, and which reversible commitments are displaced. This would turn planning into a small, source-linked decision rehearsal before execution.
- **path:** relay-realtime → relay → mac-planner → browser-extension → pendant
- **model tier:** Use deterministic schedule/conflict calculations first; use a cheap background model to phrase alternatives. Realtime is used only while the owner compares options aloud.
- **latency:** Produce two or three alternatives in under 10 seconds from current state; refresh after a state change or stale-plan revalidation.
- **cost:** Under $0.03 per comparison; model phrasing is the dominant cost, while schedule arithmetic is local.
- **security:** A rehearsal must not mutate calendars, mail, reminders, or browser state. Mark estimates versus observed commitments, show stale evidence, and require explicit confirmation before any external effect.
- **missing:** A typed alternative/impact representation rather than a single plan preview; A read-side join across calendar, reminders, mail, browser state, and existing commitments with freshness timestamps; A spoken comparison renderer that preserves uncertainty and supports selecting one alternative

### "“When something changes after I acted, tell me what that change invalidated and what—if anything—I should do now.”"
- **useful because:** The system can revalidate a pending plan and explain provenance, but the owner still has to discover that a completed action’s assumptions became false. This is a post-action consequence watch: it detects meaningful state changes, links them to the original decision, and offers a reversible next step instead of silently continuing an obsolete plan.
- **path:** relay → mac-planner → browser-extension → pendant
- **model tier:** Use deterministic source diffs, freshness, and policy evaluation; use a cheap background model only to summarize the consequence. Realtime speaks only when the arbiter permits interruption.
- **latency:** Check at natural source refreshes and within 1 minute of a relevant browser/calendar/mail change; suppress duplicate notices for a configurable window.
- **cost:** Usually under $0.02 per consequence; source polling and browser reads dominate, not the summarizer.
- **security:** Do not infer causality from timing alone. Require an evidence chain and confidence threshold, never undo automatically, and redact private source details in spoken alerts. External remediation remains staged and owner-approved.
- **missing:** A durable post-action watch linking an action receipt to the assumptions and sources it used; Typed changed-field diffs with provenance from browser/Mac sources; A consequence policy distinguishing informational changes from changes that warrant a draft, reminder, or approval


## What it asked for

_Nothing._
