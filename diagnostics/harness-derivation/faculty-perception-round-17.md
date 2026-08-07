# Harness derivation — faculty-perception — round 17

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac/browser availability** — As of live /ops/status, Mac agent v0.5.0 is healthy and full-control/planner are configured, but computer-use loop is disabled, Accessibility trust is false, vision upload consent is false, and the browser extension is offline with 2 pending commands.
  - evidence: GET /ops/status returned HTTP 200 at this round; fields agent.ok=true, computerUse.loopEnabled=false, accessibility.trusted=false, visionUploadConsented=false, browserExtension.online=false, pendingCommands=2.
- **pendant pipeline state** — The live pipeline includes a pendant-origin run still marked processing whose only recorded event is alert_delivered: 2 held alerts surfaced from microSD offline storage, uptime 323 seconds; this demonstrates offline alert replay occurred but run completion is not established.
  - evidence: GET /pipeline live response showed pipelineId job_27616bb0-ccff-41fb-a752-09d3c6648baa, source nrf9160, status processing, event stage alert_delivered status done, meta.storage microSD, origin pendant-offline-store.
- **current audio topology** — The current prototype is asymmetric: 15,625 Hz I2S capture is Opus-encoded as 16 kHz/16 kbps uplink, while playback decodes Opus at 24 kHz and resamples to a 31,250 Hz I2S wire clock. Encode and decode together consume about 87% of one 64 MHz Cortex-M33 core; the documented status is PROTOTYPE.
  - evidence: get_hardware_spec(audio) live specification: capture 15,625 Hz, uplink 16 kHz/16 kbps, playback 24 kHz→31,250 Hz, libopus encode ~15.0 ms/call and decode ~25.4 ms per 60 ms packet, ~87% one core.
- **Mac agent health** — The Mac local agent is reachable and healthy at version 0.5.0.
  - evidence: GET /health returned HTTP 200 with {ok:true, service:'AI Pendant Mac Local Agent', version:'0.5.0'}.

## Capabilities it proposed

### "When my pendant or Mac reconnects, tell me exactly what happened while it was offline—what was queued, delivered, duplicated, or still unresolved—and give me one concise receipt."
- **useful because:** Today the system can surface held alerts and has pending browser commands, but a processing pipeline state does not tell the owner whether work completed or was replayed twice. A cross-node reconciliation receipt would prevent silent loss and duplicate actions after LTE/browser outages.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background: a cheap structured reconciliation model for normal receipts; realtime only if the owner asks while reconnecting
- **latency:** Generate within 10 seconds of a reconnect event; spoken receipt under 20 seconds and one short sentence by default
- **cost:** Roughly $0.01–$0.05 per reconnect batch; dominated by model synthesis, not metadata collection
- **security:** Private job and browser metadata must remain in the owner's relay/Mac scope; do not export page contents. Require confirmation before retrying any irreversible action. Use event IDs/idempotency keys and explicitly label unknown outcomes rather than infer success.
- **missing:** A shared durable event ledger spanning pendant microSD, relay pipeline, Mac jobs, and browser command queue; Reconnect reconciliation endpoint that correlates event IDs and idempotency keys and marks delivered/duplicate/unknown; Pendant and relay lifecycle events for queue enqueue, forward, acknowledgement, and replay completion; Dashboard/voice receipt renderer with source timestamps and uncertainty labels

### "Check whether my pendant audio is actually good right now, and tell me in one sentence whether you can hear me clearly and I can hear you clearly."
- **useful because:** Today the owner can be told that a pipeline is processing or that playback is configured for 24 kHz, but cannot obtain a user-facing proof of microphone intelligibility, speaker output, packet loss, clipping, latency, or rate fallbacks. An on-demand self-test would turn hidden audio failures into a clear answer before an important conversation.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Use deterministic firmware/relay measurements and a cheap structured summarizer; reserve realtime only for the spoken request and result.
- **latency:** A 3–5 second guided test and a spoken result within 8 seconds; passive health metrics should be attached to the next normal session without extra delay.
- **cost:** Under $0.01 per test after implementation; dominated by a few diagnostic audio packets and optional summarization.
- **security:** The test should use synthetic tones or an owner-spoken phrase, never retain the recording by default, and delete temporary audio immediately. Require explicit confirmation before uploading diagnostic audio; expose raw measurements and confidence when speech intelligibility cannot be established.
- **missing:** A pendant firmware diagnostic mode that emits a short known test signal, captures a spoken/calibration response, and reports clipping, RMS/SNR, actual I2S and codec rates, and frame timing; A relay test endpoint that measures packet loss, jitter, round-trip latency, and negotiated-rate mismatches without persisting audio; A Mac/dashboard result view that distinguishes measured facts from inferred intelligibility and shows the last successful test timestamp; A safe local abort path so a test cannot unexpectedly transmit private speech


