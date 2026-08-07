# Harness derivation — faculty-judgement — round 110

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current cross-surface readiness** — Relay and Mac bridge are online and relay reports durable audio/persistent state, but browser extension is offline with 10 pending commands; computer-use is disabled because Accessibility and Screen Recording are not granted. The current pipeline has 24 kHz Mac TTS output but an observed live uplink at 15,625 Hz, so “24 kHz end to end” is not yet true.
  - evidence: GET /ops/status and GET /pipeline at round 110: browser online=false pendingCommands=10, accessibility.trusted=false, screenRecording.granted=false; pipeline telemetry shows input sampleRate=15625 and TTS sampleRate=24000.

## Capabilities it proposed

### "“Hold this for me until I have a quiet ten minutes.” The pendant should save what I said, have the relay and my Mac/browser gather only the relevant private context, and later give me a short cited audio packet with the decision or next step—without sending, submitting, or changing anything."
- **useful because:** This turns an interruption into progress instead of another forgotten note. The pendant is the only surface present at the interruption, the relay can keep the task alive, and the Mac/browser are the only places that can inspect private mail, calendar, files, and logged-in pages. It is deliberately preparation-only, so the owner gets value without an accidental commitment.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use gpt-realtime-2.1 only to capture/confirm the short handoff and play the final packet; use gpt-5.6-luna background jobs for evidence gathering and synthesis; use gpt-4.1-mini only for browser visual extraction if needed.
- **latency:** Acknowledge the handoff on the pendant in under 2 seconds; background evidence collection may take 1–5 minutes. Deliver at the next owner-selected quiet window, or queue it durably if every surface is offline.
- **cost:** Roughly $0.02–$0.10 per handoff depending on browser pages and synthesis; realtime audio and repeated private-page extraction dominate.
- **security:** Private mail/calendar/browser content stays on the authenticated Mac/browser path and only a minimized, cited evidence packet crosses to the relay. Never send mail, submit forms, delete, buy, or create external commitments without a separate owner approval. Expire raw audio and page captures quickly; show sources and an undo/clear control in the dashboard.
- **missing:** A durable handoff record linking pendant capture, evidence jobs, and final audio packet; an owner-controlled quiet-attention window and delivery acknowledgement queue; a cross-surface preflight/recovery path when the browser is offline or evidence becomes stale; a compact provenance/citation format for spoken packets

### "“Answer me privately; I’m in public.” The pendant should classify whether the reply contains sensitive information, keep private evidence on the Mac/browser, and deliver the answer through a private listening channel—or silently defer it—rather than speaking it aloud around other people."
- **useful because:** Today the owner must choose between getting useful assistance and exposing mail, calendar, health, finance, or work details to nearby people. This makes the pendant socially safe: it can still use the Mac and authenticated browser for rich answers, while the owner receives only an appropriately private rendering.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use the realtime model only for the live request and a short sensitivity decision; use the slower Mac planner for private-page retrieval and answer synthesis. A deterministic policy layer must override the model for secrets, authentication data, and owner-defined sensitive categories.
- **latency:** Acknowledge mode selection in under 500 ms and deliver a short answer in under 5 seconds when context is already available. If evidence gathering takes longer, provide a neutral private “working” cue and queue the result without speaking content aloud.
- **cost:** About $0.01–$0.06 per request; private browser retrieval and synthesis dominate, not the sensitivity classifier.
- **security:** Raw private page content must remain on the authenticated Mac/browser path; only the minimum answer crosses the relay. The device must never announce sensitive text while privacy mode is uncertain. Require a physical mode confirmation for ambiguous cases, provide a hard local mute/stop control, and log only policy decisions rather than spoken content.
- **missing:** A product pendant with a genuinely private output path (bone-conduction, near-ear speaker, or encrypted paired earbud) and a local proximity/wear-state sensor; an authenticated sensitivity-policy evaluator with owner-editable categories and a fail-closed default; an end-to-end delivery acknowledgement that distinguishes privately heard, deferred, and accidentally audible; relay and Mac routing that keeps citations/evidence off the spoken/public channel while retaining them in the dashboard


## Changes it proposed to its own stack

