# Harness derivation — faculty-perception — round 117

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device registry** — At 2026-08-07T17:50Z, only home-macbook-bridge is online; Safari on MacIntel browser device is online with 3 tabs; cloudflare-contract-test mobile is offline. No nRF9160 pendant is registered.
  - evidence: discover(devices) returned exactly Safari on MacIntel, home-macbook-bridge, cloudflare-contract-test; no pendant.
- **Mac control truth** — The running AI Pendant Agent is not Accessibility-trusted and lacks Screen Recording; inputReachability is failed and UI actions such as click/type/keys report success while doing nothing. Automation grants are present for many apps, and browser extension is online with zero pending commands.
  - evidence: GET /observe and GET /ops/status at 2026-08-07T17:51Z.
- **pipeline provenance** — GET /pipeline currently contains historical runs whose events claim pendant delivery or nRF9160 download, while the live device registry has no pendant. At least one run remains status=processing with old timestamps, so pipeline status alone cannot establish current physical delivery.
  - evidence: GET /pipeline at 2026-08-07T17:51Z alongside discover(devices).

## Capabilities it proposed

### "Tell me whether my answer, reminder, or audio actually reached the device—not merely whether the relay accepted it."
- **useful because:** The current pipeline can contain stale processing records and claims of nRF9160 delivery even when no pendant is registered. This gives the owner a binary, evidence-backed delivery answer with the exact break (relay accepted, Mac rendered, device acknowledged, or playback completed) instead of false reassurance.
- **path:** relay-realtime → relay → mac-planner → faculty-perception → dashboard
- **model tier:** Use deterministic correlation and device acknowledgements first; use the realtime model only to phrase a spoken result when the owner asks. No LLM is needed to establish truth.
- **latency:** Under 500 ms for an existing job; under 3 s if a fresh Mac/relay/device status check is required.
- **cost:** Near-zero model cost for status checks; roughly $0.01 or less only if a spoken explanation requires realtime generation. Storage cost is small append-only receipt metadata.
- **security:** Expose only the owner's job IDs and device IDs; never infer physical playback from a relay upload. Mark historical telemetry stale, bind acknowledgements to a device nonce and audio hash, and require confirmation before retransmitting private audio.
- **missing:** A durable end-to-end receipt schema tying relay result, Mac-rendered audio hash, registered device delivery, and playback completion to one request; A live nRF9160 registration/ack path (currently no pendant is registered); A dashboard/spoken status formatter that refuses to call stale pipeline events current

### "Fix the browser page I was using, but do not lose my logged-in session; tell me exactly what you changed and prove the page is usable."
- **useful because:** The live Safari bridge is online, yet its active tab reports “Failed to open page” while authenticated Gmail and durable browser sessions remain available. Today a browser command can be delivered without establishing that navigation or reading succeeded. This lets the owner recover a broken tab through the extension, preserve session affinity, and receive a verified result rather than a success receipt for a no-op.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → faculty-perception
- **model tier:** Deterministic browser inspection/navigation and read-back; use the cheaper planner only for choosing among safe recovery steps. Realtime is only for the owner's short spoken request/result.
- **latency:** 3–8 seconds for inspect, reload or reopen, and read-back; never silently wait beyond 15 seconds.
- **cost:** Usually no model call if the recovery policy is deterministic; at most a small planner call (<$0.01) for ambiguous tab selection. No page content leaves the Mac except the requested read-back.
- **security:** Keep authenticated cookies in Safari; never export them. Require explicit URL allow/deny policy before navigating, preserve the original URL, and redact page text containing secrets. A recovery must be reversible (duplicate tab or history snapshot) and report when it cannot verify content.
- **missing:** A browser recovery transaction that snapshots tab/session affinity, performs reload/reopen, then reads the page back; A typed browser result with before/after URL, title, load error, and content-verification timestamp; A safe duplicate-tab fallback for pages that cannot be reloaded in place

