# Harness derivation — unified — round 1

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **deployment topology** — Unified runs on owner's MacBook; Mac local agent v0.5.0 at localhost:8000 is bearer-token protected (except /health), while Cloudflare relay is reachable and paired, with mac bridge online.
  - evidence: GET /health returned service AI Pendant Mac Local Agent v0.5.0; GET /ops/status returned relay reachable=true, pairingRequired=true, macBridgeOnline=true.
- **device availability** — home-macbook-bridge is online; cloudflare-contract-test mobile is offline. Browser extension is currently offline with zero devices and zero pending commands.
  - evidence: discover(devices) listed home-macbook-bridge online and cloudflare-contract-test offline; GET /ops/status returned browser online=false.
- **pendant audio path** — Prototype nRF9160 pendant captures I2S at 15,625 Hz, Opus uplink 16 kHz/16 kbps, and decodes 24 kHz/60 ms playback resampled to 31,250 Hz I2S into ESP32; encode/decode consume substantial CPU (~87% combined).
  - evidence: get_hardware_spec(audio) returned these rates and CPU figures.
- **Mac readiness** — Mac agent has full-control planner enabled but is not ready because Accessibility and Screen Recording permissions are missing; automation grants are cached and requiredMissing is empty, yet ready=false.
  - evidence: GET /ops/status agent.permissions returned accessibility.trusted=false, screenRecording.granted=false, ready=false.
- **owner context** — Owner timezone is America/Chicago; browser may be read/clicked without asking, destructive actions require confirmation, reminders/notes can be created without asking, and replies should be one short spoken sentence by default. Current project is AI Pendant Simulator; owner wants reliable voice interaction, LLM-first Mac planning, smarter multi-tier context memory.
  - evidence: discover(owner) remembered profile and active project data.
- **persistent state** — Relay uses Cloudflare Worker + D1 for jobs/history/memory and R2 for audio; audio retention is 30 days with sweep disabled and roughly 100 recordings stored.
  - evidence: get_hardware_spec(stack) returned relay storage and retention details.

## What it asked for

### `t1-nphy` (tool) — mac_workspace_edit
- why: Useful work will require implementing and testing the owner's requested 24 kHz superwideband pendant audio path and other code changes in ~/AI-Pendant-Workspace. Existing Mac actions can run limited shell commands but do not expose a safe, structured multi-file edit/test workflow with diffs and receipts.

```json
{
  "type": "object",
  "properties": {
    "root": {
      "type": "string",
      "description": "Workspace root, constrained to an approved project directory such as /Users/evanliu/AI-Pendant-Workspace or /Users/evanliu/agentic-gadget/software/ai-pendant-simulator"
    },
    "operations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "kind": {
            "type": "string",
            "enum": [
              "read",
              "write",
              "patch",
              "run_test",
              "git_diff"
            ]
          },
          "path": {
            "type": "string"
          },
          "content": {
            "type": "string"
          },
          "unified_diff": {
            "type": "string"
          },
          "command": {
            "type": "string"
          }
        },
        "required": [
          "kind",
          "path"
        ]
      }
    },
    "spoken_reply": {
      "type": "string"
    }
  },
  "required": [
    "root",
    "operations"
  ]
}
```

### `p1-dmre` (permission) — macOS Accessibility and Screen Recording permissions for AI Pendant Agent
- why: The live Mac agent reports ready=false because Accessibility is untrusted and Screen Recording is not granted. These permissions are needed for reliable computer-use/browser vision and end-to-end validation of pendant workflows.
- risk it sees: Accessibility permits synthesized input and UI control; Screen Recording permits capturing visible UI. Grant only to the signed AI Pendant Agent app, and retain existing confirmation gates for destructive actions. No permission is needed for read-only health probing itself.

### `c1-m6gd` (context) — 24 kHz superwideband audio-path acceptance criteria
- why: The owner memory says to ship the 24 kHz superwideband audio path end to end, but reconnaissance only exposes current prototype rates and hardware; it does not specify target codec framing, latency, bandwidth, firmware/relay files in scope, or required validation.
- would change: With the acceptance criteria I can propose or implement a bounded firmware/relay change and select meaningful build/audio integration tests instead of guessing what 'superwideband' means.

## Its own summary

Reconnaissance complete. Unified runs on the owner's Apple Silicon MacBook and can reach a bearer-protected Mac local agent at localhost:8000 (v0.5.0), plus a reachable paired Cloudflare relay (v1.1.0). The Mac bridge is online, but browser extension currently has zero online devices; Mac readiness is false because Accessibility and Screen Recording permissions are missing. The owner is in America/Chicago, allows browser read/click and non-destructive reminders/notes without asking, requires confirmation for destructive actions, and prefers one short spoken sentence. Current project is AI Pendant Simulator, with goals of reliable voice interaction, LLM-first Mac planning, and smarter context memory. Hardware is prototype nRF9160 + ESP32 bridge: 15,625-Hz mic capture, Opus 16-kHz/16-kbps uplink, 24-kHz playback decoded in 60-ms frames and resampled to 31,250-Hz I2S; ESP32 resamples to 44.1 kHz SBC Bluetooth. Relay stores jobs/history in D1 and audio in R2 with 30-day retention, sweep disabled. I recorded these findings, requested a structured workspace edit/test tool, requested narrowly scoped Mac permissions, and requested acceptance criteria for the 24-kHz superwideband task. The backlog confirms a high-priority unresolved retention-sweeper defect: only newest 100 captures are scanned, no scheduled invocation, deletion disabled, bindings omitted, and no owner-pin/dashboard controls.

**Biggest unknown:** The exact implementation and acceptance criteria for the owner's requested 24-kHz superwideband end-to-end audio path (codec sample rates/framing, relay transcoding contract, target firmware/bridge changes, and tests) remain unspecified; also pending orchestrator decisions on workspace-edit capability and Mac permissions.

