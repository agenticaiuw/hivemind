# Harness derivation — faculty-judgement — round 214

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me a morning brief only when it is trustworthy; tell me exactly what you could not read, what is stale, and whether I can safely rely on it.”"
- **useful because:** The current system can confidently say “calendar clear” when EventKit is unauthorized, and it has duplicate daily briefs. This turns a brief into an honest decision: speak only supported facts, name unknowns, and avoid waking the owner with a false all-clear. It is the single most useful behavior this system could add because it protects every other proactive feature from silently inventing certainty.
- **path:** relay → mac → pendant → dashboard
- **model tier:** Cheap deterministic checks first (reconcile_personal_state, cross_surface_preflight, routine/job receipts, delivery ACKs); use the realtime model only to phrase the final one-sentence result and explain a conflict.
- **latency:** Under 2 seconds for checks; under 5 seconds including phrasing. If a source exceeds its budget, report it as unavailable rather than waiting indefinitely.
- **cost:** Usually <$0.01: mostly local/relay reads; one short realtime utterance only when the owner asks for spoken detail.
- **security:** Do not speak calendar/mail contents when the owner has not allowed notification content aloud. Include source IDs and freshness, but redact sensitive snippets. Never treat empty EventKit results as evidence of an empty calendar. Require explicit policy values for quiet hours and spoken-content classes.
- **missing:** A single brief-integrity orchestrator that runs the existing reconciliation and preflight checks before briefing generation; A fix in /notifications and /day-plan to propagate unreadable EventKit state instead of “nothing waiting”; Routine deduplication/coalescing for the two 07:00 briefs and delivery-aware suppression; An owner-set policy object for what may be spoken, rather than a hidden default

### "“What did I miss while I was away, and what still needs me?”"
- **useful because:** Today a completed relay job, a queued browser result, an unheard briefing, and audio that never reached playback are different records with no owner-facing distinction. The answer should separate delivered-and-heard, delivered-but-unheard, blocked, expired, and never attempted, then rank only the items that still require the owner. This prevents both repeated nagging and the dangerous assumption that a generated answer was actually received.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic event folding and deduplication; a cheap model summarizes only the small set of unresolved items. Realtime is reserved for a spoken follow-up on one selected item.
- **latency:** A catch-up query in 2 seconds from durable receipts and ACKs; spoken summary in 4 seconds. Offline pendant events reconcile on reconnect without replaying duplicates.
- **cost:** <$0.01 per catch-up query; one short model call only when more than three unresolved items need grouping.
- **security:** Show item titles and provenance without raw private content by default. Treat a playback_started ACK as not necessarily heard to completion. Do not infer owner dismissal from missing ACK. Preserve idempotency and require confirmation before turning a missed item into an external action.
- **missing:** A durable cross-surface delivery ledger joining relay job, Mac job, browser command, artifact, and pendant event IDs; A fold/reconciliation endpoint that distinguishes generated, downloaded, started, finished, interrupted, expired, and unknown; A durable event join for relay-job-id to Mac-job-id (currently only telemetry metadata); Owner-facing policy for how long an unheard item remains actionable

### "“Give me the top world and US headlines from the last 12 hours in three short spoken sentences, and let me ask which source supports each sentence.”"
- **useful because:** This is the owner's most repeated unmet request. A useful version must enforce a 12-hour cutoff, diversify sources, detect copied wire stories, retain citations, and produce a playable artifact instead of merely generating text. The owner can then interrupt one headline and ask for its evidence or a correction without replaying the whole brief.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** Use web_search/read_web_page and deterministic timestamp/source clustering first; use a cheap synthesis model for three sentences; use realtime only for spoken follow-up or a correction request.
- **latency:** Initial answer under 12 seconds, with a progressive “sources found” status if browsing is slow. Follow-up evidence under 4 seconds when the source capsule is already stored.
- **cost:** Roughly $0.02–$0.08 depending on search/read calls and synthesis; follow-ups <$0.01 from cached evidence.
- **security:** Cite URLs and publication timestamps; never present an undated or older-than-cutoff story as current. Preserve the raw source only under the existing evidence retention policy, redact secrets and personal data before TTS, and do not let a headline trigger external action without confirmation.
- **missing:** A freshness-and-source-quorum planner that rejects stale, duplicate, or single-source stories; A durable citation bundle linking each spoken sentence to evidence capsules and the exact cutoff time; A research-to-audio handoff that reports artifact download/playback status, not just synthesis completion; A correction path that supersedes a spoken item and marks the prior claim as corrected

