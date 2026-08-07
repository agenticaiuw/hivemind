# Harness derivation — mac-planner — round 37

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac readiness and audio baseline** — Mac local agent is online v0.5.0 with FULL_CONTROL_MODE and relay reachable, but readiness is false because Accessibility is not trusted and Screen Recording is missing; Chrome extension is offline with two pending commands. Audio baseline is 15,625 Hz I2S capture, 16 kHz/16 kbps Opus uplink, 24 kHz Opus decode, 31,250 Hz I2S wire clock, and ESP32 44.1 kHz SBC Bluetooth output.
  - evidence: GET /ops/status and describe(audio), describe(bridge) on 2026-08-07

## Capabilities it proposed

### "“Give me a protected 45 minutes.”"
- **useful because:** Today the owner has to configure Focus, silence the pendant, and manage browser notifications separately—and urgent interruptions may still arrive through another surface. This would create one temporary, spoken-controlled interruption boundary across the wearable, Mac, authenticated browser, and always-awake relay, then restore the prior state and deliver only the items that arrived during the boundary.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only to understand the short spoken command and acknowledge it. Use deterministic routines and a cheaper background model to classify queued notifications and produce the end summary; do not spend realtime turns on the timer or state restoration.
- **latency:** Acknowledge and apply the local pendant/Mac state in under 2 seconds. Relay buffering is immediate; restoration and the short digest should complete within 30 seconds of expiry or an explicit “I'm back.”
- **cost:** Low API cost: one short realtime turn plus an occasional inexpensive digest classification. The dominant cost is implementation and reliable platform notification APIs, not inference.
- **security:** The relay must buffer metadata and notification bodies only under an explicit per-source policy; private browser content should remain on the Mac/browser and be summarized there. Never suppress safety-critical alerts, calls from an owner-selected allowlist, or a pending destructive-action confirmation. Restore exact previous Focus, volume, browser notification, and pendant modes even after a crash, with an auditable state receipt.
- **missing:** A cross-surface interruption lease with an expiry, owner-selected exceptions, and crash-safe restoration; Pendant firmware support for a temporary quiet mode plus a distinct expiry/urgent-alert indication; Mac integration for saving/restoring Focus, notification, and audio state without relying on cursor focus; Browser-extension support to pause nonessential web notifications and report deferred events by source; Relay notification buffering and a local-first privacy filter so browser bodies do not leave the Mac by default; A small dashboard control showing the active lease, exceptions, deferred count, and one-tap early release

### "“I lost the pendant—protect everything and help me get back in.”"
- **useful because:** A disconnected wearable currently looks like a transport failure, not a security or continuity event. This would let the relay detect an unexpected loss, have the Mac/browser protect authenticated sessions and preserve resumable work, then guide the owner through re-pairing and restore only after the physical device is verified.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic relay/device state handling for loss detection, lock/quarantine, pairing, and restoration. Use a cheap background model only to turn the recovery event into a concise owner-facing checklist; reserve realtime for the owner's spoken recovery questions.
- **latency:** Trigger quarantine after a configurable grace period (for example 30–120 seconds) to avoid false alarms, then apply Mac/browser protections within 5 seconds. Re-pairing guidance should be spoken in under 2 seconds per step.
- **cost:** Very low inference cost; mostly local state transitions and cryptographic pairing. Storage is a small encrypted recovery journal and action receipts.
- **security:** Do not transmit secrets or browser contents to the relay. On loss, revoke the pendant session key, pause queued browser mutations, lock or close only explicitly selected sensitive surfaces, and preserve drafts locally. Recovery must require a new physical pairing gesture plus a Mac-local confirmation; never allow voice alone to restore authenticated sessions. A false trigger should be reversible after the grace period.
- **missing:** A cryptographic pendant presence/lease protocol with revocation and replay-resistant re-pairing; A Mac/browser quarantine policy that can suspend authenticated tabs and queued mutations while preserving drafts; A durable, encrypted recovery journal shared by relay and Mac, with no secret payloads in the relay; Pendant firmware feedback for lost-link, quarantined, and successfully re-paired states; A dashboard recovery view showing exactly what was paused, closed, or preserved and how to restore it


## Changes it proposed to its own stack

