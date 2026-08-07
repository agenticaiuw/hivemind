# Harness derivation — faculty-judgement — round 62

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I got interrupted—pick up exactly where I left off.” The pendant should give me a 20-second resume briefing, reopen the relevant Mac document and browser tabs, and offer the single next step without repeating work or sending anything."
- **useful because:** Real interruptions currently erase the thread between a spoken intention, a private browser page, and Mac work. This would make the wearable a continuity anchor: I can leave a meeting, lose connectivity, or switch devices and return to the exact unfinished decision with evidence and a safe next action.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the realtime tier only to capture the interruption marker and speak the short resume brief. Use a cheaper background model to compile the packet and reconcile job/session/browser evidence; use deterministic code for ordering, deduplication, and safety checks.
- **latency:** On the next pendant interaction, acknowledge in under 300 ms from a locally cached marker. Compile or refresh the packet in 2–5 s; if a surface is offline, say so and resume from the last verified checkpoint rather than blocking.
- **cost:** About $0.005–$0.03 per resume, dominated by background summarization of changed evidence; near-zero when the cached packet is still fresh. Audio generation is a smaller additional cost.
- **security:** The packet can expose sensitive page titles, mail, or documents, so store pointers and short redacted excerpts rather than full page content, apply per-source TTLs, and keep it device/owner scoped. Never replay secrets aloud by default. Reopening is reversible; any send, delete, purchase, or mutation still requires the existing confirmation gate. If evidence is stale or agents disagree, present uncertainty and ask one clarification instead of inventing continuity.
- **missing:** A durable intent-continuity record with explicit interruption and checkpoint events across pendant, relay, Mac jobs, and browser sessions.; A resume-packet compiler that links the spoken intent to tab IDs, Mac paths, job IDs, receipts, and the last confirmed step, with freshness and redaction.; A local/offline pendant marker and reconnect reconciliation so an interruption survives a dropped link.; A one-tap/spoken “resume / discard / snooze” interaction and a dashboard showing packet provenance.

### "“What promises have I made recently that I’m quietly failing to keep?” Give me a private, evidence-linked list of commitments inferred from my conversations, calendar, notes, and logged-in pages; rank the ones whose silence is most likely to hurt someone, and prepare a repair plan without contacting anyone."
- **useful because:** Today the owner can remember explicit reminders, but no system can notice the human commitments that were casually spoken or implied (“I’ll send that tonight,” “let’s meet next week”) and then compare them with what actually happened. This protects relationships and reputation without turning the assistant into an autonomous sender.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Use a cheaper background model for nightly extraction and reconciliation; use realtime only when the owner asks for the private spoken summary. Deterministic code handles dates, evidence links, deduplication, and ranking inputs.
- **latency:** Nightly scan completes within 2 minutes in the background; an on-demand spoken answer starts in under 1 second from the cached ledger and refreshes in under 10 seconds if sources are online.
- **cost:** Roughly $0.02–$0.10 per nightly scan depending on message/page volume; most cost is extracting candidate commitments. Incremental refreshes should be far cheaper through hashes and source cursors.
- **security:** This is unusually sensitive social inference. Keep raw messages and page contents on the Mac/browser session, store only a redacted claim, source pointer, confidence, and expiry in the relay, and let the owner exclude people/accounts. Never present an inference as fact: say “possible promise,” quote the minimal evidence privately, and allow dismiss/correct. No message, reminder, or calendar mutation occurs without explicit approval.
- **missing:** A commitment-specific evidence schema distinguishing explicit promises, tentative ideas, and ordinary plans.; Cross-surface extraction connectors for spoken pendant events, AppleScript-readable Mail/Messages/Calendar/Notes, and authenticated browser pages, with source cursors and deletion propagation.; A reconciliation job that marks commitments kept, deferred, expired, or unresolved without treating absence of evidence as failure.; A private review UI and voice flow for confirm, dismiss, snooze, redact, and repair-plan generation.


## Changes it proposed to its own stack

### `context` — Add a durable cross-surface continuity graph and compiler. On every spoken task, browser command, Mac delegated job, and confirmation, emit a typed checkpoint event {intentId, sessionId, surface, object refs, step, status, evidence timestamp, sensitivity, expiry}. On interruption/offline/reconnect, deterministically select the latest verified branch, redact content by surface policy, and compile a small resume packet with provenance and one safe next action. Persist only refs/hashes plus short encrypted excerpts; make resume/discard/snooze idempotent.
- **owner gets:** The owner can stop mid-task and later say one sentence instead of reconstructing which tab, file, or pending job mattered. It prevents duplicate submissions and makes the system honestly say when a handoff is stale or incomplete.
- effort: Medium-high: event schema and emitters in relay, Mac job runner, browser bridge, and pendant reconnect; compiler and retention tests; dashboard and voice interaction are moderate.  ·  risk: Incorrect branch selection could resume the wrong task or reveal private context. Mitigate with explicit confidence, source timestamps, visible provenance, conservative no-op reopen behavior, and discard/undo. If a surface is unreachable, never infer completion.
- cost: Small durable storage and hashing cost; background compilation roughly $0.005–$0.03 per refresh, with caching keeping normal resumes near zero.  ·  latency: Sub-300 ms local interruption acknowledgment; 2–5 s network refresh. Cached packets make common resumes immediate.
- security: Cross-surface linking increases metadata sensitivity. Encrypt excerpts, scope by owner/session, enforce TTL and source-specific disclosure (especially browser/private mail), and keep secrets out of spoken summaries.
- depends on: Existing /sessions and /jobs need a shared event identity rather than unrelated IDs; Browser command results must include tab/session provenance; Mac job receipts must expose last verified step and object refs; Pendant reconnect/offline marker and owner interruption preferences (currently missing)

