# Harness derivation — faculty-judgement — round 160

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If my pendant disconnects or enters privacy mode, stop all external actions immediately, tell me what was held, and let me safely resume only after the pendant is back."
- **useful because:** A dropped USB/LTE link currently looks like an ordinary transport failure; a Mac or relay job can remain in progress while the owner believes the physical control is present. This makes the worn device a real safety boundary across the Mac, browser, and relay.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic link-state and policy evaluation; use the expensive realtime model only to summarize the held actions when the owner asks.
- **latency:** Under 250 ms from authenticated disconnect/privacy event to local cancellation of reversible work; no model call on the stop path. Resume summary in under 3 seconds.
- **cost:** Near-zero model cost on stop/resume gating; roughly $0.005–$0.02 only when generating a concise held-work summary.
- **security:** Fail closed on missing heartbeat, stale session, invalid device event, or ambiguous ownership. Do not cancel irreversible work after submission; mark it as needing review. Do not put page contents or credentials in the pendant envelope. Require explicit physical resume, not voice alone.
- **missing:** Authenticated pendant link-state/privacy events consumed by the Mac bridge; A Mac-side supervisor that cancels or quarantines in-flight reversible jobs on that event; Relay job leases/requeue semantics and a durable relay↔Mac job mapping; A resume endpoint that presents held jobs through autonomy_policy_evaluate and revalidate_pending_plan

### "When I say “that’s wrong” during a spoken brief, bind my correction to the exact item and source, retract the bad claim, and remember the corrected version without making me repeat the URL or title."
- **useful because:** The system can now explain provenance, but explanation alone leaves the owner doing the hardest work: identifying and repairing a wrong claim. A physical/audio cursor plus source-linked correction would turn trust failures into durable learning across browser, Mac, relay, and future briefs.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime model only for resolving the owner's correction against the active item and drafting a normalized claim; deterministic provenance/revocation, sensitivity, and policy checks must remain local/server-side.
- **latency:** Pause and acknowledge within 300 ms; produce a reviewable correction in under 2 seconds; never mutate memory or retract evidence until the owner confirms if ambiguity is above the policy threshold.
- **cost:** About $0.01–$0.04 per correction, dominated by transcript/item disambiguation; deterministic evidence and memory writes are negligible.
- **security:** Carry only item IDs, cursor tokens, and source IDs to the pendant. A correction must not silently overwrite a sensitive fact or trigger an external action. Show the evidence chain and exact policy rule before a mutation; use conservative redaction for spoken acknowledgement.
- **missing:** A correction operation and durable claim record that links capsuleId/evidence to derived facts; A real writer for fleet memory and a revocation cascade from evidence to facts/context graph; A spoken correction-confirmation path that distinguishes “draft correction” from “apply correction”; Stable correlation between relay job, Mac job, browser command, and active audio item

### "When I reconnect after being away, give me one short, source-cited “what changed while I was gone” briefing: only items not actually delivered or played, grouped by what needs my decision, and let me defer an item without losing my place."
- **useful because:** A queued job, generated artifact, and spoken sentence are currently easy to confuse. Delivery ACKs make it possible to distinguish created, downloaded, started, finished, and never heard, so the owner gets a true return-from-absence briefing instead of duplicated news or false completion.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Cheaper background model to cluster and compress already-recorded receipts/evidence; realtime model only for the owner's follow-up question or interruption.
- **latency:** On reconnect, deterministic candidate selection under 500 ms; spoken digest under 5 seconds and no more than three items. Deferring or resuming an item must be immediate and idempotent.
- **cost:** Roughly $0.01–$0.05 per reconnect digest depending on item count; most work is deterministic filtering, deduplication, and receipt joins.
- **security:** Never infer that downloaded means heard. Require authenticated device session and monotonic event IDs; suppress expired/private content unless policy permits it. Keep citations as opaque source IDs on the pendant and use explain_action_provenance for detail. Do not duplicate an item after offline replay or a repeated ACK.
- **missing:** A durable relay↔Mac↔browser correlation key and delivery-state join; A catch-up projection that consumes record_pendant_delivery_event and existing job/pipeline receipts; Reconnect-triggered scheduler and a durable per-item seen/deferred state; A repair for relay jobs stranded in processing when the Mac disappears

