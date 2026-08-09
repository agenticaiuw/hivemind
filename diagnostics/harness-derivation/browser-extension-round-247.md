# Harness derivation — browser-extension — round 247

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension live Safari** — Safari extension v1.2.0 is online with 2 tabs: an authenticated DoorDash order tab (tabId 6516355) and active YouTube video (tabId 7975357). POST /execute browser_list_tabs succeeds and pendingCommands=0.
  - evidence: GET /browser/status at 2026-08-09T02:00:31Z; POST /execute browser_list_tabs at 01:59:58Z

## Capabilities it proposed

### ""Watch this authenticated page I pin, and tell me on the pendant only when something materially changes—what changed, why it matters, and what I can do next.""
- **useful because:** This is the highest-value browser-only capability: it turns an existing logged-in Safari session into a quiet, evidence-backed sentinel for bills, orders, dashboards, applications, and other changing pages without inventing a site list. The owner gets an interruption only for a material delta, not a recurring dump of page text.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Background/cheap model for scheduled page extraction and change classification; realtime tier only to answer a follow-up spoken question. Browser remains the source of truth and the pendant is the notification surface.
- **latency:** Initial pin under 3 seconds; scheduled checks 30–120 seconds depending on origin; alert delivery under 5 seconds after a detected delta.
- **cost:** Roughly $0.001–$0.01 per check when extraction is selector/diff based; model cost dominates only when the DOM delta needs semantic ranking. Storage is short claims, not page bodies.
- **security:** Never guess origins or categories: ship an empty per-origin policy that the owner fills explicitly. Read-only checks use an allow set containing browser_read_page/browser_snapshot only. Persist only short host-keyed claims with URL/evidence, 24-hour TTL and 200-character cap; do not persist HTML, screenshots, or credentials. Alert payloads need category redaction before speech.
- **missing:** A first-class browser page-watch scheduler that stores a pinned locator/selector and last content hash; Material-delta classifier wired to browser provenance and offline_alert_inbox; Owner-editable empty per-origin read/extract/redact/never-store configuration in the dashboard

### ""I'm stuck at a login or verification page in Safari. Ask me on the pendant for the exact approval you need, let me approve or deny without reading the page aloud, then resume the browser task.""
- **useful because:** Authenticated work currently breaks at the precise boundary where a browser agent cannot safely infer identity, consent, or a one-time code. This makes the pendant a physical approval channel and lets the browser continue without exposing secrets to the model or storing them. It is useful for long-running tasks, but stops short of submitting purchases or messages unless separately requested.
- **path:** browser → mac-bridge → relay → pendant → iOS
- **model tier:** Realtime tier handles the short approval dialogue; cheap background logic detects login/verification states and resumes the preplanned browser action sequence. iOS is an optional peer that can surface a code without passing its contents through the model.
- **latency:** Detect block within 2 seconds; pendant prompt within 5 seconds; resume within 3 seconds after a button response.
- **cost:** Usually <$0.01 per interruption; no model call is needed for a simple approve/deny. Cost is dominated by a realtime turn only if the page presents an unfamiliar challenge.
- **security:** The model must receive only challenge type and origin, never passwords, cookies, OTP contents, or full page text. The pendant response is a signed nonce-bound approve/deny with expiry and task hash. Do not auto-submit irreversible forms; show the proposed final action and stop. Owner policy remains maximum access, so this is an observability/secret-isolation protocol rather than a permission gate.
- **missing:** Browser challenge-state detector for login, CAPTCHA, passkey, and 2FA interstitials; Nonce-bound relay event from pendant and a resumable browser action plan; Optional iOS handoff that returns only verification-state success, never the secret itself

### ""While I'm watching this video or reading this page in Safari, answer 'what did they just say?' from the current position, give me a two-sentence explanation on the pendant, and optionally save a timestamped note on my Mac.""
- **useful because:** The browser is the only node that can see the owner's authenticated, current tab and its live position. A timestamp-aware question-answer loop is more useful than a generic page summary: it preserves attention, answers in context, and produces a durable note only when asked. It also works for private courses, internal videos, and logged-in documents that public search cannot reach.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Cheap model extracts/collapses the nearby transcript or DOM text; realtime tier speaks the short answer and handles a follow-up. Use the expensive tier only when the local excerpt is ambiguous.
- **latency:** Capture current tab and nearby text in under 1 second; answer in 2–4 seconds; note creation under 3 seconds after explicit request.
- **cost:** About $0.002–$0.03 per question; transcript extraction and model summarization dominate. Notes are small and local.
- **security:** Read only the active tab or an owner-selected tab, not all tabs. Send a bounded excerpt plus URL/title, never cookies or the whole page. Authenticated content should not be persisted by default; a note is an explicit owner action and should include only the chosen summary and timestamp. Keep page evidence ephemeral and redact secrets before speech.
- **missing:** A browser action that returns current media time/selection plus a bounded surrounding excerpt; Transcript/DOM adapters for video captions and paginated documents; A pendant query event carrying tab evidence and a Mac note action tied to the source timestamp

