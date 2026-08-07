# Harness derivation — faculty-action — round 58

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **action-execution readiness** — Mac local agent is reachable and full-control planner is configured, but not ready: browser bridge offline with 5 pending commands; Accessibility trusted=false and Screen Recording granted=false. Relay is reachable and reports mac bridge online.
  - evidence: GET /ops/status and GET /browser/status at 2026-08-07T11:55Z

## Capabilities it proposed

### "“Queue this for when my Mac and browser are back, and ask me on the pendant right before anything irreversible happens.”"
- **useful because:** Today judgement can decide an action, but execution fails or becomes unsafe when the browser bridge is offline, the Mac sleeps, or the page changes. This creates a durable cross-surface escrow: relay preserves the approved plan, Mac/browser revalidate it when reachable, and the pendant presents a short nonce-bound summary for physical approval immediately before send/delete/purchase. The owner can leave a task unattended without losing it or accidentally authorizing stale work.
- **path:** faculty-judgement creates a typed action plan with expiry, required evidence, and irreversible boundary → relay stores the encrypted pending action and wakes/retries it when the Mac bridge reconnects → mac-planner/mac-terminal performs read-only preflight and computes a before/after diff → browser-extension executes only reversible preparation, then reports current tab/session provenance → pendant displays/announces destination, exact effect, and expiry; one deliberate button gesture authorizes the nonce → faculty-action commits the final step and returns a signed receipt/undo handle to the pendant and Mac dashboard
- **model tier:** Use the realtime model only for the short pendant approval conversation; use a cheaper background model for retry scheduling, preflight diff normalization, and receipt summarization.
- **latency:** Immediate queue acknowledgement under 1 s; reconnect polling within 10 s; preflight under 30 s; physical approval prompt under 2 s after preflight. Expire/replan if evidence or page provenance changes.
- **cost:** ~$0.01–$0.05 per queued task, dominated by one background reasoning pass and optional realtime approval turn; retries and relay storage are negligible.
- **security:** Never persist raw secrets or form contents beyond encrypted, short-lived capsules. Bind approval to plan hash, destination, tab/session, evidence hash, and expiry; fail closed on any mismatch, duplicate delivery, or browser reconnect after stale commands. Require explicit confirmation for send/delete/buy, while reminders/notes remain policy-allowed. Show exactly what leaves the device before approval.
- **missing:** Durable relay-side action escrow schema and wake/retry worker; typed preflight/revalidation endpoint with plan-hash and evidence binding; pendant-local physical approval UX and nonce display; signed cross-surface receipts and cancellation/expiry propagation; browser reconnect handshake that quarantines stale queued commands

### "“Make sure I actually get this done before the deadline—only interrupt me when it matters, and keep trying until it’s finished or I explicitly release it.”"
- **useful because:** The owner can create a reminder today, but a reminder is not an outcome: it cannot tell whether the work was completed, whether the relevant browser/Mac state changed, or whether a missed alert should be escalated. This would create a closed-loop commitment that observes permitted completion evidence across the Mac and logged-in browser, adapts interruption timing to the owner's meeting/quiet state, and keeps a concise spoken status on the pendant until the owner acknowledges completion or cancels it.
- **path:** faculty-judgement defines the commitment, acceptable completion evidence, deadline, quiet hours, escalation ceiling, and cancellation policy → relay persists the commitment and runs the low-cost schedule/evidence checks while the Mac sleeps → mac-planner/mac-terminal checks local artifacts, calendar state, and application evidence without sending or deleting anything → browser-extension checks only the named authenticated page/session and returns provenance-bound evidence → pendant gives a brief vibration/audio prompt, accepts completion/defer/cancel, and escalates only according to the stored policy → faculty-action updates reminders or drafts reversible follow-up work and emits a final evidence-backed completion receipt
- **model tier:** Use a cheap background model for schedule decisions, evidence comparison, and concise status generation; reserve realtime only for the owner's live response on the pendant.
- **latency:** Status checks every 5–15 minutes near the deadline, with exponential backoff otherwise; prompt acknowledgement in under 2 seconds; completion receipt within 10 seconds of observed evidence.
- **cost:** Approximately $0.01–$0.08 per commitment per day, dominated by background evidence normalization; most polling and scheduling can be deterministic.
- **security:** The owner must choose the evidence sources and escalation audience. Never infer completion from sensitive content without an allowlisted selector or local artifact hash. Do not send messages or alter records automatically. Store hashes, timestamps, and provenance rather than page text; require confirmation for any follow-up external action. Provide a pendant emergency mute and immediate cancellation.
- **missing:** Durable commitment state machine with deadline, quiet hours, escalation budget, and explicit terminal states; Evidence adapters that compare local files/calendar and authenticated browser regions without retaining secrets; Pendant acknowledgement/defer/mute events delivered to relay when the Mac is asleep; Cross-surface notification policy and deduplicated escalation delivery; A completion verifier that requires two independent signals or explicit owner acknowledgement for ambiguous tasks


## Changes it proposed to its own stack

### `integration` — Add a cross-surface execution lease. When faculty-judgement creates an action with an irreversible boundary, relay issues a short-lived lease containing plan hash, destination, evidence hash, and required pendant presence. Mac/browser may prepare and pause, but cannot cross the boundary unless the pendant has recently attested the lease nonce; disappearance, expiry, browser-session change, or plan mutation revokes it. Relay deduplicates lease consumption and fans cancellation to the Mac job and browser command queue. Receipts record lease issuance, attestation, consumption, and revocation separately.
- **owner gets:** A task can be prepared while the owner is away, yet a sleeping/reconnected Mac or stale browser tab cannot send, delete, or buy just because an old approval exists. The owner gets a dependable physical stop/start control from the thing they are wearing, without opening the Mac or exposing credentials.
- effort: Medium-high: relay D1 schema and atomic consume, Mac job gate, browser queue gate, pendant attestation protocol/UI, and failure-injection tests for reconnects and duplicate delivery.  ·  risk: A lost pendant or dropped radio could strand a task; recover by explicit cancel/replan from Mac or voice. Clock skew and reconnect races require server-issued monotonic expiry and idempotency. Never treat mere BLE proximity as authorization; use a button gesture plus nonce and show the exact effect.
- cost: Low recurring API cost (<$0.01/task for storage/events); engineering cost is protocol and test work. No new pendant hardware required, though secure element support would strengthen attestation.  ·  latency: Adds ~100–300 ms for attestation on a live link and up to 2 s for a spoken/button prompt; no impact on read-only preparation.
- security: Improves safety by binding authorization to wearer-held hardware, but introduces a new credential. Store only rotating device keys/lease hashes; rotate and revoke keys, rate-limit attempts, and fail closed on any mismatch.
- depends on: durable relay action escrow (the queued cross-surface task primitive); physical_action_confirmation pendant skill; browser stale-command quarantine and reconnect handshake; signed action receipts with plan/evidence provenance


## What it asked for

_Nothing._
## Its own summary

Discovered and recorded the live execution gap: Mac agent is configured but not ready because browser bridge is offline (5 queued commands), Accessibility and Screen Recording are still unavailable. Proposed two connected action improvements: durable cross-surface action escrow for work that survives disconnected devices, and a nonce-bound execution lease requiring a fresh pendant button attestation immediately before irreversible actions. Informed faculty-judgement and mac-planner, and recorded the readiness finding.

**Biggest unknown:** Whether the orchestrator will implement the pending pendant physical-confirmation skill and relay escrow primitives; until then, irreversible browser work must remain blocked and stale queued commands must not be replayed.

