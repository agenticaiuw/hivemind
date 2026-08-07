# Harness derivation — faculty-judgement — round 5

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Start this, and if I get interrupted or lose connection, keep my place and pick it back up when I’m ready.”"
- **useful because:** Today a dropped link or context switch makes the owner repeat themselves and leaves uncertainty about what happened. This would make the pendant a dependable continuity layer: it captures intent locally, the relay keeps a durable job, the Mac/browser checkpoint evidence and reversible changes, and the next conversation resumes from the exact safe boundary rather than restarting.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use gpt-5.6-luna for planning and reconciliation, gpt-4.1-mini for routine browser/UI steps, and gpt-realtime-2.1 only for the short spoken interruption/resumption exchange.
- **latency:** Acknowledge locally in under 300 ms; durable checkpoint within 2 s; background work can continue without the voice session. Resume briefing should be one short sentence, with detail on request.
- **cost:** About $0.01–$0.08 per ordinary resumed job, dominated by planner/reconciliation context; local acknowledgements and routine checkpoints should be negligible.
- **security:** The journal may contain private page excerpts and drafts, so encrypt it and retain only task-scoped evidence with expiry. Never replay or retry an irreversible action after interruption; require confirmation again if the checkpoint is stale or the target changed. The pendant should store only a compact intent token, not page content.
- **missing:** A shared resumable-job protocol with idempotent checkpoints across relay, Mac, and browser; Pendant offline intent/checkpoint queue and reconnect handshake; A durable owner-facing resume inbox/dashboard with evidence and safe-boundary status; A single policy engine that distinguishes reversible progress from confirmation-required actions

### "“When I’m in a meeting or focused, protect my attention; let only truly urgent things through, and catch me up afterward.”"
- **useful because:** The owner should not have to manually manage notification settings, remember which tabs matter, or fear missing something important. Calendar context on the Mac, the pendant’s explicit voice command and optional local sound/activity cues, browser account urgency, and the always-on relay can jointly enforce a temporary attention boundary and produce a quiet, prioritized catch-up afterward.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic rules plus gpt-4.1-mini for urgency classification and summarization; reserve gpt-5.6-luna for ambiguous policy conflicts. Realtime is only for the spoken 'focus/protect/I'm free' interaction.
- **latency:** Focus mode acknowledgement under 300 ms from the pendant; notification gating under 1 s; post-focus digest ready within 30 s of the owner becoming available.
- **cost:** Usually under $0.01 per focus session, mostly small classification/summarization calls; calendar and notification reads are local or relay metadata. Storage is a few event records per session.
- **security:** Notification content and calendar titles are sensitive. Keep raw content on the Mac where possible, send only urgency metadata to the relay, encrypt the digest, and make external changes (sending an auto-reply or changing shared status) confirmation-gated. Provide a physical/button escape to disable protection.
- **missing:** A cross-surface attention policy with explicit urgency categories and quiet hours; Mac notification interception and reversible focus-mode adapter; Calendar-aware session detector with owner override; Pendant local focus-state indicator and offline override; Post-session change ledger that deduplicates alerts already seen

### "“Remember the commitments I make in conversation, and help me keep them without making promises on my behalf.”"
- **useful because:** People routinely lose track of informal promises that never become calendar events or tasks. With an explicit phrase such as “remember that,” the pendant can capture a compact commitment, the relay can preserve it, and the Mac/browser can resolve the person, relevant thread, deadline, and supporting context. The system can then suggest a reminder or prepare a follow-up draft, while never contacting anyone or inventing a commitment without approval.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use gpt-realtime-2.1 only to detect and confirm the short explicit capture utterance; use gpt-5.6-luna asynchronously for entity/deadline resolution and conflict checking; use gpt-4.1-mini for routine extraction and draft preparation.
- **latency:** A local spoken acknowledgement in under 500 ms; commitment extraction and matching within 30 seconds; reminder or draft suggestions can be prepared in the background.
- **cost:** Approximately $0.01–$0.05 per captured commitment, dominated by asynchronous resolution across calendar/mail/browser context. Routine local capture and reminder storage should be negligible.
- **security:** Conversation audio and relationship data are highly sensitive. Require an explicit activation phrase or button, process the utterance transiently where possible, store only the commitment text plus provenance and expiry, and show the exact source and inferred fields. Never send a message, create a shared calendar event, or disclose that the system was listening without confirmation.
- **missing:** An explicit pendant capture mode with local buffering and immediate confirmation; A private commitment object with provenance, confidence, deadline, people, status, and expiry; Cross-source entity and thread matching across local contacts, calendar, mail, and authenticated browser pages; A review queue that distinguishes owner-stated commitments from model-inferred suggestions; Reminder and draft generation that is confirmation-gated for all outward communication


## Changes it proposed to its own stack

