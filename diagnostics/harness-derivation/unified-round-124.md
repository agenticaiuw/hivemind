# Harness derivation — unified — round 124

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“During a meeting, listen for decisions and promises, then leave me a private, sourced follow-up queue on my Mac and read me only the urgent items afterward.”"
- **useful because:** The pendant is the only always-present microphone, the Mac can maintain a local transcript and create reminders, the browser can contribute authenticated meeting context, and the relay can coordinate them. This turns passive conversation into actionable follow-through without sending messages automatically.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for transcript segmentation and extraction; realtime only for the spoken urgent alert
- **latency:** Capture locally/over USB with under 2 s segmentation; produce the queue within 2 minutes of meeting end; urgent alert within 5 s of a high-confidence commitment.
- **cost:** Roughly $0.01–$0.08 per meeting hour depending on local versus hosted transcription; storage and Mac CPU dominate, not realtime inference.
- **security:** Meeting audio and transcript are sensitive. Default to Mac-local encrypted storage, upload only short derived snippets when needed, show source timestamps, auto-delete raw audio, and require explicit opt-in per meeting. Never send or accept commitments automatically.
- **missing:** meeting-mode capture trigger and visible recording indicator; local streaming transcription and speaker/decision extraction; encrypted transcript-to-reminder workbench with source timestamps; browser context adapter for the active meeting page

### "“If I start a conversation while the pendant is plugged into my Mac, keep that exact conversation alive when I unplug it and walk away; tell me clearly whether it is using USB, LTE, or waiting to reconnect.”"
- **useful because:** The hardware is physically testable over USB today but LTE is not registered. A real wearable must not reset the conversation at the desk boundary: the Mac should hand off session state and buffered intent to the relay, while the pendant gives an unambiguous local truth signal about its transport.
- **path:** pendant → mac-terminal → mac-planner → relay-realtime → dashboard
- **model tier:** Deterministic protocol/state machine; use the realtime model only for the ongoing voice turn, never for handoff decisions.
- **latency:** USB-to-relay handoff under 1 second; LTE reconnect and session resume under 10 seconds when coverage returns; LED/audio status immediate.
- **cost:** Negligible model cost; small relay D1 session writes and a few kilobytes of bounded local buffering per interrupted turn.
- **security:** Authenticate the serial device and bind the handoff to the same session; never replay buffered microphone audio after a user-visible privacy stop; encrypt any queued audio and expire it quickly.
- **missing:** authenticated framed USB serial protocol shared by nRF9160 and Mac; transport-neutral session token and resume protocol in relay; bounded handoff buffer with duplicate suppression; truthful LED/voice status mapping for USB, LTE, and reconnecting

### "“If the pendant misses part of what I said or the reply breaks up, notice it and ask for only the missing piece—or replay the last sentence—instead of making me start over.”"
- **useful because:** The current LTE-M duplex path has measured multi-second speech loss under contention. A wearable assistant should recover conversationally: the pendant, relay sequence telemetry, and Mac transcript context can identify a gap and repair it with one short spoken prompt.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Deterministic packet-gap and transcript alignment first; realtime model only for a concise repair prompt or semantic reconstruction when confidence is high.
- **latency:** Detect a transport gap within 500 ms; replay or ask within 2 s; never stall an entire turn waiting for perfect reconstruction.
- **cost:** Usually no extra model call for replay; occasional short realtime repair call, under $0.005 per incident, plus bounded ring-buffer storage.
- **security:** Do not infer or fabricate missing private speech. Mark reconstructed text as uncertain, keep raw recovery audio ephemeral, and require the owner to repeat anything that could trigger an external action.
- **missing:** cross-link packet sequence numbers to transcript spans; small encrypted pre-roll/post-roll audio ring on the pendant or Mac; repair policy that distinguishes replayable assistant audio from owner speech; spoken uncertainty marker and dashboard diagnostics

### "“When I say ‘call [person]’, use my phone to place the call and let me conduct it through the pendant; if I say ‘send this as a text’, prepare the exact message and wait for my button press before sending.”"
- **useful because:** The pendant is currently an assistant but not a genuinely hands-free communications device. An iOS companion can resolve contacts and place the call, while the pendant supplies the microphone, playback, and a physical confirmation boundary for messages. The Mac and relay can retain a concise call outcome without needing the owner to reach for a screen.
- **path:** pendant → iOS → relay-realtime → mac-planner → dashboard
- **model tier:** Realtime only for command parsing and live call control; deterministic contact resolution and message confirmation; background model optionally summarizes an opted-in call transcript.
- **latency:** Contact disambiguation and confirmation under 2 seconds; call setup under 5 seconds; audio routing must remain conversational with under 200 ms added latency.
- **cost:** Negligible model cost for calls; iOS telephony and Bluetooth/HFP integration dominate engineering. Optional transcription costs a few cents per hour and must be opt-in.
- **security:** Contact names, phone numbers, and call audio are highly sensitive. Require explicit confirmation for every outbound text and unknown contact, never auto-send from inferred speech, show the resolved contact aloud, and store no call audio by default.
- **missing:** iOS CallKit/telephony companion integration; Bluetooth HFP-capable pendant audio path (current ESP32 A2DP source is output-only); signed command and confirmation protocol across iOS, relay, and pendant; contact disambiguation and spoken pre-send receipt