## Changes it proposed to its own stack

### `hardware` — Replace the prototype nRF9160-DK + ESP32 audio chain for the product with a low-power audio front end that natively samples and plays 24 kHz (or 48 kHz with deterministic 2:1 decimation), with DMA-backed I2S and a hardware audio codec; keep the nRF9160 for LTE-M/control and move Opus encode/decode to a companion MCU/DSP. Preserve the SD failure buffer but store packet sequence, capture clock, and codec configuration beside each chunk.
- **owner gets:** The owner's requested 24 kHz superwideband path would be real in both directions instead of today's asymmetric path (15,625 Hz capture → 16 kHz Opus uplink; 24 kHz decode → 31,250 Hz wire playback). Speech would sound consistently wideband, and simultaneous encode/decode would not consume roughly 87% of one Cortex-M33 core.
- effort: High: select codec/DSP and power budget, redesign PCB and audio clocking, implement DMA/clock recovery, update firmware and relay transcoding, then validate RF/audio coexistence and long-run battery behavior.  ·  risk: Clock drift, codec driver bugs, added power draw, and RF/codec integration failures could regress current playback. Recover with a feature flag and retain the existing path as a compatibility mode; packet metadata permits replay and diagnosis.
- cost: Prototype engineering plus roughly $10–$30 BOM increase for codec/DSP, microphone/amp/clock components; likely tens of mW additional active draw, to be measured.  ·  latency: Hardware offload should reduce encode/decode contention and jitter; target end-to-end audio latency unchanged or lower than current 60 ms Opus framing.
- security: No new cloud data required; audio remains packetized as today. A companion MCU adds firmware attack surface and must use signed updates and a constrained control interface.
- depends on: A measurable end-to-end 24 kHz acceptance test covering capture, relay, decode, playback, and dropped-link replay; Current firmware/relay codec configuration and clock telemetry; Product-level power and enclosure requirements

### `integration` — Add an end-to-end audio truth manifest emitted for every session: capture sample rate/clock, Opus input rate and bitrate, relay transcode decisions, playback decode rate, I2S wire rate, frame duration, sequence gaps, and measured encode/decode timing. Have the relay reject or visibly label a session when the negotiated rates cannot satisfy the requested 24 kHz mode, and expose one signed session receipt to the Mac dashboard.
- **owner gets:** The owner can ask for 24 kHz and receive proof of what actually traversed the pendant rather than trusting a configured constant. It makes a clipped, resampled, or fallback call diagnosable from one spoken receipt and prevents a nominal '24 kHz' label hiding 16 kHz capture.
- effort: Medium-high: define versioned manifest schema, add low-overhead firmware and relay counters, persist receipts through reconnects, and add dashboard/voice rendering plus automated mismatch tests.  ·  risk: Telemetry overhead and incorrect clock measurements could create false alarms; keep counters compact, mark estimates versus measured values, and fall back to local logs when the manifest is incomplete.
- cost: Small storage/network overhead (roughly hundreds of bytes/session); low API cost because normal synthesis can use a cheap structured summarizer.  ·  latency: Negligible per packet; receipt generation asynchronous after session or on demand.
- security: Manifest contains operational metadata, not transcript/audio; authenticate it and avoid exposing identifiers or raw recordings beyond the owner's relay scope.
- depends on: A defined 24 kHz contract and fallback policy; Firmware hooks for actual I2S/codec rates and timing; Relay persistence for session receipts


## What it asked for

_Nothing._
## Its own summary

Established and recorded: Mac agent v0.5.0 is healthy, but Accessibility is untrusted, computer-use/vision are disabled, browser extension is offline with 2 pending commands; a pendant-origin pipeline run replayed 2 microSD-held alerts but remains marked processing. Audio is still a documented prototype with asymmetric rates (15,625 Hz capture/16 kHz uplink versus 24 kHz playback) and ~87% Cortex-M33 load. Proposed a cross-node reconnect reconciliation receipt, a product audio hardware/DSP redesign, and an end-to-end audio truth manifest that proves actual rates and fallbacks.

**Biggest unknown:** I still need authoritative live evidence of the current 24 kHz implementation and its acceptance-test result, plus lifecycle/ack events that distinguish the observed alert replay and pending browser commands as completed, duplicated, or unresolved. The outstanding instrumentation/diagnostic access would answer both without relying on status labels.

