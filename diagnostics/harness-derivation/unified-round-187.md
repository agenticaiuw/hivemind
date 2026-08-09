# Harness derivation — unified — round 187

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep my conversation going when the Mac, LTE link, or USB path drops; switch transport without repeating or losing a turn, and tell me only if continuity cannot be preserved."
- **useful because:** The pendant is useful only if a transient link failure does not make the owner repeat themselves. This is a cross-surface behavior: the worn device owns sequence boundaries, the Mac owns USB today, the relay owns job continuity, and the audio layer proves whether a turn was actually delivered.
- **path:** pendant → relay → mac-bridge → dashboard-ux
- **model tier:** Realtime for the active turn; deterministic state machine and background reconciliation for recovery.
- **latency:** Transport decision within 150 ms of heartbeat/failure; no audible gap beyond one 60 ms audio frame where possible; reconciliation under 2 s after reconnect.
- **cost:** Negligible model cost during healthy calls; roughly $0.001–$0.01 per recovered turn for metadata and any needed low-tier summary, dominated by duplicate suppression and TTS only if replay is required.
- **security:** Sequence numbers and authenticated session/turn IDs must prevent replay or cross-session audio injection. Do not persist raw audio except the existing failure-path spool. Require explicit owner notice before replaying an ambiguous turn.
- **missing:** A production transport arbiter that joins LTE and USB ownership at turn boundaries; Relay job lease/requeue for Mac death; End-to-end use of audio_delivery_ack_queue and duplex_audio_congestion_guard; A compact cross-surface continuity record with last committed uplink/downlink sequence

### "Continue the interrupted task safely after the Mac or browser comes back, but never repeat an action that might already have happened; show me the exact step it is waiting on when it cannot decide."
- **useful because:** The system already records action intent, replay safety, approvals, and receipts, but startup never invokes the decision engine and ordinary ledgers are left open. Making this callable turns a dangerous silent failure into an honest recovery flow for real multi-step work.
- **path:** mac-planner → mac-vision → browser-extension → relay → pendant → dashboard-ux
- **model tier:** Deterministic ledger/receipt engine first; background planner only for explaining an ambiguity, never for deciding to replay an unknown action.
- **latency:** Detect on surface recovery within 5 s; produce a dry-run decision list within 1 s; require physical approval for risky steps at the next owner conversation.
- **cost:** Near-zero for ledger classification; under $0.01 per recovery when a low-tier explanation is generated. No model call for idempotent/additive steps.
- **security:** Gate replay on replaySafety, not reversibility: auto-resume only idempotent/additive steps; ask for unrepeatable/unknown. Bind any approval to plan digest, world fingerprint, expiry, and the physical transaction nonce. Never infer that an open ledger means an incomplete action.
- **missing:** Orchestrator closeLedger call for successful plans; Startup scanner that distinguishes genuinely interrupted ledgers; Relay job lease_until and requeue sweep; A production caller that executes only the planResume runnable subset; Dashboard/pendant presentation for ask/blocked decisions

### "Show me every fact you inferred about me, let me erase one fact and all of its copies, and report what is still pending off-device instead of claiming it is gone."
- **useful because:** The owner explicitly cannot currently see or selectively delete extracted facts. This makes memory accountable without deleting the action audit trail: the Mac can present the evidence, the relay can request replicated erasure, and the pendant can confirm the result privately.
- **path:** mac-planner → relay → browser-extension → pendant → dashboard-ux
- **model tier:** Deterministic index/evidence traversal for listing and deletion; background model only to render human-readable labels, never to choose deletion scope.
- **latency:** List in under 2 s locally; local deletion receipt under 1 s; off-device propagation status within 30 s and visibly marked requested-and-pending until acknowledged.
- **cost:** Negligible API cost for indexed reads and tombstones; occasional low-tier summarization under $0.005 per fact batch.
- **security:** Require explicit confirmation for each deletion; bind the tombstone to fact ID, derived-copy IDs, evidence capsule IDs, and relay replication status. Preserve job history and action receipts. Redact evidence by default and never send raw audio to the relay for this feature.
- **missing:** A read API for extracted facts with stable IDs and evidence capsules; A transactional tombstone that fans out to context graph, facts.json, derived copies, and relay replicas; A user-facing dashboard/pendant confirmation and retry state; A relay acknowledgement route for replicated erasure


## Changes it proposed to its own stack

### `firmware` — Add a bridge-side audio admission controller on the ESP32 that measures A2DP queue depth and SBC callback lateness, caps buffering below the known 44 kB starvation cliff, and emits a compact bridge_delivery_state (queued_ms, underruns, callback_late, last_sequence) alongside the existing audio delivery acknowledgements. Keep the Nordic 24 kHz/60 ms framing unchanged; this is specifically the 44.1 kHz stereo A2DP boundary.
- **owner gets:** When Bluetooth headphones go silent, the owner should hear a bounded recovery or get an honest 'headphones lost audio' indication, not continue speaking into a conversation that the bridge is discarding. The relay and Mac can then stop replaying audio that already reached the bridge and choose a safe fallback.
- effort: Moderate: instrument firmware/esp32-airpods-bridge/src/main.cpp, add bounded queue watermarks and a serial/USB status frame, then run long-duration tests across reconnects. No new radio protocol is required if the status rides the existing bridge receipt path.  ·  risk: Too-aggressive admission control could create audible gaps; recover by retaining the current static buffer as a fallback profile and gating the controller behind a diagnostic flag until soak tests pass. Do not increase the buffer past the measured cliff.
- cost: No model/API cost. A firmware-only change; RAM remains bounded below 44 kB. If later productized, an ESP32-class bridge remains inexpensive, but this DK measurement must not be treated as product power or thermal data.  ·  latency: Adds under 1 ms of local queue accounting; avoids multi-second silent buffering and makes loss visible within one A2DP callback interval.
- security: Sequence and state counters must be authenticated/bound to the active conversation; status contains no audio or headphone identity. Reject stale bridge state after a turn/session change.
- depends on: audio_delivery_ack_queue must accept bridge queue/underrun fields; A production USB fallback audio session must expose bridge status to the Mac/relay; audio_path_diagnostic_fixture should include A2DP callback-lateness and queue-watermark assertions

