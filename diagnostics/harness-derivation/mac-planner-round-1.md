# Harness derivation — mac-planner — round 1

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **local agent identity** — The Mac local agent identifies as AI Pendant Mac Local Agent, version 0.5.0, and responds successfully at GET /health.
  - evidence: GET /health returned HTTP 200 {"ok":true,"service":"AI Pendant Mac Local Agent","version":"0.5.0"}
- **system architecture** — This planner runs on owner's MacBook, while the pendant and ESP32 are remote. Mac harness includes planner, computer-use loop, browser bridge, action risk scoring, atomic JSON store, and context graph; it polls the Worker at /v1/bridge/work and posts job results.
  - evidence: get_hardware_spec(stack) returned the architecture and polling description.
- **available relay tools** — Realtime relay agent currently has exactly five tools: get_mac_status, mac_run_actions, browser_run_actions, web_search, and mac_delegate.
  - evidence: get_hardware_spec(stack) agent_tools_today field.
- **browser architecture** — Browser is driven through the Mac agent browser bridge; Cloudflare Browser Run also exists as a possible server-side browser path.
  - evidence: get_hardware_spec(stack) browser_harness field.
- **audio storage policy** — Pendant microSD is an upload-failure buffer only, not routine storage; exFAT/FATFS over SPI.
  - evidence: get_hardware_spec(storage) returned policy and filesystem details.
- **pendant hardware** — Remote pendant is nRF9160 DK, Cortex-M33 64MHz, Zephyr/NCS 3.4.0, 211,608B app RAM, 1MB flash.
  - evidence: get_hardware_spec(pendant)
- **pendant controls** — Pendant has one button (start/end conversation) and one LED; I2C/SPI are free, one full-duplex I2S peripheral must be shared for audio.
  - evidence: get_hardware_spec(io)
- **audio pipeline** — Pendant captures I2S at 15,625Hz, Opus uplink 16kHz/16kbps; decodes 24kHz/60ms frames and resamples to 31,250Hz for ESP32 bridge.
  - evidence: get_hardware_spec(audio)
- **ESP32 bridge** — Remote Adafruit HUZZAH32 receives pendant I2S, resamples 31,250→44,100, and acts as SBC-only A2DP source to Bluetooth headphones.
  - evidence: get_hardware_spec(bridge)
- **power telemetry** — Pendant uses USB or battery; no battery gauge is wired, so charge state is unavailable.
  - evidence: get_hardware_spec(power)

## What it asked for

### `c1-zw6r` (context) — Mac local-agent job and action contract
- why: HTTP probing only exposed /health; I need the exact local endpoints, request schemas, and safety semantics to turn server plans into concrete Mac desktop actions.
- would change: I would use the documented job/action contract rather than guessing routes or issuing unsafe side-effecting requests; I could identify which actions are available and when to ask for permission.

### `t1-5cft` (tool) — mac_run_actions
- why: To perform the core role of this Mac planner—turning server-side plans into concrete desktop actions—I need a controlled executor for apps, files, shortcuts, and browser operations with risk/confirmation handling.

```json
{
  "type": "object",
  "required": [
    "actions"
  ],
  "properties": {
    "actions": {
      "type": "array",
      "description": "Ordered list of desktop actions",
      "items": {
        "type": "object",
        "required": [
          "type"
        ],
        "properties": {
          "type": {
            "type": "string",
            "enum": [
              "launch_app",
              "quit_app",
              "open_url",
              "open_file",
              "create_file",
              "write_file",
              "move_file",
              "copy_file",
              "delete_file",
              "keystroke",
              "type_text",
              "click",
              "hotkey",
              "run_shortcut",
              "wait"
            ]
          },
          "app": {
            "type": "string"
          },
          "path": {
            "type": "string"
          },
          "url": {
            "type": "string"
          },
          "content": {
            "type": "string"
          },
          "destination": {
            "type": "string"
          },
          "key": {
            "type": "string"
          },
          "modifiers": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "text": {
            "type": "string"
          },
          "x": {
            "type": "number"
          },
          "y": {
            "type": "number"
          },
          "shortcut": {
            "type": "string"
          },
          "ms": {
            "type": "number"
          }
        }
      }
    },
    "dry_run": {
      "type": "boolean",
      "default": true
    },
    "confirmation_token": {
      "type": "string"
    }
  }
}
```

## Its own summary

Recon complete: this is the owner's MacBook local agent (AI Pendant Mac Local Agent v0.5.0), healthy at GET /health. The stack says a Mac harness polls Worker /v1/bridge/work for jobs and posts results, with planner, computer-use loop, browser bridge, risk scoring, atomic JSON store, and context graph. Relay currently exposes get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate. Browser tasks normally route through the Mac browser bridge, though Cloudflare Browser Run exists. Remote pendant/ESP32 hardware and audio/power constraints were recorded. I requested the exact job/action contract context and a controlled mac_run_actions capability because no executable desktop-action tool or route was exposed to me.

**Biggest unknown:** Exact local-agent HTTP routes and schemas for receiving jobs, reporting results, querying Mac status, and executing/risk-scoring desktop/browser/file actions. GET probes beyond /health returned 404; POST probing is permission-gated and was not attempted because this was reconnaissance.

