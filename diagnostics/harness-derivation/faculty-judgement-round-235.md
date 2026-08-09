# Harness derivation — faculty-judgement — round 235

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me a weekly autonomy report: which things did you do, ask me about, or undo unnecessarily, and what one policy change would make you less annoying?”"
- **useful because:** The owner gets a measurable way to improve the system instead of repeatedly correcting the same behavior. It distinguishes successful automation from hesitation, owner rejection, undo, stale-plan failure, and duplicate notification, then proposes one reversible policy edit with receipts behind it.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Background model for aggregation and a cheap deterministic classifier for outcomes; realtime only to answer a follow-up question on the pendant.
- **latency:** Under 10 seconds for a weekly report; under 1 second to read the supporting receipt when asked.
- **cost:** Roughly $0.03–$0.10 per weekly report; dominated by summarizing receipts, not device work.
- **security:** Use metadata and redacted summaries by default, never replay page bodies or mail content. A policy change is draft-only and must pass autonomy_policy_evaluate and explicit owner approval. The report must link every claim to receipt IDs and show sample size.
- **missing:** A durable owner feedback record for reject/accept/undo/correction outcomes; A query that joins relay job IDs to Mac action IDs (currently only telemetry localJobId exists); A dashboard view for the proposed policy diff

### "“Did I actually hear today's brief? If not, give me the shortest missing item when I press the pendant—don't replay what I finished.”"
- **useful because:** A generated briefing is not useful merely because the server says it completed. The owner gets an honest, item-level delivery guarantee that survives dropped links, retries, duplicate ACKs, and interrupted playback, with one-button recovery rather than a full replay.
- **path:** relay → pendant → mac → dashboard
- **model tier:** Deterministic delivery reconciler and item cursor; background model only creates a short recovery sentence when several items are missing.
- **latency:** Delivery state under 500 ms after an ACK reaches the relay; recovery audio prepared within 5 seconds.
- **cost:** Usually under $0.01 per recovery; audio synthesis dominates and only runs for missing items.
- **security:** ACKs carry opaque artifact IDs, byte/checksum evidence, monotonic device sequence, and playback position—not transcript text. Deduplicate by eventId and reject events from unknown device sessions. Never infer that downloaded means heard.
- **missing:** Wire pendant audio_delivery_ack_queue into the relay ingestion path and job/briefing item records; A durable item-to-artifact manifest and idempotent cursor service; A spoken/UI status surface that distinguishes generated, downloaded, started, finished, and interrupted

### "“Before my next meeting, make me a private 60-second rehearsal: what is the decision, what do I owe, and quiz me once; use the browser only for the documents already open.”"
- **useful because:** The system turns scattered calendar context, authenticated documents, and prior commitments into preparation the owner can use hands-free. It asks one focused question instead of dumping a briefing, and it can defer safely when the browser is offline or the meeting data is unreadable.
- **path:** mac → browser → relay → pendant
- **model tier:** Background model assembles and cites the rehearsal; realtime model only conducts the one-question spoken quiz.
- **latency:** Prepare in 15–30 seconds; spoken turn latency under 1.5 seconds.
- **cost:** About $0.05–$0.20 per rehearsal, dominated by document extraction and synthesis; no cost when required surfaces are unavailable.
- **security:** Read-only browser actions limited to existing tabs and an explicit source list; no page body is persisted in the rehearsal by default. Attendee/client names are private and must not be spoken unless the owner has explicitly allowed content aloud. Never send mail or edit calendar. Show source locators and permit revocation.
- **missing:** A meeting-triggered scheduler or owner-invoked meeting lookup that provides the relevant event; A bounded authenticated-document bundle API over browser_read_page with source IDs; A private-output policy that can route sensitive material to the pendant only after a press, rather than unconditional TTS

### "“If I say yes to this, what does it force me to miss, delay, or break? Give me the best alternative before I commit.”"
- **useful because:** The owner gets consequences, not merely a task ranking: accepting a meeting, purchase, trip, or browser action is evaluated against existing time, obligations, routines, and reversible options before commitment. This is a counterfactual decision service, not another briefing.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic constraint and time-impact engine first; a background model explains tradeoffs in plain language; realtime only handles the owner's follow-up choice.
- **latency:** Initial impact map in 3 seconds for local data; under 15 seconds when authenticated browser research is required.
- **cost:** $0.02–$0.08 per analysis, mostly explanation and optional research.
- **security:** Read-only by default. Never accept, purchase, send, or reschedule without a separate physical approval. Show assumptions, stale sources, and confidence; do not infer obligations from private text without citing its source.
- **missing:** A typed counterfactual/constraint engine with time, obligation, and dependency inputs; A read surface for reminders/tasks and a trustworthy calendar permission result; A reversible alternative planner that can compare plans without executing them

