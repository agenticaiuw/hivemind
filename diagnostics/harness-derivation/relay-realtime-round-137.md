# Harness derivation — relay-realtime — round 137

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Tell me what’s urgent across my private accounts and leave drafts ready to review, but don’t send anything."
- **useful because:** It saves time every day by triaging across multiple systems and preparing safe, reversible next steps.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception
- **model tier:** Planner/extractor model for triage; realtime only to present results and take quick follow-ups.
- **latency:** A quick spoken acknowledgement; results arrive when ready.
- **cost:** Cost is dominated by authenticated page reads and extraction, plus summarization.
- **security:** Logged-in data is sensitive. Must limit extraction to relevant fields, store minimal artifacts, and require approval before any submission or send.
- **missing:** Durable authenticated browser job runner and reliable command queue; Page-watch definitions and baselines for change detection; A review queue UI or voice-first review flow

### "Summarize what changed on the pages I care about and only alert me to meaningful changes."
- **useful because:** Reduces noise and prevents missed updates by turning web churn into a concise, evidence-backed feed.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception
- **model tier:** Cheaper extraction/compare pipeline; realtime for brief alerts.
- **latency:** Background cadence; alert only when changes are detected.
- **cost:** Dominated by page fetches and diffing; alerts are cheap.
- **security:** Must avoid leaking sensitive page content. Store normalized fingerprints and minimal snippets, not full pages, and respect quiet hours.
- **missing:** No scheduler for periodic checks; No durable watch registry with semantic diffing; No relay-to-pendant alert delivery channel that doesn’t depend on an active session

### "“What am I looking at, and what should I do next?” while I’m away from my desk."
- **useful because:** The pendant would combine a short spoken/audio description from the wearer, the Mac’s current screen/app state, and the authenticated browser tab into one grounded answer. Today the nodes can inspect these separately, but no owner-facing interaction fuses a worn-device observation with live computer context and explains the next safe step aloud.
- **path:** pendant → relay-realtime → mac-vision → mac-planner → browser-extension → dashboard
- **model tier:** Realtime relay for the short spoken response; faculty-perception/mac-vision extracts screen facts; a cheaper background model ranks relevant page content; mac-planner is invoked only when a concrete reversible next action is requested.
- **latency:** Under 4 seconds for an answer; under 10 seconds if a screenshot, authenticated page extraction, and citation synthesis are needed.
- **cost:** About $0.01–$0.05 per invocation, dominated by vision plus page extraction; no continuous audio upload.
- **security:** Only a user-triggered 5–10 second audio/screen snapshot leaves the pendant/Mac. Authenticated page text must remain in the relay’s encrypted transient context and be discarded after the response. Mutating Mac/browser actions require the owner’s explicit spoken follow-up, not inference from the question.
- **missing:** A pendant-triggered ephemeral audio/snapshot envelope with sequence and expiry; A Mac-vision endpoint that returns a redacted screen observation to the relay; A cross-node fusion endpoint that correlates pendant event, active tab, and Mac observation; A spoken response path that can cite which node supplied each fact

### "“I’m leaving now.” Have my work state safely follow me, and tell me what is still exposed."
- **useful because:** A single spoken departure command would make the worn pendant the owner’s reliable boundary: the Mac agent snapshots and labels active work, the browser facet records which authenticated sessions/tabs remain open, and the relay returns a concise exposure report (unsaved edits, playing audio, unlocked screen, sensitive tabs) while preserving a resumable handoff. Today no node can produce one cross-surface departure/resume contract.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Realtime only for acknowledgement and the short exposure summary; deterministic collectors gather Mac/browser state; a background model creates the resumable work digest.
- **latency:** Acknowledge in under 1 second, exposure report in under 8 seconds, with a later detailed digest available without keeping the voice channel open.
- **cost:** Roughly $0.005–$0.02 per departure, mostly digest generation; collectors should be local and free.
- **security:** The report itself can reveal sensitive apps, so deliver it only to the paired pendant/session and retain the digest encrypted with a short TTL. The owner explicitly initiated the command; locking/closing is opt-in per spoken phrase, while the default is observation and report.
- **missing:** A durable cross-node handoff record with encrypted field-level redaction; Mac collectors for unsaved documents, lock/audio/display state, and active app identity; Browser collector for authenticated tab sensitivity and pending form state; A resume command that reopens only the owner-selected work, not every prior session; A pendant-visible completion/acknowledgement event

### "“Translate that, explain the unfamiliar term, and give me a reply I can say back.”"
- **useful because:** In a face-to-face conversation the owner could use a button press and a short local audio window to get a whispered translation/explanation/reply through the pendant, with optional browser lookup for a technical term and Mac context for the relevant calendar/contact. This gives the worn node a genuinely unique use when the owner is away from the desk.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Realtime speech model for transcription, translation, and a one-sentence reply; a slower model is used only when the owner asks for domain research. Mac/browser are consulted only when the utterance contains an ambiguous proper noun or technical term.
- **latency:** First translation in 1.5 seconds after the capture window ends; explanation/reply within 4 seconds; lookup enrichment may arrive as a second spoken update.
- **cost:** About $0.01–$0.04 per exchange, dominated by realtime audio inference; local VAD and short clips keep bandwidth and spend bounded.
- **security:** The system must make capture visibly/audibly explicit (button press, LED, and a start/stop tone), never continuously record, and discard raw audio after transcription unless the owner says to save it. Do not send nearby people’s speech to browser/Mac unless the owner explicitly requests enrichment. Translation is advisory and must identify uncertainty.
- **missing:** A local button-triggered capture window and LED/audio capture indicators on the pendant/bridge; Streaming speech input/output with interruption support on the relay; A language-detection and translation route that can return partial results; An explicit enrichment request path to browser/Mac with per-utterance expiry; A compact pendant playback queue so translation and reply do not overlap


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: (1) pendant-triggered fusion of a spoken observation with live Mac screen and authenticated browser context, (2) a spoken departure command that creates a cross-node exposure report and resumable work handoff, and (3) explicit short-window face-to-face translation/explanation/reply through the pendant. The remaining work is not model prompting: it needs explicit pendant capture/indicator semantics, streaming audio playback, cross-node correlation, redacted transient handoff storage, Mac/browser state collectors, and expiry-safe enrichment paths. The pendant is physically testable over USB now, but these capabilities still need their device/relay contracts and end-to-end delivery acknowledgements.

**Biggest unknown:** Whether the live pendant/ESP32 firmware already exposes a button-triggered capture window, LED/audio start-stop indicators, and a playback queue over the currently connected USB serial links; the available context confirms the hardware is connected but does not expose those firmware semantics.

