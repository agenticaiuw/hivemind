# Harness derivation — unified — round 33

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make the pendant audio reliable: run a one-minute guided audio check, show me whether my mic, speaker, LTE link, and 24 kHz path are healthy, then keep a short evidence-backed quality report after each call."
- **useful because:** The current prototype can silently lose speech (measured simultaneous traffic dropped about 7.8 seconds of uplink) and its capture, codec, playback, and wire clocks are mismatched. The owner needs to know whether a bad call is their environment, the link, or our pipeline—and needs that answer without reading UART logs.
- **path:** pendant → relay-realtime → relay → mac-planner → dashboard-ux → iOS
- **model tier:** Use firmware and relay measurements for the test; use a cheap background model only to summarize trends. Reserve realtime for the spoken one-sentence result and never send raw audio to a model for this.
- **latency:** Guided test completes in under 60 seconds; per-call telemetry is emitted within 5 seconds of hangup; spoken verdict under 1 second after the final measurement.
- **cost:** Usually <$0.01 per test/report; dominant cost is optional background summarization, not telemetry. Storage is small if only aggregates and hashes are retained.
- **security:** Raw microphone loopback must stay on-device and be discarded. Relay receives packet timing, loss, jitter, codec profile, and coarse levels—not recordings. Require confirmation before uploading any diagnostic audio sample; encrypt and expire reports.
- **missing:** A firmware loopback/calibration primitive that can exercise the I2S mic and ESP32 playback path offline; A versioned 24 kHz acceptance profile and packet-level telemetry schema shared by firmware, relay, and dashboard; A relay endpoint that correlates uplink/downlink sequence numbers and emits a signed per-call quality receipt; Dashboard and spoken-result UI for the guided test and retention controls; A product hardware decision: the current nRF9160 DK capture is 15,625 Hz and LTE-M is effectively half-duplex; a real product needs an audio-capable MCU/radio budget

### "When my pendant call becomes unreliable, move the live conversation to the best available surface—Mac microphone/speaker or phone—without making me repeat myself, then return it to the pendant when the link recovers."
- **useful because:** Today an LTE-M drop simply loses speech. The owner should be able to keep talking while walking between coverage and Wi‑Fi, with one continuous conversation and no manual reconnection or repeated context.
- **path:** pendant → relay-realtime → relay → mac-planner → mac-vision → iOS → dashboard-ux
- **model tier:** Use deterministic link/audio state machines for detection and handoff. Use the realtime model only for the ongoing conversation; do not invoke a second model for transport changes.
- **latency:** Detect degradation within 500 ms, announce a brief local cue within 250 ms, and complete a prepared Mac/phone handoff within 2 seconds. Preserve the current turn and buffered audio; do not wait for an LLM response to switch surfaces.
- **cost:** Negligible model/API overhead; transport signaling and a short-lived duplicate audio buffer dominate. A few kilobytes of encrypted session metadata per handoff.
- **security:** Only pre-authorized devices in the owner’s account may receive audio. Never activate a Mac or phone microphone without an explicit paired-device consent and visible indicator. Encrypt handoff tokens, expire them quickly, and discard duplicated audio after acknowledgement. A physical pendant gesture must cancel handoff.
- **missing:** A session-level media abstraction with simultaneous standby legs and deterministic source selection; Mac and iOS low-latency audio endpoints that can join an existing relay session, not just start a new call; A resumable turn/sequence protocol with replay protection and bounded encrypted audio buffering; Pendant haptic/LED and one-button UX for accept, cancel, and return-to-pendant; A privacy-preserving pairing and microphone-activation consent flow across dashboard, Mac, and iOS


## Changes it proposed to its own stack

### `firmware` — Add an offline `audio_diag` state machine to the pendant: on a long-press (or a relay-issued authenticated test command), generate a short coded chirp/voice-free stimulus through the ESP32 playback path, capture the mic response, and emit only aggregate diagnostics (RMS/noise floor, clipping, estimated round-trip delay, I2S underruns, Opus encode/decode timing, sequence counters, and firmware/profile ID). During live calls, append compact uplink/downlink loss/jitter and codec-profile counters to the hangup receipt. Keep raw samples in a bounded ring buffer only while testing, then erase them.
- **owner gets:** They can distinguish a blocked microphone, a bad speaker path, codec starvation, and LTE congestion in one minute instead of guessing or sending another failed call. It also makes the promised 24 kHz path measurable rather than a label in configuration.
- effort: Medium-high: Zephyr state machine and I2S/ESP32 bridge protocol, authenticated command plumbing, relay receipt schema, and dashboard rendering; test on the DK first, then repeat on the product audio design.  ·  risk: A test tone could be audible or interrupt a call; gate it to idle, require a deliberate long press, and provide a local mute/abort. Counter rollover or old firmware can corrupt reports; version the schema and mark unsupported fields. Recovery is simply reboot plus discard of the bounded diagnostic state.
- cost: Negligible API cost and under a few KB of flash/RAM for counters and a small ring buffer; power cost is one short playback/capture burst. Product cost is likely a modest audio-capable MCU/codec and better microphone/amp, rather than adding cloud compute.  ·  latency: No measurable live-path latency if counters are updated lock-free; the idle diagnostic takes about 30–60 seconds and adds one small receipt after hangup.
- security: No raw audio leaves the pendant by default. Authenticate remote test commands, redact identifiers in receipts, encrypt transport, and apply short retention to diagnostic metadata.
- depends on: The link-aware duplex governor must expose its selected profile and counters rather than hiding them; A shared 24 kHz acceptance profile and audio telemetry schema; The ESP32 bridge must support a bounded test stimulus and timestamped response; A local output-mute latch/abort path for safe user control

