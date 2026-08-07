# Harness derivation — faculty-action — round 123

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I'm at my Mac and say “make this happen,” use the pendant's physical presence as the authorization: prepare the browser/Mac changes, show me a compact before/after summary, and execute only while I hold the pendant button; releasing it or unplugging the pendant aborts any not-yet-committed step."
- **useful because:** This gives the owner a fast, unambiguous physical consent gesture for consequential work without granting the agent ambient authority. It is testable now with the pendant's USB serial connection and ties voice intent, authenticated browser state, Mac actions, and a physical revoke signal into one action.
- **path:** relay-realtime → faculty-judgement → faculty-action → browser-extension → mac-planner → mac-terminal
- **model tier:** Realtime model interprets the short spoken command; a cheaper background planner prepares multi-step actions and the Mac executes typed reversible steps.
- **latency:** Preparation under 5 seconds; button-held execution feedback under 250 ms per step; disconnect/release abort observed within 500 ms.
- **cost:** About $0.01–$0.04 per invocation for planning and summarization; serial/event handling and Mac/browser work dominate latency, not tokens.
- **security:** The pendant's serial identity and a fresh button-hold nonce must be bound to the exact planned action, with expiry and replay protection. Sensitive page contents leave the browser only as minimally extracted fields; irreversible submits still require a final explicit approval. USB presence is not proof of intent by itself, hence the hold gesture.
- **missing:** firmware button-hold event and serial attestation; server-side action lease bound to a plan hash; abort propagation from serial disconnect through relay to Mac/browser queues; owner-configurable list of actions allowed under hold-only consent

### "Give me a 'walk-away handoff': when I tap the pendant before leaving, freeze the current browser/Mac task into a resumable handoff with the exact tabs, selected text, files, pending jobs, and next safe step; when I tap again later, brief me through the pendant and resume only the steps I approve."
- **useful because:** The owner can leave a task without losing their place or trusting memory. This is materially different from a generic background job: the wearable marks the physical transition away and back, while the Mac/browser preserve the exact working set and the relay holds it through sleep or disconnection.
- **path:** faculty-perception → faculty-judgement → faculty-action → browser-extension → mac-planner → relay-realtime
- **model tier:** A cheap background model extracts a structured handoff and redacts secrets; realtime is used only for the return briefing and approval conversation.
- **latency:** Snapshot in under 3 seconds; return briefing starts within 1 second of the tap and resumes only after explicit approval.
- **cost:** Roughly $0.005–$0.02 per handoff, mostly context extraction; storage is a small encrypted JSON record plus references to existing tabs/jobs.
- **security:** Never store passwords, cookies, or raw page dumps in the handoff. Store tab/session identifiers, redacted snippets, hashes, and local file paths with sensitivity labels. Revalidate tab and file state on resume; stale or changed targets become review-only.
- **missing:** pendant gesture events that survive relay loss; encrypted handoff record with TTL and device binding; browser snapshot API that returns selected text and stable tab identity; resume validator that compares snapshot hashes before Mac/browser action

### "If I hold the pendant's emergency gesture, start a timed safety check: alert me locally, notify my chosen contact with my last confirmed location/status, and escalate only if I do not cancel. Let me cancel from the pendant even if the Mac or voice session is unavailable."
- **useful because:** A wearable should be able to summon help when the owner cannot reach a phone or speak. The pendant, relay, Mac, and browser/phone surfaces together can provide a resilient escalation path rather than a cloud-only panic button.
- **path:** faculty-action → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Deterministic firmware and relay state machine; no expensive model during the emergency. Realtime model is used only if the owner speaks afterward and asks for explanation.
- **latency:** Local alert under 250 ms; relay notification under 2 seconds; escalation window configurable from 15 seconds to 10 minutes.
- **cost:** Negligible model cost; SMS/push delivery and relay storage dominate, roughly cents per activation.
- **security:** Require an intentional gesture, an unmistakable countdown, explicit contact configuration, encrypted status, and no location sharing outside the configured escalation chain. Test mode must be impossible to confuse with a real alert.
- **missing:** device-local emergency gesture and cancel latch; relay emergency state machine with authenticated device identity; location/status source and a configured notification provider; owner-configured contacts, escalation delay, and test mode

### "Move an active private browser task between my Mac and another trusted device without copying passwords: package the exact task state and a short-lived capability, let me approve the transfer with the pendant, and reopen it on the destination with secrets remaining in the destination's authenticated browser."
- **useful because:** The owner can leave the Mac, continue on another trusted surface, and return without losing a half-finished private task or exposing credentials to the relay. The pendant supplies a physical, human-visible handoff rather than an invisible session clone.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-action → unified
- **model tier:** Deterministic state packaging and cryptographic capability transfer; a cheap model summarizes the task state, while realtime handles only spoken approval.
- **latency:** Package in under 2 seconds; destination becomes resumable within 5 seconds; capability expires quickly if not redeemed.
- **cost:** Under $0.01 per transfer for summarization; storage and encrypted relay transport dominate.
- **security:** Never export cookies, passwords, or raw session tokens. Bind the short-lived capability to both devices, a task hash, and the pendant gesture; revoke on mismatch or expiry. Require explicit approval for any resumed mutation.
- **missing:** cross-device trusted-pair registry; browser task-state export/import that excludes credentials; relay-encrypted one-time capability exchange; destination-side reattachment and stale-state validation


