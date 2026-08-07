# Harness derivation — faculty-judgement — round 143

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Use my private information to complete this, but keep the actual values on my Mac—tell the cloud and the pendant only what is necessary.”"
- **useful because:** The owner can get real work done on logged-in sites without turning the relay into a holder of passwords, health details, or financial data. The browser has the session, the Mac can compute locally, and the pendant can authorize without exposing the payload.
- **path:** browser-extension → mac-planner → relay-realtime → unified → faculty-judgement → faculty-action
- **model tier:** Use the cheap local planner for extraction/filling and the relay realtime model only to understand the spoken request and summarize a redacted result.
- **latency:** Under 5 seconds to identify the private fields; under 15 seconds for a normal form. The owner should hear one short confirmation and only wait longer for multi-page workflows.
- **cost:** ~$0.01–$0.05 per invocation; local browser/Mac work dominates latency, with a small realtime interpretation call.
- **security:** Private field values must never enter relay logs, D1, R2, model prompts, or spoken confirmations. Require owner confirmation before submission, and retain only field names plus hashes. Missing per-job data-locality policy and redaction enforcement.
- **missing:** A locality/redaction contract enforced at every event boundary; Browser action schema that can pass opaque local values without serializing them to the relay; A receipt that proves which fields were used without recording their values

### "“I changed my mind about that—find everywhere I committed to it, prepare the cancellations or corrections, and show me one review list.”"
- **useful because:** People revise plans after sending messages, creating reminders, editing documents, or submitting reversible browser forms. Today each surface forgets the others; this would turn a spoken change of mind into a bounded, reviewable cleanup instead of a scavenger hunt.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → mac-terminal → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap background model builds the candidate impact graph from receipts, calendar, mail, notes, browser history, and jobs; realtime is used only for the owner’s short request and the final spoken list.
- **latency:** Return an initial candidate list in 10 seconds, then progressively add evidence. Never execute corrections without explicit per-item or batch approval.
- **cost:** ~$0.03–$0.15 per review; scanning local indexes and browser tabs dominates, not model tokens.
- **security:** Do not infer commitments from private content without showing evidence. Separate drafts from sent messages and distinguish safe undo from destructive cancellation. Require confirmation for mail, deletion, purchases, or external submissions.
- **missing:** A cross-surface commitment/impact index with provenance and expiry; A correction-plan object that groups reversible actions and supports partial approval; Independent observation of sent-vs-draft state for each candidate

### "“Before I leave, give me a 20-second handoff: what I was doing, what is waiting on me, what is waiting on someone else, and the one thing I should carry forward.”"
- **useful because:** A worn device is present at the moment the owner walks away, unlike a desktop notification. This converts scattered Mac jobs, browser tabs, drafts, reminders, and pending replies into a tiny decision-free handoff that preserves momentum without demanding a full briefing.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → unified → faculty-perception → faculty-judgement
- **model tier:** Use a cheap local/background summarizer over structured receipts and current tabs; reserve realtime for a concise spoken rendering when the pendant button or disconnect event asks for it.
- **latency:** Generate in 2 seconds from cached state and speak in under 20 seconds. If state is stale, say so instead of blocking.
- **cost:** ~$0.005–$0.03 per handoff; mostly local summarization and one short audio response.
- **security:** The handoff may reveal sensitive project or browser titles to anyone nearby. Support a privacy level (headlines only, names omitted, or silent LED cue), and never read secrets aloud. Need owner-configured quiet/privacy behavior.
- **missing:** A device-local trigger on button/disconnect and a cached structured state snapshot; A freshness-aware reducer for jobs, browser tabs, reminders, and drafts; A private audio/LED delivery acknowledgement and retry policy

### "“Keep talking to me when the network disappears, remember the last few turns locally, and send the conversation outcome when you reconnect.”"
- **useful because:** The owner should not lose an interaction merely because LTE coverage, the Mac, or the relay drops. A genuinely wearable assistant needs graceful offline behavior rather than becoming a silent button outside coverage.
- **path:** pendant → relay-realtime → mac-planner → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** A small on-device speech/intent model handles a constrained offline vocabulary and queues encrypted audio or structured intents; the expensive realtime model resumes only after reconnection.
- **latency:** Local command acknowledgement under 500 ms; reconnect reconciliation within 10 seconds. Offline free-form conversation can be limited to clearly disclosed supported intents.
- **cost:** ~$0.01–$0.05 for reconciliation; the major cost is new hardware/firmware and encrypted local storage, not inference.
- **security:** Offline transcripts are sensitive and must be encrypted, bounded, and erasable by a physical gesture. Replayed intents must be idempotent and never perform irreversible actions without renewed confirmation.
- **missing:** A larger pendant MCU/RAM or a dedicated low-power speech/intent accelerator; Encrypted offline conversation journal and replay protocol; Firmware-side reconnect reconciliation with duplicate suppression; An explicit supported-offline-intent vocabulary