### `hardware` — For the wearable revision, replace the DK's single 64 MHz nRF9160 audio workload with a small audio-capable companion (DSP/codec or higher-performance low-power MCU) connected over I2S, leaving the LTE modem responsible for transport only. Give the companion independent mic/earpiece clocks, hardware sample-rate conversion to a true 24 kHz profile, DMA ring buffers, and a wake/interrupt line for underrun and brownout markers; add a fuel gauge on the currently-unused I2C bus.
- **owner gets:** The owner gets intelligible duplex speech instead of a prototype that spends roughly 87% of one core encoding and decoding while its mic captures at 15,625 Hz, plays at 24 kHz, and its LTE-M link drops speech under simultaneous traffic. Battery and brownout evidence also stops false diagnoses of audio failures.
- effort: High: select and validate codec/MCU, redesign board and power rails/antenna coexistence, implement bridge protocol and firmware drivers, then run RF/audio certification and long-duration wear tests.  ·  risk: More components increase BOM, firmware surface, and power states; clock drift or bridge failures could be worse than today. Keep a bypass mode for the current path, watchdog the companion, and fall back to narrowband mono with an explicit LED code. Recovery path is firmware rollback plus companion reset.
- cost: Roughly $3–$12 incremental prototype BOM (audio companion/codec, gauge, passives) and tens of mW during calls; likely cheaper than paying cloud retries and failed conversations. No per-call API increase.  ·  latency: DMA and hardware conversion should reduce encode/decode contention and keep end-to-end audio under the current frame budget; startup may add <100 ms for companion wake.
- security: The companion should expose no debug transport in production, sign firmware, and clear its audio buffers on reset. Fuel and audio diagnostics remain metadata-only unless explicitly exported.
- depends on: Measured 24 kHz acceptance criteria and codec profile selection; A versioned nRF9160↔audio-companion protocol; Link-aware duplex governor and relay telemetry; Prototype power/RF coexistence measurements

### `integration` — Introduce a relay-owned live-session conductor with two-phase media handoff: the pendant, Mac, and iOS clients register capabilities and current audio sequence; the relay selects a primary leg, opens a muted standby leg, mirrors only encrypted sequence metadata, and commits the new leg after a health/consent acknowledgement. The conductor persists the conversation turn cursor and a bounded jitter/replay window so a handoff resumes at the exact unacknowledged audio boundary. On recovery, it performs the same commit in reverse rather than starting a new session.
- **owner gets:** A walk through a dead LTE patch or a low-battery pendant would no longer end a conversation. They could continue on the Mac or phone, hear exactly one response, and return to wearing the pendant without explaining what was missed.
- effort: High: a relay session state machine, authenticated multi-client signaling, real-time audio endpoint support in Mac/iOS, sequence-aware buffering in firmware, and failure-injection tests for simultaneous disconnects.  ·  risk: Two surfaces could speak at once, duplicate audio, or leave a microphone live. Use a single relay commit token, hard mute before activation, visible client indicators, a 3-second lease timeout, and an owner-configurable kill gesture on the pendant. If coordination fails, drop the standby leg and retain the original call rather than guessing.
- cost: Low API/model cost; relay memory and egress rise briefly during a handoff (bounded to a few seconds of encoded audio). iOS/Mac implementation and end-to-end test work are the main costs.  ·  latency: Adds no steady-state latency. Handoff target is under 2 seconds; worst case falls back to a concise local error cue and keeps the current leg.
- security: Expiring, audience-bound session tokens; explicit microphone consent; no raw audio persistence beyond the bounded encrypted replay window; audit every leg activation and commit.
- depends on: A shared audio sequence/receipt format and accurate packet health telemetry; Low-latency Mac and iOS audio clients capable of joining an existing relay session; A pendant-local cancel/mute gesture and reliable link-health signal; Relay session storage that can survive a Worker instance change


## What it asked for

_Nothing._
## Its own summary

Discovered the owner’s real priority is the 24 kHz path. The live prototype is materially mismatched (15,625 Hz capture, 24 kHz decode, 31,250 Hz I2S wire clock), CPU-heavy (~87% encode+decode), and LTE-M drops about 7.8 seconds of uplink during simultaneous speech. I added three non-duplicate proposals: a cross-surface guided quality check with per-call evidence receipts, an offline firmware audio_diag state machine with no raw-audio export, and a product hardware revision using a dedicated audio companion plus fuel gauge. Still needed: the actual firmware/relay implementation tools and the authoritative 24 kHz acceptance profile/compatibility target; a shared telemetry schema and bridge protocol; safe local mute/abort; and product-level power/RF/audio constraints. The current granted directory still reports empty, so no implementation grant is visible yet.

**Biggest unknown:** Whether the intended product can sustain true 24 kHz full-duplex audio over LTE-M at the target latency and power budget; the current DK measurements show it cannot, but the product hardware constraints and acceptance thresholds are not authoritative yet.

