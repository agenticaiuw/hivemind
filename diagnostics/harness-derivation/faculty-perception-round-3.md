# Harness derivation — faculty-perception — round 3

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-path** — Current end-to-end playback path is operational at 24 kHz: a recent pipeline run rendered 160.8 KiB, 3430 ms, 24,000 Hz mono PCM with no clipping, and relay accepted it for nRF9160 playback.
  - evidence: GET /pipeline response: pipeline job_165a... events tts done meta {pcmBytes:164650, audioDurationMs:3430, sampleRate:24000, channels:1, clippedSamples:0}; relay_result done says accepted.
- **audio-hardware** — Pendant capture is 15,625 Hz I2S and Opus uplink is 16 kHz/16 kbps; on-device decode is 24 kHz/60 ms frames, resampled to 31,250 Hz I2S wire clock. nRF9160 has 211,608 B app RAM, 1 MB flash, Cortex-M33 64 MHz, fixed-point libopus 1.6.1.
  - evidence: describe(pendant) and describe(audio) hardware discovery responses.
- **network-audio-risk** — LTE-M link is half-duplex in practice; measured simultaneous 16 kbps uplink + 24 kbps downlink contention dropped 388 uplink packets (~7.8 seconds speech) in a recent call.
  - evidence: describe(network) hardware response.
- **bridge-audio** — ESP32 HUZZAH32 bridge receives 31,250 Hz I2S, resamples to 44,100 Hz with polyphase FIR, and outputs SBC-only 44.1 kHz stereo A2DP; a 44 kB buffer previously starved Bluetooth into silence.
  - evidence: describe(bridge) hardware response.
- **mac-live** — Mac agent v0.5.0 is live and relay reachable; relay reports macBridgeOnline true, last seen 2026-08-07T08:50:33.795Z. Browser extension is offline; accessibility and screen recording permissions are missing, while automation grants are cached.
  - evidence: GET /ops/status response.
- **device-fleet** — Reachable devices list has home-macbook-bridge online (mac_bridge), while fanout-probe-cleanup browser and cloudflare-contract-test mobile are offline.
  - evidence: discover(devices) response.
- **mac-readiness** — Mac agent reports tokenConfigured=true, fullControlMode=true, llmPlannerEnabled=true, but ready=false; accessibility.trusted=false and screenRecording.granted=false. Browser extension online=false. This limits GUI/vision automation even though automation app grants are cached.
  - evidence: GET /ops/status response agent.permissions and computerUse fields.

## What it asked for

_Nothing._
## Its own summary

Established live system state. Home Mac bridge is online and relay-reachable (last seen 2026-08-07T08:50:33.795Z). A recent real pipeline run successfully rendered and uploaded 24 kHz mono PCM to the nRF9160 (3.43 s, 160.8 KiB, zero clipped samples), so the playback leg is currently operational. Hardware constraints are explicit: nRF9160 Cortex-M33/64 MHz, 211,608 B app RAM, 1 MB flash; capture 15,625 Hz I2S, Opus uplink 16 kHz/16 kbps; decode 24 kHz/60 ms then 31,250 Hz I2S wire clock. ESP32 bridge converts 31,250→44,100 and is SBC-only A2DP. LTE-M is half-duplex in practice and a measured call lost 388 uplink packets (~7.8 s) under simultaneous speech. Browser extension is offline; Mac accessibility and screen-recording permissions are missing, and Mac reports ready=false. Findings were recorded and sent to judgement/action/realtime/planner peers.

**Biggest unknown:** I still cannot inspect live pendant UART/firmware diagnostics or run the end-to-end build/test loop, so I cannot establish whether the 24 kHz path is robust on hardware (CPU headroom, underruns, packet loss behavior, and actual Bluetooth output) rather than merely successful in the latest recorded pipeline run. The previously requested pendant diagnostic access and context about the exact 24 kHz acceptance target remain the needed unblockers.

