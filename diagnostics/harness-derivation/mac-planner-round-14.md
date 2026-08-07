# Harness derivation — mac-planner — round 14

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Every weekday at 8:30, prepare a concise workday brief: today's calendar, unread mail grouped by urgency, and the top three actions; save it as an audio briefing I can play later."
- **useful because:** The owner gets useful planning without opening apps or holding a live voice session. It can run unattended and arrive on the pendant's normal audio queue.
- **path:** relay → mac-bridge → dashboard → pendant
- **model tier:** Use a cheap background model to summarize redacted Calendar/Mail snippets and produce a short script; use TTS/background audio generation, not realtime. Escalate only ambiguous priority decisions to realtime when the owner asks.
- **latency:** 2–5 minutes after the schedule fires is acceptable; playback is on demand.
- **cost:** Low: bounded source snippets (for example 50 mail items and one day's calendar) plus one short summary/TTS. Dominant cost is audio generation; cap the script at 250 words.
- **security:** Calendar and mail leave the Mac only as bounded snippets; redact bodies by default and include only sender/subject/time unless the owner opts in. Never send mail or alter calendar from this routine. Require explicit confirmation for any suggested reply or event change.
- **missing:** A durable Worker scheduler or a Mac-sleep-independent trigger; A typed audio-job queue from background jobs to the pendant; A Mac bridge operation that reads Calendar/Mail on schedule and returns bounded redacted data

### "When I say 'triage my inbox', classify unread mail into urgent, reply soon, reference, and noise, draft replies for the first two categories, and show me a reviewable list without sending anything."
- **useful because:** It removes repetitive sorting while preserving the owner's control over communication. Drafts can be reviewed from the dashboard or Mac Mail.
- **path:** relay → mac-bridge → dashboard → iOS
- **model tier:** Use a cheaper background model for classification and draft generation; realtime only handles the spoken command and reports completion.
- **latency:** 30–90 seconds for up to 50 messages; stream progress/status rather than holding the voice turn open.
- **cost:** Low to moderate, dominated by message snippets and draft tokens. Use sender/subject/snippet first and fetch full body only for messages selected for drafting.
- **security:** Treat mail as private and potentially adversarial prompt content; delimit and sanitize it. No send, archive, delete, or mark-read actions. Drafts must be visibly labeled and require explicit confirmation before insertion or sending.
- **missing:** A persistent job/status API for long-running triage; A Mail write operation limited to creating drafts, separate from send; Dashboard review UI with per-draft approve/edit/discard

### "Keep a daily 'closeout' routine: at 5:30 PM, summarize unfinished calendar items and the notes/files I touched today, then create a short checklist for tomorrow."
- **useful because:** It converts a scattered workday into a concrete next-day plan and runs without needing the owner to remember to ask.
- **path:** mac-bridge → relay → dashboard
- **model tier:** Use a cheap background model after deterministic collection of today's calendar and an explicit list of recent files/notes; no realtime model needed.
- **latency:** Under 3 minutes after trigger; audio and dashboard checklist can appear asynchronously.
- **cost:** Low if file collection is metadata-only and capped (for example 30 recent files), with a 200-word summary. Audio is the main variable cost.
- **security:** Do not read arbitrary file contents by default; use names, timestamps, and app metadata, with per-folder allowlists. Exclude sensitive folders. Creating the checklist is reversible, but never edit source files or send anything without confirmation.
- **missing:** Read-only Mac source for recent files/notes with allowlists; Background job scheduler that survives Mac sleep; A durable checklist/task object in D1 and optional audio rendering

### "Watch my chosen logged-in web pages once a day and tell me only what changed; prepare drafts for any follow-up forms, but stop before submitting."
- **useful because:** The owner gets monitored updates without repeatedly opening sites, while risky authenticated actions remain under their control.
- **path:** relay → browser → dashboard → pendant
- **model tier:** Use deterministic page-diff extraction first, then a cheap background model to summarize changed sections. Realtime is only for the initial spoken setup and questions.
- **latency:** Daily result within 5 minutes of the scheduled run; no live waiting.
- **cost:** Low when selectors and hashes avoid sending unchanged pages; model cost scales with changed text only. Audio should be a short delta summary.
- **security:** Logged-in pages contain sensitive data and may include prompt injection. Restrict to owner-approved domains/selectors, isolate page text as untrusted, redact secrets, and require explicit confirmation before submit/send/purchase or any account change.
- **missing:** Implemented browser command enqueue/job execution (currently wrappers report no implementation); Watch definitions with domain and selector allowlists; Persistent page snapshots/diff storage with retention limits; Reviewable draft and confirmation flow


## Changes it proposed to its own stack

### `model-routing` — Add an asynchronous job router: realtime handles only immediate conversational acknowledgement and dispatch; a cheaper background model handles calendar/mail/file summarization, classification, and draft generation; deterministic code performs collection, limits, redaction, and formatting.
- **owner gets:** Routine work completes in the background at much lower cost, while spoken interactions remain fast and responsive.
- effort: Medium: job schema, queue worker, model selection, retry/status handling, and output delivery.  ·  risk: A background job could fail or summarize stale data; show source timestamps and failure state, and allow rerun. Do not silently retry side effects.
- cost: Reduces token/audio spend by keeping long work off realtime; adds small queue/worker cost.  ·  latency: Immediate acknowledgement under a second; results arrive seconds to minutes later depending on job.
- security: Centralize redaction and data minimization before model calls; treat source text as untrusted input.
- depends on: Durable job/status storage; Background scheduler or worker; Audio/output queue

### `memory` — Replace per-surface hand-written fleetContext prompt sections with a compact, typed context service that returns only task-relevant facts, each with source, timestamp, confidence, and expiry; automatically prune stale session detail and raw audio references.
- **owner gets:** The assistant remembers useful preferences without repeatedly spending tokens on irrelevant history, and it is less likely to act on outdated information.
- effort: Medium-high: typed schema, retrieval filters, expiry/pruning jobs, migration from fleetContext.js, and dashboard controls.  ·  risk: Over-pruning can lose important preferences; preserve pinned facts and provide inspect/delete/export controls. Retrieval errors should be visible in action plans.
- cost: Lower per-turn context tokens; modest D1 query and migration cost.  ·  latency: Small retrieval overhead, offset by shorter prompts.
- security: Explicit retention and deletion improve privacy; never put raw mail/calendar bodies in durable memory unless explicitly pinned.
- depends on: Memory schema migration; Surface-neutral retrieval API; Owner-facing memory controls

### `mac-harness` — Add typed, read-only observability endpoints for job execution: running apps, foreground app, accessibility state, browser tabs, and allowlisted directory listings, plus structured per-action result/error records for existing execution.
- **owner gets:** The assistant can report what actually happened, recover from partial failures, and avoid blindly repeating actions while the owner is using the Mac.
- effort: Medium: endpoint schemas, permission-aware adapters, redacted results, and relay/dashboard display.  ·  risk: Observability can expose sensitive window titles, URLs, or filenames; default to redaction, cap result size, and require explicit source scope. It must remain read-only.
- cost: Small implementation and token overhead; reduces expensive failed retries and unnecessary model calls.  ·  latency: Usually sub-second; only request inspection when needed.
- security: No new write authority; strict allowlists and redaction reduce accidental disclosure.
- depends on: Typed result schema; Relay tool exposure for read-only inspection; Dashboard status rendering

### `dashboard-ux` — Add a unified Jobs inbox shared by web, menubar, and iOS: queued/running/completed/failed jobs, source timestamps, concise result, audio-play button, retry, cancel where safe, and a per-action audit trail. Separate 'draft ready' from 'executed' states.
- **owner gets:** Long tasks stop feeling like vanished voice commands; the owner can find results later, understand what changed, and review drafts before any consequential action.
- effort: Medium: shared SvelteKit view, D1 job records, result cards, audio integration, and status polling/push.  ·  risk: Status UI could reveal private job contents to anyone viewing the screen; redact by default and support lock/hide. Cancellation may not stop already-started external work, so label it accurately.
- cost: Small dashboard/storage cost; reduces repeated requests and duplicate model runs.  ·  latency: No impact on execution; near-real-time status refresh adds minimal network traffic.
- security: Improves auditability, but needs scoped authentication and retention controls for job results.
- depends on: Durable asynchronous job schema; Background worker and output queue; Surface authentication and redaction policy


## What it asked for

### `s10-qrm2` (skill) — offline_audio_delivery_retry
- does: When generated audio is received but the cellular link drops during delivery, atomically buffer the incomplete audio chunk on the existing microSD failure buffer, resume upload when connectivity returns, and expose a clear LED error/retry state. Delete the SD copy only after server acknowledgement.
- must be on-device because: Only firmware can detect the local modem/link failure and preserve bytes before they are lost; it must work while disconnected and cannot depend on a live voice turn.
- trigger: Automatic network upload failure/reconnect event on the device; no new button gesture required.
- storage: Use the existing FATFS microSD failure-buffer policy, with bounded queue metadata (sequence, byte count, checksum, retry count) and FIFO eviction/error when capacity is exhausted. Do not use SD for routine storage.
- RAM budget: 16–32 kB ring buffer plus small metadata (well below the 211,608 B application RAM budget); stream to SD rather than holding complete recordings in RAM and share the existing full-duplex I2S path unchanged.

## Its own summary

Proposed background workday briefs, inbox triage with draft-only replies, daily closeout checklists, authenticated browser change watches, a unified cross-surface Jobs inbox, cheaper asynchronous model routing, typed/pruned memory, and read-only Mac observability. Also requested an on-device offline audio delivery retry using the existing microSD failure buffer, staying within the nRF9160's 211,608 B app RAM and one full-duplex I2S path. The highest-value remaining work is implementing durable background jobs, audio delivery, browser enqueue, and reviewable draft/status surfaces.

**Biggest unknown:** Whether the relay already has a durable scheduler/job queue and pendant audio-output queue beyond the currently described five realtime tools; browser authenticated-job execution still appears unimplemented. I also need exact retention/authentication semantics for cross-surface job results before designing data flows.

