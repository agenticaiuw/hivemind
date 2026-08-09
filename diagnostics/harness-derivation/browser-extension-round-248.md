# Harness derivation — browser-extension — round 248

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari 26.5.2 is online with 2 tabs, unlike prior zero-tab state; the currently granted browser wrappers still fail resolution because list_tabs/snapshot/read_page are ambiguous against nearby actions.
  - evidence: discover devices returned Safari on MacIntel · Safari · 2 tab(s) · online; browser_enqueue_command(list_tabs) returned resolver ambiguity between action:browser_list_tabs and action:browser_list_sessions.

## Capabilities it proposed

### "When I press the pendant, answer a question about whatever authenticated Safari page I’m looking at—without making me copy or describe it."
- **useful because:** This is the browser surface’s defining advantage: the pendant supplies low-friction intent and speech, Safari supplies private logged-in context, and the relay returns a short answer. It makes inaccessible pages usable while walking, and stores only bounded claims with provenance rather than page text.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Realtime for the spoken question and concise answer; a cheaper background extractor only when the page is large. Browser text extraction should precede model use, with a task-specific slice.
- **latency:** Under 5 seconds for ordinary pages; stream a brief acknowledgement from the pendant while extraction runs.
- **cost:** Roughly $0.01–$0.05 per question, dominated by model tokens for extracted page text; browser and relay calls are negligible.
- **security:** The browser session is private and page content must not leave the local browser/relay except for the requested slice. Persist only the existing host-keyed, 24-hour, 200-character findings with URL provenance. The owner’s empty per-origin rules remain the configuration input. Never infer or read a different tab silently; show the tab title in the answer and let the owner cancel.
- **missing:** A non-ambiguous browser action for browser_read_page/browser_snapshot (the current resolver confuses them with nearby names); A button/event route tying a spoken pendant query to the active Safari tab; A compact active-tab identity and extraction result contract

### "Start this browser task, and if the connection drops or I walk away, save exactly where you got to so I can say ‘resume it’ later."
- **useful because:** Authenticated browser work is fragile today: a multi-step task can lose its session or stop between safe steps. A durable checkpoint lets the owner delegate research or reversible form preparation from the pendant, continue later, and see the next action instead of restarting.
- **path:** pendant → browser → relay → mac-planner → dashboard
- **model tier:** Use a cheaper background model to summarize completed steps and identify the next safe browser action; use realtime only for the owner’s resume/stop conversation.
- **latency:** A checkpoint should be written within 2 seconds of every browser result; resume should acknowledge state in under 3 seconds.
- **cost:** About $0.01–$0.04 per resumed task, mostly model summarization; storage and browser calls are negligible.
- **security:** Persist a structured checkpoint (origin, tab title, step IDs, extracted claims, and undoable filled-field identifiers), never screenshots or page bodies. Expire session credentials and page claims under existing browser TTLs. Stop before send/purchase/delete and expose the exact pending action to the pendant and dashboard.
- **missing:** A browser-job checkpoint schema that survives extension reconnects and records the last command receipt; A resume route that validates the tab/session still matches before continuing; Pendant commands for resume, pause, and abandon

### "Take the useful points from this private page and put a short, linked note in my Mac notes—keep the source and tell me what you saved."
- **useful because:** It turns a logged-in page into a durable, reviewable artifact without copying sensitive page bodies into system memory. The browser does the only available private read, the model compresses it, the Mac writes the note, and the pendant gives a spoken receipt with the source URL.
- **path:** browser → relay → mac-planner → pendant → dashboard
- **model tier:** A background/cheaper model performs claim extraction and a short summary; realtime is unnecessary except for the owner’s spoken request and completion receipt.
- **latency:** 15 seconds for a normal article or dashboard; report progress on the pendant if extraction takes longer.
- **cost:** About $0.01–$0.06 per page, dominated by extracted-text summarization; Mac Notes and browser calls add no meaningful API cost.
- **security:** Default to claims-only storage and existing 24-hour browser TTL; do not retain HTML, screenshot, or full text. Include the source URL and retrieval time in the note, and make the note creation undoable. Respect the owner’s still-empty per-origin and category rules rather than inventing sites or sensitive categories.
- **missing:** A first-class action that atomically extracts selected page claims and creates a Mac note; A provenance block format that survives into Notes without leaking page text; An explicit spoken receipt and undo handle for the created note

