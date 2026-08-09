# Harness derivation — browser-extension — round 241

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before I pay this invoice, check that the bank/payment page, the invoice PDF on my Mac, and the vendor details in my contacts agree; tell me exactly what differs and prepare—but do not submit—the payment.”"
- **useful because:** This catches changed bank coordinates and invoice fraud at the moment it matters. The browser alone sees the authenticated payment page, the Mac alone sees local documents and contacts, and the pendant is the only place that can deliver a concise warning while the owner is away from the screen.
- **path:** browser-extension → mac-planner → relay-realtime → offline_alert_inbox
- **model tier:** background for extraction and comparison; realtime only to explain a mismatch over voice
- **latency:** 20–45 seconds for page/document comparison; under 2 seconds to speak an already-computed warning
- **cost:** One background planner call plus cheap local extraction; roughly $0.02–$0.10 depending on PDF/OCR size. No model call for matching exact account/name fields.
- **security:** Payment and invoice fields leave the Mac only as redacted structured values, not whole pages. Never persist account numbers or page text; retain only a short-lived mismatch claim and provenance. The action must stop before submit and expose the exact pending payload.
- **missing:** structured local PDF/contact extraction with field-level redaction; a cross-surface comparison job and mismatch schema; a browser form-fill preview receipt that can be discarded

### "“I’m on a website with a deadline or appointment—turn the exact date, timezone, cancellation rules, and required next step into a calendar/reminder plan, check it against my Mac calendar, and warn me on the pendant if there is a conflict.”"
- **useful because:** Websites routinely hide deadlines and timezone/cancellation details that generic calendar access cannot see. This joins authenticated browser state with the Mac calendar and makes the result audible and durable on the worn device, so a deadline is not lost when the tab closes.
- **path:** browser-extension → mac-planner → relay-realtime → offline_alert_inbox
- **model tier:** background extraction and timezone normalization; realtime only for the owner's follow-up question
- **latency:** 10–20 seconds after the owner asks; alert delivery should be immediate once a conflict is found
- **cost:** Usually one small extraction/classification call, about $0.01–$0.04; exact date parsing and calendar conflict detection are local.
- **security:** Persist only normalized event fields and source URL, never page HTML or full appointment text. Keep the reminder undoable and show the proposed title/time before creating it. Browser-origin rules remain explicit configuration rather than hardcoded sites.
- **missing:** calendar read/conflict query exposed to the cross-surface planner; timezone/cancellation field extractor for arbitrary authenticated pages; a pendant alert payload that includes deadline, source, and undo token

### "“Check the security alert I’m looking at: determine whether it is a real account event or a phishing page, compare its time/device/location with my Mac’s recent activity, and if it looks real put a short urgent alert on my pendant with the safest next step—without clicking any remediation link.”"
- **useful because:** A logged-in security page is uniquely available to the browser agent, while the Mac can provide local activity evidence and the pendant can interrupt the owner even after Safari is closed. It turns a confusing alert into a bounded decision without following an attacker-controlled link.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → offline_alert_inbox
- **model tier:** background for page extraction and evidence correlation; realtime only if the owner asks follow-up questions
- **latency:** Under 30 seconds for an initial verdict; urgent pendant delivery under 2 seconds after classification
- **cost:** One small classifier/correlation call, roughly $0.02–$0.08; local timestamps and domain checks are deterministic.
- **security:** Treat page content as untrusted input. Never navigate to remediation URLs, enter credentials, or persist page text. Store only a short-lived verdict, domain, timestamp, and evidence URLs. Require an explicit owner request before any account mutation.
- **missing:** local Mac activity evidence provider (recent login/device/network events); browser URL/domain and link-target extraction with no navigation; a security-alert severity route into offline_alert_inbox; evidence-aware verdict receipts visible to the owner

