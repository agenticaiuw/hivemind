# Harness derivation — faculty-perception — round 257

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac perception boundary** — At 2026-08-09T04:04Z the Mac agent reports Accessibility and Screen Recording granted, requiredMissing=[], permissions.ready=true; browser extension online on Safari YouTube tab 85 with zero pending commands; relay reachable and Mac bridge online. The registered nrf9160-pendant is present but offline, so no current pendant liveness or playback can be asserted.
  - evidence: read_continuity_snapshot(include=['relay','pipeline']) invoked GET /ops/snapshot HTTP 200; returned permissions.ready=true, browser online/tab 85, relay reachable, and device discovery lists nrf9160-pendant offline.

## Capabilities it proposed

### "“What actually happened across my Mac, browser, relay, and pendant while I was away—and which claims are proven, stale, or still unknown?”"
- **useful because:** This would be the system's single most useful perception capability: an evidence-ranked reconstruction rather than a reassuring but false completed/online summary. It would distinguish Mac execution from browser observation, relay acceptance from device playback, and current liveness from stale records, then expose contradictions and missing witnesses in plain language.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Use a cheap background model to assemble and cluster the bounded event graph; reserve realtime only for the owner's follow-up question. Deterministic freshness, provenance, and contradiction rules must run before the model so it cannot promote a Mac-side completion into proof of hearing.
- **latency:** Initial snapshot under 2 seconds from parallel reads; narrative another 1–2 seconds. Recompute only changed sources, with a visible capturedAt and per-source freshness.
- **cost:** About $0.01–$0.04 per on-demand reconstruction depending on event count; most cost is the final synthesis, not the bounded reads.
- **security:** Do not send raw page bodies, message contents, or audio to the relay unnecessarily. Keep hashes, redacted snippets, device IDs, and timestamps by default; require confirmation before surfacing sensitive browser-derived claims. Explicitly mark absent pendant telemetry as unknown, never offline-proof.
- **missing:** A unified event envelope with source, observedAt, capturedAt, evidence strength, and causal links across /ops/snapshot, /pipeline, browser results, and relay jobs; A relay-to-Mac provenance bridge for cloud browser reads: stable ID plus content hash, then mintCapsule/recordExtraction locally; A real device-playback witness from the accepted audio_delivery_ack_queue, not the existing bytes-to-socket announcement state; A persisted, bounded contradiction index so a later snapshot can explain what changed rather than silently replacing it

### "“Before you execute anything from what I just said, tell me whether my utterance was clear enough to trust—and if not, ask me to repeat only the risky part.”"
- **useful because:** A single clipped or noisy word can turn a harmless request into a dangerous action. This makes perception an enforceable precondition: the worn device measures capture quality, the relay transcribes, and the Mac/action layer refuses to commit when the evidence is degraded instead of guessing silently.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Use deterministic device-side quality thresholds and a cheap transcription-quality classifier for ordinary requests. Escalate to realtime only when ambiguity intersects a high-impact action; never let the expensive model override an unusable capture verdict.
- **latency:** Quality verdict at utterance end with no added conversational turn when clear; 300–700 ms for a repeat request when degraded. High-impact action gets a visible hold state rather than timing out.
- **cost:** Usually under $0.005 per utterance for metrics and a small classifier; escalation costs one normal realtime turn. Device computation is already budgeted by offline-capture-integrity-sentinel.
- **security:** Transmit only metrics and the disputed transcript span, not continuous raw audio. Require explicit confirmation after a degraded repeat for destructive, financial, messaging, or access-control actions. Preserve the original quality verdict with the action receipt so later auditing cannot rewrite history.
- **missing:** A relay policy that carries the sentinel's sequence-numbered clear/degraded/unusable verdict alongside transcription; A Mac planner/action gate that binds an action to that exact utterance sequence and rejects stale or degraded evidence; A risk taxonomy shared by judgement and action so 'repeat' is required only where consequences warrant it; A user-visible explanation in the dashboard and voice response when an action is held

### "“When the pendant reconnects, show me exactly what it witnessed offline, what was already handled on the Mac, and merge the two without replaying or losing anything.”"
- **useful because:** The pendant can be physically present while the relay knows nothing. A reconnect should not create duplicate reminders, duplicate commands, or a false clean slate. This gives the owner a bounded offline handoff: monotonic beacon and capture sequences from the wearable, Mac pipeline/action receipts, and relay job state are reconciled into kept, duplicated, conflicted, and unverified buckets before judgement sees them.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Use deterministic sequence/range and idempotency-key reconciliation first; a cheaper background model summarizes conflicts. Realtime is only for the owner's spoken request to inspect or resolve a conflict.
- **latency:** On reconnect, ingest and deduplicate within 2 seconds for the normal bounded queue; surface a compact conflict card within 5 seconds. Never block the pendant's live conversation on full historical reconciliation.
- **cost:** Negligible model cost for normal sync; roughly $0.005–$0.02 only when conflict summaries need language generation. Main cost is a few kilobytes of NVS and one bounded sync exchange.
- **security:** Use per-device authenticated sequence ranges and do not trust a pendant timestamp as an instant because its timezone is unknown. Do not upload SD fallback audio automatically; upload only metadata and require confirmation for sensitive recordings. Treat a missing range as unknown, not as empty, and retain an audit record of every deduplication decision.
- **missing:** A reconnect endpoint that accepts the offline-reality-beacon frame plus signed, monotonic event batches and returns an acknowledged high-water mark; A shared idempotency-key format spanning pendant audio_delivery_ack_queue, Mac pipeline events, action receipts, and relay jobs; A durable bounded handoff ledger on the relay or Mac that records missing ranges and conflicts across restart; A reconciliation reader used by judgement, with explicit states kept/duplicate/conflict/unverified rather than a single completed flag

