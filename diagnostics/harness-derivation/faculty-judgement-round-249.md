# Harness derivation — faculty-judgement — round 249

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “that’s wrong” or “forget what you learned from that site/person,” find every derived copy of the claim, show me what will change, then revoke or correct it everywhere with one confirmation."
- **useful because:** Today a browser fact can survive evidence revocation, a capture can survive deletion in the context graph, and there is no global forget. This gives the owner a trustworthy correction/forget action instead of forcing them to know which store leaked the old belief. It is a concrete privacy and life-quality feature, not another provenance viewer.
- **path:** pendant → relay → mac → browser
- **model tier:** background for fan-out discovery and impact analysis; realtime only to resolve the owner’s short correction and read back the affected stores
- **latency:** Under 2 seconds for an impact summary from indexed records; mutation may take 5-15 seconds across Mac and relay, with a durable receipt and retry
- **cost:** ~$0.01-0.04 per invocation; most work is local indexed lookup and deterministic fan-out, with the expensive model used only for ambiguous natural-language target resolution
- **security:** Default to draft-only impact preview. Require explicit physical confirmation for revocation/correction that affects multiple stores or external relay memory. Never speak the old secret value. A derived fact must gain capsule/source links before it can be promised as deletable; unlinked copies are reported as unresolved rather than falsely claiming deletion.
- **missing:** Add source/capsule linkage to memory facts and context-graph copies, then implement a cascade over facts, graph entities/relations, browser provenance, fleet-memory retractions, and cached briefing text; A durable relay-memory writer and migration for relay_memory_events; currently the fleet-memory routes have no production writer and schema.sql may lack the table; An owner-facing target resolver for “that site/person” that returns candidates with source references, not an ungrounded guess

### "What can I realistically finish in the next 20 minutes? Give me one or two tasks that fit the time I actually have, the apps already open, and what is safe to do now; if I say yes, stage them without losing my place."
- **useful because:** A calendar day plan ranks obligations but does not turn a small free interval into a feasible next action. This would use the Mac’s real foreground/browser state and the relay’s durable jobs to choose an appropriately sized action, avoiding the common failure of starting a 45-minute task in a 12-minute gap.
- **path:** pendant → relay → mac → browser
- **model tier:** background model for task decomposition and duration estimation; deterministic policy for permission, reversibility, and confirmation; realtime only for the spoken question and final choice
- **latency:** Initial answer in 3 seconds, using cached state where possible; a selected reversible task stages within 5 seconds and reports a receipt
- **cost:** ~$0.01-0.03 per request; model cost is task sizing and fit, while calendar/browser/app inspection and policy checks are local/cheap
- **security:** Never infer a free interval from an unauthorized empty calendar. Mark calendar/reminder reads unreadable when EventKit access is absent. Reading browser tabs and foreground app names is allowed only in the owner’s local context; external sends, purchases, deletion, and deadline-risk actions remain ASK. Present the estimated duration, blocked dependencies, and exact side effects before staging.
- **missing:** A small-window planner that combines day-plan events/reminders, foreground app, browser tabs, and current Mac job load into feasible task candidates; Expose the existing idle/presence signal and foreground app through a typed read route; do not pretend macOS Focus/DND exists; A durable ‘resume at this point’ cursor for staged work, distinct from a generic job receipt, so a later pendant request can continue rather than restart

### "I’m leaving now. Prepare a compact ‘out-the-door’ packet for where I’m going and what matters before I arrive, then make it available on the pendant; when I return, give me the shortest useful catch-up instead of replaying everything."
- **useful because:** The owner should not have to remember to ask separately for directions, the next appointment, a boarding pass or a pending browser task. A physical moment marker can trigger a cross-surface context switch: Mac/browser gather the relevant local and authenticated state, relay signs and compresses it, and the pendant carries only the actionable packet while disconnected. This is a new life behavior, not another queue.
- **path:** pendant → relay → mac → browser
- **model tier:** background model for selecting and compressing context; realtime only for the owner’s brief request and a concise readback; deterministic policy for sensitivity, expiry, and whether a source may be included
- **latency:** Stage in under 8 seconds while connected; packet must remain useful if LTE drops, with a 15-minute expiry for volatile details and a durable return marker
- **cost:** ~$0.02-0.06 per departure/return pair; browser and Mac reads dominate implementation time, not tokens
- **security:** The packet must contain opaque references or minimal actionable text, never credentials, page secrets, or raw mail bodies. Authenticated browser content requires an explicit source policy and redaction before it leaves the Mac. Destination and travel details can be sensitive; default to a private, owner-initiated request and expire aggressively. Return mode must report sources unavailable rather than inventing a catch-up.
- **missing:** A mode-switch packet schema and signed expiry that can ride the existing offline alert inbox without creating a second firmware queue; A relay route that accepts a physical marker and requests a bounded Mac/browser gather, then returns one compact artifact with source receipts; A real location/destination input or explicit owner destination; the current pendant has no GNSS/NITZ and zoneless device timestamps must not be treated as location; A return-mode reducer that consumes delivery ACKs and prior spoken items, so it can say what changed since departure rather than replaying the packet

