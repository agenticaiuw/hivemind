# Harness derivation — faculty-action — round 258

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Handle this end to end, and keep going if a surface drops: capture my spoken request on the pendant, carry it through the Mac/browser/iPhone, and wake me only with a verified result or a clear request for one decision.”"
- **useful because:** This is the single most useful missing behavior: today the mind can decide a multi-surface task, but execution fragments across browser, Mac, and phone and a dropped link can leave the owner guessing. A durable operation graph would preserve intent, resume only idempotent steps, require the existing physical latch for consequential steps, and have faculty-perception independently verify every postcondition before claiming success. The owner gets one truthful outcome instead of a plausible narration.
- **path:** pendant → relay → mac-planner → browser → iOS → dashboard
- **model tier:** Use realtime only to acknowledge/capture the short request; use a cheaper background model for plan expansion, retries, and summarization. Use faculty-perception for read-only verification, never the planner's own assertion.
- **latency:** Acknowledge in under 500 ms; first progress beacon within 2 s; ordinary reversible steps within 10 s. Long browser/phone tasks may continue in background, with haptic progress and a final spoken result.
- **cost:** Roughly one realtime turn plus 2–6 inexpensive planner/verifier calls per operation; browser/Mac latency dominates, not tokens.
- **security:** The pendant receives opaque operation IDs and risk summaries, never page contents or secrets. Irreversible actions pause at the existing physical_transaction_approval_latch. Every completion requires verify_operation_step provenance; unknown state is surfaced as unknown, never success. Data leaves the device only as the captured request and bounded status events.
- **missing:** A durable cross-surface operation DAG with idempotency keys and resumable checkpoints; A standard executor-to-faculty-perception handoff carrying operation_id and step_id; A dashboard view of blocked, retrying, verified, and unknown steps

### "“When I take the pendant off or cover it, stop speaking private answers aloud; keep listening only if I explicitly resume, and give me a discreet haptic status instead.”"
- **useful because:** A wearable that can speak private mail, health, or account details aloud is unsafe in a room full of people. The already-owned LSM6DSOX and ESP32 audio bridge can provide a local privacy perimeter: infer worn/removed/covered transitions on-device, immediately duck or halt downlink audio without waiting for LTE, and let the Mac/relay downgrade output to a notification or encrypted pending item. This is a user-visible safety feature no Mac-only agent can guarantee during a link stall.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** No realtime model is needed for the immediate gate. A tiny on-device classifier handles motion/proximity heuristics; a cheap background model can learn per-owner thresholds from explicit corrections. Realtime resumes only after the owner deliberately asks.
- **latency:** Local audio mute/duck under 100 ms after the transition; relay policy update within 2 s when connected. False positives should be recoverable by one deliberate button gesture.
- **cost:** Near-zero inference cost after firmware integration; one occasional background calibration call. Hardware cost is $0 because the IMU, amplifier, and bridge are already owned.
- **security:** The IMU stream stays on-device; transmit only state transitions and confidence, not raw motion. Default conservatively to silence for private content when confidence is low. Never use motion alone to approve an external action. The pendant must retain a local mute latch across a dropped link and expose an unmistakable haptic/audio-safe cue.
- **missing:** Wire LSM6DSOX on i2c2 in firmware and calibrate worn/removed/covered states; A local downlink mute/duck control in the nRF9160-to-ESP32 bridge protocol; A content sensitivity label from planner/browser outputs so private audio is gated more strictly than public responses; Owner calibration and an explicit resume gesture

