# Harness derivation — browser-extension — round 242

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with one real tab currently at https://www.doordash.com (tabId 6516355, Safari 26.5.2, extension 1.2.0); no queued commands.
  - evidence: GET /browser/status returned online=true, tabCount=1, tabUrl=https://www.doordash.com, pendingCommands=0.

## Capabilities it proposed

### "“When I ask ‘what needs my attention?’, check my open authenticated browser tabs and my Mac mail/calendar, rank only urgent or time-sensitive items, and tell me the top three with links and the next action.”"
- **useful because:** This is the system’s highest-value browser use: it combines sessions only Safari can reach with Mac-local mail/calendar and the pendant’s always-available voice. It turns scattered portals into a short actionable briefing instead of making the owner manually inspect each site.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheaper background planner for extraction, deduplication, and ranking; reserve realtime only for the final spoken answer and follow-up questions.
- **latency:** 15–30 seconds for an on-demand sweep; speak partial results as each source completes if one site is slow.
- **cost:** Usually one small planner call plus one realtime response; roughly $0.01–$0.05 depending on page count and extracted text. Browser sessions and Mac data dominate latency, not tokens.
- **security:** Reads authenticated pages and local mail/calendar. Default to claims only (no page bodies), 24-hour browser TTL, provenance URLs, and no screenshots. Ship an empty per-origin configuration; the owner later specifies origins/categories. Never submit or send anything during triage.
- **missing:** A coordinator that fans one request to browser sessions and Mac briefing sources, normalizes deadlines, and deduplicates the same item across them; A stable browser read/snapshot result path exposed to the planner (the current enqueue wrappers are inconsistent); Owner-supplied per-origin/category configuration

### "“Before my next meeting, build me a private briefing from the calendar event, the linked authenticated browser pages, and relevant local files; tell me the people, decisions, unanswered questions, and the exact links to open.”"
- **useful because:** A calendar link often hides the real context behind a login. The Mac knows the event and local files, Safari knows the authenticated project/CRM/wiki pages, and the pendant can deliver a two-minute brief while the owner is walking. No single node can assemble this reliably.
- **path:** mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** Background model gathers and cites facts and produces a compact dossier; realtime is used only if the owner asks follow-up questions aloud.
- **latency:** Prepare asynchronously 5–10 minutes before the event; under 10 seconds to answer a spoken follow-up.
- **cost:** About $0.02–$0.10 per meeting depending on linked pages and file count; browser extraction and context transfer dominate.
- **security:** Calendar titles, local files, and authenticated pages are combined into one temporary dossier. Keep page text out of durable memory; retain only short claims with URLs and a meeting-scoped TTL; show the source for every assertion. Empty per-origin rules remain the default until the owner configures them.
- **missing:** Calendar-event link extraction and a meeting-scoped context object shared between Mac and browser workers; Browser traversal of links from the event with read-only action allowlists; A compact citation-bearing dossier format that the relay can stream to the pendant

### "“I’m looking at this page—tell me what matters, explain any jargon I point to, and compare the visible options. Don’t leave the page or change anything.”"
- **useful because:** This makes the authenticated browser a conversational surface rather than a remote click robot. The owner can ask about a private billing, benefits, travel, or work page from the pendant; Safari supplies the current page, while the relay explains it without exposing the whole page to durable memory.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** A small local/browser extraction pass identifies headings, tables, selected text, and links; realtime handles the low-latency spoken explanation and only requests a larger slice when needed.
- **latency:** 2–5 seconds per question after the initial page snapshot; initial snapshot under 8 seconds.
- **cost:** Approximately $0.005–$0.03 per question, dominated by sending page structure and table text; substantially cheaper than repeatedly sending the whole DOM.
- **security:** Read-only by construction: navigation, click, type, and submit are unavailable in this mode. Keep raw page content in the active job only, redact account numbers before relay transfer, persist no screenshots or HTML, and retain only cited short-lived findings if the owner explicitly asks to remember one.
- **missing:** A reliable browser_read_page/browser_snapshot result that identifies the active tab and supports focused regions or selected text; A page segmentation/redaction stage that sends only the relevant region to the model; Pendant protocol for a short spoken answer plus a source/link reference

