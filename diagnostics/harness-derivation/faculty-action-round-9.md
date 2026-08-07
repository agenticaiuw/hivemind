# Harness derivation — faculty-action — round 9

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac control readiness** — Mac Local Agent v0.5.0 is reachable with bearer token configured and full-control planner enabled, but readiness is false because Accessibility is not trusted and Screen Recording is missing; no required permissions are missing according to the status payload, yet computer-use loop is disabled and vision upload consent is false.
  - evidence: GET /ops/status returned agent.ready=false, accessibility.trusted=false, screenRecording.granted=false, computerUse.loopEnabled=false, visionUploadConsented=false.
- **Browser bridge availability** — The Safari/browser bridge is offline, with two pending commands; browser actions cannot currently execute.
  - evidence: GET /browser/status returned online:false, extensionId fanout-probe-cleanup online:false, pendingCommands:2. GET /jobs showed recent browser_navigate jobs failed explicitly because the extension was offline.
- **Audio pipeline current state** — The live pendant capture path is currently 15,625 Hz mono PCM (not 24 kHz), while synthesized reply speech is successfully rendered and uploaded as 24,000 Hz mono PCM; a recent reply was 164,650 bytes, 3.43 seconds, with no clipping.
  - evidence: GET /pipeline returned inputTelemetry.sampleRate=15625 and a TTS event reporting 24000 Hz mono PCM, 164650 pcmBytes, 3430 ms, clippedSamples=0.
- **Relay and bridge health** — Cloud relay is configured and reachable, pairing is required, and the Mac bridge is online; relay advertises pendant pipeline telemetry, speech, persistent state, and durable audio.
  - evidence: GET /ops/status relay.payload: ok true, version 1.1.0, pairingRequired true, macBridgeOnline true, capabilities all true.
- **Audio retention defect** — Audio retention cleanup remains only proposed and is materially incomplete: disabled, forced dry-run, limited to newest 100 records without cursor, no scheduled invocation, and deletion bindings are not threaded, risking orphaned R2 objects.
  - evidence: describe chg-a813b918 reports status proposed and verifies these defects against live files.
- **Durable browser runner gap** — Browser backend routing exists, but the durable job runner with job IDs, persistence, retries, and planner result stream is still missing; voice-path wiring is also unapplied.
  - evidence: describe chg-16bc5dee reports router done but durable runner missing and voice path unreachable.
- **Physical audio architecture** — The pendant prototype captures I2S at 15,625 Hz, Opus uplinks at 16 kHz/16 kbps, and decodes playback at 24 kHz in 60 ms frames before resampling to a 31,250 Hz I2S wire clock. Both encode/decode consume about 87% of one nRF9160 core, so true 24 kHz capture would require firmware, codec, timing, and CPU-budget validation rather than a relay-only change.
  - evidence: get_hardware_spec(audio) returned the complete current audio chain and prototype status.

## What it asked for

### `t11-joec` (tool) — propose_capability_or_change
- why: The owner explicitly requires recording a new capability or implementation change, but this tool is not present in the currently exposed tool namespace. I need the recorder to submit one non-backlog idea grounded in the reconnaissance.

```json
{
  "type": "object",
  "properties": {
    "kind": {
      "type": "string",
      "enum": [
        "capability",
        "change"
      ]
    },
    "title": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "why": {
      "type": "string"
    },
    "layer": {
      "type": "string",
      "enum": [
        "pendant",
        "firmware",
        "relay",
        "mac",
        "browser-harness",
        "memory",
        "audio",
        "power"
      ]
    },
    "owner_value": {
      "type": "string"
    },
    "implementation_requirements": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "dependencies": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "kind",
    "title",
    "description",
    "why",
    "layer",
    "owner_value",
    "implementation_requirements"
  ]
}
```

## Its own summary

Round 9 reconnaissance is complete. The Mac agent and relay are reachable, but Mac readiness is false (Accessibility untrusted; Screen Recording missing), the browser bridge is offline with two queued commands, and browser jobs are demonstrably failing. The current audio chain is not end-to-end 24 kHz: capture is 15,625 Hz, Opus uplink 16 kHz, while output TTS/playback is 24 kHz. Hardware detail shows 24 kHz decode already exists, but encode+decode use roughly 87% of one nRF9160 core. I recorded the relay health, browser outage, audio mismatch, physical audio chain, retention defect, and durable-browser-runner gap.

**Biggest unknown:** I still cannot safely make the requested firmware/audio changes in this round: the granted-capabilities projection is empty, and the previously requested Mac build/device tool, implementation/proposal tool, pendant firmware permission, 24 kHz acceptance criteria, and owner approval policy have not appeared as usable grants or responses. I therefore need those specific grants/context (or an explicit statement that implementation is deferred) before acting. Separately, the owner/Mac must enable Accessibility and Screen Recording and bring Safari's bridge online for computer/browser actions.

