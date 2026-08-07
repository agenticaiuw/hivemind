# Harness derivation — unified — round 26

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Reopen the thing we were working on.”"
- **useful because:** The owner can abandon a task mid-conversation and later resume from the pendant without remembering which tabs, drafts, evidence, or background job were involved. It is more than history: it revalidates stale browser state and reconstructs a safe, reviewable next step across all surfaces.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use the relay realtime model only for the short spoken request and confirmation; use a cheaper background model to summarize the saved task capsule and compare fresh browser evidence. Mac planner executes reversible workspace restoration; authenticated browser reattaches tabs and refreshes sources; relay coordinates and delivers the result to the pendant.
- **latency:** Acknowledge in under 1 second from the pendant. Restore and freshness-check within 10–20 seconds; if browser or Mac is offline, speak a precise parked-state receipt and retry in the background.
- **cost:** Roughly $0.01–$0.05 per resume, dominated by background summarization and authenticated-page extraction; realtime cost is limited to two short turns.
- **security:** Task capsules may contain private URLs, snippets, drafts, and account metadata. Encrypt at rest, apply sensitivity/TTL fields, redact secrets from spoken summaries, bind browser operations to the original tab/session, and require explicit confirmation before sending, deleting, purchasing, or submitting anything. Never replay a stale approval.
- **missing:** A durable cross-surface task-capsule schema containing goal, evidence pointers, open decisions, approvals, expiry, and next action; Relay storage and retrieval keyed to the owner's voice/session identity; Mac endpoint to restore a named workspace and report exactly what changed; Browser freshness validation and provenance-preserving reattachment for authenticated tabs; Pendant-facing resume command and a compact spoken receipt; Dashboard view showing capsule contents, staleness, and pending confirmation

### "“Capture the last few minutes and turn the decisions into follow-ups.”"
- **useful because:** After a meeting or hallway conversation, the owner can mark a short audio window from the pendant and receive a sourced, editable follow-up packet instead of trying to remember decisions. The system connects spoken commitments to the relevant Mac workspace and authenticated browser records, while stopping before any external message or calendar change is sent.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use the realtime model only to acknowledge the pendant command and confirm the capture boundary. A cheaper background model transcribes and extracts decisions, owners, dates, and uncertainties. Mac planner searches local notes/workspace for project identity; authenticated browser checks matching private records; relay assembles the packet and queues it for spoken or dashboard review.
- **latency:** Acknowledge capture in under 1 second. Produce a draft packet in 30–90 seconds after upload. If the Mac or browser is unavailable, retain the marked segment and deliver a partial transcript with explicit missing-source notices.
- **cost:** Approximately $0.05–$0.30 per capture, dominated by audio transcription and background extraction; browser and Mac work add little model cost but may require several tool calls.
- **security:** Audio may contain other people and confidential material. Capture must be explicit and visibly indicated by the pendant LED, use a short bounded window with automatic deletion after extraction, encrypt transit/storage, and let the owner discard before any cloud processing where feasible. Browser-derived details need provenance and sensitivity labels. Creating or sending messages, calendar events, or tasks requires separate confirmation.
- **missing:** A pendant local ring buffer with explicit mark-start/mark-end control and a recording indicator; A relay audio-upload and transcription job that preserves segment boundaries and deletion policy; Cross-surface entity matching between transcript terms, Mac workspace files, and authenticated browser records; A review packet format with transcript snippets, extracted decisions, confidence, source, and suggested follow-up actions; A dashboard and pendant interaction for correction, discard, and confirmation before external changes

