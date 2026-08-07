# Harness derivation — browser-extension — round 43

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m looking at this in Safari—give me the useful parts, compare it with my calendar and local files, and leave me a short audio summary I can hear on the pendant.”"
- **useful because:** This turns the private browser session into an immediate, cited cross-surface answer: the browser is the only node that can see logged-in content, the Mac can correlate it with local documents and calendar, and the relay/pendant can deliver the result without making the owner read a long page. It is read-only and useful even when the site has no API.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Use a cheap background extraction/summarization model for page text and local-file/calendar correlation; use realtime only to interpret the owner's spoken scope and deliver the final short spoken answer. Escalate to a stronger model only when page structure or cross-source conflicts are ambiguous.
- **latency:** Capture and extraction in 10–30 seconds for a normal page, correlation and audio generation in another 5–15 seconds; give a spoken progress acknowledgment if Safari is slow. Never submit forms or send messages as part of this capability.
- **cost:** Roughly $0.01–$0.08 per invocation depending on page length and whether local correlation needs a second pass; most cost is text extraction/summarization, not the brief realtime response.
- **security:** Authenticated page text, local file snippets, and calendar metadata leave the device only to the relay/model needed for the answer. Minimize by extracting only the active tab and explicitly requested fields, redact credentials/tokens, retain the cited result briefly, and include URL/title/timestamp and source excerpts so the owner can verify. Read-only by default; any later action such as replying or booking must be a separate request and stop before submission.
- **missing:** A reliable live browser enqueue/heartbeat path: the current status reports Safari absent/offline and three pending commands, so active-tab capture cannot currently be trusted.; A single cross-surface job schema that binds the browser tab, Mac correlation sources, and pendant audio result with provenance and expiry.; A small audio-queue handoff from relay to pendant for generated summaries, including cancellation and replay of the last result.

### "“Make an evidence packet for this problem: collect the relevant pages from my logged-in browser and matching local documents, preserve the exact wording and timestamps, redact secrets, and leave me a file I can review and send.”"
- **useful because:** Today the system can at most summarize private pages or prepare isolated drafts. The owner cannot reliably turn scattered authenticated web records and local files into a verifiable, reviewable packet for a refund dispute, warranty claim, travel cancellation, or support escalation. Exact source captures plus provenance are materially more useful than an AI paraphrase.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal
- **model tier:** Use a cheaper background model for source discovery, deduplication, redaction suggestions, and chronology. Use the realtime tier only for the owner's spoken request and a concise completion report; use a stronger model only to resolve conflicting dates or identify missing evidence.
- **latency:** One to three minutes for a typical packet, with progress updates if multiple authenticated tabs or documents are involved. The owner should be able to review the output asynchronously rather than wait on a live conversation.
- **cost:** Approximately $0.03–$0.20 per packet, dominated by OCR/page extraction and document processing; local hashing and bundling should be performed on the Mac with negligible API cost.
- **security:** Private page contents and local documents are sensitive. Keep raw captures on the Mac where possible, send only selected text or hashes for reasoning, redact credentials, session tokens, payment numbers, and unrelated personal data, and encrypt the resulting bundle at rest. Include source URL/title, capture time, local file path, and cryptographic hashes. Never send the packet or upload it without a separate explicit request.
- **missing:** A provenance-preserving capture/bundling service that can combine authenticated browser snapshots with local files and produce an encrypted, redacted export.; On-device secret/PII detection and an owner-editable redaction review before export.; A durable Mac artifact and pendant notification path so the packet remains available after the live job ends.


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-bridge liveness and recovery protocol, distinct from the job queue: each extension heartbeat reports a device lease, active tab inventory, protocol version, and last-seen command cursor; when the lease expires, the relay marks pending commands as stale, stops waiting, and requires a fresh session snapshot before replaying only idempotent reads. On reconnect, reconcile command results by request ID, discard orphaned results, and expose a clear “Safari unavailable / 3 stale commands” state to the Mac and pendant instead of silently timing out.
- **owner gets:** The owner will not lose time wondering whether a private-page answer ran, and a Safari reconnect cannot unexpectedly execute old browser operations against a new tab. Once recovered, read requests resume automatically and the owner gets an honest status and receipt.
- effort: Medium: extension heartbeat/schema update, relay lease and cursor state, stale-command reconciliation, and a small status surface in the Mac/pendant brief. Add fault-injection tests for sleep, Safari restart, tab replacement, duplicate results, and reconnect after timeout.  ·  risk: A reconnect may leave a requested read incomplete; recover by explicitly reporting it and offering a fresh read. Never replay non-idempotent browser mutations automatically. Cursor bugs could suppress a result, so retain a short-lived audit record and provide manual retry.
- cost: Low ongoing API/storage cost: heartbeat traffic and a few small D1/R2 records; approximately <$0.001 per active device-day. Engineering cost is mainly protocol and failure-mode testing.  ·  latency: Heartbeat state is immediate; a recovered read adds roughly one heartbeat interval (target 2–5 seconds), but avoids the current 45-second blind timeout.
- security: Improves security by preventing stale commands from applying to a different authenticated tab/session. Device leases and command IDs should be opaque, and page content remains end-to-end scoped to the requested job.
- depends on: A functioning extension enqueue/poll path and Safari heartbeat reporting; The existing browser request IDs/tab affinity and receipt infrastructure; A shared job status projection consumed by Mac and relay

### `integration` — Add a local-first evidence-bundle pipeline shared by the browser and Mac surfaces. It should accept a set of browser page captures and local files, normalize them without rewriting originals, compute SHA-256 hashes and capture metadata, detect likely secrets/PII, generate a redacted review copy plus an encrypted manifest, and expose a review/edit/export state machine. The relay receives only the task description and derived findings unless the owner explicitly chooses to export raw material.
- **owner gets:** The owner gets a trustworthy folder they can inspect and attach to a dispute or support request, rather than an unverifiable AI summary or a pile of screenshots with unclear dates. They can correct redactions before anything leaves the Mac.
- effort: Medium-high: local artifact format, browser snapshot adapter, file-selection and redaction UI, hashing/manifest logic, encrypted storage, and tests proving originals are unchanged and exports are reproducible.  ·  risk: Over-redaction could remove useful evidence; preserve originals locally and let the owner adjust the review copy. Under-redaction could expose sensitive data; default to conservative detection, visibly mark uncertain fields, and require review before export. Browser reconnects or changed pages could create an incomplete chronology; label every missing or stale source.
- cost: Low runtime API cost; local hashing, OCR, and packaging use Mac CPU/storage. Engineering cost is the main expense. Typical packets should be tens of MB at most, with configurable retention and deletion.  ·  latency: A small packet can be ready in under a minute; OCR or many pages may take several minutes asynchronously. Pendant gets an immediate acknowledgment and a completion notification rather than blocking the conversation.
- security: Strongly improves containment by keeping raw authenticated content local, encrypting artifacts, minimizing relay payloads, and making every exported field auditable. No automatic upload, submission, or message sending.
- depends on: A reliable authenticated browser capture path; Mac-local encrypted artifact storage and a review surface; Shared provenance metadata across browser and Mac jobs


## What it asked for

_Nothing._
