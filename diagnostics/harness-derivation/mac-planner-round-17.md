# Harness derivation — mac-planner — round 17

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Every weekday morning, give me a short brief of my calendar and important unread mail, and open the first meeting's materials on my Mac.”"
- **useful because:** The owner gets actionable context without manually checking several apps; the Mac can prepare documents while the audio brief remains hands-free and brief.
- **path:** dashboard → relay → mac-bridge
- **model tier:** Scheduled extraction and summarization should use a cheap background model; realtime is only used if the owner asks a follow-up by voice. mac-planner reads bounded Calendar/Mail sources, then uses mac_run_actions to open only the selected meeting links/files.
- **latency:** Under 60 seconds after the scheduled trigger; a 30–60 second audio brief is acceptable. Opening a file should happen immediately after the brief is generated.
- **cost:** Low: one small scheduled summarization call plus generated audio; dominant costs are audio synthesis/storage, not Mac actions. Keep source snippets capped and avoid sending full mail bodies.
- **security:** Mail/calendar content leaves the Mac only in redacted, bounded snippets. Never open an attachment or external URL selected from untrusted mail without explicit confirmation; opening a known calendar link is reversible but can leak presence to the service. Store the brief for a short retention period.
- **missing:** A durable scheduler for weekday jobs; A bounded calendar/mail-to-audio pipeline and audio playback/delivery path; A policy for trusted meeting domains and attachment confirmation

### "“After each meeting, prepare a follow-up workspace: open the meeting notes, create a draft summary file with attendees and action items, and show me the relevant unread emails.”"
- **useful because:** It turns the few minutes after a meeting into a repeatable workflow, reducing forgotten commitments while keeping the final sending or filing decision with the owner.
- **path:** mac-bridge → dashboard → relay
- **model tier:** Use a cheap background model to structure the bounded calendar event and any owner-selected notes; use mac-planner for file creation and opening. Realtime is only for an optional voice correction, not for document synthesis.
- **latency:** Draft workspace within 1–2 minutes of the event ending; file creation/opening should take under 10 seconds once content is ready.
- **cost:** Low to moderate: one compact summarization call per meeting, with token cost controlled by attendee list, event description, and selected notes. No audio is necessary unless requested.
- **security:** Do not infer or invent action items; mark uncertain extraction. Write only to a dedicated drafts directory, never overwrite existing notes. Creating a draft is safe, but emailing, changing calendar events, or moving files requires explicit confirmation. Redact unrelated mail and exclude personal accounts unless selected.
- **missing:** Meeting-end event trigger and event-to-job linkage; A reliable notes-source selector (local file or owner-selected browser tab); A confirmation-aware email/calendar write tool if follow-up actions are later enabled

### "“Once a week, clean up my Downloads: group files by type and project, flag duplicates and stale installers, and show me a review list before anything is deleted.”"
- **useful because:** The owner gets a consistently usable Downloads folder without risking accidental loss; the assistant does the tedious classification and the owner retains control over deletion.
- **path:** mac-bridge → dashboard → relay
- **model tier:** Use deterministic file metadata/hash tooling for grouping and duplicate detection, with a cheap background model only for ambiguous project naming. Realtime is unnecessary unless the owner asks by voice.
- **latency:** Run unattended in the background, completing within a few minutes for a bounded directory; dashboard results should appear as each batch finishes.
- **cost:** Very low API cost if hashes and metadata stay local; only ambiguous filenames need model tokens. No audio unless the owner requests a spoken summary.
- **security:** Read only an allowlisted Downloads path. Never upload file contents by default. Moves should target a generated staging directory and be undoable; deletion, cloud upload, or opening suspicious files requires explicit confirmation.
- **missing:** Local metadata/hash operation exposed to the Mac harness; A recurring scheduler and review queue; Undoable batch move plus a confirmation-gated delete operation


## Changes it proposed to its own stack

