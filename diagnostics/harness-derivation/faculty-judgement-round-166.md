# Harness derivation — faculty-judgement — round 166

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “what actually needs me now?”, give me one ranked next action across my calendar, mail, browser, routines, and pending pendant items, explicitly separating known facts from unreadable sources and asking at most one clarification."
- **useful because:** This would become the system's most valuable daily behavior: not another feed or digest, but a single honest decision about where the owner's attention buys the most. It can refuse to manufacture an all-clear when EventKit or the browser is unreadable, cite the evidence behind the ranking, and turn the selected item into a reversible reminder, note, or draft without losing the source.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** A deterministic arbiter and ranker should do the first pass; use the expensive realtime model only to resolve ties, phrase the one spoken sentence, or ask the one missing-data question. Background source collection uses the cheaper model or no model.
- **latency:** Under 2 seconds when cached; up to 8 seconds for a fresh browser/mail/calendar collection. The pendant should speak a short provisional status if a source exceeds that budget.
- **cost:** Usually <$0.01 per invocation; model cost is dominated by one tie-breaker/phrasing call, not the source reads.
- **security:** The spoken result must never expose secret or sensitive source text by default. Every candidate needs evidence references, freshness, sensitivity, and an unreadable/unauthorized state. External actions remain draft-or-confirm under autonomy_policy_evaluate; no guessed calendar permission may count as an empty calendar.
- **missing:** A unified candidate envelope carrying source freshness, unreadable state, due time, sensitivity, and evidence references; A real ranking adapter that consumes reconcile_personal_state plus mail/browser/page-watch/routine results; A route that exposes owner idle/presence to attention_arbitrate; A compact dashboard explanation of why one candidate won

### "While the pendant is plugged into my Mac, keep the conversation and audio alive across LTE/link changes: detect USB attach/detach, route audio and delivery ACKs over the live serial path, drain offline events, and tell me in one sentence whether my last reply was downloaded, started, finished, or lost."
- **useful because:** The hardware is physically present and testable now even though LTE registration is not. This makes the pendant dependable rather than mysteriously silent: a dropped radio or Mac bridge becomes an explicit transport handoff, and the owner gets truthful playback completion instead of assuming that generated audio was heard.
- **path:** pendant → relay → mac → dashboard
- **model tier:** No frontier model for transport state. Firmware and a small Mac serial supervisor perform detection, framing, replay, and deduplication; the realtime model is called only to phrase a recovery sentence when the owner speaks.
- **latency:** USB attach/detach detection under 1 second; ACK upload within 500 ms of a state change; recovery speech within 2 seconds after the next owner utterance.
- **cost:** Near-zero model cost for normal operation; approximately <$0.001 per recovery utterance if phrased by a small model. Engineering cost is a USB serial supervisor and test harness, not inference.
- **security:** Authenticate the serial session and bind events to deviceSessionId; never send raw microphone/audio content through the status path. Deduplicate by eventId and monotonic device sequence. A stale USB peer must not replay old ACKs or authorize actions.
- **missing:** A production USB serial transport/supervisor for /dev/cu.usbmodem00096003658* and the ESP32 bridge path; A typed transport handoff state shared by Mac and relay; Integration of audio_delivery_ack_queue and record_pendant_delivery_event with offline replay and duplicate suppression; A spoken recovery formatter that exposes only artifact status, not hidden content

### "When I say “that was wrong,” “not that,” or “remember this instead” after an answer, attach my correction to the exact spoken item and evidence, show me what will change, and use it to improve future rankings without silently rewriting history."
- **useful because:** The system currently can explain provenance and store facts, but it cannot learn a correction as a bounded, attributable change. A one-utterance correction would turn daily use into a safe feedback loop: wrong urgency, stale source, misunderstood preference, and bad action choice become explicit policy or memory updates rather than repeated failures.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use deterministic item/cursor binding and provenance lookup first. A small model classifies the correction as preference, factual retraction, source revocation, or one-time exclusion; use the realtime model only when the classification is ambiguous. No model should directly mutate durable memory without an owner-visible preview.
- **latency:** Bind the utterance in under 500 ms after playback stops; return a spoken acknowledgement in under 2 seconds. The dashboard may take several seconds to render the proposed change and evidence diff.
- **cost:** <$0.005 per correction, usually one short classification call; storage is tiny event metadata plus a bounded correction record.
- **security:** Corrections must be append-only and reversible, never destructive edits to the original evidence. Sensitive content stays masked in spoken confirmation. External actions and broad source revocations require physical consent or explicit dashboard confirmation. A correction must be scoped to item, source, task, or global preference and show that scope.
- **missing:** A durable correction event schema linked to item_id, cursor_token, provenance, and policy version; A preview-and-approve route for changing memory/policy, with rollback; An adapter that writes retractions to fleet memory and links derived facts to evidence before revocation; A spoken “undo that correction” path

