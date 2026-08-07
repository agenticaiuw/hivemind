# Harness derivation — mac-planner — round 96

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac_readonly_inspect implementation** — The newly granted mac_readonly_inspect schema is present but every operation currently returns 'tool was granted a schema but has no implementation yet'; it cannot report running apps, foreground app, accessibility, UI snapshot, browser tabs, or directories this round.
  - evidence: Four live calls to mac_readonly_inspect (running_apps, foreground_app, accessibility_enabled, browser_tabs) all returned the same implementation error.

## Capabilities it proposed

### "When I start talking over the pendant's reply, stop or duck it immediately, understand my interruption as a correction or new request, and continue with the right response without making me repeat myself."
- **useful because:** Today duplex speech can make the owner talk over playback, lose words, or wait through a response that is no longer relevant. This would make the pendant feel conversational rather than like a walkie-talkie: the owner's intent wins within one speech turn, while the interrupted reply remains available for recovery if needed.
- **path:** pendant → relay-realtime → mac-bridge
- **model tier:** Realtime for the live barge-in decision and turn boundary; a cheaper background model may summarize abandoned replies for diagnostics, but must not sit in the hot path.
- **latency:** Local playback duck/pause within 100 ms of a reliable voice-onset signal; relay turn arbitration within 300 ms; resumed answer should begin within 1.5 s after the owner's utterance ends.
- **cost:** Small incremental realtime cost because interruption detection and turn arbitration reuse the active call; roughly one extra short event and possibly a truncated response per interruption. The dominant cost remains audio streaming, not a new model invocation.
- **security:** The pendant must detect voice onset locally and send only control markers until the owner continues speaking; do not open a microphone on the Mac. An interrupted response may contain private content, so retain it only in the existing call receipt policy and expose a local delete control. Never interpret playback leakage as owner speech without confidence and hysteresis.
- **missing:** A local pendant voice-activity/onset detector with echo-awareness against its own speaker output; A duplex turn-control protocol carrying interrupt, duck, resume, and abandon events with sequence numbers; Relay support for cancelling or checkpointing an in-flight realtime response and preventing stale audio packets from playing; Mac TTS/playback cancellation that can stop an audio render without affecting microphone state; A per-call interruption receipt and recovery state machine, including a fallback when onset confidence is low


## Changes it proposed to its own stack

### `integration` — Add a cross-node duplex-audio congestion controller. The pendant periodically emits compact loss/jitter/queue telemetry; the relay combines it with WebSocket backpressure and transcoder load; the Mac bridge contributes current network/CPU availability when present. A shared controller then selects among 24-kHz wideband, 16-kHz speech, packet-duration/FEC presets, and brief downlink suppression, with hysteresis and an explicit reason in the call receipt. It must preserve the owner's speech first, recover to 24 kHz after a stable window, and never make the Mac microphone active.
- **owner gets:** During simultaneous talking and agent playback, the owner currently loses about 7.8 seconds of speech. This would make conversations intelligible instead of silently dropping their words, while returning to the richer 24-kHz sound when the link recovers.
- effort: Medium-high: define a tiny telemetry frame and state machine in firmware, relay-side controller and Opus preset table, bridge health adapter, dashboard diagnostics, and end-to-end impairment tests.  ·  risk: A bad controller could oscillate quality or over-prioritize downlink. Use hysteresis, hard upper bounds, local pendant fallback, and a call receipt showing every mode change. If telemetry stops, fall back to conservative 16-kHz speech rather than disabling audio.
- cost: Negligible model/API cost; a few hundred bytes/minute of telemetry and modest relay CPU. Firmware RAM likely 4–8 kB for telemetry ring/state, plus test effort. No new per-call service expected.  ·  latency: Telemetry adds under one frame of control delay; mode changes take roughly 0.5–2 seconds due to hysteresis. Conservative mode may add a small packetization delay but prevents multi-second speech loss.
- security: Telemetry contains transport health only, not audio or transcript. Keep Mac network metrics local to the relay job, redact device identifiers in receipts, and retain mode history with existing short audio-job retention.
- depends on: A 24-kHz/16-kHz dual-mode codec path on the pendant and relay; A durable per-call audio telemetry/receipt schema; A bridge health endpoint that does not require microphone or screen access; An owner-visible audio quality preference (speech-first default)


## What it asked for

_Nothing._
## Its own summary

Discovered the new grants and live state. Mac local agent is healthy (v0.5.0), but the browser extension is offline with 5 pending commands. The newly granted mac_readonly_inspect tool is only a schema: running_apps, foreground_app, accessibility_enabled, and browser_tabs all return that no implementation exists. I informed mac-vision that current policy is maximum access/no gates, with separate explicit vision-upload consent still advisable. I proposed a new cross-node duplex-audio congestion controller: pendant loss/jitter telemetry + relay backpressure/transcoder load + Mac health choose 24-kHz, 16-kHz, FEC, and packetization modes with hysteresis, protecting speech and recovering wideband quality.

**Biggest unknown:** Whether the owner wants the browser extension reconnected now, and when the granted mac_readonly_inspect implementation will actually ship. The audio controller also needs a product decision on speech-first versus quality-first preference.

