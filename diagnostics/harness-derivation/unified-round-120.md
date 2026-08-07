# Harness derivation — unified — round 120

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make the pendant my computer’s universal voice headset: when it is plugged into my Mac, route my Mac’s call/media audio through the bridge, let me start a relay conversation with the button, and if LTE drops migrate the same conversation to the Mac without losing the turn.”"
- **useful because:** The owner gets one reliable spoken interface instead of a prototype that goes silent when LTE or Bluetooth changes. It is testable now over the two USB serial links and can later become a seamless LTE/USB handoff.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension
- **model tier:** Realtime for the active conversation and handoff; background model only for reconnect diagnostics and post-call summaries.
- **latency:** Button-to-audio under 500 ms locally; migration under 2 s, with at most one spoken sentence replayed.
- **cost:** About $0.01–$0.05 per active voice minute depending on realtime model; USB audio routing and Opus transcoding dominate engineering, not API cost.
- **security:** Audio and browser-call media may cross the relay; default to local USB routing when attached, show a privacy LED, and require confirmation before joining or transmitting into a third-party call.
- **missing:** USB audio-class mode or Mac virtual-audio driver for the ESP32 bridge; conversation migration protocol carrying session id, transcript cursor, and replay window; full-duplex audio acceptance tests across USB and LTE

### "“Switch me between Work, Focus, and Travel modes from the pendant, and make every surface follow: change Mac notification/audio behavior, pause or allow browser watches, and adjust how aggressively the relay interrupts me.”"
- **useful because:** A single button gesture gives the owner a physical, glance-free way to control interruption and privacy. The mode follows the person across the pendant, Mac, browser sessions, and always-on relay instead of living as separate settings.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Cheap deterministic policy for mode changes; realtime only when announcing the new mode or resolving an ambiguous voice request.
- **latency:** LED acknowledgement within 150 ms; Mac and relay policy convergence within 2 s.
- **cost:** Near-zero per switch; occasional background model cost only when converting a natural-language custom mode into policy.
- **security:** Modes can suppress urgent alerts or expose private audio. Keep a local hard override, log each mode transition, and never let a browser watch submit or mutate data because of a mode change.
- **missing:** persistent shared mode state with TTL and precedence rules; pendant gesture firmware and local LED patterns; Mac notification/audio AppleScript adapter and browser-watch pause hooks

### "“When I say ‘save this moment,’ package the last 20 seconds of pendant audio, the live transcript, the active Mac app and Safari tab, and the relevant relay/job identifiers into one private, searchable evidence card—then let me replay or delete it from the pendant.”"
- **useful because:** The owner can preserve a fleeting idea, decision, or failure with its surrounding context instead of reconstructing it later from separate logs. The wearable supplies the moment, the Mac supplies authenticated context, and the relay makes it durable.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only to detect/confirm the command; a cheaper background model creates the title, tags, and concise transcript.
- **latency:** Acknowledge capture under 300 ms; card available within 10 s.
- **cost:** A few cents per saved moment if transcription and summarization run in background; storage and audio retention dominate.
- **security:** This is sensitive ambient audio and potentially logged-in page content. Encrypt end-to-end, use a short default retention, redact secrets, require a deliberate gesture for capture, and provide physical delete confirmation.
- **missing:** on-device rolling 20-second encoded audio buffer; atomic cross-surface capture transaction with transcript cursor and tab provenance; encrypted retention/index and pendant replay/delete protocol

### "“If I trigger an emergency gesture or say my safe word, start a private safety escalation: confirm locally, share my current location and a short live transcript with my chosen contacts, and keep retrying through the relay, Mac, and browser until I cancel or someone acknowledges.”"
- **useful because:** The owner gets a safety net that does not depend on having the Mac in hand or navigating a phone while distressed. The pendant supplies the deliberate trigger and immediate feedback; the always-on relay retries; the Mac/browser can reach authenticated messaging and emergency services.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic local trigger and relay workflow; no expensive model for dispatch. Use a background model only to summarize the captured context for contacts, never to decide whether an emergency occurred.
- **latency:** Local acknowledgement under 200 ms; first contact attempt under 5 s; retry with escalating backoff for 15 minutes.
- **cost:** Usually near-zero model cost; SMS or messaging-provider charges and encrypted short-lived telemetry storage dominate.
- **security:** Location, microphone audio, and contacts are extremely sensitive. Require explicit enrollment, a spoken/local cancel window, signed event logs, encryption, strict retention, allowlisted recipients, and a prominent unmistakable indication before anything leaves the device. Never auto-contact emergency services without the owner's explicit policy and jurisdiction support.
- **missing:** a pendant-local emergency gesture state machine and non-volatile event record; GNSS or a trusted phone location companion plus location freshness/accuracy reporting; relay durable escalation with acknowledgement receipts and deduplication; authenticated, allowlisted outbound messaging connector and a browser fallback


