# Harness derivation — browser-extension — round 210

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Prepare this logged-in form for me, but do not send it: use the information on the page and my Mac files, fill the draft, and tell me exactly what would be submitted.”"
- **useful because:** The browser is the only node with authenticated sessions, while the Mac is the only node with local files and automation. This turns a high-friction form into a reviewable, evidence-backed draft without crossing the owner's stop-before-submit boundary.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Use the cheaper background/local planner for field mapping and reconciliation; reserve realtime only for the owner's spoken request and final concise readback.
- **latency:** 30–90 seconds for page inspection, local lookup, and fill; under 5 seconds for the spoken preview after completion.
- **cost:** About $0.01–$0.05 per invocation, dominated by model calls over extracted fields; browser execution and local file reads are negligible.
- **security:** Never persist page HTML or screenshots. Keep the empty per-origin policy until the owner configures origins. Persist only short-lived, host-keyed claims with existing 24-hour browser TTL and provenance. Fill is reversible; stop before submit and show every field/value and destination.
- **missing:** A reliable browser action resolver for browser_list_tabs/browser_read_page (the current granted wrappers are ambiguous even though Safari is online); A field-level diff/preview receipt joining browser-origin values to local-file evidence; Owner-supplied per-origin read/extract/redact/never-store configuration

### "“Give me a 60-second brief on the authenticated page I’m looking at, cross-check it against my calendar and local notes, and tell me the one decision or next action that matters.”"
- **useful because:** This is a genuinely cross-surface answer: the browser supplies private page context, the Mac supplies private calendar/notes, and the relay/pendant turns them into an immediately useful decision brief instead of a page dump.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Background planner performs extraction, deduplication, and calendar/note cross-check; realtime tier only handles the owner's request and a compact spoken result.
- **latency:** 15–45 seconds when the page is already open; a brief should be ready before the owner leaves the screen.
- **cost:** Roughly $0.01–$0.04 each, with cost dominated by summarizing extracted claims; local calendar/note access and browser actions are cheap.
- **security:** Read-only browser allow-set for this workflow; no clicks or form fills. Store only cited claims, not page text, under existing browser TTL/provenance rules. Do not speak categories the owner later marks must-not-speak; configuration ships empty rather than guessing.
- **missing:** A robust read-current-tab/browser_read_page action (Safari now reports two live tabs, but the granted read tool does not resolve); A joiner that aligns page entities/dates with calendar and local-note entities and emits citations; Owner's explicit authenticated-origin and spoken-category configuration

### "“Watch the authenticated account pages I nominate, and if a security, billing, deadline, or access change appears, verify it against my Mac context and put a short alert on my pendant—even if the Mac goes offline.”"
- **useful because:** This is the highest-value thing the hive could do: continuously notice consequential changes behind logins that public search cannot see, reduce false alarms with local context, and reach the owner through the worn device when the computer is unavailable.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Scheduled/background model for polling, semantic diffing, and prioritization; realtime only if the owner asks follow-up questions. No expensive model call for unchanged pages.
- **latency:** Poll cadence configurable per origin (for example 5–30 minutes); alert generation under 20 seconds after a detected change.
- **cost:** Approximately $0.00 when unchanged using hashes/DOM fingerprints; $0.01–$0.05 per changed page for extraction and prioritization. Browser session traffic dominates operational cost.
- **security:** Only owner-configured origins; empty configuration by default. Claims only, no page bodies/screenshots, 24-hour browser TTL, host/url provenance, and explicit stale-session labeling. Alert text must be short and category-filterable; do not perform account actions automatically.
- **missing:** A durable authenticated page-watch scheduler and semantic-DOM fingerprint store; A browser read/watch action that can target a named tab/session reliably (current tool resolver is ambiguous); A relay-to-pendant delivery adapter using the already accepted offline_alert_inbox behavior; Owner-provided origin list and may-speak/must-not-speak categories

