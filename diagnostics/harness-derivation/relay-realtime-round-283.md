# Harness derivation — relay-realtime — round 283

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What’s going on with the thing I asked you to do?"
- **useful because:** Hands-free status checks reduce friction and prevent duplicate commands when the owner is away from the Mac.
- **path:** relay → mac-bridge
- **model tier:** Realtime, since the answer is short and time-sensitive.
- **latency:** Under a second when possible; no Mac round trip is needed.
- **cost:** Very low; a single job-status read dominates.
- **security:** Do not embellish; speak exactly what the job system reports to avoid false claims.
- **missing:** 

### "If I get interrupted, remember the task and pick up where we left off next time I talk to you."
- **useful because:** Real life is messy. This reduces re-explaining and prevents mistakes when the owner resumes after a break.
- **path:** relay → mac-bridge → memory
- **model tier:** Realtime for the quick recap; cheaper tier to store and summarize context.
- **latency:** A short recap in under a second; deeper context can be fetched lazily.
- **cost:** Low; the cost is mainly context projection and a small write/read to memory.
- **security:** Only store what’s necessary; avoid sensitive content, and let the owner ask to forget.
- **missing:** The live prompt path must actually use the existing memory projection instead of legacy context blocks

### "When I say “log this decision and keep me honest,” have the pendant capture the decision, have the Mac and browser gather the relevant context, turn it into a concrete next action, and later ask me whether it was resolved; if I answer, close the loop and remember the outcome."
- **useful because:** Today the system can capture commands or create reminders, but it cannot carry a spoken decision through context gathering, execution, follow-up, and outcome learning. This would turn the pendant into a reliable personal accountability loop rather than a one-shot assistant.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime for the short capture and follow-up conversation; background model for extracting the decision, researching context, and drafting the action.
- **latency:** Acknowledge the capture in under 2 seconds; context/action preparation within 30 seconds; follow-up at the owner’s chosen time.
- **cost:** About $0.01–$0.05 per decision lifecycle; background extraction and browser/Mac work dominate, not the spoken acknowledgement.
- **security:** The decision may contain sensitive personal or work information. Store scoped facts and source URLs, expose only the relevant context to each surface, and never silently send external messages or make purchases.
- **missing:** A first-class decision record with status, owner-chosen follow-up time, and outcome fields; A cross-surface context bundle joining pendant transcript, Mac state, and authenticated browser findings; A follow-up worker that can invoke the existing routine/watch machinery and deliver a spoken question; Outcome writes back into the existing scoped memory projection

### "Why did you tell me that, and what did you actually use? Give me a short spoken explanation and, if I ask, open the exact source page, Mac artifact, memory fact, or action receipt that supports the answer."
- **useful because:** A wearable assistant must be trustworthy when it acts across private browser sessions and a Mac. Today the owner hears conclusions but cannot reliably trace them to the source, the memory selected, or the observed result. Provenance would make mistakes diagnosable and sensitive claims contestable.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime answers from structured provenance already attached to the turn; background models are used only to summarize a long evidence chain.
- **latency:** One short spoken explanation in under 2 seconds when metadata is present; opening the supporting artifact within 10 seconds.
- **cost:** Usually under $0.01 because the evidence is structured; long source summarization is the dominant cost and should use a cheaper background tier.
- **security:** Do not read a private source aloud by default. Speak source type, title, and confidence first; require an explicit request to open or quote sensitive content. Redact tokens, passwords, and private page bodies from receipts.
- **missing:** A provenance graph linking each answer span to selected memory facts, browser observations, Mac reads, and action receipts; A relay query that resolves “that” to the current spoken turn and can return a compact evidence chain; Stable deep links or safe artifact viewers for Mac and browser evidence

### "Before changing anything, tell me what would change across my Mac, browser, and iPhone, show me the conflicts and the exact reversible steps, then let me say “do it” to apply that same plan and report what actually changed."
- **useful because:** The owner currently has to choose between a vague plan and immediate action. A cross-surface dry run would expose stale pages, conflicting edits, and side effects before execution, while preserving a one-sentence path to completion for routine reversible work.
- **path:** pendant → relay → mac-planner → mac-vision → browser → ios → dashboard
- **model tier:** Use the cheaper planner/vision tiers for inspection and diff generation; realtime only narrates the compact preview and receives the final apply command.
- **latency:** Preview in 10–30 seconds for a normal Mac/browser task; application and receipt within 30 seconds after “do it.”
- **cost:** Roughly $0.03–$0.15 per preview/apply cycle, dominated by screenshots, browser reads, and multi-step planning; no need to spend realtime tokens on the full plan.
- **security:** Inspection must not mutate. The preview must label uncertain or stale observations, avoid exposing secrets in screenshots, and bind the apply command to a hash of the preview so a changed page cannot silently receive an old action list.
- **missing:** A read-only plan/preview mode that returns typed preconditions, expected diffs, and a plan hash; A cross-surface diff format for Mac files/apps, authenticated browser pages, and iPhone-mirroring state; An apply endpoint that revalidates the hash and returns per-step before/after evidence; A pendant-friendly spoken confirmation of the preview without introducing a blanket permission gate


