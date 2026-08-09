# Harness derivation — faculty-action — round 244

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep my spoken conversation intelligible when the cellular link or audio bridge is struggling: detect degradation, switch to a measured safe audio profile, and tell me when quality is restored."
- **useful because:** The owner gets continuity instead of silent dropouts or a falsely confident 'working' state. The relay can react to packet loss and bridge telemetry while the pendant remains the immediate audible endpoint; no single node can observe and correct the whole path.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background for telemetry classification and profile selection; realtime only for the live conversation itself
- **latency:** Detect within 2 seconds; profile change at the next Opus boundary (under 1 second); restoration notice within 3 seconds of stable measurements.
- **cost:** Usually <$0.001 per transition; dominant cost is telemetry/storage, not model inference. Use deterministic thresholds first and invoke a cheap model only to summarize repeated failures.
- **security:** Send only counters (loss, starvation, decode time, profile ID), never microphone content. A profile change must be bounded to approved codec/frame/bitrate combinations and logged; do not silently lower quality during a sensitive call without an audible status cue.
- **missing:** Pendant/bridge runtime telemetry envelope for decode time, tx_starved, mic_drops and packet loss; Relay policy that can request a bounded profile change and receive an acknowledgement; A small owner-visible quality state in the dashboard or spoken status path

### "After you change something on my Mac or in my browser, show me a concise, trustworthy before/after account of what actually changed, and offer undo only when the recorded postcondition and receipt support it."
- **useful because:** The owner can distinguish 'the assistant said it did it' from an independently observed change, without exposing full page contents or requiring them to inspect logs. It turns action into an accountable hand rather than an opaque command runner.
- **path:** mac-bridge → browser → relay → pendant → dashboard
- **model tier:** Deterministic receipt/postcondition assembly first; a cheaper background model may summarize the already-redacted diff. Realtime is used only if the owner asks during a live action.
- **latency:** Verified result within 2 seconds after each step; spoken summary under 5 seconds; dashboard can update asynchronously.
- **cost:** <$0.002 per action in the normal case; verification and hashes are local/route calls, with model cost only for optional natural-language summarization.
- **security:** Default to hashes, field names, counts and redacted snippets; sensitive/secret locators must never be echoed. Undo must be gated by the original receipt's reversibility and a fresh verification, and the pendant's physical approval remains required for risky undo.
- **missing:** A stable actionId/attemptId correlation carried from executor receipt into verify_operation_step; A redacted before/after diff formatter for app_state, file_state and browser_field evidence; An owner-facing delivery path that can render the digest as a short haptic/audio status without leaking secrets

### "Do not play private answers aloud when I have taken the pendant off or left it on a table; detect that state locally, keep the answer queued, and give me a discreet warning when it is safe to resume."
- **useful because:** This prevents the most embarrassing and dangerous failure of a wearable assistant: private content broadcast into a room after the owner removed it. The pendant's IMU can detect wear/removal immediately, while the relay knows whether the pending response is private and the bridge controls playback; no one node can make that decision safely alone.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic firmware classifier for motion/contact transition; background model only for tuning per-owner motion patterns. Realtime model must not decide privacy state.
- **latency:** Mute or pause within 250 ms of a removal transition; resume only after 2 seconds of stable worn evidence and a short haptic cue.
- **cost:** Near-zero inference cost after firmware integration; one-time tuning telemetry is small. Storage is a few bytes of state and counters.
- **security:** Fail closed: uncertain means do not play private audio. Do not upload raw motion traces by default; send only state transitions and confidence. Emergency/non-private alerts need a separately configured policy and must not bypass the physical approval boundary.
- **missing:** Enable i2c2 and integrate the owned LSM6DSOX into nRF9160 firmware; A calibrated worn/removed classifier and a local mute gate before audio reaches the bridge; Relay metadata marking responses private, non-private, or emergency; A resumable pending-audio state that preserves ordering and does not replay a response twice

### "Let me grant the assistant temporary, narrowly scoped access to one browser tab or Mac task—such as “use this checkout page but never read or repeat my payment details”—and automatically revoke that access when the task ends."
- **useful because:** Today the system has approval and verification, but not a user-visible capability boundary for what the acting agents may inspect. This would let the owner delegate useful work without granting the model blanket access to every logged-in session or secret field.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic policy enforcement and redaction; use the realtime model only to interpret the owner’s spoken scope. Never ask a model to enforce its own scope.
- **latency:** Scope confirmation within 2 seconds; enforcement on every browser/Mac operation with no perceptible added delay; revoke immediately on completion, timeout, or cancellation.
- **cost:** <$0.001 per task beyond ordinary execution; cost is policy evaluation and audit storage, not inference.
- **security:** The capability token must be opaque, audience-bound, least-privilege, short-lived, non-forwardable, and deny-by-default. Secrets and disallowed fields must be blocked before model context construction, not merely redacted in the final answer. Physical approval remains required for irreversible actions.
- **missing:** A capability-token policy evaluator shared by browser and Mac action layers; Field- and locator-level deny rules that execute before snapshots are sent to a model; A pendant-readable scope summary and revocation gesture; Audit records proving which scopes were granted and actually used

