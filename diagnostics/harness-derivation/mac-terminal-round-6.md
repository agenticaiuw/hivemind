# Harness derivation — mac-terminal — round 6

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **backend health** — The probed service identifies itself as AI Pendant Mac Local Agent version 0.5.0 and returns healthy.
  - evidence: GET /health -> 200 {"ok":true,"service":"AI Pendant Mac Local Agent","version":"0.5.0"}
- **backend route exposure** — GET requests to /v1/bridge/work, /v1/ops/memory, and /v1/jobs are not exposed on this HTTP surface (all 404).
  - evidence: probe_http returned 404 Cannot GET for each path.
- **remote pendant hardware** — Remote pendant is nRF9160 DK, Cortex-M33 64MHz, 211,608B app RAM, 1MB flash, Zephyr/NCS 3.4.0; one button and one LED.
  - evidence: get_hardware_spec(pendant/io) returned these firmware-sourced specifications.
- **remote audio path** — Pendant captures 15,625Hz I2S, encodes Opus uplink 16kHz/16kbps, decodes downlink 24kHz/60ms and resamples to 31,250Hz I2S; encode+decode consume about 87% of one core.
  - evidence: get_hardware_spec(audio) returned firmware-sourced values.
- **remote bridge constraints** — ESP32 HUZZAH32 receives I2S, resamples 31,250 to 44,100Hz, and Bluetooth A2DP source is SBC-only/44.1kHz stereo; RAM pressure can starve Bluetooth.
  - evidence: get_hardware_spec(bridge) returned firmware-sourced values.
- **remote power** — Pendant accepts USB or battery, but has no battery gauge, so charge state is unavailable to the agent.
  - evidence: get_hardware_spec(power) returned no fuel gauge driver.

## What it asked for

### `t7-cyr8` (tool) — mac_readonly_diagnostics
- why: The granted safe_mac_command has no implementation, while my only job is environment reconnaissance. I need a narrowly scoped read-only diagnostic capability rather than arbitrary shell execution.

```json
{
  "command": {
    "type": "string",
    "description": "One command selected from a fixed read-only diagnostic allowlist; reject shell metacharacters, pipes, redirects, command substitution, interpreters, network clients, privilege escalation, and writes."
  },
  "timeout": {
    "type": "integer",
    "minimum": 1,
    "maximum": 30
  }
}
```

### `c6-7p2h` (context) — Mac shell safety policy and migration scope
- why: The current FULL_CONTROL_MODE executes arbitrary shell unattended, but the intended replacement depends on whether the owner needs only diagnostics, approved app automation, or deliberate filesystem/network administration.
- would change: If only diagnostics are needed, I will use a fixed read-only argv allowlist; if administration is required, I will recommend separate explicitly confirmed capability tokens and keep network, secrets, and destructive filesystem operations isolated. I need the required legacy command classes to assess compatibility.

## Its own summary

Round 6 reconnaissance: hardware specs confirm the Mac agent is local-agent v0.5.0; remote pendant/ESP32 audio and power constraints are now recorded. HTTP probing found only GET /health (healthy) on this surface; root, status, metrics, bridge, memory, jobs, and mac-status GET routes all return 404. The granted safe_mac_command cannot execute because its backend reports no implementation. I queued a narrowly scoped read-only mac_readonly_diagnostics tool request and asked for the required legacy shell command classes/safety policy. I also informed mac-planner that typed argv actions must preserve cwd/timeout semantics while eliminating unattended arbitrary shell execution.

**Biggest unknown:** I still cannot inspect the actual Mac (OS version, user, mounted volumes, permissions, processes, local-agent files, or network state) until a functioning read-only diagnostic tool is implemented. The exact shell capabilities the owner considers necessary for migration are also pending orchestrator context.