### "“If you just did something reversible, give me a short window to undo it from the pendant—without making me remember which app or ask you to reconstruct what happened.”"
- **useful because:** Approval protects before an action; it does not help when the owner notices a mistake immediately after a reversible action. A compact post-action undo affordance turns the pendant into a real safety hand: the relay sends only an opaque job ID and expiry, the pendant signals a reversible window, and one deliberate gesture asks the Mac to undo the exact last eligible job. The system then verifies the restored state and reports verified, failed, or unknown.
- **path:** pendant → relay → mac-planner → browser → iOS → dashboard
- **model tier:** No expensive reasoning is needed for the gesture. Use the existing action ledger and a cheap policy lookup to determine eligibility; use faculty-perception only for post-undo verification. Realtime is reserved for the owner's spoken explanation if verification is ambiguous.
- **latency:** Show the undo window within 300 ms of the action receipt; send the undo request immediately on gesture; target restored-state verification within 3 s.
- **cost:** Usually no additional model call; one verifier call only when the undo writes state. Mac/browser round trip dominates.
- **security:** Only explicitly reversible jobs with a still-valid undo token are eligible. The pendant sees no content or secrets. Expired, already-undone, cross-owner, or digest-mismatched tokens are rejected locally and server-side. For messages, purchases, deletions, or other irreversible actions, show no undo affordance and rely on the existing approval latch.
- **missing:** A bounded undo-token envelope delivered to the pendant with job ID, expiry, reversibility class, and digest; A relay endpoint that atomically consumes the token and calls the matching job undo, rather than generic undo-last; A post-undo verifier receipt joined to the original action ledger entry; A pendant haptic pattern distinguishing undo available, accepted, and unknown

### "“Treat this as local-only: understand it on my Mac, but do not send the recording, transcript, screen contents, or files through the relay or browser unless I explicitly unlock that boundary.”"
- **useful because:** The owner has no trustworthy way today to express a data-residency boundary across a wearable, relay, Mac, and logged-in browser. A single spoken policy should become an enforceable capability, not a promise in the model's reply: local processing may continue, while relay upload, browser injection, cloud research, and iPhone handoff are blocked until the owner explicitly changes the scope. This matters for health, legal, financial, and confidential work.
- **path:** pendant → relay → mac-planner → browser → iOS → dashboard
- **model tier:** Use realtime only to capture and acknowledge the boundary. Enforce it with deterministic policy code and signed labels; use a cheaper background model for local summarization. No model may override the boundary.
- **latency:** Apply the local-only label before any upload or cross-surface dispatch, under 100 ms at capture time. A policy change should be acknowledged in under 1 s and require a deliberate physical gesture for widening scope.
- **cost:** Negligible per request after implementation; occasional local summarization cost on the Mac. Storage and audit metadata are small compared with captured media.
- **security:** The default must be most restrictive when a label is missing or stale. Labels need integrity protection, expiry, and an append-only audit trail of attempted boundary crossings. The pendant should receive only policy state and opaque event IDs, never transcripts. Explicitly widening scope must use the existing physical approval latch.
- **missing:** A signed data-classification/ residency label carried with every audio, transcript, file, browser, and iPhone handoff artifact; A relay and Mac policy enforcement point that rejects disallowed destinations before bytes leave the current trust zone; A local-only processing route that does not silently fall back to cloud models; A dashboard showing blocked transmissions and the exact boundary a future action would cross

### "“Forget everything from that conversation everywhere it was copied—voice capture, transcript, relay job, Mac notes, browser draft, and phone handoff—and show me what could not be erased.”"
- **useful because:** Today the owner cannot reliably revoke a piece of personal context once it has crossed surfaces. A cross-surface erasure transaction would discover all derived artifacts from one opaque provenance ID, delete only those artifacts, invalidate queued retries and cached audio, and report verified deletion versus unknown or retained copies. It gives the owner a real privacy control rather than a request to each subsystem.
- **path:** pendant → relay → mac-planner → browser → iOS → dashboard
- **model tier:** Deterministic provenance traversal and deletion; no expensive model is needed. Use faculty-perception only to verify file, draft, and app state after deletion. A cheap model may help map a natural-language reference to a provenance ID, but must ask when ambiguous.
- **latency:** Acknowledge immediately; revoke future delivery under 500 ms; complete ordinary erasure within 10 s, with long-running storage deletion reported asynchronously.
- **cost:** One inexpensive reference-resolution call when needed plus verification calls; storage/index scans and browser/Mac latency dominate.
- **security:** Require exact provenance or an explicit confirmation when multiple conversations match. Tombstone before deletion so queued retries cannot resurrect data. Do not claim erasure from a delete receipt alone; distinguish deleted, inaccessible, retained-by-policy, and unknown. Keep only a minimal deletion receipt, not the content being erased.
- **missing:** End-to-end provenance IDs linking capture, transcript, audio artifacts, jobs, files, browser drafts, and phone handoffs; A tombstone/revocation mechanism shared by relay queues and Mac/browser/iPhone executors; Deletion adapters with independently verifiable postconditions for each surface; A retention exception policy and owner-visible audit of what remains

