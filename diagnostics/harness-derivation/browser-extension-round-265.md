# Harness derivation — browser-extension — round 265

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Watch this authenticated page for me and, when a meaningful value changes, tell me exactly what changed on the pendant—even if my Mac is asleep afterward."
- **useful because:** A logged-in page watch is more useful than periodic browsing: bills, reservations, deliveries, dashboards, and work portals can change without the owner remembering to check. The browser reads the session while available; the relay compares bounded claims; the pendant's offline inbox preserves the alert across a dropped link.
- **path:** Safari browser extension reads the configured page/session → relay scheduler and change detector → browser provenance store for before/after claim evidence → offline_alert_inbox on the pendant → relay-realtime speaks only the alert summary when requested
- **model tier:** Cheaper background/scheduled model performs extraction and semantic diff; realtime is reserved for turning an alert into a conversational explanation when the owner asks.
- **latency:** Polling cadence can be minutes to hours depending on owner configuration. A detected change should enqueue within one polling interval and be spoken or LED-indicated on the next device connection.
- **cost:** One bounded extraction/diff per poll; low cost if selectors and hashes suppress unchanged pages. Roughly cents per day per frequently watched page, dominated by authenticated page extraction.
- **security:** Ship with no origins or categories assumed. Require an explicit per-origin rule supplied by the owner; store only short claims, not HTML/screenshots; retain 24-hour browser facts and URL evidence; redact configured categories before alerts; never treat a changed page as authorization to click or submit.
- **missing:** A first-class persistent page-watch schedule tied to a browser session and extraction recipe; Semantic diff that distinguishes cosmetic changes from actionable changes; Scheduler-to-pendant alert delivery and deduplication across offline_alert_inbox

### "I lost a detail in a page I was just using—find the confirmation number, date, amount, or address across my recent authenticated browser pages and read back the answer with where you found it."
- **useful because:** This turns the browser session into a private, short-lived memory without storing page bodies. It solves the common “I saw it five minutes ago” problem across tabs and navigation history while keeping evidence auditable and expiring quickly.
- **path:** Safari extension and its named browser sessions → Mac agent searches recent page findings/provenance → relay-realtime resolves the natural-language field requested → pendant speaker gives the answer and source host → browser provenance trace supports “where did that come from?”
- **model tier:** Use a cheap extraction/indexing model when pages are read; realtime only parses the owner’s field request and speaks the selected claim.
- **latency:** Under 4 seconds for already indexed recent claims; up to 10 seconds when the active session must be reread. Return “not found” rather than guessing.
- **cost:** Near-zero for indexed claims; one small extraction call for a cache miss. Storage stays bounded by existing record limits and 24-hour browser TTL.
- **security:** Search only the owner’s explicitly selected recent browser sessions, never the public web. Return the minimum matching value, not surrounding page text. Keep host, URL, timestamp, and evidence capsule for traceability; apply the existing 200-character browser-value cap and expiry.
- **missing:** A queryable recent-claims index keyed by field type and session; Natural-language field extraction with confidence and conflict handling when two pages disagree; A pendant utterance route that can request provenance (“where did you get that?”)

### "Translate the page I’m looking at into plain spoken Spanish (or another language I name), keeping dates, prices, and names exact, and let me ask follow-up questions about the same page without reopening it."
- **useful because:** This makes private authenticated pages usable hands-free for travel, family, and accessibility. Safari contributes the page behind the login; the pendant provides low-friction language choice and audio; the relay maintains a bounded, temporary translation context rather than sending the owner to a public translator.
- **path:** Safari browser extension reads the active authenticated page → Mac agent bounds and chunks visible text → background model translates and extracts immutable fields → relay-realtime answers follow-ups in the requested language → pendant speaker and button provide playback/follow-up
- **model tier:** Use a cheaper background model for translation and chunking; use realtime only for the owner’s spoken language choice, follow-up question, and final response.
- **latency:** Speak a short first section within 5 seconds, then stream or paginate the rest. Follow-up answers from the temporary claim set should be under 3 seconds.
- **cost:** One translation call per bounded page section; roughly $0.02–$0.15 for a long page, dominated by text volume. Cache only short translated claims for the session, not the page body.
- **security:** Never send screenshots or hidden fields. Preserve numeric/date fields from source and label uncertain translations. Use the existing 24-hour browser TTL and 200-character finding cap for any persisted claims; default to session-only context and delete it on request. Do not click links or submit forms.
- **missing:** A session-scoped page translation pipeline with chunking and field preservation; Language selection and spoken follow-up routing from the pendant; A streaming/paginated playback protocol so long translations do not monopolize the speaker

