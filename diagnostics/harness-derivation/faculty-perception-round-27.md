# Harness derivation — faculty-perception — round 27

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-bridge-readiness** — At fresh probe, Mac Local Agent v0.5.0 is online but not ready: Accessibility trusted=false and Screen Recording granted=false; requiredMissing is empty, optionalMissing empty, and fullControlMode=true.
  - evidence: GET /ops/status at 2026-08-07 round 27 returned agent.ready=false, permissions.accessibility.trusted=false, permissions.screenRecording.granted=false.
- **browser-connectivity** — Chrome browser extension is offline with 3 pending commands; last seen 2026-08-07T09:21:08.821Z.
  - evidence: GET /browser/status and /ops/status both returned online=false and pendingCommands=3 for home-chrome.
- **audio-path-observed** — Observed relay response pipeline rendered 24 kHz mono PCM successfully: 164650 bytes, 3430 ms, no clipping; same run's input telemetry was live LTE PCM at 15625 Hz, 937500 bytes, 1441 ms.
  - evidence: GET /pipeline run job_165a9c9a... events: tts done meta sampleRate=24000, pcmBytes=164650, clippedSamples=0; agent event inputTelemetry.sampleRate=15625.
- **relay-health** — Cloud relay is configured and reachable; its payload reports macBridgeOnline=true and capabilities pendantPipelineTelemetry, pendantSpeech, persistentAgentState, durableAudio enabled.
  - evidence: GET /ops/status relay payload returned reachable=true, macBridgeOnline=true, and listed those capabilities.

## Capabilities it proposed

### "“What happened while I was away?”"
- **useful because:** The owner currently gets disconnected fragments: the pendant may hold bookmarks/alerts offline, the relay may receive late replies, the Mac may have receipts, and the browser may have commands that never ran. This gives one chronological, evidence-backed account, explicitly separating observed completion, delivered-but-unplayed, queued, failed, and unknown—so a late message is never mistaken for a successful action.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background: deterministic event join and contradiction checks first; use gpt-4.1-mini only to compress the reconciled timeline into the owner's one-sentence spoken brief. Realtime is used only if the owner asks live.
- **latency:** Under 2 seconds when local caches are available; up to 10 seconds after reconnect while the relay fetches durable events. Never block reconnect or playback on summarization.
- **cost:** Usually <$0.01 per briefing; dominated by the small final summary (target <=1,500 input tokens), with joins and status classification deterministic.
- **security:** Private event metadata, browser URLs/titles, and action receipts leave the Mac only as typed, redacted event records; page contents stay local unless already authorized for research. Secret values must be excluded. Require confirmation only for any suggested follow-up action, never for reading the timeline.
- **missing:** A shared event schema with stable event IDs, device clock/monotonic timestamps, observedAt versus occurredAt, and source provenance across pendant, relay, Mac, and browser.; Relay endpoint to query a bounded since-cursor timeline and acknowledge which offline alerts/bookmarks were surfaced, without deleting evidence.; Mac/browser adapters that emit terminal receipts and explicit unknown outcomes when permissions or extension connectivity prevent observation.; A reconciliation reducer that detects contradictory states (for example queued plus completed) and preserves both claims instead of choosing silently.; Dashboard and pendant UI for 'unseen since last brief' cursor and a compact evidence capsule linked to each sentence.

