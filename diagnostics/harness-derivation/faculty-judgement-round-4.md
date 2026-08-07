# Harness derivation — faculty-judgement — round 4

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep track of the promises I make, even casually. If I say I’ll send something, call someone, or follow up, remind me at the right time and prepare whatever I need.”"
- **useful because:** People lose commitments made in hallway conversations and voice chats, not just tasks they deliberately create. The pendant can hear the commitment at the moment it happens; the relay can interpret it, the Mac can find supporting context, and the browser can prepare a draft without silently sending anything. This closes the gap between intention and follow-through while keeping ambiguous statements reviewable.
- **path:** pendant → relay → Mac → browser → dashboard
- **model tier:** gpt-realtime-2.1 only for low-latency extraction of a likely commitment and a brief disambiguation question; background gpt-5.6-luna to link the commitment to email/calendar/files/browser context and prepare a review card; no model call for simple reminder delivery.
- **latency:** A tentative commitment card within 2 seconds of the utterance; ask at most one short clarification only when date/person/action is genuinely ambiguous. Background enrichment within 5 minutes, and a scheduled reminder at the chosen time.
- **cost:** About $0.01–$0.04 per detected commitment, dominated by realtime audio interpretation and one background context/linking pass; ordinary reminders are near-zero incremental cost.
- **security:** Speech snippets and linked private mail/calendar/browser evidence leave the pendant for processing; retain only the normalized commitment and provenance, with a short audio TTL. Never send mail, submit forms, or contact people automatically. Show source quote, inferred person/date, and proposed action; require confirmation before saving a low-confidence commitment or taking any external action. Provide a physical-button or voice “forget that” path.
- **missing:** A commitment entity with confidence, source timestamp, sensitivity, due-time uncertainty, and provenance in the shared context service; A lightweight on-device trigger/VAD marker and relay endpoint for candidate commitment events (not continuous raw-audio retention); Cross-surface linker for calendar, mail, notes, and authenticated browser tabs; A dashboard review queue and pendant card/voice protocol for confirm, edit, snooze, and forget; A scheduler that can deliver escalating reminders and a completion check-in without duplicating existing reminders

### "“I’m with other people now—keep helping, but don’t reveal anything private or use my logged-in accounts unless I explicitly ask.”"
- **useful because:** Today the assistant has durable memory and authenticated browser reach, but no reliable social-context boundary. The owner should be able to enter a temporary, expiring ‘public presence’ mode from the pendant, so spoken replies stay sanitized and Mac/browser work cannot accidentally expose secrets, private pages, or sensitive notifications. This is a practical safety boundary for an assistant that is always physically present.
- **path:** pendant → relay → Mac → browser → dashboard → iOS
- **model tier:** Realtime handles only the short mode command and confirmation; enforcement is deterministic policy at relay, Mac agent, and browser bridge. A cheap background model may classify queued content for sensitivity, but it must fail closed rather than decide autonomously in the live path.
- **latency:** Local mute/policy indication and spoken confirmation within 300 ms; every subsequent reply/action checked synchronously before release. Mode expires automatically after a user-selected interval (default 30 minutes) and can be extended with one button press.
- **cost:** Negligible per invocation beyond normal conversation; deterministic policy checks add milliseconds. Optional queued sensitivity classification is under $0.01 per batch and should not be needed for ordinary actions.
- **security:** The mode itself is sensitive metadata, but it should not record who is present or raw audio. While active, suppress secret memory retrieval, redact private identifiers from speech and dashboard previews, block browser navigation/read actions to authenticated pages, and require an explicit override for any external action. Fail closed on relay/Mac disconnect, show a tactile/LED state, audit overrides, and make expiration unmistakable.
- **missing:** A signed, shared privacy-policy token propagated from relay to Mac, browser bridge, dashboard, and iOS with TTL and fail-closed semantics; A deterministic secret/sensitivity labeling and redaction layer applied before model prompts, spoken output, screenshots, logs, and notifications; Pendant firmware support for a mode gesture and persistent local indicator, including operation during a dropped link; Browser and Mac executors that enforce the token independently rather than trusting planner instructions; A dashboard control showing current mode, remaining TTL, blocked attempts, and an explicit one-action override flow


## Changes it proposed to its own stack

