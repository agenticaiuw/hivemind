# Harness derivation — browser-extension — round 118

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What’s waiting for me across my logged-in sites? Check every account I’ve connected, tell me only what is genuinely urgent, and keep anything that needs a reply ready for me to review.”"
- **useful because:** Today the browser can read specified origins, but nothing discovers or maintains the owner’s connected-account inventory, detects a quietly expired login, or preserves a cross-site review queue. This turns the pendant into a dependable private-account inbox without sending or submitting anything.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use the realtime tier only for the short spoken request and final summary; use a cheaper background model for origin classification, urgency scoring, deduplication, and draft composition. Browser extraction stays local to Safari; Mac handles any local attachment parsing; relay persists only compact evidence and drafts.
- **latency:** A spoken acknowledgement under 2 seconds; fan out authenticated reads in parallel and return a first summary in 20–45 seconds. If a site is logged out or slow, report that account separately and continue rather than blocking the whole run.
- **cost:** Roughly one background-model invocation per origin batch plus a small realtime turn; dominant cost is page text/context, capped by per-origin extraction and evidence snippets. No model call for unchanged pages after fingerprints match.
- **security:** Private page content and draft text must remain on the local bridge or encrypted relay job store with short retention. Store origin identifiers, not passwords or cookies. Detect login redirects and explicitly say “I couldn’t inspect this account”; never attempt login. Drafts are review-only and require a separate owner action before any send/submit.
- **missing:** A user-managed authenticated-origin registry with labels, allowed cadence, and per-origin privacy/retention settings; A session-health detector that distinguishes login redirects, consent pages, rate limits, and real content; A web-content urgency scorer and deduplicating review queue; A draft generator/store that links each draft to quoted source evidence and keeps it unsent; A durable fan-out job that can resume after Safari, Mac, or relay disconnects

### "“Save this private webpage as a sourced note on my Mac, including the important attachments, and tell me the key points from the pendant.”"
- **useful because:** The browser is the only surface that can see an already-authenticated private page, while the Mac is the only surface that can place a durable, searchable artifact in the owner’s files. Wiring those reaches together prevents losing a useful page when a session expires and gives the owner an auditable local copy without sending or submitting anything.
- **path:** pendant → browser-extension → mac-planner → mac-terminal → relay-realtime
- **model tier:** Use realtime only to acknowledge and speak the final short digest. Use a background model to select relevant sections, summarize attachments, and generate Markdown; use deterministic local code for download, hashing, and file placement.
- **latency:** Acknowledge in under 2 seconds; capture and write the note in 15–60 seconds depending on attachment count. If an attachment is inaccessible or the session expires, save the page note with an explicit missing-item record and continue.
- **cost:** One background summarization call per page plus one per non-text attachment; deterministic extraction and SHA-256 hashing dominate neither API cost nor latency. Context is bounded by selected sections and attachment size caps.
- **security:** The artifact contains private page data and potentially sensitive attachments: write only to an owner-selected directory, encrypt or apply local file permissions, and retain source URL/tab/time/hash. Never upload attachments to the relay or public browser backend; announce any unsupported file type instead of silently forwarding it. This is a read/download action only, with no form submission.
- **missing:** A browser-to-Mac artifact handoff carrying page text, attachment bytes/paths, and provenance; A deterministic attachment downloader that rejects cross-origin redirects and records hashes; An owner-configurable destination and retention policy for private browser artifacts; A resumable local writer that atomically replaces partial notes after Safari or Mac disconnects; A compact pendant digest and dashboard link to the resulting artifact

### "“Remember the important parts of this private page so I can ask about it later, even when Safari is closed.”"
- **useful because:** A logged-in page disappears when the owner closes Safari or loses the session, while the pendant remains with them. This would create a deliberately user-triggered, encrypted continuity capsule: the browser captures only the selected page regions and citations, the relay indexes it for later retrieval, and a compact digest is available on the pendant even without a live browser. It is neither a page watch nor a draft/action workflow.
- **path:** browser-extension → relay-realtime → pendant → mac-planner → dashboard
- **model tier:** Use the realtime tier only when the owner later asks a question aloud. Use a cheaper background model once, at capture time, to select and compress the requested regions; use deterministic hashing, encryption, and retrieval afterward. Keep the pendant response model small and grounded strictly in the capsule.
- **latency:** Capture acknowledgement in under 3 seconds and finish a normal capsule in under 20 seconds. Offline pendant lookup should answer from the cached digest in under 1 second; full cited text can be fetched when the relay or Mac reconnects.
- **cost:** One bounded background summarization call per explicit save, with page text capped by the owner; subsequent lookups use retrieval and incur only a small realtime call when spoken. Storage is compact encrypted text plus hashes, not screenshots by default.
- **security:** This is sensitive private data and must be opt-in per page, visibly labeled with origin and expiry, encrypted in transit and at rest, and deletable from pendant, relay, and Mac. Do not capture passwords, payment fields, hidden DOM, cookies, or unrelated tabs. The offline digest must refuse answers when the requested fact is absent rather than infer it.
- **missing:** An explicit browser action such as “save capsule” that captures owner-selected regions with URL, title, timestamp, and source hashes; End-to-end encrypted capsule storage with separate short digest and recoverable cited payload, plus expiry and deletion propagation; A pendant/relay retrieval route that works from the digest while disconnected and reconciles on reconnect; A grounded voice query mode that cites capsule origin and freshness instead of treating it as durable general memory; Dashboard controls to list, export, expire, and erase capsules


## Changes it proposed to its own stack

### `browser-harness` — Replace the granted-but-unimplemented browser enqueue wrapper with a live bridge call: accept one typed browser action, attach device/tab affinity and an idempotency key, enqueue through the local agent, wait for the extension result, and return a typed result or a structured timeout/session-lost error. Add a read-only list_tabs bootstrap so the planner can select the current Safari tab before extracting content.
- **owner gets:** The real Safari extension is online and now reports a tab, but this agent still cannot actually read or operate it: every granted enqueue tool returns an implementation error. This is the last-mile fix that makes the owner’s existing logged-in browser reachable instead of merely observable.
- effort: Small-to-medium: implement the bridge wrapper over the existing POST /execute browser action path, normalize result/error schemas, and add tests for tab disappearance and duplicate command IDs.  ·  risk: A malformed action could affect the wrong tab; enforce device/tab affinity and keep irreversible actions as explicit separate commands. On timeout, return unknown outcome with commandId rather than retrying blindly. Recovery is a later list_tabs/read-only retry.
- cost: Negligible API cost; one local request per browser action and existing extension polling. No new cloud storage required.  ·  latency: Adds up to the existing extension poll interval plus result wait (typically seconds); list_tabs is immediate.
- security: Uses the already-authenticated Safari bridge; do not copy cookies or page contents into the wrapper logs. Redact typed text and cap returned page payloads.
- depends on: A real implementation behind the already-granted browser command enqueue schema; The existing POST /execute browser action dispatcher and Safari extension result callback


## What it asked for

_Nothing._
## Its own summary

Discovered Safari is online with one tab, but the actual browser command path is still unavailable: the granted enqueue tool returns an implementation error. I proposed the concrete last-mile bridge fix (typed enqueue, tab affinity, idempotency, structured timeout/session errors, and list-tabs bootstrap), plus two new owner-facing workflows: a connected-account urgency/review queue and a private-page-to-local-sourced-note handoff. I notified mac-planner of the live state and limitation.

**Biggest unknown:** Which specific authenticated site/workflow the owner wants first; the previously requested workflow/sensitivity context is still unavailable, and no browser action should be attempted until the enqueue implementation exists.

