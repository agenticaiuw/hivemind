# Harness derivation — faculty-action — round 208

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Finish this multi-step task, but if any verified postcondition fails, stop before the next irreversible step and tell me exactly where it stopped.”"
- **useful because:** This is the single most useful action guarantee: the system can act across browser and Mac without silently continuing after a wrong page, stale session, or failed save. It turns a long request into bounded, inspectable progress rather than a misleading final success.
- **path:** faculty-judgement → faculty-action → mac-planner → browser-extension → faculty-perception → relay-realtime → pendant
- **model tier:** Use the slower background planner for decomposition; use the low-latency tier only for owner-facing clarification. Execution is deterministic Mac/browser actions, and faculty-perception independently verifies each checkpoint.
- **latency:** Up to 2 seconds per checkpoint verification; long tasks may run in background with a concise pendant beacon when each step commits or halts.
- **cost:** Low-to-moderate: planner once per task, then route/verification calls dominate; no model call needed for deterministic checkpoints.
- **security:** Never proceed after unknown or contradicted verification. Sensitive browser values are verified as hashes or semantic predicates, not sent to the pendant or planner. Irreversible steps remain staged under the existing owner policy.
- **missing:** A coordinator that treats verify_operation_step as a barrier between steps and records halted/committed state; A standard checkpoint schema joining operation_id, attempt_id, executor receipt, and verifier provenance; Owner policy entries defining which steps are irreversible

### "“If I get interrupted while you are doing something on my Mac, pause safely, preserve the exact step and browser session, and let me say ‘continue’ or ‘cancel’ later.”"
- **useful because:** Long tasks currently risk finishing after the owner's attention has moved elsewhere. A pause point makes the pendant a real control surface: interruption becomes a safe state transition, not a lost job or accidental continuation.
- **path:** relay-realtime → pendant → faculty-action → mac-planner → browser-extension → faculty-perception
- **model tier:** Use deterministic job state and receipt handling; reserve realtime model use for recognizing the owner's short continue/cancel utterance and resolving ambiguity.
- **latency:** Pause acknowledgement under 500 ms when link is present; resume can take normal Mac/browser startup latency. Pending work must remain paused indefinitely until expiry.
- **cost:** Low: mostly state persistence and existing job polling; occasional realtime intent classification.
- **security:** On interruption, no new side effects are allowed. Resume requires the same operation lease and fresh verification of the current app/browser state; cancel must be idempotent. Do not persist page contents in the pendant.
- **missing:** A first-class PAUSED job state with resumable step cursor and expiry; An interrupt event from pendant/realtime to the Mac job coordinator; A resume preflight that re-verifies state before executing the next action

### "“When I say ‘what did you change?’, give me a private, haptic-guided audit of the last action: what was attempted, what was verified, and what remains unknown.”"
- **useful because:** Owners need trustworthy answers after delegation, especially when a browser or Mac action partially succeeds. This exposes the difference between executor receipt and independently observed result without reading sensitive page contents aloud or requiring the owner to inspect logs.
- **path:** pendant → relay-realtime → faculty-action → faculty-perception → mac-planner → browser-extension
- **model tier:** Use deterministic ledger/provenance assembly; use realtime only to summarize the already-redacted audit in the owner's words.
- **latency:** Initial audit response in 1–2 seconds from cached receipts; fresh verification may add up to 2 seconds and must state its observation time.
- **cost:** Low: ledger and verifier reads dominate; one short realtime summary when spoken.
- **security:** Default to hashes, app names, action types, and redacted predicates. Never transmit passwords, full message bodies, or form secrets to the pendant. Require explicit confirmation before exposing private snippets on any surface.
- **missing:** A user-facing audit projection over actionLedger plus verifier outcomes; A pendant interaction pattern for next/previous audit item using the forthcoming rotary input; A consistent redaction policy shared by Mac, browser, relay, and speech

### "“Keep this completely on my devices: use my private files and browser session to do the task, but prove that no content, credential, or screenshot crossed into the relay or model context.”"
- **useful because:** This gives the owner a meaningful privacy mode rather than a promise. Today the Mac, browser, relay, and model can each handle pieces, but there is no end-to-end, inspectable boundary proving that sensitive material stayed local while the action still completed.
- **path:** pendant → relay-realtime → faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-terminal → browser-extension
- **model tier:** Use a small policy/classification model locally on the Mac for data labels and deterministic enforcement in the relay and action executor. Use realtime only for the owner's short command and a redacted status response; do not send private content to the expensive model.
- **latency:** Policy evaluation under 200 ms per action; local file/browser operations retain their normal latency. If a step cannot be proven compliant, block it rather than silently downgrade privacy.
- **cost:** Low recurring inference cost if classification is local; engineering cost is substantial because every cross-surface handoff must carry data-flow labels and an auditable receipt.
- **security:** The boundary must cover prompts, tool arguments, screenshots, logs, crash reports, browser results, and cached audio—not just network egress. Secrets must be represented by opaque handles or hashes. A privacy-mode failure is a hard stop requiring explicit owner choice; never claim proof from an executor receipt alone.
- **missing:** A data-flow label and taint policy understood by relay, planner, browser bridge, and Mac executor; A local-only execution route that accepts opaque file/browser handles without returning contents to the model; An append-only redacted proof of what crossed each boundary, independently inspectable by faculty-perception; A kill switch that expires privacy mode and discards prohibited queued payloads

