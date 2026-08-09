# Harness derivation — faculty-action — round 240

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Send this message, but only if the final recipient, attachment names, and message text are exactly what I said; tell me if anything differs.”"
- **useful because:** This is the most useful trust boundary for an agent with access to private browser sessions: it turns a vague spoken request into a checked, owner-approved send, while catching wrong-account, wrong-recipient, and stale-draft failures before they become irreversible.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use the realtime model only to clarify the spoken request; use the cheaper planner for drafting and the deterministic verifier for field/file checks.
- **latency:** Draft in 5–10 seconds; verification under 2 seconds per step; require one deliberate pendant approval before send.
- **cost:** Usually one realtime turn plus one planner/verifier pass, roughly $0.01–$0.05; browser and Mac calls dominate latency, not tokens.
- **security:** The pendant receives only a canonical summary and digest, never message secrets or page contents. Require confirmation for send; if recipient, body, or attachment digest changes, cancel rather than silently repair. Store only hashes and a short redacted summary in the ledger.
- **missing:** A transaction bundle that binds recipient/body/attachment digests to the physical approval nonce; Verifier support for attachment/file digests as a first-class postcondition; A single commit endpoint that refuses execution when any pre-send verification is stale

### "“When my Mac or browser task finishes, give me a short spoken result and a tactile pattern that distinguishes completed, partially completed, and unknown—without making me ask what happened.”"
- **useful because:** A queued action should not disappear into a job list. The owner gets immediate, truthful closure even when the pendant is away from the Mac, and can distinguish safe retry from dangerous duplicate execution.
- **path:** relay → pendant → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Use background workers and deterministic receipt aggregation; reserve realtime speech generation for the final one-sentence summary only when the owner is actively listening.
- **latency:** Emit a compact outcome event within 1 second of a receipt or verifier result; deliver it on reconnect and suppress duplicate announcements.
- **cost:** Low: no model call for normal outcomes, less than $0.005 per job; storage and delivery are the main costs.
- **security:** Speak only a redacted summary and opaque job label. Never announce message contents, secrets, or private file names aloud by default. Unknown means unknown: do not phrase an executor receipt as success without independent verification.
- **missing:** A durable outcome-event envelope shared by relay and pendant; A policy for spoken-summary sensitivity and quiet hours; A compact event-ID acknowledgement path from pendant to relay

### "“Mark what just happened.” When I press the pendant bookmark button, capture a synchronized, private incident packet: the pendant event/audio cursor, Mac foreground app and recent action receipt, and the current browser URL/title—then later let me ask the agent to file or explain the incident."
- **useful because:** A physical bookmark is the only reliable timestamp the owner can create while something is going wrong. Joining it to the Mac/browser state turns an otherwise useless moment marker into a reproducible bug or support report, without continuously recording the owner's screen or microphone.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Use deterministic collection and hashing first; invoke a background model only when the owner later asks for a narrative or a filed report. Realtime is unnecessary unless they ask by voice immediately.
- **latency:** Acknowledge the button within 150 ms; collect host/browser metadata within 2 seconds; upload later if the link is down.
- **cost:** Near-zero for capture (metadata and hashes); $0.01–$0.05 only when generating a report or explanation.
- **security:** Default packet contains metadata, not screenshots or raw audio. Browser URL/title and app names may be private: encrypt at rest, apply a per-surface sensitivity policy, and require confirmation before sharing or filing externally. The pendant stores only an opaque incident ID and bounded cursor, using the existing failure-path spool.
- **missing:** A synchronized correlation ID spanning pendant bookmark, Mac ledger receipt, and browser snapshot; A bounded recent-event index on the relay so a bookmark can collect the preceding few seconds without continuous capture; An owner-facing incident review that shows exactly what will be shared before filing

