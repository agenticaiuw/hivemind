# Harness derivation — relay-realtime — round 282

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What changed across my digital life since I last checked, and is any of it urgent?” Give me one short spoken answer with evidence, not a generic briefing."
- **useful because:** Today the owner must query Mac history, authenticated browser watches, and pendant health separately. This would make the worn device a trustworthy cross-surface change detector: it distinguishes a real change from a stale or unreachable surface and names the source before speaking.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use the realtime model only to clarify the spoken question and summarize. Fan out cheap/read-only collectors on the relay: Mac ops/history and state, browser watch reports and session checks, and device health; use the realtime tier again only for the final ranked sentence.
- **latency:** 4–8 seconds for a normal answer; partial results should be explicitly labeled if one surface is offline.
- **cost:** Roughly one realtime turn plus 3–5 cheap reads; most cost is the final synthesis and the context needed to explain provenance.
- **security:** The answer may reveal authenticated browser data over the voice channel. Surface-level permissions and sensitivity labels must be honored, and every claim needs a source timestamp and an “unavailable” state rather than being inferred from silence. No mutations occur.
- **missing:** A relay fan-out aggregator that queries Mac, browser-watch, and pendant-health surfaces in one request; A normalized change/provenance schema with freshness and reachability fields; A compact spoken renderer that cites the source without dumping private page contents

### "“That thing you just tried failed. Read the failure, fix the cause, and try again without making me repeat the task.”"
- **useful because:** A job status endpoint can tell the owner that something failed, but today the owner has to reconstruct the original request and error before asking again. This turns the pendant into a recovery front door: it binds the spoken “that” to the latest failed job, gives the Mac planner the receipt and relevant logs, and retries only the corrected plan.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use the realtime model for reference resolution and a one-sentence explanation. Let the cheaper Mac planner inspect the failed job receipt/log, produce a repair plan, and execute it; use the realtime model only to summarize the result.
- **latency:** Acknowledge in under 1 second, then 5–20 seconds for diagnosis/retry. If diagnosis is incomplete, say exactly what remains rather than silently repeating the failed action.
- **cost:** One short realtime turn plus one planner invocation; log and receipt retrieval are cheap. Cost is dominated by planner context if the failed workflow was large.
- **security:** Automatic retry can duplicate a mutation. The repair planner must use the original job's idempotency/receipt data, identify which steps already succeeded, and never replay them blindly. The owner prefers no confirmation for reversible actions, but an ambiguous or irreversible retry should be reported as needing attention, not guessed.
- **missing:** A failure-recovery route that joins GET /jobs/:jobId, receipts, and journal/log evidence into a bounded planner input; An idempotency-aware retry/resume primitive that marks completed steps and starts at the first failed step; Reference resolution from “that” to the latest failed job in the live voice session

### "“Run a hearing and microphone check on my pendant now, and tell me whether it is healthy.”"
- **useful because:** The pendant and audio bridge are physically connected over USB today, but the owner has no spoken, end-to-end diagnostic. A single request could test the actual worn hardware, serial transport, microphone capture, 24 kHz Opus decode, speaker path, packet loss, and SD fallback, then explain which component is failing instead of making the owner run scripts.
- **path:** pendant → relay → mac-terminal → dashboard
- **model tier:** No expensive reasoning is needed for measurement: a deterministic diagnostic worker runs the test and computes thresholds. The realtime model translates the measured result into one short spoken answer and can answer a follow-up question.
- **latency:** Start feedback immediately; complete the normal test in 10–30 seconds. The owner should hear progress if a serial or audio phase takes longer than 3 seconds.
- **cost:** Negligible model cost; one deterministic diagnostic job and a short synthesis. Hardware test time and USB serial/audio capture dominate.
- **security:** The test must not record or retain ordinary speech. Generate synthetic tones or a controlled test phrase, discard raw captures after measurements, and require an explicit physical press or spoken command to start because it powers the microphone and speaker. Firmware identity and counters can be reported; private audio cannot.
- **missing:** A signed diagnostic command understood by the nRF9160 and ESP32 bridge over their live USB serial links; A relay/mac-terminal runner that captures raw measurements and returns a structured diagnostic receipt; A deterministic acceptance suite for the already-shipped 24 kHz path: alias rejection, codec CPU, mic drops, tx starvation, and silent preamble; A pendant progress/error surface that works with its one LED and existing speaker


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: (1) a provenance-backed cross-surface change digest spanning Mac, authenticated browser watches, and pendant health; (2) voice-directed diagnosis and repair of the latest failed job without repeating the original task; and (3) a deterministic spoken end-to-end pendant hearing/microphone self-test using the live USB-connected hardware. The first is the highest-value daily capability because it turns fragmented, stale surface state into one trustworthy answer. The main missing work is orchestration and evidence normalization, not another model or another queue.

**Biggest unknown:** The exact live route schemas and permissions for the ops/history, watch-report, device-health, job-journal, and diagnostic surfaces are still unclear. I was explicitly told not to discover further this round, so the next implementation step must verify those contracts before wiring the aggregators and USB diagnostic runner.

