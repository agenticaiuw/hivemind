# Harness derivation — faculty-judgement — round 231

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Don't just tell me a briefing completed—tell me whether it reached the pendant and was actually played, and recover it automatically if it wasn't."
- **useful because:** A completed relay or Mac job is not the same as the owner hearing it. This closes the only user-visible reliability gap: generated, downloaded, started, finished, or honestly pending, with no duplicate replay.
- **path:** relay → mac → pendant → dashboard
- **model tier:** Background model for reconciliation; deterministic delivery state machine for normal operation; realtime only for the spoken status.
- **latency:** Under 2 seconds for status; retry on reconnect without waking the owner unless policy marks the item urgent.
- **cost:** Usually <$0.01 per briefing; dominated by one background reconciliation call, not audio generation. Retries reuse the existing artifact.
- **security:** Use opaque artifact IDs and authenticated device sessions; never put briefing text in ACKs. Require attention_arbitrate before retrying or interrupting. A checksum failure must quarantine the artifact rather than loop.
- **missing:** A durable relay-side delivery ledger keyed by artifactId and eventId; A job lease/requeue path so a relay job abandoned mid-delivery can recover; A policy that distinguishes downloaded from actually heard; LTE-registered pendant transport in production (USB is bench-only)

### "When I ask what changed, give me only changes I have not already heard—not a replay of the same mail, page, or research story."
- **useful because:** The current system can collect mail, calendar, reminders, page-watch reports, and research, but it has no owner-facing notion of 'heard'. A delivery-anchored delta brief reduces repetition and makes the pendant useful during a busy day.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** Cheap background model clusters and summarizes only new deltas; deterministic fingerprints and delivery ACKs decide novelty; realtime speaks the final short digest.
- **latency:** Build a delta set in under 10 seconds after a request or scheduled run; speaking starts within 2 seconds once the set is ready.
- **cost:** <$0.03 per run for clustering/summarization, with most work deterministic. Reuse existing page-watch and research artifacts rather than rereading pages.
- **security:** Persist hashes, source IDs, timestamps, and sensitivity—not raw quotes by default. Explain each item with provenance and let the owner revoke a source through explain_action_provenance. Never treat 'generated' as 'heard'; advance the baseline only on a pendant playback_started or explicit owner read.
- **missing:** A durable per-source novelty baseline linked to record_pendant_delivery_event; Stable story/entity fingerprints across mail, browser pages, and research; A writer for shared fleet memory or another cross-surface baseline store; A safe fix for unauthorised EventKit empty reads before calendar deltas can be trusted

### "If a routine or delegated task fails halfway through, recover it without doing the successful steps twice, and tell me exactly what remains."
- **useful because:** Today an in-flight relay job can remain processing forever when the Mac dies, while browser actions have separate IDs and receipts. The owner should get recovery rather than a silent 24-hour limbo or duplicate external action.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic lease/recovery and idempotency checks first; a cheap background model classifies the remaining work; realtime only states the result.
- **latency:** Detect an orphan within 1 minute of lease expiry; provide a recovery status within 3 seconds of asking; never auto-submit an irreversible step.
- **cost:** <$0.01 for normal recovery; model cost only when a failed workflow needs semantic classification. Existing receipts and action IDs avoid replaying completed steps.
- **security:** Fail closed on uncertain completion. Revalidate current state before any retry, run autonomy_policy_evaluate, and require physical_transaction_approval_latch for irreversible actions. Surface the exact receipt/evidence chain.
- **missing:** lease_until and requeue sweep for relay_jobs; A durable relay-job to Mac-job correlation key (not telemetry-only); A recovery manifest that records completed step IDs and remaining steps; A single cross-surface status view for relay, Mac, and browser

### "Before you play a queued briefing, check that its sources are still fresh; if anything important changed while it waited, rebuild it instead of making me hear stale advice."
- **useful because:** A briefing can be generated successfully and delivered successfully yet be wrong by the time the owner hears it—especially news, prices, travel, or a page-watch alert. Freshness should be checked at the last responsible moment, not inferred from a job receipt.
- **path:** relay → browser → mac → pendant → dashboard
- **model tier:** Deterministic age/version checks and source fingerprints first; background model regenerates only the invalidated items; realtime speaks the resulting short brief.
- **latency:** A freshness check under 500 ms for cached metadata; regeneration may take seconds but must not start playback until it passes or is explicitly marked stale.
- **cost:** <$0.02 typical, dominated by regeneration only when a source changed. Stable items reuse their existing audio segments.
- **security:** Check only source IDs, timestamps, ETags/content hashes, and sensitivity labels in the gate; do not send raw private content to the relay merely to validate freshness. A source revocation must invalidate dependent artifacts.
- **missing:** A source-version/freshness manifest attached to each briefing item and audio artifact; A dependency link from generated item to evidence capsule or browser/mail source so revocation can invalidate it; An explicit owner policy for acceptable staleness by category (news, reminders, research, etc.); A safe partial-regeneration path that preserves item IDs and playback position

