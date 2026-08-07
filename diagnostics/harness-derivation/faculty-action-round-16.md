# Harness derivation — faculty-action — round 16

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent** — Mac local agent is live at localhost:8000, version 0.5.0, with 120 authenticated routes; health is unauthenticated and capabilities confirms bearer auth/token configured.
  - evidence: GET /health returned 200 service AI Pendant Mac Local Agent version 0.5.0; GET /capabilities returned ok true, routeCount 120, tokenConfigured true.
- **devices** — Only home-macbook-bridge is online; home-chrome is offline with 0 tabs and cloudflare-contract-test is offline.
  - evidence: devices discovery returned home-macbook-bridge online last seen 2026-08-07T09:25:33.856Z; home-chrome offline and cloudflare-contract-test offline.
- **audio** — Current audio path captures at 15,625 Hz, encodes Opus uplink at 16 kHz/16 kbps, decodes at 24 kHz/60 ms frames, then resamples to 31,250 Hz I2S; simultaneous codec load is ~87% of one core. It is prototype firmware.
  - evidence: get_hardware_spec(audio) returned these rates, frame size, codec version 1.6.1, timing, and status PROTOTYPE.
- **power** — Pendant supports USB or battery but has no fuel-gauge driver, so charge state cannot currently be read; LTE-M bursts draw substantially more than idle.
  - evidence: get_hardware_spec(power) returned supply and no battery gauge driver.
- **action-routing** — Reversible Mac control can be executed through mac_run_actions (1–3 actions), complex workflows through mac_delegate, browser work through browser_run_actions, and live battery/wifi/volume/focused-app readings through get_mac_status. Browser device is currently offline, so browser actions are not presently actionable.
  - evidence: Tool descriptions for mac_run_actions, mac_delegate, browser_run_actions, get_mac_status plus devices discovery showing home-chrome offline.
- **network** — Pendant LTE-M link is half-duplex in practice over one TLS WebSocket; 16 kbps uplink + 24 kbps downlink contention caused 388 uplink packets (~7.8 seconds) dropped in a recent call.
  - evidence: get_hardware_spec(network) measured result.
- **bridge** — ESP32 HUZZAH32 bridge receives 31,250 Hz I2S, resamples to 44.1 kHz, and uses SBC-only Bluetooth A2DP source; 44 kB buffering starved Bluetooth into silence, so RAM is tight.
  - evidence: get_hardware_spec(bridge).
- **io** — Pendant has one button and one LED, one full-duplex I2S peripheral shared by mic/speaker; I2C/SPI are currently free. Button starts/ends conversation and LED indicates recording/buffering/errors.
  - evidence: get_hardware_spec(io).
- **storage** — microSD is a failure buffer only when chunk upload fails, not routine audio storage; FATFS with exFAT is enabled.
  - evidence: get_hardware_spec(storage).
- **unrecorded-proposal-request** — Requested a durable propose_capability tool because the owner required a proposal record, but that tool is absent this round. Candidate distinct capability: seamless loss-resilient wearable conversations with turn ordering preserved across LTE interruption, requiring encrypted on-device rolling turn journal, resumable acknowledged session protocol, bridge buffering/adaptive transport, and explicit recovery UX. This is distinct from listed browser/memory/retention backlog.
  - evidence: request_tool returned queued id t18-0s4b; no propose_capability or propose_change tool is present in the available namespace.

## What it asked for

### `t18-0s4b` (tool) — propose_capability
- why: The owner explicitly requires recording a new capability proposal this round, and the proposal tool is not exposed in my current tool namespace. I need a durable recording mechanism rather than emitting discarded text.

```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Concise capability name"
    },
    "owner_value": {
      "type": "string",
      "description": "What the owner should be able to have that they cannot have today"
    },
    "required_changes": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Concrete product/system changes required; do not constrain to currently wired hardware"
    },
    "why_now": {
      "type": "string",
      "description": "Evidence-grounded reason this is a gap now"
    },
    "non_duplicate_basis": {
      "type": "string",
      "description": "Why this is distinct from existing backlog items"
    }
  },
  "required": [
    "title",
    "owner_value",
    "required_changes",
    "why_now",
    "non_duplicate_basis"
  ]
}
```

## Its own summary

Recon complete for this round. The Mac local agent is live (v0.5.0, 120 authenticated routes, bearer token configured) and the Mac bridge is the only online device. I can route reversible Mac work through mac_run_actions, complex work through mac_delegate, browser work through browser_run_actions (but home-chrome is offline), and live Mac state through get_mac_status. Hardware constraints recorded: prototype nRF9160 audio captures 15,625 Hz, Opus uplink 16 kHz/16 kbps, decodes 24 kHz/60 ms then resamples to 31,250 Hz I2S; simultaneous codec load is ~87% of one core. The ESP32 bridge is SBC-only 44.1 kHz A2DP with tight RAM; LTE-M is half-duplex and has documented packet loss under bidirectional load; no battery gauge exists; SD is failure-buffer-only. I also contacted perception, judgement, planner, and relay agents for current action-relevant state.

**Biggest unknown:** I still cannot inspect/build the pendant firmware or enumerate serial/J-Link hardware from this facet, and cannot safely implement the owner's stated end-to-end 24 kHz audio goal until the previously requested Mac build/device capability and acceptance criteria/approval mechanism become available. No new capability is visible in the granted category this round.

