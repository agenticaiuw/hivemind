# Harness derivation — faculty-judgement — round 251

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Give me a morning brief I can trust: tell me what is known, what was unreadable, what changed since yesterday, and do not call an empty source clear."
- **useful because:** The owner currently has two overlapping 07:00 briefs and a 07:30 brief, while unauthorized EventKit reads can look like an empty calendar. This would make the first thing they hear a calibrated account rather than a confident fiction, and would coalesce duplicates into one spoken result.
- **path:** relay → mac → pendant → dashboard
- **model tier:** Background model for source comparison and concise drafting; realtime only for the owner's follow-up question.
- **latency:** Under 20 seconds after the scheduled jobs finish; source reads dominate, with no model call when every input is unchanged.
- **cost:** About $0.01–$0.05 per brief depending on source volume; most cost is one compact synthesis, not the deterministic checks.
- **security:** Speak only redacted headlines by default. Calendar/mail unreadability must be stated, not inferred. The dashboard should show source provenance; external mutations are out of scope and require confirmation.
- **missing:** A canonical scheduler/coalescer that recognizes the existing duplicate routine intents; A permission-aware source result contract for EventKit empty-pair corroboration; A persisted last-delivered brief fingerprint and delivery receipt so 'changed since yesterday' is real

### "Did that actually happen, or did the system only accept my request? Re-check the real world and tell me what changed, what did not, and what I can undo."
- **useful because:** Current receipts mostly stop at generation or acceptance. A job can be marked complete while the browser/Mac effect is stale, partially applied, or never delivered to the pendant. The owner needs an outcome statement grounded in a fresh observation, not a success-shaped receipt.
- **path:** relay → mac → browser → pendant
- **model tier:** Deterministic revalidation and receipt correlation first; use the background model only to summarize conflicting observations. Realtime is used only if the owner asks the question aloud.
- **latency:** 3–8 seconds for reversible Mac/browser effects; up to 15 seconds if a fresh browser read or Mac state probe is required.
- **cost:** Usually <$0.01 because the checks are route calls; model cost only occurs when evidence conflicts or needs natural-language synthesis.
- **security:** Read-only rechecks by default. Never retry a mutation as part of verification. Show the exact evidence chain and require confirmation before any undo or compensating action; redact secrets from spoken output.
- **missing:** A typed postcondition declaration attached to each plan/action; A durable relay-job to Mac-job/browser-command join key (currently only telemetry localJobId exists); Read adapters for important effects such as created reminders/notes, plus a standard undo locator

### "When I tell you a claim was wrong or useful, learn how reliable that source and kind of inference is for me, and show me when that experience changed your confidence."
- **useful because:** The system has confidence fields and provenance, but confidence is currently a static per-record value rather than an owner-calibrated estimate. A source that repeatedly misleads the owner should stop driving reminders or spoken interruptions; a source that proves reliable can be used without repeatedly asking. This gives the owner a way to improve judgement without silently rewriting facts.
- **path:** pendant → relay → mac → dashboard → browser
- **model tier:** Deterministic Bayesian or weighted calibration update; background model only clusters equivalent source/inference patterns. Realtime is unnecessary except for a spoken 'that was wrong' correction.
- **latency:** Immediate acknowledgement; under 1 second to update local calibration and under 10 seconds to propagate it to other surfaces.
- **cost:** Negligible for deterministic updates; occasional <$0.01 background clustering.
- **security:** Store only source-level reliability metadata, not raw private content. Never let calibration suppress safety-critical alerts without a visible rule. Every confidence change needs an evidence and owner-feedback receipt, and the owner can reset a source.
- **missing:** A durable calibration store and event type for owner feedback; A shared projection consumed by briefing triage, autonomy policy, and attention arbitration; A physical/voice correction gesture bound to the currently spoken item, with replay-safe item IDs

