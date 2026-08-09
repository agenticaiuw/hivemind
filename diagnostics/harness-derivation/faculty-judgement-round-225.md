# Harness derivation — faculty-judgement — round 225

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Tell me which briefings I actually heard, and give me only the important parts I missed."
- **useful because:** A generated briefing is not the same as a delivered briefing. The owner currently cannot distinguish 'the Mac completed it' from 'the pendant played it'; this prevents duplicate replays while making missed urgent information recoverable.
- **path:** relay → mac-planner → pendant
- **model tier:** Use the cheap background model to reconcile delivery receipts and rank missed items; reserve realtime for the short spoken catch-up.
- **latency:** Under 2 seconds for a status answer; under 8 seconds to prepare a compact catch-up. Playback itself remains normal audio latency.
- **cost:** About $0.002-$0.01 per catch-up, dominated by summarizing missed items; status-only queries should be near-zero model cost.
- **security:** Speak only item titles and redacted summaries by default; require the existing physical approval latch for sensitive replay. Keep opaque artifact IDs and delivery timestamps, not raw audio, in the receipt path.
- **missing:** Bind each briefing item to an opaque artifactId and stable item_id at synthesis time.; Feed record_pendant_delivery_event results into catchupDigest and briefing review.; Persist a durable heard/missed projection with deduplication across offline ACK replay.; Add an owner-facing 'heard/missed' route and a compact replay planner.

### "Put me back into the work I was doing before I got interrupted, without changing anything until I say so."
- **useful because:** The system can act across Mac, browser, relay, and pendant, but an interruption currently loses the owner's situational context. A read-only spoken handoff would save the owner from reconstructing the active project, browser session, pending job, and last brief item every time.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Use a cheap deterministic assembler for the state card; invoke the realtime model only when it must turn conflicting state into one short explanation.
- **latency:** 1-3 seconds for a read-only handoff card; any optional app reopening is a separate, explicitly confirmed step.
- **cost:** Near-zero for assembly; at most $0.001-$0.005 when conflict explanation needs a model.
- **security:** Return names, IDs, and small redacted titles—not page bodies, form fields, or secrets. Revalidate any stale plan before offering an action, and never reopen or mutate an app automatically.
- **missing:** A durable cross-surface handoff record linking relay job, Mac job, browser session, active project, and audio cursor.; A read-only endpoint that assembles current state with per-field freshness and provenance.; An explicit 'show only' versus 'reopen after confirmation' policy decision.; A small pendant trigger and spoken formatter that does not require the owner to remember an item ID.

### "Make my morning brief happen once, at the right time, and tell me exactly what was merged or disabled."
- **useful because:** The owner currently has overlapping daily routines at 07:00 and 07:30 that can produce duplicate audio and conflicting completion records. A single reviewable merge would turn a noisy automation collection into one dependable morning ritual without silently deleting anything.
- **path:** relay → mac-planner → pendant
- **model tier:** Use deterministic reconciliation for duplicate schedules and item deduplication; use the realtime model only to explain the proposed merge in one sentence.
- **latency:** Under 3 seconds to inspect and propose; applying the merge should complete within 10 seconds and return a receipt.
- **cost:** Near-zero model cost for schedule matching; at most $0.001 for the spoken explanation.
- **security:** Default to prepare-only. Require explicit owner confirmation before disabling or changing any routine. Preserve an undo record, and do not speak private calendar or mail content while describing the merge.
- **missing:** A routine-specific merge planner that groups overlapping commands by time, intent, and output channel.; An explicit prepare/approve flow for routine edits with an undo receipt.; A single dedupe key shared by routine run, briefing item, audio artifact, and pendant delivery ACK.; A post-merge verification that exactly one routine fired and whether its audio was heard.

### "Find the thing I was referring to yesterday—the file, page, or note—and show me why you think it is the right one before opening it."
- **useful because:** People remember intent and fragments, not filenames or URLs. Today the Mac, browser, capture store, and job history are separate; the owner must manually search each one and cannot see why a candidate was chosen. A provenance-ranked finder would turn a vague spoken reference into a reviewable shortlist without making changes.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Use deterministic lexical/time/project filters first; use a cheap model only to rank ambiguous candidates and explain the match. Realtime is needed only for the final spoken shortlist.
- **latency:** Return a first shortlist in 3 seconds from local stores; allow up to 10 seconds for browser reads or broad search.
- **cost:** Usually near-zero; $0.002-$0.01 when model ranking or page extraction is needed.
- **security:** Search metadata and redacted snippets by default; never read password fields or private page bodies until the owner selects a candidate. Opening a candidate is read-only and should remain separate from any mutation.
- **missing:** One query endpoint joining captures, memory facts, active project, jobs, browser sessions, and file metadata.; A durable provenance link for each candidate (source, timestamp, project, and matching evidence) with secret-safe snippets.; A pendant-friendly disambiguation response that can refer to candidates by number without exposing private content aloud.; A browser/file read adapter that returns bounded metadata consistently.

### "Which of my automations have quietly failed or gone unheard this week, and what should I fix first?"
- **useful because:** The owner sees individual completion records, but not the difference between a routine that ran, one that produced no useful result, and one whose audio was never heard. A weekly reliability coach would expose silent failure before the owner builds trust around a broken habit.
- **path:** relay → mac-planner → pendant
- **model tier:** Use deterministic aggregation of routine, job, receipt, and delivery events; use a cheap background model only to rank causes and phrase the top three repairs.
- **latency:** Under 5 seconds for a seven-day report; repairs remain reviewable and asynchronous.
- **cost:** Near-zero for aggregation; approximately $0.002-$0.01 when cause clustering needs a model.
- **security:** Keep the report at routine names, error classes, timestamps, and delivery states. Do not include mail, calendar contents, or audio text unless explicitly requested.
- **missing:** A durable join from routine execution to job, artifact, and pendant delivery events.; A classifier separating generation failure, source-unreadable result, link failure, and unheard audio.; A trend store retaining only bounded reliability statistics rather than raw content.; A reviewable repair proposal that can change one routine or retry policy with undo.

