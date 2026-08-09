# Harness derivation — mac-planner — round 230

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac accessibility and screen state** — AI Pendant Agent currently has Accessibility and Screen Recording trusted; synthesized input posted successfully, secure input is off, Safari is foreground, and 19 apps are running. The granted mac_readonly_inspect browser_tabs/accessibility_enabled selectors are currently ambiguous/unresolved despite GET /observe containing this data.
  - evidence: mac_readonly_inspect foreground_app invoked GET /observe at 2026-08-08T22:44:28.520Z and returned accessibility.trusted=true, screenRecording=true, inputReachability.status=verified, foregroundApp=Safari.

## Capabilities it proposed

### "When I press the pendant bookmark button, turn that moment into a usable task: tell me what I just marked, attach the active Mac/browser context, and either create a dated reminder or leave a clearly named draft for me."
- **useful because:** The button already gives the owner a durable moment marker, but today it stops at an event. This closes the loop from fleeting thought to an actionable artifact without requiring the owner to repeat context or find the right app.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime tier only to acknowledge the button and classify a short spoken follow-up; use a cheaper background model to extract task/date/context and rank ambiguity. Mac performs the deterministic reminder or draft operation.
- **latency:** A local LED acknowledgement is immediate; context capture and a proposed task within 5 seconds; execution only after the owner's configured policy permits that destination.
- **cost:** Roughly $0.01–$0.05 per marked moment depending on whether speech/context interpretation is needed; Mac/browser reads and reminder creation dominate neither token nor latency cost.
- **security:** The context capsule must contain only active app, URL/title and a bounded redacted selection, never cookies or page contents by default. Creating reminders is low impact; sending messages or submitting forms must remain an explicit separate action. Expire capsules and show the exact artifact before high-impact destinations.
- **missing:** A relay API that joins offline_moment_bookmark records with a short owner utterance and a bounded Mac/browser context capsule; A typed destination policy for reminder versus draft, configurable by the owner rather than inferred from FULL_CONTROL_MODE; A deterministic postcondition receipt proving which reminder/draft was created

### "Before I leave for a meeting or trip, prepare my departure pack: check the calendar event, find the relevant files and authenticated browser tabs, make a small offline folder on the Mac, and tell me on the pendant what is missing."
- **useful because:** Leaving the desk is where context is lost. This combines the calendar's intent, the Mac's local files and the browser's private session into one bounded, inspectable handoff instead of making the owner hunt through three surfaces.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model ranks likely relevant files/tabs from deterministic metadata; realtime tier only handles a follow-up question. Mac creates the pack atomically and the pendant receives a short missing-items summary.
- **latency:** Generate a preview in under 10 seconds; atomic pack creation in under 3 seconds after confirmation; no network-dependent claim that the private browser content was copied unless the browser explicitly exports it.
- **cost:** About $0.02–$0.08 per pack; file/tab metadata is cheap, while summarizing the event and missing items is the main model cost.
- **security:** Never export cookies or authenticated page bodies into the pack. Browser items should be URL/title/owner-selected export only. Use an allowlisted workbench root, hash every file, and expire packs after the event. The owner must see a manifest before any browser download or external share.
- **missing:** Calendar-to-event relevance matching that can be overridden by the owner; A browser command to export an owner-selected authenticated document without exposing session credentials; A pendant delivery path for the compact checklist when LTE is unavailable; A dashboard manifest/expiry view

### "When I ask the pendant “what did I decide about X?”, search my captured moments, calendar/mail context, Mac notes, and the browser session history, then answer with a short decision card showing the evidence, date, and what remains unresolved."
- **useful because:** People remember the conclusion but not why they made it. A spoken answer grounded in the owner's own records is more useful than a generic search result, especially when the evidence is split between a private browser session and local Mac data.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap retrieval/reranking model over redacted metadata and snippets; invoke realtime only to resolve an ambiguous entity or read the final card aloud. Keep source extraction deterministic and attach citations before generation.
- **latency:** Return an initial answer within 4 seconds and source references within 8 seconds; if a private browser source is unavailable, say so rather than hallucinating continuity.
- **cost:** Approximately $0.01–$0.04 per query; retrieval and snippet transfer dominate more than generation.
- **security:** Search only the owner's pre-authorized account scope and local stores. Do not send full mail bodies or browser HTML to the relay; use local redaction and short snippets. Every claim must carry a source timestamp and confidence, and the owner must be able to delete the generated card.
- **missing:** A unified, provenance-preserving search index spanning /capture, mac_read_sources, browser session claims, and context-graph entities; A browser-side history/decision export limited to explicitly enabled domains; current tabs alone cannot establish past decisions; A citation-bearing response schema and retention/deletion controls; A relay route that can request Mac-local retrieval while keeping private snippets on the Mac

### "Let me ask the pendant to explain the authenticated page I am looking at without sending that page to the relay: read the selected region or owner-approved fields locally on the Mac, answer aloud, and optionally produce a redacted citation."
- **useful because:** The browser holds sessions that the relay should never receive. Today the owner must either expose the page to a remote model or manually copy it out. A local interpretation path would make the private browser genuinely useful as part of the hive rather than an isolated surface.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Run extraction and summarization on a local Mac model or local inference service; use the realtime tier only for the short spoken request and response orchestration. Never transmit raw authenticated page content by default.
- **latency:** Answer in 3–8 seconds for a selected region or bounded form; full-page interpretation may take 15 seconds and should visibly show progress.
- **cost:** Near-zero relay token cost when local inference is available; otherwise a small per-query cost only for an explicitly approved redacted excerpt. Local GPU/CPU time is the main cost.
- **security:** Require an owner-selected DOM region or fields, redact secrets and personal identifiers before any citation leaves the Mac, and maintain a visible local-only indicator. Do not permit hidden page-wide scraping or action execution from the interpretation result.
- **missing:** A browser-extension command that returns a bounded, owner-selected semantic region rather than an ambiguous whole-tab inspection; A Mac-local inference endpoint or model runtime with a strict no-upload mode; A relay request/response type that distinguishes local-only content from shareable citations; A visible privacy indicator and deletion policy for temporary extracted text

