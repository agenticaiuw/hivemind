# Harness derivation — faculty-perception — round 12

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-readiness** — Mac local agent v0.5.0 is reachable and token-configured, but reports ready=false because Accessibility and Screen Recording permissions are not granted; browser extension is offline with 2 pending commands.
  - evidence: GET /ops/status at 2026-08-07T09:32:09Z: permissions.accessibility.trusted=false, screenRecording.granted=false, browser.online=false, pendingCommands=2.
- **audio-path-observed** — A recent completed response was rendered as 24,000 Hz mono s16le PCM: 164,650 bytes, 3,430 ms, no clipping; the observed pendant capture telemetry remains 15,625 Hz PCM uplink.
  - evidence: GET /pipeline: tts done meta sampleRate=24000, pcmBytes=164650, clippedSamples=0; inputTelemetry sampleRate=15625, format=pcm-s16le.
- **relay-connectivity** — Mac bridge and cloud relay were reachable at observation time; relay reports pendantPipelineTelemetry, pendantSpeech, persistentAgentState, and durableAudio enabled.
  - evidence: GET /ops/status: relay.reachable=true, macBridgeOnline=true, payload.capabilities all true.

## Capabilities it proposed

### "“Before I start, tell me whether you can hear me, speak back, and act on my Mac right now—and if not, tell me exactly what still works.”"
- **useful because:** Today the system can sound healthy while the Mac is not actionable: the live status observed ready=false because Accessibility and Screen Recording are missing, while relay and 24 kHz response audio are working. A truthful end-to-end readiness answer prevents the owner from issuing commands that will silently queue or fail, and distinguishes conversation, playback, Mac control, and browser access instead of one misleading green light.
- **path:** pendant → relay → mac-bridge → dashboard → browser
- **model tier:** background for periodic health snapshots and cheap rule-based classification; realtime only to answer the spoken readiness question immediately
- **latency:** Under 500 ms for cached status; refresh relay/Mac/pendant probes in parallel within 2 s when stale. No model call for the normal case.
- **cost:** Near-zero API cost for cached typed probes; occasional background synthesis under $0.01 per refresh. Main cost is telemetry storage and LTE bytes, not inference.
- **security:** Expose only capability states and remediation labels, never bearer tokens, account contents, URLs, or raw audio. Browser-private readiness must report online/offline and permission state without tab data. Require confirmation before any automated permission-changing step; do not claim a permission was fixed unless a fresh probe verifies it.
- **missing:** A signed, freshness-bounded readiness contract shared by pendant firmware, relay, Mac bridge, and browser extension; Pendant-side diagnostics/readback for link, capture, playback, SD, and modem state (currently not available to this agent); A relay endpoint that aggregates the Mac /ops/status result with last pendant telemetry and browser heartbeat; A small pendant UI/audio cue for partial readiness and queued-work state

### "“Resume the conversation where it dropped.”"
- **useful because:** Today a dropped LTE/M or Mac link can leave the owner unsure whether the pendant heard the request, whether the answer was generated, and where playback stopped. The owner should be able to resume from the exact acknowledged utterance and audio position, without repeating private context or accidentally executing a request twice.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Rule-based event reconciliation and a cheaper background model for compact context repair; use realtime only for the resumed live exchange.
- **latency:** On reconnect, recover state and offer a one-sentence spoken continuation within 2 seconds; no model call is needed to determine the last durable checkpoint.
- **cost:** Usually under $0.01 per interrupted conversation; storage is a small encrypted checkpoint and optional short audio tail. Inference cost is dominated only by context repair when the transcript is incomplete.
- **security:** Encrypt the pending utterance and checkpoint at rest and in transit, bind them to the paired pendant and session, and expire them quickly. Never replay or execute an action solely because it was found in a recovered checkpoint: require an idempotency check and fresh confirmation for irreversible actions. Dashboard must show exactly what is being resumed and allow discard.
- **missing:** A durable conversational checkpoint protocol with separate heard, transcribed, planned, executed, and played-through markers; Pendant-local encrypted ring storage for a short utterance/playback tail and a reconnect marker; Relay reconciliation that deduplicates resumed jobs across LTE retries and Mac reconnects; A playback cursor and acknowledgement event from firmware, not merely an audio-upload record; A spoken and dashboard recovery UX distinguishing resume, discard, and start over


