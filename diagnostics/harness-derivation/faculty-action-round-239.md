# Harness derivation — faculty-action — round 239

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do this multi-step task, but stop safely if any step differs from what you expected.”"
- **useful because:** The owner gets reliable execution rather than a misleading 'done': each Mac/browser mutation is independently checked before the next begins, and an unexpected state leaves the remaining work staged instead of compounding an error.
- **path:** faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime → pendant
- **model tier:** Background model plans and summarizes; realtime model only handles the owner's short spoken interaction.
- **latency:** First plan 2–5 s; each step 1–3 s including verification; stop immediately on mismatch.
- **cost:** Usually 1 planning call plus cheap verifier calls; roughly $0.02–$0.10 depending on step count, dominated by vision/browser evidence.
- **security:** Never send secrets or page contents to the pendant. Mutations remain staged until the existing physical approval latch is satisfied. A mismatch, timeout, or unknown result is a stop—not an automatic retry.
- **missing:** A durable operation coordinator that joins step IDs, executor receipts, independent verification receipts, and the approval nonce; policy data for which action classes may run without approval.

### "“If something I asked you to do may have happened but you cannot prove it, tell me exactly what is known and make sure it cannot happen twice.”"
- **useful because:** This is the single most useful trust behavior: a network drop or crashed bridge no longer turns an uncertain send, purchase, edit, or deletion into a duplicated side effect. The owner gets a concise spoken/haptic status and a safe recovery path.
- **path:** faculty-action → faculty-perception → faculty-judgement → relay-realtime → mac-planner → mac-vision → browser-extension → pendant
- **model tier:** Cheap background reconciliation checks state; realtime is used only to explain the outcome or ask for a new approval.
- **latency:** Initial uncertainty notice under 2 s; reconciliation within 10 s when surfaces are online; no action is retried automatically.
- **cost:** One receipt lookup plus one read-only verifier per uncertain step, typically under $0.03; vision evidence dominates.
- **security:** Use idempotency keys and operation leases; never infer success from executor receipts alone. The verifier receives only the specific postcondition and returns hash/minimal evidence. An unknown state stays unknown and expires rather than being guessed.
- **missing:** A first-class idempotency/lease record shared by relay, Mac executor, browser command, and verifier; a user-visible distinction among verified, not-done, and unknown outcomes.

### "“Only let this system approve actions from my pendant if the pendant itself can prove it is genuine; if the Mac or relay is compromised, fail closed.”"
- **useful because:** Today a signed approval can establish that a protocol message was formed, but not that a genuine physical pendant—not a copied software client—authorized it. Device-bound attestation would make the pendant a real security boundary for messages, purchases, account changes, and other high-consequence actions.
- **path:** pendant → relay-realtime → faculty-judgement → faculty-action → mac-planner → browser-extension
- **model tier:** Background model handles policy and verification; realtime only explains a refusal or asks the owner to reconnect.
- **latency:** 100–300 ms local signature/verification; under 2 s end-to-end when the relay is reachable.
- **cost:** Negligible per action after provisioning; hardware addition roughly $2–$8 for a secure element, plus firmware and relay integration.
- **security:** Private keys never leave the secure element. Attestation must bind firmware version, device identity, approval nonce, operation digest, and monotonic counter; revocation and recovery must exist before deployment. A failed attestation is a refusal, never a fallback to a software key.
- **missing:** Secure element on the pendant; Provisioning, attestation, revocation, and recovery protocol; Relay-side enforcement that high-risk operations require device attestation

### "“Show me what this risky browser or Mac task would change without actually contacting the outside world, then let me approve the exact diff.”"
- **useful because:** The owner could inspect a realistic result before an email, purchase, deletion, settings change, or form submission. A normal plan describes intent; a quarantined rehearsal exposes the actual files, fields, navigation, and side effects that would differ.
- **path:** faculty-judgement → faculty-action → mac-vision → browser-extension → mac-terminal → pendant
- **model tier:** Background model builds the rehearsal and summarizes the diff; realtime speaks only the short result and approval prompt.
- **latency:** 5–20 s for a bounded rehearsal; no external side effect until explicit approval.
- **cost:** $0.05–$0.50 per rehearsal, dominated by disposable VM/browser startup and vision snapshots.
- **security:** Run in a disposable snapshot with network denied by default and synthetic credentials/data. Clearly mark effects that cannot be simulated. Approval must bind to a hash of the rehearsal diff and expire if the live page or files change.
- **missing:** Disposable Mac/browser execution sandbox with filesystem snapshot and network policy; Diff extraction for GUI, browser, and file effects; Approval envelope bound to the rehearsal hash


