# Harness derivation — faculty-judgement — round 122

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Give me my briefing on the pendant, and keep it understandable and resumable even if the pendant is low on battery, the connection drops, or I get interrupted."
- **useful because:** A spoken brief should survive the conditions of real life rather than silently fail. The pendant can detect local battery/audio health, the relay can choose a frame/codec profile and retain a short encrypted queue, and the Mac/browser can supply cited text and regenerate only the missing segment. A button press resumes at the last acknowledged item instead of replaying everything.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use a cheap background model for summarization and segmentation; use realtime only for the owner's interruption/resume conversation. Codec negotiation, acknowledgements, retries, and resume offsets are deterministic.
- **latency:** Start playback within 2 seconds when a prepared brief exists; resume within 500 ms after a button press. Reconnect recovery may take up to 10 seconds and should be announced honestly.
- **cost:** Usually <$0.01 per prepared brief beyond existing TTS/transcoding; retry cost is dominated by regenerated audio only for lost segments. Device telemetry and acknowledgements are negligible.
- **security:** Brief text/audio can contain private mail, calendar, and authenticated-page data. Encrypt queued segments, keep only a short TTL, bind resume tokens to the owner's device/session, and require confirmation before any browser or mail mutation. Do not upload raw microphone audio beyond the existing voice interaction.
- **missing:** End-to-end 24 kHz capability negotiation and a verified loopback test (current pendant capture is 15,625 Hz while decode is 24 kHz).; Durable per-item audio segment queue with delivery acknowledgements, bookmark/resume offsets, and idempotent replay protection.; A local battery/thermal/link-health event from the pendant and a relay policy that selects a lower-cost fallback without pretending quality is unchanged.; A Mac/browser text fallback that can regenerate one cited item when an audio segment is unavailable.

### "Keep me aware of genuinely urgent changes without making me pull out my phone or broadcasting private information in public; use a private signal now and explain it later."
- **useful because:** Today the system can speak, queue jobs, and inspect surfaces, but it cannot reliably arbitrate urgency across calendar/mail/browser/Mac signals and deliver a discreet, offline-tolerant signal on the wearable. This would let the owner stay reachable during a commute, meeting, or hands-busy moment without turning every notification into an interruption.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → unified
- **model tier:** Use deterministic rules and a cheap background model to classify urgency and deduplicate events; reserve realtime for the owner's follow-up question. Never spend the expensive conversational tier merely to decide that an unchanged notification is nonurgent.
- **latency:** Urgent events should reach the relay within 5 seconds and the pendant within 2 seconds of connectivity. If disconnected, latch the signal locally and deliver the explanation when the link returns; nonurgent items can wait for the next briefing.
- **cost:** Usually <$0.005 per event batch; the dominant cost is occasional model classification of ambiguous messages. Haptic delivery and event metadata are negligible.
- **security:** Urgency classification must minimize content exposure: prefer sender, deadline, and user-defined domains before message bodies. Keep private signals content-free, encrypt event metadata, expire raw excerpts, and require confirmation for any resulting external action. The owner must be able to define people, topics, and quiet hours, with an unmistakable physical all-clear/stop control.
- **missing:** A pendant actuator and firmware protocol for at least three private urgency patterns plus a local latch that survives a dropped link and reboot.; A shared event-ingestion and deduplication stream from Mac notifications, Calendar, Mail, and authenticated browser watches, with source, deadline, confidence, and expiry.; A policy engine that combines urgency, quiet hours, current activity, and repetition history without silently escalating low-confidence events.; A delivery receipt and later explanation view that proves why the signal fired, what evidence supported it, and whether it was acknowledged.


## Changes it proposed to its own stack

### `firmware` — Replace the prototype's implicit audio assumptions with an explicit negotiated profile and loopback contract: pendant advertises capture/playback rates, frame duration, Opus mode, battery/thermal headroom, and firmware version; relay selects a profile, stamps every segment with profile+sequence+CRC, and runs a nightly fixture test that compares a 24 kHz source through uplink/transcode/decode/I2S output. Fail closed to a clearly labeled narrowband profile when the 15,625 Hz microphone path cannot satisfy superwideband, rather than upsampling and calling it 24 kHz.
- **owner gets:** The owner gets audio that is genuinely 24 kHz when promised, and an honest fallback when this development kit cannot provide it. Regressions become visible before they turn into a day of muffled or missing pendant speech.
- effort: Medium-high: firmware capability packet and sequence metadata, relay negotiation/transcode changes, deterministic test fixture, and one hardware measurement pass. Product hardware may need a microphone/clock path capable of 24 kHz capture; software alone cannot recover information absent from 15,625 Hz capture.  ·  risk: A negotiation bug could strand older firmware or cause silence. Keep a backward-compatible profile, require an explicit ACK before switching, and retain a server-side narrowband fallback. Test with packet loss and reconnects.
- cost: No meaningful per-request model cost; modest relay CPU/storage for loopback tests. Hardware prototype cost roughly $10–$30 for a suitable codec/mic/clock change, with power impact to be measured; current Opus encode+decode already consumes about 87% of one core when simultaneous.  ·  latency: Capability exchange adds <100 ms. 24 kHz encode/decode remains bounded by existing 60 ms framing; fixture tests run off-path.
- security: Telemetry contains device/firmware/profile and sequence metadata, not message content. Encrypt any diagnostic audio fixtures and expire them quickly; never retain owner speech for QA by default.
- depends on: A durable audio delivery acknowledgement/bookmark layer; An end-to-end audio acceptance test and the owner's decision on whether this development kit may be called superwideband; Physical microphone/clock redesign if true 24 kHz capture is required

