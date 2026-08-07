# Harness derivation — mac-terminal — round 4

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac local agent HTTP surface** — GET /health returns service AI Pendant Mac Local Agent version 0.5.0; root, /status, /capabilities, /api/status, and /diagnostics returned 404.
  - evidence: probe_http GET /health => 200 {ok:true,service:'AI Pendant Mac Local Agent',version:'0.5.0}; probes of other paths => Cannot GET.
- **Mac shell execution risk** — The shell action accepts an arbitrary command string with optional cwd and timeout; FULL_CONTROL_MODE bypasses actionRisk classification, so commands execute unattended with unrestricted environment, filesystem, network, and no separate audit log.
  - evidence: Granted context explicitly states executor.js branches on FULL_CONTROL_MODE and calls executeComputerAction directly; real commands include pmset, scutil, system_profiler, osascript.
- **Remote audio/pendant topology** — Mac is remote from the nRF9160 pendant and ESP32 A2DP bridge. Pendant uses LTE-M half-duplex WebSocket; uplink 16 kbps and downlink 24 kbps can saturate link, with a measured 7.8s uplink loss during concurrent agent speech. Audio is retained to SD only on failed upload.
  - evidence: get_hardware_spec network/audio/storage/bridge responses.
- **Existing agent tool surface** — Realtime agent has exactly five tools: get_mac_status, mac_run_actions, browser_run_actions, web_search, mac_delegate. Mac harness includes planner, computer-use loop, browser bridge, action risk scoring, JSON store, and context graph.
  - evidence: get_hardware_spec stack response.

## What it asked for

### `p4-vvc1` (permission) — mac_bridge.read_diagnostics
- why: I need a read-only, implementation-backed way to inspect Mac OS/version, local-agent process health, network, battery, and connected devices without invoking arbitrary shell.
- risk it sees: Low if commands are fixed and outputs are redacted; avoids exposing files, secrets, or mutating state.

### `t5-hq2f` (tool) — mac_read_diagnostics
- why: The granted safe_mac_command has no implementation, while reconnaissance and future routing need bounded host facts without arbitrary shell execution.

```json
{
  "type": "object",
  "properties": {
    "checks": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "os_version",
          "hardware_model",
          "current_user",
          "uptime",
          "battery",
          "network_interfaces",
          "wifi_status",
          "bluetooth_devices",
          "audio_devices",
          "local_agent_health",
          "running_process_summary",
          "disk_space"
        ]
      },
      "maxItems": 8
    }
  },
  "required": [
    "checks"
  ],
  "additionalProperties": false
}
```

### `c5-gpel` (context) — execution grant and replacement shell policy
- why: The planner previously requested mac_bridge.execute_plans, but I do not see whether it was granted or what policy now governs execution. The current FULL_CONTROL_MODE bypasses all risk gates.
- would change: If granted, I can describe the exact safe execution contract; if denied, I will only recommend read-only diagnostics and confirmation-gated typed actions.

### `t6-ckig` (tool) — mac_execute_typed_actions
- why: Replace arbitrary run_shell exposure with a narrow executor for the Mac planner's foreseeable tasks while preserving confirmation and auditability.

```json
{
  "type": "object",
  "properties": {
    "actions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "kind": {
            "type": "string",
            "enum": [
              "open_app",
              "get_status",
              "set_volume",
              "set_brightness",
              "launch_url",
              "focus_window",
              "file_select"
            ]
          },
          "app": {
            "type": "string",
            "enum": [
              "Safari",
              "Finder",
              "Terminal",
              "System Settings",
              "Music"
            ]
          },
          "value": {
            "type": "number",
            "minimum": 0,
            "maximum": 100
          },
          "url": {
            "type": "string",
            "maxLength": 2048
          },
          "query": {
            "type": "string",
            "maxLength": 512
          }
        },
        "required": [
          "kind"
        ],
        "additionalProperties": false
      },
      "maxItems": 10
    },
    "confirmation_token": {
      "type": "string",
      "maxLength": 256
    },
    "dry_run": {
      "type": "boolean"
    }
  },
  "required": [
    "actions",
    "dry_run"
  ],
  "additionalProperties": false
}
```

## Its own summary

Recon complete for this round. Local agent /health is Mac Local Agent v0.5.0; guessed status/capability routes do not exist. Hardware inspection confirms Mac is remote from the LTE-M pendant and SBC-only ESP32 bridge, with constrained half-duplex bandwidth and SD failure-buffer policy. The critical finding remains that FULL_CONTROL_MODE bypasses actionRisk, exposing arbitrary shell with unrestricted cwd/environment/filesystem/network and no separate audit log. I queued a low-risk read-only diagnostics permission, a fixed-schema mac_read_diagnostics tool, and a typed mac_execute_typed_actions replacement, plus requested confirmation of the planner execution grant. Recommended boundary: never expose arbitrary command strings to relay/planner; use structured allowlisted operations, fixed cwd, sanitized environment, bounded outputs/timeouts, explicit confirmation for mutations, and append-only audit IDs.

**Biggest unknown:** Whether mac_bridge.execute_plans is now granted and what exact post-grant execution policy applies; also the safe_mac_command grant is present but has no implementation, so I cannot directly inspect host process/network/device state.

