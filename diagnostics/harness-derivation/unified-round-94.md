# Harness derivation — unified — round 94

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before answering me, make sure the pendant-to-headphones audio path is healthy; if it is not, quietly repair or switch to a safe fallback and tell me what happened."
- **useful because:** Today the relay can accept a 24 kHz PCM response while the pendant, LTE-M half-duplex link, I2S clock, ESP32 resampler, and SBC Bluetooth bridge each have independent failure modes. A short negotiated preflight would prevent the owner from hearing silence or a clipped answer, and would produce a concrete receipt instead of making them repeat themselves.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** No expensive model for the preflight: deterministic firmware/bridge DSP and relay telemetry. Use the realtime tier only for the actual conversation; use a cheap background model only to summarize repeated faults in a daily report.
- **latency:** <=250 ms for a cached health check; <=2 s only when a calibration chirp and round trip are required. Never delay an urgent spoken response more than one check interval; fall back to a short local tone/LED plus dashboard text.
- **cost:** Near-zero API cost; roughly 1–3 KB telemetry per check and one 20–100 KB test PCM/Opus exchange when calibration is needed. Engineering cost is firmware, ESP32 bridge, and relay protocol work.
- **security:** Test audio must be synthetic and contain no microphone content. Telemetry should contain only counters, codec/clock parameters, and opaque job IDs. Do not upload owner speech merely to test playback. Any automatic fallback must be reversible and must not change Bluetooth pairings without confirmation.
- **missing:** A pendant-local audio preflight/calibration skill that can emit a synthetic frame and report I2S underruns, LTE loss, decode time, and playback acknowledgement; ESP32 bridge telemetry for FIFO starvation, resampler lock, A2DP connection state, and SBC enqueue latency; A relay endpoint that correlates preflight telemetry with the exact response job and records a delivery receipt; A typed Mac/dashboard health result and fallback policy (retry, text-only, or local alert)

### "Always deliver your reply through the best output I currently have—my paired headphones, the pendant, or my Mac—and switch safely if one disappears, without making me repeat the request."
- **useful because:** Today a response can be accepted by the relay yet become inaudible when the Bluetooth bridge, headphones, LTE-M path, or pendant playback fails. A coordinated output handoff would let the owner keep using the assistant while moving between desk, headphones, and pendant, with one concise receipt naming the actual output.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic capability negotiation and health scoring should do the routing; use the realtime model only to phrase the final spoken response, never to decide transport health. A cheap background model may summarize recurring device failures.
- **latency:** Use cached health in under 100 ms; perform a one-time probe within 1 s after a route change. Fallback must happen within 2 s and preserve the already-generated response, not regenerate it.
- **cost:** Negligible model cost; approximately 1–5 KB of device telemetry per route decision and no duplicate TTS unless the selected output format requires it. Main cost is bridge/firmware and Mac audio-route integration.
- **security:** Respect the owner's privacy boundary: never route private content to an untrusted room speaker without an explicit policy. Store only output capability, connection state, and opaque response IDs. Bluetooth pairing and Mac audio controls remain local; changing a pairing or sending audio to a new device requires confirmation.
- **missing:** A shared output capability/health contract covering pendant speaker path, ESP32 Bluetooth state, and Mac audio devices; A relay response object that can be fetched and replayed in alternate formats without re-running the model; Mac bridge support to enumerate and select an already-authorized audio output; Pendant and bridge playback acknowledgements with nonce and response ID


## Changes it proposed to its own stack

### `firmware` — Add a deterministic audio-path preflight protocol spanning nRF9160 firmware and the ESP32 bridge: the pendant sends a synthetic nonce-tagged 24 kHz test burst, the bridge reports I2S FIFO depth, resampler phase-lock, A2DP enqueue/connection state, and a playback acknowledgement, while the pendant records modem loss, Opus decode headroom, and underruns. Gate response playback on the result, with bounded retry and a local tone/LED fallback; persist only compact counters and the last receipt on the SD failure buffer.
- **owner gets:** The owner gets an answer they can actually hear instead of silent or late audio, and a truthful one-sentence explanation when headphones, LTE-M, or the bridge are unhealthy. It also turns today's opaque 'response waiting for pendant' state into a diagnosable delivery result.
- effort: Medium: a small framed control message and state machine in nRF9160, bridge telemetry/ack in ESP32, and relay correlation. Requires bench tests across Bluetooth reconnects, modem contention, and dropped packets.  ·  risk: A false negative could delay speech; cap the check at 2 seconds, allow one retry, then deliver text/dashboard status and a distinctive local alert. A stale acknowledgement must be rejected by nonce and job ID. Roll back by disabling the gate and returning to current playback.
- cost: No per-call model cost. A few KB of control telemetry; likely 1–2 weeks firmware/bridge work. No hardware cost unless later measurements show the fixed A2DP buffer needs external RAM.  ·  latency: Normally <250 ms from cached state; calibration path adds up to 2 s only after reconnect, repeated underruns, or a codec/clock change.
- security: Synthetic audio only; do not transmit microphone samples. Nonces/job IDs prevent replay. Store no owner speech in the diagnostic record.
- depends on: An agreed 24 kHz PCM/Opus delivery receipt schema; ESP32 bridge state/latency counters exposed to the pendant; Relay persistence linking /pipeline/audio and /pipeline/events to one response job

