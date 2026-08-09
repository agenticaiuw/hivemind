# Harness derivation — faculty-judgement — round 176

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When my pendant is tethered, treat it as my desk presence: if the USB link drops, stop speaking, pause non-urgent queued work, and offer to resume the exact unfinished task when it reconnects."
- **useful because:** A dropped cable currently looks like an ordinary transient failure. This would prevent private audio or half-finished actions from continuing unattended and give the owner a reliable leave-desk boundary with no extra gesture.
- **path:** pendant → mac → relay → dashboard
- **model tier:** background for link-state classification and resume summaries; deterministic relay policy for stop/pause/resume; realtime only for the spoken reconnect prompt
- **latency:** USB disconnect detection under 1 second; mute/pause under 2 seconds; reconnect status under 3 seconds
- **cost:** Negligible model cost for most events; occasional short background summary, under $0.01 per reconnect
- **security:** A cable drop is evidence of transport loss, not proof the owner left. Default to silencing and pausing only reversible, non-urgent work; never cancel or resume external mutations automatically. Persist only opaque job IDs and a context handle, not audio or page contents.
- **missing:** authenticated USB serial heartbeat and disconnect event exposed to the Mac agent; a resumable lease/state for relay jobs (currently orphaned processing jobs do not requeue); a policy rule binding link loss to pendant mute, relay cancellation, and Mac job pause; a reconnect UI/voice status that can list paused work without exposing sensitive text

### "After a meeting, ask me for a 20-second voice debrief, match it to the meeting and the tabs I had open, and turn only confirmed commitments into dated reminders or a reviewable draft."
- **useful because:** The owner loses commitments at the boundary between conversation and action. This would turn a spoken recollection into a small, attributable follow-through list without pretending that an inferred promise is a fact.
- **path:** pendant → mac → browser → relay
- **model tier:** realtime for the short debrief and clarification question; background for matching tabs, calendar context, and drafting reminders
- **latency:** Prompt within 2 minutes after the event ends when the pendant is available; produce a draft within 30 seconds; never block the owner's other work
- **cost:** One short realtime turn plus one small background extraction, roughly $0.01–$0.05 per meeting depending on transcript and page evidence
- **security:** Meeting content and third-party names are sensitive. Keep raw audio on the existing failure-only path, redact before any cloud model call, retain only confirmed action text and source references, and require explicit confirmation before sending or creating an externally visible artifact. Calendar emptiness must be treated as unreadable when EventKit is unauthorized.
- **missing:** a reliable event-ended trigger from calendar state or a user-marked meeting boundary; a short-lived, source-linked debrief record joining pendant audio, calendar event, and browser provenance; a confirmation UI that distinguishes inferred candidate commitments from owner-confirmed ones; a real writer for shared fleet memory if the commitment must be available to relay and pendant later

### "Before carrying out anything I prepared earlier, re-check the current Mac and browser state; if it changed, show me the exact difference and rebuild the plan instead of blindly executing it."
- **useful because:** A stale tab, changed price, moved file, or changed calendar state can turn a previously safe plan into the wrong action. This gives the owner a practical 'don't act on yesterday's screen' guarantee while keeping reversible work fast.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** deterministic revalidation and autonomy policy for the normal path; realtime only when the changed fields require a concise owner decision; background model for rebuilding an ambiguous plan
- **latency:** Read-only recheck under 3 seconds; changed-state explanation under 8 seconds; never commit a stale plan automatically
- **cost:** No model cost when unchanged; roughly $0.01–$0.05 only when a plan must be reconstructed or explained
- **security:** Recheck with least privilege and return field-level diffs, not full sensitive page text. Fail closed if a source is offline, expired, or permission state is ambiguous. External or destructive actions still require the existing physical approval path and explicit confirmation.
- **missing:** a plan format that records source snapshots, age, and intended side effects across relay, Mac, and browser IDs; typed adapters that compare current state without executing the pending action; automatic invalidation and rebuild of stale browser/Mac plans; a single owner-facing receipt joining revalidation, policy verdict, approval, and final effect

