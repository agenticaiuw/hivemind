# Harness derivation — relay-realtime — round 159

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Summarize what’s on my screen right now and what I should do next."
- **useful because:** A quick situational brief lets the owner recover context fast, especially when returning to the Mac after being away.
- **path:** relay → mac-vision → mac-bridge
- **model tier:** Mac-side model for vision; relay only for conversation.
- **latency:** A few seconds; if it takes longer, provide a quick placeholder and stream updates.
- **cost:** Moderate, dominated by screen capture/vision and summarization.
- **security:** Screen content may include secrets. Redact known sensitive fields and avoid exfiltrating more than needed.
- **missing:** An implemented relay-to-mac intent routing mechanism (relay_route_intent is unresolved); A live mac-vision loop (currently disabled); A typed, privacy-aware screen redaction policy

### "While I’m offline, record a quick thought and send it to my inbox as a typed note when you reconnect."
- **useful because:** Turns the pendant into a reliable capture tool that survives dead zones, then delivers structured notes to the owner’s systems.
- **path:** pendant → relay → mac-bridge
- **model tier:** Cheap background for transcription/classification after upload; realtime only for capture UX.
- **latency:** Capture is instant; delivery depends on connectivity. Provide LED feedback using existing patterns.
- **cost:** Low; dominated by transcription and storage. Use the existing outbox/inbox manifest rather than new queues.
- **security:** Voice content is sensitive. Use encryption in transit/storage and clear retention rules.
- **missing:** Typed payload support in the existing outbox/inbox manifest; A small classification step to tag notes (task/idea/contact, etc.); A route to deliver typed notes into the owner’s preferred destination (Reminders/Notes)

### ""What is the one thing I need to know before I leave, and show me the evidence?" — Have the pendant ask the always-on relay to take a time-bounded snapshot across my Mac state and authenticated browser tabs, reconcile contradictions, and speak one prioritized answer with an explicit as-of time and source trail."
- **useful because:** Today the owner can get isolated Mac actions, browser reads, or a generic job result, but not a trustworthy decision-ready snapshot spanning both surfaces. This would turn the pendant into a genuinely useful last-mile perception layer when the owner is away from the desk.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Use the low-latency relay only to capture the question and acknowledge it; run parallel Mac/browser collection and reconciliation on a cheaper background planner, escalating only unresolved contradictions to the realtime model.
- **latency:** 3–8 seconds for a first spoken answer; up to 20 seconds for authenticated-tab reads, with an interim 'collecting evidence' response.
- **cost:** About $0.01–$0.05 per invocation; the dominant costs are parallel page extraction and the final synthesis context, not the short relay turn.
- **security:** Authenticated page text and local Mac metadata leave their surfaces for synthesis. Minimize collection to the requested question, retain citations and timestamps rather than raw pages, and never mutate anything in this read-only mode.
- **missing:** A cross-surface evidence envelope with source IDs, timestamps, and contradiction flags; A planner operation that can fan out perception jobs and merge typed results before synthesis; A relay response format that can stream a provisional answer then a corrected answer

### ""Remember this as a commitment, and tell me if I am about to break it." — Let me dictate a commitment on the pendant, then have the relay compare future Calendar, Mail, Reminders, and browser activity against it and surface only a concrete conflict with the original wording and evidence."
- **useful because:** A normal reminder fires at a time; it does not understand a promise or notice that a later action violates it. This gives the owner a durable, conversational commitment ledger that spans the wearable capture and the systems where commitments actually appear.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-judgement → faculty-action
- **model tier:** Use realtime for the initial dictation and confirmation-free transcription; use a cheaper background model for semantic commitment extraction and periodic event matching, with realtime reserved for a surfaced conflict.
- **latency:** Capture and acknowledgement under 1 second; conflict detection within 1 minute of a relevant Calendar/Mail/browser change.
- **cost:** Roughly $0.005–$0.03 per commitment plus low-cost incremental matching; browser polling and model context are the main ongoing costs.
- **security:** Commitments are sensitive personal data. Store encrypted structured claims with the owner's chosen expiry, avoid retaining full source messages, and make alerts specific enough to be useful without reading private content aloud in public.
- **missing:** A durable commitment record distinct from ordinary Reminders; Change-triggered or scheduled watchers over Calendar/Mail and authenticated browser sessions; A semantic conflict matcher with provenance and expiry handling; A delivery policy that routes only high-confidence conflicts into the existing pendant inbox

