# Harness derivation — faculty-judgement — round 255

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""What changed since I last checked in?" Give me only meaningful changes across my calendar, mail, browser watches, Mac jobs, and pendant briefings, and let me mark each change seen."
- **useful because:** The owner currently gets separate pull-only surfaces and repeated briefings. A durable acknowledged baseline would make the pendant useful as a continuity layer: it can say what changed while the owner was away, avoid replaying unchanged items, and be honest when a source was unreadable. This is the single most useful missing everyday behavior because it turns many disconnected signals into one trustworthy answer without pretending a calendar is clear when permission is absent.
- **path:** relay → pendant → mac → browser → dashboard
- **model tier:** background for snapshot/delta computation; realtime only to answer the spoken question and summarize selected deltas
- **latency:** under 3 seconds for a spoken delta query when the baseline is current; up to 30 seconds for a refresh of all sources
- **cost:** low: one background delta job plus a short realtime response; dominated by mail/browser reads, not model tokens
- **security:** Persist hashes, timestamps, source IDs, and owner acknowledgements rather than raw mail or page bodies. Sensitive deltas default to 'something changed' until the owner asks for detail. Every item needs evidence refs and an explicit unreadable-source flag. Marking seen is reversible metadata; never mutate source content without confirmation.
- **missing:** a durable cross-surface baseline/ack store (not a second memory system; can extend the existing briefing queue or fleet-memory event schema); source adapters that emit comparable fingerprints for mail, calendar/reminders, browser watches, Mac jobs, and pendant delivery ACKs; a route to acknowledge a delta and query only changes since a cursor; a scheduler hook for refresh; current triage and briefing schedulers are pull-only

### ""Why did this keep failing, and what should we change?" Correlate repeated failures across my browser, Mac jobs, relay, and pendant link, then give me one safe fix and a reviewable draft change."
- **useful because:** Today a browser command, relay job, or audio delivery failure is isolated in its own receipt. The owner experiences one broken task, not four subsystems. A cross-surface failure narrative would detect patterns such as stale browser leases, orphaned Mac jobs, permission-induced empty reads, or pendant underruns, distinguish a transient failure from a systematic one, and recommend a reversible next step instead of silently retrying.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** background model clusters receipts and diagnostics; realtime only answers the owner's question; deterministic rules handle severity and retry safety
- **latency:** under 5 seconds for a recent failure already indexed; up to 60 seconds for a 24-hour correlation scan
- **cost:** low to moderate: mostly local receipt/log processing, with a short model synthesis; no external search unless requested
- **security:** Keep raw UART, page content, mail, and command arguments local. Send only redacted event IDs, error classes, timings, and hashes to the relay. Draft changes must never auto-apply. Any recommendation affecting permissions, credentials, or external side effects requires explicit confirmation and autonomy_policy_evaluate.
- **missing:** a durable join between relay job IDs, Mac/browser action IDs, pipeline IDs, and pendant artifact/event IDs; a read-only failure-correlation endpoint over GET /jobs/:jobId/receipts, GET /journal/:jobId, GET /logs, browser command results, and pendant diagnostics; a structured draft-change object with owner approval and rollback metadata; automatic orphan-job and browser-lease sweeps so the detector can distinguish active work from abandoned work

### ""Give me a weekly trust report." Show where you were certain, where you guessed, what I approved, what was blocked, and what information you retained or spoke across the pendant, Mac, browser, and relay."
- **useful because:** The owner cannot currently audit the system as one agent: receipts show completion, memory shows facts without a complete revocation chain, and spoken audio has weaker confidentiality enforcement than briefing text. A concise weekly trust report makes the system accountable in terms the owner can act on: false certainty, stale permissions, unacknowledged delivery, unexpected retention, and actions that need policy changes.
- **path:** dashboard → pendant → relay → mac → browser
- **model tier:** background model compiles a weekly report from deterministic provenance and policy records; realtime provides a short spoken headline and points to the dashboard for sensitive detail
- **latency:** generate asynchronously in under 2 minutes; spoken retrieval under 2 seconds if already generated
- **cost:** low: mostly aggregation and redaction; model cost is a single weekly synthesis, not per event
- **security:** The report itself is sensitive. Keep raw snippets on the Mac, redact spoken output to counts and categories by default, and require a local dashboard action to reveal source text. Include an immutable evidence chain for each claim, explicit unknowns, and a retention/deletion status. Never treat sensitivity classification as authorization; use a separate owner policy table with empty/conservative defaults.
- **missing:** a unified append-only audit stream for evidence -> judgement -> effect -> owner acknowledgement; retention and deletion propagation from evidence capsules to derived facts and context-graph copies; a real policy version recorded on each autonomy and attention decision; a dashboard/report route that can export a reviewable, redacted report and let the owner revoke a source or task

