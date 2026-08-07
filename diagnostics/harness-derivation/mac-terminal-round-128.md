# Harness derivation — mac-terminal — round 128

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-readiness** — Live /ops/status shows Mac agent fullControlMode=true and browser extension online with 3 Safari tabs, but Accessibility trusted=false and Screen Recording granted=false; computer-use loop is disabled and readiness=false. Relay and mac bridge are reachable.
  - evidence: GET /ops/status returned agent.computerUse.loopEnabled=false, permissions.accessibility.trusted=false, permissions.screenRecording.granted=false, browserExtension.online=true, relay.reachable=true.

## Capabilities it proposed

### "Keep my pendant conversational when it is plugged into my Mac, even if LTE or the relay is unavailable: I press the button, speak, hear the response through the audio bridge, and sync the transcript and pending work when connectivity returns."
- **useful because:** This is the first genuinely local/offline use of the hardware that is physically attached today. It makes the pendant useful on a plane, in a basement, or during an outage instead of becoming dead weight whenever the cloud link drops.
- **path:** pendant → mac-planner → mac-terminal → relay-realtime → relay → browser-extension
- **model tier:** Use a cheap local Mac model for speech/intent triage and deterministic device protocol; use realtime only when the relay is reachable, and sync summaries in background with a cheaper model.
- **latency:** Button acknowledgement under 150 ms; local response under 3 s; cloud handoff and reconciliation can take seconds after reconnect.
- **cost:** Near-zero incremental API cost offline; occasional background sync uses a small model. Engineering cost is the serial protocol, local audio path, queue reconciliation, and a Mac launch agent.
- **security:** Raw audio and private browser text can remain on the Mac in offline mode. Persist encrypted queue records, expose a clear local/cloud indicator, and require confirmation before replaying queued mutations after reconnect.
- **missing:** nRF9160 USB-serial framing and button/audio control protocol; ESP32 bridge serial/audio playback service; Mac launch agent that discovers /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; offline speech recognition and TTS or a local fallback; idempotent cloud-sync/reconciliation protocol

### "Give me a private-mode answer: inspect my currently open authenticated Safari tabs and local Mac state, but keep the page contents and audio on my Mac; send the relay only a redacted request and a short answer, with a switch to reveal the evidence if I ask."
- **useful because:** The wearable can reach the owner anywhere, while the browser holds secrets. This makes that combination usable for banking, health, and work pages without blindly shipping authenticated page contents to the cloud.
- **path:** pendant → mac-planner → mac-terminal → browser-extension → relay-realtime → relay
- **model tier:** Local Mac model performs extraction, redaction, and evidence selection; realtime handles only the spoken request/response envelope. Use a cheaper background model for redaction QA and caching.
- **latency:** Acknowledge mode in 200 ms and answer in 5 s for already-open tabs; evidence reveal is an explicit second turn.
- **cost:** Small realtime token usage for redacted text; most extraction stays local. Main cost is a local redaction/evidence broker and browser bridge changes.
- **security:** Treat DOM, screenshots, cookies, and audio as Mac-confidential. Redaction must fail closed on uncertain fields, log hashes rather than contents, and never let a cloud prompt request raw tab data implicitly.
- **missing:** Mac-local redaction service with field/secret detectors; browser result schema separating private evidence from shareable summary; relay metadata flag enforcing no-raw-context mode; pendant indication of private mode and reveal action; auditable local evidence store

### "When I say 'continue that later' on the pendant, save the exact state of the conversation and the open Mac/browser work, then let me resume from the pendant or Mac with a one-sentence spoken checkpoint and no repeated explanation."
- **useful because:** Long tasks currently lose the owner's place when attention or connectivity changes. A physical button and spoken checkpoint can suspend work safely and resume it across the wearable, Mac, browser session, and relay.
- **path:** pendant → mac-planner → mac-terminal → browser-extension → relay-realtime → relay
- **model tier:** Use deterministic state capture and a cheap summarizer; reserve realtime for the resume conversation, not for indexing every event.
- **latency:** Checkpoint confirmation under 1 s; resume context ready under 2 s from local state, with cloud sync eventually.
- **cost:** Low API cost because only compact deltas and a short summary are stored. Engineering cost is cross-surface checkpoint schema and browser/tab attachment persistence.
- **security:** Checkpoint may contain private tab state. Encrypt sensitive fields, store capability-scoped references rather than cookies, expire stale browser attachments, and make spoken summaries avoid secrets by default.
- **missing:** Cross-surface checkpoint schema with versioning; pendant double-press or spoken checkpoint event; Mac job/session and browser-tab snapshot adapter; resume conflict detection when tabs or files changed; sync queue for relay reconnect

### "If the Mac or browser agent starts doing something I no longer want, let me long-press the pendant to stop all in-flight work immediately, hear what was cancelled, and later resume only the safe unfinished parts."
- **useful because:** A wearable is the only control surface still in the owner's hand while the Mac is busy or a browser workflow has gone wrong. A physical stop is faster and more reliable than finding a window or speaking over an active response.
- **path:** pendant → mac-terminal → mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** Deterministic device event fan-out and job cancellation; realtime only speaks the concise cancellation receipt, with no model call needed for the stop itself.
- **latency:** Hardware acknowledgement under 100 ms; cancel requests dispatched under 300 ms; spoken receipt under 2 s.
- **cost:** Negligible API cost. Requires serial button-event firmware, relay cancellation fan-out, Mac/browser abort handlers, and a compact receipt.
- **security:** Long-press must be hard to trigger accidentally and never erase data. Cancel is safer than undo; report which operations could not be stopped and preserve receipts.
- **missing:** Pendant long-press event and debounce policy; authenticated emergency-cancel endpoint keyed to owner session; fan-out cancellation for Mac jobs, browser commands, vision loops, and relay streams; device haptic/LED acknowledgement; partial-cancel receipt schema

