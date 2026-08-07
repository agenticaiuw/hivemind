# Harness derivation — faculty-perception — round 8

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-readiness** — Mac local agent is reachable at version 0.5.0 with full-control and LLM planner enabled, but reports ready=false because Accessibility trust and Screen Recording permission are missing; browser extension is offline with 2 pending commands.
  - evidence: GET /ops/status returned HTTP 200: permissions.accessibility.trusted=false, screenRecording.granted=false, ready=false; browser.online=false and pendingCommands=2.
- **audio-path-observed** — A recent end-to-end response produced 24 kHz mono PCM (160.8 KiB, 3.43 s) with zero clipped samples and was accepted by the relay; the same pipeline records pendant input as 15,625 Hz PCM over live LTE and transcribes via audio-native realtime.
  - evidence: GET /pipeline returned pipeline events: TTS 24000 Hz mono PCM, pcmBytes=164650, clippedSamples=0; inputTelemetry sampleRate=15625, storage=live_lte, uploadedFormat=pcm, transcriptionSource=audio-native-realtime.
- **relay-mac-link** — Cloud relay is reachable and currently reports the Mac bridge online; relay version 1.1.0 has pendant telemetry, speech, persistent state, and durable audio enabled.
  - evidence: GET /ops/status relay payload: reachable=true, macBridgeOnline=true, capabilities pendantPipelineTelemetry/pendantSpeech/persistentAgentState/durableAudio all true.

## Capabilities it proposed

### "“Did that actually go through?” Give me a short, evidence-backed receipt for my last request: heard, understood, acted on, delivered to the pendant, and played—or tell me exactly where it stopped and keep the unfinished part resumable."
- **useful because:** Today a late response, offline-held alerts, and a completed Mac job can all look like the same success from one surface. This gives the owner a truthful answer instead of confident-but-wrong completion language, especially after LTE gaps or a sleeping Mac.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background: gpt-5.6-luna compiles the receipt from persisted event telemetry; realtime only answers an immediate spoken status question from already indexed state
- **latency:** Immediate spoken acknowledgement under 1 s from cached state; definitive receipt within 5 s after querying relay and Mac pipeline. No polling audio or expensive vision.
- **cost:** ~$0.002–$0.02 per receipt, dominated by background synthesis; event retrieval and hashes are negligible.
- **security:** Receipt may expose private command text, URLs, or account results on the pendant. Store only event metadata plus redacted excerpts by default; require owner confirmation before replaying or resuming any side effect. Never claim ‘played’ from relay acceptance alone—require a pendant playback-start/complete acknowledgement.
- **missing:** A shared receipt schema with immutable event IDs and causal links across nRF9160 offline store, relay job, Mac job/pipeline, and playback acknowledgement; Pendant firmware telemetry for playback started, playback completed, interrupted, and locally queued/deleted; Relay endpoint that joins those events and marks uncertainty instead of collapsing accepted/uploaded/played into completed; A resumable-job token and idempotency key carried from voice request through Mac action and pendant delivery

### "“What is actually available to me right now?” Give me one short, spoken operating picture of the pendant, LTE link, relay, Mac, browser sessions, permissions, and any queued work—explicitly calling out stale or contradictory observations, and refresh it when I ask again."
- **useful because:** Today each surface can report a locally plausible state while the owner cannot tell whether a request is executable: the Mac agent can be reachable but not ready, the browser can have queued commands while offline, and the relay can accept audio while physical playback remains unknown. A freshness- and contradiction-aware picture prevents wasted commands and false confidence.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** A deterministic status joiner should collect and rank observations; use a cheap background model only to compress the already-structured result into one spoken sentence. Realtime is unnecessary except for the immediate voice reply.
- **latency:** Cached summary under 300 ms; active refresh under 3 seconds, with each component's observation age spoken when it exceeds its freshness bound.
- **cost:** Near-zero model cost for structured status; approximately $0.001–$0.005 only when prose compression is needed. Network calls and device wake-ups dominate latency and battery, not inference.
- **security:** The summary can reveal private browser session presence, account availability, hostnames, and permission state. Authenticate every component, omit URLs/account names by default, expose detailed evidence only on the paired dashboard, and never treat a stale ‘online’ heartbeat as current consent or readiness.
- **missing:** A cross-surface status contract with per-field observedAt, expiresAt, source, confidence, and contradiction groups rather than a single online boolean; Pendant-side link and queue status export that survives offline operation and reports its observation age; Mac and browser heartbeats that include readiness and permission scope, not merely process reachability; A relay join endpoint and dashboard/voice formatter that preserve ‘unknown’ and ‘conflicting’ states instead of silently choosing one


## Changes it proposed to its own stack

