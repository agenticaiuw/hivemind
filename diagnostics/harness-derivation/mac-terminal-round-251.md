# Harness derivation — mac-terminal — round 251

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-24k-readiness** — The live prototype is not 24 kHz end-to-end: the pendant microphone captures at 15,625 Hz, uplink Opus is 16 kHz/16 kbps, playback decodes at 24 kHz, and both encode/decode consume about 87% of one nRF9160 core. The ESP32 bridge then resamples 31,250 Hz I2S to fixed 44.1 kHz SBC/A2DP.
  - evidence: get_hardware_spec(audio) and get_hardware_spec(bridge) in round 251

## Capabilities it proposed

### "“Make the pendant sound like a real wideband call: capture and deliver my voice at 24 kHz end to end, and tell me automatically if the path has fallen back or is underrunning.”"
- **useful because:** This is the single most useful missing experience: conversations become intelligible and natural rather than prototype-quality, while the owner gets an honest answer when hardware or radio cannot sustain it. It requires the worn capture device, relay transcoding, and the Mac/ESP32 headphone bridge to agree on one negotiated format; no one node can provide that alone.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime only for codec/transport negotiation and the short spoken status; background jobs should run a cheaper model for quality reports.
- **latency:** Capture-to-ear under 180 ms p95; 60 ms packet cadence; negotiation under 1 s. A quality report can arrive within 10 s after a call.
- **cost:** Negligible model cost during calls (binary codec metadata and counters); roughly $0.01–$0.05 per post-call report if an LLM is used, dominated by summarization rather than audio transport.
- **security:** Voice remains on the existing relay path; expose only aggregate packet loss, jitter, codec mode, and underrun counters to the dashboard. Never upload raw bench audio unless the owner explicitly asks.
- **missing:** A negotiated 24 kHz capture profile on the pendant (the live microphone is 15,625 Hz and current uplink is 16 kHz/16 kbps).; A relay session contract carrying sample-rate/channels/frame-duration and explicit fallback reasons, rather than assuming Opus 16 kHz uplink and 24 kHz downlink.; ESP32 bridge telemetry for resampler starvation and SBC/A2DP underruns, plus a Mac-side end-to-end acceptance harness.

### "“After I plug the pendant and audio bridge into the Mac, run a one-button hearing test and tell me whether the complete microphone-to-headphones chain is healthy.”"
- **useful because:** Today the owner cannot distinguish a bad microphone clock, Opus starvation, USB framing issue, ESP32 resampler starvation, or Bluetooth silence without reading logs. A bounded self-test gives a human answer before a call and creates a reproducible regression check for the live 24 kHz work.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** Use deterministic signal generation and counter comparison first; use a cheap background model only to turn the resulting metrics into one short diagnosis. Do not send raw audio to a model.
- **latency:** 10–15 seconds from button press to spoken/LED verdict; fail fast at each stage within 2 seconds.
- **cost:** Near-zero API cost: local tone and counters dominate. Optional diagnostic summary is under $0.01 per run.
- **security:** Generate a synthetic tone locally and discard samples after verification. Persist only timestamp, firmware versions, negotiated format, loss/jitter, and underrun counters. Require an explicit opt-in before recording the owner's voice.
- **missing:** A shared test-session ID and timestamped counter frame emitted by both chips and the relay.; A deterministic 24 kHz sweep/loopback mode that is clearly impossible to confuse with live microphone audio.; A Mac action that invokes the existing dual-UART capture scripts and parses bounded frames into a pass/fail report.; An explicit dashboard/pendant verdict vocabulary: capture, encode, transport, decode, resample, and Bluetooth each get a distinct failure reason.

### "“Protect my hearing while I use the pendant: warn me when the headphone level has been unsafe for too long, and automatically bring it down without interrupting the conversation.”"
- **useful because:** The owner wears this system for long conversations, yet the current audio path has no exposure accounting. A loudness guard would prevent accidental sustained high output when Bluetooth gain, bridge resampling, or a noisy environment causes the owner to compensate by turning it up. It is a user-visible capability that is different from transport-health reporting: it protects the person, not merely the packets.
- **path:** mac-bridge → pendant → relay → dashboard
- **model tier:** No realtime model is needed for exposure calculation. Use deterministic A-weighted/RMS estimates and a cheap background model only to explain a persistent warning in plain language.
- **latency:** Per-frame level estimation under 20 ms; attenuation within one audio frame after crossing the limit; spoken/LED warning within 1 second.
- **cost:** Zero model cost during calls. Optional weekly exposure summary costs less than $0.01 per report and is dominated by storage/querying, not inference.
- **security:** Store exposure aggregates rather than raw audio: rolling dose, peak estimate, duration, and device identity. The owner must be able to disable automatic attenuation, but the default should be protective. Do not infer medical hearing status.
- **missing:** A calibrated output-level estimate for the ESP32/A2DP path; Bluetooth volume percentage alone is not SPL.; A bridge-side rolling dose accumulator with a conservative safe-limit table and a hard ceiling independent of model output.; A low-latency command from bridge to pendant/relay so the owner hears why volume changed, without sending audio through a model.; Dashboard history and an explicit owner setting for warning-only versus automatic attenuation.

