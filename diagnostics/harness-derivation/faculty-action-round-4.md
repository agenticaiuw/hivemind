# Harness derivation — faculty-action — round 4

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-action-readiness** — Mac Local Agent v0.5.0 is reachable and fullControlMode/fullControlPlanner/LLM planner are enabled, but ready=false because Accessibility trusted=false and Screen Recording granted=false; browser extension offline with 2 pending commands. All required automation grants are cached true.
  - evidence: GET /ops/status returned 200 with these exact fields.
- **pendant-audio-pipeline** — Cloud relay is configured and reachable; mac bridge online. A completed pipeline run rendered and uploaded 164650 bytes of 24 kHz mono s16le PCM, 3430 ms, unclipped, and relay accepted it for nRF9160 playback.
  - evidence: GET /pipeline returned pipelineId job_165a9c9a... events tts done and relay_result done with pcmBytes=164650, sampleRate=24000.
- **browser-action-failure** — Browser navigation cannot execute while extension is offline; recent jobs failed without touching anything and explicitly instruct opening Safari and enabling AI Pendant Browser Bridge so it polls.
  - evidence: GET /browser/status online=false pendingCommands=2; GET /jobs result.reason says extension offline and touched=[] reversible=false because step did not complete.
- **action-surface** — Mac agent exposes authenticated planning/execution, jobs/receipts/undo, pipeline audio/events, browser command/session, briefing/research/routines/reminders/tidy/sweep routes; read-only probing is available, but no safe UI or browser action can complete until permissions/extension state changes.
  - evidence: discover(routes) listed these routes; GET /ops/status and /browser/status show readiness blockers.

## What it asked for

### `p2-5ac8` (permission) — Enable macOS Accessibility and Screen Recording for AI Pendant Agent, and enable/poll the AI Pendant Browser Bridge extension in Safari
- why: Without Accessibility/Screen Recording the computer-use loop reports success while doing nothing, and without the browser bridge all browser actions fail immediately; these are the only observed blockers to executing Mac/browser work.
- risk it sees: Accessibility and Screen Recording permit UI observation/input automation; browser bridge permits authenticated tab reads/clicks. Keep destructive actions behind existing confirmation policy and do not authorize sending/deleting/purchasing implicitly.

### `t3-ihgx` (tool) — propose_capability_or_change
- why: The orchestrator explicitly requires recording a non-backlog capability/change this round, but the proposal tool is not present in my available tool list. I need the exact recording interface to avoid losing the proposal.

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
    "layer": {
      "type": "string"
    },
    "problem": {
      "type": "string"
    },
    "required_changes": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "why_not_backlog": {
      "type": "string"
    }
  },
  "required": [
    "kind",
    "title",
    "description",
    "layer",
    "problem",
    "required_changes",
    "why_not_backlog"
  ]
}
```

### `t4-rjkr` (tool) — propose_change
- why: Record the action-readiness proposal required by the orchestrator; no proposal recorder is exposed in this round.

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
    "layer": {
      "type": "string"
    },
    "problem": {
      "type": "string"
    },
    "required_changes": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "why_not_backlog": {
      "type": "string"
    }
  },
  "required": [
    "title",
    "description",
    "layer",
    "problem",
    "required_changes",
    "why_not_backlog"
  ]
}
```

