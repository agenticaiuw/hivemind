# Harness derivation — browser-extension — round 217

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-tab-targeting** — Safari is online with two tabs (YouTube active tabId 3186198; Google News tabId 5688537), but POST /execute browser_read_page supplied tabId 5688537 and returned the active YouTube page/tabId 3186198. The command result's session also pinned the active tab.
  - evidence: POST /execute / browser_list_tabs at 2026-08-08T23:59:10Z listed both tabs; POST /execute browser_read_page tabId=5688537 at 23:59:15Z returned tabId=3186198 and YouTube content.

## Capabilities it proposed

### "“What am I looking at in Safari? Read me the important part, and if there’s an obvious deadline tell me.”"
- **useful because:** This makes the pendant a hands-free lens onto the owner’s authenticated browser. A spoken question becomes an active-tab read, targeted extraction, and concise audio answer; no copying URLs or switching devices. It is useful for dense dashboards, tickets, receipts, and pages whose contents public search cannot reach.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime for the short spoken turn and final answer; a cheaper background extraction model handles page text before the realtime model speaks.
- **latency:** 2–6 seconds after the question, dominated by the extension round trip and page extraction; return a partial “I’m reading it” cue if extraction exceeds 1.5 s.
- **cost:** Usually one realtime turn plus a small extraction call; roughly $0.01–$0.05 per use depending on page length. Do not resend the whole page to the realtime tier—send only the selected passages and deadline candidates.
- **security:** The browser session is the authority and may contain secrets. Read only the addressed active tab, retain no page body, and attach URL/title/hash provenance to the answer. Speak only the extracted answer, not arbitrary hidden fields. The owner’s existing maximum-access policy means this is not a confirmation gate, but the system must stop at reading and never click or submit.
- **missing:** A reliable action:browser_read_page invocation that preserves the requested active tabId (the live probe returned the active YouTube tab even when another tabId was supplied); A pendant-to-browser query correlation carrying the active tab, question, and expiration; A page-content selector/extractor that returns relevant passages and deadline candidates without persisting HTML

### "“Keep an eye on this logged-in page until Friday. If the status changes or a deadline is within 48 hours, tell me on the pendant; otherwise stay quiet.”"
- **useful because:** A one-time authenticated read is not enough for portals and booking/account pages that change after the owner leaves the desk. The browser holds the session, the relay can poll while the Mac sleeps, and the pendant’s offline alert inbox can deliver a short warning even after the browser link drops. The owner gets attention only when the watched condition changes.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Cheaper background model for scheduled snapshots, normalization, and semantic diff; realtime is used only to phrase an urgent spoken alert or answer a follow-up.
- **latency:** A scheduled check every 15–60 minutes is acceptable; alert delivery within one polling interval. Setup should answer in under 5 seconds.
- **cost:** One small extraction/diff call per check, roughly $0.001–$0.02 depending on page size; substantially cheaper than repeatedly sending full pages to realtime. Store only a compact state hash and extracted claims.
- **security:** The owner must supply an explicit per-origin watch rule; ship configuration empty rather than guessing sites or sensitive categories. Never persist page HTML, screenshots, or credentials. Claims need host, URL, timestamp, and 24-hour browser-fact expiry; alert text should omit values classified as never-speak. Expiry, pause, and delete must be visible and easy to invoke.
- **missing:** A durable browser watch scheduler that can re-address a specific tab/session after Safari tab IDs change; A semantic-diff/condition evaluator for page claims and deadlines, with host-scoped short-lived state; A relay-to-pendant alert delivery path that queues and deduplicates watch alerts through offline_alert_inbox; Owner-facing watch creation and cancellation, including an explicit empty per-origin policy configuration

### "“Before I submit this booking, check the details against my calendar, tell me the total and cancellation terms, and draft any reminder I’ll need.”"
- **useful because:** The browser can see the checkout fields and logged-in terms that the Mac planner cannot, while the Mac can inspect the owner’s calendar and create a reversible reminder. The pendant gives a fast spoken preflight before money or an irreversible submission. This prevents wrong dates, hidden fees, and missed cancellation windows without asking the owner to transcribe anything.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Background model extracts structured fields and terms from the page; a cheap deterministic checker compares dates against calendar. Realtime is reserved for the owner’s spoken question and the compact final preflight.
- **latency:** 5–12 seconds for extraction plus calendar comparison; provide a spoken progress cue after 2 seconds. Never submit automatically.
- **cost:** Roughly $0.01–$0.06 per preflight, dominated by one page extraction and terms summarization; calendar comparison should be local and nearly free.
- **security:** Checkout pages contain payment and personal data. Use an explicit per-action allow set containing read/extract only; redact card numbers and tokens before model handoff. Show the exact fields, total, dates, and reminder text before any mutation. Creating a local reminder is reversible, but submitting the booking, sending a message, or clicking final purchase remains outside this capability.
- **missing:** A browser structured extractor for checkout fields, totals, dates, and cancellation clauses that does not expose payment secrets; A calendar availability/deadline comparison contract between browser results and the Mac planner; A single preflight receipt that records source URL, extracted fields, conflicts, and proposed reminder, while retaining no page body; A pendant response mode that can speak the preflight and let the owner request a correction without losing the browser context