### "Before I commit to this plan, show me two plausible futures—what happens if I do it today and what happens if I defer it—and let me choose without changing my calendar, mail, reminders, or browser."
- **useful because:** The owner can currently rank tasks and prepare actions, but cannot see the likely downstream tradeoffs of a choice. A reversible counterfactual would turn the pendant from an executor into a decision aid: it could expose a meeting collision, a deadline cascade, an unanswered thread, or a stale browser dependency before the owner commits. It is especially valuable when the owner is walking and cannot inspect several apps.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background model builds the narrative from deterministic snapshots and compares branches; realtime is used only to answer a follow-up. No branch is allowed to mutate state.
- **latency:** A useful two-branch answer in 10–20 seconds; source collection and conflict detection dominate, with an immediate compact answer possible from cached snapshots.
- **cost:** Roughly $0.02–$0.10 per invocation depending on the number of sources and branch depth; deterministic snapshotting is cheap, while model cost is the branch comparison.
- **security:** Read-only by construction. Clearly label forecasts as estimates, cite every premise, distinguish owner commitments from model assumptions, and expire snapshots so stale plans cannot masquerade as current facts. Choosing a branch must create a reviewable plan, not execute it; external actions still require the existing autonomy policy and physical confirmation where applicable.
- **missing:** A typed counterfactual/branch object with assumptions, snapshot timestamps, predicted consequences, and expiry; Read adapters for reminders/notes and a durable commitment/dependency representation; current reconciliation is not a general dependency graph; A deterministic stale-snapshot check that rejects a branch when calendar, mail, browser, or job evidence changed; A dashboard and pendant interaction that lets the owner compare, select, or discard branches without sending the underlying private details aloud

### "Have I dealt with something like this before, and what happened when I chose each option? Find my own precedents before you advise me, but do not expose private details from unrelated situations."
- **useful because:** The system can store facts, context-graph entities, jobs, and receipts, but it cannot use the owner's lived history as a bounded precedent library. Personal precedent is often more useful than generic advice: it can reveal that a recurring meeting was always deferred successfully, or that a particular kind of rushed browser action repeatedly needed repair.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic retrieval and outcome matching first; a background model abstracts precedents and removes irrelevant specifics. Realtime only presents the short comparison.
- **latency:** Under 8 seconds for local precedent retrieval; up to 20 seconds when joining browser and Mac receipts and abstracting multiple cases.
- **cost:** Usually <$0.03; retrieval is local, and the model is used only to summarize matched precedents.
- **security:** Use purpose-limited, redacted abstractions rather than raw old messages or page contents. Do not surface third-party names or secrets. Every precedent needs source IDs, match reasons, confidence, and an easy 'do not use this memory again' control.
- **missing:** A durable precedent record that links an owner's decision, alternatives considered, outcome, and later correction; Outcome labels and cross-surface joins for completed Mac/browser/relay actions; A retrieval policy that enforces topic and sensitivity boundaries instead of searching the full context graph; An owner-facing correction and revocation flow for a precedent

### "Which intentions have I been carrying without moving, and should I finish, delegate, reschedule, or consciously drop them? Show me the evidence and ask before changing anything."
- **useful because:** The owner accumulates plans, reminders, browser drafts, and unfinished jobs that remain plausible forever. Existing routines can create reminders and watches, but nothing notices an intention that has repeatedly failed to progress or distinguishes a deliberate delay from an abandoned goal. A weekly, evidence-backed retirement conversation would reduce invisible cognitive load without silently deleting commitments.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic aging and activity analysis first; a background model clusters duplicate intentions and drafts four choices. Realtime presents only the short list and waits for the owner's decision.
- **latency:** Under 10 seconds from local stores and receipts; model drafting can complete in under 30 seconds as a background weekly job.
- **cost:** <$0.05 per weekly review; most work is local scanning and deduplication.
- **security:** Never infer that a goal is unwanted solely from inactivity. Show last evidence, source, and uncertainty; require explicit owner choice before creating, changing, or deleting reminders, plans, drafts, or browser watches. Private source content stays off the spoken channel.
- **missing:** A durable intention object linking captures, reminders, plans, jobs, drafts, and watches; Progress signals and an owner-defined aging policy, distinct from generic TTL deletion; A safe transition protocol for finish/delegate/reschedule/drop with preview and undo; Cross-surface joins so an action in one body updates the same intention rather than creating another


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: (1) a calibrated, duplicate-coalesced morning brief that says when a source was unreadable instead of calling it clear; (2) an outcome verifier that re-reads the world after an action and distinguishes acceptance from actual effect; and (3) owner-feedback calibration so repeated right/wrong judgments change future confidence with visible provenance. I also tested two tempting ideas—global erasure and playback catch-up—and the recorder correctly identified both as existing backlog themes rather than allowing restatements.

**Biggest unknown:** The missing connective identity remains the central blocker: there is no durable join across relay jobs, Mac jobs, browser commands, generated audio artifacts, and pendant delivery ACKs. Without that, outcome verification, truthful morning briefs, and calibrated feedback can each work only partially. I still need an authoritative inventory of the newly granted /v1/memory routes and a decision on the owner’s preferred confidence/feedback vocabulary; I will not invent either.

