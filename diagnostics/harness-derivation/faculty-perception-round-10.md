# Harness derivation — faculty-perception — round 10

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **device availability** — At this observation, home-macbook-bridge is online (last seen 2026-08-07T09:29:33.847Z), while home-chrome is offline with 0 tabs; cloudflare-contract-test is offline.
  - evidence: devices discovery response
- **mac agent health** — Mac local agent health endpoint responds HTTP 200, service AI Pendant Mac Local Agent, version 0.5.0.
  - evidence: GET /health returned {ok:true,status:200,version:0.5.0}
- **pendant audio prototype** — Pendant prototype captures I2S at 15,625 Hz and encodes uplink at 16 kHz/16 kbps; playback decodes Opus at 24 kHz/60 ms frames then resamples to 31,250 Hz I2S wire clock. Encode ~15 ms and decode ~25.4 ms per call; simultaneous load ~87% of one core.
  - evidence: get_hardware_spec(audio)
- **audio bridge constraint** — ESP32 bridge resamples 31,250 to 44,100 Hz and A2DP source is SBC-only, hard-locked to 44.1 kHz stereo; a 44 kB buffer previously starved Bluetooth into silence.
  - evidence: get_hardware_spec(bridge)

## Capabilities it proposed

### "“Before you start, tell me what you can actually reach right now—and if something is unavailable, keep trying and tell me when it comes back.”"
- **useful because:** Today a healthy Mac bridge can coexist with an offline browser extension and unknown pendant state. The owner needs an honest, current reachability answer before relying on private-site actions or live audio, plus recovery notification instead of silent failure.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for periodic probes and state reconciliation; realtime only to answer the owner's immediate spoken question
- **latency:** Spoken readiness answer within 1–2 seconds from cached signed snapshot; probes refresh asynchronously every 15–30 seconds and on link events
- **cost:** About $0.001–$0.01 per refresh if model summarization is needed; ideally zero model calls for typed status aggregation. Main cost is heartbeat traffic and dashboard storage.
- **security:** Do not expose tokens, private URLs, or account contents in the snapshot. Report capability classes (browser session present, accessibility grant, screen recording grant), timestamps, and unknown states. Require confirmation before using a recovered browser session for irreversible actions.
- **missing:** A typed cross-surface readiness schema with per-surface heartbeat, capability, timestamp, confidence, and stale threshold; Pendant/relay health and audio-path telemetry (including sequence/packet loss and negotiated sample rates); Mac bridge endpoint that reports Accessibility and Screen Recording grants; Browser extension heartbeat with session/tab counts and queued-command state; A relay-to-pendant recovery event and owner notification policy

### "“Remember this moment, and later show me the exact evidence and context you attached to it.”"
- **useful because:** A wearable can notice the owner's intent at the moment it happens, but today it cannot reliably turn that moment into a provenance-preserving item that the Mac and authenticated browser can enrich later. The owner should get a reviewable memory with the spoken cue, precise device time, nearby audio-derived keywords, and linked calendar/document context—without continuously recording them.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the brief spoken cue; background model for transcription, entity linking, and context enrichment after capture
- **latency:** Pendant acknowledgment under 300 ms; initial receipt within 5 seconds; enrichment can complete asynchronously within 1–3 minutes
- **cost:** Roughly $0.005–$0.03 per captured moment, dominated by transcription and background context extraction; storage is small if raw audio is discarded after a short verification window
- **security:** Capture must be explicit (spoken phrase or button gesture), show a local acknowledgment, and default to deleting raw audio after transcription. Browser enrichment must use the existing logged-in session only for the selected task, redact secrets from the receipt, and require confirmation before attaching or sharing anything externally. Every attached fact needs source URL/document, timestamp, and confidence.
- **missing:** A pendant-local capture marker that survives a dropped connection and assigns a monotonic event ID; Relay protocol for encrypted, ordered event handoff with deduplication and expiry; Mac service that correlates the event with calendar, files, and active project context without uploading unrelated content; Browser adapter that can enrich only an explicitly selected authenticated page/session; A provenance receipt UI and retention controls covering transcript, links, and deletion


## Changes it proposed to its own stack

### `integration` — Add an end-to-end audio canary protocol: relay emits a tagged, inaudible-or-briefly-muted Opus test frame; pendant and ESP32 attach sequence, negotiated-rate, decode-time, underrun, resampler, and Bluetooth-queue counters; the relay stores a compact signed receipt and marks each segment (uplink, downlink, I2S, A2DP) pass/fail. Run only on explicit owner request or after reconnect, never continuously during conversation.
- **owner gets:** The owner can ask whether the pendant audio is really working and get a segment-specific answer instead of “connected.” It catches the current 16/24/31.25/44.1-kHz boundary and buffer-starvation failures before they interrupt a call.
- effort: Firmware packet metadata and counters, ESP32 bridge diagnostics, relay receipt aggregation, and a small dashboard/voice formatter; requires a controlled test mode and acceptance fixtures for packet-loss, drift, and Bluetooth silence.  ·  risk: A test frame could be audible or compete with live playback; gate it behind explicit request, duck/stop playback briefly, and restore state on timeout. Counter schemas must be versioned across firmware updates. If headphones do not expose loopback, report that A2DP delivery was queued—not that the ear heard it.
- cost: Negligible runtime/API cost outside explicit tests; roughly 1–3 kB persistent counters and under 2 kB transient firmware state. No new hardware required for transport-level proof; a test fixture or microphone loopback is needed for true acoustic acceptance.  ·  latency: A transport canary can complete in <500 ms; acoustic fixture validation takes 1–2 seconds and briefly interrupts playback.
- security: Payload contains no owner speech; use random challenge IDs and authenticated receipts to prevent stale/forged pass reports. Never upload raw audio for the canary.
- depends on: A typed audio telemetry schema on pendant and bridge; Relay endpoint to request/correlate canary IDs; A user-visible readiness/status surface

### `hardware` — Add a low-power haptic actuator and a small nonvolatile event queue (for example,  ferroelectric RAM or wear-leveled external flash) to the wearable product, with a monotonic clock checkpoint and hardware event counter. A short vibration confirms an explicit “remember this moment” marker offline; the event ID and timestamp survive power loss and are reconciled by the relay when connectivity returns.
- **owner gets:** The owner gets trustworthy confirmation that a moment was captured even when the phone, Mac, browser, or cellular link is unavailable. They no longer have to wonder whether a spoken note was lost while moving between rooms or networks.
- effort: Product-board redesign, haptic driver and enclosure/acoustic review, firmware queue/reconciliation protocol, and privacy/retention controls. The current development kit is provisional, so this should be designed into the wearable rather than retrofitted around it.  ·  risk: Vibration can be missed or annoying; make intensity and confirmation behavior configurable. Persistent markers could outlive the owner's intended retention period; encrypt them, cap the queue, and provide a long-press purge. Added hardware may affect RF layout and battery life; validate before committing to a board spin.
- cost: Approximately $2–$8 BOM increase depending on actuator, memory, and assembly; roughly 5–20 mW during a brief haptic pulse and negligible standby draw with FRAM. No per-invocation API cost.  ·  latency: Offline acknowledgment is effectively immediate; reconnect synchronization adds no foreground delay and can happen in the background.
- security: Store only opaque event IDs, timestamps, and encrypted short metadata locally—not raw speech. Bind reconciliation receipts to device keys so a replayed marker cannot create duplicate memories.
- depends on: The explicit moment-capture capability and its event-ID protocol; A product wearable board replacing the current nRF9160 development kit; Relay-side encrypted queue reconciliation and owner-controlled retention


## What it asked for

_Nothing._
