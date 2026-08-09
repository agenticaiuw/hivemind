# Harness derivation — faculty-judgement — round 274

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make the system watch its own storage and tell me before it can no longer record, retain, or deliver anything."
- **useful because:** The owner has repeatedly asked for free-disk information and currently gets no dependable answer. A resource guardian would prevent silent loss of voice notes, audio artifacts, and durable Mac state, instead of discovering the problem after a briefing or capture failed. It would speak one short warning only when a threshold is crossed and leave a detailed dashboard report.
- **path:** Mac terminal checks workspace volume, audio-retention bytes, and atomic-store health → relay records the warning and suppresses nonessential generated audio when the Mac reports a critical state → pendant receives a compact signed alert through the existing alert inbox and can still play the alert offline → dashboard shows the measured path, threshold, affected stores, and recovery steps
- **model tier:** background for periodic measurement and classification; realtime only when the owner asks why a warning occurred
- **latency:** measurement under 2 seconds; warning delivery can take one relay tick; no model call for ordinary healthy checks
- **cost:** Near-zero API cost when healthy; occasional background classification is under a cent, with disk probes and retention accounting dominating engineering cost rather than tokens
- **security:** Only byte counts, filesystem identifiers, and health states leave the Mac; never upload filenames or note/audio contents. Critical suppression must fail closed for destructive or external actions, and every warning needs a source timestamp.
- **missing:** A scheduled Mac resource probe with per-store byte accounting and configurable owner thresholds; A relay-side resource-state record and hysteresis so repeated checks do not spam; A signed compact alert envelope field for resource severity and expiry; A dashboard/voice explanation route for why output was suppressed

### "Forget everything the system learned from this website or person, and prove to me what was removed and what could not be removed."
- **useful because:** Today revoking a source capsule does not reach derived facts or the context graph, and there is no global forget operation. A source-scoped erasure ceremony would let the owner revoke a mistaken or sensitive source without hunting through unrelated stores, while an honest residue report prevents a false claim that deletion was complete.
- **path:** browser identifies the origin and its evidence/provenance links → Mac performs a preview-only fan-out over capsules, facts, context-graph entities/relations, local notes, and queued drafts → relay records a signed revocation event and propagates a retraction to fleet memory when that store is available → pendant receives only a terse completion/failure alert, never the erased content → dashboard presents an itemized erasure receipt with remaining copies, retention reason, and retry action
- **model tier:** background deterministic workflow; use the realtime model only to interpret an ambiguous owner target, never to choose deletion scope silently
- **latency:** preview in under 5 seconds for normal stores; apply may take up to 30 seconds and must be resumable; the spoken result stays one sentence
- **cost:** No model cost for an exact origin identifier; less than a cent for optional ambiguity resolution. Storage scans and durable tombstone writes dominate.
- **security:** Default to preview and require explicit confirmation for the destructive apply. Do not expose secret values in the receipt. Preserve only hashed identifiers, tombstones, provenance IDs, and failure reasons. A partial failure must be reported as partial, never complete.
- **missing:** A source-link field on memory facts and graph copies so derived records can be reached; A cross-store deletion/retraction coordinator with idempotent tombstones; A durable erasure receipt and retry queue on the Mac and relay; A fleet-memory writer and migration in the deployed relay schema; A safe preview/apply endpoint that reports exact residual stores