## Changes it proposed to its own stack

### `relay` — Implement a real completion-event path: a background job watcher that monitors job terminal states and enqueues a short pending alert for delivery to the pendant or phone, using the existing inbox model rather than a new queue.
- **owner gets:** They can start something and walk away; the system will tell them when it’s done or needs attention.
- effort: Medium to high; requires wiring a watcher loop and a delivery path, plus idempotency and retries.  ·  risk: Duplicate or missed alerts if state tracking is wrong; recover by storing last-emitted state and allowing re-ack/replay.
- cost: Low ongoing compute; storage is small text alerts.  ·  latency: Slightly higher background load; interactive latency unchanged.
- security: Alerts must be privacy-aware; avoid speaking sensitive content by default.

### `hardware` — Add a low-power vibration motor and a second deliberate button to the pendant, with firmware support for tactile urgency patterns, acknowledge/dismiss, and a long-press privacy mute. The relay’s existing alert inbox and completion events should target haptics when the owner cannot or should not hear audio; the second button must not compete with the current recording button.
- **owner gets:** The owner can receive an urgent result, reminder, or failure notice while walking, in a meeting, or in a noisy place without broadcasting speech or staring at an LED. A second button also gives the owner a safe way to acknowledge or mute an alert without interrupting recording.
- effort: New enclosure revision, motor driver and battery characterization, one GPIO/button input, firmware event/state-machine work, and relay alert-payload fields. Prototype: 2–4 weeks; productionized jewellery enclosure: 1–2 months.  ·  risk: Vibration can be missed or mistaken for ordinary phone notifications; add a short learnable pattern and a test mode. Extra power draw and mechanical noise need measurement. Recovery is to fall back to the existing LED/audio inbox if the motor is unavailable.
- cost: Roughly $2–$8 in components plus enclosure redesign; approximately 5–20 mA only during a short vibration burst, negligible idle draw.  ·  latency: Immediate local feedback once an alert arrives; no model latency. Button debounce and privacy-mute state must be handled locally.
- security: A physical mute/ack state reduces accidental disclosure. Do not encode sensitive content in patterns; haptics should convey urgency and count only.
- depends on: Extend the existing offline_alert_inbox record with urgency, acknowledgement, and delivery-preference fields; Extend the existing relay event/completion delivery path to advertise haptic capability; Keep audio and LED fallback behavior unchanged

### `context` — Replace the live-turn legacy working-project and long-term-memory concatenation with the already-shipped contextProjection surface/task query, while retaining the legacy blocks only as a fallback when projection fails. Record projection version, selected fact IDs, dropped-for-budget count, and task key in the turn receipt so every spoken answer can be audited and replayed with the same context.
- **owner gets:** The assistant would remember the right preference or active task without repeatedly sending irrelevant history, respond faster, and stop exposing unrelated facts to a turn. If an answer is wrong, the owner can see exactly which memories informed it instead of guessing.
- effort: Small server integration plus receipt schema and regression tests across voice, Mac, browser, and iOS tasks; the projection and memory store already exist.  ·  risk: A projection bug could omit a needed fact. The explicit legacy fallback and a metric comparing selected versus legacy context make rollback safe. Incorrect task classification could select the wrong scoped facts.
- cost: Expected to save roughly 222 tokens per turn (about 59% of the measured context) and reduce uncached context cost by about 82%; negligible implementation/runtime cost.  ·  latency: Slightly faster prompt construction and smaller model input; one local projection lookup per turn.
- security: Improves least-context exposure by honoring surface scoping and excluding browser-origin facts unless relevant; receipts must store IDs and metadata, not sensitive values.
- depends on: Use GET /memory/projection?surface=&task=&budgetTokens=&revealSensitive=&includeWeb=; Update conversationContext.js/buildConversationContext; Add projection metadata to existing voice-run/job receipts


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: a decision-to-outcome accountability loop spanning pendant, relay, Mac, and browser; provenance/explanation for every answer and action; and a cross-surface dry-run/apply workflow with stale-state detection. Also recorded two enabling changes: tactile pendant alerts with a second deliberate control, and wiring the existing scoped memory projection into live turns with audit metadata. The recorder flagged the haptic and memory changes as close to existing backlog entries, so they should be treated as implementation refinements rather than wholly new ideas.

**Biggest unknown:** Whether the existing /prepare and provenance/receipt routes already expose enough structured data to implement the dry-run and explanation experiences without new APIs; I was instructed not to discover further this round.

