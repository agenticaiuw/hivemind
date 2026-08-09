# Harness derivation — mac-terminal — round 239

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make the pendant audio path pass an end-to-end 24 kHz test, and tell me exactly where it fails if it doesn’t.”"
- **useful because:** The owner’s stated priority is shipping the 24 kHz superwideband path. This would turn separate firmware, ESP32 bridge, relay transcoding, and playback into one observable acceptance test instead of guessing from logs. It can run on the two USB-attached boards today, while clearly distinguishing bench USB success from LTE wearable readiness.
- **path:** mac-terminal → relay-realtime → unified → faculty-perception
- **model tier:** Use a cheap background model for test orchestration and log comparison; use realtime only to explain the final spoken result.
- **latency:** 10–30 seconds for a bounded capture/playback round; under 2 seconds for the final spoken verdict after logs arrive.
- **cost:** Usually <$0.03 in model/API cost; dominated by local serial capture and audio test duration, not tokens.
- **security:** Only local UART diagnostics and synthetic audio should leave the Mac; no microphone recording and no authenticated browser data. Require explicit opt-in before playing test audio aloud; never claim LTE coverage from a USB result.
- **missing:** A real, resolved bounded serial-reader action (the currently granted mac_usb_serial_diagnostics schema is unresolved in the live inventory) or a typed wrapper around the existing dual_chip_autocapture.sh script.; A deterministic 24 kHz test vector and loopback marker understood by nRF9160, ESP32, and relay.; A receipt that records sample rate, frame duration, encode/decode CPU time, packet loss/PLC count, and final playback checksum.

### "“Is the system wearable right now? Give me one honest score for the pendant, audio bridge, relay, and Mac, and name the weakest link.”"
- **useful because:** The owner currently has several partial health signals but no single answer that distinguishes ‘works on USB bench’ from ‘works as a wearable’. A cross-node readiness verdict prevents false confidence before leaving the desk and tells them whether to fix radio, audio, relay, or host state.
- **path:** relay-realtime → mac-terminal → unified → faculty-perception → mac-planner
- **model tier:** Background model aggregates bounded health telemetry; realtime model speaks only the concise verdict when requested.
- **latency:** Under 3 seconds from a voice request; cache passive health for 30 seconds and refresh only stale components.
- **cost:** <$0.01 per request when using cached telemetry; dominated by a few local/relay probes, not generation.
- **security:** Report only coarse health, timestamps, firmware version, link type, and error counters—never credentials, UART payloads, microphone content, or browser data. Explicitly label USB-connected/bench-only state so a healthy Mac bridge cannot imply LTE readiness.
- **missing:** A shared health schema with component, transport (USB/LTE), freshness, confidence, and failure reason.; Pendant and ESP32 health frames surfaced through a real serial action or the existing capture scripts.; A relay endpoint that combines pipeline/audio health with device registration state and expires stale reports.; A small dashboard/voice formatter that uses the weakest-link rule rather than averaging away a hard failure.

### "“When you have a destructive browser action ready—send, delete, or buy—show me exactly what is queued, then let one deliberate press of my pendant approve only that action.”"
- **useful because:** The owner already wants confirmation for destructive work, but a spoken “yes” while walking or while several browser tabs are active is easy to misapply. A physical, single-use approval bound to the exact tab, action hash, and expiry would make confirmations reliable without reducing the system’s maximum-access behavior for ordinary work.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-action
- **model tier:** Use a cheap background model to render the pending action summary and hash; use realtime only to speak the concise summary and receipt.
- **latency:** Under 2 seconds to present the pending action; approval-to-dispatch under 1 second when the pendant link is healthy.
- **cost:** <$0.01 per confirmation; dominated by normal browser dispatch, not model generation.
- **security:** The approval token must be single-use, short-lived, and bound to tab identity, origin, action parameters, and a canonical action hash. A stale tab, changed form value, navigation, or expired token invalidates it. Never expose the confirmation token in spoken audio or page content; preserve a receipt of what was actually approved.
- **missing:** A relay-mediated pendant approval event with a monotonic counter and replay protection.; Browser action previews that expose canonical target, origin, and parameter hash before dispatch.; An execution join that consumes the approval atomically at the browser command boundary and records the resulting receipt.; A clear pendant pattern for ‘approval waiting’ distinct from dispatched/completed/failed status.

### "“Lock down my authenticated browser sessions whenever I walk away, and restore them when I return without losing the task I was doing.”"
- **useful because:** The browser holds sessions that no other node can reach, so an unattended Mac is a uniquely dangerous and useful boundary. Today the system can drive those sessions but has no owner-presence signal or resumable privacy handoff. This would protect logged-in work while preserving the exact tab/task context for the owner’s return.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-perception
- **model tier:** Use local deterministic logic for proximity and tab shielding; use a background model only to summarize the paused task when the owner returns.
- **latency:** Shield within 3 seconds of confirmed departure; restore within 2 seconds of return, with no network round-trip required for the lock.
- **cost:** Near-zero per event; the cost is a small local presence service and browser-extension state machine.
- **security:** Presence must be cryptographically tied to the owner’s pendant, not merely Wi-Fi or an arbitrary Bluetooth device. On departure, revoke extension control and blur/lock sensitive tabs without copying page contents. On return, require a fresh authenticated nonce; never auto-submit forms or replay queued mutations.
- **missing:** A short-range authenticated presence channel (BLE/UWB companion, or a product pendant radio that supports it); LTE alone cannot establish proximity.; A browser extension lock screen that preserves tab IDs and encrypted task metadata while withholding page content.; A Mac local presence daemon that survives relay outages and emits signed arrival/departure events.; A resumable browser task checkpoint with tab lease validation, separate from action replay.


