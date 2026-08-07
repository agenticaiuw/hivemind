# Harness derivation — unified — round 85

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If the pendant connection cuts out while I’m talking, keep the conversation alive: recover what I said, tell me what was heard, and continue from the last confirmed point without making me repeat myself.”"
- **useful because:** Current measurements show LTE-M half-duplex contention drops about 7.8 seconds of uplink while the agent speaks. A wearable should fail visibly and recover conversational state, rather than silently losing the owner's words. This requires local capture, relay acknowledgement/transcription, and Mac-side continuation—not a feature any one node can provide.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Realtime model only for the live turn and a short recovery sentence; use a cheaper background model to reconcile the recovered transcript and generate the durable receipt.
- **latency:** A local loss decision in under 300 ms; replay/acknowledgement within 2 s after reconnect; no more than one recovery prompt spoken aloud.
- **cost:** Usually one realtime turn; recovery adds roughly 1–2 short model calls and transient audio storage. Dominant cost is duplicated audio/transcription during replay, not routing.
- **security:** Audio fragments and transcript checkpoints leave the pendant and remain briefly in relay storage. Encrypt in transit, retain only until acknowledgement plus a short TTL, bind checkpoints to the authenticated session, and require confirmation before any resumed action that could send, delete, purchase, or otherwise be irreversible.
- **missing:** A device-local acknowledged-audio ring buffer and replay protocol; Relay sequence/ack checkpoints that survive reconnect and deduplicate packets; Mac planner input that can consume a recovered transcript as the same session turn; An owner-visible recovery receipt and retention/expiry controls

### "“Pause everything you’re doing, preserve exactly where you are, and tell me what is safe to resume.”"
- **useful because:** Today a long-running Mac or browser workflow can outlive the owner's attention, but there is no single spoken, cross-surface pause barrier. The owner needs to be able to interrupt from the pendant while the relay, Mac planner, and browser bridge atomically stop issuing new work, preserve the current step and evidence, and report whether anything was already committed. This is different from undo: it prevents the next action and makes the handoff understandable before resuming.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only to recognize and acknowledge the short interruption; use a cheaper background model to summarize checkpoints and classify resumable versus committed steps.
- **latency:** The pendant acknowledgement should arrive within 500 ms. New Mac/browser actions must be blocked within 1 s; checkpoint summarization may take up to 5 s.
- **cost:** One short realtime turn plus an inexpensive checkpoint summarization. Storage is small structured state and evidence metadata; raw screenshots or page text should be retained only under the existing job retention policy.
- **security:** The pause command must be authenticated to the active owner session and take precedence over queued work. It must not falsely claim that an already-submitted external transaction was stopped. Every surface needs an append-only barrier event, action sequence number, and receipt; resuming an irreversible step requires explicit confirmation.
- **missing:** A cross-surface pause barrier with monotonically ordered action epochs; Mac and browser adapters that check the barrier immediately before every side effect; A checkpoint schema containing current step, precondition, evidence, committed status, and safe resume point; A pendant spoken acknowledgement that distinguishes halted, in-flight, and already-committed work


## Changes it proposed to its own stack

### `firmware` — Implement an end-to-end conversation checkpoint protocol: packet sequence numbers and server ACKs, a bounded flash-backed uplink ring buffer on the pendant, reconnect replay with deduplication, and an explicit gap marker when the buffer is exhausted. Relay persists the last acknowledged sequence and transcript/session ID; Mac planner resumes only from acknowledged or replayed segments and emits a compact recovery receipt. Start with the current 16 kHz/16 kbps uplink and 24 kHz downlink; do not pretend this fixes the separate 24 kHz capture target.
- **owner gets:** When LTE-M contention or a dropped link loses speech, the owner gets a truthful “I recovered X seconds; Y was not heard” and can continue without repeating the entire request. It turns today's silent failure into bounded, recoverable behavior.
- effort: Medium-high: firmware ring buffer and protocol, Worker durable state, Mac session plumbing, dashboard receipt, and an RF fault-injection test matrix.  ·  risk: Replay duplication could repeat an action if transcript-to-action is not idempotent; enforce action gates on recovered turns and require confirmation for irreversible operations. Flash wear and buffer overflow are bounded with a fixed TTL/size and explicit gap events. Recover by starting a fresh turn when integrity cannot be proven.
- cost: Small relay D1/R2 metadata and temporary audio overhead; occasional duplicate realtime transcription. Firmware needs flash wear budgeting, not necessarily new silicon. Exact cost depends on replay volume.  ·  latency: Adds under 300 ms local buffering/ACK behavior and typically 1–2 s recovery after reconnect; normal connected turns should be unchanged.
- security: Session-bound sequence IDs, authenticated ACKs, encrypted transport, short retention, and deletion after receipt are required; never persist raw audio beyond the recovery window.
- depends on: The already-requested link-aware duplex audio governor; The already-requested incident diagnostics and delivery receipt surfaces; A server-side idempotency gate for actions derived from replayed transcripts

