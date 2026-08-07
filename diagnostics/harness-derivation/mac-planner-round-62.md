# Harness derivation — mac-planner — round 62

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-readonly-inspection** — The newly granted mac_readonly_inspect interface is present in the schema but has no implementation yet; all four attempted inspection operations returned the explicit implementation error. Live /ops/status independently reports Accessibility trusted=false, Screen Recording=false, browser offline with 3 pending commands, and overall ready=false.
  - evidence: mac_readonly_inspect returned 'This tool was granted a schema but has no implementation yet' for running_apps, foreground_app, accessibility_enabled, and browser_tabs; GET /ops/status HTTP 200 reported those permission and browser states.

## Capabilities it proposed

### "When I say “close out that meeting,” use the meeting that just ended to turn my notes into a reviewable follow-up packet: identify decisions and owners, check the relevant logged-in task/project page, draft follow-up messages (never send), and create suggested reminders."
- **useful because:** It removes the most error-prone post-meeting work while preserving control. The pendant provides an immediate, hands-free trigger; the Mac supplies local notes and calendar truth; the browser can reach private project/task pages; the relay keeps the workflow alive and reconciles evidence even if one surface briefly disconnects.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheaper background model for extraction, deduplication, and task matching; use realtime only to understand the spoken trigger and give a short acknowledgement. Escalate ambiguous owners/dates to the judgement model.
- **latency:** Acknowledge on the pendant in under 1 second. Produce an initial packet in 30–90 seconds, continuing in the background if browser or Mac reads are slow. Dashboard should show partial results and a final receipt.
- **cost:** Roughly $0.01–$0.05 per closeout, dominated by model tokens for note extraction and authenticated-page reconciliation; realtime cost is limited to the short trigger exchange.
- **security:** Private notes, calendar metadata, and authenticated task pages leave the Mac only as structured excerpts to the relay/model. Redact unrelated note content and scope browser access to explicitly bound tabs/sites. Never send messages, submit forms, or create external tasks automatically; require owner review. Record source URLs, note filename, timestamps, and extracted evidence for each proposed item.
- **missing:** A first-class cross-surface closeout job with a durable state machine and correlation to the just-ended calendar event.; A bounded local note/transcript reader that can select the meeting’s note without arbitrary filesystem scraping.; Browser session reattachment and reliable queue processing when the extension is offline (currently offline with 3 pending commands).; A review dashboard that presents decision/owner/date evidence and supports accept/edit/reject per draft or reminder.; Truthful degraded-mode receipts: accessibility is currently untrusted and Screen Recording is unavailable, so blocked Mac actions must not report success.

### "When I say “resume where I left off,” reconstruct my last interrupted work session across the Mac and authenticated browser: reopen the relevant files and tabs, recover the unsent draft or pending form without submitting it, summarize what was completed and what remains, and let me continue from the pendant."
- **useful because:** The owner loses context whenever they close a laptop, switch tasks, or move away. This would restore the actual work state—not merely a chat summary—while keeping unsent communication and browser transactions safely reviewable.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a background, lower-cost model to build and rank the session snapshot. Use realtime only for the spoken resume command and a short spoken orientation. Use the judgement/action faculties only for restoration steps that match recorded state.
- **latency:** Acknowledge in under 1 second; present the recovered session summary within 10 seconds; restore files and tabs progressively within 30–60 seconds. If a surface is unavailable, show exactly what can and cannot be restored.
- **cost:** Approximately $0.01–$0.04 per resume, dominated by summarizing the compact session ledger; restoration itself is mostly local operations and browser commands.
- **security:** The snapshot may contain sensitive URLs, drafts, and document names. Keep full content local where possible, send only hashes, labels, and selected excerpts upstream, encrypt the ledger, and expire it after a configurable period. Never submit forms or send messages during restoration. Require explicit confirmation before reopening a sensitive account or exposing private content on screen.
- **missing:** A cross-surface interruption ledger recording active files, browser tab/session IDs, draft buffers, unsent transaction state, and the last confirmed checkpoint.; Mac and browser snapshot APIs that can capture and restore state without claiming success when Accessibility, Screen Recording, or the extension is unavailable.; A privacy-aware compactor that separates resumable metadata from sensitive content and supports expiry/deletion.; A dashboard resume view with per-item restore status, conflict handling, and a safe preview of drafts/forms before reopening them.; A pendant command and relay protocol for selecting among multiple interrupted sessions and reporting partial restoration.


