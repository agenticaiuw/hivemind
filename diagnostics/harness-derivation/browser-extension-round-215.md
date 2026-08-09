# Harness derivation — browser-extension — round 215

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with 2 tabs; current addressed tab is YouTube video https://www.youtube.com/watch?v=Xc4klGbq8v8, and POST /execute with browser_read_page successfully returned live page text plus evidence capsule and receipt.
  - evidence: GET /browser/status at 2026-08-08T23:51:48Z; POST /execute browser_read_page at 2026-08-08T23:52:09Z returned tabId 3186198, title, content, provenance, and receipt.

## Capabilities it proposed

### "“Pendant, tell me what I’m looking at in Safari, and if it’s long, give me the three decisions or actions it implies.”"
- **useful because:** This is the clearest unique browser value: the owner can keep a logged-in page on screen and ask hands-free for a grounded explanation. The browser reads the addressed tab, the model summarizes only the live page with URL/title provenance, and the pendant speaks a short answer without making the owner copy/paste or expose the page to a public web reader.
- **path:** pendant → browser → relay-realtime → mac-planner
- **model tier:** Realtime for the short spoken summary; use a cheaper background model only when the page exceeds a configurable length and needs section-level compression.
- **latency:** 2–5 seconds for ordinary pages; up to 15 seconds for a long authenticated document, with an immediate spoken “reading this page” acknowledgment.
- **cost:** About $0.003–$0.02 per request depending on page length; browser extraction and provenance dominate latency, model tokens dominate cost.
- **security:** The browser session is the source of truth and the page text must not be persisted. Read-only browser actions should be used by default; store only the existing short-lived, host-keyed claims/evidence capsules (24-hour TTL, 200-character value cap). The response should say which tab/title it used and refuse to silently use another tab. No submit/click is needed.
- **missing:** A reliable current-tab/read-page command path exposed to the planner without ambiguous tool resolution (POST /execute already works as a practical fallback); A pendant intent that binds “this page” to the Safari addressed tab and a compact spoken-response route; A page-length chunking/summarization policy that preserves URL/title/evidence provenance

### "“Keep an eye on this logged-in page and alert me only if a material change happens—price, deadline, status, or a new required action.”"
- **useful because:** The owner currently has to remember to revisit volatile authenticated pages. A browser session can periodically reread the exact page while the relay is awake, compare normalized claims rather than noisy DOM diffs, and send only meaningful deltas to the pendant’s offline alert inbox. This is a true browser–relay–pendant capability: it survives the Mac being unattended and does not require the owner to keep the tab visible.
- **path:** browser → relay-realtime → pendant → mac-planner
- **model tier:** Background/scheduled inexpensive model for normalization and change classification; realtime only when the owner asks what changed. Deterministic field extraction should run before any model call.
- **latency:** Checks can run on a 15-minute to daily schedule; alert delivery should be under 30 seconds after a detected change. No conversational latency is required for polling.
- **cost:** Roughly $0.01–$0.10 per watched page per day depending on cadence and page size; browser/relay execution dominates operational complexity, while semantic diff calls dominate API cost.
- **security:** The watcher must use the existing authenticated Safari session and never navigate away or submit. Persist only compact extracted claims and hashes, not HTML, screenshots, or page text. The owner must explicitly name the page and fields (or choose a conservative “status/deadline/amount/action” extractor); an empty per-origin configuration remains valid. Alerts should include URL, observed time, old/new short claims, and expire through the existing offline inbox behavior.
- **missing:** A durable browser watch job that pins a tab/session and schedules rereads; A field-aware semantic diff with debounce, login-expiry detection, and “material vs cosmetic” classification; A relay-to-offline-alert-inbox delivery adapter and owner controls to pause/delete a watch

### "“Take the key claims from this private page and attach them to my active project, with the source link and a short note about why each matters.”"
- **useful because:** Authenticated pages contain the owner’s most valuable research, but today their useful content disappears when the tab closes. This turns a spoken request into durable, inspectable project evidence: browser extracts selected claims, the Mac project/context graph stores only short claims plus provenance, and the pendant reads back exactly what was saved. It is not a generic page summary—the deliverable is reusable, source-linked project knowledge.
- **path:** pendant → browser → mac-planner → relay-realtime
- **model tier:** Background/standard model for claim extraction and deduplication; realtime only for the owner’s spoken confirmation and read-back. No expensive model is needed for URL/title/hash bookkeeping.
- **latency:** 5–12 seconds for a normal page; long pages may return a first claim set in 5 seconds and continue extraction in the background.
- **cost:** About $0.01–$0.08 per page, mostly proportional to extracted text; graph writes and browser reads are otherwise low cost.
- **security:** Saving is an explicit owner request, but the system must show a preview before writing and support undo. Never save raw HTML, screenshots, credentials, or full page text; cap each claim and retain URL, title, timestamp, content hash, and evidence capsule. Browser facts should remain short-lived unless the owner explicitly promotes selected claims into the active project. Redact secrets before graph insertion.
- **missing:** A browser extraction action that accepts a bounded claim schema and returns selectors/evidence rather than an unbounded page dump; A promotion endpoint from browser findings/evidence into an active project/context-graph entity with undo and provenance links; A spoken preview/confirmation flow that can select, reject, or edit individual claims

