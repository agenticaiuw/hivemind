# Harness derivation — unified — round 169

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Stage this browser action and ask me to approve it on the pendant; only submit after the pendant confirms the exact page, amount, and destination.”"
- **useful because:** Makes high-consequence browser work (send, purchase, publish, delete) genuinely safe: the Mac/browser can reach authenticated sessions, while the pendant supplies a deliberate physical consent that cannot be forged by a stale tab or a replayed relay job.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** deterministic approval and digest checks; background model only summarizes the staged action; realtime model speaks the short confirmation
- **latency:** Stage in under 2 s; physical approval acknowledged locally immediately and submitted within 3 s after reconnect.
- **cost:** Near-zero model cost for digest/verification; roughly $0.001–$0.01 only if a model is needed to summarize complex page fields. Browser and relay I/O dominate.
- **security:** Send only a normalized action summary and cryptographic digest to the pendant, never page secrets or form contents. Bind approval to tab/session, URL origin, field digest, expiry, and nonce; refuse if the page changes. Require confirmation for irreversible/off-machine actions.
- **missing:** Implement the relay half of the existing approvalHandoff contract and delivery/readback path; Wire browser form/action staging to the physical_transaction_approval_latch; Add a privilege boundary so approval is not equivalent to the Mac bearer token; Ensure orchestrator closes completed ledgers and relay jobs have expiring leases

### "“Am I private right now?”"
- **useful because:** A single spoken answer backed by a convergence receipt prevents false reassurance: the pendant latch, microphone/playback state, queued relay work, Mac capture, and browser exposure are checked together instead of trusting one LED or one process flag.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** deterministic read-only checks and a fixed response template; no expensive model required
- **latency:** Under 1 s when connected; if any surface is unreachable, say exactly which claim could not be verified rather than returning ‘private’.
- **cost:** No model cost; a handful of authenticated reads dominate.
- **security:** Return only state and redacted diagnostics. Authenticate the latch ID and convergence receipt; never expose captured content. Treat unknown as unknown and never infer privacy from link loss.
- **missing:** Bind the local_privacy_latch state event to an authenticated latch ID usable by the server; Add Mac/browser capture-state adapters that work without Accessibility permission; Define a fail-closed response when relay or bridge evidence is stale

### "“Protect this site from the AI—never inspect it, click it, or submit anything there, even if I ask in a later conversation unless I physically unlock it on the pendant.”"
- **useful because:** The browser is the only node holding authenticated sessions, so a mistaken model plan or stale command can reach accounts the pendant cannot see. An owner-controlled protected-origin boundary makes privacy durable across conversations, Mac restarts, and relay jobs rather than relying on the model to remember a warning.
- **path:** pendant → browser → relay → mac-planner
- **model tier:** deterministic origin matching, command rejection, and audit receipts; no expensive model required
- **latency:** Reject a protected-origin inspection or action before dispatch, under 50 ms. Unlock should require a deliberate physical gesture and expire automatically.
- **cost:** Negligible model cost; small browser/relay policy checks dominate.
- **security:** Store only origin/pattern policy and opaque rule IDs, never credentials or page contents. Match registrable domain plus explicit subdomain/path exceptions to prevent lookalike bypasses. Fail closed when policy state is stale or the relay cannot verify the pendant unlock.
- **missing:** Browser extension enforcement before inspect and action dispatch; Relay-signed policy distribution and replay-resistant versioning; A pendant physical unlock event distinct from the existing transaction approval nonce, or an explicit reuse policy; Owner-defined protected-origin list and recovery procedure

