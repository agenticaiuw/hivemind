# Harness derivation — faculty-judgement — round 134

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before, during, and after my meetings, keep me from losing the thread: brief me from Calendar and the relevant logged-in tabs, let me tap the pendant to capture decisions and commitments offline, then reconcile those captures with the meeting notes on my Mac and prepare reminders or drafts for my review.”"
- **useful because:** This closes the loop that meeting-prep features leave open: the owner gets continuity from intention to remembered commitment, even when the pendant is disconnected and the Mac/browser permissions are imperfect. It is a genuinely joint wearable+Mac+browser+relay workflow.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → mac-terminal → unified
- **model tier:** Realtime only for the short spoken briefing and button-confirmation dialogue; use a cheaper background model to reconcile notes and generate proposed follow-ups after the meeting.
- **latency:** Briefing under 8 seconds; an offline button capture must acknowledge locally in under 150 ms; post-meeting reconciliation can take 1–3 minutes.
- **cost:** About $0.01–$0.05 per meeting depending on transcript length; browser extraction and speech transcription dominate, while the spoken acknowledgment is tiny.
- **security:** Private calendar, meeting notes, and authenticated tabs leave the Mac only to the relay/model path; redact unrelated tabs and default to drafts/reminders, never send mail or submit forms without confirmation. Offline captures must be encrypted at rest and expire after reconciliation.
- **missing:** A pendant-local commitment capture queue and offline handoff marker; A cross-surface intent/obligation reconciliation service; A reliable meeting audio/transcript source and explicit owner interruption preferences; A browser session selector that can restrict briefing to named tabs

### "“When you answer a factual question about my accounts, machine, schedule, or browser, tell me whether the evidence is fresh and sufficient; if it is stale, contradictory, or a permission-blocked guess, say so in one sentence and offer the smallest next check instead of pretending.”"
- **useful because:** The current system can report successful-looking no-ops and has already observed stale browser heartbeats, failed accessibility probes, and a timezone conflict. This makes trust a user-visible behavior: the owner can distinguish an answer from a guess and repair bad state without learning the internals.
- **path:** faculty-perception → faculty-judgement → faculty-action → relay-realtime → mac-planner → browser-extension
- **model tier:** Use a cheap classifier/rules layer for freshness, provenance, permission, and contradiction checks; reserve realtime reasoning for explaining the conflict and asking the one necessary question.
- **latency:** Add less than 300 ms to ordinary answers; a corrective probe may take up to 5 seconds, with an immediate spoken 'I need to check' acknowledgment.
- **cost:** Under $0.005 for routine answers; costs rise only when a corrective browser/Mac probe or model reconciliation is required.
- **security:** Expose source age and coarse failure reasons, not tokens, URLs from unrelated tabs, or sensitive snippets. Never silently downgrade a blocked read into an inferred account state.
- **missing:** A provenance-aware claim reconciler with freshness/permission semantics; A compact spoken uncertainty format and owner correction path; Cross-surface probes that return typed evidence rather than receipt-only success

### "“Give me a private, one-button 'where I left off' capsule: from the pendant, resume the last unfinished conversation or Mac/browser job with its goal, what was actually completed, what failed, and the single safest next action—without replaying anything.”"
- **useful because:** The owner's repeated failed requests for bridge activation, status, and completion receipts show that knowing whether work really happened is harder than starting it. A physical resume gesture turns fragmented sessions and dropped links into an actionable next moment, while explicitly preventing duplicate browser or Mac mutations.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Use deterministic job/session receipt retrieval and a cheap summarizer; use realtime only to speak the capsule and handle a follow-up command.
- **latency:** Local button acknowledgment under 150 ms; capsule spoken within 3 seconds when receipts are cached, or within 8 seconds after a live status check.
- **cost:** Typically under $0.01 per resume; the dominant cost is a live check or summarization when the prior job has many receipts.
- **security:** Capsules may reveal private work, so require the pendant's local button gesture and suppress sensitive values by default. Resume is read-only until the owner explicitly confirms a mutation; stale or ambiguous jobs must be labeled rather than retried.
- **missing:** A pendant-local resume trigger and small encrypted handoff marker; A cross-surface recovery/revalidate service that can classify completed/failed/unknown without replay; A concise receipt-to-speech renderer

