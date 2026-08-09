# Harness derivation — browser-extension — round 238

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Read the four newest items in my Safari Reading List and give me the titles, source, and one-line reason each might matter.”"
- **useful because:** This is a concrete request the owner has already repeated and it uniquely needs the authenticated Safari session; public search cannot see the Reading List. The relay can turn the result into a short spoken answer while keeping page bodies out of memory.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background for extraction and ranking; realtime only for the final one-sentence-per-item spoken response
- **latency:** 10–30 seconds for navigation, extraction, and ranking; under 2 seconds once the result is ready to speak
- **cost:** About $0.01–$0.05 per invocation; browser and local extraction dominate latency, model cost is only title/source relevance ranking
- **security:** Use a read-only browser action allow-set and never click article links or mutate the list. Persist only short claims with host/URL provenance under the existing 24-hour browser-fact TTL and 200-character value cap; do not retain HTML, screenshots, or page text.
- **missing:** A Reading List-specific extraction recipe that can identify unread/new entries in Safari's authenticated UI; A stable browser_read_page result path in the command wrapper (navigate/list already resolve); A result-to-audio handoff that queues the four claims to offline_alert_inbox when the Mac link drops

### "“Fill out this browser form from the details in my note, then tell me exactly what would be submitted; don't submit it until I approve.”"
- **useful because:** It turns the browser's authenticated reach into a trustworthy two-body workflow: the Mac can do tedious field mapping, while the pendant gives the owner a concise, audible final diff before an irreversible send. It is safer and faster than asking the owner to inspect a dense page on the phone.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** mac-planner/background for field extraction and filling; realtime for the spoken payload summary; no expensive model for deterministic diffing
- **latency:** 5–20 seconds to fill and generate a field-by-field preview; approval-to-submit under 5 seconds
- **cost:** Roughly $0.01–$0.08 per form, dominated by computer-use turns and page extraction; approval itself should be local and free
- **security:** Keep the form in the authenticated browser session. Store only field names, redacted values, origin, and an undo token; never persist the full page or secrets. Before submit, speak sensitive fields as categories unless the owner explicitly asks for values. The owner-approved destructive-action policy still applies: preview is automatic, submit requires explicit approval and produces a receipt.
- **missing:** A browser transaction journal that snapshots pre-fill and post-fill field values and can undo every reversible fill; A pendant approval event carrying a short-lived preview hash, bound to the same browser tab and origin; A submit continuation that refuses to replay if the page, origin, or field hash changed

### "“Re-check that claim you told me from the website yesterday and tell me whether it is still true, what changed, and how certain you are.”"
- **useful because:** Browser facts expire quickly, but today there is no owner-facing way to revisit one claim and distinguish a real page change from stale memory. This makes authenticated browsing auditable: the relay identifies the exact prior claim, Safari revisits the source while logged in, and the pendant reports a compact old-versus-new answer rather than silently repeating yesterday's scrape.
- **path:** relay-realtime → browser-extension → mac-planner → mac-vision → pendant
- **model tier:** cheap background extraction/diff for page claims; realtime only to resolve “that claim” from the conversation and speak the result
- **latency:** 15–45 seconds for a source revisit and semantic diff; under 2 seconds to answer from an already completed check
- **cost:** About $0.02–$0.10 per check, mostly authenticated page navigation and one small semantic-diff call
- **security:** Revisit only the recorded host and URL, with a read-only action allow-set. Keep old and new values as short claims with timestamps and provenance, never page text/screenshots. If the URL now redirects to a different origin or requires a new login, stop and report that rather than following arbitrary links.
- **missing:** A claim-check job that resolves a conversational reference to one browser finding and schedules a fresh browser read; A semantic diff schema that records unchanged/changed/removed/uncertain plus evidence URLs and timestamps; A spoken result formatter that says both values only when the category is allowed to be spoken

