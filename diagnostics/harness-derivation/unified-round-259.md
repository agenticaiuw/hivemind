# Harness derivation — unified — round 259

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser readiness** — At 2026-08-09T03:33Z the Mac agent, relay, browser extension, Accessibility, Screen Recording, and required automation grants are all online/ready; Safari has one YouTube tab and no pending browser commands. This supersedes the older denied-permission context for future proposals.
  - evidence: GET /ops/snapshot returned agent.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser online=true, relay reachable=true, pendingCommands=0, requiredMissing=[]

## Capabilities it proposed

### "“Forget this fact completely.” Then show me exactly what was removed and what is still pending off-device."
- **useful because:** The system extracts facts the owner never explicitly created, yet there is no owner-visible, individually addressable erase path. This makes memory trustworthy: the fact, derived copies, and evidence capsule are removed together, while relay replication is honestly reported as requested-and-pending and action history remains auditable.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** deterministic/background; no realtime model unless the spoken request needs disambiguation
- **latency:** Under 2 seconds for lookup and local deletion; off-machine erase acknowledgement may remain pending and be polled in the background.
- **cost:** Near-zero model cost for an exact fact ID; small background relay requests dominate.
- **security:** Require an exact owner-selected fact or a spoken disambiguation when multiple matches exist. Never delete job history as a side effect. Redact evidence previews by default and authenticate relay deletion receipts.
- **missing:** Owner-facing list of extracted facts with stable IDs and recognizable evidence; One transaction spanning facts.json, context-graph entities/relations, and evidence capsules; Relay/D1 and R2 tombstone plus replication-status protocol; Dashboard and pendant confirmation receipt

### "“What did you promise to do that still has no proof?” Give me only unresolved commitments, with the exact next thing you need from me."
- **useful because:** A commitment can be spoken, handed to the Mac, partially completed, or completed without evidence. Existing evidence querying can find candidates, but the owner needs a conservative cross-surface answer that distinguishes proven, contradicted, expired, and unknown instead of claiming success from a job receipt.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for periodic reconciliation; deterministic evidence scoring first, low-cost planner only for ambiguous natural-language commitments
- **latency:** On-demand answer in 3–5 seconds; reconciliation can run asynchronously after browser/Mac results arrive.
- **cost:** Low: route reads and evidence scoring dominate; use the expensive realtime tier only when the commitment text or binding is ambiguous.
- **security:** Search only the commitment's explicitly bound tabs/apps and time window. Return evidence excerpts with source and timestamp, not broad browser contents. Never mark a commitment complete from absence of an error alone; ask before taking a new external action.
- **missing:** Durable commitment records with lifecycle and evidence policy; A join that correlates relay jobs, Mac receipts, browser results, and delivery receipts; Evidence confidence/provenance schema and contradiction handling; Owner-facing unresolved queue and dismissal flow

### "“Pause this task safely; I’ll continue tomorrow.” Tell me what is finished, what is frozen, and what cannot be resumed without asking me again."
- **useful because:** A deliberate pause is different from crash recovery: the owner should be able to stop a multi-surface task without leaving a browser command running, a Mac job half-applied, or an approval silently expiring. A signed checkpoint makes tomorrow's continuation understandable and prevents the system from pretending that a partial task completed.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic orchestration with a cheap background summarizer; realtime tier only speaks the concise confirmation
- **latency:** Acknowledge the pause within 1 second; checkpoint and receipts settle within 10 seconds, with explicit pending states for browser/Mac work that cannot stop immediately.
- **cost:** Low model cost; state snapshots, lease cancellation, and receipt reconciliation dominate.
- **security:** Pause must not undo completed external actions. Freeze or cancel only actions classified idempotent/additive; mark unrepeatable or unknown steps as requiring fresh approval. Do not snapshot page secrets or raw audio. The pendant's physical approval latch remains required for any later irreversible continuation.
- **missing:** A first-class pause/cancel protocol spanning relay jobs, Mac workbench contexts, and browser command leases; Checkpoint schema with completed steps, durable outputs, held leases, expiry, and resume decisions; Safe browser quiescence acknowledgement and Mac action cancellation receipts; Owner-visible continuation summary and explicit re-approval on stale world state

### "“For the next 30 minutes, work only in this browser tab and this project folder; you may draft but never send, delete, purchase, or contact anyone.”"
- **useful because:** The owner currently has to trust a whole agent credential and a broad action surface. A temporary, human-readable work envelope would let them delegate bounded work without granting unrestricted access. The envelope would be enforced independently at relay, Mac, and browser boundaries and expire even if the conversation disappears.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic policy enforcement; background model only translates natural-language limits into a reviewed policy, never relaxes them
- **latency:** Create and acknowledge the envelope within 2 seconds; every action checks it locally before dispatch.
- **cost:** Low runtime cost; policy matching and signed checks dominate, with negligible model cost after creation.
- **security:** Default deny outside the named tab, folder, action types, destinations, and expiry. Prevent path traversal, tab substitution, credential extraction, and policy widening by prompt injection. Bind the envelope to a browser session, Mac path fingerprints, relay job, and physical pendant nonce; show every denied attempt.
- **missing:** A signed capability-token format shared by relay, Mac agent, and browser bridge; Enforcement hooks before every Mac and browser action, not just plan creation; A path/tab identity attestation and anti-substitution check; Expiry, revocation, and inheritance rules for child jobs; Owner-visible audit of allowed and denied actions


