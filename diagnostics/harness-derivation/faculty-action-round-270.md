# Harness derivation — faculty-action — round 270

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Finish this task across my Mac and browser, but if anything changes or the link drops, continue from the last verified step instead of repeating it.”"
- **useful because:** Today a multi-step action can leave the owner unsure whether it stopped before or after a side effect. This gives one truthful, resumable transaction: the Mac/browser executes, faculty-perception independently verifies each postcondition, the relay checkpoints it, and the pendant reports verified, retryable, unknown, or cancelled. A reconnect cannot duplicate a sent message, submitted form, or file mutation.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for planning and checkpoint reconciliation; realtime only for the owner's live clarification
- **latency:** Initial plan under 2 s; each verified step under 3 s; reconnect reconciliation may take 5–10 s but must never claim completion before fresh verification.
- **cost:** Usually 1 planning call plus cheap verifier calls per step; roughly $0.01–$0.08 per task depending on step count. Browser/Mac execution and receipts dominate wall time, not tokens.
- **security:** The relay stores opaque operation IDs and hashes, not page secrets. Verification evidence defaults to hash_only and sensitivity labels. Irreversible or ambiguous steps remain staged behind the existing physical transaction approval latch. A timeout yields unknown, never success.
- **missing:** A durable operation checkpoint schema joining actionId/attemptId to verifier receipts; A resume endpoint that replays only uncommitted steps after fresh verification; A dashboard view of per-step provenance and unknown states

### "“If I fall, stop treating the pendant as ordinary input, ask whether I’m okay, and escalate through my Mac if I do not respond.”"
- **useful because:** A pendant is the one surface that can notice a sudden impact and prolonged stillness while the owner is away from the Mac. The IMU already exists but is unwired. A local detector can alert immediately without opening a microphone; the relay can deliver the check-in, and the Mac can send a pre-approved message or call workflow only after the owner-defined escalation policy. This is the strongest genuinely wearable capability in the current hardware.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** Firmware thresholding first; background model only for policy selection and event summarization, never for the emergency trigger.
- **latency:** Impact classification locally within 1 s; haptic check-in immediately; escalation after an owner-configured grace period such as 30–120 s.
- **cost:** Negligible model cost for normal operation; occasional relay/Mac calls under $0.01 per event. Battery cost is the main expense: low-rate IMU sampling continuously, high-rate sampling only around candidate impacts.
- **security:** False positives and missed events are safety-critical. No raw motion stream leaves the pendant by default—only signed event class, confidence, monotonic counter, and battery/link state. Escalation contacts, message text, and location must be explicitly configured and require confirmation before activation. The device must offer a local cancel gesture and an unmistakable haptic countdown.
- **missing:** Firmware integration for LSM6DSOX on i2c2, including calibrated impact/free-fall/stillness state machine; A signed emergency policy and contact registry on the relay; A Mac/iOS escalation action with explicit owner approval and audit receipts; Bench validation across carrying, dropping, and normal jewelry motion

### "“Only let a high-impact action proceed while I am physically holding the pendant; if it has been sitting down, make me deliberately re-confirm.”"
- **useful because:** The existing approval latch proves a button gesture happened, but it cannot distinguish a deliberate in-hand confirmation from a button pressed accidentally in a pocket or by another object. A short IMU-derived handling proof—orientation change, grip movement, and a fresh button gesture—would bind approval to the owner's physical interaction without sending secrets to the device. The relay, Mac, browser, and pendant together become a materially stronger security boundary.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic firmware feature extraction and relay signature validation; no model needed for the security decision.
- **latency:** Less than 500 ms from the deliberate gesture to a signed handling proof; action starts only after relay validation and normal postcondition verification.
- **cost:** Near-zero inference cost; one small signed event per approval. Engineering cost is calibration and abuse testing rather than API spend.
- **security:** Never treat motion alone as approval. Require the existing deliberate sw1/encoder gesture plus a nonce-bound handling proof, expiry, monotonic counter, and replay rejection. If IMU data is missing or ambiguous, fail closed to staged approval. Keep raw motion local and expose only coarse features.
- **missing:** Firmware i2c2/LSM6DSOX driver and calibration persistence; An amendment to physical_transaction_approval_latch for nonce-bound handling evidence; Relay validation and audit fields for motion-proof freshness; A test harness for pocket, table, vibration, and remote-button attacks

