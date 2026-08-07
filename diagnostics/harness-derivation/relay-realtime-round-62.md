# Harness derivation — relay-realtime — round 62

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working after I stop talking, and leave me a ready-to-review result I can hear on the pendant when I come back."
- **useful because:** This is the missing glue for long tasks: you can hand off work to the Mac or browser, let it run, and later get a concise, trustworthy status and summary without needing the Mac awake.
- **path:** relay → mac-bridge → browser → relay → pendant
- **model tier:** Realtime for handoff and follow-up, cheaper planner tier for the work, and a small summarizer for the final spoken result.
- **latency:** Fast handoff (under a second when possible). Results can arrive minutes later; the spoken summary must be immediate once available.
- **cost:** Low relay cost per invocation; the expensive part is downstream planning/extraction, which should run on the Mac/browser tiers.
- **security:** Summaries may include sensitive account data. Store only what’s needed for the spoken recap, keep provenance, and avoid leaking private page content beyond the owner’s devices/services.
- **missing:** A durable job runner or scheduler for non-interactive continuation; A cross-surface result inbox with provenance and retention rules; A way to package a short audio queue for the pendant when the Mac is asleep

### "“Do that on my Mac, and if you need a choice from me, ask me on the pendant and continue when I answer.”"
- **useful because:** Today a spoken request handed to the Mac must either be guessed, fail, or end as a queued job; the owner cannot resolve an ambiguity while away from the Mac. This would make the wearable a true conversational front door for multi-step Mac/browser work rather than a one-shot command channel.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use relay-realtime only to acknowledge and ask the short clarifying question; mac-planner (gpt-5.6-luna) plans the work; mac-vision/browser-extension perform it; a cheaper background worker watches the job and wakes the relay when input is needed.
- **latency:** Immediate acknowledgement under 500 ms; clarification prompt within 2 s of the planner detecting ambiguity; resume within 2 s after the owner's spoken answer. No requirement that the Mac remain attended, but its agent must be online for execution.
- **cost:** About one realtime turn for each clarification plus normal planner/action costs; idle jobs should cost near zero with Durable Object alarms or event callbacks. The dominant extra cost is planner context rehydration after a pause, which should be stored as a compact typed state rather than replaying the whole transcript.
- **security:** The relay must bind each question and answer to the authenticated owner, job, and target session; stale or late answers must not mutate a different job. The question should state the consequential choice and current options, while preserving the owner's maximum-access/no-confirmation policy for ordinary reversible actions. Send only the minimum pending plan/context to the pendant and retain an auditable answer and action receipt.
- **missing:** A durable conversational-job state machine with WAITING_FOR_OWNER_INPUT, timeout, cancellation, and resume transitions; A push path from Worker to the pendant and a correlation protocol for spoken answers; Planner output schema for explicit questions/options instead of silently guessing; Mac/browser executors that can suspend and safely resume with the same session/tab affinity; A compact job checkpoint store and dashboard view of pending questions

### "“Stop whatever you’re doing on my computer right now.” (press and hold the pendant button)"
- **useful because:** A queued or multi-step Mac/browser task can outlive the owner's intent. Today the owner has no reliable physical interrupt while away from the Mac; a spoken stop may be missed during an active turn. A pendant-level abort gives the owner an immediate, substrate-independent kill switch without requiring access to a screen.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** No expensive reasoning is needed: the pendant firmware emits a signed abort event, the relay routes it immediately, and local Mac/browser executors enforce cancellation. Realtime only confirms the stop and reports which job acknowledged it.
- **latency:** Abort signal should leave the pendant in under 200 ms and reach each executor within 1 s; confirmation within 2 s. If disconnected, the device must retain the abort until uplink returns and the relay must treat it as scoped to the most recent active job, not as a generic future denial.
- **cost:** Negligible model cost; a small persistent event and one short realtime confirmation. Engineering cost is concentrated in cooperative cancellation at every executor boundary and testing races between action completion and abort receipt.
- **security:** The event must be authenticated and monotonic, with explicit scope/job ID where known; replay must be harmless. Cancellation should stop future steps and attempt to interrupt current browser/Mac operations, then emit a receipt showing what did and did not stop. It must not delete data or roll back unrelated completed actions.
- **missing:** A pendant firmware long-press/abort event with local LED acknowledgement and a tiny offline outbox; Relay fan-out of signed aborts to all executors plus idempotency and race handling; Cancellation tokens checked by mac-planner, mac-vision, browser extension, and shell/action runners; A job status/receipt state distinguishing cancelled, partially completed, and too-late-to-stop; A dashboard and spoken response that identify the affected job


## Changes it proposed to its own stack

### `integration` — Introduce a cross-surface "result inbox": a durable store of job outputs (status, short spoken summary, evidence links, and next-step affordances) keyed by a stable task id. The relay can query it to answer "what happened?" and to stream a short audio recap to the pendant; the Mac/browser can append updates as they work.
- **owner gets:** They can ask later, from anywhere, and get an accurate recap without reopening apps or waking devices.
- effort: Medium-high: define a schema, add append-only update writes from Mac/browser, add retention and redaction, and add read APIs plus a compact audio packaging format.  ·  risk: Stale or misleading summaries if updates are dropped. Mitigation: append-only logs, last-updated timestamps, and a clear "incomplete" state when evidence is missing.
- cost: Storage and a few reads per task; cheap compared to re-running work. Audio packaging adds bandwidth but remains small.  ·  latency: Slight overhead on write; big win on read because the relay can answer immediately.
- security: Must treat as sensitive: encrypt at rest, strict tenant isolation, redact secrets, and avoid storing full page contents unless necessary.
- depends on: Durable storage for job updates; A standard task id shared by relay, Mac, and browser harnesses

### `routines` — Add a scheduler primitive (cron triggers or durable alarms) to run watches/briefings at set times. The relay should only orchestrate and speak results; background work runs on cheaper tiers.
- **owner gets:** They can say "every morning" and it actually happens without keeping the Mac awake or wearing down the pendant.
- effort: High: choose one scheduling backbone, implement persistence, retries, and idempotency, and wire it to routines and page-watch features.  ·  risk: Duplicate runs or missed runs. Mitigation: idempotency keys, run windows, and receipts.
- cost: Cheaper than always-on polling; cost concentrated in scheduled runs.  ·  latency: No impact on conversational latency; background work happens off the critical path.
- security: Scheduler must not become a data exfil path; keep jobs scoped and audited.
- depends on: Durable job runner; Typed routine definitions with permissions and data-source constraints


## What it asked for

_Nothing._
