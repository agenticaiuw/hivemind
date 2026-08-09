# Harness derivation — mac-terminal — round 153

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make my voice audio HD for this call.” Then keep the 24 kHz wideband path end to end and tell me if any link falls back."
- **useful because:** The owner explicitly wants 24 kHz superwideband, but today the pendant uplink is 16 kHz/16 kbps while only downlink decode is 24 kHz. This would make spoken replies materially clearer and expose silent quality regressions instead of pretending the path is HD.
- **path:** pendant → relay-realtime → mac-planner → new-surface
- **model tier:** Realtime only for the short mode negotiation and link-quality sentence; fixed firmware/relay DSP for all audio frames.
- **latency:** No more than 100 ms added to a turn; mode switch acknowledged in under 1 second.
- **cost:** Negligible incremental API cost; bandwidth and CPU dominate. Firmware work is the cost: 24 kHz Opus encode on the nRF9160 competes with its measured decode/encode load, and relay transcoding must be removed or made conditional.
- **security:** Audio remains in the existing authenticated transport. The mode announcement must be truthful and must never claim HD unless both encoder and bridge acknowledge it.
- **missing:** 24 kHz/24–32 kbps uplink Opus profile and negotiation message; nRF9160 CPU/memory benchmark for simultaneous 24 kHz encode and decode; relay capability to pass native wideband without downsampling; ESP32 bridge buffering/profile that preserves wideband into its fixed 44.1 kHz SBC source

### "“What exactly failed on the Mac?” after a command or browser action, and give me one short spoken diagnosis with a retry option."
- **useful because:** Today a failed shell result loses exit code, PID, environment provenance, and often the real stderr; the pendant can only report a generic failure. A compact forensic receipt would turn an opaque failure into an actionable answer while the evidence is still fresh.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Background/cheap model summarizes structured receipts; realtime is used only when the owner asks aloud.
- **latency:** Receipt must be persisted synchronously with the action; diagnosis under 3 seconds for retained output.
- **cost:** Low API cost because the summarizer receives capped structured fields, not the whole job log. Disk cost is a bounded per-job forensic record and ring retention.
- **security:** Never persist inherited secrets: record env key names plus hashes, not values. Redact tokens from stderr/stdout, and expose raw evidence only on the Mac. Retry must carry the original job/action id and be explicitly marked as a new attempt.
- **missing:** execFile/argv-aware shell execution or at least capture of parsed argv; exit code, signal, PID, start/finish/duration and effective cwd in the durable receipt; bounded stdout/stderr chunks with redaction and a GET /jobs/:id/evidence route; retry attempt linkage and a pendant-readable failure receipt

### "“Run this when my Mac is idle and on power, then tell me what it found.”"
- **useful because:** Long research, builds, and cleanup tasks should not steal CPU or battery during a call. The wearable can state the intent now, the relay can hold it while the Mac is unsuitable, and the Mac can start only when concrete conditions are true, then return a concise result and receipt.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Cheap background model evaluates the user's condition sentence and summarizes completion; realtime only confirms acceptance or an exception.
- **latency:** Immediate acknowledgement under 1 second; condition polling is event-driven where possible, otherwise 30–60 seconds. Completion report within 5 seconds of job finish.
- **cost:** Very low API cost: one planning call plus one completion summary. Mac polling is local; relay storage is a small durable job and condition record.
- **security:** Persist the command, conditions, and expiry encrypted/with redacted sensitive parameters. Never run after expiry or after the requested network/power condition changes meaningfully. Browser steps retain their existing authenticated-tab boundary; destructive actions still follow owner policy.
- **missing:** A durable conditional-job state machine with expiry, wake conditions (AC/battery, idle, network, active call), and exactly-once dispatch; Mac event/diagnostic feed for power, idle, network, and foreground audio state; Relay-to-pendant queued/deferred/completed event mapping with the existing truthful beacon; A result digest that links the final receipt to the original spoken request

### "“Put this one-time code into the login page, but never repeat or save it.”"
- **useful because:** The owner can wear the pendant while authenticated browser sessions remain on the Mac, but today there is no private, ephemeral path from spoken input to a specific browser field. This would let them complete MFA and short-lived codes without sending the secret through model context, shell history, browser logs, or notes.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime handles only intent and field targeting; a device-local protected buffer and the extension perform the opaque secret handoff without an LLM ever receiving the value.
- **latency:** Target under 2 seconds from button-confirmed capture to field insertion; discard the value immediately after successful insertion or a 30-second timeout.
- **cost:** Negligible per-use API cost if the relay forwards an encrypted opaque blob. Engineering cost is substantial: secure capture, authenticated tab/field binding, and failure-proof zeroization.
- **security:** This is intentionally a high-risk capability: require a physical button confirmation and visible field/origin binding, reject password/payment fields unless explicitly named, prevent clipboard use and shell exposure, encrypt end to end with a per-request key, and make replay impossible. If target verification fails, discard rather than guess.
- **missing:** A pendant-local ephemeral secret-capture mode that never enters transcription or model context; Per-request key agreement between pendant, relay, Mac agent, and Safari extension; An extension API that identifies and fills exactly one eligible field while proving origin/tab freshness; Auditable success/failure metadata that excludes the secret and automatic zeroization on every hop

