# Harness derivation — browser-extension — round 258

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-device-live-state** — Capability discovery now reports Safari on MacIntel online with 1 tab, unlike the previously observed zero-tab state; browser work may be immediately testable, but the unresolved browser command wrapper still prevents reliable inspection from this agent.
  - evidence: discover(category=devices) returned Safari on MacIntel — browser · Safari · 1 tab(s) · online at round 258; browser_read_or_navigate and browser_enqueue_command both failed schema resolution because browser_list_tabs is ambiguous with browser_list_sessions.

## Capabilities it proposed

### "Fill out this authenticated web form using the relevant information on my Mac, read me a concise preview on the pendant, and leave it ready for my final submit."
- **useful because:** This joins the only browser session that can see the logged-in form, the Mac that can retrieve local documents and normalize fields, and the pendant that can give a hands-free, privacy-preserving preview. Today those surfaces can each act, but none can safely turn a multi-field form into a reviewable, submit-ready draft without copying data manually.
- **path:** browser → mac-bridge → pendant → relay
- **model tier:** Use the background/cheaper model to map labels and normalize local data; use realtime only to answer the owner's spoken clarification or read the final compact diff. Browser and Mac agents execute deterministic fills; no expensive model sees the whole page after extraction.
- **latency:** 20–45 seconds for page inspection and local lookup; under 5 seconds for a spoken clarification. Never submit or send; stop with a field-by-field diff and the exact submit target.
- **cost:** Usually <$0.03 per invocation; model cost is dominated by ambiguous labels and local-document matching, not browser actions. Deterministic extraction/fill should be near-zero.
- **security:** The browser session and local files are sensitive and must remain on-device. Persist only short-lived field claims/provenance, never HTML, screenshots, or full form values. Empty per-origin rules remain the default until the owner configures them. The system must show source for every filled field, highlight guesses and missing values, and never silently overwrite existing form contents.
- **missing:** A browser action contract that returns field labels, current values, and stable refs as a structured draft (not only page text); A local-agent join operation that can search approved Mac sources and attach provenance to each proposed field; A pendant-readable diff/ack protocol; final submit remains an explicit separate action if the owner later asks

### "After I complete a booking or purchase in Safari, reconcile the confirmation against my calendar and saved details, then tell me on the pendant what changed and create any needed reminders."
- **useful because:** Confirmation pages are where errors become expensive: wrong date, duplicate booking, missing cancellation window, or a price different from what was expected. The browser can see the authenticated confirmation, the Mac can compare it with Calendar/files, and the pendant can deliver a two-line result while the owner is away from the screen.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Use a cheap background extractor for confirmation fields and deterministic comparison against Calendar/files; reserve realtime for a spoken discrepancy explanation. No model should infer a booking as successful without a confirmation identifier and source URL.
- **latency:** Inspect within 10 seconds after the owner asks; speak a compact receipt within 3 seconds once extraction completes. Calendar/reminder writes are reversible and should happen only after presenting the proposed changes.
- **cost:** <$0.02 typical; extraction and field comparison dominate, with one small model call for ambiguous labels. Browser and calendar operations are deterministic.
- **security:** Confirmation data is private and may include payment or travel identifiers. Redact payment tokens and retain only a short host-keyed claim with 24-hour expiry and provenance; never store page text or screenshots. Detect duplicate confirmation IDs and timezone/currency ambiguity. Do not cancel, refund, or contact a merchant automatically.
- **missing:** A browser completion trigger that can bind the just-finished tab to a job without polling every page; A normalized confirmation schema for dates, amounts, identifiers, cancellation deadlines, and timezone; A reversible calendar/reminder transaction with an owner-visible before/after receipt