### ""Compare what I’m seeing across these private web pages with public information, resolve contradictions, and tell me the answer with a source trail—without saving the private pages.""
- **useful because:** Today the browser can read one page and the public-search tier can search the web, but neither can perform a trustworthy cross-source comparison across the owner's authenticated tabs. This would answer high-stakes practical questions such as comparing a private quote against public terms, reconciling an account notice with a policy document, or checking whether two logged-in dashboards disagree. The owner receives a concise spoken conclusion and can inspect exactly which claim came from which page.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Background model performs extraction, entity alignment, contradiction detection, and citation assembly; realtime model only speaks the final short answer or handles follow-up questions. Use a stronger model selectively for unresolved contradictions rather than every page.
- **latency:** Capture 2–5 selected tabs in under 5 seconds; first comparison in 10–20 seconds; follow-up under 3 seconds from the stored ephemeral evidence capsule.
- **cost:** Approximately $0.02–$0.15 per comparison, dominated by model context for multiple excerpts. Public search and browser extraction are otherwise inexpensive. Private page text should be held only in an encrypted, short-lived working buffer.
- **security:** The owner explicitly chooses tabs or origins; never crawl every open tab. Private excerpts are memory-only working data and are deleted after the job, while durable records contain only short claims, source URLs, hashes, and confidence. Keep private claims out of unrelated prompts and out of pendant speech unless the owner asked for them. Contradictions must be reported, not silently resolved; no financial, medical, or contractual action is taken automatically.
- **missing:** A multi-tab browser extraction operation with owner-selected tab IDs and bounded excerpts; A private/public evidence joiner that preserves source-level citations and detects contradictions; An ephemeral encrypted comparison workspace with automatic expiry and a dashboard evidence trail; A relay prompt mode that can distinguish authenticated evidence from public search results

### ""When I tell you a browser task while I’m away from my Mac, keep the exact intent and resume it in my existing Safari session when the Mac comes back—then tell me what happened, even if the link dropped.""
- **useful because:** Today the wearable, relay, and browser are separate moments: an owner can speak an intent while mobile, but cannot reliably hand it to a later authenticated Safari session with its context intact. This creates a true asynchronous bridge between the device that hears the request and the browser that holds the login. It is especially useful for collecting a document, checking a status, or preparing a draft during travel, with a durable outcome rather than a lost voice turn.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Cheap background model normalizes the spoken intent into a resumable browser plan and checks completion; realtime model handles ambiguity at capture time and speaks the final result. Do not spend realtime tokens while waiting for the Mac or extension.
- **latency:** Capture and acknowledge offline in under 2 seconds; resume within 10 seconds of Safari becoming available; final alert within 5 seconds of completion.
- **cost:** Typically $0.005–$0.05 per task, mostly intent normalization and final summarization. Queue metadata is tiny; no page body needs to be retained while offline.
- **security:** Persist the intent and permitted action kinds, not authenticated page content or credentials. Bind execution to the intended origin/tab context when Safari returns; if the origin or page state changed, report a pause rather than improvising. Keep the owner’s maximum-access policy, but stop before an irreversible submission and provide the exact proposed action. Queue expiry and cancellation must be visible on the dashboard and pendant.
- **missing:** A signed, durable relay-to-browser intent envelope that survives link loss and records expiry; Browser-side plan resumption with origin/tab revalidation and partial-progress checkpoints; Pendant offline capture of a structured browser intent, beyond offline alert playback; Completion/failure notifications routed back through offline_alert_inbox


## Changes it proposed to its own stack

### `browser-harness` — Add an in-extension redaction-and-minimization boundary before any browser result leaves Safari: extract only the requested DOM region and named fields, replace credential-like values, payment numbers, addresses, tokens, and hidden form values with typed placeholders, and attach a local content hash plus selector provenance. The bridge receives the minimized projection, never the raw page text, except for an explicit owner-selected diagnostic mode.
- **owner gets:** Private pages become safe to use with the whole hive instead of forcing the owner to choose between usefulness and exposing everything visible in Safari. A wrong selector or malicious page cannot casually cause a password, card number, or hidden token to be spoken, persisted, or forwarded.
- effort: Medium-to-high: Safari content-script extraction, field classification, selector scoping, redaction tests against real sites, and a compatibility fallback for pages that render through shadow DOM or canvas.  ·  risk: Over-redaction could remove the very amount, date, or account identifier the owner asked about; recover by showing placeholder labels and allowing a narrower owner-selected region, never by silently sending the raw page. Site-specific DOM changes require adapter updates.
- cost: Negligible runtime/API cost; modest engineering and ongoing adapter maintenance. No hardware cost.  ·  latency: Adds roughly 50–200 ms for DOM projection and classification; large pages improve because far less text crosses the bridge.
- security: Substantially reduces secret exfiltration and accidental retention. It is defense in depth, not a permission gate: the owner can still request maximum-access actions, but the default data crossing is minimized.
- depends on: A browser action schema carrying an explicit tabId and selector/region; A shared field taxonomy between Safari extension redaction and local-agent/redaction.js; Evidence receipts that record hashes and provenance without storing the redacted source


## What it asked for

_Nothing._
