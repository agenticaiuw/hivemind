# Harness derivation — browser-extension — round 250

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension currently has two open tabs: authenticated-looking DoorDash order URL and active YouTube video; browser_list_tabs and browser_read_page execute successfully through POST /execute.
  - evidence: POST /execute {actions:[{type:'browser_list_tabs'}]} returned tabIds 6516355 and 7975357; prior result log included successful browser_read_page on tab 7975357.

## Capabilities it proposed

### "“Keep an eye on this checkout and tell me if the total, delivery time, or substitutions change before I buy.”"
- **useful because:** Shopping pages change underneath the owner, especially after address, inventory, or delivery updates. A browser session can observe the private checkout while the relay compares structured values and the pendant gives a short alert; this catches a material change without ever placing the order. It is more useful than a generic page summary because it watches the exact commitment the owner is about to make.
- **path:** browser (read-only snapshots of the active checkout tab at an owner-chosen interval) → relay (structured extraction and diffing of total, fees, ETA, item/substitution lines) → pendant (spoken alert and offline_alert_inbox entry) → mac-bridge (keeps Safari awake and hands the active tab/session to the watcher)
- **model tier:** Cheaper background model or deterministic DOM extraction for each poll; realtime only when a material change is detected and needs to be spoken.
- **latency:** Poll every 30–60 seconds while armed; alert within one polling interval, with no voice-model call when nothing changed.
- **cost:** Roughly $0.001–$0.01 per poll for structured extraction, plus $0.01–$0.03 only on a detected change; browser polling dominates duration, not tokens.
- **security:** Owner explicitly arms the watcher for the current tab and can stop it. Read-only action allow set: browser_read_page/browser_snapshot/browser_wait_for only; no click, type, or submit. Do not save page text or payment data; retain only a short diff claim with existing browser TTL/provenance. Alert wording must redact card/address details.
- **missing:** A browser watcher job that can poll one tab and cancel cleanly; Checkout-specific structured diff fields with conservative redaction (total, ETA, item state, substitutions) rather than site constants; A relay-to-pendant alert path that includes a change summary and stop/disable control

### "“Before I place this order, check the merchant’s policy and this checkout and tell me the cancellation deadline, mandatory fees, and anything that conflicts.”"
- **useful because:** The owner often needs a cross-page answer, not a summary of either page: checkout shows the actual total while a policy/help page contains cancellation and fee conditions. The browser is uniquely able to read both private tabs; the relay can reconcile them and the pendant can speak the few material conflicts while the owner still has a chance to back out.
- **path:** browser (read-only extraction from the checkout tab plus the merchant policy tab, without clicking submit) → relay (cross-page claim matching, conflict detection, and short evidence-linked answer) → pendant (spoken risk summary and optional alert inbox item) → mac-bridge (preserves the two-tab session and can open the policy URL if the owner asks)
- **model tier:** Background model for extraction and claim comparison; realtime only for the owner's question and final spoken answer.
- **latency:** 5–10 seconds for two ordinary pages; return a partial result if one page is slow rather than blocking the voice turn.
- **cost:** Approximately $0.03–$0.12 per check, dominated by two page extractions and comparison context; no recurring cost after the one-shot check.
- **security:** Explicitly read-only; never click checkout controls or submit. Keep payment/address values out of model context where possible via DOM redaction. Persist no page body; retain only short claims with URL provenance and existing 24-hour browser TTL. Owner supplies any per-origin rules later; configuration ships empty.
- **missing:** A multi-tab browser action that addresses named tabs rather than assuming only the active tab; A claim comparator that distinguishes policy text from the actual order state and marks uncertainty when they disagree; A spoken citation format that can say which tab/URL supports each material claim

### "“I bought this online—find the receipt, tell me the return/warranty deadlines, and put reminders on my Mac before each deadline.”"
- **useful because:** A purchase is not finished when the checkout closes. The browser can reach the owner’s authenticated order/receipt, extract the specific return and warranty dates, and the Mac can turn those dates into reminders while the pendant speaks only the key deadlines. This joins a private web session, an acting machine, and an always-available wearable in a way none can do alone.
- **path:** browser (read the authenticated order/receipt and, if needed, the merchant policy page) → relay (identify the purchased item, normalize dates, distinguish return window from warranty, and cite the source) → mac-bridge (create dated reminders with item, deadline, and source URL) → pendant (speak the deadline summary and later deliver an offline alert if a reminder is due)
- **model tier:** Background model for receipt/policy extraction and date normalization; realtime only for the owner's request and concise confirmation.
- **latency:** 10–20 seconds for the initial extraction and reminder creation; later alerts are local/scheduled and do not require realtime inference.
- **cost:** About $0.05–$0.20 per purchase, mostly two-page extraction and date reconciliation; reminder delivery is negligible.
- **security:** Never expose full receipt, address, or payment details in speech or long-term memory. Persist only item label, deadline, source host/URL, and confidence with existing browser TTL/provenance. Creating reminders is a reversible local action with receipts; if a deadline is ambiguous, create no reminder and report the ambiguity rather than guessing.
- **missing:** A browser-to-reminder workflow that can carry evidence capsules into a dated reminder; Receipt/policy extraction templates that recognize return, exchange, warranty, and final-sale language without hardcoded merchants; A durable deadline scheduler that can hand reminder events to offline_alert_inbox