### ""I was wrong about that—fix every place you used it." Find all recommendations, reminders, drafts, memory facts, graph relations, and pending jobs derived from my correction, show me the impact, and revoke or amend them as one reviewable operation."
- **useful because:** The owner can currently revoke an evidence capsule or delete an individual fact, but derived copies and downstream actions survive. A correction should behave like a correction to one mind, not a cleanup hunt across unrelated stores. This would prevent stale assumptions from continuing to shape briefings or actions days later.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** deterministic provenance traversal and policy evaluation first; background model only explains the impact graph; realtime reads a short confirmation request
- **latency:** under 5 seconds to produce the impact set for normal histories; mutation only after explicit owner confirmation
- **cost:** low to moderate: graph traversal is local and deterministic; model cost is limited to explanation of ambiguous dependencies
- **security:** Default to tombstoning and amendment rather than destructive deletion. Never revoke unrelated facts merely because they share words. Require source-linked evidence and an explicit confirmation token for every external or destructive effect. Keep sensitive values local and display only redacted dependency summaries.
- **missing:** mandatory provenance links from every derived fact, reminder, draft, briefing item, and job to its source evidence; a dependency traversal and impact-preview route spanning Mac and relay stores; a transactional revoke/amend operation with idempotency and rollback; propagation adapters for memory facts, context-graph relations, reminders, browser drafts, and queued jobs

### ""Ask me the one question that would unlock the most useful work, and then remember my answer only for the scope I choose." Rank unresolved ambiguities across my pending jobs, routines, browser tasks, and personal state, ask one concise question at the right time, and apply the answer only where it belongs."
- **useful because:** The system currently either guesses, fails, or asks the owner repeatedly in separate surfaces. A clarification broker would turn uncertainty into a deliberate, bounded interaction: one high-value question instead of a stream of interruptions, with scope and expiry so a temporary answer cannot silently become a permanent preference.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** deterministic ambiguity scoring and scope checks; realtime asks and parses the short answer; background model may rank competing questions
- **latency:** ranking under 1 second; one spoken question under 2 seconds; applying the answer under 5 seconds
- **cost:** low: mostly policy and graph operations, with a brief realtime turn
- **security:** Never infer consent from silence. Show the proposed scope, expiry, affected tasks, and sensitivity before applying an answer. Answers involving destructive actions, spending, credentials, or external communication remain confirmation-gated. Store the answer as a scoped, expiring fact rather than a global preference.
- **missing:** a durable clarification queue with question, competing interpretations, scope, expiry, and evidence refs; an ambiguity scorer that can compare pending jobs, routines, browser tasks, and reconciled personal state; an owner response route that binds the answer to a specific question ID and rejects stale questions; attention-arbitrate integration so questions are deferred or coalesced rather than interrupting independently

### ""What did we know and decide at that moment?" Reconstruct the state of my work across the pendant, Mac, browser, and relay as of a past time, including what evidence was available then, what the system believed, and what actions had actually happened."
- **useful because:** Current status and memory views answer from now, while receipts and logs are fragmented and often lack the evidence-to-decision chain. When a deadline, purchase, message, or automation is disputed, the owner needs a trustworthy historical account—not a present-day reconstruction that accidentally uses later knowledge.
- **path:** dashboard → pendant → relay → mac → browser
- **model tier:** event-sourced deterministic reconstruction first; background model turns the result into a readable timeline; realtime gives only a short answer unless the owner requests detail
- **latency:** under 5 seconds for a week-long window; under 30 seconds for a large historical reconstruction
- **cost:** moderate storage and indexing cost; low model cost because summaries are generated from typed events
- **security:** Historical snapshots may contain sensitive content. Default to metadata, hashes, classifications, and source IDs; reveal snippets only in the local dashboard after an explicit request. Preserve corrections as later events rather than rewriting history. Retention and deletion requests must visibly mark gaps instead of fabricating continuity.
- **missing:** append-only, timestamped decision/evidence/effect events from every surface with trustworthy clock provenance; historical projections that distinguish observed-at, recorded-at, and effective-at times; stable joins among relay, Mac, browser, pipeline, memory, and owner-approval records; a local timeline query and redacted export route with explicit missing-data intervals


## What it asked for

_Nothing._
