# Harness derivation — faculty-perception — round 209

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live browser context** — At the live probe, Safari extension is online with active tab https://www.youtube.com (tabCount 2), while its stored affinity includes sessionId url:https://news.google.com/search; this is a current context mismatch, not an inferred historical state.
  - evidence: GET /ops/snapshot at 2026-08-08T23:59Z returned browser.devices[0].tabUrl=https://www.youtube.com and affinity[0].sessionId=url:https://news.google.com/search.
- **pipeline delivery contradiction** — A live pipeline run for the scheduled news brief is relay_result done but delivery state held_by_relay with awaitsDevice=true, playbackActive=false, heard=unknown; its TTS telemetry reports 9,824 ms and 471,570 PCM bytes while event text says 58.5 seconds of audio.
  - evidence: GET /pipeline returned pipelineId job_a3740055-b1c1-4b08-bccb-3615ea4af7cd with delivery and tts event fields.
- **mac permissions and relay liveness** — The Mac local agent is currently ready with Accessibility, Screen Recording, and required automation permissions granted; the relay is reachable and the Mac bridge is online, while no pendant is registered.
  - evidence: GET /ops/status and discover devices at round 209.

## Capabilities it proposed

### "Make sure scheduled briefings reach me even when the pendant is unavailable."
- **useful because:** Today a completed Mac run can leave 471 KB of audio held at the relay with the pendant absent, and the owner receives no alternate delivery. This would detect that precise state, produce a short text/notification fallback on the Mac, and retain the full audio for later instead of silently losing the briefing.
- **path:** relay → pendant → mac-planner → browser → dashboard
- **model tier:** background model for classification and concise fallback drafting; no realtime call unless the owner asks a follow-up
- **latency:** Detect within 60 seconds of a routine result; fallback notification in under 5 seconds after the relay reports held_by_relay.
- **cost:** ~$0.001–$0.01 per routine, dominated by one short summarization; zero model cost when the existing brief text is already available.
- **security:** Fallback may expose briefing text in a macOS notification or browser surface; honor the existing routine sensitivity and require confirmation before sending outside the device. Never claim the pendant heard it.
- **missing:** A relay-to-Mac delivery-policy event carrying held_by_relay/awaitsDevice and an expiry, rather than requiring inference from pipeline traces; A Mac notification or browser inbox target for routine fallback; A user policy for which routines may be text-fallbacked and how long audio remains valid

### "Before you tell me a routine finished, check that its evidence agrees and explain any contradiction."
- **useful because:** The live pipeline contains a concrete contradiction: the spoken text claims 58.5 seconds of audio while the same run's telemetry reports 9.824 seconds and 471,570 bytes. A perception fence should prevent a false 'done' or misleading owner report when duration, byte count, stage state, and delivery state disagree.
- **path:** relay → mac-planner → faculty-perception → faculty-judgement → dashboard
- **model tier:** cheap deterministic validator first; background model only to phrase an explanation when fields conflict
- **latency:** Under 100 ms for numeric/state checks; under 2 seconds for a human-readable explanation.
- **cost:** Near-zero for validation; <$0.001 for an occasional explanation.
- **security:** Telemetry can include command text and snippets; keep raw payload local, send only field names and bounded discrepancy facts to any model. Never auto-retry or mark success based on a model judgment.
- **missing:** A shared evidence contract defining which fields are authoritative for audio duration, bytes, and completion; A relay/local-agent status that can be 'contradictory' instead of collapsing to completed/failed; A reader in the owner-facing briefing and job-status paths that surfaces the contradiction and withholds completion language

### "Before acting in my browser, tell me if the active tab and the session you remember are different."
- **useful because:** The live browser is on a YouTube tab while the stored session affinity still points to news.google.com. Acting on the remembered session without noticing this split can click or read the wrong site. The guard would compare fresh extension state, session affinity, and the requested target, then pause with a one-sentence clarification instead of guessing.
- **path:** browser-extension → mac-vision → mac-planner → faculty-perception → faculty-judgement
- **model tier:** deterministic URL/host comparison; use the realtime model only to ask the short clarification during an active voice turn
- **latency:** Under 300 ms before any browser action; clarification within one voice turn.
- **cost:** Zero for comparison; negligible realtime tokens for a clarification.
- **security:** URLs and tab titles can reveal sensitive activity. Keep comparisons on the Mac, redact query strings by default, and require confirmation when the mismatch involves a logged-in or destructive action.
- **missing:** A first-class browser context snapshot with active tab, session affinity, last-seen timestamps, and confidence in one schema; A precondition hook in browser_run_actions/mac vision that can block execution on context mismatch; An explicit owner policy for when a host change is safe versus when to ask

