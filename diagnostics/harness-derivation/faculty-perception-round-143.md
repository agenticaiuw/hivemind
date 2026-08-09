# Harness derivation — faculty-perception — round 143

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-permissions** — The running AI Pendant Agent currently has Accessibility and Screen Recording granted; /ops/snapshot reports permissions.ready=true and no required or optional missing permissions.
  - evidence: Authenticated GET /ops/snapshot at 2026-08-08T01:42:57Z returned hostFingerprint com.aipendant.agent, accessibility.trusted=true, screenRecording.granted=true, requiredMissing=[], ready=true.
- **live-cross-surface-state** — At the latest snapshot the Mac bridge, relay, browser extension, and Mac agent are live, but the pipeline history still contains a completed run whose final event says the relay accepted audio and it is waiting for the pendant; no device_playback event is present in that run.
  - evidence: GET /ops/snapshot reported relay reachable, macBridgeOnline=true, browser online, permissions ready. GET /pipeline showed job_309f... status completed with final relay_result/done detail 'Response waiting for the pendant' and no device_playback event.

## Capabilities it proposed

### "Before you act, tell me whether the facts you are relying on are live, stale, or contradictory—and refuse to present a guess as current."
- **useful because:** The owner currently cannot distinguish a live Mac bridge from a stale relay row, or a completed job from audio actually heard. A pre-action reality gate would prevent confident wrong actions and explain exactly which prerequisite is missing.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model for periodic state normalization; realtime only to phrase an urgent contradiction.
- **latency:** Under 1 second when invoked before an action; periodic normalization every 30 seconds.
- **cost:** <$0.01 per check when using structured state and a cheap model; dominated by no model call if rules settle it.
- **security:** Only metadata and hashes leave the Mac; page contents stay local. Any action block should be explainable and overridable only by explicit owner confirmation.
- **missing:** A typed freshness/contradiction evaluator over /ops/snapshot, device registry, pipeline, browser, and job receipts; A policy hook in faculty-action that requires the evaluator result before irreversible actions; A real pendant-originated playback event when the pendant exists

### "Tell me when two parts of you disagree about reality—for example, the relay says a device is stale while the Mac says it is online—and show me the evidence for both sides."
- **useful because:** Today contradictory telemetry is silently collapsed into one status. Surfacing disagreement is the most valuable perception behavior: it lets the owner decide whether to retry, wait, or reconnect instead of acting on a false consensus.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Rules and structured comparison first; cheap background model only to summarize the conflict in natural language.
- **latency:** Sub-second for a live voice answer; batch comparison every minute.
- **cost:** Negligible for rules; <$0.005 for occasional summarization.
- **security:** Expose only field names, timestamps, identifiers pseudonymized in the UI, and redacted provenance—not page bodies or secrets. Conflicts must be append-only and tamper-evident.
- **missing:** A normalized observation envelope with source, observedAt, expiresAt, value, and provenance; Conflict classes and precedence rules that never convert disagreement into success; A dashboard and voice tool that can retrieve the last conflict and its raw observations

### "When you tell me something based on a web page, job, or device, tell me how long that fact remains trustworthy and automatically ask for a fresh check when it has expired."
- **useful because:** The system has count-capped Mac history, a 24-hour relay job TTL, unpruned announcements, and no owner-heard signal. Time-aware claims prevent yesterday's result or a socket write from being treated as current evidence.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Deterministic TTL and provenance engine; background model only for concise owner-facing explanation.
- **latency:** No added latency for cached claims; fresh check only when a claim is expired.
- **cost:** Near-zero for structured checks; fresh browser/device probes dominate and are invoked only on expiry.
- **security:** Persist claim metadata and hashes, not raw sensitive content. Expired claims must be visibly marked, never silently reused; refreshes requiring login or side effects require confirmation.
- **missing:** Claim objects carrying observedAt, expiresAt, source, content hash, and confidence; Expiry-aware retrieval wrappers around browser, pipeline, relay, and device reads; A voice/dashboard presentation that distinguishes expired, unknown, and verified

### "Hold important answers in evidence escrow until two independent surfaces corroborate them, then tell me exactly which sources agreed; if they do not agree, leave the answer pending instead of guessing."
- **useful because:** For high-consequence claims such as payments, appointments, messages, or account changes, one stale browser tab or one relay result is not enough. The owner gets a deliberate, verifiable answer rather than a fluent falsehood.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** Deterministic quorum and hash comparison; use the cheap background model only to summarize corroboration or explain why escrow remains pending.
- **latency:** Fast claims under 2 seconds; asynchronous escrow may wait up to 5 minutes for a second source.
- **cost:** Minimal structured comparisons; typically <$0.01 per escrowed claim, with browser or Mac rechecks dominating.
- **security:** Escrow stores redacted claim digests and source metadata, not account contents. Any source requiring login remains inside its owning surface. Release to the owner is read-only unless separately confirmed.
- **missing:** A durable claim-escrow record with quorum policy, source diversity rules, hashes, and expiry; Adapters that obtain independent observations from the browser session and Mac or relay without treating duplicated relay data as independent; A faculty-judgement hook that prevents action on an unresolved escrow

### "Alert me only when a fact that matters to me materially changes, and show the before-and-after evidence and which surface detected the change."
- **useful because:** The owner should not have to repeatedly ask whether a page, job, device, or permission changed. A change-only feed turns perception into useful awareness without flooding them with routine heartbeats or stale repeats.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Hashing, typed diffs, and threshold rules; background model only for grouping related changes into one plain-language alert.
- **latency:** Seconds for safety-relevant changes; under 5 minutes for ordinary changes.
- **cost:** Near-zero for hashes and structured diffs; <$0.01 for occasional grouping.
- **security:** Default to field-level diffs and redacted values. Sensitive browser content should produce a change classification and digest, not copied text. Require confirmation before converting a detected change into an action.
- **missing:** A durable cross-surface baseline with content hashes and semantic field extraction; Per-domain materiality rules and owner-configurable quiet hours; A deduplicated change event stream shared by relay, Mac, browser, and pendant

### "Set a personal evidence policy such as 'never act on a single source or on facts older than ten minutes,' and have every answer and action obey it automatically, with an explanation when the policy blocks progress."
- **useful because:** The owner should be able to choose how much uncertainty they tolerate once, rather than trusting each model turn to make an invisible judgement. This converts perception into a dependable personal safety boundary across all substrates.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Rules engine for enforcement and freshness; cheap model for translating policy failures into speech, never for deciding whether to bypass them.
- **latency:** No noticeable delay for already-valid evidence; one fresh probe when policy requires it.
- **cost:** Near-zero enforcement cost; probe costs depend on the source and occur only when a policy check fails.
- **security:** Policies are owner-controlled, versioned, and fail closed for external side effects. A policy cannot grant a surface more permissions than it has. Sensitive policy details stay local unless explicitly synchronized.
- **missing:** A versioned owner evidence-policy schema covering age, source count, source diversity, and required confirmation; One enforcement middleware used by realtime answers, Mac actions, browser actions, and routines; A clear override flow requiring explicit owner confirmation and recording the exception


## What it asked for

_Nothing._
