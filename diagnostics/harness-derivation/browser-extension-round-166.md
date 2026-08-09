# Harness derivation — browser-extension — round 166

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — Safari extension is online with 9 tabs, including an authenticated Gmail inbox and active X tab; POST /execute successfully executed browser_list_tabs and returned command receipts.
  - evidence: GET /browser/status returned online=true, tabCount=9; POST /execute browser_list_tabs returned tab IDs and titles at 2026-08-08T02:29:08Z.

## Capabilities it proposed

### "“What am I looking at right now, and what do I need to do?” (while a logged-in Safari page is open)"
- **useful because:** This is the highest-value browser-only interaction: the pendant can turn a private page that no cloud search can access into a concise, spoken, actionable answer without making the owner describe or copy anything. The browser reads the active tab, the relay-realtime model summarizes it, and the Mac can optionally cross-check local calendar/reminders before speaking.
- **path:** pendant → browser-harness → relay-realtime → mac-planner
- **model tier:** Realtime for the short spoken summary; cheaper background model only if the page is long and needs extraction before the turn.
- **latency:** 2–6 seconds for a normal page; up to 15 seconds for a long authenticated dashboard.
- **cost:** Usually one realtime turn plus a browser extraction; roughly $0.01–$0.05 depending on extracted page length. No raw page text needs persistent storage.
- **security:** The page text leaves Safari for the relay only for this request. Per-origin configuration must be explicit and start empty: read/extract/redact/never-store plus categories that may or may not be spoken. Never include hidden form fields, tokens, or passwords in the extraction. If a follow-up action is suggested, stop at a preview rather than silently submitting.
- **missing:** A voice intent that targets the active browser tab; A bounded browser_snapshot/browser_read_page extraction contract with secret redaction; Owner-supplied per-origin and spoken-category policy

### "“Compare these private documents with the public web and tell me which option I should choose.”"
- **useful because:** The browser can read documents and dashboards behind the owner's logins while web_search covers public facts and the Mac can inspect local files. A single evidence pack with source labels and contradictions is substantially more useful than asking the owner to export private pages or manually reconcile tabs. The pendant delivers the decision in a short spoken answer and can leave a resumable capture.
- **path:** pendant → browser-harness → relay-realtime → mac-planner → relay-realtime
- **model tier:** A cheaper background synthesis model handles the multi-source comparison; realtime is used only to turn the final recommendation into a brief interactive spoken answer.
- **latency:** 10–30 seconds for 3–8 sources; immediately speak progress if extraction takes longer.
- **cost:** About $0.03–$0.20 depending on document size, dominated by synthesis tokens. Store source URLs, timestamps, and short quoted evidence rather than full private pages by default.
- **security:** Each source must carry origin, tab title, timestamp, and whether it is authenticated. The owner's per-origin policy controls extraction and persistence; ship empty rather than guessing sites. Redact credentials, personal identifiers, and hidden fields before synthesis. Recommendations must distinguish facts from model judgment.
- **missing:** A browser-to-relay evidence manifest with source provenance and redaction; A bounded multi-source extraction orchestrator; Owner-configured private-origin rules

### "“Watch my authenticated accounts for a real security or payment anomaly, and alert me on the pendant with the evidence.”"
- **useful because:** Public monitoring cannot see the owner's logged-in account pages. A browser watcher can compare sanitized semantic snapshots of selected pages (for example, a new sign-in, changed payout destination, or unexpected order), while the relay correlates timestamps across tabs and the Mac's local mail/calendar. The pendant's offline alert inbox makes the warning available even after Safari or the link goes away.
- **path:** browser-harness → relay → mac-planner → pendant
- **model tier:** Cheap scheduled/background extraction and anomaly classification; realtime only when the owner asks “what changed?” or needs a spoken explanation.
- **latency:** Polling cadence chosen per origin (5 minutes to daily); alert delivery under 10 seconds after a detected change.
- **cost:** Roughly $0.01–$0.10 per watched origin per day, mostly page extraction and comparison; hashes and redacted diffs can avoid retaining page text.
- **security:** This must be opt-in per origin and category, with an explicit never-store option. Never auto-click recovery, payment, or account-change controls. Alert payloads should contain only the minimum evidence and expire locally. The owner must supply the first origins and what counts as speakable.
- **missing:** A durable browser page-watch scheduler that can reuse existing Safari sessions; Semantic diffing that ignores ads/timestamps/layout churn; Anomaly-to-offline_alert_inbox delivery path and owner policy editor

