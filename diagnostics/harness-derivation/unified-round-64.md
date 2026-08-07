# Harness derivation — unified — round 64

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-path reality** — Live pipeline telemetry currently records 15,625 Hz PCM capture (937,500 bytes, 1,441 ms) while TTS output is 24,000 Hz PCM (164,650 bytes, 3,430 ms); the system labels output wideband but has no negotiated contract or post-call quality receipt. Relay reports 24k playback decode, while LTE-M is half-duplex and measured to drop 388 uplink packets during simultaneous speech.
  - evidence: GET /pipeline live response job_165a9c9a... inputTelemetry sampleRate=15625 and GET /pipeline event pipe_evt_bb53116... sampleRate=24000; get_hardware_spec audio/network

## Capabilities it proposed

### "After each call, tell me in one sentence whether my pendant audio was truly wideband and, if not, what caused the problem; keep a history so I can see whether firmware or network changes fixed it."
- **useful because:** The owner currently experiences missing speech and has no trustworthy distinction between a bad microphone, LTE contention, relay transcoding, or speaker underruns. This turns an invisible systems problem into a concise answer and a trend, without sending raw conversations anywhere.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Use firmware and relay instrumentation for classification; use a cheap background model only to turn structured metrics into one short explanation. Reserve realtime for the live call and do not spend it on post-call summarization.
- **latency:** Metrics are batched during the call; verdict within 10 seconds after hangup. Dashboard history loads under 500 ms from structured receipts.
- **cost:** Near-zero API cost for normal calls; under $0.01 only when a background model is needed to explain an unusual combination of metrics. Dominant cost is a few KB of durable telemetry per call, not inference.
- **security:** Store sequence/jitter/codec metrics and signed profile receipts, never PCM or transcripts by default. The owner can delete history. Any raw-audio diagnostic upload requires explicit confirmation and a short expiry.
- **missing:** Negotiated versioned audio contract and signed receipt schema; Pendant per-direction sequence, encode/decode timing, underrun, and clock telemetry; Relay aggregation/classification and retention/deletion controls; A dashboard audio-health timeline and explicit narrowband fallback label; 24 kHz acceptance thresholds and a loss/jitter conformance test

### "Let me say “continue this on my Mac” or “send this to the pendant” and move the live conversation, its unfinished answer, and the exact next action between the wearable and Mac without repeating myself."
- **useful because:** Today the pendant is the owner's ear and voice while the Mac is their hands, but changing surfaces loses the active conversational state. This would let the owner start hands-free, move to a screen for review or private browser work, then return to the pendant with the same thread and no duplicate action.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic session transfer and structured state serialization; use the background tier only to compress a long transcript into a handoff brief. Realtime is used only while the owner is actively speaking, not to rewrite the whole conversation.
- **latency:** A handoff acknowledgment in under 2 seconds; the receiving surface resumes in under 5 seconds. No model call is needed for a short structured transfer.
- **cost:** Usually zero additional model cost; at most a few cents for an unusually long transcript compressed in the background. Storage is a small encrypted handoff record plus references to existing job and browser-session state.
- **security:** The handoff must preserve surface permissions: browser cookies and secrets never move to the pendant, and a pendant request can carry intent but not silently authorize a destructive Mac/browser action. Encrypt records, expire them after the conversation, and require the existing confirmation gate when the receiving surface would send, delete, purchase, or submit.
- **missing:** A first-class handoff record containing conversation checkpoint, pending plan, action receipts, target surface, and expiry; A pendant voice/button command that names the destination surface and acknowledges transfer; Relay routing that binds one conversation to both clients with idempotent resume tokens; Mac and dashboard resume UI that shows the last spoken sentence, pending action, and approval state; Browser-session references that remain on the Mac while their findings are summarized into the handoff


## Changes it proposed to its own stack