### "Which things you believe about my life are becoming unreliable? Show me only claims whose source changed, expired, or disagreed with another source, explain the consequence, and let me reaffirm, correct, or retire each one."
- **useful because:** A memory system that merely stores facts quietly turns yesterday’s fare, policy, preference, or relationship detail into false certainty. The owner needs a periodic epistemic maintenance view: not a generic activity log, but a short list of beliefs whose reliability has changed and the practical decisions they could distort. Nothing today detects source decay across browser evidence, Mac records, relay memory, and spoken interactions.
- **path:** pendant → relay → mac → browser
- **model tier:** Background model for clustering claims and estimating practical consequence; deterministic source-change, expiry, conflict, and sensitivity rules for inclusion; realtime only for the owner’s reaffirm/correct/retire response
- **latency:** A scheduled scan under 30 seconds on the relay/Mac; each pendant interaction under 3 seconds per claim, with no interruption unless an owner-configured consequence threshold is met
- **cost:** ~$0.02-0.08 per scan depending on the number of changed sources; most comparison is hash/timestamp/index work, with model spend reserved for ambiguous conflicts and consequence summaries
- **security:** Default to metadata and short redacted excerpts, never silently read private source bodies aloud. A claim must carry source IDs, sensitivity, confidence, observed-at, and expires-at. Reaffirmation must not overwrite history: it appends a new owner decision and preserves the prior claim for audit. External actions based on an unreaffirmed stale claim require confirmation.
- **missing:** A durable cross-surface claim index linking memory facts and context-graph entities to evidence capsules, browser provenance, mail/calendar observations, and relay memory events; A source-change and expiry scheduler that emits a typed stale-claim event instead of relying on pull-only triage; A lifecycle distinct from deletion: stale, contested, reaffirmed, superseded, and retired, with owner-visible consequence links; A compact pendant presentation that can walk one claim at a time and accept reaffirm/correct/retire without speaking the sensitive value

### "What am I repeatedly avoiding, and what is the smallest honest next step? Use unfinished work across my Mac, browser, mail, and pendant—not just my calendar—and distinguish a deliberate deferment from something I silently abandoned."
- **useful because:** The owner’s real obligations are scattered across half-finished browser jobs, drafts, reminders, interrupted Mac work, and spoken intentions. Today those surfaces expose queues independently; none recognizes a repeated avoidance loop or asks whether the owner deliberately chose it. This would turn shame-inducing backlog into one concrete, reversible next step.
- **path:** pendant → relay → mac → browser
- **model tier:** Background model for grouping related unfinished threads and inferring effort; deterministic rules for age, repeated deferral, explicit refusal, and confidence; realtime only for the owner’s answer to ‘deliberate defer or abandoned?’
- **latency:** Daily scan under 20 seconds; spoken result under 90 seconds and capped to three patterns; staging the chosen next step under 5 seconds
- **cost:** ~$0.02-0.06 per scan; local receipts, drafts, watches, and browser spool provide most evidence, with model cost dominated by grouping rather than generation
- **security:** Never label a health, character, or mental state. Say ‘repeatedly deferred work’ and cite evidence, not ‘you are procrastinating.’ Private mail and browser material stays local unless explicitly included. Suggestions are draft/reversible only; sending, deleting, or contacting another person always requires confirmation.
- **missing:** A cross-surface unfinished-thread index with stable joins between relay jobs, Mac jobs/actions, browser commands, drafts, reminders, captures, and pendant bookmarks; A deliberate-defer signal and a durable owner response so the system does not repeatedly nag after ‘not now’; A classifier for abandonment versus active work, grounded in receipts and state transitions rather than elapsed time alone; A scheduler and attention budget that surfaces at most one or two patterns and respects the owner’s policy rather than inventing urgency

### "Tell me when I’m spending far longer than the value justifies, summarize what I learned, and leave me a clean stopping point I can resume later."
- **useful because:** The system can already see browser page changes, Mac jobs, foreground context, and audio interruptions, but it cannot recognize a research or admin rabbit hole. The owner gets an intervention that preserves progress instead of losing an hour or receiving another generic focus timer.
- **path:** pendant → relay → mac → browser
- **model tier:** Background model for estimating diminishing returns from page churn, repeated failed actions, and goal progress; deterministic thresholds and owner policy decide whether to interrupt; realtime model only produces the short spoken intervention
- **latency:** Continuous local scoring under 100 ms per observation; at most one interruption per owner-defined window; summary and resume point under 10 seconds after acceptance
- **cost:** ~$0.01-0.04 per intervention; local telemetry and page-watch signals do the detection, with model spend only for the compact synthesis
- **security:** Do not treat duration alone as failure or infer emotional state. Require a stated goal or an explicitly owner-started research/task session before monitoring progress. Never expose private page contents in the spoken warning; use a generic ‘this task has produced little new progress’ unless the owner asks for detail. The intervention must be snoozable and auditable.
- **missing:** A goal-scoped progress model that records expected output, evidence gained, failed actions, and diminishing-return signals across Mac and browser; A resumable stopping-point artifact that stores the goal, exact source references, open tabs/jobs, and next safe step without copying private page bodies; A local attention-budget adapter that can ask the existing arbiter for a single interruption and suppress repeats; A reliable join between browser commands, page-watch reports, Mac action receipts, and the owner’s pendant interaction


## What it asked for

_Nothing._
