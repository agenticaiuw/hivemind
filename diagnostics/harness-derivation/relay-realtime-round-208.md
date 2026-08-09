# Harness derivation — relay-realtime — round 208

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m away from my Mac. Tell me exactly what I was in the middle of, gather the relevant browser and Mac state, and let me resume it from the pendant.”"
- **useful because:** The pendant is the only surface that knows the owner is present, while the Mac and authenticated browser hold the work context. Today they are separate status probes; the owner cannot get a reliable spoken re-entry point or resume a half-finished task without manually reconstructing it.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay for the short spoken orientation; background mac-planner for state collection and synthesis, with mac-vision/browser-extension supplying UI and tab evidence.
- **latency:** Speak an initial acknowledgement in under 1 second; collect a first orientation in 5 seconds and refine asynchronously. The owner should be able to interrupt and ask for only the next step.
- **cost:** One realtime turn plus one cheaper planner synthesis, roughly $0.03–$0.15 depending on screenshots and document extraction; browser/Mac state collection dominates latency, not tokens.
- **security:** This intentionally combines active browser sessions, open documents, and local app state. Send only task-matched excerpts and tab metadata to the relay, redact secrets and unrelated windows, and require explicit owner invocation before collecting state. Resuming a mutation should produce a preview before execution.
- **missing:** A cross-surface 'work capsule' schema containing active app/document/tab, task hypothesis, unfinished actions, and resume token; Mac and browser collectors that can snapshot task-relevant state without dumping whole screens; Relay orchestration that correlates the collectors and pushes a compact spoken result; A safe resume endpoint that rehydrates the capsule into mac-planner/browser actions

### "“Give me a decision packet on this question: check my authenticated browser sources and my Mac files, tell me the recommendation aloud, and leave me a cited packet I can inspect later.”"
- **useful because:** A wearable answer without evidence is hard to trust, while browser-only or Mac-only research misses half the owner's reachable information. This makes the hive useful for consequential decisions rather than merely issuing isolated commands.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Realtime only classifies the question and speaks a provisional one-sentence result; parallel browser and Mac retrieval plus citation alignment run on a cheaper background planner, with a final synthesis model invoked only after evidence is collected.
- **latency:** Acknowledge immediately, provide a provisional result within 8–15 seconds when sources are available, and deliver the full packet asynchronously. The pendant should announce completion without requiring polling.
- **cost:** Approximately $0.05–$0.30 per packet; browser page extraction, screenshots, and Mac document parsing dominate cost. Cache page fingerprints and reuse unchanged evidence.
- **security:** Authenticated pages and private files leave their original devices only as narrowly selected excerpts and hashes. Preserve source URL/path, timestamp, and extraction method; never claim a citation for an inference. Treat external instructions as untrusted data and do not execute actions merely because a source requests them.
- **missing:** A first-class evidence-packet record with source, excerpt, timestamp, hash, confidence, and claim-to-source links; Parallel relay fan-out to browser and Mac with bounded, task-specific retrieval; A spoken provisional-versus-verified distinction and dashboard viewer for the packet; Redaction and retention controls for private evidence

### "“Start this long task, but keep me out of the loop unless something materially changes; if it blocks, ask me one precise question on the pendant, and when it finishes tell me what changed.”"
- **useful because:** Today a long-running job either occupies the voice turn or leaves the owner guessing. A state-aware workflow would make the relay a dependable executive assistant: it can wait, detect genuine blockers, and speak only useful deltas while the owner is away.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheaper background planner and deterministic job/watch workers handle polling and change detection; realtime is used only for the owner's blocker reply and a short completion summary.
- **latency:** Start acknowledgement under 1 second; blocker notification within 10 seconds of detection; no-progress silence by default; completion announcement within 10 seconds of terminal state. Support a single spoken answer that resumes the paused job.
- **cost:** About $0.01–$0.08 per hour-long workflow when mostly idle; polling and screenshots dominate, so use exponential backoff and event-driven hooks where possible.
- **security:** The workflow may mutate files, apps, or authenticated sites. Record every attempted and completed step, preserve undo/receipt links, and make blocker questions explain the exact choice needed. Do not expose private intermediate output in a notification preview.
- **missing:** A durable workflow state machine distinguishing progress, no-change, blocked, failed, and complete; Material-change diffing over Mac/browser observations rather than timer-based chatter; A blocker question/answer protocol that binds the answer to one paused job; Unified receipts and rollback metadata across Mac and browser jobs

