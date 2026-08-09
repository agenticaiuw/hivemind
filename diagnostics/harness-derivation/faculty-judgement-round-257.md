# Harness derivation — faculty-judgement — round 257

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I tell you an action was wrong—or stop it halfway—learn exactly what failed, show me the evidence, and avoid making the same class of mistake again without silently changing your rules."
- **useful because:** Today stop/undo, delivery ACKs, receipts, and provenance are separate. The owner has to reconstruct failures and the system cannot distinguish a wrong target from stale evidence or an audio delivery problem. A reviewable correction loop turns the pendant’s physical interruption and Mac/browser outcomes into safer future decisions, while keeping policy changes explicit and owner-approved.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** background for classification and weekly pattern summaries; realtime only to acknowledge the correction and state the immediate safe action
- **latency:** Immediate acknowledgement under 1 second; classification within 10 seconds; no blocking of the owner’s next request
- **cost:** About $0.002–$0.02 per correction depending on whether a model is needed; most cases are deterministic labels from receipts, ACKs, and policy verdicts
- **security:** The correction record must contain IDs and structured failure labels by default, not transcript or page contents. Provenance is shown through explain_action_provenance. Never auto-promote a learned rule; stage a policy patch and require explicit approval. A malicious or accidental stop must not rewrite autonomy policy.
- **missing:** A typed correction event API linking a pendant stop/undo/approval to one action or briefing item; A durable cross-surface action identity joining relay, Mac, browser, and artifact IDs; A review route that proposes policy changes without applying them; A background evaluator that clusters repeated corrections with source-linked evidence

### "When I come back, tell me what actually happened while I was away: what finished, what reached the pendant, what is still stuck, and what needs me—without making me ask every surface separately."
- **useful because:** Catch-up today is assembled from partial sources and cannot prove pendant playback, does not reliably identify orphaned Mac jobs, and has no single owner-facing continuity report. A delivery-aware return brief would prevent duplicate work and expose silent failures such as audio downloaded but never heard or a job left processing after a Mac crash.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** background model to summarize structured events; deterministic rules first for completion, expiry, and duplicate suppression
- **latency:** Generate in under 5 seconds on request; optional scheduled preparation under 30 seconds
- **cost:** Roughly $0.005–$0.03 per report; token cost dominates only when many heterogeneous receipts need summarization
- **security:** Speak only item titles/statuses unless the owner explicitly requests detail; do not include raw mail, page text, or private audio in a default report. Every line must carry an evidence reference and freshness timestamp. Stale or missing ACKs must be reported as unknown, never as completed.
- **missing:** A relay-to-local durable job identity and lease/requeue semantics for orphaned processing jobs; A report aggregator joining relay job receipts, Mac/browser receipts, context handoffs, and authenticated pendant delivery ACKs; A durable last-seen cursor so reconnect/replay does not duplicate items; An owner-facing route and compact audio rendering for finished/stuck/needs-you sections

### "Do this once, even if the Mac, browser, or relay reconnects halfway through—and if you already did it, prove that before trying again."
- **useful because:** The system currently has five unrelated ID namespaces and only Mac-local idempotency. A single owner-visible action identity would prevent duplicate reminders, duplicate browser submissions, repeated drafts, and confusing handoffs after reconnects. This is the difference between a hive mind and several agents independently repeating the same request.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic routing and idempotency checks; use the realtime model only for ambiguous natural-language matching to an existing action
- **latency:** Under 300 ms for known IDs; under 2 seconds for ambiguous matching; no external mutation until identity and current-state checks pass
- **cost:** Near-zero for deterministic hashes and store lookups; up to $0.01 for ambiguous matching
- **security:** The identity must bind intent, target, and allowed effect—not secrets or page contents. Never treat a textual similarity match as proof for destructive actions. Expired or state-changed identities become ASK/PREPARE, not retries. Owner can inspect and revoke the chain.
- **missing:** A relay-issued correlation ID carried unchanged through Mac jobs, browser commands, action receipts, pipeline artifacts, and pendant ACKs; A durable idempotency ledger shared or reconciled across relay and Mac; Adapters that map browser command IDs and Mac action IDs into the shared record; A fail-closed duplicate decision integrated before POST /execute and browser mutation

