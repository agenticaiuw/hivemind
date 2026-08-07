# Harness derivation — mac-planner — round 10

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac planner confirmation mismatch** — POST /plan marks even a read-only Downloads listing as requiresConfirmation:true and says review before confirming, while granted execution contract says FULL_CONTROL_MODE bypasses actionRisk and has no confirmation gate. The UI/planner promise and actual enforcement can diverge.
  - evidence: POST http://127.0.0.1:8000/plan for read-only Downloads request returned status ready, requiresConfirmation:true, safety:'Full computer control is enabled. Review the plan carefully before confirming.', fullControl:true.

## Capabilities it proposed

### "“Every morning, check my calendar, unread email, and today’s files, then give me a short spoken brief with the meetings that need preparation and a proposed priority list.”"
- **useful because:** It turns scattered desktop information into a hands-free briefing the owner can play when convenient, without occupying a live conversation. It can also create a preparation checklist and identify conflicts before the day starts.
- **path:** relay-realtime schedules/accepts the routine and delivers a compact audio notification → browser harness reads calendar/mail web apps where permitted → mac-planner reads local files and writes a dated briefing/checklist → dashboard/iOS shows source links, transcript, and controls to rerun or disable
- **model tier:** Background planning model for extraction, deduplication, and summarization; realtime model only if the owner asks follow-up by voice. Use deterministic code for dates, unread counts, and meeting conflict detection.
- **latency:** Run asynchronously in 1–3 minutes before the chosen time; audio should be ready before the owner asks. No live wait is needed.
- **cost:** Roughly $0.02–$0.10 per run depending on email/file volume; token use is dominated by raw message text, so summarize locally and send only metadata/snippets to the model. Audio is a small additional cost.
- **security:** Mail, calendar, and filenames leave the Mac/browser boundary for processing. Redact unrelated message bodies and keep source URLs local where possible. Reading is opt-in per account. Creating calendar events, sending mail, or modifying files must be separate explicit actions; never infer permission from the routine’s read access.
- **missing:** A scheduler and durable per-routine permission scopes; Connectors for calendar/mail or a browser-bridge allowlist; Audio generation/queue and a pendant-playback notification path; A real confirmation gate for any write or external side effect

### "“Clean up my Downloads every Friday: group files by project, rename obvious duplicates, and show me a review list before anything is deleted.”"
- **useful because:** The owner gets a consistently usable Mac without spending attention on filing. A review-first mode makes the result trustworthy and lets them approve only the risky changes.
- **path:** mac-planner inventories Downloads and project folders, computes proposed moves/renames, and creates an undo manifest → mac-vision handles ambiguous GUI-only files/apps only when needed → dashboard/menubar presents a diff with checkboxes and an Approve button → relay/pedant announces that the review is ready; iOS can approve selected reversible moves
- **model tier:** Cheap background model for filename classification and project matching; deterministic filesystem code for hashes, duplicate detection, path validation, and the move operation. Realtime is unnecessary.
- **latency:** Inventory under 30 seconds for a normal Downloads folder; classification can finish in a few minutes asynchronously.
- **cost:** Typically under $0.01–$0.05 per run because only filenames, sizes, and small extracted metadata need model tokens. Avoid uploading file contents unless the owner opts in.
- **security:** The current FULL_CONTROL_MODE bypasses action-risk confirmation, so delete/move operations are dangerously permanent. Default to no deletion, quarantine rather than remove, never follow outside-scope symlinks, and require explicit approval of the exact diff. Keep an atomic manifest to reverse moves; encrypt or locally retain it.
- **missing:** Safe filesystem inventory and hash helper; Per-folder rules and exclusions; Review/approval API with idempotent job IDs; Quarantine plus robust undo support; Re-enable action-risk confirmation in FULL_CONTROL_MODE

### "“Research this topic and leave me a concise source-linked briefing on my Mac, with an audio version I can play later.”"
- **useful because:** The owner can delegate multi-source research while continuing other work, then consume the result hands-free. A saved brief and citations make it useful beyond a one-off voice answer.
- **path:** relay accepts the request and tracks an asynchronous job → Cloudflare Browser Run gathers public pages server-side; mac-planner only writes the final Markdown/audio manifest locally → dashboard shows progress, citations, transcript, and a rerun button → pendant/iOS announces completion and plays or queues the audio
- **model tier:** Cheap background research/synthesis model with bounded source count and token budget; use realtime only for conversational refinement after delivery. Deterministic fetch/citation extraction where possible.
- **latency:** 5–10 minutes is acceptable for a thorough brief; stream progress/status rather than holding a voice turn.
- **cost:** About $0.05–$0.30 per brief depending on browser invocations and source text. Cap pages, deduplicate boilerplate, cache fetched pages, and summarize in stages to control tokens.
- **security:** Public pages can contain prompt injection; treat all page text as untrusted data and never let it authorize Mac actions. Do not access logged-in sites unless separately enabled. Cite exact URLs and timestamps; sanitize downloads and avoid writing executable content. Require confirmation before emailing or publishing the brief.
- **missing:** Async research-job orchestration and cancellation; Cloudflare Browser Run integration with source extraction and injection isolation; Audio synthesis/storage/playback queue; A local write endpoint with path allowlisting


## Changes it proposed to its own stack

