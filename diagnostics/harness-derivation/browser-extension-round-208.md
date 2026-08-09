# Harness derivation — browser-extension — round 208

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Watch this authenticated page for a meaningful change, and alert me on the pendant only when the change affects me; include the before/after claim and a link, but never speak or store the surrounding page."
- **useful because:** This creates an always-on browser sentinel: the relay can wake Safari to inspect a page behind an existing login, while the pendant delivers a useful interrupt even when the owner is not at the Mac. It filters cosmetic churn and turns changes in bills, reservations, applications, or work dashboards into actionable alerts without retaining page bodies.
- **path:** browser → relay-realtime → pendant → mac-planner → dashboard
- **model tier:** A cheap scheduled/background model computes structured diffs and impact ranking; realtime is used only when the owner asks for the alert explanation.
- **latency:** Polling cadence configurable from 15 minutes to daily; alert generation within one cadence plus 10 seconds. No persistent browser tab should block the owner’s Safari.
- **cost:** Approximately $0.01–$0.10 per watched page per day depending on cadence and extraction size; browser wakeups dominate.
- **security:** The owner explicitly starts each watch on a concrete origin and chooses retention/speech categories; configuration ships empty rather than assuming sites. Store only bounded changed claims with URL/provenance under the existing 24-hour browser TTL; do not store HTML, screenshots, or unchanged snapshots. Alert payloads must be encrypted/expired and deduplicated.
- **missing:** A durable page-watch schedule bound to a Safari session and origin; Semantic DOM extraction and change classification that ignores timestamps, ads, and layout churn; Integration from page-watch findings to offline_alert_inbox with expiry and unread state; Owner-facing controls to pause, delete, or inspect the watch and its last evidence

### "Compare the open tabs I name, including my logged-in tabs, and tell me where they disagree; cite each tab and separate facts from guesses without changing any tab."
- **useful because:** Search engines cannot see the owner’s private Discord, YouTube, or account pages together. A cross-tab comparison can resolve conflicting appointment details, claims, or instructions while preserving the distinction between public evidence and private context. The owner gets a concise spoken verdict rather than manually copying text between tabs.
- **path:** pendant → browser → relay-realtime → mac-planner → dashboard
- **model tier:** A background model extracts bounded claims from each selected tab and clusters contradictions; realtime only speaks the final comparison or answers a follow-up.
- **latency:** Under 12 seconds for three ordinary tabs; up to 30 seconds for five long tabs, with progress events and cancellation.
- **cost:** About $0.05–$0.30 per comparison, primarily extraction and reasoning tokens; no cost for the tab-selection metadata.
- **security:** Require explicit tab IDs or a spoken selection such as “the Discord and Google tabs”; never sweep all tabs implicitly. Keep source URLs and short claims only, with the existing browser TTL and provenance, and do not quote private text into durable memory. Any follow-on click is a separate action.
- **missing:** A multi-tab browser extraction action that accepts an explicit tab list and returns bounded evidence capsules; Claim normalization with source-specific timestamps and contradiction confidence; A spoken citation format that identifies tabs without reading sensitive page text aloud; An ephemeral comparison workspace with automatic expiry

### "On the page I’m viewing, find the section about [topic], scroll it into view, and read just that section to me; keep my place so I can say “next” or “go back.”"
- **useful because:** Long authenticated pages are difficult to use hands-free even when they can already be read. Anchored navigation lets the owner inspect a portal, policy, or document while walking, with the browser showing the exact source and the pendant speaking only the requested section. A maintained section cursor makes follow-up commands meaningful instead of rereading the whole page.
- **path:** pendant → browser → relay-realtime → mac-planner
- **model tier:** A cheap extraction model identifies headings, anchors, and section boundaries; realtime handles the short spoken navigation loop and cancellation.
- **latency:** Find-and-scroll under 5 seconds, first audio under 3 seconds after anchor resolution, next/back under 2 seconds.
- **cost:** Approximately $0.01–$0.06 per section request; DOM extraction is the main cost and can be cached only in memory for the active session.
- **security:** Read-only browser action set: no clicks, typing, navigation, or submissions. Keep the cursor tied to tab ID and page revision; clear it on navigation or timeout. Do not persist section text or screenshots; apply existing browser claim TTL/provenance only if the owner explicitly asks to remember a fact.
- **missing:** DOM heading/section boundary extraction robust to client-rendered pages; A browser scroll/highlight action that returns the exact locator and page revision; Session-scoped cursor state shared between relay speech and the extension; A spoken next/back/cancel intent parser

