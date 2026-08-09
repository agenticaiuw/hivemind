# Harness derivation — faculty-judgement — round 260

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Undo the last thing you did, wherever it happened.”"
- **useful because:** Today undo exists as separate Mac/job/plan endpoints, but the owner cannot safely invoke one semantic undo across a browser action, Mac action, or queued job. This would turn the hive's receipts into a trustworthy escape hatch after a mistaken action.
- **path:** pendant → relay → mac → browser
- **model tier:** gpt-5.6-luna for selecting and explaining the target; deterministic receipt/reversibility checks for execution, with realtime only for the spoken request
- **latency:** Under 2 seconds to identify and speak the candidate; under 5 seconds to execute a reversible undo. Ask for confirmation if more than one candidate or if any step is not provably reversible.
- **cost:** About $0.01–$0.04 per invocation when model selection is needed; receipt lookup and policy checks dominate latency, not tokens.
- **security:** Never guess across multiple recent actions. Require a receipt-backed inverse, run autonomy_policy_evaluate and cross_surface_preflight, and fail closed when the inverse is absent. Do not undo destructive or externally committed actions; explain why. No new data leaves the Mac beyond existing receipt metadata.
- **missing:** A durable cross-surface join between relay job IDs, Mac action IDs, and browser command IDs; A typed inverse-operation registry that maps receipts to existing undo endpoints; A single owner-facing endpoint that selects the latest eligible action

### "“I lost the connection—continue from exactly where I stopped, and don't repeat what I already heard.”"
- **useful because:** A dropped LTE session currently risks repeating an entire response or silently losing it. Combining the durable context handoff, semantic audio cursor, and authenticated pendant delivery ACKs would make the pendant feel continuous rather than like a radio that forgets.
- **path:** pendant → relay → mac
- **model tier:** Deterministic cursor reconciliation first; gpt-5.6-luna only to regenerate a compact replacement when the original artifact is unavailable. Realtime is used only for the reconnect utterance.
- **latency:** On reconnect, return a resume decision in under 500 ms; begin playback within 2 seconds. Regeneration may take up to 8 seconds but must be explicitly labeled as a replacement.
- **cost:** Near-zero for cursor/ACK reconciliation; $0.01–$0.06 only when audio must be regenerated.
- **security:** Use opaque artifact IDs and authenticated device sessions; never infer completion from download alone. Deduplicate offline ACK replay, honor universal_stop_latch, and do not replay secret text merely because it was partially downloaded. Preserve provenance to the original item and mark replacement audio distinctly.
- **missing:** A relay-side durable delivery ledger joining artifact IDs to briefing items and context handles; A reconnect route that computes the first unplayed cursor from record_pendant_delivery_event events; A firmware/relay contract for expiry and deletion of audio artifacts after confirmed playback

### "“Learn how much interruption I can actually tolerate, and only interrupt me when it is worth breaking my attention.”"
- **useful because:** The current arbiter can rank events but has no outcome loop: it cannot distinguish an urgent interruption the owner acted on from one they repeatedly deferred. A bounded, explainable calibration loop would reduce nuisance speech without hiding deadlines.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Cheap deterministic policy update from explicit outcomes (acknowledge, defer, replay, dismiss) and observed attention state; use gpt-5.6-luna only for weekly plain-language summaries of what changed.
- **latency:** No added latency to event arbitration; update policy in under 100 ms after an outcome. Weekly summary can be generated in the background.
- **cost:** Usually under $0.005 per update; weekly summary roughly $0.01–$0.03.
- **security:** Never silently learn a rule that suppresses safety-critical or deadline-bound events. Keep learned weights bounded, time-decayed, and visible by policy field; separate content sensitivity from urgency. Store only event class/outcome, not raw mail or page text, and allow reset of learned state.
- **missing:** An outcome event schema and durable store linking an attention decision to later owner action; A constrained learner layered on the existing owner-editable briefing policy, with hard floors for deadlines; A dashboard/voice command to inspect, reset, or freeze learned preferences

### "“If two parts of my life disagree, tell me the smallest question that resolves it, then remember my answer.”"
- **useful because:** The system can now detect conflicts and explain provenance, but a conflict still becomes a technical report rather than a decision the owner can settle in one sentence. This turns timezone, permission, duplicate-briefing, and goal disagreements into a focused spoken question with a durable, retractable answer.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Deterministic conflict grouping and question templates first; gpt-5.6-luna only to phrase the one-question summary and map the owner's answer. Realtime handles the short spoken exchange.
- **latency:** Under 1 second to identify the highest-impact unresolved conflict; one short question under 10 seconds of owner attention. Persist only after the owner answers.
- **cost:** $0.005–$0.03 per conflict session; source reads and storage dominate, with model use limited to phrasing.
- **security:** Show the competing sources and timestamps without exposing sensitive snippets by default. Never silently overwrite a source; write an explicit owner decision with expiry/scope and allow revocation. A spoken answer must not authorize a destructive action.
- **missing:** A durable conflict-question record with status, scope, source IDs, and owner answer; A route that appends the explicit decision to the existing typed memory/fact and context-graph stores with provenance; A spoken/dashboard UI for answering, snoozing, or revoking one conflict

