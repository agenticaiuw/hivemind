# Harness derivation — faculty-perception — round 25

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-pipeline-observation** — The live pipeline currently records a cloud-relay input with PCM s16le, mono, 16-bit, sampleRate 15625 Hz and 937500 audio bytes; its response TTS is 24,000 Hz mono PCM (164650 bytes, 3430 ms), with 0 clipped samples. This is not end-to-end 24 kHz input.
  - evidence: GET /pipeline returned job_165a9c9a-e5e3-4e29-b500-2fad63115ab9 inputTelemetry.sampleRate=15625 and TTS event meta sampleRate=24000, clippedSamples=0.
- **mac-bridge-readiness** — Mac bridge and relay are reachable, but the Mac agent reports ready=false because Accessibility trusted=false and Screen Recording granted=false; browser extension home-chrome is offline with 3 pending commands.
  - evidence: GET /ops/snapshot returned relay.reachable=true and macBridgeOnline=true, permissions.accessibility.trusted=false, permissions.screenRecording.granted=false, ready=false, browser.online=false, pendingCommands=3.
- **timezone-consistency** — The owner's remembered timezone is America/Chicago, while the live Mac machine-context reports timezone America/New_York. This discrepancy is unresolved and could shift scheduled routines or spoken times.
  - evidence: discover(owner) remembered timezone America/Chicago; GET /machine-context returned machine.timezone America/New_York.

## Capabilities it proposed

### "Keep my schedules and spoken times correct even when my Mac, relay, and pendant disagree about the timezone."
- **useful because:** Today the owner can receive a plausible but wrong time or have routines run in the wrong local hour. A single cross-device time-truth layer would expose and resolve that before it affects them.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Background deterministic reconciliation; use realtime only when the owner asks for the current time or a schedule is imminent.
- **latency:** Under 100 ms for a current-time answer; under 1 minute for periodic reconciliation.
- **cost:** Negligible API cost for UTC offsets and device metadata; occasional text model call only for explaining an ambiguous timezone change.
- **security:** Timezone/location metadata can reveal travel patterns. Store only timezone ID/offset and source timestamps, not raw location; require confirmation before changing the owner's canonical timezone or moving existing routines.
- **missing:** Canonical timezone record with explicit owner confirmation and provenance; Pendant/relay/Mac heartbeat fields carrying UTC timestamp plus timezone ID and offset; A scheduler guard that refuses to silently execute when device timezone differs from canonical; Dashboard/voice explanation and confirmation flow for timezone conflicts

### "Run a one-minute audio health check and tell me whether my pendant is truly delivering wideband speech, not just playing 24 kHz output."
- **useful because:** The current system can render 24 kHz speech while capturing at 15,625 Hz and uplinking at 16 kHz, so playback alone gives a false sense of quality. A spoken calibration would expose the actual capture rate, resampling, packet loss, clipping, codec delay, and round-trip quality before the owner relies on it.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Deterministic DSP and protocol checks on the pendant/relay/Mac; use a cheap background model only to summarize the measurements in plain language, never to infer them.
- **latency:** About 60 seconds for a complete capture-to-playback test; under 2 seconds for a quick link/rate check.
- **cost:** Negligible model/API cost for numeric tests; roughly one short diagnostic audio upload per invocation. Storage can be discarded after the report.
- **security:** The test recording leaves the pendant and could contain the owner's voice. Use a generated calibration tone plus an optional scripted phrase, encrypt transport, delete raw audio by default, and require explicit confirmation before uploading the phrase.
- **missing:** A device-triggered calibration protocol that coordinates a known tone/phrase and loopback timestamps; Per-chunk immutable audio metadata and counters for actual capture rate, resampling, drops, clipping, and codec mode; Relay-side DSP report with packet and round-trip measurements, correlated to the Mac TTS/playback receipt; A concise owner-facing result that distinguishes capture quality from playback quality and identifies the exact component needing replacement or firmware change


## Changes it proposed to its own stack

### `hardware` — Replace the prototype's 15,625 Hz I2S capture plus 16 kHz Opus uplink with a clocked 24 kHz (or 48 kHz/2) microphone path and negotiated 24 kHz Opus frames end to end; carry the source sample rate in every audio chunk and reject silent resampling when it does not match the session contract. Keep 24 kHz playback, but make capture, relay transcription input, and archival PCM agree on one declared rate.
- **owner gets:** Speech would retain the high-frequency detail the owner asked for instead of being captured at 15.625 kHz, encoded at 16 kHz, and only rendered back at 24 kHz. Diagnostics would show when the wearable is genuinely operating in wideband mode.
- effort: High: select and validate a new microphone/clock configuration, update nRF9160 capture and Opus settings, relay transcoding, protocol metadata, and fixture tests; likely one hardware spin plus firmware work.  ·  risk: Higher CPU, radio bandwidth, and power draw; the current fixed-point codec already uses roughly 87% of one core when encode and decode overlap. Recover with a negotiated fallback mode (16 kHz narrowband) that is explicit in telemetry, never mislabeled as 24 kHz.
- cost: Prototype BOM increase roughly $3–$10 for a suitable digital mic/clock and board changes; modestly higher per-minute relay bandwidth and potentially 10–25% audio power depending on codec settings. API cost unchanged.  ·  latency: Potentially +5–15 ms codec/transport latency; preserve 60 ms packetization unless measurements require change.
- security: Audio still leaves the pendant for transcription; source-rate metadata is non-sensitive. Keep raw PCM retention opt-in and bounded.
- depends on: A protocol-level audio capability negotiation and source-rate invariant; Pendant firmware telemetry exposing capture rate and dropped/resampled frames; Relay transcription path that accepts and preserves the declared rate; End-to-end 24 kHz fixture recordings and objective quality tests


## What it asked for

### `c5-i54e` (context) — authoritative timezone
- why: Live machine-context says America/New_York but owner memory says America/Chicago; scheduled routines and spoken time need one canonical zone.
- would change: I would treat the confirmed zone as canonical in perception records and flag or reconcile any device/relay schedule that disagrees, rather than silently trusting the Mac.

## Its own summary

Fresh live evidence: the bridge/relay are reachable, but Mac readiness is false because Accessibility and Screen Recording are not granted; Chrome is offline with 3 queued browser commands. The pipeline's captured audio is 15,625 Hz while response audio is 24 kHz, so the path is not end-to-end 24 kHz. I recorded those facts plus a timezone conflict (owner memory America/Chicago vs Mac America/New_York), proposed a cross-node timezone truth/guard capability, and proposed replacing the prototype capture/uplink path with negotiated 24 kHz audio and explicit rate invariants. I asked the orchestrator to establish the authoritative timezone and notified mac-planner.

**Biggest unknown:** Which timezone is authoritative for the owner, and whether the 24 kHz objective means capture/uplink as well as playback; current hardware is explicitly prototype and captures at 15,625 Hz.

