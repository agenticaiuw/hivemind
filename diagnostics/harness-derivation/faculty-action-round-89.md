# Harness derivation — faculty-action — round 89

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser execution reliability** — Live backend currently reports browser bridge online=false with pendingCommands=9; recent browser_navigate jobs failed after ~45 seconds due to offline extension or no response. Failed receipts say no change occurred, but queued commands can accumulate.
  - evidence: GET /browser/status returned {online:false, pendingCommands:9}; GET /jobs returned failed browser_navigate receipts with durations 45386–45367ms and reasons extension offline/no answer.

## Capabilities it proposed

### "“I’m leaving now—carry out the prepared departure packet, but stop and tell me if anything no longer matches.”"
- **useful because:** Judgement can prepare a departure packet, but today there is no single action-side operation that binds the approved intent to the right private browser tab and Mac app, checks freshness immediately before each mutation, executes only safe steps, and returns evidence. This turns a spoken 'go' into dependable real-world completion without silently sending stale or wrong things.
- **path:** pendant → relay-realtime → faculty-judgement → faculty-action → browser-extension → mac-planner → mac-terminal → relay
- **model tier:** Use the realtime model only to resolve the spoken packet reference and report interruptions; use a cheaper background planner to compile and validate the packet, then deterministic executors for each typed step.
- **latency:** Acknowledge on the pendant within 1 second; validate and begin the first step within 3 seconds; speak per-step completion or pause on stale state. Long-running steps continue as durable jobs and are reported later.
- **cost:** About $0.01–$0.05 per packet for background compilation/validation, usually dominated by private-page extraction; realtime cost is limited to brief acknowledgement and exception speech. Mac/browser execution itself adds no model cost when typed.
- **security:** Private tab contents and local files remain on their owning surfaces except for minimum fields needed for validation. Never auto-send, purchase, delete, or publish unless the packet marks that exact irreversible step and the owner gives a fresh confirmation. Bind every step to session/tab identity, expiry, before-state hash, and idempotency key; if any check fails, pause rather than improvise.
- **missing:** A shared DeparturePacket/ActionStep schema between faculty-judgement and faculty-action; A precondition/postcondition checker that can read current browser and Mac state immediately before mutation; Per-step proof records and compensation/undo linkage, not merely a final job status; A durable coordinator that can resume after relay or Mac sleep without repeating completed steps

### "“If this changes while I’m away, carry out the fallback I approved—within these limits—and tell me exactly what you did.”"
- **useful because:** Today the mind can inspect pages and run a task, but it cannot safely connect a future observation to a bounded action policy. This would let the owner delegate time-sensitive contingencies—such as responding to a cancellation, moving a meeting, or completing a prepared fallback—without granting open-ended autonomy. Perception detects the triggering fact, judgement evaluates whether the policy still applies, and action executes only the pre-authorized bounded branch.
- **path:** pendant → relay-realtime → faculty-perception → faculty-judgement → faculty-action → browser-extension → mac-planner → mac-terminal → relay
- **model tier:** Use a cheaper background model to normalize trigger evidence and compile policy branches. Use deterministic predicates and typed executors for enforcement. Reserve realtime only for the owner’s setup, interruption, or exception report.
- **latency:** Register a policy in under 5 seconds. On a qualifying event, evaluate in under 10 seconds and begin a reversible branch promptly; pause for a fresh spoken confirmation when a branch is irreversible, ambiguous, or outside its limits.
- **cost:** Roughly $0.01–$0.08 per triggered policy, dominated by private-page/calendar reads; idle monitoring should use event pushes or low-cost polling rather than realtime inference.
- **security:** Policies must be capability-scoped, time-bounded, destination-scoped, and budget-limited—not general permission to act. Store only the minimum trigger and action fields, redact private evidence in relay logs, and require confirmation for sending, purchasing, deleting, publishing, or contacting a new recipient. Every execution needs a receipt tied to the triggering evidence and policy version; revoke immediately when the owner says stop.
- **missing:** A conditional-policy schema with explicit predicates, branches, limits, expiry, and revocation; Event correlation across authenticated browser sessions, Mac Calendar/Mail/files, and relay events; A policy evaluator that distinguishes a genuine state transition from page noise and prevents repeated firing; A secure policy registry and per-branch approval/receipt audit trail