### `integration` — Create a versioned, negotiated audio contract shared by pendant firmware, Cloudflare relay, and Mac/dashboard: capabilities (capture/playback sample rate, frame size, bitrate, FEC/PLC, resampler delay) are exchanged at session start; every call emits per-direction sequence-gap, decode-time, jitter, underrun, and resampler metrics. Add an automated 24 kHz superwideband conformance run that injects loss/jitter, captures both directions through /pipeline audio, checks bit-exact rate/frame metadata and intelligibility thresholds, and stores a signed receipt linked to the call. Refuse to label a session '24 kHz' unless the actual negotiated path and captured evidence satisfy the contract.
- **owner gets:** The pendant will stop claiming wideband audio when one link silently falls back or loses speech. After a firmware or relay update, the owner gets a plain pass/fail receipt and a useful diagnosis (mic clock, LTE loss, relay transcode, or speaker path) instead of guessing whether the device is broken.
- effort: Medium-high: protocol schema and firmware handshake, relay metrics/receipt storage, Mac test runner, dashboard presentation, and a lab audio fixture. Roughly 2–4 engineer-weeks plus repeatable acoustic fixtures.  ·  risk: A strict contract could reject calls on marginal networks or expose incompatible old firmware; retain a compatibility profile and degrade explicitly to narrowband. Test audio must be synthetic or consented; do not retain raw speech by default, only hashes and aggregate metrics. Recovery is rollback to the previous profile and a visible 'narrowband fallback' state.
- cost: Negligible per-call model/API cost; a few hundred bytes of handshake and metrics per call, plus modest D1/R2 receipt storage. Lab fixture cost roughly $100–300 if not already available.  ·  latency: Handshake adds under 1 second at session setup; metric batching adds no conversational latency. Conformance tests run offline/background, not on the realtime model.
- security: Signed capability and receipt fields prevent false device claims but must avoid embedding audio or secrets. Authenticate firmware/profile versions and reject downgrade except an explicit compatibility fallback.
- depends on: A defined 24 kHz end-to-end acceptance target (sample-rate tolerance, one-way latency, packet-loss concealment, and intelligibility threshold); A firmware audio telemetry frame and relay schema; A retention policy that stores receipts/metrics without raw audio; The existing /pipeline, /pipeline/events, /pipeline/audio, and /pipeline/:pipelineId/audio/:direction routes

### `hardware` — For the product revision, replace the prototype's 15,625 Hz I2S microphone/clock path with a microphone and audio front end that natively captures 24 kHz (or 48 kHz with deterministic 2:1 decimation), and move Opus work off the nRF9160's overloaded single core onto a companion low-power audio MCU/DSP. Keep the nRF9160 for LTE-M and control, and expose the audio MCU's clock lock, FIFO depth, and encode/decode load as telemetry consumed by the negotiated audio contract.
- **owner gets:** Their speech will actually contain superwideband input, not merely 24 kHz playback generated from narrowband capture, and simultaneous talking/listening will not consume nearly all pendant CPU or create avoidable dropouts.
- effort: High: select and validate a wearable microphone/codec, redesign the I2S and power domains, implement an MCU-to-nRF transport and firmware update path, then run RF/acoustic validation. Several hardware spins and 6–12 engineer-weeks.  ·  risk: New clocks, RF noise, power draw, and an inter-processor failure mode could make reliability worse. Prototype first on a dev board; retain the current path as a fallback profile and watchdog the audio MCU. This cannot be honestly solved by resampling the current 15,625 Hz microphone.
- cost: Prototype BOM increase roughly $8–25 for audio MCU/codec/clock and board changes, plus tens of mW while active; negligible per-call API cost.  ·  latency: A well-sized audio MCU FIFO should add under 10 ms; avoid large buffering and expose measured one-way delay in the receipt.
- security: Signed firmware for both processors, authenticated inter-processor messages, and no raw-audio persistence. A compromised audio MCU must not gain modem credentials.
- depends on: The current nRF9160 prototype measurements (211,608 B RAM, 87% combined Opus CPU, 15,625 Hz I2S capture); A versioned negotiated audio contract and conformance receipt; A product-level power budget and acoustic/RF coexistence test plan


## What it asked for

_Nothing._
## Its own summary

Round 64 produced three concrete outcomes. Live evidence shows the current path is not truly end-to-end SWB: capture is 15,625 Hz PCM while playback is 24,000 Hz, and LTE-M contention has already caused about 7.8 seconds of lost uplink speech. I recorded this finding and proposed (1) a negotiated, versioned audio contract plus loss/jitter conformance receipts, (2) an owner-facing post-call audio-health verdict and history, and (3) a product hardware revision with a native high-rate audio front end and companion audio MCU rather than pretending resampling is capture quality. The existing pipeline/ops routes can carry much of the telemetry, but they do not yet connect it into a trustworthy verdict.

**Biggest unknown:** I still need the authoritative 24 kHz acceptance thresholds (capture versus playback target, allowable clock error, one-way latency, loss/PLC limit, and intelligibility criterion), the production power/BOM envelope, and confirmation of whether raw audio may ever be uploaded for diagnostics. The orchestrator's granted category is still empty this round, so no new audio-validation or workspace-edit tool is actually visible to me. Accessibility and Screen Recording also remain unavailable; that does not block the audio work.

