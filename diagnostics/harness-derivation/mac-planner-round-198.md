# Harness derivation — mac-planner — round 198

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-mac-and-browser-state** — Mac bridge and Safari browser bridge are online; AI Pendant Agent has Accessibility and Screen Recording, browser has 9 tabs, and no pending browser commands. The pendant LTE registration remains absent, so USB is the live path for hardware testing.
  - evidence: GET /observe, GET /browser/status, GET /ops/status at 2026-08-08T02:49Z

## Capabilities it proposed

### "“After my workday, find commitments I made across today’s meetings, mail, and browser work, and prepare one private checklist with the source beside every item.”"
- **useful because:** People lose commitments across channels even when each channel is individually searchable. This creates a provenance-preserving checklist: each suggested item links to the calendar event, mail thread, or browser page that supports it, marks uncertainty, and never sends messages or changes tasks automatically. The owner gets one evening review instead of reconstructing the day.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** A cheaper background model extracts candidate commitments and ranks confidence; realtime is only used if the owner asks follow-up questions. Deterministic rules handle deduplication and source links.
- **latency:** Run asynchronously after the configured workday boundary; target 1–3 minutes for a normal day and show incremental results.
- **cost:** About $0.03–$0.15 per day, dominated by model input size; local source extraction and deduplication are cheap.
- **security:** Only bounded Calendar/Mail reads and explicitly selected browser sessions are included. Mail bodies should default to redacted snippets; sensitive threads and domains can be excluded. The system must show evidence and confidence, and require an explicit owner action before creating reminders or sending anything.
- **missing:** A cross-source commitment extraction and provenance data model (distinct from a generic briefing).; A browser read API that can enumerate opted-in session pages and return bounded text with source IDs.; A review UI that supports accept/edit/dismiss per candidate and preserves the evidence link.; A scheduler trigger at the owner's workday boundary.

### "“Test the pendant and audio bridge now, tell me which link or codec stage is unhealthy, and give me a receipt I can attach to a bug report.”"
- **useful because:** The hardware is physically attached to this Mac today, but the owner has no one-command commissioning test. This would run the existing bidirectional diagnostic fixture over USB, correlate pendant counters with relay pipeline telemetry, and produce a plain-language verdict such as radio/link, capture, Opus encode, downlink decode, or speaker path—without recording private speech.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Deterministic checks and thresholds should do the diagnosis; use a cheap model only to turn the structured receipt into a concise explanation. Realtime is unnecessary.
- **latency:** 90 seconds maximum for a full fixture; show stage-by-stage progress after each test vector.
- **cost:** Negligible API cost; one optional summary call under $0.01. Main cost is engineering the USB command/receipt protocol.
- **security:** The fixture must synthesize audio only and must never open the microphone for owner content. Receipts should contain counters, firmware/build IDs, and timings—not PCM. Running a test should stop any active call and require an explicit user command.
- **missing:** The requested mac_serial_exchange capability, or an equivalent allowlisted serial transport for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA.; A framed USB command protocol that arms and collects audio_path_diagnostic_fixture results from both chips.; Relay-side receipt correlation between the USB test and /pipeline telemetry.; A dashboard report template with acceptance thresholds and downloadable JSON.

### "“Every weekday, check my already-authenticated work portal and tell me only what is new, urgent, or blocked—without opening or submitting anything.”"
- **useful because:** The owner explicitly wants attention triage, not a generic web summary. The browser extension is online with authenticated tabs, while the relay can schedule the check and the Mac can speak a short result through the pendant. A source-linked delta prevents repeatedly reporting the same tickets or exposing bulk portal content.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → dashboard
- **model tier:** Use a background model for bounded extraction and priority ranking; use realtime only to answer a follow-up. Deterministic hashes and watch state suppress duplicates.
- **latency:** Run at the configured weekday times; target 30 seconds to enqueue and 2 minutes for a portal with several sections. Never block the owner's browser.
- **cost:** Approximately $0.01–$0.08 per check, depending on extracted portal text; browser inspection and change hashing dominate neither API nor latency.
- **security:** Read-only inspection of explicitly named authenticated sessions; never submit forms, click destructive controls, or copy secrets. Store hashes and short redacted excerpts rather than full portal pages. Require an owner-selected allowlist of portal origins and retention period.
- **missing:** A browser watch mode for authenticated, multi-section portals with stable selectors and per-section change hashes.; A scheduler that can run browser watches while the Mac agent is asleep, with a durable relay result.; A priority policy configured by the owner (urgent states, due-date horizon, assignee); no invented policy defaults.; A pendant delivery route that summarizes only the ranked deltas.

