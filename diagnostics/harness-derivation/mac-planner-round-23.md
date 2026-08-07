# Harness derivation — mac-planner — round 23

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Get me ready for my next meeting.”"
- **useful because:** The owner gets a useful meeting workspace without manually searching calendar, mail, files, and browser tabs: identify the next event, summarize only relevant unread context, open the right documents or meeting link, and create a small scratchpad with agenda, decisions needed, and follow-ups.
- **path:** mac_read_sources reads the next calendar event and bounded recent/unread mail → relay/background worker ranks mail and resolves event attendees/subject to known local artifacts → browser harness locates the authenticated meeting or project page without exporting raw page content → mac_run_actions opens the meeting link and relevant files, and writes a timestamped scratchpad in a configured local folder → relay-realtime delivers a short pendant briefing only after the workspace is staged
- **model tier:** Cheap background model for calendar/mail filtering and artifact matching; realtime tier only for the owner's conversational request and final concise briefing. Escalate to the expensive model only when the event or mail is genuinely ambiguous.
- **latency:** 15–30 seconds for the first pass; open the meeting link immediately, then enrich the scratchpad asynchronously. The owner should be able to say “just open it” to skip enrichment.
- **cost:** Roughly $0.005–$0.03 per invocation depending on mail volume and whether browser extraction is needed; most cost is model summarization, not Mac actions.
- **security:** Calendar/mail snippets and document names leave the Mac only as redacted, bounded extracts; meeting URLs and authenticated page contents should remain in their respective local/browser surfaces. Never send full mail bodies by default. Opening a link or modifying files should be visible in the action receipt; use a dedicated scratchpad directory and atomic writes.
- **missing:** A durable local artifact index mapping calendar subjects/projects to files and browser pages; A browser-harness API that returns bounded semantic extracts and stable evidence references; A Mac routine for atomic scratchpad creation plus idempotent reuse when the same meeting is requested twice; A shared redaction policy and event/job ledger across relay, browser, and Mac


## Changes it proposed to its own stack

### `context` — Add a compact, durable Mac execution context cache and handoff protocol. Each server plan gets a jobId, parentId, monotonic sequence, intent hash, referenced local resources, and a short result receipt. The Mac stores only the minimum state needed to resume or deduplicate a plan (not the conversation transcript), and returns a delta receipt rather than requiring the full plan/context on every retry. Include TTLs, explicit invalidation when files/apps change, and a human-readable local activity log.
- **owner gets:** Actions stop repeating when connectivity or voice streaming glitches, and the owner does not pay for the same context over and over. Long-running workflows can resume after sleep or a dropped relay without losing their place, while the owner can inspect what the Mac did.
- effort: Medium: shared schema in relay and Mac agent, local SQLite/JSON ledger, idempotency checks around action batches, and receipt rendering in the dashboard. Pilot on file creation/opening and meeting-prep routines before generalizing.  ·  risk: A stale cache could open the wrong document or skip a needed action. Mitigate with resource fingerprints, short TTLs, sequence checks, and treating uncertain state as a fresh read rather than silently acting. Corrupt ledger recovery should discard cache and rerun safely; do not delete user data as part of recovery.
- cost: Small storage and implementation cost; lower API spend and fewer duplicate Mac executions. No meaningful per-invocation API increase; compact receipts may add a few hundred tokens when surfaced.  ·  latency: Usually lower latency by avoiding repeated planning; a small local lookup on every job. Fresh-state verification adds latency only after a stale or ambiguous fingerprint.
- security: Keep the ledger local, redact paths/content in server receipts, encrypt sensitive metadata at rest if available, and define retention/clear-history controls. This improves auditability without introducing an approval gate or reducing the owner's maximum-access policy.
- depends on: A shared job/receipt schema accepted by relay, browser, and Mac; Stable file/app/browser resource fingerprints; An atomic local ledger implementation and recovery test suite


## What it asked for

_Nothing._
## Its own summary

Proposed an owner-facing “Get me ready for my next meeting” capability that combines bounded Calendar/Mail reads, browser evidence, local file/link staging, and a concise pendant briefing. Also proposed a local Mac execution-context cache with job sequencing, idempotency, resource fingerprints, compact receipts, TTLs, and recovery so dropped links do not repeat actions or resend expensive context. Coordinated the ledger shape with browser-extension’s portal-watch work.

**Biggest unknown:** The missing shared artifact/evidence index: how calendar subjects, local files, and authenticated browser pages are safely mapped without exporting sensitive content. I do not need another permission this round; the next useful infrastructure is the shared job/receipt schema and local atomic ledger.