### "While you are speaking a recommendation or reporting an action, let me interrupt with 'why that?' and get the evidence, policy rule, and a safe undo or correction for exactly the item you just said."
- **useful because:** The owner should not have to remember a job ID or open a dashboard to challenge a decision. Binding a spoken question to the currently playing item makes the system accountable at the moment trust matters, rather than after the fact.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** deterministic item binding, provenance lookup, policy explanation, and undo discovery; realtime model only to compress the evidence chain into one short spoken answer
- **latency:** Pause playback immediately; identify the item under 500 ms; speak a grounded explanation within 5 seconds; never perform the undo without confirmation unless it is a previously authorized reversible stop
- **cost:** No model cost for lookup-only explanations; under $0.01 for a short natural-language rendering
- **security:** Bind the query to an opaque audio cursor and authenticated session, not the most recent global job. Do not speak sensitive evidence aloud by default; offer a dashboard detail view. Undo must be scoped to the exact receipt and fail closed if state changed.
- **missing:** a durable semantic audio cursor that survives item transitions and reconnects; a join from spoken item IDs to evidence capsules, policy matches, action receipts, and available undo operations; a relay route that resolves 'why' against the current item rather than a free-text guess; a spoken-vs-dashboard sensitivity policy for explanations

### "Once a week, tell me which parts of your help actually improved my week, which created friction, and one routine you recommend stopping or changing—using observed completion, interruption, and correction patterns rather than asking me to fill out a survey."
- **useful because:** An assistant that never learns whether its interventions helped becomes a source of invisible friction. The owner should receive an evidence-backed recommendation to simplify or retune the system, not merely more automation.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** background model over a bounded weekly aggregate; deterministic counters and privacy filters before any model call; realtime only when the owner asks a follow-up
- **latency:** Generate during a quiet overnight window; dashboard and next spoken briefing should be ready within 60 seconds of the scheduled run
- **cost:** One small weekly background analysis, roughly $0.02–$0.10; no realtime cost unless discussed
- **security:** Analyze aggregates and event IDs, not raw audio, page bodies, mail contents, or third-party names. Keep the report local by default, attach provenance to every claim, allow per-routine exclusion and deletion, and never change a routine without explicit confirmation.
- **missing:** a cross-surface outcome model connecting interventions to owner corrections, completion, undo, interruption, and non-delivery; a durable writer for fleet memory or an equivalent weekly aggregate store; a user-visible causal disclaimer distinguishing correlation from improvement; a scheduled report route with source-linked findings and a reversible recommendation workflow

### "Let me say 'run a safety drill' and have the whole hive simulate a dropped link, interrupted audio, stale browser plan, and pending approval without touching the outside world, then tell me exactly what would recover and what would be lost."
- **useful because:** A safety mechanism that is never exercised is only a promise. The owner should know before an actual outage whether the pendant, Mac, browser, and relay preserve cancellation, context, audio position, and approval boundaries.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** deterministic fault-injection and receipt comparison; background model only to summarize the drill and rank gaps
- **latency:** A standard drill in under 2 minutes; emergency stop and rollback paths must be tested first and remain read-only externally
- **cost:** No model cost for the drill; under $0.02 for an optional summary; bounded local logs only
- **security:** Use synthetic artifacts, sandbox browser pages, fake job IDs, and a non-production relay namespace. Prove that no send, purchase, deletion, or external mutation occurred. Require explicit confirmation before any test that touches a real local file or live session.
- **missing:** a first-class simulation namespace accepted by every surface; fault-injection hooks for USB/link loss, audio interruption, stale plans, and relay failure; a machine-checkable invariant report covering cancellation, idempotency, provenance, and recovery; a dashboard history of drill results and regressions


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate owner-facing capabilities: USB-tether presence safety that pauses and silences on disconnect, stale-plan revalidation that refuses to execute changed Mac/browser state, and spoken “why that?” accountability bound to the exact item being played. I also attempted delivery-aware briefing reconciliation, but the recorder correctly rejected it as already covered by the granted delivery-ACK work. I still need four concrete pieces before these can be honest end-to-end: an authenticated USB serial heartbeat/disconnect event, relay job leases and requeue, durable joins between audio cursors/plans and provenance or receipts, and field-level read-only state adapters for Mac/browser revalidation. The owner-facing defaults should remain conservative and policy-configurable rather than fabricated.

**Biggest unknown:** Whether the live USB-tethered pendant can expose a trustworthy disconnect/heartbeat signal to the Mac harness today; the prior USB feasibility context request is still unresolved, so I will not claim this capability is runnable yet.