### "“I’m offline now—answer the question I have about the authenticated page I read earlier, and tell me how fresh and trustworthy that answer is.”"
- **useful because:** Today authenticated browser knowledge disappears when Safari or the Mac is unavailable. A privacy-bounded, time-stamped claim capsule synchronized from browser to relay and then to the pendant would let the owner retrieve a recently read deadline, policy, or amount during travel or a network outage, with honest staleness instead of pretending it is live.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model extracts a small set of owner-requested claims at read time; realtime model answers the offline spoken query from the compact local capsule. No page replay or expensive inference is needed.
- **latency:** Under 3 seconds for an offline pendant lookup; extraction happens opportunistically after the page is read.
- **cost:** Under $0.01 per page-read capsule and near-zero per lookup; storage and synchronization dominate rather than inference.
- **security:** Never cache HTML, screenshots, credentials, or unrestricted page text. Cache only explicit, short claims with source URL, captured-at time, expiry, and sensitivity label; encrypt in transit and at rest; automatically erase on expiry or owner deletion. The pendant must say “captured 18 hours ago,” not imply current truth.
- **missing:** An encrypted browser-to-relay claim capsule and sync protocol; A pendant-resident query/index skill that fits available RAM and survives a dropped link; A user-visible capture/expiry/delete control and provenance display

### "“Check whether the details across my private booking pages and my calendar agree; if they do not, tell me the exact conflict and which source is newer.”"
- **useful because:** The owner currently has to manually compare authenticated confirmations, calendars, and local notes. This hive-only capability reconciles sources that no single node can reach together and reports a concrete conflict—wrong date, time zone, name, amount, or location—rather than producing another generic summary.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Use a cheaper background reconciliation model for structured field extraction and conflict classification; use realtime only to answer follow-up questions or speak the final exception list.
- **latency:** 20–60 seconds for up to five nominated pages and local sources; under 5 seconds for a follow-up clarification.
- **cost:** $0.02–$0.08 per reconciliation, dominated by extraction across changed pages; unchanged source fingerprints should avoid repeat calls.
- **security:** Read-only by default, no booking changes. Keep source-specific provenance for every compared field, retain only bounded claims under existing browser TTL rules, and expose the newer-source decision rather than silently choosing one. Origins and categories remain explicit owner configuration.
- **missing:** A multi-source schema mapper for dates, time zones, amounts, identities, and locations; A provenance-aware conflict engine that can explain why one value is newer; A browser action that can reliably read several named authenticated tabs

### "“Build me a private evidence packet from these logged-in pages and my Mac files: a timeline, the claims each source supports, and the gaps. Keep it local and let me inspect it before I send anything.”"
- **useful because:** When disputing a charge, service failure, or administrative decision, the owner needs traceable evidence rather than a prose answer. The browser contributes authenticated records, the Mac contributes local documents, and the relay/pendant makes the packet reviewable without automatically contacting anyone.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Background model performs OCR/field extraction, timeline normalization, and gap detection; realtime is limited to the owner's spoken review questions.
- **latency:** 1–3 minutes for a packet from 10–20 sources; incremental additions under 15 seconds.
- **cost:** $0.05–$0.25 per packet depending on document count and OCR; local hashing and assembly are cheap.
- **security:** Packet remains on the Mac unless explicitly exported. Store source references and extracted claims, not browser HTML or screenshots by default; mark uncertain or redacted fields; never send or upload without a separate explicit owner action. Provide deletion and provenance trace for every claim.
- **missing:** A local evidence-packet format with claim-to-source links and uncertainty fields; A cross-surface importer for authenticated browser findings plus local files; A pendant-friendly review protocol that can read the packet's exceptions without leaking full sensitive documents


## What it asked for

_Nothing._
## Its own summary

Discovered fresh live state: Safari is online with 2 tabs (active YouTube tab 3186198), while the granted browser command wrappers still cannot resolve reliably—list-tabs is ambiguous with list-sessions and read-page has no usable implementation. Recorded three capabilities: authenticated form drafting with field-by-field preview and no submit; private-page plus local-calendar/notes decision briefs; and authenticated consequential-change monitoring that reaches the pendant offline inbox. The proposals deliberately preserve existing browser retention rules (claims only, host provenance, 24-hour TTL) and require explicit owner-supplied origins/categories rather than inventing them. I also informed mac-planner of the live-tab/resolver state.

**Biggest unknown:** The exact live browser action resolver and read-current-tab contract. Until that is fixed, the system can see that Safari is online but cannot reliably inspect either of its tabs. After that, the remaining product gaps are the page-watch scheduler/semantic diff, browser-to-local evidence join, and relay adapter to offline_alert_inbox.