### "Forget this memory everywhere, then show me exactly what was erased and what could only be revoked or left as a non-readable trace."
- **useful because:** Today deletion is store-specific: a capture can survive in the context graph, derived facts can survive evidence revocation, and relay memory has no reliable tombstone writer. The owner needs a truthful erasure result, not a success response from one local file.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Use deterministic provenance traversal and deletion; use realtime only to explain residual traces in plain language after the operation.
- **latency:** Prepare an erasure plan in under 3 seconds; execute within 15 seconds when all surfaces are online, otherwise return a durable pending/revocation state.
- **cost:** Near-zero for traversal and deletion; under $0.005 for an explanation if residuals are ambiguous.
- **security:** Require explicit physical approval for destructive erasure. Never speak the memory value aloud; identify it by a redacted label and source. Preserve only non-content audit hashes and deletion receipts.
- **missing:** A shared provenance graph linking captures, facts, context-graph entities, browser claims, capsules, fleet events, and audio artifacts.; A fan-out erasure/retraction transaction with idempotency and per-store results.; A durable tombstone protocol for relay and offline pendant replay.; An owner-facing receipt that distinguishes content erased, content revoked, and unavoidable metadata retained.

### "Before I depend on the pendant today, run a private end-to-end canary and tell me whether speaking, delivery, playback, and cancellation all work—without sending or saving any personal content."
- **useful because:** The owner currently learns that a link, audio, or cancellation path is broken only during a real conversation. A content-free canary would test the complete chain and distinguish relay, Mac, radio, codec, playback, and stop failures before they matter.
- **path:** relay → mac-planner → pendant
- **model tier:** Use deterministic synthetic payloads and device telemetry; use realtime only to summarize a failed component in one sentence.
- **latency:** Complete in 10 seconds when the pendant is reachable; if offline, return a precise unavailable stage rather than waiting indefinitely.
- **cost:** Negligible model cost; small network and audio transport cost for one synthetic artifact.
- **security:** Use a fixed synthetic phrase or checksum, never microphone input or account data. Mark all canary artifacts non-retainable and exclude them from briefing history and memory.
- **missing:** A signed synthetic canary artifact type that cannot be mistaken for owner audio.; A test handshake covering relay acceptance, Mac synthesis, download, playback start/finish, and universal-stop cancellation.; A bounded diagnostics result with per-stage latency and failure reason.; A scheduler or owner-triggered route that runs only on explicit request and never interrupts an active conversation.


## Changes it proposed to its own stack

### `integration` — Make every scheduled or on-demand briefing pass through a truthful source-readiness gate: distinguish an empty calendar from an unreadable calendar, attach source status and freshness to each item, and refuse to say 'clear' when EventKit returned an unauthorised empty result. If a source is unavailable, speak one short uncertainty sentence and continue with the sources that were actually read; record the decision and the exact failed source for later repair.
- **owner gets:** The owner will stop receiving confident all-clear mornings when Calendar or Reminders access silently failed. They get a useful partial brief plus an actionable explanation instead of false reassurance.
- effort: Medium: reuse briefingTriage/meetingPrep corroboration, add a source-readiness object to briefing output, and route routine briefings through it; then add regression tests for unauthorized-empty and genuine-empty cases.  ·  risk: A conservative gate may occasionally mention an unavailable source when the day is genuinely empty. Recovery is a clearly labeled retry after permission/readability is restored; no calendar mutation occurs.
- cost: Negligible API cost; one cheap local read-status pass and fewer unnecessary model retries.  ·  latency: Adds roughly the existing EventKit probe/read latency; no extra model round trip for normal cases.
- security: Improves privacy by preventing unreadable private data from being inferred as absent; source errors and titles should still pass through existing redaction before speech.
- depends on: briefingTriage.js and meetingPrep.js empty-pair corroboration; GET /briefing/latest; GET /notifications; GET /day-plan; reconcile_personal_state; cross_surface_preflight

### `hardware` — Add a small secure monotonic event counter and tamper-evident status element to the next pendant revision, exposed to the relay as part of every physical interaction and privacy/approval state transition. The counter must survive power loss and the status element must make 'capturing', 'playing', 'latched', and 'awaiting approval' distinguishable without relying on the single shared LED timing language.
- **owner gets:** The owner would be able to trust that a physical press or privacy state was neither replayed nor silently lost, and could tell the pendant's security state at a glance even when the Mac and relay are unreachable.
- effort: High: hardware revision plus secure nonvolatile counter integration, firmware protocol changes, relay verification, and usability testing in daylight and at night.  ·  risk: A failed counter or indicator could block legitimate interactions. Fail closed for approvals and privacy transitions, but retain a recovery path through a deliberate local reset that does not erase the audit epoch.
- cost: Roughly a few dollars in components and board-layout cost; negligible steady-state power, with occasional nonvolatile writes requiring wear-leveling.  ·  latency: Adds only a few milliseconds to local state transitions and negligible radio payload overhead.
- security: Strengthens replay resistance and makes security state observable locally. It does not replace the existing physical approval or privacy-latch semantics.
- depends on: A defined signed event-envelope protocol; Relay-side monotonic-counter validation and rollback handling; A hardware design with an additional indicator channel and protected nonvolatile storage


## What it asked for

_Nothing._
