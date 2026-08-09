# Harness derivation — faculty-judgement — round 164

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **owner timezone and interruption policy** — The Mac's authoritative routine timezone is America/New_York, while the owner's projected preference says America/Chicago; no owner interruption/disclosure policy has been supplied. I must not silently use either as the owner's physical timezone or invent spoken-content rules.
  - evidence: discover:owner remembered.text plus granted context 'authoritative routine timezone and quiet-hours policy' and declined owner interruption/disclosure-boundary requests

## Capabilities it proposed

### "“Test the pendant and audio bridge end to end now, and tell me if it is healthy.” The Mac should run a bounded USB-serial test: exercise microphone upload, 24 kHz downlink, interruption, reconnect, and the ESP32 sink; collect on-device counters and produce a pass/fail report plus a reviewable bug draft if a criterion fails."
- **useful because:** The hardware is physically connected and testable today, but the owner currently has to know firmware scripts, UART commands, and acceptance thresholds. This turns a fragile lab procedure into a one-sentence health check and catches regressions before daily use.
- **path:** mac-terminal → mac-bridge → pendant → relay → dashboard
- **model tier:** background/cheap deterministic runner for the test; expensive reasoning only interprets anomalous results and writes the short owner explanation.
- **latency:** A 60–120 second bounded test is acceptable when explicitly requested; status milestones should be available within 5 seconds and the test must never seize the microphone or interrupt an active conversation without confirmation.
- **cost:** <$0.02 per run, mostly zero-cost shell/serial/audio measurements; model cost only for a failure summary and draft.
- **security:** USB serial commands must be an allowlisted test profile, never arbitrary shell from a voice utterance. Do not upload raw microphone audio or UART secrets. Store only metrics, firmware/build identifiers, and a redacted log excerpt. Bug filing remains a local or reviewable draft, never an automatic external submission.
- **missing:** A typed Mac action/test runner that can open both live serial ports, flash or reset only with explicit confirmation, and collect synchronized counters; A deterministic test profile encoding the existing numeric criteria (alias rejection, codec <100%, mic drops, tx starvation, no pre-speech audio); A join between test-run ID, pipeline artifact, pendant delivery events, and pendant_diagnostics_and_bug_draft; A safe USB-serial permission/locking policy so the normal bridge and test cannot write concurrently

### "“For each scheduled routine, prove it delivered what its command promised—not merely that the job completed.” At the end of a routine, check typed postconditions (for example, battery and Wi‑Fi fields are present, a cited briefing exists, audio is playable, and an evening summary contains three next actions), report any partial fulfillment, and queue a repair or review instead of silently marking it successful."
- **useful because:** The current routine status can say completed while a downstream stage failed, produced an empty result, or never reached the owner. This gives the owner dependable automation rather than green checkmarks that hide missing work.
- **path:** relay → mac-bridge → pendant → dashboard
- **model tier:** Cheap deterministic postcondition checkers per routine; background model only extracts a proposed schema from a new routine command, always requiring owner review before it becomes enforcement.
- **latency:** Add at most 2 seconds to a routine completion path; deferred checks may finish within 30 seconds. Never block or retry an external mutation automatically.
- **cost:** Near-zero for typed checks; <$0.01 when a model is needed to classify an untyped result or draft a repair.
- **security:** Postconditions must validate structure and provenance, not trust model prose. A failed check may create a local draft or reminder, but cannot resend mail, buy, delete, or submit anything. Show the exact evidence and policy rule behind each verdict.
- **missing:** A durable routine contract schema mapping command intent to postconditions, freshness windows, and acceptable partial results; A postcondition evaluator that can read routine output, pipeline/audio state, receipts, and pendant delivery ACKs under one routine-run ID; A true cross-surface routine-run correlation key; current relay, Mac, and browser IDs are not foreign keys; A safe remediation planner that proposes (rather than executes) a repair and routes it through autonomy_policy_evaluate

### "“Show me where your judgement has been wrong lately, and let me correct the rule once.” Give me a weekly trust report of interrupted, deferred, suppressed, and acted-on items, group mistakes by policy field/source, and let one owner correction update future decisions with an undoable versioned policy change."
- **useful because:** The system already makes triage and autonomy decisions, but the owner cannot see whether it is too interruptive, too quiet, or trusting a bad source. A compact error-driven review turns opaque automation into something that improves from the owner's actual corrections instead of silently accumulating bad defaults.
- **path:** pendant → relay → mac-bridge → dashboard → browser-extension
- **model tier:** Background deterministic aggregation and policy-diff generation; use the expensive model only to phrase clusters in plain language. The policy evaluator remains the final decision authority.
- **latency:** A report can be generated in under 10 seconds weekly; a correction should affect subsequent decisions within one minute and never retroactively mutate an already executed action.
- **cost:** <$0.02 per weekly report; event aggregation is local/SQL and dominates no API spend.
- **security:** Store event summaries and policy decisions, not notification bodies or secrets. Sensitive items appear as redacted counts unless the local dashboard explicitly reveals them. Policy edits require explicit confirmation, immutable versioning, and a rollback; spoken relay cannot request sensitive reveal.
- **missing:** A durable decision journal linking attention_arbitrate/autonomy_policy_evaluate outputs to the eventual owner outcome; A feedback endpoint for owner labels such as correct, too-late, unnecessary, wrong-source, and missed; A versioned policy store and rollback path shared by relay, Mac, browser, and pendant; A retention rule that removes detailed event text while preserving aggregate calibration statistics

### "“Make the pendant last through the rest of my day without losing the conversations that matter.” The system should forecast pendant, bridge, and Mac energy demand from upcoming routines and queued audio, then choose reversible quality, batching, upload, and briefing-time tradeoffs; it must preserve urgent owner-requested work and explain what was deferred or degraded."
- **useful because:** Today the owner has no way to express an outcome such as 'stay available until my commute ends.' Battery-saving decisions are fragmented across codec work, scheduled routines, audio queues, and Mac jobs. A fleet-wide energy budget would make the pendant dependable in real life rather than merely functional while tethered.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** Deterministic forecast and policy engine for telemetry, queue sizes, routine deadlines, and codec profiles; background model only summarizes tradeoffs. Realtime is unnecessary.
- **latency:** A forecast should return within 5 seconds; adaptations happen at safe utterance or job boundaries and must never interrupt an active owner conversation.
- **cost:** Under $0.01 per forecast; computation is local and telemetry-based. No additional model call is needed for ordinary adaptations.
- **security:** Expose coarse energy estimates, not raw location or speech. Never silently disable the privacy latch, safety alerts, or owner-requested capture. Any reduction in audio quality, upload delay, or routine execution must be visible and reversible; external side effects remain subject to autonomy_policy_evaluate.
- **missing:** Authenticated battery, charging, radio, codec-load, and queue telemetry from both physical chips; A shared energy budget and forecast model spanning pendant, ESP32 bridge, Mac jobs, and relay routines; Safe runtime controls for selecting among already-verified audio profiles and deferring non-urgent work; A durable owner policy describing protected work, acceptable audio degradation, and the deadline at which the forecast should fail closed


## What it asked for

_Nothing._
