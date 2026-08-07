# Harness derivation — relay-realtime — round 82

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Route this to the right place and tell me what’s happening with it."
- **useful because:** The owner can speak naturally. The relay turns that into an explicit intent, sends it to the correct downstream agent, and can report status without guessing. This reduces latency, avoids brittle ad-hoc routing, and keeps the conversation grounded in actual job state.
- **path:** pendant → relay → mac-bridge → browser → unified
- **model tier:** Realtime at relay for intent capture; cheaper planner/model on Mac for execution; perception/judgement/action faculties for status and validation.
- **latency:** Fast first response under ~300ms to acknowledge routing; longer execution happens off the critical path.
- **cost:** Low per invocation at relay; most cost is downstream planning/execution and any browser automation.
- **security:** Routing must not exfiltrate sensitive transcript unnecessarily. Only send the minimum utterance/context required. Status reporting must not fabricate completion.
- **missing:** relay_route_intent needs an implementation and a stable schema for intent labels and context fields; Job status events/streaming back to relay while a task runs

### ""Just talk normally" — have the pendant and Mac automatically keep my voice turns intelligible and correctly timed even when the wearable's real audio clock differs from the declared rate, with no calibration procedure for me."
- **useful because:** The live voice front door should not intermittently sound slow, fast, clipped, or lose turn boundaries. Fresh pipeline evidence shows pendant input declared at 15,625 Hz while Mac TTS is 24,000 Hz, so trusting metadata can silently distort every conversation. This would make the device dependable while worn away from the Mac.
- **path:** pendant → relay → mac-planner → faculty-perception
- **model tier:** No LLM for calibration; deterministic DSP and telemetry at the relay/firmware boundary. Use the realtime model only for the resulting speech turns, and faculty-perception only when telemetry indicates an ambiguous or degraded segment.
- **latency:** Add under 100 ms to a turn for streaming resampling/clock correction; run a short calibration exchange in the background during connection establishment, never as an owner-facing setup flow. Recovery from drift should converge within 1–2 seconds.
- **cost:** Negligible API cost (DSP and small telemetry packets dominate; no extra model calls). Engineering cost is firmware clock telemetry, relay resampling, and Mac output metadata/loopback reporting.
- **security:** Audio remains within the existing pendant-to-relay-to-Mac path. Calibration packets contain levels, timestamps, and rates—not transcript or raw audio. Do not persist raw calibration audio; cap telemetry retention and authenticate device/session IDs.
- **missing:** Pendant-side actual ADC/DAC sample-clock and buffer telemetry (including underrun/overrun counters); A relay media layer that can resample and time-stretch PCM per stream while preserving speech turn markers; Mac TTS/input endpoints that report actual emitted sample rate and timestamps rather than only declared format; An end-to-end calibration state machine and health indicator exposed to the live voice session

### "When LTE-M gets weak, keep my request usable: automatically switch from live audio to a compact command representation, confirm what was understood, and finish the action when the link recovers instead of making me repeat myself."
- **useful because:** A worn LTE-M pendant will encounter coverage gaps where a full PCM stream cannot be sustained. Today a dropped voice stream can strand the owner away from the Mac with no durable indication of whether the request arrived. A negotiated degraded mode would preserve the useful intent and provide an honest spoken receipt when delivery resumes.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception
- **model tier:** Realtime model handles only the short spoken confirmation and ambiguity resolution. Deterministic voice-activity/framing and compact transport run at the pendant/relay; mac-planner or browser-extension performs the eventual action. No background expensive inference is needed.
- **latency:** Detect degradation within 300 ms of packet loss or rising retransmits; emit a local LED/button state immediately. For a compact intent, acknowledge within 1 s when possible. Queue delivery may take until coverage returns, with no promise of execution before that.
- **cost:** Near-zero additional model cost for clearly recognized commands; modest relay storage and LTE bytes. Ambiguous or novel speech may incur one normal realtime turn after reconnection.
- **security:** The compact envelope must be authenticated, replay-protected, encrypted, and bound to a session/device nonce. Never silently execute a stale command after a long outage; include creation time and a spoken/LED expiration status. Browser or Mac credentials stay on their existing surfaces.
- **missing:** A pendant/relay transport mode negotiation with sequence numbers, resumable chunks, and an authenticated compact-intent envelope; A small on-device or relay recognizer for a constrained emergency vocabulary plus an explicit 'raw audio pending' fallback; Durable-but-expiring relay storage and reconnect delivery acknowledgements; Mac/browser consumers that accept the envelope and return a typed execution receipt


## Changes it proposed to its own stack

### `integration` — Add an end-to-end audio calibration and telemetry sanity-check pipeline. The relay can initiate a calibration probe; the pendant reports capture clock/format; the Mac reports playback format; the system compares and stores a calibration profile used to resample correctly and detect drift.
- **owner gets:** Voice quality improves and weird audio bugs (chipmunk/slow playback, truncation) can be detected and corrected automatically, reducing frustration and miscommunication.
- effort: Medium to high: requires firmware telemetry, relay validation, and storage of calibration state. Some pieces exist (telemetry), but it needs a coordinated flow.  ·  risk: Bad calibration could degrade audio. Mitigate with rollback to defaults and periodic re-checks.
- cost: Low per run; occasional calibration costs more but is still small. Development effort is the main cost.  ·  latency: Calibration is offline/maintenance; normal conversations get better reliability without added delay.
- security: Telemetry includes device characteristics; store minimal and protect access.
- depends on: Pendant telemetry schema for clock and sample rate; Storage for calibration profile; A route to trigger calibration and retrieve results


## What it asked for

_Nothing._
## Its own summary

Recorded two new owner-facing capabilities: (1) automatic end-to-end audio clock calibration and drift correction so the worn voice link remains intelligible despite the observed 15,625 Hz versus 24,000 Hz mismatch; (2) LTE-M degraded-mode delivery that preserves compact, authenticated command intent through weak coverage and returns an honest execution receipt. Both require new pendant/relay transport or telemetry work plus integration across the existing pipeline, Mac planner, and browser surfaces.

**Biggest unknown:** Whether the existing relay actually has a media resampler, durable expiring queue, or authenticated reconnect envelope hidden behind routes that have not been inventoried; the owner explicitly ended discovery this round, so those should be checked before implementation rather than assumed absent.

