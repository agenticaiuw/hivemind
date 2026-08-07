# Harness derivation — mac-planner — round 83

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-readonly-inspection** — The newly granted mac_readonly_inspect schema is present to this agent but every operation currently returns an implementation error. /observe remains usable and reports foreground Claude, 16 running apps, browser sessions, and TCC state. Therefore the grant changed the contract, not runtime capability.
  - evidence: Five parallel mac_readonly_inspect calls (running_apps, foreground_app, accessibility_enabled, browser_tabs, list_directory) each returned: 'This tool was granted a schema but has no implementation yet. Report what you would have done with it.'; GET /observe returned HTTP 200 with those fields.

## Capabilities it proposed

### "“If the pendant, Mac agent, or browser bridge stops working, figure out what failed, collect the smallest useful evidence, and leave me one plain-language recovery card; tell me only when it needs me.”"
- **useful because:** Today a failure is fragmented: /ops/status already shows browser offline, Accessibility false, five pending browser commands, and the relay alive, while the pendant can capture ideas and the Mac has jobs/receipts. This capability turns those facts into one actionable incident instead of silent retries or a misleading success receipt. It is genuinely cross-node: the pendant supplies the symptom, relay correlates telemetry, Mac supplies observation/job evidence, and the browser bridge contributes queue/session state.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Use a cheap background classifier/rule engine for health correlation and deduplication; use the realtime tier only to speak a concise alert when the owner asks or when a high-confidence owner-visible outage crosses its quiet-hours policy.
- **latency:** Capture and correlation under 2 seconds after a heartbeat/error event; background evidence bundle under 30 seconds. No browser or Mac action should be retried automatically unless explicitly marked idempotent.
- **cost:** About $0.001–$0.01 per incident if rules and a small background model summarize only anomalous events; storage/egress and log retention dominate, not inference.
- **security:** Evidence can contain URLs, mail/calendar snippets, file paths, and UART data. Redact secrets and page bodies by default, retain hashes plus short excerpts, encrypt relay storage, and require explicit confirmation before any remediation that deletes data, sends mail, submits a form, or changes system settings. Never upload screenshots unless separately consented.
- **missing:** A durable incident schema with correlation IDs spanning pendant event, relay pipeline, Mac job, and browser command; A deduplicating health monitor with quiet hours and severity thresholds; A dashboard recovery card showing timeline, evidence provenance, and safe suggested next steps; An actually implemented read-only Mac inspection tool (the granted mac_readonly_inspect currently returns 'no implementation yet'); Browser extension heartbeat restoration; current /browser/status is offline with five pending commands; Owner-side Accessibility TCC fix if UI-level remediation is ever suggested; /observe reports the running binary is not trusted

### "“When I press the pendant button at the start and end of a meeting, keep a private meeting packet: identify the agenda and attendees from my calendar and open work tabs, capture only the notes I explicitly mark, then leave me decisions, action items with owners and dates, and unsent follow-up drafts.”"
- **useful because:** The owner can get calendar briefs and prepare meetings, but cannot today carry a private, evidence-linked thread from meeting start through follow-up. This would join the pendant’s deliberate physical markers, Mac Calendar/Mail context, authenticated browser context, and relay memory without leaving a microphone continuously open or sending anything on the owner’s behalf.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime tier only for short button-triggered note acknowledgements and low-latency spoken status. Use a cheaper background model after the end marker to organize notes, resolve dates and owners, and draft follow-ups.
- **latency:** Start packet acknowledgement under 1 second. Each explicit note should be persisted within 2 seconds. End-of-meeting synthesis within 60 seconds; no need for continuous transcription latency.
- **cost:** Roughly $0.02–$0.15 per meeting depending on note volume and browser/calendar context; background summarization dominates. Audio cost is near zero if the owner supplies text or short marked clips rather than continuous recording.
- **security:** Meeting content, attendee identities, calendar details, and logged-in page context are sensitive. Default to explicit button-marked notes only; show provenance for every decision/action; retain raw snippets briefly and delete them after synthesis; never send drafts or alter browser forms without a separate owner command. Require a local indication that capture is active.
- **missing:** A pendant start/end meeting marker and explicit note-capture event protocol; A relay meeting-packet object with encrypted short retention, append-only note events, and idempotent close; Calendar attendee/agenda normalization and browser-tab context adapters; An evidence-linked action-item extractor that distinguishes quoted commitments from suggestions; A dashboard review page for editing drafts and approving individual follow-ups; A durable audio/text clip path that honors the owner’s no-continuous-microphone default


## What it asked for

_Nothing._
