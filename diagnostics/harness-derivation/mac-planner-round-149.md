# Harness derivation — mac-planner — round 149

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m about to start a meeting—prepare me.”"
- **useful because:** The system would combine today’s Calendar event, the relevant recent Mail thread, and the owner’s currently open Safari tabs, then create a compact meeting packet on the Mac (agenda, unresolved questions, links, and a follow-up checklist) and speak only the top items through the pendant. This is more useful than a generic morning brief because it is tied to the meeting happening now and uses private browser context that the relay cannot access alone.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use realtime only for the short spoken request and response; use a cheaper background model for retrieval, deduplication, and packet composition.
- **latency:** Return a spoken three-item preview in 5 seconds; write the full packet within 20 seconds, continuing as a durable job if browser extraction is slow.
- **cost:** About $0.01–$0.04 per invocation; realtime audio dominates the interactive portion, while background summarization is small.
- **security:** Private Mail, Calendar, and authenticated tab text leave the Mac only as the minimum extracted context needed by the relay/model. Never send or alter mail. Show source links and timestamps in the packet; require no confirmation for creating a local file, but confirmation would be needed before any external send.
- **missing:** A single orchestrator job that joins Calendar/Mail reads with authenticated Safari extraction and writes one cited meeting packet; A pendant/relay intent for meeting preparation and a durable completion notification

### "“Capture this thought and put it where it belongs.”"
- **useful because:** A one-sentence voice capture would become a typed, reviewable item rather than another undifferentiated note: infer whether it is a reminder, calendar candidate, project note, or draft reply; attach the originating time and current project context; and place it in the right Mac destination while leaving ambiguous items in an inbox. The pendant supplies immediate capture, the relay interprets it, and the Mac performs the local write—something no node can do alone.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Realtime handles transcription and a fast intent guess; a cheap background model resolves project/context and generates the destination-specific text.
- **latency:** Acknowledge capture in under 2 seconds; persist the raw utterance immediately, then classify and route within 10 seconds. Never lose the raw capture if the Mac disconnects.
- **cost:** Roughly $0.005–$0.02 each; transcription/realtime turn dominates, with local file/Reminder/Notes writes negligible.
- **security:** Raw thought and inferred category are sensitive. Keep the raw item on the relay only until Mac receipt, redact account identifiers in telemetry, and expose an undo link. Do not send messages or create calendar events automatically; those become drafts or proposed actions.
- **missing:** A durable capture schema with raw text plus typed destination and confidence; A Mac-side adapter for creating Reminder/Note/draft artifacts and returning an idempotent receipt; Offline pendant queue and retry, which is especially important while the pendant is USB-attached but not LTE-registered

### "“Give me the evidence and options before I decide.”"
- **useful because:** For a question that spans private sources—such as whether to accept a meeting, follow up on an email, or complete a browser task—the hive would gather cited facts from Calendar/Mail and authenticated Safari, separate facts from assumptions, present two or three options with consequences, and save an editable decision packet on the Mac. The pendant gives a concise spoken answer while the Mac preserves the links and excerpts needed to verify it later.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use a cheaper reasoning model for source reconciliation and option generation; reserve realtime for the final spoken summary and follow-up questions.
- **latency:** Speak a provisional answer in 8 seconds, with a cited packet and complete source reconciliation in 30 seconds; if a source is unavailable, explicitly mark the gap rather than guessing.
- **cost:** Approximately $0.02–$0.08 per decision packet, dominated by private-page extraction and model context; cache unchanged page excerpts and mail snippets to reduce repeat cost.
- **security:** This is high-sensitivity cross-source synthesis. Keep source excerpts scoped to the current question, include provenance/timestamps, and never treat generated options as facts. Do not mutate browser pages, mail, or calendar; local packet creation is the only automatic side effect.
- **missing:** A typed evidence bundle format with source URL/message/event IDs, excerpts, freshness, and confidence; A cross-surface planner that can ask browser and Mac readers in parallel and reconcile contradictory data; A review UI on the dashboard that lets the owner mark a fact wrong or an option chosen

