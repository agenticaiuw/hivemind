# Harness derivation — faculty-judgement — round 129

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I have 20 minutes. What is the one thing I should do now—and set it up for me?”"
- **useful because:** This is the system's highest-value daily decision: it converts a vague pocket of time into one concrete, achievable next action. The always-worn pendant supplies the interruption and spoken confirmation; the relay keeps the request alive; the Mac reconciles calendar, reminders, notes, current project, and machine state; the browser supplies private account context when relevant. It should prefer finishing an existing obligation over inventing work, explain the tradeoff in one sentence, and prepare reversible steps without sending or buying.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the short choice and spoken explanation; a cheaper background model compiles the candidate actions and scores fit against the time window.
- **latency:** Under 5 seconds for three candidates and a choice; preparation may continue as a durable Mac job with a spoken completion receipt.
- **cost:** About $0.01–$0.04 per request; most cost is the candidate-ranking context, not the brief final response.
- **security:** Private mail/calendar/browser data stays on the authenticated Mac/browser surfaces. Never send, delete, purchase, or commit without confirmation. Show which sources drove the recommendation and allow “not now” without penalty.
- **missing:** A reliable current-time/timezone authority (machine is America/New_York while remembered owner timezone is America/Chicago); A cross-surface candidate scorer that knows duration, reversibility, and interruption cost; A pendant-attached confirmation/continuation path while the Mac prepares the action

### "“Before I commit to this, show me what it will cost me next week.”"
- **useful because:** The system should turn a proposed calendar booking, purchase, reply, or workflow into a small life-impact preview: schedule collisions, travel time, deadlines displaced, recurring obligations, and which private facts it relied on. The browser can inspect the logged-in transaction, the Mac can compare Calendar/Mail/Reminders/Notes, and the pendant can read the before/after tradeoff aloud while the owner is away from the screen. This prevents the common failure of completing a locally correct action that makes the owner's week worse.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background model builds the impact graph and counterfactual; realtime model only answers follow-up questions and obtains the final approval.
- **latency:** A first impact slate in 10 seconds; deeper browser/account checks can run asynchronously and return a durable receipt. No irreversible mutation before explicit approval.
- **cost:** Roughly $0.03–$0.12 per preview depending on number of tabs and calendar items; browser extraction and context transfer dominate.
- **security:** Treat proposed changes and account pages as sensitive. Keep data on the Mac/browser bridge, redact unrelated events, show provenance and uncertainty, and require confirmation immediately before sending, buying, deleting, or booking.
- **missing:** A counterfactual impact graph spanning calendar, reminders, mail threads, and browser transaction fields; A typed preview format that distinguishes facts from forecasts; A single approval token bound to the exact before/after mutation

### "“I corrected you—make sure you stop using the old version everywhere.”"
- **useful because:** A spoken correction should become a controlled repair, not merely another note. The system would identify the stale fact and every dependent routine, briefing, draft, and browser watch; present the affected places; update only the approved scope; and retain the old value as superseded evidence rather than silently erasing history. This makes the owner's AI trustworthy over months, especially when timezone, work role, addresses, preferences, or recurring plans change.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Cheap background model finds dependent references and proposes the repair set; realtime handles the owner's natural-language scope choice and concise confirmation.
- **latency:** Acknowledge immediately on the pendant; produce the dependency list within 15 seconds; apply only after the owner says “all” or selects specific items.
- **cost:** About $0.02–$0.08 per correction, dominated by searching historical notes, routines, and browser-watch definitions.
- **security:** Never alter secrets or external account data by inference. Display old/new values, source and timestamps, affected artifacts, and an undo. Corrections should be local by default; cross-account propagation requires explicit approval.
- **missing:** A dependency index from durable facts to routines, briefs, watches, and pending jobs; A supersession-aware fact store with scope and expiry; A cross-surface repair transaction with preview and rollback

### "“Translate what they just said, and whisper the meaning to me without interrupting the conversation.”"
- **useful because:** A wearable can solve the social moment a phone cannot: privately translate a nearby sentence, preserve speaker turn-taking, and optionally suggest a culturally appropriate short reply. The pendant captures only the requested utterance, the relay runs low-latency translation, and the Mac/browser can supply terminology from an open document or authenticated glossary without exposing the whole conversation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime speech translation model for capture, translation, and brief speech output; a cheaper model may cache domain terminology but must not process ambient audio continuously.
- **latency:** First translated phrase in 1–2 seconds, with a local cancel button. No recording after the utterance window ends.
- **cost:** Approximately $0.01–$0.08 per translated turn, dominated by audio duration and realtime inference.
- **security:** Ambient speech is highly sensitive. Require a physical press-and-hold or explicit wake phrase, show a listening indicator, discard source audio by default, and never consult authenticated browser content unless the owner explicitly names the source.
- **missing:** A pendant/bridge duplex audio path with an explicit bounded listening window; Relay realtime audio translation and low-volume/private playback; A spoken-language and terminology preference store with automatic deletion of source audio