### "“For a truly sensitive action, require both my pendant gesture and Face ID on my iPhone, then carry it out in the browser and prove exactly what changed.”"
- **useful because:** A single button press is not enough protection for account recovery, financial transfers, or changing a primary email. The pendant supplies deliberate physical intent while the real iPhone supplies an independent biometric factor; the relay coordinates both without exposing secrets to the pendant, and Mac/browser execution plus fresh verification produces an auditable result.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** Deterministic protocol and policy checks; background model only explains the requested action and summarizes receipts.
- **latency:** Challenge propagation under 2 s; owner has up to 60 s for both approvals; verification within 5 s after execution.
- **cost:** Usually under $0.05 in model/API cost; iOS/browser round trips dominate latency.
- **security:** Use independent nonces and audience binding so an approval for one action cannot authorize another. The pendant receives only a digest and human-safe summary, never credentials or page contents. Face ID status must come from the actual iPhone control path, not a simulated success. Any disagreement yields cancelled/unknown.
- **missing:** A cryptographic two-device approval protocol joining the existing pendant latch and iOS action result; An iOS Face ID confirmation surface exposed through the Mac mirroring control path; A policy registry marking which action classes require dual approval; A verifier receipt that binds both approvals to the exact browser mutation

### "“Update my information everywhere I ask—such as my address or email—and tell me which services changed, which failed, and which are still inconsistent.”"
- **useful because:** Changing the same identity detail across several logged-in services is currently a dangerous sequence of unrelated edits. This capability would discover the relevant forms, stage a complete change set, request one bounded physical approval, execute service by service, independently verify each result, and leave an explicit exception list instead of claiming global success.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** Background planner for service discovery and field mapping; deterministic executor and verifier for every mutation.
- **latency:** Preview in under 10 s; execution may take minutes because services can require waits or reauthentication. No service is marked changed without fresh verification.
- **cost:** Approximately $0.05–$0.30 for a multi-service run, dominated by browser interaction and verification context.
- **security:** Never infer that similarly named fields are equivalent without a preview. Mask secrets and unrelated profile data. Each service gets its own approval-bound step and receipt. If one service fails, stop or continue only according to the owner’s explicit policy; never silently retry an irreversible change.
- **missing:** A cross-service change-set and dependency model; Browser field equivalence and postcondition verifiers with service-specific locators; A partial-success dashboard and compensating-action planner; Owner policy for stop-on-first-failure versus continue-with-exceptions


## Changes it proposed to its own stack

### `integration` — Add a relay-coordinated two-device trust ceremony: the relay creates an action-specific challenge, the pendant signs deliberate physical intent, the real iPhone completes a native biometric confirmation, and the Mac/browser executor accepts the action only when both signatures and the exact postcondition-verification scope match.
- **owner gets:** They can reserve the strongest protection for the few actions where one accidental press or one compromised session would be unacceptable, without sending passwords or page contents through the pendant.
- effort: High: protocol design, iOS native confirmation surface, relay key management, Mac/browser enforcement, and adversarial replay testing.  ·  risk: A broken iOS bridge could strand an action; recover by expiring the challenge and returning a clear staged state. A protocol bug could authorize the wrong action, so require domain-separated signatures, short TTLs, monotonic counters, and independent verification before release.
- cost: Low recurring API cost; moderate engineering and iOS integration cost. No new pendant hardware strictly required, though a secure element would materially improve key protection.  ·  latency: Adds roughly 1–5 seconds for the second-device confirmation.
- security: Substantially improves authorization for high-risk actions; adds key lifecycle and recovery requirements. The pendant remains content-blind.
- depends on: Existing physical transaction approval latch; iOS control path with real Face ID result; Durable operation IDs and verifier receipts; Owner-defined action risk policy


## What it asked for

_Nothing._
