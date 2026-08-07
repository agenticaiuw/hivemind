# Harness derivation — faculty-judgement — round 116

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep my pendant useful all day: when its battery or connection is getting weak, quietly move non-urgent work to my Mac or the relay, save anything needed for later, and only interrupt me if I must act before the device goes offline."
- **useful because:** The pendant is the one surface that follows the owner, but it cannot be the only place work lives. This would preserve briefings, queued requests, and follow-ups through battery drain, Wi‑Fi loss, or leaving the Mac behind—without making the owner micromanage which machine is awake.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → dashboard
- **model tier:** Use a cheap background model for forecasting battery/connection risk and classifying urgency; use realtime only for the spoken warning or owner conversation. The Mac/relay should execute deterministic migration and checkpoint logic without an LLM where possible.
- **latency:** Health scoring every 1–5 minutes; migration/checkpoint within 10 seconds of a threshold; spoken warning under 1 second once a genuinely time-sensitive item is identified. No warning for routine degradation.
- **cost:** Near-zero model cost for deterministic telemetry and queue migration; occasional small background-model calls for urgency classification (sub-cent scale). Main cost is durable queue/checkpoint storage and a few relay wakeups.
- **security:** Battery, network, and queued-work metadata leave the pendant only to the authenticated relay/Mac; page contents and secrets must not be copied merely because a migration occurs. Require confirmation before migrating an irreversible action or sending anything; preserve owner-visible receipts and allow cancellation.
- **missing:** Pendant battery/link telemetry exposed to the relay with hysteresis and last-known timestamp; A portable, resumable job checkpoint format with leases and deduplication across relay and Mac; Urgency/deadline metadata on queued work and a policy that distinguishes safe background migration from owner approval; A reconnect handoff protocol that lets the pendant retrieve a compact spoken summary and pending actions after an outage


## Changes it proposed to its own stack

### `relay` — Add an energy-and-link-aware work lease coordinator between pendant, relay, and Mac. It polls authenticated health/ops telemetry, assigns every queued job a deadline, reversibility, required surface, and checkpoint cursor, then uses hysteresis thresholds to checkpoint and lease safe work to the relay/Mac before pendant loss. On reconnect it reconciles leases by idempotency key and emits one compact recovery receipt; it must never silently transfer an irreversible step.
- **owner gets:** A dying or disconnected pendant would stop being a cliff. The owner would hear only the few things that truly cannot wait, while ordinary research, briefings, and drafts finish elsewhere and are ready when the pendant returns.
- effort: Medium-high: typed job schema and migrations, relay coordinator, pendant telemetry event, Mac handoff endpoint, reconnect reconciliation, failure-injection tests for power loss and duplicate execution.  ·  risk: A stale battery reading could migrate too late or wake the Mac unnecessarily; use hysteresis, timestamps, conservative defaults, and leases. Duplicate work is contained by idempotency keys; unresolved jobs remain visibly pending rather than claiming success. Recovery is cancel/undo where supported plus a receipt explaining the boundary.
- cost: Small relay storage and polling overhead; occasional Mac wake/network traffic. No meaningful per-request model cost if urgency and thresholds are deterministic.  ·  latency: Adds seconds of checkpoint overhead only near a risk threshold; normal interactive requests unchanged. Reconnect recovery should be available within one health poll.
- security: Authenticated device-to-relay telemetry only; do not replicate private page contents unless the job already authorized it. Preserve per-surface provenance and require owner confirmation at irreversible checkpoints.
- depends on: A durable cross-surface job/checkpoint contract; Pendant battery and link telemetry; Owner-approved urgency and quiet-hours policy; Typed receipts and idempotency already present in the job runner

### `hardware` — Replace the prototype pendant’s single-button/single-LED interaction with a physical two-position microphone privacy switch that electrically disconnects the microphone bias line, plus a high-visibility LED driven from the same hardware state. Add a small fuel-gauge/RTC-backed event counter so firmware can report privacy transitions and power state after reconnect; the relay and Mac must treat a hardware-muted interval as authoritative and reject audio capture or deferred transcription from it.
- **owner gets:** The owner can be certain—without trusting an AI explanation—that the pendant is not listening. They can enter a meeting, bedroom, or private conversation with one tactile motion, see the state, and later verify exactly when it was muted. That trust is unavailable from software mute alone.
- effort: High: revise the wearable PCB/enclosure and microphone power path, validate pop/noise behavior, add sealed tactile switch and LED visibility tests, implement firmware state/event logging, and thread the authoritative state through relay, Mac, and dashboard. The current nRF9160 development kit is explicitly provisional, so this belongs in the product hardware rather than a workaround.  ·  risk: A damaged or ambiguous switch could leave the owner uncertain; use hard two-state detents, a fail-quiet electrical design, startup self-test, and a visible disagreement fault. Cutting microphone power may require codec reinitialization and lose the first audio frame after unmute; announce readiness with haptic/LED feedback. Recovery is physical switch movement, not a hidden software override.
- cost: Roughly $2–6 BOM increase for switch, LED driver, fuel gauge/RTC support, PCB/enclosure changes, plus validation NRE; negligible steady-state power increase and likely a small power saving while muted. No API/model cost.  ·  latency: Unmute-to-ready may add 100–300 ms for codec startup; mute is immediate at the electrical path. Privacy-state propagation to relay/Mac should be best-effort and never delay the local cutoff.
- security: This is a defense-in-depth boundary: audio cannot leave the device while the switch is muted. Log only transition timestamps/counters, not audio; authenticate state events and make the physical state higher priority than server commands.
- depends on: A firmware privacy-state event and durable transition counter; Relay/Mac audio pipelines honoring hardware mute as an authoritative deny; Dashboard/briefing UI that shows the last observed physical privacy state and any telemetry gap


## What it asked for

_Nothing._
## Its own summary

I found no new granted tools this round, but proposed a genuinely connective capability: energy/link-aware continuity. A coordinator would checkpoint safe work and move it between pendant, relay, and Mac before battery or connectivity loss, then reconcile on reconnect and warn only about urgent actions. I also specified the relay change needed to make this real, grounded in the prototype pendant’s 211,608 B RAM and nRF9160 platform.

**Biggest unknown:** The system still lacks trustworthy pendant battery/link telemetry, a durable cross-surface checkpoint/lease contract, and explicit urgency metadata. I still need those primitives—not another model tool—before this can be implemented safely. Browser remains offline and Mac Accessibility/Screen Recording grants remain owner-blocked.

