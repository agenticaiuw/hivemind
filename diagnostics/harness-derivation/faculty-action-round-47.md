# Harness derivation — faculty-action — round 47

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If an action is blocked because my Mac or browser is unavailable, keep it safe, tell me exactly what I need to fix, and resume automatically when the required connection or permission returns."
- **useful because:** Today a request can fail after a long timeout or appear successful despite doing nothing. The owner should not have to remember which extension or macOS permission to repair, nor repeat the original intent.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background/state-machine orchestration with a cheaper model for recovery instructions; realtime only for the short spoken alert.
- **latency:** Immediate blocked status within 1 second; health-triggered retry within 5 seconds of Accessibility/bridge recovery; no repeated action without idempotency and fresh preflight.
- **cost:** Low: mostly local health polling and durable state; occasional small-model recovery message, under $0.01 per blocked job excluding voice.
- **security:** Store the intent and minimum parameters encrypted; never replay irreversible actions automatically. Require renewed approval if an approval window expired or page/account state changed; surface exact target and expiry on pendant/dashboard.
- **missing:** Fail-closed reachability and postcondition adapter; Durable blocked-action state with idempotency keys and expiry; Mac permission/bridge health transition events; A pendant/relay notification path that can distinguish blocked, resumed, and expired

### "When I ask you to create something—like a reminder, note, or draft—from my pendant, make sure it appears exactly once even if the pendant, relay, and Mac all retry or reconnect in a different order."
- **useful because:** A wearable can hear an instruction while offline, the relay can queue it, and the Mac can independently retry it after reconnecting. Today those paths can create duplicates or leave the owner unsure whether to try again. Exactly-once intent handling would make everyday capture dependable.
- **path:** pendant → relay → mac-planner → mac-terminal → dashboard
- **model tier:** Deterministic idempotency ledger and reconciliation first; use a cheap background model only to normalize equivalent natural-language intents. Realtime is not needed except to acknowledge capture.
- **latency:** A local spoken acknowledgement immediately; durable deduplication and Mac reconciliation within 5 seconds of connectivity. Never block capture on a cloud round trip.
- **cost:** Low: a small durable intent record and hash per capture; occasional background normalization under $0.01. No extra realtime inference required.
- **security:** Bind each intent to the paired owner/device and retain only the minimum content until execution. Do not deduplicate across different destinations without showing the owner the target; drafts and reminders may execute automatically, while sends/deletes/purchases still require confirmation.
- **missing:** A shared intent-id and semantic-fingerprint ledger spanning pendant, relay, Mac, and browser; Adapters that accept idempotency keys for Reminders, Notes, drafts, and shell actions; A reconciliation view that distinguishes applied-once, conflicting, and expired intents; A conflict policy for two captures that sound similar but are not the same request


## Changes it proposed to its own stack

### `mac-harness` — Add a fail-closed action reachability adapter shared by mac_run_actions, mac-vision, and browser routing. Before any UI action, verify the running host binary (bundle identity/path) is Accessibility-trusted and the browser bridge has a live heartbeat; if not, mark the step blocked rather than successful. After each reversible UI step, require an independent postcondition observation (frontmost app/title, file/reminder existence, or browser result) and classify outcomes as applied, blocked, or unknown. Persist the reason and a concrete recovery instruction in the receipt, and prevent dependent steps from running after blocked/unknown.
- **owner gets:** The owner currently receives success-shaped receipts for clicks and typing that did nothing, and browser jobs can spend 45 seconds before discovering the extension is offline. This makes actions trustworthy: either the requested change happened and is evidenced, or the owner gets an honest, immediately actionable failure.
- effort: Medium: central adapter plus adapters for common action types, tests against the current untrusted Accessibility state and offline browser state.  ·  risk: Some legitimate actions may be reported unknown and stop earlier until a postcondition observer exists; recover by allowing explicit retry or a manually confirmed override. No action should be silently repeated.
- cost: Negligible API cost; small local observation overhead per step.  ·  latency: Adds roughly 100–500 ms per UI step; saves tens of seconds on offline-browser failures.
- security: Improves safety by failing closed and avoiding duplicate retries; does not broaden permissions or exfiltrate screen data.
- depends on: A correct Accessibility grant for the actual AI Pendant Agent binary; Browser bridge heartbeat/polling in the selected browser; Typed postcondition observers for each action family

### `firmware` — Make the uplink genuinely 24 kHz end to end: configure the I2S microphone/clock and DMA for 24,000 Hz capture, encode Opus at 24 kHz (or perform a documented high-quality 15.625→24 kHz resample before encoding), and carry the sample-rate contract through relay transcoding, pipeline telemetry, and Mac STT. Add a loopback/impulse and speech fixture that verifies timestamps, frame duration, no drift, and intelligibility over a 10-minute LTE-M run.
- **owner gets:** The current path advertises 24 kHz playback but captures at 15,625 Hz and uplinks Opus at 16 kHz, so the owner cannot actually use a superwideband voice path. Correcting the contract should make spoken commands clearer and reduce resampling artifacts.
- effort: High: clock/DMA and Opus changes, relay format negotiation, memory/performance profiling, and hardware validation on the current DK before choosing production audio hardware.  ·  risk: The nRF9160 prototype has only 211,608 B application RAM and audio already consumes roughly 87% of one core when encode and decode overlap; overruns or battery/radio cost may rise. Recover with 20/16 kHz negotiated fallback, bounded jitter buffering, and explicit telemetry rather than silently downsampling.
- cost: No per-request API increase; possible production BOM increase for a 24 kHz-capable mic/clock and modest higher LTE payload. Prototype power draw may increase during simultaneous encode/decode.  ·  latency: Target unchanged 60 ms frames; initial firmware profiling may add buffering while tuning DMA and Opus complexity.
- security: No new data class; higher-fidelity audio increases sensitivity, so retain short-lived buffers and expose negotiated sample rate in receipts.
- depends on: A 24 kHz-capable microphone and stable I2S clock on the product design; Relay and Mac pipeline sample-rate negotiation; Acceptance tests for 24 kHz audio quality and CPU/RAM headroom


## What it asked for

_Nothing._
## Its own summary

Discovered the live action path is not safe to claim success: /observe reports Accessibility untrusted for the actual AI Pendant Agent binary, synthesized events rejected, and UI receipts therefore cannot be trusted. Browser bridge is offline with 3 pending commands. Proposed (1) a fail-closed reachability/postcondition adapter that blocks dependent steps and records honest recovery reasons, (2) a parked-and-resume capability keyed to health transitions and idempotency, and (3) the missing 24 kHz uplink firmware/relay contract (current mic is 15,625 Hz and Opus uplink 16 kHz while playback is 24 kHz).

**Biggest unknown:** Whether the orchestrator can grant Accessibility to the exact running AI Pendant Agent bundle and bring the browser bridge online; without those, I cannot validate real-world action execution. I also still lack the requested 24 kHz acceptance criteria and firmware build/device-inspection tool.

