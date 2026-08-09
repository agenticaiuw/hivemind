# Harness derivation — relay-realtime — round 247

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “fill this out for me,” have the pendant capture my answers, have the browser fill the authenticated form, and then read back only the fields whose final values do not exactly match what I said before submitting anything."
- **useful because:** Dictating sensitive forms while away from the Mac is fast, but a silent autofill mistake can be costly. This gives the owner a spoken, field-level verification loop rather than trusting a generic browser automation success message.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime relay for clarification and concise readback; mac-planner for deterministic field mapping; browser extension for authenticated DOM interaction; a cheaper background verifier for comparing transcript, entered value, and rendered final value.
- **latency:** A first spoken acknowledgement under 2 seconds; field extraction and browser work may take 10–30 seconds, with the pendant interruptible while it runs.
- **cost:** Roughly one realtime turn plus one planner/verifier invocation; about $0.03–$0.15 per form depending on number of fields and screenshots. Browser and Mac execution dominate latency, not speech.
- **security:** Form contents and dictated answers leave the pendant for relay processing and may include health, financial, or identity data. Never submit until every changed field is read back and explicitly accepted; redact values from dashboard logs and retain only a short-lived audit hash.
- **missing:** A structured form-field transcript/value comparison contract across browser DOM, speech transcript, and planner; A submit barrier that is verification-specific rather than a generic confirmation gate; Browser-side extraction of final rendered values, including masked and custom controls; Short-lived encrypted storage for the pending form session

### "What changed since I last checked? Have the pendant compare the last approved snapshot of a chosen project across my authenticated browser tabs and Mac files, then tell me only consequential additions, removals, and conflicts, with a one-tap spoken drill-down."
- **useful because:** The owner currently has to remember which app or tab held the previous truth. A cross-surface diff turns the wearable into a reliable change detector for a project, catching a changed deadline in a web portal, a modified local file, or contradictory versions without dumping a briefing.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use a cheap background model to normalize and diff snapshots; use realtime only for selecting the project and speaking the short result. Mac-planner and browser extension collect evidence, while the relay maintains the user-visible snapshot identity.
- **latency:** Return a scope acknowledgement in under 2 seconds; a small project should produce its first diff in 15 seconds and support later completion notification.
- **cost:** About $0.02–$0.10 per check for compact structured snapshots; browser/Mac calls and optional screenshot/OCR are the dominant cost. Repeated unchanged checks should avoid model calls through hashes.
- **security:** Authenticated browser content and local filenames may be sensitive. Snapshots need per-project encryption, redacted dashboard views, explicit retention/expiry, and source links. A changed page must never be treated as authoritative merely because it changed; report source and confidence.
- **missing:** A user-scoped snapshot registry with canonicalization and content hashes for Mac and browser evidence; A cross-surface diff engine that distinguishes semantic edits from layout/session churn; A project selector and snapshot approval gesture on the pendant; A conflict model for two sources disagreeing, rather than silently choosing one; A background trigger or routine integration that can run checks while the owner is away


## Changes it proposed to its own stack

### `hardware` — Add a low-power coin or linear-resonant haptic actuator and a sealed driver to the pendant, then define a firmware tactile vocabulary: one short pulse for a queued ordinary alert, two pulses for a finished delegated action, repeating long-short for needs-attention, and a deliberately different pattern for an incoming call/urgent alert. Keep audio and the single LED as existing surfaces; haptics are private and usable when the owner cannot hear or look at the pendant.
- **owner gets:** The owner can know that something is waiting without pulling out a phone, making noise, or confusing the LED with recording state. This makes the already-existing inbox and asynchronous work genuinely useful in meetings, transit, and crowded places.
- effort: Mechanical enclosure revision, one driver/GPIO or PWM path, firmware pattern scheduler, and end-to-end tests for dropped-link inbox events. Moderate hardware and firmware work; validate comfort and false-trigger resistance with several wear positions.  ·  risk: A stuck driver could drain the battery or buzz continuously; enforce a hardware timeout and boot-time watchdog cutoff. Patterns could be mistaken for notifications, so provide a button replay and a documented mapping. Do not use haptics for consent or destructive-action approval without a distinct physical interaction.
- cost: Approximately $2–$8 in components and PCB/enclosure changes at prototype quantity, plus roughly 5–20 mA only during pulses and negligible idle draw. No per-event API cost.  ·  latency: Near-immediate local feedback once an inbox record or relay event reaches the pendant; no speech round trip required.
- security: Improves privacy because status can be conveyed silently. Avoid encoding message contents or secrets in patterns; only urgency/category should be tactile.
- depends on: Extend the existing offline_alert_inbox record with urgency/category fields rather than creating another queue; Map relay event delivery and pendant inbox polling to the haptic pattern scheduler; Add a physical mute/snooze state that persists only for a bounded interval


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing proposals: (1) a voice-dictated authenticated-form workflow that compares every final browser field to the owner's words before submission, (2) a cross-surface project snapshot/diff service spanning authenticated browser state and Mac files, and (3) a physical haptic channel for private inbox and delegated-job status. The first two need new connective state/diff/verification contracts; the third needs a pendant hardware revision and firmware integration with the existing inbox.

**Biggest unknown:** The remaining uncertainty is product prioritization and implementation ownership: which project or form workflow the owner wants as the first concrete end-to-end test, and whether the pendant enclosure can accept a haptic actuator without compromising its jewellery form.

