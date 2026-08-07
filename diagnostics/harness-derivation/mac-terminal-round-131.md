# Harness derivation — mac-terminal — round 131

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Test the pendant and headphones end to end, and tell me what is actually broken.”"
- **useful because:** The hardware is physically present over USB today but is not relay-registered. A single spoken request should validate serial links, firmware identity, button/LED events, audio framing, ESP32 resampling, Bluetooth headphone connection, and a short playback loop, then identify the first failing boundary instead of making the owner debug two dev boards by hand.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → bridge
- **model tier:** background for the multi-step diagnostic plan; realtime only to report the concise result through the pendant
- **latency:** 30–90 seconds for serial discovery, loopback, and playback; report progress immediately and final evidence when complete
- **cost:** Usually <$0.02 per invocation; most cost is one planning call, while serial probes and a 3-second test tone are local
- **security:** Serial identifiers, Bluetooth device names, and diagnostic logs remain on the Mac/relay; do not record microphone audio. Playback should use a generated tone, never captured content. No confirmation needed because this is read-only except changing temporary audio routing.
- **missing:** A serial diagnostics adapter for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A bridge health/loopback protocol with versioned checks and bounded timeouts; A relay route that reports per-boundary evidence and preserves the diagnostic receipt

### "“If something you ran fails, fix it yourself and tell me exactly what changed.”"
- **useful because:** Today the Mac can run unrestricted commands, but a failed command leaves the owner to interpret logs and retry. The agent should classify the failure from stdout/stderr and receipts, choose a bounded retry or alternate local path, verify the result, and speak one truthful outcome—success, repaired, or still blocked—with the original and recovery evidence.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → faculty-perception → faculty-judgement → faculty-action
- **model tier:** background/cheap model for failure parsing and retry selection; realtime only for the owner's short request and final status
- **latency:** Under 5 seconds for diagnosis, up to 2 minutes when a retry is warranted; never hide a long-running recovery
- **cost:** <$0.01 for common failures; local command output dominates, with a model call only when deterministic remediation rules do not match
- **security:** Unrestricted shell means an incorrect retry can have real side effects. Preserve the exact command, working directory, environment class, output, and retry chain; never silently widen scope. The owner policy allows execution without gates, but high-impact retries must be explicitly labeled in the spoken result.
- **missing:** Failure taxonomy plus remediation recipes for the Mac shell and typed actions; A retry executor with attempt limits, idempotency, and verification predicates; Receipt fields linking original action, recovery action, and final evidence; Pendant-visible truthful status events for queued/running/repaired/blocked

### "“When I unplug the pendant, save exactly where we are; when I plug it back in, pick up from there and tell me what happened while I was away.”"
- **useful because:** The pendant is a real USB-attached wearable now, so cable loss is a meaningful presence signal even before LTE registration. This turns accidental disconnects, moving rooms, and sleep into a reliable pause/resume boundary: the Mac snapshots the active task and browser tabs, the relay keeps only the compact checkpoint, and reconnecting gives a spoken delta rather than forcing the owner to reconstruct context.
- **path:** pendant → mac-terminal → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Cheap background model to compress the checkpoint and compute a delta; realtime only for the reconnect briefing
- **latency:** Checkpoint within 2 seconds of serial loss; reconnect briefing within 5 seconds, with long-running jobs continuing independently
- **cost:** <$0.01 per disconnect/reconnect; local serial and job reads dominate, not inference
- **security:** A checkpoint can contain private tab titles, file paths, and task text. Encrypt it at rest, expire it after 24 hours by default, and redact page contents unless explicitly included. Never claim a job finished merely because the USB link returned.
- **missing:** Pendant USB attach/detach heartbeat and monotonic sequence numbers; Mac serial watcher that snapshots active job, focused app, browser tab IDs, and pending receipts atomically; Compact encrypted checkpoint store and reconnect-delta route; A reconnect event path from Mac to relay and pendant speech/audio output

