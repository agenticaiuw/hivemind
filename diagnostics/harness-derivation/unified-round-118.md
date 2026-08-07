# Harness derivation — unified — round 118

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-contract** — Live pipeline telemetry currently shows pendant input at 15,625 Hz with 16 kHz Opus uplink, while Mac TTS reports 24,000 Hz mono PCM output (74.0 KiB, 1,578 ms). The system labels the latter as 24 kHz but has no demonstrated end-to-end capture/playback contract.
  - evidence: GET /pipeline returned inputTelemetry {sampleRate:15625, format:pcm-s16le, uploadedFormat:pcm} and a TTS event meta {sampleRate:24000, format:s16le, channels:1}; get_hardware_spec(audio) reports 15,625 Hz capture and Opus 16 kHz/16 kbps.

## Capabilities it proposed

### "“I got disconnected—continue the task from exactly where it stopped, tell me what already happened, and never do a step twice.”"
- **useful because:** LTE-M is half-duplex and the pendant can lose its link mid-conversation or while a Mac/browser job is running. Today the owner cannot distinguish a completed side effect from an interrupted one, so retrying can duplicate messages, bookings, or form submissions. This gives one safe recovery flow: the pendant supplies the interaction/task identity, the relay reconciles durable receipts, the Mac and authenticated browser resume only from an idempotent checkpoint, and the pendant speaks a compact recovery summary when it reconnects.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Use the cheap background model for checkpoint reconciliation and receipt summarization; reserve gpt-realtime-2.1 for the owner's short reconnect conversation and final spoken confirmation.
- **latency:** On reconnect, local status should appear within 1 s; receipt reconciliation within 3 s; any resumed Mac/browser step may take its normal task latency. No expensive model call unless receipts conflict or intent is ambiguous.
- **cost:** Usually <$0.01 per recovery (mostly D1/R2 and one small background-model summary); conflicts may require one realtime turn and cost materially more.
- **security:** Persist only opaque task IDs, action hashes, and minimal outcome metadata—not page contents or secrets. Never auto-resume an irreversible or ambiguous step; require the owner's pendant button/voice confirmation for send, purchase, delete, or submit. Surface before/after evidence and an undo link where available.
- **missing:** A cross-surface task journal with monotonic checkpoints and idempotency keys shared by relay, Mac jobs, and browser commands; A reconnect reconciliation endpoint that can classify completed, in-flight, and unknown side effects; Browser durable runner/result stream (the existing router still lacks persistence and retries); Pendant-local checkpoint gesture/status indicator and a small reconnect receipt cache; Explicit resume policy for unknown irreversible actions

### "“What is the real state right now?” — reconcile my pendant, relay, Mac, browser, and any running task, and tell me what is live, stale, contradictory, or waiting for me."
- **useful because:** Today each surface can report a locally plausible state while the owner still cannot know whether the pendant is connected, a Mac job committed, a browser tab is current, or an approval is blocking progress. This is a distinct cross-surface truth service, not another task runner or briefing: it correlates freshness and causal links, calls out contradictions, and gives one short spoken answer with drill-down evidence.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic freshness/receipt correlation first and a cheap background model to phrase the result; use gpt-realtime-2.1 only when the owner asks a follow-up or evidence is genuinely contradictory.
- **latency:** Return a compact status in under 2 seconds from cached telemetry; refresh only stale surfaces in parallel with a 5-second ceiling. Never block the answer on a sleeping Mac.
- **cost:** Typically <$0.005 using existing telemetry and a small summary; conflicts may require one planner call. No raw audio or page content is needed.
- **security:** Return only owner-scoped metadata, task labels, timestamps, and redacted receipt summaries; never expose secrets, page text, or another session's status. Treat stale data as unknown rather than inventing health. Require confirmation before any offered repair action.
- **missing:** A shared freshness and causal-correlation schema linking pipeline IDs, relay jobs, Mac jobs, browser command IDs, and pendant sequence numbers; A read-only federation endpoint that snapshots all surfaces atomically enough to label observations as consistent or contradictory; A dashboard and spoken response format that distinguishes offline, stale, blocked-on-approval, committed, and unknown; Per-surface monotonic sequence/heartbeat semantics; current browser and pipeline records are not a common timeline


## Changes it proposed to its own stack

### `integration` — Implement a single append-only task ledger spanning relay, Mac jobs, and browser commands. Every logical task gets a taskId; every side effect gets a monotonic step number, idempotency key, precondition hash, surface, and receipt state (planned, started, committed, failed, unknown). Write the commit receipt before acknowledging completion, reconcile unknown steps on reconnect, and expose one GET endpoint that joins Mac job receipts with browser command results and pipeline disconnects. Resume only the first uncommitted reversible step; quarantine unknown irreversible steps for explicit pendant approval. Add crash/reconnect contract tests with duplicated requests and late results.
- **owner gets:** After a dropped LTE-M link or sleeping Mac, the owner can safely say “continue” and receive a truthful one-sentence account of what happened, instead of guessing and risking duplicate sends, purchases, or submissions.
- effort: Medium-high: shared schema and migrations, relay integration, Mac/browser adapters, and failure-injection tests across at least four components.  ·  risk: A false committed receipt could suppress a needed action; a false unknown state could pause work. Recover with immutable raw receipts, visible quarantine, explicit approval, and existing per-job undo/cancel paths. Do not claim exactly-once semantics for external systems without their idempotency support.
- cost: Negligible storage/compute per step; one small background reconciliation call on reconnect. No audio cost unless a spoken receipt is requested.  ·  latency: ~10–50 ms ledger writes locally/relay; reconnect reconciliation target under 3 s, with normal external action latency unchanged.
- security: Ledger must redact payloads and page text, encrypt or access-control task metadata, bind records to the authenticated owner/session, and make approval tokens single-use and short-lived.
- depends on: Durable browser job runner and result stream (chg-16bc5dee remains open); A pendant-local checkpoint/reconnect receipt mechanism (requested device skill, not yet granted); An explicit policy for unknown irreversible external side effects; Owner manually granting Accessibility/Screen Recording if GUI-only Mac steps must participate; AppleScript/browser routes remain usable without it

