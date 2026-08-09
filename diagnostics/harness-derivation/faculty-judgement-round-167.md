# Harness derivation — faculty-judgement — round 167

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Tell me which parts of my briefing actually reached me, and recover anything that didn't.”"
- **useful because:** A generated briefing is not delivered merely because the relay says it succeeded. This closes the loop from relay artifact to pendant download and playback, distinguishes unheard from failed audio, and offers a safe replay or defer without losing the item cursor. It is the single most useful trust feature for a wearable assistant: the owner can rely on it rather than wonder whether a morning brief vanished.
- **path:** relay → pendant → mac → dashboard
- **model tier:** Background model assembles and ranks the briefing; deterministic delivery ledger and attention arbiter handle ACK reconciliation; realtime model speaks only the short owner-facing recovery sentence.
- **latency:** Normal brief generation under 30s; ACK reconciliation under 1s after reconnect; replay decision under 2s. No model call for ordinary ACKs or deduplication.
- **cost:** Near-zero for ACK reconciliation and replay selection; roughly one background briefing-generation call per scheduled brief. Storage is a few hundred bytes per item plus existing pipeline receipts.
- **security:** Persist opaque artifact IDs, item IDs, playback positions, and checksums—not audio text in the delivery ledger. Spoken recovery must not reveal sensitive item content. Replay, defer, and append actions remain scoped and idempotent; external mutations still require the existing autonomy policy and physical approval where applicable.
- **missing:** A durable join between briefing item IDs, pipeline artifact IDs, and pendant delivery events.; A server-side consumer that turns record_pendant_delivery_event events into item state and retries only missing artifacts.; A reconnect-safe delivery worker that respects attention_arbitrate rather than independently interrupting.; A dashboard view of generated/downloaded/started/finished/interrupted states.

### "“If the pendant audio is failing, fix the next reply automatically and tell me only if I need to act.”"
- **useful because:** Today a failed decode, underrun, or stale bridge can look like the assistant simply ignored the owner. A closed-loop recovery path would use the pendant's authenticated delivery evidence, Mac-side UART metrics, and relay pipeline state to choose a reversible fallback profile, replay the affected item once, and produce a concise explanation instead of making the owner debug codecs.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Deterministic rules classify checksum errors, underruns, missing ACKs, and link loss; a cheap background model may summarize the incident. Realtime is used only for the final spoken sentence if the owner is actively waiting.
- **latency:** Classify within 500 ms of an error; apply a reversible fallback within 3 s; replay only after the next utterance boundary. If confidence is low, queue a diagnostic rather than changing settings.
- **cost:** Near-zero for rule evaluation and profile rollback; occasional background summarization. Device storage is limited to a compact incident counter and last-good profile, not audio.
- **security:** No PCM or transcript leaves the Mac for diagnosis. Changes are restricted to approved audio profiles and are recorded with before/after measurements. Never loop retries indefinitely; cap one automatic recovery per artifact and require owner confirmation for firmware changes.
- **missing:** A typed audio-profile apply/verify/rollback operation spanning Mac and pipeline; existing audio routes expose artifacts but do not provide atomic profile transitions.; A durable incident correlation linking delivery ACK event IDs, UART evidence, pipeline ID, and the replayed item.; A policy rule that distinguishes transient link loss from a persistent hardware fault and routes the latter to the existing reviewable bug draft.

### "“When I walk away from one device and pick up another, continue exactly where I left off without making me explain the context again.”"
- **useful because:** The owner should be able to move from pendant to Mac to browser and back as naturally as moving between rooms. Today the system can hand off prompt context, but it does not preserve a durable, user-visible continuation of the active conversational objective, cursor, pending questions, or safe next step across surfaces.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** A cheap deterministic continuity service stores and validates the active thread and cursor; a background model compresses only when the context exceeds the budget. Realtime is used only when the owner resumes by voice.
- **latency:** Resume state under 500 ms when cached; compressed context under 3 s. Never block a simple spoken reply on a full-history model call.
- **cost:** Low: bounded state records and occasional compression. One background summarization call only when a thread crosses its size threshold.
- **security:** Store opaque handles and short task summaries, not browser secrets or raw page bodies. Require source freshness checks before resuming a prepared action; stale or mutated state must become a review prompt, never an automatic mutation.
- **missing:** A durable active-thread record with a stable cross-surface identifier, distinct from the existing relay/Mac/browser job IDs.; A typed cursor for browser page, audio item, pending question, and next safe action.; A surface handoff protocol that lets the owner inspect, pause, or discard the continuation.; Automatic expiry and revocation of handoff state when its source evidence or authorization becomes stale.

