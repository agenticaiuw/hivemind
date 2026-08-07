# Harness derivation — relay-realtime — round 148

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep listening and keep the thread going across my devices—if I stop talking on the pendant, pick back up on the Mac or browser without losing context."
- **useful because:** This would feel like a single conversation that follows the owner, instead of a bunch of disconnected sessions. It’s the most useful thing because it removes the biggest friction: context loss when switching surfaces.
- **path:** relay → pendant → mac-bridge → browser → integration
- **model tier:** Realtime for turn-by-turn speech; cheaper planner models for continuation and tool use when the owner isn’t actively speaking.
- **latency:** Sub-second while the owner is speaking; seconds are fine when resuming on another surface.
- **cost:** Low for voice turns; higher when summarizing long context or querying sessions. Cost dominated by context transfer and session reconciliation.
- **security:** Conversation history is sensitive. Only the owner’s surfaces should be able to resume. Needs explicit session binding and audit logs.
- **missing:** A relay-visible session inventory endpoint so the relay can see its own conversations; A durable conversation state store keyed to the owner and session; A reliable event channel to notify the Mac/browser to resume

### "If I say “remember this”, capture the last few seconds of speech, store it with a label, and later let me ask for it back."
- **useful because:** It turns fleeting spoken context into a usable memory. That’s uniquely valuable for a wearable because it’s hands-free and happens in the moment.
- **path:** pendant → relay → mac-bridge → storage
- **model tier:** Realtime for detecting the intent; a cheaper text model for summarizing and indexing.
- **latency:** Fast capture (under a second). Retrieval can take a few seconds.
- **cost:** Small per memory; dominated by audio storage and transcription.
- **security:** Stored audio/text is sensitive. Needs clear retention rules, encryption at rest, and a way to delete memories by voice.
- **missing:** On-device circular audio buffer or a relay-side short grace buffer; A memory index with labels and timestamps; Voice command to delete or list stored memories

### "Tell me if I’m talking but nothing is being sent—like the mic is muted, the bridge is down, or LTE is failing—and help me fix it."
- **useful because:** This is a daily-wear reliability feature. It prevents silent failure, which is frustrating and hard to diagnose while you’re out and about.
- **path:** pendant → bridge → relay → mac-bridge → integration
- **model tier:** Realtime for feedback; cheap diagnostics when needed.
- **latency:** Under a second for alerts while speaking; a few seconds for troubleshooting steps.
- **cost:** Low; mostly event telemetry and occasional diagnostics.
- **security:** Telemetry should be minimal and not include content. Only status and error codes should be sent.
- **missing:** A consistent health heartbeat from pendant and bridge; Standardized error codes for audio pipeline failures; A guided recovery flow (reconnect bridge, restart audio path)

### "When I ask “is this legitimate?” about a message, invoice, offer, or webpage, have my pendant return a short verdict with the exact evidence it checked across my authenticated browser, Mac files/apps, and recent conversation context."
- **useful because:** The owner gets a trustworthy answer to high-consequence everyday questions without manually copying information between devices; the worn front door, browser sessions, and private Mac data each contribute evidence no single node can reach.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → faculty-perception → faculty-judgement
- **model tier:** Realtime handles the spoken question and final concise reply; a cheaper background planner performs evidence extraction and comparison, with faculty-judgement synthesizing confidence and conflicts.
- **latency:** Acknowledge in under 500 ms; return a preliminary answer in 5 seconds and refine within 20 seconds if browser/Mac evidence is slow.
- **cost:** Roughly $0.03–$0.15 per investigation; authenticated page extraction and Mac-context retrieval dominate, while realtime speech should see only the compact question and final evidence summary.
- **security:** Sensitive browser pages and local files leave their surfaces only as narrowly scoped excerpts; citations and uncertainty must be retained. Never claim legitimacy from one source, and clearly say when evidence is unavailable. Require explicit confirmation before sending, paying, deleting, or replying.
- **missing:** A cross-surface evidence broker that accepts one question, queries browser and Mac in parallel, and returns typed cited evidence; A durable per-investigation record with source provenance, conflict detection, and expiration of sensitive excerpts; A relay response path that can deliver a multi-stage result to the pendant without making the owner repeat the question

