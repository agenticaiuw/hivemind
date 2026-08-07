# Harness derivation — unified — round 121

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Teach the pendant a routine once: “When a new invoice arrives, gather the matching order, fill the bookkeeping form, and ask me before submitting.” Then run that routine automatically when the trigger appears, with a spoken preview and a one-button approval."
- **useful because:** The owner can turn a repeated multi-site chore into a supervised habit without writing rules. The browser supplies private authenticated data, the Mac can handle local files, the relay persists the trigger and job, and the pendant is the interruption/approval surface.
- **path:** pendant → relay-realtime → relay → browser-extension → mac-planner → dashboard
- **model tier:** background for trigger detection and extraction; planner only to create or revise a routine; realtime only for the approval conversation
- **latency:** Trigger checks may take minutes; preview under 5 seconds after detection; approval response must feel immediate.
- **cost:** Usually a few background calls per trigger plus one planner call when the routine changes; roughly $0.01–$0.08 per run depending on private-page extraction, with no realtime spend until approval.
- **security:** Authenticated page contents and local invoice files leave their surfaces only to the relay for the requested job. Never auto-submit, send mail, or pay; require a fresh physical button press or explicit spoken approval bound to the exact before/after preview. Encrypt routine definitions and redact account numbers in spoken output.
- **missing:** voice-to-routine capture and versioned routine schema; durable trigger evaluator over browser/mail events; sandboxed dry-run executor that can span browser and Mac; approval token bound to a specific preview and expiry

### "When something important happens across my Mac or logged-in browser, interrupt me only if it beats my current attention threshold; otherwise queue it and give me one concise spoken catch-up when I am free."
- **useful because:** Today each surface can discover events, but none understands that the owner is in a meeting, already speaking, or deliberately ignoring low-value noise. This makes the pendant a useful attention filter rather than another notification channel.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard → relay-realtime
- **model tier:** deterministic rules plus a cheap background classifier for urgency; realtime only to deliver a genuinely urgent one-sentence alert or answer a catch-up request
- **latency:** Urgent events classified in under 2 seconds; nonurgent batching can wait until the next availability window; catch-up under 3 seconds.
- **cost:** Near-zero for rules, cents per day for background classification of event summaries, and no planner call for ordinary batching.
- **security:** Event summaries should be minimized and sensitivity-tagged before leaving Mac/browser. Calendar state can suppress audio but must not expose meeting titles aloud in public. Never infer an emergency from arbitrary content without a visible dashboard explanation and a mute/override control.
- **missing:** cross-surface event envelope with sensitivity and urgency fields; availability state sourced from calendar plus active pendant session; deduplicating attention broker with quiet hours and escalation rules; spoken catch-up composer that links each item to its source

### "Give the assistant a temporary, narrowly scoped lease—such as “for the next 30 minutes, monitor this support portal and prepare updates, but do not send or purchase anything”—then revoke it instantly from the pendant."
- **useful because:** The owner can delegate bounded work without granting a permanent blanket permission. The browser holds private sessions, the Mac handles local files, the relay enforces expiry, and the pendant gives a trustworthy revoke path even when the Mac UI is unavailable.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard → relay-realtime
- **model tier:** deterministic policy engine for scope, expiry, and revocation; background model for monitoring; planner only for ambiguous work inside the lease
- **latency:** Lease creation and revocation under 1 second; revocation must stop new actions within 2 seconds; monitoring can be minutes apart.
- **cost:** Low: deterministic policy checks plus background polling; approximately $0.01–$0.05 per monitoring cycle, with planner usage only for unusual cases.
- **security:** Least-privilege scopes, expiry, audience, URLs, and action classes must be signed into a lease. Destructive actions remain separately gated. A physical pendant revocation must work offline and synchronize as soon as the link returns. Log every action and rejected attempt.
- **missing:** signed capability-lease format and verifier on every executor; revocation registry replicated to Mac, relay, and browser bridge; lease editor showing exact allowed resources and actions; offline pendant revoke queue with monotonic sequence numbers

