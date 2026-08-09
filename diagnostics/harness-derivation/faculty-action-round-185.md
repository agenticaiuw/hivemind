# Harness derivation — faculty-action — round 185

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Save my place" when I walk away — preserve exactly what I was doing and give me a one-tap way to resume it later."
- **useful because:** The pendant's motion sensor can detect a deliberate departure from the Mac without requiring a spoken command. The system would preserve the active app, browser tabs/URLs and unfinished draft as a resumable work card, preventing lost context during interruptions.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Background/cheap model only to summarize the checkpoint; deterministic collectors and action executor do the state capture and resume.
- **latency:** Capture within 2 s of the departure gesture; resume actions staged in under 5 s when requested.
- **cost:** One small summary call per checkpoint, otherwise local/relay metadata. Storage is a few KB per checkpoint plus optional redacted snippets.
- **security:** Never capture passwords, secret fields, microphone audio, or arbitrary page contents. Browser extension supplies URL/title and field classifications; Mac supplies frontmost app and draft-safe metadata. Resume must be staged and require the existing physical approval latch for external side effects.
- **missing:** Firmware IMU integration and a calibrated departure gesture/state machine; A redaction-aware Mac/browser checkpoint collector; Durable resumable-card schema linking state snapshots to action steps; Resume executor with postcondition verification

### ""Only let sensitive actions run while I am wearing the pendant" — establish a short-lived physical presence lease, and automatically freeze queued actions when the lease expires."
- **useful because:** This turns the pendant into a hardware-backed presence boundary. A stolen/unlocked Mac or stale browser session cannot continue an approved workflow after the owner walks away, while ordinary low-risk work can remain available.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** No model call; cryptographic lease validation and risk routing are deterministic.
- **latency:** Lease renewal every 5–15 s; action freeze within one renewal interval plus 1 s. Reconnect should recover without replaying expired actions.
- **cost:** Negligible API cost; small signed heartbeat traffic and a bounded relay state record.
- **security:** The lease must contain an opaque device-bound nonce, monotonic counter, expiry, and action-risk scope; no secrets or page contents go to the pendant. Expiry is fail-closed for high-risk actions but must not kill an already-running safe read. Replays, clock rollback, and link drops need explicit handling.
- **missing:** Device-bound key or equivalent authenticated pendant lease primitive; Relay lease registry and risk-scoped expiry enforcement; Mac/browser hooks that pause rather than silently discard queued work; Dashboard visibility into present/expired/frozen state

### ""Finish this workflow without losing my place" — if any step fails or the browser disconnects, stop safely, preserve the exact next action, and let me resume without repeating completed steps."
- **useful because:** Long workflows currently risk an ambiguous half-completed state. A resumable execution plan with per-step receipts and fresh postcondition checks would make the Mac/browser hands dependable rather than forcing the owner to guess what happened.
- **path:** mac-planner → browser-extension → relay-realtime → pendant → dashboard
- **model tier:** Cheap background planner for recovery suggestions; deterministic executor and verifier for step state. Realtime is used only if the owner asks by voice.
- **latency:** Failure detection under 2 s; checkpoint persistence before the next mutation; resume preview under 3 s.
- **cost:** Small metadata writes and verification calls per step; model cost only when recovery requires replanning.
- **security:** Never retry a mutation unless its prior postcondition is independently verified. Preserve only redacted locators and hashes for secret fields. Expired sessions and changed pages must force a fresh approval, and the pendant must receive only a human-readable summary.
- **missing:** First-class workflow/checkpoint schema with idempotency keys; Executor integration that pauses on uncertain receipts instead of guessing; Independent verifier attached to every mutating step; UI/voice resume command and bounded retention policy

### ""Why did you do that?" — explain any action as a short, trustworthy chain from my request and physical approval to the exact Mac/browser changes, including what was uncertain or refused."
- **useful because:** Receipts tell the system that something ran, but the owner needs to understand causality and scope after the fact—especially when several surfaces acted or a workflow partially failed. This makes the AI accountable without exposing secrets or requiring the owner to reconstruct logs.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Cheap background summarization over structured provenance; deterministic collection and redaction. Realtime only speaks the final concise explanation when requested.
- **latency:** A concise spoken explanation within 3 seconds; detailed dashboard provenance within 5 seconds.
- **cost:** Low: structured event joins dominate; one small summarization call only for natural-language explanation.
- **security:** The pendant receives only a redacted human-readable explanation, never form secrets or page contents. Every claim must link to an immutable event/verification receipt, distinguish observed facts from inference, and say 'unknown' when evidence is missing. Retain sensitive provenance locally with configurable expiry.
- **missing:** A cross-surface provenance graph linking request, plan, approval nonce, executor attempt, verifier result, and external effect; Redaction and sensitivity policy for explanations; Stable causal IDs propagated through relay, Mac, and browser commands; Owner-facing explanation endpoint and pendant voice query