### "“Find the earliest appointment that fits my constraints across the authenticated sites I use, compare the actual available slots, and stop before booking anything.”"
- **useful because:** Today the browser can inspect one page, but it cannot perform a bounded search across several private portals and return a normalized comparison. This would turn opaque authenticated scheduling into one spoken decision: the owner hears real slots and chooses, while no appointment is accidentally booked.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** background planner for portal-specific navigation and deterministic slot normalization; realtime only for the final comparison and owner choice
- **latency:** 30–120 seconds for three to five portals; under 3 seconds to read back a cached comparison
- **cost:** $0.05–$0.30 per search, dominated by browser computer-use turns and portal variability
- **security:** Start from an explicit, empty per-origin configuration supplied by the owner. Permit reads and slot selection only; never click booking/checkout. Retain only provider name, slot, URL, and expiry, with no page text or credentials. Revalidate every slot immediately before presenting it.
- **missing:** A multi-origin browser workflow runner with per-origin recipes and bounded retries; A normalized appointment-slot schema with timezone, expiry, and source provenance; A hard stop boundary that can inspect/select a slot but cannot invoke booking until a separate owner command

### "“Reconcile the invoices in this logged-in portal with the invoices in my Mac folder, tell me which are missing or duplicated, and draft—not send—the follow-up messages.”"
- **useful because:** No single node can do this today: Safari holds the private portal session, the Mac holds local documents and mail context, and the pendant is the only practical way to hear a short exception list while moving around. It turns a repetitive financial chore into an auditable set of discrepancies and drafts without sending anything.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** background document extraction and deterministic invoice matching; realtime only to summarize exceptions or answer a follow-up
- **latency:** 30–90 seconds for a normal month of invoices; draft generation within 10 seconds after matching
- **cost:** $0.05–$0.25 per run, dominated by OCR/document parsing and authenticated page extraction
- **security:** Keep invoice bodies local where possible. Send only normalized fields needed for matching (issuer, invoice number, amount, date, status) to the planner; redact account and payment details. Save drafts locally with source URLs and provenance; require the owner's existing explicit confirmation before any message is sent.
- **missing:** A cross-surface normalized document/invoice schema and matcher with tolerance for currency/date formatting; A browser download/read path that can hand portal documents to local parsing without storing page HTML; A draft composer that links each sentence to the portal URL or local file and leaves mail unsent


## Changes it proposed to its own stack

### `browser-harness` — Add an extension-side semantic page capsule: for the active authenticated tab, compute a compact accessibility/DOM tree containing headings, labels, controls, selected text, table rows, and stable element identifiers; redact password/payment fields before sending it through the relay, and invalidate the capsule on navigation or DOM mutation. Let browser actions target capsule IDs rather than brittle CSS selectors.
- **owner gets:** Private, dynamic pages would become understandable and operable by voice even when screenshots are ambiguous: the owner could ask about a table or say “open the second result,” and the system would use the exact visible control instead of guessing. It also reduces the amount of private page content that leaves the Mac.
- effort: Medium-high: Safari extension content-script/accessibility extraction, mutation invalidation, relay serialization, and action-ID translation.  ·  risk: Some sites expose misleading accessibility labels or virtualized rows; fall back to the current visual/computer-use path and report uncertainty. Never cache capsules beyond the active task.
- cost: Small CPU/memory overhead on the Mac; lowers model/image-token cost by replacing repeated screenshots with compact trees. No meaningful API cost increase.  ·  latency: Initial capsule 100–500 ms; mutation refreshes incremental. Voice actions should be faster than screenshot reasoning.
- security: Improves privacy if redaction is correct, but a DOM tree can still contain secrets; enforce field-type redaction, origin-scoped lifetime, and no durable storage.
- depends on: A working browser_read_page/browser_snapshot result path; A browser action protocol that accepts stable capsule element IDs; Owner-provided per-origin configuration, initially empty


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct browser capabilities: authenticated Safari Reading List triage (the owner's repeated failed request), a fill-but-don't-submit form workflow with a pendant-spoken exact payload preview, and a claim re-check that revisits the original logged-in source and reports what changed. The single most useful is the form preview: it joins browser session reach, Mac field work, relay speech, and pendant approval at the irreversible boundary. What remains needed is not another wrapper name: implement a stable browser_read_page result path, a browser transaction journal plus hash-bound pendant approval/undo, and a claim-check job. I also need the owner to supply actual authenticated origins/categories before enabling automation; the config should ship empty rather than inventing sites.

**Biggest unknown:** Whether the live Safari extension currently exposes a usable tab and returns browser_read_page results after browser_navigate; the previously observed state had zero tabs, although navigate is expected to bootstrap one.