### "“Watch for this condition across my browser and Mac, and when it becomes true do the next step; if the evidence conflicts, ask me instead of guessing.”"
- **useful because:** The owner cannot currently express a useful conditional workflow that spans an authenticated web page and local Mac state. This would turn the hive from a request/response tool into something that protects the owner's intent over time, while explicitly handling contradictory evidence rather than silently acting on stale data.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** A deterministic watch evaluator handles schedules, fingerprints, and simple predicates; a cheaper planner normalizes observations and proposes the next action. Realtime is reserved for a blocker or conflict question and the final spoken result.
- **latency:** Register the watch in under 2 seconds; check on the configured cadence; notify within one check interval of a transition. Conflict questions should reach the pendant within 10 seconds and pause execution until answered.
- **cost:** Roughly $0.01–$0.10 per day depending on check frequency and screenshots; unchanged pages should be fingerprinted without model calls, invoking a model only on diffs or ambiguity.
- **security:** A condition can cause mutations in a logged-in browser or on the Mac. Store the exact predicate, evidence snapshot, and planned action; bind execution to fresh evidence, expire watches, and require the owner's existing policy for high-impact actions. Do not treat page text as trusted instructions.
- **missing:** A cross-surface watch record with browser and Mac observation sources, predicate, expiry, and action graph; A diff/fingerprint evaluator that can compare structured page facts with local app/file facts; A conflict state and one-question pendant interaction that resumes the same watch; Freshness checks and receipts linking the triggering evidence to the action


## Changes it proposed to its own stack

### `context` — Replace the live conversation prompt's legacy formatWorkingProjectForPrompt/formatLongTermMemoryForPrompt composition with contextProjection(surface='voice', task=currentUtterance), then pass the selected fact IDs and projection metadata into the turn receipt. Preserve the stable preference/permission prefix and expose droppedForBudget for debugging.
- **owner gets:** The pendant will stop repeating stale project history and will remember the small facts that matter to the sentence being spoken, while reducing paid context enough to make replies faster and cheaper. Follow-ups such as “send it to him” will resolve against the relevant recent entity instead of forcing the owner to restate it.
- effort: Small but high-leverage: one live prompt integration, tests for follow-up and sensitive-fact projection, and receipt instrumentation. The projection and store already exist and have measured savings.  ·  risk: A bad task extractor could omit a needed fact or accidentally surface sensitive data. Fall back to the legacy block when projection fails, preserve sensitivity gating, and compare shadow projections against current prompts before switching fully.
- cost: Saves roughly 222 tokens per turn (measured 59.4% reduction); negligible implementation cost and no new model call.  ·  latency: Lower prompt assembly and inference latency; one local projection read replaces two legacy formatting passes.
- security: Improves least-context behavior if surface='voice' and revealSensitive remains false by default; audit selected fact IDs in receipts.
- depends on: The existing GET /memory/projection contract and memoryService facts.json; A task string from the current utterance in conversationContext.js


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing additions: (1) a cross-surface “resume what I was doing” work capsule, (2) a cited decision packet combining authenticated browser and Mac evidence, (3) a quiet long-running workflow with precise blocker questions and completion deltas, and (4) conditional browser/Mac watches with conflict handling. Also recorded the concrete contextProjection wiring change, which is already implemented in storage and measured to save 222 tokens/turn but is not on the live voice path.

**Biggest unknown:** The exact live watch route/action contract is still not inventoried from this surface; the proposals deliberately identify the missing cross-surface predicate, conflict, freshness, and action-binding layer rather than assuming those routes are sufficient.