### "“What am I actually agreeing to here? Give me the one risk and one question to ask before I say yes.”"
- **useful because:** In a live conversation, the owner often needs judgment before a commitment, not a transcript afterward. A deliberate pendant button marks a short audio window; the relay extracts proposed obligations, money, dates, cancellation terms, and ambiguity; the Mac/browser checks an explicitly named document or account page; then the pendant whispers one risk and one clarifying question. It gives the owner leverage while there is still time to use it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime model for bounded extraction and one-sentence coaching; background model can produce a fuller private analysis after the conversation, never as the immediate answer.
- **latency:** Return a risk/question pair within 5 seconds of the marked window; keep recording off unless the owner starts another window.
- **cost:** About $0.03–$0.15 per window, mostly audio transcription and optional private-document retrieval.
- **security:** Consent must be explicit for every capture window; do not record third parties continuously or upload unrequested conversation. Label this as decision support, not legal advice. No external action or saved transcript without a second confirmation.
- **missing:** A hardware-triggered bounded capture mode with visible/physical recording feedback; A low-latency obligation-and-ambiguity extractor; A safe redaction layer before any Mac/browser lookup

### "“Once a month, tell me what keeps going wrong in my life-admin—and change one routine to make next month easier.”"
- **useful because:** Instead of another activity summary, the system should learn from outcomes: missed or rescheduled commitments, repeatedly deferred tasks, unanswered drafts, failed automations, and routines that arrive at bad times. It would explain one recurring friction with evidence, propose exactly one reversible behavioral or scheduling change, and apply it only after approval. The Mac supplies durable job/routine results, the browser supplies whether private workflows completed, the relay keeps the monthly report available, and the pendant makes it a short spoken conversation.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Cheaper background model performs the monthly longitudinal analysis; realtime model is used only for the owner’s short review and choice.
- **latency:** Analysis can run overnight; the owner gets a 60-second spoken finding and one proposed change, with a detailed dashboard available on demand.
- **cost:** Approximately $0.05–$0.25 per monthly audit, dominated by summarizing a month of receipts and routine outcomes.
- **security:** Use aggregate behavior, not raw message content, by default. Show every evidence item behind the finding, allow exclusion/deletion of sources, and never infer sensitive health, relationship, or employment attributes. Routine changes require confirmation and must be undoable.
- **missing:** A durable outcome taxonomy that distinguishes owner choice, external failure, and agent failure; Longitudinal analysis over receipts, routines, and browser-watch outcomes; A one-change-at-a-time experiment mechanism with measurement and rollback


## Changes it proposed to its own stack

### `context` — Install a user-visible temporal contract rather than silently choosing one timezone: maintain device timezone, remembered home timezone, and event timezone separately; when they disagree, ask once on the pendant which clock governs the current request, attach that choice to the resulting job/routine, and show the clock in every scheduled receipt. Expire travel/location overrides automatically and require re-confirmation when the device and event zones diverge again.
- **owner gets:** Reminders and morning briefs will happen at the time the owner means, not merely the time the Mac happens to report. It prevents silent missed meetings and 7am/7:30am routines drifting across travel or machine configuration.
- effort: Medium: typed temporal contract, one confirmation dialog/voice turn, scheduler integration, and migration of existing routines.  ·  risk: An extra question is mildly annoying; wrong carry-forward could still schedule incorrectly. Recover with a visible timezone label, a one-tap/voice “use device/home/event,” and routine-level undo.
- cost: Negligible API cost; one short realtime turn only when clocks conflict.  ·  latency: Adds 1–3 seconds only on ambiguous requests; normal requests unchanged.
- security: Timezone/location metadata is sensitive; retain only the selected zone and expiry, not a movement history.
- depends on: A scheduler that can store per-routine timezone and expiry; An owner confirmation path on the currently USB-attached pendant or voice relay; Existing machine-context and routine routes


## What it asked for

_Nothing._
## Its own summary

Round 129 produced four distinct additions. The strongest is a 20-minute “what should I do now?” navigator that combines the worn pendant’s immediate attention, relay continuity, Mac calendar/notes/reminders, and authenticated browser context, then prepares one reversible next action. I also proposed a consequence preview (“what will this cost me next week?”) before commitments, correction propagation that repairs stale facts and all dependent routines/watches with provenance and rollback, and a temporal contract that stops America/Chicago vs America/New_York conflicts from silently corrupting schedules. The owner-facing gaps are not more generic browser automation: they are a cross-surface candidate/impact graph, dependency-aware fact supersession, exact approval binding, and a timezone confirmation UX.

**Biggest unknown:** Whether the pendant can currently deliver or receive live audio over the USB-attached setup: it is physically testable but not relay-registered, while Accessibility/Screen Recording remain owner-side grants. Until that changes, the Mac/browser portions can run, but the uniquely wearable confirmation and interruption loop cannot be honestly claimed.

