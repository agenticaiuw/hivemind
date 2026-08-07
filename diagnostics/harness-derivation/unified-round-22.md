# Harness derivation — unified — round 22

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-capture-limit** — The present prototype cannot capture true 24 kHz-bandwidth speech: its microphone path is 15,625 Hz capture, while only playback is decoded at 24 kHz and sent to a 31,250 Hz I2S wire clock. A genuine symmetric 24 kHz path requires a higher-rate capture front end or an explicitly asymmetric acceptance target.
  - evidence: get_hardware_spec(audio): mic I2S 15,625 Hz capture; Opus uplink 16 kHz; playback Opus decode 24 kHz / 60 ms and resample to 31,250 Hz I2S.

## Capabilities it proposed

### "“Keep the conversation clear, and tell me if the connection or audio quality is degrading.”"
- **useful because:** The owner should not have to guess whether silence, clipping, or delayed replies is their microphone, LTE-M, the relay, or the speaker. The worn device can measure local capture/playback health, the relay can see transport and decode timing, and the Mac/dashboard can retain a short diagnostic timeline. Together they can automatically stay at 24 kHz when viable, fall back gracefully when necessary, and give one brief spoken explanation instead of silently failing.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** gpt-realtime-2.1 for the live quality decision and one-sentence explanation only; no model call for telemetry thresholds, codec negotiation, or recovery. A cheaper background model may summarize recurring failures later if the owner asks.
- **latency:** Under 100 ms for local telemetry and codec-mode changes; under 300 ms for relay-to-pendant mode negotiation. Spoken warning should be at most one short sentence and should not interrupt an active utterance unless quality is unusable.
- **cost:** Near-zero incremental API cost during healthy sessions because thresholds and negotiation are deterministic. Occasional realtime explanation is a few cents or less per incident; storage is a small bounded event record, not audio.
- **security:** Transport metrics, battery state, and short-lived quality events leave the pendant and may be stored on the relay/Mac. Do not store raw microphone audio for diagnostics by default. The dashboard must redact network identifiers, cap retention, and require confirmation before uploading a diagnostic bundle or sharing it externally.
- **missing:** A versioned audio-session telemetry schema shared by firmware and relay (sample rate, frame sequence, packet loss, jitter, decode/encode duration, underruns, battery, and selected mode).; A real 24 kHz end-to-end acceptance test that exercises capture, relay transcode, decode, I2S playback, and induced LTE loss; the currently documented path is asymmetric (15,625 Hz capture and 24 kHz playback).; A deterministic capability handshake and hysteresis policy for 24 kHz, narrowband fallback, and recovery so mode changes do not oscillate.; A dashboard quality timeline and a relay endpoint for bounded, owner-approved diagnostic export.

### "“When I say private, make sure nothing from this room is sent anywhere, and tell me when it is safe to resume.”"
- **useful because:** Today the owner cannot establish a trustworthy, immediate privacy boundary across a worn microphone, an active relay stream, and work continuing on the Mac/browser. This would provide a physical, understandable privacy state: the pendant cuts or locally buffers capture even if LTE is still connected; the relay revokes the session and rejects late frames; the Mac/browser pauses queued transcription or actions; and resumption requires an explicit spoken or button action. The owner gets a clear local cue and a verifiable receipt rather than hoping mute propagated.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No model for enforcement: firmware and relay use a signed session-state transition. gpt-realtime-2.1 may generate only the short spoken confirmation after the state is verified. Background models are not involved.
- **latency:** Pendant capture cutoff under 50 ms from the trigger; relay acknowledgement under 500 ms when connected. If disconnected, local privacy state must take effect immediately and remain authoritative until explicit resume.
- **cost:** Negligible inference cost in normal use; a tiny authenticated state event per transition and bounded audit record. Optional later summaries use a cheaper background model, only if requested.
- **security:** This must fail closed: no cloud interpretation of the privacy trigger, no raw audio retention while private, and no automatic resume. Session keys and monotonic counters must prevent replay of stale resume/mute messages. The dashboard should show state and receipt without exposing room audio or precise location. Browser jobs that already caused irreversible external effects cannot be undone, so they must be blocked at the action checkpoint before private mode is acknowledged.
- **missing:** A hardware-local privacy control independent of the network (a long press or dedicated mute switch; the current single button is overloaded with conversation start/end).; A signed, monotonic privacy-state protocol shared by firmware, relay, Mac bridge, and browser job queue, including behavior for in-flight frames and disconnected operation.; A relay-side hard gate that drops audio before transcription/storage and a Mac/browser pause barrier for queued jobs.; A dashboard and spoken receipt that distinguish local mute, relay-confirmed mute, and safe-to-resume; this must be tested with LTE loss, process crash, and reconnect races.


