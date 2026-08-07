# Harness derivation — mac-planner — round 30

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **24 kHz conversational audio reliability** — Current path is already 24 kHz Opus decode but runs ~87% of one core when encode+decode overlap; LTE-M contention has measured 388 dropped uplink packets (~7.8 seconds), while the Mac pipeline already receives pendant offline-store alert events. This makes sequence-aware QoS and repair the immediate cross-node gap.
  - evidence: get_hardware_spec(all): audio and network measurements; GET /pipeline 200 showed source nrf9160 event alert_delivered with storage microSD and origin pendant-offline-store.

## Capabilities it proposed

### "“Keep the conversation intact even when the cellular link is struggling—prioritize my speech, recover anything that was lost, and tell me plainly if something could not be recovered.”"
- **useful because:** Today the owner can lose many seconds of speech when LTE-M contention occurs while agent audio is playing, and the existing offline-store alerts do not guarantee that the missing audio is reassembled into the conversation. This would make a dropped link a bounded interruption rather than silent loss, while preserving smooth 24 kHz playback when conditions are good.
- **path:** pendant firmware → relay-realtime → ESP32 audio bridge → Mac local agent → dashboard
- **model tier:** gpt-realtime for live loss-policy decisions and concise spoken status; background relay workers for de-duplication, replay assembly, and receipts; no expensive model needed for packet repair.
- **latency:** Under 100 ms added latency on a healthy call; under 250 ms when loss control activates. A recovery receipt should arrive within 10 seconds of reconnecting, without blocking the next conversation.
- **cost:** Negligible model cost beyond the existing realtime call; roughly 10–20% extra LTE bytes only during detected loss, plus bounded SD writes and a small amount of relay storage/compute. Hardware revision would be a one-time prototype cost rather than per-invocation cost.
- **security:** Audio chunks and recovery manifests must stay encrypted in transit and at rest, use opaque call IDs, and be deleted after acknowledgment or a short TTL. The owner should hear only a brief recovery status by default; transcripts or replayed audio require an explicit request. Never claim success when sequence ranges remain missing.
- **missing:** A versioned frame envelope with call ID, sequence, timestamp, and loss-window acknowledgment shared by pendant and relay; A relay jitter/replay service that is idempotent across reconnects and can distinguish recovered, duplicated, and irrecoverable ranges; Firmware support for bounded encrypted SD failure manifests and adaptive speech-first bitrate/FEC modes; ESP32 bridge underrun/clock-health telemetry and a dashboard receipt that summarizes recovery without exposing raw audio; A wearable hardware revision with enough audio/PSRAM headroom and a fuel gauge if firmware-only contention control cannot meet the latency target


## Changes it proposed to its own stack

### `firmware` — Ship an end-to-end conversational audio QoS/repair protocol for the 24 kHz path. The pendant stamps every 60 ms Opus frame with call/sequence/timestamp and a rolling loss window; the relay measures uplink/downlink contention and sends compact control frames that switch among speech-protection modes (pause/downsample agent audio, lower Opus bitrate/complexity, or interleave a bounded FEC frame). Missing uplink sequences are NACKed while the pendant is still online; if LTE disappears, the pendant writes only the affected encrypted chunks plus a manifest to its existing microSD failure buffer. On reconnect the relay de-duplicates/reorders/re-encodes and emits a completion receipt; the Mac bridge reports actual Bluetooth underruns and the Mac dashboard shows one human-readable 'speech recovered / irrecoverable' result rather than raw packet counts.
- **owner gets:** The owner can speak while the agent is talking without losing nearly eight seconds of their words, and a dropped connection becomes a recoverable pause instead of a broken conversation. 24 kHz playback remains intelligible on the existing headphones while the system automatically protects speech when LTE-M is congested.
- effort: Medium-high: define a small binary control/sequence protocol; implement fixed-point loss-window accounting and bounded replay in the nRF9160; add relay jitter buffer/FEC policy and idempotent SD-manifest ingestion; instrument the ESP32 A2DP bridge for underrun counters; add a dashboard receipt and integration tests that replay the observed 388-drop trace.  ·  risk: Extra buffering can increase conversational latency and SD wear; FEC consumes LTE airtime and RAM. Bound replay to one call and a small byte budget, prefer dropping agent playback before owner uplink, expire encrypted recovery chunks after successful receipt, and fall back to today's codec path if control frames are unsupported. Never silently claim recovery: expose missing sequence ranges in the receipt.
- cost: Negligible model cost; modest LTE overhead only when loss is detected (roughly 10–20% FEC/control overhead), plus small firmware/relay CPU and bounded microSD writes.  ·  latency: Healthy calls add under one frame of jitter; loss mode may add 60–180 ms for repair, while agent playback is deliberately ducked/paused under contention.
- security: Audio recovery chunks remain encrypted at rest and transit; manifests contain opaque IDs and sequence ranges, with deletion after acknowledgment. Dashboard should show metadata by default, not audio or transcript.
- depends on: A stable audio frame envelope shared by nRF9160, Cloudflare relay, and ESP32 bridge; A relay-side idempotent audio-ingest/receipt store; Bridge firmware counter export and a dashboard pipeline receipt view