### "When I press the pendant's bookmark button as I leave my desk, give me a private, spoken 'leave-behind' checklist: unfinished work, unsaved drafts, pending browser actions, and the one thing I most likely need when I return."
- **useful because:** The current moment marker records that a moment happened, but it does not preserve the owner's working state or turn departure into a useful handoff. This would prevent the daily loss of context between desk, commute, and return without requiring the owner to narrate a checklist.
- **path:** pendant → mac → browser → relay → dashboard
- **model tier:** Cheap deterministic collectors for jobs, action receipts, drafts, browser tabs, and reminders; a background model ranks the likely return-critical items; realtime only speaks the compact checklist.
- **latency:** Capture the marker immediately offline; assemble the checklist within 5 seconds when the Mac is reachable; deliver it to the pendant only after the owner requests or authorizes playback.
- **cost:** Usually <$0.01: local collection and ranking dominate, with one small background synthesis call. No audio recording is needed.
- **security:** The pendant receives only the rendered checklist, never browser secrets, page bodies, credentials, or full draft contents. Treat open tabs and drafts as private; require explicit confirmation before including sensitive titles. Store a short-lived state snapshot with a visible expiry and a delete action.
- **missing:** A departure-marker event hook that triggers a Mac/browser snapshot rather than only storing a timestamp; Read-only collectors for unsaved editor state, draft state, pending browser commands, and foreground task context; A durable, source-linked leave-behind snapshot with expiry and deletion propagation; A return trigger or owner-invoked resume route that compares the snapshot against current state and reports only what remains

### "When two sources disagree about something that affects me, don't silently pick one—tell me what conflicts, which source is more trustworthy for this question, and what would change the decision."
- **useful because:** Real life contains contradictory calendar/mail/browser/research state. Today the system can collect sources and can explain provenance, but it cannot present an explicit disagreement with a bounded recommendation; silent averaging is dangerous for travel, deadlines, prices, and permissions.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** Deterministic normalization and contradiction detection first; a background reasoning model evaluates source authority and uncertainty; realtime speaks only the conflict and recommended next check.
- **latency:** Under 3 seconds for cached evidence; under 15 seconds when a fresh public source read is required. Never block an unrelated request on conflict resolution.
- **cost:** <$0.04 for a typical conflict, dominated by a small evidence-comparison call; hashes and structured fields avoid resending full documents.
- **security:** Keep private source content on the Mac where possible and send only redacted excerpts or digests. Every conclusion must carry source IDs, timestamps, authority rationale, and an uncertainty label. Never convert a conflict into an external action without owner confirmation.
- **missing:** A typed conflict record with field-level competing values and source timestamps; An owner-editable authority policy by domain (for example, calendar versus email versus a logged-in site); A durable comparison run linked to evidence capsules and revocation; A spoken rendering that names uncertainty without exposing private source text

### "Let me correct a wrong statement while I'm hearing it—'that's not my deadline'—and have the system retract that claim everywhere, stop repeating it, and show me what sources still disagree."
- **useful because:** A spoken correction is currently just another utterance. The stale claim can remain in facts, the context graph, a briefing queue, and derived audio. A single correction should repair the owner's future experience, not merely acknowledge the sentence.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic claim/source graph update and retraction first; a background model resolves paraphrases and finds affected derived items; realtime confirms the correction without repeating sensitive content.
- **latency:** Acknowledge in under 1 second; retract local queued audio immediately; propagate to Mac/relay/browser stores within 10 seconds when connected.
- **cost:** <$0.02 per correction; most work is indexed lookup and tombstoning, with model use only for ambiguous references.
- **security:** Require the owner to identify or confirm the target claim when ambiguity exists. Preserve a minimal audit tombstone, not the corrected sensitive value. Do not alter external calendars, mail, or sites automatically; external mutations require the existing policy and physical confirmation.
- **missing:** A stable claim ID carried from evidence through facts, graph entities, briefing items, and audio artifacts; A cross-store retraction cascade, including relay fleet memory and queued audio; A pendant barge-in binding that associates the correction with the currently spoken item; A reviewable conflict view showing surviving source evidence after retraction


## What it asked for

_Nothing._
## Its own summary

Produced four owner-facing capabilities: end-to-end heard-vs-generated delivery, heard-anchored change-only briefs, orphaned delegated-task recovery without duplicate actions, and freshness validation before queued audio plays. The recorder accepted all four; the first and third are connective reliability work over existing primitives, while the fourth adds source dependency/version invalidation.

**Biggest unknown:** The owner still has not set the values that determine behavior: acceptable staleness by briefing category, what counts as urgent, quiet hours, and whether notification content may be spoken. Technically, production LTE registration and durable cross-surface writers/leases remain missing; USB is bench-only.