### "“Before you do anything in a website, tell me which account and workspace you are about to affect, and stop if it changed.”"
- **useful because:** A browser action can be technically successful while targeting the wrong account, organization, workspace, or tenant. The owner needs protection against silent session drift—not merely a confirmation that an action is destructive. This would catch the dangerous case where a familiar URL is open under a different identity.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** Deterministic browser/session checks extract origin, signed session identity, visible account/workspace markers, and recent identity changes. A background model may normalize labels when the page is ambiguous; realtime only speaks a compact warning.
- **latency:** Under 1 s for known identity markers; up to 3 s for an ambiguous page read. A mutation is blocked until identity is stable and the owner confirms only when policy requires it.
- **cost:** Low: read-only browser inspections and small identity fingerprints. Occasional model call for ambiguous labels, with no page body sent unless explicitly allowed.
- **security:** Never store passwords, tokens, or full page content. Persist salted identity fingerprints and origin-scoped labels with short TTLs. A missing or changed identity is fail-closed; do not infer identity from URL alone. The warning must name the origin and account label without speaking secrets.
- **missing:** An extension-side identity extractor with site-specific, secret-safe selectors.; A durable origin/account/workspace fingerprint and change history shared with the Mac and relay.; A pre-mutation hook that makes identity stability a hard prerequisite, separate from destructive-action approval.; Owner policy for trusted multi-account origins and whether an identity label may be spoken aloud.


## Changes it proposed to its own stack

### `routines` — Make every scheduled routine carry an explicit time-zone provenance and a pre-fire conflict check. If the owner's remembered zone (currently America/Chicago) differs from the authoritative Mac routine zone (America/New_York), mark the routine 'needs timezone confirmation', do not fire spoken or external effects, and place a terse, non-sensitive alert in the existing inbox. Once confirmed, persist the chosen zone per routine and show the source and next fire instant in its receipt.
- **owner gets:** It prevents a daily brief or tidy job from arriving at the wrong local hour while the system has contradictory timezone evidence. The owner gets one clear question instead of silently missed or badly timed routines.
- effort: Medium: extend the existing routine record and scheduler preflight, call reconcile_personal_state for timezone provenance, and add a review/confirm route. No new model is needed.  ·  risk: Existing routines could pause on the first conflict, which is safer but surprising; recover by preserving the original schedule and allowing one explicit confirmation to resume. Never silently convert the instant.
- cost: Negligible API cost; one small reconciliation read per routine tick or cached policy version. No hardware cost.  ·  latency: Under 100 ms when cached; a brief delay only on the first conflict check.
- security: Timezone metadata is low sensitivity, but routine command text must not be spoken in the alert. Confirmation must be owner-authenticated and auditable.
- depends on: The owner must decide whether America/Chicago or America/New_York governs personal routines; do not infer this from either source.; reconcile_personal_state timezone output; A durable routine policy field and review endpoint

### `hardware` — Add a small ear-wear/proximity sensor and ambient-light sensor to the next pendant revision, with a local firmware privacy state: worn-near-ear, worn-on-body, removed, and likely-public. The device should expose only coarse signed state and confidence, never raw sensor data. The relay and Mac use it as an input to the existing speech redaction and attention decisions; when removed or likely-public, sensitive content is automatically converted to a non-revealing notification.
- **owner gets:** The pendant would stop making the owner choose between useful speech and privacy every time they enter a room, take it off, or put it on a desk. It could remain helpful in public without announcing private details.
- effort: High: hardware revision, sensor driver and calibration, signed state messages, and policy integration across pendant, relay, and Mac. Requires real-world false-positive testing in pockets, bags, and near the ear.  ·  risk: Sensor inference can be wrong and could suppress useful speech or falsely permit disclosure. Fail closed for sensitive content, show a clear local LED state, and always allow a deliberate physical override for ordinary playback. No camera or raw audio should be added.
- cost: Roughly $2–$8 in components and PCB changes, plus a few mW while sensing; engineering and enclosure validation dominate.  ·  latency: Under 200 ms for local state changes; no model latency for the safety decision.
- security: Improves privacy only if raw sensor streams stay local and state messages are authenticated. It must never be treated as proof that no bystander exists.
- depends on: A policy table defining which content classes may be spoken in each coarse state; Firmware support for authenticated state telemetry; Mac/relay speech-output gate that applies the state before TTS, not after


## What it asked for

_Nothing._