### "Just do this wherever you can reach me right now, and don't pretend my pendant heard it if it wasn't connected."
- **useful because:** The system currently has a live Mac bridge and browser but no registered pendant, while historical pipeline events imply wearable delivery. This capability chooses the reachable output (Mac speech, browser notification, or pendant), announces the chosen channel, and degrades honestly when the wearable is absent—so a request remains useful today without inventing physical-world completion.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → dashboard → faculty-perception
- **model tier:** Deterministic reachability and channel selection; cheap text model for concise fallback wording. Reserve realtime for the live conversational turn, not routing or background retries.
- **latency:** Reachability decision under 300 ms; Mac/browser fallback under 3 s; queued wearable delivery must remain visibly pending until a live device acknowledgement.
- **cost:** Near-zero for routing and Mac speech; <$0.01 for an occasional concise fallback response. Browser and relay metadata are the dominant storage cost, not inference.
- **security:** Treat device presence and delivery as separate facts; never route private content to an unpaired browser or generic desktop notification. Persist the selected channel and reason, expire pending audio, and require confirmation before switching from a private wearable channel to a visible screen.
- **missing:** A single live reachability contract shared by relay, Mac bridge, browser extension, and pendant registry; Output-channel fallback that can speak through macOS or post to the authenticated browser without claiming pendant delivery; A user-visible pending/expired state for work awaiting a future wearable connection

### "Pause whatever I’m doing, handle this interruption, then put me back exactly where I was and tell me what changed while I was away."
- **useful because:** A wearable conversation, Mac automation, and authenticated browser session currently have no shared notion of an interrupted task. The owner should not lose a half-written document, browser tab, selection, or pending decision just because they asked the pendant one question. This creates a recoverable human-scale context switch across the surfaces rather than merely running another command.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles the interruption itself; a cheaper background model builds the checkpoint diff and resume brief. Deterministic Mac/browser APIs restore state; vision is used only when a semantic UI state cannot be represented structurally.
- **latency:** Capture the checkpoint within 1 second of the interruption; answer immediately; restore or present a resume card within 5 seconds after the owner says 'back'.
- **cost:** One small background summarization call per interruption (typically <$0.01); storage is a compact state snapshot plus optional encrypted screen crop. Realtime cost is only the spoken interruption exchange.
- **security:** Checkpoint content may include drafts, private tabs, and credentials. Encrypt snapshots, never capture password fields, keep them on the Mac unless explicitly synced, expire them automatically, and require a spoken/button confirmation before restoring a destructive state. If Accessibility/Screen Recording are absent, report that restoration is partial rather than claiming success.
- **missing:** A cross-surface checkpoint object with versioned Mac, browser, relay, and pendant state; Transactional capture/restore adapters for text cursor/selection, active browser tab and scroll position, pending jobs, and audio conversation state; A diff generator that can distinguish owner changes from agent changes; Owner-controlled retention and an explicit resume/abandon interaction

### "Handle this privately—don’t say the sensitive part aloud; show it only on the screen I’m using, and give me a brief cue when it’s ready."
- **useful because:** A wearable voice channel is inherently audible, while the Mac and authenticated browser can display private material. The owner currently cannot make one request that safely splits a response across pendant audio and the correct private screen, with a reliable cue and no sensitive text leaking into relay speech or logs.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime classifies the spoken privacy instruction and gives only a generic acknowledgement; deterministic routing sends the payload to the authenticated active browser/Mac surface. A cheaper model can redact and format the display copy.
- **latency:** Generic audio acknowledgement under 500 ms; private display within 3 seconds; if the target screen cannot be authenticated, refuse to display and say only that it could not safely deliver.
- **cost:** Usually <$0.01 for redaction/formatting; no additional model call for deterministic routing. Storage and relay cost are limited to encrypted short-lived payloads.
- **security:** Never put the sensitive payload in spoken TTS, routine telemetry, ordinary pipeline labels, or browser URLs. Bind delivery to a browser session nonce, encrypt at rest, auto-expire after viewing, and require an explicit fallback confirmation before showing it on another surface.
- **missing:** A privacy-mode contract propagated from realtime intent through relay, Mac planner, and browser extension; Authenticated screen/session targeting and an ephemeral display channel with viewed/expired receipts; Payload-aware redaction of logs, pipeline events, and TTS transcripts; A physical or UI cue that confirms readiness without revealing content


