# Harness derivation — faculty-perception — round 56

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent reachability and browser state** — At 2026-08-07T12:00:55Z, Mac agent is online/full-control configured but permissions.ready=false: Accessibility trusted=false, Screen Recording false, and inputReachability failed; browser extension home-chrome offline with 5 pending commands and 3 durable browser sessions observed.
  - evidence: GET /ops/status and GET /observe both returned these exact statuses.
- **audio pipeline sample-rate asymmetry** — A completed Mac-bridge pipeline run rendered response speech as 24,000 Hz mono PCM (75,734 bytes, 1.578 s), while a recent realtime pendant input telemetry event reports 15,625 Hz mono PCM (937,500 bytes) uploaded as live LTE audio. Thus output is 24 kHz but observed input remains 15.625 kHz.
  - evidence: GET /pipeline response: pipeline job_309f... TTS event metadata sampleRate=24000; job_165a... inputTelemetry sampleRate=15625, format=pcm-s16le.
- **computer-use safety state** — Mac agent reports computerUse loopEnabled=false, vision model configured, but visionUploadConsented=false and maxSteps=25; therefore no active screenshot-based computer-use loop is currently authorized or enabled.
  - evidence: GET /ops/status agent.computerUse payload.

## Capabilities it proposed

### "“Did that actually reach you and get handled?” — Give me one trustworthy answer about my last spoken request, including whether the pendant audio arrived intact, whether the relay and Mac received it, whether any browser or Mac action really happened, and what remains queued after an offline gap."
- **useful because:** Today the owner can receive a plausible spoken reply even when input is downsampled, the browser is offline, or UI actions report success without reaching the screen. This capability would distinguish heard, accepted, executed, delivered, and merely queued, with timestamps and an honest unknown state—especially useful when walking away from Wi-Fi or LTE coverage.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background deterministic aggregation first; use the expensive realtime model only to translate the resulting verified state into the owner's short spoken answer.
- **latency:** Initial acknowledgement under 2 seconds when connected; final reconciliation within 10 seconds of reconnection or action completion. No model call is needed for routine status checks.
- **cost:** Near-zero per invocation for event joins and receipt lookup; occasional short TTS only when the owner asks or a discrepancy is announced. Storage and event indexing dominate, not inference.
- **security:** The trace can expose private URLs, app names, and timing. Keep raw audio and page contents out of the status record, retain hashes/types/timestamps and redacted action labels, enforce pairing and bearer authentication, and require confirmation before exposing sensitive destination details.
- **missing:** A durable cross-surface correlation ID carried from pendant capture through relay transcription, Mac planning, browser command, action receipt, and response audio; A verified audio-ingress receipt containing measured sample rate/bytes and upload completion, not only a planner event; A terminal state machine distinguishing heard, accepted, executed, delivered, queued, expired, and unknown, with replay-safe reconciliation after reconnect; A server-side join/index over pipeline events, Mac job receipts, browser command results, and pendant delivery acknowledgements

### "“Run a quiet connection check.” — In one minute, tell me whether my pendant can currently hear me and speak back reliably, measuring the live audio path end to end and identifying the failing leg without recording conversational content."
- **useful because:** The owner currently cannot tell whether a bad interaction came from microphone capture, LTE transport, relay processing, Mac bridging, 24 kHz playback, or a disconnected browser. A privacy-preserving synthetic check would turn guesswork into a concrete diagnosis before they depend on the pendant.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic scheduled/ on-demand diagnostics; use a cheap text model only to summarize measurements. Realtime is unnecessary except for an optional live echo test.
- **latency:** Complete in 30–60 seconds on demand; a lightweight passive status should be available in under 2 seconds. Never delay normal conversation.
- **cost:** Minimal: telemetry and a short generated test payload; one optional TTS/STT test costs less than a normal turn. No vision or large language call required for raw diagnosis.
- **security:** Use generated tones and nonce phrases, not the owner's speech; discard captured test audio after measurements; do not expose browser URLs or account data; require explicit opt-in before transmitting any diagnostic payload beyond the paired relay.
- **missing:** A pendant diagnostic mode that emits a nonce test tone/phrase and reports capture rate, packet loss, jitter, and playback acknowledgement; Relay-side loopback and per-leg measurement IDs spanning LTE ingress, transcription ingress, Mac bridge, TTS render, and pendant download/playback; A known-good 24 kHz test fixture and acceptance thresholds for both input and output, rather than trusting event labels; A dashboard/voice response formatter that reports the first failing leg and confidence without claiming an end-to-end pass when any leg is unknown


## Changes it proposed to its own stack

### `integration` — Add an evidence-invariant monitor spanning pendant telemetry, relay pipeline events, and Mac /observe: normalize every audio leg and device reachability state into a timestamped health record, compare declared target (24 kHz) against measured input/output formats, detect stale/offline browser queues and false-success UI actions, and publish a compact 'what is actually reachable/working' snapshot with freshness and confidence. Do not block actions; expose discrepancies to judgement and receipts.
- **owner gets:** The owner gets honest answers instead of a 24 kHz claim when only playback is 24 kHz, and is told when browser work is queued offline or UI receipts cannot be trusted. This prevents silent failures and saves repeated troubleshooting.
- effort: Medium: shared schema plus relay aggregation, Mac observer adapter, pendant event parser, and tests for stale timestamps and sample-rate mismatches.  ·  risk: Incorrect clock skew or partial telemetry could create noisy warnings; use explicit unknown state, freshness windows, and never infer success from missing events. Recovery is replaying retained events and recomputing the snapshot.
- cost: Negligible storage/compute; one small event per pipeline transition and compact D1 record. No additional model call required.  ·  latency: No hot-path impact if asynchronous; snapshot available within seconds of an event.
- security: Telemetry contains device and app state, so retain minimal fields, redact URLs/account data, and apply existing bearer/pairing controls.
- depends on: durable pendant pipeline telemetry; Mac /observe and /ops/status routes; relay event persistence


## What it asked for

_Nothing._
## Its own summary

Fresh truth established: Mac agent is online but not UI-reachable (Accessibility and Screen Recording false; input probe failed); browser extension is offline with 5 queued commands despite 3 durable sessions; computer-use is disabled and vision upload consent is false. The audio path is asymmetric: observed 24 kHz mono TTS output, but recent pendant realtime input is still 15,625 Hz PCM. I recorded all three findings, informed judgement/relay/Mac planner, and proposed an asynchronous cross-surface evidence-invariant monitor that reports these discrepancies without blocking actions.

**Biggest unknown:** Authoritative live pendant/firmware telemetry and the current implementation status of the 24 kHz input path remain unavailable this round; I also cannot determine whether the 5 browser commands are safe to replay without the offline extension returning.