### "“If I tap the pendant twice, stop starting new work everywhere, finish nothing silently, and tell me what is still running when I’m ready.”"
- **useful because:** A wearable is the one surface the owner can reach while a Mac/browser automation is surprising, a meeting starts, or a device is being carried away. A physical pause boundary across relay, Mac, and browser is more dependable than finding the right app window; it freezes dispatch, leaves already-running actions explicitly marked, and resumes only when the owner asks.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-action
- **model tier:** No model for the double-tap and dispatch freeze; cheap background model only to summarize the resulting running/queued work
- **latency:** Pause acknowledgement under 300 ms locally and under 2 seconds across the relay; status summary under 5 seconds
- **cost:** Near-zero for control; <$0.01 for an optional running-work summary
- **security:** A false double-tap could pause useful work, so require a clear two-press interval and LED acknowledgement. Do not kill processes mid-write; mark them draining and let the executor expose truthful state. Store only job IDs and state, not content.
- **missing:** Firmware double-tap recognizer and an explicit local pause latch; Authenticated pause/resume event path from pendant through relay to Mac/browser dispatchers; A global dispatch lease checked by every new job, with durable state and reconnect reconciliation; Spoken/LED acknowledgement and a resume command

### "“When the pendant is plugged into my Mac, keep the whole assistant working even if the relay or LTE is down.”"
- **useful because:** This is runnable today: both chips are physically connected over USB even though the pendant is not relay-registered. The pendant microphone can stream a short command to the Mac, the Mac can run local planning/actions and authenticated Safari work, and the ESP32 can return speech to headphones. The owner gets a real local-first assistant rather than a dead wearable whenever cloud connectivity fails.
- **path:** pendant → mac-terminal → mac-planner → browser-extension → bridge → relay-realtime
- **model tier:** Local/cheap model for short commands and extraction; use realtime only when relay is reachable or the command needs live conversation
- **latency:** Button-to-local acknowledgement under 500 ms; command result under 5 seconds for Mac/browser reads; queue longer work locally and reconcile later
- **cost:** Zero network/API cost during local operation for deterministic actions; <$0.01 when a local model is used, with USB serial and audio processing dominating latency
- **security:** The Mac becomes the trust anchor: bind the serial ports to the paired device, authenticate framed commands, encrypt sensitive checkpoints, and never upload captured audio merely because the relay returns. Local Safari sessions and shell access remain subject to the owner's deliberate maximum-access policy; expose an LED/audio indicator when operating locally.
- **missing:** A USB serial transport carrying authenticated control, Opus audio, and typed local results between pendant and Mac; A local relay-replacement session manager with capability discovery and offline queue/reconciliation; Mac-side microphone/audio playback routing through the ESP32 bridge; Connectivity-aware model routing and a truthful local-vs-cloud status indicator

### "“Before you change anything across my Mac and logged-in browser, show me a machine-checkable forecast of every file, tab, account field, and device state that will change—and after you do it, prove the forecast matched reality.”"
- **useful because:** The owner deliberately allows maximum access, so the missing value is not another approval gate: it is a predictive shadow run. Today an action can execute and leave receipts, but the owner cannot ask for a pre-execution consequence map spanning shell commands, Safari mutations, relay jobs, and pendant/bridge state, nor see a quantified mismatch afterward. This would make powerful automation legible without reducing its reach.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap background model compiles the plan and explains predicted deltas; deterministic adapters perform the shadow run and compare postconditions; realtime is only for the owner's spoken request and concise result
- **latency:** 2–10 seconds for ordinary Mac/browser plans; permit longer plans to stream a forecast before execution and a reconciliation report afterward
- **cost:** <$0.03 for a typical multi-surface invocation; cost is dominated by duplicate reads/snapshots, not model inference
- **security:** Shadow execution must not send messages, submit forms, mutate files, or emit audio. Private browser DOM and shell paths stay on the Mac unless the owner explicitly requests relay analysis. Forecasts need sensitivity labels and expiry because they expose account fields and local paths. A mismatch must be reported as unknown, never silently treated as success.
- **missing:** A side-effect-free shadow executor for shell intents, browser DOM/form operations, relay jobs, and device commands; A typed state-delta schema covering files, processes, browser fields/tabs, job state, audio routing, and firmware state; Pre/post snapshot adapters with stable identifiers and redaction controls; A reconciliation engine that classifies predicted, observed, unexpected, and unverifiable changes; A spoken and visual forecast/reconciliation surface on the pendant and Mac

