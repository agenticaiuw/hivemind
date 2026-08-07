# Harness derivation — faculty-judgement — round 117

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I get interrupted halfway through something, save exactly where we were and let me safely resume it later from the pendant."
- **useful because:** Today a conversation, browser tabs, and a half-filled form can all be lost when attention shifts. This creates a durable, human-readable escrow: the original request, evidence gathered, reversible changes already made, exact next step, expiry/deadline, and what still needs approval. The owner can resume without repeating themselves or accidentally sending a stale action.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → dashboard
- **model tier:** Realtime model only for the brief spoken interruption/resume exchange and final approval question; a cheaper background model compiles evidence and a deterministic state machine validates and resumes the plan.
- **latency:** Capture interruption in under 1 second; resume card spoken in under 3 seconds. Background compilation may take minutes while the owner is away.
- **cost:** Roughly $0.01–$0.05 per background packet, dominated by private-page extraction and audio generation; resume voice turn uses the normal realtime budget.
- **security:** Private tab contents and draft data leave the browser only through the authenticated relay. Never persist secrets or raw screenshots by default. Sending, deleting, purchasing, or submitting remains a fresh confirmation. Expire stale packets and provide one-tap discard.
- **missing:** A durable interruption-escrow state machine with explicit states (captured, awaiting-owner, stale, resumed, discarded); Atomic checkpointing of Mac jobs and browser command queues so a checkpoint cannot claim an action that did not complete; A pendant-readable resume queue with offline acknowledgement and replay protection; Owner-visible packet diff showing what changed since capture

### "When I leave something somewhere or put something on hold, let me ask later where it is and what I was supposed to do with it."
- **useful because:** People lose physical objects and the intention attached to them, not just the objects themselves. A quick pendant button press or spoken 'remember this' would create a private, time-and-place memory; later the pendant can answer 'where are my passport and the forms I still need to send?' instead of forcing the owner to reconstruct the moment.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → dashboard
- **model tier:** Realtime only for capture confirmation and the later short answer. A cheaper background model performs entity linking and summarizes the memory; vision runs only when the owner explicitly asks to inspect a photo or scene.
- **latency:** Capture acknowledgement under 500 ms locally, even without connectivity. Retrieval answer under 3 seconds when online; offline retrieval from the pendant's recent index under 1 second.
- **cost:** About $0.005–$0.03 per memory after capture, dominated by optional transcription/vision embedding; negligible cost for offline text-only entries.
- **security:** This can reveal home layout, possessions, travel documents, and locations. Store recent entries encrypted, default to coarse location and short retention, never upload a scene/photo without explicit consent, and require confirmation before sharing a location or acting on an attached intention.
- **missing:** A pendant-local encrypted memory capsule with button-triggered audio/text capture and bounded retention; A cross-surface entity-and-intention linker that can join a spoken capture to Mac notes, calendar, email, browser pages, and optional photos; An owner-facing retrieval UI that shows provenance (capture time, place, transcript/photo) and lets the owner correct or delete it; Optional low-power BLE/UWB tags or phone-assisted location if the owner wants reliable object location rather than remembered placement


## Changes it proposed to its own stack

### `integration` — Add an interruption-escrow coordinator between the existing planner, job runner, browser queue, receipts, and pendant audio pipeline. At every irreversible boundary and on link loss, atomically write a checkpoint containing intent hash, completed action receipts, browser tab/session IDs, evidence references, next safe step, required confirmation, expiry, and a monotonic resume token. Expose a compact spoken resume queue and a dashboard diff; resuming revalidates page freshness and job state before executing anything.
- **owner gets:** A dropped connection or sudden distraction would stop being a lost half-finished task. The owner can hear one accurate sentence later and continue exactly where they left off, without duplicate clicks or stale submissions.
- effort: Medium-high: coordinator/state machine, transactional hooks in Mac and browser runners, pendant queue protocol, and crash/replay tests.  ·  risk: A bad checkpoint could replay an action twice or present stale evidence. Default to no-op on uncertainty, require confirmation for irreversible steps, use idempotency keys and receipts, and allow discard/undo. Recovery is to invalidate the resume token and leave the underlying job untouched.
- cost: Negligible storage/compute; one small background summarization call per interrupted packet, with optional TTS cost only when surfaced.  ·  latency: Under 1 second to checkpoint; 1–3 seconds to produce a spoken resume card. No added latency on ordinary completed actions beyond a small write.
- security: Persist references and hashes rather than raw page content or secrets; enforce per-owner auth and short TTL; redact sensitive fields from spoken summaries.
- depends on: Durable job runner and browser command queue must emit atomic action receipts; Pendant delivery acknowledgement/offline queue; Cross-surface state persistence and stale-evidence revalidation