### "When I ask for a briefing, tell me only information that was fresh at the requested cutoff, and say exactly what was too old or unverifiable."
- **useful because:** A scheduled news brief can be generated successfully while its sources, cached browser pages, or relay-held audio are stale. The owner needs temporal truth, not merely a completed run. This would enforce per-claim freshness across browser captures, Mac research, and relay scheduling, then speak a bounded uncertainty statement instead of silently blending old and new material.
- **path:** browser-extension → mac-planner → relay → faculty-perception → faculty-judgement → pendant
- **model tier:** Cheap deterministic timestamp/provenance checks first; background model for compressing the resulting freshness ledger into one spoken sentence.
- **latency:** Under 2 seconds of validation after research completes; no more than 3 seconds added to a scheduled brief.
- **cost:** Near-zero for timestamp checks; <$0.005 per briefing for a short uncertainty summary.
- **security:** Source URLs, page titles, and private browser captures must remain local unless the owner explicitly requests cloud research. Never treat an undated page as current merely because retrieval succeeded.
- **missing:** A common source-observation record carrying observedAt, publishedAt when known, requested cutoff, and freshness verdict; Browser and relay research paths that preserve those timestamps instead of returning only text; A speech/template layer that names stale or unverifiable claims without exposing sensitive URLs

### "Let the pendant and Mac agree on whether I am available before interrupting me, and queue low-priority things without making me manage another setting."
- **useful because:** The relay, browser, and Mac can each be alive while the owner is actually in a call, speaking to someone else, or actively typing. A single availability decision using pendant voice activity, Mac foreground/meeting state, and browser activity would prevent badly timed interruptions while preserving urgent items.
- **path:** pendant → mac-planner → browser-extension → relay → faculty-perception → faculty-judgement
- **model tier:** Deterministic state machine for availability and priority; realtime model only for interpreting an ambiguous spoken override.
- **latency:** Availability updates within 1 second; interruption decision under 100 ms; spoken override responds within one voice turn.
- **cost:** Near-zero steady-state; <$0.001 for rare ambiguous overrides.
- **security:** Microphone-derived availability must be reduced to short-lived state, not uploaded audio. Calendar titles and active-window names should stay on the Mac. Emergency/high-priority policy must be explicit and never inferred from model confidence.
- **missing:** A cross-surface availability protocol with leases, expiry, confidence, and reasons; A pendant-side local occupancy signal that works offline, rather than relying on relay registration; Scheduler and announcement delivery that honor the lease and expose why an item was deferred; A user-editable priority/escalation policy

### "After you change something on my Mac, let me ask 'what changed?' and hear a before-and-after explanation tied to the exact file, browser page, or app state."
- **useful because:** Today action receipts and browser results can establish that an operation ran, but they do not give the owner a compact, cross-surface explanation of the resulting state. This would join Mac action ledgers, browser provenance, and relay speech into a durable, owner-auditable change narrative with an undo path where available.
- **path:** mac-planner → mac-vision → browser-extension → relay → pendant → dashboard
- **model tier:** Deterministic diff and receipt join first; cheap background model to phrase the spoken explanation, never to invent a change.
- **latency:** Record the change synchronously; answer a follow-up in under 2 seconds.
- **cost:** Near-zero for structured diffs; <$0.005 when summarization is needed.
- **security:** Before/after values may contain secrets. Redact credentials and private page content at capture, retain only bounded hashes/snippets, and require confirmation before replaying sensitive values aloud. Destructive undo remains confirmation-gated.
- **missing:** A cross-surface change identifier joining action ledger step, browser command/result, evidence capsule, job receipt, and spoken response; A durable owner-facing change journal with redaction and retention rules; Diff adapters for files, browser mutations, and application state; A read-only voice/dashboard query over that journal


## Changes it proposed to its own stack

### `routines` — Add a cross-surface routine collision and freshness gate: before scheduler execution, group enabled routines by local firing instant and semantic overlap, compare their last successful run and output receipts, then present one merged run or ask which to keep. Record the decision and suppress only the duplicate invocation, never delete routines automatically.
- **owner gets:** The owner currently has multiple daily routines at 07:00 and multiple at 17:00, including overlapping briefs. This can produce duplicate spoken interruptions and stale audio while making the system look healthy. One coherent brief is more useful than several 'completed' runs.
- effort: Medium: scheduler-side grouping, Mac timezone resolution, lightweight semantic similarity, and a reversible decision record in the routine-run history.  ·  risk: A genuinely distinct routine could be merged or skipped. Recovery is a preview-first collision report, conservative threshold, and one-click 'run separately' override; no automatic routine deletion.
- cost: <$0.01/day for semantic comparison if needed; deterministic timestamp grouping is free.  ·  latency: Adds <1 second before a scheduled run; no impact on audio generation.
- security: Routine names and commands stay within relay/Mac stores; do not send command text to an external model unless the owner permits it.
- depends on: GET /routines; GET /routines/:routineId/runs; POST /routines/:routineId/run; GET /pipeline; GET /ops/snapshot; Authoritative America/New_York timezone for Mac-resolved firing times


## What it asked for

_Nothing._
