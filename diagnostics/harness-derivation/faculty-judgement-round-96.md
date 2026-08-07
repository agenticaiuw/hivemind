# Harness derivation — faculty-judgement — round 96

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make sure my routines run at the right local time, and tell me if anything is off.”"
- **useful because:** The owner is in America/Chicago while the live Mac reports America/New_York; a routine that says 07:00 can silently run an hour early, especially across DST. The pendant should speak a short discrepancy alert, show each routine's intended local time versus actual next run, and offer a review before changing anything. This prevents missed morning briefs and accidental quiet-hour interruptions without requiring the owner to inspect scheduler internals.
- **path:** relay-realtime → mac-planner → unified → faculty-perception → faculty-judgement → faculty-action → mac-terminal
- **model tier:** background for the daily audit and schedule calculation; realtime only when the owner asks or confirms a correction
- **latency:** Audit under 10 seconds and cache the result; spoken discrepancy alert under 3 seconds when requested. Schedule edits occur only after explicit confirmation.
- **cost:** About $0.01–$0.05 per daily audit, dominated by the model summarizing only changed routines; route calls and timezone/DST arithmetic are negligible.
- **security:** Routine names and commands may reveal private work habits; retain only normalized schedule metadata and never send routine command bodies to third-party APIs. Do not alter schedules or run commands without confirmation; timezone correction must be preview-only first.
- **missing:** A timezone-aware routine schema with an explicit IANA timezone and DST-safe next-run calculation, rather than inheriting the Mac timezone; A cross-surface audit that compares owner timezone, machine timezone, relay scheduler timezone, pendant quiet hours, and each routine's nextRunAt; A spoken discrepancy card with per-routine preview and confirm/cancel action

### "“When something important arrives or needs my approval, let me feel it privately; use different tap patterns for urgent, routine, and waiting-for-me, and let me acknowledge it without speaking.”"
- **useful because:** The owner cannot reliably hear or speak to the pendant in meetings, on transit, or in noisy streets. Today a browser result, Mac completion, or confirmation request can be effectively invisible until a spoken interaction is possible. A private tactile signal would make the wearable genuinely present without broadcasting sensitive content.
- **path:** relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension
- **model tier:** No expensive model for ordinary signaling; a cheap background classifier may assign urgency from existing job metadata. Realtime is used only if the owner asks for the pending item's spoken details.
- **latency:** Tactile signal within 1 second of a high-priority event and within 3 seconds for routine completion. Acknowledge state should return to the relay within 2 seconds when connected.
- **cost:** Negligible per-event API cost; hardware retrofit roughly $3–$10 for a low-power coin vibration motor or linear resonant actuator plus driver, with firmware work. Battery impact should be under 1% per day for fewer than 100 short pulses.
- **security:** Patterns must encode urgency, not message content, so an observer cannot infer private details. Do not vibrate during owner-defined sleep or driving modes except for an explicitly enabled emergency class. Acknowledging must not approve an irreversible action; it only marks the item seen. Persist only event id, pattern, and acknowledgement timestamp.
- **missing:** A haptic actuator and driver on the pendant (or a secure clip-on accessory); Firmware support for a tiny pattern table, queued pulses, cancellation, and button acknowledgement while offline; A relay-level event-to-urgency contract shared by Mac jobs, browser commands, and scheduled briefings; A durable pending-attention record so a missed pulse can be replayed as audio or shown in the next spoken interaction


## Changes it proposed to its own stack

### `integration` — Add a single timezone-integrity service between relay routines and all surfaces. Store ownerTimezone (IANA), routineTimezone, quietHoursTimezone, and an explicit DST-safe nextRunLocal/nextRunUtc pair on every routine. On each /routines read or daily audit, compare against /machine-context and relay clock, mark mismatches as warning (never silently rewrite), and generate a preview patch. Have /pipeline/audio announce only newly detected mismatches; PATCH /routines/:routineId applies a correction only after pendant confirmation.
- **owner gets:** Their saved preference is America/Chicago but the Mac is America/New_York. This makes morning briefs and quiet hours happen when the owner actually expects them, and tells them before changing anything.
- effort: Medium: schema migration, IANA/DST calculation, audit endpoint, and confirmation wiring across relay and Mac agent.  ·  risk: Existing routines without timezone metadata could be misclassified; recover by treating them as unknown and requiring a one-time confirmation. DST edge times (02:30) need explicit skip/shift policy. Never auto-edit on mismatch.
- cost: Negligible route/storage cost; roughly cents per daily audit if an inexpensive background model is used only for the spoken summary.  ·  latency: No impact on ordinary routine execution; audit under 1 second without model, spoken summary under 3 seconds.
- security: Schedule metadata is sensitive behavioral data. Keep it in the authenticated relay/Mac store, redact command text from audio and logs, and require owner confirmation for edits.
- depends on: Owner timezone must be authoritative and distinct from machine timezone; A typed routine schema and confirmation/receipt path must exist; Pendant audio delivery acknowledgement is desirable but not required for the audit

### `hardware` — Add a sealed low-power haptic actuator (prefer an LRA for crisp short patterns) with a dedicated driver and one interrupt-capable acknowledgement button to the pendant; expose a firmware queue for three urgency patterns, cancel/replace, offline replay, and a monotonic event id. Keep all message text out of the haptic path. Add battery budgeting and a hardware mute switch or long-press quiet mode.
- **owner gets:** They can privately notice and acknowledge an urgent result or approval request even when they cannot hear or speak, making the pendant useful in meetings and noisy environments without exposing what the event says.
- effort: Medium hardware revision plus firmware and enclosure work; validate vibration strength through clothing, accessibility, and false-trigger behavior. Relay/Mac/browser integration then maps existing event receipts to patterns.  ·  risk: Added vibration may disturb sleep or be missed through clothing; recover with configurable intensity, quiet hours, repeated escalation to audio, and replay on demand. Button bounce or stale events could create false acknowledgements; require event-id matching and never treat haptic acknowledgement as authorization for irreversible actions.
- cost: Approximately $3–$10 in components and PCB/enclosure changes at prototype volume; roughly 1–5 mA only during short pulses, with negligible average draw under normal use.  ·  latency: Sub-second local actuation after a queued event; connected acknowledgement normally under 2 seconds, with offline acknowledgement reconciled later.
- security: Improves privacy because the signal carries category only. A physical mute control is important so sensitive situations do not reveal event urgency. Store only opaque event IDs and timestamps on the pendant.
- depends on: A typed cross-surface attention event contract with urgency and expiry; Durable event receipts and replay semantics in the relay; Pendant firmware update path and a button/haptic hardware revision


## What it asked for

_Nothing._
## Its own summary

Round 96 produced a new, owner-specific gap: timezone integrity across relay routines, Mac machine context, and pendant quiet-hours/audio. The owner preference is America/Chicago while the Mac reports America/New_York, so scheduled briefs can be consistently wrong. I proposed both the user capability (“make sure my routines run at the right local time”) and the integration change: explicit IANA timezone/DST-safe local+UTC fields, mismatch previews, spoken alerts, and confirmation-gated PATCHes. The existing /machine-context, /routines, /pipeline/audio, and /ops/snapshot routes are sufficient building blocks, but the connective service and schema do not exist yet.

**Biggest unknown:** Which timezone should be authoritative for travel or temporary location changes, and what should happen to nonexistent/ambiguous DST times (skip, shift earlier, or ask)? Also, GUI automation remains blocked until the owner manually grants per-binary macOS Accessibility/Screen Recording and reconnects the browser bridge; I did not re-request those denied grants.

