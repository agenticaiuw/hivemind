# Harness derivation — unified — round 128

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What was I just looking at, and what should I do next?”—give me a one-sentence spoken handoff from my Mac and authenticated browser, with a resume button."
- **useful because:** This turns the pendant into a true continuity device: after walking away, losing focus, or switching rooms, the owner gets the current page/app, the unresolved decision, and one safe next action instead of hunting through tabs and memory.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Background planner extracts state from Mac and browser artifacts; realtime model only answers the spoken query and handles the resume confirmation.
- **latency:** Under 3 seconds for a concise answer, with a deeper evidence view available on the dashboard. No audio recording needs to leave the Mac unless requested.
- **cost:** About $0.005–$0.03 per request, mostly planner tokens; local browser extraction is the dominant latency, not API spend.
- **security:** Show source app, URL, and freshness in the dashboard; redact secrets and private fields from spoken output. Resume only reversible actions automatically; drafts and submissions remain approval-gated.
- **missing:** A cross-surface attention snapshot that captures active app, browser tab, selection, and unfinished jobs atomically; A durable ‘resume point’ record with expiry and provenance; A pendant-local short confirmation/undo interaction

### "“Keep an ear on this meeting/task and tell me only when I need to act.”"
- **useful because:** The owner gets selective interruption rather than a transcript: calendar and browser context establish what matters, the Mac watches the relevant source, the relay evaluates changes while away, and the pendant delivers a short alert with a safe prepared next step.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Cheap scheduled/background model monitors and classifies changes; realtime model is invoked only for the alert wording or when the owner asks a follow-up.
- **latency:** Meaningful alerts within 30–60 seconds of a source change; spoken alert under 10 seconds and limited to one sentence. Quiet hours and per-source urgency are required.
- **cost:** Approximately $0.02–$0.10 per monitored hour depending on polling and page extraction; use hashes/local event filters to avoid model calls on unchanged content.
- **security:** Monitoring must be opt-in per meeting/page and visibly armed. Keep raw audio and page contents local where possible; send only change summaries. Never send messages, accept invites, or submit forms without explicit confirmation.
- **missing:** A unified watch that correlates Calendar event, active browser page, and Mac notifications; An urgency policy and quiet-hours/interrupt budget; A durable alert queue with deduplication and spoken delivery receipts

### "“Keep the conversation alive if LTE disappears—use my Mac over USB transparently, then return to LTE when it comes back.”"
- **useful because:** The pendant is physically wearable today but LTE is not registered, and the current half-duplex LTE path loses speech under contention. A transparent USB fallback would make the device dependable at home, at the desk, and during radio dead zones instead of silently abandoning a conversation.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** No expensive model is needed for failover: firmware and the Mac bridge detect link state and buffer frames; realtime is used only if the conversation itself needs a response.
- **latency:** Detect failure in under 500 ms, resume audio in under 2 seconds, and hide one reconnect blip from the owner. Preserve ordering and never replay a completed utterance.
- **cost:** Near-zero per invocation beyond ordinary realtime audio; engineering cost is firmware/USB transport and test coverage. A local fallback actually reduces paid relay calls when LTE is unavailable.
- **security:** USB audio and transcripts stay on the owner's Mac unless the existing relay connection is healthy. Authenticate the serial peer, encrypt any persisted fallback buffer, cap retention, and visibly indicate local-only mode with the LED/dashboard.
- **missing:** A framed bidirectional USB audio/control protocol for the nRF9160-to-Mac serial link; A relay session migration/failover protocol with sequence numbers and duplicate suppression; Mac-side audio I/O integration and fault-injection tests for LTE↔USB transitions

### "“Why did I decide this, and what evidence was I looking at?” Give me the short answer plus a timeline of the sources that led to the decision."
- **useful because:** The owner can recover the reasoning behind a choice made days ago instead of rereading tabs, messages, notes, and spoken conversations. The pendant supplies the question hands-free; the relay correlates time; the Mac and authenticated browser provide the private evidence; the dashboard shows citations and uncertainty.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheaper background model to build and index an evidence timeline; use the realtime model only to answer the spoken question and summarize the already-ranked evidence.
- **latency:** A one-sentence answer within 5 seconds; a cited timeline within 15 seconds. If evidence conflicts, explicitly say so rather than inventing rationale.
- **cost:** Approximately $0.02–$0.10 per recall, dominated by timeline retrieval and synthesis; local extraction and hashed indexes keep routine indexing inexpensive.
- **security:** Only search sources the owner authorized, preserve source-level sensitivity labels, and never speak secrets aloud by default. Store citations and hashes rather than raw page content where possible; require confirmation before exposing sensitive evidence on the dashboard or pendant.
- **missing:** A provenance-preserving decision ledger that links spoken captures, notes, browser observations, calendar context, and executed actions by time and session; A cross-surface retrieval API with source citations, confidence, and contradiction detection; An owner-facing retention and deletion control for the linked evidence trail

