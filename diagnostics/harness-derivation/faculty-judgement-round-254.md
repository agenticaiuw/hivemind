# Harness derivation — faculty-judgement — round 254

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Learn how much interruption I actually tolerate, and stop nagging me when I keep skipping things.”"
- **useful because:** The current arbiter can choose interrupt/defer, but it has no closed loop from what the owner physically did. This would turn repeated skip, stop, replay, and successful playback into a bounded daily attention budget—without silently changing urgency or confidentiality rules. The pendant is the only surface that observes the owner's immediate acceptance; the relay is the only always-awake place that can aggregate it; Mac/browser provide the event evidence.
- **path:** pendant → relay → mac → browser
- **model tier:** background for daily calibration and cheap deterministic rules for each event; realtime only to explain a changed decision when asked
- **latency:** Under 100 ms for a per-event decision; overnight calibration can take seconds and must never block an urgent alert
- **cost:** Negligible for deterministic updates; roughly $0.01–$0.05/day only if a model is used to summarize the calibration
- **security:** Store counts and policy-rule IDs, not spoken content or page text. Never downgrade a hard deadline because of learned behavior. Owner must be able to freeze learning and inspect/reset the learned budget; every adjustment is provenance-linked.
- **missing:** A durable attention-feedback record keyed to event/dedupe_key and the pendant delivery ACK/stop/skip outcome; A policy field selecting whether learning is enabled, its maximum daily adjustment, and protected urgency classes; A relay writer for fleet memory or another durable cross-surface store

### "“Before you tell me everything is fine, tell me what you could not actually check.”"
- **useful because:** The system currently has dangerous false-all-clear paths: unauthorised EventKit reads can look empty, offline browser/Mac surfaces can look quiet, and scheduled jobs can complete without proving pendant playback. This is a user-facing blind-spot report, not another briefing. It returns verified facts, unverified domains, stale evidence, and the exact reason each omission occurred, so silence stops masquerading as safety.
- **path:** relay → mac → browser → pendant
- **model tier:** Deterministic provenance-backed aggregation first; use the slower background model only to compress the final explanation into one short spoken sentence
- **latency:** Under 2 s when requested; scheduled generation may take up to 30 s, but must fail closed and say 'unable to verify' rather than infer clear
- **cost:** Usually <$0.01 per report; model compression is the dominant cost and can be skipped for dashboard output
- **security:** Speak only domain names and failure reasons by default, never mail subjects, page text, or calendar details. A dashboard may reveal source snippets only after explicit local request. Do not turn an unverified source into a negative claim. Preserve source timestamps and permission provenance.
- **missing:** A typed blind-spot report schema with per-domain states verified|unverified|stale|contradictory|not_applicable; Authoritative permission probes for EventKit Calendar/Reminders and a real Focus/DND adapter, or explicit permanent 'unknown' results; A scheduler hook that submits the report to the existing attention arbiter without creating duplicate briefings

### "“If the pendant audio path starts failing, quietly switch me to a safe fallback and give me one useful bug report—not five repeated alerts.”"
- **useful because:** A checksum error, underrun, or repeated no-audio event is currently an observation, not a user-safe response. This capability makes delivery health an actual circuit breaker: classify the failure, stop generating more unusable audio, preserve the owner's pending content as a text/dashboard item, and draft one correlated UART/relay/Mac issue. Recovery is automatic only after a measured clean window.
- **path:** pendant → relay → mac
- **model tier:** Deterministic failure counters and state machine on relay/Mac; background model only for a concise human-readable bug draft; no realtime model in the failure path
- **latency:** Within one delivery event (under 1 s) for fallback and suppression; draft within 30 s; recovery requires a configurable clean sample window
- **cost:** Near-zero for counters and state; <$0.02 per incident if a model summarizes diagnostics
- **security:** Bug drafts must redact speech, mail, and page contents; include opaque artifact IDs, codec metrics, firmware/build identifiers, and timestamps only. Never upload raw PCM by default. Require owner review before external issue submission. A circuit breaker must not discard the owner's text/audio artifact without a recoverable local/relay record.
- **missing:** A durable per-artifact audio-health circuit-breaker state shared by relay and Mac; A typed fallback artifact that can be rendered as text or queued in the existing alert inbox; A correlation join between relay job, Mac job, pipeline artifact, UART diagnostics, and pendant ACK event; A measured recovery probe and owner-visible status route

