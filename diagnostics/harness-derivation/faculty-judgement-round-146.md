# Harness derivation — faculty-judgement — round 146

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I leave my Mac, hand me a tiny spoken 'pick-up packet' on the pendant, and when I return let me say 'resume' to restore exactly what I was doing."
- **useful because:** The owner loses threads at transitions. A departure packet turns the current browser tabs, unsent drafts, calendar context, and active job into a durable, private handoff; return can resume without reconstructing the task.
- **path:** mac-planner → browser-extension → relay-realtime → relay-realtime → unified
- **model tier:** background for packet compilation; realtime only for the owner's resume exchange
- **latency:** Capture within 5 seconds of Mac sleep/USB detach; spoken packet starts within 2 seconds after the pendant reconnects; resume actions require explicit confirmation.
- **cost:** ~$0.01–$0.04 per departure packet, dominated by summarization; event detection and storage negligible.
- **security:** Packet may contain private tab titles, drafts, or messages. Keep raw content on Mac, send only an encrypted summary to relay, expire after 24 hours, and never resume irreversible actions without confirmation.
- **missing:** Mac sleep/USB-presence event forwarded to relay; pendant reconnect/offline packet playback and an explicit Resume button gesture; typed handoff schema with tab/job/session provenance and expiry; safe resume planner that revalidates stale pages before acting

### "If someone is nearby or I am in a meeting, answer privately and briefly; if I am alone, you can speak normally. Never read sensitive content aloud in public."
- **useful because:** A wearable assistant that speaks without knowing its audience can leak mail, codes, and health details. This makes everyday use safe instead of forcing the owner to micromanage a privacy setting.
- **path:** relay-realtime → faculty-perception → mac-planner → browser-extension → unified
- **model tier:** small background classifier for acoustic/calendar presence; realtime model only for the requested answer
- **latency:** Privacy state updates within 1 second of a meeting/nearby-voice signal; no more than 300 ms added to normal replies.
- **cost:** <$0.005 per state update; local audio feature extraction dominates, with no raw audio upload.
- **security:** Process microphone features locally and discard recordings. Treat uncertainty as sensitive: use haptic/text-only fallback. Calendar titles and browser sensitivity labels stay on-device; require an explicit owner override to speak a secret.
- **missing:** Local bystander/meeting detector on the ESP32 or Mac using features rather than raw audio; A sensitivity classifier for response content and browser fields; Pendant haptic/text-only delivery and a persistent physical override; Privacy-state events shared across relay, Mac, and browser

### "When my calendar, email, and browser commitments conflict, tell me the smallest decision I need to make and prepare the messages or reschedules for each option—without sending anything."
- **useful because:** The owner currently discovers conflicts one app at a time and must remember everyone affected. A single spoken decision packet exposes the tradeoff, preserves relationships, and turns one choice into prepared reversible actions.
- **path:** mac-planner → browser-extension → relay-realtime → faculty-judgement → faculty-action
- **model tier:** background model continuously clusters commitments and computes conflicts; realtime only explains the one decision the owner asks about
- **latency:** Detect within 10 minutes of a changed event/message; a spoken decision packet under 20 seconds; drafts ready within 1 minute.
- **cost:** ~$0.03–$0.12 per conflict, mostly background extraction and drafting; idle monitoring should be event-driven, not polling.
- **security:** Commitments can expose work and personal relationships. Keep source bodies on-device, send minimized entities to relay, cite every proposed change, and require confirmation before any send, cancel, or booking.
- **missing:** A cross-source commitment normalizer spanning Calendar, Mail, and authenticated browser tabs; Conflict scoring based on hard deadlines, travel/time zones, and relationship cost; A decision packet with alternatives and provenance; Draft-but-never-send adapters for mail, calendar, and browser forms

### "Let the pendant give me private live captions of the conversation around me, and let me ask for a one-sentence clarification or translation without interrupting anyone."
- **useful because:** This would make meetings, appointments, and noisy public conversations accessible through a device the owner already wears. It is different from a spoken assistant: the pendant becomes a discreet second channel for hearing, comprehension, and translation.
- **path:** pendant → mac-planner → relay-realtime → browser-extension → unified
- **model tier:** small streaming speech model for transcription/translation; realtime model only for an explicit clarification request
- **latency:** Caption chunks under 1.5 seconds behind speech; clarification response under 2 seconds; degrade to local rolling transcript when the relay is unavailable.
- **cost:** ~$0.03–$0.15 per 30-minute conversation depending on transcription and translation; raw audio transport and streaming inference dominate.
- **security:** Conversation audio is highly sensitive. Default to local Mac processing, show an unmistakable recording indicator, retain only the last 60 seconds unless the owner bookmarks it, and require consent before cloud relay or persistent storage.
- **missing:** A streaming caption surface on the Mac or phone; A pendant gesture for pause, bookmark, and clarification; Local speech separation/noise suppression and language identification; Explicit consent and retention controls for bystander audio; A low-latency audio uplink from the currently USB-connected pendant/bridge

