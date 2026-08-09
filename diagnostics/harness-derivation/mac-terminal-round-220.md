# Harness derivation — mac-terminal — round 220

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **USB serial bench access** — The granted mac_usb_serial_diagnostics schema is still unresolved in the live inventory; no serial/USB capability exists, so it cannot read the physically connected nRF9160 or ESP32 ports. Bench access still requires POST /execute run_shell and the existing capture scripts.
  - evidence: Called mac_usb_serial_diagnostics for all four published device paths with 1s/8192-byte bounded read; resolver returned unresolved, nearest action:get_mac_status.

## Capabilities it proposed

### "Make my pendant audio stay superwideband: keep 24 kHz playback when the relay and bridge can sustain it, but automatically fall back and recover without clicks when decode, LTE, or Bluetooth buffering runs out."
- **useful because:** The owner hears a continuous conversation instead of silent gaps or stale audio, while getting the requested 24 kHz quality whenever the whole path can actually afford it. This is the single most useful missing behavior because it turns the prototype audio path into something wearable rather than a demo.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** Realtime only for the transport controller's low-latency decisions; a cheaper background model analyzes hourly quality summaries and recommends thresholds. No LLM should sit in the 20 ms audio loop.
- **latency:** Controller decision within one audio frame (20–60 ms); quality mode change at a packet boundary, with 100–200 ms crossfade/jitter-buffer concealment. Background summary under 30 seconds after a bench run.
- **cost:** Negligible inference cost in the real-time loop; roughly $0.01–$0.05 per daily diagnostic summary if a model is used. Dominant costs are LTE airtime and engineering time for synchronized counters.
- **security:** Transmit counters and mode transitions, not microphone content, to diagnostics. The relay must authenticate turn IDs and reject stale mode commands. Never let a diagnostic upload include raw audio or shell environment values; require explicit confirmation before exporting logs off the Mac.
- **missing:** A negotiated audio-profile message carrying sample rate, frame duration, bitrate, and reason-coded fallback; Synchronized monotonic counters from pendant encoder/decode timing, relay jitter, and ESP32 FIFO depth/Bluetooth underruns; A relay policy that changes profile only at packet boundaries and emits an auditable mode receipt; An end-to-end bench acceptance command that compares the three counter streams against audible gap and latency thresholds

### "Run a one-minute end-to-end audio qualification and tell me whether my wearable path is ready: pendant capture, relay Opus turn, 24 kHz decode, ESP32 resampling, and Bluetooth playback, with the first failing hop and a saved report."
- **useful because:** Today each component can appear healthy while the complete conversation still has gaps. This gives the owner one answer before wearing it and names the failing hop instead of wasting time guessing between LTE, Opus, I2S, or Bluetooth.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner
- **model tier:** No model in the measurement loop: deterministic signal generation, timestamp/counter collection, and threshold checks. Use a cheap background model only to turn the resulting report into a short spoken explanation when the owner asks.
- **latency:** One-minute test plus at most 15 seconds to drain buffers and write the report; failure localization must be available immediately after each stage's counters arrive.
- **cost:** No inference cost for the test itself; negligible local CPU/disk. If run over LTE, ordinary test audio traffic is the dominant cost, so default to a 10-second low-volume synthetic chirp and require confirmation for the full one-minute cellular run.
- **security:** Use a generated tone or fixed speech fixture, never record the room. Keep raw captures on the Mac and retain only hashes, timestamps, counters, and pass/fail in the relay. Bluetooth device names and network identifiers stay local. The test must not send audio to any third-party analytics service.
- **missing:** A test-mode protocol with a generated sequence number and known 24 kHz fixture that the pendant can inject without opening the microphone; A synchronized per-hop timestamp/counter envelope for capture, relay encode/decode, I2S output, ESP32 FIFO, resampler, and A2DP callback; A Mac runner that starts the existing dual-UART capture, starts a tagged pipeline audio turn, waits for completion, and correlates logs even when the USB serial capability is unavailable; A deterministic report schema with thresholds for packet loss, decode overrun, I2S underrun, FIFO starvation, Bluetooth underrun, and end-to-end latency