### `hardware` — Replace the nRF9160-DK prototype audio core in the product pendant with a two-domain design: retain a certified LTE-M/NB-IoT modem, but add a low-power audio/DSP MCU (at least 400 kB application RAM, hardware I2S/PDM, DMA, and a DSP/FPU) plus a real 24 kHz-capable microphone path and codec/bridge. Give the audio MCU ownership of capture, jitter buffering, Opus encode/decode, local checkpoint storage, and clock conversion; the modem MCU transports framed packets and survives radio stalls. Keep a physical privacy/mute latch independent of firmware.
- **owner gets:** The current prototype spends roughly 87% of one Cortex-M33 core encoding and decoding simultaneously, captures at 15,625 Hz despite a 24 kHz playback target, and loses speech under duplex LTE-M contention. A wearable built this way can deliver intelligible superwideband audio while preserving the owner's words during radio stalls, instead of trading audio quality against reliability.
- effort: High: select and certify modem/audio parts, redesign PCB and power tree, port Zephyr/audio firmware, validate RF coexistence and acoustic tuning, then run production EVT/DVT.  ·  risk: More components and clock domains create integration and battery risks; modem/audio IPC failure must fail closed to local mute and preserve a diagnostic marker. Recover by shipping the current DK as a development fallback and qualifying the new audio path behind a feature flag.
- cost: Rough prototype delta of $15–$35 BOM and roughly 10–30 mA average additional draw depending on DSP and codec; production cost could fall after volume. API/model cost is unchanged, though fewer retranscribed/recovered turns reduce it.  ·  latency: DMA and a dedicated audio core should reduce encode/decode scheduling jitter; IPC adds under 10 ms if framed correctly. Radio latency remains the dominant factor.
- security: A hardware mute latch must disconnect microphone power or data, not merely set a software flag. Secure-boot both MCUs, authenticate IPC frames, and avoid storing raw audio outside the bounded recovery buffer.
- depends on: The requested 24 kHz target architecture and end-to-end audio acceptance thresholds; The requested link-aware duplex audio governor; A production pendant specification beyond the nRF9160 DK

### `integration` — Add a cross-surface action-epoch lease to the job protocol. Every relay-dispatched Mac or browser side effect carries {jobId, epoch, stepId, preconditionHash}; the relay can atomically advance the epoch to PAUSED. Mac and browser bridges reject stale epochs before execution, while in-flight operations report an outcome of not-started, started-not-confirmed, or committed. Persist a checkpoint and evidence pointer for each transition, then expose one spoken/dashboard receipt.
- **owner gets:** The owner can stop a workflow from the pendant without racing the Mac or browser. They get a precise answer about what happened, rather than an unreliable cancellation message or a need to reconstruct state from logs.
- effort: Medium: shared protocol and D1 schema, bridge preflight checks, job-worker integration, and race-condition tests with delayed browser and shell actions.  ·  risk: A pause arriving after an external site accepts a request cannot undo that request; the receipt must say so. A stale client could otherwise execute after pause, so fail closed on missing or expired epochs and require a fresh lease to resume.
- cost: Negligible model cost; a few durable metadata writes per action and modest dashboard storage. No new hardware required.  ·  latency: One lightweight preflight/lease check per side effect, targeting under 50 ms locally and under 200 ms through the relay; pause propagation under 1 s.
- security: Improves containment by making pause authoritative and auditable. Epoch tokens must be unguessable, scoped to the authenticated owner session, and never treated as proof that an external transaction was reversible.
- depends on: A durable job runner that honors cancellation; Browser request IDs and tab/session affinity; The existing job receipt and undo records; A shared action idempotency gate


## What it asked for

_Nothing._