### "“Remember this page so I can use it from the pendant later.”"
- **useful because:** The owner can mark the current authenticated Safari tab, and the extension would capture a bounded, redacted semantic snapshot plus URL/title and save it as a named private reference. Later, away from the Mac or with the browser tab closed, the pendant can answer questions against that snapshot and say when it was captured. This turns the browser’s otherwise ephemeral private context into a deliberate handoff without granting the relay ongoing account access.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a cheap background model to compress and redact the page; realtime is only for the pendant interaction and follow-up question.
- **latency:** Acknowledge the save in 2 seconds, finish extraction in 10 seconds, and answer later questions in under 5 seconds from the stored snapshot.
- **cost:** About $0.005–$0.03 per save and a few cents per question depending on snapshot size; browser extraction and model context dominate.
- **security:** Snapshots may contain private account data. Require an explicit owner gesture/phrase to save, encrypt at rest, apply TTL and per-item delete, exclude passwords/payment fields, and show URL, capture time, and redaction status whenever it is used. Never silently retain an entire tab.
- **missing:** A browser-extension command for explicit ‘save this page’ selection and bounded semantic extraction; Encrypted, owner-visible reference storage with TTL/delete and a citation-aware query endpoint; Relay routing that can answer from a saved snapshot without reopening the authenticated account

### "“Before I send this, tell me exactly what personal information it reveals and give me a safer version.”"
- **useful because:** The system would inspect a draft in Mail, Safari, or another Mac app, identify sensitive entities and unintended recipients, explain each disclosure in plain language through the pendant, and prepare a minimally redacted alternative while preserving the owner’s intent. It would catch accidental account numbers, private names, home details, and internal links before they leave the device—something a relay-only assistant cannot see and a browser-only assistant cannot assess across Mac apps.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a local/cheap model for entity detection and redaction suggestions; use realtime only to answer the owner’s short question or read the risk summary.
- **latency:** Produce a first risk report in under 4 seconds and a redacted draft within 10 seconds; never block the owner from sending, but make the diff available before they choose.
- **cost:** About $0.002–$0.02 per draft, dominated by model inspection of text; local extraction and diffing are negligible.
- **security:** The original draft must remain on the Mac whenever possible. Send only hashes or redacted spans to the relay, never passwords or full private content. Treat the safer version as a draft, preserve the original unchanged, and record exactly which spans were altered.
- **missing:** A Mac-side read/write draft adapter spanning Mail and browser text without screen scraping; A disclosure classifier with configurable private-entity classes and recipient/domain rules; A side-by-side diff surface and pendant intent for ‘explain leak’ versus ‘make safer’

### "“Keep track of every promise I make and remind me before I break one.”"
- **useful because:** Across sent Mail, calendar commitments, and authenticated work pages, the hive would extract explicit and implied commitments (‘I’ll send this Friday’, ‘we’ll review next week’), ask a brief clarification only when the due date or owner is ambiguous, and maintain a private commitments ledger. The pendant would surface only commitments approaching risk; the Mac would provide the original evidence and let the owner mark them done, renegotiated, or rejected.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a background model for periodic extraction and duplicate resolution; use realtime for brief clarification and urgent spoken reminders.
- **latency:** Capture a newly detected commitment within a few minutes of a source sync; urgent reminders should reach the pendant within 30 seconds of crossing the configured risk window.
- **cost:** Roughly $0.01–$0.05 per daily extraction batch, with cost dominated by reading and reconciling source text; incremental reminders are cheap.
- **security:** This is sensitive behavioral profiling. Keep evidence snippets local/encrypted, let the owner set source allowlists and retention, never infer a commitment solely from an ambiguous sentence, and make every reminder link back to the exact source and confidence.
- **missing:** A durable commitments data model with evidence spans, due-date uncertainty, status history, and recurrence; Incremental Mail/browser source cursors and a scheduler that can evaluate risk without rereading everything; A dashboard workflow for correction and a pendant notification policy that avoids nagging