### "After you do something important, tell me whether it actually changed the outside world—not merely whether the job completed—and show me the smallest evidence that proves or disproves it."
- **useful because:** A successful receipt currently proves server acceptance or local execution, not that a calendar entry exists, a browser setting changed, a file has the intended contents, or an external page accepted the action. The owner needs outcome truth rather than optimistic completion language.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Deterministic read-back and diffing first; use a cheaper background model only to summarize conflicting evidence. Realtime is reserved for explaining the result aloud.
- **latency:** Verification within 5 seconds for local files, Mac state, and browser state; up to 30 seconds for a remote page. Never claim success before verification or explicitly label it unverified.
- **cost:** Usually negligible; $0.005–$0.03 when a model must reconcile multiple read-backs. The dominant cost is remote/browser latency, not inference.
- **security:** Verification must use least-privilege read scopes and never expose secrets in spoken output. A failed read-back must not retry a potentially destructive action automatically. Preserve before/after hashes and source provenance, with owner confirmation required before any compensating mutation.
- **missing:** Typed postcondition declarations for each action class; A read-back executor that compares expected state to observed state across Mac and browser; A durable outcome record separate from execution receipts; Action-specific idempotency and compensation rules for ambiguous remote results

### "Never tell me that my calendar, inbox, or day is clear unless the system has proved that each source was readable; if a source is unavailable, say exactly what is unknown and automatically put a bounded recheck on my attention queue."
- **useful because:** Today an unauthorised EventKit read can look exactly like an empty calendar, and some briefing routes confidently report 'nothing waiting.' This capability prevents a dangerous false-clear state and turns missing access into an actionable, expiring uncertainty rather than silent omission.
- **path:** mac-planner → relay-realtime → pendant → dashboard → browser-extension
- **model tier:** Deterministic permission/readability corroboration and source freshness checks; a cheap model may compress the uncertainty into one sentence. No expensive model is needed for the safety verdict.
- **latency:** Under 2 seconds for a source-availability verdict; the owner-facing sentence should be immediate. Rechecks should be scheduled without blocking the current brief.
- **cost:** Near-zero inference cost; at most $0.001–$0.01 for spoken compression when several sources disagree.
- **security:** Report only the minimum failure detail aloud—never permission paths, message contents, or private source names unless requested. A recheck must be read-only, bounded, deduplicated, and expire rather than repeatedly interrupting the owner.
- **missing:** A shared source-readability contract distinguishing empty, unreadable, stale, and fresh-empty; Fixes to notificationTriage and dayPlan so unauthorised EventKit emptiness cannot become 'all clear'; A scheduler that can enqueue a recheck into the existing attention arbiter; An owner-visible uncertainty and freshness receipt

### "When an important source contradicts another, give me a one-sentence conflict and the two concrete facts behind it, then let me choose which interpretation governs future actions without rewriting the original evidence."
- **useful because:** The system currently has many independent readers and receipts but no owner-facing distinction between source disagreement, stale data, and model error. This would let the owner resolve ambiguity once while preserving both observations and making later automation predictable.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Deterministic conflict detection over normalized typed observations; realtime model only translates a confirmed conflict into a concise spoken explanation. Never let the model silently choose a winner.
- **latency:** Detect conflicts during source reads in under 1 second; speak the conflict in one short sentence and defer the choice if the owner is busy. Apply a selected interpretation atomically after confirmation.
- **cost:** Near-zero for detection; approximately $0.005–$0.02 for natural-language compression of a complex conflict.
- **security:** Keep original evidence immutable and source-linked. A chosen interpretation must be scoped, expiring where appropriate, and never treated as proof that the losing source was false. Sensitive conflicts should be dashboard-only unless the owner explicitly requests spoken detail.
- **missing:** A normalized observation schema with freshness, confidence, and source identity; A durable owner resolution record distinct from raw evidence and memory facts; Conflict-aware policy evaluation that requires confirmation before external actions; Cross-surface writers so the resolution reaches relay, Mac, browser, and future briefings


## What it asked for

_Nothing._
