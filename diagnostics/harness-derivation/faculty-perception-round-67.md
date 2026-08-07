# Harness derivation — faculty-perception — round 67

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-perception** — At 2026-08-07T12:32Z the Mac local agent is online v0.5.0 and relay reachable, but Accessibility and Screen Recording are still not granted; /observe reports inputReachability failed and UI actions cannot be trusted. AppleScript automation grants are present and requiredMissing is empty.
  - evidence: GET /ops/status and GET /observe returned permissions.accessibility.trusted=false, screenRecording.granted=false, inputReachability.status=failed, uiActionsWillReachTheScreen=false; automationMissing=[]; relay.reachable=true.
- **audio-perception** — The latest completed Mac pipeline response rendered 24,000 Hz mono s16le PCM successfully (75,734 bytes, 1,578 ms, zero clipped samples) and uploaded it to the relay for pendant playback. A separate realtime incoming job recorded 15,625 Hz mono PCM, not 24 kHz.
  - evidence: GET /pipeline response: TTS event metadata format=s16le, sampleRate=24000, channels=1, pcmBytes=75734, clippedSamples=0; realtime job inputTelemetry sampleRate=15625.
- **browser-perception** — The Chrome browser bridge is offline at observation time with five pending commands; durable browser sessions still list three tabs, including https://time.is/UTC and two form probes.
  - evidence: GET /browser/status and GET /observe returned online=false, pendingCommands=5, sessions=3 and the listed tab URLs.
- **timezone-perception** — Timezone sources disagree: owner memory says America/Chicago, while live Mac machine-context reports America/New_York. Do not silently use either for scheduling until resolved.
  - evidence: Owner discover output remembered timezone America/Chicago; GET /machine-context returned machine.timezone=America/New_York.

## Capabilities it proposed

### "Before you schedule anything, tell me which timezone the action will use and warn me if my Mac, calendar, or browser disagree."
- **useful because:** The live Mac reports America/New_York while the owner's remembered preference is America/Chicago. A contradiction-aware gate prevents reminders and calendar actions from silently landing an hour away, while still allowing ordinary reads and drafts.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for periodic reconciliation; realtime only for the owner's brief spoken confirmation when a conflict blocks an action
- **latency:** Under 2 seconds for a read; under 5 seconds for a proposed schedule with cited timezone evidence
- **cost:** Usually <$0.01 per check; most work is deterministic timezone/provenance comparison, with model tokens only for explaining an unusual conflict
- **security:** Timezone and event metadata leave the Mac only as typed facts; private calendar contents stay local unless the owner asks. Never create or modify an event until the owner resolves a conflict.
- **missing:** A typed timezone provenance record shared by relay, Mac planner, and browser session; A pre-action contradiction gate that can pause scheduling without pretending the action succeeded; Pendant UI/audio wording for selecting owner preference versus machine timezone

### "When I ask something by voice, let me later ask “Did that actually make it through?” and hear one truthful end-to-end receipt: what the pendant captured, what the relay transcribed, what the Mac/browser did, what answer was rendered, and whether the pendant confirmed playback—with any missing leg clearly named."
- **useful because:** Today the system can report a completed Mac job or uploaded audio, but cannot establish that the owner's spoken request survived every boundary and was actually heard back on the wearable. This gives the owner a trustworthy answer after LTE drops, browser disconnects, stale queues, or misleading UI receipts.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic event correlation and a cheap background summarizer; realtime is used only when the owner asks verbally for the receipt.
- **latency:** Capture and acknowledgements stay on the existing path; receipt lookup under 1 second, spoken summary under 2 seconds.
- **cost:** Below $0.01 per lookup; storage is small typed event metadata, while audio/transcripts remain under existing retention policy.
- **security:** Receipts may expose private transcript snippets and authenticated URLs. Encrypt them, redact secrets and page contents by default, retain only hashes plus short labels, and require explicit confirmation to reveal verbatim audio or transcript.
- **missing:** A globally correlated conversation-attempt ID spanning pendant capture, relay transcription, Mac/browser work, TTS, and pendant playback; Signed monotonic acknowledgements from the pendant for capture, download, decode, and audible completion; A durable receipt ledger that distinguishes uploaded, processed, delivered, played, expired, and unknown rather than inferring success from HTTP 200; A compact spoken receipt renderer and dashboard drill-down


## Changes it proposed to its own stack

### `integration` — Make the audio contract honest and machine-verifiable across pendant, relay, and Mac: tag every PCM/Opus segment with capture rate, encoded rate, decoded rate, and resampler stage; add an automated loopback that proves the current 15,625 Hz mic → 16 kHz Opus uplink and 24 kHz Mac TTS → pendant decode paths separately. Reject or flag any event claiming '24 kHz end-to-end' when the source is 15,625 Hz, while preserving 24 kHz playback output and zero-clipping checks.
- **owner gets:** The owner hears reliable 24 kHz playback and can trust spoken status about audio quality instead of being told a 15,625 Hz microphone path is superwideband. Failures become diagnosable rather than silent.
- effort: Moderate: shared telemetry schema, relay validation, firmware loopback fixture, and pipeline dashboard assertions.  ·  risk: Older firmware/events may omit fields; treat missing metadata as unknown (not failure) and keep backward-compatible decoding. A false-positive contract warning is recoverable by replaying the loopback fixture.
- cost: Negligible API cost; a few kilobytes of metadata per job and occasional local test CPU. No hardware cost unless a future product microphone is changed.  ·  latency: No perceptible playback latency; validation is asynchronous. Loopback tests add CI time only.
- security: Metadata contains audio format only, no speech content. Keep waveform samples local to the fixture and do not upload them by default.
- depends on: A shared pipeline audio metadata schema; A relay-side invariant checker; A pendant firmware diagnostic event for actual I2S capture/playback rates


## What it asked for

_Nothing._
## Its own summary

Round 67 established four actionable truths: Mac relay path is online but UI input is not trustworthy because TCC grants remain absent; browser bridge is offline with five queued commands; Mac-generated speech is genuinely 24 kHz mono with zero clipping while mic input remains 15,625 Hz; and timezone evidence conflicts (owner America/Chicago vs live Mac America/New_York). I recorded these, notified unified/mac-planner, and proposed a timezone contradiction gate plus an audio format/provenance contract and loopback validation.

**Biggest unknown:** Authoritative pendant-side live diagnostics: whether the physical device actually receives, decodes, and plays the 24 kHz payload, and how queued/offline alerts are acknowledged. I still need the pending pendant diagnostics/continuity tools (and, separately, an owner decision on the timezone conflict and browser reconnection).

