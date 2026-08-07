# Harness derivation — faculty-judgement — round 72

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Did that actually happen?” Give me a truthful answer across the pendant, relay, Mac, and browser: what was requested, what each surface confirmed, what is still only claimed, and the safest next step if anything failed."
- **useful because:** Today a top-level job can say processing while its useful event is done, or report UI success when the bridge is unreachable. The owner needs one accountable answer, not a plausible completion sentence—especially after leaving a long-running job unattended.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use the cheap background model to normalize receipts and event timelines; reserve realtime judgement for ambiguous contradictions or an owner-facing spoken answer. Never infer success from absence of an error.
- **latency:** Under 2 seconds for existing receipts/events; up to 10 seconds only when a live surface must re-check. Spoken result stays to one short sentence plus an optional detail card.
- **cost:** Usually <$0.01 per check when evidence is already stored; live re-checks and screenshots dominate cost, not reconciliation.
- **security:** Expose only task-scoped evidence, redact private page contents and secrets, and distinguish 'not observed' from 'failed.' Re-running must be limited to reversible actions; sending mail, deleting, purchasing, or submitting still requires confirmation.
- **missing:** A durable outcome-claim record linking request ID, surface, event, receipt, timestamp/TTL, and contradiction state; Event-derived terminality for pipelines/jobs instead of trusting the top-level status field; A standard action result vocabulary: confirmed, observed-only, attempted, blocked, expired, contradictory; A recovery planner that proposes but does not silently repeat an irreversible step

### "“Stop everything I asked you to do.” A deliberate long press on the pendant must immediately stop speech and issue a single cancellation across every active Mac, browser, relay, and background job—even if the network is down—and later show me exactly what was stopped, what could not be stopped, and whether anything irreversible had already happened."
- **useful because:** A person wearing an agent needs an unconditional escape hatch. Today stopping one surface does not reliably stop the others, and a disconnected pendant cannot communicate urgency. This is a safety and trust primitive, not another task workflow.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** No expensive model for the stop itself: firmware and relay perform deterministic cancellation. Use a cheap background model only to summarize the eventual receipts; use realtime only to speak the immediate acknowledgement.
- **latency:** Local audio stop and latch under 100 ms; relay cancellation fan-out under 1 second when connected. Offline cancellation is durable and must be delivered on reconnect before new work is accepted.
- **cost:** Near-zero inference cost; small durable cancellation records and one reconciliation pass dominate.
- **security:** Require an intentional long press or two-step tactile gesture to avoid accidental cancellation. Scope tokens to this owner's active work, authenticate them, reject replay, and never claim an irreversible action was undone—only whether it was prevented or already committed.
- **missing:** A firmware stop latch that works without the relay and suppresses playback immediately; An authenticated cancellation-token protocol with monotonic generation numbers and reconnect replay; Cancellation endpoints and cooperative checkpoints in Mac jobs, browser commands, pipelines, and relay work; A final cross-surface cancellation receipt that distinguishes stopped, in-flight/unknown, committed, and not-reachable


## Changes it proposed to its own stack

### `integration` — Create a cross-surface outcome ledger and evaluator. On every delegated execution, correlate requestId/idempotencyKey across job records, pipeline events, browser command results, and Mac receipts. Derive terminal state from the event graph (including done-but-unacknowledged and approval-blocked), attach evidence timestamps and TTLs, mark contradictions explicitly, and make the owner-facing response refuse the word 'done' unless a trusted receipt or independently observed result exists. Add a reversible recovery suggestion rather than an automatic retry.
- **owner gets:** The pendant will stop telling the owner that something happened when only a request was queued or an inaccessible UI claimed success. They get a reliable answer and a clear recovery path after walking away from the device.
- effort: Medium: shared schema plus event consumer, evaluator, and response adapter across relay and faculty layers; add replay tests for stale processing, missing browser bridge, duplicate events, and approval waits.  ·  risk: Late or duplicated events could produce a false terminal state; mitigate with monotonic event IDs, bounded TTLs, and an explicit contradictory/unknown state. Never auto-retry irreversible actions.
- cost: Negligible storage/compute relative to existing jobs; background reconciliation is inexpensive. No extra model call for straightforward timelines.  ·  latency: Reads local persisted evidence in milliseconds; live verification remains opt-in and can add seconds.
- security: Evidence must be scoped by owner/job and redact page text, email content, and tokens. Do not persist sensitive payloads merely to prove completion.
- depends on: Stable request IDs across POST /execute, browser commands, and Mac action receipts; Event-derived pipeline terminality and receipt trust metadata; A shared action-result vocabulary and owner-facing summary formatter


## What it asked for

### `s7-8chj` (skill) — universal_stop_latch
- does: A deliberate long button press (and, when locally recognized, a spoken 'stop everything') immediately silences queued playback, marks the current interaction cancelled, and emits a tiny signed stop token. The relay, Mac planner, browser runner, and any pending pipeline consume that token to cancel only owner-owned in-flight work, while irreversible actions remain stopped before submission. When the link is down, the pendant keeps the latch active and reports cancellation as soon as it reconnects.
- must be on-device because: The owner may need to stop an action while the network, relay, or Mac is unreachable; only the pendant can provide an immediate, tactile, offline-safe escape hatch and prevent more audio from playing into an unsafe moment.
- trigger: Dedicated long button hold (for example 1.5 seconds); optional local wake-word phrase only if the existing offline recognizer can meet a low false-trigger threshold.
- storage: One latch bit, monotonic counter, last stop-token hash, and up to 8 compact pending cancellation tokens in pendant flash/NVS; well under 1 KB.
- RAM budget: About 2–4 KB for state machine, debounce, token buffer, and transport framing—comfortably below the 211,608 B application RAM budget, without retaining audio.

## Its own summary

This round I added a new owner-facing guarantee: “Did that actually happen?” The outcome ledger correlates job/pipeline/browser/Mac evidence, derives terminality from events, exposes contradictory or merely attempted states, and refuses to say “done” without trusted evidence. I also queued a pendant-local universal_stop_latch: a deliberate long press silences playback and propagates cancellation even while offline, so the owner has a real escape hatch from cross-surface work. I did not re-request denied macOS/browser grants.

**Biggest unknown:** Whether the existing job, pipeline, browser, and Mac receipt records already share stable request/idempotency identifiers and whether cancellation endpoints can safely propagate a stop token. I still need that schema/route fact before the outcome ledger or stop latch can be implemented without risking duplicate or uncancellable actions.

