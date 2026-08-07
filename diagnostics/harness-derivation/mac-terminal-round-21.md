# Harness derivation — mac-terminal — round 21

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-pipeline** — The live system's output side is genuinely 24 kHz mono PCM, but input telemetry is 15.625 kHz PCM and the prototype ESP32 bridge is 31.25 kHz I2S resampled to 44.1 kHz SBC/A2DP. Thus no end-to-end 24 kHz path exists yet; only the Mac TTS hop is 24 kHz.
  - evidence: GET /ops/status and GET /pipeline live responses on 2026-08-07; get_hardware_spec(pendant,bridge,io)

## Capabilities it proposed

### "“Run an audio check.” The pendant should play a short private test phrase, measure the microphone-to-relay-to-Mac-to-headphones path, and tell me exactly whether the problem is capture, LTE transport, speech generation, or headphone playback—then switch to the best compatible audio profile for the next call."
- **useful because:** Today the owner can hear degraded, delayed, or silent audio but cannot identify which node is responsible. This turns an opaque multi-device failure into a one-sentence diagnosis and an automatic recovery choice, without sending the owner's test recording into long-term storage.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Background/diagnostic work should use a cheap deterministic protocol and DSP checks; use the realtime model only to phrase the final spoken result if needed. No expensive model call is needed to detect sample-rate mismatch, packet loss, clipping, underruns, or latency.
- **latency:** The owner should get the diagnosis in under 5 seconds. A normal conversation must not pause unless the owner explicitly asks for the check.
- **cost:** Negligible API cost: one small marked test burst and compact telemetry. The dominant cost is engineering the shared test protocol and implementing bounded DSP counters on the pendant and bridge.
- **security:** Use a synthetic tone or locally generated phrase rather than uploading live microphone content. Persist only aggregate measurements and an expiring correlation ID. Switching profiles must be limited to known-safe audio settings; do not change Bluetooth pairing or transmit recordings without confirmation.
- **missing:** A versioned diagnostic protocol understood by the nRF9160, Cloudflare relay, Mac bridge, and ESP32 or replacement audio bridge; Firmware counters for I²S overruns/underruns, Opus loss, clock drift, and playback completion; A relay job that correlates capture, upload, TTS generation, download, and playback timestamps; A small dashboard or spoken-result formatter that maps measurements to actionable diagnoses and records the selected fallback profile; A production audio bridge capable of reporting its actual A2DP sample rate instead of exposing only the current 31.25-to-44.1 kHz prototype path

### "“Use the best audio quality available for these headphones.” The pendant should negotiate and remember a per-headphone profile, preserving the network's 24 kHz speech quality until the final Bluetooth boundary, selecting 44.1 or 48 kHz only when required, and fall back safely when the headphones reconnect or change."
- **useful because:** The owner should not have to understand that LTE speech, I²S clocks, and A2DP have different sample-rate contracts. Today the prototype silently resamples through a fixed 31.25-to-44.1 kHz path and gives no indication whether a connected headset can do better. This would make every headset sound as good and as reliably as it can.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Use deterministic capability negotiation and DSP configuration, not an LLM. The realtime model is unnecessary; a cheap background planner may explain an incompatibility only when one occurs.
- **latency:** Profile selection should complete within 1 second of headphone connection and add no more than 10 ms to normal playback. Reconnection should automatically reuse the last known-good profile.
- **cost:** Near-zero per-use API cost. Engineering cost is concentrated in Bluetooth capability discovery, clock configuration, and profile persistence; hardware redesign may dominate if the current ESP32 A2DP source cannot expose the required controls.
- **security:** Store only a non-secret headphone identifier, supported codec/rate profile, and health counters. Pairing keys remain on the bridge. Never upload Bluetooth identifiers or audio samples to the relay unless the owner enables diagnostics.
- **missing:** Bluetooth source capability discovery and per-device profile storage; A bridge implementation with selectable 44.1/48 kHz output and observable actual clock rate; A canonical distinction between 24 kHz relay PCM and the final Bluetooth output rate; A pendant/bridge reconnect handshake that rejects stale profiles and reports fallback reasons; Hardware or firmware replacement for the current HUZZAH32 precompiled 44.1 kHz-only path if it cannot support negotiated output


## Changes it proposed to its own stack

