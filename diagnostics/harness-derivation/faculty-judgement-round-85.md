# Harness derivation — faculty-judgement — round 85

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“That didn’t work—tell me why, fix whatever is safe, and either finish it or tell me the one thing I need to do.”"
- **useful because:** Today a failed request is a dead end (the owner has repeatedly seen failed Gmail, calendar, GitHub, and browser requests). This turns an opaque failure into a useful outcome: classify whether the cause was offline/expired session/unsupported action/permission, retry only idempotent steps, preserve the original intent, and give one short spoken repair instruction when human intervention is unavoidable. It is specifically cross-surface: the pendant supplies the interrupted intent and speaks the result, the relay correlates the failure and keeps it durable, Mac diagnostics inspect the local bridge/job, and the browser session reports authentication/tab state.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background/cheap model for receipt classification and retry planning; realtime only for the final one-sentence explanation or a live confirmation.
- **latency:** Under 3 seconds to classify a completed failure; up to 30 seconds for safe retries. Never block the pendant conversation while diagnosis runs.
- **cost:** About $0.001–$0.01 per failure, dominated by a small classification call; retries and status reads are local/HTTP with negligible API cost.
- **security:** Diagnostics must redact page text, cookies, tokens, and secret memory. Never retry sends, purchases, deletes, or submissions; require confirmation for any irreversible step. Show the owner exactly which safe steps were retried and retain a short receipt with expiry.
- **missing:** A typed failure taxonomy with retryability and owner-action codes; A durable link from spoken intent to job/action receipt and its originating surface; A redacted cross-surface diagnostic bundle and a repair queue UI; Idempotent retry policy that understands browser session expiry versus action failure

### "“Remember why I decided this, and remind me of that reason when the decision comes back up.”"
- **useful because:** The system currently remembers requests and outcomes, but not the owner's own rationale. Capturing a 10-second spoken reason while it is fresh—and resurfacing it when the related meeting, deadline, email, or logged-in page returns—prevents repeated reconsideration and makes the assistant feel continuous rather than merely archival. It is a genuinely hive-only behavior: the pendant hears the rationale in the moment, the relay stores a compact privacy-labeled rationale, Mac correlates it with Calendar/Mail/Notes or a task, and browser evidence can identify the same decision when it reappears.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Cheap background model to extract the decision, alternatives, rationale, and revisit trigger; realtime only to ask a single clarification when the audio is ambiguous and to speak the resurfaced reminder.
- **latency:** Capture acknowledgement under 1 second; extraction and linking within 10 seconds. Resurfacing should add no more than one short sentence to an otherwise requested brief.
- **cost:** Roughly $0.002–$0.02 per captured rationale and under $0.001 per resurfacing, dominated by transcription/structured extraction; store text, not raw audio, by default.
- **security:** Rationales can contain sensitive health, work, or relationship information. Encrypt at rest, apply owner-selected sensitivity and TTL, never send rationale text to a website, and require confirmation before writing it into a shared calendar, CRM, or outbound message. Spoken reminders should be private and suppressible.
- **missing:** A first-class rationale record (decision, chosen option, alternatives, reason, confidence, revisit trigger, sensitivity, expiry); Entity linking across spoken intent, Mac records, and authenticated browser pages without exporting private page contents; A lightweight owner correction flow ('that is not why') and deletion by voice; Trigger evaluation on calendar/email/page-watch events

