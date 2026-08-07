# Harness derivation — unified — round 111

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio architecture** — Current prototype cannot honestly claim robust 24 kHz duplex: nRF9160 Opus encode+decode consumes ~87% of one core, capture is 15,625 Hz, and the ESP32 bridge is SBC-only 44.1 kHz with a documented starvation failure.
  - evidence: get_hardware_spec(audio) and get_hardware_spec(bridge): 25.4 ms decode + 15.0 ms encode per 60 ms; HUZZAH32 A2DP hard-locked 44.1 kHz and 44 kB buffer starved Bluetooth.
- **timezone** — Memory says owner timezone America/Chicago, while machine-context established earlier reported America/New_York; scheduled routines therefore need an authoritative owner timezone before changing or interpreting times.
  - evidence: discover(owner) remembered.timezone=America/Chicago; established probe_http GET /machine-context reported timezone America/New_York.

## Capabilities it proposed

### "“If my pendant audio is failing, keep the conversation going without making me repeat myself, and tell me what changed.”"
- **useful because:** A wearable should degrade gracefully: the owner still gets an answer or can approve a task during LTE, Bluetooth, or speaker trouble, while the system preserves the exact in-flight intent and later gives one concise recovery receipt instead of silently dropping it.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime model only for the live utterance and a one-sentence spoken fallback; use a cheaper background model to reconcile queued transcript fragments, action state, and recovery receipts.
- **latency:** Detect local audio/link degradation in under 250 ms; switch to a short spoken/LED fallback within 1 s; background reconciliation may take minutes and should not block the owner.
- **cost:** Usually one realtime turn plus a small background summarization (~$0.01–$0.05 depending on audio duration); the dominant cost is retransmitted audio, so cap retries and prefer a compact transcript/event frame.
- **security:** A degraded path must not accidentally execute an irreversible browser or Mac action: preserve the existing confirmation policy, encrypt queued transcript fragments, expire them quickly, and require explicit confirmation again if intent or identity confidence changes. Dashboard should show which words and actions were recovered.
- **missing:** pendant-local link/audio health events and a resumable interaction journal; audio-path preflight receipt and fault-injection test coverage; an explicit queued-action resume policy; a local output-mute/privacy latch; a durable receipt index that joins pendant, relay, Mac, and browser request IDs


## Changes it proposed to its own stack

### `hardware` — For the product revision, replace the HUZZAH32 Classic-Bluetooth A2DP bridge plus nRF9160 audio burden with a dedicated low-power audio companion (nRF5340 Audio or equivalent) connected to the LTE modem over a framed SPI link: run 24 kHz LC3/PCM buffering and Bluetooth LE Audio there, with hardware clocking, ≥512 kB RAM, a real fuel gauge, and a physical amplifier/mute path. Keep the nRF9160 for LTE/control, but move encode/decode, jitter buffering, and headphone transport off its nearly saturated single core.
- **owner gets:** The pendant can hold a natural 24 kHz conversation without the current 15.6/31.25/44.1 kHz conversions, Bluetooth starvation, or silence after a buffer hiccup; it also reports honest battery remaining and can mute locally even when the relay or Mac is unreachable.
- effort: High: product PCB and enclosure revision, LE Audio qualification, SPI framing/firmware protocol, codec and RF coexistence validation, and end-to-end voice tests. Prototype with an nRF5340 DK before committing the board.  ·  risk: New RF/firmware complexity and headphone compatibility failures; retain a wired/Classic-Bluetooth fallback during rollout, gate LE Audio per headset capability, and make the old bridge path selectable. A bad SPI or companion reset must fail silent and reconnect rather than leak audio.
- cost: Roughly +$12–25 BOM in volume for companion, PMIC/fuel gauge, codec/amp, and RF/PCB changes; negligible API cost. Power should fall during audio versus burning ~87% of the nRF9160 core, though LE Audio transmit duty cycle must be measured.  ·  latency: Expected 20–50 ms lower and substantially less jitter by eliminating two resamplers and moving buffering to a clocked audio MCU; LTE round-trip remains unchanged.
- security: Audio crosses an additional MCU and SPI boundary: authenticate/control-frame sequence numbers, keep keys in the modem-side secure world, disable debug in production, and ensure mute is hardware-enforced.
- depends on: 24 kHz superwideband end-to-end acceptance criteria; audio-link fault injection and preflight receipts; product pendant constraints beyond the current nRF9160 DK; a tested LE Audio headphone compatibility matrix

### `hardware` — Add a two-microphone near-field array and a dedicated vibration/bone-conduction output transducer to the product pendant, with a small always-on audio DSP front end. Use the array for beamforming and wind/noise suppression before LTE upload, and let the owner choose ordinary speaker, bone conduction, or both. Keep the existing codec path as a compatibility mode rather than treating one I2S microphone and an open speaker as the final industrial design.
- **owner gets:** They can talk to the pendant on a street, in a café, or beside other people and actually be understood; replies can be heard privately without broadcasting personal mail, calendar, or account information. This makes the assistant dependable in the situations where wearing it matters most, not just in a quiet room.
- effort: High: acoustic/mechanical design, two-channel AEC and beamforming firmware, wind and clothing-rub testing, hearing-safety tuning, and a production headset/output compatibility study. Build an enclosure prototype and collect consented noisy-environment samples before freezing the DSP.  ·  risk: Poor microphone spacing or vibration coupling could make recognition worse, and bone conduction varies substantially by fit and wearer. Provide a hardware output selector, automatic gain limits, a conventional speaker fallback, and a calibration/self-test; never use the microphone array to infer or retain bystanders' speech beyond the active interaction.
- cost: Approximately +$8–20 BOM in volume for the second microphone, DSP/audio front end, transducer, driver, and mechanical changes; no meaningful per-request API cost. Power rises during active DSP/output, so duty-cycle the always-on detector and measure it against the battery target.  ·  latency: Adds roughly 5–15 ms local DSP latency, but can reduce retransmissions and recognition retries in noise, improving effective conversational latency.
- security: A second microphone increases accidental bystander capture risk. Keep wake detection and raw buffers local, discard non-trigger audio immediately, expose a physical recording indicator, and upload only the post-trigger speech window. Bone-conduction output reduces disclosure but is not private at high volume, so retain output-level limits and a mute control.
- depends on: production acoustic and enclosure constraints; end-to-end noisy-environment speech intelligibility targets; local privacy indicator and output-mute behavior; validated 24 kHz audio transport after the front-end DSP


## What it asked for

_Nothing._