### "Make my Mac and browser automatically enter a private state when my pendant leaves me: pause spoken output, hide sensitive Safari tabs, stop sharing, and restore everything when the pendant returns—without me touching the keyboard."
- **useful because:** The pendant is the one object that travels with the owner. Presence-based privacy protects authenticated work, banking, and health sessions during interruptions or when the owner walks away, something a Mac alone cannot reliably infer.
- **path:** pendant → mac-terminal → mac-planner → browser-extension → relay
- **model tier:** Deterministic presence and policy engine; no expensive model call for lock/unlock. Use realtime only to announce state changes when appropriate.
- **latency:** Detect departure within 2 seconds and apply browser/audio protections within 1 second; restore within 2 seconds after return.
- **cost:** No per-use model cost. Requires a low-power proximity signal, Mac presence daemon, Safari tab masking, and relay session coordination.
- **security:** False departures must not destroy work; suspend and restore exact tab state. Never treat presence alone as authentication for financial actions. Keep presence history local and expire it quickly.
- **missing:** Low-power pendant-to-Mac proximity transport; Pendant presence heartbeat firmware; Mac privacy-state daemon; Safari tab redaction/restore API; Relay stream pause/resume tied to presence state

### "When a sensitive value is visible in my authenticated browser—such as a one-time code, delivery address, or account number—let me ask from the pendant for just that value and whisper it locally through the audio bridge, without sending the page or value through the relay."
- **useful because:** The browser has private sessions and the pendant has the owner's attention, but today there is no safe local handoff between them. This would make the wearable useful for quick lookups while sharply reducing exposure of secrets.
- **path:** pendant → mac-terminal → browser-extension → relay-realtime → relay
- **model tier:** Mac-local deterministic extraction first, with a small local model only for semantic field identification; realtime is limited to the spoken request envelope and should not receive the secret.
- **latency:** Under 3 seconds for an already-open tab; no cloud round trip for the extracted value.
- **cost:** Near-zero API cost per lookup. Engineering cost is local browser extraction, secret-type validation, and ESP32 audio playback.
- **security:** Do not persist the value, include it in logs, or expose it to relay telemetry. Require a deliberate button gesture for playback, redact browser evidence, and refuse ambiguous matches.
- **missing:** Mac-local browser extraction endpoint; Secret-value classification and non-persistence rules; USB audio-bridge playback protocol; Pendant gesture for sensitive playback; Local-only request routing


## Changes it proposed to its own stack

### `mac-harness` — Add a command execution ledger at the shell boundary that records argv after safe tokenization, cwd, selected environment fingerprints (never raw secrets), start/finish/timeout, stdout/stderr hashes plus a bounded tail, process tree, exit code, and whether the command is reversible. Expose a structured failure bundle and retry recipe through the existing job journal; do not gate or block anything.
- **owner gets:** When the agent says something failed, the owner gets a truthful explanation and a one-tap retry or handoff instead of a vague error. It also makes unattended work auditable without reducing the maximum-access policy.
- effort: Medium: shell wrapper, redaction, D1 schema, journal API, and UI/voice formatter.  ·  risk: Secrets can leak through output or environment; redact known secret patterns and store only hashes by default. Process-tree capture may be incomplete; mark unknown rather than claiming success. Recovery is to retain the existing raw job record.
- cost: Negligible API cost and modest local disk/D1 storage; bounded tails cap growth.  ·  latency: Under 50 ms per command plus asynchronous ledger flush.
- security: Improves accountability but creates sensitive metadata; encrypt or access-scope ledger entries and omit raw env/command interpolation values.
- depends on: Existing /jobs, /journal, and /jobs/:jobId/receipts contracts; A stable shell wrapper that preserves current FULL_CONTROL_MODE behavior

### `hardware` — Add a low-power, cryptographically rotating BLE presence beacon to the pendant, with a companion Mac receiver/daemon and a hardware-visible privacy-state indicator. The beacon should expose only an ephemeral identifier and support a signed return-to-presence handshake; it must not become a general-purpose tracking device.
- **owner gets:** The owner's wearable can become a reliable privacy boundary: walking away can protect browser sessions and audio automatically, while returning restores the exact working state. The current button and USB connection cannot detect daily physical presence once unplugged.
- effort: Medium-high hardware revision plus firmware, macOS daemon, Safari integration, and relay session-state support.  ·  risk: Radio loss can cause nuisance privacy transitions; use hysteresis and suspend/restore rather than destructive actions. Battery life and pairing bugs are the main recovery concerns.
- cost: Approximately $2–8 in added BLE-capable beacon/sensor hardware depending on board revision, with low average power draw; negligible model cost.  ·  latency: Sub-second local detection after radio tuning; no network latency required.
- security: Use rotating identifiers, authenticated pairing, no location history, and local-only presence logs. A stolen beacon must not unlock accounts or authorize transactions.
- depends on: Pendant firmware support for rotating beacon identity; Mac privacy-state daemon; Browser tab masking/restoration integration; Relay pause/resume state model


## What it asked for

_Nothing._
## Its own summary

Recorded three non-backlog proposals: presence-triggered privacy state, local-only sensitive-value whispering from authenticated Safari, and a BLE presence beacon hardware/firmware change enabling that privacy boundary. Each names the missing cross-surface work rather than pretending existing routes are sufficient.

**Biggest unknown:** Whether the pendant board can support an acceptable low-power proximity transport without a hardware revision; the current nRF9160/USB setup cannot provide daily worn presence once unplugged.

