# Harness derivation — unified — round 77

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I was offline—what happened while I was away?”"
- **useful because:** The worn device, always-awake relay, Mac job queue, and authenticated browser are the only combination that can reconstruct a trustworthy catch-up: held pendant alerts, completed or failed Mac/browser work, and private-page changes, each with a short spoken explanation and a receipt. It prevents missed work without pretending queued actions succeeded.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model builds the digest and clusters duplicate events; realtime is used only when the owner asks from the pendant for a low-latency spoken answer.
- **latency:** Return the first three high-confidence items in under 3 seconds from indexed receipts; complete browser/account reconciliation in the background within 1 minute. Pendant should play a concise 30–45 second summary and offer item-by-item follow-up.
- **cost:** About $0.01–$0.05 per catch-up depending on browser-page extraction; receipt/event indexing is local or relay-side and dominates no model cost. Realtime cost is limited to the brief spoken query.
- **security:** Only inspect browser sessions explicitly marked available to the agent; never include secret values in the digest. Separate 'observed', 'attempted', and 'completed' states, cite job IDs/URLs and timestamps, and require confirmation before any retry, send, delete, or purchase. Expire audio and raw page extracts quickly.
- **missing:** A durable cross-surface event index joining pendant alert IDs, relay jobs, Mac receipts, and browser command results; A typed outcome schema distinguishing observed/queued/running/completed/failed/approval-required; An offline catch-up endpoint and pendant playback queue with deduplication and acknowledgement state

### "“Find the answer in my own stuff, and show me where it came from.”"
- **useful because:** Today the owner's answer is fragmented across Mac files and notes, currently-open authenticated browser pages, relay history, and snippets captured while the pendant was offline. No single node can search and reconcile those private sources with provenance. This capability would return a concise answer plus source-by-source evidence, explicitly marking conflicts and stale material instead of silently blending them.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheaper background model for indexing and candidate extraction; use the realtime tier only for the owner's spoken query and short answer. A stronger model is reserved for conflict resolution when sources disagree.
- **latency:** Answer from the local/private index in 2–4 seconds; if a logged-in page must be opened, speak an immediate progress acknowledgement and finish within 30 seconds. Evidence should remain available for review after the spoken summary.
- **cost:** Indexing is mostly local and incremental. Typical query costs $0.01–$0.04 for reranking and synthesis; authenticated page fetches and conflict resolution dominate. Do not send the full private corpus to the cloud.
- **security:** Build and query indexes on the Mac/relay with per-source sensitivity labels; raw browser content, audio, and secrets stay local unless the owner explicitly authorizes a source. Every claim needs a source locator, capture time, and freshness; exclude secret facts from spoken output by default. Require confirmation before opening a new private site or using a finding to send, delete, purchase, or change anything.
- **missing:** An on-device/private hybrid index spanning Mac workspace files, browser extraction results, relay records, and explicitly retained pendant snippets; A common evidence schema with source locator, capture timestamp, content hash, freshness/expiry, sensitivity, and claim-to-source links; A retrieval route and spoken citation format that can reference a file, tab, or timestamp without leaking its contents; Incremental change notifications from the Mac and browser so the index does not become silently stale


## Changes it proposed to its own stack

### `relay` — Add a durable cross-surface outcome ledger and catch-up projection. Normalize pendant held-alert events, /jobs state and receipts, /pipeline events, and browser command results into one append-only record keyed by a stable correlation ID. Materialize per-owner 'since last acknowledged' items with source, timestamp, status (observed/queued/running/completed/failed/approval-required), evidence link, sensitivity, expiry, and dedupe key. Expose GET /catch-up and POST /catch-up/:id/ack; never infer completion from a timeout or HTTP 200. Feed the projection to background digest generation and the pendant's replay queue.
- **owner gets:** After a dropped LTE link, sleeping Mac, or offline browser extension, the owner can ask once and hear exactly what arrived, what actually finished, and what still needs approval—without duplicate alerts or falsely claiming success.
- effort: Medium: event adapters for existing pipeline/jobs/browser routes, D1/R2 schema and idempotent upserts, projection tests for reconnect/replay, then a small pendant acknowledgement protocol. No GUI automation permission is required.  ·  risk: Out-of-order and duplicate events could produce misleading summaries; mitigate with monotonic event timestamps plus source sequence numbers, explicit unknown state, and immutable raw evidence. If the ledger is unavailable, retain current per-surface behavior and do not block live speech. Recovery is replay from existing job/pipeline records.
- cost: Negligible storage/indexing cost; roughly a few hundred bytes per event plus short-lived evidence pointers. One cheap background summarization call per catch-up batch; no Realtime call unless spoken interaction is requested.  ·  latency: Writes add under 50 ms asynchronously to existing event handling. GET /catch-up should be sub-200 ms from the materialized projection; browser reconciliation remains asynchronous.
- security: Ledger must inherit source sensitivity and avoid copying raw page text or audio by default; encrypt at rest, enforce owner/session scoping, redact secrets in evidence, and apply retention/TTL per source.
- depends on: A stable correlation-ID propagated by pendant → relay → Mac/browser jobs; A documented browser result schema and receipt schema; The pending link-aware duplex governor for reliable replay under LTE loss

