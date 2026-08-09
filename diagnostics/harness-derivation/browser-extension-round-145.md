# Harness derivation — browser-extension — round 145

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with 9 tabs; active tab is authenticated OpenAI Platform billing overview at https://platform.openai.com/settings/organization/billing/overview, tabId 1148327, and default browser session points to it. There are no pending commands or inspections.
  - evidence: GET /browser/status and GET /browser/sessions both returned HTTP 200 at round 145.

## Capabilities it proposed

### "“Watch my logged-in billing and account pages for unexpected changes, and tell me only when something materially changed.”"
- **useful because:** Only the browser can see authenticated account dashboards. A relay schedule plus browser snapshots can detect a changed invoice, plan, payment method, or security setting without reading private pages aloud continuously; the pendant can deliver a short alert even when the Mac link later drops.
- **path:** browser-extension → mac-planner → relay-realtime → unified
- **model tier:** Background/cheap model for scheduled diff classification; realtime only to answer follow-up questions from the owner.
- **latency:** Initial setup under 2 minutes; scheduled checks can take 10–30 seconds and do not need to block conversation. Alert delivery under 2 seconds once a diff is classified.
- **cost:** Low: one browser extraction and a small-model diff per watched page per interval; dominant cost is authenticated page extraction, not synthesis.
- **security:** Page contents leave Safari for processing and may include financial data. Ship empty per-origin rules and require the owner to explicitly choose origins, selectors/categories, retention, and speakability. Store only redacted field-level hashes and change summaries by default, never raw page text; show the source URL and timestamp in every alert.
- **missing:** A durable authenticated page-watch scheduler that invokes browser extraction; Field-level redaction/diffing for dynamic dashboards rather than whole-page text diffs; Relay delivery into the already-accepted offline_alert_inbox skill; Owner-configurable per-origin rules and retention controls

### "“Reconcile this order across the sites I’m already logged into, and tell me whether anything needs action.”"
- **useful because:** A single site cannot answer whether an order, shipment, return, or refund is actually resolved. The browser can inspect the retailer and carrier/ payment tabs behind existing logins, while the relay correlates order identifiers and dates, and the Mac creates a reminder only for an unresolved next step. This turns scattered authenticated tabs into one answer the owner cannot get from public search.
- **path:** browser-extension → relay-realtime → mac-planner → mac-vision → unified
- **model tier:** Cheap background extraction and deterministic identifier matching first; realtime model only explains conflicts or answers the owner's follow-up.
- **latency:** About 20–45 seconds for two to four logged-in tabs; speak a preliminary result as soon as two sources agree, then append conflicts.
- **cost:** Moderate: browser extraction dominates, with a small model call for normalization and conflict explanation. Far cheaper than sending full page text to the realtime tier.
- **security:** Cross-origin correlation is sensitive. Keep raw pages in Safari/local ephemeral memory, pass only selected fields and citations to the relay, redact account numbers, and default to no persistence. The owner must explicitly configure allowed origins and which categories may be spoken. Creating a reminder is reversible but should include the exact extracted due date and source URLs in its receipt.
- **missing:** A multi-origin correlation planner with per-origin extraction contracts; A browser command that can target several existing sessions without losing tab affinity; Structured redaction of order IDs, addresses, and payment data; A Mac reminder action fed by a cited, normalized result

### "“Fill out this logged-in web form from the notes on my Mac, read me the exact draft, and leave it ready for me to submit.”"
- **useful because:** This combines the browser's authenticated session with local files the browser cannot access. The Mac extracts only the requested fields from a note, the browser fills the form, and the pendant reads a concise field-by-field diff while Safari remains on the final review state. It removes tedious copying without sending a message or placing an order on the owner's behalf.
- **path:** mac-planner → browser-extension → relay-realtime → mac-vision → unified
- **model tier:** Cheap deterministic field mapping and local extraction; realtime model only resolves ambiguous labels or handles voice edits.
- **latency:** 10–30 seconds for a normal form; each voice correction should update the draft within 3 seconds. Never wait on an external submit response because submit is intentionally out of scope.
- **cost:** Low to moderate: browser DOM interaction and local note parsing dominate; use the realtime tier only for ambiguous natural-language corrections.
- **security:** Form contents may contain identity, health, or financial data. Keep source notes local, send only field/value pairs needed for this form, redact sensitive values in logs, and persist neither page text nor drafts after the tab closes unless explicitly saved. The browser must stop at the final review page, display the exact payload and target origin, and require an explicit owner action outside this capability to submit.
- **missing:** Reliable semantic form-field mapping across arbitrary authenticated sites; A typed draft state that can be diffed and edited without submitting; A durable cross-surface correlation ID linking the local note, browser tab, and spoken review; A clear final-review extraction that captures what the site would submit