### `hardware` — Replace the prototype's fixed 15,625 Hz I2S microphone clock path with a clocked 24 kHz-capable digital MEMS microphone (or add an ASRC front end) and a shared clock plan that keeps Opus encode at true 24 kHz while preserving the existing 31.25 kHz playback wire clock. Add firmware capability negotiation so the relay never labels 15.625 kHz capture as 24 kHz, and fall back explicitly when the old board is attached.
- **owner gets:** The pendant would capture speech with the same superwideband bandwidth it can already play, improving recognition and natural turn-taking instead of silently upsampling narrowband audio.
- effort: High: board spin or audio front-end redesign, Zephyr I2S/clock driver work, Opus 24 kHz encode tuning, relay negotiation, and acoustic/regression testing.  ·  risk: Clock drift, increased CPU/RAM use, battery impact, and incompatibility with the prototype bridge. Recover with negotiated 16 kHz mode, watchdog-reset-safe buffering, and an explicit sample-rate badge in diagnostics.
- cost: Prototype redesign roughly $5–$15 in added audio/clock components per unit and perhaps 10–25 mW while recording; API cost is unchanged or slightly lower if 24 kHz Opus replaces server resampling.  ·  latency: Potentially +10–20 ms capture buffering; tune to retain under 200 ms end-to-end turn latency.
- security: No new data class; audio remains encrypted in transit. Diagnostics should report sample rate without retaining raw audio.
- depends on: 24 kHz acceptance criteria and relay codec negotiation; Measured CPU headroom for simultaneous encode/decode on the nRF9160; A/B acoustic test against the current 15,625 Hz microphone

### `firmware` — Add a local 'place-memory capsule' to the pendant: a long-press captures up to 10 seconds of audio plus timestamp, monotonic event ID, and coarse device/location context; encrypts it at rest, keeps a bounded ring of the newest entries, and uploads only after an explicit sync policy permits. The server returns a signed receipt and can tombstone individual entries; retrieval must work from the local ring when offline.
- **owner gets:** The owner can preserve a fleeting physical-world fact with one deliberate gesture and recover it later even when the network or Mac is unavailable, without keeping the microphone continuously active.
- effort: Medium firmware plus relay protocol work; requires encrypted storage, button debounce/UI feedback, upload retry, tombstones, and a small retrieval endpoint.  ·  risk: Accidental captures, sensitive recordings, flash wear, and lost keys could expose private information. Mitigate with a short fixed maximum, LED/haptic/audio acknowledgement, retention limits, authenticated encryption with device-bound keys, and an unmistakable delete gesture.
- cost: No API cost for local capture; roughly 1–3 MB flash reserved for a bounded ring depending on codec. Estimated under 5 mW average while recording, plus brief radio upload cost.  ·  latency: Immediate local acknowledgement; upload is deferred and must not block conversation. Offline retrieval is sub-second for recent entries.
- security: This creates a new sensitive data class (location-linked personal memory). Encrypt locally and in transit, minimize metadata precision, prohibit background capture, and require explicit owner opt-in before cloud sync.
- depends on: A device key/secure-storage abstraction; A relay endpoint for signed, idempotent memory receipts and deletion tombstones; Owner retention and sync policy


## What it asked for

_Nothing._
## Its own summary

Round 117 produced two concrete additions beyond the backlog: (1) an interruption-escrow coordinator that atomically checkpoints intent, receipts, browser session, evidence freshness, next step, and confirmation requirements, then offers a replay-safe spoken resume card; and (2) a hardware/audio redesign for genuine 24 kHz microphone capture rather than labeling the current 15,625 Hz input as superwideband. The key owner-facing boundary is: resume may revalidate and prepare, but never execute a stale or irreversible step without fresh confirmation.

**Biggest unknown:** I still need the authoritative 24 kHz acceptance criteria and the actual cross-surface persistence/receipt transaction primitives to size the coordinator correctly. The current pendant is explicitly a prototype: simultaneous Opus encode/decode is already about 87% of one core, so the hardware/firmware tradeoff cannot be finalized from the available facts. Accessibility/TCC grants remain owner-side and denied; I did not re-request them.

