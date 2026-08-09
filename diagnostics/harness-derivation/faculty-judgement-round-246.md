# Harness derivation — faculty-judgement — round 246

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If my pendant didn't actually play an important alert, make sure I still get it exactly once on the best available surface—without repeating something I already heard."
- **useful because:** Today a job can be completed server-side while the owner never downloads or hears its audio. This closes the loop from decision to human receipt: an unheard urgent item can move to the Mac/browser, an interrupted item can resume or be compacted, and a successfully played item is suppressed everywhere else.
- **path:** relay → pendant → mac → browser
- **model tier:** Deterministic delivery/attention state machine first; use the cheap background model only to produce a shorter fallback summary when an item was interrupted. Reserve realtime for a live owner request.
- **latency:** ACK ingestion under 1s; reroute decision under 2s after a terminal delivery event; fallback summary under 10s. Never block the original alert on model summarization.
- **cost:** Usually <$0.01 per item; most cases are state transitions and existing audio/text artifacts. A fallback compression costs one background-model call, roughly $0.005–$0.03 depending on length.
- **security:** Carry only opaque artifact/item IDs and delivery evidence between surfaces; do not copy private audio into browser notifications by default. Require the existing autonomy policy for any external side effect. Expire reroute tokens and dedupe by item/request ID; provenance must show why a reroute occurred.
- **missing:** A durable join between the attention event, audio artifact, and delivery ACK (the new ACK tool supplies events, but the persistence/association needs implementation); A Mac/browser presentation action that is explicitly marked as an attention fallback rather than a new notification; A policy field for maximum retries and allowed fallback surfaces

### "Before you replay an old briefing item or reminder, check whether its underlying source is still true; if it changed, tell me what changed instead of reading stale advice."
- **useful because:** Queued audio can outlive the mail, page, calendar state, or job that produced it. This prevents the pendant from confidently replaying obsolete information and turns a stale item into a small, actionable delta.
- **path:** relay → mac → browser → pendant
- **model tier:** Cheap deterministic source rechecks and hash comparison; background model only summarizes the changed fields. Realtime is used only if the owner asks a follow-up.
- **latency:** Recheck under 3s for local/browser sources; if a source is offline, fail closed and say it is unverified rather than silently replaying. Delta summary under 8s.
- **cost:** <$0.01 for unchanged items; $0.005–$0.03 for a background delta summary. Browser reads and mail scans dominate latency, not model cost.
- **security:** Recheck only the minimum fields named in the original evidence; never expose raw private snippets to the pendant unless the delivery policy permits it. Preserve the original and fresh evidence references, and show a stale/unavailable reason. No mutation is allowed during recheck.
- **missing:** A typed source recheck adapter for each evidence kind (mail, page watch, reminder/calendar, job result) that returns changed fields plus provenance; A durable freshness fingerprint on briefing items and a policy for maximum age by source type; A render path that clearly distinguishes verified, changed, and unverified playback

### "Show me a weekly attention postmortem: which interruptions you made, which I actually heard or acted on, what you deferred, and where your judgement was wrong—then let me correct the rule without silently learning my preferences."
- **useful because:** An interruption policy is currently a placeholder and its failures are invisible. A compact postmortem makes the system accountable: the owner can see missed urgent items and needless interruptions, correct a named rule, and distinguish delivery failure from bad judgement.
- **path:** relay → pendant → mac → browser → dashboard
- **model tier:** Deterministic aggregation over attention decisions, delivery ACKs, item actions, and provenance. Use a background model only to phrase a short narrative after the facts are computed; never infer a new policy automatically.
- **latency:** Generate on demand in under 5s for a seven-day window; dashboard can refresh asynchronously. Spoken response is one sentence plus an option to open detail.
- **cost:** <$0.01 per report; storage/query work dominates. Optional narrative compression is about $0.005–$0.02.
- **security:** Keep sensitive summaries local/dashboard-only by default; the pendant gets counts and rule IDs, not subjects or private content. Make every correction an explicit policy write with versioning, preview, and rollback. Do not treat 'not heard' as owner rejection when the device was offline.
- **missing:** A durable attention-decision ledger joining event, policy version, surface decision, and outcome; An outcome taxonomy separating delivered/heard/acted-on, skipped, expired, offline, and unknown; A dashboard/API view for rule-level aggregates and explicit policy edits