## Changes it proposed to its own stack

### `firmware` — Add a compact event journal on the pendant for physical interaction context: button edge/hold, haptic outcome ID, link state, and the last 3 seconds of IMU motion summary (not raw sensor data). Sign and upload the journal only when an action outcome or failure needs diagnosis; expose a redacted incident ID to the owner by haptic pattern. Enable i2c2 for the already-owned LSM6DSOX and DRV2605L, with bounded RAM and crash-safe SD records.
- **owner gets:** When an action is unexpectedly triggered, missed, or reported unknown, the system can explain whether the owner pressed, acknowledged, was moving, or lost the link—without recording a continuous surveillance stream or requiring the owner to reproduce the problem.
- effort: Medium firmware integration: enable i2c2, add sensor sampling and compact CBOR journal, connect to the existing typed OUTBOX and tactile outcome beacon, then validate RAM and SD wear.  ·  risk: Sensor or I2C failure must never block recording or approval; fall back to button/link-only evidence. Store summaries, not raw motion or audio, and expire entries after successful upload. No action may be authorized from motion classification alone.
- cost: No new hardware; roughly 1–3 mA while sampling and a few KB of flash/SD per incident, with negligible API cost for occasional diagnostics.  ·  latency: <10 ms sampling path; no impact on the 24 kHz audio task if sampling is timer/batched at 25–50 Hz.
- security: Improves auditability while minimizing sensitive data. Journal records must be signed, monotonic, and exclude page contents, form secrets, and raw microphone data.
- depends on: Existing typed OUTBOX manifest in pendant_store; tactile_action_outcome_beacon; physical_transaction_approval_latch; motion_context_safety_gate request already queued

### `interaction` — Add a signed, time-bounded owner policy capsule that the pendant can hold and enforce locally: allowed action classes, maximum risk level, quiet hours, and a daily spend/destructive-operation budget. The relay and Mac must reject operations outside the capsule, while the pendant gives a distinct refusal pattern and can revoke the capsule with a deliberate physical gesture. Sync only hashes and counters, not private task content.
- **owner gets:** The owner can say “for the next hour, reminders and drafts are fine, but never send, buy, delete, or change accounts,” and trust that rule even if the relay is delayed or the Mac reconnects later. This is a tangible safety control, not merely a preference the planner may forget.
- effort: High: define policy grammar and signatures, store a compact capsule in pendant flash, enforce it consistently in relay/Mac/browser, handle clock uncertainty and replay, and provide recovery when the capsule expires.  ·  risk: A stale or malformed capsule must fail closed for high-risk actions but never prevent emergency cancellation. Counters must be monotonic and policies must be auditable; no hidden broadening of permissions during reconnect.
- cost: No recurring model cost; approximately 1–2 KB durable storage and minimal flash/RAM. Hardware secure element would strengthen this but is not strictly required for a first prototype.  ·  latency: Local policy check under 10 ms; one extra signature verification at action staging.
- security: Moves critical authorization from model judgment into a bounded, owner-controlled capability token. Policy contents should be minimized and encrypted at rest; revoked capsules must be rejected across all surfaces.
- depends on: Existing actionRisk.js and policyRouter.js; physical_transaction_approval_latch; A durable operation/idempotency record; A defined owner policy schema and recovery flow


## What it asked for

_Nothing._
## Its own summary

Round 239 produced three recorded items: (1) fail-stop multi-step execution with independent verification between steps, (2) idempotent handling of unknown outcomes so uncertain side effects are never blindly retried, and (3) a firmware incident journal using the owned IMU/haptic hardware, recording only compact signed interaction/motion summaries. I also confirmed the live inventory still exposes execution, job, browser, observation, and journal routes, but no observed /approve route.

**Biggest unknown:** I still need a durable cross-surface operation coordinator: one record joining approval nonce, idempotency lease, executor receipt, verifier receipt, expiry, and final status. Without it, the system can execute and inspect pieces but cannot truthfully prove that a multi-step action stopped, resumed, or did not duplicate after a crash or link drop. Physically, end-to-end pendant validation still awaits LTE registration and firmware integration of i2c2; USB remains bench-only.

