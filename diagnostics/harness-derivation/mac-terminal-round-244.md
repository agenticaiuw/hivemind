# Harness derivation — mac-terminal — round 244

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live USB bench reachability** — The granted mac_usb_serial_diagnostics schema still does not resolve against the live inventory; no serial/USB capability is published. The two chips may be physically connected, but this agent cannot read bounded UART frames through a callable diagnostic tool.
  - evidence: functions.mac_usb_serial_diagnostics returned unresolved; nearest action:get_mac_status score 0.226, inventory has no serial/usb/tty/baud capability.

## Capabilities it proposed

### "“Run that long Mac job, give me a spoken progress update every minute, and stop the actual process when I press the pendant button.”"
- **useful because:** Today a job can be marked cancelled while a run_shell child continues for up to its timeout, and the owner has no useful progress channel away from the Mac. This turns the pendant into a real remote control for long-running work: progress is honest, and cancel means the process is actually terminated rather than merely flagged for the next step.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Use a cheap background monitor for process progress and a realtime turn only for the initial request or a terse spoken status; do not invoke the expensive model for every heartbeat.
- **latency:** Dispatch under 2 seconds; progress updates at a configurable 30–120 second cadence; button cancellation should reach the Mac in under 2 seconds and SIGTERM the child, escalating only after a bounded grace period.
- **cost:** Very low model cost: mostly structured process events and templated speech. CPU/network overhead is a lightweight monitor and event stream; the expensive part is the underlying job itself.
- **security:** The Mac agent already has deliberate maximum access. Record the PID/process group, command label, and termination result without recording inherited secrets. Never report stopped until the process group is confirmed gone; distinguish graceful exit, forced kill, and an already-dead process.
- **missing:** Run shell with an abort signal wired to the child process or process group, not only between action steps; A bounded stdout/stderr progress extractor that emits redacted structured events instead of asking a model to parse the whole stream; Relay-to-Mac push for cancel and Mac-to-relay progress events; Pendant mapping for progress speech and a dedicated cancel intent that does not interfere with the recording edge

### "“I plugged the pendant and audio bridge into my Mac. Run a five-minute wearable bench test and tell me whether both chips, the audio clock, and the button-to-playback path are healthy.”"
- **useful because:** The hardware is physically present now but the relay has no LTE registration, so this is the only honest way to validate the complete wearable path today. It gives the owner a single spoken verdict from two UARTs and an audio loopback rather than asking them to interpret raw captures, and it can catch a cable, clock, framing, or starvation fault before an apparent cloud failure is blamed.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** Use a deterministic background diagnostic/parser, not the realtime model; use realtime only to summarize the final pass/fail and the one next action.
- **latency:** Start acknowledgement under 2 seconds; collect for five minutes; publish incremental phase status and a concise final result within 10 seconds of capture completion.
- **cost:** Negligible model cost. Mac CPU/storage and a short USB capture dominate; retain compact counters and failure windows rather than raw audio by default.
- **security:** USB logs can contain identifiers and audio diagnostics can expose speech timing. Keep raw captures local with a retention limit, send only counters/error windows to relay, and require explicit opt-in before uploading waveform data. The test must never open the Mac microphone; it uses the attached UART/I2S path and known test stimuli.
- **missing:** A typed host-side serial diagnostic action (the granted schema still cannot resolve because no serial capability is implemented); A deterministic parser for diagnostics/dual_chip_autocapture.sh and diagnostics/start_dual_capture.sh output, including framing, sequence gaps, clock drift, and reset counts; A safe test stimulus and loopback assertion for nRF9160 -> ESP32 A2DP/playback without recording ambient audio; A final result route that correlates the two ports and exposes a compact receipt to the relay and pendant

### "“Clip the last 30 seconds of what I just said, turn it into a private note on my Mac, and do not send the audio or note to the relay unless I later ask.”"
- **useful because:** The owner can currently speak to the system, but cannot create a deliberate, local-only audio memory from a bounded segment without making it part of the conversational/cloud path. This gives them a reliable private scratchpad for ideas, names, or instructions while preserving an explicit boundary between a local note and an AI conversation.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** Use a deterministic local clip buffer and on-device/Mac transcription where possible; use the realtime model only if the owner explicitly asks for cleanup or summarization later.
- **latency:** Button-to-recording confirmation under 150 ms; save the clip and a provisional transcript within 5 seconds after release; no relay round trip required.
- **cost:** Near-zero API cost for capture and local transcription; Mac CPU/storage and optional later transcription dominate.
- **security:** The clip is sensitive speech. Keep a short rolling buffer in volatile pendant/bridge memory, encrypt the resulting local file, never upload by default, show the note's local-only status on the pendant, and provide explicit deletion of both audio and transcript. Do not activate an open-ended microphone; only retain audio surrounding an explicit button action.
- **missing:** A firmware ring buffer that preserves a bounded pre-trigger audio window without changing the existing active-edge recording semantics; A local Mac action that receives the clip over the bench/bridge path and writes an encrypted note with audio and transcript together; A local transcription route that does not forward data to the relay; A pendant-visible local-only receipt and deletion command


