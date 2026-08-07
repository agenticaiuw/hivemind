# Harness derivation — faculty-perception — round 115

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac control truth** — At 2026-08-07T17:43Z the Mac bridge and browser extension are online, but AI Pendant Agent Accessibility and Screen Recording are both untrusted; observe reports synthesized UI input is not accepted and ui_actions_will_reach_the_screen=false. Automation grants are present.
  - evidence: GET /ops/status and GET /observe
- **live browser truth** — Safari bridge is online with 3 durable sessions/tabs, including a Gmail inbox session; the extension's current foreground tab is https://example.com titled 'Failed to open page', with zero pending commands.
  - evidence: GET /browser/status, GET /observe, GET /ops/status
- **live relay/device truth** — Relay is reachable and mac bridge online, but no pendant is registered/live; device discovery lists only home-macbook-bridge online and cloudflare-contract-test offline. Pipeline data includes historical nrf9160 records and must not be treated as current hardware telemetry.
  - evidence: devices discovery plus GET /ops/status and GET /pipeline
- **current routing economics** — Routing has 9 recent requests: 44% off planner, but planner requests average ~9,001 prompt tokens and ~3.1s; deterministic exact briefing matching avoids model calls. A reality check should be deterministic/cheap before planner escalation.
  - evidence: GET /routing

## Capabilities it proposed

### "Before you do anything, tell me what is actually reachable right now, what is blocked, and which parts of my request can safely be completed without pretending an action happened."
- **useful because:** This is the system's most important trust primitive: it prevents false success when a browser tab is broken, the Mac cannot inject input, or a pendant is absent, while still offering the reversible portions that really work.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** deterministic first using live status; background model only to phrase a concise explanation; realtime only for spoken delivery
- **latency:** under 1 second for status collection, under 2 seconds for wording
- **cost:** near-zero for deterministic status aggregation; at most a small gpt-4.1-mini call when natural-language explanation is needed; dominated by no model call in the common case
- **security:** Must expose capability state without leaking page contents; never infer a pendant is present from historical pipeline rows. Require confirmation before any fallback action or browser mutation.
- **missing:** A relay-side live device registry endpoint exposed to the unified planner with delivery freshness and explicit stale-vs-historical labels; A typed capability snapshot schema shared by relay, Mac, and browser; A planner gate that consumes the snapshot before claiming completion

### "Why didn't that work? Trace my last request across the pendant, relay, Mac, browser, and action receipt, distinguish queued, blocked, executed, and merely reported success, and tell me the next safe option."
- **useful because:** Today a receipt can say success even when UI input was discarded, while pipeline history can look live after the device disappeared. A causal trace would let the owner recover instead of repeating a request or trusting a phantom completion.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → mac-terminal → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** deterministic event correlation first; background model summarizes the causal chain; realtime speaks only the final short diagnosis
- **latency:** 2 seconds for recent jobs; up to 8 seconds for a deep historical trace
- **cost:** usually no model cost for event classification; one small background call for ambiguous traces; storage/query work dominates
- **security:** Show only the owner's own job/page metadata and redact page contents and tokens. Never retry an irreversible action automatically; surface stale or unverified receipts explicitly.
- **missing:** A cross-surface correlation ID propagated into browser commands, Mac action receipts, relay jobs, and pendant acknowledgements; A receipt verifier that consults /observe and browser result state instead of trusting action success alone; A unified trace endpoint with bounded retention

### "When I am interrupted, use where I am and what I am doing to decide whether to speak now, hold it, or give me a one-line heads-up—and let me retrieve everything held later."
- **useful because:** A wearable assistant should not blurt a long answer while the owner is in a call or typing sensitive information. Combining the pendant event, relay reachability, foreground Mac app, browser session, and pending work makes interruption behavior genuinely personal rather than a timer.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** deterministic interruption policy from foreground app, secure-input, device link, and urgency; background model compresses held content; realtime handles only an immediate one-line alert
- **latency:** under 300 ms to choose speak/hold; under 2 seconds to produce a short heads-up
- **cost:** near-zero for policy; occasional low-cost background summarization for held items; realtime cost only when the owner actually requests speech
- **security:** Sensitive foreground apps and authenticated tab URLs must be represented as coarse categories, not content. Holding private alerts requires encrypted relay storage and explicit owner retrieval; never read a page aloud without an owner-triggered request.
- **missing:** A pendant event/ack protocol that can carry urgency and hold state when offline; A privacy-preserving foreground-context classifier on the Mac; A durable held-item queue shared by relay and pendant with acknowledgement and expiry semantics; A policy surface for owner-defined quiet contexts

