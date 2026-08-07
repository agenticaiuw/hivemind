# Harness derivation — mac-planner — round 142

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-path-diagnostics** — Current audio is prototype: pendant captures 15,625 Hz and uplinks Opus 16 kHz/16 kbps; playback decodes Opus at 24 kHz in 60 ms frames and resamples to 31,250 Hz I2S. Decode is ~25.4 ms per frame and encode ~15 ms, ~87% of one core when both run. No conformance receipt or local self-test is established yet.
  - evidence: get_hardware_spec(audio) and get_hardware_spec(pendant), Round 142

## Capabilities it proposed

### "When my pendant audio sounds wrong, say “diagnose the audio path” and tell me exactly whether the fault is the pendant, relay, network, or Mac playback; save a repair-ready report without recording my microphone."
- **useful because:** Today the owner can hear a failure but cannot localize it. This would turn an intermittent wearable audio problem into a concrete component-level diagnosis and a reproducible report for the next firmware change, while preserving privacy by using synthetic test audio and device counters rather than microphone recordings.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Use a cheap background model for threshold comparison and report generation; reserve realtime only for interpreting the owner's spoken trigger and delivering the short result.
- **latency:** A deliberate diagnostic should complete in 10–20 seconds. The owner receives a concise spoken verdict immediately, with the detailed report available on the Mac afterward.
- **cost:** Low: one bounded synthetic test and a small JSON receipt per invocation; model cost is dominated by the final explanation, not audio transport. No stored audio is required.
- **security:** The pendant must never open its microphone for this command. Test packets need authenticated correlation IDs and an unmistakable diagnostic marker so they cannot be played as user content. Reports should contain firmware/build and timing counters but redact network identifiers before any cloud retention. No confirmation is needed because the operation is read-only and creates only a local report.
- **missing:** A pendant-local diagnostic gesture or command handler that exercises decode/I2S offline and emits compact counters; Authenticated relay test-mode support with packet sequencing and correlation IDs; A shared diagnostic schema covering decode time, PLC, underruns, packet gaps, clock drift, clipping, and resampling; A Mac-side receipt parser that writes a repair-ready report into ~/AI-Pendant-Workspace/audio-diagnostics; Fixed test vectors and thresholds for distinguishing pendant, relay, network, and Mac playback faults

### "If my pendant loses the audio link during a briefing or call, keep the conversation usable: switch the output to my Mac, remember the exact playback position, and resume on the pendant when the link recovers without replaying or losing content."
- **useful because:** Today a brief or live response can simply become unusable when the wearable radio or decoder stalls. A coordinated handoff would make the system dependable in real life: the owner keeps hearing the current response, and the pendant later resumes from the correct frame instead of restarting or silently dropping audio.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Use deterministic firmware and relay state machines for detection, buffering, and cursor handoff; use no expensive model for the failover itself. A cheap background model may summarize a failed job only after recovery.
- **latency:** Detect a stalled link within two audio frames and switch to Mac playback within 1–2 seconds. Resume on the pendant within 2 seconds after a stable reconnect.
- **cost:** Negligible model cost. Network and storage cost is limited to a short encrypted rolling audio buffer, typically tens of seconds per active response.
- **security:** The rolling buffer contains private spoken responses and must be encrypted, bounded, and deleted after acknowledgement or expiry. Mac takeover must use an explicit preconfigured output device and never activate the microphone. Resume tokens must be scoped to one session and invalidated after completion.
- **missing:** A shared playback cursor and resumable frame protocol between relay and pendant; A pendant heartbeat that distinguishes radio loss, decoder stall, and speaker-path failure; A bounded encrypted relay buffer with expiry and duplicate suppression; A Mac audio-output takeover route and restoration hook; A user-visible status indicator on the pendant/dashboard so failover is not silent


## Changes it proposed to its own stack

### `integration` — Build an end-to-end 24 kHz audio conformance loop spanning relay, pendant, and Mac: the relay emits a versioned synthetic sweep and spoken test packet through the production Opus/transcode path; the pendant reports per-frame decode/PLC/underflow/timing counters over its existing UART/telemetry channel; the Mac harness captures the return diagnostics, computes packet-loss, latency, clipping, and resampling checks against fixed thresholds, and writes a signed JSON receipt plus a human-readable bug report into ~/AI-Pendant-Workspace/audio-diagnostics. Run it on firmware/codec changes and on demand from the dashboard, with no microphone opened.
- **owner gets:** The owner can tell whether a bad-sounding 24 kHz briefing is caused by the network, relay transcoding, firmware decode, clock/resampling, or the speaker instead of guessing or reflashing. It directly advances the requested superwideband path and turns the pendant's existing UART bug-report idea into actionable evidence.
- effort: Medium-high: define a deterministic fixture and schema, add lightweight firmware counters, add relay test mode, and add a Mac receipt/parser plus dashboard trigger. Firmware work must stay within the 211,608 B application RAM budget; counters and a compact ring buffer should be under 4 KB RAM.  ·  risk: A test packet must never be mistaken for owner audio; require an explicit diagnostic trigger and tag every test frame end-to-end. Counters can expose device/network identifiers, so redact them in cloud receipts and retain raw UART locally. If a component is offline, report the exact missing leg rather than passing the test. Recovery is simply disabling test mode; no production audio settings are changed.
- cost: Negligible per routine run (small synthetic packets and one compact receipt); implementation cost is engineering time. Storage is a few KB per run locally, with no need to retain audio recordings.  ·  latency: On-demand test takes roughly 5–15 seconds and runs out of band; normal conversational audio latency is unchanged.
- security: No microphone or private page data is needed. Relay test mode must be authenticated and reject arbitrary packet injection; local reports should inherit workspace permissions.
- depends on: A firmware/relay diagnostic telemetry contract for 24 kHz decode, PLC, underflow, and clock counters; A deterministic audio fixture and validation thresholds (the pending audio_path_diagnostic_fixture request); A Mac-side read-only diagnostic parser/receipt writer, or an equivalent local-agent route; The production 24 kHz playback path being enabled end to end


## What it asked for

### `s17-ntok` (skill) — offline_audio_path_self_test
- does: On a deliberate long-press-plus-click gesture, the pendant plays a short locally stored diagnostic chirp/voice marker, exercises the 24 kHz decode and 31.25 kHz I2S playback path, records compact counters (decode time, underrun, PLC, sequence gap, peak/clipping), and emits a signed diagnostic event over the next available link. It never opens the microphone and never sends test audio as a normal conversation.
- must be on-device because: The key failures are in the pendant's decoder, scheduler, clock, and I2S wire path; the server cannot observe those accurately, and the test must still work when the link is degraded or absent. Local trigger also prevents accidental remote test injection.
- trigger: A deliberately documented two-stage button gesture (for example, hold 2 seconds, release, then click); alternatively a server diagnostic command may arm but not trigger it.
- storage: A compact 2–4 KB rotating diagnostic record in flash/NVS plus a <1 KB built-in test vector in flash; persist only the latest few results until acknowledged.
- RAM budget: About 3–6 KB worst case: counters/state, one small compressed test buffer, and a bounded event record. No second audio stream or large waveform buffer; stay comfortably within 211,608 B application RAM and avoid increasing Opus working memory.

