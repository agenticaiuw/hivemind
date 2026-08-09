# Harness derivation — faculty-judgement — round 223

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Tell me what actually changed in my life this week—not a list of notifications, but the important shifts, unfinished threads, and decisions that now matter.""
- **useful because:** The owner currently has many pull-only surfaces and fragmented receipts, but no way to understand the shape of a week. This is the highest-value judgement capability: compress noisy cross-surface evidence into a grounded life delta, explicitly separating observed change from interpretation and unknowns.
- **path:** relay → pendant → mac → browser → dashboard
- **model tier:** Background model for collection and clustering; expensive realtime model only for the owner's follow-up questions and spoken three-sentence version.
- **latency:** A weekly run may take 30–90 seconds; spoken answer under 8 seconds after the owner asks, using a precomputed signed snapshot.
- **cost:** Roughly $0.03–$0.15 per weekly run depending on mail/page volume; realtime follow-ups dominate only when the owner drills into a thread.
- **security:** Private mail, authenticated pages, calendar/reminder results, and pendant markers must remain local or relay-redacted. Never speak names or message content by default. Every claim needs source references, freshness, confidence, and a sensitivity-aware delivery decision; owner confirmation is required before creating any task or contacting anyone.
- **missing:** A durable weekly snapshot and comparison job with source-linked claims; A reliable EventKit permission/readability result before using calendar absence as evidence; A production fleet-memory writer so Mac/browser/pendant observations can be joined; A scheduler/trigger for weekly collection; A presentation that exposes unknowns instead of treating empty sources as all-clear

### ""Show me which decisions I made recently, what evidence I used, what happened afterward, and what I should change next time—without pretending the outcome was caused by me.""
- **useful because:** The system records plans, executions, evidence, and browser/page observations, but it cannot turn them into an honest learning loop. This gives the owner decision-quality feedback rather than another task list, while preserving uncertainty and alternative explanations.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Background model builds a causal ledger and asks a cheaper verifier to check source links; realtime model answers one decision review conversationally.
- **latency:** Initial review 20–60 seconds for a selected decision; spoken drill-down under 6 seconds.
- **cost:** $0.02–$0.10 per reviewed decision, dominated by evidence retrieval and long-page summarization; no cost when only showing stored receipts.
- **security:** Do not infer causality from temporal order. Label observed, owner-stated, and model-inferred links separately. Keep raw quotes local, redact before relay/TTS, and require explicit confirmation before persisting a behavioral lesson or changing future policy. Revocation must remove derived links as well as source presentation.
- **missing:** A durable decision record linking plan, approval, execution, evidence, and later outcome; A causal-language policy that forbids unsupported 'because of you' claims; A real cascade from evidence revocation into facts, graph entities, and derived lessons; A later-observation trigger (watch or scheduled review) that reopens the decision; Owner-facing review UI for correcting the model's interpretation

### ""What is quietly consuming my attention lately, and what is one humane change I can make without dropping anything important?""
- **useful because:** The owner gets triage and interruption decisions, but no reflective view of recurring attention costs across email, browser churn, calendar transitions, pendant interruptions, and unfinished work. It turns those traces into one bounded, reversible recommendation rather than silently optimizing the owner's life.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Cheap background aggregation and trend detection; realtime model only conducts the private conversation and handles ambiguity.
- **latency:** Generate a weekly pattern in under 2 minutes; answer a spoken question in under 7 seconds.
- **cost:** $0.02–$0.08 per weekly pattern, mostly summarizing browser/mail and action receipts; negligible incremental realtime cost.
- **security:** Attention patterns can reveal health, relationships, employment, and location. Keep raw event data on Mac, send only redacted aggregates, default to private dashboard rather than speech, and never classify a person as 'draining' from sparse evidence. Suggestions must be reversible and owner-approved; no automatic blocking, hiding, or message changes.
- **missing:** A cross-surface event normalizer with consistent timestamps and dedupe; An honest idle/presence and interruption history route (focusPolicy is not exposed and macOS Focus is unavailable); A privacy-preserving aggregation layer that emits counts/trends rather than raw content; An owner-editable preference for what kinds of attention costs matter; A reversible recommendation executor tied to autonomy_policy_evaluate

