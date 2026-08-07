# Harness derivation — mac-planner — round 157

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I double-press the pendant while you are working on my Mac, stop the current desktop or browser task immediately, tell me what was already done, and leave a resumable checkpoint."
- **useful because:** This is the single most useful missing behavior: the owner can interrupt a runaway or simply-wrong action from the one device always on their body, even when the Mac screen is away or occupied. It combines pendant input, relay routing, and Mac/browser cancellation rather than duplicating a Mac feature.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime classifier for the tiny button event and a cheap background model for the checkpoint summary; no expensive reasoning is needed to stop work.
- **latency:** Hard stop signal under 300 ms from USB/LTE event to Mac worker; checkpoint receipt within 3 seconds.
- **cost:** <$0.01 per interrupt; dominated by one short summary call only when partial work needs explaining.
- **security:** A false double-press could cancel a benign task, so require a deliberately distinct long-press/double-press pattern and make cancellation idempotent. Do not transmit audio; send only job ID and action state. No confirmation should be required for stopping work.
- **missing:** pendant firmware event type for an interrupt distinct from conversation end; relay cancellation endpoint that propagates a cancel token to Mac and browser workers; Mac/browser workers that checkpoint after each action and persist a resumable cursor; dashboard status showing stopped, completed actions, and resume action

### "Say “check my pendant” and have the Mac run a complete tethered health check: verify the nRF9160 and ESP32 serial links, exercise microphone-to-headphone audio, measure packet loss and latency, and leave a dated bug report with the exact failing stage."
- **useful because:** The pendant is physically attached to this Mac today but is not relay-registered, so the owner has no honest way to know whether a bad conversation is radio, TLS, Opus, I2S, Bluetooth, or the bridge. One spoken request would turn the live hardware into a self-diagnosing instrument and produce a report they can hand to themselves or a developer.
- **path:** pendant → mac-planner → mac-terminal → relay-realtime → dashboard
- **model tier:** Deterministic serial/audio fixtures and a cheap parser should do the measurements; use the realtime model only to turn the result into one spoken diagnosis.
- **latency:** Initial link checks in 5 seconds; full audio exercise and report in under 45 seconds.
- **cost:** Near-zero model cost; local serial and audio fixtures dominate. Optional report upload costs only a small text payload.
- **security:** Keep raw microphone samples local and delete test tones after measurement. Upload only metrics and redacted logs unless the owner explicitly asks to attach UART data. Never trigger a live LTE conversation as part of a test.
- **missing:** allowlisted Mac route for opening both known USB serial ports and collecting bounded UART output; ESP32 loopback/test-tone command with timestamp markers; nRF9160 diagnostic command for I2S/Opus buffer counters and packet statistics; a shared diagnostic schema correlating clocks across pendant, bridge, and Mac; bug-report writer that saves to ~/AI-Pendant-Workspace and optionally posts a redacted receipt

### "When I say “send this to my pendant” while a browser page is open, take the page title and my current selection, turn it into a 20-second spoken brief with a link, queue it for the wearable, and mark it read when I finish listening."
- **useful because:** It turns the browser's private, authenticated context into a wearable memory aid without making the owner dictate or lose the page. The browser extension can see selection and tab identity, the relay can summarize and queue audio, and the pendant can provide the only reliable completion signal while away from the desk.
- **path:** browser-extension → relay-realtime → pendant → mac-planner → dashboard
- **model tier:** Use a cheap summarizer for selected text; realtime is only for the spoken command and delivery acknowledgement. Do not send full pages when a selection exists.
- **latency:** Capture selection immediately; spoken brief available within 8 seconds; queue survives link loss and resumes later.
- **cost:** <$0.02 per item, mostly TTS/audio encoding; summarization is a few hundred tokens. Storage is a small text/audio object with a short TTL.
- **security:** Selection and URL may contain private data; keep it scoped to the active tab and show source URL in the receipt. Never capture passwords or page-wide content implicitly. Require explicit words “send this” and auto-delete unplayed items after 24 hours.
- **missing:** browser extension event exposing current selection and stable tab/session ID to the relay; relay audio queue with per-item TTL, delivery acknowledgement, and played watermark; pendant playback-complete event distinct from conversation audio; a citation-bearing spoken payload format linking summary, URL, and selection hash