### "“If I take this on, what will it displace, who will be affected, and what becomes hard to undo?”"
- **useful because:** The system can preview an individual action, but it cannot simulate the owner-level consequences of accepting a commitment across time, mail, calendar, browser work, and pending tasks. This would produce a read-only counterfactual: conflicts, likely displaced work, third-party visibility, irreversible edges, and the evidence supporting each conclusion. It is decision support, not execution and not another plan preview.
- **path:** relay → mac → browser → ios → pendant
- **model tier:** Background reasoning over deterministic extracts; realtime only for a short spoken answer after the simulation is ready
- **latency:** 3–10 seconds for a normal scenario; up to 60 seconds for a multi-surface scenario; never mutate while simulating
- **cost:** Approximately $0.03–$0.15 per scenario, dominated by the model’s synthesis after cheap calendar/mail/browser extraction
- **security:** Default to redacted summaries and opaque identifiers. Do not send the scenario to external model providers when it includes private mail, client names, or credentials unless the owner explicitly permits it. Label forecasts separately from observed facts and include confidence/evidence links.
- **missing:** A read-only common snapshot format for calendar, mail, browser sessions, iOS state, tasks, and pending jobs; A counterfactual dependency model that represents displaced time and third-party effects rather than merely listing conflicts; A durable scenario ID with provenance and expiry, so the owner can inspect or discard it

### "“Before you speak something private, tell whether this is a safe moment—or keep it on the screen and say only that it is waiting.”"
- **useful because:** Today speech confidentiality depends on which caller remembered to redact; the audio path itself has no disclosure gate, and there is no bystander or meeting signal. This capability makes output modality a judgement: combine Mac foreground/browser/iOS call state with an optional local acoustic audience detector, then permit, summarize, or withhold content. It protects the owner from an accidental spoken disclosure without pretending that idle time means privacy.
- **path:** pendant → mac → browser → ios → relay
- **model tier:** Local deterministic classifier for speech modality; no cloud model for ambient audio. Background model may classify the already-redacted content class, never raw audio
- **latency:** Under 150 ms before synthesis starts; no network round trip required to choose screen-only versus spoken
- **cost:** Near-zero runtime API cost; hardware/firmware work dominates if an audience sensor or local classifier is added
- **security:** Ambient audio must be processed and discarded locally, never uploaded. Fail closed when audience confidence is unknown. Emergency policy must be explicit and owner-configurable. Never treat a private label as permission to speak; destination and context both matter.
- **missing:** A local bystander/meeting-state signal; current Mac idle and foreground signals are insufficient; A modality gate directly in pendantSpeech/audioBrief before synthesis, covering every caller; A policy table mapping content classes and audience confidence to speak, summarize, screen-only, or suppress; Optional hardware or firmware support for a low-power local audience detector

### "“Ask the bodies independently, then tell me where they disagree before you give me an answer.”"
- **useful because:** The hive’s surfaces have different reach, but today their observations are usually collapsed into one model response. For consequential questions, the owner should get an explicit quorum: what the Mac saw, what the browser saw, what the relay knows, and which claims conflict or lack an observer. This is not majority voting; a single authoritative source can win, while unexplained disagreement blocks confident action.
- **path:** relay → mac → browser → ios → pendant
- **model tier:** Cheap parallel extractors and deterministic conflict rules first; background model summarizes the dissent; realtime speaks only the final compact verdict
- **latency:** 2–8 seconds for read-only questions; 30 seconds for a broad investigation; no mutation until dissent is resolved or the owner explicitly accepts uncertainty
- **cost:** Approximately $0.02–$0.10 per investigation, with parallel source reads dominating latency rather than token cost
- **security:** Each surface receives only the minimum query needed for its evidence. Do not merge private snippets into a relay prompt by default. Keep source-local evidence and expose hashes/labels rather than raw content. Any action based on a non-unanimous result requires explicit policy and provenance.
- **missing:** A typed independent-observation envelope with source, timestamp, authority, confidence, and claim identity; A cross-surface claim matcher that distinguishes true disagreement from stale snapshots or different scopes; A durable dissent record and owner-facing explanation showing which observer would change the result; A policy hook that prevents mutation when a protected claim remains unresolved


## Changes it proposed to its own stack

### `relay` — Add a lease_until/lease_owner to relay_jobs, reclaim expired processing jobs with an idempotent sweep, and persist the relay-job↔Mac-job↔pipeline-artifact join in the same receipt. On reclaim, emit one owner-visible 'resuming/needs review' event rather than silently duplicating execution; require the existing autonomy policy before retrying any mutation.
- **owner gets:** A Mac sleep, browser disconnect, or relay restart should not turn a requested task into a permanently invisible half-completion—or execute it twice without explanation. The owner gets one truthful status and a safe retry/stop choice.
- effort: Medium: schema migration, claim/reclaim transaction, bridge heartbeat/receipt updates, and tests for crash-before-receipt and duplicate completion.  ·  risk: A lease that is too short can duplicate a slow job; a lease that is too long delays recovery. Use routine's existing lease pattern, renew only while progress is observed, and make all mutation retries idempotency/policy-gated. Recover by marking ambiguous jobs needs_review rather than replaying destructive steps.
- cost: Negligible storage and CPU; no model cost.  ·  latency: Adds no latency to healthy jobs; recovery occurs after a configurable lease, e.g. 5 minutes.
- security: Preserve owner/job scope and do not let a reclaimed job inherit stale approval; require fresh revalidation for external effects.
- depends on: Durable relay-job↔Mac-job mapping; revalidate_pending_plan for stale plans; autonomy_policy_evaluate before any reclaimed mutation; Existing routine lease implementation as the transaction template


## What it asked for

_Nothing._
