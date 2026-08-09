# Harness derivation — faculty-judgement — round 190

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **owner timezone conflict** — Owner projection says America/Chicago, while authoritative Mac routine policy is America/New_York; do not silently use either for owner-location claims. Routine scheduling remains New York until owner clarifies personal timezone.
  - evidence: discover:owner remembered timezone America/Chicago; granted context authoritative routine timezone says Mac resolves America/New_York and pendant has no timezone.

## Capabilities it proposed

### "“When I return to my desk, give me a two-minute handoff: what I marked while away, what changed in the browser, and the one next step.”"
- **useful because:** A moment bookmark is currently just a marker. This turns returning into continuity: the worn device supplies the offline boundary, the browser supplies changed pages, and the Mac turns it into an actionable handoff without making the owner reconstruct the last hours.
- **path:** pendant → mac → browser → relay
- **model tier:** Background model for gathering and compression; realtime only if the owner asks follow-up questions
- **latency:** Prepare within 10 seconds of the Mac becoming active; speak at most one short sentence and leave detail as a note
- **cost:** Low to moderate: browser reads dominate; model sees bounded diffs and bookmark metadata, not whole page histories
- **security:** Read-only browser scopes by default; redact page secrets and do not include URLs/snippets from private origins in spoken output unless policy allows. The handoff is a draft/note, never an external action.
- **missing:** A live event bridge from sw1 offline_moment_bookmark to relay/Mac; A desk-return detector combining bookmark state with owner idle/foreground signals; A bounded diff query over page-watch reports since the bookmark

### "“I’m torn between these options—show me the consequences, ask one clarifying question, and prepare the safest reversible choice.”"
- **useful because:** The system can plan and execute, but it does not help the owner decide when several actions are plausible. This is a genuine judgement capability: compare options across current browser/Mac state, surface uncertainty, and stop at a reversible prepared plan rather than acting.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** Background model gathers evidence and drafts the comparison; realtime handles the single clarifying question; deterministic policy evaluates the final candidate
- **latency:** Initial comparison in 5–15 seconds; one spoken question; no mutation until the owner explicitly approves
- **cost:** Moderate: browser/Mac evidence collection dominates; one model pass for synthesis, then cheap autonomy_policy_evaluate
- **security:** Evidence is source-linked and redacted; external side effects, spending, deletion, and messages are always ASK/physical approval. Stale evidence triggers revalidate_pending_plan rather than execution.
- **missing:** A typed option-set/criteria object with provenance and reversibility; A dashboard card showing tradeoffs and the exact policy rule that blocks mutation; A physical approval binding from the existing transaction-approval latch to the prepared plan

### "“If the pendant has no LTE, keep the conversation working over its USB-tethered Mac, then reconcile everything when it reconnects.”"
- **useful because:** The hardware is physically present and testable now, but LTE registration is false. The owner should not experience a dead pendant or duplicate jobs merely because transport changed. This capability makes USB a real local fallback and later merges queued audio, bookmarks, approvals, and delivery receipts exactly once.
- **path:** pendant → mac → relay → dashboard
- **model tier:** Realtime for the live USB conversation; background model only for reconnect reconciliation and conflict summaries
- **latency:** USB audio/control within the existing conversation latency; reconnect reconciliation under 5 seconds before announcing state
- **cost:** Low ongoing API cost; USB serial and local audio dominate. Background synthesis is invoked only when queued events conflict.
- **security:** Authenticate the USB session separately, bind it to the device session and monotonic counters, and fail closed on replay. Do not treat USB presence as LTE identity. Sensitive content stays local unless the relay policy explicitly permits upload; external actions remain gated by autonomy_policy_evaluate and physical approval.
- **missing:** A production USB transport/session adapter for the nRF9160 and ESP32 serial devices; A transport-neutral event log that deduplicates queued events across USB and LTE; A reconnect merge policy for conflicting playback, bookmarks, and pending approvals

### "“At the end of the day, tell me what derailed my plans, which interruptions mattered, and what one change would have prevented the biggest loss.”"
- **useful because:** The system can report events and receipts, but cannot explain the causal shape of a day. A retrospective would distinguish owner choices, missed delivery, stale automation, browser churn, and interruptions, then show a counterfactual rather than merely listing activity.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background model after the day ends; realtime only when the owner asks a follow-up
- **latency:** Under 30 seconds for a daily retrospective; one short spoken conclusion with detail on the dashboard
- **cost:** Moderate: event joining and browser diff extraction dominate; one synthesis pass per day
- **security:** Use event IDs and summaries by default, not raw mail/page text. Sensitive evidence stays local and is revealed only in the dashboard after explicit request. Do not infer blame or health claims; label causal links as hypotheses with confidence.
- **missing:** A durable cross-surface correlation key joining relay jobs, Mac actions, browser commands, pendant markers, and attention decisions; A causal timeline schema that records planned, attempted, delivered, interrupted, and completed states; A counterfactual evaluator that can compare the day against alternate interruption or scheduling choices

### "“When I correct one of your judgement calls, remember the correction as a temporary rule, test it on the next similar case, and show me whether it helped.”"
- **useful because:** Today a correction is usually lost as conversational context or becomes an opaque preference. This would let the owner teach judgement safely: the rule has scope, expiry, evidence, and an explicit before/after evaluation rather than silently changing future behavior.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Realtime to acknowledge the correction; background model to generalize and evaluate it
- **latency:** Acknowledge immediately; propose the normalized rule within 5 seconds; evaluate after the next matching event
- **cost:** Low to moderate: cheap deterministic matching, with background synthesis only for ambiguous corrections
- **security:** Never generalize from a correction involving secrets or third-party private data without confirmation. Rules must be scoped, expiring, revocable, and explainable; they may constrain autonomy but never grant mutation authority.
- **missing:** A durable correction/rule record with scope, expiry, confidence, and owner confirmation; A shadow-mode evaluator that predicts what the old and new rule would have done without acting; A feedback receipt linking the next decision to the rule and recording outcome


## Changes it proposed to its own stack

### `context` — Add a cross-surface ‘state capsule’ created at every deliberate context switch: the pendant marker identifies the boundary, the Mac records foreground app and active reversible jobs, the browser records tab IDs plus redacted page fingerprints, and the relay stores only a bounded encrypted digest. On return, compare the capsule with current state and offer a read-only restoration plan without reopening or mutating anything automatically.
- **owner gets:** The owner could leave a task without losing the thread, then resume with the exact unfinished state and visible changes instead of reconstructing it from memory or reopening stale tabs.
- effort: High: requires a durable join ID across five namespaces, pendant marker ingestion, browser fingerprint export, Mac snapshotting, encrypted relay storage, and a restore-plan UI.  ·  risk: Stale or misidentified context could reopen the wrong work. Recovery is read-only by default, expires capsules quickly, requires revalidation before any action, and lets the owner discard the capsule.
- cost: Low ongoing API cost; bounded digest storage and one background comparison on return. Engineering cost is substantial.  ·  latency: Capture under 1 second; return comparison under 5 seconds for normal-sized snapshots.
- security: High sensitivity: browser content must remain redacted and secrets excluded. Relay receives opaque fingerprints and encrypted metadata, not page bodies or credentials.
- depends on: offline_moment_bookmark; a durable relay-job/Mac-job/browser-command correlation ID; revalidate_pending_plan; authenticated browser fingerprint export; owner-configured retention and disclosure policy


## What it asked for

_Nothing._
