# Harness derivation — mac-planner — round 281

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Get me ready for my next meeting: find the meeting materials in my files and browser, build a one-page prep packet, open it beside the meeting link, and tell me the three things I need to decide.”"
- **useful because:** This is the system's highest-value everyday behavior: it combines what the Mac can read locally, what the browser alone can see behind logged-in sessions, and the pendant's interruption-free spoken interface. The result is not a generic summary; it leaves the owner with the actual document and meeting link ready, plus a compact decision list they can hear while walking to the call.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use the cheaper background model for file/tab/calendar retrieval and packet drafting; use realtime only to answer a follow-up spoken question. The relay should merge calendar identity, browser session evidence, and Mac file evidence before drafting.
- **latency:** Initial packet in 20–45 seconds; pendant answer in under 2 seconds after the packet exists. Browser and Mac reads can run in parallel.
- **cost:** About $0.01–$0.06 per preparation depending on document extraction; realtime follow-ups dominate cost only if the owner asks questions.
- **security:** Authenticated browser pages and local documents leave their surfaces only to the relay/model. Redact secrets and unrelated tabs, retain source URLs and hashes rather than whole documents where possible, and never send or edit external content without an explicit later request. The packet should be staged locally first so a failed run cannot destroy source material.
- **missing:** A browser-to-relay bounded page/document extraction operation that returns citations and selected text without screen scraping; A cross-surface packet assembler that can correlate a calendar event with browser tabs and local files; A typed local packet open/layout action (or a Shortcuts handoff) with a receipt

### "“Run a complete pendant bench check now, without opening the microphone: verify the USB-connected nRF9160 and audio bridge, run the synthetic two-way audio fixture, collect timing/drop counters, and leave me a pass/fail report I can attach to a bug.”"
- **useful because:** The hardware is physically on this Mac today even though LTE registration is absent. This turns a fragile engineering ritual into a spoken, repeatable answer: is the worn device healthy, and which measured acceptance criterion failed? It exercises the exact audio path that has repeatedly regressed, without recording the owner or pretending USB is a product transport.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Use a cheap background model to execute the fixed diagnostic procedure and parse counters; use realtime only if the owner asks why a metric failed.
- **latency:** A fixture run may take 30–90 seconds; provide immediate acknowledgement and a final receipt, not a conversational spinner.
- **cost:** Under $0.01 per run; USB test execution and log storage dominate, not model tokens.
- **security:** The fixture must generate synthetic frames only and explicitly keep the microphone closed. Restrict shell commands to an allowlisted test script and the two observed USB device paths; redact serial logs that could contain environment paths. No firmware flashing or arbitrary writes should be implicit.
- **missing:** A bounded bench-procedure runner that can invoke the already-accepted audio_path_diagnostic_fixture over USB serial, capture its structured report, and distinguish timeout from a measured failure; A stable parser for the acceptance numbers: alias rejection, encode/decode cost, mic drops, tx starvation, clipping, and packet completion; A report artifact/receipt route that links the fixture run to the exact firmware build and timestamp

### "“Put me into writing mode for the next 45 minutes: identify the document I was last editing, open only the references I used for it, start the right timer, silence distracting apps, and restore my previous workspace when I say ‘I'm done’.”"
- **useful because:** The owner should be able to change physical context with one spoken request while away from the keyboard, then get the exact prior desktop back instead of manually reconstructing it. The Mac knows apps and files, the browser bridge knows logged-in reference tabs, the relay can keep the timed state, and the pendant is the only interface that remains available while the owner is moving around.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Cheap model for deterministic workspace inventory, matching recent documents, and timer bookkeeping; realtime only for the short spoken command and completion acknowledgement.
- **latency:** Acknowledge in 1 second, enter the workspace within 8 seconds, and restore within 8 seconds of the exit phrase.
- **cost:** Under $0.02 per transition; model reasoning is minor, while Mac UI and browser operations dominate latency.
- **security:** Capture a redacted workspace manifest (app bundle IDs, window titles, tab URLs, file paths) before mutation; do not capture page bodies or keystrokes. Make restore idempotent and keep the manifest local with a TTL. Because FULL_CONTROL_MODE currently has no gate, this routine must consult an owner-configured policy entry and stop when that entry is absent; it must never silently close unsaved documents.
- **missing:** A semantic window/tab inventory with document identity and unsaved-change state, beyond the current running_apps/foreground_app observation; An atomic workspace snapshot/restore primitive spanning Mac windows, browser sessions, and Shortcuts timers; A timer/state coordinator that survives relay reconnects and expires without leaving apps muted or hidden

