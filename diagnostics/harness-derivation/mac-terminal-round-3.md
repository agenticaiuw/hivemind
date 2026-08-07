# Harness derivation — mac-terminal — round 3

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac local agent HTTP service** — Health endpoint reports AI Pendant Mac Local Agent version 0.5.0; probed root and likely API paths returned 404, so no discoverable unauthenticated read API at those paths.
  - evidence: GET /health => 200 {"ok":true,"service":"AI Pendant Mac Local Agent","version":"0.5.0"}; GET /, /v1/bridge/work, /v1/status, /v1/ops/memory, /v1/jobs, /status => 404.
- **System architecture** — Mac local agent polls Cloudflare Worker bridge jobs and has planner, computer-use loop, browser bridge, action risk scoring, atomic JSON store, and context graph. Realtime agent has exactly five tools including mac_run_actions and mac_delegate; browser Run could move web tasks off Mac.
  - evidence: get_hardware_spec(component=stack) returned architecture and tool inventory.
- **Network boundary** — Pendant uses LTE-M nRF9160, one TLS WebSocket to Cloudflare Worker, with measured contention causing 388 uplink packets (~7.8s speech) dropped at 16 kbps uplink + 24 kbps downlink.
  - evidence: get_hardware_spec(component=network).
- **Pendant power/status** — Pendant has USB or battery power but no wired battery gauge, so agent cannot read charge state; LTE transmit bursts draw substantially more than idle.
  - evidence: get_hardware_spec(component=power).
- **Pendant storage policy** — Pendant microSD is FATFS/exFAT over SPI and is intended only as a failure buffer when audio chunk upload fails, not routine storage.
  - evidence: get_hardware_spec(component=storage).
- **Pendant I/O** — Pendant has one user button and one LED; I2C/SPI are currently unused, and one full-duplex I2S peripheral is shared by mic/speaker, constraining new audio paths.
  - evidence: get_hardware_spec(component=io).
- **ESP32 bridge** — Remote Adafruit HUZZAH32 receives pendant I2S, resamples 31.25kHz to 44.1kHz, and Bluetooth A2DP SBC source to headphones; 44kB buffers can starve Bluetooth due to tight RAM.
  - evidence: get_hardware_spec(component=bridge).

## What it asked for

### `c4-14v3` (context) — Mac shell authorization policy
- why: The shell executor currently runs arbitrary commands unattended because FULL_CONTROL_MODE bypasses actionRisk; I need the owner's intended confirmation and escalation policy for destructive, networked, credential-accessing, and long-running commands.
- would change: I would define an allowlisted read-only diagnostic surface and require explicit confirmation or a separate narrowly scoped capability for every mutation, external network access, credential/keychain access, process control, and filesystem write.

### `t4-o97e` (tool) — mac_readonly_diagnostics
- why: The granted safe_mac_command has no implementation, while arbitrary shell is unsafe. We need useful Mac status discovery without arbitrary command execution.

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "enum": [
        "identity",
        "os",
        "hardware",
        "battery",
        "network",
        "disk",
        "processes",
        "audio",
        "displays",
        "permissions"
      ]
    },
    "timeout_seconds": {
      "type": "integer",
      "minimum": 1,
      "maximum": 30
    }
  },
  "required": [
    "query"
  ]
}
```

## Its own summary

Round 3 reconnaissance: /health identifies the local service as AI Pendant Mac Local Agent v0.5.0; root and likely /v1 status/bridge/memory/job routes are not exposed via GET. Architecture confirms this Mac is a polling worker for the Cloudflare bridge, while pendant/ESP32 are remote. Hardware inventory: pendant has no battery gauge, SD is failure-buffer-only, one button/LED and one shared full-duplex I2S; ESP32 is a RAM-constrained SBC A2DP bridge. Critical safety issue remains: FULL_CONTROL_MODE bypasses actionRisk, so arbitrary run_shell executes unattended with unrestricted filesystem, network, credentials, process, and persistence access. The granted safe_mac_command cannot actually execute (tool reports no implementation). I requested owner shell policy context and a structured enum-based mac_readonly_diagnostics capability, and recommended separate explicit capabilities for mutations/network/credentials/process control.

**Biggest unknown:** Owner-approved Mac task classes and confirmation policy: specifically which read-only diagnostics are needed, and whether any mutation, network, keychain, process-control, or persistence actions should ever be available to the shell tier. Also, the implementation/availability of the safe structured diagnostics tool remains unresolved.