### "“Is the hive caught up and in sync?”"
- **useful because:** Today the owner cannot tell whether a spoken reply, offline bookmark, Mac action, or browser command has propagated through every body. This gives a single convergence answer—caught up, partially converged, or split-brain—with the specific missing edge and age, instead of making them inspect four dashboards or trust a late delivery.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic state/convergence computation on the relay and Mac; use a cheap background model only to phrase a short explanation. Realtime is unnecessary unless asked during a live interaction.
- **latency:** Under 1 second from cached heartbeats and cursors; under 5 seconds for a reconnect probe. Must degrade to “cannot verify” rather than waking an expensive model or claiming synchronization.
- **cost:** Near-zero API cost for the normal path; at most <$0.005 for an optional background explanation. Storage is a small per-surface cursor/heartbeat record.
- **security:** Expose only health metadata, event IDs, ages, and redacted categories—not private page contents, mail, or secrets. Pairing and bearer authentication remain mandatory. A reconnect or replay operation must require confirmation if it could trigger an external action; passive health checks do not.
- **missing:** A per-surface durable cursor and monotonic sequence number for commands, audio delivery, playback acknowledgement, browser results, and Mac receipts.; A relay convergence endpoint that compares pendant, relay, Mac, and browser cursors and reports missing/duplicate/conflicting edges.; Pendant firmware telemetry for download, start-playback, interruption, and acknowledgement, including offline queue depth and a monotonic clock.; Mac and browser heartbeat contracts that distinguish offline, stale, connected-but-not-ready, and fully observed.; A small owner-facing status surface and spoken vocabulary for converged, pending, divergent, and unverifiable states.


## Changes it proposed to its own stack

### `integration` — Add an evidence-capsule contract shared by pendant, relay, Mac, and browser: each event carries eventId, source, occurredAt, observedAt, state (observed_done, delivered, queued, failed, unknown), claim, evidenceRefs, freshness/expiry, and correlationId. The reducer must refuse to upgrade queued or stale observations to success, emit contradiction records when sources disagree, and expose a typed capsule to faculty-action and receipts. Mac readiness=false and browser offline must produce unknown—not failure or success.
- **owner gets:** The owner will hear what really happened after a dropped connection, rather than a confident but wrong “done.” They can distinguish “the pendant heard it,” “the relay delivered it,” “the Mac completed it,” and “nobody can currently verify it.”
- effort: Medium-high: shared schema and reducer, adapters for pipeline/jobs/browser commands, durable relay cursor/ack endpoint, and receipt/dashboard rendering; then fault-injection tests for dropouts and late delivery.  ·  risk: Old or duplicated events could create apparent contradictions; mitigate with idempotency keys, monotonic per-source sequence numbers, bounded retention, and displaying unresolved conflicts. Roll back by keeping the current receipt path as a compatibility projection.
- cost: Negligible runtime/API cost for deterministic joins; roughly 1–2 KB metadata per event in D1/local JSON, plus small dashboard storage. No model call needed except optional spoken compression.  ·  latency: Sub-100 ms local reduction; relay reconciliation adds one bounded read on reconnect. It must not delay pendant audio playback.
- security: Capsules should contain redacted claims and hashes/IDs, not page bodies, message text, or secrets. Access is scoped by job/session and bearer-authenticated; evidence links remain local where possible.
- depends on: Durable relay event cursor and acknowledgement semantics; Terminal Mac job receipts and explicit unknown state; Browser command results with request/tab/session IDs; Clock/monotonic timestamp capture on pendant and Mac


## What it asked for

_Nothing._
## Its own summary

Fresh truth established: relay and Mac bridge are reachable, but Mac automation is not ready (Accessibility and Screen Recording are both ungranted); Chrome is offline with 3 queued commands. A real pipeline run proves 24 kHz mono output (160.8 KiB, 3.43 s, no clipping), but its captured input telemetry is 15,625 Hz, so 24 kHz is not yet proven end-to-end. I recorded these facts, notified faculty-action/judgement, and proposed a new cross-surface “What happened while I was away?” timeline plus an evidence-capsule contract that distinguishes observed_done, delivered, queued, failed, and unknown.

**Biggest unknown:** The authoritative pendant-side lifecycle and continuity acknowledgement state remain unavailable: we cannot yet prove whether a downloaded 24 kHz response was actually played, interrupted, or acknowledged on the gadget, nor reconcile its clock with Mac/relay event time. The implementation still needs a shared event schema, relay cursor/ack query, terminal Mac/browser adapters, and pendant playback telemetry.

