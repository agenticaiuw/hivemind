# Harness derivation — browser-extension — round 236

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-state** — Safari extension is online with 5 tabs, including authenticated-looking USPS tracking, Adafruit order history, and DoorDash pages. Active tab USPS tracking shows package 9200190323035201509394 delivered to mailbox in Madison, WI on Aug 8, 2026 at 11:42 AM. Browser actions execute successfully through POST /execute.
  - evidence: POST /execute browser_list_tabs and browser_read_page at 2026-08-09T00:57Z returned 5 tabs and live USPS page text with delivery status.

## Capabilities it proposed

### "“Keep an eye on my deliveries and orders across the sites I’m already signed into, and tell me only when something needs attention.”"
- **useful because:** A single authenticated, cross-site exception view would catch missed delivery attempts, stalled shipments, refunds, and order changes without making the owner open five tabs. The browser is the only node that can see these logged-in pages; the relay can compare them over time and the pendant can surface urgent exceptions while offline.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard-ux
- **model tier:** Background scheduled browser extraction and deterministic diffing; use the expensive realtime model only when the owner asks “what changed?” or needs a spoken explanation.
- **latency:** Run each origin on its own schedule (15–60 minutes); an exception should reach the relay in under 2 minutes and the pendant on its next connection. Initial setup is a one-time 2–5 minute review of tracked origins and fields.
- **cost:** Low: mostly browser commands and short structured diffs; roughly <$0.02 per daily origin sweep excluding model calls. The dominant cost is browser session wakeups, not inference.
- **security:** This reads authenticated order pages and may expose addresses, order contents, or tracking numbers. Ship with an empty per-origin configuration, redact identifiers in spoken alerts, persist only short claims (not page text), and require the owner to approve each origin/field. Never click purchase, cancel, refund, or message controls.
- **missing:** A durable scheduled browser-watch runner that can invoke POST /execute against a specific tab/session; Semantic field extractors for delivery state, ETA, exception, refund, and cancellation across arbitrary origins; A diff-to-offline_alert_inbox adapter and owner-editable empty origin configuration

### "“Take the important dates and commitments on the page I’m looking at and make me a plan for them—draft the reminders and messages, but don’t send anything.”"
- **useful because:** This turns authenticated web pages into completed personal organization rather than a transcript. The browser extracts dates and obligations behind the owner’s login, the Mac converts them into concrete reminders and drafts, and the pendant gives a compact spoken review while preserving the owner’s control over sending.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheaper background extraction/planning model for dates, entities, and draft generation; use realtime only for the owner’s follow-up conversation or spoken review.
- **latency:** A page-to-plan request should return a reviewable draft in 10–30 seconds. Creating local reminders is immediate; draft messages remain visibly unsent until the owner explicitly asks later.
- **cost:** About $0.01–$0.05 per page depending on length; browser extraction and model context dominate, while reminder creation is negligible.
- **security:** Page content may contain private names, addresses, and account details. Do not persist raw text; retain only bounded claims with URL provenance. Show every proposed reminder/message with source and target, redact secrets in speech, and never submit forms or send messages in this workflow.
- **missing:** A robust page-to-obligation schema (date, timezone, owner, action, source quote); A draft-only bridge from browser findings into Mac reminder and message-draft primitives; A pendant review protocol that can speak a numbered list and let the owner choose one item without losing provenance

### "“Make a proof packet for this order or delivery: capture the relevant authenticated page facts, receipt identifiers, and timestamps so I can use it later, without saving the whole page.”"
- **useful because:** When a delivery is missing or a charge is disputed, the owner needs a compact, trustworthy record—not a screenshot buried in a tab. The browser can access the logged-in receipt/tracking page, the relay can preserve provenance and hashes, and the Mac can create a clearly named local packet that the pendant can later locate or summarize.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard-ux
- **model tier:** Use deterministic extraction and hashing by default; use a cheaper model only to label fields and identify the relevant order/delivery facts. Realtime is unnecessary unless the owner asks for a spoken explanation.
- **latency:** Generate a packet in under 15 seconds for one page and under a minute for a small set of linked pages. The owner should hear a short confirmation immediately and see the packet location on the Mac.
- **cost:** Under $0.01 per packet when extraction is rule-based; storage and browser calls dominate, with optional model labeling adding a few cents.
- **security:** Packets can contain addresses, order IDs, and payment-adjacent data. Default to local Mac storage, encrypt or restrict file permissions, retain only selected claims plus URL/time/hash, and make redaction fields explicit. Never include cookies, tokens, full HTML, or screenshots unless separately requested.
- **missing:** A user-invoked browser evidence-packet action that selects fields rather than dumping page text; A local encrypted packet writer with stable schema and content hashes; A pendant lookup/replay command for packet IDs and a dashboard view of provenance

