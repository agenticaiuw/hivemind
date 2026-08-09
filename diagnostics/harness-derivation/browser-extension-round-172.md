# Harness derivation — browser-extension — round 172

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with 9 tabs, including authenticated Gmail at mail.google.com and active X at x.com/home; POST /execute with browser_list_tabs succeeds and returns tab IDs plus provenance receipts.
  - evidence: POST /execute 2026-08-08T02:49:13Z returned 9 open web tabs; tab 901464 Gmail, active tab 1163292 X.

## Capabilities it proposed

### "“On the page I’m looking at, find anything that requires action, draft the next steps, and put the concrete deadlines on my Mac as reminders—but don’t send or submit anything.”"
- **useful because:** This turns an authenticated page into completed personal follow-through rather than a spoken summary. Safari can see logged-in content, the model can distinguish obligations from boilerplate, the Mac can create reminders, and the pendant can report exactly what was created while the owner is away from the screen.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Background model for extraction and deadline ranking; realtime only for the owner’s short spoken request and confirmation of the reminder list.
- **latency:** 10–20 seconds for one page; reminders may be created asynchronously, with a concise pendant reply as soon as the draft is ready.
- **cost:** Roughly $0.01–$0.05 per page depending on page length; browser/Mac calls dominate wall time, not tokens.
- **security:** Authenticated page text leaves Safari for processing and may contain private data. Use existing per-origin redaction rules, retain only extracted obligations and URLs, and show the exact reminder titles/dates before creating them. Never submit, send, or alter the source page.
- **missing:** A page-to-obligation extractor that emits structured {title, due, evidence, confidence} records; A browser action to target the current tab and return bounded readable text plus URL; A reminder preview/commit protocol linking each reminder to its source evidence

### "“Fill out this logged-in web form from what I just told you, then read back every field and leave it ready for me to submit.”"
- **useful because:** Form filling is where the browser’s private sessions provide unique value: the Mac and relay cannot reach the same authenticated form. The owner gets the tedious work done without losing control of an irreversible submission, and the pendant provides an audible field-by-field check when the screen is inconvenient.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Realtime model for parsing the request and resolving ambiguities; a cheaper background pass validates field types, required fields, and suspicious mismatches.
- **latency:** Under 30 seconds for a normal form, with incremental progress after each page section and a final spoken diff.
- **cost:** About $0.02–$0.10 per form; long forms and screenshot/DOM extraction dominate.
- **security:** Values such as addresses, health data, or payment details must be treated as transient and redacted from logs. Existing per-origin policy should control read/fill/store. Stop at the final submit/send/purchase control and expose the exact payload; do not infer missing high-impact values.
- **missing:** Reliable DOM-label to value mapping with a screenshot fallback; A transient sensitive-field channel that excludes values from receipts and model memory; A final-state verifier that detects fields changed by site JavaScript before handoff

### "“Save this authenticated page as a private, searchable note, summarize it for me now, and let me ask follow-up questions about the saved evidence later.”"
- **useful because:** The browser can reach pages behind existing logins while the Mac can provide durable local search and the pendant can give an immediate spoken summary. This creates a useful bridge between a fleeting web session and later conversations without persisting the entire page by default.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model makes a structured summary, entities, and quote-level index; realtime handles only the immediate summary and later questions.
- **latency:** Initial capture and indexing in 5–30 seconds depending on page size; spoken summary in under 8 seconds.
- **cost:** Approximately $0.01–$0.08 per capture; OCR or long-page extraction is the main cost.
- **security:** Default to local encrypted storage on the Mac, not relay memory. Apply per-origin ‘never store’ and category redaction rules before persistence; retain source URL, timestamp, and minimal quoted evidence only when allowed. The owner must be able to delete the note and all derived index entries.
- **missing:** A user-visible private-note store with encryption and deletion propagation; A bounded evidence extractor that can answer follow-ups without retaining raw page text; A policy editor for per-origin read/extract/redact/never-store choices

### "“Compare the relevant open tabs, including my logged-in sources and public pages, and tell me what facts agree, conflict, or still need checking—with links I can revisit.”"
- **useful because:** Safari currently has nine live tabs, including authenticated Gmail and public research pages. No other node can inspect those private tabs. A provenance-aware comparison would replace tab hopping with an answer that distinguishes evidence from inference and can be spoken briefly through the pendant.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Background synthesis model for extraction, deduplication, and contradiction analysis; realtime only compresses the result into a spoken answer.
- **latency:** 15–45 seconds for up to ten tabs; stream an initial tab inventory in under 3 seconds.
- **cost:** About $0.03–$0.15 per comparison, driven by page length and OCR.
- **security:** Private tab content must be origin-scoped and excluded from logs unless allowed. Preserve citations and confidence, but redact secrets and personal messages. Make the source set explicit before reading broad tab groups.
- **missing:** A bounded multi-tab capture operation with per-origin policy checks; Claim-level provenance and contradiction representation; A compact spoken citation format plus a Mac view for the full evidence

### "“If a site I’m using logs me out, changes its domain, or shows a suspicious login/payment page, warn me on the pendant and save a local diagnostic—but never enter credentials or continue.”"
- **useful because:** The browser extension is the only node that sees the owner’s authenticated session and can notice an unexpected redirect or altered checkout. A wearable warning is useful when the Mac is unattended, while a local diagnostic helps recover without exposing credentials to the relay.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap background rules/model for URL, title, and DOM-change classification; realtime only speaks a high-priority warning.
- **latency:** Detect within one browser poll (roughly seconds), alert within 5 seconds.
- **cost:** Pennies per monitored tab per day; most work is local URL/DOM comparison.
- **security:** Never capture passwords, OTPs, card numbers, or page bodies by default. Store only origin, redirect chain, redacted labels, and hashes locally. Warning must be informative, not an automatic action or login gate.
- **missing:** A persistent per-origin baseline and redirect anomaly detector; A pendant alert priority/source payload for security events; A local-only redacted diagnostic writer with retention limits