## Changes it proposed to its own stack

### `hardware` — Replace the prototype's 15,625 Hz I2S microphone path with a production audio front end that can capture 48 kHz (or 32 kHz minimum if the acceptance target is explicitly 16 kHz SWB), with clock metadata and a low-power digital mic/ADC. Keep the nRF9160 for LTE-M control, but let the ESP32-class bridge own sustained audio buffering/resampling and expose timestamped PCM frames to the nRF9160. Add a brownout-safe audio power rail and a second status LED or haptic/audio cue for mode/fault indication.
- **owner gets:** The current microphone cannot produce a genuine 24 kHz capture path: 15,625 Hz sampling must be upsampled, so the owner can hear a 24 kHz playback format without receiving 24 kHz speech detail. A proper capture clock plus bridge buffering would make the owner's voice clearer and make the advertised superwideband mode real, while preventing LTE transmit bursts from causing audible dropouts.
- effort: High: select and qualify a digital microphone/audio codec, revise the pendant PCB and power tree, implement DMA/ring buffers and clock synchronization on the ESP32, update nRF9160 framing, and rerun RF/audio coexistence tests. Prototype with the existing HUZZAH32 before committing to a custom board.  ·  risk: Higher peak power and RF coupling may reduce battery life or introduce interference; added clock domains can cause drift and buffer overruns. Recover with a hard 16 kHz compatibility mode, watchdog-supervised bridge reset, and a hardware bypass that preserves the current prototype path during bring-up.
- cost: Prototype engineering plus roughly $8–$25 BOM increase for microphone/codec, regulators, PCB, and haptic/indicator components; likely 10–40 mA additional audio/bridge draw depending on duty cycle. No meaningful per-call API cost.  ·  latency: A 10–20 ms PCM ring buffer and resampling add roughly 10–30 ms; careful DMA scheduling should keep total conversational latency within the existing 60 ms Opus framing budget.
- security: No new external data beyond audio already sent over LTE-M. Firmware images and bridge control must be signed/authenticated; raw PCM should remain in volatile buffers and be wiped on session end.
- depends on: Define and approve the 24 kHz superwideband acceptance criteria.; Implement the shared audio telemetry/capability handshake so the new front end can negotiate safely.; Decide whether 24 kHz applies to capture, playback, or both; the current documented path only guarantees 24 kHz playback.


## What it asked for

### `c4-zq5r` (context) — production pendant constraints beyond the current nRF9160 DK
- why: The current prototype cannot establish whether a real 24 kHz capture path is acceptable on battery, thermals, enclosure, and wearability. I need the owner's actual constraints before recommending a production audio front end rather than a bridge-only workaround.
- would change: With battery life, maximum pendant size/weight, acceptable heat, and target talk-time, I can choose between a higher-rate digital mic on the nRF9160, sustained audio on the ESP32 bridge, or a different low-power audio SoC, and quantify the tradeoff instead of assuming the DK is representative.

## Its own summary

I discovered the prototype's key audio mismatch: capture is 15,625 Hz with 16 kHz uplink, while only playback is 24 kHz. I proposed (1) a cross-surface live audio-quality guardian that negotiates modes, detects packet/codec/underrun problems, and explains degradation briefly; and (2) a production hardware/audio-front-end change capable of genuine higher-rate capture, with the ESP32 bridge handling sustained buffering. I also recorded the capture limitation and asked for production pendant constraints (battery/talk-time, size/weight, heat) so the hardware recommendation can be made honestly.

**Biggest unknown:** The authoritative 24 kHz acceptance definition is still missing: whether 24 kHz applies to capture and uplink as well as playback, plus the production battery, thermal, and enclosure budget. Without that, end-to-end validation and component selection cannot be finalized.

