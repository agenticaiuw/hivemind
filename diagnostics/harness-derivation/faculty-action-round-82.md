# Harness derivation — faculty-action — round 82

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-system-status-round-82** — Mac bridge and relay are reachable, but browser extension is offline with 7 pending commands; Accessibility and Screen Recording are ungranted, computer-use loop disabled, and live pipeline metadata shows 15,625 Hz capture while TTS output is 24 kHz.
  - evidence: GET /ops/status HTTP 200 and GET /pipeline HTTP 200 at round 82

## Capabilities it proposed

### "“Do it, and don’t tell me it’s done until you’ve verified the result.”"
- **useful because:** Today the system can queue Mac/browser actions and issue receipts, but a receipt only proves an attempt—not that the world changed. This cross-surface capability would execute the judged plan, then have perception independently inspect the relevant Mac window, browser tab, or device state and report success, partial completion, or an actionable failure. It is especially valuable for reminders, edits, browser forms, and multi-step work where silent no-ops are costly.
- **path:** faculty-judgement emits a typed plan with target state and verification predicate → relay persists an action transaction and coordinates retries/timeout → faculty-action dispatches reversible Mac or browser steps → faculty-perception captures a fresh observation and compares it with the predicate → relay stores an evidence capsule linked causally to the transaction → relay-realtime speaks one short outcome on the pendant; dashboard shows before/after evidence and offers undo where supported
- **model tier:** Use the realtime tier only to interpret the owner's spoken request and resolve ambiguity. Use the cheaper background planner for multi-step execution and a cheap deterministic comparator for typed predicates; reserve a vision-capable model only when structured UI evidence is insufficient.
- **latency:** Immediate acknowledgement in under 1 second; reversible execution typically under 10 seconds; verification within 5 seconds of the final step. Long jobs continue asynchronously and notify only on verified completion or a meaningful blocker.
- **cost:** Roughly $0.01–$0.08 for ordinary typed verification, dominated by planner and any screenshot-vision fallback; most checks should use structured status or extracted page text and avoid a second expensive model call.
- **security:** Private page text, screenshots, and local state remain on the Mac/relay according to existing retention policy; evidence must be redacted before persistence and expire quickly. Never verify by performing a second destructive action. Sending, deleting, purchasing, or submitting still requires the owner's confirmation before execution; verification may run automatically afterward.
- **missing:** A typed verification-predicate schema shared by judgement, action, and perception; A transaction state machine separating attempted, observed, verified, contradicted, and unknown; A fresh-observation route that binds evidence to target, timestamp, and causal action id; Retry/rollback rules for contradicted or stale observations; Retention and redaction policy for linked evidence capsules


## Changes it proposed to its own stack

### `integration` — Add an end-to-end audio format contract enforced at every pipeline boundary. The contract must carry declared sample rate, actual PCM frame count, channels, codec, clock domain, and resampler stage; validate that capture (currently observed as 15,625 Hz), Opus uplink (16 kHz), relay transcode, TTS output (24 kHz), and pendant playback (24 kHz decoded / 31,250 Hz I2S wire clock) are not silently conflated. Reject or mark a run as format_mismatch when metadata and byte-derived duration disagree, and emit one machine-readable resampling manifest with the pipeline receipt.
- **owner gets:** The owner gets speech that is intelligible and correctly timed instead of a system that can claim “24 kHz” while an earlier stage is actually 15,625 or 16 kHz. Failures become diagnosable from one receipt rather than requiring UART archaeology, and acceptance of the requested 24 kHz path becomes measurable.
- effort: Medium: shared schema plus validators in relay and local pipeline, byte-duration checks, one fixture per boundary, and a dashboard/briefing display of the manifest. Firmware changes should follow only after the contract exposes the real clock mismatch.  ·  risk: Strict validation may temporarily reject existing prototype captures or surface clock drift as failures. Recover by retaining the raw artifact, labeling the failing boundary, and allowing an explicitly flagged compatibility mode during development; never silently resample twice.
- cost: Negligible API cost; a few hundred bytes of metadata per run and modest CPU for arithmetic checks. No new hardware required for the contract.  ·  latency: Under 1 ms for metadata and duration validation; no additional model call. A corrective resample, if required, adds only the existing codec/resampler latency.
- security: Metadata is non-sensitive; raw audio retention remains governed by existing policy. Do not upload additional audio solely for validation—derive checks from headers, frame counts, and already-authorized payloads.
- depends on: Owner-provided 24 kHz acceptance criteria (still outstanding); A real pendant/device connection for hardware verification (currently no pendant is connected); An explicit choice whether the product contract is 24 kHz speech at the decoded playback boundary or 24 kHz capture, since current hardware reports 15,625 Hz capture

### `firmware` — Add a factory/service-mode audio clock calibration protocol spanning the nRF9160, relay, and ESP32 bridge. On request, the pendant emits a short deterministic PCM/Opus calibration sequence with monotonic sample counters; the bridge returns captured I2S edge counts and the relay compares declared versus measured duration across capture, uplink, decode, resampling, and playback. Persist only the resulting calibration coefficients and pass/fail record, not the calibration audio. Refuse to advertise the 24 kHz playback path as healthy when drift or an unexpected clock domain exceeds the configured tolerance.
- **owner gets:** The owner can trust that speech will not slowly change pitch, timing, or truncate when the pendant is worn for a long conversation. When the path is wrong, the system can say exactly which device or clock is responsible instead of presenting a plausible but misleading 24 kHz status.
- effort: High: firmware test mode and monotonic counters, a bridge loopback/edge counter, relay comparison endpoint, persisted calibration record, and a service report in the dashboard. Requires a real pendant and bridge fixture for validation.  ·  risk: Calibration could interrupt an active conversation or falsely fail under radio loss. Restrict it to startup/service mode, keep the last known-good coefficients, distinguish transport loss from clock failure, and never overwrite a good calibration with an incomplete run.
- cost: No per-request model cost. Small firmware and relay storage overhead; likely under 1 KiB per calibration record. Hardware cost is zero if the existing I2S bridge exposes measurable edges; otherwise a low-cost timer capture/GPIO instrumentation revision may be needed.  ·  latency: No normal-path latency. Service calibration takes roughly 1–3 seconds when explicitly requested.
- security: Calibration carries no owner content and should not upload conversational audio. Authenticate service-mode requests and require a physical button gesture or maintenance authorization before running diagnostics.
- depends on: A connected pendant and ESP32 bridge; An agreed tolerance and definition of acceptable 24 kHz playback; Firmware build/toolchain access controlled by the owner; A relay route for calibration manifests and dashboard rendering


## What it asked for

_Nothing._
