# Harness derivation — mac-planner — round 13

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me a workday brief at 8:30, and let me play it from the pendant when I’m ready.”"
- **useful because:** The owner gets a compact, asynchronous briefing without opening apps or spending a realtime turn. It combines today’s calendar, unread mail, and outstanding Mac-side work, then delivers audio on demand.
- **path:** relay scheduler/D1 → mac_read_sources for calendar and mail → cheap background summarizer → R2 audio generation → pendant playback queue → dashboard/iOS history
- **model tier:** Scheduled extraction and summarization on a cheap background model; TTS on a low-cost batch/audio model. Realtime is used only if the owner asks a follow-up by voice.
- **latency:** Generate by 8:30 in under 60 seconds; playback starts within 1 second after the pendant request.
- **cost:** Low: one bounded calendar/mail extraction plus a short summary and one TTS clip per day. Dominant cost is TTS/audio storage, not reasoning; retain 7 days and deduplicate unchanged briefs.
- **security:** Mail/calendar snippets leave the Mac only to the authorized relay account and should be redacted before summarization. Never include message bodies by default, secrets, or private event details in audio. Require explicit setup consent and provide a delete-history control.
- **missing:** Scheduler and idempotent recurring-job records; Audio generation and pendant playback queue; Per-source redaction and account-scope policy; A bounded mac_read_sources-to-relay adapter

### "“Before my next meeting, prepare me: open the agenda, summarize relevant email, and put a private briefing on the pendant.”"
- **useful because:** Meeting preparation finishes in the background while the owner continues working. The Mac can gather local agenda/files while the relay handles a short briefing, with no need to keep a microphone open.
- **path:** relay scheduler triggered by calendar → mac planner using accessibility/read-only file actions → mac_read_sources for matching mail → background model → R2 private audio → pendant and dashboard notification
- **model tier:** Cheap background model for retrieval, ranking, and summarization; no realtime model unless the owner asks a conversational question.
- **latency:** Start 15 minutes before an event and finish within 2 minutes; never steal focus while the owner is using another app.
- **cost:** Low-to-moderate per meeting, bounded by a maximum of 10 mail snippets and 3 local documents. Audio is generated only when content changed.
- **security:** Calendar title/attendees and matching mail are sensitive. Use sender/subject/snippet by default, redact credentials and attachments, and keep local file contents on-device unless the owner explicitly enables upload. Opening files is safe; sending, editing, or sharing anything must be a separate confirmed action.
- **missing:** Calendar-triggered scheduler; Read-only local document index or typed file retrieval; Meeting-to-mail matching policy; Audio notification/playback queue; Non-focus-stealing Mac action implementation

### "“Research this topic, compare the best options, and leave me a short audio recommendation—don’t buy anything.”"
- **useful because:** The owner gets useful web research without waiting in a live voice session or having browser tabs and focus disturbed. It can run concurrently with other jobs and produce citations plus an audio summary.
- **path:** relay job queue → Cloudflare Browser Run read-only session → web search → cheap background synthesis → R2 report/audio → dashboard and pendant playback
- **model tier:** Cheap background model for query decomposition, extraction, and comparison; realtime only for follow-up conversation. Browser actions are read-only and bounded by domain/time/result limits.
- **latency:** Typical result in 2–5 minutes, with progressive status in the dashboard; audio available when complete.
- **cost:** Moderate and bounded: browser/search calls dominate, followed by a short synthesis and TTS. Cache URL snapshots and reuse unchanged evidence; no browsing for a follow-up if cached.
- **security:** Use isolated server-side browser context, never Mac cookies, and label uncertain or sponsored claims. Do not log tokens or form data. The agent must not purchase, submit forms, or contact vendors; any mutating action is a separate exact-confirmation flow.
- **missing:** Cloudflare Browser Run integration in the relay; Evidence/citation schema and cache; Async job status and audio pipeline; Budget and domain allowlist controls

### "“Every Friday, tidy my Downloads into dated folders, show me a preview, and only then apply it.”"
- **useful because:** The Mac handles repetitive housekeeping while preserving control: the owner receives a proposed move list and can approve once, instead of manually sorting files.
- **path:** relay scheduler → Mac read-only directory inventory → background planner → dashboard preview/diff → mac action executor after exact approval
- **model tier:** Cheap background model or deterministic rules for classification; no realtime model needed. Use the realtime model only if the owner asks for a voice explanation of the preview.
- **latency:** Preview ready within 1 minute of the scheduled run; applying moves should finish in seconds and be cancellable where possible.
- **cost:** Very low: local metadata listing and deterministic grouping dominate; no upload of file contents and no TTS unless requested.
- **security:** Never inspect or upload file contents by default. Exclude hidden/system files, preserve extensions, detect name collisions, and require exact approval for deletion or overwriting. Moves should be journaled with a rollback manifest.
- **missing:** Safe local directory inventory action; Preview/diff and approval UI; Atomic move/rollback journal; Scheduler and exclusion rules


## Changes it proposed to its own stack

