# Harness derivation — faculty-judgement — round 2

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **owner** — Owner explicitly wants the next agent changes derived from the harness ledger and to ship the 24 kHz superwideband audio path end to end on the pendant; replies should be one short spoken sentence by default; browser reads/clicks are allowed, but sending mail/deleting/buying require confirmation.
  - evidence: owner discovery returned remembered Now/Relevant/permissions/replies facts.
- **hardware** — Pendant audio is only a prototype: nRF9160 captures at 15,625 Hz and uplinks Opus 16 kHz/16 kbps; playback decodes Opus at 24 kHz in 60 ms frames then resamples to 31,250 Hz I2S. Decode+encode consume ~87% of one Cortex-M33 core. ESP32 bridge resamples 31,250 to 44,100 and emits SBC-only A2DP, with tight RAM.
  - evidence: get_hardware_spec audio, pendant, and bridge returned these specs.
- **devices** — Only home-macbook-bridge is online; fanout-probe-cleanup and cloudflare-contract-test are offline.
  - evidence: discover(devices) live status.
- **mac readiness** — Mac agent is live v0.5.0 and relay reachable, but ops status says ready=false: Accessibility trusted=false and Screen Recording granted=false. Browser extension is offline with zero pending commands, while home-macbook-bridge is online.
  - evidence: GET /ops/status returned permissions and browser state.
- **routines** — Five routines exist; four have completed runs, but 'Daily brief: calendar, mail, files' has never run (lastRunAt/status null). The daily LPWAN research brief already requests cited audio for the pendant.
  - evidence: GET /routines returned the live routine records.

## What it asked for

### `p1-na2j` (permission) — macOS Accessibility and Screen Recording permissions for AI Pendant Agent, plus reconnect/authorize the AI Pendant Browser Bridge extension
- why: The live Mac ops status reports ready=false because Accessibility and Screen Recording are missing, and browser work is impossible while the extension is offline. These are prerequisites for reliable computer-use, authenticated page reads, and end-to-end validation of pendant workflows.
- risk it sees: Accessibility and Screen Recording permit UI observation and synthetic interaction on the owner's Mac; browser authorization permits reading/clicking logged-in pages. Keep existing confirmation gates for sending mail, deleting files, purchasing, and submitting forms; grant only to the signed AI Pendant Agent/extension.

## Its own summary

Recon established the owner’s explicit priority: ship the 24 kHz superwideband pendant audio path end to end. Hardware is still prototype-grade: nRF9160 uplink is 16 kHz/16 kbps Opus, playback decodes at 24 kHz then resamples to 31.25 kHz I2S, and the ESP32 bridge resamples to 44.1 kHz SBC A2DP; codec load is ~87% of one core and bridge RAM is tight. The live Mac agent (v0.5.0) and relay are reachable, but ops status is not ready: Accessibility and Screen Recording are missing, and the browser extension is offline. Five routines exist; the daily calendar/mail/files brief has never run. I recorded these findings and notified action/planner/relay peers. I queued a permission request for the two macOS grants and browser reconnection, with confirmation gates preserved. Prior ledger evidence also confirms the audio-retention sweeper and durable browser job runner remain unimplemented proposals.

**Biggest unknown:** Whether the current firmware/relay implementation actually delivers the intended 24 kHz path end to end; validating that requires the action/engineering tier and likely the pending macOS/device access grants.

