# Harness derivation — mac-planner — round 160

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I press the pendant button while it is USB-tethered, tell me what I’m looking at and what I need to do next.”"
- **useful because:** This creates a genuinely available tethered mode today: the worn button supplies intent, the Mac supplies live foreground/browser/calendar context, and the relay/model turns it into a short spoken answer queued back to the pendant. It still works when LTE registration is absent.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Realtime only for interpreting the button event and composing the brief; use a cheaper background model for optional enrichment.
- **latency:** Under 2 seconds from button event to text/audio enqueue; serial transport and current-tab inspection dominate.
- **cost:** A few cents per interaction if a model call is needed; local context collection is negligible.
- **security:** The Mac may expose the active private tab and calendar title to the relay. Send only the selected tab title/URL and minimal snippets, redact page bodies by default, and make the button gesture explicit. No browser mutation or external send.
- **missing:** A USB serial event listener for /dev/cu.usbmodem00096003658*; A Mac-to-pendant response/audio spool over the same serial link; A relay intent for tethered button events; A small dashboard status/control for tethered mode

### "“Start a focused work session for what I’m doing right now.”"
- **useful because:** The pendant gives a physical, interruption-free trigger; the Mac identifies the foreground app and active Safari tab, the browser agent extracts the task context, and the relay produces a bounded session plan. The Mac then opens only the needed note, checklist, or URLs and reports completion back to the pendant—turning vague intent into a usable workspace without asking the owner to narrate it.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Use a fast model for intent classification and a cheaper background model for extracting and formatting the session plan.
- **latency:** 3–5 seconds for a first plan; desktop actions should begin immediately after context capture.
- **cost:** Roughly 1–3 cents per session, dominated by context synthesis; local app/tab reads are free.
- **security:** Active-tab content can be sensitive. Keep extraction scoped to the current tab and visible task cues, redact secrets, and never submit forms or send messages. File creation should be in a designated Work Sessions folder.
- **missing:** A tethered pendant-button event source; A read-only foreground-app/active-tab context packet; A per-session artifact format and local workspace directory; A serial response path to acknowledge start/finish

### "“Test my pendant and audio bridge.”"
- **useful because:** The owner gets a trustworthy, one-command health check while both boards are plugged into the Mac: exercise the pendant button and LED, verify serial framing and reconnect behavior, play a short known audio fixture through the ESP32 path, and report exactly which link or component failed. This makes hardware that is physically present useful before LTE registration exists.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** No realtime model needed for the test; use deterministic firmware fixtures and a cheap background model only to turn raw results into a plain-language report.
- **latency:** Under 30 seconds for a complete test, with per-step progress available immediately.
- **cost:** Near-zero API cost; local serial and audio fixture execution dominate.
- **security:** Do not open the microphone or upload captured audio. Use a synthetic fixture, avoid changing persistent device configuration, and require an explicit destructive flag for firmware reset (not part of the normal test).
- **missing:** A documented serial diagnostic command set for both chips; A synthetic audio loopback/known-fixture test that does not access the microphone; A Mac route that streams per-step test receipts; A dashboard view of device test history

### "“Use my pendant as a physical presence key: when it is with me, put my Mac into my private workspace, and when it leaves, lock or redact sensitive views.”"
- **useful because:** The pendant would provide a physical, non-password presence signal that coordinates the worn device and Mac. It could automatically switch between a private work profile and a safe-away profile, reducing accidental exposure when the owner walks away from the desk. This is materially different from ordinary Mac automation because presence is supplied by the worn hardware.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** No model required for presence detection or policy execution; use a cheap background model only to explain state changes.
- **latency:** Presence transitions should be detected within 2–5 seconds; workspace changes should complete within another 2 seconds.
- **cost:** Near-zero API cost. Hardware/firmware integration and reliable presence detection dominate.
- **security:** A stolen or spoofed pendant must not grant unrestricted access. Use a locally paired cryptographic identity, short-range USB/BLE proof, explicit safe profiles, and never transmit private workspace contents to the relay. Locking behavior must fail closed.
- **missing:** A cryptographic device-identity and pairing protocol; A presence signal independent of an easily copied serial string; A Mac profile broker that can lock, hide, or restore approved applications and windows; Owner-configurable safe/private workspace policies