### "On the private page I’m viewing, try the available options in a disposable browser session and tell me which choice gives the best outcome—total price, delivery date, coverage, or eligibility—without changing my real account."
- **useful because:** Today the owner must manually explore every combination in a logged-in site and remember the results. A disposable authenticated session could answer counterfactual questions (“what if I choose the annual plan?”, “which delivery option is fastest?”) while preserving the real page untouched. This combines the pendant’s natural-language intent, Safari’s private login, Mac execution, and relay reasoning in a way no single node can do.
- **path:** pendant microphone and speaker for the counterfactual question → relay-realtime turns the question into bounded option/constraint criteria → Mac browser extension duplicates or forks the current authenticated session → browser automation explores only enumerated reversible controls in the disposable session → background model compares resulting prices/dates/eligibility and returns a compact spoken ranking → pendant alert inbox retains the result if the Mac link drops
- **model tier:** Use a cheaper background model for option enumeration, extraction, and comparison; use realtime only to clarify the owner’s objective and speak the ranked result.
- **latency:** Allow 15–60 seconds for a small option set, with progress updates after each candidate. Large or combinatorial sets should be scheduled as a background job rather than blocking conversation.
- **cost:** A few browser actions per candidate plus extraction; roughly $0.05–$0.50 per small exploration, dominated by model calls and site latency. Never send full page bodies to the model when bounded fields suffice.
- **security:** The fork must be provably disposable and must not submit purchases, messages, cancellations, or irreversible changes. Some sites do not support safe session duplication; in that case use a new tab and allow only reversible controls, then discard it. Treat prices and eligibility as volatile, retain only the final short claims with URL/time provenance, and require explicit owner confirmation before applying any selected option to the real session.
- **missing:** A browser session fork/isolation primitive with automatic teardown; A reversible-action allowlist that can enumerate controls and detect submit/commit boundaries without silently blocking owner-approved work; A structured counterfactual result schema (option, observed fields, timestamp, confidence) and comparison planner; A final apply step that revalidates the real page before any mutation

### "Before I enter anything, check whether this page is the real service I intended, explain any suspicious redirects or payment changes, and tell me what is safe to do next."
- **useful because:** The owner gets a browser-specific phishing and account-takeover check at the moment of risk, including private-session context that public search cannot see. It can catch lookalike domains, unexpected redirect chains, changed payment destinations, and injected instructions before the owner types or clicks.
- **path:** Safari extension reports active URL, redirect chain, visible origin, and form/action destinations → Mac agent checks certificate/origin/network metadata and compares the page against prior provenance → relay background model assesses anomalies and explains them in plain speech → pendant speaks a short warning and can place a high-priority offline alert
- **model tier:** Cheap background classifier handles URL/DOM/network indicators; realtime is used only for the owner’s question and concise spoken recommendation.
- **latency:** Under 3 seconds for cached origin reputation and URL checks; up to 8 seconds for a fresh page inspection. If uncertain, say so and recommend stopping rather than guessing.
- **cost:** Low: metadata and bounded visible fields, usually under $0.02 per check; reputation lookups dominate where needed.
- **security:** Do not transmit passwords, form values, cookies, or page bodies. This is advisory and must not claim a site is safe with certainty. Never auto-fill or click a flagged form. Persist only a short finding with host, URL, evidence, and expiry.
- **missing:** Origin/redirect and form-destination inspection exposed by the extension; Local certificate and network metadata reader; A maintained reputation/anomaly evaluator with explainable evidence; A pendant warning priority distinct from ordinary informational alerts