## Changes it proposed to its own stack

### `integration` — Add a hard 'live-vs-history' provenance gate to every pipeline and job response: join each event to a current relay device heartbeat and a monotonic request nonce; label old events HISTORY, reject claims of pendant delivery when no pendant is registered, and expose a machine-readable delivery state (rendered, relay-accepted, device-downloaded, playback-confirmed, expired).
- **owner gets:** Today the owner can be told that audio is waiting for or was delivered to an nRF9160 even though the live registry has no pendant. This prevents the system from confidently lying about whether the owner actually received something.
- effort: Medium: schema migration plus relay/Mac bridge correlation and dashboard labels; add fixtures for absent-device and delayed-device cases.  ·  risk: Older jobs may appear changed when relabeled; recover by retaining raw events and making the gate a derived view. A clock mismatch could misclassify events, so use server sequence/nonces rather than wall clock alone.
- cost: Negligible inference/API cost; a few bytes of receipt metadata per event and modest D1 growth.  ·  latency: Under 50 ms for a joined status read; no impact on audio hot path.
- security: Improves privacy and integrity by preventing accidental disclosure via false delivery claims; device IDs and nonces must remain opaque to browser pages.
- depends on: A durable end-to-end receipt schema; Live pendant registration and acknowledgement when hardware is connected

### `hardware` — Add a low-power BLE companion (for example an nRF52840-class module) to the pendant, with a signed proximity/presence beacon and a small local event queue shared with the nRF9160 over SPI/UART. The Mac bridge should use the beacon to distinguish 'pendant physically nearby but LTE unavailable' from 'no pendant', then ferry queued audio/alerts when USB or network returns.
- **owner gets:** The owner gets honest presence-aware behavior and useful offline continuity: nearby pendant requests can be acknowledged locally and synchronized through the Mac instead of waiting for LTE, while a missing pendant is never mistaken for a delivered response.
- effort: High: board spin, antenna/RF validation, power-management firmware, signed pairing protocol, Mac bridge transport, and relay device-state integration.  ·  risk: Added radio and firmware complexity can drain the battery or create ambiguous dual-link ordering. Recover with monotonic event IDs, explicit link priority, watchdog isolation, and a hardware-disable fallback that leaves LTE behavior intact.
- cost: Roughly $8–$20 in added components/PCB work at prototype volume; BLE beaconing can be tens to hundreds of microwatts average, with sync bursts adding modest peak current. No per-request model cost.  ·  latency: Presence detection under 2 seconds; nearby Mac ferrying can reduce delivery from LTE-scale seconds to sub-second, subject to USB/network availability.
- security: Use rotating authenticated beacons and encrypted pairing; do not expose a stable owner identifier over BLE. Treat proximity as a transport fact, not proof of wearer identity, and require relay authentication for queued data.
- depends on: A device registry that records transport and acknowledgement provenance; Firmware event IDs and durable replay semantics; Mac bridge support for a second serial/radio transport


## What it asked for

_Nothing._
## Its own summary

Round 117 established three live facts: the relay has no registered nRF9160 pendant (only the Mac bridge and Safari extension are online); AI Pendant Agent Accessibility and Screen Recording remain false, with inputReachability failed so UI-action receipts are not trustworthy; and /pipeline contains stale processing/delivery claims that contradict the live registry. I recorded these and proposed four non-duplicate pieces: end-to-end delivery truth, verified authenticated-tab recovery, honest channel fallback when the pendant is absent, and a live-vs-history provenance gate. I still need an actual pendant registration/ack path and a durable receipt correlation across relay, Mac rendering, device download, and playback; until then wearable delivery cannot be established.

**Biggest unknown:** Whether the physical nRF9160 and ESP32 are connected to the Mac in a way the running bridge can enumerate; the HTTP registry proves only that no pendant has registered, not why. The pending hardware/continuity context requests would resolve this, but I did not re-ask for them.

