# Harness derivation — unified — round 229

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Continue the task that was interrupted, but don’t repeat anything or send anything without asking me.”"
- **useful because:** This is the single most useful missing behavior: after a Mac, browser, or relay outage, the owner gets a truthful continuation instead of a duplicate action or a dead job. The system can inspect the durable ledger, workbench handoff, browser lease, and relay job state, automatically skip only idempotent/additive steps, and hold unrepeatable or unknown steps for the next conversation and physical approval.
- **path:** relay → pendant → mac-bridge → browser
- **model tier:** background for ledger classification and handoff planning; realtime only to explain the result and ask for a deliberate approval
- **latency:** Under 2 seconds for a status answer; continuation runs asynchronously and reports each skipped, rerun, blocked, and awaiting-approval step
- **cost:** ~$0.01–$0.05 per continuation depending on planner use; deterministic ledger checks dominate and should avoid model calls
- **security:** Never infer completion from an open ledger alone. Require orchestrator closeLedger correctness, replaySafety (idempotent/additive auto-resume; unrepeatable/unknown blocked), a live relay job lease, bound plan/world digests, and the physical transaction approval latch for irreversible/off-machine steps. Do not expose withheld secrets in the spoken summary.
- **missing:** orchestrator must close ordinary ledgers; relay_jobs lease_until and requeue sweep; startup/job-trigger caller for planResume and resumeLedger; relay persistence and delivery path for pending physical approvals; a distinct authorization boundary so approval is not identical to execution

### "“Before you do anything outside this Mac, tell me exactly what will change; after it runs, prove the external system changed once, and stop if the proof is ambiguous.”"
- **useful because:** A browser click or API submission can succeed while its receipt is lost, and retrying can duplicate a purchase, message, or booking. This capability turns every off-machine action into a staged, nonce-bound transaction: the owner sees the intended side effect, physically approves it when required, and the browser/Mac agent verifies the postcondition before declaring success or offering a retry.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** background for extracting the intended side effect and selecting a verifier; deterministic policy, nonce, receipts, and postcondition checks must not depend on the model
- **latency:** Preview under 1 second; physical approval waits indefinitely until the next conversation; postcondition proof within 5 seconds of submission
- **cost:** ~$0.01–$0.04 per action for intent normalization and verifier selection; browser snapshots and receipts dominate latency, not token cost
- **security:** Bind preview, approval, action, and verification to one plan digest and nonce. Never retry an ambiguous unrepeatable action. Verify against the specific browser tab/session and expected state, redact page secrets, and keep an immutable action audit record while allowing separate fact deletion. Require physical approval for off-machine, irreversible, or uncontained effects.
- **missing:** a generic postcondition verifier that accepts per-action evidence predicates; browser result receipts containing before/after state and idempotency key; relay implementation of the approval handoff contract and delivery on the next conversation; authorization separation between approval and execution; a policy for ambiguous external state that leaves the owner with a recovery choice instead of auto-retrying

### "“I’m leaving now—put every surface into away mode, and tell me exactly what you could not lock down.”"
- **useful because:** The owner should have one reliable departure action rather than remembering separate browser, Mac, relay, and pendant states. It can stop or defer capture, pause queued external actions, close only explicitly bound browser sessions, enable a Mac focus/lock policy, and leave a bounded audit of anything that remained reachable.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** deterministic policy engine for the state transition; background model only to summarize exceptions in plain language
- **latency:** Local pendant privacy state within one frame; Mac/browser convergence within 5 seconds; spoken exception report within 2 seconds after convergence
- **cost:** ~$0.00–$0.02 per invocation; mostly deterministic state reads and browser/Mac actions
- **security:** Default to fail-closed for capture and pending approvals, but never claim browser logout or Mac lock without receipts. Limit browser operations to explicitly bound sessions; do not close unrelated tabs. Require a deliberate physical confirmation for destructive cleanup, and preserve an audit trail of what was stopped versus merely requested.
- **missing:** a named away-mode policy and durable state machine spanning pendant, relay, Mac, and browser; safe Mac lock/focus action with a verifiable receipt that works without Accessibility; browser session shutdown and reauthentication semantics; relay queue transition that pauses new off-machine work and safely handles already-processing jobs; a convergence receipt combining pendant privacy_convergence_check with browser/Mac/relay state

