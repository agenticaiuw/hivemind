# Harness derivation — faculty-judgement — round 55

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-path-limitation** — Current pendant is prototype: 15,625 Hz I2S mic and 16 kHz/16 kbps Opus uplink, while playback decodes 24 kHz/60 ms and resamples to 31,250 Hz. Simultaneous encode/decode uses ~87% of one 64 MHz core, and LTE-M contention recently dropped 388 uplink packets (~7.8 s) during simultaneous speech.
  - evidence: get_hardware_spec audio, pendant, and network responses in Round 55

## Capabilities it proposed

### "“Do this, and tell me only when you can prove it worked.”"
- **useful because:** Today the system can execute typed actions and return receipts, but a receipt is not proof—especially while Mac Accessibility and Screen Recording are unavailable. This gives the owner a dependable distinction between completed, observed-complete, and unable-to-verify, instead of confident false success.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal → mac-vision → dashboard-ux
- **model tier:** Use the realtime model only for the owner's short confirmation and spoken status; use gpt-5.6-luna for planning/contracts and a cheap background verifier for polling/re-observation. Use mac-vision only when permissions make visual observation trustworthy; otherwise prefer typed shell/browser evidence.
- **latency:** Immediate acknowledgement under 1 s; reversible actions within 5–10 s; background jobs can finish later. If verification is delayed, the pendant says it is still checking rather than claiming success.
- **cost:** Roughly 1 planning call plus a cheap verification call per action; about $0.01–$0.05 for normal tasks, dominated by model context and any screenshot/vision upload. Realtime cost is limited to the spoken interaction.
- **security:** Evidence may include private page text or file paths, so keep it local to the Mac/relay and redact secrets from receipts. Never infer success from a UI toast; require a typed postcondition or fresh observation. Sending mail, deleting files, or buying still requires confirmation even if the postcondition is satisfiable.
- **missing:** A typed expected-postcondition field in every action/job contract; A re-observe verifier that can refuse success on mismatch or stale evidence; Permission-aware routing that marks visual evidence unavailable when Accessibility/Screen Recording are false; A compact pendant receipt format for verified/failed/unverified states; Dashboard history linking intent, action, evidence, and final state

### "“Keep the conversation natural, even when the connection is busy or I talk over you.”"
- **useful because:** The owner should be able to wear the pendant as a dependable conversation instrument rather than losing several seconds of their speech during talk-over. It should preserve the beginning of an interruption, keep playback intelligible, and recover without making them repeat themselves; the current prototype cannot do that.
- **path:** pendant → relay-realtime → unified → faculty-perception
- **model tier:** Use gpt-realtime only for the live turn-taking loop. Put congestion estimation, jitter buffering, packet-loss concealment, codec negotiation, and replay of a recovered interruption in firmware/relay code; do not spend model tokens on transport repair.
- **latency:** Local button/voice barge-in response under 100 ms; conversational audio one-way target under 120 ms; congestion mode switch under 300 ms; never queue more than one frame of stale speech.
- **cost:** Near-zero incremental model API cost; engineering and bandwidth dominate. A production audio board/DSP and validation fixture are the main expense, with modest additional device power. 24 kHz full-duplex traffic may increase radio usage, so adaptive mode must protect battery and data budget.
- **security:** Keep audio and transport telemetry TLS-protected. The relay may retain at most a tiny encrypted, expiring interruption buffer solely for loss recovery; never turn it into a transcript or durable recording without explicit consent. Authenticated codec negotiation prevents downgrade or injection.
- **missing:** A product microphone/MCU/DSP capable of sustained 24 kHz capture and decode without consuming nearly the entire application core; A bounded full-duplex scheduler with admission control, jitter buffering, packet-loss concealment, and interruption sequence numbers; Relay support for codec/profile negotiation and selective retransmission or forward-error protection within the LTE-M record limit; A firmware/relay acceptance harness that measures speech loss, barge-in latency, intelligibility, and battery under simultaneous talk-over; A clear fallback policy that preserves continuity rather than allowing seconds of queued audio


## Changes it proposed to its own stack

### `hardware` — Replace the DK-era single-core audio path with a product audio design: a 24/32 kHz-capable digital microphone and an audio-capable dual-core MCU (or dedicated low-power DSP) with enough RAM for two Opus frame rings. Pair it with an adaptive full-duplex transport: 24 kHz superwideband by default, explicit uplink/downlink bandwidth admission, packet-loss concealment, and a deterministic fallback to narrowband before queue growth can cause multi-second speech loss. Add an end-to-end acceptance test that measures intelligibility, one-way latency, packet loss, and battery under simultaneous talk-over.
- **owner gets:** The pendant would sound natural and remain usable when both of you speak. Today the microphone is not actually superwideband and the radio/core budget demonstrably loses seconds of the owner's speech during talk-over; a codec label alone cannot fix that.
- effort: High: product audio schematic and enclosure revision, firmware ring-buffer/clock work, relay negotiation, and a hardware-in-loop test fixture. Prototype a transport fallback on the DK first, then bring up the production audio board.  ·  risk: A new board and clock domain can introduce power, EMI, and echo problems; adaptive downgrade could sound inconsistent. Recover with a hard codec profile version, feature flag, packet/clock telemetry, and keep the current 16 kHz path as a rollback until field trials pass.
- cost: No meaningful per-call API increase if Opus remains; prototype board roughly $30–$80 BOM increment, with a few mW to tens of mW additional audio/DSP draw depending on MCU.  ·  latency: Target 60–120 ms one-way audio plus bounded jitter; fallback must happen within 300 ms of congestion rather than waiting for seconds of queued audio.
- security: Audio remains TLS-protected; new telemetry should contain packet counts and codec state only, never audio. Firmware images and codec-profile negotiation must be authenticated.


## What it asked for

_Nothing._
## Its own summary

Round 55 produced two new actions beyond the backlog: (1) a product-grade 24 kHz audio architecture with adaptive congestion fallback and hardware-in-loop acceptance gates, grounded in the current 15.625 kHz mic, 87% single-core load, and observed 7.8 s uplink loss; (2) a cross-surface capability that refuses to claim success without a typed postcondition and fresh evidence, routing around currently untrusted Mac UI receipts. I recorded the audio limitation as a finding.

**Biggest unknown:** The actual 24 kHz acceptance thresholds and whether the owner will authorize the required Mac Accessibility/Screen Recording and browser-bridge permissions remain unresolved; current live evidence says visual/input automation must be treated as unavailable.

