# Harness derivation — faculty-judgement — round 193

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me my morning brief, and only tell me it was delivered if I actually heard it.”"
- **useful because:** Today a routine can complete when audio is generated or accepted, which is not the same as the owner hearing it. This makes the promise honest: one brief, one delivery receipt, and a quiet fallback when the pendant never plays it—without duplicate spoken briefings.
- **path:** relay → mac → pendant → dashboard
- **model tier:** Background model composes the brief; realtime model is used only for a spoken retry or owner question. Deterministic delivery state decides whether to retry, queue, or suppress.
- **latency:** Routine generation can take 30–90 seconds. Delivery acknowledgement should settle within 10 seconds after playback; a missed acknowledgement waits until the next owner interaction rather than interrupting again.
- **cost:** One background brief-generation call plus normal TTS/audio cost; retries are deterministic and should add no model call unless the owner requests a shorter replay.
- **security:** The pendant reports only opaque artifact IDs, byte/checksum status, and playback state—not transcript or raw audio. A missing ACK must never be represented as heard. Require policy evaluation before any retry and keep the fallback item in the existing alert inbox.
- **missing:** An end-to-end routine-to-artifact correlation ID (routine run, pipeline, artifact, and pendant ACK currently have separate identities); A durable delivery deadline and deduplicated retry policy in the routine runner; A user-visible receipt that distinguishes generated, downloaded, playback_started, playback_finished, and unheard

### "“When I’m somewhere noisy, keep your replies understandable without making me repeat myself.”"
- **useful because:** A wearable conversation fails in noise even when the network and model are healthy. The pendant can detect only coarse local sound pressure, the relay can choose concise phrasing and robust encoding, and the Mac/bridge can avoid competing playback. The owner gets fewer repeats rather than a louder, indiscriminate speaker.
- **path:** pendant → relay → mac → dashboard
- **model tier:** No expensive model for detection: firmware computes short-window noise/voice-energy features. A cheap background policy maps those features to speech rate, reply length, and codec profile; realtime is used only for the live reply.
- **latency:** Noise classification under 100 ms locally; adaptation at the next utterance boundary. Never interrupt a sentence to change settings.
- **cost:** Negligible inference cost; one small policy decision per turn. Hardware work is firmware and possibly a calibrated bridge gain curve, not a new radio or microphone.
- **security:** Send quantized acoustic features (noise band/level and confidence), never room audio or a transcript. Do not infer location or other people. Owner can disable environmental telemetry; dashboard shows why a shorter/slower reply was selected.
- **missing:** A calibrated pendant noise/voice estimator and signed feature packet; A relay policy that maps noise confidence to maximum spoken words, speech rate, and 24 kHz/16 kHz profile while preserving the measured audio acceptance limits; A bridge-side limiter/AGC policy with a hard safe-volume ceiling and an owner override

### "“Make sure you never tell me my day is clear when you actually couldn’t read my calendar.”"
- **useful because:** An unauthorised EventKit read returns an empty list, and some existing routes turn that into ‘calendar clear.’ This capability makes absence of evidence audible: it cross-checks permission provenance and corroborating sources, refuses a false all-clear, and gives the owner a useful degraded brief instead.
- **path:** mac → relay → pendant → dashboard
- **model tier:** Deterministic permission/read-integrity checks and conflict classification; use the realtime model only to phrase the short spoken warning. No model should infer that an empty calendar means no events.
- **latency:** Under 3 seconds for a routine preflight. If the calendar read is unresolved, speak one short warning and queue the full diagnostic for the dashboard rather than repeatedly interrupting.
- **cost:** No recurring model cost beyond an occasional short warning; reads use existing local EventKit and permission probes.
- **security:** Expose permission state and source freshness, not event bodies, to relay unless the owner has requested the brief. Never claim the owner’s physical timezone from the Mac timezone. Require confirmation before changing permissions or creating substitute reminders.
- **missing:** A first-class EventKit Calendars/Reminders authorization probe that distinguishes unreadable from genuinely empty; A typed ‘all-clear is prohibited’ result consumed by day-plan, notification triage, and briefing routines; A durable degraded-brief receipt and owner-facing repair path, with the pendant saying only ‘calendar access needs attention’

### "“That decision was wrong—show me exactly why you made it, let me correct the rule, and prove what future decisions would change before you adopt it.”"
- **useful because:** The owner can inspect individual provenance and policy verdicts, but cannot turn a correction into a safe, testable change. This creates a human-in-the-loop policy laboratory: a mistaken interruption, approval request, or retry becomes a counterexample; the proposed rule change is simulated against recent decisions before it affects the live hive.
- **path:** dashboard → relay → mac → browser → pendant
- **model tier:** Deterministic policy evaluation and replay do the simulation. Use the expensive model only to translate the owner’s natural-language correction into a candidate rule and to summarize conflicts; never let it silently publish policy.
- **latency:** Explain the triggering decision immediately. Produce a replay over the last 7 days in under 10 seconds; adoption remains a separate explicit action and does not block current work.
- **cost:** One model call only when the owner phrases a correction freely; replay and diff are deterministic. Storage is bounded by compact decision inputs, matched rule IDs, and redacted outcomes rather than transcripts.
- **security:** Corrections may reveal sensitive context, so retain only redacted decision facts and provenance IDs by default. A candidate policy is inert until explicit confirmation. Fail closed on ambiguous rule precedence, and show every affected surface and action class before activation.
- **missing:** A durable decision journal joining autonomy verdicts, attention arbitration, cross-surface preflight, and final receipts under one correlation ID; A policy sandbox that can replay historical inputs without executing Mac, browser, relay, or pendant side effects; A versioned owner-facing rule editor with conflict detection, rollback, and a signed activation receipt


## What it asked for

_Nothing._
## Its own summary

Round 193 produced three distinct owner-facing capabilities: (1) honest brief delivery that says heard only after pendant playback_finished and avoids duplicate retries; (2) acoustic-environment adaptation that uses local noise features to shorten/slow replies without exporting room audio; and (3) fail-closed calendar integrity, prohibiting a false 'day is clear' when EventKit is unreadable. A proposed global forget operation was correctly rejected as an existing backlog item and was not rephrased.

**Biggest unknown:** I still need the owner’s explicit disclosure and interruption policy values (what may be spoken aloud, quiet windows, and emergency classes), plus implementation work for the missing cross-surface correlation/tombstone pieces. LTE registration remains absent, so delivery behavior must be validated first over the real shipping path rather than assuming the currently USB-connected bench hardware is a product transport.

