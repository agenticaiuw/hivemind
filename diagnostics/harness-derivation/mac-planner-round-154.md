# Harness derivation — mac-planner — round 154

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Test my pendant’s 24 kHz audio path now and tell me whether the microphone, Opus, LTE/WebSocket simulation, ESP32 bridge, and headphones each pass.”"
- **useful because:** The owner can verify the complete wearable audio chain on the hardware actually attached today instead of guessing from logs; failures are localized to a cable, codec, modem simulation, or Bluetooth bridge with a short spoken result.
- **path:** mac-planner → mac-terminal → relay-realtime → pendant → browser-extension
- **model tier:** background for serial parsing and waveform comparison; realtime only for the final spoken verdict
- **latency:** Under 90 seconds for a bounded fixture; final verdict under 2 seconds after measurements
- **cost:** <$0.03 per run; dominated by one short analysis call, with serial capture and signal metrics local
- **security:** Audio fixture should be synthetic or a 3-second local test tone; never upload raw microphone audio. Running firmware test commands needs explicit test mode and should not alter user files.
- **missing:** A Mac serial-fixture runner that can address /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A deterministic test-tone/loopback command in both firmwares; A relay-side packet-loss and Opus-quality report schema; A headphone loopback or user-confirmed audible checkpoint

### "“When I unplug or reconnect my pendant, preserve what I was doing and give me a one-sentence resume brief.”"
- **useful because:** A dropped LTE call or USB move should not erase the owner’s task: the worn device, Mac, browser sessions, and always-on relay together can checkpoint the active work and resume it at the next physical connection.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** background model for checkpoint compression and resume ranking; realtime only to speak the resume sentence
- **latency:** Checkpoint within 3 seconds of disconnect; resume brief within 5 seconds of reconnect
- **cost:** <$0.01 per disconnect/reconnect; mostly local event handling, with a small context summarization call
- **security:** Checkpoint must redact page bodies, secrets, and private audio by default, retaining task IDs, URLs, titles, and pending action state. Never replay browser commands merely because a device returned.
- **missing:** A USB serial presence watcher on the Mac; A signed reconnect/session identity shared by pendant and relay; A resumable task capsule persisted with TTL and redaction policy; Browser session/tab checkpoint hooks and a Mac foreground-task snapshot

### "“Prepare this browser action, show me the exact before/after, and let me approve it with the pendant’s physical button.”"
- **useful because:** The owner gets a genuinely wearable approval step: Safari can hold authenticated state, the Mac can gather evidence and fill reversible fields, and a deliberate button press can authorize the final send without requiring the owner to return to the keyboard.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** realtime for the short approval prompt and spoken summary; background for evidence collation and draft preparation
- **latency:** Draft in 10 seconds; evidence view in 2 seconds; button approval acknowledged in under 1 second
- **cost:** $0.02–$0.08 per transaction; dominated by evidence extraction and final spoken summary
- **security:** Bind approval to a single nonce, tab/session, exact URL, and hash of all outgoing fields; expire quickly and reject if any field changes. Sending, deleting, purchasing, or submitting remains explicitly confirm-only.
- **missing:** Pendant button event transport over the current USB/LTE path; A cryptographic approval nonce verifier in relay and Mac browser bridge; A compact before/after evidence renderer suitable for spoken plus browser display; A final-submit command that accepts only the verified nonce

### "“If my pendant leaves the Mac, seal my private work session; when it returns, restore only the safe parts and tell me what was held.”"
- **useful because:** The pendant becomes a physical custody signal: walking away can stop live audio and hide authenticated pages without relying on the owner to remember a shortcut, while reconnecting restores continuity without replaying actions.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** deterministic local rules for seal/restore; background model only to summarize held work
- **latency:** Seal within 2 seconds of serial disconnect; safe-state report within 5 seconds of reconnect
- **cost:** <$0.005 per event; local automation dominates, with optional small summarization
- **security:** Disconnect must never delete or submit anything. Seal actions should be limited to locking/obscuring windows, pausing audio, and revoking browser command leases; restore requires a fresh physical reconnect nonce and must not expose page bodies in speech.
- **missing:** A signed USB serial presence and reconnect nonce; Mac seal/restore primitives for Safari windows and audio pipeline; Browser command-lease revocation plus safe tab parking; A user-configurable allowlist of apps/tabs allowed to remain visible

