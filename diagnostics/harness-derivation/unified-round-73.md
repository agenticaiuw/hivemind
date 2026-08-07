# Harness derivation — unified — round 73

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If the connection stutters while you’re speaking, keep the answer understandable: pause or recover cleanly, and let me say ‘resume that’ or ‘repeat the last part’ without starting over.”"
- **useful because:** Today the measured LTE-M link drops about 7.8 seconds of uplink when duplex traffic contends, while the pendant decoder is already heavily loaded. The owner should hear a coherent answer rather than clipped audio, and recover hands-free when attention is elsewhere. This is genuinely cross-node: the pendant detects decode/jitter state, the relay retains addressed audio segments and delivery receipts, and the Mac can regenerate only the missing/last segment.
- **path:** pendant → relay-realtime → mac-planner → dashboard-ux
- **model tier:** Deterministic packet/jitter state and segment replay first; use background gpt-4.1-mini only to produce a short recovery summary when replay is impossible. Do not spend realtime-tier tokens on transport repair.
- **latency:** Normal playback adds no intentional delay beyond a 1–2 second jitter buffer. ‘Resume’ should restart within 500 ms after the button/voice intent; regeneration may take 2–4 seconds.
- **cost:** Negligible per replay (stored Opus/PCM already produced); regeneration is one short background-model call, roughly a few thousand input tokens at most. Storage is bounded by retaining only the current response and a small recent segment window.
- **security:** Audio segments and transcripts are private and must use the existing session authorization; do not expose cross-session replay. Auto-replay is safe, but regeneration must not repeat sensitive content into an open environment without the same output policy.
- **missing:** A shared segment manifest with sequence numbers, timestamps, codec/sample-rate metadata, and per-segment delivery/played receipts; Pendant-side jitter/decode feedback and a local ‘resume last response’ intent surviving a dropped link; Relay endpoint to replay a missing range or ask the Mac to regenerate a specific sentence; An explicit owner-facing audio interruption/recovery state in the dashboard and spoken UI

### "“If I take the pendant off, lose LTE, or walk out of range, keep the conversation alive and hand the reply to whichever of my Mac, browser, phone, or pendant is available; when I put the pendant back on, continue from exactly where I stopped.”"
- **useful because:** Today a spoken turn is effectively tied to one live pendant path: a network or device transition can strand the response or force the owner to repeat themselves. The owner should experience one conversation that follows them across their actual surfaces, with no duplicate speech and no lost work. This is not merely audio replay: it requires identity-aware handoff, playback position, and surface selection across the wearable, always-on relay, Mac agent, browser sessions, and iOS/dashboard client.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** Use deterministic session and playback-state reconciliation for handoff. Use background gpt-4.1-mini only to summarize a partially heard turn when an exact continuation is impossible; reserve realtime for the live conversation itself.
- **latency:** A healthy handoff should be under 1 second for state transfer and under 3 seconds to begin playback on a fallback surface. Rejoining the pendant should not repeat more than the last unacknowledged sentence.
- **cost:** Near-zero model cost for state transfer; bounded metadata and short audio-segment storage per active session. A rare fallback summary costs one small background call, dominated by transcript context.
- **security:** Only already-authorized devices in the owner's session may receive speech or transcript. Browser content must never be used as a fallback output without an active authenticated browser session. Encrypt handoff state, expire it promptly, and require an explicit privacy mode to disable automatic fallback in public settings.
- **missing:** A single session identity and lease shared by pendant, Mac, browser, and iOS surfaces; Per-surface availability, output capability, and last-heard/playback acknowledgements; A relay handoff state machine that chooses one output owner and prevents duplicate delivery; A compact transcript/audio checkpoint format that can resume or summarize without replaying sensitive history; A user-visible setting for allowed fallback surfaces and automatic handoff


## Changes it proposed to its own stack

