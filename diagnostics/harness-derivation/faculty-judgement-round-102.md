# Harness derivation — faculty-judgement — round 102

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When something genuinely urgent happens in my mail, calendar, or logged-in browser, alert me silently with a distinct vibration pattern, and let one pendant tap tell me whether it is worth speaking aloud."
- **useful because:** The owner can remain reachable in a meeting, on transit, or in public without a spoken interruption or screen glance. The Mac/browser can do the expensive evidence gathering while the pendant communicates only urgency and a tiny private summary.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model to classify and deduplicate events; escalate to the realtime model only after the owner taps for the spoken explanation. The judgement layer must require corroborating evidence from at least one authenticated source before marking an event urgent.
- **latency:** Urgency classification within 30 seconds of an event; haptic delivery within 2 seconds after classification; spoken detail begins within 1 second of an explicit tap.
- **cost:** Usually well under $0.01 per event with small-model classification and hashing; occasional realtime tap explanations dominate cost. Hardware adds roughly $1–$3 for a vibration motor, driver, and mechanical integration, plus a small alert-time battery cost.
- **security:** The vibration must encode only coarse severity, never message content. Sensitive account names and snippets stay off the pendant until an explicit tap, and no mail is sent, deleted, or purchased from an alert. Require deduplication, quiet hours, a physical stop gesture, and an audit receipt for every alert.
- **missing:** A pendant haptic actuator and firmware pattern table with an offline acknowledgement/stop path; An event-to-urgency classifier that consumes normalized, provenance-bearing mail/calendar/browser events without ambient audio; A low-latency authenticated push channel from relay to pendant and delivery acknowledgement telemetry; Owner-configurable severity sources, quiet contexts, and escalation policy

### "Run a seven-day experiment for me: turn a specific intention into tiny check-ins, notice whether it is helping from my explicit replies and completed actions, and give me a verdict with evidence and a recommendation to keep, change, or stop."
- **useful because:** The owner gets help changing behavior without committing to a permanent automation or relying on vague end-of-week memory. The pendant provides timely, low-friction check-ins; the Mac and browser provide objective completion evidence; the relay preserves the experiment while the owner is away.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model for scheduling, aggregation, and trend summaries; use realtime only when the owner answers a check-in or asks for interpretation. Never infer health or emotion from ambient audio.
- **latency:** A check-in should arrive at its scheduled boundary within 30 seconds; a daily summary under 10 seconds; the final verdict under 20 seconds on demand.
- **cost:** About $0.02–$0.10 per seven-day experiment, dominated by the final synthesis and any realtime conversation; storage is a few kilobytes of explicit responses and event references.
- **security:** Experiments may reveal sensitive health, work, or relationship information. Require explicit opt-in, a named purpose and expiry, local/private storage by default, deletion at experiment end, and confirmation before creating external reminders or changing routines. Report uncertainty and avoid medical claims.
- **missing:** A durable experiment schema with hypothesis, intervention, check-in cadence, stop conditions, outcome measure, expiry, and consent receipt; A cross-surface evidence joiner that distinguishes explicit owner responses from weak behavioral proxies; Pendant-local scheduled check-in and snooze state that works through a temporary relay outage; A final decision report that cites observations and supports one-tap keep/change/stop


## Changes it proposed to its own stack

### `hardware` — Replace the prototype audio front end with a production capture chain whose microphone/codec natively samples at 24 kHz or 32 kHz (with a documented anti-alias filter), and reserve DSP/CPU and power budget for simultaneous 24 kHz Opus encode and decode. Keep the existing bridge transport negotiable so older pendants can fall back to 16 kHz, while the new device advertises its actual capture/playback capabilities during handshake.
- **owner gets:** The owner gets genuinely clearer speech and more natural voice replies instead of a nominal 24 kHz playback path fed by 15.625 kHz capture. It also prevents us from shipping a misleading 'superwideband' mode that cannot carry superwideband input.
- effort: Medium-high: select and validate an audio codec/mic, update board layout and power analysis, add capability negotiation, and run MOS/latency/battery tests on the enclosure prototype.  ·  risk: A new codec can introduce EMI, driver instability, or worse battery life; recovery is a negotiated 16 kHz fallback and a hardware revision using the validated reference design. Do not enable 24 kHz mode unless the handshake and loopback test pass.
- cost: Roughly $5–$20 incremental BOM for a suitable codec/mic and supporting passives; modest additional API cost only if higher-bitrate Opus is selected. Expect a measurable but bounded increase in audio power draw during calls.  ·  latency: Potentially neutral to slightly better if the codec performs resampling; simultaneous encode/decode still needs profiling because the current software path already consumes roughly 87% of one core.
- security: No new data class leaves the device; capability negotiation should be authenticated and must not expose identifiers beyond codec/sample-rate support.
- depends on: End-to-end 24 kHz relay/firmware acceptance test; A production hardware reference design rather than the current Nordic development kit; Audio capability negotiation in the pendant↔bridge handshake

### `hardware` — Add a sealed low-power haptic actuator and driver to the production pendant, with three firmware-owned patterns (notice, urgent, critical), a physical long-press stop, and a retained delivery/ack bit that survives a dropped relay link. Expose only pattern ID and acknowledgement state to the server; never encode content in vibration timing.
- **owner gets:** The owner can receive a meaningful alert discreetly in a meeting or while moving, without speech, a phone, or a screen. They can silence it locally even when the network is unavailable.
- effort: Medium: mechanical enclosure/acoustic testing, driver and firmware work, battery characterization, and relay protocol support. Requires a small user study to ensure patterns are distinguishable without being annoying.  ·  risk: False urgency could erode trust or distract the owner; firmware bugs could leave an alert latched. Mitigate with conservative defaults, quiet hours, a guaranteed long-press stop, watchdog expiry, and a server-side alert receipt/undo record.
- cost: Approximately $1–$3 BOM increase and a few milliwatt-seconds per alert; negligible model/API cost. The enclosure and certification work will dominate engineering cost.  ·  latency: Local haptic start is sub-100 ms after a received push; offline stop remains immediate. No impact on conversational audio.
- security: No message content or account identity is emitted through the actuator or BLE advertisements. Delivery metadata should be encrypted and retained only briefly.
- depends on: Authenticated relay-to-pendant push and acknowledgement protocol; Owner urgency/quiet-hours policy; Event normalization and deduplication between mail, calendar, and browser sources


## What it asked for

_Nothing._
## Its own summary

I discovered no new orchestrator grants this round. The important remaining blocker is physical: the pendant currently captures at 15,625 Hz, so its 24 kHz playback/Opus path cannot be true end-to-end superwideband. I recorded a new hardware change proposing a production 24/32 kHz microphone/codec chain, authenticated capability negotiation, and a safe 16 kHz fallback. I also notified relay-realtime so the server cannot advertise superwideband when the device cannot capture it.

**Biggest unknown:** Whether the owner wants to revise the provisional pendant hardware now, or accept a software-only 24 kHz playback demonstration on the current development kit. To proceed honestly, we still need a codec/mic reference design, measured battery/power limits, and a loopback acceptance test defining what '24 kHz end to end' means.