### "I have a meeting in 20 minutes—open the relevant logged-in project or customer page, combine it with the matching Calendar event and my local notes, and give me a three-point prep brief on the pendant."
- **useful because:** The browser is the only node that can reach the owner's authenticated project/customer context; the Mac has the calendar and private notes; the relay can rank conflicts and the pendant can deliver a brief while the owner is moving. This is more useful than a generic page reader because it resolves which page and notes belong to this specific meeting.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Cheap background model retrieves and clusters candidate pages/notes; a small synthesis call produces three points and explicitly labels uncertainty. Realtime is used only if the owner asks a follow-up aloud.
- **latency:** Start from the next Calendar event and return within 30 seconds. If page matching is ambiguous, read the candidates and ask one concise question rather than guessing. Read no more than 60 seconds of audio.
- **cost:** <$0.04 per brief; authenticated extraction and local-note retrieval dominate, with synthesis kept to a small context. No screenshot or full page body needs to leave the Mac.
- **security:** Do not persist meeting page text or customer names beyond short-lived host-keyed claims. Respect an empty per-origin configuration until the owner supplies rules; allow a per-job exclusion such as 'don't speak financial or HR content.' Cite each point by page title/event/note source, and never send an email or modify CRM records.
- **missing:** A meeting-to-browser-page resolver using the Calendar title, attendees, and current Safari tabs; A server-side join that can pass only selected claims from browser and local notes into synthesis; A pendant brief packet with source labels and a one-button 'repeat the second point' interaction

### "Check the profile details across my logged-in services against the canonical address and contact details on my Mac, tell me exactly which accounts disagree, and prepare—not submit—the corrections."
- **useful because:** Stale addresses and phone numbers silently break deliveries, billing, account recovery, and emergency contact. The browser is the only surface that can inspect each authenticated account, while the Mac can hold the canonical record and the pendant can summarize discrepancies without making the owner visit every site. This is a cross-origin consistency check, not a generic page read or a scheduled portal briefing.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Use a cheap structured extractor for labeled profile fields and deterministic normalization for postal addresses, phone numbers, and email. Use realtime only for the owner's spoken choice when two canonical values conflict. Never use a generative model to invent a missing value.
- **latency:** Run one requested sweep in under 90 seconds for 3–5 configured origins, with progressive results on the pendant. Prepare correction drafts after comparison, but stop before any save/submit action.
- **cost:** About $0.03–$0.08 per sweep, dominated by authenticated page extraction and normalization; no full-page context needs to reach the expensive model.
- **security:** This touches identity and recovery data. Ship with an empty origin list and require explicit per-origin configuration; redact values in logs and spoken output (for example, last four digits only), retain only a short-lived discrepancy claim with URL provenance, and never store page HTML, screenshots, passwords, or recovery answers. Saving a correction must remain a separate owner-directed action.
- **missing:** A multi-origin browser job that can open configured profile pages and return labeled fields with stable refs; A local canonical-contact record with field-level provenance and conflict resolution; A redacted discrepancy report and reversible per-field fill plan that can be reviewed on the pendant

### "Prepare a support case from the logged-in order or account page: gather the order ID, status, dates, and relevant policy text, combine it with my local notes, draft a short accurate message, and read it to me before sending."
- **useful because:** Support forms are repetitive and easy to get wrong, especially when the evidence is behind a login. Safari can retrieve the authoritative order/account facts, the Mac can add the owner's notes and contact context, and the pendant can let them review the draft hands-free. It reduces copying sensitive identifiers into the wrong field while preserving the owner's control over sending.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Deterministic field extraction and local-note retrieval first; a cheaper model drafts the message constrained to extracted evidence. Realtime only handles spoken edits or reads the final draft. The system must refuse to infer missing order facts.
- **latency:** Produce a draft in 30 seconds or less. Read identifiers partially masked, then offer the complete draft on the Mac for visual review. Never press Send/Submit without a separate explicit instruction.
- **cost:** Roughly $0.02–$0.05 per case; browser extraction and evidence-grounded drafting dominate. Keep the prompt small by passing claims and spans, not page HTML.
- **security:** Order IDs, addresses, and account details must stay local or in short-lived redacted claims with source URLs. Do not persist the support draft by default, do not include credentials or payment data, and show every sentence's evidence source. Sending remains a distinct irreversible operation.
- **missing:** An evidence-bounded browser extractor that returns quoted spans and field provenance; A draft composer that rejects unsupported claims and exposes sentence-level sources; A pendant review protocol supporting masked identifiers, spoken edits, and explicit send handoff