### "“Privacy shield.” A deliberate pendant gesture should immediately stop all staged actions, hide or blur private browser workspaces, mute spoken summaries, and report when every surface has entered the safe state."
- **useful because:** The owner may need to protect private work in a meeting, at a checkout counter, or after losing the laptop—precisely when speaking to the agent or navigating a menu is unsafe. One physical gesture creates a fast, cross-surface emergency boundary rather than merely cancelling one transaction.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-action → faculty-perception
- **model tier:** Deterministic event fan-out and state checks; no realtime model. Use the model only later if the owner asks which work was interrupted.
- **latency:** Pendant acknowledgement under 150 ms; relay fan-out under 500 ms; Mac/browser safe-state verification within 3 seconds. If verification cannot complete, report unknown rather than claiming protected.
- **cost:** Negligible per activation; a few signed events and read-only verification calls. No model call in the emergency path.
- **security:** The gesture must be locally recognized and authenticated by a monotonic counter, not by voice. It must never delete data or send messages. Browser masking should preserve drafts but prevent exposure; the system needs an explicit policy for whether to lock the whole Mac, hide selected tabs, or merely stop agent activity. A timeout or deliberate clear gesture must be required to resume.
- **missing:** A pendant-to-relay emergency event that is accepted while ordinary action traffic is queued; Mac/browser safe-state operations with independent postcondition verification; A persistent safe-mode bit that blocks new execution until the owner clears it physically; An owner-configurable privacy policy describing masking, audio muting, and lock behavior


## Changes it proposed to its own stack

### `firmware` — Wire the already-owned DRV2605L and motor into the nRF9160 firmware: enable i2c2 in devicetree, add a bounded non-blocking haptic queue, and map the accepted tactile_action_outcome_beacon patterns to short, intensity-limited effects. Keep the audio path untouched; fall back to the existing LED/audio cue if I2C is absent or the driver faults. Add a bench self-test and event receipts, but do not flash automatically.
- **owner gets:** The pendant can communicate success, retry, unknown, and cancellation discreetly in a pocket or jewellery enclosure instead of forcing the owner to look at a single LED or listen to speech in public.
- effort: Moderate firmware integration: devicetree, DRV2605L driver, queue/state machine, and bench test. No new parts; requires owner-controlled build and later flash approval.  ·  risk: A stuck I2C bus or motor command could block input or drain the battery. Use timeouts, reset the controller, cap duty cycle, and degrade to LED/audio. Recover by disabling the haptic feature flag without affecting recording or LTE.
- cost: Existing hardware; negligible incremental BOM. Brief motor pulses add roughly tens of milliwatts during effects, with low average energy.  ·  latency: Under 100 ms from received outcome to tactile cue; no impact on 24 kHz codec tasks if the I2C worker is separate.
- security: Only signed outcome classes and opaque IDs reach firmware; no message or page contents. Haptic output must never approve an action.
- depends on: tactile_action_outcome_beacon; physical_transaction_approval_latch; owner-controlled firmware build and flash approval

### `hardware` — Add a low-profile detented rotary encoder with an integrated push switch and one additional deliberate-action button to the jewellery pendant, then define a physical approval inbox: the wheel selects among queued staged transactions, each detent produces a distinct short haptic tick, a press reads a redacted class/target summary through the audio bridge, and only the separate deliberate-action button approves the selected transaction. Selection must never execute or approve anything; changing selection invalidates any approval nonce until the owner explicitly re-confirms.
- **owner gets:** The owner can safely review and act on several pending computer tasks from the pendant without opening a phone or trusting a single ambiguous gesture. This makes an always-worn pendant useful for real queues—messages, purchases, file shares—rather than only one action at a time.
- effort: New input hardware and enclosure work, plus firmware GPIO/interrupt and queue-navigation state machine. Relay must expose bounded pending transactions and canonical redacted summaries. Requires a future hardware revision; do not pretend the current DK has the control.  ·  risk: Accidental detents or pocket movement could change selection, but cannot approve. Audio summaries could leak sensitive targets, so default to category plus masked destination and require an explicit listen gesture. A lost link must leave the local queue read-only; expired or digest-mismatched entries are rejected.
- cost: Roughly $2–$8 in prototype encoder/button parts and modest PCB/enclosure redesign; negligible idle power, with brief haptic/audio activity during navigation.  ·  latency: Selection feedback under 100 ms locally; pending-queue refresh depends on relay connectivity. No impact on the 24 kHz codec worker if input handling is event-driven.
- security: Improves security by separating selection from approval and invalidating stale approvals after selection changes. The pendant receives only opaque transaction IDs, risk classes, masked summaries, digests, and expiry—not secrets or page contents.
- depends on: physical_transaction_approval_latch; tactile_action_outcome_beacon; a relay endpoint exposing ordered pending transaction summaries; a future jewellery enclosure/PCB revision


## What it asked for

_Nothing._
