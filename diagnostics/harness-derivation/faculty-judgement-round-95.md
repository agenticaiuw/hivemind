# Harness derivation — faculty-judgement — round 95

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live cross-surface contradiction** — At 13:35, /browser/status says extension offline with 9 pending commands, while /observe still exposes 3 browser tabs including a UTC page last used at 06:26. /pipeline contains processing runs from 07:22 and 07:17 despite a completed 12:00 run. /jobs has browser failures that waited ~45 seconds. These must not be treated as current reachable browser capability.
  - evidence: GET /observe, GET /browser/status, GET /pipeline, and GET /jobs in round 95

## Capabilities it proposed

### "“I’m back—what was I in the middle of, and what should I do next?” Give me one trustworthy resume card assembled from my pendant conversation, Mac work, browser tabs, calendar, and unfinished jobs; let me say continue, park it, or discard it."
- **useful because:** Today each surface remembers a different fragment and stale browser/pipeline records look live. This turns an interruption or link loss into a safe, human-sized re-entry point rather than making the owner reconstruct context. It is specifically hive-native: only the pendant knows the return moment and spoken intent, the Mac knows active project and local work, the browser knows private tabs, and the relay knows jobs that continued while away.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use a cheap background model to assemble and rank candidate threads; use realtime only to speak the short card and interpret the owner's continue/park/discard choice. Deterministic freshness, conflict, and authorization checks must run before either model sees data.
- **latency:** On reconnect, capture locally in under 1 second; relay reconciliation under 3 seconds; spoken card under 5 seconds. If browser is offline, say so and produce a partial card rather than waiting.
- **cost:** About $0.005–$0.03 per return event, dominated by the small synthesis prompt; most events should be deterministic/no-model when there is one obvious active thread.
- **security:** Private browser titles/content and local project names leave their surfaces only when selected for this card. Never include secrets or raw page bodies by default. Continue must revalidate state hashes, lease, and idempotency keys; discard must cancel only queued reversible work and never delete data. Require confirmation before any external send or destructive action.
- **missing:** A durable resume-thread record linking spoken intent, active Mac project, browser session/tab evidence, pipeline/job IDs, and last-seen state hashes.; A freshness/contradiction auditor that marks stale offline browser and pipeline records as unavailable instead of evidence.; A pendant reconnect/pause event with a monotonic sequence and local nonce, plus a three-way disposition (continue, park, discard).; A compact spoken-card/audio delivery acknowledgement path and a reviewable park list.

### "“How will this land?” Before I reply to this person, show me the likely interpretations, what I may be implicitly promising, and three short replies in my voice—considering the current thread, our recent calendar context, and whether I have already left them waiting. Do not send anything."
- **useful because:** The owner can already ask for a draft, but not for the human consequences of sending it. This prevents accidental escalation, overpromising, and tone mismatch by combining private message context, timing, and the owner's actual schedule into a decision aid. It is a judgement capability, not an auto-reply system.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use a cheaper background model to collect and normalize thread/calendar timing and produce candidate interpretations; use the realtime tier only when the owner asks aloud and only for the concise spoken comparison. Keep final wording generation local or on the authenticated surface where possible.
- **latency:** Collect context in 2–5 seconds; spoken answer in under 8 seconds. If a private surface is unavailable, identify the missing evidence and give a clearly labeled partial answer.
- **cost:** Approximately $0.01–$0.06 per request, dominated by analyzing the selected thread and generating three alternatives; deterministic timing checks add negligible cost.
- **security:** Message contents and relationship context are highly sensitive. Scope access to the explicitly selected thread/contact, avoid retaining raw text after the response, and show which sources were used. Never send, schedule, or modify a message. The owner must explicitly choose any later send action.
- **missing:** A short-lived, source-cited communication-context bundle spanning Mail/Messages, authenticated browser threads, and Calendar.; A local-only or encrypted relationship/tone profile that the owner can inspect and delete; it must not infer sensitive traits.; A consequence rubric distinguishing observation from speculation, with confidence labels and an explicit unknown state.; A handoff that preserves the selected draft and evidence without silently crossing the send boundary.


## Changes it proposed to its own stack

