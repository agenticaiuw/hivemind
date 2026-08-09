# Harness derivation — mac-terminal — round 269

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-connectivity** — Mac bridge and relay are reachable; browser extension is online with one active YouTube tab, but the nRF9160 pendant is reported offline. The granted USB serial diagnostic schema remains unresolved, so attached-chip health cannot be read through a dedicated tool.
  - evidence: GET /ops/status returned relay.reachable=true, relay.macBridgeOnline=true, browser.online=true, and devices discovery reported nrf9160-pendant offline; mac_usb_serial_diagnostics returned unresolved.

## Capabilities it proposed

### "“Test my pendant audio quality now, end to end, and tell me in one sentence whether it is good enough for a call.”"
- **useful because:** The current stack can report that transports are connected without proving intelligibility. A measured test catches the real failure the owner feels: clipped, delayed, or silent speech, especially while the chips are USB-bench-connected and LTE is unavailable.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background for the measurement and report; realtime only to speak the final one-sentence result
- **latency:** 30–60 seconds for a bounded test; spoken verdict under 2 seconds after the final frame
- **cost:** Low: one short background inference plus a few kilobytes of telemetry; the dominant cost is the optional audio-quality model, which can be replaced by deterministic signal metrics
- **security:** The test must use synthetic tones or an owner-approved short phrase, never open the microphone indefinitely. Raw audio should stay on the Mac/bridge and be discarded after metrics; require explicit confirmation before uploading samples to the relay.
- **missing:** A Mac-side implementation of the already-granted bounded USB serial diagnostic schema; the current resolver still cannot call it; A deterministic loopback/test-frame mode in the pendant and ESP32 firmware; A relay endpoint to correlate injected frames, decoded playback timing, packet loss, jitter, and round-trip IDs; A concise quality score based on PLC rate, latency, underruns, and clipping rather than model guesswork

### "“Keep the call as clear as possible, and switch settings automatically if the link or battery gets worse.”"
- **useful because:** The present path is fixed at 16 kbps uplink while the pendant is already near one full core when encoding and decoding. A closed-loop controller could preserve intelligibility under LTE congestion or thermal/battery pressure instead of letting the call become silent or laggy, while explicitly reporting when it has traded quality for continuity.
- **path:** pendant → relay-realtime → mac-bridge → dashboard
- **model tier:** Deterministic controller for the fast loop; background model only summarizes the tradeoff after the call. No expensive realtime inference is needed.
- **latency:** Apply a bounded change within 1–2 seconds after three consecutive bad measurement windows; never renegotiate more often than once per 10 seconds.
- **cost:** Negligible inference cost; telemetry and a few control messages dominate. Optional post-call summary is a small background-model call.
- **security:** Only codec/rate/complexity controls cross the relay; raw audio stays on the existing path. The controller must have hard bounds and an owner-visible history so it cannot silently degrade indefinitely or hide a fallback.
- **missing:** A versioned control message accepted by the nRF9160 and bridge for Opus bitrate, frame duration, complexity, and output mode; Per-window metrics: packet loss, PLC duration, encode/decode budget, underruns, battery and modem state; A relay-side policy that chooses continuity versus fidelity and emits a reason code; A dashboard/pendant summary of the active profile and the last automatic change

### "“That last call dropped out — tell me exactly what failed, when it failed, and whether it was the pendant, relay, Mac, or headphones.”"
- **useful because:** Today the owner can see isolated job and transport states, but cannot get a causal postmortem for a real audio failure. A synchronized incident record would turn an inexplicable silence into an actionable answer and prevent repeated debugging sessions.
- **path:** pendant → relay-realtime → mac-bridge → dashboard
- **model tier:** Deterministic correlation first; a cheap background model turns the resulting timeline into one short spoken explanation. Realtime is unnecessary after the call.
- **latency:** Capture continuously with under 1% bandwidth overhead; produce the postmortem within 10 seconds of the owner's request.
- **cost:** Low: compact event counters and timestamps dominate storage; one short background summarization call per requested incident.
- **security:** Persist counters and state transitions, not raw speech. Retain only a bounded incident window, redact network identifiers, and require explicit owner request before sharing diagnostics with the relay or dashboard.
- **missing:** A shared monotonic/UTC clock correlation scheme across pendant, relay, Mac, and bridge; A ring buffer of audio transport events: frame IDs, acknowledgements, PLC, underrun, reconnect, codec, and output-device changes; A durable incident identifier spanning the relay pipeline and Mac job/receipt records; A causal classifier that distinguishes source capture, radio, relay, host, and headphone failures

