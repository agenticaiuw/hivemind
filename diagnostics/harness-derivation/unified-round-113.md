# Harness derivation — unified — round 113

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-continuity-gap** — The live pipeline can render and upload 24 kHz mono PCM successfully (example: 75,734 bytes, 1.578 s), but the current hardware path is fragmented: pendant captures 15,625 Hz and Opus uplink is labeled 16 kHz; playback decodes at 24 kHz, drives a 31,250 Hz I2S wire, then the ESP32 bridge resamples to 44.1 kHz SBC/A2DP. There is no observed cross-stage playback cursor or resume receipt.
  - evidence: get_hardware_spec(audio), get_hardware_spec(bridge), GET /pipeline showing tts done at 24000 Hz mono and relay_result done, plus /briefing/latest

## Capabilities it proposed

### "If the pendant gets interrupted or the link drops while speaking, say “resume” (or press the button) and continue the last response from the nearest safe word; say “repeat” to replay it, even if I have moved from the Mac to headphones."
- **useful because:** Today a response can be rendered and accepted by the relay yet still be lost to a dropped LTE/Bluetooth link; the owner has to ask the whole question again. This makes spoken briefings and urgent confirmations dependable across pendant, ESP32 headphones bridge, Mac, and relay.
- **path:** pendant → relay-realtime → mac-planner → dashboard → iOS
- **model tier:** No model for resume/repeat. Use the expensive realtime tier only for a new utterance; use a cheap background worker to normalize word/phoneme checkpoints when audio is rendered.
- **latency:** Button acknowledgement locally under 100 ms; resume playback under 500 ms once a link exists. Checkpoint metadata is generated alongside TTS and adds under 50 ms; no extra model call for replay.
- **cost:** Near-zero incremental inference cost; roughly 1–3 KB checkpoint metadata per response and existing PCM/Opus storage dominate. A cheap scheduled cleanup call is optional and infrequent.
- **security:** Responses may contain private mail or account data, so checkpoints must be opaque offsets/hashes rather than transcript excerpts; encrypt retained audio, honor the existing 30-day policy, and delete checkpoints with the audio. Resume/repeat is reversible and needs no confirmation; never auto-replay after an unexpected connection to avoid speaking private content aloud.
- **missing:** A durable audio-playback manifest keyed by pipeline/job id with safe-word or frame boundaries and expiry; Pendant button gestures and local playback cursor persistence for resume/repeat; Bridge acknowledgements that identify the currently buffered/played frame; An idempotent relay endpoint to request a byte/frame range and emit a completion receipt; End-to-end 24 kHz acceptance thresholds and a link-aware duplex governor (already requested, still unanswered)

### "Tell me, without making me ask again, whether an important answer was actually heard—and deliver it privately to the right device. If I walk away from my headphones or remove the pendant, hold the answer and offer it on the pendant or Mac instead of speaking it into the room."
- **useful because:** Today the relay can report that audio was uploaded, but that does not mean the owner heard it. The Mac, browser, relay, ESP32 bridge, and pendant have no shared notion of output privacy, wearer presence, or confirmed audibility. This would prevent missed urgent information and accidental disclosure through a disconnected or unattended speaker.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard → iOS
- **model tier:** No realtime model for transport or presence decisions. Use a small background classifier only to categorize urgency from already-produced text; ordinary responses use existing text and audio. Realtime is used only if the owner asks for clarification.
- **latency:** Local presence/output decision under 200 ms; delivery acknowledgement under 1 second when connected. An urgency classification may take up to 2 seconds in the background and must never block ordinary playback.
- **cost:** Negligible inference cost for transport receipts; approximately 1–5 KB of delivery metadata per response. Optional urgency classification is a low-cost background call and can be disabled.
- **security:** Presence is sensitive behavioral data and must stay local where possible. Never use a room microphone to infer third-party identity. Require explicit pairing and encrypted acknowledgements; a private response must be held rather than rerouted to an untrusted speaker. Retain only delivery state, not ambient audio, and expire it with the response.
- **missing:** A pendant/bridge presence signal or explicit wearer/headphone state with freshness and confidence; A shared output-policy service that knows which endpoints are private, available, and currently active; A cryptographic heard/acknowledged receipt distinct from relay upload or Bluetooth buffer acceptance; Urgency and privacy labels attached to generated responses before routing; A cross-surface notification contract so the Mac, browser, iOS client, and pendant can offer a held response without duplicating it; Product-level audio and privacy acceptance tests across LTE loss, Bluetooth loss, headphone removal, and pendant removal


