# Harness derivation — unified — round 250

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “do this,” stage the risky action, tell me what is waiting, and let me approve it with the pendant’s physical button; then carry it out exactly once and tell me what happened—even if the Mac or relay restarted."
- **useful because:** This closes the currently broken approval promise and makes the pendant a real consent boundary: the owner can approve a browser/Mac action without trusting an invisible software flag, and a crash cannot silently turn an approval into a duplicate action.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the spoken summary and confirmation; deterministic relay/Mac code for digest, nonce, lease, execution, and receipts; background model optional for explaining the result.
- **latency:** Stage acknowledgement under 1 s; physical approval reflected within one reconnect/heartbeat (normally under 2 s); execution status within 5 s for local actions. No action runs before the approval receipt is verified.
- **cost:** Usually <$0.01 per invocation when the spoken summary uses a small realtime turn; deterministic storage and receipt work dominate neither latency nor cost.
- **security:** The pendant receives only an opaque transaction nonce and digest, never page contents or secrets. Bind approval to plan digest, world fingerprint, expiry, and monotonic anti-replay counter; require a fresh physical approval for off-machine, irreversible, or unrepeatable steps. Surface refused/expired/world-moved outcomes rather than retrying.
- **missing:** Implement relay persistence for the existing APPROVAL_STORE_CONTRACT and deliver the pending frame on the owner’s next conversation (the pendant cannot be interrupted out of band).; Connect POST /prepare to the planner and POST /approve to the physical_transaction_approval_latch event.; Give the execution a durable workbench context and a single final receipt joined to the approval nonce.

### "When you tell me something important, let me ask “why?” and receive the small set of source records that support it—what the pendant heard, what the relay stored, what the Mac/browser observed, and how fresh each source is."
- **useful because:** A fluent answer can otherwise hide whether it came from a stale memory, a browser observation, or an executed action. Evidence capsules make the system correctable and let the owner challenge one claim without exposing full transcripts, credentials, or private pages.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic provenance index selects and redacts evidence; a background model can compress it into a readable explanation. Realtime is only needed to answer the spoken follow-up.
- **latency:** Under 2 s for a bounded capsule of up to five evidence items; if evidence is stale or absent, say so explicitly rather than filling the gap with model inference.
- **cost:** <$0.01 per explanation; indexing and redaction are local/relay compute, with model tokens only for optional compression.
- **security:** Evidence is least-privilege and claim-scoped: no chain-of-thought, cookies, raw audio, or unrelated page content. Each item carries source, timestamp, integrity marker, and redaction status. Owner deletion of extracted facts must also remove their capsules, while action history remains intact.
- **missing:** A claim/evidence ID attached to owner-facing spoken assertions and a bounded provenance query spanning pendant events, relay receipts, Mac jobs, and browser results.; A redaction layer that returns excerpts or hashes rather than whole transcripts/pages.; A retention and freshness policy for capsules, including explicit UNKNOWN when the source cannot be rechecked.

### "My pendant or browser is not responding. Diagnose the whole path, explain the single most likely fault, and—only for safe repairs—fix it and give me a receipt; otherwise tell me exactly what I must do."
- **useful because:** Today failures look like silence, stale jobs, or repeated timeouts. A single owner-facing recovery path can distinguish pendant/link, relay, Mac bridge, and browser faults, perform only idempotent wake/restart/lease cleanup, and stop wasting the owner’s time on blind retries.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic health probes and repair planner; a cheap background model ranks human-readable hypotheses. Realtime is only for the short spoken diagnosis.
- **latency:** Initial diagnosis under 3 s; safe repair under 10 s; revalidation under 5 s. Never claim repaired until a fresh post-repair probe passes.
- **cost:** <$0.01 per incident; probes and receipts dominate, with no model call for straightforward faults.
- **security:** Repairs are allowlisted, idempotent, and scoped to the named surfaces: wake browser bridge, restart polling, clear stale command lease. Opening macOS permission settings is suggested but never represented as success. Preserve before/after health evidence and require confirmation for anything beyond safe repairs.
- **missing:** A typed owner-facing diagnosis route that correlates pendant events, relay receipts, Mac jobs, browser leases, and system health.; A repair result schema with before/after probes, idempotency key, and explicit blocked-permission outcome.; A small spoken status vocabulary for healthy, degraded, repaired, and owner-action-required.

### "Give me a temporary, narrowly scoped delegation—such as “handle this one site and task for ten minutes”—that I can revoke from the pendant, and refuse every action outside that exact scope."
- **useful because:** Today the Mac, browser, relay, and approval routes effectively share one broad bearer authority. A single mistake or compromised session can reach beyond the owner’s spoken intent. Scoped delegation would let the owner safely hand over a bounded task without granting the system general control.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic capability-token issuance, scope matching, expiry, revocation, and enforcement; realtime model only translates the owner’s request into a proposed scope and reads back the final boundary.
- **latency:** Scope preview under 1 s; pendant revocation effective within one heartbeat and under 2 s locally; every action checks the token before dispatch.
- **cost:** Under $0.01 per delegation, mostly deterministic signing and audit writes; no model call is required for enforcement.
- **security:** Use an audience-bound, short-lived, signed token containing allowed surfaces, origin/path patterns, action classes, resource IDs, maximum spend/volume, expiry, and a revocation epoch. Never pass cookies or secrets into the token. Default deny on ambiguous scope, navigation, account change, stale heartbeat, or relay uncertainty. Preserve an immutable issuance/revocation/action audit trail.
- **missing:** A real authorization boundary distinct from the single AGENT_TOKEN, enforced by relay, Mac executor, and browser bridge.; A scope compiler that turns spoken intent into a reviewable allowlist and refuses unsupported constraints rather than broadening them.; Pendant delivery and revocation acknowledgements that work across link loss, with fail-closed expiry on every surface.


## Changes it proposed to its own stack

### `relay` — Add a lease_until/lease_owner to relay_jobs, requeue expired processing jobs, and make every Mac execution carry an idempotency key tied to its workbench context. Also make the orchestrator close its action ledger on terminal success/failure, then run a startup reconciliation that only resumes steps whose replaySafety is idempotent/additive and whose lease is still valid; all other steps become owner-visible 'needs approval' rather than replaying.
- **owner gets:** A Mac sleep, browser disconnect, or relay restart will no longer leave work stuck for 24 hours or duplicate an unrepeatable action such as sending a message, while safe file/status work can recover without making the owner start over.
- effort: Medium-high: schema migration and sweep worker, executor idempotency plumbing, ledger close calls, and crash/restart integration tests across browser and Mac jobs.  ·  risk: A lease race could cause two workers to contend; enforce compare-and-set claims and idempotent receipts, and default ambiguous/inflight/unrepeatable steps to blocked. Reconciliation must be dry-run logged before enabling automatic safe resumes.
- cost: Negligible storage and worker CPU; one small D1 update per claim/heartbeat and periodic sweep. No model cost.  ·  latency: Normal jobs gain one claim/receipt write; recovery begins on the next sweep (target under 30 s) instead of waiting for TTL pruning.
- security: Improves safety by narrowing replay to explicit replaySafety and retaining approval for risky steps. Does not grant new authority; it should preserve the existing single-token limitation until a separate authorization boundary exists.
- depends on: Use the existing actionLedger replaySafety/riskTier classification rather than inventing a reversibility vocabulary.; Wire the existing workbenchTransaction commit/retry engine into production execution.; Add integration tests for browser command lease expiry and Mac crash between inflight record and receipt.


## What it asked for

_Nothing._
