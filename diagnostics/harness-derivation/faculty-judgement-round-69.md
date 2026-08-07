# Harness derivation — faculty-judgement — round 69

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before I head out, make sure this appointment or trip is actually ready.”"
- **useful because:** It prevents the costly failures a generic morning brief misses: a calendar time that differs from the booking, a changed gate or address buried in logged-in mail, a missing preparation item, or weather/traffic that changes when the owner must leave. The pendant gives a natural, hands-free request; the relay can continue checking after the owner walks away; the Mac and authenticated browser can inspect private sources together. It reports only contradictions or time-critical exceptions, with a short spoken plan, rather than another noisy digest.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard-ux
- **model tier:** Use the cheap background model for scheduled/pre-departure reconciliation and extraction; reserve realtime only for the owner's follow-up questions or a last-minute voice exchange.
- **latency:** Initial answer under 15 seconds when sources are already open; up to 2 minutes in background for re-checks. Pendant response is one short sentence plus an optional queued detail brief.
- **cost:** Roughly $0.01–$0.05 per check depending on number of private pages and web lookups; browser extraction and TTS dominate, not the planner model.
- **security:** Private calendar/mail/reservation content stays on the Mac/browser bridge where possible; only normalized fields, contradictions, and citations go to relay. Never book, cancel, send, or edit without explicit confirmation. Location and travel details need short TTL and deletion controls.
- **missing:** A typed cross-source itinerary object linking calendar event, email confirmation, browser reservation, and optional map/weather facts; A discrepancy/risk evaluator with freshness and confidence, distinct from a generic daily briefing; A departure-triggered scheduler and pendant audio queue with explicit playback acknowledgement; Owner-configurable travel radius, preferred buffers, and quiet-hour/urgency policy; A provenance-rich short spoken receipt that names which source resolved each conflict

### "“After this trip or project, reconcile what actually happened and leave me only the loose ends.”"
- **useful because:** Today the owner must manually compare calendar plans, confirmation emails, authenticated booking/order pages, local files, and receipts. This capability would reconstruct the completed event, identify mismatches (changed/cancelled items, duplicate charges, missing refunds, unfiled receipts, promised follow-ups), and produce a short, prioritized loose-end list. It is post-event reconciliation—not a morning brief, page watch, generic inbox scan, or form-filling flow.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard-ux
- **model tier:** Use a cheap background model for extraction, entity matching, and prioritization; use realtime only if the owner asks a spoken follow-up or approves a draft.
- **latency:** A scheduled or manually started reconciliation may take 2–5 minutes; the pendant should immediately acknowledge scope and later speak a 30-second exception summary. Detailed evidence waits in a Mac workbench.
- **cost:** Approximately $0.03–$0.15 per reconciliation, dominated by authenticated page reads, OCR/document parsing if needed, and optional TTS; the planner model is a minor fraction.
- **security:** Receipts and account pages can expose financial and travel data. Keep raw pages and documents on the Mac/browser session; send only normalized entities, amounts, dates, and citations to the relay; redact payment credentials; retain a short-lived encrypted workbench. Never dispute, request a refund, submit reimbursement, or send mail without confirmation.
- **missing:** A cross-source event ledger that groups plans, confirmations, receipts, files, and follow-up promises under one event identity; Receipt/document extraction with currency, tax, refund, and duplicate detection plus provenance; A completion test that distinguishes planned, attended, cancelled, refunded, and unresolved items; A durable post-event trigger (calendar end, travel return, or owner command) and resumable background job; A review workbench that lets the owner dismiss, correct, or approve each loose end without losing source citations


## Changes it proposed to its own stack

