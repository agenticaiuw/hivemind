# Harness derivation — faculty-judgement — round 79

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Read my private brief, but keep it private if anyone is nearby.”"
- **useful because:** The owner should be able to use the pendant in public without accidentally broadcasting email, calendar, account, or browser content. The system would classify the requested content's sensitivity, use a local bystander/voice-presence signal, and either play it privately through the paired headset, reduce it to a non-sensitive cue, or ask for a button confirmation before speaking. This is a safety boundary no Mac-only or browser-only agent can enforce at the moment of audio output.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the spoken request and final one-sentence decision; a small background classifier handles local acoustic presence and sensitivity labels. Do not send ambient audio off-device. Mac/browser agents supply the content and provenance; relay arbitrates output mode.
- **latency:** Under 300 ms for a local bystander/voice-presence decision; under 1 s to switch from speech to a haptic/short cue. Content retrieval can remain asynchronous, but no sensitive sentence should start until the gate resolves.
- **cost:** Negligible model/API cost for the local gate; occasional low-tier classification of content metadata only. Hardware prototype roughly $3–8 for a short-range presence sensor or better microphone/beamforming path, plus firmware and headset integration work.
- **security:** Ambient audio must be processed and discarded locally; never upload recordings or identify people. Sensitivity labels need provenance and conservative defaults: unknown/private content is blocked from speaker output. A false negative is a privacy incident, so require an explicit pendant button hold to override. Do not reveal the sensitive text in notifications or dashboard previews.
- **missing:** A pendant-local acoustic presence/bystander detector or proximity sensor, with an honest confidence score; A relay output gate that can interrupt an in-progress /pipeline/audio stream before the next sentence; Typed sensitivity labels and source provenance propagated from browser and Mac reads into the audio request; A user-visible policy setting for headset-only, haptic-summary, and hold-to-speak override


## Changes it proposed to its own stack

### `hardware` — Replace the prototype HUZZAH32 SBC-only A2DP bridge with a small BLE-Audio-capable bridge (nRF5340-class, with LC3/LE Audio and SBC fallback), and add a real fuel-gauge/charger IC. Keep the pendant's 24 kHz Opus contract, but make the bridge negotiate a native 24/48 kHz mono voice path when the headset supports it; otherwise resample in bounded blocks for legacy A2DP. Add a bridge capability/clock report so relay and pendant select the best mode instead of assuming 31,250→44,100 Hz.
- **owner gets:** The owner's promised 24 kHz voice quality would survive the last hop instead of being squeezed through a hard-locked 44.1 kHz SBC prototype. Speech should sound clearer with less buffering and fewer dropouts, the bridge can become a small wearable rather than a development board, and the fuel gauge makes the morning battery brief truthful instead of guessing.
- effort: Medium-high: schematic/PCB and enclosure revision, BLE Audio interoperability testing across the owner's headphones, Zephyr audio transport changes, capability negotiation in relay, and a legacy-SBC fallback. Prototype in 2–4 weeks; production validation longer.  ·  risk: Some current AirPods/headsets may not expose LE Audio, so SBC fallback is mandatory. A bad clock-negotiation implementation could create drift or silence; retain the existing fixed-rate mode behind a feature flag and add loopback/dropout tests. Fuel-gauge calibration can be wrong until characterized. Recovery is firmware rollback to the current A2DP bridge.
- cost: Approximately $15–30 incremental prototype BOM (nRF5340 module, audio/power parts, fuel gauge, PCB/enclosure); roughly 50–150 mW bridge draw depending on radio and codec, versus the current dev-board footprint. No per-call API cost.  ·  latency: Native LE Audio can remove one resample and reduce buffering by roughly 20–60 ms; SBC fallback remains near current latency. Capability negotiation adds one short setup exchange only.
- security: Bluetooth pairing keys remain on the bridge; expose only codec/rate/health metadata to relay, never microphone PCM. Require authenticated firmware updates and erase pairing keys on reset/RMA.
- depends on: End-to-end 24 kHz pendant/relay audio acceptance tests; A documented headset compatibility matrix and decision on whether SBC fallback is required; A bridge capability handshake in the relay/pendant protocol

### `hardware` — Build a production wearable audio bridge around an LE-Audio-capable nRF5340-class radio, with LC3/24 kHz mono support, mandatory SBC fallback for existing headphones, and a fuel-gauge/charger IC. Add an authenticated bridge-capability handshake (codec, sample rate, clock, battery, and dropout counters) so the pendant and relay choose and verify the actual end-to-end audio mode rather than assuming the current HUZZAH32's fixed 44.1 kHz SBC path.
- **owner gets:** The owner should be able to wear a small, dependable pendant and hear natural 24 kHz speech without the current development-board bridge degrading it, silently starving, or lying about battery state. They would get clearer voice, lower buffering, and a truthful warning before the wearable dies.
- effort: Medium-high hardware revision plus Zephyr transport, relay negotiation, headset interoperability, enclosure, calibration, and end-to-end dropout testing. Keep the existing bridge as a rollback fixture during validation.  ·  risk: Some existing headphones may lack LE Audio; SBC fallback must remain. Clock negotiation or RF coexistence bugs could cause silence, so retain a fixed-rate compatibility mode and local watchdog rollback. Battery estimates require per-cell calibration.
- cost: About $15–30 in prototype components and PCB/enclosure work; approximately 50–150 mW bridge draw depending on radio and codec. No per-call model cost.  ·  latency: Native LE Audio can remove one resampling stage and reduce buffering by roughly 20–60 ms; legacy SBC remains at current latency. Capability negotiation costs only setup time.
- security: Pairing material stays on the bridge; relay receives only authenticated capability/health metadata, never raw PCM. Require signed firmware and erase keys on service reset.
- depends on: A headset compatibility decision (current AirPods versus LE Audio-capable targets); An end-to-end 24 kHz audio acceptance test covering pendant, relay, bridge, and headset; Protocol support for authenticated capability and clock negotiation


## What it asked for

_Nothing._
## Its own summary

Discovered the live owner context and audio hardware. The current pendant captures 15.625 kHz, uplinks Opus at 16 kHz, decodes 24 kHz, then hands audio to an ESP32 bridge that is hard-locked to 44.1 kHz stereo SBC with tight RAM. I proposed a genuinely new hardware change: a compact BLE-Audio/LC3 bridge with SBC fallback, explicit codec/clock negotiation, and a fuel gauge, so the owner's 24 kHz goal survives the final hop and battery reports become real.

**Biggest unknown:** The product decision is still missing: which headphones must remain compatible (especially current AirPods), and whether the owner prefers a small replacement bridge now or a full pendant/bridge redesign. That determines LE Audio-only versus mandatory SBC fallback and the acceptance tests.