### `interaction` — Add a spoken quality/provenance preamble only when needed: the relay tells the pendant whether this item is verified 24 kHz, resampled playback, or narrowband fallback, and attaches a one-tap 'repeat / resume / read text on Mac' control. Store the claim with the briefing item so later retries cannot silently change the promised quality.
- **owner gets:** The owner can trust what they hear and recover quickly when a weak link affects playback; they no longer have to guess whether silence, distortion, or a shortened brief means the system failed.
- effort: Small-medium: profile metadata in briefing/audio events, a concise pendant prompt, and Mac text fallback routing. No new model behavior is required.  ·  risk: Too many notices would annoy the owner. Speak only on a profile change, failed delivery, or explicit request; keep the default to one short sentence.
- cost: Negligible API cost and tiny metadata storage; one extra short TTS utterance only on exceptions.  ·  latency: No impact on normal playback; exception notice adds under 1 second.
- security: Quality metadata is non-sensitive. Text fallback must retain the existing authenticated-session and TTL protections for private briefings.
- depends on: Negotiated audio profile metadata; Per-item delivery acknowledgement and resume offset; Existing /briefing/latest and /pipeline/audio wiring

### `hardware` — Add a low-power haptic actuator with a dedicated interrupt-capable driver and a small nonvolatile attention latch (plus a physical acknowledge/stop input) to the wearable. Define three patterns—urgent, time-sensitive, and informational—whose waveform carries no message content; the relay sends only a signed event class and expiry, while the pendant can signal urgent events during a link outage and report acknowledgement after reconnect.
- **owner gets:** The owner can receive a private, glance-free warning in public or while hands are occupied, without a speaker announcing sensitive content and without losing an important event just because Wi-Fi or the Mac went to sleep.
- effort: Hardware revision plus firmware driver, battery characterization, enclosure/acoustic isolation tests, relay event signing, and a small user calibration flow. This deliberately adds a capability rather than pretending the current single-LED/button prototype can provide reliable private urgency levels.  ·  risk: False alarms could erode trust; missed alarms could be serious. Start with advisory notifications, require explicit owner-selected sources, expose a physical universal stop, expire stale latches, and log every trigger/acknowledgement for review. Haptic vibration can affect battery life and comfort.
- cost: Rough prototype addition: approximately $2–$8 for actuator, driver, and passives, plus PCB/enclosure changes; brief pulses likely add tens of milliwatts while active, with negligible average draw at low event rates. No model cost for delivery.  ·  latency: Local haptic onset can be under 100 ms after a signed event arrives; event arbitration and Mac/browser ingestion remain network-bound.
- security: The pendant receives only an authenticated class, expiry, and event identifier—not message text. Protect the latch against spoofing and ensure a stolen pendant cannot reveal private content through pattern semantics beyond the owner-configured vocabulary.
- depends on: A cross-surface urgency/deduplication policy and event stream; Owner-configured quiet hours, source allowlist, and confidence threshold; Delivery receipt and explanation records for every haptic event


## What it asked for

_Nothing._
## Its own summary

Round 122 discovery confirms the owner’s priority is still the 24 kHz audio path. The live hardware truth is a 15,625 Hz I2S microphone, 16 kHz/16 kbps Opus uplink, 24 kHz decode resampled to a 31,250 Hz wire clock, with encode+decode using about 87% of one core. I proposed a negotiated, measured audio contract with honest fallback, resumable briefing delivery, and quality/provenance notices. Safari and the Mac bridge are currently online; no new orchestrator grants are visible this round.

**Biggest unknown:** Whether the owner wants to redesign the prototype microphone/clock path so “24 kHz” means true 24 kHz capture, or accepts verified 24 kHz playback from a narrowband source. I still need the audio acceptance criteria and a physical hardware measurement/decision; software cannot restore information the 15,625 Hz microphone never captured. Accessibility/Screen Recording remain owner-side blockers for GUI automation, but AppleScript, shell, and browser read paths remain the honest fallback.

