# Harness derivation — unified — round 66

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep my routines correct when I travel or my Mac and pendant disagree about the time.”"
- **useful because:** The system currently has America/Chicago in owner memory but the live Mac reports America/New_York. A daily routine can therefore run an hour early or late while still appearing successful. This capability makes time-sensitive voice prompts, browser jobs, and Mac reminders agree, and asks once when the evidence conflicts instead of silently choosing.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Background model for routine reconciliation and timezone-change detection; realtime only for the short spoken conflict question and final answer.
- **latency:** Normal routine execution stays unchanged; conflict detection is sub-second at scheduling time, with a 5–10 second spoken clarification only when needed.
- **cost:** <$0.01 per routine-day in the common case (rule-based timezone and schedule evaluation); <$0.05 when a model must explain a conflict. Dominant cost is model explanation, not routing.
- **security:** Timezone and travel clues are sensitive metadata. Keep them local to relay/Mac context, retain only the chosen zone and provenance, and never infer location from browser pages without permission. Changing a routine's execution time or sending a time-sensitive action should require confirmation when confidence is low.
- **missing:** Authoritative timezone policy from the owner (already requested; current remembered Chicago conflicts with machine evidence); A typed timezone/provenance field in routine records; A pendant-safe confirmation/deferral prompt for a conflict while offline

### "“Let this one task keep working while I’m away, but only on the tabs and apps it needs, and stop automatically at 6.”"
- **useful because:** Today authorization is effectively attached to a surface or a broad session: the relay, Mac agent, and logged-in browser cannot share a narrow, expiring delegation that follows one task. The owner must either remain present or grant a much wider standing trust. A task-scoped lease would make unattended work useful without turning the whole Mac or browser into an always-authorized agent.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model plans and executes the task; realtime is used only to capture the owner's spoken scope and to report an exception or expiry.
- **latency:** Lease issuance under 1 second; normal execution unchanged. Exceptions should reach the pendant within 2 seconds when connected, otherwise appear in the dashboard on reconnection.
- **cost:** <$0.03 per task for policy compilation and exception summarization; most work is deterministic token validation and existing Mac/browser execution.
- **security:** The lease must be narrowly scoped to task ID, allowed domains/apps/actions, data classes, and absolute expiry; bind it cryptographically to the pendant's physical confirmation and revoke on a second press or lost-device signal. Never allow lease chaining, privilege escalation, destructive actions, purchases, or message sends without a separate confirmation. Record a receipt of every delegated step, but do not persist page contents unnecessarily.
- **missing:** A relay-issued, cryptographically signed task lease format understood by both local-agent and browser bridge; Mac and browser enforcement at every action boundary, rather than only at planner entry; A pendant physical-confirmation and revoke event that survives a dropped link; Dashboard controls to inspect, narrow, revoke, and review an active lease


## Changes it proposed to its own stack

### `integration` — Add a single time-authority service between /machine-context, /routines, and the relay scheduler. Each routine stores IANA zone, wall-clock intent, UTC next-run, source and confidence. At dispatch, compare the Mac-reported zone with the owner's authoritative zone; if they differ, pause only time-sensitive routines, emit a concise pendant confirmation event, and resume with an auditable before/after receipt. Do not rewrite historical run times.
- **owner gets:** A routine will stop quietly firing at the wrong local hour when the Mac, relay, or remembered preference disagrees. The owner gets one short question and a clear receipt instead of having to debug missed or early reminders.
- effort: Medium: schema migration, scheduler gate, machine-context normalization, one dashboard conflict view, and a small pendant event/ack path. No Accessibility permission is needed.  ·  risk: A stale zone could pause a routine unnecessarily; recover by retaining the last valid schedule, expiring unanswered conflicts, and offering a dashboard override. DST transitions need tests for ambiguous and nonexistent wall times.
- cost: Negligible API cost; rule-based. Small D1/storage increase for provenance and conflict receipts.  ·  latency: <100 ms on normal dispatch; conflict path adds one network round trip and human response time.
- security: Improves safety by preventing wrong-time actions. Store only timezone identifiers and provenance, not inferred location or page contents; require confirmation for actions with external side effects.
- depends on: Owner's authoritative timezone policy (already requested and still unanswered); A local pendant confirmation event/ack transport; Durable routine schema and scheduler ownership being clarified