### "“Before each calendar event, assemble the exact preparation packet I need from the relevant mail, local files, and browser tabs, explain why each item was selected, and read me the three most important points through the pendant.”"
- **useful because:** Today the sources are separately searchable, but the owner still has to decide which documents and tabs belong to a particular event. Event-linked retrieval would turn a calendar transition into useful preparation rather than a generic morning brief. It should preserve a reason and source for every included item so the owner can correct the association.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** A background model performs document/tab clustering and ranking; deterministic calendar matching, deduplication, and source citations do the rest. Realtime is only needed for spoken follow-up questions.
- **latency:** Begin 10 minutes before an event and produce an initial packet within 60 seconds; update incrementally if a relevant tab or mail arrives.
- **cost:** Roughly $0.02–$0.12 per event, dominated by extracting and ranking text; local metadata matching is inexpensive.
- **security:** Only the event's explicitly selected account and allowed folders/browser origins are searched. Exclude sensitive mail, passwords, and private tabs by policy. Show source citations and retention controls; never send or modify source documents.
- **missing:** An event-scoped retrieval and association model that links Calendar attendees, subjects, projects, files, and browser sessions.; A bounded local-file content index with per-folder consent and redaction.; A browser extraction API that returns page text and stable source identifiers for opted-in tabs.; A pendant delivery queue that can replace or defer a packet when the owner is already in a call.

### "“When I switch from one project to another, preserve a private handoff of where I stopped, what was unresolved, and the exact files and browser pages to reopen when I return.”"
- **useful because:** Project switching currently destroys working context in the owner's head. This capability would create a lightweight, user-visible handoff at the moment of switching, then restore only the relevant working set later. It is not a generic backup: it records unresolved questions and the causal trail of the last work session, while leaving all files and browser data in place.
- **path:** mac-planner → browser-extension → relay-realtime → dashboard → pendant
- **model tier:** Use deterministic app/tab/file collection and a cheap background model to summarize unresolved work. Realtime is unnecessary except when the owner asks to reopen a handoff by voice.
- **latency:** Capture within 3 seconds of a project switch; restore a selected handoff within 10 seconds, with a preview before opening anything.
- **cost:** Under $0.02 per handoff; most work is local metadata collection, with a small summarization call.
- **security:** The owner must explicitly map folders, apps, and browser sessions to projects. Do not capture page bodies, passwords, or private windows by default. Handoffs expire and can be deleted; reopening files or URLs must be explicit rather than automatic background activity.
- **missing:** A project-switch detector spanning foreground applications, active browser session, and the existing project graph.; A compact handoff record containing unresolved questions, source IDs, and reopenable actions.; A restore planner that previews and then coordinates Mac opens with browser-session selection.; A pendant marker or voice command that can name a project when automatic classification is uncertain.


## Changes it proposed to its own stack

### `interaction` — Add a cross-surface “quiet continuity” mode: when the owner begins a live pendant conversation, the relay snapshots the current Mac/browser work context and temporarily treats that context as the conversation's working set. If the owner says “that page,” “this file,” or “the thing I was doing,” the Mac and browser nodes resolve the reference against the snapshot rather than guessing from whatever is foreground later. End the mode on explicit stop or after a short idle timeout, and expose the captured context for deletion.
- **owner gets:** The owner can speak naturally while moving between the pendant, Mac, and browser without repeating URLs, filenames, or project names. It makes the hive feel like one assistant instead of independent tools that lose the referent as soon as focus changes.
- effort: Medium-high: define a time-bounded context lease, collect stable references from Mac/browser, and teach relay planning to resolve pronouns against it.  ·  risk: A stale or sensitive page could be mistaken for the intended reference. Mitigate with visible context indicators, expiry, source citations, and a spoken clarification when multiple candidates match. Recover by deleting the lease and starting a fresh one.
- cost: Low storage cost; approximately $0.01–$0.05 per conversation for context extraction and occasional disambiguation.  ·  latency: Initial context capture under 2 seconds; reference resolution adds under 1 second when deterministic, with model fallback only for ambiguity.
- security: Potentially sensitive context crosses Mac/browser/relay. Default to metadata and short redacted excerpts, encrypt the lease, do not retain it after expiry, and honor per-app/domain exclusions.
- depends on: A relay context-lease schema and expiry semantics; Stable browser and Mac source identifiers; Owner-configured redaction and retention policy; A clarification path over the pendant when references are ambiguous


## What it asked for

_Nothing._
