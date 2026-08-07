# Harness derivation — faculty-judgement — round 52

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If the connection or my Mac disappears halfway through, pick up exactly where we left off—without repeating an action or losing what I said.”"
- **useful because:** Today a dropped LTE link, offline browser bridge, or unavailable Mac can strand a spoken request. This would preserve the owner's words, the partial research/form state, evidence, and approval boundaries across the pendant, relay, Mac, and browser, then present one short resume card when any surface returns. It is more than a background job: it keeps conversational intent and action safety continuous.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the short spoken recovery exchange; a cheaper background model compiles the durable resume packet and reconciles evidence/action receipts.
- **latency:** On reconnect, local acknowledgment under 1 s; resume summary under 5 s after the first reachable surface. No action replay until the coordinator verifies the lease and asks again where approval is required.
- **cost:** Roughly $0.01–$0.05 per interrupted task, dominated by background reconciliation and any regenerated summary; normal uninterrupted turns add no model cost.
- **security:** The packet contains potentially sensitive spoken text, page excerpts, and draft fields, so encrypt it in transit and at rest, enforce per-task expiry, and redact secrets. Never infer approval from a stale packet; sending mail, purchases, deletion, and submissions require a fresh confirmation. A durable lease plus idempotency key must prevent duplicate clicks or submissions.
- **missing:** A durable cross-surface task journal with append-only intent/evidence/receipt events; A lease and idempotency coordinator shared by relay, Mac, and browser bridge; Pendant-side outage marker and bounded encrypted SD queue for the last utterance; A resume-packet compiler with explicit approval state and expiry; Reconnect handshake that verifies surface identity and revalidates preconditions before continuing

### "“If something seems wrong and I stop responding, check on me in stages and get help without exposing my private data.”"
- **useful because:** A wearable that can hear and speak should also protect the person wearing it when they cannot answer. The system would combine pendant-local signs (missed check-ins, an explicit distress gesture, or an unusual prolonged silence), relay availability, and the owner's calendar/location-free routine signals to decide whether to ask again, notify a chosen contact, or escalate. No single Mac, browser, or cloud service can provide this responsibly by itself.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic rules and a small background model classify event combinations; realtime is used only for the pendant's immediate spoken check-in. No expensive model is needed for escalation decisions.
- **latency:** Local distress acknowledgment under 500 ms; first check-in within 10 seconds of a qualifying event; escalation stages separated by an owner-configured grace period (for example 2, 5, and 15 minutes).
- **cost:** Usually under $0.01 per event for state evaluation and notifications; occasional background summarization is the dominant cost. Cellular data and SMS/voice escalation may add provider fees.
- **security:** This is safety-critical and must never silently infer a medical emergency from ordinary quiet. Store only minimal event metadata, encrypt contact details, and require explicit opt-in, test mode, and a conspicuous cancel gesture/phrase. Never send calendar contents, page data, or location unless the owner separately authorizes it. Escalation contacts need signed, auditable templates and rate limits; emergency services should require a distinct owner policy and regional integration rather than an improvised model decision.
- **missing:** A pendant-local, offline-capable distress/check-in event detector with false-trigger safeguards; An owner-configured escalation policy and signed contact directory; A relay-held durable escalation state machine that survives Mac/browser outages; A secure notification/voice/SMS delivery integration with delivery receipts; A dashboard for simulation, cancellation, audit history, and periodic policy re-confirmation; A formal safety review and regional emergency-services policy before any emergency escalation is enabled


## Changes it proposed to its own stack

### `firmware` — Make the 24 kHz path interruption-tolerant with a coordinated congestion controller: pendant-side VAD and Opus DTX suppress silent uplink frames; uplink speech packets get a bounded priority queue and sequence numbers; relay pacing caps downlink audio to the measured LTE-M budget, emits in-band loss/congestion feedback, and briefly switches to a lower complexity/bitrate profile when both directions contend. Keep a tiny rolling jitter buffer and explicit barge-in marker so the owner can interrupt instead of competing with playback. Validate with packet-loss, latency, and 60-minute battery tests before enabling by default.
- **owner gets:** The owner gets natural 24 kHz playback without the current failure mode where assistant speech causes roughly eight seconds of lost uplink. They can interrupt reliably, and short LTE contention becomes a tiny quality dip rather than a lost request.
- effort: Medium-high: firmware queue/VAD/sequence work, relay pacing and transcoding, telemetry, and a hardware-in-loop acceptance harness. Requires revisiting the current 15,625 Hz mic/16 kHz uplink assumptions rather than pretending the path is already symmetric.  ·  risk: Aggressive suppression or bitrate fallback could clip quiet speech or make playback sound worse; stale packets could be replayed after reconnect. Recover with feature flags, monotonic sequence validation, a fixed queue cap, and automatic return to the known profile after congestion clears. Preserve the SD failure-buffer policy—do not turn it into routine recording.
- cost: Near-zero per-call API cost; modest engineering/test cost. VAD and queue metadata consume some RAM, likely a few KB, while existing encode+decode already uses about 87% of one core. A product revision may need a more capable audio/DSP path if profiling leaves no headroom.  ·  latency: Adds approximately 20–60 ms of jitter buffering in the normal case; congestion fallback can add one frame. Barge-in recognition should remain under 150 ms.
- security: Sequence numbers and authenticated feedback reduce replay/injection risk. If VAD diagnostics are uploaded, send aggregate counters only; raw audio remains transient and SD remains failure-only.
- depends on: End-to-end 24 kHz playback acceptance tests; A relay/pendant telemetry schema for packet loss, queue depth, and barge-in; Confirmed Opus DTX and encoder controls in the vendored fixed-point build; A product hardware decision if the 87% CPU profile cannot meet worst-case scheduling


## What it asked for

_Nothing._
## Its own summary

This round added two owner-facing gaps beyond the repeated browser/briefing backlog: (1) reconnect-safe conversational continuity, preserving the utterance, evidence, partial form state, receipts, and approval boundary across pendant↔relay↔Mac↔browser, with lease/idempotency and fresh confirmation; (2) a concrete 24 kHz firmware+relay congestion controller (VAD/Opus DTX, priority uplink, paced downlink, sequence validation, jitter buffer, and barge-in) to address measured LTE contention and ~8 seconds of lost uplink. Both were recorded as proposals and faculty-action/unified were informed.

**Biggest unknown:** I still need the actual current cross-surface journal/lease primitives and the 24 kHz acceptance criteria that the orchestrator said it would provide; without those I cannot distinguish what is already implemented from the missing recovery and audio-control pieces. The Mac Accessibility/Screen Recording and browser-bridge authorization also remain operational prerequisites for validating the resume path.

