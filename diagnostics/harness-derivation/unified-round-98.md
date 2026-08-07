# Harness derivation — unified — round 98

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make the pendant’s audio quality self-calibrating: run a private end-to-end test, choose the best safe profile for today’s link, and roll back if the owner’s voice or replies degrade.”"
- **useful because:** The live system currently renders 24 kHz mono PCM on the Mac, but the pendant uplink is 15,625 Hz PCM and LTE-M is half-duplex. A calibration transaction would turn those mismatched stages into a measured, reversible profile rather than silently resampling or failing in the field. It can use synthetic tones and a short owner-approved voice sample, then leave a concise receipt.
- **path:** pendant → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use a cheap background model for interpreting measurements and selecting among bounded profiles; reserve realtime for the owner’s conversation and the final spoken result.
- **latency:** 30–60 seconds when requested or after a firmware/link change; normal conversations are unaffected. A degraded LTE-M profile must be selected locally within 2 seconds if the link changes.
- **cost:** Usually under $0.01 per calibration (mostly telemetry and optional short audio); no model call is needed for raw signal measurements. A voice sample, if approved, is the dominant data/cost.
- **security:** Default test uses generated tones and discards raw audio. Any voice sample requires explicit confirmation, encrypted transport, short retention, and a visible delete action. Profile changes are bounded and reversible; never change microphone gain or output loudness without a receipt.
- **missing:** An end-to-end calibration transaction spanning pendant capture/playback, bridge forwarding, relay echo, and Mac 24 kHz rendering; A versioned audio-profile store with atomic activate/rollback and per-stage measurements; A dashboard/pendant receipt that distinguishes measured pass, degraded pass, and failed calibration

### "“Whisper the answer only to me, even when I’m in a room with other people.”"
- **useful because:** Today the pendant’s ordinary speaker makes a spoken reply audible to everyone nearby, so the owner must either avoid using it publicly or miss the answer. A private output mode would let them ask for calendar, navigation, account, or work information discreetly while keeping the interaction hands-free.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Realtime handles the active conversation and short spoken response; no background model is needed. The Mac/relay only classify the response as private and deliver the selected audio route.
- **latency:** Route selection under 150 ms after the owner says “whisper”; audio should begin within 500 ms of the normal response path.
- **cost:** Negligible incremental API cost; the dominant cost is a one-time hardware redesign and a small amount of calibration audio. No cloud transcription beyond the existing conversation.
- **security:** Private mode must be explicit, latched, and announced with a local tactile/LED indication so the owner knows which output route is active. Never infer privacy solely from location or microphone context. Keep the response encrypted in transit and avoid storing the private audio. Require confirmation before routing sensitive content to any external speaker or phone.
- **missing:** A private-output actuator such as a bone-conduction transducer or tightly coupled in-ear/near-ear receiver integrated into the pendant; Firmware audio-router state with a physical/local privacy indication and a hard local mute fallback; Relay and Mac metadata distinguishing private versus room-audible output, with an end-to-end route acknowledgment; Acoustic calibration and hearing-safety limits for the private transducer


## Changes it proposed to its own stack

### `integration` — Add a versioned audio-profile activation transaction across the pendant, ESP32 bridge, relay, and Mac agent. The transaction should record the actual sample rate/codec/bitrate/direction at every hop, run a synthetic loopback plus packet-loss/jitter test, activate only after pass thresholds, and automatically restore the prior profile on timeout or failed playback acknowledgment. Expose one receipt containing profile id, measured rates, loss, clipping, latency, and rollback reason.
- **owner gets:** They get a pendant that stays intelligible as LTE-M conditions and firmware change, instead of hearing unexplained silence, pitch shifts, clipping, or a reply that arrives too late. A failed test leaves the last known-good profile in place.
- effort: Medium-high: protocol/schema work in relay and Mac agent, firmware/bridge state machine, and a small dashboard view; requires hardware-in-loop tests on the nRF9160 DK and ESP32.  ·  risk: A bad activation could interrupt a live conversation or strand the device. Gate activation outside active calls, use a two-phase commit with a short watchdog, preserve the prior profile, and make rollback idempotent. Calibration recordings must not be retained by default.
- cost: Negligible model/API cost for synthetic tests; modest telemetry storage. Optional external codec hardware would be additional, but this transaction should first work with current hardware.  ·  latency: Adds no steady-state latency. Calibration takes roughly 30–60 seconds and may briefly reserve the audio path.
- security: Profile metadata is low sensitivity; voice samples are opt-in. Authenticate every activation and prevent a remote job from selecting arbitrary gain, codec, or radio settings.
- depends on: Complete the already-requested audio preflight receipt, link-aware duplex governor, and audio-path validation work; define the owner-approved 24 kHz acceptance thresholds.