### "“Compare the coverage or subscription plan I’m viewing in my logged-in browser with the plan document on my Mac; identify exclusions, renewal traps, and missing benefits, then make a short question list I can take to the provider.”"
- **useful because:** The owner cannot get a trustworthy comparison today because the browser can see the current authenticated offer while the Mac can see the locally stored contract, but neither surface can join those sources and produce a clause-level comparison. This could prevent costly renewal or coverage mistakes without making any account change.
- **path:** browser-extension → mac-planner → relay-realtime
- **model tier:** Background model for clause alignment and concise explanation; realtime only when the owner asks follow-up questions aloud.
- **latency:** 30–90 seconds for two documents/pages; under 2 seconds for follow-up answers from the extracted comparison.
- **cost:** About $0.05–$0.25 per comparison depending on PDF length; deterministic local parsing should handle dates, prices, and headings before model work.
- **security:** Send only extracted clauses and redacted figures, never whole authenticated pages or account identifiers. Store no contract text by default; retain an expiring comparison receipt with source URLs and document names. Never click enrollment, renewal, or cancellation controls.
- **missing:** a redacted local-document clause extractor available to the cross-surface planner; a browser-to-local-document comparison job with clause/source alignment; an expiring, user-visible comparison receipt and deletion action

### "“If my airline or hotel page shows a cancellation or major change, compare the available alternatives with my calendar and local trip documents, tell me the real consequences, and prepare the best rebooking choice without confirming it.”"
- **useful because:** Today the browser can see the authenticated reservation but cannot reason against the owner’s calendar and saved itinerary as one task. During a disruption, a spoken ranked choice and a prepared-but-unsubmitted rebooking is materially more useful than a generic alert.
- **path:** browser-extension → mac-planner → relay-realtime → offline_alert_inbox
- **model tier:** Background model for itinerary reconciliation and ranking; realtime for the owner’s urgent spoken choice.
- **latency:** 15–40 seconds after a disruption is detected; urgent pendant alert within 2 seconds once a ranked option exists.
- **cost:** Roughly $0.03–$0.15 per incident; dates, durations, and calendar conflicts should be parsed locally.
- **security:** Treat airline/hotel pages as untrusted. Do not accept upsells, payment changes, or cancellation links automatically. Persist only itinerary IDs, times, and a short-lived recommendation; redact loyalty and payment data. Stop before final confirmation.
- **missing:** reservation/itinerary schema shared by browser and calendar readers; availability and conflict ranking across authenticated options and local documents; a reversible rebooking form-fill preview with a clear final payload


## Changes it proposed to its own stack

### `browser-harness` — Add an explicit ‘active-tab vs pinned-session’ resolution mode to browser jobs. When a request refers to “this page/what I’m looking at,” bind to Safari’s active tab (currently DoorDash); when it names a saved task, bind to its pinned session (currently USPS). Every read receipt should include the resolved tab title, origin, and whether the choice was active or pinned, and ambiguous references should return the candidate tabs instead of silently using the default USPS session.
- **owner gets:** It prevents the most dangerous browser failure: answering from a stale authenticated tab while the owner is looking at a different account or order. The owner gets the answer about the page actually in front of them and can see exactly which site was read.
- effort: Medium: resolver parameter, active-tab lookup, receipt metadata, and a small ambiguity response; browser extension already reports active tab and tab list.  ·  risk: A stale active tab could be selected for vague requests; mitigate by showing title/origin before any mutation and retaining the existing pinned-session path for named jobs. Recovery is simply rerunning with an explicit tab/session.
- cost: Negligible API cost; one tab-list/heartbeat lookup. No new hardware cost.  ·  latency: Adds roughly 1–2 seconds for active-tab resolution.
- security: Improves origin correctness and auditability; does not add an origin allowlist. Continue existing 24-hour, claim-only browser retention.
- depends on: POST /execute browser_list_tabs; GET /browser/status; GET /browser/sessions; browser receipt provenance


## What it asked for

_Nothing._
## Its own summary

Fresh browser discovery succeeded: Safari is online with 5 tabs and an active DoorDash tab; the saved default browser session is still pinned to a different USPS tab. I recorded four non-duplicate items. The most immediately useful is active-tab versus pinned-session resolution with title/origin receipts, preventing the system from answering about the wrong authenticated page. I also recorded: cross-surface invoice/payment discrepancy checking; deadline extraction plus calendar-conflict alerts; and security-alert/phishing triage correlated with Mac activity and delivered through the pendant inbox.

**Biggest unknown:** The remaining product gaps are implementation gaps, not browser access: a field-level redacted extractor for local PDFs/contacts and Mac activity, an active-tab resolver in the browser harness, and cross-surface job wiring into reminders and offline_alert_inbox. I do not need another browser enqueue wrapper; POST /execute is live and successfully listed the real tabs.

