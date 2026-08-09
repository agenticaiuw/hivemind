# Harness derivation — browser-extension — round 230

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m looking at this form—figure out what it needs, find the right information from my other logged-in tabs, fill a reviewable draft, and tell me exactly what you’re about to submit.”"
- **useful because:** This is a genuinely cross-surface job: Safari can see authenticated pages, the Mac can coordinate and extract values, the relay can reason over the joined evidence, and the pendant can announce missing fields or a draft while the owner is away from the screen. It saves the owner from tab-switching and transcription without silently sending a form.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap background model for field mapping and normalization; use realtime only for the owner's spoken clarification and final concise readback.
- **latency:** 3–8 seconds to inspect and populate a draft; under 1 second for a spoken clarification. Stop before submit/send/purchase and expose the exact outgoing payload.
- **cost:** Roughly $0.01–$0.05 per form depending on number of authenticated pages; browser actions and local extraction dominate latency, not tokens.
- **security:** Read only the explicitly selected tabs and fields; never persist page text. Store only short-lived claims under existing browser provenance/24-hour limits. Cross-origin values must be shown with source URLs. Submitting remains a separate explicit action; a failed login or MFA challenge is reported, never bypassed.
- **missing:** A browser action that can target a stable tab/session and return structured form labels, values, and field provenance (current generic snapshot/read-page output is too lossy).; A draft-field ledger joining source claim -> destination field -> transformed value, with undo/clear.; An explicit empty per-origin and per-category owner configuration, filled later rather than guessed.

### "“Tell me if any of my open logged-in accounts suddenly asks for a password, shows a security warning, or signs me out—and put the precise account and page on my pendant.”"
- **useful because:** A generic page watcher reports content changes; this is a safety sentinel for authentication state. It turns the browser's unique access to existing sessions into an early warning system for account takeover, expiring sessions, or urgent security notices, with a short wearable alert even when the owner is not at the Mac.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Run scheduled polling and deterministic classifiers locally/cheaply; use the expensive realtime model only when a change is ambiguous or the owner asks for explanation.
- **latency:** Poll on an owner-selected interval (for example 5–15 minutes); alert within one poll interval. A spoken explanation should take under 2 seconds after the owner asks.
- **cost:** About $0.001–$0.02 per poll cycle, primarily browser and relay execution; ambiguous screenshots/pages are the expensive tail.
- **security:** Default to metadata and security-banner text, not account content. Keep host-scoped, 24-hour claims with URL provenance; never store screenshots or page bodies. Do not click recovery links or change credentials. The empty origin policy must remain explicit until the owner chooses accounts.
- **missing:** A persisted watch definition bound to a browser session/tab with last-known authentication state and semantic fingerprint.; A security-focused classifier for login/MFA/password-expiry/session-revocation UI, including confidence and deduplication.; A relay-to-offline-alert-inbox delivery path that includes host, timestamp, reason, and a safe truncation.

### "“Compare this receipt/order with the charge in my logged-in account, and tell me if the amount, merchant, and date agree—do not dispute or buy anything.”"
- **useful because:** It catches billing mistakes and fraud that no single tab can establish. The browser reads two authenticated origins, the Mac normalizes dates/currencies, the relay explains a discrepancy, and the pendant delivers a compact alert while retaining source links for inspection. It is a concrete, high-value use of multi-origin access rather than another generic page summary.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use deterministic extraction and currency/date normalization first; background model for matching. Escalate only ambiguous discrepancies to realtime conversation.
- **latency:** 10–20 seconds for two pages and a comparison; under 2 seconds to speak the result once evidence is ready.
- **cost:** $0.01–$0.08 per comparison, dominated by two browser reads and occasional model disambiguation.
- **security:** Cross-origin correlation is sensitive: require the owner to name the two tabs/origins for each run and never infer a broad account inventory. Persist only the result claim (matched/discrepant, amount/date/merchant, URLs) under the existing short TTL; discard raw values after comparison. Never click dispute, refund, checkout, or payment controls.
- **missing:** A user-visible two-tab selection and correlation job, rather than implicit active-tab guessing.; A typed comparison result with field-level evidence and tolerance rules for tax, currency conversion, tips, and pending charges.; A redaction layer that can speak a discrepancy without reading full account identifiers aloud.

### "“I’m reading this claim on the page—check it against independent sources, tell me what agrees or conflicts, and keep the original page and citations together.”"
- **useful because:** The owner currently has to copy a claim out of a logged-in or paywalled page, search separately, and manually reconcile sources. This would let the browser retrieve the exact claim behind the owner's session, the public web tier find independent evidence, and the relay explain agreement, conflict, and uncertainty through the pendant without treating the source page as true merely because it is authenticated.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use deterministic claim extraction, URL/domain diversity checks, and a cheaper background model for evidence clustering; reserve realtime for the owner's follow-up question or an ambiguous conflict.
- **latency:** 15–30 seconds for an initial evidence bundle; a spoken follow-up under 2 seconds once the bundle is cached.
- **cost:** Approximately $0.02–$0.12 per claim, dominated by independent web retrieval and synthesis; no cost for repeated pendant follow-ups against the cached bundle.
- **security:** Read only the page and region the owner names; send a claim rather than the whole authenticated page to public search. Strip account identifiers and hidden page metadata. Persist only short-lived claim/evidence hashes and source URLs, never page text or screenshots. Clearly label sponsored, copied, and low-independence sources; do not publish, edit, or interact with the original page.
- **missing:** A browser extraction operation that returns a selected text range with stable DOM locator and source URL, rather than an entire lossy page dump.; A research orchestrator that accepts one browser claim, retrieves independent public sources, scores source independence, and preserves claim-to-citation links.; A compact evidence bundle that the relay can hand to the pendant and later reopen without re-reading the sensitive page.; An explicit empty per-origin policy and owner-selected speech/retention categories before authenticated content is processed.