### "Move this conversation to my Mac speakers, AirPods, or the pendant without losing the turn: keep listening where I left off, drain the old output safely, and tell me which device is active."
- **useful because:** Today the owner must manually reconnect or restart when they move rooms or remove headphones, risking duplicated or missing speech. A single spoken handoff would make the AI feel present across the wearable, Mac, and bridge rather than trapped in one transport.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension
- **model tier:** Deterministic routing and turn-cursor transfer; realtime model only interprets an ambiguous destination such as 'the headphones'. No background model is needed.
- **latency:** Acknowledge the requested destination within 250 ms, establish the new sink within 2 seconds, and resume at an exact packet cursor with no more than 100 ms overlap or gap.
- **cost:** No per-request model cost for explicit destinations; at most a few cents monthly for ambiguous utterance resolution. Engineering dominates: sink discovery, cursor handoff, and device health tests.
- **security:** Only route to devices already paired or authorized in the owner's Mac session; never expose Bluetooth names or audio to the relay beyond opaque sink IDs. A handoff must invalidate the old sink's stream token so a disconnected speaker cannot resume playback later.
- **missing:** A shared sink registry spanning the pendant, ESP32 bridge, Mac CoreAudio, and browser session, with capabilities, health, and opaque IDs; Relay protocol messages for prepare-sink, commit-sink, and abort-sink carrying turn ID and replay cursor with exactly-once semantics; Mac-side CoreAudio/Bluetooth route inspection and switching, plus ESP32 A2DP pause/drain/resume controls; Pendant-local confirmation state and recovery when the new sink cannot be reached

### "I’m with someone—make the next replies safe to hear aloud and hide private browser and Mac details until I say I’m alone."
- **useful because:** The owner can wear the AI in public or around colleagues without accidentally speaking a secret, calendar detail, or browser title. It turns physical presence into a usable privacy boundary rather than requiring the owner to stop using the system.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Realtime model classifies only the owner's explicit mode command; enforcement is deterministic. Background processing is unnecessary.
- **latency:** Privacy mode must take effect before the next spoken sentence, under 300 ms; restoration must require an explicit command and be announced locally without reading sensitive queued content.
- **cost:** Near-zero inference cost; modest engineering for synchronized mode state and redaction tests. No cloud audio or page content should be added.
- **security:** Default to fail-closed on link loss: the pendant uses a local privacy bit and generic tones, while Mac/browser surfaces suppress titles, notifications, clipboard, and page text. Do not claim redaction if a node has not acknowledged the mode. Secret-bearing queued replies remain encrypted and inaccessible to speech until restoration.
- **missing:** A signed privacy-mode state replicated to pendant, relay, Mac agent, and browser extension with monotonic version and acknowledgement; A deterministic spoken-output sanitizer that rejects secret facts, raw URLs, names, and page titles rather than merely asking a model to summarize them; Browser and Mac hooks to pause page watches, mask snapshots, suppress notifications, and redact active-window metadata; A local pendant command and visible/tonal acknowledgement that does not itself reveal why privacy mode changed


## Changes it proposed to its own stack