## Changes it proposed to its own stack

### `hardware` — Replace the prototype's single nRF9160 audio workload with a product pendant that keeps the LTE modem but adds a tiny always-on audio companion (or a modem/MCU module with a hardware audio/DSP path). Put Opus encode/decode, resampling, and transport buffering on the companion; expose a bounded shared-memory/ring interface to the application MCU. Keep the current ESP32 bridge as the bench A2DP adapter until the product radio/audio path is validated.
- **owner gets:** The current wearable spends roughly 87% of one Cortex-M33 core on simultaneous Opus encode/decode, so a busy turn is vulnerable to dropouts, delayed button response, and battery drain. The owner gets a pendant that can speak and listen continuously without the voice link starving its controls, and the Mac/relay can remain available for richer tasks instead of compensating for audio glitches.
- effort: High: select a cellular module plus companion codec/DSP, redesign the board and power tree, define a shared-buffer ABI, port the existing fixed-point Opus path, and run months of RF/audio/battery tests. Prototype first by moving only resampling and packet buffering onto the ESP32 over the existing I2S/USB bench link.  ·  risk: Clock drift, DMA/ring overruns, RF coexistence, and a new failure boundary could make audio worse. Recover with a bypass mode that routes the existing nRF9160 path, sequence-numbered buffers, watchdog reset of the companion, and captured dual-chip traces. Do not claim product LTE continuity until RF certification and power tests pass.
- cost: Prototype companion/DSP and board spin roughly $15–40 in parts per unit at low volume plus substantial NRE; likely tens of milliwatts extra while streaming, potentially offset by lower nRF9160 CPU duty cycle.  ·  latency: Should reduce decode/encode scheduling jitter and make 60 ms frames consistently meet deadlines; no intentional conversational latency increase.
- security: The companion sees raw audio and encoded frames, so use authenticated firmware, no persistent plaintext audio, zeroize shared buffers after acknowledgement, and retain the existing relay encryption boundary.
- depends on: A measured dual-chip audio benchmark over the physically connected USB devices; A stable framed shared-memory/serial protocol with sequence and CRC; Power and RF measurements on the actual wearable enclosure rather than the DK

### `firmware` — Add a bounded, encrypted pre-trigger audio clip buffer dedicated to an explicit private-note action: continuously keep only the last 30 seconds in volatile circular storage, freeze it on the separate note-button event, transfer it over the local bridge, and wipe the ring after a verified local write. Keep the conversation microphone path and its active-edge semantics unchanged; this is a separate note event, not a gesture layered onto sw0.
- **owner gets:** The owner could capture an idea they just finished saying without sending it through the cloud conversation. A dropped link or absent relay would not lose the note, and the clip would remain private on the Mac until the owner chooses to share it.
- effort: High firmware and bridge work: reserve RAM or external PSRAM for the rolling PCM/Opus window, add authenticated framing and wipe-on-ack semantics, add a physical note control in the product enclosure, and implement encrypted local-file receipt plus transcription on the Mac.  ·  risk: A pre-trigger buffer can accidentally retain sensitive speech longer than intended, and memory pressure can disturb live Opus. Mitigate with a product-level second button, a hard 30-second volatile limit, encryption, visible local-only state, watchdog-backed transfer, and a compile-time RAM budget test. The current DK should not pretend to support this with a gesture.
- cost: Prototype requires a second button and likely external RAM or a larger product MCU; roughly $1–5 in components at volume, plus engineering and modest streaming power overhead.  ·  latency: No impact on normal conversation if the buffer runs on a companion audio path; freezing and transferring should complete in a few seconds after the explicit event.
- security: Improves privacy by keeping the clip off the relay, but creates a new local sensitive artifact. Encrypt at rest with a Mac-held key, avoid plaintext crash dumps, wipe volatile and temporary buffers after acknowledgement, and make deletion verifiable.
- depends on: A product enclosure with a dedicated note button rather than a gesture on the active recording button; A local-only bridge transfer and encrypted note writer; A bounded audio-memory design validated against the 211,608-byte nRF9160 application RAM limit


## What it asked for

_Nothing._
