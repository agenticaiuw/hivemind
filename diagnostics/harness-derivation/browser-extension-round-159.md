# Harness derivation — browser-extension — round 159

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — Safari extension is online with 9 tabs, including authenticated Gmail and X; POST /execute browser_list_tabs and browser_read_page both completed successfully. browser_read_page ignored the supplied Gmail tabId and returned the active X tab, so tab affinity is currently unreliable for direct reads.
  - evidence: POST /execute browser_list_tabs at 2026-08-08T02:05:12Z returned 9 tabs; POST /execute browser_read_page with tabId 901464 returned tabId 1163292, URL https://x.com/home.

## Capabilities it proposed

### "When I press the pendant button, tell me what the authenticated page I'm looking at means and what, if anything, needs my attention."
- **useful because:** This turns the browser's unique access to logged-in pages into an always-available wearable action: no screen hunting or copying sensitive content into chat. The Mac extension reads the active tab, relay summarizes only the actionable parts, and the pendant speaks one short sentence. It is useful for mail, dashboards, tickets, and account pages without baking in a site list.
- **path:** pendant → browser → mac-bridge → relay-realtime
- **model tier:** background for page extraction and compact summarization; realtime only for the spoken follow-up
- **latency:** Under 5 seconds after the button press; extraction dominates, then a small summary call.
- **cost:** About $0.002–$0.01 per invocation depending on page length; browser extraction and redaction dominate latency, not tokens.
- **security:** Page text leaves Safari only long enough to reach the local relay/model and must be ephemeral by default. Per-origin rules should ship empty and be explicitly configured for read/extract/redact/never-store; never speak or persist categories the owner marks private. No navigation or mutation is performed.
- **missing:** A pendant button event routed to a browser-read job; An active-tab read action that preserves tab affinity (the current execute path can list/read but navigate payload validation is brittle); Ephemeral page capsule handoff from browser to spoken relay with owner-configurable redaction

### "Before I submit anything in Safari, read back exactly what will happen, who it goes to, and the important fields—without blocking me."
- **useful because:** Authenticated browser actions are where accidental high-impact mistakes happen, yet the owner explicitly wants maximum access rather than confirmation gates. A wearable preflight gives a final spoken checksum while preserving autonomy: it summarizes the rendered form or composed message, then leaves the submit click entirely to the owner.
- **path:** browser → mac-bridge → pendant → relay-realtime
- **model tier:** background extraction plus a deterministic field diff; realtime only to speak the compact checksum on demand
- **latency:** 2–4 seconds after a button press or before the click is offered; DOM extraction and redaction are the main cost.
- **cost:** Roughly $0.001–$0.005 per preflight; most pages can use local structured extraction and avoid a model call.
- **security:** Never transmit passwords, payment fields, tokens, or unredacted message bodies unless the owner’s per-origin policy allows it. Keep a hash and field names, not page content, in receipts. This is an advisory observability step, not a blocking policy or approval gate.
- **missing:** A browser DOM/form extraction action that returns field labels and values with sensitive-input classification; A pendant pre-submit event or a browser-side submit-intent signal; A local redaction/classification contract shared by browserSessions and the spoken relay

### "Save the useful part of this logged-in page to my workspace, with a citation and a one-line reason why it matters."
- **useful because:** A browser page is often valuable only while its session is open. This lets the owner turn an authenticated ticket, research result, or account detail into a local note without manually selecting, copying, and switching apps. The pendant supplies the trigger, Safari supplies exact context, the model writes a concise note, and the Mac saves it to ~/AI-Pendant-Workspace.
- **path:** pendant → browser → mac-bridge → mac-planner → relay-realtime
- **model tier:** background model for quote selection and note drafting; realtime only if the owner asks a follow-up
- **latency:** 5–10 seconds; browser extraction and local file write dominate.
- **cost:** About $0.002–$0.01 per capture, mostly proportional to extracted page text; local Markdown persistence is negligible.
- **security:** Default to a user-selected passage or bounded viewport rather than the whole page. Redact credentials, financial identifiers, and hidden form values; do not store page HTML or session cookies. The note should include origin, title, timestamp, and a content hash so stale facts are visible. Creation is allowed by remembered owner policy; never auto-submit or send anything.
- **missing:** A browser select/clip action that returns the selected DOM text plus URL and title; A pendant event carrying the clip request and optional short voice label; A Mac note writer that atomically creates a cited Markdown artifact and returns its path; A retention/redaction policy for authenticated page captures

