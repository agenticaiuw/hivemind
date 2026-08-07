# Harness derivation — faculty-action — round 78

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-path** — Current prototype is asymmetric: I2S mic capture is 15,625 Hz and uplink Opus is 16 kHz/16 kbps, while playback decodes at 24 kHz over 60 ms frames and resamples to a 31,250 Hz bridge wire clock. There is no verified end-to-end 24 kHz capture acceptance result yet.
  - evidence: get_hardware_spec(audio) returned mic 15,625 Hz, uplink 16 kHz, playback 24 kHz and 31,250 Hz wire clock; owner memory says ship the 24 kHz superwideband path end to end.

## Capabilities it proposed

### "“Before my next call, verify that my pendant audio is healthy; if it is not, fix what you can and tell me exactly what failed.”"
- **useful because:** Today the mind can decide that audio quality matters but cannot establish which hand is broken. This gives the owner a one-sentence preflight result and an automatic, reversible recovery path instead of discovering a bad mic, relay profile, or bridge playback after the call starts.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → dashboard
- **model tier:** Use the realtime tier only to interpret the spoken request and announce the result; use a cheap background/local worker for metric comparison, packet accounting, and receipt generation.
- **latency:** Interactive preflight under 10 seconds; fallback/reconnect may continue in background with a completion receipt.
- **cost:** Usually under $0.01 per preflight, dominated by one short audio/test exchange and storage of metrics; no expensive model call is needed after intent parsing.
- **security:** The pendant generates a synthetic test signal and should not upload ordinary speech. The relay receives only counters and timestamps; any Mac repair action must be limited to reversible audio-route/profile changes and produce an undoable receipt. Require confirmation before changing unrelated system audio or starting a microphone.
- **missing:** pendant-local calibration chirp/capture test and counters; relay-side 24 kHz profile validation and safe fallback; Mac-side audio route/bridge health probe without opening the microphone; typed conformance receipt and owner-defined pass thresholds


## Changes it proposed to its own stack

### `integration` — Add a cross-surface 24 kHz audio conformance sentinel: a pendant firmware test mode emits a short locally generated calibration chirp and captures a timestamped reference window; the relay tags each Opus packet with sequence, source sample-rate, encode/decode timestamps, and loss markers; the Mac harness runs the test on demand and stores a compact receipt (measured capture rate, decoded rate, jitter, packet loss, underruns, CPU headroom) in the job receipt. The relay rejects silently mislabelled 16 kHz packets and selects a safe fallback profile rather than claiming superwideband success. Expose the latest pass/fail and failure stage through the existing pipeline/job status surfaces.
- **owner gets:** The owner can ask “is my pendant audio really 24 kHz?” and get a trustworthy answer instead of subjective audio quality or a green connection light. Regressions become actionable (mic clock, Opus profile, relay transcode, bridge playback, or underrun) and the system can preserve intelligible speech when the wideband path is unhealthy.
- effort: Medium-high: firmware test capture/generator and counters, relay packet metadata/validation, Mac test orchestration, and dashboard/receipt rendering. Requires one hardware-in-loop session for calibration.  ·  risk: A bad calibration threshold could report false failures or force an unnecessary fallback; keep test mode explicit, retain raw audio only in RAM, and make fallback reversible. No Accessibility or Screen Recording is required. Recover by rerunning the sentinel after link stabilization and keeping the last known-good profile.
- cost: Negligible API cost; one short test packet burst and a small D1 receipt. Engineering time is the main cost.  ·  latency: No steady-state latency change. An explicit test takes roughly 2–5 seconds; packet tagging adds only a few bytes per frame.
- security: Calibration audio should never leave the pendant; only numeric metrics and hashes cross the relay. Receipts must avoid retaining speech content or sensitive waveform data.
- depends on: 24 kHz acceptance criteria from the owner; permission to inspect/build the pendant firmware and connected serial/J-Link devices; an authenticated pendant-to-relay test trigger and a typed audio receipt schema

### `hardware` — Replace the prototype audio front end with a native 24 kHz-capable capture and playback clock domain: use a microphone/codec path whose actual sample clock supports 24 kHz (or an integer-related clock with verified low-jitter conversion), add an independent audio DMA clock rather than deriving capture from the current 15,625 Hz path, and give the bridge a negotiated clock/profile contract. The firmware, Opus configuration, relay, and acceptance tests must all advertise measured rates rather than hard-coded labels.
- **owner gets:** The owner gets genuinely superwideband speech instead of a 16 kHz uplink being relabeled or reconstructed as 24 kHz on playback. Voices, environmental cues, and transcription quality improve, and the pendant remains reliable when the network changes because both ends agree on the real clock and profile.
- effort: High: select and prototype a production audio codec or I2S microphone clocking scheme, revise the pendant/bridge PCB or carrier, update Zephyr drivers and DMA buffering, then requalify Opus, RF power, thermal behavior, and enclosure acoustics. This is a product-hardware change, not a simulator-only patch.  ·  risk: A new clock tree can introduce drift, buffer overruns, RF interference, or higher power draw; the development kit must remain supported as a compatibility profile during migration. Recover with a negotiated 16 kHz mode and hardware-in-loop drift tests before deployment.
- cost: Prototype engineering plus roughly $8–$25 per production unit for codec/clock/audio components and PCB changes; likely tens of milliwatts additional draw depending on codec. API cost is negligible.  ·  latency: Potentially neutral or slightly lower once DMA is correctly clocked; initial buffering and resampling tests may add 10–30 ms until tuned.
- security: No new cloud data is required. Keep raw microphone samples local except during an explicitly active call; expose only negotiated profile and health metrics to the relay.
- depends on: Owner-defined 24 kHz acceptance criteria; Firmware inspection/build access and serial/J-Link hardware-in-loop testing; The previously proposed end-to-end conformance sentinel to prove the new clock path


## What it asked for

_Nothing._
