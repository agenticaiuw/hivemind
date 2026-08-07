# Harness derivation — browser-extension — round 76

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If Safari goes away while you are working on a private webpage, pause safely and continue from where you left off when it comes back—without repeating clicks or losing a prepared draft—and tell me what remains."
- **useful because:** Today the browser is offline while five commands remain pending; a voice-started task can simply time out, and retrying can duplicate a click or lose filled-but-unsent work. This makes authenticated browser work dependable across sleep, browser restarts, and Wi‑Fi interruptions while preserving the owner's explicit stop-before-submit policy.
- **path:** pendant → relay → browser → mac-bridge
- **model tier:** Background durable job runner for orchestration and retries; realtime only for the short pendant status update. Use a cheaper text model to summarize recovery state; no vision/model call unless the page changed materially.
- **latency:** Acknowledge pause on the pendant within 1–2 seconds; detect extension return on its next heartbeat (target under 10 seconds); resume safe reads/fills in the background and report completion within one browser action timeout (45 seconds), with exponential backoff.
- **cost:** Usually near-zero model cost while paused; one short summarization call on recovery (roughly $0.001–$0.01 depending on context). Safari bridge and relay storage dominate engineering/runtime cost, not inference.
- **security:** Persist only encrypted task state, URL/session identifier, step idempotency key, and redacted evidence; never copy passwords or full page text into relay logs. Auto-replay only navigation, reads, and locally reversible fills; stop and surface a fresh before/after preview if the DOM, account, recipient, or submit target changed. Never auto-submit or send.
- **missing:** Durable browser job runner with jobId, persisted step ledger, retries, and result stream (the remaining gap in chg-16bc5dee); Browser reconnect leases and stale-command expiry so offline pending commands are not replayed blindly; A draft/evidence store that can restore a filled form and show its exact current values after reconnection; Relay-to-pendant job status push for pause/resume notifications

### "Tell me what this logged-in page says, but keep the page contents on my Mac; send only the short answer and the minimum evidence needed to my pendant."
- **useful because:** Authenticated pages can contain highly sensitive work, health, financial, or account data. Today the browser can read them and the relay can carry voice, but there is no owner-facing mode that guarantees raw page text stays local while still making the result useful over the pendant. This gives the owner private-page assistance without treating the cloud relay as a second copy of their browser.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Use a local Mac text model or deterministic extraction for page parsing and summarization; use realtime only to speak the already-redacted answer. Do not upload DOM, screenshots, cookies, or full extracted text to the relay.
- **latency:** Local extraction and summary in 3–8 seconds for a normal page; pendant response within 1–2 seconds after the local result is ready. If local processing fails, say so rather than silently falling back to cloud.
- **cost:** Near-zero relay inference cost; local model/CPU is the dominant cost. One short realtime response uses only a small answer context rather than the page, roughly cents or less per request.
- **security:** Enforce a local-only data boundary: page text, DOM, screenshots, URLs where sensitive, and credentials remain on the Mac; relay receives an opaque task ID, redacted answer, bounded evidence quote chosen by local policy, and confidence. Clearly label when a quote is being sent. Never include hidden fields or form values. Store no raw page content in job logs.
- **missing:** A browser-to-local summarizer contract that returns an answer plus bounded evidence and sensitivity labels without forwarding raw extraction; Relay payload enforcement that rejects raw DOM/screenshot/page-text fields for this mode; A pendant interaction state that announces local-only processing and handles low-confidence or blocked answers; Local audit receipts proving which fields crossed from Mac to relay


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-command lease and recovery ledger between /execute and the extension: every queued command gets an expiry, job/step id, tab/session binding, idempotency key, and replay class (read, reversible fill, irreversible). When /browser/status goes offline, stop dispatching and mark the lease paused; on heartbeat, reconcile the extension's acknowledged command IDs before replaying anything. Expire the five currently stranded pending commands instead of allowing an eventual reconnect to execute stale clicks. Emit a compact pause/resume/reconciled event to the relay job stream and retain the last safe form snapshot for review.
- **owner gets:** Safari sleep or a closed tab would no longer cause duplicate clicks, mysteriously stale actions, or lost prepared forms. The owner gets a trustworthy answer—completed, paused, or needs review—instead of a timeout and guesswork.
- effort: Medium: schema migration for pending browser commands, lease/reconciliation state machine, extension heartbeat acknowledgment support, and tests for offline/reconnect/DOM-changed cases.  ·  risk: A false offline or missed acknowledgment could leave a task paused. Recover by manual resume from the job record; never replay an unknown mutation automatically. A stale command might be discarded and require one safe re-read.
- cost: Negligible inference cost and a few D1/local JSON records per step; small storage increase for redacted form snapshots and receipts.  ·  latency: Adds one status/ack reconciliation round on reconnect; normal online commands remain unchanged. Recovery may take 1–10 seconds depending on heartbeat.
- security: Improves safety by preventing stale replay. Keep snapshots redacted and local where possible; relay receives only hashes, status, and explicitly selected evidence.
- depends on: Durable browser job runner (remaining half of chg-16bc5dee); Extension heartbeat must report acknowledged command IDs and active tab/session identity; Existing browser request IDs/tab affinity/typed results from chg-14accc01


## What it asked for

_Nothing._
## Its own summary

Discovered a live failure mode rather than restating the page-watch backlog: Safari is currently offline and five browser commands are pending, while three stale browser sessions remain recorded. I proposed a cross-surface pause/resume capability and the concrete browser-harness change it needs: per-command leases, expiry, step idempotency, offline pause, heartbeat acknowledgment reconciliation, safe replay classes, and redacted draft snapshots. This prevents stale clicks or duplicate mutations when Safari reconnects. I also notified mac-planner of the live state and recommendation.

**Biggest unknown:** The extension protocol's actual acknowledgment payload is still unknown; implementing reconciliation needs the extension to report command IDs plus active tab/session identity on heartbeat or result. The durable browser job runner and relay status push are also not yet implemented.

