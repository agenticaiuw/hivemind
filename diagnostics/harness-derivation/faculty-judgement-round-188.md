# Harness derivation — faculty-judgement — round 188

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If I missed part of a briefing, catch me up from exactly where playback stopped—without replaying what I already heard.”"
- **useful because:** Today generation receipts prove a job ran, not that the pendant downloaded or played it. With delivery ACKs, the system can distinguish unheard, partially heard, and completed items, then offer a short delta on the next owner interaction instead of making them hunt or endure a duplicate briefing.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Use deterministic delivery reconciliation and item boundaries first; use the cheaper background model to compress only the unheard segment. Reserve realtime for the one-sentence spoken offer and owner reply.
- **latency:** Under 300 ms to identify the missed item from ACKs; under 5 s for a generated catch-up. No network wait should block the next button press.
- **cost:** ~$0.002–$0.01 per catch-up, dominated by summarizing unheard text; zero model cost for fully played items.
- **security:** Send artifact IDs, playback positions, and provenance—not raw audio—to the relay. Do not infer that downloaded means heard. Require the owner’s explicit play/accept action before speaking private content in a new context; apply the configured sensitivity policy and retain ACKs only for the owner’s selected delivery window.
- **missing:** An item-level transcript/time-span map in generated artifacts so a playback position can map to content boundaries; A durable reconciler joining record_pendant_delivery_event events to briefing items and exposing an unheard queue; A conservative default for how long delivery telemetry is retained, surfaced as an owner policy

### "“When you’re blocked on something I asked for, ask me the single smallest question that would unblock it, then continue automatically.”"
- **useful because:** The system currently either guesses through conflicts or hands the owner a broad failure. A cross-surface uncertainty checkpoint would inspect permissions, freshness, and pending plans, identify the highest-value missing fact, ask one short spoken question, and resume the existing plan without making the owner restate context.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic preflight, stale-plan revalidation, and autonomy policy evaluation to identify blockers; use realtime only to phrase the one question and interpret the short answer. Persist the answer with a cheap model or typed event, not a full reasoning trace.
- **latency:** Blocker detection under 1 s; spoken question on the next attention window; resume within 5 s after the answer. Never ask more than one blocking question per turn.
- **cost:** ~$0.001–$0.01 per checkpoint, depending on whether answer interpretation needs the realtime tier; most checks are deterministic.
- **security:** The question must reveal the minimum needed (for example, a permission choice or target), never quote private page/mail contents aloud by default. A reply must not silently authorize a destructive action: route any mutation through autonomy_policy_evaluate and physical confirmation where required. Store the owner answer with expiry and provenance, not as an unbounded preference.
- **missing:** A durable typed blocker/question/answer record that binds to a planId and survives a Mac or relay restart; An answer-ingestion route that maps a spoken response to the pending question without treating arbitrary speech as consent; A resume hook that invokes revalidate_pending_plan before continuing

### "“If a link drops while something might have happened, tell me whether it happened, did not happen, or is genuinely unknown—and do not retry until you know.”"
- **useful because:** A browser or Mac action can lose its result after the side effect, while current job state can remain processing or invite an unsafe retry. The hive should reconcile post-disconnect state using the browser session, Mac receipts, and the owner’s physical stop latch, then present a three-way truth rather than claiming success or duplicating a purchase/message.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Deterministic lease/idempotency and read-back checks do the first pass. Use a cheaper background model only to summarize evidence conflicts; realtime speaks the short status. Any unknown external effect remains ASK, never ACT.
- **latency:** Detect a dropped lease in under 2 s; attempt bounded read-back for up to 15 s; surface UNKNOWN immediately if read-back is unavailable, then update when a surface returns. No automatic retry of external side effects.
- **cost:** ~$0.001–$0.005 per incident; mostly deterministic HTTP/browser read-back, with model use only for conflict wording.
- **security:** Read back only the minimum state needed to establish outcome; do not replay form values or expose secrets to the pendant. A physical stop token cancels retries but cannot erase an already-committed external effect. Every verdict must list evidence and freshness, and destructive or financial actions require the existing owner confirmation path.
- **missing:** Relay job leases and orphan requeue for relay_jobs, so processing is not mistaken for completion; A durable cross-surface correlation record joining relay job, Mac job, browser command, and action idempotency key; Typed read-back adapters and an outcome enum (committed, not_committed, unknown) for each external action kind; A policy-enforced retry barrier that consults the outcome record before POST /execute

### "“Run a private readiness drill once a week and tell me whether the pendant could still stop, store, deliver, and account for an interaction if the Mac or link failed.”"
- **useful because:** The owner cannot currently know whether the safety properties are alive until a real failure occurs. A controlled drill would exercise the physical stop latch, offline queue, audio-delivery acknowledgements, relay recovery, and receipt chain without sending mail, buying anything, or exposing content, then give one honest readiness score and the exact failed component.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Use deterministic fault-injection and invariant checks; use a cheap background model only to turn failures into a short owner-readable report. Realtime should speak only the result and recommended next step.
- **latency:** Run unattended in under 2 minutes; report on the next convenient interaction. The pendant-side portions must complete offline and never interrupt an active conversation.
- **cost:** Less than $0.01 per drill, dominated by telemetry storage; no expensive model call is needed for a passing run.
- **security:** The drill must use synthetic payloads and a non-routable test artifact. It must prove that cancellation prevents submission, not test by making a real external action. Store only component health, counters, and evidence references; require dashboard confirmation before any repair or firmware change.
- **missing:** A signed synthetic-test mode shared by pendant, relay, Mac, and browser so test traffic cannot be mistaken for owner work; Fault-injection hooks for link loss, process crash, duplicate ACK, stale lease, and interrupted playback; An invariant-based readiness report with a history and explicit unknown state rather than a single green/red score; A scheduler and owner-configurable quiet window for the drill