### `integration` — Add a readiness-aware cross-surface handoff protocol for long-running jobs. Before the relay claims a pendant request can continue, it polls the Mac ops snapshot and browser heartbeat, records a capability vector (relay reachable, Mac bridge online, Accessibility/Screen Recording readiness, browser session online, pending command count), and persists the job at a resumable boundary. When a blocked prerequisite returns, the Mac resumes idempotently; the pendant receives one concise state transition (queued, blocked-with-exact-fix, resumed, completed) and a receipt. A missing permission or offline browser must never be reported as a generic failure. Include expiry and duplicate-command suppression keyed by job ID.
- **owner gets:** A spoken request made away from the desk will not silently fail when the browser is offline or Mac automation is not ready. The owner gets a useful explanation in one sentence and the work picks up automatically when the Mac/browser returns, instead of having to remember and repeat it.
- effort: Medium: relay job state machine plus Mac /ops and browser heartbeat adapter, resumable action boundaries, and pendant status events; test crash/reconnect and duplicate delivery.  ·  risk: A resumed job could repeat a mutation if an action receipt was lost. Require idempotency keys and reconcile the Mac job receipt before retrying; expire stale jobs rather than guessing. Permission diagnostics reveal local state only to the paired relay.
- cost: Small D1 storage and heartbeat overhead; one cheap status poll per queued job transition. No extra realtime-model turn for routine state updates; use templates, escalating to the expensive model only for ambiguous recovery.  ·  latency: Adds a sub-second readiness check before execution; reconnect completion is event-driven rather than polling-heavy.
- security: Keep browser URLs/content out of readiness events; transmit only booleans, job IDs, and redacted error classes. Preserve the owner's existing policy that destructive actions require confirmation, while allowing resumption of already-authorized reversible steps.
- depends on: A durable job record with action-level receipts and idempotency keys; Relay-to-Mac authenticated ops/heartbeat access; Browser extension reconnect and command result events

### `firmware` — Add an end-to-end audio capability/clock handshake and conformance telemetry rather than treating '24 kHz' as a compile-time claim. On session start, pendant, relay, Mac TTS, and ESP32 bridge exchange capture/playback sample rate, Opus frame duration, bitrate, resampler ratio, and measured decode/queue headroom; reject or explicitly label any leg that falls back to narrowband. Emit compact sequence-numbered audio receipts (source rate, delivered rate, underruns, PLC frames, end-to-end latency percentiles) into the existing pipeline trace, with a developer test mode that plays a swept-tone fixture and verifies 24 kHz content survives the 31.25 kHz I2S wire clock and 44.1 kHz A2DP conversion.
- **owner gets:** The owner will know whether the pendant is genuinely delivering the promised superwideband speech or merely saying '24 kHz' while the microphone/uplink remains 16 kHz. When quality drops, the system can identify whether LTE, Opus decode, I2S clocking, or Bluetooth conversion is responsible instead of making the owner debug silence or distorted audio.
- effort: Medium-high: firmware session metadata and counters, relay negotiation fields, Mac TTS metadata, ESP32 bridge telemetry uplink, and an automated fixture test. Keep telemetry sampled and bounded so it cannot starve the audio loop.  ·  risk: Extra instrumentation can consume RAM/CPU and leak timing metadata. Use fixed-size counters, no raw audio in telemetry, compile-time test instrumentation, and rate-limit reports. If negotiation fails, use the existing known-good mode rather than dropping the conversation.
- cost: Negligible API cost for structured telemetry; modest firmware/bridge engineering. Runtime RAM target under 8 kB and CPU under 1% outside audio decode; no hardware purchase required initially.  ·  latency: One short capability exchange at session start; no per-frame model latency. Counters are asynchronous.
- security: Transmit only codec/clock statistics and opaque session IDs; never transmit microphone samples through the diagnostics path. Pairing/authentication remains required.
- depends on: A shared audio capability schema across pendant, relay, Mac TTS, and ESP32 bridge; Pipeline trace storage and a small local/CI audio fixture; A documented policy for whether uplink must also be 24 kHz or only playback


## What it asked for

### `c10-uhf4` (context) — audio superwideband acceptance target
- why: The owner memory says ship a 24 kHz superwideband audio path, but the live hardware baseline captures at 15,625 Hz and uplinks 16 kHz Opus while only playback decode is 24 kHz. I need the intended acceptance boundary to avoid proposing the wrong migration.
- would change: If playback-only is acceptable, I will prioritize clock/codec verification and latency. If true end-to-end wideband capture is required, I will propose the microphone/I2S and LTE uplink changes, including power and bandwidth impact, rather than claiming the current path is superwideband.

## Its own summary

Discovered the live Mac/relay state and recorded the important baseline: relay and bridge are online, but Mac readiness is false because Accessibility is untrusted and Screen Recording is missing; Chrome is offline with two queued commands. The current audio chain is 15.625 kHz capture → 16 kHz Opus uplink, 24 kHz decode → 31.25 kHz I2S → 44.1 kHz SBC Bluetooth, so playback is 24 kHz but the path is not yet true end-to-end superwideband. I proposed (1) readiness-aware, resumable pendant→relay→Mac/browser job handoff with idempotent receipts and useful blocked-state speech, and (2) an end-to-end audio capability/clock handshake plus bounded conformance telemetry to prove where quality is lost.

**Biggest unknown:** The acceptance target for “24 kHz superwideband” is still unclear: playback-only versus 24 kHz capture and uplink too. I also still need the owner/Mac to restore Accessibility and Screen Recording, and the browser extension to reconnect, before desktop/browser execution can be honestly tested.

