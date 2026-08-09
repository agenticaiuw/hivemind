# Harness derivation — browser-extension — round 169

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-read** — Safari extension is currently online with 9 tabs; POST /execute browser_read_page with tabId 1163292 successfully extracted the authenticated X home timeline and returned an evidence capsule. browser_navigate via /execute rejected a plain url field as invalid, so navigation payload shape remains unresolved.
  - evidence: POST /execute body {actions:[{type:'browser_read_page',tabId:1163292}]} returned 200 success, title Home / X, content, capsuleId evd_cf7f24874861; a browser_navigate action with {url:'https://www.google.com'} returned Failed: navigation command did not contain a valid URL.

## Capabilities it proposed

### "“What’s on the active Safari tab? Give me the one-minute version, and tell me what I should do next.”"
- **useful because:** This is the browser node’s unique value made tactile: the owner can ask while walking, and the system reads the page behind existing login rather than requiring copy/paste or exposing page text to a public search service. It can summarize Gmail, a dashboard, or a document and return only a spoken answer.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime for the short spoken summary; use a cheaper background model only if the page is long and needs chunking.
- **latency:** 2–5 seconds for normal pages; up to 15 seconds for a long authenticated document, with a brief “reading” acknowledgement on the pendant.
- **cost:** ~$0.01–$0.05 per invocation, dominated by sending extracted page text to the model; local tab discovery and extraction are negligible.
- **security:** Page text leaves Safari for relay summarization, potentially including private mail or financial data. Ship with an explicit per-origin policy/configuration (initially empty), redaction before model submission, no raw page persistence, and a spoken warning for origins not yet configured. No confirmation is needed for reading; any suggested action must remain a draft until separately requested.
- **missing:** A stable active-tab/read-page orchestration endpoint that selects the current Safari tab and limits extraction size; Owner-supplied per-origin read/extract/redact/never-store configuration; A compact spoken-result route from relay to the pendant

### "“Scan my open authenticated tabs and interrupt me only if there is something time-critical or money-related I need to act on today.”"
- **useful because:** Instead of making the owner ask about each tab, the browser reads the already-open private sessions, extracts only actionable deltas, and routes a tiny prioritized alert to the always-worn device. This turns scattered logged-in dashboards and inboxes into an attention filter that works away from the Mac; it is materially different from summarizing whichever tab is active.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background/cheap model for classification and deduplication; realtime only to phrase an alert when one qualifies.
- **latency:** 20–60 seconds for a scan of up to 10 tabs; alert delivery under 2 seconds after classification. Scheduled scans should be opportunistic and not block voice.
- **cost:** ~$0.02–$0.10 per scan, dominated by page extraction and classification; origin-specific rules can reduce tokens substantially.
- **security:** This is high-sensitivity aggregation. Require an inspectable owner configuration per origin and category: read, extract, redact, never-store, and may-speak. Never persist raw pages or notify with secrets; include source origin/title and an evidence capsule hash only. Alerts should expire and be dismissible locally; do not auto-click or send anything.
- **missing:** A browser multi-tab scan primitive with per-tab extraction limits and change/dedup hashes; Owner-configured origin/category policy, shipped empty rather than guessed; A scheduler that can invoke scans while Safari remains online; Relay-to-pendant alert delivery using the accepted offline_alert_inbox behavior

### "“Fill this authenticated web form using the appointment details on my Mac, but stop and read me the exact fields before you submit.”"
- **useful because:** The browser can reach the private form, while the Mac can supply the owner’s local calendar/contact context and the pendant can provide a hands-free review checkpoint. This eliminates tedious transcription without silently submitting a booking, application, or message. The owner gets a concrete preview and can then explicitly ask for the final action.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime for field mapping and the spoken preview; use deterministic extraction first and a cheaper model for ambiguous field labels. No model should invent missing values.
- **latency:** 5–12 seconds to inspect the form and local appointment context; preview should arrive before any submit-capable action.
- **cost:** ~$0.01–$0.08 per form, dominated by multimodal/field-label interpretation if needed; local calendar lookup is cheap.
- **security:** Forms may contain identity, health, financial, or message data. Apply per-origin/category policy and redact model context where possible. Filling is reversible; submission, file upload, payment, or message send must be a separate explicit action after presenting an exact field/value diff. Never store the completed form or page text by default.
- **missing:** A form-schema extraction and field-mapping layer that can distinguish editable fields from submit/payment controls; A cross-surface context query for selected Mac calendar/contact data with provenance; A pendant-friendly field diff/preview and explicit final-submit command; Owner-supplied origin/category policy