### "“Keep my conversation alive when I move from USB to LTE: switch paths without making me repeat myself or losing the sentence.”"
- **useful because:** The owner gets one wearable conversation instead of two brittle modes. While attached to the Mac, audio can use the low-latency local path; when they walk away, the relay migrates to LTE with buffered, ordered audio and no manual reconnect.
- **path:** pendant → mac-planner → relay-realtime → browser-extension
- **model tier:** realtime for the conversation; deterministic media-session logic for migration, with no extra model call
- **latency:** Path switch in under 500 ms locally and under 2 seconds to LTE; no more than one duplicated or missing 60 ms frame
- **cost:** Small incremental realtime cost; local USB traffic is effectively free, LTE bandwidth and relay WebSocket time dominate
- **security:** Authenticate both transports to the same session and prevent a nearby USB device from hijacking it. Do not persist raw audio; retain only short encrypted jitter buffers until migration completes.
- **missing:** A local USB audio/control transport between the Mac and pendant; Relay session migration with sequence numbers, deduplication, and bounded jitter buffering; A device-bound session credential shared across USB and LTE; Firmware support for transport handoff without resetting the Opus decoder

### "“After my Mac restarts, put me back into the exact work setup I chose—apps, safe browser tabs, files, and the pending task—without sending anything or replaying destructive actions.”"
- **useful because:** A reboot should cost seconds, not reconstruction. The pendant’s presence can identify the owner’s intended workspace while the relay preserves the manifest and the Mac/browser restore only safe, declared state.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** background model only to summarize the pending task; deterministic manifest restore for apps, files, and tabs
- **latency:** Detect readiness within 10 seconds of login; restore the workspace within 30 seconds
- **cost:** <$0.01 per restore; local app/tab launches dominate, with optional task-summary inference
- **security:** Never restore private tabs on an untrusted device or replay queued form submissions. Encrypt manifests, expire them, and require a fresh pendant presence nonce for sensitive workspace entries.
- **missing:** A user-authored workspace manifest with safe/unsafe item classes; Mac login/startup restore coordinator; Browser tab restoration that verifies URL/session before opening; Relay persistence for the pending-task manifest and restore receipts

### "“When I say ‘make this accessible later,’ turn the current browser page and Mac document into a durable, private brief I can navigate by voice from the pendant.”"
- **useful because:** The owner can convert a fleeting authenticated page into a compact voice-addressable artifact: the browser supplies private source material, the Mac stores a local copy and citations, and the pendant later answers navigation questions without reopening a fragile tab.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** background model for extraction, chunking, and citation; realtime only for later voice navigation
- **latency:** Capture and index in under 20 seconds; voice lookup response under 2 seconds
- **cost:** $0.02–$0.10 per captured page depending on length; embedding/summarization dominates
- **security:** Default to local encrypted storage, redact credentials and hidden fields, preserve source URL and timestamp, and let the owner delete the artifact. Never treat the snapshot as permission to submit changes.
- **missing:** A consented page/document capture command spanning browser and Mac; Encrypted local artifact store with TTL and deletion; Citation-preserving chunk/index service; Pendant voice navigation protocol for selecting a source and section


## Changes it proposed to its own stack

### `integration` — Add a Mac USB-device event daemon that recognizes the nRF9160 and ESP32 by stable serial identity, emits signed connect/disconnect events to the relay, and exposes a short-lived device lease consumed by browser and audio jobs. Include a local fixture mode so the owner can test it with the boards attached now.
- **owner gets:** The owner gets reliable physical-state behavior: the system knows whether the wearable and audio bridge are actually present instead of claiming a stale online state, and can immediately explain or recover from a cable/device failure.
- effort: Medium: launchd daemon plus serial identity enrollment, event signing, relay endpoint, and tests for unplug/replug races.  ·  risk: False disconnects could pause a call or seal a session; debounce for 2–3 seconds and make recovery idempotent. If the daemon fails, existing manual operation continues.
- cost: Negligible runtime/API cost; small local daemon and one relay event per state transition.  ·  latency: Adds under 2 seconds to presence-triggered behavior; no impact on normal voice packets.
- security: Device identity becomes a local bearer for presence, so use per-device keys and never treat presence alone as authorization for destructive actions.
- depends on: Stable serial identifiers for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A relay endpoint for signed device-presence events; Browser/audio jobs consuming lease state


## What it asked for

_Nothing._