### `integration` — Add a cross-layer 24 kHz audio conformance/loopback harness. The Mac bridge emits a short marked PCM/Opus test burst; relay and pendant preserve a correlation ID plus declared sample rate, codec, frame duration, byte count, and timestamps at capture/upload/decode/playback. The pendant returns periodic counters (underruns, overruns, resampler ratio, dropped frames, CRC) via existing pipeline telemetry. A CI/live diagnostic compares the declared and measured rates and fails loudly on any implicit 15.625/31.25/44.1 kHz conversion. Keep the current 24 kHz TTS output but make the capture and ESP32 bridge mismatch explicit until they are migrated.
- **owner gets:** The owner gets speech that sounds consistently natural instead of discovering weeks later that capture is 15.625 kHz and the bridge silently converts through 31.25/44.1 kHz. When audio breaks, the pendant can say which hop lost samples, rather than requiring UART archaeology.
- effort: Medium: shared telemetry schema in relay/Mac bridge, a small nRF9160 counter packet, ESP32 instrumentation, and a host loopback test. No new pendant peripheral; use the existing full-duplex I2S and pipeline event path.  ·  risk: Telemetry overhead and test bursts could contend with live audio; gate tests to explicit diagnostics and keep counters compact. A false alarm from clock drift is recovered by thresholding over a full burst and reporting raw counters. No audio payload needs to leave the owner's devices beyond the existing relay path.
- cost: Negligible API cost; one small diagnostic burst and a few hundred bytes of telemetry. Firmware RAM under ~8 KiB for counters/ring metadata if kept out of the audio buffers.  ·  latency: No live-path latency change; diagnostic mode adds one test-burst round trip, roughly under a second on LTE.
- security: Correlation IDs and aggregate counters only; do not persist microphone samples. Mark diagnostic payloads separately from owner audio and expire them quickly.
- depends on: A canonical audio telemetry schema shared by relay, Mac bridge, nRF9160, and ESP32; A firmware build/test runner or connected-device test target; A documented migration plan for 24 kHz capture and the ESP32 A2DP 44.1 kHz limitation

### `hardware` — Replace the prototype HUZZAH32 bridge's 31.25→44.1 kHz path with a production Bluetooth-audio bridge that runs one explicit 24→48 kHz conversion (or 24→44.1 only at the final A2DP boundary), has hardware I2S clocking, and exposes underrun/clock telemetry. Keep the nRF9160's 24 kHz PCM/Opus contract across LTE; the bridge should not pretend A2DP can carry 24 kHz—A2DP remains a 44.1/48 kHz headphone boundary.
- **owner gets:** The owner hears clean, stable responses and recordings instead of audio whose pitch/latency changes when the current development bridge's 31.25 kHz clock and 44.1 kHz SBC path drift. It also makes 24 kHz quality real through the network while honestly handling the unavoidable headphone conversion once.
- effort: Medium hardware redesign: select a Bluetooth-audio SoC/module with documented 48 kHz I2S and source profile, add clocked I2S and power/charging, port the existing bridge protocol, then certify with the conformance harness.  ·  risk: Headphone interoperability may force 44.1 kHz fallback; retain both 44.1/48 profiles and a deterministic resampler. Module replacement can introduce pairing regressions; recover with the existing ESP32 bridge during bring-up. Physical redesign is required because the HUZZAH32 prototype is not a shippable product.
- cost: Prototype module/BOM roughly $15–$40 plus board work; production power target under ~100 mA active, versus the current ESP32 board's higher dev-board draw. No meaningful per-call API cost.  ·  latency: Removes one unnecessary resampling stage and should reduce jitter; conversion itself adds under 2 ms with a bounded small buffer.
- security: Audio remains local between pendant and headphones after relay delivery; pairing keys must be stored in protected flash and diagnostic telemetry must exclude samples.
- depends on: Cross-layer audio conformance telemetry; A product decision whether headphones remain A2DP or move to LE Audio; A validated 24 kHz capture/Opus profile on the nRF9160


## What it asked for

_Nothing._
## Its own summary

Recorded two new, non-backlog capabilities: an owner-invoked end-to-end audio diagnostic that identifies the failing hop and selects a safe fallback, and automatic per-headphone audio-profile negotiation that preserves 24 kHz quality until the unavoidable Bluetooth boundary. Both require coordinated pendant, relay, Mac bridge, and audio-bridge protocol/firmware changes.

**Biggest unknown:** The actual firmware source/build and connected-device state remain uninspectable because the granted read-only shell interface has no implementation.