### `hardware` — For the product revision, add a tiny coin/LRA haptic actuator with a dedicated low-side driver and expose a wake-capable second tactile input (or capacitive side strip) while retaining the existing button/LED. Use haptic patterns for “checkpoint saved,” “resume packet ready,” and “confirmation required,” with the firmware keeping the event marker and pattern state locally until reconnect.
- **owner gets:** The owner can mark an interruption or notice a ready-to-resume task discreetly in a meeting or while walking, without looking at a screen or hearing private content aloud. A second control avoids overloading one button with ambiguous short/long presses.
- effort: Medium hardware revision plus Zephyr driver, enclosure, and usability/power testing; prototype on a small board first before committing industrial design.  ·  risk: Added vibration can be distracting, drain the battery, or be triggered unexpectedly. Make patterns opt-in, cap duration, provide a hardware/voice mute, and default to a single short pulse. A second input can cause accidental marks; require deliberate press duration and show LED acknowledgment.
- cost: Approximately $1–$3 BOM increase in volume ($5–$15 in prototype parts/PCB), with roughly 5–25 mA only during a pulse and negligible idle draw; driver quiescent current should be under 1 µA.  ·  latency: Local haptic acknowledgment under 50 ms; no network dependency.
- security: Positive for privacy because it reduces spoken notifications, but patterns must not encode sensitive content where bystanders could infer it. Do not use distinct patterns for mail/calendar categories without owner opt-in.
- depends on: The continuity checkpoint event schema and offline marker from the proposed context change; Pendant firmware event persistence and reconnect reconciliation; A product enclosure/PCB revision; current nRF9160 DK prototype has only one button and one LED

### `memory` — Create a privacy-preserving commitment ledger and reconciliation pipeline that is separate from reminders. Ingest timestamped candidate commitments from pendant transcripts, Mac Mail/Messages/Calendar/Notes, and authenticated browser evidence; classify explicit promise vs tentative plan vs wish; attach minimal evidence pointers, people/entities, due-window, confidence, and sensitivity. Reconcile against later evidence (sent message, completed calendar event, note, or owner correction), propagate source deletions, and expose only unresolved/high-impact items to a private review queue.
- **owner gets:** It lets the owner repair neglected promises before they become relationship or work failures, while avoiding the false confidence and nagging caused by treating every thought as a task.
- effort: High: new event schema, source adapters, entity/time resolution, deletion propagation, review UX, and extensive false-positive evaluation with owner corrections.  ·  risk: Social inference can be wrong or invasive; a missed promise can be harmful, and a false accusation can be worse. Require evidence snippets and uncertainty labels, default to review-only, support per-person/source exclusions, and never send or schedule anything automatically.
- cost: Nightly background extraction approximately $0.02–$0.10 depending on source volume; local hashing/cursors reduce repeated processing. Storage is small if raw content stays on-device.  ·  latency: Background reconciliation in minutes; cached review list available immediately, with source refresh under 10 seconds on demand.
- security: High sensitivity. Keep raw content on the Mac or browser session, encrypt relay metadata, use short TTLs, honor deletion propagation, and do not speak names or evidence aloud until the owner requests the item.
- depends on: A shared event identity and provenance format across /sessions, /jobs, browser results, and Mac receipts; Mac-side read-only adapters for Mail, Messages, Calendar, and Notes; Authenticated browser extraction with source cursors; Owner-configurable disclosure and retention policy; A review queue with correction/dismissal feedback


## What it asked for

_Nothing._
## Its own summary

Discovered the owner profile and current backlog, then proposed a genuinely connective capability: interruption-safe cross-surface resume packets linking pendant intent, relay sessions, Mac jobs/receipts, and private browser tabs. Also proposed the missing continuity event graph/compiler and a hardware revision adding discreet haptics plus a second deliberate input for offline checkpoint/resume signals. Existing routes are mostly primitives; the connective layer is not present.

**Biggest unknown:** I still need the actual cross-surface persistence/event primitives, the owner’s interruption and disclosure preferences, and the 24 kHz audio acceptance criteria to turn this into an implementable contract. No new granted tools appeared in this round (granted catalog is empty), so I did not re-request previously denied/pending items.