### "“I had to walk away from that web task. When I’m back at my Mac, restore the exact place I left off and remind me what was still unfinished.”"
- **useful because:** Today an interrupted authenticated workflow is effectively lost among tabs, redirects, and partially filled pages. This capability would let the browser extension capture a privacy-preserving checkpoint of the owner’s position—origin, tab, page state, focused step, and unsent draft—not the raw private page—and later reunite it with the pendant’s spoken reminder and Mac’s restored workspace. It is continuity across the worn device, browser session, Mac, and relay rather than another page summary.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Use a cheap background model to name the workflow step and detect unfinished state; use realtime only when the owner asks for the spoken reminder or restoration.
- **latency:** Checkpoint under 3 seconds when the owner leaves or locks the Mac; restore under 8 seconds, with a short pendant acknowledgement.
- **cost:** About $0.01–$0.04 per checkpoint/restore, dominated by semantic step labeling; most state capture is local metadata and DOM field descriptors.
- **security:** Never persist raw page text, passwords, cookies, or completed sensitive field values. Store an encrypted checkpoint bound to the origin and browser profile, with redacted field labels and hashes for unsent drafts. Restoration must visibly show the target origin and reopen the prior tab without submitting, sending, purchasing, or uploading anything.
- **missing:** A browser lifecycle/checkpoint hook that captures focused element, scroll position, route, and unsent-form structure without secrets; An encrypted cross-device checkpoint store with expiry and owner-visible deletion; Mac workspace restoration that can reopen the recorded tab and any local supporting document; A pendant reminder/resume command that survives a dropped Mac link

### "“Check whether the details in this private confirmation match my calendar and the email receipt on my Mac. Tell me exactly what conflicts, if anything.”"
- **useful because:** Owners routinely have the same appointment, reservation, or purchase represented in a logged-in web page, local mail, and calendar, with silent discrepancies in dates, amounts, names, or locations. No single node can compare all three sources: the browser holds the private session, the Mac holds local records, and the pendant can deliver a concise discrepancy report while the owner is away.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap structured extraction and deterministic field comparison first; realtime only for the final spoken explanation. Escalate ambiguous entities to a slower model rather than guessing.
- **latency:** 10–20 seconds for one page plus up to three local records; speak only after all sources have been collected.
- **cost:** Approximately $0.02–$0.08 per reconciliation, mostly model extraction from semi-structured pages and messages.
- **security:** This joins browser, mail, calendar, and possibly financial data. Keep raw artifacts on their originating devices, send only normalized fields and provenance, redact secrets, and expire the comparison result. Never make a correction or contact a vendor automatically.
- **missing:** A cross-surface evidence join API with provenance and confidence per extracted field; Local Mac selectors for the relevant calendar/mail records without broad mailbox export; Browser extraction of confirmation fields from the current authenticated origin; A spoken discrepancy format that names sources without reading sensitive contents aloud

### "“On the page I’m looking at, find the section that answers my question, navigate there, and read just that section—not the whole page.”"
- **useful because:** Long private dashboards and help centers are difficult to use hands-free. The browser extension can search the rendered authenticated page, follow same-origin links or expand the relevant disclosure, and return a bounded excerpt to the pendant. The owner gets targeted navigation and can ask follow-ups without touching the Mac or leaking the entire page to the model.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime for intent resolution and a short answer; use local DOM text search first and a cheaper model only when section matching is ambiguous.
- **latency:** 2–6 seconds for a loaded page; under 12 seconds if one same-origin expansion or navigation is needed.
- **cost:** ~$0.005–$0.03 per question, with local extraction and matching dominating less than model calls.
- **security:** Limit traversal to the current origin and the specific requested section; do not crawl unrelated links or persist page text. Apply per-origin rules and redact secrets before synthesis. Navigation and expansion are reversible; never trigger submit, purchase, send, download, or account changes.
- **missing:** A bounded DOM search/section locator that can expand accordions and return the smallest relevant excerpt; A browser action for same-origin navigation with explicit traversal limits; A conversational state token tying follow-up questions to the current page section; Owner-configured origin read policies


## Changes it proposed to its own stack

### `browser-harness` — Make browser_navigate accept and normalize the same canonical URL payload used by the extension (including scheme validation), return the created tabId, and expose a single active-tab read operation that chains navigate/list/read without requiring callers to know extension command details. Add a live contract test against Safari for https URLs and authenticated redirects.
- **owner gets:** The owner can say “open my portal and read the urgent items” from a blank or stale browser state and it will actually work, rather than failing with an opaque “invalid URL” or forcing the voice agent to know tab IDs.
- effort: Small-to-medium: reconcile the action schema between /execute and browserBridge.js, add result propagation, and test against the live extension.  ·  risk: A malformed URL could open an unintended site; preserve explicit https/http validation and show the final URL before any follow-up action. If extension polling is offline, return a clear failure and leave existing tabs untouched.
- cost: Negligible API cost; one extra local round trip only when bootstrapping a tab.  ·  latency: Adds roughly 0.5–2 seconds to bootstrap navigation; active-tab reads remain one round trip.
- security: No new data access beyond existing Safari cookies. Do not log full URLs containing tokens or persist page content; retain origin and redacted URL only.
- depends on: POST /execute; browser_enqueue_command; Safari extension online heartbeat; A confirmed canonical navigation payload from the browser bridge


## What it asked for

_Nothing._