### "When I unplug the pendant from my Mac and walk away, keep the same conversation alive over LTE; when I return and reconnect it, synchronize the transcript, audio position, and any unfinished Mac task without making me start over."
- **useful because:** Today USB-tethered testing and LTE operation are separate worlds. The owner should be able to move naturally between desk and outside: the wearable remains the same endpoint, and work does not reset when transport changes. This requires the pendant, Mac, relay, and durable session state to cooperate; no single node can provide it.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Realtime transport/session coordinator; use a cheap background reconciler for transcript and task-state merge.
- **latency:** Transport handoff under 2 seconds when LTE is registered; reconnect and state reconciliation under 10 seconds.
- **cost:** Small per-session metadata overhead; audio cost is unchanged because only the active transport carries frames. Reconciliation is a few hundred tokens at most.
- **security:** Bind the session to the authenticated pendant identity and Mac job ID; never let a newly connected device inherit an old session without proof. Store only encrypted transcript/task deltas and expire handoff state after 24 hours.
- **missing:** dual-transport session protocol supporting USB serial and LTE-M with a monotonic event sequence; pendant firmware that detects USB attach/detach and reconnects its WebSocket without losing conversation state; relay session authority that accepts one active audio transport while preserving ordered events; Mac job runner checkpoint export/import keyed to the wearable session; dashboard visibility for active transport and last synchronized sequence


## Changes it proposed to its own stack

### `hardware` — Replace the one-button nRF9160 pendant enclosure with a two-control design: retain the conversation button and add a physically latching microphone-mute/privacy switch with a red hardware LED state. Wire the switch to a GPIO interrupt that gates I2S mic DMA locally before any codec, while still allowing speaker playback and a mute-state event to the relay.
- **owner gets:** The owner can guarantee the microphone is off by touch, even if LTE, firmware, the Mac, or the model is misbehaving. It makes private conversations and meetings practical instead of relying on a spoken command or software state.
- effort: Moderate hardware revision: enclosure/PCB input, debounce and GPIO driver, I2S gate, event protocol, and relay/dashboard state. Prototype first with a GPIO jumper on the live DK and a 3D-printed switch enclosure.  ·  risk: A stuck or bouncing switch could leave the mic muted or unexpectedly enabled; default hardware state should be muted on boot and firmware should emit state transitions. Recovery is a physical toggle plus visible LED; no server dependency.
- cost: Prototype <$15 in switch, LED, resistor, and enclosure parts; production BOM roughly <$1.50. Negligible power draw for a latching switch and LED only when changing state.  ·  latency: Local gating is immediate (<10 ms) and avoids uplink traffic while muted.
- security: Strongly positive: privacy control is physically enforced before Opus and TLS. The relay receives only mute/unmute state, never raw audio while muted.
- depends on: GPIO allocation and debounce driver in nRF9160 firmware; a protocol event for local mute state; relay/UI representation of hardware mute; a clear owner-facing LED behavior


## What it asked for

_Nothing._
## Its own summary

Round 157 produced four new directions: (1) the wearable double-press emergency stop with resumable Mac/browser checkpoints—the highest-value cross-surface behavior; (2) a tethered spoken pendant health check, though the recorder flagged it as close to an existing diagnostic idea; (3) browser-selection-to-pendant spoken handoff, also flagged as adjacent to an existing remember-this-page idea; and (4) a hardware-level latching microphone mute switch that gates I2S locally. Live discovery confirmed /health is up, while the newly granted mac_readonly_inspect tool is still schema-only and cannot inspect apps or tabs yet.

**Biggest unknown:** The critical unknown is whether the existing relay/job records can actually propagate cancellation and durable checkpoints end-to-end, rather than merely exposing /execute, /jobs, and receipts. I still need implemented (not schema-only) serial access to /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, a pendant interrupt event, and a tested audio queue/playback acknowledgement. The owner also still needs to manually grant Accessibility/Screen Recording if vision/UI automation is required.

