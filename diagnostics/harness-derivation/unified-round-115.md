# Harness derivation — unified — round 115

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m leaving my desk—carry this browser work with me and let me pick it up from the pendant later.”"
- **useful because:** The owner can move between Mac, browser, and pendant without losing the exact logged-in page, extracted facts, or unfinished reversible steps. The pendant becomes a continuity anchor rather than a separate chat; no single surface can preserve authenticated browser state and provide hands-free later recall.
- **path:** browser-extension → mac-planner → relay-realtime → relay-realtime → dashboard
- **model tier:** Use gpt-5.6-luna in the Mac/browser planner for page-state extraction and step checkpointing; use the realtime tier only for the brief spoken handoff and later recall. Use a cheaper background model for compaction and expiry.
- **latency:** A handoff receipt in under 5 seconds while the tab is open; later pendant recall under 1.5 seconds for the spoken acknowledgement, with detailed state fetched asynchronously.
- **cost:** About $0.01–$0.04 per handoff dominated by page extraction/planning; later one-sentence recall is a small realtime turn. Storage is tiny JSON plus optional encrypted snippets.
- **security:** Authenticated page text and URLs leave the Mac only to the relay, so encrypt the snapshot, apply a short TTL, redact secrets/payment fields, bind it to the browser session, and never submit queued actions during handoff. Reopening or executing a pending step requires explicit confirmation.
- **missing:** A first-class cross-surface handoff object with tab/session binding, checkpoint state, TTL, and resume/abort status; An authenticated browser snapshot API that returns current tab metadata and only the selected semantic regions; Pendant voice intents for list, resume, forget, and confirm a handoff; Encrypted short-retention storage and a receipt that says exactly what was captured

### "“Start meeting mode. Keep me oriented, capture decisions and action items, and give me a private spoken nudge only when I need to act.”"
- **useful because:** Today the pendant can answer questions and the Mac can separately inspect Calendar or a browser, but nothing follows a live meeting across the wearable, authenticated meeting tab, Mac workspace, and relay. This would let the owner stay present while receiving only urgent, private guidance, then leave with a sourced decision log and assigned follow-ups instead of reconstructing the meeting afterward.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime tier only for low-latency interruption triage and short spoken nudges. Use gpt-5.6-luna on the Mac for calendar/meeting-page context, diarization-free action-item extraction, and note drafting; use a cheaper background model to compact the transcript and produce the final minutes.
- **latency:** Start-up context in 5 seconds. A spoken nudge within 2 seconds of an urgent trigger. Decision/action extraction can lag by 30–60 seconds and the final review packet can finish after the meeting.
- **cost:** Approximately $0.10–$0.50 per 60-minute meeting depending on audio transcription volume; the dominant cost is continuous speech processing and optional Mac system-audio capture. Storage can be reduced by retaining structured events and a short-lived encrypted transcript rather than raw audio.
- **security:** Meeting audio, calendar details, and private browser content are highly sensitive. Meeting mode must require an explicit physical start and stop, display a visible LED/dashboard indicator, announce recording/transcription status to participants where required, provide a local mute latch, encrypt in transit and at rest, redact secrets, and default to deleting raw audio after event extraction. Never send messages or create external commitments without confirmation.
- **missing:** A meeting-mode session spanning pendant, relay, Mac, and browser with explicit start/stop and participant-notice state; A Mac audio-ingest path that can separate meeting audio from the owner's microphone without Accessibility/Screen Recording assumptions, or an honest degraded mode using only pendant mic input; Low-latency event extraction for decisions, questions addressed to the owner, deadlines, and action items with timestamped evidence; A private nudge channel that can interrupt playback without leaking meeting content aloud; A reviewable workspace packet linking each extracted item to its time range and source, with confirmation before creating reminders or sending follow-ups


## Changes it proposed to its own stack

### `hardware` — Replace the nRF9160 DK + ESP32 audio prototype for the product audio path with a cellular SoC/audio design that has a dedicated 24 kHz-capable I2S codec, DMA ring buffers, and enough DSP headroom for simultaneous Opus encode/decode; keep the modem control plane separate from the audio task and make the negotiated sample rate explicit end to end. Target at least 2x the measured current audio CPU margin and a hardware mute path.
- **owner gets:** Speech will remain intelligible and natural during real two-way use instead of depending on a half-duplex, CPU-starved development-board chain that can glitch or go silent. A local mute also gives the owner immediate privacy even if the link or relay misbehaves.
- effort: High: product-board schematic/layout, codec and antenna validation, Zephyr audio driver, DMA/clocking work, Opus profiling, and RF/audio coexistence testing. Prototype first with the current boards using instrumentation, then EVT/DVT hardware.  ·  risk: New silicon, clocks, and RF layout can introduce noise, modem regressions, or battery drain. Recover with a compile-time 16 kHz compatibility profile, watchdog-restartable audio tasks, packet-loss concealment, and a hardware bypass/mute. Do not claim 24 kHz acceptance until measured across the entire path.
- cost: Roughly $15–$40 added prototype BOM per unit for codec, clocking, power, and board changes, plus substantial one-time engineering cost; higher active current than the current dev kit but potentially lower total energy through fewer retransmits and shorter calls.  ·  latency: DMA buffering and negotiated 24 kHz should keep added local latency below 20 ms; simultaneous encode/decode may reduce relay buffering versus the current 60 ms decode frames.
- security: A physical mute latch must be fail-safe and report its state to the relay; audio should not be retained beyond the existing short-retention policy, and diagnostic logs must exclude raw audio.
- depends on: 24 kHz end-to-end audio acceptance thresholds; audio pipeline preflight and link-fault validation; measured current draw and battery budget for the production pendant; A product audio compatibility decision for the headphone/bridge path

### `hardware` — Add a sealed low-power haptic actuator and a small ambient-light/proximity sensor to the production pendant, with a dedicated hardware mute/status state exposed to firmware. Use distinct short vibration patterns for urgent nudge, confirmation request, and successful capture; automatically suppress them in an owner-configured quiet mode while retaining a physical tactile mute indication.
- **owner gets:** The owner can receive private, intelligible alerts in a meeting, on a walk, or in a noisy room without the pendant speaking sensitive content aloud or requiring them to look at a screen. Today’s single button and LED cannot provide reliable discreet feedback.
- effort: Medium hardware revision plus firmware driver, enclosure/acoustic isolation, pattern design, and end-to-end tests for false triggers and comfort. Prototype with an ERM/LRA actuator and tune against the final enclosure before committing to production.  ·  risk: Vibration can be missed, mistaken for a phone alert, or consume battery; an ambient sensor can create privacy or false-presence concerns. Provide a spoken/LED fallback, conservative duty-cycle limits, a user-disable control, and make mute state fail-closed on boot or firmware fault.
- cost: Approximately $1–$4 BOM increase per unit and a few mA only during short vibration events; negligible idle draw if the sensor is duty-cycled.  ·  latency: Under 100 ms from a relay nudge to a tactile pattern once the link is alive; no effect on speech latency.
- security: The actuator conveys only a local event class, never meeting content. Sensor readings should remain local and expose only coarse state; do not upload raw proximity/light data.
- depends on: Production pendant industrial-design revision; Local privacy/mute state machine; Attention-event severity taxonomy and delivery receipts


## What it asked for

_Nothing._