### `integration` — Add an itinerary-reconciliation contract at the relay boundary. Each background check emits a signed, expiring record keyed by a stable event/reservation identity, with source facts (calendar, mail, browser, optional web), observedAt/freshUntil, normalized local times and addresses, confidence, and explicit conflicts. The relay should deduplicate equivalent facts, retain the source citation, and deliver an exception-only audio packet; if a check is interrupted, the next node resumes from the contract rather than restarting all reads.
- **owner gets:** When plans change across several services, the owner hears one trustworthy answer—what conflicts, which source is current, and what to do next—instead of reconciling tabs and messages themselves. It also prevents stale travel advice from being presented as current.
- effort: Medium: shared schema, source adapters, conflict rules, expiration handling, and a small dashboard inspection view; no Accessibility grant required for Calendar/Mail AppleScript paths, but private browser reads still depend on the bridge being online.  ·  risk: A false conflict could create unnecessary alarm, or a stale source could win. Mitigate with source-specific freshness rules, confidence labels, citations in every spoken item, and a safe 'could not verify' outcome. Interrupted jobs must never be treated as verified.
- cost: Negligible storage and model overhead; one compact normalized record per check. Background extraction costs remain proportional to private pages read; no realtime model needed unless the owner asks a question.  ·  latency: Adds milliseconds to reconciliation and avoids repeated reads on resume; first check remains bounded by Calendar/Mail/browser latency.
- security: Potentially sensitive itinerary data crosses the relay, so store only normalized fields with short TTL, encrypt at rest, redact message bodies, and bind records to the owner's authenticated session. Do not retain raw page content.
- depends on: An authenticated browser session/queue with stable tab identity and typed extraction results (chg-14accc01 / chg-16bc5dee); A durable background job and receipt path (cap-26c609fc and existing /jobs receipts); A compact provenance-aware context projection rather than full transcript injection (chg-a82e0b13 family); A pendant audio queue with playback acknowledgement

### `memory` — Create a privacy-preserving post-event reconciliation ledger. Give each planned or discovered event a stable eventId and store only typed claims—planned time/place, observed confirmation, attendance/completion signal, amount/currency, refund state, artifact hash, source URI, observedAt, freshness, and confidence. Let Mac, browser, and relay append claims; a background reconciler emits unresolved edges (missing receipt, conflicting time, unclosed promise, duplicate charge) and a cited review packet. Expire raw artifacts separately from the compact claims and allow one-tap dismissal/correction from the pendant or dashboard.
- **owner gets:** The owner gets closure after a trip or project instead of a pile of tabs, receipts, and half-finished promises. They see only what still needs action, with enough evidence to trust it, while sensitive raw documents do not become permanent memory.
- effort: High: define event identity and claim schema, adapters for Calendar/Mail/browser/files, entity matching and financial normalization, durable resumable jobs, and a review UI/audio protocol. This is connective infrastructure not present as one feature today.  ·  risk: Incorrect matching could merge unrelated events or falsely report a missing refund. Require confidence thresholds, preserve competing claims rather than overwriting them, show citations, and treat 'unverified' as distinct from 'failed.' Never initiate disputes, refunds, reimbursements, or messages automatically.
- cost: Small typed records are cheap; extraction/OCR and authenticated browser reads dominate per-event cost. Background model tier is sufficient; no realtime call unless the owner asks.  ·  latency: Initial reconciliation is minutes for a large event; incremental checks become seconds because claims and hashes avoid rereading unchanged sources.
- security: Financial and travel information must remain on-device/Mac where feasible. Relay receives redacted typed claims with short TTL; raw receipts use encrypted local storage and independent deletion. Event IDs must not expose account identifiers.
- depends on: A durable cross-surface job runner and resumable receipts; Authenticated browser sessions with stable tab/session identity; A compact provenance-aware context/memory service; Mac adapters for Calendar, Mail, and local receipt files; Pendant audio queue and dashboard review controls


## What it asked for

_Nothing._
## Its own summary

I discovered the owner profile and backlog, then added a new capability: a hands-free pre-departure readiness check that reconciles Calendar, Mail, authenticated reservations, and optional weather/traffic, reporting only contradictions and time-critical exceptions. I also proposed the integration contract needed to make this reliable: expiring, cited, confidence-scored itinerary facts that survive interruptions and produce an exception-only audio packet. This is distinct from generic morning briefs, page watches, and draft/submit workflows.

**Biggest unknown:** The actual cross-surface persistence and scheduling primitives remain unclear: whether there is already a durable event identity, source-specific freshness policy, departure trigger, and pendant playback acknowledgement. I still need those implementation truths—and the browser bridge's current authenticated/online state—to turn this into a concrete build plan. No further permission request is needed this round.