### "“What did I know, decide, and do about this on that day—and what changed afterward?”"
- **useful because:** The owner has receipts, captures, jobs, browser evidence, and provenance, but no temporal reconstruction. This would let them inspect the evolution of a decision or situation rather than receiving today's projection with the past flattened away.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** A background indexing/projection job using a cheaper model; gpt-5.6-luna only for the owner's interactive synthesis, with realtime limited to the short spoken answer.
- **latency:** A prepared topic timeline should open in under 2 seconds; cold reconstruction may take 10–20 seconds and should be announced as such.
- **cost:** $0.02–$0.10 for a cold reconstruction, dominated by summarizing multiple dated sources; cached timeline views are near-zero.
- **security:** Default to metadata and owner-authored summaries, not raw private quotes. Every claim must show its source and date, respect revocations, and distinguish contemporaneous evidence from later interpretation. Never let historical context silently influence a current external action.
- **missing:** An append-only temporal index joining captures, facts, context-graph changes, action receipts, browser provenance, and pendant delivery events; A point-in-time projection API with source revocation awareness; A dashboard/talk-back view for disputed or missing intervals

### "“Show me which of my routines actually improve my life, and which ones are just making noise.”"
- **useful because:** The system executes scheduled briefs and routines, but completion counts do not reveal usefulness. The owner should get an outcome review: which routines led to an opened brief, completed action, avoided duplicate work, or repeated dismissal, with uncertainty called out rather than pretending correlation is causation.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic event aggregation and confidence scoring in the background; a cheaper model writes the weekly digest, while gpt-5.6-luna is reserved for questions about a specific routine.
- **latency:** No impact on routine execution; a weekly review should be ready within 30 seconds of the scheduled analysis.
- **cost:** $0.01–$0.05 per weekly review; storage and aggregation dominate.
- **security:** Use coarse outcome signals and owner confirmation, not hidden behavioral profiling. Keep routine evaluation separate from medical or psychological claims. Never disable a routine solely because of inferred non-use; propose changes and let the owner decide.
- **missing:** A routine-outcome event model linking a firing to delivery, attention, and downstream owner action; A retention-limited analytics store with explicit sampling and reset controls; A review UI that supports keep, tune, pause, and compare-before-change

### "“Before I commit to this, show me the likely second-order consequences and the safest smaller version.”"
- **useful because:** Existing plans and previews describe immediate mutations, but the owner cannot ask for a consequence map: follow-up obligations, affected routines, stale assumptions, privacy exposure, or what will become harder to undo later. This is the missing judgement layer between preview and consent.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic dependency and reversibility analysis first; gpt-5.6-luna synthesizes only the compact consequence explanation. Realtime handles the spoken summary.
- **latency:** A first-pass consequence map in under 3 seconds; deeper browser or mail impact analysis can take up to 15 seconds before asking for confirmation.
- **cost:** $0.02–$0.12 per complex decision, depending on how many surfaces need inspection.
- **security:** Read-only analysis must not trigger the proposed action. Mark speculative consequences separately from evidence-backed ones, show affected destinations and data classes, and require explicit confirmation before any mutation or external communication.
- **missing:** A typed dependency graph for jobs, plans, routines, facts, browser sessions, and external side effects; A consequence-analysis endpoint that consumes a prepared plan without executing it; A compact owner-facing representation of reversible, irreversible, and merely speculative effects


## Changes it proposed to its own stack

### `relay` — Add a user-visible stalled-work recovery loop for relay jobs: persist a lease_until and attempt number, requeue expired processing jobs, and expose a single human-readable state (running, paused, needs-owner, recovered) with the original relay↔Mac↔browser correlation IDs. Before replay, revalidate the pending plan and run the deterministic autonomy policy; never blindly repeat a mutation.
- **owner gets:** A dead Mac or dropped connection would no longer leave an invisible job stuck for 24 hours. The owner would hear “that task stopped safely and is ready to resume” instead of wondering whether it happened twice or not at all.
- effort: Medium: schema migration, claim/requeue sweep modeled on the existing routine lease, correlation mapping, and a small owner-facing status adapter.  ·  risk: A bad lease could duplicate a side effect. Mitigate with idempotency keys, receipt checks, stale-plan revalidation, bounded attempts, and ASK rather than replay when the action is non-idempotent. Recovery is to mark the job needs-owner and preserve the original receipt trail.
- cost: Negligible storage and worker CPU; no model call for ordinary lease decisions. One cheap model call only when the owner asks for an explanation.  ·  latency: Adds no latency to healthy jobs; stale detection within one scheduler interval, target under 30 seconds.
- security: Improves safety by failing closed on stale plans and making replay provenance explicit; does not grant new permissions.
- depends on: relay_jobs lease_until + requeue sweep; durable relay-job↔Mac-job↔browser-command correlation; revalidate_pending_plan; autonomy_policy_evaluate


## What it asked for

_Nothing._