### `hardware` — Replace the prototype nRF9160 DK plus ESP32 audio bridge for the product audio path with a low-power cellular SoC/module that has a dedicated audio DSP (or add a tiny fixed-point audio coprocessor) and a native Bluetooth LE Audio endpoint; retain the ESP32 only as a bench adapter. Budget the DSP for 24 kHz Opus decode, echo/noise processing, and packet concealment independently of the Cortex-M33, and provide a hardware FIFO with underrun watermark interrupts. Keep the existing LTE control protocol so the relay and pendant state machine can migrate incrementally.
- **owner gets:** The owner gets 24 kHz speech without the current 87% single-core contention, fewer stalls, no cable-bound bridge in daily wear, and a smaller device with a realistic battery life. It removes the prototype's most likely source of silence rather than tuning around it forever.
- effort: High: select and validate a cellular/audio module, design a power and audio board, port Zephyr or vendor SDK, qualify Bluetooth audio interoperability, and migrate the current 15,625 Hz I2S microphone and 31,250 Hz output wiring. Prototype on an evaluation board first, then a wearable PCB and enclosure.  ·  risk: New silicon and Bluetooth stack can introduce certification, driver, and interoperability failures. Preserve a USB UART debug mode and the current ESP32 bridge as a fallback during bring-up; gate production rollout on the end-to-end qualification report. Avoid claiming the DK's timing or RF performance represents the final device.
- cost: Roughly $25–$80 incremental prototype BOM for a cellular/audio module and power/audio components, plus PCB/tooling/NRE; likely 100–300 mW active audio depending on modem and DSP. This can reduce bridge battery and enclosure cost but increases certification cost.  ·  latency: Potentially lowers decode scheduling jitter by removing contention; native LE Audio can cut bridge buffering by tens of milliseconds. Initial port may add latency until FIFO and codec tuning are measured.
- security: A native radio/audio endpoint increases firmware attack surface and requires signed updates, secure pairing, and modem isolation. Keep raw audio local to the device/relay and expose only counters in diagnostics; do not make the ESP32 debug bridge a production trust anchor.
- depends on: An end-to-end 24 kHz qualification harness and hop counters; A negotiated audio-profile protocol that supports fallback; A product-level power budget and Bluetooth certification target; Hardware selection with published Opus/DSP and LE Audio support

### `firmware` — Add an end-to-end hearing-safety governor: measure output level and cumulative dose at the pendant/bridge boundary, enforce a hard ceiling before samples reach the ESP32/A2DP path, and use a slow ambient-noise estimator to recommend (never abruptly force) a lower volume. Persist dose in a small monotonic record across reboots, expose only dose/ceiling events to the relay, and have the pendant announce a generic warning when the limit is reached.
- **owner gets:** The owner can wear the AI for hours without an unnoticed loudness spike during reconnection, fallback, or Bluetooth volume changes. A transport bug cannot turn a quiet reply into a damaging burst, and the owner gets an honest local warning even when the Mac or relay is offline.
- effort: Medium-high: calibrate I2S/bridge sample amplitude to headphone output, add fixed-point RMS/peak windows and a dose accumulator, enforce limiter attack/release bounds, test reconnect and A2DP volume races, and add a product calibration path.  ·  risk: Without per-headphone calibration, dose is approximate; label it as an estimate and fail to a conservative ceiling. Limiter pumping can degrade speech, so use a short attack and slow release with a hard emergency clamp. Never infer medical risk or replace hearing-protection advice.
- cost: Small firmware RAM/flash and CPU cost; perhaps $1–$4 for calibration/test components in a product revision, with no ongoing API cost. The current ESP32 bridge's 44 kB buffer limit is unaffected because the governor uses small rolling windows.  ·  latency: Under 10 ms for the fixed-point limiter; ambient recommendation changes over seconds, not in the speech path. No added relay latency.
- security: Dose data is health-adjacent and should remain local by default; relay receives only a boolean safety event unless the owner explicitly requests a report. Signed firmware is required so the ceiling cannot be silently removed.
- depends on: A calibrated output-level measurement point in the ESP32 bridge or production audio codec; A shared volume-command protocol that prevents Mac, relay, and A2DP gain races; Product headphone calibration fixtures and a documented conservative maximum; A pendant-local warning state that coexists with existing recording and action-status LED patterns


## What it asked for

_Nothing._
## Its own summary

Produced three non-duplicate recorded proposals: (1) cross-node adaptive 24 kHz audio profile negotiation and recovery, (2) a one-minute deterministic end-to-end audio qualification with hop localization, and (3) a product hardware migration off the 87%-busy nRF9160-plus-ESP32 audio path to DSP/native LE Audio. Live discovery confirms Safari (3 tabs) and the Mac bridge are online. The newly granted USB serial diagnostic schema still does not resolve, so I recorded that bench reads must currently use POST /execute and the existing capture scripts. I also asked relay-realtime for current live audio counters.

**Biggest unknown:** Actual live serial logs and relay/bridge per-hop counters remain unavailable. I still need a real bounded serial-reader capability (or a typed POST /execute bench runner) and the audio-profile/test-mode protocol implemented across pendant, relay, and ESP32 before I can establish whether the 24 kHz path is truly ready.

