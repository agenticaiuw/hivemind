# Harness derivation — faculty-action — round 86

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If the pendant's reply was clipped, garbled, or interrupted, say “repeat that” or press the button once and have the system resend only the missing part, then report whether recovery succeeded."
- **useful because:** A dropped LTE packet or speaker underrun should not make the owner repeat an entire request. The pendant can detect its own playback gap, the relay knows the exact PCM receipt, and the Mac can regenerate only when the original is unavailable.
- **path:** pendant → relay-realtime → mac-planner → unified → dashboard
- **model tier:** Realtime only for the owner's short recovery command; no LLM for packet repair. Use the cheaper background tier to reconcile telemetry and regenerate speech only when needed.
- **latency:** Detect locally within 150 ms; resume cached audio immediately; relay resend target under 1 s; fallback regeneration under 4 s.
- **cost:** Usually near-zero model cost because the original PCM is reused; fallback TTS is one small speech generation, dominated by audio transfer and retention.
- **security:** Audio receipts and telemetry must be authenticated and short-lived; never expose prior private speech to another device. Require confirmation only if recovery would replay a sensitive response after a long delay.
- **missing:** Pendant playback sequence numbers, underrun/CRC telemetry, and a local replay buffer; Relay endpoint to fetch/resume an audio segment by pipelineId and sample range with idempotency; Mac-side audio repair/regeneration worker and a user-visible recovery receipt; Dashboard timeline showing which samples were replayed and whether fallback TTS occurred

### "When I tell the pendant “finish this when I’m at my Mac,” have it preserve the exact spoken intent, wait until my Mac and browser session are both present, complete the reversible parts, and leave me a proof-backed review packet instead of making me repeat myself."
- **useful because:** Today a request made while walking cannot reliably become a finished computer task later. This would turn the pendant into a durable handoff point: the wearable captures intent, the always-on relay preserves it, the Mac acts only when reachable, and the browser supplies authenticated context.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard → unified
- **model tier:** Use realtime only to capture and acknowledge the short handoff. Use a cheaper background model to normalize the intent, select the Mac/browser execution plan, and summarize the completed packet.
- **latency:** Immediate local acknowledgement; handoff persistence under 1 second; execution starts within 10 seconds of both presence signals; review packet ready within the task's normal duration.
- **cost:** One short realtime turn plus low-cost background planning; browser and Mac work dominate latency, not inference.
- **security:** Encrypt the intent and bind it to the owner's device identity; do not execute while only the pendant is present. Browser mutations remain reversible or stop at a review gate, and the packet must include before/after evidence and timestamps. Expire stale handoffs rather than acting on ambiguous old speech.
- **missing:** A durable handoff object carrying raw transcript/audio reference, normalized goal, expiry, sensitivity, and required surfaces; Presence attestation from both the Mac bridge and the authenticated browser session, not merely an online heartbeat; A scheduler that wakes the handoff when those surfaces co-occur and leases it to one executor; A review-packet schema linking browser evidence, Mac receipts, and the original pendant capture; Pendant UI for listing, cancelling, or deferring pending handoffs without network access


## Changes it proposed to its own stack

### `firmware` — Add an authenticated audio playback journal to the pendant: every response is addressed by pipelineId plus 20 ms frame sequence, with a 2–4 second ring buffer, CRC/underrun markers, and a single-button replay request. On reconnect it posts a compact missing-range event; the relay serves only those ranges and the Mac falls back to TTS when the source PCM has expired.
- **owner gets:** When speech drops out, the pendant repairs the sentence instead of leaving the owner guessing or forcing them to ask the whole question again. It also makes the 24 kHz path measurable in real use.
- effort: Medium firmware + relay integration; requires a real pendant for power/RAM testing and a simulator acceptance test first.  ·  risk: Ring-buffer pressure or replay loops could stall playback; cap retries, evict oldest frames, and expose a clear audible failure tone plus receipt. Do not flash until the owner approves and a device is connected.
- cost: Negligible runtime/API cost; 2–4 seconds of mono s16le at 24 kHz is about 96–192 KiB, so storage should be external/streamed rather than consuming application RAM. Fallback TTS costs one speech call.  ·  latency: Local repair is sub-second; network range fetch typically under 1 s; fallback regeneration several seconds.
- security: Bind requests to authenticated pipeline/session IDs, expire audio quickly, and avoid logging PCM. Replay of sensitive audio after a delayed reconnect should be opt-in or require a button press.
- depends on: A connected pendant and measured RAM/storage budget; Relay range-fetch and idempotent audio-segment endpoint; Mac audio worker that can correlate pipeline receipts and regenerate expired PCM; 24 kHz acceptance criteria and device-side audio-path probe

### `integration` — Introduce a cross-surface Handoff Lease protocol. A pendant-originated handoff stores an immutable capture pointer plus a normalized goal and expiry; the relay waits for cryptographically attested Mac-bridge and browser-session presence, grants one short lease to the executor, and collects Mac receipts plus browser evidence into a single review packet. Leases expire and return to pending without duplicate execution.
- **owner gets:** The owner can speak an unfinished task once while away and trust that it will resume at the right machine, with an understandable proof of what happened, rather than losing the request or accidentally running it twice.
- effort: Substantial relay/database integration, Mac and browser heartbeat changes, pendant pending-handoff controls, and dashboard review UI; requires protocol and failure-injection tests.  ·  risk: Stale or duplicated leases could perform an unintended action. Use idempotency keys, explicit expiry, surface identity binding, and stop before irreversible browser actions. If either presence attestation disappears, pause and report rather than continue.
- cost: Small durable metadata storage and occasional background polling; no repeated realtime inference after capture. Evidence retention cost is bounded by packet TTL.  ·  latency: Adds at most one presence/scheduling delay; execution itself is unchanged. Offline pendant acknowledgement remains immediate.
- security: Raises security requirements because authenticated browser context is intentionally joined to wearable intent. Encrypt handoff payloads, minimize transcript retention, scope leases to named surfaces, and redact secrets from review packets.
- depends on: A durable handoff record and scheduler; Attested presence rather than simple online status; Typed cross-surface receipt/evidence schema; Offline pendant controls for cancel/expiry; Owner-defined policy for irreversible actions


## What it asked for

_Nothing._
## Its own summary

Discovered that no pendant is currently connected; only the Mac bridge is online. The live pipeline already renders and uploads 24 kHz mono PCM, and the pendant has microSD reserved strictly as a failed-upload buffer. I recorded a new cross-device capability and firmware change for frame-addressed audio recovery: local underrun detection/replay, relay range fetch, and Mac fallback regeneration, with authenticated receipts. Still needed: a real pendant/device test target, measured 24 kHz acceptance criteria, and the pending audio-path probe/firmware-build access; no unattended flash or build should occur.

**Biggest unknown:** Whether the actual product's RAM, speaker path, and transport can sustain a 2–4 second frame-indexed replay buffer; the current Nordic kit is explicitly prototype hardware and there is no connected device to measure.