### "“What did you decide not to tell me, and why?”"
- **useful because:** A proactive assistant inevitably suppresses duplicates, low-confidence findings, and items during quiet hours. Today the owner cannot audit that silence, so they cannot tell whether the system protected their attention or simply missed something. This gives them a private, chronological omission log: suppressed Mac jobs, browser-watch changes, relay notifications, and pendant brief items, each with the reason, confidence, expiry, and a one-sentence option to promote or permanently dismiss it. It is not another briefing or page watch; it is an accountability surface for the assistant's decisions about the owner's attention.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Cheap background policy/model pass to classify and summarize omitted items; realtime only when the owner asks aloud or promotes an item.
- **latency:** Maintain the log asynchronously with no impact on live speech. Return a concise answer in under 2 seconds from durable records.
- **cost:** About $0.001–$0.01 per omitted-item summary; most work is local event storage and deterministic policy explanation.
- **security:** The log itself may reveal private mail, pages, or sensitive jobs. Keep raw content on its originating surface, store redacted summaries and hashes, encrypt at rest, apply short retention, and require explicit confirmation before replaying sensitive content aloud. Never treat omission as consent to discard.
- **missing:** A durable attention-decision/omission record with policy reason, confidence, source, expiry, and content sensitivity; A redacted cross-surface event feed spanning relay, Mac jobs, browser watches, and pendant queues; Owner controls to promote, dismiss, or delete an omitted item; A deterministic explanation vocabulary so the assistant cannot invent a post-hoc reason


## Changes it proposed to its own stack

### `memory` — Add a Decision-Rationale Ledger between pipeline audio/events and the Mac/browser surfaces. It stores only structured rationale records (decisionId, chosen option, rejected alternatives, owner words or redacted summary, revisit trigger, sensitivity, TTL, and source/audio receipt), resolves links to calendar/mail/task/page entities, and emits a single `rationale_due` event. Provide voice correction/deletion and deterministic conflict rules: newer owner correction wins; never infer a rationale from an action alone.
- **owner gets:** When an old choice resurfaces, the pendant can remind the owner of their own reason instead of making them reconstruct it; if circumstances changed, they can correct or discard it in one sentence.
- effort: Medium: schema/API, entity-linking adapters for Calendar/Mail/browser watch events, and a small pendant voice command grammar; no new model training.  ·  risk: Wrong links or stale reasons could mislead. Mitigate with confidence thresholds, explicit 'you said...' wording, expiry, source/time shown in dashboard, and no reminder when confidence is low. Recovery is delete/correct by voice or dashboard.
- cost: Low storage and background extraction cost (~$0.002–$0.02 per capture); no recurring model cost except event-trigger evaluation.  ·  latency: Acknowledgement remains realtime; structured extraction is asynchronous. A due reminder adds <1 second to an existing brief.
- security: Potentially sensitive personal reasoning; encrypt, redact by default, enforce sensitivity TTL, and keep it out of browser/Mac payloads unless the linked action explicitly needs it.
- depends on: A typed event bus carrying source IDs and timestamps; A privacy-aware compact context projection rather than raw fleet context; Owner-visible delete/correct controls

### `interaction` — Create an append-only Attention Decision Ledger that records every item the system deliberately suppresses, merges, delays, or drops across pendant audio, relay notifications, Mac jobs, and browser watches. Each entry must contain a machine-selected policy code, confidence, source reference, sensitivity, expiry, and whether the decision was reversible; the owner can ask for omissions, promote one, or delete it. Generate explanations only from the recorded policy code, never from a fresh model guess.
- **owner gets:** The owner gets verifiable control over the assistant's silence: they can confirm that quiet hours or deduplication protected them, discover a missed important item, and correct the policy without having to monitor every surface.
- effort: Medium: event schema, adapters at each notification/queue boundary, redaction, and a small dashboard plus pendant command grammar.  ·  risk: Logging too much could itself become distracting or expose sensitive information. Use redacted summaries, short retention, sensitivity-aware spoken output, and a single explicit audit command rather than proactive announcements. If the ledger is unavailable, normal delivery behavior continues.
- cost: Low storage and negligible inference cost; summaries can be generated in batch by a cheap model.  ·  latency: No live-path delay if writes are asynchronous; audit response is a database read plus optional summarization.
- security: The ledger is a sensitive map of the owner's life. Encrypt it, isolate per owner, retain hashes/source IDs rather than raw content, and require confirmation to replay private text aloud.
- depends on: A shared typed event envelope with source IDs and timestamps; Redaction and sensitivity classification at ingestion; A durable owner-visible retention/deletion policy


## What it asked for

_Nothing._
