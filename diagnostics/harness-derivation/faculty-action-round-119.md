# Harness derivation — faculty-action — round 119

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m holding the pendant—commit the prepared transaction now, but only if I press its button within the next 10 seconds.”"
- **useful because:** Makes an irreversible browser or Mac action require a physical, time-bound presence signal, while still letting the mind prepare everything hands-free. The owner gets a clear spoken before/after summary and the action expires safely if the pendant is absent or the link drops.
- **path:** faculty-judgement → relay-realtime → mac-planner → browser-extension → faculty-action → pendant
- **model tier:** Realtime for the short confirmation exchange; background/local code for expiry, receipt, and delivery.
- **latency:** Prepare in the background; commit within 1 second of the button event; spoken result within 3 seconds.
- **cost:** Low API cost: one realtime turn only when committing; local serial and relay receipt work dominate, not model tokens.
- **security:** The button is a possession factor, not identity proof. Require an explicit transaction digest spoken/displayed before arming, bind the nonce to the exact tab/action, enforce 10-second expiry and idempotency, and never send secrets from the pendant.
- **missing:** pendant button event bridged over USB/LTE; a commit-lease endpoint binding nonce, tab/session, and exact action digest; firmware LED/audio acknowledgement for armed/expired/committed states

### "“I plugged in the pendant—run a safe end-to-end health check and tell me whether the microphone, 24 kHz playback path, ESP32 bridge, and headphones each work.”"
- **useful because:** Turns today’s USB-connected prototype into something the owner can trust before relying on it. One command would exercise the actual serial devices and audio chain, isolate failures, and leave a timestamped report instead of guessing whether silence is caused by codec, I2S, bridge, Bluetooth, or relay.
- **path:** faculty-action → mac-terminal → relay-realtime → pendant → mac-planner
- **model tier:** Cheaper background/local diagnostic logic; realtime only to narrate the concise result if requested.
- **latency:** 15–30 seconds for the full test; immediate progress LED/status is preferable to a silent wait.
- **cost:** Near-zero model cost; serial probes and a short generated test tone are the dominant work.
- **security:** Use a generated tone and synthetic recording only—never upload ambient microphone data. Require explicit opt-in before any cloud echo test; redact serial logs and retain only pass/fail plus firmware/bridge versions.
- **missing:** mac_read_build_and_devices or equivalent USB serial enumeration; audio_path_probe with a synthetic loopback/latency test; a protocol command in both firmwares for deterministic tone, mic loopback, and bridge acknowledgements

### "“If the Mac finishes an action while my pendant is disconnected, save the result and tell me exactly once when I reconnect—without rerunning anything.”"
- **useful because:** Prevents the worst real-world failure mode: the owner cannot tell whether a remote action happened and repeats it. The Mac/relay would escrow a signed receipt while offline, and the pendant would announce the outcome on reconnection with the target, timestamp, and undo option where available.
- **path:** mac-planner → browser-extension → relay-realtime → faculty-action → pendant
- **model tier:** No model for storage/deduplication; cheap background summarization for a short spoken receipt.
- **latency:** Store receipt immediately; deliver within 2 seconds of reconnection; no polling burden on the owner.
- **cost:** Minimal storage and relay invocation cost; one short TTS/realtime turn per queued receipt.
- **security:** Encrypt receipts at rest, retain only action metadata and a redacted summary, bind each receipt to an idempotency key, and require button confirmation before any undo. Never replay page contents or credentials over the audio link.
- **missing:** a durable per-device receipt inbox with exactly-once acknowledgement; USB/LTE reconnect identity and monotonic event cursor; pendant reconnect event plus a small spoken-receipt playback queue

### "“When I’m in the middle of something, protect my attention: pause background work, suppress non-urgent alerts, and bring back only the one item that truly needs me when I’m free.”"
- **useful because:** Today the system can act across the Mac, browser, relay, and pendant, but it cannot coordinate those surfaces around the owner’s changing availability. This would make the wearable an attention boundary rather than another notification stream: a button gesture or spoken state pauses queued browser/Mac work, while the always-awake relay triages urgent exceptions and restores the work at a deliberate moment.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action
- **model tier:** Cheap background classifier/rules for urgency and queue management; realtime only for the owner’s brief state change and urgent announcement.
- **latency:** Pause within 1 second of the pendant event; urgent exception within 2 seconds; resume only on explicit owner release or scheduled window.
- **cost:** Low ongoing cost: event-driven relay state and local queue operations; model calls only for ambiguous urgency classification.
- **security:** Availability state is sensitive behavioral data. Store coarse states with short retention, do not infer from microphone continuously, and require explicit opt-in for calendar/browser-derived urgency. Paused actions must not silently expire into execution.
- **missing:** a shared attention-state protocol across pendant, relay, Mac, and browser; queue pause/resume semantics that preserve idempotency and deadlines; an urgency policy that can distinguish an exception from ordinary notification

