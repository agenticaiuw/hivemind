# Harness derivation — browser-extension — round 189

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “prepare this authenticated web task,” inspect the logged-in page, gather the exact facts and fields needed, compare them with my Mac files/calendar, and leave a spoken decision packet on my pendant plus a draft on my Mac—without submitting anything."
- **useful because:** This turns browser access into a genuinely cross-surface assistant: it can reconcile private web state with local context, while the owner gets a concise actionable result instead of a copied page or an unsafe automation.
- **path:** browser-harness → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** background for page extraction and local comparison; realtime only to clarify the owner's spoken goal and read the final short packet
- **latency:** 20–60 seconds for extraction/comparison; under 2 seconds to acknowledge on the pendant
- **cost:** About $0.01–$0.05 per task; browser extraction and model comparison dominate, not speech
- **security:** Authenticated page text and selected local files leave the browser tier for processing; owner-configured per-origin extraction/redaction rules must be explicit. Never submit, send, purchase, or delete; show exact proposed mutations and source URLs.
- **missing:** a durable cross-surface decision-packet schema with source citations and draft artifacts; browser page extraction plus origin rule configuration; a relay-to-pendant packet queue that can include a Mac draft link; owner-selected matching rules for which local files/calendar items may be compared

### "Tell me, in one short spoken update, what materially changed across the authenticated pages I left open and the related files on my Mac since yesterday, and give me the next action for each change."
- **useful because:** The owner currently has to remember both browser tabs and local work. This produces a cross-surface delta that is useful even when no single site has a built-in notification, and delivers it when the Mac/browser are available or queues it for later on the pendant.
- **path:** browser-harness → mac-planner → relay-realtime → pendant
- **model tier:** scheduled/background model for snapshots, diffs, and ranking; realtime model only for an on-demand follow-up question
- **latency:** Scheduled overnight or 30–90 seconds on demand; immediate spoken acknowledgement under 2 seconds
- **cost:** Roughly $0.02–$0.10 per daily run depending on page count and diff size; authenticated snapshots and summarization dominate
- **security:** Persist hashes and minimal redacted excerpts by default, not full page bodies. Per-origin and per-category rules are owner-supplied and inspectable. Do not speak secrets aloud; include deep links but no automatic mutation.
- **missing:** authenticated tab snapshot persistence with semantic diffing; linking page entities to local files/calendar without hardcoded sites; a change-ranking policy and deduplication across daily runs; scheduled delivery to the accepted offline_alert_inbox

### "While I am looking at a logged-in web form, say “stage it,” and have the browser fill it from my spoken instructions and Mac context, show me a compact before/after preview on the Mac and read the critical fields on the pendant; let me say “undo” or “submit” afterward."
- **useful because:** This is the highest-value browser workflow: it removes tedious authenticated data entry while preserving the owner's control at the final irreversible boundary, with a recovery path if the browser or Mac link drops.
- **path:** browser-harness → mac-vision → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** realtime for interpreting the spoken command and critical-field readback; background/local planner for field mapping and validation
- **latency:** Field staging within 10 seconds; preview under 3 seconds after staging; submit only after explicit owner utterance
- **cost:** About $0.02–$0.15 per staged form; visual extraction and validation dominate, with realtime used briefly
- **security:** Form values are sensitive and must remain ephemeral unless the owner asks to save them. Display exact diff, target origin, and submit button label. Explicit submit is required; undo must restore original values and a receipt must record what happened.
- **missing:** browser DOM/value snapshot and reliable field-level undo transaction; cross-surface preview card and spoken critical-field policy; voice intent binding for stage/undo/submit with idempotent receipts; recovery when the extension disconnects between fill and submit

### "When I press the pendant button while a Safari page is open, tell me the three things on that page that need my attention, cite the page title, and offer to save one as a Mac reminder."
- **useful because:** It makes the browser's unique authenticated reach available without composing a voice command: one physical gesture captures the owner's current context, gives a useful spoken result, and can turn a chosen item into a reminder.
- **path:** pendant → browser-harness → relay-realtime → mac-planner
- **model tier:** realtime for the short extraction and spoken answer; background model only if the page is long and needs chunking
- **latency:** Button acknowledgement under 500 ms; answer within 8 seconds
- **cost:** About $0.01–$0.04 per invocation; page extraction and summarization dominate
- **security:** Only the active tab is read; never persist raw page text. Per-origin redaction rules remain explicit. Creating a reminder is reversible and allowed by owner preference, but the exact reminder text and date must be spoken before creation.
- **missing:** a physical-button event routed to the active browser tab; active-tab identity and browser_read_page result returned through the relay; a compact attention extractor that distinguishes content from navigation/chrome; a reliable pendant speech response and optional reminder action

