# Harness derivation — unified — round 27

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When the connection gets bad or you start talking, don't lose what I'm saying—keep the conversation natural and catch me up if anything was missed.”"
- **useful because:** The current measured path drops about 7.8 seconds of uplink speech during simultaneous downlink, so the pendant can silently miss the owner's most important words. This makes voice interaction unreliable in exactly the conditions where hands-free use matters.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for turn-taking and a short loss-repair prompt; use a cheap background model to summarize/reconcile any recovered or transcribed fragments. The relay performs deterministic packet accounting and does not invoke a model for transport decisions.
- **latency:** Local buffering and governor decisions under 100 ms; normal turn latency unchanged. If a gap is detected, ask one brief spoken clarification within 1 s, while the relay can continue a low-rate transcript repair in the background.
- **cost:** Usually <$0.01 per call beyond existing inference; transport metadata and Opus adaptation dominate. Background repair costs a small additional transcription/model call only when packet loss exceeds a threshold.
- **security:** Audio fragments remain encrypted in transit and should use a bounded, per-call ring buffer with automatic expiry. Never upload buffered speech after the call unless the owner explicitly enables repair; dashboard shows loss events and offers delete. Confirmation is required before replaying or exporting recovered audio.
- **missing:** A pendant firmware link-aware duplex governor with a bounded local pre-roll/ring buffer and explicit packet sequence/ACK metadata; Relay-side loss map, jitter/late-packet handling, and a deterministic downlink/uplink bitrate governor that respects the ~2 kB TLS record limit; 24 kHz end-to-end audio acceptance tests and a real-device packet-loss test harness; A user-visible interruption/recovery state on the pendant LED/audio and dashboard call diagnostics; A policy deciding whether recovered audio may leave the device after disconnect

### "“Save what we were just talking about, along with the page and the exact moment, so I can find it later.”"
- **useful because:** Today a spoken idea, the authenticated page it came from, and the surrounding context are separate and easy to lose. This would let the owner capture a reliable, searchable memory hands-free: the pendant contributes the recent audio, the relay timestamps and transcribes it, the Mac stores a durable note, and the browser contributes the private tab URL/title and a cited snapshot without exposing page contents unnecessarily.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles only the short capture acknowledgement and interruption-safe transcript. A cheaper background model normalizes the transcript, extracts a title/tags, and links it to the cited page and timestamp.
- **latency:** A local acknowledgement in under 300 ms; durable receipt within 5 s. The owner should be able to continue speaking while the background packaging completes.
- **cost:** Typically below $0.01 per capture; transcription and optional summarization dominate. Storage is small text plus metadata, with audio retained only if explicitly requested.
- **security:** Authenticated page content and audio are sensitive. Capture must be explicit (button or phrase), show what sources were included, redact secrets, encrypt the local handoff, and default to transcript plus page citation rather than retaining raw audio or full-page HTML. Require confirmation before sharing the capsule outside the owner's workspace.
- **missing:** A cross-surface capture transaction with one capture ID, timestamp, source manifest, and completion receipt; A pendant-side rolling pre-capture buffer that can be committed only after an explicit owner trigger; Browser extraction of the active authenticated tab's URL/title and a minimal cited snippet with permission boundaries; Mac workspace writer that creates an atomic note and can later resolve the capture ID; A durable search/index projection and dashboard view for capture provenance, retention, and deletion


## Changes it proposed to its own stack

### `hardware` — For the wearable revision, replace the nRF9160-DK-style single-chip audio path with a modem-plus-audio architecture: a modem MCU for LTE-M and a dedicated low-power audio MCU/DSP (or application SoC with hardware I2S/Opus acceleration), a 24 kHz-capable digital microphone, and a full-duplex audio codec/amp. Keep a small local PSRAM/flash ring buffer for 2–5 seconds of encoded uplink. Define 24 kHz capture, 24 kHz Opus, and 24 kHz playback as one negotiated profile, with a 16 kHz fallback.
- **owner gets:** The owner gets intelligible, natural hands-free conversation instead of a prototype that runs out of CPU and drops speech when it is speaking. It also enables local capture continuity during LTE bursts and makes the requested 24 kHz superwideband path physically achievable rather than merely resampling playback.
- effort: High: new schematic/PCB, power and RF coexistence validation, enclosure/acoustic tuning, firmware split, codec integration, and carrier certification. Prototype first with the existing DK plus an external audio MCU/codec to validate the protocol before committing to industrial design.  ·  risk: Added BOM, size, power draw, and firmware complexity; RF/audio interference and clock drift are likely. Recover by retaining the existing nRF9160/16 kHz compatibility mode, feature-gating the new board by negotiated capabilities, and maintaining a wired debug transport. Do not claim 24 kHz quality until loopback, packet-loss, and intelligibility tests pass.
- cost: Rough prototype BOM increase $25–$60 (audio MCU/DSP, codec, mic, memory, board); production increase roughly $8–$20 depending on volume. Audio DSP power may add ~10–40 mW average, while LTE bursts remain dominant.  ·  latency: Dedicated audio processing removes current contention (about 87% of one Cortex-M33 core for simultaneous encode/decode), reducing jitter; buffering adds 20–100 ms depending on the negotiated loss-protection mode.
- security: A local ring buffer creates a new sensitive-data surface: encrypt it with a per-device key, cap retention to the active call, wipe on hangup, and expose a hardware/firmware disable policy. Keep modem credentials isolated from the audio MCU.
- depends on: 24 kHz audio target architecture and product compatibility decision; A loss-aware duplex transport protocol and acceptance-test harness; Measured power budget and RF/audio coexistence validation on the intended enclosure


## What it asked for

### `t6-ggnh` (tool) — audio_link_fault_inject
- why: The live measurements show simultaneous uplink/downlink loss, and the requested 24 kHz path cannot be responsibly shipped without repeatable fault-injection across modem, relay, and codec. Existing discovery exposes no tool that can run this end-to-end test.

```json
{
  "type": "object",
  "properties": {
    "profile": {
      "type": "string",
      "enum": [
        "legacy_16k",
        "swb_24k"
      ]
    },
    "uplink_loss_percent": {
      "type": "number",
      "minimum": 0,
      "maximum": 100
    },
    "downlink_loss_percent": {
      "type": "number",
      "minimum": 0,
      "maximum": 100
    },
    "jitter_ms": {
      "type": "number",
      "minimum": 0
    },
    "duration_s": {
      "type": "integer",
      "minimum": 1,
      "maximum": 300
    },
    "capture_artifacts": {
      "type": "boolean"
    }
  },
  "required": [
    "profile",
    "duration_s"
  ]
}
```

## Its own summary

This round produced two new, owner-facing outcomes. First, I proposed “don’t lose what I’m saying when the link is bad or you speak”: bounded on-device speech buffering, relay packet/loss accounting and adaptive duplex control, explicit recovery prompts, and privacy-preserving repair. Second, I proposed the product hardware change needed for genuine 24 kHz end-to-end audio: separate modem and audio-processing resources, a 24 kHz mic/codec path, and a small encrypted ring buffer, while retaining a 16 kHz fallback. I also queued a precise audio fault-injection tool covering loss, jitter, latency, underruns, CPU, and recovered speech.

**Biggest unknown:** The authoritative 24 kHz product acceptance criteria and audio architecture are still unavailable, as is a real-device end-to-end fault-injection/validation tool. Without those, the system can describe the path but cannot honestly certify that the requested superwideband experience works under LTE contention.