### "Before I commit to a plan, show me the likely consequences of doing it, postponing it, or doing nothing—across my calendar, inbox, browser work, reminders, and pending jobs—without changing anything."
- **useful because:** The owner can currently get plans and previews, but not a grounded counterfactual: which commitments collide, which deadlines become risky, what work is duplicated, and what remains reversible under each choice. This is the judgement layer that turns a list of actions into an informed decision.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Use deterministic state snapshots, dependency rules, and deadline arithmetic for the candidate branches. Use the background model only to explain the computed differences in plain language; realtime is unnecessary unless the owner asks conversational follow-ups.
- **latency:** Initial branch comparison in 5–10 seconds; dashboard can stream evidence as each surface responds. No branch may mutate state. Spoken output should be a short verdict with an option to hear details.
- **cost:** Approximately $0.01–$0.08 per comparison, dominated by one background explanation call and any browser/mail reads; deterministic branches should be effectively free.
- **security:** Read-only by default. Each branch must carry source timestamps, confidence, and an explicit unknowns list; never invent calendar access when EventKit is unreadable. Do not expose private mail/page contents on the pendant unless the disclosure policy permits it. Any transition from simulation to execution requires a fresh autonomy-policy evaluation and physical/owner confirmation where required.
- **missing:** A typed counterfactual graph that represents dependencies, deadlines, reversibility, and cross-surface side effects without executing actions; Snapshot isolation or immutable evidence references so all branches compare the same as-of state; A result schema for branch deltas, confidence, unknowns, and stale-source warnings; A handoff from simulation to a revalidated prepared plan, rather than directly executing the winning branch

### "Let me ask, ‘what did you know and why did you decide that yesterday at 3pm?’ and get a faithful replay of the evidence, policy version, surface state, and actions as they existed then—not today's rewritten memory."
- **useful because:** Current receipts explain completed actions, but they do not reconstruct the complete historical decision context. A temporal audit lets the owner distinguish bad judgement from bad data, understand a missed task, and challenge a decision without trusting mutable current state.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic event-sourced reconstruction and provenance joins; use a background model only to narrate the already reconstructed timeline. Never let the model fill missing history.
- **latency:** Under 8 seconds for a day-scale query; longer windows stream progressively. The spoken result is one sentence and a dashboard deep link because full evidence is not suitable for audio.
- **cost:** <$0.02 per query when indexes exist; storage/indexing is the main cost, with optional narration around $0.005–$0.02.
- **security:** Historical views may contain secrets and private third-party content. Dashboard authentication and sensitivity-aware redaction are mandatory; spoken output must default to identifiers and rule names only. Preserve deletion/revocation tombstones and mark gaps instead of resurrecting deleted content.
- **missing:** Append-only, timestamped decision records spanning relay, Mac, browser, and pendant; Historical snapshots of policy, source freshness, permission state, and surface reachability; Stable cross-surface IDs linking relay jobs, Mac actions, browser commands, audio items, and delivery outcomes; A retention and redaction policy for audit records, including how revocation appears in historical replay

### "Undo the last thing you did for me—even if it crossed the Mac and browser—and show me exactly what can be reversed, what cannot, and what related state must be repaired before you do it."
- **useful because:** Undo exists only in isolated action/job paths and cannot reliably find or reverse a cross-surface operation. The owner needs one honest recovery command after a mistaken rename, draft, browser change, or multi-step workflow, with no claim that an irreversible external effect was undone.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic action-ledger lookup, dependency analysis, and compensating-action planning. Use a background model only to explain consequences or disambiguate the owner's reference; never invent an undo.
- **latency:** Identify the candidate and produce a reversal preview in under 3 seconds; execute only after the existing policy/confirmation path. Spoken response stays to one sentence unless detail is requested.
- **cost:** <$0.01 for lookup and preview; execution uses existing surface calls. Optional explanation costs roughly $0.005–$0.02.
- **security:** Never reverse destructive or externally visible effects automatically. Require a fresh owner confirmation for mail, purchases, deletion, or third-party changes. Use idempotent compensating actions, retain the original receipt, and clearly mark partial recovery and residual effects.
- **missing:** A shared operation ID and cross-surface action graph, not merely telemetry localJobId; Compensating-action contracts for browser and Mac actions, including explicit non-reversible effects; A durable dependency/undo ledger with partial-success states and stale-plan revalidation; A unified owner-facing route that previews reversal before mutation


## What it asked for

_Nothing._
