# Harness derivation — faculty-judgement — round 42

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep track of the promises I make, and help me close the loop.”"
- **useful because:** People lose trust and peace of mind not because they cannot create reminders, but because commitments are scattered across spoken conversations, meeting notes, email, calendar, and private web apps. The pendant can capture a commitment at the moment it is spoken; the relay can turn it into a structured, uncertainty-labeled item; the Mac/browser can later verify context and prepare the smallest useful follow-up. The owner gets a short, prioritized spoken prompt and a ready-to-review draft rather than another noisy task list.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for a brief local confirmation (“I heard you promise X to Y by Friday—track it?”); a cheaper background model extracts candidate commitments, merges duplicates, and ranks lateness. Mac/browser perform authenticated evidence lookup and draft preparation; the dashboard is the review surface.
- **latency:** Pendant acknowledgement under 1 second; extraction within 30 seconds after an utterance or meeting; nightly reconciliation under 2 minutes. Never interrupt an active conversation except for high-confidence, time-critical commitments.
- **cost:** About $0.01–$0.05 per daily reconciliation depending on transcript and authenticated-page evidence; realtime cost is limited to explicit capture confirmations. Dominant cost is background transcript summarization and cross-source extraction, not reminders.
- **security:** Raw audio should remain transient and be discarded after transcription unless explicitly saved. Do not record bystanders or infer commitments while capture is off. Mail, calendar, and logged-in pages leave the Mac only as structured fields and cited snippets. Require confirmation before sending any reply, changing an appointment, or notifying another person; reminders and private drafts may be created automatically. Every item needs source, confidence, due date, and an edit/delete control.
- **missing:** A pendant-side commitment cue with an explicit capture/ignore affordance and offline queue; Durable cross-surface commitment records with provenance, uncertainty, deduplication, and expiry; A background reconciler that can inspect Calendar/Mail/private browser pages and produce cited evidence; A low-noise interruption policy and dashboard review queue for approve/edit/dismiss; End-to-end audio/transcription acceptance and reliable Mac Accessibility/Screen Recording plus browser-bridge authorization

### "“When something changes my day, re-plan the rest of it and tell me the one next thing to do.”"
- **useful because:** A daily brief becomes stale as soon as a meeting moves, a train is delayed, an urgent message arrives, or a task takes longer than expected. The owner should have a continuously updated, human-sized recovery plan: what can be safely dropped, what must move, who needs a draft update, and the single next action worth doing now. This is not another notification stream—it is a cross-surface response to disruption, with the pendant delivering one concise spoken choice.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use a cheap background model to maintain a compact dependency graph and simulate alternatives; reserve realtime for the interruption itself and for resolving an ambiguous tradeoff. Mac reads and edits reversible calendar/task state, browser reads authenticated travel/work updates, and the dashboard presents the proposed revised timeline with evidence.
- **latency:** Detect a meaningful disruption within 2 minutes; produce two at most ranked recovery options within 60 seconds; spoken interruption under 15 seconds. No interruption during an active call or quiet hours unless the plan threatens a hard deadline.
- **cost:** Roughly $0.02–$0.10 per disruption, dominated by authenticated-page reads and graph recomputation; ordinary unchanged periods should cost nearly nothing through event-driven triggers and cached facts.
- **security:** Calendar, mail, travel, and task data are sensitive and must stay in typed, expiring facts with source citations. Never cancel, reschedule, send an explanation, or contact another person without confirmation. The system must distinguish observed changes from inferred urgency, show why an item was moved, and provide one-step undo. Voice capture for the trigger must be opt-in and transient.
- **missing:** A cross-surface event bus that turns calendar, browser-watch, Mac, and pendant observations into deduplicated disruption events; A durable dependency/priority model for the owner's plans, including hard constraints, soft preferences, and uncertainty; A planner that can generate reversible schedule alternatives and explain the tradeoff in one sentence; A pendant interruption policy with defer/snooze/accept buttons and an offline-safe pending decision; Authenticated browser and Mac observation/action reliability, plus a dashboard timeline with provenance and undo


## What it asked for

_Nothing._
## Its own summary

Proposed a new cross-surface capability: Promise Radar. The pendant captures a candidate commitment with sub-second acknowledgement, background processing structures and deduplicates it, and Mac/browser evidence reconciles whether it was fulfilled before creating a concise reminder or a cited, unsent follow-up draft. It includes explicit capture consent, transient audio handling, provenance/confidence, quiet-hours/noise controls, and confirmation gates for any outbound action. I still need the capability's durable commitment/event primitives, the pendant capture skill, and the Mac Accessibility/Screen Recording plus browser-bridge authorization to make it real. Fresh perception still reports those permissions false, browser offline, and computer-use disabled; audio end-to-end acceptance criteria also remain an important blocker.

**Biggest unknown:** Whether the orchestrator's newly granted persistence/audio work is actually live in production; current /observe evidence still shows the Mac and browser cannot perform the authenticated reconciliation.