### `hardware` — For the production pendant, add a low-power 24 kHz-capable mono audio codec/ADC-DAC on the existing audio bus (or replace the current microphone/playback front end) and expose its clock, gain, and measured sample-rate status to firmware. Keep the nRF9160 as modem/control plane and let the ESP32 bridge perform only bounded buffering/transport, not silent resampling.
- **owner gets:** The owner’s requested 24 kHz superwideband path would be real at the microphone and speaker, not just Mac-side TTS metadata. Speech would retain more consonant detail and the system could report when it is genuinely operating at 24 kHz versus falling back to the current 15,625 Hz capture path.
- effort: High: select and validate codec, PCB/layout and power work, Zephyr driver and clocking, acoustic tuning, bridge framing, and hardware-in-loop certification. Prototype on the current nRF9160 DK first with an external codec board.  ·  risk: New clock domains can introduce drift, RF/audio noise, higher power draw, and boot failures. Retain the current audio path as a firmware-selectable fallback, add watchdog-safe codec initialization, and require the calibration/rollback transaction before activation.
- cost: Prototype roughly $15–$40 in codec, mic, DAC, and breakout hardware; production BOM likely a few dollars. Expect additional tens of mW during audio, to be measured rather than assumed. No recurring API cost.  ·  latency: Potentially reduces resampling delay but adds small codec/buffer delay (target under 20 ms one-way). LTE-M half-duplex remains the dominant latency constraint.
- security: No new cloud data by itself. Firmware must authenticate profile updates and avoid exposing raw microphone buffers over debug/UART in production.
- depends on: The already-requested 24 kHz target architecture and end-to-end acceptance thresholds; Audio profile activation/rollback transaction; A production pendant constraint review beyond the current nRF9160 DK

### `hardware` — Add a low-power bone-conduction or near-ear private-output transducer to the production pendant, with an independent amplifier, hard local mute, and a dedicated route-status LED/haptic indicator. Add a measured maximum SPL limiter and a boot-safe default to the existing room-audible path until the owner explicitly enables private mode.
- **owner gets:** The owner can receive sensitive answers hands-free in public without broadcasting them, while retaining a clear fallback when the private transducer is not seated or cannot be heard.
- effort: High: mechanical/acoustic design, codec/amplifier integration, hearing-safety validation, battery characterization, firmware routing, and end-to-end relay acknowledgment. Prototype with an off-the-shelf bone-conduction module before committing to enclosure tooling.  ·  risk: Poor coupling can make speech unintelligible and encourage unsafe volume; the actuator may increase power draw or leak sound. Enforce a hardware volume ceiling, fit/self-test, automatic fallback, and a visible private-mode indicator. Recovery is a local mute and return to the ordinary speaker.
- cost: Prototype roughly $20–$60; production BOM likely $5–$20 plus enclosure changes. Expect tens of additional mW only while private audio is active; no recurring API cost.  ·  latency: Under 20 ms additional local audio delay; route negotiation should not delay the response more than 150 ms.
- security: Improves privacy only if route state is authenticated end to end. A stale or spoofed acknowledgment must never claim that sensitive audio was private; log route state without retaining the audio.
- depends on: A route-aware audio protocol in the relay and Mac agent; Pendant firmware support for an independently controlled output path; Acoustic and hearing-safety acceptance tests


## What it asked for

_Nothing._
## Its own summary

Fresh discovery confirms the Mac/relay path is online and already renders 24 kHz mono PCM (75,734 bytes for 1.578 s), while the live pendant uplink still reports 15,625 Hz PCM and LTE-M is half-duplex. Browser is offline with 9 queued commands; Mac Accessibility/Screen Recording remain unavailable, though AppleScript automation is broadly granted. I recorded two new items: a closed-loop, reversible audio-profile calibration/rollback transaction across pendant–bridge–relay–Mac, and a production hardware path with a genuine 24 kHz-capable codec while retaining the current path as fallback. The first is connective work across existing pipeline routes; the second is intentionally beyond the current DK.

**Biggest unknown:** The authoritative 24 kHz acceptance thresholds and production pendant constraints are still pending. Without them, we cannot determine whether to validate a 24 kHz capture path, a 16 kHz SWB fallback, or a hardware redesign. The already-requested audio preflight, governor, offline spool, privacy latch, and diagnostic skills also remain unanswered this round.

