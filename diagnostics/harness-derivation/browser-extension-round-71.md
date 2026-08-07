# Harness derivation — browser-extension — round 71

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Compare information on a logged-in web page with my local Mac files and tell me what does not match—for example, reconcile a private invoice or subscription page against downloaded receipts—without sending either source's raw contents to the relay."
- **useful because:** Today the browser can read a private page and the Mac can inspect local files, but there is no privacy-preserving cross-surface reconciliation. This would answer practical questions such as duplicate charges, missing receipts, or changed contract totals while keeping sensitive source material on the owner's devices.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** Use a background/cheaper model running on the Mac bridge for parsing, normalization, and matching; use the realtime tier only to interpret the spoken comparison goal and deliver the concise result. The relay should receive only a redacted result and provenance metadata.
- **latency:** 30–90 seconds for a normal invoice/receipt set; spoken acknowledgment within 2 seconds, followed by an asynchronous completion notice.
- **cost:** One small background extraction/matching call per source set, generally under $0.03; local file scanning and browser extraction dominate latency, not API spend.
- **security:** The browser and Mac must exchange typed, minimized records rather than page text or files. Keep raw HTML, screenshots, filenames, and financial identifiers local; redact account numbers and retain only fields needed for the comparison. Show source URLs and local-file references in the result, encrypt temporary working data, and expire it. Reading and reporting mismatches is reversible; any proposed correction, purchase, cancellation, or message must remain a separate owner-approved action.
- **missing:** A device-local privacy-preserving join service that accepts browser-extracted and Mac-extracted typed records and returns only mismatches, confidence, and source references; Browser extraction contracts that can identify relevant fields semantically while redacting secrets before leaving Safari; A Mac file-ingestion adapter with explicit folder/file scope, normalization of PDFs/CSVs, and temporary-data expiry; A cross-surface provenance schema linking a mismatch to a page region and local file without copying either raw source into relay context; A pendant-friendly asynchronous result and drill-down protocol for asking about one mismatch


## Changes it proposed to its own stack

### `browser-harness` — Add an offline-extension recovery supervisor. When a browser job sees /browser/status offline or a command timeout, it should (1) record the failed command without duplicating it, (2) ask mac-planner to bring Safari forward/open a neutral Start Page URL, (3) wait for a fresh extension heartbeat and tab identity, (4) rebind the job to that tab only if the URL/session policy still matches, and (5) retry idempotent reads once. Surface a clear pendant/Mac notice when recovery cannot establish Safari, rather than silently dropping the job.
- **owner gets:** Authenticated browser tasks would recover after sleep, Safari restart, or an extension hiccup instead of appearing randomly broken. The owner would not need to remember to open a tab, while private work remains in the existing Safari session and no mutation is retried blindly.
- effort: Medium: supervisor state machine in browser bridge/job runner, Mac open-URL handoff, heartbeat correlation, one-read retry tests, and a small status/receipt representation.  ·  risk: Opening Safari may reveal the browser UI at an inconvenient time; use a neutral URL and do not steal focus if the Mac harness supports background launch. Never retry clicks/types/submits automatically. If tab identity or URL policy changes, mark the job interrupted and retain the original receipt for review. Recovery is safe by canceling the supervisor and rerunning manually.
- cost: No recurring model cost; one local Mac action and a few lightweight HTTP polls per failed job. Minimal storage for recovery state.  ·  latency: Adds up to roughly 5–15 seconds only after a failure; healthy browser jobs are unchanged.
- security: Do not transmit page contents during recovery. Bind retries to extension device, tab ID, URL origin, and session ID; neutral bootstrap URL must not contain credentials or query secrets. Log only metadata and hashes.
- depends on: A reliable durable browser job/command record with idempotency and typed receipts; Mac action path capable of opening Safari without exposing page contents; Extension heartbeat carrying device, tab, and URL identity

### `integration` — Create a device-local 'private join' broker on the Mac bridge. Browser and Mac extractors submit separately scoped, typed records tagged with a one-time job key; the broker performs normalization, matching, and discrepancy detection locally, then emits only a redacted result containing mismatch IDs, confidence, and provenance pointers. The relay and pendant never receive raw page text, screenshots, filenames, or account identifiers. Add schema negotiation, field-level redaction, TTL deletion, and receipts proving which fields were compared.
- **owner gets:** The owner can reconcile private web accounts with local records without exporting either dataset to the cloud, turning two isolated surfaces into a trustworthy personal analyst.
- effort: High: local broker, browser and file adapters, PDF/CSV normalization, redaction rules, provenance pointers, temporary encrypted storage, and end-to-end tests for false matches and deletion.  ·  risk: Incorrect normalization could report a false discrepancy or miss a real one. Return confidence and supporting local references, never silently mutate anything, and preserve the original source data untouched. Abort and delete temporary records on schema mismatch or timeout.
- cost: No additional relay model cost for the join; modest local CPU/storage. Optional background model calls for parsing are the main API expense.  ·  latency: Adds local preprocessing, typically seconds; large PDF sets may take up to a minute.
- security: Raw private records remain on the Mac/Safari boundary. One-time job keys, encrypted temp storage, field-level redaction, TTL deletion, and metadata-only relay receipts are required. A compromised Mac still has access to the source files by definition, but the relay exposure is reduced.
- depends on: A browser semantic extractor that produces typed redacted fields; A Mac file-ingestion adapter for receipts/invoices; A durable cross-surface provenance and one-time job identity; An asynchronous result path to relay and pendant


## What it asked for

_Nothing._
## Its own summary

Round 71: discovered the live browser state and proposed a genuinely new browser-harness change. Safari is currently offline; the only registered device is offline home-chrome with no tab, while five browser commands remain pending and the session registry contains stale probe tabs. I recorded an offline-extension recovery supervisor: on read timeout, launch a neutral Safari page through the Mac, await a fresh heartbeat, verify device/tab/origin/session identity, and retry only idempotent reads once. I also notified mac-planner.

**Biggest unknown:** I still need a live Safari extension heartbeat with an open tab to verify end-to-end authenticated extraction and recovery. The implementation dependencies are durable idempotent browser jobs, background-capable Safari launch, and heartbeat/tab identity correlation; no further owner context is needed this round.