### "“Forget everything from that conversation everywhere.”"
- **useful because:** The owner gets a real privacy control rather than hoping each surface deleted the same data. One spoken request can locate a bounded interaction across pendant buffers, relay jobs, Mac drafts, browser extraction caches, and audio artifacts, show what will be removed, and then provide a verifiable deletion receipt.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use realtime only to identify the conversation window and confirm the destructive request. Use a cheaper background model and deterministic indexes to locate artifacts; Mac and browser agents perform deletion locally; relay coordinates and records only a minimal tombstone receipt.
- **latency:** Inventory within 5 seconds and speak the artifact count and scope. Deletion may take up to 60 seconds across offline surfaces; the pendant should report partial completion and retry status rather than claiming success.
- **cost:** About $0.01–$0.05 per request; most work is deterministic indexing and deletion, not model inference.
- **security:** Deletion is destructive and must require explicit confirmation, exact time/topic scope, and an owner-authenticated voice session. Preserve no recoverable content in logs, prompts, caches, browser session state, or backups beyond a non-content tombstone. If a device is offline, clearly state what remains and avoid implying global deletion.
- **missing:** A cross-surface artifact index linking interaction IDs to pendant, relay, Mac, browser, and dashboard data; Deletion APIs on Mac and browser that can remove drafts, extraction caches, and queued actions safely; A relay purge workflow covering audio objects, transcripts, job payloads, and derived summaries; A cryptographically signed, content-free deletion receipt with partial/offline status; A confirmation UI that displays scope and exceptions before destructive execution


## Changes it proposed to its own stack

### `hardware` — Replace the prototype nRF9160 + ESP32 classic SBC bridge audio chain with a product audio front end: a low-power 24 kHz-capable stereo codec/mic interface on the pendant and a BLE Audio/LC3-capable bridge (nRF5340-class or equivalent) that preserves 24 kHz frames through the bridge instead of forcing 31.25 kHz I2S, 44.1 kHz resampling, and SBC. Keep the LTE modem as the control/uplink transport, but make the negotiated audio profile explicit (24 kHz SWB or 16 kHz fallback).
- **owner gets:** They hear and send clearer speech with fewer resampling and Bluetooth artifacts, and the system can honestly claim a tested 24 kHz path rather than decoding 24 kHz only to distort it through a fixed 44.1 kHz prototype bridge. The fallback keeps calls usable when network or headset compatibility is poor.
- effort: High: select codec and BLE Audio silicon, redesign pendant/bridge boards and power rails, port fixed-point capture/playback and LC3, qualify headsets, then run an end-to-end acoustic and packet-loss test matrix.  ·  risk: New hardware may lose compatibility with the owner's current AirPods/classic Bluetooth setup, and BLE Audio interoperability is uneven. Recover with a dual-mode bridge supporting classic SBC during migration and an explicit 16 kHz fallback. Preserve the existing prototype firmware as a test fixture.
- cost: Engineering and two new boards are the main cost; roughly $10–$30 incremental prototype BOM per wearable/bridge pair, plus certification. Runtime power should fall versus the current ESP32 bridge, but must be measured under LTE transmit peaks. API cost unchanged.  ·  latency: LC3 framing can keep playout near the current 60 ms target; removing the 31.25→44.1 FIR and SBC staging should reduce bridge buffering by roughly 10–30 ms, subject to headset buffering.
- security: No new cloud data requirement. Secure-boot/sign firmware and authenticate the pendant↔bridge link; avoid exposing raw microphone PCM over unauthenticated BLE.
- depends on: An agreed 24 kHz acceptance test covering intelligibility, MOS/artifacts, latency, packet loss, and fallback behavior; A transport budget decision: current LTE-M measurements show simultaneous 16 kbps uplink + 24 kbps downlink drops speech, so the 24 kHz profile needs packet-rate/bitrate scheduling; A product decision on BLE Audio headset compatibility versus retaining classic Bluetooth


## What it asked for

### `c5-q4wq` (context) — product audio compatibility target
- why: The current bridge is classic-Bluetooth SBC-only while the proposed true 24 kHz path needs BLE Audio/LC3 or a dual-mode bridge. I need to know whether the owner values existing AirPods/classic-headset compatibility over a clean SWB product path.
- would change: If classic compatibility is mandatory, I will design a dual-mode migration and treat BLE Audio as optional; if not, I will optimize the next proposal and acceptance plan around BLE Audio/LC3 and 24 kHz end to end.