### "“Forget everything you know about this person, topic, or source—and prove what was erased and what, if anything, could not be erased.”"
- **useful because:** Today deletion is store-local: captures can survive in the context graph, evidence revocation does not reach derived facts, and there is no global forget operation. The owner cannot honestly withdraw a piece of their life from the system. This capability makes forgetting an auditable outcome rather than a reassuring button: identify every copy and derivative, tombstone or delete it across Mac, relay, browser provenance, audio, and fleet memory, then return residuals with reasons and expiry.
- **path:** dashboard → mac → relay → browser → pendant
- **model tier:** Deterministic subject/source graph traversal and deletion first; use a cheap model only to resolve ambiguous natural-language references (“the United trip”) into candidate IDs, always showing candidates before mutation.
- **latency:** Preview in under 3 seconds for local stores and under 8 seconds including relay; apply asynchronously with progress and a final residual report. No spoken content should be generated during deletion.
- **cost:** Usually <$0.01 for traversal and writes; model cost only for ambiguous reference resolution.
- **security:** Destructive and potentially irreversible: require explicit confirmation listing stores and matched records, use tombstones and idempotent request IDs, never expose deleted secret contents in the report, and retain only minimal deletion receipts. Relay deletion must be authenticated and fail closed if its durable store is unavailable.
- **missing:** A global forget orchestrator with a typed subject/source scope and dry-run preview; Provenance links from derived memory facts to evidence capsules and source captures; Deletion/retraction propagation to context graph, fleet memory, browser provenance, audio artifacts, and relay replicas; A residual scanner that verifies each store after mutation and reports unavailable surfaces; Owner-visible deletion receipts with retention that does not itself recreate the forgotten content


## Changes it proposed to its own stack

### `integration` — Make every proactive briefing pass through a strict evidence-state gate: EventKit empty-pair results become unreadable, not clear; duplicate routines are coalesced by semantic command plus schedule; each spoken item carries a durable evidence reference and a delivery state; the pendant's playback ACK can downgrade “completed” to “generated but unheard.” The gate returns one short owner-facing sentence and a dashboard drill-down rather than silently failing open.
- **owner gets:** The owner stops hearing confident lies such as “your calendar is clear” when access is denied, stops receiving duplicate morning jobs, and can tell whether a briefing was actually heard.
- effort: Medium: adapt briefingTriage/dayPlan readers, routine scheduler, job receipts, and the new pendant ACK ingestion; add integration tests for unauthorized EventKit, duplicate schedule, interrupted playback, and reconnect replay.  ·  risk: A conservative gate may withhold a useful brief when a source is temporarily unavailable. Recover by exposing the exact blocked source and allowing an explicit one-time “read what is available” request; never fall back to an invented all-clear.
- cost: Negligible recurring API cost; mostly local reads and storage. One short synthesis call only when the owner asks for a spoken explanation.  ·  latency: Adds roughly 100–500 ms for local checks; remote source timeouts are bounded and reported rather than delaying indefinitely.
- security: Improves privacy and truthfulness: source references are safe by default, sensitive content stays behind policy, and no raw calendar/mail text is sent to TTS without an allowed class.
- depends on: Implement the missing EventKit unreadable signal in /notifications and /day-plan; Persist relay↔Mac job correlation rather than telemetry-only localJobId; Wire record_pendant_delivery_event to the durable pipeline/job receipt path; Apply the owner's eventual spoken-content and quiet-hours policy


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities and one concrete integration change: an evidence-gated trustworthy morning brief, a delivery-aware “what did I miss?” catch-up answer, a fresh cited 12-hour world/US news brief with sentence-level follow-up, and a strict gate preventing unauthorized-calendar false all-clears, duplicate routines, and generated-but-unheard audio from being reported as complete. The owner’s repeated headline request is the clearest immediate product test.

**Biggest unknown:** I still need owner decisions, not more discovery: whether America/Chicago is the owner’s actual personal timezone or merely a sampled machine value (the authoritative routine zone is currently America/New_York), which notification-content classes may be spoken aloud, and the desired quiet-hour/emergency policy. Implementation still needs durable relay↔Mac job correlation, the EventKit unreadable state propagated through notifications/day-plan, and wiring pendant delivery ACKs into receipts. I did not request denied permissions again.

