# Harness derivation — faculty-perception — round 79

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **device presence** — Live device discovery shows no pendant: only home-macbook-bridge online, cloudflare-contract-test offline, and home-chrome offline. GET /v1/devices/status is not a route on the Mac agent.
  - evidence: discover(devices) at 2026-08-07T13:11Z returned exactly those three devices; probe GET /v1/devices/status returned 404.
- **Mac input truth** — AI Pendant Agent is not ready for trustworthy GUI input: Accessibility trusted=false, Screen Recording=false, inputReachability.status=failed, eventsPost=false; UI actions may report success while doing nothing. AppleScript automation grants are present.
  - evidence: GET /ops/snapshot and GET /observe at 2026-08-07T13:11Z.
- **audio pipeline truth** — Recorded pipeline demonstrates asymmetric formats: nRF9160 live LTE input telemetry is pcm-s16le mono 15,625 Hz (937,500 bytes), while Mac TTS output is s16le mono 24,000 Hz (75,734 bytes, 1,578 ms), with relay accepted output for later pendant download. This is historical telemetry, not a live pendant.
  - evidence: GET /pipeline response: pipeline job_165a... inputTelemetry.sampleRate=15625; job_309... TTS meta sampleRate=24000 and relay_result done.

## Capabilities it proposed

### "Did that actually reach me?"
- **useful because:** Today the system can prove that a Mac job ran, speech was rendered, and the relay accepted bytes, but it cannot distinguish that from audio being downloaded and played by the owner's pendant. This gives a concise, evidence-backed answer with a timestamped chain and says 'unknown—no pendant connected' instead of falsely claiming success.
- **path:** relay → mac-planner → pendant → dashboard
- **model tier:** Use a cheap background/text model to reconcile structured events; use realtime only when the owner asks this during a live voice exchange.
- **latency:** Under 2 seconds from cached receipts; up to 5 seconds if a live relay/device acknowledgment is requested.
- **cost:** Usually <$0.01 per query; dominated by no model call if predicates are evaluated in code, with a small text-model call only to phrase contradictory evidence.
- **security:** Expose only this owner's job IDs and device IDs; never include PCM or transcript contents by default. Require confirmation before replaying audio or changing retention. Explicitly surface stale acknowledgments and an unknown state when no pendant is registered.
- **missing:** A typed delivery contract linking one response artifact to relay download, pendant receipt, playback start/completion, and failure reason.; A durable pendant playback acknowledgment event (device ID, artifact hash, bytes, playback interval, firmware version, monotonic counter). No pendant is currently registered, so this cannot be exercised yet.; A cross-surface evidence reducer with freshness/expiry and a dashboard card for the chain.

### "Can you tell me when my voice is hard for you to hear, and what I should change?"
- **useful because:** The owner currently receives no trustworthy, actionable indication that a conversation is failing because of wind, clothing rub, distance, Bluetooth path, or microphone clipping. A cross-surface voice-quality sentinel would distinguish a quiet speaker from a broken link and tell them whether to move the pendant, repeat themselves, or wait for the network—before misunderstandings compound.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Deterministic signal metrics and a small background model for trend classification; use the realtime model only to deliver the short spoken warning during an active exchange.
- **latency:** Local warning within 250 ms when clipping, silence, or link loss is obvious; trend diagnosis within 3 seconds using the relay and Mac pipeline.
- **cost:** Near-zero for RMS/peak/dropout metrics; under $0.01 for occasional classification, dominated by a small model call only when metrics are ambiguous. No raw audio needs to leave the pendant for routine monitoring.
- **security:** Default to metrics, not stored audio; retain short rolling windows only with an explicit debug action. Device and session identifiers must be owner-scoped. Never infer health or emotion from voice quality. Spoken warnings should be rate-limited so a noisy environment does not become an annoyance.
- **missing:** Pendant firmware must emit timestamped acoustic/link-quality counters (noise floor, speech activity, clipping, packet loss, queue delay, codec underruns) with a monotonic sequence number and an offline ring buffer.; The relay must correlate those counters with upload, transcription, and response events without retaining raw PCM, and expose a quality episode API.; The Mac pipeline must publish transcription confidence, resampling/codec status, and response latency as typed observations; faculty-perception needs a reducer that identifies sustained episodes and selects one actionable explanation.; A dashboard and pendant interaction must support a one-tap 10-second calibration capture, with the result explicitly marked as diagnostic and deletable.


## Changes it proposed to its own stack

### `context` — Add a temporal reality fence to faculty-perception: normalize every cross-surface observation into {subject, predicate, value, observedAt, source, freshnessWindow, live|historical|inferred, deviceId}; reject or downgrade historical pipeline telemetry when answering current device/audio questions, and emit an explicit 'no registered pendant' fact from the live device registry. Contradictions (for example 15,625-Hz input versus 24-kHz output) remain separate observations rather than being silently reconciled.
- **owner gets:** The owner stops hearing confident claims based on yesterday's audio or a relay receipt when no pendant is connected. They get a truthful answer about what is happening now, what happened earlier, and exactly where knowledge ends.
- effort: Medium: shared observation schema, freshness policy, reducer tests, and faculty-perception output contract; no model training required.  ·  risk: A clock skew or overly short freshness window could label a real but quiet device stale. Recover by preserving raw events, exposing source timestamps, and allowing a bounded grace period; never convert stale to live.
- cost: Negligible API cost; small storage/index overhead for provenance fields.  ·  latency: Adds tens of milliseconds for deterministic normalization; avoids expensive model calls by making temporal status computable.
- security: Reduces leakage by returning typed status and hashes instead of audio/transcript payloads; device IDs must remain owner-scoped.
- depends on: A live relay device-registry endpoint (currently no /v1/devices/status route on the Mac agent); Typed audio delivery/playback events when a pendant firmware exists; A shared observation projection between relay and Mac agent


## What it asked for

### `c7-kr48` (context) — authoritative relay device registry and delivery acknowledgments
- why: I established the Mac agent has no /v1/devices/status route, while live discovery says no pendant is registered. To design the temporal reality fence and avoid treating historical pipeline events as current, I need the authoritative relay-side endpoint/schema and whether any download/playback acknowledgments already exist.
- would change: I will either record the relay registry and acknowledgment fields as established facts, or explicitly mark them missing and keep all pendant delivery claims at unknown.

## Its own summary

Fresh perception facts recorded: no pendant is registered (only the Mac bridge is online); Mac GUI input is untrustworthy because Accessibility and Screen Recording are absent; and historical pipeline evidence confirms 15,625-Hz mono input versus 24-kHz mono TTS output, with relay acceptance but no proof of end-device playback. I sent the audio predicate fields to faculty-action and the missing cross-surface delivery chain to faculty-judgement. I proposed a temporal reality fence that labels observations live/historical/inferred and prevents stale telemetry from being presented as current, plus a delivery-proof capability; the latter is connective work and may overlap existing backlog. I also queued a request for the authoritative relay device registry/ack schema.

**Biggest unknown:** Whether the relay already exposes a durable download/playback acknowledgment for a pendant, and what its authoritative device-registry route is. Until a pendant registers and emits those events, end-to-end audio delivery remains unknown rather than verified.