### "Before doing anything on a logged-in website, tell me which account and organization the active tab is using, compare it with the person or project I named, and warn me on the pendant if they do not match."
- **useful because:** A browser can be authenticated and still be authenticated as the wrong person, workspace, or tenant. This would prevent the most dangerous class of silent browser mistake before any click or form fill, especially when Safari has several tabs and accounts open.
- **path:** browser-harness → mac-vision → relay-realtime → pendant → mac-planner
- **model tier:** background/local extraction for account and workspace signals; realtime only when the owner is waiting for a spoken go/no-go answer
- **latency:** Under 3 seconds for a preflight on a loaded tab; immediate pendant warning if a mismatch is detected
- **cost:** About $0.005–$0.03 per preflight; DOM extraction and account-identity comparison dominate
- **security:** Identity signals are sensitive. Keep only a salted account fingerprint and origin, never passwords or full profile data; owner supplies per-origin selectors/rules. A mismatch should warn, not silently switch accounts or alter the page.
- **missing:** per-origin account/workspace identity extraction rules configured by the owner; a browser preflight hook that runs before any mutating action; a cross-surface identity comparison against the spoken target/project and selected Mac context; a high-priority pendant warning with the origin, detected account label, and requested target

### "Compare the two pages I have open and tell me whether they disagree about any important date, amount, status, or name; quote each source and save a short discrepancy note to my Mac if there is one."
- **useful because:** The owner often has a source page and a dashboard, confirmation, or message open at the same time. No single browser read can notice that two private pages contradict each other; this catches stale reservations, wrong totals, and status mismatches before the owner acts.
- **path:** browser-harness → relay-realtime → mac-planner → pendant
- **model tier:** background model for structured extraction and contradiction checking; realtime for the concise spoken result
- **latency:** 10–30 seconds for two pages; under 2 seconds to acknowledge the request
- **cost:** About $0.02–$0.08 per comparison; extracting and normalizing both pages dominates
- **security:** Do not retain full pages; persist only redacted claim/value pairs, source URLs, hashes, and the owner-approved discrepancy note. Never infer that a mismatch is fraud; present evidence and confidence.
- **missing:** multi-tab capture in one consistent browser snapshot; claim extraction with source spans and normalization for dates/currency/names; contradiction scoring and stale-page detection; a Mac note artifact linked to the exact browser evidence capsules


## Changes it proposed to its own stack

### `browser-harness` — Make every browser read/click operation bind to the extension-reported active tab by default, and update the durable session record atomically after list_tabs/navigation/read. Today the live result reports active tab 1419527 while the returned default session still points at stale tab 1403455/example.com; add a visible mismatch receipt and self-heal instead of silently targeting stale state.
- **owner gets:** When the owner says “what am I looking at?”, the answer will describe the page actually in front of them—not an old tab left over from a previous task.
- effort: Medium: reconcile browserBridge session binding, tab-list result handling, and receipts; add regression tests against two-tab Safari state.  ·  risk: A navigation or read could target a different active tab if Safari changes focus mid-command. Recover by requiring tabId captured in the same list/read transaction and report a mismatch rather than guessing.
- cost: Negligible API cost; one extra tab-list or active-tab check per operation.  ·  latency: Adds roughly 0.5–1.5 seconds when a fresh tab snapshot is required.
- security: Improves security by preventing stale authenticated-tab targeting; does not broaden origin access.
- depends on: browser extension tab list and read_page results; atomic session receipt/state update

### `browser-harness` — Add a first-class multi-tab evidence bundle: capture an ordered set of tabId, URL, title, content hash, and redacted text spans in one operation, with a single timestamp and snapshot-consistency marker. Expose the bundle to the planner and Mac note writer instead of forcing separate browser_read_page calls whose tabs can change between reads.
- **owner gets:** When the owner asks whether two private pages agree, the answer will be based on what was actually visible at the same moment, with citations they can open—not on a race between changing tabs or an untraceable summary.
- effort: Medium-high: extension command schema, browser bridge aggregation, redaction, evidence-capsule linkage, and note artifact formatting.  ·  risk: One page may fail or contain sensitive text. Return partial bundles with explicit missing-tab status and retain only redacted spans; never silently substitute a different tab.
- cost: One model invocation can replace multiple page summaries; storage is small if hashes and selected spans are retained.  ·  latency: Parallel tab reads should take about 1–3 seconds, versus serial reads.
- security: Improves provenance and minimizes retention, but bundles cross-origin private content; require the owner’s per-origin rules and encrypt persisted artifacts.
- depends on: browser_read_page with explicit tabId; browser evidence capsules and redaction; planner access to browser receipts; Mac note creation


## What it asked for

### `c16-nvsd` (context) — owner-approved browser origins and retention rules
- why: Live Safari access now works, but useful authenticated automation needs to know which origins may be read, what may be spoken, and what may be persisted; inventing these would risk secrets.
- would change: Until supplied, I will only demonstrate on the currently visible public tabs and propose an empty explicit configuration rather than automate logged-in sites.

## Its own summary

Live browser access is confirmed: Safari has two tabs, and POST /execute browser_list_tabs plus browser_read_page returned the active YouTube page with an evidence capsule. I recorded four owner-facing proposals: cross-surface authenticated decision packets, authenticated/local change deltas, staged form filling with preview/undo, and a pendant-triggered current-page attention brief; I also proposed fixing stale default-tab binding so “what am I looking at?” cannot read an old tab. I told faculty-judgement the browser path is working and queued a request for the owner’s explicit per-origin read/speak/retention rules.

**Biggest unknown:** Which authenticated origins the owner actually wants automated, and which content categories may be spoken or persisted. Until the owner supplies that configuration, only public/current-tab demonstrations are safe.

