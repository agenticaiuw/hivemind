# Harness derivation — faculty-judgement — round 94

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **24kHz audio feasibility** — Current prototype audio path is structurally CPU- and clock-limited: nRF9160 performs Opus encode (~15 ms) and decode (~25.4 ms per 60 ms frame), with both consuming ~87% of one core; playback is 24 kHz but I2S wire clock is 31,250 Hz and ESP32 bridge resamples again to fixed 44.1 kHz SBC.
  - evidence: get_hardware_spec(audio) and get_hardware_spec(pendant/bridge), Round 94

## Capabilities it proposed

### "“Pause there—I need to deal with this. When I say resume, continue exactly where we left off, and tell me if anything changed while I was away.”"
- **useful because:** Today an interruption loses the audio position and can leave a Mac/browser job running without a clear boundary. This gives the owner a dependable conversational pause: the pendant marks the spoken-word checkpoint locally, the relay freezes generation and records a resumable transcript/action boundary, the Mac/browser finish or safely pause work, and resume begins with a one-sentence delta before continuing. It is useful precisely because no single surface knows both what was heard and what changed elsewhere.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Realtime only for the short pause/resume utterance and delta wording; a cheaper background model compiles the checkpoint and compares job/browser receipts while paused.
- **latency:** Pause acknowledgement under 300 ms locally; resume acknowledgement under 1 s, delta under 3 s. Checkpoint writes are asynchronous and must never block audio.
- **cost:** About $0.002–$0.01 per interruption, dominated by background transcript summarization; no model call if the checkpoint is already structured.
- **security:** Checkpoint may contain private speech and logged-in page facts. Encrypt at rest, retain only the active thread until resolved, and never include page contents in the spoken delta unless the owner asks. Pausing must stop irreversible browser/Mac steps; resuming may continue only pre-approved reversible steps.
- **missing:** A durable cross-surface checkpoint schema keyed to spoken audio sequence and action/job IDs; A relay-side pause fence that is understood by the pendant and Mac/browser workers; A diff service that compares checkpoint-time receipts with resume-time state; A local pendant checkpoint marker that survives a dropped LTE link

### "“Give this one action a 10-minute authorization from my pendant, and revoke it automatically if I walk away or the facts change.”"
- **useful because:** The owner cannot safely delegate a narrowly bounded action today: a browser or Mac worker either lacks authority or receives a broad, stale approval. A physical pendant-held authorization would let them approve one prepared transaction while away from the screen, then make that authority expire, become unusable off-device, or be invalidated when the page, price, recipient, or other precondition changes. This is a new security primitive for a hive of agents, not another review queue.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Realtime is used only to identify the prepared action and speak the short confirmation; a cheap background verifier evaluates deterministic preconditions and expiry. No expensive model call is needed after issuance.
- **latency:** Issue/revoke acknowledgement under 500 ms when connected; workers must verify the token immediately before execution, adding under 100 ms. If the link is down, the pendant must show that no authorization was issued rather than guessing.
- **cost:** Under $0.001 per authorization for signed-token storage and deterministic checks; model cost is near zero unless the spoken scope is ambiguous.
- **security:** The token must be scoped to one canonical action hash, owner identity, target account, expiry, and preconditions; never grant general browser or Mac access. Store only a hash and minimal metadata on the pendant, use secure-element-backed keys in production, revoke on button hold or owner command, and require an explicit confirmation for irreversible actions. A lost pendant must be remotely revocable.
- **missing:** A pendant-side signing key and secure monotonic clock or nonce journal; A relay authorization service that issues single-action, expiring capability tokens and maintains a revocation list; Mac and browser executors that verify the token and re-check the action hash/preconditions at the final boundary; A physical confirmation interaction and clear LED/audio failure states; An audit receipt binding token, exact before/after diff, executor, and revocation/expiry reason


## Changes it proposed to its own stack

### `hardware` — Replace the prototype nRF9160-plus-ESP32 audio split with a production audio front end: an nRF5340-class dual-core application MCU (or equivalent DSP-capable MCU) with a dedicated 24 kHz voice codec/I2S clock, while retaining a separate LTE-M modem. Give the audio core independent DMA rings for capture/playback, hardware clock recovery, and a small nonvolatile checkpoint/event journal; keep the bridge as a transport fallback rather than the real-time audio clock master.
- **owner gets:** The current pendant spends roughly 87% of one Cortex-M33 core when Opus encode and 24 kHz decode overlap, then resamples twice (24 kHz to 31,250 Hz and 31,250 Hz to 44.1 kHz). That makes speech vulnerable to dropouts exactly when the owner talks over a response. The owner gets stable full-duplex voice, lower perceived latency, and resumable playback instead of a development-board audio chain that can go silent.
- effort: High: redesign PCB and power rails, port Zephyr audio/Opus transport, validate RF coexistence and Bluetooth bridge interoperability, and run long-duration packet-loss/audio-clock tests.  ·  risk: A new MCU/modem split can introduce clock drift, RF certification work, and firmware migration bugs. Recover with a board-level bypass mode that routes the existing nRF9160/ESP32 path, feature-flagged codec and transport, and golden audio loopback tests before enabling it for the owner.
- cost: Roughly $15–35 added prototype BOM versus the DK/ESP32 stack, plus PCB/NRE; likely modestly higher idle draw but lower peak DSP duty. API/model cost unchanged.  ·  latency: Removes two resampling stages and CPU contention; target 20–40 ms lower playout latency and fewer underruns. LTE round-trip remains the dominant delay.
- security: More firmware and a second MCU increase update and supply-chain surface. Require signed images, secure boot, encrypted checkpoint journal, and no raw audio persistence by default.
- depends on: Define and test the 24 kHz end-to-end packet/timestamp contract in relay and Mac pipeline; Implement underrun telemetry and checkpoint markers before the board redesign; Keep the existing ESP32 bridge compatibility mode during rollout