## Changes it proposed to its own stack

### `firmware` — Replace the current simultaneous full-rate Opus encode/decode loop with an explicit duplex audio governor: timestamped 24 kHz playback frames, 16 kHz uplink frames, bounded jitter buffers, and a congestion policy that temporarily lowers uplink complexity/bitrate or pauses nonurgent playback before dropping microphone packets. Add sequence/clock telemetry across nRF9160, relay, and ESP32, and make the ESP32 resampler report underrun/overrun receipts.
- **owner gets:** Speech should stop cutting out during the moments when the agent talks back. Today the measured LTE-M contention drops about 7.8 seconds of uplink in one call; this makes the pendant feel unreliable exactly when it is most useful.
- effort: High: firmware scheduler and buffers, relay frame policy, ESP32 telemetry, and a USB fault-injection/acceptance harness. Must fit 211,608 B app RAM and the single shared full-duplex I2S peripheral.  ·  risk: A governor that reacts too aggressively could make speech sound slow or mute playback. Ship behind a feature flag, retain the existing codec path as fallback, and expose a diagnostic mode before enabling it by default.
- cost: No per-call API increase; modest RAM for bounded queues (target 20–35 kB total) and negligible ESP32 power increase. Engineering cost is substantial.  ·  latency: Adds roughly 60–120 ms buffering in congested conditions, but reduces multi-second gaps and underruns.
- security: Telemetry contains timing and packet metadata, not audio; ensure logs omit transcript/content and expire with audio diagnostics.
- depends on: 24 kHz audio-path acceptance criteria; audio_link_fault_inject tool; audio_pipeline_validate tool; link_aware_duplex_audio_governor device skill

### `hardware` — Add a low-power haptic actuator and a capacitive wear/contact sensor to the pendant, with firmware-owned patterns for transport truth, urgent alert, confirmation-required, and privacy-stop states. The relay and Mac must be able to send only typed urgency events; firmware must suppress haptics when the pendant is not being worn and keep a local event counter for later reconciliation.
- **owner gets:** The owner can receive a discreet, glance-free signal in a meeting, while walking, or with headphones on, instead of missing important events or having the pendant speak at the wrong moment. Contact sensing also prevents an unattended pendant from announcing private information.
- effort: Medium-high hardware revision plus enclosure, battery, GPIO/ADC firmware, USB/LTE event protocol, and relay urgency classification. Prototype immediately with a small I2C haptic driver board on the currently free I2C bus, then integrate into the wearable revision.  ·  risk: False contact readings could suppress alerts; vibration could be annoying or reveal presence. Provide a physical long-press disable, conservative defaults, test patterns, and audio fallback when contact is unknown.
- cost: Prototype roughly $5–$15 in parts and under 10 mA only while pulsing; production BOM increase roughly $2–$6. No meaningful API cost.  ·  latency: Local haptic response under 100 ms after a signed event arrives; no model latency for the pattern itself.
- security: Contact state and urgency events are sensitive metadata. Do not upload continuous wear history; transmit only the minimum event acknowledgment, and keep privacy-stop behavior local and fail-closed.
- depends on: authenticated framed USB serial protocol; typed relay urgency events; pendant firmware event receipt and reconciliation


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: meeting decision/commitment capture into a sourced private follow-up queue; USB-to-LTE conversation continuity with truthful transport status; and packet-loss-aware conversational repair so the owner need not repeat whole turns. I also proposed the concrete duplex audio governor needed to address the measured ~7.8 seconds of uplink loss during simultaneous speech. What I still need is not another abstract route: the pending 24 kHz acceptance criteria, audio validation/fault-injection tools, and the authenticated framed USB protocol/session-resume implementation. The pendant is USB-attached and testable now, but LTE registration remains absent, so handoff needs a USB-first test harness before field validation.

**Biggest unknown:** Whether the owner accepts local meeting audio capture and how long raw audio/transcripts may be retained; this determines whether the first capability can ship privately on the Mac or needs relay processing.