### "“Tell me, for the last hour, exactly what the pendant heard, what left the device, what was retained, and what was discarded.”"
- **useful because:** The owner has no trustworthy sensory ledger. Audio retention, voice notes, pipeline artifacts, browser evidence, and memory facts live in separate stores, so privacy decisions require guesswork. A compact chain-of-custody view would make the pendant understandable and let the owner revoke or verify data without reading raw private content aloud.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Build the ledger from signed device events and deterministic store joins. Use no model for the facts; use a cheap summarizer only for the dashboard’s plain-language explanation. Spoken output should contain counts, destinations, and retention deadlines—not captured content.
- **latency:** A one-hour query should return in under 2 seconds locally and under 5 seconds when the relay must be consulted. The pendant should expose a short status code offline and sync details later.
- **cost:** Negligible model cost; bounded local/relay storage and event joins dominate. A daily digest could cost under $0.001.
- **security:** The ledger itself can reveal sensitive activity, so it needs local authentication and redacted spoken output. It must distinguish microphone-active time from intelligible speech and downloaded from played audio. Tamper or clock uncertainty must be shown as unknown, never silently repaired. Raw PCM and transcript text should be excluded by default.
- **missing:** Authenticated capture-start/stop, upload, discard, and local-retention events from the pendant; A common artifact lineage connecting PCM chunks, transcripts, generated audio, playback ACKs, notes, facts, and evidence capsules; A read-only privacy ledger route with retention deadlines, destination classes, and revocation fan-out status; A device-local compact status response that works while USB/LTE is unavailable

### "“Before an important conversation, test whether you can actually hear me and hear the pendant, then fix or warn about the audio path without making me troubleshoot it.”"
- **useful because:** The current acceptance tests prove codec performance in development, not whether this particular worn setup is intelligible in the owner’s environment. A short two-way self-test could catch a muted bridge, bad USB serial path, packet starvation, clipping, or microphone loss before the owner relies on it.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Use deterministic loopback, counters, checksum, latency, and spectral measurements first. Use a cheap model only to translate measured failures into an owner-readable diagnosis; realtime is unnecessary unless the owner asks for the spoken result.
- **latency:** Under 10 seconds end to end, with no external network requirement when USB-tethered. It must never interrupt an active call without explicit initiation.
- **cost:** Near-zero model cost; a few synthetic audio packets and local measurements. Storage is a single bounded diagnostic record.
- **security:** Use synthetic tones or generated phrases only—never record or upload the owner’s speech during the test. Clearly identify whether a result is electrical/codec health versus actual room intelligibility. Do not change volume during an active conversation; apply changes only after confirmation.
- **missing:** A signed test-session protocol shared by the nRF9160 and ESP32 bridge, including loopback markers and expected packet counts; A firmware command that runs a bounded synthetic downlink/uplink test without persisting PCM; An objective report combining mic level, decode underruns, tx starvation, latency, checksum, and bridge reachability; A safe optional calibration profile with rollback, rather than an unverified volume change


## Changes it proposed to its own stack

### `relay` — Turn the three capabilities above into one owner-visible outcome ledger: add lease_until and reclaim timestamps to relay_jobs; persist a correlation row linking relay job ID, Mac job ID, browser command ID, Mac action idempotency key, artifact/item IDs, and the latest surface generation; expose a fail-closed outcome resolver that returns committed, not_committed, or unknown with evidence refs and freshness. Before any retry or POST /execute continuation, require autonomy_policy_evaluate to accept the resolver verdict. Make the ledger append-only for evidence and retain explicit uncertainty rather than overwriting it with a guessed success.
- **owner gets:** After a crash or dropped link, the owner gets an honest answer and does not accidentally send the same message, buy twice, or repeat a browser submission. This is the foundation that makes the pendant’s physical stop and delivery acknowledgements meaningful across the whole hive.
- effort: Medium-high: D1 migration and memory-store parity, bridge correlation plumbing, per-action read-back adapters, and tests for crash-after-side-effect and duplicate delivery. Start with Mac/browser reversible actions, then add external side effects one by one.  ·  risk: A false committed verdict is worse than UNKNOWN, so default to UNKNOWN when evidence conflicts or is stale. Reclaiming a lease while the old worker is alive can create duplicate work; use worker generation/fencing tokens and preserve idempotency. Recover by cancelling retries and showing the evidence chain in the dashboard.
- cost: Negligible storage and request cost; occasional read-back calls. No standing model cost. D1 rows and receipts grow, so apply a bounded retention policy with owner-visible deletion semantics.  ·  latency: Adds tens of milliseconds for local ledger writes; bounded read-back may take seconds only after a failure. Normal successful actions should not wait for model adjudication.
- security: Correlation metadata must exclude payloads, credentials, and page text. Evidence refs can be sensitive and should obey the existing disclosure policy. Never allow an UNKNOWN result to authorize an irreversible retry.
- depends on: Relay job lease/requeue migration modeled on the existing routine lease; A real relay↔Mac↔browser correlation foreign key rather than telemetry-only localJobId; Typed read-back adapters for each external side-effect action; Integration of autonomy_policy_evaluate at the retry/continuation gate


## What it asked for

_Nothing._
