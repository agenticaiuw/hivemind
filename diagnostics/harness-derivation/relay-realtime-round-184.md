# Harness derivation — relay-realtime — round 184

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "While I’m talking, quietly keep a running summary and then ask if I want it saved as a note when I’m done."
- **useful because:** The owner can think out loud. Instead of a full transcript, they get a short, structured recap they can accept or discard, reducing friction and clutter.
- **path:** relay → mac-bridge
- **model tier:** Realtime model for incremental summarization while the session is active; cheaper tier can store the note if accepted.
- **latency:** Summary updates must not interrupt speech; final prompt should appear immediately after the session ends.
- **cost:** Low. Incremental summary tokens dominate; storage is minimal if the user discards.
- **security:** Summaries may contain sensitive information. Offer a confirmation step before saving and keep summaries out of long-term storage if the user declines.
- **missing:** A place to persist session summaries tied to an owner (memory/context store).; A small UI/voice affordance to accept, reject, or edit the summary.; A policy for what counts as a note versus a transient recap.

### "If I’m about to do something risky on my Mac, warn me and ask for a quick confirmation before it happens."
- **useful because:** It keeps the owner safe from accidental high-impact actions while still allowing fast, trusted control most of the time.
- **path:** relay → mac-bridge → mac-vision
- **model tier:** Mac planner/vision should classify risk; relay only asks the question and relays the answer.
- **latency:** Most actions should remain fast. Only high-risk operations add a brief confirmation step.
- **cost:** Low to moderate. Risk classification is cheap; confirmations are rare.
- **security:** This is a guardrail. It must not become a blanket gate on routine actions, and it should be configurable or disabled per the owner’s preference.
- **missing:** A typed action risk classification output from the Mac planner.; A confirmation mechanism that can pause a job mid-flight and resume after confirmation.; A log of confirmations for auditability.

### "When I walk away from my Mac, freeze any in-progress AI computer work and browser actions; when I come back, tell me what was paused and resume only the work I explicitly choose."
- **useful because:** The pendant is worn and the Mac is often unattended. This prevents an agent from continuing with stale context while the owner is physically absent, yet makes returning to interrupted work effortless.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime relay handles the immediate pause/resume conversation; a cheap background state machine tracks proximity and pending jobs, with no LLM on every heartbeat.
- **latency:** Pause signal under 2 seconds after a confirmed departure; spoken return summary under 5 seconds after the owner presses the button.
- **cost:** About $0.005-$0.03 per pause/resume episode, dominated by one short summary; proximity heartbeats should be non-LLM.
- **security:** A false departure must not destroy work: checkpoint jobs and make pause idempotent. Do not transmit raw audio for proximity. Resumption must never silently approve a mutation; it may restore only a previously authorized, reversible step.
- **missing:** A reliable pendant-to-Mac proximity signal (BLE/UWB or signed USB/BLE handoff) with hysteresis; Pause/resume/cancel semantics in the Mac planner and browser command executor; Relay-side event state machine and durable pending-job ownership

### "Give me a spoken, evidence-backed handoff whenever I switch between the pendant and my Mac: what the agent believes it changed, what it could not verify, and the exact next action I can say to continue."
- **useful because:** Today a wearable conversation can hand work to a machine, but the owner cannot reliably reconstruct the machine's state after walking away or losing audio. This turns every cross-device interruption into a usable continuation rather than a mystery.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Cheap background summarization builds a compact handoff from action receipts, browser inspections, and planner state; realtime only renders or answers the owner's follow-up.
- **latency:** Generate within 3 seconds of job completion, pause, or link loss; playback starts in under 1 second when requested.
- **cost:** Roughly $0.002-$0.01 per handoff using a small summarizer; storage is a few KB of structured state plus optional short speech.
- **security:** Quote only observed facts and label inference versus verification. Strip page secrets and tokens from the handoff. Keep an append-only version so a later agent cannot overwrite evidence of an earlier state.
- **missing:** A normalized cross-surface action receipt schema including observations and unverifiable claims; Relay storage and retrieval for per-session handoff snapshots; A planner prompt/API that accepts a handoff as authoritative context without replaying stale actions

### "If I hold the pendant button for three seconds, immediately stop every agent action, mute or end the live voice session, and lock the Mac; then tell me which jobs were stopped and which could not be interrupted."
- **useful because:** A wearable is the one control surface the owner can reach when the Mac is across the room or an agent is doing the wrong thing. A single physical escape hatch is more dependable than finding a phone or speaking over a runaway response.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Firmware and relay perform deterministic cancellation and session shutdown; a cheap model only summarizes receipts after the stop. Realtime is used solely for the short confirmation.
- **latency:** Local LED acknowledgement immediately; relay cancellation fan-out within 1 second; spoken outcome within 5 seconds.
- **cost:** Under $0.01 per invocation; cancellation is deterministic and the only model cost is a short result summary.
- **security:** False holds should be hard to trigger and visibly acknowledged. The command must be authenticated to the paired device, idempotent, and logged. Locking the Mac can interrupt unsaved owner work, so default to stopping agent-owned jobs first and make Mac lock a configurable part of the gesture.
- **missing:** A firmware long-hold gesture distinct from normal press/release; Relay fan-out cancellation endpoint covering voice, plan, execute, browser queue, and delegated Mac jobs; Mac harness emergency-stop that can abort in-flight AppleScript/shell/browser actions and return per-job receipts


## Changes it proposed to its own stack

### `hardware` — Add a low-power, signed proximity channel between the worn pendant and the Mac (BLE advertisement from the pendant, with optional UWB-capable companion for distance confidence), and expose departure/return confidence plus a physical 'hold to reclaim control' gesture to the relay.
- **owner gets:** The system would know whether the person wearing the pendant is actually near the computer, so it can stop acting on stale unattended sessions and safely hand control back when they return.
- effort: Medium hardware/firmware and Mac harness work: BLE radio/companion integration, encrypted rotating identifiers, hysteresis calibration, and event delivery into the relay. UWB is optional; BLE is the deployable first step.  ·  risk: Radio loss could look like departure. Recover with conservative hysteresis, explicit unknown state, and never auto-cancel—checkpoint and pause only. A stolen pendant must not unlock the Mac; pair cryptographically and require the button gesture for reclaim.
- cost: BLE-only companion roughly $5-$20 in parts and under 10 mW average; UWB adds roughly $20-$50 and more power. No meaningful per-request API cost.  ·  latency: BLE event detection and relay propagation about 1-3 seconds; UWB can improve confidence but not materially reduce voice latency.
- security: Adds a proximity signal, not an authentication bypass. Rotating signed advertisements and encrypted pairing are required; proximity alone must never authorize destructive actions.
- depends on: Mac planner pause/resume/cancellation protocol; Relay durable job state and event delivery; A firmware gesture distinct from the existing short press


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing proposals. The strongest is a physical emergency stop: a deliberate pendant hold must cancel agent-owned Mac/browser work and live audio, then report per-job interruption results. I also recorded presence-aware pause/resume for unattended Macs and a signed proximity hardware change. The proposed handoff summary was recorded too, but the recorder flagged it as close to an existing resume-work idea; its genuinely missing part is provenance-normalized evidence, not another generic continuation feature.

**Biggest unknown:** The live stack still lacks a discoverable relay-side inventory and a real cross-surface cancellation contract. Before implementation, the orchestrator must map which POST /execute jobs can be interrupted safely and define idempotent cancellation receipts.

