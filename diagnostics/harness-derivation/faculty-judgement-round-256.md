# Harness derivation — faculty-judgement — round 256

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“While you’re reading my brief, let me say ‘remind me about that tomorrow’ (or ‘add that to the draft’) and have it act on the exact item I’m hearing, then continue where you stopped.”"
- **useful because:** This turns the pendant from a one-way newsreader into an assistant that can capture an owner’s decision at the moment the relevant context is present. It avoids the current failure mode where a later ‘that’ loses the source item, creates the wrong reminder, or makes the owner replay the brief.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Realtime only for the short utterance binding and ambiguity check; deterministic item-action and autonomy policy for the write; background model is unnecessary.
- **latency:** Pause within 250 ms of the button/barge-in event; confirm the bound item and prepare the reversible write within 1 s; resume audio from the saved cursor within 500 ms after completion.
- **cost:** Usually one realtime turn or less; roughly $0.001–$0.01 depending on transcript/context length. Dominant cost is resolving ‘that’ against the current item, not the Mac write.
- **security:** The item must be identified by an opaque cursor, not by replaying its potentially sensitive text into the device. Creating a reminder/note is an external write: autonomy_policy_evaluate should require confirmation when policy says so. Never speak secret item contents in the confirmation.
- **missing:** Firmware/relay wiring for spoken_status_interrupt to emit the current item_id and cursor_token on barge-in; A production caller that maps the resolved operation to audio_brief_item_action and resumes playback transactionally; A durable cross-surface receipt linking the item, request_id, and Mac reminder/note identifier

### "“I’m walking / driving / at my desk—give me the version of my brief that fits this moment, not the same list every time.”"
- **useful because:** The owner should not have to choose between silence and a 92-word generic digest. A walking brief can be a few decisions and deadlines, a desk brief can include links and drafts, and a meeting/quiet state can queue everything except a true deadline. The adaptation changes content and interaction shape, not merely interruption timing.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use deterministic briefingTriage and day-plan ranking for most selection; use the cheaper background model to compress/rewrite the selected items. Realtime is only for an explicit mode change or follow-up.
- **latency:** Mode selection under 300 ms from known signals; first spoken sentence within 2 s; background compression may complete before the next scheduled brief and must never block urgent delivery.
- **cost:** About $0.001–$0.02 per brief if a small background model rewrites selected items; the dominant cost is speech generation/audio, not judgement.
- **security:** Mode must be an owner-visible, revocable policy value, not inferred as fact from a single idle signal. Do not infer driving/location from browser or idle telemetry. Secret/sensitive content remains non-spoken unless the owner explicitly permits it; every spoken item carries source and policy refs for explanation.
- **missing:** A mode policy object with owner-set fields for length, interaction, and speakable sensitivity (with conservative defaults); A mode resolver that combines explicit mode, idle/presence, focusSession, browser online state, and calendar time without claiming unavailable macOS Focus state; A briefing renderer that emits per-item evidence and an audio artifact rather than one opaque paragraph

### "“Before you tell me my day is clear, prove that the sources were actually readable; if calendar, reminders, mail, or the browser was unavailable, tell me what you could not verify and give me the smallest repair step.”"
- **useful because:** A false all-clear is more dangerous than a delayed brief: the current notification/day-plan paths can turn unauthorised EventKit reads into ‘nothing waiting’. This capability makes uncertainty audible and actionable, while still allowing a useful partial brief. It is the single most valuable trust feature because it prevents the assistant from confidently erasing obligations from the owner’s attention.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic checks and provenance-backed reconciliation first; a cheap background model may phrase the bounded explanation. Realtime is reserved for the owner’s follow-up (‘what was unavailable?’).
- **latency:** Run checks before a brief and return a verified/partial/unverified verdict within 2 s; never wait indefinitely on a permission probe. A repair suggestion can be queued without interrupting unless the owner’s policy marks it urgent.
- **cost:** Near-zero model cost for checks; at most $0.001–$0.01 for concise explanation. The dominant cost is the existing AppleScript/EventKit and browser read latency.
- **security:** Do not treat Automation-TCC success as proof of EventKit access. Preserve source-specific evidence (read attempt, timestamp, empty-result corroboration, error/timeout) and speak only the failure class, not private mail/calendar contents. Repairs that open settings or mutate permissions require explicit owner confirmation.
- **missing:** A unified source-health result that records readable, unreadable, stale, and not-attempted per source with provenance; Fixes to GET /notifications and GET /day-plan so empty EventKit results cannot be formatted as clear without the briefingTriage/meetingPrep corroboration rule; A small repair workflow that offers open-settings or retry as a draft/confirmation, then reruns the check and attaches the new result to the briefing receipt

### "“Quarantine everything you know about this person/project for now—don’t use it in answers, briefs, or actions, but keep an auditable record so I can release the quarantine later.”"
- **useful because:** The owner needs a reversible boundary between forgetting and unrestricted use. Today a fact can survive in facts.json, the context graph, browser-derived memory, evidence, an inherited prompt projection, or a queued job, and there is no single way to stop all of those copies influencing a decision. Quarantine would let the owner handle a sensitive dispute, client matter, or family situation immediately without destructive deletion or pretending revocation propagated.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use deterministic policy enforcement for matching, blocking, and expiry. Use a background model only to help map the owner’s natural-language subject to candidate entities/facts, with the owner reviewing ambiguous matches; realtime is only for the spoken command and confirmation.
- **latency:** A confirmed quarantine should block new prompt projections and external-action planning within 1 s across relay and Mac. Existing queued work must be marked blocked before execution; listing affected records can finish in the background.
- **cost:** Low ongoing model cost; one small model call for ambiguous entity matching, then local indexed lookups. Storage grows by compact quarantine rules and tombstone references, not copied content.
- **security:** Fail closed: an uncertain subject match blocks rather than leaks. The pendant confirmation must not repeat the sensitive subject aloud. Quarantine metadata should contain opaque IDs and hashed selectors where possible. It must cover prompt projection, brief narration, browser extraction, memory retrieval, queued jobs, and action planning, while preserving only the minimum audit evidence needed to explain a block. Release, expiry, and exceptions require deliberate owner confirmation.
- **missing:** A shared quarantine policy and matcher consumed by relay memory projection, Mac memory/context-graph retrieval, browser provenance, briefing/audio rendering, and job/action planners; Stable provenance links from derived facts and graph entities to their source capsules, browser records, jobs, and fleet-memory events; current facts and graph copies cannot be reached by evidence revocation; A durable cross-surface propagation protocol with version/epoch so an offline Mac, browser, or queued relay job cannot continue using a stale policy; A dashboard view showing blocked surfaces, affected pending work, expiry, and an explicit release operation


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: item-bound barge-in actions during briefs; attention-shaped briefs for walking/desk/meeting contexts; and a source-verification contract that refuses false all-clear results and offers a bounded repair path. The delivery-ACK idea was rejected as an existing duplicate, so I did not rephrase it. The strongest proposal is the truthful all-clear gate: it directly prevents the known unauthorised-EventKit-empty-results failure. I still need owner policy values rather than invented assumptions: named brief modes, what may be spoken in each, and whether repair prompts may interrupt. Implementation still needs a unified source-health record, fixes to /notifications and /day-plan empty-result handling, and mode-aware rendering; no additional orchestrator tool request is needed this round.

**Biggest unknown:** The owner has not yet specified the desired morning-brief reliability or disclosure/interrupt policy. Until they do, the system should use conservative defaults, label them as defaults, and never infer driving, location, macOS Focus state, or calendar readability from weak signals.