### "Pair the pendant and audio bridge over this Mac, run one spoken round trip, and tell me separately whether USB, relay delivery, speech, and playback each passed—without calling it LTE-connected."
- **useful because:** The hardware is physically testable now even though it has never registered with LTE. A staged round-trip test turns two inert serial devices into an evidence-backed check of the exact link that exists today and pinpoints the first failing layer.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** deterministic protocol test and telemetry verdicts; background model only converts failures into owner-friendly next steps; realtime is used for the actual low-latency spoken sample
- **latency:** 30 seconds end-to-end including serial enumeration and a short audio sample
- **cost:** No planner cost for the test; one realtime utterance and tiny telemetry payload; dominated by the audio sample and relay transfer
- **security:** Require a physical button or explicit Mac confirmation to start microphone/playback capture. Use a nonce-bound test session, retain only pass/fail and hashes by default, and clearly distinguish USB-local from LTE.
- **missing:** USB serial enrollment/identity protocol; Mac serial watcher and firmware flasher-free test harness; Relay route for USB-local device leases and per-stage acknowledgements; A playback completion signal from the ESP32 bridge

### "Treat a spoken command as mine only when the pendant's physical interaction, my voice, and the currently paired Mac agree; otherwise ask me to confirm instead of acting."
- **useful because:** A wearable that can reach private browser sessions and control a computer needs protection from a television, another speaker, or an accidental hot-mic transcript. This gives the owner hands-free convenience without making every command an unconditional remote-control credential.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** small deterministic classifier for button/nonce/device pairing and coarse voice-liveness; realtime model transcribes the utterance; planner is invoked only after the trust gate passes and the requested action is otherwise ambiguous
- **latency:** under 500 ms for local trust decision; under 2 seconds for a spoken confirmation when confidence is insufficient
- **cost:** No model cost for physical-pairing and nonce checks; one realtime turn for speech already being processed; optional low-cost liveness model, with storage and secure-key management dominating engineering cost
- **security:** This must not claim biometric identity from voice alone. Keep voiceprints, if enabled, on-device and opt-in; default to ephemeral liveness features. Bind each command to a short-lived device nonce and Mac session, expire it on disconnect, redact audio after verification, and always require explicit confirmation for irreversible actions.
- **missing:** Firmware support for a physical-button/gesture nonce and signed challenge response; A relay-issued short-lived command-attestation protocol binding pendant, Mac bridge, and browser session; An on-device or local-Mac voice-liveness implementation that does not upload a persistent voiceprint; Planner/action gates that consume attestation state and downgrade to confirmation instead of executing


## Changes it proposed to its own stack

### `integration` — Add a local USB-device truth and enrollment bridge: watch /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, identify nRF9160 and ESP32 firmware versions, issue a signed local presence nonce, and forward only explicit device telemetry to the relay. The relay must label this as USB-local (not LTE-registered), maintain last local ACK, and refuse to present historical nrf9160 pipeline rows as current presence.
- **owner gets:** The owner can test the worn hardware today while it is attached to the Mac and receive an honest end-to-end answer, instead of waiting for LTE registration or being told that old telemetry means the pendant is alive.
- effort: medium: Mac serial watcher and protocol adapter, relay presence schema, firmware hello/nonce response, dashboard status card, and an audio loopback test.  ·  risk: Malformed serial frames or a stale USB process could create false presence; require signed nonce plus short TTL and show 'USB attached, relay-unregistered' distinctly. Recovery is to drop the local lease and revert to no-device state.
- cost: No per-request model cost; modest Mac CPU and serial I/O, negligible power beyond existing USB devices; engineering cost is protocol and firmware work.  ·  latency: Presence under 1 s locally, relay update within network RTT; no impact on realtime path.
- security: Device identity must be authenticated with a firmware key; never upload raw microphone/audio by default, only health metadata and explicit test payloads.
- depends on: Firmware hello/nonce command in both chips; Mac serial permission and device watcher; Relay device registry accepting USB-local leases; An explicit owner-started end-to-end audio test


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: Mac bridge and Safari extension are online; Gmail durable session exists, but current extension tab is a failed example.com page. Accessibility and Screen Recording remain false, and /observe explicitly says UI actions can report success while doing nothing. Relay is reachable but no pendant is registered; nrf9160 pipeline entries are historical. Routing currently averages ~9k planner prompt tokens and ~3.1s, so deterministic preflight is important. Recorded four findings, proposed three cross-surface capabilities (truthful preflight, causal failure trace, interruption policy), a USB-local hardware enrollment/audio-loopback integration, and a staged spoken round-trip capability. Informed judgement/action/unified peers.

**Biggest unknown:** The exact serial protocol and firmware capabilities of the physically USB-attached nRF9160 and ESP32, plus the relay's authoritative device-registry/ack contract needed to implement USB-local presence and end-to-end audio verification.

