# Harness derivation — unified — round 4

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent liveness and control readiness** — Mac local agent v0.5.0 is live at localhost:8000; relay and Mac bridge are reachable. Required permissions are still reported missing: Accessibility and Screen Recording, so full-control readiness is false.
  - evidence: GET /ops/status returned ok=true, version 0.5.0, relay.reachable=true, permissions.accessibility.trusted=false, screenRecording.granted=false, ready=false.
- **Browser bridge availability** — Authenticated browser bridge is currently offline with no devices and 5 pending commands; browser account/page tasks cannot be executed now.
  - evidence: GET /browser/status returned {"online":false,"devices":[],"pendingCommands":5}; GET /ops/status agrees.
- **Audio pipeline evidence** — The Mac pipeline has successfully rendered 24 kHz mono s16le PCM for pendant playback (160.8 KiB, 3.43 s, no clipping), and relay accepted it; however current stored runs include processing/stale entries and do not establish end-to-end acoustic acceptance.
  - evidence: GET /pipeline returned a completed cloud-relay run with TTS metadata sampleRate 24000, channels 1, pcmBytes 164650, clippedSamples 0, and relay_result status done.
- **Pendant physical status and limits** — Pendant is a prototype nRF9160 DK with one I2S full-duplex peripheral, 15.625 kHz mic capture, 24 kHz Opus decode/resampling to 31.25 kHz I2S, and LTE-M half-duplex contention; no battery gauge exists. Current telemetry proves rendered 24 kHz PCM, not speaker/acoustic correctness.
  - evidence: get_hardware_spec(all) reports prototype status, single shared I2S, audio rates, LTE-M packet-loss contention (388 uplink packets dropped), and power.no fuel gauge driver.

## What it asked for

_Nothing._
## Its own summary

Recon complete. The Mac agent is live (v0.5.0), relay reachable, and the Mac bridge is online. Current evidence: Accessibility and Screen Recording are still false and overall readiness is false; browser bridge is offline with 5 pending commands; computer-use loop is disabled. The pipeline has rendered and relayed 24 kHz mono PCM successfully (3.43 s, no clipped samples), but this does not prove end-to-end pendant speaker/acoustic acceptance. Hardware is a prototype nRF9160 DK: one shared full-duplex I2S, 15.625 kHz mic, 24 kHz Opus playback resampled to 31.25 kHz, LTE-M contention, and no battery gauge. Still needed for useful work: (1) make the granted macOS Accessibility/Screen Recording permissions actually visible to the AI Pendant Agent process (or reconcile the grant/status discrepancy), (2) bring the browser bridge online if private web tasks are required, and (3) provide/enable the already-requested workspace-edit and audio-pipeline-validation capabilities plus the pending 24 kHz acceptance criteria so the audio path can be changed and objectively validated. No side-effecting actions were performed.

**Biggest unknown:** Whether the orchestrator's permission grants were applied to the running AI Pendant Agent process; live /ops/status still reports both missing.