### "“Read this private page to me section by section. I’ll say ‘next’, ‘back’, or ‘stop’, and when I say ‘that one’, tell me which link or control I’m pointing at without clicking it.”"
- **useful because:** This gives the owner hands-free access to authenticated web content rather than a one-shot summary. The browser exposes a structured reading stream—headings, table rows, form labels, links, and controls—while the pendant supplies low-latency next/back/stop commands. It makes dense private portals usable while walking, driving, or when the screen is difficult to operate, without granting the system permission to click or submit.
- **path:** pendant → browser → relay-realtime → mac-planner
- **model tier:** Realtime only for interpreting short navigation utterances and selecting the next bounded segment; deterministic DOM landmark extraction should do most of the work. A cheaper background model can produce accessible labels for poorly marked-up pages.
- **latency:** Under 700 ms for next/back/stop and under 3 seconds to prepare the first section. A long page should stream in bounded chunks rather than wait for whole-page summarization.
- **cost:** Approximately $0.002–$0.02 per reading session; browser extraction and speech generation dominate, with model usage limited to ambiguous labels or commands.
- **security:** Read-only by construction: the browser action allow-set must exclude click, type, select, and submit. Never persist page text or audio. The current tab, URL, section identifier, and evidence capsule should be retained only for the active session. If the page contains secrets, the pendant should support an immediate stop and discard buffer.
- **missing:** A browser accessibility-tree/landmark extraction action that returns bounded sections and stable element identifiers; A pendant playback protocol carrying section IDs and next/back/stop events; A realtime session coordinator that keeps browser position, speech position, and tab identity synchronized

### "“Read the useful parts of this private page aloud, but automatically skip account numbers, addresses, passwords, and one-time codes; tell me when you skipped something.”"
- **useful because:** The owner can use authenticated browsing around other people without accidentally broadcasting sensitive page content. This is different from merely refusing to store data: it is a live spoken-output firewall that preserves task-relevant meaning while suppressing secrets before audio leaves the Mac. The owner hears an explicit omission marker instead of unknowingly receiving an incomplete answer.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** Deterministic local redaction and DOM-label classification first; a small background model can classify ambiguous sensitive fields. Realtime is used only to turn the already-redacted result into speech.
- **latency:** Add less than 500 ms for ordinary page segments; never delay an emergency stop or leak unclassified text while waiting for a model.
- **cost:** Under $0.005 per page segment in normal use; local pattern matching is nearly free, with model cost limited to uncertain classifications.
- **security:** The unredacted page must remain on the Mac/browser boundary and must never enter relay prompts, logs, memory, audio buffers, or evidence capsules. Redaction should fail closed for uncertain numeric strings and credential-like controls, provide an omission count, and preserve a local audit that contains only categories and positions—not the secret values. The owner can explicitly ask to reveal a category in a future session, but the default must remain suppressive.
- **missing:** A pre-speech redaction gate that runs after browser extraction and before relay/audio transport; A DOM-aware sensitive-field classifier covering visible text, labels, tables, and video captions; A spoken omission marker and test harness proving that suppressed values do not reach logs or memory

### "“While this private meeting or webinar is playing in Safari, quietly track the conversation and tell me through the pendant only when my name, a decision, a deadline, or an action item appears. At the end, give me the unresolved items.”"
- **useful because:** This turns an authenticated browser session into a personal attention filter. The owner does not need to keep watching a long meeting or webinar: the browser captures available captions/transcript fragments, the Mac detects personally relevant events, and the pendant delivers short interruptible alerts. It is especially valuable when the owner is multitasking, and unlike a generic recording it produces actionable, time-linked moments.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** A cheaper streaming/background model should classify caption fragments and maintain a compact event state; realtime is reserved for an immediate spoken alert or an owner query such as “what did I miss?”
- **latency:** Detect and queue an event within 3–8 seconds of its caption appearing; deliver only high-confidence events immediately, with a configurable digest for lower-confidence items.
- **cost:** Approximately $0.03–$0.30 per hour of captions depending on transcript rate and model tier; browser caption extraction and streaming context are the dominant costs.
- **security:** This must be opt-in per tab/session and visibly indicate that monitoring is active. Do not retain the transcript or audio; retain only short event claims with timestamp, page URL, and evidence hash, using the existing short-lived browser-fact policy. Never send alerts to anyone else or act on an action item automatically. Provide a hardware stop gesture that immediately ends capture and clears the in-flight buffer.
- **missing:** A browser caption/transcript stream action with timestamps and bounded chunks; A streaming event classifier with deduplication, confidence thresholds, and end-of-session unresolved-item synthesis; A relay-to-pendant interrupt channel that coexists with normal playback and honors the existing stop/barge-in behavior


## What it asked for

_Nothing._