### `interaction` — Add a cross-surface Intent Thread and checkpoint protocol. Every task gets a stable thread ID, owner goal, current safe boundary, evidence pointers, pending confirmation, expiry, and idempotency key. The pendant can append a tiny offline 'pause/resume/cancel' event; relay durably orders events; Mac and browser workers acknowledge checkpoints only after recording before/after evidence. On reconnect, reconcile divergent state and present one resume decision instead of silently retrying.
- **owner gets:** If Wi‑Fi, the browser, or the Mac disappears mid-task, the owner will know whether anything changed and can continue with one phrase instead of reconstructing the task. It prevents duplicate sends, duplicate purchases, and ambiguous half-completed work.
- effort: Medium-high: shared schema and event store, adapters in relay/Mac/browser, pendant queue firmware, reconnect tests, and a small resume view.  ·  risk: A stale or duplicated event could resume the wrong task. Use monotonic sequence numbers, idempotency keys, expiry, and fail-closed behavior for irreversible steps; recovery is to mark the thread conflicted and ask the owner.
- cost: Small durable relay/D1/R2 storage cost; roughly one compact event per step. No meaningful model cost except occasional reconciliation, which should use the cheaper planner tier.  ·  latency: No added latency to the first spoken response; local pendant acknowledgement is immediate. Reconnect adds roughly 0.5–2 seconds for state reconciliation.
- security: Thread-scoped encrypted evidence and sensitivity labels reduce leakage. Do not copy secrets into the pendant; redact page text in events and require explicit confirmation tokens for external side effects.
- depends on: A durable browser command queue with tab/session affinity and typed results; A shared typed context service with provenance and expiry; A pendant-side offline queue that fits within the existing RAM/storage budget; Mac Accessibility/Screen Recording and browser bridge authorization being available

### `hardware` — Make the wearable product (not the current nRF9160 DK prototype) include a low-power haptic actuator, a two-color status LED, and a second physical button or capacitive touch zone. Reserve a tiny always-on event ring in external FRAM for intent/checkpoint controls, while keeping private content off-device. Define distinct tactile patterns for urgent alert, task paused, confirmation required, and focus mode.
- **owner gets:** The owner can pause, resume, cancel, or acknowledge work discreetly in a meeting or when the voice link is down, and can understand the pendant’s state without looking at a screen or speaking aloud. This turns continuity and attention protection into something dependable in real life rather than a phone-like software feature.
- effort: Medium hardware revision and firmware input/power work; validate wearability, accidental presses, and tactile patterns with the owner.  ·  risk: Extra components increase enclosure complexity and battery drain; accidental input could cancel or acknowledge a task. Require long-press for destructive controls, debounce locally, and make all irreversible actions fail closed. Recovery is a reconnect state reconciliation.
- cost: Roughly $2–$8 BOM increase at moderate volume; haptic pulses add low instantaneous draw but should be duty-cycled. FRAM is a few dollars or can be replaced by a small flash partition if endurance is acceptable.  ·  latency: Local feedback under 100 ms; negligible network or model impact.
- security: Physical controls should carry only opaque thread IDs and control events; never persist transcripts, account data, or secrets on the ring.
- depends on: Intent Thread/checkpoint protocol; Focus/attention policy; A product hardware design replacing the provisional DK enclosure

### `memory` — Build a consent-scoped commitment ledger rather than treating all captured speech as memory. Each entry records activation method, exact owner wording, source timestamp, inferred people/deadline separately from stated facts, confidence, sensitivity, retention/expiry, and permitted uses. The relay stores the encrypted canonical entry; the Mac/browser may resolve context only through short-lived, purpose-bound queries; the pendant retains only an opaque acknowledgement token. Every reminder or draft links back to the original wording and offers correct, defer, expire, or delete controls.
- **owner gets:** The owner can rely on help with promises without worrying that an overheard conversation becomes permanent surveillance or that an uncertain inference turns into a false obligation. They get useful follow-through while retaining control over what was remembered and why.
- effort: Medium: ledger schema, consent UX and pendant capture mode, scoped retrieval APIs, provenance display, expiry/deletion jobs, and tests for inference-versus-stated facts.  ·  risk: False captures or incorrect person/deadline resolution could create stress or inappropriate reminders. Default uncertain entries to suggestions, never commitments; require owner confirmation before escalation or outward action, and make deletion immediate across indexes and caches.
- cost: Low storage cost; modest asynchronous model cost for resolution and conflict checks. Retention limits keep relay storage bounded.  ·  latency: Sub-second acknowledgement locally; enrichment is asynchronous and should not interrupt the conversation.
- security: Meaningfully improves privacy by preventing ambient transcript retention and enforcing purpose limitation. Requires encrypted storage, strict access logs, redaction, and explicit user-visible consent state.
- depends on: A pendant explicit capture trigger and local transient audio buffer; A relay encrypted personal-state store with expiry/deletion semantics; Mac/browser scoped context queries across calendar, mail, contacts, and authenticated pages


## What it asked for

### `c2-9uig` (context) — current cross-surface job and event persistence primitives
- why: My proposals depend on knowing whether relay, Mac, and browser already share request IDs, idempotency keys, durable storage, or reconnect semantics. The capability list shows tools but not the underlying state guarantees.
- would change: If these primitives exist, I would narrow the proposal to policy/UI and avoid duplicating infrastructure; if not, I would prioritize the Intent Thread/checkpoint protocol as the foundational change and specify the smallest viable schema.

