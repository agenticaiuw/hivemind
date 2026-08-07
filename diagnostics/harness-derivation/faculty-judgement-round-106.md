# Harness derivation — faculty-judgement — round 106

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current cross-surface readiness** — Relay and Mac bridge are online, but the Mac agent reports ready:false; Accessibility and Screen Recording are still false, browser bridge is offline with 9 queued commands, and the pendant is not registered. Automation grants for Calendar, Mail, Notes, Reminders, Safari, Chrome, and System Events are present.
  - evidence: GET /ops/status 200 at round 106

## Capabilities it proposed

### "“Translate this conversation for me, quietly.” The pendant should listen only while I hold the button, speak a concise translation through my earpiece, and show the original plus translation on my Mac when I want to review it."
- **useful because:** This gives the owner a discreet language bridge in travel, work, or appointments without handing a phone to another person. The pendant supplies the intimate, immediate interaction; the relay supplies low-latency speech translation; the Mac preserves a readable transcript; and the browser can look up unfamiliar names or terms without exposing the whole conversation to a public search.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime for turn-by-turn speech recognition/translation and short spoken output; a cheaper background text model for transcript cleanup, speaker-turn grouping, and terminology lookup. Never send raw audio to the background model unless the owner explicitly asks for a transcript.
- **latency:** The first translated phrase should begin within 1.5 seconds of a completed utterance; short phrases should stream incrementally. Mac review can lag by several seconds. If network quality drops, the pendant should say that translation is unavailable rather than inventing one.
- **cost:** Realtime audio translation dominates, roughly $0.01–$0.08 per minute depending on provider and audio duration; background cleanup and occasional public lookups are cents or less per session. Storage cost is small if raw audio is discarded after translation.
- **security:** Conversation audio and translations may contain health, financial, or identifying information. Require press-to-listen, a visible LED/haptic recording indicator, an explicit per-session retention choice, automatic deletion of raw audio, and local-only mode for a user-supplied phrasebook. Do not retain or search third-party speech by default. Browser lookups must use only public sources unless separately authorized. Translation is advisory: for medical, legal, or financial conversations, label uncertainty and offer the original transcript rather than silently substituting it.
- **missing:** A translation session protocol with hold-to-talk boundaries, language selection, interruption handling, and an honest unavailable state; Streaming speech-to-speech translation in the relay with timestamps and confidence/uncertainty markers; Pendant firmware support for a press-to-talk translation mode and a distinct recording indicator; A Mac transcript viewer that can pair original and translated segments and delete the entire session; A privacy/retention gate that prevents raw third-party audio from entering routine memory; Optional terminology lookup that asks before sending a phrase or name to browser search


## Changes it proposed to its own stack

### `hardware` — Replace the prototype's single-button/LED interaction with a small haptic actuator and low-power IMU on the free I2C bus, plus a fuel-gauge IC. Define a three-state tactile protocol: one short pulse = safe/reversible completion, two pulses = approval needed, long pulse = blocked/error; a deliberate double-tap/tilt gesture can approve or dismiss only a pre-authorized reversible action. The relay records an action nonce and the Mac/browser surfaces must verify that nonce before committing. Keep the physical button as the emergency stop and voice trigger.
- **owner gets:** The owner can approve a prepared reminder, browser draft, or Mac action discreetly in a meeting or while walking, without taking out the phone or relying on a tiny LED. Battery warnings become real instead of guessed, and a dropped link leaves an honest tactile blocked signal rather than a falsely spoken 'done'.
- effort: Prototype: choose I2C fuel gauge and coin/ERM haptic driver, route two GPIOs and add IMU polling; firmware gesture/state machine; relay nonce/ack endpoint; Mac and browser adapters; bench-test false taps and LTE reconnects. Product enclosure and wear-test are required.  ·  risk: Accidental approval from motion or pocket contact; mitigate with explicit arming pulse, two-step gesture, short expiry, and never permit irreversible actions (send/delete/purchase) by haptic gesture. Haptic motor noise and battery draw may affect audio. On sensor failure, fall back to button/voice and mark unavailable.
- cost: Roughly $8–20 in prototype components (fuel gauge, haptic driver/actuator, 6-axis IMU, passives), <10 mA average when sampled intermittently and 60–100 mA only during haptic pulses; negligible API cost.  ·  latency: Local acknowledgement under 100 ms; relay nonce verification adds roughly one LTE round trip for connected actions. Offline gestures should only acknowledge/queue, never claim committed state.
- security: Physical gestures are possession signals, not identity; require nonce binding, expiry, replay protection, and confirmation policy. Battery telemetry and gesture events should be treated as private device metadata.
- depends on: Execution Truth Contract / postcondition verification; A durable cross-surface action nonce and acknowledgement record; Owner-selected haptic gesture policy; irreversible actions remain voice/dashboard-confirmed


## What it asked for

_Nothing._
## Its own summary

Round 106 produced a new hardware-and-protocol proposal: a haptic/IMU/fuel-gauge interaction module on the pendant, with nonce-bound tactile approval for reversible actions, emergency-stop button semantics, and truthful battery/error feedback. It enables discreet cross-surface control that voice, Mac, relay, or browser alone cannot provide. Current live state was recorded: relay/Mac online but Mac ready:false, browser offline with 9 queued commands, pendant unregistered, and Accessibility/Screen Recording unavailable.

**Biggest unknown:** Whether the owner wants to evolve beyond the nRF9160 DK prototype into a wearable hardware revision, and which physical gesture they would find reliable enough for reversible approvals.