### "Gather the relevant information across my open logged-in tabs about this task, reconcile contradictions, and tell me the next action—without saving the pages."
- **useful because:** Today the browser can expose one page at a time, but the owner has to manually correlate an email, a calendar page, a support ticket, and a document. A temporary cross-tab task capsule would use Safari's session access to join those private sources, identify conflicts (dates, amounts, status), and give the pendant one actionable sentence. This is more than summarizing the active page and deliberately leaves no durable copy.
- **path:** pendant → browser → mac-bridge → relay-realtime → mac-planner
- **model tier:** background model for bounded multi-tab extraction, deduplication, and contradiction detection; realtime only for the final spoken answer
- **latency:** 8–15 seconds for up to six explicitly selected tabs; extraction and page-size limits dominate.
- **cost:** Approximately $0.01–$0.04 per task capsule, depending on the number and size of pages; most cost is context tokens.
- **security:** The owner must explicitly select the tabs or origins for each capsule; never sweep every open tab by default. Apply per-origin read/extract/redact/never-store rules, strip cookies and hidden fields, retain only an in-memory short-lived capsule, and expose source titles/URLs in the spoken answer so the owner can detect a wrong join. No clicks or submissions.
- **missing:** A browser action to read several explicit tabIds while preserving tab affinity; A bounded, ephemeral multi-document context object with source provenance and contradiction markers; A pendant trigger that can carry a task label or selected-tab set; Cross-origin redaction and retention enforcement at the capsule boundary

### "Check this link in my existing browser session, even if it requires my login, and tell me whether it is legitimate and what it contains; do not leave a new tab open."
- **useful because:** Public web search cannot reach pages behind the owner's active sessions, and today a voice request cannot safely inspect a one-off authenticated URL without manual Safari work. This capability would open a temporary tab using the already-authenticated Safari context, extract the page and origin, run a provenance-aware legitimacy check, speak the result, and close the tab—useful for ticket links, shared documents, invoices, and account notices.
- **path:** pendant → relay-realtime → browser → mac-bridge
- **model tier:** background model for page extraction and source/redirect analysis; realtime for the short spoken verdict
- **latency:** 5–10 seconds including redirects and login; do not wait indefinitely on MFA or CAPTCHA.
- **cost:** About $0.003–$0.02 per link, dominated by extracted page context.
- **security:** Never auto-submit login, MFA, payment, or consent forms. Show the final URL and redirect chain in the spoken result; reject non-HTTPS or unexpected-origin redirects unless the owner explicitly allows them. Do not persist page text, credentials, or the temporary tab's history. Require explicit owner invocation because opening a URL is an external side effect.
- **missing:** A browser_open_temporary_tab/read/close transaction with guaranteed cleanup; A voice/pendant command payload that carries a URL and returns a result asynchronously; Redirect, origin, login-interstitial, and CAPTCHA detection in the browser harness; A short-lived provenance capsule that the relay can summarize without storing page contents


## Changes it proposed to its own stack

### `browser-harness` — Make every browser_read_page/browser_snapshot/browser_click resolve an explicit tabId first, reject silently falling back to the active tab, and return the requested tab's URL/title in the result. Add an integration test with Gmail and X tabs open; fix browser_navigate URL normalization to accept ordinary https URLs.
- **owner gets:** The assistant must never summarize or click the wrong logged-in tab. Today a requested Gmail read returned the active X page, and a normal https navigation was rejected. Fixing this makes browser automation trustworthy rather than merely more polished.
- effort: Small-to-medium: browserBridge/session routing plus extension command payload and end-to-end tests.  ·  risk: Existing callers that relied on implicit active-tab behavior may fail; recover with an explicit active-tab sentinel and a clear error. No page data needs to leave the Mac beyond the requested result.
- cost: Negligible runtime/API cost; one extra tab-routing field and test suite work.  ·  latency: No meaningful latency change; explicit routing may remove retries.
- security: Strongly improves isolation between authenticated origins and prevents accidental cross-tab disclosure or mutation.
- depends on: browserSessions.js tab/session affinity changes; A browser action schema that preserves tabId through POST /execute; Safari extension support for explicit tab targeting


## What it asked for

_Nothing._
## Its own summary

Produced three distinct browser capabilities: (1) a pendant-triggered spoken summary of the active authenticated page, (2) a non-blocking pre-submit spoken checksum for forms/messages, and (3) cited capture of a selected authenticated page passage into the Mac workspace. Also verified Safari is live with 9 tabs and found a serious tab-affinity defect: requesting Gmail by tabId returned the active X tab. I recorded and sent that evidence to mac-planner and proposed an explicit-target fix. The system still needs reliable tab-target propagation, URL normalization, DOM/form extraction with redaction, and a pendant-to-browser trigger path. I do not need another browser tool grant this round: direct POST /execute is working.

**Biggest unknown:** Whether the current browser action schema can be extended to preserve tabId and selected DOM ranges without changing the Safari extension; this determines how quickly the three capabilities can move from proposal to implementation.