### "Translate a nearby conversation through the pendant in real time: speak to me in my chosen language, keep technical names intact, and show the original and translated transcript on my Mac only when I ask."
- **useful because:** This would make the pendant useful in a conversation where reaching for a phone is awkward. The pendant is the always-present microphone and earpiece, the bridge handles low-latency audio, the relay translates, and the Mac provides an optional private transcript and terminology lookup.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** realtime speech and translation model for the live exchange; background model for transcript cleanup and terminology extraction; never use the expensive planner for each utterance
- **latency:** First translated phrase within 700 ms and steady-state under 500 ms where the link permits; degrade to phrase mode when LTE quality drops.
- **cost:** Realtime audio/translation dominates, roughly $0.01–$0.08 per minute depending on codec and model; transcript cleanup runs only after the exchange.
- **security:** Explicit button activation and a visible LED state are required. Do not retain source audio by default; encrypt transient audio and delete it after translation. The Mac transcript must stay local unless the owner explicitly exports it. Add a clear stop gesture and remote kill switch.
- **missing:** full-duplex low-latency audio path at the target quality; streaming speech-language identification and translation protocol; jitter buffer and link-aware phrase-mode fallback; local transcript-only storage and explicit retention controls

### "Before I say something sensitive near other people, have the pendant recognize whether the current listener is me or an unknown speaker and automatically switch to silent haptic/LED responses instead of reading private information aloud."
- **useful because:** The owner gets an assistant that remains safe in public spaces. The pendant can make the immediate audio decision locally, while the relay and Mac provide sensitivity labels and the dashboard explains why output was muted.
- **path:** pendant → relay-realtime → relay → mac-planner → dashboard
- **model tier:** small on-device speaker-presence/voice-match model for the immediate decision; deterministic sensitivity policy; background model only to classify ambiguous content
- **latency:** Local output decision under 150 ms; no relay round trip for muting. An ambiguous case defaults to silent output and can be unlocked by the button.
- **cost:** Small one-time firmware/model work; negligible per-turn API cost because the safety decision is local. Occasional background classification costs less than a cent per interaction.
- **security:** Store only an encrypted voice embedding, never raw enrollment audio. Unknown-speaker detection must fail closed, with no private content spoken. Do not claim biometric identity; treat it as a coarse local presence signal. Provide enrollment deletion and a physical privacy latch.
- **missing:** on-device speaker-presence/voice-match model within the nRF9160 RAM budget; sensitivity labels attached to generated responses and queued audio; local output mute latch integrated with the I2S playback path; safe enrollment and deletion flow


## Changes it proposed to its own stack

### `hardware` — Add a low-power 6-axis IMU and a small haptic actuator to the product pendant, with a local privacy/removal state machine: detect wrist-off/body-off, double-tap, and deliberate shake patterns; expose only coarse events to firmware and relay. Use haptics for silent completion/approval prompts and automatically stop microphone capture when removed.
- **owner gets:** The owner gets a wearable that can be used silently in a meeting, confirms actions without speaking, and cannot keep listening after it is taken off. Gestures also make the device usable when the Mac is asleep or the LTE link is absent.
- effort: Product-board revision, IMU driver/calibration, haptic driver, gesture tuning, enclosure testing, and firmware state-machine integration. Prototype quickly on the free I2C/SPI buses and ESP32 bridge before committing a PCB.  ·  risk: False removal or gesture detections could mute a conversation or approve the wrong thing; approval gestures must never be sufficient for irreversible actions without the existing server-side gate. Recover with explicit button press and a visible LED error pattern; provide a hardware disable/override.
- cost: Roughly $3–$8 BOM increase in modest volume, plus under 10 mA peak haptic current and tens of µA to a few hundred µA for the IMU depending on mode; negligible API cost.  ·  latency: Local gesture/removal response under 100 ms; no relay round trip for privacy mute or haptic acknowledgement.
- security: Improves local privacy because removal can cut the mic before the server sees anything. Gesture events must be authenticated and sequence-numbered so replayed serial/LTE packets cannot approve actions.
- depends on: production pendant enclosure and power budget; firmware audio state-machine hook; relay event schema for privacy and gesture state; end-to-end audio-path validation


## What it asked for

_Nothing._