### "Give me a portable, complete account of what this system knows about me, where each claim came from, what it caused, what I revoked, and what is still retained—so I can inspect it or leave without trusting the system’s own dashboard."
- **useful because:** Today provenance is queried per action or evidence item, while facts, graph records, browser captures, relay memory, audio artifacts, and revocations are split across stores with no owner-controlled export or completeness proof. The owner cannot independently audit the system’s memory, detect orphaned copies, or migrate away. A signed, resumable export with omission proofs makes trust inspectable rather than assumed.
- **path:** dashboard → relay → mac → browser → pendant
- **model tier:** Deterministic extraction, joins, redaction, and hashing; background model only to produce an optional human-readable summary after the exact manifest is generated
- **latency:** Start streaming within 2 seconds; export incrementally in the background; summary under 30 seconds for a typical month
- **cost:** Near-zero for manifests, hashes, and structured records; up to $0.02 for an optional natural-language summary
- **security:** Exports are highly sensitive and must be local-first, encrypted, expiring, and explicitly downloaded. Default output contains metadata and source references, not raw secrets or audio. The owner must choose whether to include sensitive bodies. Every omitted record needs a reason (expired, revoked, inaccessible, or unsupported), never silent omission. No third-party model receives the export unless explicitly requested.
- **missing:** A cross-store export protocol joining Mac facts/graph/captures/evidence, browser provenance, relay jobs/memory, pipeline artifacts, and pendant delivery events; Stable source and deletion identifiers so revocations and derived copies can be proven to propagate or be reported as orphaned; A signed manifest with per-store watermarks, record hashes, omission reasons, and export encryption; An owner-controlled import/delete verification path rather than a dashboard-only rendering

### "Watch yourself for violations of your own promises and tell me before I rely on you: for example, if private content was spoken, an action bypassed consent, a stale source drove a decision, or an artifact was delivered without a valid receipt."
- **useful because:** The current system records many events but does not continuously compare them against safety invariants. Failures can remain invisible unless the owner already knows which route to inspect. An independent watchdog gives the owner an honest trust signal and a reviewable incident report, rather than assuming successful HTTP responses mean safe behavior.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic invariant checks and signed event joins; background model only for grouping incidents and drafting a plain-language explanation
- **latency:** Critical violations surfaced within seconds; routine audit every 15 minutes; report generation under 10 seconds
- **cost:** Near-zero for structured checks; under $0.01 per incident summary when a model is used
- **security:** The watchdog must be isolated from the component it audits and append-only for incident evidence. It must not replay, repair, or conceal a violation. Spoken alerts must reveal only a safe category by default. False positives should create review items, never automatically cancel unrelated work. Retention and export of incident records need explicit owner controls.
- **missing:** A typed invariant registry covering consent, freshness, sensitivity, delivery, and revocation rules; An append-only cross-surface event stream with authenticated timestamps and correlation IDs; A verifier independent of the normal planner and speech path; A critical-alert route that can reach the existing pendant inbox without exposing sensitive payloads; A dashboard showing invariant, evidence, impact, and remediation state


## Changes it proposed to its own stack

### `relay` — Add a lease_until/attempt counter and requeue sweep to relay_jobs, then preserve one relay correlation ID through bridge handoff and local/browser receipts. On reconnect, the relay must classify each job as completed, safely retryable, or owner-attention-required using idempotency evidence; never blindly replay a mutation.
- **owner gets:** A sleeping or crashed Mac will no longer make a request vanish for 24 hours or cause a duplicate when it comes back. The owner gets one truthful status and one safe continuation instead of repeating themselves across surfaces.
- effort: Medium: D1/memory-store schema and sweeper, bridge propagation, receipt joins, and tests for crash/reconnect races.  ·  risk: A lease that is too short can duplicate a slow action; too long delays recovery. Fail closed for external or destructive actions, and require current-state revalidation before retry. Roll back by leaving old processing semantics behind a feature flag while migrating rows.
- cost: Negligible storage and CPU; no model cost for deterministic lease decisions.  ·  latency: Adds one lookup/update before retry; normal first execution unchanged.
- security: Improves auditability. Correlation records must carry opaque IDs only, not page contents, credentials, or audio.
- depends on: A durable relay↔Mac↔browser correlation mapping; revalidate_pending_plan for stale prepared actions; autonomy_policy_evaluate before any replay; record_pendant_delivery_event for audio completion evidence


## What it asked for

_Nothing._
