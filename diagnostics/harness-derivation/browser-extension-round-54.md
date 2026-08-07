# Harness derivation — browser-extension — round 54

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — At 2026-08-07T11:08Z, /browser/status reports Safari device absent/offline and only home-chrome registered offline; tabCount/tabId are null and there are 3 pending browser commands. No authenticated page can be read until Safari heartbeats again.
  - evidence: GET /browser/status returned online:false; devices:[home-chrome online:false, tabId:null, tabCount:null]; pendingCommands:3.

## Capabilities it proposed

### "“Save this page for me.” Later: “Remind me what I saved and why.”"
- **useful because:** The browser is the only node that can see the owner's authenticated page, while the pendant is the only node that can bring the saved context back hands-free. This turns a fleeting private webpage into a provenance-preserving, searchable personal bookmark rather than an opaque URL that may expire or require the same tab session.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → unified
- **model tier:** Use the cheap background tier to extract and normalize the page; use realtime only when the owner asks by voice for a saved item. The background pass should identify title, canonical URL, selected/most relevant passage, page timestamp, and an optional local screenshot, then generate a short spoken recall card.
- **latency:** Capture acknowledgement under 2 seconds after the extension is online; extraction and indexing in under 15 seconds. Voice recall should start within 1 second and stream the answer while the relay fetches the cited local capsule.
- **cost:** Roughly $0.002–$0.02 per save depending on page length and whether OCR/screenshot understanding is needed; recalls are usually under $0.01. The dominant cost is page extraction/context tokens, not the small metadata record.
- **security:** Authenticated DOM and screenshots remain on the Mac in an encrypted, expiring evidence capsule; the relay receives only a minimal redacted summary, opaque capsule ID, and hashes unless the owner explicitly asks for the full passage. Detect and redact secrets, payment data, and session tokens before any relay sync. Show source URL, capture time, and excerpt on recall; support immediate delete and TTL. Saving is reversible, but never follow page links or perform actions as part of capture.
- **missing:** A browser-extension command/event for “save current page” with optional user-selected text and active-tab identity.; A local evidence-capsule index that links page excerpts to the owner's memory graph and supports deletion/TTL, rather than only per-job inspection records.; A relay endpoint and pendant audio-card protocol for retrieving a capsule by ID or semantic query without uploading raw authenticated content.; A voice intent and review UI to list, rename, expire, or delete saved pages.

### "“Is this option on the page compatible with my schedule and constraints?” For example, while viewing a logged-in travel, appointment, or purchase page: “Can I do this?”"
- **useful because:** Today the browser can see the private offer and the Mac can see local calendar/files, but neither can join those facts into a timely answer while the owner is hands-free. This would turn a private page into a decision rather than forcing the owner to copy dates, prices, and terms between apps. It deliberately answers and prepares evidence without changing the booking, order, or calendar.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → unified
- **model tier:** Realtime handles the owner's short question and routes extraction; a cheaper background model normalizes page fields and compares them with calendar, reminders, preferences, and local documents. Escalate to the expensive tier only when terms are ambiguous or sources conflict.
- **latency:** A spoken first answer in 2–4 seconds using visible page text and cached local context; a sourced, complete comparison in under 15 seconds. The owner can interrupt or ask for one field at a time.
- **cost:** Approximately $0.005–$0.04 per comparison. Page extraction and document/calendar context dominate; most straightforward date/price comparisons should use deterministic code plus a cheap model.
- **security:** Raw authenticated page text stays on the Mac wherever possible. Send the relay only the question, normalized fields, and minimal redacted context needed for speech. Treat prices, health/appointment details, and travel identity as sensitive; show citations and freshness. Never click purchase, reserve, submit, accept terms, or modify the calendar. If the page is ambiguous or stale, say so rather than infer.
- **missing:** A browser-side “current page/selection context” capture that can return structured fields and citations without requiring navigation or form mutation.; A local constraint resolver joining browser fields with Calendar, reminders, budgets/preferences, and relevant files, with freshness and conflict reporting.; A relay protocol for streaming a compact evidence-backed comparison to the pendant, including page citations and uncertainty.; A unified voice intent that binds “this/that option” to the active tab or selected page region and keeps the decision read-only.


## Changes it proposed to its own stack

### `browser-harness` — Add a first-class browser_save_page action and extension-side capture event. The extension sends active tab identity, user-selected text (or bounded readable text), title, canonical URL, and a content hash; the Mac agent creates an encrypted local evidence capsule with redacted excerpt, screenshot reference, provenance, TTL, and a stable capsule ID. Add a lightweight pending-save queue so capture survives a relay hiccup, and expose capsule lookup/delete to the pendant relay. This is capture/indexing only: no navigation beyond the current page and no form submission.
- **owner gets:** The owner can say “save this” while looking at a private page and trust that the useful passage—not merely a fragile login URL—will be available later from the pendant, even after the tab closes or the website changes.
- effort: Medium: extension event/UI and content extraction, local encrypted capsule/index schema, redaction and TTL sweeper integration, relay lookup/delete routes, and pendant recall intent plus end-to-end tests across tab close and reconnect.  ·  risk: A buggy extractor could capture too much sensitive content or a stale page. Bound capture size, redact credentials/payment patterns, retain URL/title/time and hashes for provenance, make the capsule visibly deletable, and test queue replay/idempotency. Recovery is delete-and-recapture; no external mutation occurs.
- cost: Low ongoing API cost for metadata and short excerpts; occasional cheap extraction-model call. Local disk use is bounded by per-capsule size and TTL; screenshot storage should be opt-in and short-lived.  ·  latency: Immediate local acknowledgement; extraction/indexing completes asynchronously in roughly 5–15 seconds. Recall adds only local lookup plus a short background summary unless raw excerpt is requested.
- security: Improves privacy by keeping raw authenticated content on the Mac and syncing only redacted summaries/hashes. Requires encryption at rest, strict capsule access control, explicit TTL/delete propagation, and audit records for every read.
- depends on: A reliable browser command/event enqueue path and tab identity from the Safari extension; The existing evidence-capsule provenance/revocation primitives; A relay endpoint for capsule metadata and pendant voice recall; A typed save-page voice intent and dashboard review/delete UI


## What it asked for

_Nothing._