### ""Where am I acting against my own stated priorities, and what is the smallest honest change that would bring my week back into alignment?""
- **useful because:** The system can eventually remember preferences and actions, but it cannot compare the owner's declared priorities with their observed allocation of time, attention, and commitments without collapsing that comparison into generic productivity advice. This gives the owner a non-moralizing mirror: evidence, contradiction, uncertainty, and one reversible experiment.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background model performs monthly or weekly aggregation; realtime model is used only for a private spoken conversation and never invents a priority.
- **latency:** A full audit in 1–3 minutes; spoken answer under 8 seconds from a prepared, source-linked report.
- **cost:** $0.04–$0.20 per audit, dominated by longitudinal summarization; follow-up questions are low incremental cost.
- **security:** This can expose intimate values, work patterns, relationships, and health-adjacent inferences. Store declared priorities separately from model interpretations, require owner confirmation before treating an inferred value as real, keep raw evidence on the Mac, and default delivery to the private dashboard rather than aloud. Never infer a diagnosis or personality trait.
- **missing:** An owner-authored priority/value record with versioning and expiry; A longitudinal, privacy-preserving aggregate of time, attention, interruptions, and actions; A typed distinction between owner-declared, observed, and inferred claims; A correction loop that lets the owner reject a comparison without poisoning unrelated memory; A reversible experiment mechanism whose result is reviewed rather than silently adopted

### ""Before I walk into this recurring situation, remind me of the context that matters to me—what I decided last time, what I promised, and what I should not forget—without making me relive private details aloud.""
- **useful because:** A calendar title, browser tab, or message is not enough context, and a generic briefing is too broad. The owner needs a just-in-time private context packet attached to a recurring situation, with a silent or spoken-safe version on the pendant and full citations on the dashboard.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** Background model prepares packets from prior evidence and observed outcomes; realtime model selects the smallest safe spoken rendering at trigger time.
- **latency:** Packet prepared at least 2 minutes before a known trigger; pendant rendering starts within 2 seconds when the owner requests it.
- **cost:** $0.01–$0.06 per packet, mostly retrieval and compression; realtime cost is limited to the brief rendering.
- **security:** A context packet can reveal names, disputes, medical or financial details to bystanders. Maintain separate silent/full and spoken-safe projections, apply redaction before TTS, expire packets after the situation, and never include credentials or page secrets. The owner must be able to inspect and delete every attached source.
- **missing:** A durable situation identity that survives recurring calendar/browser changes; A source-linked packet store with expiry and spoken-safe projection; A trigger adapter for calendar-like and browser-like situations that reports unreadability honestly; A pendant delivery/readback acknowledgement tied to the current situation; A policy field specifying whether a situation may be spoken or only shown


## Changes it proposed to its own stack

### `interaction` — Add a durable 'owner correction becomes a rule' loop: when the owner corrects a judgement (for example, why a task mattered, what evidence was misleading, or what must never be spoken), present the proposed rule, scope, expiry, affected surfaces, and historical violations; on confirmation, publish it to the shared policy evaluator and attach it to future provenance receipts. Every later use must show whether the rule matched, was overridden, or was unavailable.
- **owner gets:** The owner would teach the system once instead of repeatedly correcting the same mistake, while retaining control over scope and expiration. It turns lived corrections into visible behavior rather than hidden model memory.
- effort: High: a durable versioned rule record, correction UI/voice flow, historical backtest, cross-surface publication, and enforcement at relay, Mac, browser, and pendant boundaries.  ·  risk: An over-broad inferred rule could suppress useful help or block urgent work. Fail closed for external side effects, require confirmation for rule creation or widening, support one-tap rollback, and show matched-rule provenance on every decision.
- cost: Small storage and evaluation overhead; occasional background backtests cost roughly $0.01–$0.05 per rule. No new audio cost beyond normal delivery.  ·  latency: One extra deterministic policy check per action; rule creation may take seconds for a historical backtest but must not delay emergency stop behavior.
- security: Improves privacy and consent if rules are scoped, expiring, and local-first; creates a sensitive record of the owner's boundaries, so encrypt it locally and redact rule text before third-party model calls.
- depends on: A durable cross-surface policy store rather than the current in-memory capability registry; A real relay-to-Mac policy publication path; Owner-visible correction and rule approval UI; Integration with autonomy_policy_evaluate, explain_action_provenance, and the physical consent latch


## What it asked for

_Nothing._
## Its own summary

Recorded three distinct owner-facing capabilities: a grounded weekly life-delta review (the single most useful), an outcome-aware decision review that refuses unsupported causality, and a privacy-preserving attention-cost reflection. All three require cross-surface judgement rather than another single-node action.

**Biggest unknown:** The owner has not chosen disclosure and interruption policies, and the live inventory still needs verification for several proposed route names. The practical blockers are durable cross-surface joins, truthful EventKit readability, and scheduled background collection—not model cleverness.

