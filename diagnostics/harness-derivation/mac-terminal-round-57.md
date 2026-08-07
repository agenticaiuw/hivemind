# Harness derivation — mac-terminal — round 57

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-link constraint** — Current prototype is asymmetric: pendant captures 15,625 Hz and uploads Opus 16 kHz/16 kbps; playback decodes Opus 24 kHz. LTE-M half-duplex contention already caused 388 lost uplink packets (~7.8 s) while downlink speech was active. The bridge is fixed to 44.1-kHz stereo SBC and has tight buffering.
  - evidence: get_hardware_spec(audio), get_hardware_spec(network), get_hardware_spec(bridge) in round 57

## Capabilities it proposed

### "“Make our live conversations sound wideband when the network allows, but never lose my speech just because we talk over each other.”"
- **useful because:** Today the pendant's LTE-M link can lose many seconds of uplink speech while downlink audio is active. The owner should get clear 24-kHz speech in good conditions and graceful, intelligible degradation under contention instead of silent gaps and having to repeat themselves.
- **path:** pendant → relay-realtime → mac-planner
- **model tier:** Realtime for the live conversation and profile decisions; no extra model call is needed for packet scheduling or quality adaptation.
- **latency:** Profile changes should complete within about 1 second. Add no more than 20–60 ms jitter/FEC buffering during a call.
- **cost:** Negligible incremental inference cost. Network cost rises only during viable 24-kHz uplink periods; engineering cost is dominated by firmware clocking, modem contention, and end-to-end audio testing.
- **security:** Audio remains on the existing encrypted pendant-to-relay channel. Quality telemetry should contain only packet sequence, RTT, queue depth, and loss statistics—not decoded audio. No confirmation is needed for an audio-quality adaptation.
- **missing:** A negotiated audio-profile protocol shared by pendant firmware and relay; nRF9160 full-duplex I2S and Opus support for a 24-kHz capture profile with a reliable fallback to the current contract; Relay congestion control that prioritizes downlink speech, enables FEC/DTX, and switches profiles with hysteresis; Recorded two-way overlap/congestion tests and RF/Bluetooth validation through the ESP32 bridge; Mac-side audio status diagnostics with a working implementation so calls can report the active profile and recoverable failures


## Changes it proposed to its own stack

### `firmware` — Replace the fixed 16-kHz uplink/24-kHz downlink audio contract with a negotiated adaptive superwideband profile. The pendant should capture and Opus-encode at 24 kHz when the LTE-M link has headroom, packetize within the modem's ~2 kB TLS limit, and use Opus in-band FEC/DTX plus a small bounded jitter buffer. A relay-side congestion controller should observe RTT, queue depth, and missing sequence numbers, prioritize downlink speech during overlap, and step the uplink through 24-kHz -> 16-kHz profiles before loss becomes catastrophic; restore 24 kHz after a hysteresis window. Keep the relay transparent (no needless transcode), while the ESP32 bridge resamples the negotiated stream to its fixed 44.1-kHz SBC output.
- **owner gets:** A quiet call can actually sound like the intended 24-kHz superwideband path, but talking over the agent will no longer silently lose roughly eight seconds of the owner's speech on a saturated LTE-M link. Quality degrades briefly and intelligibly instead of failing unpredictably.
- effort: Medium-high: revise nRF9160 I2S/Opus framing and profile negotiation, relay scheduler and metrics, and bridge buffer tests; add an automated overlap/congestion test using recorded audio (no microphone needed).  ·  risk: Changing the full-duplex I2S clock is risky because the single peripheral currently requires byte-identical TX/RX configuration; a bad clock or jitter-buffer bound can cause underruns or silence. Recover with a feature-flagged profile, watchdog fallback to the proven 16/24 contract, and sequence-numbered traces for post-call diagnosis.
- cost: Negligible incremental API cost; modest LTE-M traffic increase only while 24-kHz uplink is viable. Engineering/test cost dominates, especially RF contention and Bluetooth interoperability testing.  ·  latency: Negotiation adds at most one short measurement window; FEC and jitter buffering add roughly 20–60 ms, trading a little latency for far fewer gaps.
- security: No new data class or third party is required. Audio remains in the existing TLS WebSocket; telemetry should contain sequence/timing/loss metadata, never decoded speech.
- depends on: An agreed audio-profile negotiation message shared by pendant firmware and cloud-relay; A safe way to change/test the nRF9160 full-duplex I2S clock and Opus sample-rate configuration; Relay-side packet-loss/RTT instrumentation and an automated two-way congestion test


## What it asked for

_Nothing._