## Changes it proposed to its own stack

### `integration` — Add a two-phase cross-surface action coordinator. Phase 1 (prepare) asks browser-extension and Mac executor to resolve each typed action against its current tab/app, capture a redacted before-state hash and proposed after-state, and reserve an idempotency key without mutating. Phase 2 (commit) executes steps in dependency order only if all required reservations are fresh; after every mutation it records proof and evaluates the postcondition. On partial failure it stops, marks the packet mixed, and invokes only declared compensations (or presents a precise manual recovery list).
- **owner gets:** The owner can say one clear 'go' and avoid half-finished real-world tasks: no email sent from the wrong tab, no reminder duplicated after a reconnect, and no later claim of success without evidence. If one site changes while leaving, the system safely pauses instead of guessing.
- effort: Medium-high: typed action/precondition schema, prepare adapters for AppleScript and browser refs, coordinator state machine, durable proofs, and compensation tests across sleep/reconnect.  ·  risk: A reservation can become stale between prepare and commit; enforce short TTLs and revalidate immediately before each mutation. Compensation may itself fail, so never claim rollback without a receipt; expose mixed state and offer retry/manual recovery. Roll out read-only prepare first.
- cost: Low API cost because prepare uses typed reads and hashes; background validation roughly $0.01–$0.04 per packet. Storage is small per step (IDs, hashes, receipts).  ·  latency: Adds roughly 0.5–2 seconds for prepare before the first visible mutation, but reduces costly retries and duplicate actions.
- security: Improves safety: least-privilege per surface, redacted proofs, exact tab/session binding, no irreversible commit without explicit step-level confirmation. Requires careful protection of before-state snippets and idempotency tokens.
- depends on: Shared DeparturePacket/ActionStep contract from faculty-judgement; Existing browser command queue and Mac action receipts; A durable job/coordinator store; owner-granted Accessibility remains optional for AppleScript/typed routes but GUI-only steps stay blocked

### `browser-harness` — Add a browser-bridge readiness gate and command watchdog before enqueue: require an online poll heartbeat newer than a short TTL, an attached tab/window identity, and zero stale pending commands; otherwise do not enqueue. Give each command a deadline shorter than the 45-second transport timeout, cancel/expire it explicitly, and surface a structured blocked receipt with the exact recovery (open Safari, enable bridge, dismiss dialog, or reattach tab). Add a sweeper for orphaned pendingCommands so failed browser work cannot accumulate and later run against a different tab.
- **owner gets:** When the owner asks the mind to act, it will fail fast and explain what to fix instead of waiting nearly a minute, leaving nine queued commands, or potentially replaying an old action in a newly opened tab. This is especially important for private-account actions while the owner is away.
- effort: Medium: heartbeat/affinity preflight, deadline and cancellation states in the bridge queue, orphan sweeper, and tests for Safari dialogs, sleep/wake, extension restart, and tab replacement.  ·  risk: A transient heartbeat loss could reject a safe action; allow an explicit retry from the receipt, but never silently retry writes. Queue cleanup must preserve audit records while deleting executable commands. Keep the current behavior as fallback behind a feature flag.
- cost: Negligible model/API cost; small relay storage for terminal receipts and periodic sweeper requests.  ·  latency: Healthy actions start faster (sub-second preflight); blocked actions return in under 2 seconds instead of ~45 seconds.
- security: Reduces stale-tab and replay risk by enforcing session/tab affinity and expiring commands. Do not include page contents in readiness logs.
- depends on: Existing browser command queue with request IDs and tab/session affinity; GET /browser/status; POST /browser/result/:commandId; Durable receipt storage and job cancellation semantics


## What it asked for

_Nothing._