### "“Watch my signed-in accounts for security or billing changes I didn’t make, and wake me on the pendant with exactly what changed and what I should do.”"
- **useful because:** This is a high-consequence job the owner cannot safely delegate to a normal public-web search: the browser alone holds authenticated account pages and the pendant is the only channel that can interrupt him away from the Mac. It would detect a changed recovery email, unfamiliar login, payment method, shipping address, or unexpected charge and turn it into a concise response plan.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → dashboard-ux
- **model tier:** Scheduled deterministic extraction and baseline comparison first; a small background model classifies severity and drafts next steps. Realtime is reserved for the owner asking follow-up questions while the alert is active.
- **latency:** Check configured high-risk origins every 10–30 minutes; deliver a high-confidence alert within two minutes of detection. Normal unchanged checks should be silent.
- **cost:** Low ongoing inference cost, roughly $0.01–$0.05 per active origin per day; browser wakeups and authenticated page loads dominate.
- **security:** This is itself extremely sensitive. Configuration must be explicit and empty until the owner chooses origins and fields. Store only bounded change claims, hashes, timestamps, and provenance; never store passwords, tokens, full inboxes, or page bodies. Alerts should redact account numbers and offer a local Mac detail view. It must never automatically change credentials, freeze cards, or contact support.
- **missing:** A scheduler that can revisit configured authenticated origins and maintain field-level baselines; Security/billing change extractors with confidence and false-positive suppression; A high-priority bridge into offline_alert_inbox with deduplication and escalation state; An owner-facing configuration UI for monitored origins and never-speak fields

### "“When a logged-in site disagrees with another site about an important fact—like an order amount, delivery date, appointment, or cancellation—show me the conflict and tell me which source is newer.”"
- **useful because:** The owner currently has to manually compare retailer, carrier, and confirmation pages. A cross-site contradiction resolver would catch stale promises and silent failures that a single-page watcher misses, then present a decision-ready explanation rather than multiple notifications.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard-ux
- **model tier:** Use deterministic normalized fields and timestamps for comparison; use a background model only to explain the conflict and rank source reliability. Realtime is unnecessary unless the owner asks for clarification.
- **latency:** On demand, produce a conflict report in 15–30 seconds across up to five configured pages. Optional scheduled checks can run hourly without waking the owner unless a material contradiction appears.
- **cost:** Approximately $0.02–$0.08 per report; browser page loads and cross-page context dominate, while normalized comparisons remain cheap.
- **security:** Cross-origin joins can expose more context than any one page. Require explicit origin pairing and field selection, retain only short claims with timestamps and URLs, redact identifiers in spoken output, and never infer or announce sensitive categories unless configured.
- **missing:** A normalized cross-origin fact schema with source timestamps and reliability metadata; A browser workflow that reads several authenticated tabs atomically enough to compare them; Conflict classification and a dashboard/pendant presentation that cites each source without retaining page text

### "“If I’m about to miss an online deadline, open the right authenticated page, prepare the exact next step, and guide me through it from the pendant while I’m away from the Mac.”"
- **useful because:** The browser can reach portals the pendant and relay cannot, while the pendant can interrupt the owner during travel. This would turn a deadline into a guided, reversible workflow: identify the deadline, navigate to the correct page, fill a draft or prepare the next screen, and read back what remains for the owner to submit.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → dashboard-ux
- **model tier:** Background scheduling and deadline extraction use a cheaper model plus deterministic date logic; realtime handles the short interactive voice guidance session. The browser action plan should remain inspectable and resumable.
- **latency:** Deadline checks every few hours; when triggered, prepare the workflow in under 30 seconds and keep each voice turn under two seconds. Work should survive a dropped link and resume from the last page/field.
- **cost:** Roughly $0.02–$0.10 per deadline workflow, dominated by authenticated page reads and interactive voice turns; unchanged checks are inexpensive.
- **security:** Deadlines may involve legal, financial, medical, or employment actions. Keep an explicit empty origin/category configuration, preserve field-level provenance, redact sensitive values in speech, and stop before any submit, payment, send, or irreversible confirmation. The owner must be able to inspect and discard the prepared action.
- **missing:** Deadline/entity extraction from authenticated pages with timezone and expiration semantics; A resumable browser form-state and field-diff protocol usable while the owner is away from the Mac; Pendant controls for selecting, correcting, and resuming a prepared step; A scheduler that escalates only when the deadline is near


## What it asked for

_Nothing._