### "“Before you tell me that a website, app, or device state is real, independently verify it from the rendered surface and a second observer, and show me exactly where they disagree.”"
- **useful because:** Today one browser read, one accessibility snapshot, or one relay report can be stale, incomplete, or a login-wall illusion. The owner should be able to trust a claim only after the system compares independent observations: rendered browser state, accessibility/UI state on the Mac, relay state, and—when available—the device beacon. It would catch silent stale tabs, misleading cached pages, and false 'done' states before judgement or action relies on them.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** Use deterministic field-level comparison and freshness checks first; use a cheap model only to explain semantic disagreements such as 'the page says submitted but the UI still shows draft.' Realtime is unnecessary unless the owner asks a follow-up.
- **latency:** 2–4 seconds for two observers in parallel; return a structured verdict with each observation timestamp and disagreement location. Do not wait for an unavailable pendant—label that observer missing and continue with an explicit lower-confidence result.
- **cost:** Usually under $0.01 per verification; browser and Mac reads dominate latency, with model spend limited to disagreement explanation.
- **security:** Never compare or transmit secret form values, cookies, or full screenshots by default. Redact sensitive fields before comparison and require confirmation before exposing a disagreement involving accounts, payments, or private messages. A matching pair of stale observations must not be upgraded to current truth without freshness bounds.
- **missing:** A normalized observation schema for UI state, browser state, relay state, and device health fields; A freshness-aware comparator that distinguishes agreement, contradiction, missing observer, and stale agreement; A browser/Mac capture join key so two observations of the same tab or page can be proven contemporaneous; A dashboard and voice response format that exposes the disagreement without pretending to resolve it; A policy defining which contradictions block an action and which merely lower confidence

### "“When I correct one of your observations, remember which source was wrong for this kind of fact, and use that calibration the next time—without changing the underlying record.”"
- **useful because:** The system currently treats a relay report, browser read, Mac UI state, and device telemetry as largely interchangeable even though each fails differently. The owner should be able to correct a claim once and have future perception route around that known weakness: for example, distrust a cached relay status for freshness but still use it for history. This improves truth without silently rewriting evidence.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Keep calibration updates deterministic and owner-confirmed. A small background model can classify the correction's domain and failure mode; realtime is only needed when the owner gives the correction conversationally.
- **latency:** Apply a correction immediately; future routing adds less than 100 ms because it is a local policy lookup. Show the owner the active calibration whenever it changes confidence or observer selection.
- **cost:** Under $0.005 per correction; storage is a bounded policy table, not model context or raw history.
- **security:** Only explicit owner corrections may change trust weights. Never let an inferred model disagreement demote a source permanently. Keep the original observation immutable, record who/what corrected it, scope the calibration by fact type and freshness regime, and provide undo.
- **missing:** A versioned observer-calibration store keyed by fact domain, source, failure mode, and freshness; An owner correction action that links to the exact observation and cannot mutate its original evidence; A confidence calculator that uses calibration as a bounded adjustment rather than overriding hard evidence; A visible audit and reset control so the owner can inspect or revoke learned distrust

### "“Tell me before a fact I am about to rely on has gone stale, and tell me what fresh observation would make it safe again.”"
- **useful because:** A timestamp alone does not tell the owner whether an observation remains usable: a calendar event, device connection, web price, and logged-in page all decay at different rates. This would make staleness actionable rather than merely visible. Before an action, it would identify the exact expired premise and obtain the least-invasive fresh witness instead of forcing the owner to discover the mistake afterward.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Use deterministic, domain-specific freshness budgets and action-risk rules. A cheap background model may classify an unknown fact's volatility; realtime is used only when the owner is waiting on a spoken answer.
- **latency:** Preflight under 500 ms from cached observations; refresh only the stale premise in parallel, normally under 3 seconds. If no observer is available, return a blocked/unknown result rather than guessing.
- **cost:** Usually under $0.01; most invocations are local policy checks, with model cost only for classifying new domains.
- **security:** Do not silently refresh pages or access private apps merely to extend a fact's lifetime. Require the same permission and confirmation rules as the eventual action. Preserve old and new observations separately, and show the owner whether freshness came from a new device report, a browser read, or a Mac-side inference.
- **missing:** A freshness policy registry keyed by fact type, source, volatility, and consequence level; A pre-action premise manifest that records which observations an action depends on; A refresh planner that requests only the minimum new observation and refuses unavailable or unauthorized sources; A user-facing stale-premise explanation and a way to override it explicitly for low-risk actions


## What it asked for

_Nothing._