### "Show me exactly what information left my Mac this week through the pendant system: which browser fields, files, mail snippets, and generated summaries were shared, with destination, purpose, timestamp, and a one-tap revoke/delete action where possible."
- **useful because:** The owner cannot meaningfully trust a hive with private browser and mail access unless it can answer the reverse question: what crossed a boundary? Existing job receipts describe actions, not the data exposure represented by those actions.
- **path:** dashboard → relay → mac-planner → browser-extension → pendant
- **model tier:** Use deterministic local event logging and classification; use a cheap background model only to turn event codes into plain-language explanations. Realtime is unnecessary except for an owner-requested spoken summary.
- **latency:** A seven-day report should render in under 3 seconds from local indexes; live logging must add less than 50 ms to an action.
- **cost:** Negligible model cost when classifications are structured; storage is bounded by retention and event summaries are small.
- **security:** The ledger itself is sensitive and must remain local by default, encrypted and purgeable. Record hashes and categories instead of duplicating raw content. Tamper-evident chaining is needed so the report cannot falsely claim that nothing was sent. Revocation must be honest: delete local copies and cancel queued jobs where possible, but never claim recall from a third-party service.
- **missing:** A mandatory outbound-data event emitted by every Mac, browser, relay, and workbench operation; A common schema for field categories, destination, purpose, consent/policy source, and content hash; Browser instrumentation that records selected-field export without cookies or raw page persistence; A dashboard report and pendant summary path with purge/revoke controls

### "When the pendant or Mac stops responding, let me ask “why?” and get a truthful end-to-end diagnosis: whether the failure is button capture, audio encode/decode, radio/link, relay queue, browser bridge, or Mac execution, plus the last verified stage and the safest recovery step."
- **useful because:** Today a silent failure looks the same whether the pendant never captured a button, the relay dropped a job, or the Mac acted and the result was lost. A wearable owner needs one answer that spans every node, not separate technical logs.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Collect structured health counters and correlation IDs deterministically; use a cheap diagnostic model to rank likely causes and phrase the explanation. Realtime only reads the short diagnosis aloud when asked.
- **latency:** Return the last-known diagnosis in under 2 seconds; an active probe may take up to 10 seconds and must not disturb an ongoing call.
- **cost:** Low ongoing cost because counters and receipts are structured; occasional diagnostic summarization costs cents at most.
- **security:** Diagnostics must redact audio, mail, page content, and tokens. Active probes need bounded, non-destructive fixtures. Preserve uncertainty and timestamps rather than inventing a root cause; expose raw correlation IDs for audit.
- **missing:** A single correlation ID propagated from pendant button/audio frames through relay, browser command, and Mac job receipt; A signed health envelope from the pendant and bridge, including queue depth and last successful stage; A relay graph query that joins pipeline events, job receipts, browser results, and pendant acknowledgements; A user-facing diagnosis policy that distinguishes stale telemetry from an active failure


## Changes it proposed to its own stack

### `integration` — Build a Mac-local provenance index that ingests bounded Calendar/Mail snippets, capture records, browser claim capsules, and workbench receipts into a single append-only event stream. Each event carries source surface, timestamp, retention class, redaction status, and a stable hash; the relay receives only IDs, summaries, and citations. Add a query endpoint that returns evidence bundles rather than unconstrained text.
- **owner gets:** The owner gets answers that can point to exactly where a remembered decision came from, while private browser and mail content stays on the Mac. It also makes interrupted jobs and pendant bookmarks explainable instead of disappearing into separate logs.
- effort: Medium-high: local schema and ingestion adapters, deduplication, retention UI, relay query protocol, and tests for redaction and clock skew.  ·  risk: Incorrect entity matching could merge unrelated decisions; preserve source links and confidence, never silently overwrite events, and allow deletion by source. If indexing fails, existing stores remain authoritative and queries degrade to source-specific results.
- cost: Low ongoing API cost; local SQLite/index storage grows with metadata and snippets, bounded by retention. One background embedding/rerank call may cost cents per query, but lexical retrieval should be the default.  ·  latency: Adds under 200 ms for local retrieval and a few seconds only when a model must synthesize evidence.
- security: Improves privacy by keeping raw content local, but creates a concentrated sensitive index. Encrypt at rest, enforce account_scope, redact before relay, and expose a one-click purge and retention policy.
- depends on: Owner-configurable source scopes and retention classes; A browser extension event/capsule export with no cookies or raw HTML; A relay endpoint for citation-bearing evidence bundles; mac_read_sources and existing /capture records


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: local-only authenticated-page interpretation, an outbound-data provenance ledger with honest revoke/delete semantics, and a cross-node hive failure diagnosis spoken through the pendant. Each explicitly names the missing cross-surface contracts rather than assuming current wiring is sufficient.

**Biggest unknown:** Whether any of these concepts collide with an unobserved backlog entry; discovery tools were removed as instructed, so I did not inspect further.