### "“Freeze everything the agent is doing right now.”"
- **useful because:** A physical privacy latch stops capture, but it does not stop a queued browser submission, Mac automation, or relay job already in flight. The owner needs one panic action that immediately prevents further side effects across every surface, then leaves a durable receipt of what was cancelled versus already committed.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** deterministic control-plane operation; no model required
- **latency:** Pendant must enter freeze locally in under 100 ms; relay, Mac, and browser should acknowledge or report unreachable within 2 s.
- **cost:** Negligible model cost; small persistent state and cancellation traffic.
- **security:** The command must be authenticated, monotonic, fail closed, and immune to replay. Freeze must not claim to undo effects that already committed. It should cancel queued work, revoke browser command leases, stop new Mac dispatch, and mark in-flight work unknown when cancellation cannot be confirmed.
- **missing:** A cross-surface emergency-stop epoch enforced by relay, Mac executor, and browser bridge; Firmware event binding from the existing local latch/button path to the stop epoch; Cancellation semantics for POST /execute and browser commands; A receipt that separates cancelled, completed-before-freeze, and unverified

### "“Give this conversation a temporary power to do only these things, and nothing else.”"
- **useful because:** Today authorization is effectively one bearer credential, so a conversation that can read a calendar may also be able to reach unrelated Mac or browser actions. A short-lived, least-privilege capability token would let the owner safely delegate a bounded task without granting the whole agent access.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** Deterministic policy evaluation; planner model may propose actions, but it cannot expand the issued scope
- **latency:** Issue scope in under 500 ms; reject out-of-scope actions before dispatch in under 50 ms.
- **cost:** Negligible model cost; policy checks and signed-token storage dominate.
- **security:** Bind the token to conversation, surface, action types, target paths/origins, expiry, and a nonce. Do not treat natural-language intent as authorization. Escalation must require a new physical approval and a new token; log denied attempts without sensitive arguments.
- **missing:** A capability-token policy engine between the bearer token and action executors; Per-action enforcement in Mac and browser bridges; Pendant display/voice representation of the active scope and expiry; An owner-facing way to revoke the scope immediately

### "“Show me every place my request and its results went, then erase the transient copies.”"
- **useful because:** The owner currently cannot obtain one end-to-end data-flow account for a turn: microphone input, relay processing, Mac jobs, browser results, audio output, and queued artifacts are split across stores. A portable provenance-and-erasure receipt would make the system understandable and let the owner verify that temporary material was actually deleted.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** Deterministic event join, redaction, and deletion verification; background model only summarizes the receipt if requested
- **latency:** Receipt available within 2 s after a turn; deletion confirmation within 5 s, with explicit unknown states for offline surfaces.
- **cost:** No model cost for the receipt; bounded metadata storage and deletion scans dominate.
- **security:** The receipt must contain hashes, classes, locations, timestamps, and retention outcomes—not raw audio, page contents, or secrets. Erasure must be authenticated and idempotent, and an offline node must not be declared deleted until it acknowledges.
- **missing:** A common per-turn data-lineage ID propagated through audio, relay, Mac, and browser records; Read-only joins across pipeline, job, browser, and pendant receipts; Deletion endpoints and acknowledgements for each transient store; The owner’s retention/deletion policy, which remains explicitly undecided


## Changes it proposed to its own stack

### `relay` — Implement a durable cross-surface command envelope: every browser/Mac action carries job ID, plan digest, target binding, expiry, and an execution lease; the relay requeues expired work, rejects stale browser results, and exposes one receipt that distinguishes not-dispatched, dispatched, completed, and unknown.
- **owner gets:** When the Mac sleeps or a tab disappears, the owner will know whether something happened and can safely continue without guessing or accidentally submitting twice.
- effort: Medium-high: relay schema/migrations, lease sweeper, browser result binding, and integration tests across reboot and link loss.  ·  risk: A bad lease could duplicate an unrepeatable action. Default expiry to blocked/needs-review for unknown or unrepeatable steps; only idempotent/additive steps may auto-retry. Recover with explicit owner review and the existing undo paths where available.
- cost: Negligible storage and worker CPU; no meaningful model cost.  ·  latency: Adds under 100 ms to normal dispatch; recovery waits for lease expiry or explicit sweep.
- security: Improves replay resistance and provenance, but requires careful protection of plan digests and target bindings; never place secrets in the envelope.
- depends on: orchestrator must close ordinary ledgers; relay_jobs needs lease_until and a requeue sweep; browser bridge supervisor must actually run its orphan sweep; approvalHandoff relay persistence and delivery must be implemented


## What it asked for

_Nothing._
