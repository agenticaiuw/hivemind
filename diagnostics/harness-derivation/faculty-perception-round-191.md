# Harness derivation — faculty-perception — round 191

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser reachability** — At 2026-08-08T22:35Z, GET /ops/snapshot reports the AI Pendant Agent ready with Accessibility and Screen Recording granted, all listed automation grants present, Safari extension online with 2 tabs and 0 pending commands, and relay reachable with D1 store and Mac bridge online.
  - evidence: read_continuity_snapshot include relay,pipeline invoked GET /ops/snapshot HTTP 200; body.status.permissions.ready=true, browserExtension.online=true, pendingCommands=0, relay.reachable=true, relay.payload.store='d1'.

## Capabilities it proposed

### "“Before you use a remembered preference or take an action, tell me if the system has evidence that it is still true.”"
- **useful because:** The current projection can put a machine-sampled, contradictory preference such as America/Chicago at the head of every prompt indefinitely. This gives the owner a short, spoken reality fence: source, age, independent corroboration, and what would change if it is wrong—rather than silently treating memory as intent.
- **path:** mac-planner → browser-extension → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** Background model builds a contradiction report; realtime only verbalizes the compact verdict when an action depends on it.
- **latency:** Under 2 seconds for a local fact check; do not block unrelated requests. Recheck only facts that gate an action.
- **cost:** Low: one background classification call only on a detected contradiction; otherwise route reads. Dominant cost is context projection, not inference.
- **security:** Never expose secret fact values in relay logs. Compare hashes/typed values locally and return only the minimum conflict. Require confirmation before changing or deleting a pinned fact; never auto-rewrite owner data.
- **missing:** A source-aware fact validator that compares memory facts with live Mac/browser observations and records a quarantine state without mutating the owner's fact store; A typed contradiction event consumable by judgement/action; A policy that prevents quarantined facts from entering the prompt head while preserving them for explicit review

### "“Is the thing you are about to act on still the same thing I showed you?”"
- **useful because:** A browser page, tab, or account can change after a read. Today the Mac evidence capsule can hash content, but the relay voice/browser paths can lack a capsule or freshness join, so judgement may act on stale or unauthenticated page text. This capability speaks a one-sentence freshness verdict and blocks only when identity or content drift is material.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** No realtime model for comparison: local hashes and typed region fingerprints decide; realtime summarizes only ambiguous drift.
- **latency:** 150–400 ms for an existing tab checkpoint; up to 2 s when a fresh browser read is required. Irreversible actions wait for the verdict.
- **cost:** Near-zero model cost for stable selectors and hashes; occasional small model call for semantic-region re-identification. Browser inspection and extension round trips dominate.
- **security:** Never send full page contents to the relay for a freshness check. Hash/redact locally, bind the checkpoint to tab/session generation, and require owner confirmation on identity ambiguity or sensitive fields.
- **missing:** A relay-returned request ID and content hash for read_web_page, then a Mac-side mintCapsule join for relay-originated reads; A pre-mutation browser checkpoint action returning tab/session generation and normalized target hash; A judgement policy distinguishing harmless content drift from account/recipient/amount drift

### "“When I come back, show me the things you promised or started that still have no verified outcome—one line each, with the next useful choice.”"
- **useful because:** A completed Mac job is not necessarily a completed owner task, and a browser result can be accepted without proving the intended state changed. This is not another job-status list: it reconstructs the causal chain from the owner's request to plan, action, observation, and resulting state, then exposes only open promises and the decision needed next.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Background model clusters and summarizes only open chains; realtime speaks the bounded digest when the owner returns. Deterministic joins and status rules do the primary work.
- **latency:** Incremental updates under 300 ms after a receipt/event; return digest under 2 s. Never hold an action on this report unless its own safety policy requires it.
- **cost:** Low ongoing cost using event joins; occasional cheap summarization proportional to open chains. No expensive model call for ordinary completions.
- **security:** Keep the chain store local by default; relay receives opaque IDs and redacted outcome classes. Do not infer success from silence, socket writes, or Mac completion. Destructive or financial open chains must require explicit confirmation.
- **missing:** A single causal correlation ID propagated from voice turn through plan, execute, browser command, and resulting observation; A typed outcome vocabulary separating accepted, executed, observed-state-changed, owner-confirmed, expired, and unknown; A durable bounded open-chain index with privacy-preserving summaries and a return-time trigger

### "“When you get something about my world wrong, let me correct the observation—not just the answer—and make that correction prevent the same mistake next time.”"
- **useful because:** Today a wrong machine observation, stale browser reading, failed delivery, and owner disagreement are all mixed into generic success or memory. The owner cannot teach the perception layer which sensor or inference failed. This capability turns a one-tap or spoken correction into a typed calibration record: wrong source, wrong time, wrong identity, or wrong interpretation, with later answers showing whether the correction was applied.
- **path:** relay-realtime → faculty-perception → faculty-judgement → mac-planner → browser-extension
- **model tier:** Deterministic event classification and source matching first; a cheap background model clusters repeated corrections. Realtime only confirms the correction and gives a short explanation.
- **latency:** Acknowledge a correction in under 500 ms; apply it to the next relevant observation immediately. Background clustering can take minutes.
- **cost:** Low: local typed records and hashes dominate; one small background classification call only when similar corrections need clustering.
- **security:** Corrections can contain sensitive personal facts. Store raw utterances locally, send only a redacted correction type and opaque observation IDs to the relay, and require confirmation before a correction changes a persistent preference or action policy.
- **missing:** A stable observation ID on every perception result, including memory projection entries, browser reads, Mac status reads, pipeline quality verdicts, and relay delivery claims; A correction ledger that links owner feedback to source, timestamp, confidence, and later re-evaluations without rewriting the original evidence; A calibration evaluator that measures repeated false-positive/false-negative patterns and exposes an owner-reviewable policy change

