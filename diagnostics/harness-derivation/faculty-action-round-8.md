# Harness derivation — faculty-action — round 8

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent** — Local Mac agent v0.5.0 is healthy at localhost:8000, bearer-authenticated, with 120 routes and full-control planner enabled.
  - evidence: GET /health and GET /capabilities returned 200; capabilities manifest says routeCount 120, tokenConfigured true, fullControlMode true.
- **Mac permissions** — Mac agent is not ready for GUI control: Accessibility trusted=false and Screen Recording granted=false; automation grants are cached and requiredMissing is empty.
  - evidence: GET /ops/snapshot returned permissions.accessibility.trusted=false, screenRecording.granted=false, automation entries granted=true, ready=false.
- **Browser bridge** — Browser extension bridge is offline, with two pending commands; only stale fanout-probe-cleanup device is listed.
  - evidence: GET /browser/status returned online:false, device online:false, pendingCommands:2; devices discovery shows same stale device.
- **Relay** — Cloud relay is configured and reachable, paired Mac bridge online, with speech, durable audio, persistent state and pendant telemetry capabilities; TTS is macOS say 24kHz PCM with tts-1 alloy fallback.
  - evidence: GET /ops/snapshot relay payload returned configured:true, reachable:true, macBridgeOnline:true and listed capabilities/models.
- **Host inventory** — Owner Mac is MacBook-Air-6.local, arm64 Darwin 26.5.2, timezone America/New_York, with 123 applications and extensive CLI inventory including JLink/JFlash tools.
  - evidence: GET /machine-context and /ops/snapshot returned hostname, platform, timezone, appCount and CLI inventory.
- **GUI action safety** — Observation endpoint explicitly warns UI actions may report success while doing nothing because synthesized events are not accepted; Accessibility must be granted to the running AI Pendant Agent binary.
  - evidence: GET /observe returned trusted:false, eventsPost:false, uiActionsWillReachTheScreen:false, consequence warning.
- **Browser failures** — Two recent browser navigation jobs failed after ~45 seconds because the extension was offline; no browser_* action can run until extension polling resumes.
  - evidence: GET /jobs returned failed jobs with exact failure reason and no undo available.
- **Current Mac project** — Active project is AI Pendant Simulator at /Users/evanliu/agentic-gadget/software/ai-pendant-simulator, with goals reliable voice interaction, LLM-first Mac planning, and smarter context memory; last work saved an order-page status.
  - evidence: GET /projects/active returned project path, summary, goals and open threads.
- **Scheduled work** — Five daily routines exist, including morning brief, LPWAN research audio brief, evening wrap-up, calendar/mail/files brief, and preview-only Downloads tidy; four have completed at least once and one has never run.
  - evidence: GET /routines returned five enabled routines with schedules and run statuses.
- **Pendant hardware** — Pendant is prototype Nordic nRF9160 DK, Cortex-M33 64MHz, 211,608B app RAM, 1MB flash, Zephyr/NCS 3.4.0; remote from this Mac agent.
  - evidence: get_hardware_spec pendant returned board, memory, RTOS and remote-location status.
- **Audio action constraints** — Pendant captures I2S mic at 15,625Hz and Opus uplink 16kHz/16kbps; playback decodes 24kHz/60ms frames then resamples to 31,250Hz I2S; simultaneous encode/decode uses ~87% core.
  - evidence: get_hardware_spec audio returned capture/playback/codec details.
- **Bridge hardware** — ESP32 HUZZAH32 bridge receives I2S, resamples 31,250→44,100Hz and sends SBC-only A2DP stereo; large buffers can starve Bluetooth.
  - evidence: get_hardware_spec bridge returned role and RAM limitation.

## What it asked for

### `c2-9ffj` (context) — owner action priorities and approval policy
- why: The action surface is available but GUI and browser execution are blocked; I need to know which unblock should be prioritized and what classes of reversible/irreversible actions the owner expects me to carry out proactively versus stage for approval.
- would change: I would route requests to direct Mac actions, browser staging, or approval checkpoints according to the owner's actual priorities instead of making assumptions.

### `t9-h4ld` (tool) — propose_capability_or_change
- why: User explicitly requires recording a novel owner-facing capability or system change this round; this tool is not currently exposed in my tool list.

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
    "why_now": {
      "type": "string"
    },
    "implementation": {
      "type": "string"
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
    "why_now",
    "implementation"
  ]
}
```

### `t10-u4h5` (tool) — propose_capability
- why: The user requires a persisted owner-facing proposal, but propose_capability is absent from the exposed tool list. Please expose it so I can record the proposal rather than merely describe it.

```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "why_now": {
      "type": "string"
    },
    "implementation": {
      "type": "string"
    },
    "not_in_backlog_claim": {
      "type": "string"
    }
  },
  "required": [
    "title",
    "description",
    "why_now",
    "implementation"
  ]
}
```

## Its own summary

Reconnaissance complete. The Mac agent is healthy (v0.5.0, bearer-authenticated, full-control planner, 120 routes) and the relay is reachable with Mac bridge online and 24 kHz pendant audio support. However, real GUI actions are unsafe/blocked: Accessibility is not trusted for the running AI Pendant Agent binary, Screen Recording is not granted, and the browser bridge is offline with two pending commands. Observation explicitly says UI actions can report success while doing nothing; recent browser jobs failed for this exact reason. The active project is AI Pendant Simulator, and five daily routines are configured. Pendant/bridge hardware and audio constraints are documented. I recorded all findings and requested owner action-priority/approval policy context.

**Biggest unknown:** Which unblock and action policy the owner wants prioritized: granting Accessibility + Screen Recording, bringing Safari/browser bridge online, or firmware/device inspection. I still need those operational grants (already requested; not re-requested this round), plus the pending firmware/device inspection capability/tool if it was not actually provisioned.

