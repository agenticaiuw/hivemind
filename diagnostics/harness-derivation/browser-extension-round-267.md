# Harness derivation — browser-extension — round 267

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-2026-08-09** — Safari on MacIntel is online with one active YouTube tab. POST /execute with an actions array successfully performed browser_read_page and returned substantial page text, including the current video title and recommendations. Direct granted browser wrappers still only describe actions rather than invoke them; probe_http POST /execute is the working dispatch path.
  - evidence: GET device discovery reported Safari on MacIntel · 1 tab(s) · online; POST /execute returned HTTP 200 and browser_read_page content for a YouTube page.

## Capabilities it proposed

### "“Read the page I’m looking at, give me the useful part in one minute, and let me ask follow-up questions from the pendant.”"
- **useful because:** This is the highest-value browser-only capability: the owner can consume an authenticated article, dashboard, or video without leaving the page or touching the keyboard. The browser holds the login, the relay does the reasoning, and the pendant is the private hands-free interface.
- **path:** browser → relay → pendant
- **model tier:** Use a cheap background/page extraction model for the first pass; use realtime only for the pendant's short follow-up exchange. Escalate to vision only when browser text is incomplete (canvas/video controls).
- **latency:** Initial extraction 2–5 seconds; spoken one-minute brief under 8 seconds; follow-up under 1.5 seconds after each question.
- **cost:** Usually one low-cost extraction call plus 1–3 realtime turns; roughly $0.01–$0.08 per page depending on transcript length. The dominant cost is resending page context, so retain only a compact temporary task capsule.
- **security:** The browser may expose authenticated material. Send only the extracted task-relevant text to the relay, never HTML/screenshots by default; do not persist page text. Store only short claims with host/URL provenance and the existing 24-hour browser TTL. An explicit empty per-origin configuration should remain the default until the owner fills it in.
- **missing:** A first-class browser_context_action that atomically reads the active tab and returns a bounded task capsule (the current POST /execute browser_read_page path works, but is awkward for the voice planner).; A temporary conversation/page-context ID shared by browser, relay, and pendant, with automatic expiry and no raw-page persistence.; A spoken follow-up route that can target that context without resending the whole page.

### "“If I ask about the page while my Mac is asleep or Safari is disconnected, remember the question and answer it when the browser comes back—tell me on the pendant, not by making me ask again.”"
- **useful because:** The worn device is always with the owner while the browser is not. This makes browser access resilient instead of silently failing: a spoken question becomes a durable, bounded job, and the answer arrives through the already-accepted offline alert inbox when the Mac and Safari reconnect.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Use a cheap background worker for queue reconciliation and page extraction; use realtime only to capture the short spoken question and render the final alert. No model call while waiting offline.
- **latency:** Capture and acknowledge locally in under 500 ms; execute within 10 seconds of Safari reconnecting; alert is playable immediately after delivery.
- **cost:** Near-zero while offline; roughly $0.01–$0.05 per resumed page question, mostly extraction and summarization. Persist only the question and URL/tab identity, not page content.
- **security:** A queued query could outlive the owner's intent or expose a later page state. Bind it to origin plus a short expiry, cancel on tab navigation/origin change, and label the answer with its capture and execution times. Use existing browser-fact TTL/provenance rules and the pendant's local alert queue; never speak a result that is marked stale without saying so.
- **missing:** A reconnect-triggered browser job queue that can target a tab identity and invalidate itself on origin change.; A pendant offline intent record (question, captured tab fingerprint, expiry) and a cancel gesture.; A relay event joining browser completion to offline_alert_inbox with stale/error status.

### "“Download the document I’m viewing, rename it sensibly, and put it in my AI-Pendant-Workspace; tell me what you saved.”"
- **useful because:** A logged-in browser can reach documents that shell and public web tools cannot, while the Mac can safely rename and organize the resulting file. The owner gets a complete browser-to-files workflow from the pendant instead of manually downloading, finding, and sorting each document.
- **path:** pendant → browser → mac-bridge → relay
- **model tier:** Use a background planner to identify the document and destination, browser actions to download, and a cheap local Mac action to verify/rename/move it. Use realtime only for the concise spoken completion or an ambiguity question.
- **latency:** Start within 2 seconds; complete in 5–20 seconds depending on download size; speak the resulting path and file size immediately.
- **cost:** Typically $0.005–$0.03, with cost dominated by file metadata and ambiguity handling rather than model inference. No document bytes need leave the Mac.
- **security:** Downloads may contain sensitive personal or work material. Keep bytes local, report the exact origin URL and destination, preserve the original filename in provenance, reject overwrite by default, and quarantine unexpected file types. This is reversible (move to a trash/recovery folder), but never silently upload or share the file.
- **missing:** A browser download receipt exposing the final local path, origin URL, and checksum.; A Mac file handoff action that can atomically rename/move a newly downloaded file and produce an undo receipt.; A cross-surface job ID linking the browser provenance record, local file receipt, and pendant response.