### "“Let me use the pendant as a private control surface in public: acknowledge that you heard me, tell me silently whether you are thinking, need my approval, or failed, and let me cancel before anything consequential happens—without speaking sensitive details aloud.”"
- **useful because:** Today the pendant has one button and one LED, but the owner cannot reliably distinguish a delayed request from a failed one without asking verbally. This capability makes interaction socially safe and prevents duplicate commands or accidental approvals when audio is unavailable.
- **path:** pendant → relay-realtime → faculty-judgement → faculty-action → mac-planner → browser-extension
- **model tier:** Use deterministic local state signaling for received/working/approval-needed/failed/cancelled; use realtime reasoning only for the spoken request and any actual approval dialogue.
- **latency:** Local received/cancel feedback under 100 ms; remote state transition reflected within 500 ms when connected; detailed status can wait.
- **cost:** Less than $0.005 per interaction beyond the underlying task; haptic signaling itself has no API cost.
- **security:** Never encode message content or account names in vibration patterns. Approval must be explicit and bound to a displayed/spoken action summary; cancellation must be honored locally even if the network is unavailable.
- **missing:** Haptic hardware and a second unambiguous control; A pendant-local universal stop latch that survives dropped links; A relay-to-pendant state protocol with monotonic request IDs; Action gating that cannot treat a receipt-only success as completion


## Changes it proposed to its own stack

### `firmware` — Add a one-button local 'handoff capsule' record mode: a long press stores up to 20 seconds of Opus microphone audio plus a timestamp, a short press acknowledges and queues it, and a double press cancels. Persist only a bounded ring buffer on flash; LED patterns indicate queued, uploading, and failed states. On reconnection, relay transcribes and links the capsule to the active Mac/browser job without executing it.
- **owner gets:** The owner can save a thought, decision, or recovery note while walking away from the Mac or during a dropped link, then find it attached to the right unfinished task instead of trusting memory.
- effort: Medium-high: button gesture state machine, flash wear-safe ring buffer, upload protocol, and server-side job association.  ·  risk: Accidental recording and flash wear; cap duration/count, give a clear LED acknowledgment, encrypt queued payloads, and provide a long-press erase gesture. Never upload automatically to an unrelated active job.
- cost: No API cost for capture; roughly 10–30 kB flash per 20-second low-bitrate clip, negligible added power except during recording/upload.  ·  latency: Local acknowledgment under 150 ms; upload/transcription deferred to background.
- security: Audio is sensitive. Encrypt at rest with a device key, transmit only after authenticated pairing, and enforce expiry/deletion after transcription.
- depends on: A pendant-local offline handoff marker; Cross-surface job/intent association service; A tested flash persistence layout that fits the 1 MB application image

### `hardware` — Add a small coin vibration motor and a second capacitive or tactile input to the wearable, with a dedicated low-power haptic driver and an explicit silent-mode switch. Define three haptic symbols (received, needs approval, failed) and reserve the existing LED for bench diagnostics rather than user feedback.
- **owner gets:** The owner can use the assistant in public, while walking, or with headphones off and still know whether it heard them, is waiting for approval, or failed. A second control also makes cancel/approve unambiguous instead of overloading one button's timing.
- effort: Medium hardware revision plus enclosure, power, firmware gesture, and accessibility testing; not a software-only change.  ·  risk: Added power draw, accidental touches, and confusing patterns. Recover with a physical silent-mode switch, conservative vibration durations, and a long-press universal cancel gesture; retain the current single-button behavior as a compatibility mode.
- cost: Approximately $1–$4 incremental component/BOM cost and brief 5–20 mA vibration peaks; negligible API cost.  ·  latency: Immediate local acknowledgment under 100 ms; no network latency for received/failed indication.
- security: No new network exposure. Haptic output must not reveal sensitive content to bystanders; use only coarse state symbols and suppress them in silent mode.
- depends on: A firmware-local universal cancel/stop state machine; A documented haptic vocabulary and user preference storage; A revised wearable enclosure and power budget


## What it asked for

_Nothing._