### "Make this private website usable hands-free: move through headings, fields, and results as I say “next”, “back”, or a label, and read only the focused item aloud."
- **useful because:** The owner should not need to copy text or use a mouse to operate a complex logged-in site. Safari provides the real DOM and session, the pendant supplies voice and physical feedback, and the Mac executes small reversible focus/scroll actions. This is an interaction layer for the whole private web, not a one-off page summary.
- **path:** pendant button/microphone and speaker → relay-realtime interprets short navigation commands → Safari extension exposes accessibility tree, focus, and scroll state → Mac agent performs focus/scroll/select actions and reports the focused label/value → pendant LED/audio indicates current position and errors
- **model tier:** Realtime model handles low-latency command interpretation and short speech; use a cheap local/accessibility-tree parser rather than a large model for navigation.
- **latency:** Each next/back/focus command should respond in under 1 second. Rebuild the accessibility map only after navigation or a detected DOM change.
- **cost:** Very low per command if the accessibility tree is parsed locally; occasional small model calls for ambiguous natural-language labels.
- **security:** Read values only from the focused element, never hidden fields; mask password/payment inputs by default. Keep navigation actions separate from submit/commit controls and announce when focus reaches an irreversible control. Do not persist page text.
- **missing:** Extension support for accessibility-tree extraction and stable element references; A focus-navigation state machine resilient to dynamic DOM updates; Voice command routing that distinguishes navigation from mutation; Pendant playback interruption/short-response integration for rapid commands


## Changes it proposed to its own stack

### `browser-harness` — Add an explicit, expiring “page context lease”: when a browser job begins, bind it to the current Safari tab ID, URL, title, and a content fingerprint; every read/follow-up verifies the same tab and detects navigation or account changes. If it changed, return a spoken “the page changed—use the new page?” result instead of silently answering from stale text.
- **owner gets:** Follow-up questions will answer the page the owner meant, not whichever tab Safari happens to expose seconds later. This is essential for private pages where a silent tab switch could leak the wrong account’s information.
- effort: Moderate: browser session schema, fingerprint comparison, lease expiry, and one relay result state.  ·  risk: A legitimate SPA refresh may look changed and ask unnecessarily; recover by offering an explicit re-read. No mutation is performed.
- cost: Negligible storage and hashing cost; avoids expensive re-extractions on stale contexts.  ·  latency: Adds tens of milliseconds for fingerprint/session validation.
- security: Improves isolation between tabs/accounts; do not persist page text, only bounded fingerprint and provenance metadata.
- depends on: POST /execute browser action path; GET /browser/sessions; GET /browser/status; GET /browser/provenance


## What it asked for

_Nothing._
## Its own summary

Discovered live Safari is online with one authenticated-capable tab (YouTube, tab 85), four persisted browser sessions, no pending commands, and an empty provenance store. Recorded three new owner-facing capabilities: authenticated-page change watching with offline pendant alerts, short-lived cross-page/private claim lookup with provenance, and session-scoped translation with spoken follow-ups. Also recorded an expiring active-tab context lease to prevent stale-tab or cross-account answers. The strongest immediate product is private browser claim lookup: the owner asks for a confirmation number/date/amount, and the system finds the minimum claim across recent authenticated pages with source and expiry.

**Biggest unknown:** The owner has not supplied the first real authenticated origins or categories that must never be spoken/persisted. I still need that explicit configuration (ship empty rather than inventing it), plus implementation of a reliable current-tab read/lease, a persistent page-watch scheduler and semantic diff, and a session-scoped claims index. Existing browser retention is already bounded (claims/provenance, 24-hour TTL, 200-character values); I do not need a new retention policy.