### "“Privacy stop.” Then immediately mute the pendant, stop sending audio, pause agent work, and lock down my active browser session until I resume it."
- **useful because:** A wearable is always near the owner, so it needs a physical escape hatch when a private conversation starts or the device is misplaced. Today cancellation is cooperative and audio/link state can lag; there is no single owner-visible action that cuts capture and tells every other surface to stop exposing context.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Firmware performs the immediate local mute and radio/audio cutoff; relay and Mac use a signed high-priority event, with no model call on the critical path. A cheap background model may summarize what was paused afterward.
- **latency:** Local microphone cutoff under 20 ms; relay fan-out under 500 ms; browser/session quarantine under 2 seconds. Resume requires an explicit physical action and fresh link acknowledgement.
- **cost:** Near-zero per invocation. Main cost is a priority control channel, durable paused-state record, and extension/Mac listeners.
- **security:** The event must be authenticated, monotonic, and non-spoofable; it must fail closed locally even when offline. Do not claim remote pause until each surface acknowledges it. Preserve only job IDs and timestamps, never buffered audio or page content.
- **missing:** Firmware-local privacy-stop interrupt that mutes capture and invalidates the current audio turn offline; Relay priority event fan-out and acknowledgements across Mac and browser; Mac executor hook that terminates or pauses active computer-use/browser jobs rather than waiting between steps; Safari extension quarantine mode that prevents new reads/actions and visibly reports its state


## Changes it proposed to its own stack

### `hardware` — For the wearable product, replace the prototype nRF9160 audio workload split with a modem-capable application SoC that has a second DSP/core (or add a dedicated low-power audio codec/DSP): native 24 kHz Opus uplink, simultaneous decode, framing, and LTE-M must run without the current ~87% single-core load. Replace the ESP32 A2DP bridge with a standard Bluetooth Classic/LE Audio solution that accepts negotiated wideband rather than forcing SBC 44.1 kHz resampling.
- **owner gets:** The owner gets genuinely clear two-way speech instead of a 16 kHz uplink marketed alongside a 24 kHz downlink, fewer dropouts under simultaneous talk/listen, and no audible quality cliff caused by the prototype bridge.
- effort: High: hardware selection and RF/audio board spin, codec/driver work, relay negotiation, and acoustic validation. Prototype the protocol on today's USB-connected boards before committing to a PCB.  ·  risk: A new radio/audio design can introduce certification, battery, RF coexistence, and codec interoperability failures. Recover by retaining the current 16 kHz profile as a negotiated fallback and running side-by-side USB tests before LTE validation.
- cost: Prototype firmware work is low API cost; production BOM likely +$8–25 for a better SoC/audio path and Bluetooth solution, with modest additional power but lower CPU inefficiency.  ·  latency: Potentially reduces encode/resample delay; negotiation adds under 1 second only when changing modes.
- security: No new user data class; audio still traverses the authenticated relay. Firmware signing and secure boot requirements increase with a new board.
- depends on: 24 kHz Opus profile negotiation; relay native-wideband pass-through; bridge capability inventory and benchmark; audio-link truth beacon

### `hardware` — Add a low-power LRA haptic actuator and dedicated driver to the wearable product, with a hardware-timed alert path independent of the audio stream. Reserve three tactile patterns: inbound answer ready, remote action completed, and transport/error/stale. Keep the existing single LED as the visual fallback and do not overload the recording button with gesture recognition.
- **owner gets:** They can know an answer or action result arrived while walking, in a noisy room, or with headphones disconnected, without looking at the pendant or waiting for a misleading sound. This makes the device dependable as an everyday wearable rather than a USB accessory.
- effort: Medium hardware spin plus firmware power/driver work, enclosure and acoustic testing, and relay event-to-pattern mapping. Validate on the current Mac-attached prototype with an external actuator before the PCB revision.  ·  risk: Extra vibration can be annoying, drain battery, or couple into the microphone. Use short bounded pulses, a quiet-hours setting, mechanical isolation, and a firmware kill switch; if the driver fails, preserve LED/audio behavior.
- cost: Approximately $0.50–$2 BOM increase plus driver/PCB area; roughly 5–20 mA only during brief pulses and near-zero idle draw.  ·  latency: Under 50 ms from a confirmed relay event to tactile output; no audio-path latency.
- security: No new data leaves the device. Patterns must be emitted only for authenticated, sequence-checked events so a stale completion cannot trigger a false tactile signal.
- depends on: truthful_action_status_beacon sequence/age invariant; relay event delivery with completion and stale states; product enclosure and battery budget


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities and one hardware proposal: truthful negotiated 24 kHz two-way audio; forensic Mac/browser failure diagnosis with retry linkage; and conditional execution (“run when idle/on power”) with wearable status. I also proposed the product hardware path needed to make 24 kHz real rather than a downlink-only prototype. The live Mac diagnostic grant remains ambiguous between get_mac_status and /health, so it did not execute; I have not opened a microphone.

**Biggest unknown:** Whether the relay already has any native-wideband uplink path or unconditionally downsamples to the current 16 kHz/16 kbps profile. I asked relay-realtime to verify. The other major missing facts are the bridge’s actual current negotiated codec behavior and a measured nRF9160 24 kHz encode+decode CPU/RAM benchmark.

