# Harness derivation — faculty-judgement — round 27

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Protect my attention: notice what becomes urgent across my logged-in tabs, calendar, and Mac, hold non-urgent things, and tell me at the next safe moment—briefly on the pendant, with the evidence waiting on my Mac.”"
- **useful because:** The owner should not have to choose between constant interruption and missing a deadline. This turns scattered private signals into a small, timed queue: urgent items can break through, everything else arrives when attention is available, and every spoken claim has a reviewable source.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant → dashboard-ux
- **model tier:** Background/cheap model continuously normalizes and deduplicates page, calendar, and notification deltas; a small classifier scores urgency. Realtime is used only when the pendant delivers the queued item or the owner asks a follow-up. The Mac/browser provide private evidence; relay persists the queue; pendant is the low-latency output.
- **latency:** Capture and dedup within 1–3 minutes of a source change; urgent interrupt decision under 5 seconds; safe-moment delivery under 10 seconds after a focus transition. Spoken item should be one sentence, with a button press for next/more.
- **cost:** Roughly $0.01–$0.08 per day for background extraction/classification depending on polling and page volume; realtime cost only for delivered or queried items. Dominant costs are authenticated-page reads and repeated context, so cache source fingerprints and send deltas rather than pages.
- **security:** Private mail, calendar, and page text leave the Mac only as extracted deltas and cited snippets; secrets must be excluded from the urgency model. Never send, submit, delete, or alter source data. Interrupt rules need an explicit owner policy (what counts as urgent, quiet hours, driving/meeting signals), and a first-time or high-impact escalation should ask before speaking aloud.
- **missing:** A durable cross-surface attention-event queue with idempotent source fingerprints, expiry, and receipts; A focus/safe-moment signal from macOS (Focus, calls, meetings, keyboard/screen activity) and a pendant-local deferred-audio indicator; A shared urgency policy and explanation UI showing why an item interrupted, waited, or expired; Authenticated browser watch/read primitives and the 24 kHz playback path wired into queue delivery

### "“When my commitments collide, tell me which promise is actually at risk and prepare the least-cost way to resolve it.”"
- **useful because:** Today calendars show collisions but leave the owner to manually inspect email, documents, travel time, preparation work, and dependencies. The owner should get a consequence-ranked explanation and ready-to-review alternatives, not another generic reminder.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard-ux
- **model tier:** Use a cheap background model to extract dates, obligations, travel buffers, preparation dependencies, and cancellation terms from already-authorized calendar, mail, documents, and logged-in pages. Use realtime only when the owner asks a spoken question or chooses among alternatives. The Mac and browser keep private source access local; relay stores only normalized conflict records and drafts.
- **latency:** Recompute within five minutes of a relevant change; answer a pendant query in under three seconds from the conflict cache; prepare alternatives in under two minutes. Never interrupt for a low-confidence conflict.
- **cost:** About $0.02–$0.15 per conflict scan, dominated by authenticated-page/document extraction; incremental spoken interaction uses the realtime tier only on demand. Cache source hashes, parsed obligations, and expiry times to avoid resending full context.
- **security:** The system would see sensitive work and personal commitments. Keep raw mail and page text on the Mac/browser, send the relay only structured obligations and minimal quoted evidence, and show source links plus confidence. Drafting is reversible; sending cancellations, reschedules, or messages always requires explicit confirmation. Do not infer a social priority as fact—ask when values are ambiguous.
- **missing:** An obligation/dependency graph that distinguishes hard deadlines, soft preferences, travel buffers, preparation work, and cancellation penalties; A conflict simulator that proposes alternatives and explains time, money, and relationship impact; A cross-surface draft bundle that fills reversible calendar/message changes but stops at a single explicit approval checkpoint; A durable decision record so the owner's chosen tradeoff is reflected in reminders and later briefings


## Changes it proposed to its own stack

### `hardware` — Make 24 kHz superwideband a negotiated full-duplex product mode rather than a playback-only prototype: use a microphone/clock path that natively captures 24 kHz (the current I2S capture is 15,625 Hz), a codec/DSP budget that can sustain Opus encode plus decode without the current roughly 87% single-core load, and expose measured clock/packet-loss/latency telemetry. In parallel, define a relay↔pendant capability handshake with a 16 kHz fallback and an automated acoustic loopback acceptance test covering connect, packet loss, reconnect, and battery draw.
- **owner gets:** Speech will sound natural in both directions instead of only on playback, and a weak link will degrade gracefully rather than producing gaps or a dead conversation. The owner gets a dependable daily voice experience, not a demo that passes only on a bench.
- effort: High: select and validate an audio-capable production MCU/mic/clock, update firmware Opus framing and power management, add relay negotiation, and build a fixture/test recording. Prototype with the existing dev kit first to establish latency and CPU ceilings before committing hardware.  ·  risk: A clock or codec change can introduce echo, drift, or increased heat/battery use; firmware must retain the existing 16 kHz mode and boot-safe fallback. Recover by feature-gating 24 kHz, recording only synthetic test tones by default, and refusing the mode when CPU, temperature, RSSI, or battery thresholds are exceeded.
- cost: Prototype engineering is substantial; indicative product delta is roughly $5–$20 per unit for a better audio MCU/DSP, mic/clock, and power rails, plus test-fixture cost. API cost is negligible; higher bitrate may modestly increase cellular data usage.  ·  latency: Target 60 ms frames with end-to-end mouth-to-ear under 250 ms; capability negotiation adds under 1 second at session start. A 16 kHz fallback should switch within two frames after sustained loss or resource pressure.
- security: Audio remains encrypted in transit; telemetry must exclude raw audio and use coarse counters. Capability and fallback state should be visible in the receipt so the owner knows when a conversation was not superwideband.
- depends on: A verified end-to-end 24 kHz relay/pendant path and audio acceptance criteria; Firmware and relay support for capability negotiation and 16 kHz fallback; Production audio hardware feasibility and power/thermal measurements


## What it asked for

_Nothing._
## Its own summary

Round 27 produced two forward proposals. First, an attention-protection capability: private browser/calendar/Mac changes are deduplicated into an urgency queue, suppressed during focus, and delivered at the next safe moment on the pendant with cited evidence staged on the Mac. Second, a hardware/product change to make 24 kHz superwideband genuinely full-duplex: the current 15,625 Hz mic capture and ~87% single-core simultaneous codec load are not sufficient, so the product needs a native 24 kHz mic/clock and codec budget, negotiated fallback, telemetry, and acoustic loopback acceptance tests. I still need the durable attention-event queue, focus/safe-moment signals, shared urgency policy UI, verified audio acceptance criteria, and production audio/power measurements; without those, the proposals cannot be made dependable.

**Biggest unknown:** Whether the current pendant/bridge can sustain full-duplex 24 kHz within acceptable thermal, battery, and latency limits; the existing prototype numbers show playback at 24 kHz but capture at 15,625 Hz and high combined CPU load.