### "“My pendant is missing—lock it immediately, show me exactly what it can no longer approve, and recover only the safe queued notes onto my replacement device.”"
- **useful because:** A wearable is physically lost more easily than a Mac. Today revoking its authority, separating harmless queued data from approval material, and re-enrolling a replacement are not one owner-facing operation. This prevents a lost pendant becoming either a security hole or a total loss of the owner's offline captures.
- **path:** relay-realtime → faculty-judgement → faculty-action → faculty-perception → pendant → mac-planner
- **model tier:** Use deterministic key revocation, queue classification, and replacement enrollment; use the realtime model only to explain the resulting inventory and ask for explicit recovery choices.
- **latency:** Revocation must take effect at the relay within seconds; replacement enrollment can take minutes but must remain unusable until verified. Recovery should be resumable across link drops.
- **cost:** Low per event; engineering cost is in key lifecycle, queue encryption/classification, and a careful recovery UX.
- **security:** Revocation must invalidate pending approvals, queued commands, and old device signatures immediately. Never recover secret-bearing payloads by default. Require a second owner-held factor on the Mac or a deliberate replacement-device gesture; log every recovered item and permanently destroy unrecoverable secret material.
- **missing:** A relay-side device-key registry with atomic revoke and replacement enrollment; Typed, encrypted queue items that distinguish safe notes from approvals, credentials, and action intents; A recovery ceremony using the Mac plus replacement pendant without exposing secrets to the model; A read-only inventory and proof that old approval envelopes are rejected


## Changes it proposed to its own stack

### `hardware` — Add a MAX17048-class I2C fuel-gauge board to the pendant revision, wire it onto the existing I2C bus with the LSM6DSOX/DRV2605L, and expose calibrated state-of-charge, voltage, and estimated time-to-empty to the relay. Firmware should degrade to voltage-only if the gauge is absent and never claim a percentage without a valid gauge reading.
- **owner gets:** The pendant can warn before it dies during a conversation or action, and can refuse to start a long recording when the remaining energy is genuinely insufficient. The warning can be private haptic feedback rather than a conspicuous LED.
- effort: Low-to-moderate hardware revision and firmware driver work; validate across the 500 mAh LiPo discharge curve and temperature range.  ·  risk: Incorrect calibration could create false alarms or premature refusal. Recover by treating gauge data as advisory, retaining a conservative voltage cutoff, and logging raw voltage plus gauge status for diagnosis.
- cost: Approximately $3–$8 in parts and under 1 mA typical gauge draw; negligible impact on the existing audio budget.  ·  latency: No effect on audio; battery reads can be sampled every 10–60 seconds.
- security: Battery telemetry is low sensitivity, but do not infer owner location or activity from it; relay should receive coarse state unless diagnostics are explicitly requested.
- depends on: Finalize the jewellery enclosure PCB/wiring revision; Enable the already-used I2C bus without disrupting the IMU and haptic controller; Define low-battery policy as owner-configurable rather than hard-coded

### `hardware` — Add a secure-element IC such as ATECC608B/SE050 to the jewellery pendant revision, provision a non-exportable device key at manufacturing, and require every approval, offline outbox item, and firmware identity claim to be signed by that key. Bind relay acceptance to an attested device key rather than a bearer token stored in flash.
- **owner gets:** A deliberate press on the pendant remains trustworthy even if a Mac, relay credential, or copied firmware image is compromised. The owner gets a real physical root of trust for approvals and private queued notes instead of security that depends on ordinary flash secrets.
- effort: Moderate PCB/I2C integration, provisioning ceremony, relay key registry, rotation/revocation, and firmware boot/command-path changes. Prototype on the existing bench hardware before committing the jewellery PCB.  ·  risk: Lost or damaged hardware needs recovery; a provisioning mistake could brick trust for that unit. Recover with an owner-mediated re-enrolment flow, a revocation list, and a factory-reset path that erases local queues before accepting a new identity.
- cost: Roughly $1–$5 per unit plus provisioning fixtures; tens of milliwatts only during cryptographic operations, negligible versus the audio radio budget.  ·  latency: Typically tens to hundreds of milliseconds for signing/verification, acceptable off the audio real-time path; approval UX should show pending while the signature completes.
- security: Strongly improves authenticity and replay resistance, but does not make compromised host software trustworthy; relay must still enforce operation digests, expiry, monotonic counters, and independent verification.
- depends on: Finalize the physical approval envelope and key-rotation protocol; Reserve an I2C address and board space alongside the existing IMU/DRV2605L; Define manufacturing provisioning and owner recovery procedures


## What it asked for

_Nothing._
## Its own summary

Round 208 produced three owner-facing proposals and one hardware change. The strongest is verified step-barrier execution: after every Mac/browser action, faculty-perception must independently verify the postcondition before faculty-action may continue; unknown or contradicted means halt, not success. Also proposed interruption-safe pause/resume with a preserved step cursor and fresh preflight verification, plus a fuel gauge for truthful low-battery warnings on the 500 mAh pendant. The audit/replay idea was recorded but flagged close to existing work, so I will not rephrase it. What I still need is not another tool grant: I need the missing coordinator/state-machine layer between /plan, /execute, receipts, browser results, and verify_operation_step, plus an owner-supplied policy for which action classes may proceed without approval. The owner still has to choose the proactive-versus-staged policy; defaults should remain conservative.

**Biggest unknown:** Whether the existing job implementation can be extended with PAUSED and checkpoint-barrier states without creating a second ledger. I cannot honestly claim these capabilities are reachable today until that coordinator and its durable operation/attempt/checkpoint schema exist.

