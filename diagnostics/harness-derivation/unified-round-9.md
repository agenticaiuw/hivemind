# Harness derivation — unified — round 9

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent** — Local Mac agent v0.5.0 is live on localhost:8000; authenticated routes require Bearer token, while /health and dashboard are public. It exposes 120 routes across execution, browser, pipeline, research, routines, memory, evidence, and watches.
  - evidence: GET /capabilities returned 200 with version 0.5.0, routeCount 120, auth scheme Bearer, and route groups.
- **mac-readiness** — Mac bridge and browser extension are online, but agent readiness is false because Accessibility is not trusted and Screen Recording is not granted; computer-use loop is disabled and vision upload consent is false. Automation grants are cached and requiredMissing is empty, so direct AppleScript paths may work while GUI/vision paths remain blocked.
  - evidence: GET /ops/status returned permissions.accessibility.trusted=false, screenRecording.granted=false, computerUse.loopEnabled=false, visionUploadConsented=false, ready=false; browser/status showed extension online with 0 pending commands.
- **audio-path** — Current prototype audio path captures at 15,625 Hz I2S, Opus uplink 16 kHz/16 kbps, decodes at 24 kHz in 60 ms frames, then resamples to 31,250 Hz I2S wire clock; ESP32 bridge resamples 31,250→44,100 and emits SBC-only A2DP. Thus it is not a native 24 kHz superwideband end-to-end path.
  - evidence: get_hardware_spec(audio) reported mic 15,625 Hz capture, Opus 16 kHz uplink, 24 kHz decode, 31,250 Hz wire; get_hardware_spec(bridge) reported 31,250→44,100 and SBC-only 44.1 kHz A2DP.
- **relay** — Cloud relay is configured and reachable, with pairing required, D1 persistence, speech-to-text, durable audio, and pendant pipeline telemetry; Mac bridge was last seen online at 2026-08-07T08:44:33.739Z.
  - evidence: GET /ops/status relay payload returned configured=true, reachable=true, pairingRequired=true, capabilities for pendantPipelineTelemetry, pendantSpeech, persistentAgentState, durableAudio.
- **pipeline-history** — Pipeline telemetry includes live/recent runs and confirms Mac TTS output is 24 kHz mono PCM; one recent response was 164,650 PCM bytes / 3.43 s, with no clipping. Input telemetry for a run showed 15,625 Hz mono PCM capture.
  - evidence: GET /pipeline returned events with inputTelemetry sampleRate=15625 and TTS metadata sampleRate=24000, channels=1, clippedSamples=0.
- **browser** — Browser extension is online but currently reports no attached tab/window (tabId/windowId null, empty URL/title, tabCount null); private logged-in page work therefore needs an attached/usable tab session.
  - evidence: GET /browser/status returned online=true with extensionId fanout-probe-cleanup and null tab/window metadata.
- **project** — Active project is AI Pendant Simulator at /Users/evanliu/agentic-gadget/software/ai-pendant-simulator with workspace ~/AI-Pendant-Workspace; stated goals are reliable voice interaction, LLM-first Mac planning, and smarter multi-tier context memory.
  - evidence: GET /projects/active returned project path, workspacePath, summary, and goals.
- **network-risk** — LTE-M uplink/downlink contention is a demonstrated audio reliability problem: 16 kbps uplink plus 24 kbps downlink saturated the half-duplex link and dropped 388 uplink packets (~7.8 s speech) during simultaneous playback.
  - evidence: get_hardware_spec(network) measured packet loss in diagnostics/nrf-uart-latest.log.
- **pendant-storage** — microSD is a failure buffer only: audio is written there when upload cannot proceed, with FATFS/exFAT support. Audio retention policy on relay is 30 days with sweeper disabled and about 100 recordings stored.
  - evidence: get_hardware_spec(storage) and get_hardware_spec(stack) returned SD policy and relay retention state.
- **pendant-power** — Pendant has USB/battery power but no fuel-gauge driver, so charge state cannot currently be read; LTE-M transmit bursts are the dominant high-power event.
  - evidence: get_hardware_spec(power) returned no battery gauge wired.
- **i2s-constraint** — nRF9160 design has exactly one full-duplex I2S peripheral with byte-identical TX/RX configuration; any revised audio path must share it. GPIO/I2C/SPI are enabled, but I2C/SPI have no attached devices.
  - evidence: get_hardware_spec(io) returned one I2S peripheral and free I2C/SPI.

## What it asked for

### `c2-tlpu` (context) — 24 kHz audio target architecture
- why: Current measured path cannot be native 24 kHz end-to-end: nRF capture is 15.625 kHz, uplink Opus is 16 kHz, bridge is fixed SBC 44.1 kHz, and LTE contention drops speech packets. I need to know whether this round should optimize the existing prototype or specify a product-level hardware/codec redesign.
- would change: If product redesign is intended, I will prioritize an architecture/acceptance plan (mic/codec, transport bitrate, bridge replacement, clocks, latency, packet-loss behavior). If prototype-only is intended, I will constrain work to firmware/relay resampling and measurable pipeline validation within the existing I2S and LTE limits.

## Its own summary

Recon complete. The Mac agent is live (v0.5.0, 120 authenticated routes), relay and Mac bridge are reachable, and the browser extension is online but unattached to any tab. The agent is not ready for GUI/vision automation: Accessibility is untrusted, Screen Recording is missing, computer-use loop is disabled, and vision upload consent is false. The audio prototype is not native 24 kHz SWB end-to-end: capture 15.625 kHz, uplink Opus 16 kHz/16 kbps, decode 24 kHz, nRF I2S 31.25 kHz, ESP32 resample to 44.1 kHz SBC A2DP. LTE-M contention has measured loss of 388 uplink packets (~7.8 s speech). The pendant has one full-duplex I2S peripheral, no battery gauge, and microSD only as an offline failure buffer. I recorded all findings and asked the orchestrator to choose prototype optimization versus product-level redesign.

**Biggest unknown:** The exact 24 kHz superwideband acceptance criteria and target architecture remain pending (context request c2-tlpu). Previously requested mac_workspace_edit, audio_pipeline_validate, and Accessibility/Screen Recording grants are still needed for implementation/validation; I did not repeat those requests this round.