### "“Fill in the sensitive form without showing you my password or payment number, then let me physically approve only the exact final fields before submission.”"
- **useful because:** The owner can either hand the agent secrets or avoid useful automation. A credential-blind browser handoff would let the logged-in browser/password manager fill secret fields locally while the model receives only field names, redacted values, and a digest of the final submission. The pendant confirms that exact digest, so the system can complete high-value forms without exposing credentials to the relay, model context, or Mac logs.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use a cheap deterministic browser protocol for field classification and digesting; realtime is only for the owner's short confirmation. Never send secret field values to a model.
- **latency:** Render a redacted review within 2 s of form readiness; submit within 1 s after physical approval; report field changes as a new approval requirement.
- **cost:** Low model cost; browser/password-manager integration and local cryptographic operations dominate implementation, not invocation cost.
- **security:** The browser extension must be the only component allowed to read or write secret fields. Digest canonicalization must bind origin, URL, field labels, non-secret values, and secret-field presence without revealing values. Any DOM change, navigation, origin change, or expiry invalidates approval. Never log screenshots or secrets; retain only a redacted receipt.
- **missing:** A browser-native credential-blind fill protocol with secret-field capability declarations; A canonical redacted-form digest and origin binding shared by browser and pendant; A browser-side final-submit gate that consumes the existing physical approval latch; Independent verification that the submitted origin and non-secret fields match the approved digest


## Changes it proposed to its own stack

### `firmware` — Implement a local privacy-state machine on the nRF9160: enable i2c2 for the owned LSM6DSOX, classify stable worn/removed/covered transitions with hysteresis, and gate downlink playback at the earliest local boundary. Emit only signed state-transition events and a compact reason/confidence byte; preserve mute across link loss and require an explicit sw1 resume gesture.
- **owner gets:** Private answers stop being spoken aloud when the pendant is removed or covered, even if the network or Mac is stalled. The owner gets a discreet, dependable safety behavior rather than trusting a remote policy.
- effort: Medium firmware work: devicetree/driver integration, calibration flow, state machine, bridge protocol bit, and bench validation with the existing IMU and ESP32 audio bridge.  ·  risk: Bad calibration could mute unexpectedly or fail to mute. Recover with a deliberate resume gesture and a conservative default-to-silence policy; do not allow this state machine to authorize actions.
- cost: $0 hardware; negligible RAM/CPU, with occasional calibration storage under a few KB. No per-use API cost.  ·  latency: Local gate under 100 ms; no network round trip for the safety decision.
- security: Improves privacy; raw motion remains local. Signed transition events prevent a relay spoof from silently disabling the local gate.
- depends on: Existing LSM6DSOX and ESP32 bridge must be wired and firmware bus configuration enabled; A content-sensitivity bit must be added to downlink audio metadata


## What it asked for

_Nothing._
## Its own summary

Recorded four concrete additions this round. The highest-value one is a resumable, cross-surface operation graph: capture once, execute across Mac/browser/iPhone, pause for the existing physical approval latch, resume idempotently, and claim completion only after faculty-perception verifies each postcondition. I also recorded (1) a local IMU-based privacy perimeter that mutes private downlink audio when the pendant is removed/covered, (2) a post-action pendant undo window for eligible reversible jobs, and (3) the firmware change needed to wire the owned LSM6DSOX through i2c2 and enforce that privacy gate locally. The Mac bridge and browser are online; the nRF9160 pendant remains offline/stale, so the firmware behavior is specified but not bench-verified this round.

**Biggest unknown:** The remaining blocker is not another model: it is the missing connective protocol. We still need a durable operation DAG with idempotency/checkpoints, sensitivity metadata on audio, signed bounded undo tokens, and a verifier receipt joined to each action step. The pendant must then be brought online for hardware validation; until that happens, local IMU classification and mute latency remain unmeasured.

