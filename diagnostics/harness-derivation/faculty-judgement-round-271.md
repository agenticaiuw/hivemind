# Harness derivation — faculty-judgement — round 271

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I was away. Give me one trustworthy, short answer about what changed, what I missed, and the one thing I should do next.”"
- **useful because:** This is the single most useful daily behavior: it turns scattered mail, calendar/reminder, browser-watch, relay-job, and unheard pendant items into one deduplicated answer, while explicitly saying when a source was unreadable instead of inventing an all-clear. It works across the browser, Mac, relay, and pendant rather than being another Mac-only triage screen.
- **path:** relay → mac → browser → pendant
- **model tier:** Background model for collection and ranking; realtime model only for the owner's follow-up question or a one-sentence spoken rendering.
- **latency:** Prepare in under 10 seconds when sources are online; speak in under 3 seconds once the owner asks. If a source is offline, return a partial result with provenance rather than waiting indefinitely.
- **cost:** Roughly one background model call per digest (about $0.01–$0.05 depending on source volume); realtime cost only for follow-up. Dominant cost is summarizing changed source material, not arbitration.
- **security:** Never speak raw mail/browser text unless the delivery policy permits it; route all outgoing text through the existing redaction boundary. Calendar/reminder emptiness must be marked unreadable unless the corroborating permission-aware readers agree. External actions remain drafts or require physical approval. The owner must be able to inspect evidence and revoke a source.
- **missing:** A production collector that supplies actual pendant inbox items and delivery ACK state to catchup (today those inputs are effectively empty).; A durable cross-surface correlation between relay jobs and Mac/browser jobs; today localJobId is telemetry only.; A scheduled invocation and a single persisted digest cursor so the same item is not announced twice.; A user-configurable policy object for what may be spoken, rather than relying on placeholder interruption thresholds.

### "“Do not lose this request if the Mac sleeps or the link drops; finish what is safe, then tell me exactly whether it completed, is waiting for me, or needs retry.”"
- **useful because:** Today an in-flight relay job can remain processing forever after a Mac crash, and relay/Mac/browser IDs cannot be joined reliably. The owner experiences this as silence and has to repeat work, risking duplicates. A durable request contract would make the hive dependable instead of merely clever.
- **path:** pendant → relay → mac → browser
- **model tier:** No expensive model for recovery: deterministic lease/retry and receipt reconciliation. Use the background model only to convert a recovered receipt into a short explanation; realtime is reserved for a live clarification.
- **latency:** Lease/requeue detection within 60 seconds of a dead worker; normal completion unchanged. Spoken status under 2 seconds from cached receipts.
- **cost:** Negligible model cost for normal operation; roughly $0.001–$0.01 only when a model-written explanation is requested. Storage and periodic lease sweeps dominate, not inference.
- **security:** Retries must be idempotent and fail closed for external or destructive effects. Revalidate pending plans before replay, run autonomy_policy_evaluate on every retry, and require the physical approval latch again if the old approval expired. Expose a receipt chain through explain_action_provenance; never claim success from a worker heartbeat alone.
- **missing:** lease_until, attempt count, and safe requeue/sweep for relay_jobs (the routine lease implementation is the template).; A durable relay-job-id ↔ local Mac/browser job-id mapping, not merely telemetry meta.localJobId.; A typed idempotency envelope propagated from relay through Mac and browser, with effect receipts attached.; A recovery coordinator that distinguishes retryable reads from non-replayable mutations and invokes revalidate_pending_plan before replay.