### "“Find the earliest appointment in my authenticated healthcare portal that fits my calendar, prefer locations within my travel limit, fill the booking form, and show me exactly what would be submitted.”"
- **useful because:** Today the owner must manually reconcile a private portal’s availability with his calendar and travel constraints. This would make the browser, Mac, relay, and pendant cooperate on a concrete life-admin task while stopping at a reviewable draft rather than silently booking.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a background planner for availability search, calendar conflict checking, and ranking; use realtime only for the owner’s spoken constraints and final concise review.
- **latency:** 30–90 seconds for searching several dates and locations; under 5 seconds to answer a clarification.
- **cost:** Roughly $0.03–$0.15 per search, dominated by authenticated page traversal and calendar reads.
- **security:** Healthcare details and calendar data leave Safari/Mac only for this job. Keep the form draft ephemeral, redact identifiers from model context, retain no page text, and require an explicit final submit action outside the draft workflow. The owner’s empty origin/category configuration must be populated before enabling a real portal.
- **missing:** A browser workflow engine that can iterate availability controls and preserve a field-level draft without submitting; A calendar/travel-constraint query shared between Mac and browser workers; A structured, human-readable pre-submit diff delivered to the pendant and Mac

### "“For this purchase, assemble a return or warranty claim from the retailer page, my order email, and the product files on my Mac; draft the claim with evidence and tell me what is still missing.”"
- **useful because:** The owner currently has to hunt across an authenticated retailer account, mail, and local receipts to prove a claim. This turns the browser’s private session into an evidence collector and gives the pendant a clear checklist without sending a message or uploading anything.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** A background extraction model should normalize order numbers, dates, warranty terms, and evidence; realtime should answer questions and read only the short missing-items checklist.
- **latency:** 20–60 seconds per claim; immediate incremental updates as each evidence source is found.
- **cost:** Approximately $0.02–$0.10 per claim, mostly from extracting and reconciling several sources.
- **security:** Receipts may contain addresses, payment fragments, and serial numbers. Keep evidence local or in an encrypted job capsule, send only redacted claim facts to the model, retain provenance without raw attachments, and never upload or send the draft automatically.
- **missing:** A cross-source evidence joiner for browser pages, Mail, and local files; An attachment-aware but non-persistent claim draft format with missing-evidence validation; A pendant-friendly checklist and secure handoff to the Mac for the owner’s final upload

### "“Audit the private accounts I have open for exposed personal data, find every place I can reduce it, and prepare the deletion or privacy-request forms without submitting them.”"
- **useful because:** No single node can see both authenticated account privacy controls and the owner’s local identity details. The owner would get a concrete, account-specific privacy cleanup plan instead of generic advice, with every form prefilled for review.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a background model to inventory settings and map them to a standard privacy checklist; use realtime for the owner’s preferences and a short spoken summary.
- **latency:** Several minutes for an account-by-account audit; incremental findings should appear within 20 seconds per site.
- **cost:** Roughly $0.05–$0.25 per audit, depending on the number of authenticated origins and forms.
- **security:** This handles highly sensitive identity and account settings. Process page regions locally where possible, redact identifiers before model calls, store only findings and provenance with a short TTL, and stop before any deletion, opt-out, or submission. The owner must explicitly configure which origins and data categories are in scope.
- **missing:** A privacy-control recognizer that can distinguish settings, opt-outs, deletion requests, and irreversible actions across differing sites; A cross-origin audit report that maps each finding to an actionable draft form; A secure field-level redaction and review surface shared by Safari, Mac, and the pendant


## What it asked for

_Nothing._
