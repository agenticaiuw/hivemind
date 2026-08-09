# Harness derivation — browser-extension — round 187

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with two tabs; POST /execute browser_list_tabs succeeded, active Google Maps and authenticated ChatGPT tab available.
  - evidence: POST /execute {actions:[{type:browser_list_tabs}]} returned 200 success at 2026-08-08T04:47:20Z.

## Capabilities it proposed

### "When I say “pick up my web task,” reopen the authenticated page I was working on, show me what changed since I left it, and continue from the exact form, draft, or result without losing my place."
- **useful because:** Safari sessions contain the owner's private state that the relay and Mac cannot reproduce. A durable handoff turns the pendant into a practical resume button: it preserves task state, not merely a URL, and reports a change summary before touching the page.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Background model computes a compact structured page/task summary and diff; realtime model is used only for the owner's spoken resume/correction exchange.
- **latency:** Resume acknowledgement under 2 seconds; page restore and diff within 10 seconds. If Safari is asleep or the origin session expired, state the exact recovery step rather than pretending continuity.
- **cost:** About $0.01–$0.05 per resume depending on page size; browser extraction and local hashing dominate latency, not model tokens.
- **security:** Persist only an origin-scoped encrypted task capsule (URL, tab ID, DOM selectors, redacted field labels, hashes, and owner-approved notes), never raw page text or credentials. Expire capsules per origin and let the owner say “forget this task.” Do not submit or send anything while resuming.
- **missing:** A browser task-capsule schema that survives tab IDs and selector drift; A browser-side checkpoint/diff operation with redaction and origin policy; A pendant command to select/resume a capsule from offline_alert_inbox

### "On the page I have open, find the part that answers my question, tell me the answer in two sentences, and leave Safari highlighted at the exact passage so I can inspect it."
- **useful because:** The owner can ask from the pendant while walking away from the screen, yet still get verifiable answers from private pages. The browser supplies source-grounded evidence and the Mac leaves the authenticated page at the relevant section instead of producing an uncheckable summary.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Cheap extraction/ranking model locates candidate passages; realtime model turns the selected evidence into a short spoken answer and handles follow-up. The answer must carry passage IDs and confidence, not just free-form prose.
- **latency:** First spoken answer in 6–12 seconds for an already-open page; scroll/highlight acknowledgement within 3 seconds after the answer.
- **cost:** About $0.01–$0.04 per question; page extraction is local and the model sees only a bounded set of candidate passages.
- **security:** Apply existing per-origin redaction before any relay upload; do not persist page text by default. Return a source capsule containing origin, title, section heading, character offsets, and a short ephemeral quote. Never navigate away or activate links unless asked.
- **missing:** Browser-side semantic passage anchors that survive virtualized pages and can scroll/highlight the chosen range; A bounded evidence capsule and ephemeral retention policy shared by browser and speech pipeline; Pendant follow-up routing that keeps the current tab and passage ID as conversational context

### "Check the private sites I already have open, compare the actual prices and delivery dates for this item, and tell me the best option without adding anything to a cart."
- **useful because:** Public search cannot see member pricing, regional inventory, saved addresses, or account-specific delivery dates. The browser extension can inspect those authenticated pages while the relay and pendant give a hands-free comparison, stopping before cart or purchase mutations.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Background model extracts normalized offer records from each permitted origin; realtime model asks one clarification if the item or tradeoff is ambiguous and speaks the ranked result.
- **latency:** Open-tab discovery in 2 seconds and a first comparison in 15 seconds; if a site requires navigation or login renewal, report it individually without blocking other offers.
- **cost:** About $0.03–$0.12 per comparison; browser navigation and page extraction dominate, with one model pass over compact offer records.
- **security:** Only inspect origins the owner explicitly names or has configured; redact addresses, account IDs, and payment details before relay processing. Do not add to cart, accept offers, or submit forms. Include timestamp and exact origin for every price so stale inventory is not presented as current.
- **missing:** An origin-scoped multi-tab extraction plan with per-site selectors learned from page structure, not hardcoded merchants; An offer schema handling currency, shipping, membership price, tax visibility, stock, and delivery confidence; A freshness/contradiction check that re-reads changed offers before speaking the ranking