### "“When I leave my Mac mid-task, preserve the exact state of my work and restore it when I return with the pendant.”"
- **useful because:** The owner would not have to remember which windows, browser tabs, files, drafts, and next action were active. The pendant’s departure/return events would delimit a real work interval, while the Mac records a compact, privacy-filtered state capsule and reconstructs the workspace on return. This is a physical continuity primitive, not another scheduled briefing.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Use deterministic local state capture first; use a cheaper background model to summarize the next action and resolve ambiguous window labels. Realtime is unnecessary.
- **latency:** Capture under 3 seconds on departure; restore a first useful workspace within 5 seconds of return.
- **cost:** A few cents only when semantic summarization is needed; local window/tab/file metadata is the dominant implementation work.
- **security:** State capsules may contain sensitive URLs, filenames, or draft text. Keep raw state on the Mac, encrypt any relay copy, apply per-app exclusions, and offer a hardware long-press to cancel capture.
- **missing:** Reliable pendant departure/return detection; Read-only window and document-state capture beyond current app/tab metadata; A reversible workspace snapshot/restore engine for Mac and Safari; Encrypted local capsule storage with retention controls

### "“If my Mac loses the network while I’m wearing the pendant, keep a local queue of tiny commands and execute them when the link returns, telling me which ones actually happened.”"
- **useful because:** The owner would get dependable command continuity across a real connectivity gap: simple approved local actions such as opening a note, creating a reminder, or saving a capture can be accepted over the tether and persisted locally, then reconciled after reconnection. The important benefit is truthful completion status rather than silently losing a spoken request.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** No realtime model is needed for queueing or reconciliation; use the realtime tier only to parse an ambiguous spoken command before enqueueing, and a cheaper model for post hoc summaries.
- **latency:** A local acknowledgement within 500 ms; replay starts immediately on reconnection and reports each receipt.
- **cost:** Negligible API cost for deterministic commands; storage and reconciliation logic dominate.
- **security:** Only commands with an explicit idempotency key and bounded local effect should survive offline. Never queue sends, purchases, deletions, or browser submissions. Encrypt queued payloads and expire them by policy.
- **missing:** A pendant-to-Mac offline command envelope; A durable, idempotent local queue with replay receipts; A connectivity detector spanning serial, relay, and browser links; A command allowlist and conflict-resolution policy


## Changes it proposed to its own stack

### `integration` — Add a USB-tether coordinator on the Mac that owns both serial devices: decode nRF9160 button/LED events, correlate them with ESP32 bridge connectivity, attach a monotonic event ID, and publish a single authenticated event envelope to the relay pipeline. Include heartbeat, reconnect, and a local append-only event journal so a dropped relay link cannot duplicate button actions.
- **owner gets:** The pendant becomes useful immediately while physically attached to the Mac, instead of waiting for LTE registration; button presses reliably trigger the right cross-device action and recover cleanly after cable or relay hiccups.
- effort: Medium: a small launchd service plus serial protocol framing, reconnect tests, and relay event ingestion.  ·  risk: Malformed serial bytes or reconnect races could create duplicate actions. Use event IDs and deduplication; expose a local disable command and retain only short-lived event metadata.
- cost: Negligible API cost; approximately 0.1–0.5% CPU while connected and no meaningful power increase.  ·  latency: Adds about 20–100 ms for serial framing and heartbeat handling.
- security: The service can observe button events and send device identifiers to the relay; authenticate envelopes and avoid transmitting raw audio or page data.
- depends on: A documented nRF9160 button-event framing; A documented ESP32 bridge serial status message; A relay endpoint accepting tethered device events; A response/audio framing protocol back to the pendant


## What it asked for

_Nothing._
