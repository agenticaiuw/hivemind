# Harness derivation — browser-extension — round 201

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“File the invoice I’m viewing: extract the vendor, invoice number, amount, and due date, save the original to my invoices folder with a safe filename, and remind me before it’s due.”"
- **useful because:** No single node can do this: only Safari has the authenticated invoice, while only the Mac can place and rename a local file and create a durable reminder. The pendant provides a hands-free request and confirmation summary. It eliminates repetitive clerical work while preserving the original document and provenance.
- **path:** relay-realtime → browser-extension → mac-planner → mac-terminal
- **model tier:** Cheap background extraction validates fields and proposes a filename; realtime handles the short spoken request and result. Use the local Mac tier for file movement and reminder creation rather than sending document contents to a large model.
- **latency:** Read and field extraction in 10–30 seconds; local save and reminder in under 5 seconds after the browser download is available.
- **cost:** One small extraction call per invoice; local Mac actions dominate no API cost. Optional OCR costs more only when the page exposes no text.
- **security:** The invoice is private and should never be persisted as page text. Keep only bounded claims (vendor/number/amount/date) with the existing browser TTL and provenance; save the original directly on the Mac. Treat payment instructions and bank details as redacted. Before any file overwrite or sending, show the proposed path and filename; do not pay or submit anything.
- **missing:** A browser download/export action with a verifiable completed-file receipt; A local handoff that maps a browser result to the downloaded file without copying page contents through the relay; A robust invoice-field schema plus date/amount validation and duplicate detection; A reversible file organizer action (quarantine/rename with undo) wired to reminder creation

### "“Read the message thread open in Safari, draft a concise reply using the facts in the thread and my local notes, and leave it in the mail app for me to review—do not send it.”"
- **useful because:** This combines the browser’s authenticated session with the Mac’s local notes/mail context and gives the owner a useful draft without exposing the thread to a public search or forcing them to copy/paste. The pendant can read back the proposed reply while the Mac leaves it visibly editable.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime
- **model tier:** A background/local model gathers and summarizes the thread and local notes; realtime is used only for the owner’s spoken instruction and a short read-back. Keep the final draft generation local where possible because the source is private correspondence.
- **latency:** 20–45 seconds for thread extraction and draft; under 5 seconds to insert into a new unsent draft window.
- **cost:** One small private-context drafting call, dominated by thread length; no recurring cost after the draft is placed. Avoid screenshot/OCR unless the page is image-only.
- **security:** Never send or submit. Treat recipient, thread text, and local notes as private; retain only a redacted action receipt and short provenance claim, not the message body. Display recipient/subject/body in the Mac draft and speak only a short summary unless explicitly asked to read it aloud.
- **missing:** A browser-to-local-agent private context handoff that keeps full thread text off relay logs; A deterministic mail-draft insertion action with an explicit unsent state and receipt; A context joiner for authenticated browser text plus selected local notes, with secret/redaction handling; A postcondition check that the draft exists and was not sent

### "“Before I click anything on this logged-in page, check whether this request looks legitimate, explain why, and point out exactly what information it is asking for.”"
- **useful because:** The browser can inspect the real authenticated page while web search can independently compare the origin and organization’s public guidance; the relay can give a quick spoken warning through the pendant before the owner reveals a password, recovery code, or payment detail. This is a practical safety function that neither public search nor the Mac alone can provide from the live session.
- **path:** browser-extension → relay-realtime → mac-planner
- **model tier:** Cheap background model extracts the page’s origin, request type, and suspicious indicators; web_search supplies independent public corroboration. Realtime gives the owner a short, uncertainty-aware verdict and answers follow-ups.
- **latency:** 5–15 seconds for a pre-click check; never block ordinary browsing unless the owner explicitly asks for the check.
- **cost:** One bounded page extraction plus one or two public searches per check. Costs are low compared with a compromised account; no page body should be sent beyond the minimum redacted excerpt needed for classification.
- **security:** This is advisory, not a guarantee. Never submit credentials, codes, or payments. Redact values and preserve only a short risk finding with 24-hour browser TTL; keep the URL/origin and evidence hash for provenance. Unknown origins should receive a cautious “cannot verify” result, not a confident safe verdict. The owner supplies any per-origin configuration; ship it empty.
- **missing:** A browser pre-action inspection hook that can run immediately before a click/type/submit; A combined origin-reputation and page-intent classifier with explicit uncertainty and reasons; A pendant alert/readback format for urgent phishing warnings; A way to label the next browser action as “user reviewed” without turning it into a hard execution gate

### "“Compare the two authenticated documents I have open—tell me every material difference in dates, amounts, names, and obligations, and cite which page each difference came from.”"
- **useful because:** The owner cannot reliably compare private portal documents by hand on a small screen. Safari can access both authenticated pages, while the relay can produce a concise spoken discrepancy report and the Mac can retain only bounded citations. This is especially valuable for revised invoices, contracts, insurance notices, and account terms.
- **path:** browser-extension → relay-realtime → mac-planner
- **model tier:** Use a background model for structured extraction and deterministic field comparison; use realtime only to answer follow-up questions about a cited difference.
- **latency:** 20–60 seconds for two pages, with a progress notification if either page loads slowly; follow-up answers under 5 seconds when evidence is cached.
- **cost:** One extraction/comparison call per pair of documents; cost is proportional to extracted fields, not full page size. Browser polling and page load dominate latency.
- **security:** Never persist complete documents. Extract only the requested field classes, cap values, attach URL/page provenance, and expire the evidence quickly. Do not infer legal meaning as fact; label uncertain interpretation and ask the owner whether to include a category. The owner must explicitly select the tabs or origins.
- **missing:** A multi-tab browser read operation that returns stable tab/page identifiers and bounded text; A schema-driven document extractor with field-level provenance; A comparison engine that distinguishes changed values from layout/order noise; A spoken report format that can refer back to a specific source page without retaining its body

