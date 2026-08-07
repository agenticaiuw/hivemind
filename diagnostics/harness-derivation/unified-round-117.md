# Harness derivation — unified — round 117

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“From the page I’m looking at, take care of this, but tell me what you found and ask before anything irreversible.”"
- **useful because:** The owner can discover something in a logged-in browser and complete the whole task hands-free: the pendant identifies the current page, the relay coordinates evidence gathering, the browser uses the authenticated session, and the Mac leaves a durable, reviewable receipt. No one surface can do this alone, and sending/deleting/buying still requires explicit spoken approval.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** gpt-realtime-2.1 only for the short live dialogue and approval turn; use the cheaper background planner for page extraction, cross-tab research, drafting, and receipt generation.
- **latency:** Acknowledge on the pendant within 500 ms; first sourced findings within 5 s; reversible form filling may continue asynchronously. Pause immediately at an irreversible boundary and wait indefinitely for a clear approval.
- **cost:** Roughly one realtime turn plus 2–6 background planner calls; typically $0.03–$0.20 per task, dominated by authenticated page extraction and any speech/audio processing.
- **security:** Browser data and page snippets leave the Mac only through the authenticated relay job. Redact secrets and unrelated tabs; bind every operation to the originating tab/session and show URL, fields, and before/after values. Never send, delete, purchase, or submit without explicit confirmation; expire the approval if page state changes.
- **missing:** A first-class cross-surface task object linking pendant utterance, originating browser tab, relay plan, extracted evidence, approval token, and Mac receipt; A spoken approval protocol that hashes the exact pending mutation and invalidates on DOM/value change; A pendant-friendly result/approval prompt and dashboard review view

### "“During this meeting, quietly keep track of decisions, names, and promises, and tell me through the pendant if I’m asked something I’ve already got an answer for.”"
- **useful because:** The owner gets a private, hands-free meeting copilot rather than a post-meeting transcript: the pendant hears the room, the relay maintains a low-latency local conversation state, the Mac uses Calendar and Notes for context, and the authenticated browser can retrieve relevant private documents when a question arises. It can surface a one-sentence whisper without interrupting the meeting, then leave a sourced decision log afterward.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime tier only for acoustic turn detection, short private whispers, and urgent question matching. Use a cheaper background model for rolling transcription cleanup, entity/decision extraction, document retrieval, and the post-meeting summary.
- **latency:** Detect a decision or direct question within 1–2 seconds; whisper responses within 3 seconds when a matching source is already cached. Defer non-urgent extraction and the final log until after the meeting.
- **cost:** Approximately $0.10–$0.60 per 60-minute meeting, dominated by audio transcription and rolling summarization; cached retrieval and post-meeting drafting should use the cheaper tier.
- **security:** Meeting audio is highly sensitive. Default to on-device wake/voice activity detection, encrypt transport, retain only extracted decisions unless the owner explicitly chooses transcript retention, and show a visible recording state. Never read private browser content aloud unless the owner activates private-whisper mode; do not send messages or edit shared notes without confirmation.
- **missing:** A meeting session mode with explicit start/stop, visible recording status, and participant/privacy policy; Streaming diarization and decision/promise extraction with confidence and source timestamps; A low-volume private-whisper output channel that can duck or pause safely without speaking into the room; A context joiner linking the active Calendar event, selected Notes, and explicitly permitted browser tabs; A post-meeting evidence log that distinguishes observed statements from model-inferred action items


## Changes it proposed to its own stack

### `integration` — Add a cross-surface transaction envelope shared by relay, browser bridge, Mac planner, and pendant session: transactionId, origin tab/session, evidence hashes, planned mutations, risk class, exact approval digest, expiry, and final receipt. Browser result and Mac job receipt must reject a stale digest or changed page state; pipeline events/audio carry only the transactionId and user-facing status. Persist the envelope in D1 and mirror a compact pending/approved/completed record locally for link loss.
- **owner gets:** They can say “handle this” while looking at a private page, hear a concise sourced summary, approve exactly what will happen, and later prove what changed. A refresh, navigation, or dropped connection cannot silently turn yesterday’s approval into today’s submission.
- effort: Medium: shared schema and state machine in relay plus adapters in browserBridge, Mac jobs, and pipeline event/audio handlers; add contract tests for duplicate delivery, reconnect, page mutation, and approval expiry.  ·  risk: A strict digest check may reject legitimate work after harmless page churn; recover by re-extracting and presenting a new diff. Duplicate or out-of-order events must be idempotent. Keep a manual dashboard path to cancel and inspect orphaned envelopes.
- cost: Negligible per-task storage (roughly 2–10 KB in D1/local JSON); no additional model call. Existing browser and planner calls dominate cost.  ·  latency: Adds one local hash/state check (<20 ms) and one relay lookup (<100 ms); page re-extraction after stale approval is the only noticeable delay.
- security: Improves security by binding approval to exact evidence and mutation; do not store raw secrets in the envelope, only redacted previews and hashes. Require explicit confirmation for destructive or external side effects.
- depends on: A durable browser job runner and typed browser results must be wired to the existing bridge routes; The pending approval/receipt state machine must exist in the relay; The owner must continue to grant browser read/click authority while keeping send/delete/buy confirmation