### "Review the connected-app and sign-in permissions visible in my logged-in accounts, compare them with the services I actually use, and give me a prioritized revoke plan without revoking anything."
- **useful because:** Unused OAuth grants and old sign-ins are a quiet account-takeover and privacy risk. The browser can see security pages behind the owner's sessions, the Mac can compare names against installed apps and local records, and the pendant can present a short prioritized list instead of forcing a long security-settings tour.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Use deterministic extraction for provider, app, scope, last-used date, and revoke controls; use a low-cost model only to cluster duplicates and explain risk. Realtime is reserved for spoken questions. No model should decide that a permission is safe to revoke without showing its evidence.
- **latency:** Audit 3–5 explicitly configured origins in under two minutes, with each account reported progressively. Prepare revoke targets, but never click revoke automatically.
- **cost:** Approximately $0.04–$0.10 per audit, mostly authenticated page extraction and deduplication; the final spoken ranking is tiny.
- **security:** Security pages are highly sensitive. Start with an empty origin configuration, keep secrets and tokens out of extraction, redact app identifiers in logs, retain only short-lived claims with provenance, and mask account email addresses on the pendant. Treat revoke as a high-impact mutation requiring a separate owner instruction and provide an undo/recovery note where the service supports it.
- **missing:** A security-settings page adapter that extracts permission rows and stable revoke refs without exposing tokens; A Mac-side inventory join for installed apps and known services, with uncertainty shown rather than guessed; A review queue that presents one permission at a time and records the owner's eventual decision without performing it


## Changes it proposed to its own stack

### `browser-harness` — Add a first-class 'bind current tab' operation: Safari reports the active tab's stable tabId, origin, title, and a privacy-preserving content digest to the local agent; the pendant's next voice request can bind to that tab without navigation or a fragile URL match. Return a short-lived binding token that browser actions, provenance, and the final spoken answer all carry.
- **owner gets:** The owner can say “summarize this,” “fill this,” or “watch this” while looking at a logged-in page and be certain the request targets the page in front of him—not an old tab, a duplicate origin, or whichever tab happened to win a race. It makes authenticated browser work feel immediate and trustworthy.
- effort: Medium: Safari extension active-tab event/reporting, local-agent binding state with expiry, and POST /execute action plumbing; add integration tests for tab switches and closed tabs.  ·  risk: A stale binding could expose the wrong page. Expire tokens quickly, invalidate on tab close/navigation/origin change, and return a visible mismatch instead of acting. Recovery is simply rebinding the current tab; no page data is persisted.
- cost: Negligible API cost; roughly 1–2 KB transient metadata per binding. No hardware cost.  ·  latency: Removes an entire inspection round and typically saves 1–3 seconds; active-tab event delivery should be under 200 ms.
- security: Improves target integrity but introduces a new capability to identify the active authenticated page. Keep URL/title/digest local, redact query strings, and carry the existing short-lived browser retention rules; never capture content until an explicit read action.
- depends on: A resolved browser_list_tabs/current-tab action or extension event endpoint; POST /execute browser action plumbing; Existing browser provenance and redaction rules


## What it asked for

_Nothing._
## Its own summary

Produced four non-duplicate deliverables: (1) authenticated form rehearsal that joins Safari session + Mac sources + pendant diff and stops before submit; (2) post-purchase/booking confirmation reconciliation against Calendar with discrepancy alerts and reminders; (3) on-demand meeting prep combining a logged-in project/customer page with Calendar and local notes; and (4) a browser-harness change that binds the owner's next request to the active Safari tab with an expiring token. Capability discovery now sees Safari online with one tab, but every granted browser wrapper still fails resolver ambiguity (browser_list_tabs vs browser_list_sessions).

**Biggest unknown:** I still need one actually callable browser action path (or a resolver schema that unambiguously selects browser_list_tabs/browser_read_page/browser_navigate) to inspect the live tab and demonstrate authenticated page work. I also need the owner-provided per-origin and content-category rules before automating or speaking any logged-in data; the configuration should remain empty rather than inventing sites or sensitivities.