### "“Move this conversation from my headphones to the Mac speakers without ending the turn, and move it back when I say so.”"
- **useful because:** The owner currently has separate audio surfaces, but no user-visible, turn-preserving handoff. A failed or inconvenient wearable route should not force them to repeat themselves or lose the assistant's pending reply.
- **path:** pendant → relay-realtime → mac-bridge → macOS audio
- **model tier:** Deterministic routing and buffering; realtime stays responsible only for the live conversation. No background model is needed.
- **latency:** Switch output in under 1 second, preserving at most 250 ms of audio; never duplicate a spoken response.
- **cost:** Negligible model cost. Engineering cost is in synchronized playback cursors, device selection, and a short bounded jitter buffer.
- **security:** Only paired, explicitly selected output devices may receive audio. Announce the destination locally before switching, avoid leaking speech to an unintended nearby speaker, and persist no audio beyond the handoff buffer.
- **missing:** A relay-level session handoff protocol carrying turn ID, playback cursor, and acknowledgement; Mac actions to enumerate/select the active output device and report the actual selected device; Pendant and bridge commands for pause-at-frame and resume-from-frame; A single owner-visible handoff state that refuses to claim success until the destination acknowledges playback


## Changes it proposed to its own stack

### `hardware` — Replace the classic ESP32 HUZZAH32 SBC-only A2DP bridge with a BLE Audio-capable nRF5340 (or equivalent LC3-capable audio SoC) and a clocked 24 kHz output path. Keep the current nRF9160 pendant temporarily as the USB/LTE control endpoint, but make the bridge accept timestamped 24 kHz frames and negotiate LC3 with the headphones instead of forcing 31.25 kHz -> 44.1 kHz SBC resampling.
- **owner gets:** Calls would sound like the intended 24 kHz superwideband path instead of being decoded at 24 kHz and then repeatedly resampled and compressed into a 44.1 kHz SBC link. It removes the current bridge's silence risk and makes the owner's headphones receive a low-latency, intelligible stream.
- effort: High: new bridge board, LC3/BLE Audio firmware, headphone interoperability testing, and a staged compatibility fallback to the existing ESP32. Prototype the framing and clock contract over today's USB-connected bench before spinning hardware.  ·  risk: BLE Audio headphone support varies; pairing or range could regress. Keep the ESP32/SBC path as a fallback and expose the negotiated codec/rate in the audio status beacon. Never silently claim 24 kHz when fallback is active.
- cost: Roughly $20–60 for a development bridge, then perhaps $10–25 in product BOM depending on radio/audio PMIC. Power draw likely increases modestly over a bare ESP32 bridge but removes expensive resampling CPU work.  ·  latency: Potentially 20–60 ms lower one-way latency and substantially less jitter once the native clock path is stable; first prototype may be slower during pairing.
- security: Adds BLE pairing and device identity state. Use bonded, encrypted links and do not expose raw audio over an unauthenticated debug characteristic.
- depends on: Ship and measure the requested 24 kHz pendant/relay path first; Define timestamped frame metadata and codec-negotiation telemetry shared by pendant, relay, and bridge; A deterministic USB bench test using the currently attached chips

### `firmware` — Add a 64-bit capture-clock and monotonically increasing frame sequence to every encoded audio packet, and preserve the last 128 packet headers plus transport state in a compact crash-safe ring. The relay and bridge must echo the sequence in acknowledgements and playback events, without storing the audio payload in the diagnostic ring.
- **owner gets:** When speech becomes silent or delayed, the system could prove whether frames were never captured, lost in transit, decoded late, or played late. The owner would get a real answer instead of a generic 'connection problem,' while keeping raw speech out of persistent diagnostics.
- effort: Medium-high: modify the packet envelope on nRF9160, relay, and ESP32, add wrap-safe sequence handling, and expose a compact diagnostic query. Requires compatibility handling for old firmware and careful RAM accounting against the 211,608-byte application budget.  ·  risk: A larger header could reduce effective audio payload or break old peers; deploy a versioned envelope and negotiate it. Clock drift and reboot must be represented explicitly, never inferred as packet loss. The ring must be bounded and CRC-protected.
- cost: A few bytes per audio frame and roughly 8–16 kB of RAM/flash for the diagnostic ring and parser; no inference cost. Battery impact should be negligible compared with Opus.  ·  latency: No meaningful audio latency change; acknowledgement telemetry may add a small control-path cost only.
- security: The persistent record contains timing and sequence metadata, not speech. Encrypt diagnostic export and expire the ring after a short window.
- depends on: Define the relay/bridge audio envelope version; Expose a read-only diagnostic path usable over today's USB bench connection; Connect the sequence data to the incident postmortem capability


## What it asked for

_Nothing._
