# Harness derivation — faculty-judgement — round 125

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I miss something genuinely important, keep trying to reach me quietly, and—only under rules I set—escalate to a trusted person with exactly what happened."
- **useful because:** Today a reminder, deadline, or safety-critical follow-up disappears when the pendant is offline or the owner is busy. This creates a bounded safety net across the always-awake relay, the Mac/browser evidence, and the wearable, without turning every notification into an interruption.
- **path:** relay-realtime → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension → unified
- **model tier:** Use the cheap background model for deadline monitoring and evidence summarization; use realtime only for the owner's live acknowledgement or rule change. Never let a model invent an escalation trigger.
- **latency:** Normal checks can be 1–5 minutes; an owner acknowledgement should be delivered within seconds when the pendant or Mac is reachable. Escalation waits for the owner's configured grace period, not model judgment.
- **cost:** Low: scheduled/event checks and short summaries dominate, typically cents per day per dozen watched obligations; realtime cost occurs only when the owner answers or changes a rule.
- **security:** Requires explicit allowlisted contacts, categories, quiet hours, grace periods, and a test mode. Escalation must include minimum necessary facts, never secrets or raw audio, and require confirmation before enabling a new contact or category. Every attempt needs a durable, auditable receipt and a kill switch.
- **missing:** A durable obligation/deadline record with source and confidence (calendar, browser page, or owner statement).; A policy evaluator that can distinguish 'remind again' from 'escalate' and enforce quiet hours and confirmation gates.; A reliable outbound channel to a pre-approved contact (SMS/voice/email) and delivery receipts.; A pendant or phone acknowledgement signal that works offline and reconciles when connectivity returns.

### "When I’m carrying something out in the world, let me point the pendant at it and ask what I’m looking at or what to do next—read a label, find the right switch, compare two items, or follow a repair step hands-free."
- **useful because:** The current system can act on the Mac and read authenticated browser pages, but it cannot perceive the owner’s physical surroundings. A wearable visual channel would make the assistant useful away from screens: shopping, cooking, repairs, navigation inside a building, and accessibility support.
- **path:** pendant → relay-realtime → faculty-perception → faculty-judgement → faculty-action → unified → mac-vision
- **model tier:** Use a small on-device vision preprocessor for crop, blur, and text detection; send only an owner-triggered frame or short burst to a background vision model. Use realtime only for the spoken answer and immediate step-by-step guidance.
- **latency:** Capture and answer in 1–3 seconds for a single frame; step guidance should maintain a conversational turn under 1 second after each owner question. Offline mode can provide local OCR and defer richer interpretation.
- **cost:** Usually cents per interaction; image upload and vision inference dominate. Local OCR and aggressive frame gating keep continuous streaming off and costs predictable.
- **security:** Camera activation must be physically obvious and owner-triggered, with a shutter/LED and no ambient recording. Faces, screens, and documents should be blurred locally by default; never retain frames unless the owner explicitly saves one. Require confirmation before guidance that could cause physical harm, and clearly label uncertainty.
- **missing:** A pendant camera or secure camera accessory, image sensor, shutter/indicator, and a frame-capture protocol; the current pendant has no camera.; A privacy-preserving image pipeline with local redaction, bounded resolution, upload consent, and deletion receipts.; Vision inference and spoken grounding that can maintain a short sequence of frames without silently turning into surveillance.; A physical pointing/trigger gesture and an offline OCR/basic object-recognition fallback.


## Changes it proposed to its own stack

### `hardware` — Add a low-power haptic actuator and a 6-axis IMU to the pendant, with a tiny local acknowledgement state machine: distinct vibration patterns for ordinary reminder, repeated reminder, and pre-authorized escalation; a double-tap or button press acknowledges or cancels. Log only event type, monotonic time, and acknowledgement—not motion traces or audio. Expose the acknowledgement over the existing WebSocket when connected and persist a compact offline queue in the existing microSD failure buffer.
- **owner gets:** The owner can acknowledge an important prompt silently in a meeting, while walking, or when headphones are unavailable; missed prompts remain recoverable after an LTE drop instead of escalating blindly.
- effort: Prototype I2C/SPI driver, enclosure revision, power characterization, and a small Zephyr state machine; then add relay reconciliation and test patterns with the existing ESP32 audio bridge.  ·  risk: False taps, accidental acknowledgements, extra battery drain, and confusing patterns. Require a deliberate gesture/button chord for cancel, repeat critical prompts after timeout, and fall back to audio/LED if haptic self-test fails.
- cost: Roughly $3–8 in components and modest assembly cost; haptic bursts are low duty-cycle but LTE remains the dominant power draw. Negligible model/API cost.  ·  latency: Local acknowledgement is sub-100 ms; network reconciliation is deferred during modem contention and does not add to the audio path.
- security: Improves privacy by enabling silent prompts. Do not infer location, activity, or identity from IMU data; keep raw motion off-device and retain only acknowledgement events.
- depends on: A durable obligation/escalation policy and acknowledgement receipt path; A defined pendant-to-relay event message and offline replay protection; Owner-approved haptic patterns and cancellation gesture

### `hardware` — Revise the pendant enclosure to include an owner-triggered camera module with a physical shutter, a bright capture indicator, a dedicated capture/hold gesture, and a low-power local ISP path for crop, face/screen redaction, and OCR before LTE upload. Keep the existing mic/I2S/audio path independent so visual capture cannot starve live speech.
- **owner gets:** They gain eyes-free help with real objects and printed instructions while preserving a clear physical boundary against accidental or ambient recording.
- effort: Select a low-power sensor and lens, add secure capture and redaction firmware, revise enclosure and power budget, define a bounded frame protocol in the relay, and validate speech-plus-image modem contention.  ·  risk: Privacy leaks, poor lighting, incorrect guidance, heat, and LTE contention. Shutter/indicator must fail closed; no frame upload without a deliberate trigger; cap burst length and fall back to OCR-only/offline behavior when the link is weak.
- cost: Approximately $15–40 prototype BOM increase plus enclosure redesign; camera/ISP bursts add substantial peak power, so battery capacity and thermal testing are required. Vision inference adds per-use API cost.  ·  latency: Local capture/redaction in tens to hundreds of milliseconds; remote interpretation adds roughly 1–3 seconds and must yield to live audio bandwidth.
- security: Physical shutter and local redaction reduce bystander and document exposure. Encrypt frames in transit, avoid persistent storage by default, and provide a visible deletion receipt for any saved frame.
- depends on: A secure owner-triggered frame-upload protocol; A relay vision endpoint and short-lived frame storage; A spoken answer contract that distinguishes observation from inference


## What it asked for

_Nothing._
## Its own summary

I discovered the live fleet (Mac bridge and Safari are online; pendant/mobile are offline), the owner’s standing privacy rules, and the 64-item backlog. I added a new life-level capability: bounded missed-obligation escalation to an allowlisted trusted contact, with minimum-necessary disclosure, grace periods, receipts, and a kill switch. I also proposed a concrete hardware enabler: haptic actuator + IMU with local acknowledgement and offline replay-safe event queue, so the owner can silently acknowledge prompts and prevent blind escalation. I still need owner-defined escalation contacts/categories, quiet hours and grace periods, acknowledgement/cancel semantics, and an outbound contact channel; engineering still needs an event protocol and durable reconciliation. Accessibility/Screen Recording remains owner-blocked, but this proposal does not depend on it.

**Biggest unknown:** What does the owner consider genuinely escalation-worthy, who may be contacted, and what exact information may leave the system? Without those policy answers, the system must remain reminder-only.