## Changes it proposed to its own stack

### `firmware` — Add a deterministic 24 kHz audio self-test mode that generates a short in-memory multitone/chirp, runs it through the exact Opus encode/decode and 31.25 kHz I2S playback path, and emits a compact CRC plus timing counters over UART. Include a negotiated capability header (capture rate, decode rate, frame duration, bitrate, PLC mode) so the relay and ESP32 can reject mismatched modes instead of silently resampling.
- **owner gets:** The owner gets a trustworthy answer about whether the new superwideband path itself works, without opening the microphone or needing a person to speak. It catches the dangerous case where audio sounds plausible but is actually at the old rate or overrunning the codec budget.
- effort: Medium: firmware test generator/counters, a small UART frame definition, and relay/bridge parsers; no new board required.  ·  risk: The test must never run on the active microphone edge or consume the live reply buffer. Gate it behind a maintenance command and time-limit it; if a frame is malformed, report unknown rather than pass.
- cost: Negligible runtime cost; roughly 1–2 weeks engineering. No per-call API cost; a few hundred bytes of diagnostics per run.  ·  latency: Adds no latency to normal calls. Maintenance test completes in under 5 seconds.
- security: Synthetic audio only; no microphone data or secrets. UART diagnostics should redact identifiers and use a CRC to prevent false parses.
- depends on: A bounded Mac UART capture/command path (existing dual_chip_autocapture.sh can be the interim transport); A shared versioned audio capability header in relay and ESP32 bridge

### `browser-harness` — Make every browser action use an authoritative tab lease: list tabs, bind a lease to tabId plus URL/title/origin hash and extension session generation, then require the lease on snapshot/read/click/type. If the extension returns content from a different tab, discard it, refresh the tab list, and retry once; otherwise return a hard targeting error with both expected and observed tab metadata. Persist the lease and mismatch receipt alongside the browser provenance record.
- **owner gets:** The owner can safely say “read this page” or “fill this form” without the system silently using a different logged-in tab. This fixes a real observed failure where a Dashboard read returned YouTube content, which could otherwise cause wrong answers or wrong authenticated actions.
- effort: Medium: extension response validation, a short-lived lease store, and retry/error plumbing in the Mac agent; no model training required.  ·  risk: A tab can legitimately navigate during a task, so use an origin-sensitive policy: navigation within the leased tab updates the lease only after a fresh snapshot, while cross-tab content is always rejected. Never auto-retry a click or form submission after a mismatch.
- cost: Small implementation cost and negligible API cost; one extra list/snapshot request only on mismatch.  ·  latency: No added latency on healthy actions; roughly 0.5–2 seconds to recover from a stale target.
- security: Improves security by preventing cross-tab authenticated data leakage and misdirected writes. Store hashes and metadata, not page contents, in the lease.
- depends on: POST /execute; POST /browser/inspect; POST /browser/result/:commandId; GET /browser/provenance; An extension response field containing authoritative tabId and session generation

### `hardware` — Add a low-power UWB presence/ranging companion (or a pendant revision with UWB) with a device-bound key, while retaining LTE-M for wide-area transport. Expose only signed coarse proximity transitions and a monotonic counter to the Mac; never expose raw ranging traces or use LTE cell presence as a substitute.
- **owner gets:** The owner gets a pendant that can tell the Mac ‘the wearer is here’ versus ‘the Mac is unattended’ reliably enough to protect authenticated work and to bind a physical approval to the person holding the device. It also makes return-to-task behavior dependable when Wi-Fi and LTE are unavailable.
- effort: High: new RF module, antenna/layout and power validation, secure pairing UX, Mac companion integration, and regulatory testing.  ·  risk: False departure could interrupt work, so use hysteresis and a grace period; false presence must never authorize a destructive action by itself. Preserve a manual recovery path on the Mac and make the feature opt-in per session.
- cost: Roughly $8–$20 incremental BOM plus antenna/layout work; tens of milliwatts only during short ranging bursts, with deep sleep otherwise. No ongoing API cost.  ·  latency: Presence transitions in roughly 0.5–2 seconds; no impact on normal audio streaming when the ranging radio sleeps.
- security: A secure element or hardware-backed key is required to prevent cloned pendants from approving actions. Ranging data should stay local and be reduced to signed state transitions before any relay upload.
- depends on: A Mac companion daemon and browser extension presence-lock protocol; A one-time approval protocol bound to the pendant’s key; Product pendant enclosure/RF redesign rather than the current development kit


## What it asked for

_Nothing._
## Its own summary

This round produced four non-duplicate proposals: (1) an end-to-end 24 kHz audio acceptance test across nRF9160, ESP32, relay, and Mac; (2) a firmware-only synthetic 24 kHz self-test with capability negotiation, CRC, and timing counters; (3) authoritative browser tab leases that reject stale/wrong-tab reads and writes; and (4) a cross-node “is this wearable right now?” weakest-link health verdict. The most important remaining blocker is concrete bench I/O: mac_usb_serial_diagnostics is still unresolved in the live inventory despite its grant, so the two physically connected boards cannot yet be queried through a typed read-only tool. Interim work must use the existing dual-chip capture shell scripts. The system also still needs LTE registration before any USB result can honestly be called wearable readiness.

**Biggest unknown:** Whether either attached chip is currently emitting valid UART health/audio frames, and whether the relay has any registered wearable transport; the granted serial schema cannot execute, so I cannot establish those facts directly this round.