### "Quarantine everything from this person, site, or project. Stop using it in answers or actions, show me every retained copy, and let me lift the quarantine later without pretending deletion succeeded."
- **useful because:** The owner can revoke individual evidence today, but cannot impose a durable source-wide boundary across facts, context-graph copies, browser provenance, fleet memory, prompts, and pending jobs. A single source quarantine would make trust manageable after a compromised account, stale website, or sensitive relationship changes.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic source matching, propagation, and enforcement; a small model may resolve aliases only after presenting them. No model decides that a source is safe again.
- **latency:** A quarantine acknowledgement in under 2 seconds; inventory and propagation report within 10 seconds. Enforcement must take effect before the next prompt or external action.
- **cost:** <$0.01 per invocation; most work is indexed local/relay reads and tombstone writes.
- **security:** Fail closed on ambiguous source matches. Quarantine must block prompt projection and external actions immediately, preserve an append-only audit trail, and avoid speaking sensitive retained content. Unquarantine requires explicit owner confirmation and must not restore revoked bodies.
- **missing:** A source-wide index linking evidence capsules to derived facts, context-graph entities, browser provenance, fleet events, jobs, and audio artifacts; A durable quarantine policy replicated to Mac and relay, with fail-closed enforcement at prompt, speech, and action boundaries; A complete inventory endpoint and propagation receipts; A distinction between quarantine, expiry, and irreversible deletion

### "Resolve this scheduling mess for me: find the conflicting commitments, propose the smallest set of changes that makes them feasible, draft the messages and reminders, and wait for my physical approval before anything is sent or moved."
- **useful because:** Today the system can read some sources, create reminders, and draft actions, but it cannot reason over a commitment's actual constraints and produce a coordinated repair. The owner gets a concrete choice instead of a list of conflicts, while every external change remains reviewable and reversible.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use deterministic interval/conflict analysis and autonomy policy for the safety envelope; use a cheaper planning model to generate alternatives; use realtime only for the short spoken choice. Browser and Mac agents gather authenticated details and prepare drafts, but never send without physical consent.
- **latency:** Initial conflict answer within 5 seconds from cached state; fresh source collection up to 20 seconds with progress spoken once. Draft alternatives within 30 seconds.
- **cost:** $0.02–$0.08 per repair, dominated by planning over mail/browser context; no model call for simple interval conflicts.
- **security:** Never infer a commitment from an unauthorized empty source. Keep recipient/content sensitivity out of spoken summaries. Every alternative needs affected objects, deadlines, reversibility, evidence, and an approval nonce; stale plans must be revalidated immediately before mutation.
- **missing:** A typed commitment/constraint representation spanning calendar, mail, reminders, browser tasks, and routines; A planner that can compare alternatives and explain collateral effects; A real cross-surface approval handoff and durable relay-to-Mac job correlation; Calendar read permission/route truthfulness and browser/mail source freshness metadata

### "When I say “the thing from yesterday,” “that client,” or “the draft we discussed,” resolve it to the few plausible items, tell me which one you mean if confidence is low, and keep the reference bound across my pendant, Mac, browser, and relay until the task is done."
- **useful because:** A wearable assistant fails at the moment the owner uses ordinary human reference instead of an ID. Today context handles and job IDs are implementation artifacts that do not form a durable, cross-surface referent. This would let the owner resume work naturally after a link drop, app switch, or day boundary without repeating the whole story.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic temporal/entity/source retrieval first, with confidence and candidate explanations; a cheap model resolves ambiguous language; realtime is reserved for the spoken disambiguation question. Never silently choose among close candidates for an external action.
- **latency:** Candidate list in under 1.5 seconds; one spoken clarification in under 2 seconds; durable binding after confirmation within 1 second.
- **cost:** <$0.01 per lookup, mostly local retrieval; <$0.03 for ambiguous semantic resolution.
- **security:** Referents must inherit the sensitivity and authorization of their underlying objects. Do not speak private candidate titles in public by default. Bindings expire, are revocable, and cannot broaden an action's scope. Preserve which candidate was selected and why.
- **missing:** A durable cross-surface referent record linking human aliases to evidence, jobs, drafts, reminders, browser tabs, and audio items; Entity resolution that handles time, aliases, and uncertainty without fabricating identity; A shared correlation key beyond the current unrelated relay/Mac/browser ID namespaces; Owner-visible resolution history and a scoped undo/unbind operation


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate capabilities: (1) a single honest “what actually needs me now?” decision across sources, with unreadability and evidence exposed; (2) USB-tethered transport continuity with truthful downloaded/started/finished/lost playback status; and (3) an item-bound “that was wrong” correction loop that is previewable, reversible, and provenance-linked. The first is the highest-value owner-facing behavior; the second is immediately testable on the physically connected hardware.

**Biggest unknown:** I still need the USB-tethered local voice feasibility result: which serial endpoint can carry the live session, whether the ESP32 bridge must be coordinated or is playback-only, and what reconnect framing already exists. I also need the owner to resolve two deliberately open policies before personalizing behavior: whether America/Chicago is the owner's actual location timezone versus the Mac's America/New_York routine timezone, and which notification-content classes may be spoken aloud. Until then I would ship conservative defaults and label uncertainty rather than infer either.

