# Harness derivation — relay-realtime — round 207

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If that task finishes, tell me on my pendant even if I’ve stopped talking.”"
- **useful because:** This is the biggest quality-of-life feature: the owner can fire off a long Mac job and walk away. No polling, no staring at a screen, and no lost updates if the link drops.
- **path:** relay → mac-bridge → pendant → dashboard
- **model tier:** Realtime only for the initial voice command; a cheaper background tier for monitoring and summarization.
- **latency:** Initial acknowledgement under a second; completion alert can arrive minutes later.
- **cost:** Low per event; the expensive part is job monitoring. Most of the time should run in a cheaper background context or a relay worker, not the realtime model.
- **security:** Alert text must be accurate and sourced from job status. Sensitive content should be redacted or require confirmation before being spoken aloud.
- **missing:** A real completion-event delivery path (relay_event_push is unresolved).; A durable watch mechanism in the relay for job state transitions.; A delivery target that can render speech on the pendant without storing audio by default.

### "“What’s the status of the thing you sent to my Mac?”"
- **useful because:** Owners ask this constantly. It should work even when the Mac is asleep and should speak a concise, truthful answer.
- **path:** relay
- **model tier:** Realtime, since it’s a quick conversational check-in.
- **latency:** Sub-second; no Mac round trip.
- **cost:** Very low; reads existing relay job records.
- **security:** Never summarize beyond the tool output. If the status is unknown or failed, say so verbatim.
- **missing:** 

### "“Tell me what’s going on with my setup right now.”"
- **useful because:** A quick health snapshot helps the owner trust the system: what’s online, what’s paired, and what’s missing, spoken in a friendly way.
- **path:** relay → mac-bridge → pendant
- **model tier:** Realtime for quick spoken summary; deeper diagnosis should go to a cheaper tier.
- **latency:** Under two seconds for a summary; deeper checks can be deferred.
- **cost:** Low; relies on existing status endpoints and job records.
- **security:** Avoid leaking sensitive account details; only report operational state.
- **missing:** A reliable pendant registration/status endpoint (previously 404).; A relay self-capabilities endpoint for inventory.

### "“I just finished a conversation. Turn the commitments I spoke into the right follow-ups: check my calendar and authenticated browser context, draft the needed messages and reminders on my Mac, and tell me exactly what is waiting for my approval.”"
- **useful because:** The owner can leave a conversation with actionable follow-ups without reconstructing details later. The pendant supplies the fresh spoken commitments, the browser supplies context the relay cannot see, and the Mac produces concrete drafts rather than a generic transcript. It preserves control over sending while eliminating the clerical work.
- **path:** pendant → relay → browser → mac-planner → mac-vision → dashboard
- **model tier:** Realtime extracts only commitments and urgency from the utterance; mac-planner performs the slower cross-app planning, browser-extension/mac-vision gathers evidence, and a cheaper background model normalizes duplicate commitments.
- **latency:** Acknowledge in under 1 second; gather context and create drafts within 30–90 seconds. The pendant can speak a queued completion summary after the session.
- **cost:** About $0.01–$0.05 per invocation depending on browser/vision turns; most cost is Mac/browser evidence gathering, not realtime speech.
- **security:** Calendar, authenticated pages, and spoken private content leave their local surfaces only to the relay/orchestrated agents. Never send or delete without the owner's existing policy/explicit approval; attach source snippets and confidence so inferred commitments are visible.
- **missing:** A commitment-extraction and deduplication job that links one voice utterance to browser/calendar evidence; A cross-surface draft bundle with per-artifact provenance and approval state; A single completion/approval summary that can be delivered to the pendant inbox

### "“While I’m away from my Mac, watch the specific page and local app state I name. If the condition becomes true, prepare the next action, but wait until I tap the pendant to carry it out; if it becomes false again, discard the stale plan.”"
- **useful because:** This gives the owner a safe hands-free trigger for changing real-world conditions rather than a one-shot command. The important behavior is state validity: a plan is based on a fresh observation, expires when the observed state changes, and requires only a physical tap at the final moment.
- **path:** pendant → relay → browser → mac-planner → mac-vision → dashboard
- **model tier:** A cheap scheduled/watch evaluator compares page and screen observations; mac-planner creates the candidate action; realtime is used only to explain the trigger and receive the tap.
- **latency:** Checks on the configured interval; speak or queue an alert within 10 seconds of a qualifying transition, then execute within 5 seconds of a tap while the Mac/browser is reachable.
- **cost:** Roughly $0.001–$0.02 per check depending on whether text inspection or visual reasoning is needed; the dominant cost is repeated visual/browser capture.
- **security:** Authenticated page contents and screen images remain scoped to the watch. The tap is an explicit physical commit, and every queued action carries an observation timestamp, expiry, and target fingerprint to prevent acting on stale UI.
- **missing:** A watch type that can combine browser page predicates with Mac app/screen predicates; Versioned observation snapshots and invalidation of queued plans when state changes; Pendant tap-to-commit delivery for a pending, attested action