### `context` — Add a cross-surface evidence lease and contradiction auditor. Every observation from /observe, /pipeline, /jobs, browser status/sessions, and pendant reconnect events gets a source timestamp, monotonic sequence, freshness TTL, and state hash. Before judgement or execution, the auditor classifies each fact as live, stale, unreachable, contradicted, or unknown; it emits a compact reason and suppresses stale records from plans. A browser heartbeat can revive only browser facts, and a Mac receipt can revive only its own job—not infer that the other surface is healthy.
- **owner gets:** The owner should never be told that a browser task is running when the extension is offline, or that a pipeline action is current when it is an old approval-blocked record. They get honest answers and fewer dangerous duplicate retries after interruptions.
- effort: Medium: shared schema plus adapters at observation ingestion and a preflight gate in judgement/action; add deterministic tests for offline, reconnect, duplicate receipt, clock skew, and contradictory status.  ·  risk: Over-aggressive expiry could hide useful long-running work. Recover with per-source TTL classes, explicit 'unknown/unreachable' wording, and a manual refresh path; never silently convert unknown into failure or success.
- cost: Negligible storage and CPU; roughly 100–300 tokens of metadata per observation and no model call for classification.  ·  latency: Under 100 ms locally; at most one extra read of source status when a fact is near expiry.
- security: Improves privacy by preventing stale private page data from being reused indefinitely; retain hashes and metadata rather than page bodies. Do not broaden access scopes.
- depends on: A typed event envelope with source, observedAt, sequence, stateHash, TTL, and sensitivity; Pre-execution revalidation of state hashes and idempotency keys; Browser heartbeat and Mac receipt adapters

### `integration` — Close the 24 kHz audio loop with a pendant delivery receipt: relay assigns an audioId and sequence, pendant persists received/started/finished/failed plus a short checksum and playback duration in its offline store, and reconnect uploads receipts. The spoken agent reports 'ready on pendant' only after finished (or honestly 'downloaded, not yet played'). Deduplicate by audioId and expire PCM after acknowledgement.
- **owner gets:** A 24 kHz file being rendered and accepted by the relay is not the same as the owner hearing it. This makes the pendant's answer trustworthy and prevents silent loss or repeated playback after reconnect.
- effort: Medium firmware/relay integration; add a tiny receipt state machine and reconnect upload, then test power loss during download and playback.  ·  risk: A lost receipt could cause a retry or uncertainty. Use idempotent audioId, bounded retry, and say unknown rather than replay automatically; keep the last few receipt records only.
- cost: Negligible model cost; a few dozen bytes per receipt and small LTE traffic. PCM retention can fall to zero after acknowledgement.  ·  latency: No added speech latency; adds at most one round-trip before claiming completion. Playback itself remains device-local.
- security: Receipts contain no audio text, only opaque ID/checksum/status. Enforce short PCM retention and authenticated device sequence numbers.
- depends on: Existing 24 kHz mono PCM generation and relay upload path; Pendant offline event store and reconnect sequence; Authenticated relay endpoint for delivery receipts

### `context` — Create an ephemeral communication-consequence sandbox separate from durable memory. It snapshots only the selected message thread, relevant calendar timing, and explicit prior commitments; runs tone/interpretation alternatives with provenance; presents three candidate replies and predicted commitment deltas; then destroys raw thread content after the decision unless the owner explicitly saves a draft. No candidate can enter the send queue automatically.
- **owner gets:** It gives the owner a private rehearsal space for difficult messages—seeing not just what to say, but how each choice could be understood—without turning intimate conversations into permanent AI memory or risking an accidental send.
- effort: Medium-high: authenticated connectors for Mail/Messages/browser threads, a typed commitment-delta representation, encrypted ephemeral storage, and a UI/audio flow for comparing alternatives.  ·  risk: Tone predictions can be wrong or overconfident. Mitigate with source excerpts, uncertainty labels, multiple interpretations rather than a single verdict, and a clear 'I cannot tell' outcome. Recovery is simply discarding the sandbox; it has no external side effects.
- cost: Roughly $0.02–$0.10 per analysis depending on thread length; encrypted ephemeral storage is inexpensive and should be hard-expired within hours.  ·  latency: About 5–10 seconds for a full analysis; stream the first evidence and uncertainty immediately so the owner is not left waiting silently.
- security: High sensitivity: process on the Mac where possible, encrypt any relay payload, restrict to the selected thread, redact secrets, audit access, and hard-delete raw text at expiry. Sending remains a separate explicit action.
- depends on: Authenticated Mail/Messages/browser context adapters; Ephemeral encrypted context store with hard expiry; Source-citation and uncertainty formatting; A strict separation between draft/rehearsal and external-send execution


## What it asked for

_Nothing._
