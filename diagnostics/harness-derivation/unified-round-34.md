# Harness derivation — unified — round 34

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m in public—make this private,” and later, “I’m alone again.”"
- **useful because:** Today the owner cannot atomically make a spoken AI conversation safe across the pendant, Mac, and logged-in browser. This would immediately reduce accidental disclosure: the wearable, relay, Mac, and browser all enter one privacy posture, then restore normal behavior with an explicit receipt.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime only for the short intent classification and confirmation phrase; deterministic policy enforcement and state propagation on the relay, Mac, pendant, and extension. No expensive model call for each event.
- **latency:** Acknowledge locally within 300 ms; propagate to online surfaces within 2 seconds. If disconnected, the pendant must still mute/suppress locally and replay the state when the link returns.
- **cost:** Near-zero per invocation after implementation; one short realtime turn when the owner speaks, with negligible state-sync traffic. Engineering cost is the main cost: a shared privacy-state protocol and platform enforcement.
- **security:** The privacy state must fail closed: pendant playback mutes, microphone transmission pauses or switches to an explicit indicator, relay refuses to speak sensitive fields, Mac screen capture/vision stops, browser extension blurs or hides authenticated tabs and cancels queued browser commands. Never claim privacy if a surface is offline; the pendant LED/button must show local state, and the dashboard must show which surfaces acknowledged it. Exiting privacy mode requires an explicit owner gesture or phrase, and all transitions need an auditable receipt without storing ambient audio.
- **missing:** A signed, shared privacy-state protocol with monotonic epochs and fail-closed defaults; Pendant firmware mute/privacy latch and visible status indication; Mac Screen Recording/Accessibility enforcement hooks; Browser extension tab masking and command cancellation; Relay policy that classifies data sensitivity and suppresses sensitive speech; A cross-surface acknowledgement/receipt view


## Changes it proposed to its own stack

### `integration` — Add an end-to-end wearable audio certification and drift monitor. On demand (and after firmware/relay changes), the pendant enters a 3-second local loopback test: it emits a marked playback sequence, captures the microphone return, and sends timestamped Opus frames plus clock/rate metadata. The ESP32 bridge reports I2S clock and underrun counters; the relay correlates input/output packet timestamps and verifies 24 kHz decoded output, resampling, jitter, loss, and half-duplex turn timing; the Mac agent stores a signed receipt and exposes a concise pass/fail report with the failing segment and recovery suggestion. During normal calls, retain only aggregate counters and raise a repair job when drift or repeated underruns cross thresholds, without retaining raw audio by default.
- **owner gets:** The owner can know before a real conversation whether the pendant will actually capture and play intelligible 24 kHz audio, and gets a precise explanation when it will not. Silent clock drift, bridge underruns, and LTE timing failures become one actionable repair instead of a vague 'the audio sounded bad'.
- effort: Medium-high: firmware test mode and counters, ESP32 bridge telemetry, relay correlation/validator, Mac receipt endpoint and a spoken/on-device result. Requires fixtures or a known acoustic loopback during manufacturing, plus field-test thresholds.  ·  risk: A false failure could interrupt a conversation or prompt needless repair; keep certification manual/opt-in initially, never auto-reset during a call, and make the test abortible with the button. Acoustic environments can distort the loopback, so distinguish electrical/I2S loopback from room-acoustic confidence. Recovery is to fall back to the current 16 kHz uplink path and record diagnostics.
- cost: Negligible API cost: counters and one short test transcript/receipt; no raw audio retained unless explicitly enabled. Small firmware/bridge storage overhead; no new hardware required, though a factory jig microphone/speaker would improve calibration.  ·  latency: Adds about 3–5 seconds only when explicitly testing; normal calls add timestamp/counter handling with no model round trip.
- security: Raw test audio remains on-device/in transit only for the test and is discarded; receipts contain timing and quality metrics, not speech. Any upload of waveforms requires explicit consent.
- depends on: 24 kHz superwideband acceptance criteria; audio_pipeline_validate implementation; firmware/bridge access to I2S clock and underrun counters; a durable Mac audio-certification receipt endpoint

### `hardware` — Replace the prototype HUZZAH32 SBC-only A2DP bridge with a production audio bridge that supports Bluetooth LE Audio/LC3 (or a wired USB-C digital-audio fallback), with hardware clocking, DMA underrun telemetry, and enough RAM for two jitter buffers. Keep the pendant/relay codec contract at 24 kHz, and let the bridge negotiate the headset's native sample rate instead of forcing 31,250 -> 44,100 Hz SBC resampling. The relay and Mac agent should advertise the selected path and its measured latency in the audio receipt.
- **owner gets:** The owner gets clearer, more stable speech and fewer silent dropouts across modern earbuds, while retaining a wired fallback when Bluetooth is unreliable. The system can explain whether a problem is LTE, the pendant, or the headphones instead of hiding all failures behind one resampler.
- effort: High: select and validate a LE Audio-capable module/stack, redesign the bridge firmware and enclosure/power path, add headset compatibility testing, and update relay negotiation plus Mac/dashboard status. Keep the current ESP32 bridge as a compatibility backend during migration.  ·  risk: LE Audio interoperability and battery behavior vary by headset; some existing headphones will not work. Ship dual-mode fallback and a user-selectable wired/legacy SBC path. A bad negotiation must never leave the owner without audio; watchdog and local bypass restore the legacy bridge.
- cost: Prototype module/PCB and certification cost roughly tens of dollars per unit plus Bluetooth qualification; modestly higher bridge power during active audio. No per-call model cost; LC3 may reduce transport bandwidth and therefore LTE data/power.  ·  latency: Potentially lower and more predictable than the current SBC/resampling chain, but qualification must measure capture-to-ear latency per headset; target under 180 ms for the complete path.
- security: Bluetooth pairing keys remain on the bridge; add encrypted storage and a physical pairing gesture. Wired fallback avoids radio audio leakage. Do not upload headset identifiers unless needed for compatibility diagnostics.
- depends on: end-to-end 24 kHz audio certification; a negotiated audio transport protocol between pendant, relay, and bridge; product hardware/audio compatibility target; field fallback support for current HUZZAH32/SBC devices


## What it asked for

### `c6-dp7p` (context) — audio-path delivery phase
- why: The hardware facts show the current HUZZAH32 and nRF9160 are explicitly prototypes, while the owner's immediate goal is shipping 24 kHz audio. I need to know whether to optimize the next work for a demonstrable DK path or for the production redesign.
- would change: If prototype-first, I will prioritize firmware/relay validation and graceful fallback on the existing SBC bridge. If product-first, I will prioritize the LE Audio bridge and qualification plan, accepting that it cannot be completed on the current boards.

## Its own summary

Fresh discovery confirms the immediate audio blockers: pendant capture/uplink is 15.625 kHz/16 kbps, downlink decodes at 24 kHz but the HUZZAH32 bridge forces 31.25→44.1 kHz SBC, and LTE-M contention recently lost 388 uplink packets (~7.8 s). I recorded two new items: an end-to-end audio certification/drift monitor with signed receipts and a production LE Audio/USB bridge redesign with legacy fallback. I also queued a context question to choose prototype-first versus product-first delivery.

**Biggest unknown:** The authoritative 24 kHz acceptance thresholds and whether this round should implement against the current development boards or target the production audio architecture; the previously queued validator/workspace/permission requests remain the concrete execution dependencies.