### "Press the pendant button once during a conversation or while reading something and say “save this moment”; later ask “what did I save?” and hear a time-ordered, searchable digest that links the audio moment to the relevant Mac window, calendar event, browser tab, and any follow-up I mentioned."
- **useful because:** This turns an intentionally marked real-world moment into durable memory even when the owner is away from the Mac, instead of forcing them to take notes or remember which device held the context.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception
- **model tier:** A small background model segments and labels the captured moment; realtime is used only for the save command and later spoken retrieval. Vision/browser adapters attach optional context rather than transcribing everything continuously.
- **latency:** Button acknowledgement under 300 ms; save confirmation under 3 seconds; retrieval under 4 seconds for the first digest, with deeper source expansion on demand.
- **cost:** About $0.01–$0.06 per saved moment plus storage; audio transcription and optional screenshot/page metadata are the dominant costs.
- **security:** Capture must be visibly indicated by the pendant LED and be bounded to a short pre/post window, not ambient recording. Store encrypted, owner-scoped records with retention controls; browser page text and screenshots require source-level deletion. Never silently capture other people’s conversations.
- **missing:** A local short rolling audio buffer and explicit button-triggered capture window; A cross-device context correlator using timestamp, active Mac window, calendar, and browser tab identity; A searchable memory index and spoken retrieval endpoint with source links and deletion by voice

### "While I am away from my Mac, let me ask the pendant “what changed since I left?” and get only material changes across my open browser workspaces, Mac notifications/files/calendar, and any relay jobs—grouped by urgency, with a spoken explanation and a way to say “handle the first one.”"
- **useful because:** The owner can stay oriented while mobile without opening every device or receiving noisy notifications; the pendant supplies presence and speech, while the browser and Mac provide private state that the relay cannot see alone.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Background comparison and ranking use a cheaper model against compact snapshots; realtime only interprets the query, gives the ranked digest, and routes a selected item to action.
- **latency:** Return a cached baseline summary in 2 seconds; refresh browser/Mac sources within 10 seconds; acknowledge selected action immediately and report completion asynchronously.
- **cost:** Approximately $0.02–$0.10 per refresh, dominated by page/file diffs and Mac snapshot collection; caching avoids resending unchanged context.
- **security:** Snapshots must be encrypted, scoped to the owner, and diffed locally where possible. Redact secrets and unrelated content before model submission. “Handle” must preserve the exact selected item and action receipt so the owner can tell what changed and what was done.
- **missing:** A departure/return checkpoint that captures compact, content-redacted snapshots from Mac and authenticated browser tabs; A diff-and-urgency engine that understands semantic changes rather than raw timestamps; A pendant-friendly notification/status channel and action correlation from spoken selection through Mac/browser execution

### "When my spoken request is ambiguous, have the pendant silently ask my Mac and authenticated browser what I am currently looking at, then ask me exactly one useful clarification (“the Outlook draft or the Safari page?”) before carrying out the right action."
- **useful because:** A worn voice interface cannot see the owner’s visual context, while the Mac and browser cannot hear intent reliably. This eliminates the most frustrating failure mode—an action on the wrong app, tab, or document—without making the owner explain context they already have on screen.
- **path:** pendant → relay-realtime → mac-vision → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime interprets the utterance and speaks the one clarification; low-cost perception workers inspect active-window and tab metadata, while judgement resolves candidate referents. Action runs only after the answer is received.
- **latency:** Silent context probes in 1 second; clarification within 2 seconds of the utterance; execute within 5 seconds after the owner answers.
- **cost:** About $0.01–$0.05 per ambiguity, primarily Mac/browser context extraction; most requests need no extra model turn if confidence is high.
- **security:** Only inspect the foreground Mac window and explicitly connected browser tabs; do not transmit full screen contents unless needed. Show a visible pendant LED during inspection, expire candidate context quickly, and preserve an action receipt identifying the resolved target.
- **missing:** A low-latency context probe that joins active Mac window identity with browser tab identity; A referent-resolution contract returning ranked candidates and one safe clarification question; A relay conversation state that pauses execution, accepts the spoken answer, then resumes the same intent without losing target identity


## What it asked for

_Nothing._
