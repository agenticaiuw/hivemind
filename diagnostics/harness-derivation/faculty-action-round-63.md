# Harness derivation — faculty-action — round 63

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Pause that and remind me where we left off when I’m ready.” Resume any in-progress request across the pendant, relay, Mac job, and private browser tabs without restarting or repeating completed actions."
- **useful because:** The owner can interrupt naturally while walking or in a meeting, then continue later with the exact pending decision, tab/session, and next safe action. Today each node can know status, but there is no single resumable handoff artifact.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model compiles a compact checkpoint; realtime model only speaks the short pause/resume acknowledgment.
- **latency:** Pause acknowledgment under 1 s; checkpoint durable within 3 s; resume brief under 5 s, excluding external page load.
- **cost:** ~$0.002–$0.01 per checkpoint/resume; dominated by one small background-model call, with ordinary relay/database costs.
- **security:** Checkpoint may contain private page excerpts and action parameters. Encrypt at rest, TTL by default (24 h), bind browser references to session IDs, redact secrets, and require confirmation before any irreversible resumed action.
- **missing:** A cross-surface checkpoint schema with completed/remaining steps and evidence references; Pendant reconnect event and a spoken pause/resume command route; Job runner support for idempotent continuation from a step boundary; Browser tab/session reattachment and stale-page detection; A dashboard view of resumable checkpoints

### "“Let me know silently when the thing you’re doing is ready, needs my decision, or failed.” The pendant should give distinct tactile patterns for queued, waiting-for-approval, completed, failed, and stale/disconnected work, with the Mac/browser continuing to do the work and the relay delivering the state even when voice is unavailable."
- **useful because:** The owner can walk, attend a meeting, or keep the phone away without missing a decision or completion. Today status exists in jobs and receipts, but the wearable has no private, glance-free channel that distinguishes actionable states.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → dashboard
- **model tier:** No expensive model for state transitions; deterministic event mapping. Use the realtime model only if the owner presses the button or asks for a spoken explanation.
- **latency:** Tactile state change within 500 ms of relay receipt; reconnect reconciliation within 3 s; no model latency for routine signals.
- **cost:** Negligible per event (metadata over the existing relay/job channel). Hardware prototype roughly $3–$8 for a low-power ERM/LRA haptic motor plus driver, with a few mA only during short pulses.
- **security:** Patterns can reveal that private work exists to someone holding the pendant, so allow a neutral mode and user-configurable mapping. Never encode sensitive content in vibration. Approval-required states must remain approval-required; haptics only notify and cannot authorize.
- **missing:** A pendant haptic actuator and driver (the current device exposes only one button and one LED); Firmware notification-pattern task with reconnect-safe event sequence numbers and battery-aware duty limits; Relay-to-pendant job-event push and durable last-unacknowledged state; Mac/browser job events normalized to queued, blocked, done, failed, and stale; Dashboard controls for pattern preferences, quiet hours, and a test pulse


## Changes it proposed to its own stack

### `firmware` — Make the 24 kHz playback path deadline-aware: add a bounded 60 ms-frame jitter buffer with sequence numbers, concealment on a missing frame, and a cooperative audio scheduler that reserves decode time before uplink encoding. Keep the existing SD policy (write only failed uploads), expose underrun/late/decode timing counters, and have the relay stamp end-to-end frame sequence and playout timestamps so acceptance tests can distinguish network loss from local starvation.
- **owner gets:** Speech and briefings stay intelligible through ordinary cellular jitter instead of clicking, stalling, or silently dropping audio; failures become diagnosable without storing routine recordings.
- effort: Medium firmware + relay work: ring-buffer and scheduler changes, relay metadata, and an automated 24 kHz acceptance harness across clean, jittered, and loss traces. Requires profiling on the actual board before tuning buffer size.  ·  risk: A larger buffer adds conversational delay; concealment can mask severe loss; scheduler bugs could starve uplink capture. Recover with a compile-time buffer cap, watchdog reset of the audio task, and counters/telemetry rather than indefinite buffering.
- cost: Negligible API cost; roughly 4–12 kB RAM depending on buffer depth and under 1% flash growth. No additional hardware required.  ·  latency: Adds configurable 60–180 ms playout latency, but prevents much longer stalls; interactive mode can use the smallest safe depth.
- security: Telemetry contains timing and packet IDs only, not audio. Ensure counters are authenticated with the existing session and do not retain payloads.
- depends on: 24 kHz audio-path acceptance criteria; A relay audio probe or test harness that can inject delay/loss; End-to-end sequence/timestamp fields in POST /pipeline/audio and GET /pipeline/:pipelineId/audio/:direction


## What it asked for

_Nothing._
## Its own summary

Round 63 produced two new, non-duplicate proposals. (1) A cross-surface pause/resume checkpoint: pendant interruption, relay persistence, Mac job step boundaries, and authenticated browser-tab reattachment so the owner can resume without repeating work; the proposal was recorded and the existing routes are connective pieces, not a complete feature. (2) A firmware/relay change for 24 kHz audio: bounded jitter buffer, sequence/timestamp metadata, packet-loss concealment, cooperative decode-before-encode scheduling, and diagnostic counters while preserving SD-as-failure-buffer policy. Hardware facts: nRF9160 Cortex-M33/211,608 B app RAM; decode is ~25.4 ms per 60 ms frame and encode ~15 ms, ~87% one-core combined; current capture/uplink is 15.625 kHz/16 kHz, so the requested 24 kHz path remains a real end-to-end mismatch. I also asked mac-planner whether a safe read/build harness exists.

**Biggest unknown:** I still lack the owner-approved 24 kHz acceptance criteria, audio_path_probe/verification tool, and permission to read/build the pendant simulator or inspect devices. Without those, I cannot honestly claim the audio path is shipped or run a build. I also need a concrete cross-surface checkpoint schema and idempotent job-step continuation implementation before pause/resume can be executed.

