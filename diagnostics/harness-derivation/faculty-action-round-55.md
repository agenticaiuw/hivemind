# Harness derivation — faculty-action — round 55

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If you get interrupted, pick up where you left off and finish this without doing anything twice.”"
- **useful because:** Long actions spanning the pendant, always-awake relay, Mac, and private browser currently stop at a dropped link, sleeping Mac, or expired browser lease. This would persist a typed checkpoint after every verified step, resume when the responsible surface returns, skip already-committed idempotent steps, and give the owner a concise spoken completion receipt naming what ran, what was skipped, and what still needs them. It is especially valuable for private-page workflows that cannot be moved to the relay.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the cheap background/job model to maintain checkpoints, retry transient failures, and compose receipts; invoke realtime only for the owner's live request or a concise interruption notice. Use the Mac planner for step decomposition, browser extension for authenticated tabs, relay for durable wake/retry, and pendant for offline acknowledgment/receipt playback.
- **latency:** Acknowledge interruption/resume state to the pendant within 1–2 seconds when online; resume on surface heartbeat within 10 seconds. Individual browser retry may take up to 60 seconds, but never block the voice turn. Receipt generation under 2 seconds after the final checkpoint.
- **cost:** About $0.01–$0.08 per resumed workflow depending on planner retries and receipt length; durable orchestration and browser polling dominate, not model inference. No model call for simple checkpoint transitions.
- **security:** Persist only action type, idempotency key, target surface, evidence hash, and redacted result—not page secrets or raw private content. Private tabs stay on the Mac/browser bridge; relay stores encrypted metadata and short-lived leases. Never auto-resume an irreversible send, purchase, deletion, or submission: stop at that checkpoint and require the owner's existing confirmation policy. Expire leases and allow cancel/undo from the dashboard.
- **missing:** Durable cross-surface job/checkpoint runner with restart-safe state and retry classification; Progress/event stream from browser bridge instead of the current single blocking 45-second wait; A relay-to-Mac heartbeat/wake handshake and a user-visible resume/cancel queue; Typed checkpoint schema shared by /execute, browser commands, and receipts

### "“While you’re doing that, change the plan: use the other account, skip that part, and continue.”"
- **useful because:** Today a long-running Mac/browser task is effectively committed to its initial plan: the owner must cancel it and start over, risking stale work, duplicate edits, or losing the authenticated page state. This capability lets the owner correct an in-flight job from the pendant. The relay pauses dispatch, judgement validates the requested delta against the current checkpoint, perception re-reads only the affected state in the private browser or Mac, and action resumes from the first uncommitted step with a spoken summary of what changed. It is a genuinely cross-node behavior: the pendant supplies low-friction intent, the always-awake relay arbitrates a live lease, the Mac/browser hold private state, and the action facet performs the bounded splice.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the brief spoken correction and immediate acknowledgment. A cheaper background model computes the plan delta and receipt; faculty-judgement authorizes the splice, faculty-perception verifies affected state, and faculty-action executes it. No expensive model call for a simple skip of an unstarted step.
- **latency:** Acknowledge the correction within 1 second and pause new dispatch within 2 seconds. Show the revised step list within 5 seconds; resume within 10 seconds after verification. Never wait synchronously in the voice turn.
- **cost:** Roughly $0.01–$0.06 per correction, dominated by one planner/verification call and any browser snapshot; relay pause/resume traffic is negligible.
- **security:** Corrections must be scoped to the named job and expire with its lease. Never silently broaden permissions or switch to an account without displaying the selected account and affected steps. Re-read private state before applying a delta; do not persist page contents or credentials. If a correction touches send, purchase, deletion, or submission, stop at the existing confirmation boundary rather than treating the correction as approval. Keep an immutable before/after plan diff and allow cancel/undo.
- **missing:** A first-class pause-and-replan protocol carrying a jobId, current step, requested delta, and revision number; Atomic compare-and-swap of the job plan so a late worker cannot execute the superseded plan; Pendant-to-relay interrupt messages while a background job owns the action lease; A typed plan-diff and affected-state verification record exposed in the job receipt and dashboard


## Changes it proposed to its own stack