### "“When I’m on a support or government portal, walk me through the next required step using the exact labels on the page, but never guess a field value; tell me what I need to provide and wait while I fill it.”"
- **useful because:** The browser tier can see labels and validation errors behind the owner’s login, while the pendant provides hands-free, screen-independent guidance. This makes difficult portals accessible without having the system invent personal answers or silently submit anything. It is a guided accessibility layer, not generic form automation.
- **path:** browser-extension → relay-realtime → mac-planner
- **model tier:** A low-cost model maps visible labels and validation messages into a finite checklist; realtime handles conversational turn-taking and reads only the next step.
- **latency:** Initial page interpretation under 10 seconds; each next-step response under 3 seconds after a page read.
- **cost:** Small extraction call per page transition. Most latency comes from browser round trips; no scheduled model spend.
- **security:** Use an action allow-set containing read, focus, and scroll only. Never type, click submit, or expose hidden fields. Redact values and retain no form body. If a page requests credentials or one-time codes, identify the field but do not repeat the value aloud.
- **missing:** A browser read/focus/scroll protocol that returns visible labels, validation messages, and element locators; A page-state diff so guidance advances only after the owner changes the page; A strict read-only execution profile for browser actions; A concise pendant dialogue protocol for long multi-step forms

### "“Find the cancellation or renewal deadline in the account I’m viewing, explain what action preserves my options, and put a local countdown on my Mac that links back to the exact page.”"
- **useful because:** Authenticated portals often bury deadlines in private account pages that public search cannot reach. The browser extracts the deadline and supporting wording; the Mac provides a durable local countdown even if Safari is closed; the pendant can announce the next deadline. This prevents costly missed renewals without automating a cancellation or purchase.
- **path:** browser-extension → mac-planner → relay-realtime
- **model tier:** Background extraction normalizes dates and distinguishes deadlines from merely displayed dates; realtime answers questions. Local Mac scheduling and link storage require no expensive model.
- **latency:** Initial extraction in 10–30 seconds; reminder creation under 5 seconds; optional daily countdown check is local and inexpensive.
- **cost:** One bounded extraction call per requested page, then negligible local scheduling cost. No recurring browser polling unless the owner asks for re-checks.
- **security:** Store only the deadline, account/provider label, URL, and a short evidence claim with browser TTL; never save account numbers or page text. If the deadline is ambiguous or timezone-dependent, say so and create no reminder until clarified. Opening the link may require an existing authenticated session.
- **missing:** A deadline/date extraction schema with timezone and ambiguity handling; A durable Mac reminder/countdown type that preserves a deep link and evidence freshness; A stale-link check that marks the reminder unverified when the page changes or session expires; A compact pendant alert carrying provider, date, and urgency without sensitive account details


## Changes it proposed to its own stack

### `browser-harness` — Add a browser “handoff capsule” action that captures the current authenticated page’s URL, title, selected/targeted text claim, content hash, and a user-chosen task label, then transfers the capsule directly to the Mac agent. The capsule must expire, carry host/locator/provenance, and omit raw HTML, screenshots, cookies, and credentials. The Mac can turn it into a local task or reminder and later reopen the same tab/session for verification.
- **owner gets:** The owner can say “make this a task” while looking at any logged-in page instead of copying a URL and private details by hand. The task remains useful after Safari changes pages, yet the system does not retain an entire sensitive page.
- effort: Medium: extension selection/target capture, a private browser-to-Mac handoff route, capsule schema/TTL, and a reopen-and-verify path. Requires testing across SPA pages and pages that disallow selection.  ·  risk: A captured selection may contain a secret or misleading stale instruction. Default to a short character cap, redact obvious credentials, show the exact capsule summary before creating a task, and expire unresolved capsules. If reopening fails, keep the local task but mark its evidence stale rather than pretending it was verified.
- cost: Small implementation/API cost; one bounded claim-generation call only when the owner asks. No recurring model spend. Storage is a few KB per capsule, not page content.  ·  latency: Capture should be sub-second; local task creation under 3 seconds. Reopen verification may take 5–20 seconds and should be asynchronous.
- security: Improves privacy versus copying pages into relay logs, but introduces a new sensitive handoff. Bind capsules to the owner’s authenticated device/session, encrypt in transit and at rest, retain provenance and TTL, and never include cookies, screenshots, or full page text.
- depends on: A browser extension action that can report the active tab and bounded selection/DOM target; A private handoff endpoint between browser extension and mac-planner; Existing browser provenance and short-lived browser-finding retention; A local task/reminder action on mac-planner


## What it asked for

_Nothing._