### "“Check that this booking matches my calendar and tell me exactly what differs—dates, times, address, names, and cancellation terms.”"
- **useful because:** Today the browser can read a private booking and the Mac can read calendar data, but no single capability reconciles them. This prevents missed travel, duplicate bookings, and nonrefundable mistakes by comparing two independently sourced records and speaking only the discrepancies through the pendant.
- **path:** browser (read the authenticated booking/itinerary and its policy page) → mac-bridge (read the matching calendar event and timezone/location context) → relay (normalize dates, timezones, names, addresses, and cancellation clauses; produce a discrepancy report) → pendant (short spoken result and an offline alert if a material mismatch is found)
- **model tier:** Background model for extraction and record reconciliation; realtime only for the owner's request and concise spoken discrepancies.
- **latency:** Under 15 seconds for ordinary booking and calendar records; speak a provisional mismatch immediately and refine policy details asynchronously.
- **cost:** $0.04–$0.15 per check, dominated by private-page extraction and reconciliation; no recurring cost unless the owner asks to recheck.
- **security:** Read-only browser and calendar access; never alter or cancel a booking. Do not retain itinerary bodies, names, or addresses. Store at most short-lived mismatch claims with source provenance and existing browser TTL. Redact passport/payment fields before speech.
- **missing:** A cross-surface record-reconciliation job that can receive browser evidence and Mac calendar data in one context; Extractors for itinerary entities and cancellation clauses with timezone normalization; A provenance-aware discrepancy result that the pendant can summarize without exposing the underlying records

### "“Compare this bill with the last one, explain the biggest increase using the statement or usage pages, and remind me if I need to act.”"
- **useful because:** A private bill is not useful as an isolated page: the meaningful answer is the change from the prior statement plus the provider's explanation and deadline. The browser can reach the authenticated statement/usage pages, the relay can compare short-lived findings, the Mac can schedule a follow-up, and the pendant can deliver only the actionable difference.
- **path:** browser (read the current statement, prior statement, and usage/detail pages in the authenticated session) → relay (normalize line items, detect material changes, and rank explanations and deadlines) → mac-bridge (create a dated follow-up reminder only when an action or dispute deadline is present) → pendant (speak a compact amount/change/action summary and retain it in offline_alert_inbox)
- **model tier:** Background model for statement extraction and comparison; realtime only for the owner's question and final alert wording.
- **latency:** 10–20 seconds for a three-page comparison; later deadline alerts are scheduled and independent of realtime inference.
- **cost:** $0.05–$0.20 per comparison, mainly page extraction and line-item matching; reminders and alerts are negligible.
- **security:** Never speak account numbers, full addresses, or payment details. Retain only capped, 24-hour browser claims and source URLs; do not store statement text or screenshots. Read-only browser actions; creating a reminder is the only local mutation and must carry an undo receipt.
- **missing:** A multi-page financial-statement comparator with line-item identity and confidence handling; A safe rule for deciding when a change is material enough to alert, exposed as owner-editable configuration rather than a hardcoded taxonomy; A deadline-aware bridge from browser evidence into reminders and offline alerts

### "“Use this order and the merchant policy to draft a support dispute, attach only the relevant facts, and leave it unsent for me to review.”"
- **useful because:** The browser can see the private order and policy while the Mac can prepare a real support draft, but today the owner must manually shuttle facts between them. This creates a grounded, reviewable draft without sending anything: the pendant summarizes what will be claimed, Safari supplies evidence, and the Mac leaves the final communication in a reversible draft state.
- **path:** browser (read the authenticated order, receipt, delivery record, and applicable policy) → relay (extract only relevant facts, identify the requested remedy, and generate a concise evidence-backed draft) → mac-bridge (create a support email/message draft with source links, never send it) → pendant (read the proposed claim and ask the owner whether to keep, revise, or discard the draft)
- **model tier:** Background model for evidence selection and drafting; realtime for the owner's dictation and spoken preview.
- **latency:** 15–30 seconds for a normal order; draft creation should return a receipt and remain editable while the owner reviews it.
- **cost:** $0.06–$0.25 per draft, dominated by reading multiple authenticated pages and composing grounded text; no cost for leaving an unsent draft.
- **security:** No send/submit action. Include only order facts needed for the dispute; redact payment, full address, and unrelated account data. Store the draft in the Mac mail app's normal draft store, with a browser evidence capsule and undo/delete receipt; do not persist page HTML or screenshots.
- **missing:** A browser-evidence-to-draft composer that carries citations and selected claims, not raw page text; A Mac action that creates a draft across the owner's mail/support client and returns an editable receipt; A pendant review protocol for preview, revise, discard, and explicit later send as separate actions


## What it asked for

_Nothing._
## Its own summary

Safari is live again with two real tabs, and I verified browser_list_tabs plus browser_read_page through POST /execute. I recorded three non-duplicate capabilities: (1) a read-only cross-tab checkout/policy conflict checker (the most valuable of this round because it catches hidden fees and cancellation traps before commitment), (2) an armed checkout watcher that alerts the pendant when totals, ETAs, or substitutions materially change, and (3) post-purchase receipt/policy extraction that creates return and warranty reminders on the Mac and later delivers them through the pendant. I also recorded the live tab finding and informed unified. What I still need is implementation of multi-tab targeting, structured claim/date extraction, a cancellable polling watcher, and a browser-evidence-to-reminder/alert handoff; no further browser access grant is needed because direct POST /execute now works.

**Biggest unknown:** Whether the existing browser provenance and reminder internals already expose enough evidence linkage to implement these workflows without new routes; route inventory summaries are broad and the browser wrapper resolver remains ambiguous, although direct POST /execute is operational.