### "Tell me, before I leave, whether I have created an unresolved real-world commitment today—an unanswered message, missed promised follow-up, unpaid item, or appointment risk—and let me resolve it from the pendant with one deliberate, auditable action."
- **useful because:** The current system can act on individual apps, but it cannot reliably join a spoken promise, calendar/mail/message evidence, and an owner-confirmed follow-up into one commitment ledger. This is the highest-value daily capability: preventing the things the owner forgets after the conversation ends.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model extracts candidate commitments from already-authorized notes/messages/calendar and ranks them; realtime is used only when the owner asks. Deterministic policy and physical confirmation control any outgoing action.
- **latency:** Generate a morning/leave-home digest in under 30 seconds; pendant query response under 5 seconds; mutations require explicit confirmation and may take longer.
- **cost:** <$0.01 per digest with incremental processing; the dominant cost is reading and indexing authorized sources, not every-turn realtime inference.
- **security:** Private messages and calendar content remain on the Mac where possible; relay receives commitments, deadlines, confidence, and redacted evidence rather than full text. Never infer a commitment as fact without showing provenance and an uncertainty label. Sending or scheduling anything requires the existing physical approval boundary.
- **missing:** A durable commitment object with source provenance, deadline, confidence, status, and owner disposition; Connectors that can correlate Mail, Messages, Calendar, browser transactions, and voice captures without copying full content to the relay; Conflict/uncertainty handling when sources disagree; A compact pendant interaction for accept, snooze, dismiss, or mark-done


## Changes it proposed to its own stack

### `integration` — Add a lock/wake trust source to the Mac agent and make deferred cross-surface execution require a fresh unlocked observation. Implement a read-only macOS session-state probe (for example CGSession/IOKit-backed, with unknown rather than guessed values), expose it through GET /observe with observedAt and source age, and have the job executor pause/cancel leases when the Mac locks or the observation expires. On unlock, resume only reversible or explicitly re-approved work; never auto-resume an irreversible step.
- **owner gets:** Actions will not type into, send from, or purchase through a locked session, and a laptop that slept will not be mistaken for a live human-controlled desktop. The owner gets honest 'paused while Mac locked' status instead of an action that appears successful but never reached the UI.
- effort: Medium: native session-state reader, observe schema, executor gate, tests for lock/unlock/race and stale observations.  ·  risk: The state can be unknown during fast sleep/wake or remote sessions; fail closed and surface that uncertainty. A crash between pause and resume may leave a lease stranded, recovered by expiry and explicit retry.
- cost: No meaningful API cost; small local implementation and negligible CPU.  ·  latency: Adds one local freshness check (tens of milliseconds) before a deferred action; no impact on already-running safe reads.
- security: Improves safety by preventing execution against an unattended session; exposes only locked/unlocked/unknown and timestamp, not user identity.
- depends on: GET /observe; GET /ops/snapshot; Existing job lease/approval and action-risk policy modules

### `context` — Introduce a cryptographically signed, per-task context contract spanning relay, Mac, and browser. The contract should enumerate allowed sources, prohibited fields, retention deadline, and whether evidence may leave the Mac. Enforce it at context assembly and at action dispatch, and make every receipt include the contract digest so an action cannot silently widen its own context.
- **owner gets:** The owner can ask for help with a sensitive task without relying on an agent’s promise that it will “be careful.” A task that was allowed to inspect one document cannot quietly expand into the rest of a logged-in browser or remain in memory indefinitely.
- effort: High: shared contract schema, signing/key handling, enforcement hooks in context projection, browser snapshots, Mac actions, relay jobs, and receipt verification; add adversarial tests for scope widening and stale contracts.  ·  risk: Overly narrow contracts can make legitimate tasks fail; fail closed with a clear request for expanded scope rather than guessing. Key rotation and offline relay operation require explicit expiry and recovery semantics.
- cost: Small signing and hashing overhead; modest storage for contract digests. No significant model API increase.  ·  latency: Milliseconds per context/action boundary, plus occasional owner confirmation when scope must expand.
- security: Substantially reduces secret exposure and post-task retention. The contract itself must avoid embedding secrets and must be invalidated on cancellation, timeout, or physical revocation.
- depends on: Existing action-risk and approval modules; Existing context projection and browser/Mac action dispatch; A durable audit/receipt path such as GET /jobs/:jobId/receipts


## What it asked for

_Nothing._