### "“If the pendant audio is late, clipped, or missing, tell me whether the problem was capture, radio, decode, or playback—and recover the conversation without making me repeat myself.”"
- **useful because:** A silent or partial reply is currently indistinguishable from model failure. This would give the owner a truthful diagnosis tied to measured UART/audio evidence and the exact artifact/playback state, then resume or re-enqueue only the missing segment. It uses the physical pendant and bridge as observability surfaces, not just as a speaker.
- **path:** pendant → relay → mac
- **model tier:** Deterministic metrics classification first; a cheap background model may summarize an incident. Realtime is only used to answer a live “what happened?” follow-up, never to decide whether packets were lost.
- **latency:** Local fault indication within 1 second; server diagnosis within 5 seconds after reconnect; recovery should preserve the current item and avoid duplicate playback.
- **cost:** Near-zero for metrics and receipts; <$0.01 for an optional incident summary. Storage is bounded by compact event records, not audio content.
- **security:** Send opaque artifact/session IDs, counters, checksums, and timing—not microphone PCM or transcript. Deduplicate device events by eventId and reject unauthenticated sessions. Do not replay an action or speak a sensitive answer until the delivery state is known and the normal policy gate allows it.
- **missing:** A live classifier that joins pendant_diagnostics_and_bug_draft metrics to pipeline/audio and record_pendant_delivery_event records.; A recovery operation that can request only the missing audio range or regenerate an unplayed artifact without restarting the whole conversation.; A durable cross-surface artifact ID shared by relay pipeline, bridge, and pendant; current job/action namespaces do not join.; A user-facing incident timeline and automatic, reviewable bug draft trigger for critical repeated failures.

### "“Before I agree to this, show me the personal consequences: what it conflicts with, what I would have to cancel or move, who is affected, and the safest way to say yes or no—without changing anything.”"
- **useful because:** The owner can currently ask for a plan or execute an action, but cannot rehearse a decision against their real commitments and authenticated browser state. This would prevent accidental overcommitment: it would expose hidden time, relationship, privacy, and follow-up costs before the owner says yes, while remaining a read-only analysis.
- **path:** pendant → relay → mac → browser
- **model tier:** Background model for the counterfactual narrative after deterministic collection; realtime model only for a short spoken answer or a clarification. The deterministic layer computes schedule overlap, existing obligations, pending work, and affected artifacts; the model explains tradeoffs rather than inventing facts.
- **latency:** A first conservative impact map in 10 seconds; a deeper analysis in 30 seconds. No mutation is allowed during analysis. The owner should hear a two-sentence verdict and be able to ask for detail.
- **cost:** About $0.02–$0.10 per deep scenario, dominated by synthesizing several source summaries; routine overlap and conflict calculations are local and cheap.
- **security:** The scenario text and affected-person names may be sensitive. Keep raw page/mail content on the Mac where possible, send only minimized evidence capsules, and pass every spoken conclusion through the existing delivery redaction gate. Never imply a prediction is a fact: label assumptions, confidence, stale sources, and unknowns. Any suggested cancellation, message, or purchase remains a draft and requires the existing autonomy/physical-consent policy.
- **missing:** A read-only scenario API that accepts a proposed commitment and returns a typed impact graph: conflicts, obligations created, affected parties, deadlines, assumptions, and alternatives.; A provenance-linked obligation model joining calendar/reminders/mail/browser findings, relay jobs, and owner notes; current stores cannot reliably join derived claims to their sources.; A deterministic counterfactual engine for time-budget, deadline, and dependency effects, including an explicit unknown state when calendar or reminders are unreadable rather than treating them as empty.; A review surface on the pendant and Mac that lets the owner compare alternatives and promote one to a draft without executing it.