### "“Test my personal fallback now: if the Mac, browser, or LTE disappears, what will still reach me, what will queue, and what will be lost? Then run the safest tabletop simulation without sending anything.”"
- **useful because:** The owner learns whether the system is dependable before an actual failure. It exercises the real pendant inbox, relay queues, browser reachability, Mac job recovery, and audio path in a no-side-effect simulation, exposing silent gaps such as orphaned jobs or unreadable briefings.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic fault-injection and capability matrix; background model writes the plain-language report. Realtime is unnecessary unless the owner asks a spoken follow-up.
- **latency:** Capability snapshot in 2 seconds; tabletop simulation and report within 30 seconds.
- **cost:** Under $0.05 per run; dominated by optional report synthesis and test audio.
- **security:** Use synthetic payloads only, never real mail, page text, credentials, or irreversible actions. Fault injection must be scoped to shadow queues and disposable artifacts, with an explicit owner confirmation before any live link is interrupted.
- **missing:** A cross-surface fault-injection harness with synthetic jobs and audio; A single degraded-mode contract describing queue, retry, expiry, and loss semantics for every surface; A dashboard timeline showing which synthetic events were observed by Mac, relay, browser, and pendant


## Changes it proposed to its own stack

### `memory` — Add a compact, provenance-linked outcome event whenever the owner accepts, rejects, corrects, cancels, or undoes an agent action; store only action class, policy version, surface, result, and receipt IDs, then project aggregate counts into the weekly autonomy report.
- **owner gets:** The system can finally learn from the owner's actual corrections instead of repeating the same annoying behavior, without retaining the private content of the task.
- effort: Medium: extend the existing action ledger/receipt path, add a durable event writer, and expose a read-only aggregate route.  ·  risk: A mistaken inference could bias future autonomy. Keep events advisory, require explicit policy approval for changes, and allow deletion by event ID; recover by rebuilding aggregates from receipts.
- cost: Negligible storage and model cost; weekly aggregation is background work.  ·  latency: No added latency to action execution if events append asynchronously.
- security: Metadata-only by default; redact targets and never store page/mail bodies. Provenance IDs remain local and revocable.
- depends on: A durable relay-job/Mac-job join; An owner-visible policy diff and approval path

### `integration` — Create one durable briefing manifest mapping each spoken item to an opaque audio artifact, evidence references, and delivery state; have the relay fold record_pendant_delivery_event into it and expose only missing-item state to the owner.
- **owner gets:** The pendant stops pretending a server-completed job was heard, and the owner can recover exactly what was missed after a link drop or interruption.
- effort: Medium-high: schema and idempotency work across relay, pipeline, and pendant ACK ingestion.  ·  risk: Out-of-order or replayed device events could mark an item incorrectly. Enforce authenticated device sessions, monotonic sequence checks, eventId deduplication, and an append-only audit trail.
- cost: Small D1/storage increase; audio generation cost falls because finished items are never regenerated.  ·  latency: Sub-second state updates after delivery ACK; no impact on normal playback.
- security: Opaque IDs only; no spoken content in ACKs. Respect privacy-panic revocation epochs.
- depends on: Wire audio_delivery_ack_queue firmware behavior to the live relay; A durable item/artifact manifest

### `interaction` — Add a press-to-start private rehearsal mode: the Mac assembles a time-bounded source bundle from the next calendar event and currently open browser tabs, the relay creates one cited 60-second audio item, and the pendant asks exactly one follow-up question before revealing any sensitive detail.
- **owner gets:** Meeting preparation becomes a useful hands-free conversation rather than another long briefing, while the owner retains a physical boundary before private names or document details are spoken.
- effort: High: meeting lookup, browser source bounding, source-linked synthesis, and a pendant state machine for one-question interaction.  ·  risk: Wrong event or stale tab context could mislead the owner. Require explicit event/source IDs, freshness checks, a preflight, and a visible draft before audio; never mutate external systems.
- cost: About $0.05–$0.20 per preparation, mostly synthesis and document extraction.  ·  latency: 15–30 seconds to prepare; conversational follow-up under 1.5 seconds.
- security: Sensitive content stays local until physical press; source snippets are redacted and expire. No mail/calendar writes.
- depends on: An event lookup surface with readable permission provenance; Bounded read-only browser extraction; A private spoken-content policy and pendant physical approval

### `context` — Build a content-independent provenance and deletion graph: every persisted derivative receives a source capsule/capture/audio/job edge, and a confirmed forget operation traverses those edges across Mac, browser, relay, and pendant, returning signed per-surface deletion acknowledgements.
- **owner gets:** When the owner deletes something, it would actually be gone everywhere the system copied or inferred it from, with an honest proof of which surfaces succeeded or remain offline.
- effort: Very high: add provenance edges to existing records, migrate stores, implement idempotent tombstone propagation, and handle offline acknowledgements.  ·  risk: Over-broad traversal could delete unrelated material. Require a preview, exact source scope, physical confirmation, per-edge authorization, and an undo window only for tombstones—not recovered content.
- cost: Moderate storage and engineering cost; negligible per-request inference cost.  ·  latency: Local preview is fast; remote completion may wait for disconnected browser, relay, or pendant surfaces.
- security: Strongly improves privacy, but deletion receipts and graph edges can themselves reveal relationships; retain only opaque IDs and sensitivity-minimized metadata.
- depends on: A durable cross-surface ID join; A universal privacy deletion policy; Relay and pendant acknowledgement handling


## What it asked for

_Nothing._
