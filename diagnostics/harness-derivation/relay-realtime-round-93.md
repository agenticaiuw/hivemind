# Harness derivation — relay-realtime — round 93

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “check on that for me and tell me what’s going on,” follow it, even if my Mac is asleep, and give me a clear status update."
- **useful because:** Owners will ask vague follow-ups while walking. They need continuity: what was requested, what’s queued, what finished, and what failed, without having to remember a job ID or reopen a laptop.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime model for the quick conversational follow-up; cheaper planner model on the Mac when status requires local interpretation; browser only when the task originated in a web session.
- **latency:** Under a second when reading relay job state; longer only if the Mac must be consulted or a browser session must be inspected.
- **cost:** Low for relay-side status reads (small payload). Higher if we must ask the Mac planner to explain a plan or read receipts; dominated by cross-device round trips.
- **security:** Status text may contain sensitive task names. Keep spoken output exactly as returned by the status tool and avoid adding details. Do not fetch live device state unless explicitly needed.
- **missing:** An implemented relay_route_intent to standardize intent labels and target selection.; Durable job runner / receipts that preserve enough context to explain what a queued job is.; Server-side browser actions or an equivalent headless capability for when the Mac is offline.

### "When I say “pick up where we left off,” give me a compact, current continuation of my last unfinished conversation or task—even if I stopped talking hours ago or moved away from my Mac—and let me continue by voice without repeating the setup."
- **useful because:** Today the relay can remember history or hand off a job, but it cannot assemble a trustworthy continuation state spanning the pendant conversation, queued Mac work, open authenticated browser context, and the owner’s explicit next step. This would make the wearable feel continuous rather than stateless between voice sessions.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime model only to recognize the short resume request and speak the result. A cheaper background model should periodically compact the selected session evidence into a continuation capsule; Mac-planner and browser-extension provide structured state, not prose.
- **latency:** Resume response in under 2 seconds from already-built capsule; if a live Mac/browser refresh is needed, acknowledge immediately and return an update within 10 seconds.
- **cost:** About $0.001–$0.01 per resume depending on whether a fresh compaction is needed; storage and structured snapshots dominate less than model tokens.
- **security:** Capsules must be encrypted and scoped to the owner, with per-source provenance and timestamps. Authenticated browser titles/content and local project data must not be copied into a general transcript or exposed to another session. The spoken response should summarize sensitive details only when the paired pendant is authenticated. Mutations remain separate from this read/continuation flow.
- **missing:** A relay-owned durable continuation-capsule store with TTL, source provenance, and redaction controls; A compact snapshot contract from Mac-planner and browser-extension for unfinished jobs, open relevant tabs, and pending actions; A resume endpoint that merges capsule state with current job/session status and clearly marks stale evidence; A user-visible way to pin, forget, or exclude a source from future capsules

### "Is that actually done? Check the Mac, any browser work, and the relay record, then tell me what is definitely complete, what failed, and what still needs me—without making me remember which agent did it."
- **useful because:** The current system exposes jobs, receipts, browser sessions, and Mac status separately. A wearable owner cannot practically reconcile them while away from the computer, and a queued receipt can be mistaken for completion. This is a genuinely cross-surface answer: one spoken question produces a provenance-backed settlement of distributed work.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles intent and a short spoken result. Deterministic reducers should join job/receipt/browser/Mac evidence; use a cheaper model only to phrase conflicting evidence or extract the next action.
- **latency:** Speak an immediate “checking” acknowledgement, then settle in 3–8 seconds; if a surface is offline, report that explicitly rather than waiting indefinitely.
- **cost:** Usually under $0.002 per check when structured evidence is available; occasional model phrasing is the dominant cost. No browser page content should be sent unless needed to resolve a contradiction.
- **security:** Every claim needs source, timestamp, and job/session identity. Do not infer success from a plan or queued state. Access to authenticated browser results remains scoped to the paired owner. Any suggested retry or mutation must be a separately addressed action, not an implicit consequence of asking for status.
- **missing:** A cross-surface settlement reducer with explicit states (queued, running, succeeded, failed, stale, contradicted); A common correlation ID propagated through /plan, Mac execution, browser commands, and receipts; Live read adapters for Mac and browser status with bounded freshness and offline reporting; A voice-friendly result schema plus dashboard timeline showing the evidence behind each claim


## Changes it proposed to its own stack

### `model-routing` — Add a cost-aware model-routing policy for the relay: keep the realtime model for turn-by-turn speech and intent recognition, but automatically downshift to a cheaper planner model for anything that requires multi-step reasoning or long context, and only escalate to mac_delegate when a computer workflow is involved.
- **owner gets:** Keeps voice responses snappy and reliable while reducing cost, and avoids burning expensive realtime tokens on planning tasks they cannot see.
- effort: Low to medium: policy configuration plus context handoff to the planner tier.  ·  risk: Misclassification could cause underpowered responses. Mitigate with a fallback rule: if confidence is low, ask a brief clarification or route to mac_delegate.
- cost: Moderate savings by reducing realtime usage; cost dominated by planner calls when invoked.  ·  latency: Improves perceived latency for voice while keeping complex work off the pendant.
- security: Low; routing decisions are metadata. Ensure utterances passed to planners are minimal and redacted when possible.
- depends on: A stable intent schema (relay_route_intent) and a reliable way to pass minimal context to downstream agents.

### `relay` — Add a durable cross-surface work ledger and correlation-ID propagation. Every spoken request receives a trace ID; /plan, Mac actions/delegation, browser commands, job records, receipts, and voice runs append typed events to that trace. A settlement reducer computes the current state from events and marks stale or contradictory evidence instead of treating queued work as success. Expose a small owner-facing status payload for the realtime voice layer and a detailed provenance timeline for the dashboard.
- **owner gets:** When the owner asks “did that happen?”, they get one honest answer with the next useful step, even when the Mac went offline, a browser command timed out, or two agents disagree. They no longer need to remember which surface performed the work.
- effort: Medium: event schema and middleware in relay/Mac/browser bridges, reducer tests for retries/timeouts/duplicates, and dashboard plus voice formatting.  ·  risk: Older jobs lack IDs and will appear as unlinked history until backfilled. Duplicate delivery can create duplicate events; idempotency keys and append-only sequence numbers recover safely. A reducer bug could misclassify completion, so retain raw evidence and make the detailed timeline inspectable.
- cost: Negligible storage and Worker CPU; roughly tens of bytes to a few KB per event. No additional model call for ordinary status checks.  ·  latency: A few milliseconds for event append/reduction; remote freshness checks remain bounded by the existing Mac/browser timeouts.
- security: Ledger contents can include sensitive app and browser metadata. Encrypt at rest, bind records to the paired owner/session, redact page bodies by default, and enforce retention/forget controls.
- depends on: A shared trace-ID field accepted by the existing /plan, job, receipt, browser bridge, and Mac action schemas; Durable relay storage for append-only events; A bounded status-read adapter for Mac and browser surfaces


## What it asked for

_Nothing._
