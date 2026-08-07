# Harness derivation — faculty-judgement — round 133

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m leaving my desk—make sure I can pick up exactly where I am when I come back.”"
- **useful because:** The Mac captures the active work state (document names, browser tabs, unsent drafts, and the next unfinished step), the browser supplies authenticated tab context, and the relay turns it into a compact return card the pendant can read later. It prevents the daily cost of reconstructing scattered context after interruptions without recording page contents by default.
- **path:** mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** background for state compilation; realtime only when the owner asks for the card
- **latency:** Under 10 seconds to create the card; under 2 seconds for a spoken retrieval
- **cost:** About $0.01–$0.04 per snapshot, dominated by summarizing changed context; retrieval is near-zero
- **security:** Private tab titles and draft metadata leave the Mac to the relay; redact page bodies and secrets, encrypt at rest, and require confirmation before reopening or sending anything
- **missing:** A user-facing leave/return intent that atomically snapshots Mac and browser state; A compact encrypted return-card store with expiry and explicit owner deletion; Pendant playback of a selected return card over the currently available USB audio path

### "“I was away—tell me only what changed while I was gone, and put the important things in order.”"
- **useful because:** Instead of replaying every notification, the relay compares the last acknowledged moment with Mac job receipts, browser tab changes, scheduled-run results, and captured pendant events, then speaks a prioritized delta with source links. The owner gets a trustworthy absence summary and can ask to resume one item, not hunt through multiple surfaces.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** background reconciliation with a cheap model; realtime only to answer follow-up questions
- **latency:** Compile within 30 seconds of reconnection; spoken answer in under 2 seconds
- **cost:** $0.01–$0.06 per absence window, mostly event summarization; storage is small structured deltas
- **security:** Treat absence intervals and private account changes as sensitive; keep raw events on the originating device, send only hashes/snippets, and never infer urgency from message content without a cited source
- **missing:** A durable per-surface last-seen watermark and acknowledgement cursor; An event-normalization layer spanning Mac jobs, browser inspections, schedules, and pendant events; A spoken delta queue that supports dismiss, bookmark, and resume

### "“Give me a 25-minute focus sprint on this, and bring me back only if something truly urgent happens.”"
- **useful because:** The pendant is the low-friction start/stop control, the Mac opens the intended work and records the starting state, the browser suppresses nonessential tab activity, and the relay owns the timer and escalation. At the end it returns a one-sentence progress prompt and restores the prior workspace, turning intention into a bounded session rather than another reminder.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** No expensive model for timing; cheap background model to identify the target and summarize the end state; realtime only for spoken control
- **latency:** Start feedback under 1 second; end-of-sprint summary under 5 seconds
- **cost:** $0.00–$0.02 per sprint; model cost only when target disambiguation or summary is needed
- **security:** Do not close tabs or alter notifications irreversibly; save and restore a workspace manifest locally, and require confirmation before changing global Do Not Disturb or muting calls
- **missing:** A focus-session primitive with start/end timestamps, target, and restoration manifest; Browser and Mac adapters for reversible distraction suppression; A pendant-local start/stop control that works while USB-tethered and queues state if the link drops

### "“While I’m talking, quietly warn me if I’m about to promise something that conflicts with my calendar or existing commitments—never speak aloud unless I ask.”"
- **useful because:** The pendant’s always-near microphone can locally detect a possible promise, while the Mac supplies calendar and active conversation context. The relay checks conflicts and sends a private earcon or a short haptic/audio cue, letting the owner stay socially present instead of discovering the contradiction later. This is a genuinely new wearable-plus-agent ability: timely judgment at the moment of commitment, not another after-the-fact reminder.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime only for low-latency local utterance/commitment detection; a cheaper background model verifies the candidate against calendar and task state
- **latency:** Local cue within 1 second of a detected promise; conflict check within 3 seconds; no interruption by default
- **cost:** $0.02–$0.10 per active conversation hour, dominated by streaming speech analysis; calendar conflict checks are inexpensive
- **security:** Raw conversation must remain on the pendant or Mac unless the owner explicitly enables relay analysis. Default to ephemeral audio, visible recording status, a physical mute control, no storage of bystanders’ speech, and only transmit a structured candidate promise plus the minimum calendar facts. Never make or cancel commitments automatically.
- **missing:** An opt-in local conversation mode with a hard physical mute and ephemeral ring buffer; A commitment-candidate detector that distinguishes hypothetical language from an actual promise; A low-latency conflict query joining calendar, reminders, and pending jobs; A private cue protocol to the pendant that can alert without interrupting the conversation; A clear consent indicator for people nearby when the microphone mode is active

### "“I have about 40 minutes and low energy—choose one useful thing I can realistically finish, set it up, and stop me from starting something too big.”"
- **useful because:** The system would combine the owner’s available time, calendar gaps, open work, unfinished browser tasks, and recent completion history to select a genuinely finishable action rather than producing another generic priority list. The Mac and browser prepare only that task; the pendant starts a bounded session and can say 'stop' when the time window closes.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Background model for task sizing and selection; realtime only for the short spoken request and confirmation
- **latency:** A recommendation in under 5 seconds; setup in under 15 seconds; no autonomous destructive actions
- **cost:** $0.02–$0.08 per request, dominated by synthesizing task context; execution uses existing local actions
- **security:** Task history and calendar are sensitive. Keep raw documents local, expose the evidence behind the estimate, and ask before changing deadlines, sending messages, or closing work. Energy level is user-provided and must not be inferred medically.
- **missing:** A task-sizing model grounded in the owner’s actual historical completion times; A time-window and energy preference object that expires after each request; A reversible 'prepare exactly this task' transaction across Mac and browser; A pendant session timer with a private completion or stop cue

### "“When I’m reading something important, check the claims against independent sources and quietly flag what is uncertain or out of date.”"
- **useful because:** The browser extension supplies the exact authenticated page and selected passage; the relay searches independent sources and tracks publication dates; the pendant gives a concise private uncertainty cue instead of forcing the owner to open ten tabs. This protects the owner from stale policy, pricing, health, or technical claims at the moment they matter, while preserving the source trail for review.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Cheap background retrieval and claim clustering; realtime model only to turn verified disagreements into a short spoken cue
- **latency:** Initial check in 10–20 seconds; incremental checks under 3 seconds for a selected passage
- **cost:** $0.03–$0.20 per page, dominated by web retrieval and multiple-source comparison; cache unchanged sources
- **security:** Do not leak logged-in page content to public search. Extract only owner-selected text, redact names/account data, label sources and confidence, and never present a disagreement as proof of falsehood.
- **missing:** A user-invoked selected-passage capture from the authenticated browser bridge; A claim extraction and independent-source comparison pipeline with freshness scoring; A cited result object that preserves the exact passage, sources, timestamps, and uncertainty; A private pendant notification mode that does not interrupt the page or conversation


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: a leave/return work-state card, an absence delta that reports only meaningful changes while the owner was away, and a cross-surface 25-minute focus sprint controlled from the pendant. All three are deliberately connective: Mac state, authenticated browser context, relay timing/storage, and pendant delivery. The proposals were recorded successfully, though the recorder noted that their low-level building blocks already exist and the missing work is the connective primitives.

**Biggest unknown:** No new orchestrator grants are visible: discover(granted) returned zero. I still need the actual cross-surface persistence and pendant-delivery primitives (watermarks/ack cursors, return-card or focus-session storage, and USB-tethered pendant start/stop/playback) to know which of these can be run today versus requiring implementation.