### "“Move this conversation from my ear to the screen—or from the screen to my ear—without losing what we were discussing, what I already saw, or what I meant to do.”"
- **useful because:** Today the pendant, relay, Mac, and authenticated browser each have fragments of context, but the owner must repeat the topic and reorient the system when changing modality. A true modality handoff would let the owner begin hands-free, continue visually when available, and return to audio while preserving the exact conversational position and unresolved questions.
- **path:** pendant → relay → mac → browser
- **model tier:** Use the deterministic context-handoff record and source receipts to transfer state; use a background model only to compress oversized context into a loss-aware handoff. Realtime is appropriate only while the owner is actively speaking.
- **latency:** Create a handoff in under 2 seconds and render the receiving surface in under 5 seconds. If context cannot be transferred safely, say exactly what was omitted rather than producing a cold-start answer.
- **cost:** Usually <$0.01 per handoff when the existing context record fits; up to $0.05 when compression is needed. Browser/Mac execution and state capture dominate latency.
- **security:** The receiving surface must inherit source sensitivity and revocation state; a browser page must not receive secret audio context, and the pendant must not receive raw page credentials. Bind the handoff to the active session, expire it, and show the owner which sources crossed surfaces. Do not claim that a visual page was opened unless the browser receipt confirms it.
- **missing:** A user-visible handoff command and durable handoff state containing conversation cursor, unresolved questions, selected evidence IDs, and target modality.; A real cross-surface correlation ID shared by relay, Mac, browser, and pendant; current contextHandle is useful for resume but is not an owner-facing modality contract.; Target-surface adapters that can render a compact transcript/evidence view in the browser or Mac and report an acknowledgement back to the pendant.; A policy check that filters context by destination before transfer and a receipt proving exactly what crossed the boundary.

### "“Find the recurring friction in my week—missed handoffs, repeated retries, context switches, and unfinished promises—and suggest one small experiment that would make next week easier, without changing anything automatically.”"
- **useful because:** The system currently records jobs, browser changes, audio failures, reminders, and notes as separate traces, but the owner cannot ask what pattern is making life harder. This turns the hive into a reflective instrument: it identifies repeated failure modes across physical and digital surfaces, distinguishes evidence from interpretation, and proposes a reversible experiment instead of issuing generic advice.
- **path:** pendant → relay → mac → browser
- **model tier:** Background model over compact, provenance-linked event summaries; deterministic aggregation detects repetition, latency, abandonment, and cross-surface handoff failures. Realtime is only for the owner’s follow-up. No model should infer health, personality, or motives from the traces.
- **latency:** Weekly analysis in under 60 seconds; an on-demand 7-day scan in under 15 seconds. The pendant receives only a short opt-in summary, never an unsolicited psychological profile.
- **cost:** About $0.03–$0.15 per scan, with event aggregation local and summarization the main cost. Retaining compact metrics is cheaper and safer than retaining raw conversations.
- **security:** Behavioral traces are highly sensitive. Default to aggregate counts and short retention, exclude raw audio and page/mail bodies, and require explicit opt-in for cross-surface analysis. Every finding must cite events, state confidence, and distinguish correlation from causation. Experiments must be preview-only; reminders, routine edits, or messages require owner confirmation.
- **missing:** A cross-surface event vocabulary and durable join key for job retries, browser waits, audio interruptions, reminders, and owner acknowledgements.; A retention-limited analytic projection that stores aggregates rather than indefinitely exposing the context graph’s raw telemetry.; A detector for recurring patterns and a reviewable experiment object with baseline, hypothesis, duration, success metric, and undo path.; An owner-controlled schedule and delivery policy for reflective reports; the current briefing policy is a placeholder and has no scheduler.


## What it asked for

_Nothing._
## Its own summary

I discovered the newly granted decision, provenance, attention, delivery, and diagnostics surfaces and produced three owner-facing capabilities: (1) a trustworthy “what changed while I was away?” digest, (2) lossless request continuation across Mac/link failures with truthful completion state, and (3) measured pendant-audio diagnosis and segment recovery. The strongest remaining product gap is not another model feature: it is joining the existing receipts, artifact IDs, and source evidence into durable cross-surface contracts. I also attempted a global “forget everywhere” capability; the recorder correctly rejected it as already represented in the backlog, so I did not restate it.

**Biggest unknown:** I still need a real owner decision on spoken-content/privacy policy and emergency/quiet-hour rules; the system must keep these as explicit policy values rather than guess. Technically, the largest unknowns are whether fleet-memory migration is applied on the live relay, whether the Mac↔relay job mapping can be added without breaking existing receipts, and whether the shipping LTE-M path is currently registered. Until those are answered, I would not promise cross-surface completion, fleet retraction, or live pendant recovery as already working.