### "“Make a private ‘send later’ queue that works even when my Mac is asleep, then deliver each item when I’m back.”"
- **useful because:** The owner could dictate a message, file, or browser action from the pendant while away from the Mac; the relay would store an encrypted intent and payload, then the Mac would fetch it when it reconnects, validate that the target and source context still match, and prepare the action without silently sending or submitting. This is different from a long-running Mac job: it is an offline-first personal outbox that survives disconnection and resolves stale context instead of blindly replaying it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles capture and concise confirmation; a cheaper background model normalizes the intent and detects stale or contradictory context when the Mac reconnects.
- **latency:** Acknowledge and durably queue in under 2 seconds offline; reconcile within 15 seconds after Mac reconnection; present a stale-context warning before any external mutation.
- **cost:** About $0.005–$0.03 per queued item, mostly transcription and intent normalization; storage and local preparation are negligible.
- **security:** Queued content can contain secrets and could become dangerous if replayed against a changed account. Encrypt payloads, bind each item to destination/account and expiry, delete after completion or owner cancellation, and default to preparing rather than sending. The dashboard must show queue contents and exact replay conditions.
- **missing:** An offline-capable relay outbox with encrypted payloads, expiry, destination binding, and reconnect delivery; A Mac/browser reconciler that checks stale tabs, changed recipients, and changed files before preparing actions; Pendant commands for queue/list/cancel and a dashboard showing pending, blocked, and completed items


## Changes it proposed to its own stack

### `browser-harness` — Add a first-class ‘owner-marked page capsule’ path separate from polling watches: the Safari extension sends only the selected tab’s title, URL, visible text regions, and a redaction manifest; the Mac stores an encrypted, expiring capsule and returns a stable citation id. Relay questions can retrieve only that capsule, not browse the account afresh.
- **owner gets:** They can save a complicated private webpage once and ask the pendant about it later—even after closing Safari—without repeatedly exposing their logged-in session or losing the source they meant to remember.
- effort: Medium: extension selection/serialization, local encryption and TTL, relay retrieval authorization, and a small dashboard list/delete view.  ·  risk: A bad extractor could retain secrets or omit the important section. Default to visible-text allowlists, redact credential/payment patterns, show a preview before saving, and make deletion immediate; if extraction fails, save nothing.
- cost: Low recurring API cost; one small background summarization call per capsule and storage proportional to selected text. No hardware cost.  ·  latency: Save takes roughly 1–10 seconds depending on page size; later answers are faster than reopening the site.
- security: Improves security over live re-access but creates a new sensitive store; encryption, short TTL, per-capsule authorization, and audit receipts are mandatory.
- depends on: A working browser-extension extraction/selection command; An encrypted capsule store and relay route; Owner-granted browser session authorization


## What it asked for

_Nothing._
## Its own summary

Round 149 produced four owner-facing proposals. The strongest new cross-node capability is an explicit “remember this page” capsule: Safari/browser-extension extracts a bounded, redacted snapshot of an authenticated page, the Mac encrypts it with TTL and citations, and the relay/pendant can answer from it later without reopening the private account. I also proposed meeting-now preparation (Calendar + Mail + open tabs -> cited local packet + spoken top items), typed one-sentence thought routing, and a source-grounded evidence/options packet. A browser-harness change specifies the capsule path separately from polling watches. Live discovery: the Mac bridge and Safari extension are online; Safari reports three tabs, currently showing a failed example.com page; relay is reachable. Accessibility and Screen Recording remain unavailable, and the newly granted mac_read_sources/mac_readonly_inspect/mac_run_actions tools still return “schema but no implementation,” so I could not inspect apps/tabs or read Calendar/Mail through those tools this round. I do not need another permission request this round; what is still needed is implementation of the capsule storage/retrieval path and real implementations for the granted read tools, plus owner approval at the moment a private page is explicitly saved.

**Biggest unknown:** Whether the browser extension already has an unlisted selected-tab extraction command or local encrypted storage that could make the page-capsule capability immediately runnable; the route inventory and tool schemas do not expose that detail.