### `integration` — Add a cross-surface execution fence protocol: every Mac/browser step carries a stable causal thread ID, checkpoint sequence, reversibility, expiry, and expected postcondition. A pendant pause emits a signed fence event; workers stop before the next irreversible boundary and return receipts. On resume, the relay computes a state delta from receipts and only releases steps whose preconditions still hold.
- **owner gets:** Saying “pause” would become safe rather than merely conversational. The owner would not return to find an email sent or a browser form submitted while they were distracted, and would hear exactly what changed before work continues.
- effort: Medium-high: shared schema, worker adapters, durable event ordering, receipt verification, and adversarial tests for dropped links and duplicate events.  ·  risk: A lost fence could leave work running; fail closed at every irreversible boundary, use short leases plus server-side cancellation, and expose a visible stale-fence warning. Reversible work may be resumed automatically only with an owner preference.
- cost: Small storage and queue overhead; roughly $0.001–$0.005 per paused job for receipt/delta summarization, usually no extra model call.  ·  latency: Pause path under 500 ms for local acknowledgement; worker stop at next safe boundary may take seconds. Resume adds up to 2 s for receipt reconciliation.
- security: Causal IDs and receipts can reveal private page/job metadata; scope them per owner, encrypt, redact values by default, and require confirmation for irreversible release.
- depends on: Cross-surface checkpoint schema and pendant-local marker; Durable job receipts from /jobs/:jobId/receipts and browser command results; Worker support in mac-planner and browser-extension; Owner interruption policy

### `hardware` — Add a secure-element-backed authorization button to the production pendant: generate and hold a non-exportable device key, maintain a monotonic counter for one-time approvals, and expose a short-press/long-press state machine with distinct haptic/audio/LED confirmation. The pendant signs only a server-provided canonical action digest plus expiry and counter; it never signs arbitrary text or grants a standing session.
- **owner gets:** The owner gets a trustworthy physical “yes” they can give without returning to a laptop, while a stolen browser session or ambiguous voice transcript cannot turn that yes into unlimited control. It makes approval expire and become invalid when the prepared action changes.
- effort: Medium-high hardware and firmware revision: add a secure element, button debouncing and feedback, key provisioning, signed-token protocol, and manufacturing/recovery procedures; then integrate verification into Mac and browser workers.  ·  risk: Button misfires, lost-device recovery, clock/counter rollback, or confusing feedback could approve the wrong thing. Fail closed on uncertainty, require a deliberate long press for irreversible actions, show a spoken action summary before arming, use server nonce plus monotonic counter, and provide remote key revocation and re-provisioning.
- cost: Approximately $1–3 BOM increase for a secure element and button/feedback parts, plus manufacturing/NRE; negligible model/API cost and low firmware energy overhead.  ·  latency: Under 100 ms local signing/feedback; network verification remains the action boundary latency.
- security: Substantially improves least-authority control, but introduces key custody and provisioning risk. Use secure boot, signed firmware, per-device certificates, encrypted recovery records, and no raw approval content on flash.
- depends on: Single-action authorization-token schema and relay issuer; Final-boundary verification in Mac/browser executors; Audit receipts and remote revocation service; Production pendant rather than the current nRF9160 development kit


## What it asked for

_Nothing._
## Its own summary

Round 94 produced two concrete next steps. First, an owner-facing pause/resume capability that spans pendant audio checkpoints, relay generation, Mac jobs, and logged-in browser work; it acknowledges locally, fences irreversible work, and resumes with a concise state delta. Second, a hardware change for the 24 kHz goal: move real-time audio off the overloaded nRF9160/ESP32 resampling chain onto a dedicated DSP-capable audio core/codec, retaining the current path as a fallback. I also recorded the measured bottleneck (about 87% CPU with encode+decode and two resampling stages) and sent faculty-action the stable causal IDs, pre/postconditions, expiry, idempotency, and receipt requirements.

**Biggest unknown:** The orchestrator shows no items in the granted category this round, so I cannot verify which previously requested checkpoint, interruption, audio-delivery, or reconciliation primitives were actually implemented. What remains needed is an authoritative cross-surface checkpoint schema, a relay pause fence understood by Mac/browser workers, receipt-based state diffing, and a pendant-local marker that survives LTE loss; separately, the 24 kHz path needs an implementation/test decision about whether to optimize the current MCU or redesign the audio hardware.