## Changes it proposed to its own stack

### `relay` — Add expiring leases and an idempotent requeue sweep to relay_jobs, then have the Mac worker renew/settle the lease and attach the lease epoch to every receipt. On restart, requeue only expired processing jobs; preserve the same job idempotency key and expose a clear owner-facing state: queued, running, recovered, failed, or awaiting approval.
- **owner gets:** If the Mac sleeps or loses network halfway through a task, the request will recover instead of appearing stuck for up to 24 hours or being accidentally run twice. The owner gets a truthful answer about whether the action resumed, rather than repeating themselves and risking duplicate sends or edits.
- effort: Medium: schema migration, claim/renew/requeue paths, worker heartbeat, receipt reconciliation, and crash/fault tests across relay and Mac bridge.  ·  risk: A lease timeout during a slow but healthy action could cause duplicate execution. Bind the lease epoch and idempotency key to the action ledger; require an adoption/reconciliation step when a late receipt arrives. Roll back by disabling requeue while retaining status visibility.
- cost: Negligible storage and request overhead; one heartbeat per active job. No model cost.  ·  latency: Recovery begins after a configurable short lease (for example 1–5 minutes) instead of the current 24-hour TTL; normal jobs gain only heartbeat latency.
- security: Lease ownership and epoch must be unguessable and authenticated. Do not let a stale Mac worker settle or mutate a newly claimed job.
- depends on: orchestrator must close completed action ledgers; relay_jobs schema needs lease_until/lease_epoch; worker must reconcile late receipts with idempotency keys; approval-pending jobs must not be requeued as executable work

### `hardware` — Add a small secure element with a device-unique non-exportable signing key and monotonic counter to the production pendant, and route physical approval, privacy-latch, and work-envelope attestations through it. Provision the public key during manufacturing; require relay and Mac to verify signatures before accepting an approval or capability grant.
- **owner gets:** A compromised browser, Mac process, or relay could otherwise manufacture the same approval event that a button press would produce. With a hardware-rooted signature, the owner’s physical gesture becomes a trustworthy boundary: remote software can request consent but cannot impersonate it or replay an old consent.
- effort: Medium hardware/firmware integration: secure-element driver, manufacturing provisioning, signed event envelope, relay/Mac verification, counter recovery tests, and a migration path for development boards without the chip.  ·  risk: Lost or replaced hardware needs a deliberate recovery/revocation ceremony. Counter corruption must fail closed rather than replay. Development units need an explicitly weaker test mode that can never be accepted as production identity.
- cost: Approximately $1–3 BOM cost in volume and a small standby/transaction power cost; no per-request API cost.  ·  latency: Usually a few milliseconds for signing; approval acknowledgement remains dominated by the link.
- security: Strongly improves anti-forgery and anti-replay guarantees, but creates manufacturing-key custody and device-replacement responsibilities. Never place secrets in firmware flash or send them to the relay.
- depends on: physical approval and privacy events need a versioned signed envelope; relay and Mac must verify device identity and monotonic counters; production provisioning and revocation records must exist; USB bench mode must be clearly separated from production trust

### `browser-harness` — Make every mutating browser command produce a verified before/after outcome, not merely an execution acknowledgement: bind the command to tab URL/origin and target reference, capture a redacted state hash before and after, and require a semantic success predicate (for example, the saved label or confirmation state). If the predicate is absent or the tab navigated, classify the command as unknown rather than successful.
- **owner gets:** The owner will stop hearing “done” when a click hit the wrong tab, a site ignored it, or a login/navigation race swallowed it. They get a truthful result—changed, unchanged, or unknown—with enough evidence to decide whether to retry, without exposing page contents.
- effort: Medium: browser extension protocol changes, per-command predicates, redacted state hashing, navigation/race handling, and receipt integration.  ·  risk: Some sites do not expose stable semantic markers, producing more unknown results. Never infer success from a screenshot alone; fall back to a visible confirmation request or leave the action unresolved. Keep bounded evidence to avoid collecting sensitive page data.
- cost: Small CPU/storage overhead per command; no meaningful model cost.  ·  latency: Adds one verification round or DOM/state read, typically tens to hundreds of milliseconds.
- security: Improves origin binding and prevents stale-tab execution, but state hashes must be salted/scoped so they cannot become cross-site tracking identifiers. Redact values and never hash raw secrets into relay-visible receipts.
- depends on: browser commands need declared success predicates and target bindings; browser result receipts need before/after fields; relay/Mac job receipts must preserve unknown distinctly from failed; browser session identity must be authenticated and bound to the command lease


## What it asked for

_Nothing._