### "“Reconcile the purchase, delivery, and receipt information across my logged-in sites, and tell me if anything is missing, duplicated, late, or charged differently.”"
- **useful because:** The owner cannot get this from any single tab: the order portal, email receipt, and delivery tracker each expose only part of the truth. The browser can reach all authenticated sessions, the Mac can maintain a private reconciliation ledger, and the pendant can announce only exceptions instead of making the owner search manually.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model for entity matching and discrepancy classification; realtime only speaks exceptions and asks whether to create a follow-up.
- **latency:** 30–90 seconds for three to five sites; partial results should arrive as each source is inspected.
- **cost:** Approximately $0.05–$0.30 per reconciliation, dominated by multiple authenticated page reads and long email threads.
- **security:** Payment and order data is highly sensitive. Keep raw pages transient, store only redacted transaction fingerprints and exception evidence locally, and make source domains explicit before reading them. Never cancel, dispute, or contact a merchant automatically.
- **missing:** Cross-origin transaction identity matching with confidence and user correction; A local encrypted discrepancy ledger with expiry and deletion propagation; A multi-source browser workflow that can preserve separate provenance for each claim

### "“Turn this complicated authenticated web application into a temporary spoken control panel: tell me what I can do, let me choose by saying the action, and show me the exact effect before carrying it out.”"
- **useful because:** Many important services are unusable while walking, driving, or using accessibility controls because their meaningful state is buried in dense interfaces. Safari supplies the private page, the model converts it into a short task-oriented menu, and the pendant becomes an accessible voice surface without requiring a site-specific integration.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Realtime model for low-latency menu navigation and disambiguation; background model precomputes page structure and validates the proposed effect.
- **latency:** Initial menu in under 8 seconds; each spoken choice acknowledged in under 2 seconds.
- **cost:** Roughly $0.02–$0.12 per interaction session, mostly realtime turns and occasional page re-observation.
- **security:** The temporary menu must be derived from the current page and expire on navigation or timeout. Read-only options can execute immediately; mutating options must be narrated with exact before/after effects and stop before irreversible submission. Avoid speaking sensitive field values aloud unless explicitly requested.
- **missing:** A semantic UI graph from DOM plus accessibility tree, with stable action references; A spoken menu/session protocol that survives page re-rendering; A compact effect preview and stale-page check before mutation


## Changes it proposed to its own stack

### `browser-harness` — Add a first-class “current tab evidence capsule” operation to the browser harness: capture URL/title/visible text/DOM landmarks and optional screenshot in one bounded response, apply the existing per-origin redaction policy before leaving Safari, attach tabId and timestamp, and expose a delete/expiry handle. Make it usable by the relay, Mac planner, and pendant alert pipeline rather than requiring each workflow to chain browser_snapshot, browser_read_page, and capture independently.
- **owner gets:** The owner can say “use what I’m looking at” and get a grounded answer or reminder without the system confusing tabs, losing citations, or retaining an accidental full page. It also makes authenticated browser work dependable enough for daily use.
- effort: Medium: extension result schema, local-agent browser bridge, redaction integration, and tests across nine-tab Safari sessions.  ·  risk: A capsule could accidentally include private page text or stale content. Default to visible bounded text, enforce origin policy and short TTLs, include freshness metadata, and provide deletion. If capture fails, fall back to URL/title only.
- cost: Negligible API cost change; one slightly larger browser result per invocation and modest local storage while TTL is active.  ·  latency: Adds about 1–3 seconds versus separate actions, but removes repeated round trips and ambiguity.
- security: Improves security by centralizing redaction and provenance; requires careful treatment of screenshots and sensitive origins.
- depends on: Existing local-agent redaction.js and originFanOut.js policy machinery; POST /execute browser_* action path; POST /capture and DELETE /capture/:key; A value supplied by the owner for per-origin storage rules

### `model-routing` — Add a local-first browser privacy compiler on the Mac: before any authenticated page evidence is sent to a remote model, classify and redact secrets, personal identifiers, message bodies, and payment fields locally; send only a task-specific semantic representation plus minimal quoted spans. Permit an explicit per-origin override and attach a reversible privacy receipt showing exactly what left the Mac.
- **owner gets:** The owner could use the browser agent on genuinely private accounts without having to choose between useful automation and exporting an entire inbox or account page. They would be able to inspect and revoke the evidence that was shared rather than trusting an opaque capture.
- effort: High: local classifier/redactor, schema for semantic page representations, extension-to-Mac handoff, policy UI, and tests against real Safari DOMs.  ·  risk: Over-redaction can make a task fail; under-redaction can expose private data. Fail closed for uncertain secret fields, offer a local-only retry, and keep raw evidence ephemeral with strict TTLs.
- cost: Adds local CPU and storage work but reduces remote token and image costs; likely lower ongoing API spend for long pages.  ·  latency: Adds 1–4 seconds locally per page, offset by smaller remote requests.
- security: Substantially reduces data leaving the Mac, but the classifier and policy compiler become high-value security components and require auditable tests.
- depends on: Existing local-agent redaction.js, origin policy machinery, and browser result provenance; A per-origin policy configuration supplied by the owner; A browser evidence-capsule format or equivalent bounded extraction contract


## What it asked for

_Nothing._