### `hardware` — On the product pendant, add a low-power haptic motor with a driver on the currently-unused I2C bus, plus a fuel-gauge IC on the same bus; retain the existing single button and LED. Define two short pulses for 'needs attention' and one long pulse for 'accepted/deferred', and expose battery percentage and low-power state to the relay.
- **owner gets:** The wearer can notice a routine conflict, completed handoff, or queued offline job without taking out a phone or hearing audio. Battery-aware scheduling also prevents starting a long conversation when LTE transmit power would strand the pendant.
- effort: Medium hardware spin and firmware driver work; requires enclosure/PCB revision and an offline interaction spec. Prototype breakout wiring is straightforward because I2C is currently unused.  ·  risk: Haptic vibration can be distracting and adds power draw; cap duty cycle, provide a quiet-hours setting, and fall back to LED/audio. A faulty fuel-gauge reading must never block emergency or manually-started conversations.
- cost: Roughly $3–8 BOM increase for gauge, motor, driver, passives and PCB area; haptic bursts are tens of mW and the gauge is typically sub-mW, with negligible idle impact.  ·  latency: Immediate local feedback (<50 ms); battery telemetry can be reported opportunistically rather than on every audio frame.
- security: No new cloud data beyond coarse battery/attention state; do not upload raw motion or infer wearer behavior.
- depends on: Product pendant replacing the nRF9160 DK prototype; A local event/ack protocol and quiet-hours preference; Battery gauge calibration and power-state firmware policy

### `integration` — Introduce a signed, task-scoped capability lease propagated end-to-end: the relay mints a lease after a physical pendant confirmation; the Mac job runner and browser bridge verify its signature, task binding, allowed app/domain/action set, data scope, and absolute expiry before every step; receipts include the lease ID and policy decision. Revoke is a first-class event delivered over the relay and persisted for disconnected agents to consume before resuming.
- **owner gets:** The owner can safely say 'keep doing this while I’m away' without leaving the entire Mac or logged-in browser broadly trusted. A job that wanders, expires, or is revoked stops rather than silently exceeding the owner’s intent.
- effort: High: shared policy schema, signing-key lifecycle, enforcement middleware in both harnesses, pendant confirmation/revoke event, disconnected-agent replay, and dashboard inspection. This is new connective infrastructure, not a planner prompt.  ·  risk: Clock skew, missed revocation, or a buggy allowlist could either stop useful work or permit too much. Use short leases, monotonic local expiry plus server expiry, deny-by-default on verification failure, and a durable revocation sequence number.
- cost: Low per-task compute/storage cost; modest engineering and key-management cost. No model call is needed for enforcement.  ·  latency: A local signature and policy check per action (single-digit milliseconds); relay round trips only at lease issuance, renewal, or revocation.
- security: Materially reduces standing authorization and limits blast radius. Requires secure key storage, replay protection, audit retention controls, and explicit separation from destructive-action approval.
- depends on: A pendant physical confirmation/revoke event; Action-level enforcement hooks in local-agent and browserBridge; Durable job resume semantics for disconnected Mac/browser workers; Dashboard lease review and revocation UI


## What it asked for

_Nothing._
## Its own summary

Discovered the live owner context, online Mac bridge, offline browser device, shipped tools, and current routine/pipeline routes. Recorded two new pieces: a timezone-authority capability that prevents routines firing at the wrong local hour, and an integration service that stores timezone provenance, pauses only ambiguous time-sensitive routines, and asks once via the pendant. Also recorded a product-hardware change adding haptic attention feedback and a fuel gauge over the currently-unused I2C bus so offline confirmations and battery-aware scheduling can work without a phone. The current Mac reports America/New_York while owner memory says America/Chicago, so this is an active correctness defect.

**Biggest unknown:** I still need the owner's authoritative timezone choice and the unresolved product decisions already requested upstream: 24 kHz end-to-end audio acceptance thresholds/architecture, production pendant constraints, phone-companion privacy boundary, offline queued-action resume policy, interruption/urgency policy, and whether haptic feedback is acceptable. No new permissions or tools are needed from me this round; these are owner/spec decisions.