### "“When I switch headphones, automatically use the speech profile that makes the pendant easiest to understand, and let me say ‘clearer’ or ‘less sharp’ to tune it without opening an app.”"
- **useful because:** Different Bluetooth headphones make the same 24 kHz stream sound radically different. A per-device speech EQ and a simple spoken adjustment would improve intelligibility and reduce the temptation to raise volume. The bridge can identify the connected sink, the relay can retain the owner's preference, and the pendant provides the hands-free control surface.
- **path:** mac-bridge → relay → pendant → dashboard
- **model tier:** Use deterministic biquad filters and stored per-device parameters. Realtime language interpretation is limited to a tiny command set; no expensive model is required for the DSP.
- **latency:** Apply a profile at Bluetooth connection time within 500 ms; parameter changes take effect on the next audio frame.
- **cost:** No per-call model cost. One-time calibration can use a local deterministic sweep; optional natural-language parsing is pennies only if the command exceeds the fixed vocabulary.
- **security:** Persist headphone model/address and preference, not recordings. Bluetooth identifiers should remain local or be hashed before relay storage. Do not claim audiological correction or medical benefit.
- **missing:** A2DP sink identity and connection-event telemetry from the ESP32 bridge.; A versioned EQ profile format shared by relay and bridge, with bounded gain to avoid clipping.; A short command vocabulary and pendant confirmation tone/LED for applied, unknown, or clipped profiles.; A local calibration routine that measures the bridge's actual filter response rather than assuming a headphone model's marketing curve.


## Changes it proposed to its own stack

### `hardware` — Replace the prototype 15,625 Hz I2S microphone/clock arrangement with a 24 kHz-capable digital microphone and an audio-clock design that can sustain 24 kHz capture plus fixed-point Opus encode without sharing a nearly saturated nRF9160 core; pair it with a bridge input path that accepts 24 kHz mono before the mandatory 44.1 kHz SBC conversion.
- **owner gets:** The owner gets genuinely wideband speech instead of upsampling a 15.625 kHz source and calling it 24 kHz. It also removes the current ~87% single-core audio load that makes quality degrade exactly when a conversation matters.
- effort: High: select and electrically validate a 24/48 kHz I2S microphone, revise clocks and board support, benchmark encode plus radio concurrently, and revise relay negotiation and bridge firmware. Prototype first with an external clocked microphone board; then spin the wearable audio board.  ·  risk: Clock drift, RF/audio power noise, and a new microphone's analog performance can regress speech. Keep the existing 16 kHz profile as a negotiated fallback; gate rollout behind the proposed synthetic chain test and retain the current firmware image for rollback.
- cost: Prototype microphone/clock board roughly $20–$80; production BOM increase likely $2–$8 and modest additional power. No per-call API cost.  ·  latency: No inherent added latency; 20–60 ms frames remain possible. Initial clock/codec validation may temporarily increase buffering until measured.
- security: No new data leaves the device. Hardware changes do not alter the existing relay encryption boundary.
- depends on: 24 kHz negotiated session metadata in relay and pipeline/audio; ESP32 bridge telemetry and 24 kHz input acceptance; A deterministic end-to-end audio self-test with fallback verification

### `hardware` — Add a low-power wear/placement sensor to the pendant (capacitive skin contact or optical proximity, with an IMU fallback) and expose a debounced worn/removed event to the audio state machine and relay.
- **owner gets:** The owner should be able to take the pendant off without leaving an open microphone or an active conversation playing into a desk. Removal would pause capture and playback immediately, then resume only when it is worn again, with an explicit local indication rather than silent loss of state.
- effort: Medium-to-high: select a sensor that works through the enclosure, characterize false removals while walking, add a low-power interrupt path, and define resume semantics across the pendant, relay, and bridge.  ·  risk: A false removal could cut off a sentence; a false worn state is worse because it could leave capture active. Use conservative debounce, local LED feedback, and fail closed on sensor disagreement. Keep the existing button as the explicit override.
- cost: Roughly $0.20–$2 in production components and a few hundred microwatts to a few milliwatts depending on sensor; modest enclosure/PCB changes.  ·  latency: Pause capture in under 100 ms after a confirmed removal; resume after 300–500 ms of stable contact.
- security: Improves microphone privacy by making physical removal a local stop condition. No new data leaves the device; only a worn/removed state is transmitted.
- depends on: A relay conversation state that distinguishes physical removal from radio loss; Bridge behavior that mutes output and reports acknowledgment; A pendant-local privacy indicator and recovery rule


## What it asked for

_Nothing._