## Changes it proposed to its own stack

### `hardware` — Replace the ESP32 A2DP-only bridge with a dual-role USB-C audio bridge: USB Audio Class 2.0 full-duplex to the Mac, Bluetooth output retained as an optional sink, and a small hardware source/privacy switch. The bridge should expose stable 24 kHz mono endpoints and leave resampling to one documented boundary.
- **owner gets:** The pendant can work as a real headset attached to the Mac today, with predictable audio and no dependence on the fragile SBC 44.1 kHz path. Calls and relay speech can share one wearable endpoint instead of competing for separate devices.
- effort: New ESP32 firmware plus USB descriptors/driver integration; likely a revised ESP32-S3-class board if the current classic ESP32 USB hardware cannot provide native device mode. Add end-to-end loopback and underrun tests.  ·  risk: Current bridge hardware may not support native USB device audio; Bluetooth behavior could regress. Recover by keeping the existing A2DP firmware as a fallback image and switching at boot.
- cost: Roughly $10–$25 prototype board cost, negligible API cost; modest extra power over the current bridge.  ·  latency: Removes one Bluetooth SBC hop when USB-attached, reducing and stabilizing latency by roughly 50–150 ms.
- security: USB audio stays local to the Mac; a physical mute/privacy switch prevents accidental microphone transmission. Firmware updates must be signed.
- depends on: 24 kHz audio target architecture; audio-path acceptance criteria; conversation migration protocol between USB and LTE

### `hardware` — Add a low-power 6-axis IMU and a dedicated capacitive emergency strip to the wearable product, with a hardware debounced trigger path that can wake the nRF9160 and record a signed monotonic event before the application or LTE modem is healthy.
- **owner gets:** They can summon help with one unambiguous tactile action even when speech, the Mac, or the network is unavailable, and accidental pocket presses are less likely than with the prototype's single general-purpose button.
- effort: Product-board redesign, enclosure and wearer testing, local gesture firmware, and a safety review; preserve the current button as the cancel/control input.  ·  risk: False alarms, battery cost, and user anxiety; recover with a short local cancel countdown, escalating LED/audio cues, recipient test mode, and a physical disable switch.
- cost: Approximately $3–$8 added prototype BOM and roughly 1–3 mA active IMU/trigger draw, with deep-sleep current near the existing budget.  ·  latency: Hardware trigger acknowledgement is immediate; network delivery still depends on LTE/Mac/browser fallback.
- security: The trigger must not expose location by default until the cancel window expires; signed local records prevent forged escalation events.
- depends on: emergency escalation workflow; GNSS or trusted phone-location source; durable relay acknowledgement and retry service


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities and one hardware change. The strongest is a universal voice headset with session-preserving USB↔LTE handoff; also recorded physical Work/Focus/Travel modes spanning pendant, relay, Mac, and browser, plus a deliberate “save this moment” evidence card. Proposed replacing the A2DP-only bridge with a USB Audio Class bridge so this is testable on the physically connected hardware now.

**Biggest unknown:** The remaining blocker is not model capability: it is the audio contract between pendant, ESP32, Mac, and relay. I still need the authoritative 24 kHz acceptance criteria/target architecture, a conversation migration protocol with transcript cursor and replay window, and confirmation whether the current ESP32 can support USB device audio or must be replaced with an ESP32-S3-class bridge. For the other capabilities, shared mode state/TTL, pendant gesture firmware, and encrypted rolling-capture storage are still missing.