### "“For the next hour, handle routine web tasks for me, but never spend money, send a message, expose a secret, or act outside these three sites—and stop when the budget is used.”"
- **useful because:** Today the owner can approve individual actions, but cannot give the system a bounded, revocable delegation that spans browser, Mac, relay, and pendant. A capability budget would let him delegate low-risk work without granting an all-or-nothing bearer-token power: site scope, action classes, time limit, spend limit, data-egress limit, and a remaining-budget readback are enforced across every surface.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** deterministic policy enforcement and accounting; background model only compiles the owner's natural-language limits into a reviewed policy
- **latency:** Policy preview under 2 seconds; each action authorization under 100 ms; budget and exception summary available in the next spoken turn
- **cost:** ~$0.01–$0.03 to compile a policy, then negligible per action; durable counters and receipts dominate storage, not inference
- **security:** The policy must be deny-by-default, scope-bound to exact browser sessions/domains and Mac paths/apps, expire automatically, and survive relay/Mac restarts without widening permissions. Count attempted and completed effects separately; never treat a model classification as authority. Physical pendant confirmation should activate or revoke a delegation, and every denied action should produce a receipt without leaking the blocked secret.
- **missing:** a signed, durable delegation record replicated between relay and Mac; policy enforcement hooks before browser, Mac, and relay execution rather than only after planning; typed quotas for time, money, domains, data egress, and action classes; a pendant activation/revocation flow that works offline and a convergence receipt showing all surfaces observed the revocation; a separate authorization principal from the general AGENT_TOKEN

### "“If anything starts behaving unlike me, quarantine it across every surface and tell me what triggered the quarantine; do not restore access until I physically confirm.”"
- **useful because:** Today a suspicious browser session, relay job, or Mac agent can only be diagnosed piecemeal. A cross-surface behavioral quarantine would stop queued execution, revoke browser commands, mute the pendant, and preserve redacted evidence when action patterns, destinations, timing, or approval failures exceed the owner's baseline. It gives the owner a single containment switch before investigating.
- **path:** relay → pendant → mac-bridge → browser
- **model tier:** deterministic anomaly rules and containment first; background model may cluster evidence after quarantine, never decide release
- **latency:** Containment under 1 second for relay/browser queues and one audio frame for pendant mute; explanation within 5 seconds
- **cost:** ~$0.01 per incident for evidence clustering; continuous counters are low-cost and bounded
- **security:** Avoid profiling private content: inspect metadata such as destination, rate, action type, approval failures, and session identity, not message bodies. Quarantine must fail closed, be durable across restart/link loss, and require the physical transaction approval latch to clear. Preserve tamper-evident audit evidence while respecting the owner's separate fact-erasure policy.
- **missing:** cross-surface anomaly event schema and baseline policy; relay-wide kill/quarantine state honored by job claiming and browser polling; Mac executor preflight hook that refuses work while quarantined; pendant firmware quarantine indication and offline-held release decision; tamper-evident incident bundle with owner-readable evidence and a tested recovery path


## Changes it proposed to its own stack

### `browser-harness` — Add a transaction receipt envelope to every browser command: commandId, planDigest, tab binding, idempotency key, before-state fingerprint, submittedAt, after-state fingerprint, verifier result (proven|not_proven|ambiguous), and evidence refs. Refuse automatic retry when verifier is ambiguous or the action is unrepeatable.
- **owner gets:** The owner stops hearing “done” when only a click was issued. He gets a truthful answer that the site changed, did not change, or cannot yet be proven—and avoids duplicate messages, purchases, and bookings after a timeout.
- effort: Medium: extend browserBridge command/result schema, capture bounded redacted snapshots, implement 5–10 deterministic verifier predicates, and add tests for lost-result/reconnect races.  ·  risk: Snapshots may contain sensitive page content; redact by default and bind evidence to the tab/session. A false negative may ask the owner to inspect manually, which is safer than a duplicate side effect. Recover by retaining the command receipt and offering a non-mutating recheck.
- cost: Low ongoing storage; bounded receipt metadata and small redacted fingerprints. One extra browser snapshot per mutating command; no model call required for deterministic predicates.  ·  latency: Adds roughly 0.5–2 seconds for postcondition polling; no impact when the command is observation-only.
- security: Improves security by making plan digest, tab binding, and idempotency explicit; requires strict redaction and expiry of page evidence.
- depends on: relay approval handoff persistence and next-conversation delivery; browser result route extended with before/after evidence; a verifier vocabulary and action-type policy distinguishing idempotent, additive, and unrepeatable commands


## What it asked for

_Nothing._
## Its own summary

This round produced three new owner-facing capabilities and one concrete implementation change: (1) safe continuation of interrupted work keyed to replay safety rather than reversibility, (2) a cross-surface external-side-effect firewall that proves browser/Mac changes before declaring success, (3) a deliberate “I’m leaving” away mode that converges pendant, relay, Mac, and browser state, and (4) browser before/after transaction receipts with ambiguity-safe retry behavior. The most useful of these is safe continuation: it prevents the system from silently duplicating an action after an outage.

**Biggest unknown:** The remaining blockers are implementation gaps, not discovery: ordinary orchestrator ledgers must be closed; relay jobs need expiring leases and requeue; the approval handoff must actually persist and deliver to the next conversation; browser commands need bounded before/after verifiers and receipts; and away mode needs a verifiable Mac lock/focus primitive that does not rely on denied Accessibility. I do not need another permission request this round.

