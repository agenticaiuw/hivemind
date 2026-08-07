# Harness derivation — mac-planner — round 121

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Verify my pendant’s 24 kHz audio path end to end, including while I’m speaking over the agent, and tell me whether it passes.”"
- **useful because:** The current prototype claims 24 kHz playback but measured LTE-M contention drops about 7.8 seconds of uplink speech. The owner needs an objective go/no-go result, not another codec setting: a repeatable test can distinguish codec quality, resampling defects, and half-duplex congestion before they rely on the pendant.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Use the cheap background model for test planning and report generation; reserve realtime only if the owner is actively listening to the test call.
- **latency:** A scheduled or on-demand run may take 2–5 minutes. The spoken result should be one short sentence plus a link to the detailed receipt.
- **cost:** Usually <$0.05 per run; dominated by one short controlled realtime audio session and storage of telemetry, not reasoning.
- **security:** Use synthetic prompts/test tones by default and redact transcript/audio payloads. Do not open the Mac microphone. Require explicit opt-in before recording real speech; retain only aggregate packet loss, jitter, decode underruns, and MOS proxy, with automatic deletion.
- **missing:** A firmware diagnostic mode that emits timestamped sequence-marked uplink frames and accepts a known playback fixture without opening the microphone.; Relay-side per-call telemetry correlating sequence gaps, LTE-M retransmits, Opus decode time, and resampler underruns in one trace.; A deterministic contention scenario that makes the agent speak while the pendant uplinks, plus pass/fail thresholds for intelligibility and loss.

### "“Let me have a genuinely natural, full-duplex 24 kHz conversation from the pendant—even when the agent is speaking—without my speech disappearing or the audio silently falling back to narrowband.”"
- **useful because:** Today’s measured LTE-M link is half-duplex in practice and simultaneous 16 kbps uplink plus 24 kbps downlink drops about 7.8 seconds of speech. A quality test can diagnose that, but it cannot make the owner’s everyday conversations reliable. This capability requires making the wearable’s transport and audio hardware sufficient for the experience rather than merely labeling the prototype superwideband.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Realtime model for the live conversation; a small background controller should handle codec/transport negotiation and quality telemetry so the expensive model is not used for transport decisions.
- **latency:** Under 150 ms conversational one-way latency in good coverage; under 300 ms during adaptation. Any mode change should be under one frame and audible only as a brief, intelligible status cue.
- **cost:** Realtime inference cost is unchanged for ordinary speech. Hardware redesign is the dominant cost: roughly $15–35 per prototype unit for a stronger cellular/audio subsystem, plus engineering and certification; modest additional relay telemetry storage.
- **security:** Audio remains encrypted end to end. Quality adaptation must not upload raw diagnostic samples by default. The pendant should indicate degraded or buffered mode, and the owner should be able to disable recording/telemetry independently of conversation.
- **missing:** A product-class wearable architecture with a dedicated audio DSP or second core so Opus encode/decode does not consume ~87% of the current single core.; A cellular transport with reliable simultaneous uplink/downlink capacity above the current LTE-M contention point, or a designed Wi-Fi/Bluetooth-to-phone fallback that is seamless and explicitly indicated.; A jitter buffer and packet-priority scheduler that protects owner speech over agent playback without creating an unbounded delay.; Negotiated 24 kHz capability metadata across pendant, relay, and playback endpoint, with an honest degraded-mode indicator rather than silent resampling.


## Changes it proposed to its own stack

### `integration` — Create an end-to-end audio acceptance harness that propagates one testRunId from pendant diagnostic frames through relay Opus/transcode and pipeline events into a Mac-collected receipt. The harness should run fixed fixtures (silence, speech-shaped noise, bidirectional contention), align uplink/downlink timestamps, calculate packet loss/jitter/decode CPU/resampler underruns and a conservative MOS proxy, then publish a signed pass/fail artifact with raw audio omitted by default. Add a regression threshold so a firmware or relay change cannot claim 24 kHz support without passing both idle and contention cases.
- **owner gets:** They get a trustworthy answer to “does this work?” and early warning when an update makes calls lose speech or sound narrowband. It directly addresses the measured contention failure instead of hiding it behind a nominal sample-rate label.
- effort: Medium: firmware diagnostic event format, relay trace aggregation, a Node/Python-style fixture runner, and a small dashboard receipt view. No new model training required.  ·  risk: Bad clock alignment or overly strict thresholds could produce false failures; recover with a calibration fixture and versioned thresholds. Never treat synthetic-test success as proof that real speech is safe; label the result accordingly.
- cost: Negligible API cost; one short synthetic run and small metadata receipt. Storage drops substantially if raw audio is not retained.  ·  latency: Adds no production call latency. A test run takes roughly 2–5 minutes.
- security: Synthetic fixtures by default, no Mac microphone, redacted identifiers, signed receipts, and TTL deletion for any optional captured samples.
- depends on: A pendant diagnostic event/fixture mode; Relay correlation IDs and per-packet telemetry; A defined 24 kHz acceptance threshold and clock calibration


## What it asked for

### `s16-dbfs` (skill) — audio_path_diagnostic_fixture
- does: On a deliberate diagnostic trigger, the pendant emits timestamped sequence-numbered synthetic uplink frames and plays a fixed 24 kHz verification fixture. It reports capture clock, Opus encode duration, modem send/drop counters, playback decode duration, resampler underruns, and fixture completion; it never records or persists microphone content. It can stop immediately on button press or server command.
- must be on-device because: Only firmware can measure the real I2S clock, Opus CPU budget, modem queue drops, and speaker-side underruns at the exact frame boundary, and it must work when the LTE link is degraded.
- trigger: Long button press, or a signed diagnostic command from the relay during an explicitly requested test; never on ordinary calls.
- storage: No persistent audio. A compact 256-byte rolling diagnostic record in RAM and one final event of roughly 1–2 kB sent upstream; discard after acknowledgement.
- RAM budget: About 2–4 kB for counters, timestamps, and the fixture state machine, plus reuse of existing Opus buffers; well below the 211,608 B application RAM, but must be measured against the current ~87% single-core encode+decode load.

## Its own summary

Discovered the live fleet and hardware constraints. The pendant is an nRF9160 with 211,608 B app RAM; Opus encode+decode consumes ~87% of one core, and LTE-M contention has already dropped ~7.8 seconds of uplink speech. I proposed and recorded a genuinely connective end-to-end audio acceptance harness, plus a firmware diagnostic fixture skill that uses synthetic audio only. I also sent the telemetry requirement to relay-realtime. The newly granted Mac inspection tool is still schema-only: calling it returned “no implementation yet,” so it cannot currently verify running apps, foreground state, or Accessibility status.

**Biggest unknown:** Whether the orchestrator will implement the granted Mac read/execute tools and the relay/firmware telemetry hooks. Until those exist, I cannot run the acceptance test or produce a real pass/fail receipt; I need implementation of the already-granted tools and the three dependencies named in the proposal, not another permission request.

