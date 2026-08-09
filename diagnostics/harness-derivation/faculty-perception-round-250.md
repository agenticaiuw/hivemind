# Harness derivation — faculty-perception — round 250

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current live surfaces and permissions** — As of 2026-08-09T03:37Z, the Mac bridge and Safari extension are online; the Mac agent reports Accessibility and Screen Recording granted with requiredMissing=[] and ready=true. Safari has one active YouTube tab (tab 85). The relay is reachable and D1-backed. The relay device registry visible through the local agent's route table is not available at GET /v1/devices/status on localhost; its device listing currently shows nrf9160-pendant offline, so no live pendant playback can be asserted.
  - evidence: discover(devices) plus read_continuity_snapshot(include relay/pipeline), whose live /ops/snapshot body reports permissions.ready=true, browser online/tab 85, relay reachable/store d1; probe_http GET /v1/devices/status returned local-agent 404.

## Capabilities it proposed

### "“Show me the evidence chain behind that answer, and tell me what is observation versus inference.”"
- **useful because:** The owner currently receives browser text, routine summaries, and spoken answers without a durable, inspectable join between the source page, the captured region, the answer, and the action taken. This would expose the exact source URL/title, capture time and freshness, content hash, redaction status, capsule/provenance IDs, and explicitly mark any inference or stale/unverified link. It is the single most useful perception capability because it lets the owner trust or challenge the mind instead of trusting a fluent sentence.
- **path:** browser → mac-planner → relay → dashboard
- **model tier:** Use the cheap background model to assemble and summarize an already-recorded evidence graph; reserve realtime only for a short spoken pointer. No model is allowed to invent missing links; missing provenance is reported as unknown.
- **latency:** Under 2 seconds for an existing capsule; up to 5 seconds when the authenticated Safari page must be re-read and hashed.
- **cost:** Usually <$0.01 per invocation; dominated by one browser read or no model call at all, not by storage.
- **security:** Private Safari content must stay on the Mac; relay/public reads are untrusted and must be visibly separated. Never return redacted secrets or treat a hash as proof of truth. Require confirmation before exposing sensitive snippets to a spoken channel.
- **missing:** A relay read must return a stable request/capsule correlation ID and content hash, then the Mac must mint or link the existing evidence capsule.; Mount the existing browserProvenance routes and link each voice/routine answer to capsule IDs and claims; do not create a second evidence schema.; A read-only evidence-chain query that joins answer, browser provenance, capsule, pipeline/job receipt, and action ledger.

### "“Which things you remember about me are actually mine, which were inferred from this Mac, and which are now contradicted?”"
- **useful because:** The current context projection can present a machine-written preference as an owner preference; the known timezone row is a concrete example and is pinned, high-confidence, and repeatedly injected despite contradicting the Mac's authoritative zone. The owner needs a perception answer that separates owner intent from machine observation, surfaces contradictions and last-seen age, and offers the exact fact keys to review before any action relies on them.
- **path:** dashboard → mac-planner → relay
- **model tier:** Cheap deterministic projection and conflict scoring first; a background model may summarize the conflicts. Realtime should speak only the top one or two urgent warnings.
- **latency:** Under 500 ms from the memory projection and machine-context; no external read unless the owner asks to verify.
- **cost:** Near-zero model cost for the normal path; dominated by one local projection read.
- **security:** Do not speak secret facts or values merely because they are in memory. Preserve source.origin, confidence, expiry, use count, and last-used metadata. Changes to owner facts require explicit confirmation and should be auditable.
- **missing:** A provenance-aware memory projection endpoint that returns source.origin and conflict groups instead of flattening all preferences into the Owner block.; A deterministic contradiction policy: machine-origin facts cannot outrank an authoritative live machine observation, and stale machine facts should be labeled rather than silently used.; A review UI/action for the owner to confirm, retire, or correct one fact without the model rewriting it.

### "“Before you do that, give me a one-sentence reality check: which device will act, is it reachable now, what permission does it have, and what would make the result unknowable?”"
- **useful because:** The mind currently treats route availability, Mac permission readiness, browser heartbeat, relay reachability, and pendant playback as separate facts. A concise preflight would prevent the most damaging false confidence: sending an action to a stale Safari tab, claiming a Mac action succeeded without a receipt, or treating relay socket delivery as something the owner heard. It tells the owner whether to proceed, wait, or choose a safer path.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Deterministic policy over live liveness, permission, route, and receipt fields; no model needed except optional wording. Realtime only speaks the compact verdict.
- **latency:** Under 1 second for a normal action; hard timeout at 2 seconds, with each source labeled unavailable rather than guessed.
- **cost:** Near-zero API cost; a bounded multi-source read is the dominant work.
- **security:** Do not reveal bearer tokens or private tab data. Reachability is not authorization, authorization is not successful execution, and relay delivery is not playback. Destructive actions still require the existing confirmation policy.
- **missing:** A single typed preflight response joining device lease age, permission readiness, route authorization, browser tab/session affinity, and the exact receipt/ack stage expected for the action.; A freshness deadline per source and a refusal state when the expected acknowledgement has no emitter (especially pendant playback).; A route/action adapter so the preflight can name the actual executor and fallback without executing anything.