### `mac-harness` — Add an execution journal with per-action risk labels, pre-state capture where feasible, idempotency keys, and a narrow confirmation gate for irreversible or external side effects (delete, send, purchase, credential changes). Preserve fast execution for opening apps/files, creating drafts, and reversible moves; expose undo for file moves and generated drafts.
- **owner gets:** Automations remain fast, but a mistaken instruction is less likely to delete data or send something publicly; the owner can see exactly what happened and recover common mistakes.
- effort: Medium: action wrapper, journal schema, preflight checks, and undo handlers across the local agent and dashboard.  ·  risk: A gate could interrupt a time-sensitive workflow, and incomplete pre-state capture could create false confidence. Recover by allowing owner-configured trusted destinations and making every skipped/failed action explicit.
- cost: Negligible API cost; small local disk usage for bounded journals and snapshots.  ·  latency: Milliseconds for ordinary actions; 1–3 seconds for preflight or confirmation-required actions.
- security: Strong improvement: least-privilege policy and auditability replace the current FULL_CONTROL path where actionRisk is dead. Secrets should never be copied into the journal.
- depends on: A stable action identity/idempotency format; Dashboard status UI for pending confirmations and undo; Owner privacy/approval defaults

### `memory` — Replace per-surface hand-written fleetContext prompt sections with a compact, typed context projection service: durable facts, current goals, and permissions are selected per job, with token budgets and provenance links. Automatically prune stale session details and keep sensitive mail/calendar facts ephemeral unless explicitly saved.
- **owner gets:** The assistant stays consistent across pendant, dashboard, iOS, and Mac without repeatedly paying to resend irrelevant history, while private details do not become permanent memory by accident.
- effort: Medium: projection API, provenance metadata, TTL/pruning jobs, and migration from fleetContext.js templates.  ·  risk: Over-aggressive pruning could lose an important preference; recover via explicit “save this” and a reviewable memory history. Projection bugs could hide context, so show source links and fallback to the last known safe projection.
- cost: Should reduce recurring token spend materially by shrinking every prompt; modest D1 storage for provenance and TTL metadata.  ·  latency: One lightweight D1 lookup per job; cache projections for active sessions.
- security: Improves data minimization and prevents cross-surface leakage; enforce account/surface scopes before projection.
- depends on: Typed entity/relation schema in D1; Per-surface permission scopes; Dashboard memory review controls

### `model-routing` — Introduce a job classifier before model invocation: deterministic Mac plans and bounded Calendar/Mail extraction use rules or a cheap batch model; document synthesis and web research use a slower background model; only live pendant turns and interruption handling use realtime. Attach a hard token/source budget to every job.
- **owner gets:** Routine work becomes cheaper and more predictable, while voice conversations remain responsive instead of waiting behind background tasks.
- effort: Medium: classifier, queue priorities, fallback rules, and per-job budgets/telemetry.  ·  risk: A classifier may send an ambiguous request to a weak model. Recover by detecting uncertainty/tool failures and escalating to the stronger model, with no repeated source fetches.
- cost: Likely meaningful reduction in recurring token and realtime-audio spend; classifier overhead is tiny compared with model calls.  ·  latency: Realtime unchanged; background tasks may complete more slowly by design, with progress shown in the dashboard.
- security: Budgets limit accidental broad data access; route sensitive tasks only to approved models and log model/data policy decisions.
- depends on: Job metadata including urgency, sensitivity, and required tools; Background queue/scheduler; Per-model data handling policy


## What it asked for

_Nothing._
## Its own summary

Grounded in the actual stack, I proposed four owner-facing workflows: scheduled calendar/mail morning briefs with Mac preparation, post-meeting follow-up workspaces, safe weekly Downloads triage, and a confirmation-aware Mac execution journal. I also proposed typed, privacy-scoped context projections and model routing that reserves realtime for live voice while using cheap/background tiers for routine work. The highest-value Mac improvement is restoring meaningful risk handling around the currently unrestricted FULL_CONTROL path without slowing reversible actions.

**Biggest unknown:** The owner's approval/privacy defaults and the missing scheduler/audio-delivery pipeline remain unresolved. Those determine whether briefs can be delivered automatically and which mail/calendar/file actions may run without confirmation.

