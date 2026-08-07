# Harness derivation — relay-realtime — round 8

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

- **relay environment health** — Cloud relay is reachable and configured; mac bridge is online per health endpoint.
  - evidence: GET /health returned service AI Pendant Cloud Relay version 1.1.0, relayApiKeyConfigured=true, speechToTextConfigured=true, macBridgeOnline=true.
- **device status** — A MacBook bridge device is registered and online.
  - evidence: GET /v1/devices/status shows deviceId home-macbook-bridge with online=true and lastSeenAt 2026-08-07T05:06:57.607Z.
- **voice pipeline state** — Latest voice run completed; historical voice commands include both direct answers and plan_ready jobs.
  - evidence: GET /v1/ops/voice-runs/latest status=completed; GET /v1/ops/history includes entries with jobStatus completed and plan_ready.
- **mac planning permission** — POST /v1/mac/plan is permitted and returns queued plan jobs for free-form commands; execute is not confirmed available.
  - evidence: POST /v1/mac/plan returned 202 with job queued; permissions list only probe:post:/v1/mac/plan.
- **memory visibility** — Persistent memory is available via /v1/ops/memory and contains prior actions, tools, and device-related entries.
  - evidence: GET /v1/ops/memory returned entities including Action, Tool, Device, and File records with results.

## What it asked for

### `p5-mc8x` (permission) — probe:get:/v1/state/* and probe:get:/v1/ops/* additional routes beyond latest/history/memory
- why: To route voice commands safely, I need access to session-level state (current session, routing mode, locale, user preferences, and constraints) and any available job/status endpoints to know whether to answer directly, plan on the Mac, or defer. The current grants only confirm mac planning and a few ops reads.
- risk it sees: Broader read access could expose sensitive user data (preferences, transcripts, memory). I would use it read-only for routing decisions and only surface what’s necessary.

### `t5-gk3c` (tool) — relay_job_status
- why: When I POST a plan, I receive a queued jobId but I cannot check progress or retrieve the planned actions to inform the owner. A status tool would let me read job state without inventing a protocol or requiring execute permission.

```json
{
  "type": "object",
  "properties": {
    "jobId": {
      "type": "string",
      "description": "The job id returned from a plan request."
    }
  },
  "required": [
    "jobId"
  ]
}
```

## Its own summary

Confirmed via probes that the cloud relay is healthy, speech/STT are configured, and the Mac bridge is online. I can read device status, latest voice run, history, and memory, and I can POST to the Mac planner to queue a plan job. I recorded these findings. I cannot confirm any execute path or any job status retrieval path, so I can’t responsibly say what a plan will do or when it’s ready.

**Biggest unknown:** How to observe and report downstream plan job status/actions (a read-only job status endpoint/tool), and broader session state for routing decisions (current session context, preferences, and constraints).

