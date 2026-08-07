# Harness derivation — mac-planner — round 15

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Every weekday morning, give me a short audio brief of today's calendar, unread important mail, weather, and any browser jobs that finished overnight."
- **useful because:** The owner gets a useful plan without opening apps or waiting for a live conversation; it combines local private sources with remote web results and arrives on the pendant's normal playback path.
- **path:** dashboard → mac-bridge → browser → pendant
- **model tier:** A cheap background model summarizes pre-extracted Calendar/Mail/browser fields; realtime is used only if the owner asks a follow-up. TTS/audio generation runs once per brief, not per item.
- **latency:** Generate by 07:30 when the Mac is awake; tolerate minutes of delay and show a pending state if the Mac was asleep.
- **cost:** Low: one compact summarization call plus one audio render per day; dominant cost is TTS/audio bytes, so cap the brief at 3 minutes and avoid sending raw email bodies.
- **security:** Mail/calendar snippets and browser account data leave the Mac for summarization. Default to redacted snippets and local extraction; require explicit opt-in per account. Never include secrets, full message bodies, or private browser pages in shared logs.
- **missing:** A durable scheduler wake-up or catch-up run when the Mac was asleep; A server job/audio delivery endpoint with retry and expiration; A working authenticated browser dispatch path; A user-configurable source allowlist and redaction policy

### "Check my authenticated browser accounts for anything that needs my attention, then put findings in a review queue instead of changing anything."
- **useful because:** It turns scattered web dashboards into one bounded, evidence-backed queue while preserving the owner's control over actions such as sending, purchasing, or deleting.
- **path:** browser → dashboard → mac-bridge
- **model tier:** Use Cloudflare Browser Run or the browser bridge for deterministic extraction; a cheap model classifies and deduplicates results. Use realtime only for conversational review.
- **latency:** Run on demand or on a daily schedule; 1–5 minutes is acceptable, with per-site timeouts and partial results.
- **cost:** Moderate and variable: browser execution dominates, while extraction/classification is cheap. Cache page fingerprints and only reprocess changed pages.
- **security:** Private account pages and session cookies must remain in the approved browser harness; do not upload screenshots or credentials. Read-only selectors only; every outbound message, purchase, deletion, or setting change requires explicit confirmation and a fresh preview.
- **missing:** A real POST /execute browser dispatch (current enqueue wrappers are stubs); Per-site read-only policies and authenticated account consent; Evidence storage linking each queue item to URL, timestamp, and extracted text; A shared Jobs/review inbox in the dashboard

### "When I say 'clean up my desktop', group obvious screenshots and downloads into dated folders, but show me the proposed moves first."
- **useful because:** It reduces clutter without silently losing files, and the owner can approve a bounded batch rather than managing every file manually.
- **path:** mac-bridge → dashboard
- **model tier:** Use the Mac local agent's deterministic directory listing and file metadata; use a cheap model only to classify ambiguous filenames. No realtime model is needed unless the owner asks questions.
- **latency:** Under 30 seconds for a typical Downloads/Desktop scan; proposal should be available before any move.
- **cost:** Very low: local metadata stays on-device and only a compact filename list may be summarized. No audio required unless requested.
- **security:** Never delete or overwrite by default. Restrict to approved directories, preserve reversible manifests, exclude cloud-synced and work folders unless explicitly enabled, and require confirmation for the actual move batch.
- **missing:** A read-only preflight/list operation exposed through the Mac bridge; A transaction manifest and undo operation for move batches; A reliable confirmation gate independent of FULL_CONTROL_MODE; Directory allowlist and file-size/type limits

### "Before my next meeting, prepare a one-page brief from the calendar invite, recent related mail, and approved web sources, save it to my Mac, and tell me where it is."
- **useful because:** The owner gets context assembled automatically instead of hunting through mail, files, and the web; the artifact remains available even if the live conversation ends.
- **path:** mac-bridge → browser → dashboard → pendant
- **model tier:** Cheap background model extracts the attendee/topic context and drafts the brief; deterministic local actions save it. Realtime is only for an interactive request or clarification.
- **latency:** Start 15 minutes before meetings and finish within 2 minutes; if sources fail, deliver a clearly labeled partial brief.
- **cost:** Low to moderate: compact calendar/mail snippets and selected web passages dominate tokens; no continuous audio, and reuse cached source extracts across meetings.
- **security:** Invitees, mail, and browsing topics are sensitive. Use only the selected meeting's sources, redact unrelated recipients/content, save to a user-approved folder, and never send or share the brief without confirmation.
- **missing:** Calendar/mail source integration in the server job path; A browser read-only dispatch with citation capture; A local file write with approval and durable artifact link; Meeting-triggered scheduler that catches up after sleep


## Changes it proposed to its own stack