### "“Build me a complete support case for this order: gather the relevant order and policy details from the logged-in site, find the matching receipt on my Mac, and draft the message—but do not send it.”"
- **useful because:** Today the browser can see the authenticated order while the Mac can see local receipts, but neither can assemble a defensible case across both sources. This would turn a frustrating support interaction into a ready-to-review evidence packet, delivered audibly through the pendant and editable on the Mac.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model performs document matching, timeline construction, and draft composition; realtime is only for the owner’s short instruction and spoken confirmation summary.
- **latency:** 15–45 seconds for a case packet, with progress updates. The owner should be able to review the draft on the Mac while the pendant summarizes it.
- **cost:** Approximately $0.03–$0.15 per case, dominated by extracting and comparing several documents; local receipt indexing should be reused rather than re-sent.
- **security:** Order pages and receipts may contain addresses, payment fragments, and private correspondence. Keep full documents local where possible, pass only cited excerpts to the model, retain source URLs and file paths as provenance, and never send the draft. The owner explicitly reviews before any external communication.
- **missing:** A cross-surface evidence-join job that can correlate an authenticated browser order with local files using order number, merchant, amount, and date; A citation-preserving case-packet format with redaction of payment and address fields; A Mac review surface that shows the draft and evidence side by side while the pendant gives only the summary; A durable handoff from browser extraction to local file search without persisting page HTML

### "“My trip changed—check the logged-in travel page, compare every option with my calendar and local time, and put the best two rebooking plans on the pendant. Don’t purchase anything.”"
- **useful because:** Travel disruptions require simultaneous access to a private booking session, calendar commitments, local files such as an itinerary, and immediate wearable delivery. A public search or Mac-only agent cannot see the authenticated booking controls and terms; the pendant can warn the owner while they are away from the desk.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model normalizes flight/train options and restrictions; deterministic local checks handle time zones and calendar conflicts; realtime speaks the two ranked plans and answers follow-up questions.
- **latency:** 30–90 seconds for a full comparison, then under 3 seconds for follow-up questions while the browser session remains warm.
- **cost:** Roughly $0.05–$0.25 per disruption, depending on the number of options and terms; use compact structured options rather than resending whole booking pages.
- **security:** Travel pages expose identity, itinerary, and payment data. Extract only the fields needed for comparison, redact loyalty numbers and payment details, expire the working set after the decision, and never click a purchase or final-change control. The owner can later explicitly choose a plan for a separate action.
- **missing:** A multi-page authenticated travel extractor that follows itinerary, availability, fare-rule, and seat pages while retaining the booking session; A time-zone-aware constraint solver joining browser options, Mac calendar, and local itinerary files; A pendant alert payload that can present two compact alternatives and preserve the selected option for later review; A robust irreversible-boundary detector for travel sites whose final controls vary by origin

### "“Prepare this application using the information already on my Mac, but show me every field that would be filled and leave the form unsubmitted.”"
- **useful because:** This bridges the browser’s authenticated form and the Mac’s local records without making the owner copy sensitive details manually. It is especially valuable for repetitive applications and renewals: the system can detect missing, stale, or conflicting values, fill only after showing a field-level diff, and leave the owner in control of submission.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** A background model maps form labels to local records and flags ambiguity; realtime gives the owner a short spoken summary. Deterministic validation handles dates, formats, and required fields.
- **latency:** 10–30 seconds for a typical form; field-level preview should appear progressively, with ambiguous fields held back rather than guessed.
- **cost:** Approximately $0.02–$0.10 per form, mostly for schema-to-record matching. Sensitive local values should be processed on the Mac and not sent to the cloud model.
- **security:** Forms may contain identity, financial, health, or legal information. Use a per-field provenance and redaction ledger, never persist page text or entered secrets, and make every fill undoable. Filling is reversible; submission, upload, signature, and payment must remain untouched until separately requested.
- **missing:** A browser form-schema and field-state extractor that distinguishes editable fields from submit/sign/upload controls; A local Mac record matcher with per-field provenance, freshness, and ambiguity reporting; A reversible browser-fill transaction with a complete before/after receipt and clear rollback; A pendant-friendly approval summary that can identify fields by label without speaking their sensitive values aloud


## What it asked for

_Nothing._
