# Harness derivation — faculty-judgement — round 242

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Give me my morning brief" — but only after checking that it is the one brief, based on readable sources, and actually reached my pendant."
- **useful because:** The current owner has overlapping 07:00/07:30 routines and a known calendar-permission failure mode that can confidently say 'all clear.' This would turn the most frequent daily interaction into a trustworthy answer: deduplicate the run, label unreadable sources as unknown, suppress duplicates, and prove downloaded/played delivery instead of treating server acceptance as success.
- **path:** relay → mac → browser → pendant
- **model tier:** Background model assembles and ranks the brief; realtime model only handles the owner's spoken follow-up. Deterministic reconciliation and policy checks run before either model.
- **latency:** Under 10 seconds to speak a short brief when caches are fresh; source reads may continue in background, with a compact 'still checking' alert only when needed.
- **cost:** Roughly one background-model invocation per canonical brief plus ordinary mail/browser fetch costs; near-zero model cost for duplicate detection, permission honesty, attention arbitration, and delivery ACK reconciliation.
- **security:** Never report an empty calendar as clear unless EventKit readability is positively established; redact before TTS; do not include mail bodies or browser secrets in relay payloads; require owner confirmation before any action suggested by the brief. Delivery ACKs carry opaque artifact IDs and positions only.
- **missing:** A canonical routine/brief identity with a durable deduplication lease across the two existing daily brief routines; A real EventKit Calendars/Reminders readability probe, distinct from Automation TCC; A brief-run record that joins relay job, Mac job, audio artifact, and pendant delivery events; A scheduler hook that invokes briefing triage and attention arbitration rather than waiting for pull requests

### ""Stop interrupting me when I keep skipping these, and tell me when you have learned a better time.""
- **useful because:** The arbiter can decide interrupt/defer/coalesce, but it has no memory of whether the owner actually listened, barged in, skipped, or resumed an item. An opt-in feedback loop would personalize timing from behavior instead of hiding guessed thresholds in a policy. It would also expose the reason for every learned change and allow one-tap reset.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic counters and a cheap background model summarize patterns; realtime is used only if the owner asks why a decision changed.
- **latency:** No added latency to an interruption decision: update counters asynchronously from delivery and interaction events. Weekly pattern summaries should arrive only during an owner-approved quiet window.
- **cost:** Negligible model cost for event updates; one small background summary per week. Main costs are durable event storage and retaining only coarse interaction metadata.
- **security:** Behavioral signals must stay private by default and never include spoken content, page text, or contact names. Require explicit opt-in, cap retention, distinguish 'did not hear' from 'chose not to listen,' and never silently escalate urgency. Every learned rule must be reversible and explainable.
- **missing:** A typed feedback event joining attention decisions to playback started/finished/interrupted, barge-in, defer, and explicit dismiss; A small durable preference-learning store with decay, confidence, and per-surface scope; A policy compiler that turns learned observations into proposed—not silently active—policy changes; An owner-facing review/reset route for learned interruption rules

### ""Help me run a seven-day experiment to make this habit happen, then tell me whether it worked.""
- **useful because:** The system can create reminders, watch pages, speak briefs, and record moments, but it cannot connect an intended behavior to observable evidence and a bounded outcome review. A time-boxed experiment would turn the pendant from an announcer into a quiet feedback loop: define one observable action, collect cross-surface evidence, nudge only under the owner's policy, and produce an honest result or 'not measurable' rather than pretending a reminder was progress.
- **path:** pendant → relay → mac → browser
- **model tier:** Background model helps translate the owner's goal into one measurable hypothesis and summarizes the week; deterministic watches, reminder state, delivery events, and timestamps handle observation and scoring.
- **latency:** Setup conversation under 15 seconds; nudges under 1 second once evidence is available; a seven-day review generated in the background and ready by the requested review time.
- **cost:** One setup and one review model call, plus cheap scheduled checks. Browser reads and Mac automation dominate runtime, not inference.
- **security:** Require explicit confirmation before creating recurring reminders or browser watches. Collect only the selected signal, not arbitrary page contents; show the evidence and confidence behind the score; auto-expire all watches and drafts at experiment end; do not infer health or sensitive traits from weak proxies.
- **missing:** A first-class experiment record with hypothesis, metric, observation sources, expiry, and owner-confirmed success criterion; A typed observation adapter that joins reminder completion, page-watch reports, pendant markers/audio interactions, and Mac timestamps without storing raw content; A scheduler and evaluator that emits no more than the owner's configured nudge budget; An end-of-experiment review and explicit delete/reset path

### ""Why did my plan go off track today, and what is the smallest change that would make tomorrow work better?""
- **useful because:** Today the system can show isolated jobs, reminders, page changes, and audio events, but cannot reconstruct the chain from intended plan to attention interruption to actual outcome. The owner should get an evidence-backed causal postmortem—not motivational speculation—with competing explanations, missing observations, and one reversible change to try tomorrow.
- **path:** pendant → relay → mac → browser
- **model tier:** Background model performs the retrospective synthesis; deterministic code joins timestamps, plans, reminders, attention decisions, browser reports, action receipts, and pendant delivery/interaction events. Realtime is unnecessary unless the owner asks a follow-up.
- **latency:** A daily postmortem ready within 30 seconds after the owner's chosen review time; no interruption unless explicitly scheduled. Evidence collection runs continuously but stores only selected event metadata.
- **cost:** One background synthesis call per review; storage and event-join work dominate. No model call for collection, filtering, or confidence calculation.
- **security:** Treat causality as uncertain: show evidence, alternatives, and confidence rather than blame. Do not retain page bodies, mail text, audio, or sensitive labels unless the owner explicitly includes them. The proposed change must be reversible and require confirmation before changing routines, reminders, or browser watches.
- **missing:** A cross-surface event ledger with shared IDs and normalized monotonic/wall-clock timestamps; A typed plan-outcome model linking intended tasks to observations and explicit completion evidence; A counterfactual evaluator that ranks candidate changes without silently applying them; A review surface showing citations, uncertainty, and an undoable proposed adjustment


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate proposals: a canonical, source-honest morning brief with end-to-end pendant delivery proof; opt-in interruption timing learned from actual listen/skip/barge-in behavior; and a bounded seven-day habit experiment spanning pendant, relay, Mac, and browser evidence. The attempted source-wide forget proposal was correctly rejected as an existing backlog item, so I did not rephrase it. I still need no new permission from the orchestrator. To implement the accepted ideas, the system needs durable brief identity/deduplication, feedback-event joins, and an experiment record/scheduler. From the owner, the remaining decisions are the measurable habit/experiment success criterion and whether interruption learning may be enabled; I will not invent either.

**Biggest unknown:** The owner's explicit morning-brief reliability target and experiment metric are still unknown. Existing owner interruption and disclosure preferences were declined as context requests, so all proposals must remain conservative, opt-in, and policy-driven rather than treating guessed thresholds as preferences.