### `mac-harness` — Add a typed action policy in front of FULL_CONTROL_MODE: classify every action as read-only, reversible local mutation, or high-impact mutation; require a one-use confirmation token bound to the exact manifest for sending, deleting, purchasing, account/security changes, shell, and AppleScript. Keep automatic execution for opening apps/URLs, reading, drafting, and other reversible actions. Return per-action evidence, result, and undo metadata.
- **owner gets:** Voice commands can remain fast for harmless work while preventing a mistaken transcript from deleting files, sending mail, or spending money. The owner sees exactly what happened and can recover or retry a failed step.
- effort: Medium: policy middleware, manifest hashing, token endpoint/UI, action journal, and tests across ui_* and legacy computerControl actions.  ·  risk: A false classification could block useful work or permit a dangerous one. Default unknown actions to blocked; preserve current executor as a rollback path and add dry-run tests before enabling enforcement.
- cost: Negligible API cost; small local CPU/storage overhead for hashes and journals.  ·  latency: Read-only/reversible actions unchanged. High-impact actions add one confirmation round, typically 1–3 seconds.
- security: Major improvement: closes the current FULL_CONTROL_MODE bypass where actionRisk is never consulted; prevents replay with expiry, origin/app binding, and one-use tokens.
- depends on: Shared confirmation-token service; Typed evidence schema shared with browser harness; Action journal and redaction policy

### `memory` — Replace per-surface hand-written fleetContext sections with a compact, typed context projection: stable preferences and permissions, current tasks, and only relevant recent entities. Prune by TTL and utility, store provenance, and send a small surface-specific summary rather than the full graph on every turn.
- **owner gets:** The assistant remembers useful preferences consistently across pendant, Mac, dashboard, and iOS without repeatedly costing tokens or surfacing stale/private details.
- effort: Medium: projection service, relevance/TTL rules, migration of fleetContext.js, and inspectable memory controls in the dashboard.  ·  risk: Over-aggressive pruning can make the assistant forget important facts. Keep durable facts separately, show provenance, and allow owner pin/delete/export.
- cost: Likely lowers recurring token cost substantially by shrinking prompt context; modest D1 reads.  ·  latency: Slight improvement from smaller prompts; projection may add a few milliseconds or be cached per session.
- security: Reduces accidental cross-surface leakage by explicit scopes and provenance; requires careful ACLs for private entities.
- depends on: Typed memory schema; Surface/account authorization model; D1 migration and backfill

### `model-routing` — Route all non-conversational work through an asynchronous job planner: realtime handles intent capture and confirmation only; a cheaper background model handles extraction, Mac/browser plans, retries, and summarization; a small verifier checks action manifests and evidence before execution. Return a compact status card rather than keeping the realtime session alive.
- **owner gets:** Long tasks finish without making the owner wait or pay realtime audio/token rates. Failures become visible and resumable, while simple voice questions remain immediate.
- effort: Medium: job state machine, model-router rules, verifier, cancellation/retry semantics, and dashboard status cards.  ·  risk: A cheaper model may misunderstand ambiguous requests. Require clarification for ambiguity, use bounded plans, and let the owner inspect/cancel queued work.
- cost: Should reduce cost materially by moving planning and summaries off the realtime model; verifier adds a small fixed cost per mutating job.  ·  latency: Immediate acknowledgement under 1 second; completion varies by task, with progress updates and no microphone hold-open.
- security: Centralized verifier can enforce read-only vs mutation policy, data scopes, and confirmation tokens before Mac/browser execution.
- depends on: Durable D1 job state machine; Typed Mac/browser action manifests; Shared confirmation-token service; Dashboard progress and cancellation UI

### `relay` — Enable a bounded audio-retention sweeper and per-job deletion controls: default to short retention for generated briefings, delete expired R2 objects and D1 pointers idempotently, and expose a dashboard ‘delete now’ action. Keep owner-pinned items separate with an explicit expiry.
- **owner gets:** Private voice recordings and briefings do not accumulate indefinitely or remain accessible after they are no longer useful; storage stays understandable and controllable.
- effort: Small-to-medium: scheduled Worker job, R2/D1 consistency handling, retention metadata, and dashboard controls.  ·  risk: A sweeper bug could delete a pinned or still-needed recording. Use tombstones, pinned/expiry checks, dry-run metrics, and a recovery window before physical deletion.
- cost: Reduces ongoing R2 storage cost; small scheduled Worker/D1 operations.  ·  latency: No user-facing latency except delete-now confirmation.
- security: Meaningfully reduces exposure window for sensitive audio; audit deletion events without retaining audio contents.
- depends on: Per-recording retention metadata; R2/D1 reconciliation job; Dashboard deletion and pin controls


## What it asked for

_Nothing._
## Its own summary

I obtained the real stack specification and proposed concrete owner-facing capabilities: scheduled workday briefs, calendar-triggered meeting preparation, asynchronous cited web research, and preview-first Downloads cleanup. I also proposed high-leverage changes: typed Mac/browser action manifests with exact confirmation for high-impact actions, compact scoped memory projections, async model routing away from realtime, and an R2 audio-retention sweeper. The strongest immediate safety issue remains that FULL_CONTROL_MODE bypasses actionRisk entirely, so harmless actions should stay automatic while shell/AppleScript/send/delete/purchase/account changes gain exact one-use confirmation. I attempted all newly granted Mac read-only inspections in parallel, but each currently returns 'tool ... has no implementation yet'; I reported that to mac-vision and cannot truthfully provide installed-app, foreground, accessibility, browser-tab, or directory facts.

**Biggest unknown:** The actual Mac environment and automation surface: which apps are installed/running, whether Accessibility is enabled, available Shortcuts, and current browser state. Implementing mac_readonly_inspect (or supplying those facts from mac-vision) is the remaining discovery needed to make desktop plans app-specific rather than generic.