### ""I am at the door — make the handoff safe." — Have the pendant capture a short spoken handoff, have the relay package it with the exact current Mac/browser state needed by the recipient, and create a revocable, expiring handoff brief that the owner can later retrieve or cancel by voice."
- **useful because:** The owner can dictate notes or operate their own computer, but cannot presently turn an ephemeral voice thought into a bounded, auditable handoff containing the right live context. This is useful for delegating work while walking away without exposing an unrestricted account session.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Realtime handles capture, redaction choices, and immediate receipt; a background planner gathers only the named app/tab state and renders the brief. Use realtime again only for retrieval or cancellation dialogue.
- **latency:** Receipt in under 2 seconds; assembled brief in under 15 seconds. Cancellation must take effect within 2 seconds of a connected pendant request.
- **cost:** Approximately $0.02–$0.10 per handoff, dominated by authenticated browser extraction and brief rendering; cancellation is negligible.
- **security:** This could leak private browser content or create unauthorized delegation. Require explicit recipient/scope/expiry in the spoken request, redact credentials and tokens, encrypt the brief, log every access, and make revocation invalidate it immediately.
- **missing:** A scoped, expiring handoff-token and recipient model; Redaction and least-context collection across Mac and authenticated tabs; A durable revocation endpoint checked at every retrieval; A spoken retrieval/cancel verb integrated with the existing inbox and event delivery


## Changes it proposed to its own stack

### `relay` — Implement a real completion-notification channel on the relay: when a job transitions to complete/failed/needs_attention, emit a durable event record and deliver it to the pendant/phone. Back it with a Durable Object or queue, with exponential backoff and a TTL.
- **owner gets:** They can start a task and trust they’ll hear the outcome later, without polling or keeping the session open.
- effort: Medium to high: new durable component, job-state watcher, delivery adapter, and tests.  ·  risk: Duplicate or missing notifications. Mitigate with idempotent event IDs, at-least-once delivery, and explicit ack from the device.
- cost: Low ongoing; storage for pending events and occasional checks.  ·  latency: Adds negligible overhead; delivery is near-real-time when connected.
- security: Events may contain sensitive summaries; encrypt in transit, keep payload minimal, and enforce job-scoped auth.
- depends on: Job state change hooks or a polling watcher (relay_job_status exists, but a durable runner does not); A device-facing delivery endpoint that actually exists (relay_event_push schema is unresolved)

### `relay` — Add a cross-surface Evidence Capsule protocol: every perception/action job returns typed claims (source surface, exact locator, observed_at, freshness deadline, confidence, redaction class, and immutable content hash) rather than an unstructured string. The relay can merge capsules from Mac and authenticated browser reads, detect contradictory claims, and invalidate stale capsules before speaking or acting. This is the missing connective layer behind the proposed leave-the-house snapshot, commitment conflict detection, and revocable handoffs.
- **owner gets:** The owner gets answers that say exactly what was observed, where, and when, instead of confident-sounding stale summaries. When Mac and browser disagree, the pendant can say so rather than silently choosing one.
- effort: Medium: define the schema, adapt planner/browser result adapters, add freshness and contradiction logic, and test redaction/hash behavior across existing read and action routes.  ·  risk: Incorrect freshness policies could hide useful information or create false contradictions; recover by retaining raw job receipts internally, exposing source-level drill-down, and failing open to an explicit uncertainty statement rather than inventing a resolution.
- cost: Small per-job storage and serialization overhead; synthesis token cost may fall because the relay receives compact claims instead of repeated raw context.  ·  latency: Adds tens to hundreds of milliseconds for local merge and hashing; parallel collection remains the dominant latency.
- security: Improves least-context handling and auditability, but locator metadata can itself reveal sensitive app names. Encrypt capsules, apply field-level redaction before persistence, and expire raw values independently of provenance.
- depends on: A planner/browser adapter that emits typed result envelopes; A durable expiry and revocation check for capsules; A relay synthesizer that is instructed to cite capsule IDs and surface contradictions


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: an evidence-backed leave-the-house snapshot spanning Mac and authenticated browser state; commitment conflict detection from spoken commitments; and expiring, revocable handoff briefs. Also recorded the connective relay change that makes these trustworthy: typed cross-surface Evidence Capsules with provenance, freshness, redaction, hashes, and contradiction handling. What remains needed is the fan-out/merge planner, durable commitment and handoff records, watcher triggers, scoped revocation, and pendant delivery wiring; these are not assumed to exist.

**Biggest unknown:** Whether the existing planner and browser inspection results can be adapted to emit typed provenance envelopes without exposing raw authenticated page content; that determines the implementation shape of all three capabilities.