### ""Draft-only until 6 PM" — temporarily change how the whole hive behaves, so it may research and prepare but cannot send, purchase, delete, or publish until the deadline or my deliberate override."
- **useful because:** The owner can safely delegate preparation while busy or in public without changing permanent settings. A single temporary policy should govern relay jobs, Mac actions, and browser commands consistently, instead of relying on each surface to remember a local preference.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** No model call for enforcement; the model may translate the spoken request into a policy proposal, but the policy engine applies typed action classes deterministically.
- **latency:** Policy acknowledgement under 1 s; enforcement on every action before execution; expiry within 1 s of the deadline.
- **cost:** Negligible runtime cost; one policy record and a small preflight check per action.
- **security:** Default to the more restrictive mode on ambiguity, clock disagreement, or link loss. The policy must be visible, scoped, auditable, and unable to be bypassed by a stale queued job; override requires the existing deliberate physical approval gesture.
- **missing:** Typed cross-surface action-policy lease with expiry and timezone/monotonic semantics; Policy checks in relay, Mac executor, and browser command paths; Voice/panel preview showing blocked action classes and remaining duration; A safe physical override protocol

### ""Give me a private rehearsal" — before I send or publish something consequential, let me practice the exact final interaction with a realistic local simulation, then discard the rehearsal and show me the differences from the real action."
- **useful because:** The owner could catch wording, recipients, quantities, and irreversible side effects before committing. The browser and Mac can preview the true interaction while the relay guarantees that rehearsal traffic cannot escape into a real service.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic sandboxing and diffing; a cheap model may help explain differences, but never decides whether a rehearsal is safe.
- **latency:** Preview creation within 5 s for ordinary forms/messages; diff and discard receipt within 2 s after rehearsal.
- **cost:** Low to moderate engineering cost; no external API cost if sandbox fixtures are local, though complex sites may need a browser virtualization layer.
- **security:** Rehearsal must use synthetic identities, intercepted network requests, and a hard outbound-deny boundary. Never paste real secrets into the sandbox. The system must label unsupported interactions instead of claiming equivalence, and real execution still requires explicit approval.
- **missing:** Browser/Mac sandbox or network-intercept harness with deterministic fixtures; Semantic diff between rehearsal and real action plans; Outbound deny and synthetic-identity enforcement; Owner-visible rehearsal receipt and cleanup verification


## Changes it proposed to its own stack

### `firmware` — Integrate the already-owned LSM6DSOX on i2c2 as a low-power motion event source: calibrate a departure signature, emit a signed checkpoint event only after stillness plus a deliberate orientation change, and keep raw motion on-device (never upload it).
- **owner gets:** Walking away from the desk could automatically save work context without a button or spoken command, while ordinary movement would not create noisy checkpoints.
- effort: Medium: enable i2c2/devicetree, add sensor driver and calibration, test false positives across wear positions, and define a compact event envelope.  ·  risk: False departure detection could create nuisance checkpoints or drain battery. Require a confidence threshold, cooldown, and sw1 cancel; if the sensor fails, disable the trigger and preserve normal button behavior.
- cost: No new hardware; modest firmware flash/RAM and roughly 0.5–2 mA while sampling, with duty-cycled polling to reduce draw.  ·  latency: A checkpoint event can be emitted 1–3 s after the motion signature; no impact on the 24 kHz audio path if sampling runs at low priority.
- security: Raw accelerometer/gyro data stays local; events should be authenticated and contain only event type, monotonic ID, and timestamp validity.
- depends on: A redaction-aware Mac/browser checkpoint collector; Durable resumable-card schema; Pendant-to-relay authenticated event envelope


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct recorded capabilities: (1) IMU-triggered 'save my place' that captures a redacted Mac/browser checkpoint and resumable card when the owner walks away, (2) a cryptographic pendant-presence lease that freezes high-risk queued actions when the wearable is absent, and (3) failure-safe resumable workflows that independently verify each completed step and resume only from the next safe action. I also recorded the concrete firmware change to integrate the owned LSM6DSOX over i2c2 for the departure event. The emergency privacy/panic-cord idea was correctly rejected as an existing duplicate rather than rephrased.

**Biggest unknown:** The system still lacks the connective contracts: an authenticated device-bound lease, a redaction-safe checkpoint schema/collector across Mac and browser, and a first-class workflow checkpoint with verifier/idempotency semantics. I also still need the owner's risk-policy table (which action classes may run under presence alone versus requiring explicit approval); I will not invent that policy.