### "Look across the travel accounts I already have open and my calendar, find every itinerary conflict or missing connection, and give me one coherent trip plan with the exact pages I need to fix—without changing any booking."
- **useful because:** No single node can do this today: Safari alone sees private reservations, the Mac sees calendar context, and the pendant is the only practical place to hear a conflict while away from the screen. It prevents missed connections and double-booked time without making a booking decision on the owner's behalf.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model extracts normalized itinerary segments and compares them with calendar events; realtime model speaks only the conflicts, uncertainty, and proposed order. Use deterministic time-zone and duration checks before model reasoning.
- **latency:** Initial scan in 20 seconds for up to five open accounts; individual account failures should not prevent a partial result. Spoken conflict summary under 30 seconds.
- **cost:** Approximately $0.05–$0.20 per scan; authenticated page extraction and timezone/segment normalization dominate, with the model seeing structured records rather than page dumps.
- **security:** Read-only by default: never cancel, book, or send a message. Keep passport, loyalty, payment, and full confirmation values local and redact them before relay processing. Store only segment IDs, times, origins, destinations, and explicit owner-approved notes; show each conclusion's source origin and freshness.
- **missing:** A browser multi-origin itinerary extractor that can recognize reservation pages without a hardcoded merchant list; A local Mac calendar join and deterministic timezone/connection validator that emits a provenance-linked conflict graph; A spoken conflict digest format that can name the exact Safari tab and passage to inspect, while respecting empty per-origin retention/speech policy

### "Before I submit anything online, check the private account pages I have open for mismatched names, addresses, dates, or policy numbers, tell me exactly which source disagrees, and leave each correction page ready without sending it."
- **useful because:** People routinely carry stale identity and policy data between multiple authenticated portals. The browser can see the authoritative private values, while the Mac can compare them and the pendant can announce only actionable discrepancies; today each site is an isolated task and errors surface after submission.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model canonicalizes fields and computes typed discrepancies; realtime model asks a clarification only when two sources are both plausible and speaks a concise correction list.
- **latency:** Compare up to six open pages in 15 seconds; prepare correction tabs within another 10 seconds, with no mutation performed.
- **cost:** About $0.03–$0.15 per scan; DOM extraction, field normalization, and origin-specific redaction dominate.
- **security:** Never relay full identity numbers or secrets. Keep sensitive values local, speak categories and masked suffixes only, and require an explicit per-origin configuration before reading or retaining any field. Do not type corrections into a page until the owner names the target origin; never submit.
- **missing:** A typed cross-origin field comparison engine with confidence and authority annotations; Local-only handling for high-sensitivity fields and masked spoken diffs; A browser preparation mode that fills corrections while preserving an undoable receipt and stops at submission

### "Gather the statements and receipts for this expense from the private sites I name, verify that the totals agree, and make me a dated packet I can hand to my accountant—without uploading it anywhere."
- **useful because:** Authenticated portals often hide the source documents behind separate sessions, while the owner needs one trustworthy packet rather than a pile of tabs. Safari supplies access, the Mac performs local OCR and arithmetic, and the pendant can report missing or contradictory records while the relay coordinates the job.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model performs local document classification, deduplication, and total reconciliation; realtime model is reserved for clarifying which expense and for a short completion/missing-items report.
- **latency:** Start immediately and return a progress update in 10 seconds; complete a normal 10–30 document packet in under 2 minutes, with partial output if an origin expires.
- **cost:** Roughly $0.10–$0.50 per packet; local OCR/PDF rendering and browser downloads dominate, while model input is document metadata and extracted totals rather than full sensitive files.
- **security:** Download directly to an owner-selected local folder, encrypt at rest, and never send documents or account credentials to the relay. Preserve source URL, statement date, checksum, and extraction confidence. Do not email, upload, or share the packet. Require explicit origin and destination configuration, shipped empty.
- **missing:** A browser authenticated-download collector with per-origin filename/date rules and session-expiry recovery; A Mac-local encrypted packet builder with OCR, deduplication, arithmetic reconciliation, and provenance manifest; A pendant progress/error protocol that can identify which origin needs the owner's attention without speaking sensitive amounts aloud


## What it asked for

_Nothing._
## Its own summary

Discovered and verified that Safari is usable now: two live tabs, with POST /execute browser_list_tabs returning real tab IDs and provenance. I recorded three non-duplicate owner-facing capabilities: (1) the highest-value browser feature, a durable authenticated-task resume capsule that restores state and reports changes; (2) source-grounded private-page answers that leave Safari highlighted at the exact passage; and (3) authenticated multi-site price/inventory comparison without touching carts. A form-filling idea was correctly rejected as an existing capability, so I did not rephrase it. I told mac-planner the live state and implementation gaps.

**Biggest unknown:** No owner-supplied per-origin configuration exists yet: which authenticated sites may be inspected, what may be spoken, and what may never be persisted. The next build needs that explicit configuration plus task-capsule/evidence schemas; I will not invent a site list or sensitivity policy.