### `hardware` — Replace the prototype nRF9160 DK audio runtime with a production pendant architecture that gives audio its own compute headroom: an nRF5340-class application MCU (or equivalent dual-core MCU with DSP/FPU and substantially more RAM) paired with the LTE-M modem, local PSRAM/flash ring storage, and a hardware audio clock. Keep the modem link and 24 kHz PCM contract, but move Opus encode/decode and jitter buffering off the modem application core; add a small local speaker/mic amplifier with explicit clock domains.
- **owner gets:** The current 64 MHz nRF9160 spends roughly 87% of one core when encoding and decoding, and the measured LTE-M duplex call loses about 7.8 seconds of uplink. More deterministic audio headroom means the owner can interrupt, listen, and speak naturally instead of hearing gaps or delayed replies. Local ring storage also allows a short replay after a transient link loss.
- effort: High: electrical redesign, RF coexistence validation, Zephyr port, audio-driver and power-profile work, enclosure/prototype spins, and an end-to-end acceptance test over congested LTE-M. Preserve the current PCM/Opus protocol so relay changes remain incremental.  ·  risk: Higher BOM, power draw, and RF/EMI complexity; a new MCU/modem split can introduce clock drift and wakeup bugs. Recover with a dev-board parallel prototype, measured power budget, loopback tests, and a fallback mode that disables full duplex before audio becomes corrupted.
- cost: Roughly +$15–35 prototype BOM versus the DK (production volume could be lower); expect approximately +20–60 mW during active audio depending on MCU and amplifier, offset partly by shorter modem active time. No per-call API cost change.  ·  latency: Should reduce encode/decode contention and make packet scheduling predictable; target <60 ms local buffering plus network latency, versus current stalls under duplex load.
- security: More local buffering increases the amount of sensitive audio physically stored; encrypt ring storage, cap it to the last few response segments, erase on session end, and expose a hardware privacy indicator.
- depends on: Define and test the 24 kHz superwideband end-to-end acceptance thresholds; Implement link-aware duplex scheduling and segment receipts before freezing the hardware interface; Choose production modem/antenna and validate power and RF coexistence

### `relay` — Add an end-to-end audio quality ledger, not just job completion: each response gets immutable segment sequence numbers; the pendant reports received/decoded/played ranges, PLC insertions, under-runs, and local queue depth; the relay joins those with LTE RSSI/RTT and TTS/Opus metadata into a compact per-turn quality record. Compute a deterministic quality grade and surface the exact first missing segment plus a recommended recovery (replay, regenerate, or ask the owner).
- **owner gets:** Instead of merely hearing a bad answer and wondering whether the model or network failed, the owner gets a truthful explanation and automatic recovery. Repeated failures become actionable engineering evidence rather than anecdotes from UART logs.
- effort: Medium-high: version the audio metadata, add pendant telemetry and relay aggregation, expose a read-only diagnostic view, and test clock/sequence edge cases. It can be rolled out alongside the current PCM/Opus path.  ·  risk: Telemetry can be wrong if clocks reset or packets are duplicated, and detailed audio diagnostics could retain sensitive content. Store hashes and timing, not raw speech; use monotonic sequence numbers, explicit session boundaries, and mark grades unknown when telemetry is incomplete.
- cost: Small D1/R2 metadata overhead per turn and negligible deterministic CPU; no model call required. Retention should be days, not the existing 30-day audio policy, unless the owner opts in.  ·  latency: No playback-path delay; telemetry can batch every few seconds and finalize asynchronously after playback.
- security: Quality records must inherit the audio session ACL and redact transcript/text. Diagnostic exports require explicit owner action.
- depends on: A versioned audio segment manifest and delivery/played receipts; A pendant firmware event for decoder under-run, packet loss concealment, and queue depth; A read-only dashboard/route for per-turn audio quality and recovery status


## What it asked for

_Nothing._
## Its own summary

Fresh work this round: I confirmed the pendant is a 64 MHz nRF9160 prototype where simultaneous Opus encode/decode consumes ~87% of one core, and LTE-M duplex contention has already caused ~7.8 seconds of uplink loss. I recorded (1) a cross-surface ‘resume/repeat the last spoken segment’ capability using segment manifests, pendant jitter feedback, relay replay, and Mac regeneration fallback; (2) a production hardware change separating audio compute from the modem; and (3) an end-to-end audio-quality ledger that reports missing/played segments, underruns, concealment, and a deterministic recovery recommendation. The existing pipeline and receipt routes are connective primitives, not complete delivery semantics.

**Biggest unknown:** I still need authoritative 24 kHz end-to-end acceptance thresholds, the production pendant constraints (power, enclosure, BOM, modem/bridge choice), and the owner's privacy/retention boundary for replayable audio. The already-requested audio fault injector, validation tool, delivery-receipt index, and local recovery skills would let this be verified rather than merely designed; none has surfaced in this round.