## Changes it proposed to its own stack

### `integration` — Add a MeetingCloseout orchestrator that creates one correlation ID from the calendar event (event ID/time/participants), then runs bounded Mac note extraction and browser task-page lookup as parallel evidence jobs. Merge only cited facts, classify each proposed follow-up as draft/reminder/task, and expose per-item accept/edit/reject plus resumable checkpoints. If a surface is offline, retain the checkpoint and report “pending,” never success.
- **owner gets:** After a meeting, the owner gets one trustworthy packet instead of manually rereading notes, hunting the project board, and composing follow-ups. They can approve only the items that are correct and recover cleanly when the browser or Mac is unavailable.
- effort: Medium-high: event correlation, local note selection, cross-surface job state, evidence merge, review UI, and integration tests for disconnect/replay cases.  ·  risk: Wrong event or inferred owner/date could create misleading drafts. Mitigate with explicit event matching, confidence labels, source excerpts, no automatic send/submit, and idempotent draft/reminder keys. Crash recovery resumes from checkpoints rather than duplicating work.
- cost: Low incremental API cost; most work is structured extraction and existing reads. Storage is small JSON job state plus short evidence snippets per closeout.  ·  latency: Parallel reads reduce wall-clock time; initial acknowledgement is immediate, final packet typically under 90 seconds, with partial progress visible.
- security: Only selected meeting note sections and explicitly scoped authenticated-page excerpts are sent upstream; unrelated notes and tabs remain local. Correlation IDs and audit receipts make cross-surface access reviewable.
- depends on: mac_read_sources or a bounded local note/transcript reader; Reliable browser queue with reconnect and idempotency; Durable job runner/checkpoint store; Review dashboard and truthful blocked-action receipts

### `memory` — Create a privacy-scoped interruption ledger and restoration protocol. Every Mac/browser job emits a compact checkpoint containing task identity, local file fingerprints, tab/session references, draft/form hashes, last confirmed step, and expiration. On resume, each surface validates its checkpoint against current state, returns restored/conflict/unavailable per item, and the relay composes a spoken and dashboard handoff without treating attempted UI actions as completed.
- **owner gets:** They can stop work at any point and later get back to the exact unfinished task instead of searching through files, tabs, and drafts. Conflicts are visible rather than silently overwriting newer work.
- effort: High: requires checkpoint instrumentation in the Mac and browser harnesses, encrypted local storage, expiry/deletion controls, state validation, and a restoration UI/protocol.  ·  risk: Stale or sensitive checkpoints could expose private work or reopen the wrong state. Mitigate with short TTLs, per-app/site privacy scopes, content hashes instead of raw text, explicit conflict previews, and no automatic submission or sending.
- cost: Small persistent local ledger; low model cost because restoration uses structured metadata and hashes rather than replaying full history.  ·  latency: Checkpoint writes should be asynchronous and under 100 ms; restoration can proceed in parallel, with a useful partial handoff in seconds.
- security: Improves security by making drafts and private tabs explicitly scoped and expiring, but introduces a sensitive state index that must be encrypted and excluded from broad relay context.
- depends on: Mac and browser checkpoint instrumentation; Reliable browser session identity and reconnect handling; Implemented read-only Mac/UI inspection APIs; Dashboard support for conflict and partial-restore status


## What it asked for

_Nothing._