### `memory` — Create a private, provenance-first evidence graph separate from conversational memory. Mac indexing workers emit file/note metadata and bounded excerpts; the browser bridge emits normalized page regions and locators; relay imports job/pipeline receipts and only pendant snippets explicitly marked retain. Each evidence item gets a content hash, source URI/tab or file locator, capturedAt, lastVerifiedAt, sensitivity, TTL, and deletion tombstone. A claim index stores only links to evidence IDs, never an untraceable model summary. Add source-scoped retrieval, freshness checks, conflict sets, and a citation renderer usable by voice and dashboard. Support rebuild from source adapters after corruption and immediate tombstoning when the owner deletes or revokes a source.
- **owner gets:** The owner can get a reliable answer from their own scattered information and inspect exactly which file, logged-in tab, job receipt, or retained pendant moment supports it—rather than receiving a confident but unverifiable blend of stale private data.
- effort: High: local indexing and file-watch adapters, browser extraction contract, receipt import, encrypted vector/keyword indexes, claim provenance storage, deletion propagation, and voice/dashboard citation UX. Requires an explicit retention/consent control for pendant snippets.  ·  risk: Indexing can expose sensitive data through embeddings, stale files can be mistaken for current truth, and browser DOM changes can break locators. Mitigate with local encryption, source-level opt-in, TTL and last-verified gates, hash-anchored excerpts, a visible stale/conflict state, and fail-closed retrieval when provenance is missing. If an adapter fails, omit that source and say it was unavailable.
- cost: One-time local CPU/storage cost and incremental background indexing; roughly 100–500 MB for a typical workspace, plus small relay metadata. Query synthesis is usually a low-cost model call; private raw content should not be uploaded. Hardware cost is none initially.  ·  latency: File and receipt updates are asynchronous. Local keyword/vector retrieval should add under 500 ms; browser-only sources can add 5–30 seconds and must be reported as pending rather than blocking the first answer.
- security: High sensitivity: this becomes a map of the owner's private life. Encrypt indexes and evidence, isolate browser-session tokens from the index, enforce per-source permissions, redact secrets, audit every retrieval, and offer a physical pendant privacy control that disables retained-snippet ingestion.
- depends on: A stable evidence schema and source adapters for Mac, browser, relay, and pendant; Owner-configurable retention and deletion propagation; A citation-capable response format in the pendant and dashboard; A local/private embedding or keyword-index service


## What it asked for

### `t11-iqwz` (tool) — catch_up_status
- why: The owner needs a single spoken answer after offline periods that merges held pendant alerts, relay/Mac job receipts, pipeline outcomes, and browser command results without making the realtime agent manually join four stores or guess completion.

```json
{
  "since": "string, optional ISO-8601 timestamp; defaults to last owner acknowledgement",
  "limit": "integer, optional 1-20, default 8",
  "include_pending": "boolean, optional, default true",
  "include_sources": "array of strings, optional enum pendant|relay|mac|browser"
}
```

## Its own summary

Round 77 produced a new offline catch-up capability and a relay change: a durable, deduplicated outcome ledger joining pendant held alerts, Mac/relay receipts, pipeline events, and browser results, plus a spoken “I was offline—what happened?” projection. I also queued the missing `catch_up_status` tool schema. The current live system still shows the browser extension offline with five pending commands, while the Mac bridge is online; existing pipeline history also contains processing/late-delivery records, making explicit outcome states important.

**Biggest unknown:** Whether the orchestrator will implement the cross-surface ledger and catch-up tool, and what stable correlation/acknowledgement IDs the pendant firmware currently emits. I still do not need Accessibility permission for this design; it works through existing receipts and browser/session APIs.

