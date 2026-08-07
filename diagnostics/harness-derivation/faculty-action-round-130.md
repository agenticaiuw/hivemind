# Harness derivation — faculty-action — round 130

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“During a meeting, when I tap the pendant, mark that moment and remember what was being discussed; afterward, give me a sourced action list and draft follow-ups.”"
- **useful because:** The pendant is the only always-with-me, low-friction marker. It lets the owner capture decisions without touching the Mac, while the Mac/browser can add agenda, document, and participant context afterward.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime model only for the tap/short acknowledgment; background model for transcript segmentation, document lookup, and follow-up drafts.
- **latency:** Tap acknowledgment under 300 ms; post-meeting synthesis within 2 minutes of the meeting ending.
- **cost:** About $0.03–$0.15 per meeting depending on audio duration; transcription and synthesis dominate.
- **security:** Meeting audio and private documents leave the device to the relay/Mac pipeline. Require explicit meeting-mode start, visible recording indicator, local retention limit, and approval before any draft is sent or calendar/task is changed.
- **missing:** A device-side tap marker event carrying monotonic timestamp and meeting-mode state; A Mac audio/transcript segmenter that can align marker timestamps to speech; A cross-surface evidence bundle linking transcript spans, browser sources, and generated drafts

### "“I’m leaving my desk—make sure the document or page I was working on is ready to continue later, and tell me on the pendant exactly where I left off.”"
- **useful because:** This turns an interruption into a recoverable handoff instead of lost context: the Mac records the active work state, the browser preserves the authenticated tab, and the pendant gives a concise resumption cue while walking away.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Cheaper background model for summarizing and indexing the work state; realtime model only if the owner asks a follow-up by voice.
- **latency:** Capture state within 5 seconds of the trigger; spoken resumption cue within 10 seconds.
- **cost:** Under $0.02 per handoff for local metadata and a short summary; model cost scales with page/document text.
- **security:** Authenticated URLs, document snippets, and unsaved text are sensitive. Never transmit full page contents by default; store an encrypted local pointer plus minimal excerpt, and require confirmation before reopening or sharing anything.
- **missing:** A reliable desk-away trigger (pendant button pattern or Mac idle/lock event); A browser/Mac active-work snapshot schema with unsaved-buffer detection; A pendant playback queue for short resumption cues

### "“When I double-tap the pendant, let me speak a quick thought while I’m away from the Mac; turn it into the right note, task, or reminder and read back what you captured.”"
- **useful because:** The owner can capture ideas hands-free without opening a laptop or leaving a Mac microphone on. The pendant/bridge supplies the physical input, while the Mac can place the result in the correct project or reminder system.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Realtime model for endpointing and a brief read-back; cheaper background model for classification, deduplication, and filing.
- **latency:** Start recording within 200 ms of the double-tap; read-back within 5 seconds after speech ends.
- **cost:** Roughly $0.01–$0.05 per capture; audio transcription dominates.
- **security:** Audio is private and may contain bystanders. Show a recording LED, require a deliberate gesture, encrypt queued audio, auto-delete raw audio after transcription, and ask for confirmation when classification would create an external or high-impact task.
- **missing:** A pendant/ESP32 button-to-record event and local audio framing protocol; An offline queue for captures when the pendant is only USB-attached or temporarily disconnected; A classifier that maps text to Notes, Reminders, project journal, or a review inbox with confidence and provenance

### "“Before you send, buy, publish, delete, or change anything important, ask me to press the pendant; only that physical press should authorize this exact operation.”"
- **useful because:** A physical cryptographic gesture is harder to trigger accidentally than voice and does not expose approval secrets in speech. It gives the owner one consistent, device-bound authorization across browser sessions, Mac apps, and relay jobs.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap deterministic verifier for the signed challenge; reserve the realtime model for explaining the pending operation in plain language.
- **latency:** Challenge and pendant acknowledgment under 500 ms over USB; under 2 seconds when relayed over LTE.
- **cost:** Negligible model cost; approximately 1–2 KB per authorization receipt and occasional relay storage.
- **security:** The challenge must bind to exact action arguments, target account, expiry, and session; prevent replay and downgrade to voice approval. Losing the pendant needs revocation. Show a human-readable summary before the press and retain an auditable receipt.
- **missing:** A cryptographic challenge-response protocol between pendant and Mac/relay; Action intents that expose a canonical hash of all irreversible arguments; A browser/Mac executor gate that refuses execution without a matching unexpired physical authorization