### "“While I’m in a meeting, listen for decisions and action items, then after it ends give me a private checklist and draft the follow-ups without sending anything.”"
- **useful because:** The pendant is the one surface present in the room, while the Mac and browser can resolve names, dates, projects, and existing threads afterward. This removes the need to remember commitments while preserving owner review before anything leaves.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime performs low-latency segmentation and candidate extraction; a cheaper background model reconciles names, calendar, files, and logged-in threads after the meeting.
- **latency:** Short spoken or LED capture acknowledgements immediately; checklist available within 2 minutes after the meeting. No continuous spoken summary during the meeting unless requested.
- **cost:** ~$0.10–$0.60 per meeting depending on duration; audio processing and transcription dominate.
- **security:** Explicit start/stop consent is mandatory; meeting audio must have short retention, local-first processing where possible, visible recording state, participant privacy controls, and no automatic sending.
- **missing:** A consent-aware meeting recording state on the pendant; Speaker/decision segmentation with uncertainty labels; A post-meeting entity resolver joining local files, calendar, and browser sessions; A review-only follow-up draft bundle


## Changes it proposed to its own stack

### `integration` — Add a typed private-computation envelope spanning browser bridge, Mac executor, relay event stream, and receipts. The relay issues an opaque field handle and policy (local-only, hash-only, or speakable); the Mac resolves handles inside the local process, browser fills them, and every boundary rejects raw values. Receipts contain field labels, policy decisions, and hashes only.
- **owner gets:** They can ask the system to use sensitive information on their behalf without making the cloud or spoken channel a copy of it.
- effort: High: new envelope types, browser/Mac plumbing, redaction tests, and receipt UI.  ·  risk: A missed serialization path could leak data; fail closed when policy metadata is absent, and provide a local diagnostic explaining which field blocked progress.
- cost: Negligible API cost; modest local CPU and storage for hashes and policy receipts.  ·  latency: Adds roughly 100–300 ms per field batch; local browser work remains dominant.
- security: Substantially improves confidentiality, but requires threat-model review of logs, exceptions, screenshots, and crash dumps.
- depends on: A per-job data-locality policy; Typed browser action results instead of free-form serialized payloads; Owner-visible redacted receipt viewer

### `context` — Create a cross-surface momentum snapshot with four typed buckets—owner-next, waiting-on-owner, waiting-on-other, and stale/uncertain—computed from Mac jobs and receipts, active project, browser tabs, reminders, drafts, and recent pipeline events. Attach source timestamps and a 2-minute cache, and expose a compact spoken rendering plus a silent privacy mode.
- **owner gets:** Walking away from the Mac no longer means losing the thread; the pendant can give one accurate next step rather than another noisy notification stream.
- effort: Medium-high: reducer, freshness rules, trigger integration, and a compact audio/LED delivery path.  ·  risk: False urgency or stale tabs could mislead; every item needs evidence and age, and uncertain items must be labeled rather than promoted.
- cost: ~$0.005–$0.02 per generated handoff; cached snapshots keep recurring cost low.  ·  latency: Immediate from cache; full recomputation under 2 seconds on the Mac.
- security: Potentially exposes project names in public audio; default to redacted headlines and require an explicit private mode for details.
- depends on: Device-local trigger or reliable pendant event; Freshness-aware state reducer; Audio delivery acknowledgement

### `model-routing` — Route correction-after-change-of-mind jobs through a two-pass planner: a cheap local candidate extractor first, then a stronger model only for ambiguous evidence conflicts. Require each proposed correction to cite its originating receipt, tab/source, and reversibility class before it can enter an approval batch.
- **owner gets:** Revising a plan becomes a short review instead of an unreliable sweep that either misses a commitment or overreacts to incidental text.
- effort: Medium: candidate schema, evidence joiner, conflict scoring, and approval-batch integration.  ·  risk: The extractor can miss implicit commitments; label coverage as incomplete and offer a deliberate deeper scan rather than claiming completeness.
- cost: Typically 60–80% cheaper than sending all content to the expensive tier; extra local indexing is small.  ·  latency: First candidates in 3–8 seconds; ambiguous cases may take another 10 seconds.
- security: Keep raw evidence local where possible and send only excerpts needed to resolve a conflict.
- depends on: Cross-surface commitment index; Typed reversible-action receipts; Owner approval policy for external effects

### `hardware` — Add a low-power wear/presence sensor to the pendant—capacitive skin contact or a dedicated clasp contact, backed by an accelerometer—and expose a signed worn/unworn state to firmware. When unworn, the device must suppress spoken secrets and require an explicit re-wear plus button gesture before resuming sensitive audio.
- **owner gets:** The pendant can safely behave differently when it is around the owner’s neck versus sitting on a desk or being handled by someone else, without requiring the owner to remember a privacy setting.
- effort: Medium hardware revision plus firmware driver, calibration, and false-positive testing across clothing and charging conditions.  ·  risk: False unworn readings could interrupt useful conversations; recover with a local non-secret acknowledgement and manual override that expires quickly. Sensor failure must fail closed for sensitive playback.
- cost: Roughly $1–$4 added components and under 1 mW average sensing power, subject to board revision.  ·  latency: Under 200 ms to change privacy state; negligible conversation latency.
- security: Reduces accidental disclosure from misplaced or unattended hardware, but the worn state itself should not be exposed as a remotely queryable location signal.
- depends on: A firmware privacy state machine; A signed device-event path to the relay; Owner-configurable classification of speakable versus sensitive responses


## What it asked for

_Nothing._