### "“Before I submit this page, tell me every piece of personal data it will send, which fields are unusual for this task, and show me the exact payload without sending it.”"
- **useful because:** Today the owner can see a form, but not reliably understand hidden fields, prefilled values, tracking parameters, or the destination assembled by JavaScript. This creates a browser-specific privacy check: Safari inspects the actual form and network-bound values, the Mac classifies anomalies against the task, and the pendant gives a short warning while the full field list remains on screen.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use local deterministic DOM/form and URL inspection first; use a background model to classify unusual fields; use realtime only when the owner asks why a field was flagged.
- **latency:** 2–6 seconds for ordinary forms; under 2 seconds for a spoken explanation.
- **cost:** $0.005–$0.03 per inspection; browser extraction dominates and the deterministic pass should handle most pages.
- **security:** The inspector itself must not transmit values to a remote model by default. Redact secrets and identifiers before classification, distinguish visible from hidden/disabled fields, and retain only a schema-level finding plus page provenance. Never submit, click consent, or alter form values.
- **missing:** A browser-side form/network payload inspector with an explicit no-submit mode and hidden-field detection.; A redaction-aware field taxonomy and task-relative anomaly classifier, shipped with no hardcoded sensitive-site assumptions.; A rendered, owner-readable diff between current form state and the eventual serialized payload.; An empty owner policy for origins, categories allowed to be spoken, and categories forbidden from retention.

### "“This logged-in site is broken—tell me whether it’s my session, the site, or my Mac, check the service-status page, and give me the safest recovery step without logging me out.”"
- **useful because:** An owner currently has to debug an authenticated web failure manually, often losing unsaved work by refreshing or signing out. This joins the private page's visible error state with public status endpoints and local Mac/browser diagnostics, then gives a diagnosis and reversible next step on the pendant. It is useful precisely because no single node can see all three failure domains.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use deterministic browser/Mac probes and public status retrieval; use a cheaper model to classify likely causes. Realtime is only for explaining the diagnosis or choosing between recovery options.
- **latency:** 5–15 seconds for diagnosis; recovery actions should be individually previewed and reversible.
- **cost:** $0.003–$0.03 per incident, mostly local/browser probes; public status pages are cheap and cacheable.
- **security:** Do not expose private page contents to public status lookups. Never clear cookies, sign out, resend forms, or discard drafts automatically. Capture only error text/status codes and short-lived provenance; tell the owner if a recovery step could lose state.
- **missing:** A browser diagnostic action that captures URL, visible error, HTTP/navigation state, console summary, and unsaved-form presence without page-body persistence.; A Mac-side network/DNS/TLS probe correlated with the browser tab and timestamp.; A service-status resolver that maps the owner-approved origin to its public status source without inventing a site list.; A recovery planner that ranks non-destructive actions and streams a concise diagnosis to the pendant.


## Changes it proposed to its own stack

### `browser-harness` — Make browser session targeting authoritative and self-healing: every browser_* command must resolve a tab from the latest extension tab list, reject stale session tabIds with a refreshed candidate list, and attach the actual tabId/windowId/url to the receipt. Remove or quarantine stale recovery metadata (the live list reported tab 5696555 while the default session advertised an unrelated Namecheap tabId 5698643).
- **owner gets:** The owner can say “read this tab” and trust that the assistant used the page actually open, not an old tab identity left in a session record. It prevents silent misreads—the worst failure mode for authenticated browsing—and makes spoken claims auditable.
- effort: Medium: browser bridge/session resolution, receipt schema, and extension result handling; add tests for tab close, reorder, Safari restart, and two tabs with similar titles.  ·  risk: A tab disappearing mid-command may cause a safe retry or a clear failure instead of acting elsewhere. Recover by refreshing the tab list and requiring an explicit tab choice when ambiguity remains.
- cost: Negligible API cost; one extra local tab-list call on stale-session recovery.  ·  latency: Usually none; 0.5–1 second only when refreshing a stale target.
- security: Improves security by binding every read/write to the observed origin and tab identity; does not create an origin allowlist, which must remain owner-configured.
- depends on: Stable structured tab/session identifiers in browser extension results; Field-level provenance and receipts for browser actions; An explicit empty per-origin policy rather than invented sites


## What it asked for

_Nothing._
## Its own summary

Discovered Safari is online with two tabs and proved browser execution works through POST /execute. Crucially, a read addressed to tabId 5696555 returned YouTube tab 3186198, confirming stale/unsafe session targeting. Recorded three cross-surface capabilities: reviewable authenticated form preparation, security-state sentinel alerts to the pendant, and cross-origin receipt/charge reconciliation; also recorded a browser-harness change to make tab targeting authoritative and self-healing. Sent the live mismatch to mac-planner and all agents.

**Biggest unknown:** The owner still needs to supply the first explicit browser-origin and data-category policy (which origins may be read, what may be spoken, and what may be retained). Until then, do not automate authenticated pages; and until tab targeting is fixed, do not trust a requested tabId for sensitive reads.

