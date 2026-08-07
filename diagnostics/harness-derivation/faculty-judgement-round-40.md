# Harness derivation — faculty-judgement — round 40

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep me from dropping the people I care about: notice when a meaningful conversation or promise needs follow-up, show me the evidence, and prepare a personal draft or reminder—never send anything unless I approve.”"
- **useful because:** Important relationships currently live across email, calendar, notes, and memory. A single node cannot reliably know the thread, the promise, and the right time; the hive can combine private browser evidence, Mac notes/calendar, and a brief pendant review without nagging.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → unified
- **model tier:** Background/cheap model clusters messages and calendar into candidate follow-ups; a stronger model is used only when wording a sensitive draft. Realtime is used only for the owner's final spoken review.
- **latency:** Overnight or every few days; under 2 minutes for extraction, with a 10-second spoken review when the owner asks. No interrupt unless urgency and quiet-hours policy permit.
- **cost:** Roughly $0.03–$0.15 per scan depending on message volume; drafting dominates, not extraction. Store hashes and short evidence snippets rather than whole mail.
- **security:** Private mail, calendar, and notes leave the browser/Mac only as narrowly scoped excerpts. Never infer sensitive relationship facts as certain; show source/date and confidence. Drafts and reminders are reversible; sending messages or contacting anyone always requires explicit approval.
- **missing:** A durable cross-surface relationship/commitment model that links people, conversations, promises, and last contact with provenance and expiry.; A deduplicated review queue with snooze, dismiss, 'already handled,' and sensitivity controls.; A background scheduler that can read authenticated browser pages and Mac notes/calendar while respecting quiet hours.; A pendant-friendly evidence card/audio item that lets the owner approve a reminder or request a draft without opening the Mac.

### "“When something changes my day, repair the rest of it: notice cancellations, delays, or new commitments across my calendar, mail, and logged-in services; show me what conflicts, suggest the smallest workable reshuffle, and prepare the reminders or drafts needed to recover.”"
- **useful because:** The owner currently receives isolated notifications and must manually reconstruct consequences. The hive could connect the changed external fact to the rest of the day: Mac calendar and local tasks, authenticated browser reservations or work portals, and the pendant’s immediate spoken review. It would help preserve commitments without silently changing them.
- **path:** browser-extension → mac-planner → mac-vision → mac-terminal → relay-realtime → pendant → unified
- **model tier:** Background model detects changes and computes schedule impact; a cheaper deterministic solver ranks feasible repairs. Realtime is used only when the owner asks for the short explanation or approval.
- **latency:** Recompute within 2–5 minutes of a trusted change, but defer spoken delivery until a safe attention window. A concise review should take under 20 seconds.
- **cost:** Approximately $0.02–$0.10 per event depending on how many private sources must be checked; schedule solving is mostly local and cheap. Draft generation is the dominant model cost.
- **security:** Calendar, mail, reservations, and task data are sensitive. Keep raw content on its source surface where possible, export only normalized times, obligations, and cited snippets, and attach freshness/confidence to every detected change. Never move appointments, cancel reservations, send messages, or create external commitments without explicit approval.
- **missing:** A trusted cross-surface change event with source identity, timestamp, evidence, and deduplication.; A constraint-aware day-repair engine modeling fixed events, travel/buffer time, deadlines, energy or focus preferences, and reversible alternatives.; A diff view/audio protocol that explains exactly what changed and what each proposed repair would affect.; Approval-bound execution for creating reminders, editing local plans, and preparing—not sending—communications.; A durable recovery record so a dismissed or postponed repair can be resumed without recomputing from stale facts.


## Changes it proposed to its own stack

### `routines` — Add an adaptive 'human follow-up budget' to scheduled work: learn only from explicit owner actions (snooze, dismiss, approve, mark handled), cap candidates per day, merge duplicate evidence across Gmail/calendar/notes, and schedule review when the pendant is idle rather than interrupting active conversation.
- **owner gets:** The owner gets timely help maintaining relationships without another noisy daily briefing or a stream of speculative nudges.
- effort: Medium: event schema, candidate deduplication, quiet-hours/pendant-idle signal, and a small review UI/audio protocol.  ·  risk: False positives could feel invasive or damage trust; recover with one-tap dismiss/forget and per-person pause. A bug could over-notify; enforce hard daily caps and an emergency disable.
- cost: Low incremental API cost (mostly embeddings/rules); approximately $0.01–$0.05/day for deduplication and ranking.  ·  latency: No realtime impact; background scan adds seconds to scheduled jobs and review is deferred until idle.
- security: Raises sensitivity of personal-relationship data. Encrypt stored candidate metadata, minimize excerpts, use short TTLs, and keep raw message bodies on the originating surface.
- depends on: Authenticated browser read access and Mac note/calendar access; Typed provenance/context projection; Durable review queue and owner interruption preferences

### `integration` — Create a cross-surface temporal event bus for owner-impacting changes. Each event must carry a stable subject, source surface, observedAt, effectiveAt, evidence reference, confidence, and supersedes key. The bus should reconcile duplicates and out-of-order updates, then emit an impact request to the day-repair solver rather than directly executing actions.
- **owner gets:** A cancellation, delay, or changed deadline would become one coherent explanation instead of several contradictory alerts. The owner could trust that the proposed repair reflects the newest known reality and can see why it was suggested.
- effort: High: adapters for calendar, authenticated browser pages, Mac jobs/notes, and relay schedules; durable event storage; ordering and supersession rules; impact callbacks; and a small evidence API.  ·  risk: Bad source data or duplicate events could cause unnecessary replanning. Quarantine low-confidence events, require corroboration for consequential changes, retain the prior plan, and make every proposal reversible. If the bus fails, existing calendars and jobs remain unchanged.
- cost: Low-to-moderate storage and background processing cost; roughly $0.01–$0.05 per active day before model reasoning. No need for realtime inference on every event.  ·  latency: Seconds to propagate a change; model-based impact analysis can run asynchronously. No added latency to ordinary pendant conversation.
- security: The bus becomes a high-value map of the owner's movements and obligations. Encrypt event payloads, minimize content to structured facts plus short-lived evidence pointers, apply per-source retention, and prevent one surface from reading unrelated event details.
- depends on: Cross-surface authenticated source adapters; Durable event and evidence storage; Constraint-aware day-repair solver; Explicit approval-bound action executor


## What it asked for

_Nothing._
