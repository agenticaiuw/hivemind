# Harness derivation — unified — round 16

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent** — Mac local agent is live at version 0.5.0, port 8000, with 120 routes and Bearer auth configured; /health is public.
  - evidence: GET /health returned ok=true, service AI Pendant Mac Local Agent, version 0.5.0. GET /capabilities returned port 8000, routeCount 120, Bearer auth and tokenConfigured=true.
- **audio-pipeline** — Live pipeline telemetry shows the current response path renders 24 kHz mono PCM on macOS, 164650 bytes for 3430 ms, then uploads it for nRF9160 playback; an earlier inbound run recorded 15625 Hz mono PCM, 937500 bytes, live LTE upload, with midPressStreamed=true.
  - evidence: GET /pipeline returned pipeline job_165a9c9a... events: TTS 24000 Hz mono PCM, 164650 bytes, 3430 ms; relay accepted response. Its agent metadata records input sampleRate 15625, channels 1, format pcm-s16le, storage live_lte, uploadedState uploaded, midPressStreamed true.
- **device-status** — Relay and Mac bridge are reachable and paired, but browser extension is offline; Mac automation is not ready because Accessibility and Screen Recording are ungranted, despite other automation grants.
  - evidence: GET /ops/status returned relay reachable=true, macBridgeOnline=true, browser online=false with fanout-probe-cleanup offline; permissions accessibility.trusted=false, screenRecording.granted=false, ready=false.
- **timezone** — There is an unresolved timezone conflict: owner memory says America/Chicago, while live Mac machine-context reports America/New_York. Do not schedule or interpret times until authoritative timezone is supplied.
  - evidence: Owner discovery remembered timezone America/Chicago; GET /machine-context returned timezone America/New_York.
- **audio-network** — The hardware spec identifies a major live-call constraint: LTE-M is half-duplex in practice and measured uplink 16 kbps plus downlink 24 kbps contention dropped 388 uplink packets (~7.8 seconds speech). Any 24 kHz superwideband rollout needs a bandwidth/concurrency strategy, not only codec changes.
  - evidence: get_hardware_spec(all) network.measured states the contention and packet-loss result; audio states current mic 15625 capture/16 kHz 16 kbps Opus uplink and 24 kHz/60 ms Opus downlink.
- **browser-state** — Browser bridge is currently offline even though three persisted browser sessions remain, including a UTC time page and two form pages; private browser work cannot be assumed available until heartbeat returns.
  - evidence: GET /browser/status returned online=false, pendingCommands=0; GET /browser/sessions returned sessions default, probe-form2, probe-form with stored tab/window IDs and last-used timestamps.
- **planner-observability** — The local routing counters are empty in this process (0 total requests and no tier samples), so routing performance or cost cannot yet be inferred from /routing.
  - evidence: GET /routing returned totalRequests=0, all tier requests 0, baseline samples 0.
- **project** — Active project is AI Pendant Simulator at /Users/evanliu/agentic-gadget/software/ai-pendant-simulator with workspace /Users/evanliu/AI-Pendant-Workspace; stated goals are reliable voice interaction, LLM-first Mac planning, and smarter multi-tier context memory.
  - evidence: GET /projects/active returned project proj_pendant, paths, summary, goals, and open threads.

## What it asked for

### `t4-afu9` (tool) — propose_capability
- why: The owner explicitly requires a new capability proposal to be recorded this round, but this agent's available tool list does not expose propose_capability. The capability must be recorded rather than written in text.

```json
{
  "type": "object",
  "properties": {
    "summary": {
      "type": "string",
      "description": "A capability the owner should be able to have, stated without limiting it to current wiring."
    },
    "why_now": {
      "type": "string",
      "description": "Evidence-grounded reason this is a missing owner-facing capability."
    },
    "owner_value": {
      "type": "string",
      "description": "What the owner can do or receive once delivered."
    }
  },
  "required": [
    "summary",
    "why_now",
    "owner_value"
  ]
}
```

### `t5-yxve` (tool) — propose_change
- why: The owner explicitly requires a new change proposal to be recorded this round, but this agent's available tool list does not expose propose_change. The change must be recorded rather than written in text.

```json
{
  "type": "object",
  "properties": {
    "summary": {
      "type": "string",
      "description": "A concrete implementation change, not a restatement of an existing backlog item."
    },
    "layer": {
      "type": "string",
      "description": "System layer affected, e.g. firmware, relay, Mac, bridge, or cross-surface."
    },
    "why_now": {
      "type": "string",
      "description": "Evidence-grounded reason for the change."
    },
    "owner_outcome": {
      "type": "string",
      "description": "Owner-facing result after implementation."
    }
  },
  "required": [
    "summary",
    "layer",
    "why_now",
    "owner_outcome"
  ]
}
```

## Its own summary

Reconnaissance complete. The Mac agent is live (v0.5.0, 120 authenticated routes), relay and Mac bridge are reachable, and the active project/workspace are identified. Current telemetry confirms 24 kHz mono macOS TTS output reaches the relay, while capture remains 15,625 Hz and LTE contention has caused measured 7.8 seconds of dropped speech. Browser bridge is offline; Accessibility and Screen Recording are still ungranted. I recorded all findings, including a live timezone conflict (owner memory America/Chicago vs Mac America/New_York), stale browser sessions, empty routing counters, project paths/goals, and the network/audio constraints.

**Biggest unknown:** The authoritative 24 kHz superwideband end-to-end architecture and acceptance criteria remain unavailable, as do the pending workspace-edit/audio-validation capabilities and macOS Accessibility/Screen Recording grants. These are the concrete blockers to safely implementing and validating the requested audio path; authoritative timezone is also needed before any time-sensitive scheduling.