## Changes it proposed to its own stack

### `integration` — Add a cross-surface Audio Continuity Ledger. For every rendered response, create one manifest keyed by pipelineId/jobId containing codec, sample rate, frame count, safe resume boundaries, expiry, and a monotonic playback cursor. The relay exposes idempotent range-fetch/resume operations; the pendant persists only the manifest id plus cursor on microSD; the ESP32 bridge reports buffered/played frame acknowledgements; /pipeline/events and job receipts reconcile delivery. On reconnect, do not auto-play: surface a local “resume available” cue and require the owner’s button or spoken command.
- **owner gets:** A dropped connection no longer forces them to repeat a request or wonder whether a private answer was heard. They can resume a briefing or confirmation from where it stopped, with no accidental replay when headphones reconnect.
- effort: Medium-high: relay schema and range endpoint, firmware cursor persistence, bridge acknowledgement packet, and dashboard/iOS status UI; validate with deliberate LTE and Bluetooth interruption tests.  ·  risk: Cursor corruption could skip or repeat a few frames; recover by falling back to the last acknowledged safe boundary. Stale manifests could expose old audio if authorization is wrong; bind every fetch to the owner/session and expire/delete with the source object. Never resume automatically after reconnect.
- cost: Negligible model/API cost. Small D1 manifest plus 1–3 KB metadata per response; network cost may fall because resume fetches only the missing range. Existing audio retention storage remains the dominant cost.  ·  latency: Local button response under 100 ms; reconnect resume typically under 500 ms plus network RTT. One extra acknowledgement packet per ~1–2 seconds is acceptable; throttle when LTE is weak.
- security: Private audio remains encrypted and access-controlled; manifests contain no transcript text. Require explicit local intent to replay and erase cursor/manifests when the source audio expires.
- depends on: 24 kHz end-to-end acceptance criteria; link-aware duplex audio governor; Pendant/bridge firmware support for persisted playback cursor and frame acknowledgements; An authenticated range-fetch route between /pipeline/audio and the pendant

### `hardware` — Add a low-power wearer/output-presence subsystem to the product design: a capacitive skin-contact or strap sensor plus a small IMU on the pendant, and authenticated headphone/bridge state telemetry (connected, actively rendering, last-heard timestamp). Expose only coarse states—worn/not worn, private endpoint available/unavailable, acknowledged/not acknowledged—to the relay policy service. Keep the current prototype’s single button as the explicit fallback acknowledgement control.
- **owner gets:** The pendant can stop speaking private information into an empty room and can tell the owner whether an important response was actually delivered to a private listening endpoint, rather than confusing cloud upload with being heard.
- effort: High for the product revision: sensor/PCB/enclosure work, low-power firmware, bridge protocol changes, relay policy, and privacy/failure-mode testing. Prototype with a strap contact electrode and bridge acknowledgements before committing to industrial design.  ·  risk: False not-worn readings could hold an answer; recover with an explicit button or spoken “play privately” command. Sensor data could reveal routines; process it locally, transmit coarse state only, and provide a hardware-disable setting. Never treat presence as authorization for destructive actions.
- cost: Roughly $1–4 BOM increase for contact sensor, IMU and supporting components, plus tens to hundreds of microwatts to a few milliwatts depending on sensor duty cycle. No significant model/API cost.  ·  latency: Presence state can update in 100–500 ms; bridge acknowledgement adds one control packet and usually under 200 ms. It may delay playback when state is uncertain, deliberately favoring privacy.
- security: Adds a new physical side channel; avoid raw sensor uploads, encrypt and authenticate bridge telemetry, rotate pairing keys, and expire state quickly. Output policy must fail closed for private content.
- depends on: A shared output-policy and heard-receipt protocol; Authenticated pendant–ESP32 bridge telemetry; Product audio/privacy acceptance tests; A user-visible way to override a held response locally


## What it asked for

_Nothing._
