# Harness derivation — mac-planner — round 26

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac_readonly_inspect availability** — The granted read-only inspection tool is present in the tool list but has no implementation; running_apps, foreground_app, and browser_tabs all return the same implementation error. I cannot use it to verify local state this round.
  - evidence: Three parallel mac_readonly_inspect calls returned: "This tool was granted a schema but has no implementation yet."

## Capabilities it proposed

### "Keep the conversation understandable when the connection is bad: if you miss part of what I said or your reply cannot get through, recover it automatically and tell me briefly what was lost instead of pretending the conversation continued normally."
- **useful because:** The current LTE-M link is half-duplex and measured to drop about 7.8 seconds of uplink while the agent speaks. Today that becomes silent, divergent context. A coordinated degraded mode can preserve intent with tiny control/text packets, then resume 24 kHz audio without making the owner repeat themselves.
- **path:** pendant firmware detects sequence gaps, jitter, and sustained modem contention; it keeps a tiny rolling transcript/codec recovery window and emits loss beacons → relay-realtime owns the session state, negotiates an adaptive mode (full audio, narrowband/Opus, text intent, or receive-only), asks the realtime model for a one-sentence repair prompt, and records missing ranges → Mac planner receives a durable recovery event and can write a local incident receipt/transcript marker; if the Mac is online it can provide a secondary text UI or queued audio replay → dashboard/iOS shows the owner a compact 'heard through 12:41; 3.2 seconds missing' event and lets them request replay or continue
- **model tier:** Realtime model only for the live repair sentence and mode negotiation. Use a cheaper background model to reconcile recovered transcript segments and produce a post-call loss report; firmware and relay heuristics should make the first decision without an LLM.
- **latency:** Detect loss within 300 ms; switch to control/text mode within 1 s; repair sentence within 2 s. Background reconciliation can take minutes.
- **cost:** About $0.001–$0.01 per degraded interval depending on realtime audio tokens; heuristic beacons and Opus mode switching are negligible. Background reconciliation is a small batch-model call per affected call.
- **security:** Transcript fragments and loss telemetry leave the pendant as they do today; do not add routine SD retention. Store only sequence numbers and short-lived encrypted recovery fragments, expire them after the call, and redact the dashboard event. Never infer missing words as facts: label reconstructed text with confidence and ask for a repeat when confidence is low.
- **missing:** A firmware/relay control message schema for sequence gaps, codec mode negotiation, and replay ranges; A pendant-side rolling jitter/transcript or encoded-frame buffer sized against the existing 211,608 B RAM and 87% combined audio CPU load; Relay support for low-bandwidth text/control frames independent of the saturated audio stream; Mac/dashboard event ingestion and a user-visible replay/repair state; An end-to-end loss-injection test harness; current browser bridge is offline with two pending commands, so browser work should not be a dependency


## Changes it proposed to its own stack

### `hardware` — For the wearable revision, add a small always-on audio/transport companion (for example an nRF5340-class low-power MCU with PDM/I2S and a ring-buffered codec path) between the microphone/speaker and the LTE modem, with a shared mailbox for sequence counters and loss beacons. Keep the nRF9160 for LTE and application control, but move Opus encode/decode, resampling, and jitter buffering off the 64 MHz application core. Give the companion a real fuel-gauge/charger interface and expose codec mode plus buffer depth to firmware.
- **owner gets:** The pendant can remain intelligible during simultaneous speaking and listening instead of dropping speech, run the requested 24 kHz path with less glitching, and last longer on battery. It also makes the degraded-mode recovery capability reliable rather than competing with an already measured 87% CPU load.
- effort: High: new board and audio firmware, mailbox protocol, power characterization, acoustic tuning, and LTE/audio coexistence testing. Prototype first as a small interposer board using the existing DK and bridge.  ·  risk: Clock-domain, DMA, and reset failures could produce silence or duplicated audio. Recover with a bypass mode that routes the existing I2S path, watchdog-supervised companion reset, and feature-gated rollout. Mechanical redesign is required because the current board is a development kit.
- cost: Rough prototype BOM +$20–$45 per unit (companion MCU, codec/PMIC/fuel gauge, PCB and audio components); roughly 5–20 mA active depending on codec and radio coordination, potentially offset by lower nRF9160 duty cycle. No per-call API cost.  ·  latency: Adds approximately 5–15 ms of buffering when healthy; reduces underruns and makes mode switching faster under congestion.
- security: No new cloud data if the companion only handles PCM/encoded frames and counters. Secure the mailbox protocol, disable debug access in production, and ensure failure buffers remain governed by the existing 'SD only on upload failure' policy.
- depends on: Finalize the 24 kHz end-to-end audio framing and loss-recovery protocol; Measure whether the current nRF9160 can meet the target with optimized fixed-point codec before freezing the companion split; Define a production enclosure, battery, and charging design


## What it asked for

_Nothing._
## Its own summary

Round 26 discovery completed. Live status: Mac agent and relay are healthy, FULL_CONTROL_MODE is enabled, Accessibility/Screen Recording and app automation grants are ready, but the browser bridge is offline with two pending commands. Hardware confirms the key reliability constraint: LTE-M contention loses about 7.8 seconds of uplink during downlink speech and the pendant's combined audio workload is about 87% of one core. I proposed a new cross-node degraded-conversation recovery capability and a production hardware change that moves audio buffering/codec work to a companion MCU. I also verified that the newly granted mac_readonly_inspect schema has no implementation, so it cannot currently inspect apps, tabs, or UI state.

**Biggest unknown:** Whether the relay and firmware already have an in-progress audio congestion/control protocol, and whether the owner wants a prototype interposer-board path or a software-only 24 kHz optimization first. Still needed: implement mac_readonly_inspect; define the loss/mode-negotiation wire schema; and bring the browser bridge online before browser-dependent work.