## Changes it proposed to its own stack

### `interaction` — Add a cross-surface 'physical attention beacon' routine: when the owner says “where did I leave it?” or taps a pendant gesture, faculty-judgement can ask the Mac to start an escalating, recognizable audio/LED beacon, use currently available Calendar/browser context to label the search, and stop it from the pendant button. Keep the routine local to the Mac/bridge unless the owner explicitly asks for a network action.
- **owner gets:** A wearable that can summon a misplaced phone, bag, or nearby person is useful in daily life even before LTE registration. The owner gets an immediate physical affordance rather than opening an app and can silence it without returning to the Mac.
- effort: Medium: implement a serial gesture listener, Mac audio/LED pattern controller, and a relay job with timeout and stop idempotency; validate on the connected nRF9160 and ESP32 bridge without flashing.  ·  risk: Could annoy others or start unexpectedly; require a deliberate gesture/phrase, a 60-second maximum, visible active state, and a second tap to stop. Recover by automatic timeout and POST /jobs/:jobId/cancel.
- cost: Negligible API cost; approximately 1–2 engineer-days. Uses existing bridge power while active, with no cloud media upload.  ·  latency: Under 300 ms from button event to Mac playback if serial listener is persistent.
- security: No private data needs to leave the Mac. Do not use it as an authorization mechanism for unrelated actions.
- depends on: A serial transport from /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA that is read-only until explicitly armed; An allowlisted Mac audio/LED action exposed through mac_run_actions

### `integration` — Build a pendant-bound completion channel for action jobs: every Mac/browser job emits a small signed outcome envelope (succeeded, needs-review, failed, cancelled, with human-readable next step) to the relay, which queues it for the connected Mac/ESP32 audio bridge and pulses the pendant LED. Delivery must be idempotent and resumable, so a job finished while the owner was away is announced on the next physical reconnect rather than silently disappearing.
- **owner gets:** The owner will know that a long task actually finished without reopening the dashboard, and failures become actionable instead of being lost when a voice session ends. It makes the wearable a real hand for asynchronous work, not just a microphone endpoint.
- effort: Medium: define signed outcome envelopes, add relay-to-serial delivery and acknowledgement, add compact TTS/tones on the bridge, and map existing job receipts to owner-safe summaries.  ·  risk: A stale or duplicate announcement could be confusing; include job ID, monotonic sequence, expiry, deduplication, and a local mute gesture. Never speak secrets or page contents. Recover missed deliveries from GET /jobs/:jobId/receipts.
- cost: Low API cost (one short summary or deterministic tone per job); modest firmware work and bridge battery draw only during announcements.  ·  latency: Under 1 second when the bridge is connected; queued delivery on reconnect.
- security: Outcome envelopes must be authenticated and scoped to the owner's device. The relay stores only redacted status, not browser content. Physical reconnect is a delivery channel, not authorization to execute.
- depends on: A live serial protocol for the connected nRF9160/ESP32 devices; A durable relay outbox with acknowledgement and expiry; A safe outcome summarizer that can distinguish success, review-needed, failure, and cancellation; Existing GET /jobs/:jobId/receipts and POST /jobs/:jobId/cancel wired into the outbox

### `hardware` — Add a low-power tactile/haptic actuator and a secure element to the pendant, with firmware-managed patterns for countdown, success, failure, waiting-for-approval, and cancelled states. The secure element should attest the device and protect a monotonic event counter without exposing private keys to the Mac or relay.
- **owner gets:** The owner gets unmistakable private feedback in a noisy or socially inappropriate environment and a trustworthy physical identity for approvals, transfers, and emergency actions. They can understand whether the system is waiting, finished, or cancelled without opening a screen.
- effort: High: enclosure/board revision, driver and power-budget work, secure-element provisioning, firmware protocol, and relay verification.  ·  risk: Extra power draw, uncomfortable vibration, or actuator failure could hide state. Use bounded patterns, a hardware mute, watchdog fallback to LED, and manufacturing-time key recovery procedures.
- cost: Approximately $4–$12 in components and assembly at low volume; roughly 5–20 mA during haptic pulses and negligible idle draw, plus engineering and provisioning cost.  ·  latency: Local state feedback can begin below 100 ms; attestation adds tens to hundreds of milliseconds before a remote action is accepted.
- security: Improves resistance to forged USB events and replayed approvals, but key provisioning and device replacement become security-critical. No private key should leave the secure element.
- depends on: A defined pendant event/state protocol; Relay verification of device attestation and monotonic counters; Owner-approved tactile patterns and emergency behavior; A hardware revision compatible with the existing nRF9160 enclosure and battery


## What it asked for

_Nothing._
