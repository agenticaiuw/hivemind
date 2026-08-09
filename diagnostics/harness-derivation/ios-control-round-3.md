# Harness derivation — ios-control — round 3

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **iPhone mirroring control availability** — Mac local agent advertises ios_status, ios_screenshot, ios_ocr, ios_home, ios_back, ios_open_app, ios_scroll, ios_swipe, ios_tap_text, and ios_type_text among 109 action types; computer-use loop is enabled and required permissions are ready.
  - evidence: GET /capabilities returned actionTypes; GET /ops/status returned accessibility trusted, screen recording granted, computerUse.loopEnabled=true, ready=true.
- **reachable physical devices** — The live device registry contains Safari on MacIntel (online, 2 tabs), home-macbook-bridge (online), and cloudflare-contract-test (mobile, offline). No separate iPhone device entry is exposed; iPhone is represented through the Mac's iPhone Mirroring action surface.
  - evidence: discover(devices) returned exactly these three entries; GET /machine-context lists iPhone Mirroring as an installed application; GET /capabilities lists ios_* action types.
- **computer-use safety boundary** — Accessibility-mode vision loop is ready with accessibility trust and loop enabled; screen recording is held per ops status but the vision-loop policy excludes whole-display screenshots and coordinate mouse actions. Its safe read-only operations are ui_snapshot/ui_find/ui_wait_for; ui_click has a documented mouse fallback risk and is not suitable for background iPhone Mirroring.
  - evidence: GET /vision-loop/status returned preflight ready, grants accessibility held, loopEnabled=true, and policy exclusions/fallback details.
- **iOS executor wiring gap** — The Mac agent advertises ios_status but its executor does not implement it: capability-gap inbox has one open gap, unsupported action type ios_status, asked twice, unresolved. Thus iOS action availability is currently declarative rather than reliable execution.
  - evidence: GET /capability-gaps/inbox returned gap id gap_e2ce9075-7488-46dd-a038-2d4e94a9dbb8, want 'iPhone status', detail 'Unsupported action type: ios_status', surface executor, resolvedAt null.
- **physical bridge boundary** — The physical bridge is an Adafruit HUZZAH32 ESP32 prototype used only for pendant I2S resampling and A2DP headphone output; it is remote to this ios-control facet and cannot host iPhone capture/control. The MacBook remains the only execution locality for iPhone Mirroring.
  - evidence: get_hardware_spec(component=bridge) reported role, prototype status, and 'you run on owner's MacBook (ios-control)... every device described here is REMOTE'.

## What it asked for

### `c2-7mox` (context) — independent iOS node
- why: The device registry has no separate iPhone node, while iOS actions are exposed only by the Mac-local agent. I need the intended architectural meaning before proposing routing or claiming independence.
- would change: I will either describe ios-control as a logical relay-facing capability backed by Mac-local capture/events, or request a true network/mobile endpoint if independence means operation without the Mac.

### `t4-hco3` (tool) — propose_capability
- why: The owner needs an actually recorded capability proposal, but the propose_capability tool is not present in this round's available tool manifest. The missing capability is a reliable, relay-addressable iPhone control node that can inspect and operate the real iPhone independently of the Mac planner while respecting Mirroring foreground/lock/pause constraints.

```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string"
    },
    "owner_value": {
      "type": "string"
    },
    "current_limitation": {
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
    "title",
    "owner_value",
    "current_limitation",
    "required_changes",
    "acceptance_criteria"
  ]
}
```

## Its own summary

Environment discovery complete: MacBook-Air-6.local is the execution host, with iPhone Mirroring installed and Mac bridge/permissions online. The advertised ios_* action surface is not wired end-to-end: capability-gap inbox explicitly reports ios_status unsupported by the executor. There is no separate iPhone device/node in the live registry, and the ESP32 bridge is only an audio prototype remote to this facet. Therefore “independent iOS node” can currently mean only a logical relay-facing route backed by Mac-local Mirroring, not an autonomous mobile/network node. I informed mac-planner, unified, and all agents of the wiring gap.

**Biggest unknown:** Whether the orchestrator will implement a real ios executor/inspection tool and define logical independence as relay routing; the prior context/tool requests are still pending.