### `context` — Add a first-class Commitment Ledger to the shared context service. Each record stores the owner's exact source quote (or a redacted hash plus short excerpt), inferred action/person/time window, confidence, status (tentative/confirmed/active/completed/declined), provenance links to mail/calendar/files/browser, sensitivity, TTL, and a deduplication key. A background linker may suggest evidence and drafts, but only an explicit owner confirmation promotes a tentative record to an external-action-capable commitment. Expose event hooks to relay reminders and a dashboard review queue.
- **owner gets:** The owner gets one trustworthy place where spoken promises become follow-through, instead of scattered reminders and forgotten context. They can see why the system thinks a promise exists, correct it once, and avoid duplicate nagging or embarrassing actions taken on their behalf.
- effort: Medium-high: schema and event API, realtime candidate extraction, entity linking across Mac/browser sources, reminder policy, dashboard and pendant protocol, plus evaluation on false-positive commitments.  ·  risk: False positives could create noisy reminders or incorrectly associate a person. Keep candidates tentative, require confirmation for persistence when confidence is low, allow immediate forget, cap reminder frequency, and make all generated drafts reversible. Recover by replaying the source event and editing ledger state.
- cost: Small D1/R2 and scheduler cost; roughly $0.01–$0.04 per candidate depending on audio and linker calls. No new hardware required.  ·  latency: Candidate acknowledgment remains realtime; evidence linking is asynchronous and should not block conversation. Reminder delivery is scheduler-driven.
- security: Introduces a sensitive behavioral record. Encrypt or minimize source text, apply TTLs and per-field sensitivity, audit every read, and require explicit confirmation before any browser or mail mutation.
- depends on: Typed context projection service with provenance and TTLs; Durable background job/scheduler with completion receipts; Authenticated browser queue and Mac file/calendar/mail connectors; Pendant event and short-card protocol

### `firmware` — Ship a versioned 24 kHz superwideband audio profile end to end, with an explicit negotiated session format rather than implicit resampling: pendant capture/Opus framing, relay uplink/downlink metadata, decode, I2S playback, and DAC clock configuration must agree on 24 kHz. Add a 3-second local loopback/remote test mode that emits a chirp and reports sample-rate, underrun, packet-loss, and clock-drift counters; if negotiation or buffer health fails, automatically fall back to the known 16 kHz profile and expose the reason in the diagnostic receipt.
- **owner gets:** The pendant should sound natural and stay intelligible every day, not merely claim that 24 kHz is enabled. Automatic fallback prevents a broken update from stranding voice, while a one-button test makes intermittent distortion diagnosable without engineering tools.
- effort: Medium: firmware audio clock/buffer work, relay capability negotiation, codec profile versioning, test-mode protocol, and hardware-in-the-loop acceptance tests across Wi-Fi conditions.  ·  risk: A clock mismatch can cause pitch drift, underruns, or silence; retain the 16 kHz fallback, gate rollout behind loopback and 10-minute soak tests, and make the update reversible. Test mode must not transmit private speech.
- cost: No recurring model cost; engineering/test hardware effort only. A small RAM increase for counters and test buffers (target under 8 KB) and negligible power increase during the test.  ·  latency: 24 kHz may increase bandwidth modestly; negotiation adds at most one handshake round trip. The fallback path preserves current conversational latency.
- security: Diagnostics should contain counters, not audio. Require a deliberate button gesture for loopback and authenticate profile negotiation so a network peer cannot force an unsafe mode.
- depends on: Firmware repository write/build/flash permission; Relay audio capability-negotiation endpoint; Hardware-in-the-loop audio acceptance test harness; A documented known-good 16 kHz rollback image

### `hardware` — For the product revision, add a physical, latching microphone-mute/privacy switch with a clearly visible two-color indicator, while retaining the existing action button for push-to-confirm/forget. Route the mute line to hardware/firmware so it gates capture before the application task and emits an unmistakable local indication; relay must receive only a mute/unmute state transition, never buffered audio.
- **owner gets:** The owner can have a private conversation or instantly reject capture without trusting a voice command or software state. That makes always-worn commitment capture and live voice socially acceptable, especially around other people.
- effort: Low-to-medium product hardware revision: one latching switch, LED/light-pipe, GPIO/pull configuration, enclosure change, firmware state machine, and relay indicator handling; validate accidental toggles and accessibility by touch.  ·  risk: A hidden or accidental mute could make the owner think the assistant is broken; use a tactile detent, distinct LED state, and spoken confirmation on unmute only. A failed switch should default to mute, with diagnostics exposing the state. It may increase enclosure size and assembly complexity.
- cost: Roughly $0.20–$1.00 BOM increase plus enclosure/PCB revision; negligible steady-state power, with a few mA only while indicating.  ·  latency: Immediate local gating; no network round trip. Unmute acknowledgment may add one short audio turn.
- security: Strongly improves privacy because capture is physically interrupted before software. Ensure the modem cannot override the switch and include mute transitions in an audit log without recording nearby speech.
- depends on: Product hardware beyond the current nRF9160 DK prototype; Firmware GPIO/audio-capture integration; Relay privacy-state protocol and dashboard indicator


## What it asked for

_Nothing._
## Its own summary

Discovered the Mac agent is live (v0.5.0) with a substantial authenticated route surface, including jobs, provenance/evidence, forms, watches, context graph, and pipeline traces. The pendant remains a prototype with one button/LED, no battery gauge, and a constrained LTE-M link: measured simultaneous 16 kbps uplink + 24 kbps downlink drops about 7.8 seconds of speech. I proposed a cross-surface Commitment Ledger (spoken promises become reviewable, provenance-backed follow-through), its context implementation, an end-to-end negotiated 24 kHz profile with measured fallback, and a product-level physical microphone mute switch.

**Biggest unknown:** Whether the newly granted Mac Accessibility/Screen Recording and browser authorization actually took effect, and whether firmware repository/build/flash access plus the relay audio negotiation path are available. Those determine whether the 24 kHz work can move from proposal to a verified hardware-in-the-loop test.