### `integration` — Add a cross-surface Action Checkpoint Protocol shared by relay, Mac agent, and browser bridge. Each step emits an append-only record {jobId, stepId, surface, idempotencyKey, preconditionHash, evidenceRef, outcome, committedAt}; the relay owns a durable state machine and leases, Mac/browser heartbeats renew leases, and reconnecting workers ask for the next uncommitted step. Resume logic must classify outcomes as committed, safely retryable, or unknown; unknown steps pause rather than repeat. Expose checkpoint progress and a resume/cancel control through the existing jobs, journal, browser poll/result, and pipeline event routes.
- **owner gets:** A dropped connection or sleeping Mac would no longer leave the owner guessing whether a form was filled, a file was moved, or a reversible step needs repeating. Work would continue safely and the spoken receipt would distinguish completed, skipped, and owner-required steps.
- effort: Medium-high: shared schema and durable relay state machine, adapters in local-agent executor and browserBridge, reconnect tests across process restart, and dashboard/pendant receipt plumbing.  ·  risk: A false committed classification could skip needed work; a false retry could duplicate a side effect. Default unknown to pause, require evidence hashes for commit, and retain cancel/undo. Recover by replaying the append-only log and expiring leases.
- cost: Negligible storage and inference cost; roughly a few hundred bytes per step plus existing job/receipt writes. Background model only for human-readable receipts.  ·  latency: Adds one local checkpoint write per step (typically <50 ms); reconnect resume begins on heartbeat, target under 10 s.
- security: Metadata-only records with redacted evidence references; private page content remains on Mac. Encrypt relay state, scope leases to job and surface, and avoid persisting credentials or raw form values.
- depends on: Durable browser job runner and non-blocking progress polling (chg-16bc5dee / chg-14accc01 gaps); Existing /jobs, /journal, browser poll/result, and pipeline event plumbing; A relay heartbeat/wake path to notify the Mac agent when a queued job can resume

### `integration` — Introduce revisioned live-plan splicing across relay and local-agent workers. Add a job revision and optimistic compare-and-swap endpoint/state: the relay marks a running job paused, accepts a typed delta (skip, replace target, change account, reorder), asks perception for affected-state evidence, and commits a new plan revision only if the worker’s last-seen revision still matches. Workers must reject superseded revisions before every side effect and emit a plan-diff receipt. Deliver pendant interrupt events through the live pipeline rather than waiting for the next voice turn.
- **owner gets:** The owner can correct an active task naturally instead of cancelling and restarting it. The system will change only future work, preserve completed progress, and prevent an old worker from acting on the plan the owner just replaced.
- effort: High: relay state-machine and event protocol, local-agent executor guards, browser command cancellation/renewal, planner delta generation, and dashboard/pendant controls; requires fault-injection tests for races and reconnects.  ·  risk: A pause race could allow one extra side effect or a malformed delta could target the wrong account. Enforce revision checks immediately before dispatch, pause at the next safe boundary, require affected-state evidence, and fail closed on ambiguity. Recover with existing receipts and undo where available.
- cost: Small persistent metadata and event overhead; one inexpensive planning/verification call per correction, with no ongoing realtime inference after acknowledgment.  ·  latency: Pause signal target under 2 seconds; revision validation adds tens of milliseconds per step; replanning target under 5 seconds.
- security: Job-scoped signed interrupt tokens, no raw private page data in relay events, account identity included in the diff, and existing irreversible-action confirmation remains mandatory.
- depends on: A durable job state machine with worker leases; Typed plan-diff and affected-state evidence schemas; Pendant interrupt transport over the live pipeline; Atomic revision checks in Mac and browser executors


## What it asked for

_Nothing._
## Its own summary

Discovered the live Mac bridge is online but the browser device is offline. The existing browser queue has request IDs/idempotency and session affinity, yet still blocks for a single 45-second lease; the proposed durable browser runner still lacks persistence, retries, and a result stream. I proposed a new cross-surface Action Checkpoint Protocol and the user-facing capability “If interrupted, pick up where you left off without doing anything twice,” using relay-owned durable leases, append-only step records, evidence hashes, reconnect resume, and safe pause on unknown side effects. I still need the durable runner/progress polling, relay↔Mac heartbeat/wake path, and typed checkpoint schema implemented; no further permission request this round because the requested Mac/device access and tools remain pending upstream.

**Biggest unknown:** Whether the orchestrator will grant the pending Mac firmware inspection/build tool and owner’s authoritative action/approval criteria; those determine whether I can validate the 24 kHz end-to-end path or safely exercise resume behavior against real devices.