### `integration` — Introduce a causal execution ledger shared by pendant firmware, relay, and Mac bridge. Every request gets a requestId and idempotency key; each node appends signed-ish append-only transitions (captured, transcribed, planned, action_started, action_committed, response_uploaded, playback_started, playback_completed, interrupted) with monotonic device sequence, wall-clock estimate, source, and confidence. Add a join endpoint that refuses to infer later states from earlier acceptance, and expose one compact receipt view to voice and dashboard.
- **owner gets:** After a dropped LTE link or sleeping Mac, the owner can know whether something was merely queued, actually changed, or was heard back. Failed work can resume without duplicate email, file deletion, or other side effects.
- effort: Medium-high: schema and joiner in relay, event emitters in Mac bridge, and small firmware telemetry additions; migration can tolerate old jobs as unknown-state.  ·  risk: Duplicate or reordered events could produce a misleading receipt; use idempotency keys, per-source sequence numbers, and explicit unknown states. If the ledger is unavailable, retain current behavior and say status is unavailable.
- cost: Low storage/write overhead (roughly hundreds of bytes per transition); modest D1 growth. No model call for event joining; synthesis only when the owner asks for prose.  ·  latency: Under 100 ms for structured status; a few seconds only when generating a spoken summary.
- security: Ledger metadata can reveal private commands and destinations. Encrypt or minimize payloads, redact content by default, enforce owner pairing/auth, and separate sensitive action details from generic delivery state.
- depends on: Pendant playback lifecycle telemetry (started/completed/interrupted); A durable Mac job/request id propagated into relay results; Relay endpoint and retention policy for causal events

### `integration` — Add a temporal-coherence layer rather than trusting wall-clock timestamps from individual nodes. Each pendant, relay, browser extension, and Mac heartbeat should carry a monotonic sequence plus wall-clock sample; the relay periodically estimates offset and uncertainty, detects timezone/configuration disagreement, and publishes an interval-based event order (for example, ‘after request capture, before Mac action’) when exact time cannot be proven.
- **owner gets:** The owner gets reliable answers about what happened first and whether a late response belongs to the current request, even when the Mac timezone, pendant clock, and cloud timestamps disagree or a device reconnects after hours.
- effort: Medium: shared event envelope, offset estimator, reconnect calibration, and interval-order UI/voice formatting; old records remain usable with unknown timing confidence.  ·  risk: Clock jumps, suspend/resume, modem resets, and replayed events can create false ordering. Preserve raw timestamps, mark uncertainty, and never turn an inferred order into an exact time. Roll back by showing source-local times if calibration fails.
- cost: Tiny CPU/network overhead for heartbeat samples and a few columns per event; no recurring model cost.  ·  latency: Negligible for normal requests; reconnect calibration may add one heartbeat round trip before a definitive chronology is available.
- security: Timing metadata can disclose device presence patterns. Retain coarse timing by default, restrict raw offsets to authenticated diagnostics, and avoid transmitting unrelated local clock data.
- depends on: A shared event envelope across all nodes; Persisted monotonic sequence counters on pendant and Mac; A status/observation joiner that can expose uncertainty instead of flattening it


## What it asked for

### `s1-xcuw` (skill) — playback-lifecycle-telemetry
- does: For every response audio item, persist and later upload a compact lifecycle record: response/request ID, queued, playback started, playback completed or interrupted, bytes/frames consumed, and reason for interruption. Emit a local event even when LTE is down, then reconcile it when connectivity returns.
- must be on-device because: Only the pendant knows whether audio physically began coming out of the bridge and whether the owner heard the complete response; relay acceptance cannot establish playback. It must survive a dropped link and work offline.
- trigger: Server-pushed response audio plus local playback start/stop/underrun events; upload on reconnect or next button-initiated session.
- storage: microSD append-only CBOR or line records, roughly 80–160 B per response; retain the last 256 responses (~40 KiB), with upload acknowledgement and compaction.
- RAM budget: ~2–4 KiB ring buffer and one record encoder; no audio buffering beyond existing path. Fits within 211,608 B application RAM, but must avoid increasing the already high simultaneous Opus CPU load.

## Its own summary

Established and recorded three current truths: Mac agent v0.5.0 is reachable but not ready (Accessibility and Screen Recording are missing); browser extension is offline with two pending commands; relay and Mac bridge are online, and a recent response completed the 24 kHz mono PCM path cleanly (no clipping), while pendant input remains 15,625 Hz PCM. Proposed a new cross-node capability: an evidence-backed receipt that distinguishes heard, understood, acted, delivered, and physically played, plus a causal execution ledger and requested pendant playback-lifecycle telemetry.

**Biggest unknown:** The system still cannot prove physical playback: relay acceptance is observable, but playback-start/completed/interrupted events from the pendant are not. I still need the firmware lifecycle telemetry, a shared request/idempotency ID across pendant-relay-Mac, and resolution of Mac Accessibility/Screen Recording permissions before computer-use results can be called dependable.