### `integration` — Make FULL_CONTROL_MODE execute through a capability-scoped confirmation broker instead of bypassing actionRisk. Classify every action (read, reversible local write, destructive local write, external communication, purchase/credential action), require an expiring owner confirmation token for the latter classes, and return a dry-run diff plus job ID before execution. Preserve an emergency owner setting for trusted routines, but never silently treat arbitrary run_shell/run_applescript as safe.
- **owner gets:** The assistant can remain powerful without accidentally deleting files, sending messages, or spending money when a prompt is misunderstood or a malicious webpage is present.
- effort: Medium: shared policy module in local-agent, dashboard confirmation UI, relay token plumbing, and tests for retries/idempotency.  ·  risk: A stricter gate may interrupt trusted workflows or strand a job. Recover with per-routine allowlists for narrowly defined actions, clear pending approvals, and automatic timeout/cancellation; never fall back to unrestricted execution.
- cost: Negligible API cost; small dashboard/Worker implementation cost.  ·  latency: Adds seconds only for actions requiring approval; read-only and pre-approved reversible actions remain immediate.
- security: Strongly improves security by narrowing authority, preventing prompt/web content from becoming authority, and making approvals auditable.
- depends on: A canonical action schema and stable job IDs; Dashboard approval surface; Owner-authenticated confirmation tokens

### `memory` — Replace hand-written per-surface fleetContext prompt sections with a shared, typed context service: store facts with source, confidence, sensitivity, expiry, and last-used timestamps; retrieve only task-relevant facts into each job; run periodic contradiction/expiry pruning. Keep raw source data out of the prompt and expose a user-facing memory editor/export/delete view.
- **owner gets:** The assistant remembers useful preferences consistently across pendant, Mac, web, and iOS while avoiding stale or embarrassing details and reducing repeated explanations.
- effort: Medium-high: schema migration, retrieval/ranking, consent controls, and migration tests across all clients.  ·  risk: Bad retrieval or an incorrect fact could influence actions. Mitigate with provenance shown beside important facts, low-confidence facts treated as suggestions, expiry defaults, and never using memory alone to authorize side effects.
- cost: Usually lowers token cost by sending a small relevant slice instead of the whole context; storage cost is minor. One-time migration and indexing work.  ·  latency: Adds a small D1 lookup, ideally tens of milliseconds; pruning is scheduled background work.
- security: Sensitivity labels and deletion/export controls reduce unnecessary exposure, but the service becomes a valuable target and needs encryption/access auditing.
- depends on: Typed memory schema in D1; Per-surface identity/session binding; Prompt builder that accepts retrieved context rather than handwritten blocks

### `mac-harness` — Add transactional desktop jobs: each plan has a preview, stable job/action IDs, preconditions (expected app/path/hash), checkpoints, result receipts, and compensating undo where possible. On retry, skip completed action IDs rather than replaying clicks or shell commands. Prefer accessibility selectors and declarative APIs over coordinates.
- **owner gets:** Long workflows stop failing halfway or duplicating changes, and the owner can see exactly what happened and recover after a crash or dropped connection.
- effort: Medium: action journal in the existing atomic JSON store, precondition checks, undo adapters, and planner/executor protocol changes.  ·  risk: Preconditions can reject legitimate changes or undo can be incomplete. Show the blocked step, preserve the journal, and offer a fresh preview rather than guessing.
- cost: Negligible model/API cost; modest local disk use for journals and manifests.  ·  latency: Adds milliseconds for local checks and occasional seconds for previews; saves time otherwise lost to retries.
- security: Improves auditability and limits confused-deputy damage, but journal files may contain sensitive paths/content and should be permission-restricted and retention-limited.
- depends on: Canonical action schema; Confirmation broker for risky actions; Reliable result posting to /v1/bridge/work

### `model-routing` — Route deterministic Mac requests (open app/URL, list a directory, create a standard reminder, read a known file) through a typed intent parser and local executor; reserve gpt-5.6-luna planning for ambiguous multi-step tasks. Add a small background model only for classification/summarization and enforce token/page budgets.
- **owner gets:** Simple requests happen immediately and cheaply, while complex tasks still get careful planning. The owner experiences fewer unnecessary confirmations and less latency without reducing capability.
- effort: Medium: define intent/action schemas, confidence thresholds, fallback routing, and regression tests against existing plans.  ·  risk: A parser may misinterpret an ambiguous request. Require high confidence, show the resolved target for destructive or external actions, and fall back to the planner rather than guessing.
- cost: Can substantially reduce per-turn model tokens for routine Mac operations; deterministic paths have near-zero API cost.  ·  latency: Routine actions should drop to sub-second planning; complex actions remain unchanged.
- security: Typed allowlisted intents are safer than arbitrary shell/AppleScript, but must not silently broaden path or account scope.
- depends on: Canonical action schema; Confirmation broker; Path/app allowlists


## What it asked for

_Nothing._
## Its own summary

I established the Mac stack and proposed four concrete owner-facing capabilities/changes: scheduled morning briefs, review-first Downloads cleanup, source-linked async research with audio delivery, transactional/idempotent Mac jobs, shared relevance-ranked memory, typed low-cost routing, and—most urgently—a real confirmation broker because FULL_CONTROL_MODE bypasses the existing risk layer. A /plan probe also exposed a mismatch: the planner says requiresConfirmation:true even for a read-only request, but the execution contract says no gate runs. I recorded that finding.

**Biggest unknown:** I still need the owner’s explicit data/connectivity policy: which mail/calendar/browser accounts may be read, which folders are in scope, what routines may be pre-approved, and whether audio/briefings may leave the Mac. I also need implementation decisions for the missing scheduler, audio queue, confirmation-token service, and Browser Run integration before these capabilities can be built.