### "Give me a weekly scorecard of whether your plans and briefings were actually useful: delivered, acted on, deferred, wrong, or ignored—and use that evidence to change how much you interrupt me."
- **useful because:** The system currently records many completion events but cannot tell whether the owner received an audio item, acted on it, or found it wrong. This closes the loop between what the hive decided and what happened in the owner's life, so interruption and planning become empirically less annoying rather than permanently hand-tuned.
- **path:** pendant supplies authenticated downloaded/started/finished/interrupted ACKs and lets the owner mark an item useful, wrong, or not now → Mac correlates plan/action receipts, calendar/mail/browser outcomes, and local completion signals without exporting their contents → relay aggregates only typed outcomes and confidence by policy/source/item class → dashboard presents a weekly calibration report with evidence links; the pendant speaks only the top change, such as fewer interruptions during a measured quiet period
- **model tier:** background deterministic aggregation and calibration; realtime only for a short spoken owner rating or an ambiguous outcome label
- **latency:** No synchronous cost for normal actions; a weekly report under 10 seconds after the source reads complete; owner rating acknowledged in one turn
- **cost:** Near-zero for aggregation; occasional short realtime classification is under a cent. The dominant cost is durable outcome schema and correlation work, not inference.
- **security:** Store typed outcome metadata, not mail bodies, page text, or audio. Keep evidence references revocable and distinguish 'not received' from 'ignored'. Never silently change a destructive-action policy from this scorecard; only interruption ranking and noncritical planning weights may adapt, with an owner-visible diff.
- **missing:** An outcome vocabulary and durable correlation from relay job to Mac action to pendant artifact; An owner rating path bound to the current brief item without replay or duplicate submission; A calibration aggregator that separates delivery failure, attention suppression, wrong content, and owner choice; A policy-change proposal/apply step so learned adjustments require review

### "Before I commit to a meeting, purchase, trip, or deadline, show me the consequences across my actual day and let me compare alternatives without changing anything."
- **useful because:** The owner can currently plan or preview isolated actions, but cannot ask a single truthful counterfactual question such as “what does accepting this do to my travel, existing commitments, focus time, reminders, and pending work?” A cross-surface shadow plan would make tradeoffs visible before the commitment, especially when the browser holds the decisive state and the Mac holds the schedule.
- **path:** browser reads the authenticated offer, appointment, travel, or checkout details without submitting → Mac reads available calendar/reminder/mail/task and local-plan evidence, marking unavailable sources instead of assuming empty → relay builds two or more immutable counterfactual branches and returns time, interruption, spend, privacy, and deadline consequences → pendant gives a short comparison and lets the owner choose a branch to prepare, never commit it → dashboard shows the evidence and changed assumptions side by side, with an expiry when the source state becomes stale
- **model tier:** background deterministic planner for branch construction and conflict calculation; realtime only to resolve the owner's natural-language alternatives and summarize the winning diff
- **latency:** Initial branch comparison under 8 seconds; stale-source recheck under 2 seconds; no external mutation during simulation
- **cost:** One short model call, roughly cents per comparison; browser reads and calendar/mail extraction dominate latency, while branch evaluation should be deterministic and cheap
- **security:** Simulation must be strictly read-only and redact sensitive snippets from the spoken comparison. Never infer purchase consent from selecting a branch. Every branch carries source timestamps, uncertainty, and a revalidation token before any later prepare/apply step.
- **missing:** A typed counterfactual branch and assumption model with provenance per field; A read-only cross-surface aggregator for browser, calendar, reminders, mail, and local jobs that distinguishes unreadable from empty; A consequence engine for time conflicts, deadline risk, spend, interruptions, and privacy exposure; A durable stale-plan/revalidation link from a chosen branch to the existing prepare/approval flow


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct owner-facing capabilities: a storage/resource guardian that prevents silent capture and delivery failure; a source-scoped erasure ceremony with honest residual receipts; and a weekly outcome/calibration scorecard that learns from delivered, interrupted, useful, wrong, and ignored briefings without silently changing destructive policy. A fourth correction-learning idea was rejected as already covered, so I did not rephrase it. I still need implementation work rather than more owner context: durable cross-surface outcome correlation, resource thresholds and hysteresis, source links for derived records, and a review/apply boundary for learned interruption changes. The owner-defined interruption and disclosure policies remain intentionally open; I will not invent them.

**Biggest unknown:** Whether the owner wants calibration results to modify only interruption ranking or also noncritical planning priorities; this must be an explicit policy choice, not inferred from usage.