### "“What am I looking at in Safari right now? Give me the important parts, and cite the exact page and section.”"
- **useful because:** The owner can ask hands-free about the page already in front of them, including pages behind logins that public search cannot reach. The extension supplies the active tab's rendered text and URL, the relay produces a short spoken answer, and the Mac stores only a citation if requested. This is the most immediate browser-specific capability and works with today's live 9-tab Safari.
- **path:** browser-extension → relay-realtime → mac-planner → unified
- **model tier:** Realtime for the immediate spoken answer; use a cheaper model for long-page chunking and citation extraction before handing a short result to realtime.
- **latency:** First spoken sentence within 3 seconds; full page extraction under 10 seconds. If the page is long, stream section summaries rather than blocking on one giant context.
- **cost:** Low for short pages; long pages cost more due to extraction and chunk summarization. The dominant control is sending only the relevant visible/selected section, not all tab text.
- **security:** The active page may contain highly sensitive authenticated content. Never persist raw text by default; pass the origin/title and short-lived extracted sections only, redact secrets and account identifiers, and let the owner configure per-origin may-speak/never-store rules. Say when the answer is based on the current tab and include a clickable source URL.
- **missing:** A reliable active-tab browser_read_page command exposed through the voice planner; Visible-page/selection extraction and section anchors for citations; Per-origin speaking and retention policy configuration, initially empty; A context budgeter that prefers selected/visible text over the entire DOM

### "“Read the important items in this logged-in web inbox one at a time, let me skip or bookmark each by button, and keep my place for later.”"
- **useful because:** Today the owner must look at a private web inbox or ask for a full-page reading. This would turn an authenticated, visually dense queue into an eyes-free, interruptible workflow: Safari supplies structured items, the relay ranks them, and the pendant provides next/skip/bookmark controls without deleting, archiving, or sending anything. The owner can process a queue while walking and resume at the exact item later.
- **path:** browser-extension → relay-realtime → mac-planner → unified
- **model tier:** Background model extracts and ranks item metadata; realtime is used only for the current spoken item and a short follow-up.
- **latency:** First item in under 5 seconds; next/skip response under 1 second from cached items. Bookmark state should survive a dropped Mac or relay connection where possible.
- **cost:** Moderate initial extraction cost per inbox page; low incremental cost after structured item metadata is cached. Realtime usage is limited to one item at a time.
- **security:** Inbox contents are extremely sensitive. Send only the current item and minimal metadata, never bulk raw page text; default to ephemeral retention, redact addresses and tokens, and require explicit per-origin rules for speaking, bookmarking, and persistence. Bookmarking must create a local/private reference, never mark the web item read or mutate the site.
- **missing:** A browser semantic extractor for repeated inbox/list items with stable item IDs and links; A relay-side queue and cursor protocol supporting next, skip, replay, and bookmark; A pendant interaction mapping that does not conflict with existing playback interruption and moment-bookmark behavior; An ephemeral, origin-scoped bookmark store that can reopen the exact item later

### "“Explain the chart or PDF inside this logged-in page, including the numbers and trend, without uploading the document anywhere.”"
- **useful because:** Many authenticated pages expose invoices, lab results, dashboards, and reports as canvas graphics or embedded PDFs that ordinary page extraction cannot read. Safari can capture the rendered region, the Mac can perform local OCR/table/chart parsing, and the relay can turn the resulting measurements into a spoken explanation. The owner gets access to information currently trapped behind a visual renderer while the raw document stays on the Mac.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → unified
- **model tier:** Local OCR and deterministic table extraction first; use a vision-capable background model locally or on the Mac for chart interpretation, with realtime reserved for the spoken answer.
- **latency:** 10–30 seconds for a page or report; return extracted figures progressively, with the owner able to ask about one chart rather than waiting for the whole document.
- **cost:** Moderate CPU work on the Mac and occasional vision-model cost. Keeping the raw image local avoids repeated cloud token costs and reduces transmission size.
- **security:** The source may contain health, financial, or employment data. Capture only the selected region, process the image locally, retain structured numbers only when requested, and make cloud vision opt-in per origin. Never put the raw screenshot or PDF into general conversation history by default.
- **missing:** Browser region selection and screenshot/PDF-frame capture with page coordinates; Mac-local OCR, table extraction, and chart-reading capability exposed as structured data; A citation model that maps spoken figures back to page/region coordinates; Per-origin policy for local-only versus cloud vision processing

### "“If I leave a logged-in web form with unsaved work, save a private recovery copy and restore it when I come back.”"
- **useful because:** Browser sessions today can act on a page but cannot protect the owner's in-progress work when a tab crashes, signs out, or is accidentally closed. The extension can detect dirty fields, the Mac can encrypt a local recovery snapshot, and the pendant can warn briefly before loss. Restoration can refill the same form after the owner reopens it, without ever submitting or sending the draft.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → unified
- **model tier:** No expensive model for capture/restore: deterministic DOM field serialization and local encryption. Use a small model only to remap fields when a site layout has changed.
- **latency:** Snapshot within 1 second of a dirty-field change, with no noticeable typing lag; restore in under 5 seconds after the page is ready.
- **cost:** Low API cost; storage and local DOM serialization dominate. Occasional layout-remapping inference is the only model expense.
- **security:** Drafts may contain passwords, health information, payment details, or messages. Default to origin-scoped local encryption, exclude password fields and file uploads, allow the owner to disable origins/categories, expire snapshots automatically, and never send raw drafts to the relay. Restoration must show a field-count and origin summary before filling.
- **missing:** A browser dirty-state observer and field serializer that excludes secrets; Encrypted local draft storage with expiry and origin/tab binding; A restoration matcher resilient to changed form layouts; A pendant warning event that distinguishes recoverable unsaved work from ordinary alerts


## What it asked for

_Nothing._
