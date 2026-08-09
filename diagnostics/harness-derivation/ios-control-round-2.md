# Harness derivation — ios-control — round 2

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **iOS control capability publication** — Current live tool manifest still exposes only seven tools; no ios-specific tool is granted or discoverable. Devices list has no iPhone, only Safari, Mac bridge, and offline mobile contract test.
  - evidence: list_capabilities returned granted count 0 and tools list of get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate, read_web_page, relay_job_status; discover(devices) returned three non-iPhone entries.
- **iPhone Mirroring runtime** — iPhone Mirroring is running (pid 68343) and Mac accessibility, screen recording, and synthesized input are verified; observation exposes no phone identity, pixels, or ios action schema.
  - evidence: GET /observe at 2026-08-09T01:56:21Z returned iPhone Mirroring in runningApps and accessibility trusted/eventsPost/screenRecording true, but no iOS fields.

## What it asked for

### `t3-l4wf` (tool) — propose_capability
- why: The owner needs a durable, independently addressable iPhone Mirroring node capability rather than an idea left in chat; this round explicitly requires recording that proposal.

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string"
    },
    "owner_value": {
      "type": "string"
    },
    "current_gap": {
      "type": "string"
    },
    "required_changes": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "acceptance_criteria": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "name",
    "owner_value",
    "current_gap",
    "required_changes",
    "acceptance_criteria"
  ]
}
```

## Its own summary

Reconnaissance confirms the Mac agent is live and iPhone Mirroring is running (pid 68343). Accessibility, screen recording, and synthesized input are verified, but the live manifest still publishes no iPhone identity, pixels, ios_* action schema, or iOS-specific tool; the devices catalog likewise has no iPhone. I recorded these findings and notified mac-planner/faculty-perception. To do useful work I still need the pending read-only ios_mirroring_inspect capability (with its exact input/output schema and window/Space status), plus the pending clarification of what an “independent iOS node” should mean operationally. Until those arrive, I cannot safely inspect or drive the real phone and will not guess an endpoint or action.

**Biggest unknown:** Whether the orchestrator actually granted ios_mirroring_inspect; list_capabilities currently reports granted=0 and no such tool.