### "When I say “get my latest statement,” find the newest statement in the authenticated site I name, download it, save it into the correct Mac folder with a clear filename, and tell me the period and amount from the document."
- **useful because:** Today the browser can inspect a private site and the Mac can manipulate files, but neither can complete this end to end. This would turn a recurring hunt through logged-in portals into one spoken request, while leaving the original document on the owner’s Mac rather than copying it into the cloud.
- **path:** pendant → relay-realtime → browser → mac-planner → mac-terminal
- **model tier:** Use a background/local planner for portal navigation, file naming, and PDF extraction; use realtime only for the spoken request and concise result.
- **latency:** 30–90 seconds, with progress updates after locating and downloading the document.
- **cost:** Approximately $0.05–$0.30 per statement, dominated by authenticated page extraction and document parsing; Mac file operations are negligible.
- **security:** The owner names the origin and destination folder explicitly. Never upload the document to the relay or persist its contents as browser memory; transfer it directly from Safari to the Mac filesystem where possible. Keep an undoable receipt containing only path, source URL, period, and checksum.
- **missing:** A browser download event that yields a local file handle instead of page text; A secure browser-to-Mac local transfer channel; Document classification and period/amount extraction performed locally; An idempotent file-placement action with duplicate detection and undo

### "Read the deadlines and commitments on this authenticated page, turn only the dates that require something from me into Mac reminders with links back to the exact page, and tell me which reminders you created."
- **useful because:** Private portals often contain deadlines that ordinary calendar or mail briefing cannot see. This joins browser-only context to the Mac’s durable reminder system, preventing missed renewals, application windows, and payment dates without storing the underlying page.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** A cheaper background model extracts candidate dates and classifies whether they are actionable; the owner’s realtime conversation resolves ambiguous dates and confirms the final reminder list.
- **latency:** 10–20 seconds for one page; ask about ambiguity rather than silently creating a wrong date.
- **cost:** Roughly $0.02–$0.12 per page, mostly date extraction and classification; reminder creation is negligible.
- **security:** Create reminders only from explicit owner-directed pages. Store the reminder text, due date, source URL, and a short claim—not page text. Preserve an undoable mapping so all generated reminders can be removed as one batch. Apply the owner’s not-spoken/not-persisted category rules before speaking details.
- **missing:** Date/obligation extraction that understands page-local timezone and recurrence; A cross-surface provenance link from each reminder to its browser evidence capsule; Batch undo for reminders generated by one browser task; A durable local reminder-link format that remains useful if the authenticated session expires

### "Keep this authenticated browser task alive across the day: if the site logs me out or asks for a human-only step, tell me on the pendant exactly what is blocked and leave the page ready for me, then resume automatically when I finish."
- **useful because:** Long-running private workflows fail today when a session expires or a CAPTCHA/2FA interrupts them. This would let the relay and browser extension act as a durable assistant without handling passwords or pretending to be the owner: the owner performs the human-only step, and the system resumes the already-authorized task afterward.
- **path:** browser → relay-realtime → pendant → mac-planner → dashboard
- **model tier:** A background workflow runner handles polling and checkpoint recovery; realtime is used only for the interruption notice and the owner’s “continue” command.
- **latency:** Detect session failure within one polling interval, notify within 5 seconds, and resume within 10 seconds after the owner signals completion.
- **cost:** Approximately $0.01–$0.05 per active workflow hour plus occasional browser extraction; most cost is extension wakeups, not model inference.
- **security:** Never capture or relay passwords, OTPs, CAPTCHA contents, or security answers. Checkpoint only non-sensitive workflow state: origin, tab ID, action step, and a redacted locator. Expire checkpoints automatically, invalidate them on origin change, and provide a visible pause/abort control.
- **missing:** A resumable browser workflow state machine with checkpoint and recovery semantics; Extension events for logout, authentication prompts, CAPTCHA, and tab navigation changes; A secure owner-presence handoff from pendant to the existing Safari tab; Workflow leases and expiry that survive relay restarts without retaining page content


## Changes it proposed to its own stack

### `browser-harness` — Add a Safari extension “send selection to pendant” command: capture the user-highlighted text plus page title, URL, tab ID, and a short-lived page revision; push it to the relay as an ephemeral context capsule, then let the owner ask a follow-up by voice. The extension must expose explicit selection-only mode separately from whole-page reads and clear the capsule after the interaction.
- **owner gets:** The owner can highlight one confusing paragraph, press the pendant button, and ask “what does this mean?” without copying or exposing the rest of a private page. It makes precise help possible on pages that are too sensitive or too large to read wholesale.
- effort: Medium: Safari extension content-script selection capture, relay context binding, pendant request correlation, and a small UI/voice intent path.  ·  risk: Selection may include secrets or accidental adjacent text; show the captured character count/title before sending when possible, cap size, expire quickly, and provide cancel. If relay delivery fails, the selection stays local and is discarded.
- cost: Low recurring API cost because context is bounded; roughly 1–3 engineering weeks, no hardware cost.  ·  latency: Selection upload under 1 second; answer latency follows ordinary realtime summarization, typically 2–6 seconds.
- security: Improves least-privilege relative to whole-page capture, but introduces a deliberate data-export action. No HTML/screenshot persistence; URL and bounded selection use existing provenance/TTL rules.
- depends on: A resolved browser action or extension event for selection capture; A session-scoped ephemeral context capsule in relay-realtime; An owner-visible per-origin configuration that can disable selection export


## What it asked for

_Nothing._
