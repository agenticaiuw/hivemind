# Harness derivation — unified — round 89

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Changes it proposed to its own stack

### `integration` — Add a session-level multipath audio controller. The pendant publishes link quality, queue depth, sequence number, and current route; the relay maintains a jitter buffer and deduplicates overlapping packets; a paired Mac/iOS companion can carry encrypted Opus frames over a local authenticated channel. Use hysteresis to switch LTE-M ↔ companion, send a short route-transition marker, and resume from the last acknowledged sequence. Record a receipt with route, gap/overlap duration, and recovery outcome.
- **owner gets:** Speech will not disappear merely because the pendant and the network are contending; the owner can keep talking naturally while the nearest capable device carries the bytes.
- effort: High: protocol and relay changes, native Mac/iOS audio service, pendant firmware changes, pairing UX, and RF/link fault-injection tests.  ·  risk: A bad handoff could duplicate speech, expose audio to the wrong companion, or create loops. Mitigate with device-bound keys, monotonic sequence validation, one active sender per direction, explicit fail-closed behavior, and a replayable receipt. If the companion dies, return to LTE rather than queueing indefinitely.
- cost: No steady-state API increase; modest relay CPU/R2 metadata for receipts. Mac/iOS battery rises during calls from microphone/network use. Hardware cost is none for the prototype, though a production pendant needs a radio design that supports the chosen local path.  ·  latency: Adds roughly 100–300 ms jitter-buffer headroom and up to 1 s during a route change; healthy-path latency unchanged.
- security: Adds a new local audio trust boundary. Pairing must be user-mediated, keys stored in platform secure storage, transport encrypted, and route changes auditable. No audio should be copied to R2 unless existing retention policy permits it.
- depends on: The pending link-aware duplex governor and end-to-end audio acceptance criteria; A companion audio endpoint on Mac/iOS; An authenticated pairing/key-management primitive; A relay jitter buffer with sequence-aware deduplication

### `hardware` — Replace the single-microphone prototype with a production acoustic front end: a two- or three-microphone near-field array on the pendant, a dedicated low-power audio DSP/codec for beamforming, echo cancellation, and wind/noise suppression, plus a Mac/iOS calibration routine that measures the worn device’s actual microphone and speaker response and stores a signed per-device profile. The relay must attach that profile and acoustic-quality telemetry to each live session so the realtime model can distinguish a bad utterance from a bad radio link.
- **owner gets:** The owner should be able to speak naturally while walking, in wind, or beside a laptop playing audio, and have the system recover intelligible speech instead of silently mishearing them. Today’s single I2S microphone and prototype bridge provide no spatial rejection or device-specific calibration.
- effort: High: redesign the pendant audio board and enclosure, add DSP firmware and a production calibration fixture, implement Mac/iOS calibration and profile provisioning, and add relay/model handling for acoustic-quality telemetry. This is a product-hardware change, not a patch to the current DK.  ·  risk: More microphones, DSP firmware, and calibration data add power draw, BOM cost, and failure modes; poor beamforming could suppress the owner. Recover with a hardware bypass/reference mode, signed versioned profiles, an on-device calibration validity check, and a manufacturing acoustic test before shipping.
- cost: Roughly $8–$25 additional production BOM plus a few tens of milliwatts while active, and one-time calibration-fixture cost. No meaningful per-call API increase; better capture may reduce retries and repeated turns.  ·  latency: A dedicated DSP should add under 10 ms; the Mac/iOS calibration step is offline and does not affect conversation startup after provisioning.
- security: Calibration profiles are device metadata, not conversation content, but must be authenticated to prevent malicious DSP parameters. Acoustic telemetry should be coarse and retained only with the session receipt; raw microphone data remains in the existing encrypted audio path.
- depends on: A production pendant audio-board/enclosure design rather than the nRF9160 DK; The 24 kHz end-to-end audio acceptance thresholds; A signed device-profile provisioning path shared by pendant, relay, Mac, and iOS


## What it asked for

_Nothing._
## Its own summary

Fresh discovery confirms the owner’s actual goal is still end-to-end 24 kHz audio, while the live prototype is 15.625 kHz capture, 24 kHz decode, and LTE-M contention that recently lost ~7.8 seconds of uplink speech. I recorded a new integration change: authenticated multipath audio with a paired Mac/iOS companion, sequence-aware relay deduplication, jitter buffering, hysteretic LTE↔companion handoff, and a route-transition receipt. The capability wording itself was rejected as already covered by an existing backlog item, so I did not restate it. I still need: the product audio target/acceptance thresholds, the owner’s companion privacy boundary, an authenticated pairing/key primitive, a Mac/iOS low-latency audio endpoint, and fault-injection validation. The granted category currently reports zero new grants, so no newly granted tool or device skill is visible in this round.

**Biggest unknown:** Whether the owner permits live microphone/audio to traverse a paired Mac or phone companion, and what exact end-to-end latency, loss, and handoff-gap thresholds define acceptable 24 kHz service.

