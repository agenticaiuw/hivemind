# Harness derivation — unified — round 24

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-link-contention** — Current LTE-M half-duplex WebSocket is overloaded: 16 kbps uplink plus 24 kbps downlink recently lost 388 uplink packets (~7.8 s) while agent spoke; playback decode already consumes ~87% of one Cortex-M33 core. The ESP32 bridge is SBC-only 44.1 kHz stereo and cannot absorb large buffers (44 kB caused silence).
  - evidence: get_hardware_spec(all): network.measured, audio.codec, bridge.limit

## Capabilities it proposed

### "Keep a live conversation with me even when LTE-M is congested: prioritize my speech, keep the reply intelligible, and if words were lost, tell me exactly what was missed and resume without making me repeat everything."
- **useful because:** The current call can lose nearly eight seconds of the owner's speech when downlink audio overlaps uplink. A coordinated governor lets the pendant, relay, Mac TTS, and browser/action planner degrade gracefully instead of silently dropping intent.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** gpt-realtime-2.1 only for the live speech turn; gpt-5.6-luna on the Mac for post-turn reconstruction/action planning; no model call for packet scheduling or loss metrics.
- **latency:** Keep local speech priority decisions under 20 ms; target under 250 ms added turn latency. On detected loss, send a brief spoken repair prompt immediately, then let the slower Mac planner reconstruct context in the background.
- **cost:** About $0.00 additional for scheduling/telemetry; occasional reconstruction costs one background gpt-5.6-luna call, dominated by audio transcription/context size. Dashboard telemetry is negligible.
- **security:** Audio quality metrics and small missing-span transcripts leave the pendant; raw SD fallback remains failure-only and must be encrypted/deleted after delivery. Never execute an inferred browser action without the existing confirmation rules; show uncertainty and packet-loss evidence.
- **missing:** A shared duplex QoS protocol with sequence numbers, playout deadlines, loss reports, and explicit speech-priority mode across nRF9160, Worker, and Mac bridge; Relay support for short repair prompts and resumable audio ranges rather than treating a turn as one opaque stream; A Mac-side reconstruction job that can use transcript/audio gaps and browser context without replaying or duplicating actions; Acceptance tests for intelligibility and loss-repair behavior on congested LTE-M

### "Give me a genuinely private voice mode: when I say “private note” or flip a hardware privacy switch, the pendant must stop sending raw audio to the cloud, capture locally, and later let the Mac transcribe and file only the text I approve—without exposing the note to browser sessions or relay logs."
- **useful because:** Today every live voice turn depends on cloud transport, so a private thought cannot be captured with a trustworthy hardware boundary. This would let the owner use the pendant for sensitive ideas in public or offline, while still turning approved text into a reminder, note, or draft on the Mac.
- **path:** pendant → relay → mac-bridge → browser → dashboard → iOS
- **model tier:** No cloud model in private capture mode; use a local Mac transcription model in the background, then gpt-5.6-luna only after owner approval to structure or file the text. Realtime is used only outside private mode.
- **latency:** Hardware mute and local recording indicator must engage within 100 ms. After reconnection, transcription may take 1–2 minutes; filing is explicit and can wait for review.
- **cost:** Near-zero API cost until approval; local transcription uses Mac CPU. Optional approved structuring is one background gpt-5.6-luna call, dominated by transcript length.
- **security:** Requires a physically enforced mic disconnect or analog mute, not merely a software flag; tamper-evident LED/actuator state; encrypted local storage; relay must receive only opaque delivery metadata; browser extension and dashboard must refuse private-note contents unless the owner explicitly releases them. Destructive or external actions retain confirmation.
- **missing:** A production pendant privacy switch that electrically gates the microphone path and a trustworthy local indicator; On-device encrypted note container with key handling that never sends plaintext to the relay; Mac-local transcription/import protocol with explicit release tokens and browser/dashboard redaction; A testable privacy audit showing no raw audio, transcript, or sensitive filenames leave private mode before approval


## Changes it proposed to its own stack

### `firmware` — Implement a link-aware duplex audio governor on the nRF9160: every Opus packet carries a monotonic sequence number and deadline; a local scheduler reserves uplink airtime for microphone packets, sheds or lowers-priority downlink frames before speech, reports loss ranges, and marks SD fallback chunks with call/turn IDs. Add a small jitter buffer capped below the modem TLS record constraints and an LED error pattern for unrepaired loss.
- **owner gets:** When the network is busy, the owner hears a coherent answer and the system knows which part of their request was lost, rather than silently acting on a broken sentence or forcing them to start over.
- effort: Medium-high firmware, relay protocol, and test-harness work; requires controlled LTE-M contention tests and careful interaction with the single full-duplex I2S peripheral.  ·  risk: Aggressive downlink shedding can make replies sound clipped; recover with bounded playout deadlines, a feature flag, and automatic fallback to current behavior. Sequence metadata must remain backward-compatible during staged rollout.
- cost: No per-call API cost. A few KB of RAM for packet metadata/jitter state, within 211,608 B only after measuring current headroom; no hardware cost. SD writes increase only during failed uploads.  ·  latency: Adds at most one packet scheduling interval (target <60 ms); prevents multi-second stalls caused by retransmission/contention.
- security: Sequence IDs and loss telemetry are non-content metadata, but call IDs can correlate sessions; rotate opaque IDs and encrypt SD fallback at rest.
- depends on: Relay duplex QoS and resumable audio-range protocol; Mac bridge support for loss-aware TTS/playout; A validated 24 kHz end-to-end audio acceptance test