### "“Use my saved credentials and one-time codes to complete this login, but never reveal the secrets to you, the relay, the browser page text, or the action history.”"
- **useful because:** Authenticated browser work is currently powerful but the model-facing boundary is too coarse: credentials and OTPs can become page text, screenshots, prompts, or receipts. A hardware-/Mac-resident secret broker would let the assistant complete routine authentication while exposing only opaque success/failure and field metadata. This enables useful private-site automation without turning the AI context or durable logs into a credential store.
- **path:** pendant → mac-terminal → mac-planner → browser-extension → relay-realtime → faculty-action
- **model tier:** Cheap model plans field targets and navigational steps; a deterministic local secret broker performs credential and OTP insertion; realtime only reports outcome
- **latency:** Under 3 seconds for a normal login; wait for an OTP challenge without timing out the overall task prematurely
- **cost:** <$0.01 per login; local keychain and extension IPC dominate
- **security:** Secrets must remain in the Mac Keychain/Secure Enclave or an explicitly paired hardware vault. The browser extension must insert values into the focused origin-bound field without returning values through DOM extraction, screenshots, model prompts, relay payloads, or receipts. Bind approvals to origin, tab, challenge type, and expiry; never auto-submit a new origin or transfer secret into downloads/clipboard.
- **missing:** Origin-bound secret broker IPC between mac-planner, Safari extension, and macOS Keychain; A one-time-code provider interface that returns only a write operation, not the code; Browser field classification and secure injection primitives resistant to page JavaScript exfiltration; Redacted receipt types proving which credential class was used without storing its value; A pendant-visible but secret-free login status protocol

### "“Hand this task to Alex for the next hour, but give them only the exact browser tab and files needed, and revoke everything automatically afterward.”"
- **useful because:** The current hive is optimized for the owner alone; it has no safe, auditable handoff when a colleague or family member must finish one thread. A time-limited delegation capsule would combine the browser’s private session, Mac files, relay job, and pendant confirmation without sharing the owner's whole account or conversational memory.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-judgement → faculty-action
- **model tier:** Background model prepares a minimal resource graph and redaction explanation; realtime handles the owner's confirmation and handoff status
- **latency:** Under 10 seconds to prepare the capsule; revocation should propagate within 1 second and be retried until acknowledged
- **cost:** <$0.03 per handoff; encrypted capsule storage and browser/Mac policy checks dominate
- **security:** Delegation is a high-impact access change. Require explicit owner confirmation on the pendant, bind recipient identity, resources, purpose, and expiry, watermark shared views, prevent credential export, and record every access. Revocation must invalidate browser tokens, Mac file grants, and relay job authority rather than merely hiding the UI.
- **missing:** A capability-scoped delegation token format spanning relay, Mac agent, and browser extension; Resource graph and redaction engine for selected tabs/files/job outputs; Recipient authentication and secure handoff UI/link; Enforcement hooks in Safari session access, Mac file operations, and job execution; A revocation fanout with acknowledgements and an immutable access ledger


## What it asked for

### `s18-q5pq` (skill) — usb_link_truth_beacon
- does: When the Mac serial link is present, the pendant LED encodes the last known command state: solid for connected/idle, slow pulse for a queued or running job, double flash for completed, and rapid flash for failed or disconnected. A short button press repeats the state pattern and sends a compact status request when online; offline it reports only locally known state and never invents completion.
- must be on-device because: The owner needs a truthful signal while looking at or holding the wearable, including during a dropped relay connection. LED/button handling and stale-state behavior must survive server and USB link loss.
- trigger: USB serial attach/detach, receipt state update, or short button press
- storage: One 64-byte state record in retained flash/NVS with CRC and sequence; overwrite atomically
- RAM budget: About 2 KB code/data plus one 64-byte record; comfortably below the 211,608 B application RAM, but avoid buffering audio or logs