### `hardware` — Replace the prototype ESP32 HUZZAH32 Bluetooth bridge's fixed, RAM-starved audio path with a production bridge module that has a hardware audio clock domain/converter, reserved DMA/I2S buffers, and at least 2 MB external PSRAM, while exposing FIFO/clock/A2DP acknowledgements to the nRF9160. Keep the existing 44.1 kHz SBC Bluetooth compatibility at the radio boundary, but make the 24 kHz pendant stream a first-class clock domain rather than relying on an opaque 31.25 kHz software-resample chain.
- **owner gets:** The owner should be able to wear ordinary Bluetooth headphones and hear every response clearly, without intermittent silence, clipping, or speech arriving late when the pendant is also listening. It gives the system enough observability to distinguish a bad headphone link from an LTE or pendant fault instead of asking the owner to repeat themselves.
- effort: High: select and prototype a bridge SoM/audio interface, write clock/DMA and telemetry firmware, validate SBC interoperability across headphone models, and integrate it with the pendant preflight receipt. This is a product-hardware revision, not a patch to the DK prototype.  ·  risk: New Bluetooth silicon or clocking can introduce pairing regressions and RF/power issues. Keep the current ESP32 bridge as a fallback during validation, gate rollout by bridge capability/version, and retain a wired bench-test mode for recovery.
- cost: Approximately $8–$20 incremental prototype BOM (SoM, PSRAM, clock/audio components) and roughly 100–250 mW additional bridge peak draw; no per-invocation model cost.  ·  latency: Removes software resampler jitter and should reduce playback startup/underrun latency by tens of milliseconds; preflight may still add up to 2 seconds only after reconnect or a detected fault.
- security: No new speech data needs to leave the pendant. The bridge should expose only counters, capability/version, and opaque job/nonce acknowledgements; Bluetooth pairing keys remain device-local.
- depends on: The new audio_path_preflight_receipt pendant skill; A versioned bridge telemetry and playback-acknowledgement protocol; End-to-end 24 kHz audio acceptance tests across LTE-M contention and Bluetooth reconnects


## What it asked for

### `s11-03b3` (skill) — audio_path_preflight_receipt
- does: On reconnect, before a response marked audio-critical, emits a nonce-tagged synthetic test frame, observes modem send/receive, Opus decode timing, I2S underruns, and bridge acknowledgement, then returns a compact HEALTHY/DEGRADED/FAILED receipt with retry/fallback recommendation. It never records or uploads microphone content.
- must be on-device because: Only the pendant can observe its real I2S FIFO/decode headroom and survive a dropped LTE link; the ESP32 bridge acknowledgement must be correlated locally before the relay claims delivery.
- trigger: Server push before playback, Bluetooth/link reconnect event, or a button-triggered diagnostic; automatically rate-limit to once per reconnect or after two consecutive playback faults.
- storage: Last receipt plus rolling counters and a bounded failure record on the existing SD failure buffer; under 8 KB total, deleted after successful upload/receipt according to the audio retention policy.
- RAM budget: About 6–10 KB: one synthetic 60 ms PCM/Opus test frame, framed telemetry, nonce state, and a tiny ring of counters. No second audio stream or large buffer; fits within 211,608 B application RAM but must be budgeted against the current ~87% single-core audio load.

## Its own summary

Discovered the live system still has an offline browser extension with 9 pending commands, while the Mac bridge is online. The pipeline already renders 24 kHz mono PCM and accepts it for pendant playback, but hardware evidence shows the real weak points are LTE-M contention, 24 kHz→31.25 kHz I2S conversion, ESP32 resampling/A2DP buffering, and no end-to-end delivery acknowledgement. I recorded a new cross-node capability: a synthetic, nonce-correlated audio preflight that gates playback, retries once, and falls back with a truthful receipt. I also proposed the firmware state machine and queued the pendant-local skill (s11-03b3), sized at 6–10 KB RAM and no microphone data.

**Biggest unknown:** The actual ESP32 bridge and pendant firmware telemetry interfaces do not yet expose FIFO starvation, A2DP enqueue latency, clock-lock state, or a playback acknowledgement. I still need those interfaces plus the agreed 24 kHz delivery-receipt schema and fallback policy before this can be implemented safely.

