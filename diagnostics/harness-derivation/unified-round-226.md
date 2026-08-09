# Harness derivation — unified — round 226

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Run a real bench readiness check on the two connected chips, inject a bad link, and give me one owner-readable verdict with the exact recovery step.”"
- **useful because:** The hardware is physically connected now, while LTE registration is not. Existing audio validation and fault injection can measure the shipped 24 kHz path, but they do not yet present a single bench operation that distinguishes firmware, bridge, relay and link faults or leaves a reproducible receipt. This would make the owner's actual bench setup useful today without pretending USB is a product transport.
- **path:** mac-planner → relay-realtime → pendant → mac-terminal
- **model tier:** deterministic diagnostics and threshold evaluation; background model only to turn counters into one short explanation
- **latency:** Normal run 30–90 seconds; injected-loss run up to 3 minutes; no action on the device beyond test traffic unless explicitly requested.
- **cost:** <$0.02 per run; dominated by hardware test duration, with negligible model cost.
- **security:** Read-only by default; explicitly label synthetic audio and fault injection; never save raw audio by default; redact serial identifiers in receipts; require confirmation before flashing or changing firmware; separate USB bench evidence from LTE production claims.
- **missing:** a typed bench-session orchestrator that can invoke capture, validate both directions, inject loss and correlate artifacts; a serial-log/artifact collector with exit codes and timestamps; a single verdict schema mapping acceptance thresholds to recovery actions

### "“Make my morning brief one calm update, not four routines talking over each other, and tell me what was merged.”"
- **useful because:** The live owner state has multiple daily routines at the same 07:00 time plus a 07:30 battery brief. They currently produce separate jobs and can repeat context or compete for attention. A deterministic morning compiler would collect the completed calendar/mail/files, research, battery and Wi‑Fi results, remove duplicate headlines, and deliver one short spoken update while retaining links to each source.
- **path:** relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** background model for synthesis; deterministic scheduler for collection, ordering, deduplication and quiet-hour delivery
- **latency:** Assemble within 60 seconds after the collection window; one spoken delivery under 20 seconds unless the owner asks for detail.
- **cost:** <$0.05 per morning; dominated by one background synthesis and any web research already scheduled.
- **security:** Keep source boundaries visible; do not merge sensitive mail content into a generic news sentence; respect owner’s destructive-action policy; do not interrupt an active call; preserve per-source receipts so a summary cannot masquerade as a completed action.
- **missing:** a routine grouping/collection-window primitive; a deduplication contract for briefing findings with source and freshness metadata; a single queued spoken delivery that supersedes constituent routine speech without deleting their artifacts

### "“Tune the pendant and bridge for my voice and ears, then prove the 24 kHz path still meets the quality limits.”"
- **useful because:** The shipped 24 kHz path is objectively within limits, but a wearable still needs owner-specific gain, playback loudness and fit calibration. A deliberate bench session can play short locally generated tones/speech, collect the owner’s simple comparisons, choose safe mic/speaker parameters, and rerun the existing alias, clipping, continuity and codec checks. It improves intelligibility without storing conversation audio.
- **path:** pendant → mac-planner → relay-realtime → mac-terminal
- **model tier:** deterministic signal generation, parameter search and acceptance checks; realtime model only to guide the owner through comparisons
- **latency:** 3–5 minutes once per fit/device change; immediate local level changes; no calibration during a live call.
- **cost:** <$0.03 per session; dominated by one short interactive guidance turn and hardware test time.
- **security:** Use synthetic fixtures or owner-initiated test phrases only; never upload calibration speech by default; cap gain to prevent hearing damage and clipping; persist only parameters and aggregate measurements; require an explicit start gesture.
- **missing:** a typed calibration session route spanning pendant and ESP32 bridge; safe parameter bounds and a small persistent calibration record; owner-response capture (A/B choice or intelligibility score) without retaining raw speech

### "“When you tell me something from the web, Mac, or browser, mark how you know it and warn me when that claim is stale or contradicted.”"
- **useful because:** Today the pendant can speak a confident sentence assembled from different surfaces, but the owner cannot distinguish a live observation, an old memory, an inference, or an unverified claim. A provenance-and-freshness layer would attach a compact evidence capsule to every externally grounded answer, preserve the observation time and source, and proactively downgrade or recheck claims before repeating them.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal
- **model tier:** deterministic source/time/status classification and freshness enforcement; background model only for resolving contradictions and composing the owner-facing explanation
- **latency:** Normal answer adds under 200 ms for local provenance; stale-claim recheck may take seconds and must be explicit in the spoken response.
- **cost:** <$0.02 per claim; dominated by optional web/Mac rechecks, not by the provenance record.
- **security:** Evidence must be least-privilege and redacted; never read a new browser tab or private file merely to refresh a claim; distinguish observation from inference; preserve source URLs/paths only when the owner is allowed to see them; allow the owner to delete a claim capsule without deleting action audit history.
- **missing:** a durable claim record with source kind, observedAt, freshness policy, confidence and evidence references; a cross-surface contradiction/recheck evaluator; a response contract that speaks uncertainty and age instead of flattening all evidence into one assertion


## What it asked for

_Nothing._
## Its own summary

I found and recorded three distinct owner-facing capabilities: (1) a single morning compiler that merges the overlapping 07:00/07:30 routines into one source-linked spoken brief, (2) an owner-specific pendant/bridge calibration session that preserves the shipped 24 kHz acceptance thresholds without retaining raw speech, and (3) a real bench readiness verdict that correlates the connected chips, injected link faults, pipeline validation and recovery advice. The first two failed proposals were correctly rejected as existing backlog items: fact inspection/erasure and physical approval continuation. The live devices show the Mac bridge online, Safari online, and the pendant still not registered for LTE.

**Biggest unknown:** The owner-facing policy choices still needed are calibration safety preferences (maximum loudness and whether synthetic-only tests are acceptable) and morning-brief delivery behavior (whether one merged brief should replace, or merely summarize, the existing routine outputs). Engineering gaps are the typed collection/deduplication route for routines, a cross-chip calibration route, and a bench-session artifact collector with serial timestamps and exit codes.