### "“Are my scheduled routines actually doing what they claim, or are any of them reporting success without proof?”"
- **useful because:** A routine can be marked completed after Mac-side work even when browser delivery, relay speech, or pendant playback never occurred. The owner needs a routine-by-routine audit that distinguishes intended, started, Mac-completed, relay-accepted, device-received, and physically-played—with missing stages called unknown rather than inferred. This would expose silent false success in the daily brief, research brief, evening wrap-up, and Downloads tidy.
- **path:** relay → mac-planner → browser → pendant → dashboard
- **model tier:** Deterministic stage reconciliation first; use a cheaper background model only to summarize anomalies and trends. Realtime is unnecessary except for an urgent spoken warning.
- **latency:** Under 3 seconds for the current day; historical audit may run asynchronously and notify when complete.
- **cost:** Usually under $0.02, dominated by one compact reconciliation pass; no expensive model required for ordinary runs.
- **security:** Routine content may include private mail, files, or browser data. Return stage metadata and short redacted explanations by default, with sensitive evidence requiring explicit expansion. Never call a routine successful merely because a later stage is absent.
- **missing:** A canonical routine execution state machine spanning Mac action receipt, browser result, relay acceptance, device receipt, and playback telemetry.; A reader that refuses the existing Mac-completed fallback when a downstream stage was expected.; A durable owner-facing anomaly record with run ID, missing stage, freshness, and recovery suggestion.

### "“Why did you choose that action instead of the safer alternative, and what information would have changed your decision?”"
- **useful because:** The owner cannot currently inspect the actual perception-to-judgement boundary. A fluent result hides whether the system saw a fresh browser observation, relied on stale memory, encountered a permission gap, or simply had no safer route. A decision replay would show the facts available at decision time, their freshness and provenance, rejected alternatives, required confirmations, and the precise uncertainty that remains—without pretending the model's post-hoc explanation is the original cause.
- **path:** relay → mac-planner → browser → dashboard → pendant
- **model tier:** Store structured decision inputs and policy outcomes at execution time; use a background model only to verbalize them. Never ask a model to reconstruct rationale from the final answer alone.
- **latency:** Immediate for a recent decision from the journal; under 10 seconds for a historical reconstruction.
- **cost:** Low ongoing storage cost for bounded structured records; under $0.01 for optional summarization.
- **security:** Decision records can contain private page titles, file paths, and message metadata. Store redacted references and hashes by default, enforce the original permission scope when expanding evidence, and never expose bearer credentials or secret memory values.
- **missing:** A decision journal that records input references, freshness, policy rule, selected executor, rejected alternatives, confirmation state, and uncertainty before execution.; A stable join from journal entries to evidence capsules, browser commands, Mac ledgers, relay jobs, and routine runs.; A retention and redaction policy for decision records so they remain useful without becoming a second private-content archive.

### "“At 5:00 PM yesterday, what did you actually know about my devices, browser, routines, and pending work—and which parts are reconstructed rather than observed?”"
- **useful because:** Current dashboards answer what is true now, while the owner often needs to understand a past failure or interruption. The system's stores have incompatible count and byte caps, relay jobs expire, and several timestamps are machine or inferred values. A bounded temporal reconstruction would return an evidence-time snapshot with per-field provenance, clock source, freshness, and explicit gaps instead of fabricating a continuous history.
- **path:** relay → mac-planner → browser → pendant → dashboard
- **model tier:** Build from timestamped structured events with deterministic interval joins; use a background model only to produce a short narrative after the timeline is assembled.
- **latency:** Under 5 seconds inside retained history; return a clear “not retained” result when the requested time predates available evidence.
- **cost:** Low per query; the main cost is bounded event retention and indexing, not inference.
- **security:** Historical browser and device state can reveal private activity. Enforce the same surface permissions as the original observation, redact page contents and secrets by default, and distinguish owner-visible metadata from restricted evidence.
- **missing:** A cross-surface event envelope with source clock, observedAt, receivedAt, sequence, provenance link, and retention expiry.; Indexed time-range queries over Mac traces, browser heartbeats/results, relay jobs/announcements, routine runs, and pendant health/playback events.; A clock-skew policy that never converts the pendant's zoneless time into the Mac timezone and labels irreconcilable intervals as unknown.


## Changes it proposed to its own stack

### `context` — Add a deterministic provenance-and-freshness fence to context assembly: every injected fact carries source.origin, observedAt/lastUsedAt, expiry, confidence, and contradiction status; machine-origin preferences are never rendered under the unqualified “Owner” heading when a live machine observation disagrees. Emit a compact conflict object for judgement and dashboard review, without changing or deleting the owner's stored fact.
- **owner gets:** The owner stops receiving a wrong, pinned machine-derived preference as if he personally stated it, while preserving the fact for explicit review. Future actions can say “this is machine-derived and contradicted” instead of silently using it.
- effort: Medium: projection schema/renderer, conflict comparator against machine-context, tests for timezone-like contradictions, and dashboard display.  ·  risk: Some prompts get longer and some previously automatic actions become cautious. Recover by falling back to the old value only when the owner explicitly confirms it; never mutate the source row automatically.
- cost: Negligible storage and model cost; deterministic local computation.  ·  latency: Tens of milliseconds in local projection assembly.
- security: Improves provenance handling; must keep secret fact values redacted in conflict summaries and preserve source sensitivity.
- depends on: Use the existing GET /memory/projection and GET /machine-context data; do not create a parallel memory store.; Owner confirmation path for correcting or retiring a fact.


## What it asked for

_Nothing._
## Its own summary

Recorded three capabilities the owner cannot have today: a routine truth audit that distinguishes Mac completion from actual downstream delivery/playback; a decision replay showing original evidence, policy, rejected alternatives, and uncertainty; and a timestamped cross-surface reconstruction that labels observed versus reconstructed history. All require new joins and durable provenance, not merely UI.

**Biggest unknown:** The backlog may contain superficially similar proposals, but these were framed around distinct missing perception contracts: routine stage truth, pre-execution decision causality, and historical state reconstruction.