### "“Fill out this form from what I just told you, then read me the exact final values before anything is sent.”"
- **useful because:** The browser is uniquely able to operate the owner's existing authenticated forms, while the pendant is a practical review surface away from the desk. The system can fill reversible fields, show a compact field-by-field diff, and speak the exact payload; the owner can correct it by voice or use the button to authorize the final submit. This turns tedious browser work into a safe hands-free workflow without pretending that a draft is already sent.
- **path:** pendant → browser-harness → relay-realtime → mac-planner
- **model tier:** Realtime for field clarification and the final spoken read-back; a cheaper model can map dictated answers to form labels and detect missing required fields.
- **latency:** 3–8 seconds per fill/review cycle, with no time limit while waiting for the owner’s review.
- **cost:** About $0.01–$0.08 per form, dominated by field extraction and spoken review; no page body needs to be persisted after completion.
- **security:** Never expose passwords, payment numbers, or hidden fields in speech or logs. Per-origin policy must specify which field categories may be filled and spoken. The browser should stop before irreversible submit and provide a cryptographic/action receipt; the owner’s explicit confirmation is the only transition to submit.
- **missing:** Form semantic extraction and stable field references across navigation; A pendant confirmation/correction protocol tied to one browser command; Redaction of sensitive field values in receipts and logs

### "“Audit my logged-in services for subscriptions I no longer use, collect the cancellation and refund rules, and prepare a private cleanup plan.”"
- **useful because:** Today the owner must remember every service, find each account, and manually compare renewal dates and cancellation terms. A browser agent with the owner’s existing sessions could perform a one-time, origin-by-origin audit, distinguish active commitments from merely advertised plans, and return a prioritized cleanup list without canceling anything. This is materially different from generic page reading: it produces a normalized cross-account inventory and identifies deadlines.
- **path:** browser-harness → relay-realtime → mac-planner → pendant
- **model tier:** Use a cheaper background model for extraction and normalization; use realtime only when the owner asks follow-up questions or wants the top few actions spoken.
- **latency:** Several minutes for an audit of 3–5 explicitly configured origins; spoken results should begin within 5 seconds of each origin completing.
- **cost:** Approximately $0.05–$0.40 per audit, dominated by authenticated page extraction and normalization. Persist only service name, renewal date, price, policy citation, and source timestamp—not page bodies.
- **security:** The owner must explicitly provide the origins and choose whether financial details may be spoken or stored. Do not infer subscriptions from arbitrary tabs. Never click cancellation or retention offers; generate a reviewable plan and exact links instead. Redact account identifiers and payment details.
- **missing:** A multi-origin subscription schema and deduplication layer; Origin-scoped traversal rules for account/billing pages; A private report format with policy citations and expiration timestamps

### "“Build the evidence packet for this charge and tell me whether I have a credible dispute before I contact anyone.”"
- **useful because:** When a charge, delivery, or service failure is disputed, the facts are split across authenticated order pages, email threads, receipts, shipping history, and terms. No single current node can assemble that private chronology. The system should collect only the relevant records, construct a dated timeline with quoted evidence and gaps, and produce a draft packet the owner can inspect—without sending a complaint or exposing unrelated inbox content.
- **path:** browser-harness → mac-planner → relay-realtime → pendant
- **model tier:** Background model for document retrieval, deduplication, and timeline construction; realtime for a short verdict and questions about missing evidence.
- **latency:** 2–5 minutes for a normal case; provide incremental “receipt found / timeline built” status on the pendant.
- **cost:** Roughly $0.10–$0.75 per case, primarily document extraction and synthesis. Store hashes, source links, and selected quotations rather than full inbox or page exports.
- **security:** Search must be narrowly scoped to the named merchant/order/date range. Payment numbers, unrelated messages, and authentication artifacts must be redacted. The packet is private and expiring by default. Never send, upload, or submit the dispute; show the exact destination and draft first.
- **missing:** Cross-origin, query-bounded retrieval over authenticated tabs; A citation-preserving timeline/packet generator; An ephemeral local export format (PDF/HTML) with redaction and expiry

### "“When I am on a private dashboard, explain what changed since my last visit and show me only the decisions that need me.”"
- **useful because:** A normal page summary repeats everything and a generic watcher only reports raw differences. This capability would maintain a per-origin, owner-approved semantic baseline—labels, amounts, status transitions, deadlines—and suppress harmless layout or advertising churn. It would let the owner revisit a complex private dashboard and immediately hear the consequential changes, with a side-by-side browser view available for verification.
- **path:** browser-harness → relay-realtime → mac-planner → pendant
- **model tier:** Cheap background model computes structured snapshots and change classification; realtime speaks only the filtered decision list when requested.
- **latency:** Under 10 seconds after opening a watched dashboard; baseline refresh can run asynchronously.
- **cost:** About $0.01–$0.08 per comparison depending on page size. Retain structured fields and source hashes, not page text, unless the owner explicitly chooses otherwise.
- **security:** The baseline can reveal sensitive financial, health, or work information, so per-origin rules must separately control read, compare, speak, and retain. Treat deletions and changed permissions as high-priority but do not act on them automatically. Every spoken item needs a source link and observation time.
- **missing:** A durable structured baseline store with field-level redaction; Semantic comparison tolerant of layout and timestamp noise; A browser-opened verification view linked to each reported change


## What it asked for

_Nothing._
