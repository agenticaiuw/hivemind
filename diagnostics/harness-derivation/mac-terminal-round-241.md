# Harness derivation — mac-terminal — round 241

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Is my pendant audio path healthy?” — run a 30-second bench self-test that checks the nRF9160 24 kHz decoder, ESP32 resampler/A2DP bridge, Mac Bluetooth output, and relay pipeline, then tell me the failing hop in one sentence and save a diagnostic bundle."
- **useful because:** The owner is actively trying to ship the 24 kHz superwideband path. Today a silent or distorted result requires guessing which of four machines is at fault. A single spoken test gives a pass/fail per hop, latency/jitter, underrun count, and the exact next action, without opening the microphone for a conversation.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → dashboard
- **model tier:** Use deterministic firmware/bridge counters and Mac diagnostics for measurements; use a cheap background model only to summarize the structured report. Reserve realtime for the owner's spoken request and final sentence.
- **latency:** 30 seconds for the bounded test; under 2 seconds to speak the structured result after the last counter arrives.
- **cost:** Near-zero model cost for measurement; roughly $0.01 or less for a short summary if a model is needed. The dominant cost is the 30-second bench run and Bluetooth stabilization, not inference.
- **security:** The bundle may include device identifiers, Bluetooth route names, and timestamps; redact bearer tokens and environment values, retain locally in ~/AI-Pendant-Workspace, and require explicit confirmation before uploading it anywhere. It must never capture microphone content during the test.
- **missing:** A typed bench-test orchestrator that can address both currently attached USB serial devices and parse their bounded health/counter frames (the existing serial grant is a specification, not a callable implementation).; Firmware command/response frames exposing decoder timing, sequence gaps, underruns, and the 24 kHz format; ESP32 frames exposing resampler and A2DP queue health.; A Mac Bluetooth-output diagnostic and a deterministic test-tone path that does not open the microphone.; A relay pipeline correlation ID joining the pendant turn, bridge counters, and Mac job receipt.

### "“Keep me understandable even if the superwideband path degrades.” During a live turn, automatically switch between 24 kHz playback and the proven 16 kHz fallback when the pendant or ESP32 reports deadline misses, then restore 24 kHz only after a clean stability window; tell me only if the fallback persists."
- **useful because:** A wearable conversation should fail soft, not become clipped silence because one expensive Opus decode misses its 60 ms deadline. The nRF9160 is already near one-core saturation with encode and decode together, while the ESP32 has a fragile Bluetooth buffer. Coordinated adaptation preserves intelligibility and battery instead of forcing the owner to reboot hardware.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** No model for the control loop: firmware counters and relay policy decide the codec/rate. Realtime speaks one brief notification only when degraded mode lasts beyond the grace interval.
- **latency:** Decision within one frame (60 ms) after a missed deadline or queue starvation; restoration after 3–5 seconds of clean counters; no extra conversational turn latency.
- **cost:** No incremental inference cost. Small relay CPU/bandwidth overhead for dual-format capability negotiation; 16 kHz fallback reduces bandwidth when active.
- **security:** Only transport metrics and codec mode cross the relay; never upload audio for diagnosis. Persist the last mode and reason locally so an offline pendant does not claim that 24 kHz was restored. Require no user confirmation because it is reversible audio continuity, not an external side effect.
- **missing:** A negotiated codec/rate capability and mode-switch message that is safe at a turn boundary and carries a monotonic sequence.; Relay support for parallel 24 kHz/16 kHz Opus transcode with seamless packet boundaries and a mode acknowledgment.; ESP32 bridge runtime switching that preserves its fixed 44.1 kHz A2DP output while changing only upstream decode/resample workload.; A shared hysteresis policy and dashboard visualization of mode transitions, underruns, and recovery.