### `hardware` — Replace the provisional nRF9160-DK audio path with a product audio front end: a low-power stereo/mono 24 kHz-capable ADC/DAC (or dedicated audio DSP) connected over I2S to a cellular/application MCU, with DMA ring buffers and hardware clocking. Negotiate an explicit audio profile at session start: 24 kHz superwideband when battery/network/CPU budget permit, 16 kHz fallback otherwise. Keep Opus framing compatible at the relay boundary, but carry sample rate and profile in authenticated session metadata so the relay never silently resamples a supposedly 24 kHz call.
- **owner gets:** The owner gets genuinely clearer, more natural speech in both directions rather than a 15.625/16 kHz microphone being marketed as a 24 kHz path. The fallback preserves battery and call reliability when conditions are poor, while the explicit profile prevents confusing quality regressions.
- effort: High: select codec/ADC, lay out and validate a new board, add Zephyr DMA/audio-clock drivers, tune Opus at 24 kHz under real cellular load, and add relay negotiation plus end-to-end waveform/latency tests.  ·  risk: More BOM complexity, power draw, RF/audio interference, and firmware memory pressure. Recover with the existing dev-kit profile as a compatibility mode, watchdog the audio coprocessor, and fall back to 16 kHz on underrun or thermal/battery thresholds.
- cost: Approximately $3–$12 added BOM in low volume plus board redesign; roughly 20–80 mW additional audio-front-end draw depending on codec. API cost is unchanged; 24 kHz Opus may modestly increase bandwidth.  ·  latency: Potentially 10–30 ms lower buffering with DMA, but codec load can add processing time; negotiate a 60 ms or 20 ms frame profile and measure mouth-to-ear latency end to end.
- security: Authenticated profile negotiation and signed firmware are required; raw microphone audio remains transient and should not be retained on the device beyond ring buffers.
- depends on: End-to-end 24 kHz acceptance tests that inspect capture, relay transcode, decode, and speaker output rather than route labels; relay audio-profile negotiation and telemetry; a power/battery policy for selecting 24 kHz versus fallback; hardware prototype replacing the current nRF9160-DK assumptions

### `integration` — Add a nightly, non-invasive audio conformance run that injects a known swept-tone and speech fixture at the pendant capture boundary, records relay ingress/egress metadata, verifies the Mac TTS PCM, Opus packet sample-rate declarations, decoded pendant output, clipping, underruns, and mouth-to-ear timestamps, then writes one signed receipt and alerts only on regression. Include a separate 24 kHz claim gate: the pipeline may say “24 kHz end to end” only when capture and playback measurements both pass, otherwise it must say which leg fell back.
- **owner gets:** The owner will stop receiving a falsely reassuring “24 kHz” label when only Mac TTS is 24 kHz. Regressions become visible before a daily conversation fails, without recording their private conversations.
- effort: Medium: deterministic fixture generator, relay test endpoint, pendant diagnostic mode, telemetry schema, and dashboard trend/alert view.  ·  risk: A faulty fixture or clock can create noisy alerts; isolate tests from live audio, rate-limit alerts, and retain only aggregate metrics plus signed receipts. Never upload owner speech.
- cost: Negligible API cost; a few scheduled Mac/relay invocations and small metric storage.  ·  latency: No live-path impact; a nightly run may use 1–3 minutes of device time.
- security: Use synthetic audio only, authenticated test sessions, and redact packet payloads from logs.
- depends on: A device diagnostic/test mode that can inject and measure synthetic audio; sample-rate/profile metadata carried through relay transcoding; durable receipt storage and an owner-visible regression alert; the planned 24 kHz hardware/firmware path

### `hardware` — Design the wearable around a privacy-capable output path instead of the current open playback assumption: add a near-ear bone-conduction or sealed directional transducer, a skin-contact/wear sensor, a hardware mute switch, and a secure audio-profile handshake to the relay. The firmware must refuse spoken playback when the device is not worn or the private channel is not confirmed, while retaining the existing open speaker only for explicitly non-sensitive responses.
- **owner gets:** They can use the assistant in meetings, transit, cafés, and shared homes without broadcasting private information. A physical mute and fail-closed wear check make privacy dependable even when the network or model is wrong.
- effort: High: industrial design, acoustic and RF coexistence testing, power budgeting, secure accessory pairing, new firmware drivers, and relay policy integration.  ·  risk: Bone conduction can be uncomfortable or hard to hear in loud environments; the sealed path may increase heat and battery use. Recover with an explicit open-audio fallback only after a physical button confirmation, plus local volume and mute controls.
- cost: Approximately $8–$25 incremental low-volume BOM and 30–150 mW additional draw depending on transducer and amplifier; no material per-call API cost.  ·  latency: Negligible signal latency, though pairing and wear-state confirmation may add 100–300 ms before playback.
- security: The wearable/accessory pairing key must be hardware-backed; never treat Bluetooth connection alone as proof that audio is private. Fail closed on lost pairing, removed wear contact, or uncertain mode.
- depends on: A relay-side sensitivity policy and fail-closed routing contract; authenticated private-output acknowledgement telemetry; a physical enclosure revision beyond the current nRF9160 development kit; synthetic and human acoustic leakage tests in realistic public environments


## What it asked for

_Nothing._