### "“If you cannot complete my request on the first surface, recover across the hive: use the browser if the Mac app is unavailable, use the Mac if the browser session is unavailable, and give me one honest spoken result that says what was tried, what actually changed, and what remains.”"
- **useful because:** Today a disconnected Mac, expired browser session, or changed UI turns a useful request into a dead end. This makes the system's physical diversity useful: it can route around a failed node instead of pretending success, while the owner receives one concise outcome rather than debugging logs.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Realtime classifies the request and speaks the immediate acknowledgement; a background planner runs the fallback graph and a small verifier compares receipts and observations. Use vision only on the branch that needs it.
- **latency:** Immediate acknowledgement under 1 second; fallback attempts complete within 1–2 minutes, with a queued pendant update when the session has ended.
- **cost:** About $0.02–$0.10 for a failed-first-surface invocation; cost is dominated by extra browser/Mac attempts and verification, so stop after a bounded fallback graph.
- **security:** Fallbacks must not silently broaden scope: preserve the original target, arguments, and owner policy across surfaces. Report partial completion and never claim success from an attempted action; include receipts and before/after evidence in the dashboard.
- **missing:** A capability graph that maps equivalent operations across Mac and browser surfaces; Cross-surface idempotency keys and a verifier that detects partial/duplicate mutations; A user-facing failure/partial-success summary renderer tied to the existing pendant inbox


## Changes it proposed to its own stack

### `integration` — Implement job completion monitoring in the relay and deliver a short, accurate completion summary to the pendant via the existing inbox/alert mechanism. Use GET /jobs/:jobId and receipts as the source of truth; do not invent status strings.
- **owner gets:** They can start something on the Mac, walk away, and get notified when it’s done without polling.
- effort: Medium to high; needs a relay worker path and delivery integration to the existing pendant/phone alert flow.  ·  risk: Speaking the wrong status would be confusing. Mitigate by quoting the job’s own outcome and keeping summaries short.
- cost: Low per job; monitoring can be batched and run outside the realtime tier.  ·  latency: No impact on initial command; completion notifications arrive as events.
- security: Potentially sensitive task names; redact or require confirmation for sensitive categories.
- depends on: A real event delivery route (relay_event_push is unresolved).; A reliable pendant delivery path via the existing inbox mechanism.

### `context` — Wire the existing memory projection into the live conversation context builder, replacing legacy prompt composition. Use projection to send only relevant, stable facts and reduce per-turn context churn.
- **owner gets:** More responsive conversations and fewer token-budget failures, while keeping the agent grounded in relevant preferences and tasks.
- effort: Medium; known injection point in conversationContext.js.  ·  risk: Projection bugs could omit critical context. Mitigate with staged rollout and logs of dropped facts.
- cost: Reduces per-turn token cost significantly (already measured).  ·  latency: Likely improves prompt build time.
- security: Keep sensitive facts gated; honor surface scoping.

### `relay` — Add a durable cross-surface intent ledger. Every accepted request gets an idempotency key, immutable original utterance/constraints, current target surface, observation timestamp, attempted action receipts, and explicit partial-success state. A fallback executor may claim the same intent on another surface only when the prior receipt proves no mutation or the operation is read-only; otherwise it pauses as uncertain and reports that uncertainty.
- **owner gets:** When the Mac, browser, or network drops mid-task, the owner gets one truthful answer and does not cause duplicate sends, reminders, purchases, or edits by retrying blindly.
- effort: Medium-high: schema, lease/claim logic, receipt normalization, and integration with plan/execute and browser observations.  ·  risk: A false receipt could suppress a needed retry, or a lease could strand work. Recover with lease expiry, an explicit unknown state, and a dashboard action to resume or abandon.
- cost: Small D1/storage and background-model cost; no meaningful realtime-token increase after the initial acknowledgement.  ·  latency: Adds milliseconds to dispatch and a few seconds for verification; bounded fallback attempts can run asynchronously.
- security: Improves auditability but stores utterances and target metadata; encrypt or minimize sensitive fields and preserve existing surface scoping.
- depends on: A real cross-surface operation equivalence map; Normalized action receipts from Mac and browser; A completion event path to the pendant inbox

### `context` — Wire the existing memory projection into the live conversation prompt, but attach a per-job provenance pointer for every injected fact and commitment. The relay should be able to say which remembered preference or prior task caused a downstream action, rather than treating projected context as invisible instructions.
- **owner gets:** The pendant can stay brief while still remembering the owner's editor, permissions, ongoing task, and prior commitment; if something is wrong, the owner can correct the exact memory instead of repeating their entire preference.
- effort: Low-medium: replace the legacy context composition call, carry selected fact keys through job creation, and expose them in receipts/dashboard.  ·  risk: Incorrect or sensitive memories could influence an action. Keep existing surface/sensitivity filtering, mark low-confidence facts as suggestions, and provide a one-utterance correction path.
- cost: Cuts the measured prompt context from about 374 to 152 tokens per turn, reducing recurring model cost; provenance adds a small receipt payload.  ·  latency: Likely slightly faster prompts due to fewer tokens; negligible ledger overhead.
- security: Provenance makes sensitive-context use observable, but requires careful redaction in spoken summaries and dashboard logs.
- depends on: conversationContext.js calling projectContext(surface, task); Fact-key propagation into /plan and job receipts


## What it asked for

_Nothing._