### "“Before I act on this, check whether the calendar event, the logged-in web page, and my local documents agree. Tell me exactly which dates, names, amounts, or obligations conflict, and show me the source for each claim.”"
- **useful because:** The owner currently gets summaries, but not a cross-surface consistency check. This would catch a changed meeting time, stale contract amount, contradictory deadline, or phishing-like mismatch before it becomes an expensive mistake. It is a verification capability, not another briefing or preparation flow.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use a background model for extraction and deterministic field comparison; use realtime only to explain a flagged contradiction conversationally.
- **latency:** 20 seconds for up to five sources; speak an immediate “checking” acknowledgement and return only material conflicts.
- **cost:** Approximately $0.02–$0.08 per check, dominated by document/page extraction and model comparison.
- **security:** Transmit only relevant excerpts and structured claims, not whole mailboxes or unrelated browser tabs. Every claim must retain source, timestamp, and content hash. Never silently resolve conflicts or edit records; this is read-only until the owner separately asks for a change.
- **missing:** A cross-surface claim extractor with source citations and timestamps; A contradiction engine that distinguishes true conflicts from harmless wording differences; A spoken, citation-preserving result format that can be revisited from the dashboard

### "“While I present, keep a private cue channel on the pendant: show me the current slide and my next talking point, advance the deck when I say ‘next’, capture audience questions I mark, and give me a concise question list when I finish.”"
- **useful because:** A presentation is one of the few moments when the owner cannot safely look down at a laptop. The browser or Mac can control the deck, the relay can maintain the agenda and question log, and the pendant can deliver discreet cues without exposing them to the audience. Today these surfaces operate separately and cannot maintain a synchronized presenter state.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use a low-cost background model to prepare slide notes and organize captured questions; realtime handles only the low-latency cue and ‘next’ exchange.
- **latency:** Cue response under 500 ms; slide-state reconciliation under 2 seconds; post-presentation question digest within 30 seconds.
- **cost:** About $0.03–$0.15 per presentation, mostly slide extraction and question summarization.
- **security:** Presentation contents and audience questions may be confidential. Keep the cue transcript local by default, expose only explicitly marked questions to the relay, and never advance or interact with a browser tab that is not the owner’s selected presentation session. Require a visible session indicator on the dashboard.
- **missing:** A presentation-session state machine joining active slide identity, cue index, and owner-marked questions; A low-latency pendant command path that can distinguish cue requests from ordinary conversation; A browser/Mac slide adapter supporting read-current-slide and advance without relying on fragile screen coordinates; A post-session export with explicit audience-question redaction

### "“Tell me what changed across this project since I last looked: compare local files, the relevant browser workspace, and my calendar or mail, and report only new decisions, changed deadlines, and unresolved blockers with evidence.”"
- **useful because:** The owner should not have to reread an entire project after an interruption. This is a time-bounded, evidence-backed delta across surfaces that no individual node can see: local edits on the Mac, authenticated web changes in the browser, and commitments in Calendar/Mail. It answers ‘what changed?’ rather than producing another generic summary or restoring a workspace.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use a background model for incremental diffing and clustering; use realtime only to answer follow-up questions about one change.
- **latency:** Initial delta in 30–60 seconds for a bounded project; subsequent refreshes under 10 seconds using stored hashes and cursors.
- **cost:** Approximately $0.03–$0.12 per refresh; source scanning and browser extraction dominate.
- **security:** Persist only redacted source fingerprints, extracted commitments, and provenance—not full mail or page archives by default. Scope every run to an owner-selected project and time window. Mark deletions and inaccessible sources explicitly so absence is never reported as proof that nothing changed.
- **missing:** Per-source incremental cursors and content hashes for local files, browser pages, Calendar, and Mail; A project-scoped change model that classifies new, modified, resolved, and unresolved claims; A durable provenance store with retention and redaction controls; A relay query that can merge deltas while preserving source identity


## What it asked for

_Nothing._