### "“If you are unsure, ask me for the smallest observation that would actually resolve it—not a vague confirmation.”"
- **useful because:** The system currently collapses missing evidence, stale evidence, and contradictory evidence into generic uncertainty or proceeds on a fallback. The owner should get a precise request such as “Which of these two Safari tabs is the order?” or “Should I treat this machine-derived timezone as yours?” with the exact consequence of answering, rather than repeated broad confirmations.
- **path:** faculty-perception → faculty-judgement → relay-realtime → browser-extension → mac-planner
- **model tier:** A deterministic information-gain selector chooses among available observations; a small background model verbalizes only when choices are semantic. Realtime speaks the one question.
- **latency:** Select the question in under 300 ms from current evidence; if a browser/tab observation is needed, resolve in under 2 s. Never ask more than one blocking question at a time.
- **cost:** Very low: typed candidate observations and confidence deltas; occasional small model call for natural-language rendering.
- **security:** Questions must not leak hidden account contents or secrets. Offer labels and redacted previews, keep sensitive choices local, and never treat an answer as permission to perform a destructive action.
- **missing:** A typed observation graph with candidate queries and expected confidence deltas; A cross-surface query planner that can request one bounded browser, Mac, or relay observation without exposing full context; A judgement contract that records why the question was asked and invalidates it when the underlying tab/session/device generation changes

### "“Show me when two parts of you disagree about the same real-world fact, and let me choose which observation wins for this situation without erasing either one.”"
- **useful because:** The owner cannot currently distinguish a disagreement between memory, Mac state, Safari, and relay state from a normal answer. A live disagreement card would show each observation's source, timestamp, scope, and confidence—for example a browser tab saying one account while a stored claim names another—then apply a scoped choice instead of silently corrupting memory.
- **path:** faculty-perception → faculty-judgement → relay-realtime → mac-planner → browser-extension
- **model tier:** Deterministic normalization and comparison; background model only for entity matching across differently worded observations. Realtime reads the compact disagreement card.
- **latency:** Detect within 1 second of a new observation; render in under 2 seconds. Scoping the choice should be immediate and must not block unrelated work.
- **cost:** Low to moderate: entity normalization is the main model cost, cached by observation hashes; storage is bounded by tombstoned observation references rather than raw content.
- **security:** Disagreement cards must redact secrets and avoid putting private page text into relay logs. A scoped choice may affect actions, so require explicit confirmation for destructive, financial, or communication operations; retain both original observations for audit.
- **missing:** A normalized observation envelope with source, scope, capture time, freshness, confidence, and content hash; A disagreement detector that compares observations without prematurely selecting a winner; Scoped resolution rules (this tab, this task, this session, or durable owner preference) with expiry and provenance


## Changes it proposed to its own stack

### `integration` — Make pendant presence and identity a real observed fact: on every authenticated pendant WebSocket start/heartbeat, persist a device-registry row and emit a scoped presence event; replace the firmware's admin bearer on the converse path with an nrf_pendant credential, and surface lastSeenAt plus connection generation in the Mac/relay snapshot. Keep the existing 90-second online threshold but distinguish 'never registered' from 'stale' and 'currently connected'.
- **owner gets:** The system can now prove the Mac and browser are reachable, but it still cannot honestly tell the owner whether a pendant exists, is connected, or merely has old audio history. This is the prerequisite for trusting any wearable delivery or offline-reality report.
- effort: Moderate: relay WebSocket registration and scoped auth, firmware credential/header change, one snapshot normalization, and an integration test for connect/drop/reconnect.  ·  risk: A credential mismatch could strand the pendant; recover with an admin-paired fallback during migration and a firmware feature flag. A stale registry row must never be presented as live.
- cost: Negligible runtime/API cost; no new hardware. Small D1 writes on connect/heartbeat.  ·  latency: No perceptible voice latency; one bounded registry write per heartbeat.
- security: Improves security by removing the admin key from pendant traffic. Requires credential rotation and careful device-scoped authorization.
- depends on: A physically registered pendant (currently none is in the relay registry); offline-reality-beacon firmware work; A relay schema/event field for connection generation


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: /ops/snapshot is reachable; the Mac agent is fully ready with Accessibility and Screen Recording granted, Safari bridge online (2 tabs, 0 pending), relay reachable on D1, and Mac bridge online. I recorded that finding. Proposed three owner-facing capabilities: (1) source-aware contradiction quarantine for stale machine-derived preferences, (2) pre-action browser identity/freshness verdict tied to evidence hashes, and (3) a return-time open-promises report that distinguishes accepted/executed/observed/owner-confirmed/unknown rather than equating Mac completion with success. Also proposed a scoped pendant identity/presence integration, since the relay still has no registered pendant.

**Biggest unknown:** The wearable remains the decisive blind spot: no nRF9160 is registered or heartbeat-backed, so nothing can currently establish pendant connection, receipt, or playback. The relay-originated browser-read path also still lacks a request ID/content hash bridge into the Mac evidence capsule store, and no causal correlation ID spans voice request → plan → browser/action → observed state.