### `firmware` — Add an end-to-end audio contract probe that runs at boot and before the first live turn: the pendant reports actual I2S capture rate, encoded Opus rate/bitrate, frame loss, and playback format; the relay and Mac pipeline echo the negotiated contract in telemetry and reject or explicitly resample mismatches. Persist a compact pass/fail receipt on microSD and expose it in the pipeline/dashboard. In particular, flag the currently observed split of 15,625 Hz pendant capture/16 kHz Opus against 24 kHz Mac TTS PCM rather than silently calling the path 24 kHz superwideband.
- **owner gets:** The owner gets intelligible speech instead of a nominal “24 kHz” label that hides a narrower microphone path, and knows before a conversation whether the wearable can actually deliver the promised quality.
- effort: Medium: firmware I2S/codec telemetry, relay schema, one pipeline validation route, and hardware-in-the-loop sample-rate/packet-loss tests.  ·  risk: A strict validator could block a usable degraded call. Recover by allowing an explicit “degraded but usable” mode, speaking the reason only when quality is materially affected, and keeping the last known-good contract receipt.
- cost: Tiny telemetry payload and one inexpensive validation operation per session; no additional model call. Hardware changes are not required for detection, but true 24 kHz capture would require a production microphone/clock path beyond this DK.  ·  latency: Under 100 ms at session start; no steady-state latency change.
- security: Telemetry contains technical audio metadata only; do not upload raw microphone samples as part of the probe. Authenticate receipts to the paired pendant and relay.
- depends on: Authoritative 24 kHz audio target architecture and end-to-end acceptance thresholds (still pending context); Audio-path preflight receipt skill/tool (requested but not yet granted); A production pendant audio design that can physically capture at the target rate; current nRF9160 DK reports 15,625 Hz capture

### `context` — Create a cross-surface truth snapshot service with a typed observation envelope: {surface, entityId, observedAt, sourceSequence, status, freshnessDeadline, causalityIds, confidence, redactedSummary}. Collect pendant heartbeat/audio acknowledgements, relay job state, pipeline events, Mac job receipts, browser heartbeat/tab state, and approval blockers in parallel; derive contradiction groups and stale/unknown labels without allowing a language model to overwrite raw observations. Expose a read-only snapshot plus evidence links to the spoken agent and dashboard, and add fixtures for delayed, duplicated, and contradictory events.
- **owner gets:** When the owner asks for the real state, they get a truthful answer instead of whichever surface responded last—for example, “browser is online, the task is complete, but the pendant has not acknowledged the reply for 90 seconds.”
- effort: Medium-high: schema/migration, adapters for five event sources, freshness policy, redaction, and dashboard rendering.  ·  risk: Incorrect freshness thresholds can create noisy false alarms or hide a real outage. Recover with source-specific deadlines, visible timestamps, raw evidence links, and conservative UNKNOWN rather than optimistic OK.
- cost: Low D1/storage and parallel HTTP overhead; no recurring model cost. A small summarizer call only when the owner requests natural-language phrasing.  ·  latency: ~100–300 ms for cached snapshots; up to 5 s for stale-source refresh, while returning the cached answer immediately.
- security: Strict owner/session scoping and redaction are mandatory; task identifiers may be exposed, but page contents, audio, and credentials must not enter the federated snapshot.
- depends on: The existing pipeline/job/browser IDs must be propagated consistently across event writers; A durable task ledger or equivalent causal IDs for actions that cross Mac and browser; Pendant heartbeat and acknowledgement sequence telemetry; No Accessibility permission is required for read-only AppleScript/browser/relay observations; GUI-only status remains explicitly unknown when TCC is absent


## What it asked for

_Nothing._
## Its own summary

Discovered a concrete audio contract gap and a cross-surface reconnect gap. Live telemetry confirms 15,625 Hz pendant capture/16 kHz Opus versus 24 kHz Mac TTS, without an end-to-end validator. Proposed an audio contract probe and a task ledger that safely resumes interrupted Mac/browser work without duplicate side effects. Browser bridge and relay are online; Mac GUI readiness remains blocked by owner TCC settings.

**Biggest unknown:** The authoritative 24 kHz acceptance thresholds and production pendant constraints are still unavailable, so I cannot say whether true 24 kHz capture is physically achievable on the current pendant.