### "“I’m driving” (or a short press on the pendant’s dedicated marker button) should put the whole hive into a privacy-and-distraction safe mode: the pendant gives only terse alerts, the relay stops reading sensitive content aloud, the Mac pauses browser/computer actions and queues non-urgent work, and saying “resume” restores the exact pending queue with no duplicate execution."
- **useful because:** The owner can make the entire system safe in one human moment instead of separately silencing the Mac, stopping browser automation, and hoping a queued voice reply does not disclose mail or passwords. It is useful in a car, meeting, or around other people, and it coordinates nodes that cannot enforce this policy alone.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic mode transitions, queue pausing, and redaction policy; realtime model only interprets the short spoken command and gives a one-sentence confirmation. No background model is needed.
- **latency:** Pendant-local indication immediately; relay and Mac/browser pause within 1 second when connected. Resume should acknowledge in under 2 seconds and replay only explicitly queued work.
- **cost:** Negligible inference cost; one short realtime turn per transition. Main engineering cost is propagating a signed mode state and testing pause/resume behavior.
- **security:** Safe mode must fail closed on stale links: if the relay cannot confirm the Mac/browser state, the pendant must say “paused locally; host unconfirmed,” never claim global privacy. Mode changes need monotonic sequence numbers, expiry/heartbeat, and durable pending-job IDs so resume cannot duplicate side effects. Sensitive content must be suppressed from LED/audio caches and dashboard notifications.
- **missing:** A hive-wide signed mode/lease propagated over relay, USB/LTE, Mac agent, and browser extension.; A pause contract for in-flight Mac and browser jobs that distinguishes safely resumable steps from steps that must be abandoned or reconciled.; A pendant-local durable safe-mode bit and resume cursor using the existing store, plus a distinct offline indication.; A policy layer that redacts spoken/dashboard output while safe mode is active and an audit record proving which nodes acknowledged it. 


## Changes it proposed to its own stack

### `hardware` — For the wearable revision, retain the nRF9160 solely for LTE-M/control and add a small audio companion (nRF5340-class Cortex-M33 audio MCU, or a dedicated fixed-point Opus/DSP coprocessor) connected over a framed high-speed SPI link with DMA and clocked audio FIFO. Move 24 kHz Opus encode/decode, resampling, and jitter buffering off the 64 MHz nRF9160; leave the existing single-button/LED and modem path unchanged. Include a hardware mute and FIFO watermark interrupt so the control MCU can truthfully detect a stalled audio companion.
- **owner gets:** The owner gets a wearable that can sustain superwideband speech instead of a prototype that spends roughly 87% of one core when encode and decode overlap and occasionally turns a missed 60 ms deadline into silence. It also leaves CPU headroom for LTE recovery, encryption, and offline storage, making the high-quality path reliable rather than a lab mode.
- effort: High: new board and power design, SPI framing/bootloader protocol, codec port, RF/audio coexistence validation, and enclosure/antenna redesign. Prototype first as a small companion board on the existing DK headers, then integrate.  ·  risk: A second MCU adds firmware-update and crash-recovery surfaces, SPI framing bugs, clock drift, and RF/power noise. Keep a 16 kHz nRF9160-only fallback, watchdog the companion, and make every packet carry sequence/format/CRC so a failed companion degrades to intelligible audio rather than replaying stale frames.
- cost: Roughly $8–$20 incremental prototype BOM (MCU, regulator, level shifting, PCB area), perhaps $1–$3 in volume depending on codec and integration. Expect tens of mW active audio power; measure against the current modem/audio budget before committing.  ·  latency: Can reduce codec scheduling pressure and jitter; SPI adds under 1 ms with DMA if the FIFO is sized correctly. End-to-end latency should improve, not worsen, if the companion owns the 60 ms jitter buffer.
- security: The companion must authenticate firmware and accept audio only over the authenticated MCU link; never put LTE credentials or bearer tokens on it. Secure boot/update and a fail-closed hardware mute are required.
- depends on: Freeze and measure the current 24 kHz frame deadlines and underrun causes on both chips.; Define the adaptive 24/16 kHz transport and sequence/ack protocol before pinning the SPI ABI.; Bench-test a companion against the existing ESP32 bridge and Bluetooth headphones.; Choose the product MCU/codec only after power, RF coexistence, and enclosure measurements; the current DK is explicitly provisional.


## What it asked for

_Nothing._
## Its own summary

Produced three non-duplicate next steps: (1) a bounded, microphone-free end-to-end 24 kHz bench self-test spanning pendant, ESP32 bridge, Mac Bluetooth, and relay; (2) live adaptive 24 kHz→16 kHz fallback with hysteresis so conversations fail soft; and (3) a product hardware revision adding an audio companion MCU so the nRF9160 is not pushed to ~87% combined codec load. The shell-receipt observability proposal collided with an existing backlog item, so I did not restate it. What remains needed is implementation—not another wrapper: a callable bounded USB bench orchestrator/parser, firmware and bridge health counters, codec negotiation/mode acknowledgements, and measured evidence that the current prototype misses deadlines before selecting companion hardware.

**Biggest unknown:** We still do not have live, callable serial inspection or a real bench-health runner. The chips are physically attached, but the system cannot yet prove whether current 24 kHz failures originate in nRF9160 codec timing, USB framing, ESP32 resampling/A2DP buffering, or Mac Bluetooth output.

