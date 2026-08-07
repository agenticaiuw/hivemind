# Harness derivation — unified — round 71

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current-device-reachability** — The Mac bridge is online, but the home Chrome browser device is offline with zero tabs; any browser-dependent continuity feature must degrade to Mac/pendant and must not assume a browser session exists.
  - evidence: discover(devices) returned home-macbook-bridge online and home-chrome offline, 0 tabs.

## Capabilities it proposed

### "“If my pendant connection gets bad, keep the conversation going through my Mac, then move it back to the pendant when the link recovers—without making me repeat myself.”"
- **useful because:** The current LTE-M path is half-duplex in practice and measured to lose about 7.8 seconds of uplink while the agent speaks. Today a dropped wearable link turns a live interaction into a failure. A session-preserving handoff would let the owner continue naturally: pendant remains the microphone/voice when healthy, Mac takes over only during a verified outage, and all surfaces retain the same transcript, pending action, and approval state.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime only for the handoff announcement and conversational continuity; use a cheap background model to reconcile the two audio streams/transcripts and generate a one-line recovery summary. Do not invoke the expensive model for transport health decisions.
- **latency:** Detect degraded media within 1.5 s, open Mac fallback within 3 s, and restore pendant within 5 s of stable link. Handoff announcement should be under 500 ms once the fallback is ready.
- **cost:** Low incremental API cost: health state and routing are deterministic; roughly one short background transcription/reconciliation call per handoff (about $0.005–$0.03 depending on audio duration). Main cost is engineering and local Mac audio plumbing, not inference.
- **security:** The Mac microphone and speakers must not activate silently: require an explicit owner-configured fallback policy and a visible menu-bar indicator, with a physical pendant double-press to cancel/restore privacy. Browser sessions and pending destructive approvals must remain bound to the original conversation and never be replayed after an uncertain handoff. Audio should stay on the existing authenticated relay; retain only a short encrypted handoff buffer.
- **missing:** A transport-agnostic conversation session object with sequence numbers and transcript checkpoints; Mac audio capture/playback bridge that can be enabled without Accessibility or Screen Recording permissions; A health/lease protocol distinguishing packet loss from intentional privacy mute; End-to-end audio acceptance thresholds and product audio compatibility target; Owner policy for whether Mac fallback may auto-answer or must be confirmed


## Changes it proposed to its own stack

### `relay` — Add a durable Conversation Media Lease and Handoff Protocol. Every live call gets a sessionId, monotonically increasing media sequence, transcript checkpoint, and current output target (pendant or Mac). The relay monitors bidirectional packet loss, jitter, silence, and websocket age; on a sustained threshold it emits a signed HANDOFF_OFFER containing the last acknowledged sequence and checkpoint. The Mac agent explicitly accepts or rejects, opens local audio, and sends a HANDOFF_ACCEPT. Relay then switches output/input routing without creating a new conversation. On recovery, perform the same lease exchange back to the pendant, discard duplicate frames by sequence, and expose a human-readable receipt in /jobs/:jobId/receipts and the dashboard. Never hand off an action approval itself: only the conversation state moves.
- **owner gets:** A weak LTE-M signal would no longer force the owner to start over or repeat an instruction. They get a continuous conversation with an honest, visible fallback and a recoverable transcript, while sensitive actions cannot accidentally execute twice.
- effort: High: relay state machine and durable session schema, pendant firmware lease messages, Mac audio bridge, and integration tests with packet-loss injection. Medium additional dashboard work.  ·  risk: False positives could switch audio while the pendant is still usable; use hysteresis and an owner-configured confirmation mode. A crash during handoff could leave both endpoints active; signed leases, one active epoch, duplicate suppression, and timeout rollback recover. If Mac audio permission is absent, announce failure on the pendant and continue degraded rather than silently opening another microphone.
- cost: Negligible inference cost; small durable relay/session storage and telemetry. Mac-side audio capture may require a native helper and modest battery/CPU use.  ·  latency: Adds at most 1–2 seconds during a handoff; steady-state media path unchanged.
- security: Improves security by making endpoint ownership explicit, preventing replay and duplicate approvals. Requires authenticated endpoint keys and short-lived leases; Mac fallback must display an active-mic indicator.
- depends on: End-to-end audio acceptance thresholds; Product audio compatibility target; A Mac audio bridge that does not rely on denied Accessibility/Screen Recording permissions; A physical or spoken privacy policy for whether fallback is automatic

### `hardware` — Replace the prototype single-I2S-mic nRF9160/ESP32 audio arrangement with a production pendant audio front end: a low-power audio DSP or application SoC with two closely spaced digital microphones, hardware acoustic echo cancellation/noise suppression, independent uplink/downlink DMA, and a modem-facing interface with enough buffering for concurrent 24 kHz playback and capture. Keep the nRF9160 as the LTE-M modem, but move Opus encode/decode off the 64 MHz application core or provide a second real-time audio core. Include a physical mic-power disconnect controlled by the privacy latch.
- **owner gets:** They could interrupt naturally while the pendant is speaking, and the pendant would remain intelligible in wind, a car, or a noisy room instead of losing their speech whenever downlink audio competes for the half-duplex LTE-M link. This is a real improvement in everyday conversation, not merely a software fallback.
- effort: High hardware and firmware redesign: acoustic/mechanical design, DSP tuning, modem/audio scheduling, RF coexistence validation, and a production prototype. Requires lab measurements with packet-loss and double-talk test fixtures.  ·  risk: A poor acoustic enclosure can worsen echo or introduce feedback; validate with calibrated speaker/mic tests and retain the existing single-mic mode as a diagnostic fallback. More components increase BOM and failure modes. Privacy risk is controlled by a hard mic-power disconnect, not just a software mute.
- cost: Roughly $8–$25 additional component/BOM cost for microphones, DSP/audio SoC, codec/PMIC and mechanical changes, plus higher board power (approximately 30–100 mW in active audio depending on DSP choice). No recurring model cost.  ·  latency: Hardware AEC/DSP should reduce processing latency; moving codec work off the modem application core should make 60 ms frame deadlines more reliable. Bring-up may temporarily add buffering during tuning.
- security: The physical microphone disconnect provides a trustworthy mute boundary. DSP firmware and update signing become part of the trusted audio path; prohibit remote firmware from bypassing the disconnect.
- depends on: A production pendant specification rather than the current nRF9160 development kit; End-to-end audio acceptance thresholds and product audio compatibility target; Acoustic enclosure and antenna/RF coexistence design; Signed firmware update and local privacy-latch implementation


## What it asked for

_Nothing._
## Its own summary

I discovered the live device state and added a genuinely new cross-surface capability: seamless conversation transport handoff between the LTE-M pendant and Mac, with transcript/media sequence continuity and no replay of approvals. I also recorded the relay-layer Conversation Media Lease/Handoff Protocol needed to implement it. The pendant path is currently prototype hardware, 15.625 kHz capture/16 kbps uplink, and measured contention loses about 7.8 seconds of speech; the Mac bridge is online while home Chrome is offline, so browser reachability cannot be part of the fallback assumption.

**Biggest unknown:** I still need the owner/product decisions and tests that determine when Mac fallback may activate: end-to-end audio acceptance thresholds, the product audio compatibility target, and whether fallback may auto-open the Mac microphone or must require confirmation. Engineering also needs a Mac audio bridge that works without the denied Accessibility/Screen Recording grants. I did not re-request already-pending contexts or permissions.