### "“Make the page I’m on into a voice menu: tell me the sections and let me say ‘open the second result’, ‘go back’, or ‘show the prices’ while Safari follows along.”"
- **useful because:** A summary is not enough for dense authenticated dashboards, portals, and long documents. This would let the owner operate a logged-in web application hands-free, with the browser doing navigation and the pendant providing a concise semantic interface.
- **path:** pendant → relay → browser → mac-bridge
- **model tier:** Use a cheaper structured page-semantics model to build and update the menu; use realtime only for the short voice command and confirmation loop. Use vision as a fallback for canvas-only controls.
- **latency:** Initial menu under 4 seconds; ordinary navigation response under 1.5 seconds; refresh semantics after a page transition under 3 seconds.
- **cost:** Approximately $0.01–$0.06 per page transition, dominated by rebuilding semantics for dynamic pages. Keep only a compact accessibility graph in an expiring task context.
- **security:** The voice menu must not imply that a control was activated when it was merely identified. Bind every spoken target to a current DOM/accessibility snapshot and invalidate it after navigation. Keep page text ephemeral and retain only provenance for explicitly requested findings.
- **missing:** A browser accessibility-tree/semantic-control response with stable refs across one page state.; A stateful browser voice-session protocol that maps spoken references to current controls and reports navigation outcomes.; Pendant speech support for disambiguation choices larger than a single yes/no response.

### "“Collect the pages and downloaded documents that prove this issue, make a local evidence packet with dates and citations, and show me what it contains before I send anything.”"
- **useful because:** When a billing, delivery, warranty, or account dispute spans several authenticated pages, the owner currently has to manually gather URLs, PDFs, dates, and amounts. This would turn browser access plus local Mac storage into a coherent, reviewable packet without sending it anywhere.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Use a background extraction model for claims and chronology, and local deterministic tooling for PDF/file assembly. Use realtime only to explain the packet and answer ‘why is this included?’
- **latency:** Gather a small case in 15–45 seconds; update incrementally as each source is read; provide a spoken inventory within 3 seconds of completion.
- **cost:** Roughly $0.03–$0.20 per case, mainly proportional to the number of pages and document OCR. Keep raw files and generated packet on the Mac; send only a compact claim index to the relay.
- **security:** Evidence can contain account numbers and private correspondence. Preserve original files locally, redact only copies, record source URL and retrieval time, and make outbound sharing a separate explicit action. The packet must be inspectable and deletable, with no page body stored in browser memory facts.
- **missing:** A local evidence-bundle primitive that copies files/pages into a case directory and writes a manifest with hashes and provenance.; A browser capture mode that can save a user-selected authenticated page as a local artifact without sending it to the relay.; A review surface that lets the pendant enumerate claims, omissions, and redactions before any share/send operation.

### "“Watch me do this browser task once, turn it into a reusable routine for this site, and next time show me the steps you intend before running it.”"
- **useful because:** Authenticated sites often have repetitive workflows that public automation cannot reach. A supervised demonstration would let the owner teach the system once, then invoke the task from the pendant without hardcoding the site or guessing the owner's habits.
- **path:** browser → pendant → relay → mac-bridge
- **model tier:** Use a background planner to abstract the demonstrated actions into semantic steps; use a cheaper validator to test selectors and detect site changes. Use realtime only for invocation, ambiguity, and the spoken step preview.
- **latency:** Record with no perceptible delay; produce a draft routine within 10 seconds after the demonstration; validate and preview in under 5 seconds on later runs.
- **cost:** About $0.02–$0.12 to compile or repair a routine, then pennies per invocation. The expensive part is occasional re-planning after a site redesign, not ordinary execution.
- **security:** Do not record passwords, one-time codes, page text, or keystrokes marked secret. Store semantic steps with origin, selector evidence, and an expiry/version, not a video or full transcript. A routine must stop and report when the origin, account, or target meaning changes; it must never silently generalize a destructive step.
- **missing:** A browser action recorder that emits a semantic event stream, including page origin and control identity but excluding secret values.; A versioned routine store with selector health, dry-run preview, and repair history.; A routine invocation event that the pendant can start and that returns per-step receipts.


## What it asked for

_Nothing._
