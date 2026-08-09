# Harness derivation — unified — round 251

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I pull the privacy latch, make the entire hive go dark—not just the pendant—and tell me exactly when capture, playback, queued work, and browser exposure are stopped.”"
- **useful because:** A local mute is not enough if the relay still accepts audio, the Mac keeps a capture job, or a browser command remains queued. This gives the owner one physically initiated privacy boundary with a verifiable cross-surface receipt, including stale-command rejection and recovery only after an explicit unlatch.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic state propagation and convergence checks; no model call is needed except optional owner-facing wording.
- **latency:** Pendant mute immediately; relay/Mac/browser quarantine target under 1 s, with a bounded 5 s convergence deadline and a loud failure receipt if any surface is unreachable.
- **cost:** Near-zero API cost; one signed state event and a few reads. Operational cost is bounded cancellation/expiry work.
- **security:** Use a monotonic latch epoch and device-authenticated enter/exit events. Reject commands created before the current epoch; do not delete audit history. Never claim converged if a surface is offline. Unlatching must require the local confirmation pattern and must not replay quarantined audio or browser commands.
- **missing:** Relay-side privacy epoch enforcement on ingest, playback, and queued jobs; Mac/browser supervisors that cancel or quarantine capture and pending commands; A single authenticated convergence receipt joining all surfaces; A recovery policy for work interrupted by the latch

### "“After a crash or link drop, tell me which parts of the thing I asked for actually happened, resume only safe-to-repeat parts, and ask me before anything that could happen twice.”"
- **useful because:** The code already records durable step state and can classify replay safety, but no production trigger closes ledgers or resumes them. Wiring this into a user-visible recovery report prevents duplicate messages, half-finished browser work, and the dangerous fiction that a queued job is either wholly done or wholly undone.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic ledger/replay decisions; background model only summarizes a recovery plan in plain language.
- **latency:** Recovery diagnosis under 2 s after reconnect; safe idempotent steps may resume automatically, while unrepeatable/unknown steps wait for the next conversation and physical approval where required.
- **cost:** <$0.005 per recovery; mostly local/relay reads, with optional cheap summarization.
- **security:** Gate automatic replay on replaySafety (idempotent/additive), not reversibility. Bind resume to plan digest, world fingerprint, job lease, and expiry. Never auto-repeat unrepeatable/unknown actions. Preserve receipts and expose every skipped/blocked step.
- **missing:** Production closeLedger calls for ordinary plans; A relay job lease_until and requeue sweep; A startup/reconnect trigger that invokes planResume; A user-facing recovery route and pendant delivery on the next conversation; A relay implementation of action handoff state

### "“Before you act on a website, say which account, organization, and exact tab you will use; refuse if you cannot prove the identity, and show me the proof afterward.”"
- **useful because:** A logged-in browser session can silently be the wrong account or tenant. Existing browser actions can click and type but do not give the owner a cryptographic, least-privilege identity/target attestation. This prevents sending, purchasing, editing, or publishing in the wrong place even when the page looks familiar.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic browser/session attestation and policy checks; use the planner model only to interpret the requested target, never to infer identity from page appearance.
- **latency:** Preflight under 1 s for an already-attested tab; block and explain within 2 s when identity evidence is missing. Post-action receipt under 2 s.
- **cost:** <$0.005 per action; dominated by browser snapshot/receipt storage, not model inference.
- **security:** Never treat visible profile names or page text alone as proof. Bind an attestation to tab/session ID, origin, account identifier exposed by the site, and a short expiry; redact tokens and private page content. Require physical_transaction_approval_latch for irreversible or off-machine actions. If identity changes mid-plan, invalidate the plan rather than continuing.
- **missing:** A browser_identity_attestation capability with origin/account/tenant evidence and expiry; Browser bridge hooks that bind attestations to command IDs and reject stale or changed tabs; A policy mapping requested target to allowed account/organization; A receipt joining preflight identity evidence to the resulting browser command

### "“Let me set a standing boundary such as ‘you may read my work calendar but never send mail as me, and never use the family account’; enforce it on every surface and show me when it blocked you.”"
- **useful because:** Today authority is effectively one bearer token plus scattered action-risk checks. The owner cannot express durable, human-readable boundaries that apply consistently to the pendant, relay, Mac, and browser. A policy firewall would make the system useful without requiring a fresh confirmation for every harmless read, while making prohibited authority impossible rather than merely discouraged.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic policy evaluation and command interception; a cheaper background model may translate an owner's spoken boundary into a proposed rule, but activation requires explicit confirmation and the final rule is machine-readable.
- **latency:** Evaluate each action before dispatch in under 20 ms locally; policy creation under 5 s including a spoken read-back. A blocked action should be explained on the next natural conversational turn.
- **cost:** <$0.01 per policy change and effectively zero per action; storage and evaluation are local lookups.
- **security:** Default deny for ambiguous scopes. Policies must identify surface, origin/app, account/tenant, action class, data class, and expiry; no model-generated rule may activate silently. A stronger prohibition must override an approval latch, and policy changes themselves require physical confirmation. Keep blocked-attempt audit receipts without retaining page contents or message bodies.
- **missing:** A durable, versioned authority-policy store replicated to relay and Mac; A single pre-dispatch policy hook for Mac actions, browser commands, relay jobs, and pendant-triggered requests; A typed policy language for account, origin, data, and action scopes with deny-overrides-allow semantics; A dashboard and pendant read-back showing the exact rule, version, and blocked reason; A safe spoken rule compiler with ambiguity detection and physical activation confirmation


## What it asked for

_Nothing._
## Its own summary

Recorded three distinct capabilities this round: (1) a cross-surface privacy epoch that makes the physical latch quarantine relay/Mac/browser work and proves convergence, (2) crash/link-drop recovery driven by replaySafety with leases and explicit user-visible blocked steps, and (3) browser account/tenant identity attestation bound to command receipts so actions cannot hit the wrong logged-in account. The extracted-fact daily review was correctly rejected as an existing duplicate; I did not count it.

**Biggest unknown:** Two previously requested items remain unanswered: browser_identity_attestation and the owner's mandatory-confirmation policy for external actions. Implementation also still needs relay privacy-epoch enforcement, browser/Mac quarantine hooks, production ledger closure/resume triggering plus relay job leases, and a typed browser identity evidence contract. The owner must decide which accounts/organizations may be used for a given request; the system should not infer that policy.