### `hardware` — Replace the prototype ESP32 SBC-only A2DP source in the production audio route with a bridge that has hardware-timed Bluetooth LE Audio/LC3 (or add a dedicated LC3-capable companion beside the Nordic), while retaining USB serial as the bench and recovery transport. Define a synchronized clock handoff: the pendant's monotonic frame timestamps become the bridge's playout clock, and the bridge reports rendered-frame position rather than merely accepted bytes.
- **owner gets:** The owner gets conversation audio that remains intelligible and correctly timed in real headphones instead of depending on a prototype's fixed 44.1 kHz SBC path and a fragile large buffer. Long answers stop drifting, reconnects recover faster, and the system can know whether sound was actually rendered.
- effort: High: select a BLE Audio-capable module, implement LC3 transport and clock synchronization, redesign the bridge firmware and enclosure/power path, then repeat hardware latency, loss, and rendered-frame tests. Keep the current ESP32 bridge as a development fixture during migration.  ·  risk: A new radio/audio stack can introduce pairing failures, interoperability bugs, and worse battery life. Recovery is a compile-time transport fallback to the existing SBC bridge and USB path; ship only after measured rendered-frame continuity and headphone compatibility tests.
- cost: Adds a dedicated companion/module and certification effort; exact BOM and power cannot be quoted until the owner's wearable battery/size targets are set. Runtime codec cost moves off the nRF9160, preserving its measured 24 kHz CPU headroom.  ·  latency: Potentially lowers codec and buffering latency versus SBC/A2DP, but the target must be measured end to end; clock correction should stay below one audio frame and never conceal drift by accumulating unbounded audio.
- security: Use authenticated device bonding, per-session frame counters, and explicit privacy-latch propagation. Do not expose raw PCM over an unauthenticated bridge; USB diagnostic mode must be visibly scoped to local use.
- depends on: A product decision on standalone-vs-companion transport and wearable power/size limits; A production bridge delivery receipt that reports rendered playout position; The existing 24 kHz/60 ms pendant framing and duplex congestion guard as the compatibility baseline

### `hardware` — Add an independent low-power supervisor/load-switch path to the wearable radio/audio assembly, with separate reset domains for the nRF9160 and audio bridge and a latched fault counter readable over USB/LTE. On a bounded modem, I2S, or bridge-heartbeat timeout it power-cycles only the failed domain, preserves the conversation/session sequence in retained state, and emits one recovery receipt when service returns.
- **owner gets:** A pendant that silently wedges until it is physically unplugged is not wearable. The owner should be able to keep wearing it and have a stalled modem or audio bridge recover itself without losing the fact that recovery happened.
- effort: High hardware/firmware integration: choose supervisor and load-switch parts, route reset domains, define heartbeat and retained-state protocol, and validate brownout, repeated-fault, and in-call recovery on real boards.  ·  risk: An incorrect reset threshold could cause reboot loops or interrupt valid audio. Use escalating backoff, a hard cap on autonomous resets, and a visible LED fault pattern; preserve USB service mode so the owner can recover a device that exceeds the cap.
- cost: Small additional BOM and board area, with microwatt-to-low-milliwatt supervisory draw depending on parts. No model/API cost. Product power and enclosure targets remain owner decisions.  ·  latency: A failed domain would be unavailable for several seconds during power-cycle, but this is bounded and preferable to indefinite silence; retained sequence state prevents an apparent duplicate turn afterward.
- security: Fault receipts must contain counters and component IDs only, not audio or content. Protect reset policy and retained counters from unauthenticated remote writes; privacy latch state must survive domain resets.
- depends on: A defined cross-domain session sequence/continuity record; USB/LTE delivery of recovery receipts; Product-level power, thermal, and battery targets before selecting supervisor parts


## What it asked for

_Nothing._
## Its own summary

This round recorded three owner-facing capabilities: seamless conversation continuity across LTE/USB/Mac failures, safe replay-aware recovery of interrupted Mac/browser work, and a visible, individually erasable extracted-fact view with replicated deletion status. I also recorded a bridge-specific firmware change: bounded ESP32 A2DP admission control and queue/underrun telemetry below the measured 44 kB silence cliff. Live discovery confirms the Mac agent is healthy and the HUZZAH32 bridge remains a prototype with SBC-only 44.1 kHz stereo; the pendant and bridge are not represented as registered relay devices yet.

**Biggest unknown:** The remaining critical unknown is implementation status of the newly accepted USB fallback session on the physically connected serial devices, plus whether bridge delivery acknowledgements are currently wired into the Mac/relay. I already requested the USB integration context and will not re-request it this round. Until that arrives, I can specify and edit code, but cannot honestly claim a live end-to-end USB conversation or bridge receipt.