### `hardware` — Replace the prototype audio front end with a production split: a 24/48 kHz digital I2S microphone and low-power audio codec/DSP on the pendant/bridge, with the cellular MCU reserved for framing and LTE. Use an ESP32-S3-class bridge with PSRAM (or an equivalent audio-capable companion) instead of the classic ESP32 for buffering, resampling, and simultaneous encode/decode; keep the nRF9160 modem path initially. Define a clocked 24 kHz PCM contract at both capture and playback boundaries so the relay no longer presents 15,625 Hz capture as a nominal wideband path.
- **owner gets:** They get intelligible, natural-sounding speech in both directions and fewer clipped/robotic turns, rather than a 24 kHz playback path fed by narrow, uneven capture. The pendant can remain responsive during LTE bursts and interruptions.
- effort: High: select and lay out the mic/codec, validate clocks and RF coexistence, port I2S/DMA and Opus framing, then run acoustic, thermal, battery, and cellular regression on a wearable prototype.  ·  risk: New clocking, RF noise, and power domains can introduce audio artifacts; recover with a bypass route to the existing 15.625 kHz mic and a board-level feature flag. A new bridge may break current firmware tooling, so retain a UART/J-Link compatibility header.
- cost: Prototype BOM increase roughly $15–$35 (mic/codec, ESP32-S3 module, PSRAM, power regulation) and likely +80–200 mW during active audio; per-unit cost falls with volume. No meaningful API-model cost change.  ·  latency: A dedicated audio path should remove current CPU contention and reduce encode/decode scheduling jitter; add roughly 5–15 ms for buffering, while preserving 60 ms packetization until measured otherwise.
- security: Audio remains on the existing encrypted LTE/relay route; add signed firmware and disable/debug-lock production test interfaces. PSRAM buffers must be zeroed after use and never exposed to the browser or dashboard.
- depends on: A written end-to-end 24 kHz acceptance target and authoritative capture/playback clock contract; Audio-link fault injection and preflight measurements on the current prototype for a baseline; A production pendant power budget and enclosure/RF/acoustic design review

### `integration` — Add an ephemeral meeting-context capsule spanning Calendar, pendant audio, relay, Mac Notes, and explicitly selected browser tabs. At meeting start it snapshots the event identity, attendees, agenda links, and permitted sources; during the meeting it accepts timestamped speech facts and question matches; at stop it freezes the capsule, produces a decision/action ledger with quoted evidence, and deletes raw audio by policy. Each fact must retain an origin timestamp and source type so inferred commitments cannot masquerade as spoken decisions.
- **owner gets:** They can enter a meeting with relevant private material already available, receive only useful private prompts, and leave with a trustworthy record of what was actually decided. Unrelated mail, tabs, and old memory do not leak into the meeting or its summary.
- effort: Medium-high: Calendar/Notes/browser context adapters, a streaming event schema, retention enforcement, confidence-aware extraction, and dashboard review of evidence-linked decisions.  ·  risk: Wrong attendee or event matching could expose unrelated private material; require explicit event selection when ambiguous and show the selected sources before recording. Speech recognition can invent commitments; label uncertainty and require review before creating reminders or sending notes.
- cost: Small storage overhead for compact facts and hashes; transcription and extraction are the dominant model cost. Raw audio retention can be near-zero by default.  ·  latency: Initial context assembly should complete before the meeting; cached question matching adds under 2 seconds, while final ledger generation can run asynchronously.
- security: Strongly improves privacy through an explicit source allowlist, event-scoped encryption/retention, and automatic deletion. Never grant broad browser access merely because a meeting is active.
- depends on: A meeting-session lifecycle and visible recording indicator; Streaming speech-to-fact extraction with confidence and timestamps; A private-whisper output path; Explicit owner policy for recording, retention, and participant consent


## What it asked for

_Nothing._