### "“If I set a check-in deadline and then become unreachable, try the pendant, my Mac, and my approved contact channels in order; only escalate after showing that each attempt failed.”"
- **useful because:** The wearable is the one surface that can follow the owner away from the Mac. A transparent escalation chain could provide real safety value during travel, illness, or a solo activity without requiring the owner to keep a phone conversation open.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic scheduler and delivery receipts for escalation; a background model may summarize failures, but no model should decide whether to escalate or who receives a message.
- **latency:** Heartbeat and deadline evaluation within 30 seconds; each escalation attempt gets a bounded timeout and a final status within 2 minutes.
- **cost:** Low scheduled-job cost plus SMS/email/channel fees; roughly $0.01–$0.20 per escalation attempt depending on channel.
- **security:** This is safety-critical and can expose location or distress information. Require explicit setup, named contacts, a test mode, clear cancellation, signed delivery receipts, no inferred medical claims, and confirmation of the exact message and data shared before arming.
- **missing:** A durable deadline/heartbeat contract spanning pendant, relay, and Mac; LTE/device registration and a low-power pendant heartbeat path; A verified contact-channel adapter with delivery receipts and a prominent armed/disarmed state


## Changes it proposed to its own stack

### `firmware` — Add a physical, offline-capable panic/abort gesture to the nRF9160 pendant: a long press emits a signed high-priority abort event over USB serial (and LTE when registered), flashes the LED distinctly, and is idempotently consumed by the relay to cancel all owner-scoped Mac/browser jobs that have not reached an irreversible checkpoint. The event must queue locally if disconnected and expire after a short TTL.
- **owner gets:** The owner can stop an automation immediately with the device in their hand, even when the voice link or Mac UI is stuck—preventing an unwanted send, purchase, or other external action.
- effort: Medium-high: firmware gesture/state machine, signed event framing, relay cancellation fan-out, and job-runner cancellation semantics.  ·  risk: False triggers could cancel useful work; use a deliberate 2–3 second hold plus LED/audio confirmation. A queued abort must not cancel a later unrelated job, so bind it to an owner/session epoch and TTL. Recovery is simply rerun the canceled job after review.
- cost: Negligible API cost; roughly 1–2 KB firmware flash and well under 2 KB RAM. No new hardware if the existing button/LED are usable.  ·  latency: Local LED indication under 100 ms; USB cancellation target under 500 ms, LTE path dependent on network.
- security: Abort events need authenticity and replay protection; never accept a bare serial byte as a global cancel. Keep payload to owner/session/job epoch, not content.
- depends on: A stable pendant-to-Mac serial event protocol; Durable job cancellation propagation through /jobs/:jobId/cancel and browser command deletion; An irreversible-action checkpoint contract in the Mac/browser runners

### `interaction` — Add a cross-surface 'intent lease' protocol: every action the judgement faculty hands to faculty-action carries an owner, scope, expiry, and allowed side effects. The relay displays the lease state, the Mac/browser executors enforce it at every step, and the pendant can renew or revoke it with a deliberate gesture. Expired leases halt before the next external mutation and report the exact boundary.
- **owner gets:** Long-running automation will stop being a runaway process. The owner can safely say 'continue for the next ten minutes' or revoke authority from the pendant, even if the original conversation has ended.
- effort: High: shared lease schema, enforcement middleware in both executors, relay persistence, and pendant gesture/state UI.  ·  risk: Clock skew, lost renewals, or an overly short lease could interrupt benign work. Use server-issued monotonic expiries, checkpoint only between steps, and make paused jobs resumable rather than silently failed.
- cost: Tiny metadata overhead and negligible API cost; no new hardware if the current button/LED can signal lease state.  ·  latency: One local verification per action step; renewal under 500 ms on USB and a few seconds over LTE.
- security: Strongly improves least-privilege and revocation. Lease tokens must be signed, audience-bound, non-replayable, and exclude raw credentials.
- depends on: Canonical action intents and preconditions; Durable job checkpoints and receipts; A pendant gesture/event transport


## What it asked for

_Nothing._
## Its own summary

Round 130 produced three new action-oriented proposals: meeting tap-markers that yield sourced follow-ups, desk-away continuity handoffs, and a pendant double-tap voice-capture workflow. I also proposed a firmware-level offline panic/abort gesture that can cancel owner-scoped Mac/browser jobs before irreversible checkpoints. The recorder accepted all four as non-duplicates. The connective routes already exist; the missing work is the contracts between them.

**Biggest unknown:** I still need the exact pendant/ESP32 serial event and audio framing protocol, the irreversible-action checkpoint/cancellation contract, and owner decisions on recording retention and approval thresholds. I also still lack the owner’s timezone/action priorities and the previously requested build/device probe; I will not re-request those this round. Accessibility remains manually blocked by the owner, but none of these proposals depends on it.