## Changes it proposed to its own stack

### `integration` — Add a cross-node pipeline truth reconciler. Each relay, Mac bridge, and pendant event carries an eventId, monotonic device sequence, observedAt, and terminal outcome. A reducer derives the run state from terminal evidence (for example, uploaded 24 kHz reply audio means playback-ready even if the enclosing run still says processing), marks contradictory/stale states explicitly, and publishes one signed compact status to the pendant, dashboard, and faculty-perception. Keep raw events for audit but never make the conversational agent infer completion from an ambiguous top-level status.
- **owner gets:** The live pipeline currently contains runs labeled “processing” whose events already prove alert delivery or response audio is complete. The owner should hear “your reply is ready” or “still waiting” rather than experience late, duplicate, or falsely missing responses.
- effort: Medium: shared event schema, reducer tests with dropped/reordered LTE events, relay persistence migration, Mac and firmware emitters, and dashboard rendering.  ·  risk: Out-of-order LTE delivery could prematurely mark a run complete; require terminal signatures plus a short settling window and preserve an explicit unknown state. On reducer failure, fall back to raw event display and do not trigger playback twice; idempotency keys protect delivery.
- cost: Negligible inference cost; modest D1/R2 metadata and a few hundred bytes per event. No additional audio storage beyond existing captures.  ·  latency: Adds at most 100–300 ms settling for live runs; cached terminal evidence can be surfaced immediately.
- security: Event metadata must be authenticated and scoped to paired pendant/job; do not include transcript or audio in the status projection. Audit tombstones should remain available for owner-visible history.
- depends on: A signed event envelope and device sequence source on pendant/relay/Mac; The pending playback-lifecycle telemetry request; A shared typed readiness/status contract

### `hardware` — Add a small, low-power audio codec/ADC on the bridge's I2S path with a hardware 24 kHz-capable clock and DMA buffer, while retaining the nRF9160 modem for LTE-M. Route microphone capture through the codec instead of the current 15,625 Hz path; expose clock-lock and overrun counters to the pendant telemetry.
- **owner gets:** The observed uplink telemetry is fixed at 15,625 Hz, so the owner cannot get true superwideband input even though response playback now reaches 24 kHz. A clocked codec makes both sides of a conversation genuinely 24 kHz-capable and reduces resampling artifacts and dropped speech.
- effort: High: board revision, power/EMI validation, Zephyr I2S/codec driver, DMA buffering, enclosure and production test changes.  ·  risk: Added analog noise, clock drift, or higher current could reduce battery life; provide a firmware feature flag to fall back to the existing mic path and retain raw-rate telemetry. If codec init fails, conversations remain available at the current rate.
- cost: Roughly $3–8 BOM increase plus board spin; approximately 5–20 mA during capture depending on codec, with no LTE transmit increase.  ·  latency: Potentially lower capture latency through DMA, but add 10–30 ms buffering while framing 24 kHz audio.
- security: No new network surface; ensure codec registers and diagnostic counters are not writable from untrusted relay commands.
- depends on: Current 24 kHz implementation status and pendant diagnostics; A verified end-to-end 24 kHz transport/framing contract; Battery and enclosure validation


## What it asked for

_Nothing._
## Its own summary

Round 12 established fresh live facts: the Mac agent is reachable and token-configured but not ready because Accessibility and Screen Recording are both ungranted; the browser extension is offline with two queued commands; relay and Mac bridge are reachable; a recent response was successfully rendered as clean 24 kHz mono PCM, while capture telemetry remains 15,625 Hz. I recorded these facts, informed faculty-judgement, and proposed (1) an end-to-end truthful readiness check, (2) a cross-node pipeline truth reconciler for contradictory processing/complete states, and (3) a hardware codec/clock path to make capture genuinely 24 kHz-capable.

**Biggest unknown:** I still cannot establish the pendant's current local link, capture, playback, SD, modem, or firmware state, nor verify the actual 24 kHz capture implementation. The pending pendant diagnostics/playback telemetry and implementation-status requests remain necessary; without them, any claim about the wearable side of the audio path would be speculation. Mac readiness also remains blocked until the owner grants Accessibility and Screen Recording.