### `hardware` — For the wearable revision, split modem and audio duties instead of pushing both Opus directions through the nRF9160: use an nRF5340 audio MCU (or equivalent Cortex-M33 with I2S/DMA and DSP headroom) beside the cellular modem, add  PSRAM/QSPI RAM for two bounded 24 kHz jitter/recovery rings, and add a real fuel-gauge IC on the currently free I2C bus. Keep the existing ESP32 A2DP bridge as the headphone endpoint, but expose MCU audio-health and battery telemetry to the relay in the same control channel.
- **owner gets:** The pendant can keep listening and playing smooth 24 kHz audio while LTE retransmits or the agent speaks, instead of dropping speech because one 64 MHz core is already near saturation. The owner also gets an honest battery percentage and low-battery behavior, so scheduled briefings do not unexpectedly die.
- effort: High: redesign PCB/power tree and enclosure, port Zephyr audio and modem IPC, qualify I2S clocking and RF coexistence, add fuel-gauge calibration, and run long LTE-plus-A2DP soak tests. Prototype first as a two-board wearable harness before committing to a board spin.  ·  risk: More components and a second firmware boundary increase size, power and failure modes; clock drift or IPC bugs could produce audio glitches. Keep the nRF9160 as a fail-safe voice path, use watchdog-supervised MCU IPC, and degrade to 16 kHz/half-duplex on thermal or battery limits.
- cost: Rough prototype delta $25–$60 per unit (audio MCU, PSRAM, fuel gauge, PCB/power changes); likely 20–60 mA additional active draw depending on MCU clock, but lower nRF9160 duty cycle may recover part of it. No per-call API cost.  ·  latency: Can remove the current 25 ms decode contention and shrink jitter buffering; target <100 ms healthy end-to-end and bounded repair delay under loss.
- security: Fuel-gauge data is low sensitivity. Audio remains encrypted; inter-MCU audio/control transport must use authenticated framing and erase buffers on call end.
- depends on: Measured current draw and thermal envelope of the chosen enclosure/battery; A versioned inter-MCU audio/control protocol (including the QoS proposal); A production wearable PCB and regulatory/RF review


## What it asked for

_Nothing._
## Its own summary

Round 30 produced two new, owner-facing proposals: (1) an end-to-end 24 kHz audio QoS/repair protocol spanning pendant sequence tags and SD failure buffering, relay loss control and idempotent recovery, ESP32 underrun telemetry, and Mac/dashboard receipts; (2) a wearable hardware revision that separates modem/audio workloads, adds bounded PSRAM rings, and finally adds a fuel gauge. Evidence is concrete: the current path reaches ~87% CPU and the measured LTE contention lost 388 uplink packets (~7.8 s), while the pipeline already records pendant offline-store alerts.

**Biggest unknown:** I still need the relay's current codec/loss-control implementation, a way to export ESP32 A2DP underrun counters, and measured pendant battery/thermal/current traces. Those determine whether firmware-only QoS is sufficient or the two-MCU revision is justified; I have asked relay-realtime and mac-vision and will incorporate their replies next round.