### "“Handle this until you hit a decision only I can make; ask me that one question on the pendant, then continue from the exact step without starting over.”"
- **useful because:** Current delegation either finishes a predefined action or leaves the owner to reconstruct a half-completed browser task. This would let the Mac and authenticated browser do long, messy workflows while the pendant becomes a narrow decision channel: the owner answers one constrained question, and the system resumes with the same tab, draft, and evidence instead of repeating or guessing.
- **path:** faculty-judgement → mac-planner → browser-extension → relay-realtime → pendant → faculty-action
- **model tier:** Cheaper background/local planner for deterministic steps and state serialization; realtime only for the short blocking question and answer.
- **latency:** Continue automatically until blocked; deliver a blocking question within 5 seconds; resume within 2 seconds of the answer.
- **cost:** Moderate but bounded: model calls only at step boundaries or ambiguity; browser execution and state snapshots dominate.
- **security:** Never convert an unanswered question into a guess. Persist only redacted form state and a locator/step ID, encrypt private page snapshots, and require explicit confirmation for financial, legal, or outbound communication decisions.
- **missing:** a resumable workflow state machine with durable browser checkpoints; a typed blocking-question protocol with constrained answers and expiry; tab/session reattachment that verifies the page is still the same before resuming


## Changes it proposed to its own stack

### `integration` — Add a cross-surface physical commit lease: faculty-judgement creates a canonical action digest and nonce; relay stores it with a 10-second deadline; the Mac/browser executor refuses any commit without a matching pendant button event, then writes one receipt keyed by the nonce. Expose armed/expired/committed states to the pendant LED/audio adapter.
- **owner gets:** The owner can safely say “commit” without worrying that a stale browser tab, delayed network packet, or duplicate retry will send the wrong thing.
- effort: Medium: relay schema and verification middleware, Mac/browser executor gate, serial event adapter, and end-to-end tests with dropped links.  ·  risk: A lost button event could leave an action uncommitted; recover by explicit expiry speech and a re-arm flow. Never fail open when the lease is ambiguous.
- cost: Negligible API/storage cost; one small D1/R2 record per armed action.  ·  latency: Adds at most one relay round trip and should remain under 1 second on the local USB path.
- security: Improves authorization for high-impact actions; nonce binding and digest display are mandatory. Do not treat possession as sufficient for account login.
- depends on: pendant button events over USB serial or LTE; a typed action digest from planner/judgement; executor middleware that can refuse before side effects

### `integration` — Build a USB-session guardian that watches the nRF9160 and ESP32 serial identities, performs a synthetic audio handshake on connect, records monotonic counters and firmware/bridge versions, and publishes one compact health state to relay and the pendant. On disconnect, stop issuing audio jobs and mark queued playback as pending rather than failed.
- **owner gets:** Plugging in the pendant becomes self-explanatory: the owner knows whether it is actually ready, and a cable or Bluetooth glitch cannot silently turn a conversation into lost audio.
- effort: Medium: local serial watcher, deterministic firmware test commands, bridge acknowledgement, relay health projection, and a small spoken/LED status vocabulary.  ·  risk: A noisy serial port could produce false alarms; use hysteresis and require two failed probes before declaring unhealthy. Never flash or mutate firmware automatically.
- cost: No meaningful model cost; a few local processes and tiny health records.  ·  latency: 5–15 seconds on connection for diagnostics; zero steady-state conversational latency.
- security: Keep microphone tests synthetic/local; send only status and versions upstream. Authenticate device serial identities to prevent a rogue USB device impersonating the pendant.
- depends on: USB serial enumeration tool; synthetic loopback command in both firmware images; relay device health endpoint

### `integration` — Introduce a resumable cross-surface workflow contract: every delegated browser/Mac step emits a redacted checkpoint containing workflow ID, tab/session identity, precondition hash, side-effect status, next step, and one optional owner decision schema. The relay holds the checkpoint while the Mac sleeps or the pendant is offline; on return, the executor revalidates the page hash before continuing and otherwise asks for fresh perception.
- **owner gets:** Long tasks stop being brittle. If a site pauses for a choice, a laptop sleeps, or the pendant disconnects, the owner answers one question and gets continuation from the real stopping point rather than duplicate submissions or a restart.
- effort: High: shared schema, browser and Mac adapters, durable relay storage, revalidation, redaction, and failure-injection tests.  ·  risk: Stale checkpoints could resume against changed pages; fail closed on hash/locator mismatch and expose the exact reason. A corrupted state should be recoverable by abandoning the workflow without touching the external site.
- cost: Small durable state per workflow; moderate model cost only when re-perception or ambiguity is needed.  ·  latency: Negligible for ordinary steps; 1–3 seconds for checkpoint validation and potentially longer when a changed page needs fresh inspection.
- security: Redacted state and encrypted storage are required. The contract must distinguish prepared local mutations from committed external side effects and never persist credentials or full private-page HTML.
- depends on: durable workflow state storage in relay; typed browser step results and tab/session reattachment; a pendant question/answer transport; precondition hashing or equivalent page identity verification


## What it asked for

_Nothing._