### `hardware` — Add a low-power I2C fuel-gauge IC and a small vibration/alert actuator to the production pendant, with the firmware exposing battery percentage, estimated minutes under LTE-M voice load, and a critical-power event to the relay. Keep the existing one-button/LED behavior and reserve I2C for the gauge.
- **owner gets:** The owner can trust the pendant for a full day: it can warn before a live conversation dies and the relay can defer non-urgent audio briefings when remaining runtime is low. Today there is no battery gauge at all.
- effort: Prototype-board revision plus fuel-gauge driver, calibrated load profiles, relay policy, and dashboard/voice wording; validate against real battery chemistry and enclosure thermals.  ·  risk: A poor calibration could report false confidence or the actuator could drain the cell; recover with conservative thresholds, USB calibration, and LED-only fallback if the actuator is absent.
- cost: Roughly $2–6 BOM increase for gauge, passives, and actuator; tens of milliwatts only during brief alerts, negligible idle draw. No API cost.  ·  latency: Local warning is immediate; relay notification waits for LTE-M and is non-critical.
- security: Battery telemetry is low sensitivity. Do not expose device identifiers with it; relay stores only coarse health and last-seen time.
- depends on: Production pendant constraints and battery chemistry; A device-to-relay health telemetry schema; Audio governor power profiles

### `hardware` — Revise the production pendant with a normally-open physical microphone privacy switch that removes microphone power or gates the I2S data line before the nRF9160, plus a dedicated privacy LED driven by hardware state. Add a secure-element-backed key slot so private note files on microSD are encrypted before any reconnect or Mac handoff.
- **owner gets:** The owner gets a privacy boundary they can verify by touch and light, rather than trusting a cloud-controlled software toggle. Sensitive notes remain local until they deliberately release them for transcription or filing.
- effort: Production PCB/enclosure revision, microphone power/I2S gating validation, secure-element driver and key ceremony, encrypted FATFS file format, and Mac import/release UX across dashboard and iOS.  ·  risk: A failed switch or LED could falsely signal privacy; design fail-closed (mute on uncertain state), self-test at boot, and expose a visible fault. Lost keys make notes unrecoverable, so offer an owner-controlled recovery export without weakening the live privacy boundary.
- cost: Approximately $1–4 BOM increase for switch, indicator driver, and secure element, plus minor battery draw for the indicator only. No cloud API cost in private mode.  ·  latency: Mute/unmute is sub-100 ms locally; approved Mac transcription is asynchronous and does not delay ordinary conversation.
- security: Strongly improves confidentiality by preventing raw mic samples from entering the modem path. Requires careful key backup policy, zero plaintext relay logs, and separate release authorization from normal browser sessions.
- depends on: Production pendant constraints and microphone electrical design; Encrypted local-note format and key-management implementation; Mac-local transcription and explicit release-token protocol


## What it asked for

### `s3-yfml` (skill) — link_aware_duplex_audio_governor
- does: Locally schedules microphone and speaker Opus packets by deadline and priority, tracks sequence gaps, reports loss ranges, and chooses bounded downlink shedding or SD failure buffering so owner speech is preserved during LTE-M contention.
- must be on-device because: Only the pendant sees the single modem socket, I2S deadlines, local queue pressure, and the moment a packet would miss playout; a server can react only after loss has already happened. It must also continue safely during a dropped link.
- trigger: Automatically on every active conversation; mode changes from modem send/receive pressure, WebSocket backpressure, I2S queue depth, and reconnect events.
- storage: Volatile ring metadata and jitter state, roughly 8–16 KiB RAM. Failed audio chunks retain only the existing encrypted SD failure-buffer policy, with call/turn IDs and loss manifests; no routine audio storage.
- RAM budget: Target 12 KiB total including packet descriptors and a capped jitter queue. Must be measured against the 211,608 B application RAM and existing ~87% CPU combined encode/decode load; no extra codec or large PCM buffer allowed.

## Its own summary

Discovered a concrete live-call failure: LTE-M duplex contention recently dropped 388 uplink packets (~7.8 seconds) while the owner was speaking, while the nRF9160 already spends about 87% of one core on simultaneous codec work. I recorded this finding, proposed an end-to-end loss-aware conversation capability, proposed and queued a local link-aware duplex audio governor, and proposed a production hardware addition (fuel gauge plus alert actuator) so the pendant can warn before power-related call loss. Still needed: the shared duplex QoS/resumable-audio protocol, Mac/relay loss-repair implementation, congested-LTE acceptance tests, and production pendant/battery constraints. The Mac agent also reports Accessibility and Screen Recording unavailable and the browser extension offline, which blocks reliable full computer-use/browser validation.

**Biggest unknown:** Whether the current nRF9160 firmware has enough measured RAM/CPU headroom for even a 12–16 KiB deadline/jitter governor while 24 kHz decode and 16 kHz encode run together; this needs a real instrumented build and the pending 24 kHz acceptance criteria.