### "When I point the pendant at a sign, appliance, package, or paper, tell me what it says and what matters, and remember the exact item only when I ask."
- **useful because:** The system currently reaches digital screens but not the physical world the owner is wearing it through. A tiny camera-plus-audio loop would make labels, forms, medication instructions, and unfamiliar controls accessible hands-free.
- **path:** pendant → mac-vision → relay-realtime → mac-planner → unified
- **model tier:** on-device vision prefilter and OCR; background vision model for extraction; realtime model only for the owner's spoken question
- **latency:** First useful answer under 3 seconds; OCR-only fallback under 1 second; no upload when the owner has not explicitly activated visual capture.
- **cost:** ~$0.02–$0.10 per deliberate visual query, dominated by image inference; idle sensing should be local and free.
- **security:** Camera images can contain bystanders, documents, and screens. Use a physical shutter/LED, capture only after a deliberate gesture, blur faces locally, never retain frames by default, and require confirmation before storing or acting on extracted data.
- **missing:** A pendant camera and physical privacy shutter/indicator; An authenticated low-latency image channel from pendant to Mac vision; On-device face/document redaction and OCR fallback; A gesture that distinguishes one-shot visual capture from accidental activation; A provenance record tying answers to the captured frame without retaining it


## Changes it proposed to its own stack

### `firmware` — Add an end-to-end 24 kHz audio acceptance mode: on a button gesture, the nRF9160 emits a short deterministic chirp and test phrase through the existing Opus decode → 24 kHz resample → 31.25 kHz I2S → ESP32 path, then the Mac harness records the bridge return and compares level, clipping, packet loss, and timing. Store a signed pass/fail receipt with firmware, codec, and bridge versions; refuse to call the path 'wideband' when it fails.
- **owner gets:** The owner gets speech that is consistently intelligible rather than a nominal sample-rate claim, and a clear answer when the pendant sounds bad. It makes the requested 24 kHz path verifiable on the hardware that is physically connected today.
- effort: Medium: firmware test opcode and telemetry, ESP32 capture hook, Mac acceptance script, and a small dashboard/receipt route.  ·  risk: Test audio could be audible in public and a false pass could hide intermittent radio faults. Use a low-volume test tone, require a deliberate gesture, and mark results stale after reconnect or firmware change; recover by falling back to the known 16 kHz profile.
- cost: No model/API cost. ~4–8 KB flash and <3 KB RAM; 20–40 ms test audio and negligible power beyond one playback.  ·  latency: Adds a deliberate 1–2 second test only when requested; no steady-state latency change.
- security: No speech content leaves the device during the deterministic test; receipts contain hardware/version metadata only.
- depends on: ESP32 bridge capture/loopback telemetry; 24 kHz audio implementation truth and acceptance criteria; A Mac-side receipt writer for /pipeline/audio results

### `hardware` — Revise the wearable from the current single-button/single-LED Nordic development kit to include a low-power haptic actuator and an ambient-light/proximity sensor, with a hardware microphone-power gate controlled by the nRF9160. Expose haptic patterns, pocket/desk detection, and hard audio cutoff as authenticated device events.
- **owner gets:** The owner can receive a discreet answer, warning, or confirmation in a meeting or pocket without broadcasting speech; the device can know when it is covered or being worn, and the hardware gate makes microphone privacy trustworthy rather than advisory.
- effort: High: product-board revision, enclosure and battery tuning, nRF9160 driver work, ESP32 bridge signal changes, and a privacy/notification protocol.  ·  risk: More components increase size, power draw, false proximity detections, and BOM complexity. Provide a firmware fallback to the existing LED/button, expose sensor confidence, and make the microphone gate fail closed on reset.
- cost: Roughly $3–$8 added component/BOM cost in modest volume; haptic pulses add tens of milliwatts briefly, sensors under a few milliwatts, and the gate itself negligible draw.  ·  latency: Haptic events can be immediate locally; sensor classification should complete in under 200 ms. No added conversational latency.
- security: A physical microphone gate materially improves privacy. Sensor data must remain local by default; only coarse states such as worn/covered and haptic acknowledgment may leave the device.
- depends on: A versioned device-event protocol between nRF9160, ESP32 bridge, Mac, and relay; Owner-visible privacy and notification state semantics; Battery budget and enclosure redesign


## What it asked for

### `s12-huom` (skill) — hard_mic_privacy_latch
- does: A long press on the pendant physically disables microphone capture at firmware level, shows a persistent red LED, rejects wake/audio-start commands while latched, and requires another deliberate long press to re-enable. The relay receives only a coarse latch/unlatch event after the link returns.
- must be on-device because: A server-side mute cannot protect the owner during a dropped link or a compromised/stale session. The pendant must guarantee that no microphone frames leave the device even when the Mac, bridge, or relay is confused.
- trigger: Long press of the existing pendant button; LED state is the immediate confirmation. Also latch automatically on boot until the owner explicitly enables capture.
- storage: One latch bit, monotonic transition counter, and last-transition timestamp in nonvolatile settings; under 64 bytes.
- RAM budget: ~2 KB firmware state and event handling, well within the 211,608 B application RAM; no audio buffering added. Must coordinate with the ESP32 bridge's capture-enable line, which is the key hardware dependency.

