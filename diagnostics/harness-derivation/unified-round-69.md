# Harness derivation — unified — round 69

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **cross-surface execution health** — Mac bridge and relay are reachable, but Chrome browser extension is offline with 5 pending commands; Accessibility and Screen Recording are still ungranted, so vision GUI automation is unavailable.
  - evidence: GET /ops/snapshot returned browser.online=false, pendingCommands=5, accessibility.trusted=false, screenRecording.granted=false; devices discovery showed home-macbook-bridge online and home-chrome offline.
- **timezone consistency** — Owner memory says America/Chicago while the live machine context earlier reported America/New_York; scheduled jobs therefore need an explicit authoritative timezone before time-sensitive scheduling is trusted.
  - evidence: discover(owner) remembered.timezone=America/Chicago; established GET /machine-context reported timezone America/New_York.

## Capabilities it proposed

### "When something I asked you to do fails, tell me what broke, try the safest available alternate route (pendant, Mac, browser, or relay), and continue from the last verified step—without repeating a side effect or asking me to start over."
- **useful because:** Today a dropped browser command, offline Mac, or partial action leaves the owner guessing and risks duplicate submissions. A cross-surface recovery loop would turn failures into a transparent continuation with receipts and a single confirmation only when the next step could have an external side effect.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use a cheap background model for log clustering and alternate-route selection; use realtime only to explain the incident or ask for confirmation; use faculty-action for the actual side effect.
- **latency:** Diagnosis and route selection under 10 seconds; recovery can continue asynchronously. Pendant explanation should be under 2 seconds once a receipt exists.
- **cost:** Roughly $0.01–$0.05 per incident, dominated by log/context summarization; near-zero for deterministic receipt checks and route health probes.
- **security:** Failure logs may contain URLs, account names, or page snippets, so redact secrets and minimize context. Never retry non-idempotent browser/Mac actions unless an idempotency key and pre/post evidence prove they did not occur; require explicit pendant approval before any uncertain external submission.
- **missing:** A durable cross-surface failure ledger keyed by job, step, idempotency key, and evidence state; A recovery coordinator that can select an alternate executor and resume from a verified checkpoint; Health/capability probes and typed failure classes shared by relay, Mac, and browser; Owner-facing incident cards and pendant-readable recovery status

### "When I ask “what am I waiting on?”, give me one concise live answer combining my pendant conversation, unfinished Mac and browser jobs, pending approvals, scheduled work, and anything blocked offline—then tell me the single next action that would unblock the most important item."
- **useful because:** The owner currently has to remember which surface contains each unfinished thread. A unified waiting-on view turns scattered jobs, approvals, and device outages into an actionable answer, especially when the owner is away from the Mac and only has the pendant.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard → faculty-perception → faculty-judgement
- **model tier:** Deterministic aggregation and priority rules should do most of the work; use a cheap background model only to compress and rank ambiguous items. Realtime is needed only when the owner asks live through the pendant.
- **latency:** Under 2 seconds for the normal spoken status; under 10 seconds if stale jobs or remote surfaces require reconciliation.
- **cost:** Usually near-zero model cost for typed job/status aggregation; approximately $0.005–$0.02 when background summarization is needed. Storage is small append-only status metadata.
- **security:** The answer must not reveal private browser content or secrets merely because a job exists. Project only job titles, state, required owner action, and sensitivity labels; require confirmation before reading sensitive details aloud in shared spaces. Expire stale presence and approval data.
- **missing:** A cross-surface attention-state schema linking conversations, jobs, browser commands, schedules, approvals, and blockers; A priority/urgency policy that distinguishes owner action, autonomous work, waiting-for-device, and completed states; A privacy-aware spoken projection that summarizes sensitive items without exposing their contents; A single live status endpoint and pendant intent for waiting-on queries


## Changes it proposed to its own stack

### `relay` — Add a durable cross-surface recovery coordinator and failure ledger. Record every job step with executor, idempotency key, precondition, postcondition, receipt, failure class, and confidence that the side effect did or did not happen. On failure, classify transport/offline/auth/permission/validation/unknown, probe alternate surfaces, and generate a bounded recovery plan that resumes only from the last verified checkpoint. Unknown side-effect state must become a hold requiring owner confirmation, not an automatic retry. Expose recovery state in job receipts and dashboard/pendant notifications.
- **owner gets:** A failed request becomes a clear, recoverable incident instead of a duplicated booking, an abandoned form, or a mystery about whether anything happened.
- effort: Medium-high: shared event schema, D1 migrations, coordinator worker, executor adapters, deterministic idempotency checks, and dashboard plus pendant rendering.  ·  risk: Incorrectly classifying an unknown side effect could duplicate or omit an action. Default unknown to hold; cap retries; preserve raw receipts for audit; allow undo only where an existing compensating action is safe.
- cost: Low ongoing API cost (mostly deterministic routing; occasional cheap summarization); modest D1/R2 growth from receipts and evidence, bounded by retention policy.  ·  latency: Adds 1–3 seconds for health probes and receipt reconciliation; asynchronous jobs avoid blocking the live voice turn.
- security: Failure evidence needs URL/account redaction, strict per-job access control, and short retention. Do not copy private page content to alternate executors unless required by the recovery plan.
- depends on: Typed context projection so recovery sees only task-relevant facts; Durable browser command queue with idempotency and typed results; Action receipts/undo and explicit irreversible-action checkpoints; A shared health/status contract for Mac, browser bridge, and relay

### `memory` — Create a privacy-aware cross-surface attention ledger, separate from the existing knowledge graph and job history. Every active conversation thread, Mac job, browser command, scheduled routine, approval gate, and device outage publishes a compact state record: ownerAction, urgency, sensitivity, freshness, blocker, nextSafeStep, and source receipt. A deterministic projector resolves duplicates and stale records into one materialized “waiting on” view; it must retain opaque labels for sensitive items and redact content before spoken output.
- **owner gets:** They can ask one question and immediately know what needs their attention, what is progressing without them, and what is blocked—without opening the dashboard or remembering which device started the task.
- effort: Medium: define event schema, add publishers to relay/job/browser/Mac paths, implement D1 materialization and expiry, then add a pendant intent and dashboard card.  ·  risk: A stale or incorrectly prioritized item could distract the owner or hide a real deadline. Show timestamps and source, preserve raw events for audit, expire records conservatively, and provide a “show details” escalation rather than silently asserting certainty.
- cost: Low: mostly deterministic D1 writes/reads and no additional model calls; small bounded metadata storage with TTL cleanup.  ·  latency: One extra materialized read, typically tens of milliseconds; no impact on action execution.
- security: High-value metadata can itself reveal private activities. Encrypt or access-scope the ledger, store content references rather than page text, redact spoken projections, and honor a local privacy latch when available.
- depends on: A typed cross-surface event contract for jobs, browser, Mac, schedules, and device health; A privacy projection with sensitivity labels and field-level redaction; A deterministic priority policy and stale-state expiry; A new pendant/dashboard intent backed by the materialized view


## What it asked for

_Nothing._