### `mac-harness` — Add a mandatory server-side confirmation broker around POST /execute: classify each action batch, require a short-lived token for external side effects (send, purchase, delete, overwrite, shell, AppleScript), and support dry-run previews plus idempotency keys. Keep reversible local actions fast, but make FULL_CONTROL_MODE unable to bypass this policy.
- **owner gets:** The owner can safely delegate powerful desktop work without an accidental or malicious plan sending mail, deleting files, or spending money; previews and undo manifests make failures recoverable.
- effort: Medium: action classification, token issuance in dashboard/pendant flow, batch journal, and migration of existing callers.  ·  risk: False positives could interrupt harmless work; recover with per-action allowlists and explicit 'approve this class' settings. A lost response could leave unknown state, so every job must report per-action outcomes and support reconciliation.
- cost: Negligible API cost; small D1 storage for journals and tokens.  ·  latency: Adds near-zero latency to preapproved actions; 1–2 seconds for an approval round trip.
- security: Large improvement: least privilege, replay protection, and auditable authorization. Tokens must be scoped to exact actions and expire quickly.
- depends on: A shared dashboard/pendant approval UX; Stable action schemas for browser and Mac jobs

### `model-routing` — Split work into a cheap asynchronous planner/classifier, deterministic Mac/browser executors, and realtime only for live dialogue and ambiguous confirmation. Add budgets, deadlines, cancellation, and partial-result delivery to every job.
- **owner gets:** Routine work becomes cheaper and can finish while the owner is away, while urgent voice interactions remain responsive and failures do not block unrelated tasks.
- effort: Medium: job state machine, queue priorities, model selection metadata, and result aggregation in D1/dashboard.  ·  risk: A cheap model may misclassify a request; fall back to realtime or ask a clarification when confidence is low. Enforce hard limits and cancellation to prevent runaway browser jobs.
- cost: Should materially reduce token/audio spend by avoiding realtime context and repeated polling; queue overhead is minimal.  ·  latency: Async tasks may take seconds to minutes, but live responses stay low latency; stream progress and notify only on completion or failure.
- security: Each worker receives only the minimum data needed; isolate private Mac/browser payloads from server-side prompts and redact logs.
- depends on: Durable job queue and result schema; Working browser POST /execute; Per-source data redaction

### `memory` — Replace hand-written per-surface fleetContext prompt sections with a single typed context service that stores compact facts, provenance, sensitivity, TTL, and last-used timestamps; retrieve only task-relevant facts and automatically prune stale/duplicate session text.
- **owner gets:** The assistant remembers preferences and past jobs consistently across web, menubar, iOS, and pendant without repeatedly exposing irrelevant private history or making every turn expensive.
- effort: Medium-high: schema migration, retrieval filters, provenance UI, and backfill from the knowledge graph.  ·  risk: Bad retrieval can omit an important preference; retain a user-visible pinned-facts list and fall back to explicit clarification. Incorrect facts need correction and deletion controls.
- cost: Lower recurring token cost through compact retrieval, offset by one-time migration and small embedding/index overhead.  ·  latency: A bounded retrieval adds tens to hundreds of milliseconds; compact prompts should reduce overall model latency.
- security: Sensitivity labels and per-surface ACLs prevent private mail/browser facts leaking into shared contexts; provenance makes every fact inspectable.
- depends on: Typed memory API behind /v1/ops/memory; Surface/account access-control model; Dashboard controls for inspect, correct, and delete

### `dashboard-ux` — Ship a unified Jobs inbox across web, menubar, and iOS showing queued/running/completed/failed work, source account, evidence links, data sensitivity, cost estimate, cancellation, and approval requests; add a compact 'pending while Mac asleep' state.
- **owner gets:** The owner can see what the assistant is doing, recover failures, approve risky actions, and trust that a background task finished—even when no voice session was open.
- effort: Medium: shared SvelteKit components, D1 job/event API, and local-agent heartbeat/sleep detection.  ·  risk: Too much detail creates noise; default to concise cards with expandable evidence and user-configurable notifications. Avoid exposing private snippets on lock screens.
- cost: Low API/UI cost; event retention is small if logs are summarized and raw outputs expire.  ·  latency: Near real-time for job events; no impact on execution.
- security: Requires strict per-account and per-job ACLs, redacted previews, and no sensitive content in push notification text.
- depends on: Durable job/event schema; Mac heartbeat and retry/catch-up; Browser dispatch and evidence records


## What it asked for

### `c9-4uo4` (context) — owner's approval and privacy defaults for Mac/browser automation
- why: I need to distinguish actions that may run unattended from actions that must always stop for confirmation, especially because the current Mac agent bypasses its risk scorer in FULL_CONTROL_MODE.
- would change: I would configure proposed routines and job inboxes with the correct default allowlists, notification behavior, and redaction level instead of assuming maximum automation or maximum prompting.

## Its own summary

Established the Mac stack constraints: local scheduler only runs while awake; browser enqueue wrappers are stubs; Cloudflare Browser Run exists; and FULL_CONTROL_MODE bypasses all action-risk confirmation. Proposed high-value capabilities: weekday private workday audio briefs, authenticated read-only browser sweeps with an evidence-backed review queue, safe desktop cleanup with preview/undo, and meeting briefs saved locally. Proposed stack changes: mandatory scoped confirmation broker, async model routing with budgets/cancellation, unified typed/pruned memory, and a cross-surface Jobs inbox. I also warned relay-realtime about the confirmation bypass and requested the owner's privacy/approval defaults.

**Biggest unknown:** The owner's desired unattended-action and data-sharing policy is still unknown; I requested context. Implementation blockers are the browser POST /execute dispatch, durable job/audio retry and catch-up after Mac sleep, source/account ACLs and redaction, and a confirmation gate that FULL_CONTROL_MODE cannot bypass.

