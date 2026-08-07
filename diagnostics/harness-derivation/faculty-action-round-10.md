# Harness derivation — faculty-action — round 10

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac agent readiness** — Mac local agent v0.5.0 is reachable and relay paired, but full control is not ready: Accessibility trusted=false and Screen Recording granted=false; browser extension offline with 2 pending commands. Automation grants are cached and requiredMissing is empty.
  - evidence: GET /ops/status returned agent.fullControlMode=true, computerUse.loopEnabled=false, permissions.accessibility.trusted=false, screenRecording.granted=false, browserExtension.online=false, pendingCommands=2, ready=false.
- **Available hardware** — Current pendant is prototype Nordic nRF9160 DK (64MHz Cortex-M33, 211,608B app RAM, 1MB flash, Zephyr/NCS 3.4) and bridge is prototype Adafruit HUZZAH32 ESP32 A2DP SBC-only 44.1kHz stereo; both are remote and provisional.
  - evidence: get_hardware_spec pendant and bridge responses.
- **Owner Mac environment** — Owner MacBook-Air-6.local runs Darwin arm64 macOS 26.5.2, timezone America/New_York, with 123 apps including AI Pendant Agent and Browser Bridge; active project is AI Pendant Simulator at /Users/evanliu/agentic-gadget/software/ai-pendant-simulator.
  - evidence: GET /machine-context and GET /projects/active.
- **Owner action priorities** — Owner memory says current goal is derive next agent changes from harness ledger and ship the 24 kHz superwideband audio path end-to-end on the pendant; they allow browser read/click and reminders/notes without asking, but require confirmation for sending mail, deleting files, or buying. Owner timezone memory is America/Chicago, conflicting with machine-context America/New_York; do not infer scheduling timezone.
  - evidence: discover(owner) remembered block.
- **Owner pending needs** — Owner has previously failed to get read Gmail/GitHub/Calendar and browser page access; however browser extension is currently offline, so authenticated browser work cannot proceed.
  - evidence: discover(owner) asked_for_and_did_not_get plus GET /browser/status online=false.
- **Current audio path constraints** — Prototype pendant captures mic at 15,625Hz and Opus uplinks 16kHz/16kbps; playback decodes Opus at 24kHz in 60ms frames then resamples to 31,250Hz I2S for ESP32 bridge. Both encode/decode consume ~87% of one core; one full-duplex I2S peripheral must be shared. SD is failure-buffer only, not routine audio storage.
  - evidence: get_hardware_spec audio, io, storage.

## What it asked for

### `c3-r2k8` (context) — authoritative owner timezone
- why: Machine-context reports America/New_York while owner memory reports America/Chicago; scheduled reminders and routines must not be shifted incorrectly.
- would change: I will use the authoritative timezone for all due times, routines, and spoken scheduling confirmations instead of choosing one arbitrarily.

### `t12-adx0` (tool) — propose_capability
- why: The orchestrator explicitly requires recording a new owner-facing capability this round, but the proposal recorder is not present in my exposed tool set. This capability is not a request to execute actions; it records a product proposal.

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
    "why_now": {
      "type": "string"
    },
    "owner_value": {
      "type": "string"
    },
    "requirements": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "title",
    "description",
    "why_now",
    "owner_value",
    "requirements"
  ]
}
```

## Its own summary

Reconnaissance complete. The Mac local agent is live (v0.5.0) and paired to the relay, but not action-ready: Accessibility is untrusted, Screen Recording is denied, and the browser bridge is offline with 2 queued commands. Owner priorities are the 24 kHz superwideband audio path and harness-led changes. The prototype audio path currently captures 15.625 kHz, uplinks Opus at 16 kHz, and decodes 24 kHz to 31.25 kHz I2S; one full-duplex I2S peripheral and tight CPU/RAM are hard constraints. Owner timezone is contradictory (memory: Chicago; machine: New York), and I queued a request for the authoritative value. I recorded all findings.

**Biggest unknown:** Whether the pending firmware inspection/build/device-access grant and 24 kHz acceptance criteria will be approved/provided; without them I cannot safely validate or change the pendant audio path. Accessibility/Screen Recording and browser-bridge enablement also remain unresolved, so GUI/browser actions cannot be executed.