### "“I need help now.” Have the pendant enter emergency mode, alert my chosen contacts with my location and a short live status, and keep me informed until I cancel it."
- **useful because:** A worn device is valuable precisely when the owner cannot reach a phone or screen. The pendant can provide a local trigger and voice channel, the relay stays awake, and the Mac/phone/browser can deliver the alert and location through services the pendant cannot reach alone.
- **path:** pendant → relay-realtime → mac-planner → dashboard → iOS
- **model tier:** No large model should be in the critical path. Firmware and relay handle the trigger and delivery state machine; a small background model may compose a concise status message only after the emergency channel is established.
- **latency:** Local alarm and spoken acknowledgement immediately; contact notification within 10 seconds where network permits; retry and report delivery state rather than claiming success.
- **cost:** Low API cost, roughly $0.01 or less per event; SMS/voice/location-provider fees and relay availability dominate.
- **security:** Require a deliberate gesture or phrase plus a short cancellation window to reduce false alarms. Encrypt location, use an allowlisted contact set, expire sharing automatically, log delivery receipts, and never expose emergency data to ordinary browser or memory searches.
- **missing:** A production emergency trigger and local confirmation path on the pendant; Location acquisition and a phone/relay delivery integration with provider failover; An emergency-specific contact policy, escalation timer, cancellation gesture, and delivery receipt model

### "“I lost my pendant.” Lock it immediately, revoke its credentials, show its last known connection, and preserve my unfinished work so I can continue safely on my Mac."
- **useful because:** A wearable contains microphones, recordings, network identity, and potentially sensitive cached audio. Today there is no owner-facing lost-device response. The relay, Mac USB presence, dashboard, and pendant firmware can together contain the incident and keep the owner's work usable.
- **path:** pendant → relay-realtime → mac-planner → dashboard → iOS
- **model tier:** This should be deterministic control-plane logic, not a model task. Use a small model only to summarize which sessions were affected after revocation.
- **latency:** Credential revocation and output lock within seconds; last-seen and affected-session report within 15 seconds. Recovery must work even if the pendant is offline.
- **cost:** Negligible model cost; storage and push-notification costs are minor. The major work is secure firmware and credential lifecycle design.
- **security:** Use a separately authenticated recovery channel and a clearly named device identity. Revoke WebSocket credentials, invalidate queued commands, wipe or cryptographically forget SD failure buffers on next contact, and never reveal location beyond the owner’s devices. Provide a reversible ‘found it’ unlock only after strong re-authentication.
- **missing:** Per-device credential rotation and remote revocation; A firmware boot/lock state that refuses audio and commands after revocation; Last-seen telemetry, queued-command invalidation, and encrypted-buffer destruction receipts


## Changes it proposed to its own stack

### `firmware` — Implement a transport-agnostic audio session state machine in the nRF9160 firmware: sequence every frame, expose LTE/USB link health, pause rather than discard during a bounded handoff, and resume with duplicate suppression. Exercise it over the physically connected /dev/cu.usbmodem00096003658* pendant before attempting LTE.
- **owner gets:** When radio coverage or modem contention fails, the owner hears one short gap and keeps talking through the Mac instead of losing half a sentence or wondering whether the pendant is dead.
- effort: High: firmware framing/state machine, Mac serial endpoint, relay session semantics, and live fault-injection tests.  ·  risk: A bad transition could duplicate speech or wedge the session. Gate rollout behind a feature flag, retain the current LTE path, and recover with a button-ended session and visible error LED.
- cost: No per-call API increase; modest engineering time. Existing USB serial hardware is already attached, so no immediate component cost or extra draw.  ·  latency: Adds sub-second health detection and up to 2 seconds for handoff; normal LTE audio unchanged.
- security: Authenticate the Mac serial peer and encrypt/cap any buffered frames; local fallback should not upload audio unless explicitly resumed.
- depends on: A framed USB audio/control protocol; Relay sequence/epoch support; Mac audio endpoint and LTE↔USB fault injection


## What it asked for

_Nothing._