### "Tell me whether anything I committed to locally conflicts with a change on one of my private web accounts—for example, a reservation moved, a deadline changed, or an appointment was canceled—and give me the smallest next action."
- **useful because:** A browser page is valuable not merely because it can answer questions, but because it can reveal changes that contradict the owner's calendar, notes, or planned work. This would prevent missed appointments and stale commitments without requiring the owner to remember which site to check.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Use a background model for periodic comparison and ranking; use realtime only to explain the highest-priority discrepancy when the pendant alerts the owner.
- **latency:** A scheduled comparison can take up to 2 minutes; an alert should reach the pendant within 30 seconds of detection.
- **cost:** Approximately $0.03–$0.15 per monitored account comparison, dominated by authenticated page extraction and cross-source reasoning; run only on explicit owner-configured pages.
- **security:** Ship with no origins configured. Store only a short discrepancy claim, source URL, timestamps, and confidence under the existing browser TTL; never persist page bodies. Do not change calendars, reservations, or accounts automatically. The alert should say what changed and ask before any consequential action.
- **missing:** An explicit owner-configured set of pages and matching local sources; A normalized claim-diff format for browser findings versus calendar/notes; A scheduler and pendant alert payload for high-confidence discrepancies

### "Let me browse a logged-in Safari page hands-free from the pendant: read the current section, move to the next meaningful control, and open or expand it when I say ‘that one’."
- **useful because:** This gives the owner access to private web applications while away from the keyboard, not just a summary of a page. The browser can expose semantic headings and controls; the pendant provides short spoken navigation and audio feedback, making authenticated dashboards and long forms usable while moving around.
- **path:** pendant → browser → relay → mac-planner
- **model tier:** Realtime is appropriate for low-latency spoken navigation and confirmation; use a small local/cheap model to rank headings and controls before sending only a compact accessibility tree to realtime.
- **latency:** Each spoken navigation command should complete in under 2 seconds, with immediate audio acknowledgement if the page is slow.
- **cost:** Roughly $0.005–$0.03 per navigation command; cost is dominated by repeated accessibility-tree compression, not browser actions.
- **security:** Transmit a compact semantic tree rather than screenshots or full HTML. Scope each command to the current tab and page origin. Do not activate submit, purchase, delete, or send controls through an ambiguous phrase; describe them and require an explicit command. Respect the existing claims-only retention policy.
- **missing:** An extension action that returns an accessibility tree with stable control IDs and visible labels; A pendant-to-browser focus state that survives several voice turns; An audio rendering path for headings, selected control, and page-change feedback

### "After I complete something important in Safari, show me exactly what the site says happened, save a compact receipt, and let me ask later which page and fields produced it."
- **useful because:** Private web actions often have ambiguous success states. A durable, source-linked receipt would let the owner verify a booking, application, purchase, or cancellation without reopening the site, while preserving an auditable trail of what the browser actually observed rather than what the model assumed.
- **path:** browser → relay → mac-planner → pendant → dashboard
- **model tier:** Use a cheaper background extractor to turn the resulting confirmation page into structured fields; realtime is only needed when the owner asks for a spoken receipt or discrepancy explanation.
- **latency:** Capture the confirmation within 5 seconds of navigation; later receipt lookup should answer in under 3 seconds.
- **cost:** Approximately $0.01–$0.05 per completed action, mostly confirmation-page extraction; storage is small structured JSON.
- **security:** The receipt must redact secrets, payment credentials, authentication tokens, and unnecessary personal data. Retain only owner-selected fields, source URL, timestamp, and an evidence hash or short excerpt under explicit retention rules. Never treat a receipt as proof if the site displayed an error or ambiguous state; label uncertainty and preserve the raw page only transiently.
- **missing:** A post-action browser result hook that distinguishes confirmation, error, and ambiguous states; A redacted receipt schema with field-level provenance and configurable retention; A dashboard and pendant query path for receipt lookup and uncertainty disclosure


## What it asked for

_Nothing._
## Its own summary

Recorded three new browser capabilities: cross-source commitment discrepancy alerts, hands-free semantic navigation of authenticated pages, and provenance-backed post-action receipts. Each names the missing implementation changes without assuming current wiring is sufficient.

**Biggest unknown:** Whether any of these exact combinations already exist in the unseen backlog; the recorder accepted all three without a collision refusal.

