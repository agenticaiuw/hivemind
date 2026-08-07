# Harness derivation — faculty-action — round 45

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do this even if my Mac is asleep: when it wakes, carry out the reversible part, prove it actually happened, and tell me if anything was skipped.”"
- **useful because:** Today the system can queue speech/alerts and can run Mac/browser actions, but a decision made on the pendant does not have a single durable handoff that survives link loss, Mac sleep, or a stale browser session and then verifies the real-world result. This gives the owner trustworthy deferred action rather than a false ‘done’ receipt.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use realtime only to acknowledge capture and later announce completion; use a cheap background planner for decomposition/retries. Mac planner executes typed reversible actions, browser extension handles authenticated tabs, and mac-vision is fallback only when typed/browser controls cannot reach the target.
- **latency:** Capture acknowledgement under 300 ms locally; execution begins within 30 s of Mac/bridge reconnect; verification within 10 s per step. Expire leases after 24 h or at the user-specified deadline, never retry irreversible steps.
- **cost:** About $0.01–$0.05 per deferred job depending on planner retries; most cost is background model calls and optional vision screenshots, not realtime. Storage is small JSON receipts plus hashes.
- **security:** Persist only a redacted action plan, target fingerprints, deadline, and proof metadata; never persist page secrets or raw screenshots by default. Require explicit confirmation for send/delete/purchase. Bind jobs to the paired pendant and Mac, use idempotency keys, and show a visible pending/expired state so a stale command cannot execute silently.
- **missing:** A durable cross-surface action envelope with lease, deadline, idempotency key, and dependency graph; A reconnect worker that drains pendant-held intents to relay then Mac/browser in order; Typed proof-of-effect adapters (file hash, reminder ID, app state, browser DOM/value) plus a safe ‘could not verify’ result; A single owner-facing queue showing pending, running, verified, skipped, expired, and undoable jobs; Pendant firmware support to store a compact offline action envelope and LED/button acknowledgement

### "“Continue this on my Mac exactly where I left off on the pendant, with the same tabs, evidence, decisions, and one approval still waiting for me.”"
- **useful because:** The owner currently has separate conversations and action surfaces: a spoken task can produce a reply or job, but there is no owner-facing continuity when they move from wearing the pendant to sitting at the Mac. This capability makes the AI feel like one agent rather than repeated starts, while preserving the exact boundary between decided, executed, and awaiting approval.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use realtime only for the pendant handoff cue and short spoken status. A cheaper background model compiles the task capsule and reconciles state; mac-planner executes typed work, browser-extension reattaches private tabs, and mac-vision inspects only when structured state is unavailable.
- **latency:** Pendant can mark a handoff in under 1 second. On Mac unlock/open, restore the capsule in under 5 seconds, then reconcile live state in under 15 seconds. Never block the owner from viewing the capsule while reconciliation runs.
- **cost:** Roughly $0.01–$0.04 per handoff, dominated by one compact reconciliation call; no realtime generation beyond the brief cue. Store hashes and structured facts rather than transcripts or screenshots.
- **security:** Bind capsules to the paired owner/device, encrypt them in transit and at rest, redact secrets, and preserve confirmation gates. Do not reopen a private tab or repeat a side effect solely because it appears in the capsule; compare idempotency keys and current state first. Expire capsules and let the owner revoke them from either surface.
- **missing:** A versioned task-capsule schema containing goal, completed steps, evidence references, unresolved questions, approvals, idempotency keys, and next-safe action; Relay synchronization with conflict resolution when pendant and Mac both receive updates while briefly disconnected; Browser tab/session restoration linked to capsule evidence without storing page secrets; A Mac dashboard/notification that opens the capsule and clearly separates verified facts from stale or pending state; Cross-device resume tests covering sleep, duplicate delivery, changed tabs, and revoked approval


## Changes it proposed to its own stack

### `relay` — Add a durable deferred-action envelope and reconnect executor spanning pendant→relay→Mac/browser. Envelope fields: jobId, idempotencyKey, origin, typed steps, required capabilities, confirmation class, lease/deadline, dependency IDs, redacted target fingerprint, and status. Relay claims exactly once, Mac bridge heartbeats capability readiness, local agent executes only when prerequisites are true, and each step emits proof-of-effect or an explicit unverifiable result. Reconnect drains in dependency order; expired or capability-blocked jobs remain visible rather than being silently retried.
- **owner gets:** A request made while wearing the pendant no longer disappears when LTE drops, the Mac sleeps, or Safari is unavailable—and the owner hears the difference between completed, skipped, and merely attempted.
- effort: Medium-high: relay D1 schema/worker, local-agent queue and typed proof adapters, pendant compact spool protocol, dashboard state UI, and end-to-end fault-injection tests for duplicate delivery and sleep/reconnect.  ·  risk: A retry could duplicate a side effect; prevent this with idempotency keys, per-step leases, and no automatic execution of confirmation-class actions. If proof fails, stop and report unverified. Recover by exposing cancel/undo where supported and retaining receipts.
- cost: Negligible relay storage/compute; background planner calls only for ambiguous plans. Optional vision verification adds screenshot/model cost per difficult step.  ·  latency: No impact on live conversation; offline capture is immediate. Reconnect adds queue polling (target <30 s) and proof latency (typically <10 s).
- security: Encrypted paired-device transport, least-privilege capability claims, redacted targets, short retention for proof artifacts, and confirmation gates for send/delete/purchase.
- depends on: durable browser runner and authenticated session reattachment; Mac bridge heartbeat exposing readiness/permission state; typed action receipts plus proof adapters; pendant offline envelope storage


## What it asked for

_Nothing._
## Its own summary

Discovered the live execution state and proposed a new cross-surface capability/change: deferred reversible actions captured on the pendant, durably leased through relay, executed after Mac/browser reconnect, and verified with typed proof-of-effect. Current blockers are concrete: Mac Agent readiness=false because Accessibility and Screen Recording are not granted; home-chrome is offline with 3 pending commands. Relay and Mac bridge are online. I still need those permissions/browser bridge availability, plus implementation of the durable action envelope, reconnect drain, and proof adapters before I can honestly claim deferred actions complete.

**Biggest unknown:** Whether the owner wants deferred actions to run automatically at reconnect for all reversible operations, or only after a spoken pendant confirmation when the Mac becomes available.

