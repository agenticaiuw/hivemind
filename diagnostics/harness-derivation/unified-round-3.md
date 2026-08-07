# Harness derivation — unified — round 3

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio pipeline** — Mac pipeline telemetry shows response TTS rendered as 24,000 Hz mono signed-16 PCM; observed 164,650 bytes for 3,430 ms, then uploaded to relay and marked waiting for nRF9160 playback. A separate live input telemetry record reports 15,625 Hz PCM capture, 937,500 bytes, 1,441 ms transcription.
  - evidence: GET /pipeline response: tts event meta format=s16le sampleRate=24000 channels=1 pcmBytes=164650; agent event inputTelemetry sampleRate=15625 format=pcm-s16le.
- **Mac readiness** — Mac agent v0.5.0 and relay are reachable, but /ops/status reports readiness false because Accessibility is untrusted and Screen Recording is not granted; browser extension is offline. RequiredMissing is empty, so core declared requirements are technically satisfied despite optional/control permissions absent.
  - evidence: GET /ops/status returned ready:false, accessibility.trusted:false, screenRecording.granted:false, browser.online:false, relay.reachable:true.
- **hardware constraints** — Pendant is nRF9160 Cortex-M33 64MHz with 211,608 B app RAM and fixed-point libopus; encode ~15ms and decode ~25.4ms per 60ms packet, ~87% of one core when both run. ESP32 bridge resamples 31,250 I2S to 44,100 SBC-only A2DP and previously starved with a 44kB buffer.
  - evidence: get_hardware_spec(audio), get_hardware_spec(pendant), get_hardware_spec(bridge).
- **audio artifact** — Pipeline output audio endpoint returns a RIFF/WAVE artifact whose header begins with mono PCM format and sample-rate bytes corresponding to 24 kHz (0x5dc0 little-endian), confirming downloadable output is raw 24 kHz WAV rather than merely telemetry metadata.
  - evidence: GET /pipeline/job_165a9c9a-e5e3-4e29-b500-2fad63115ab9/audio/output returned RIFF WAVE fmt header with byte sequence ...01 00 01 00 c0 5d 00 00...

## What it asked for

### `t3-trkd` (tool) — audio_pipeline_validate
- why: The owner’s stated goal is to ship the 24 kHz superwideband path end to end. Reconnaissance confirms 24 kHz WAV output, but we lack a safe, read-only validator that checks capture→relay→TTS→pendant/bridge formats, resampling, frame timing, clipping, and round-trip continuity against the acceptance criteria.

```json
{
  "type": "object",
  "properties": {
    "pipeline_id": {
      "type": "string",
      "description": "Existing pipeline run ID to validate; if omitted, choose the newest completed audio run."
    },
    "directions": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "input",
          "output",
          "both"
        ]
      },
      "description": "Audio directions to inspect."
    },
    "checks": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "wav_header",
          "sample_rate",
          "channels",
          "sample_format",
          "duration_consistency",
          "frame_continuity",
          "clipping",
          "resampler_ratio",
          "opus_packet_timing",
          "bridge_buffer_safety"
        ]
      },
      "description": "Checks to perform; defaults to all safe checks."
    }
  },
  "required": []
}
```

## Its own summary

Environment is a MacBook-hosted AI Pendant system: Mac agent v0.5.0, Cloudflare relay v1.1.0, online nRF9160 and ESP32 prototype hardware. The live pipeline is already producing downloadable mono 24 kHz PCM WAV output and telemetry records 15,625 Hz PCM capture; relay and Mac bridge are reachable. Hardware constraints are severe: nRF9160 has 211,608 B app RAM and ~87% CPU when Opus encode/decode overlap; ESP32 is SBC-only 44.1 kHz A2DP with a known 44 kB-buffer starvation limit. Current Mac readiness is false because Accessibility and Screen Recording remain ungranted, though no required permissions are formally missing; browser extension is offline. I queued a request for a read-only audio_pipeline_validate tool to verify end-to-end format/timing/resampling/continuity/clipping safely. Existing workspace-edit and permission requests were already pending and were not repeated.

**Biggest unknown:** Exact source-level gaps and acceptance-test results for the nRF9160 firmware/ESP32 bridge path remain unknown because I have no granted workspace-edit capability or dedicated read-only audio validator yet; the observed relay output alone does not prove physical pendant playback or superwideband quality.

