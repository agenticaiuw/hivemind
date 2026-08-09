# Harness derivation — faculty-perception — round 212

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser observability** — As of 2026-08-09T00:09Z, the Mac agent reports Accessibility and Screen Recording granted, all required permissions present, browser extension online on Safari with two tabs (active YouTube tab), relay reachable, and no pendant device registered; this is a live diagnostic snapshot, not historical audio evidence.
  - evidence: GET /ops/status returned status 200 with permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browserExtension.online=true, relay.reachable=true; discover(devices) lists only home-macbook-bridge and cloudflare-contract-test.

## Capabilities it proposed

### "Before you interrupt me, tell me whether I am available, busy, or unreachable—and if busy, queue it with the reason."
- **useful because:** The system currently knows isolated liveness (Mac, browser, relay) but not whether speaking now would disrupt the owner. A single perception result can prevent an announcement during a call or active dictation and explain why it was deferred.
- **path:** pendant capture sentinel and reality beacon → relay liveness and announcement queue → Mac /ops/status and /observe → browser extension heartbeat and active tab → judgement chooses interrupt/defer → action speaks or queues with the reason
- **model tier:** Deterministic local signals first (mic/VAD, audio route, meeting/app state, browser activity, relay freshness); a cheap text model only labels an ambiguous composite state. Never use the realtime tier for routine classification.
- **latency:** Under 250 ms from an interrupt request; heartbeat evidence no older than 5 s. Deferral itself must be immediate and offline-safe.
- **cost:** Near-zero for rules; occasional small-model classification under $0.001. Dominant cost is none unless ambiguity requires a model call.
- **security:** Mic/VAD and foreground-app state are sensitive. Export only coarse states and freshness, not audio or window contents; require confirmation before overriding a user-declared quiet mode.
- **missing:** A shared attention-state schema with evidence timestamps and source confidence; Mac observers for active call/audio route and user idle state; Pendant event forwarding for the already-accepted capture-integrity verdict when connected

### "Tell me which remembered facts are contradicted by the live Mac or browser, and show the source and timestamp before I rely on one."
- **useful because:** A pinned machine-derived preference can outrank live truth indefinitely; the current timezone fact is a concrete example. This lets the owner catch stale or misattributed memory before it changes schedules, messages, or purchases, without silently rewriting their memory.
- **path:** Mac memory projection and context graph → Mac live machine and permission observations → browser/session observations → faculty-perception emits contradiction records → faculty-judgement decides quarantine or asks the owner → faculty-action only applies an owner-approved correction
- **model tier:** Deterministic comparison and provenance rules; use a cheap model only to explain a conflict in one sentence. No realtime model needed.
- **latency:** A few seconds on demand; under 1 minute after a machine-context refresh. Never block an unrelated voice turn.
- **cost:** Effectively zero for comparisons; under $0.001 for optional explanation. Storage is bounded contradiction records, not copied page contents.
- **security:** Memory and browser state may contain secrets. Keep values redacted to hashes/short previews by default, show full values only after the owner asks, and never auto-delete or overwrite owner facts.
- **missing:** A live-fact comparator that joins source.origin, confidence, expiry, and observed-at timestamps; A quarantine state that removes a contradicted machine fact from prompt projection without deleting it; An owner-facing review route with competing evidence

### "Why did that request fail or go quiet? Reconstruct the causal timeline across my pendant, relay, Mac, and browser, and distinguish observed facts from gaps."
- **useful because:** Today a completed Mac job, delivered announcement, or stale browser command can look like success even when the pendant never played anything. A causal timeline would tell the owner whether the failure was capture quality, link loss, relay acceptance, Mac execution, browser delivery, or simply missing evidence.
- **path:** pendant reality beacon and capture-integrity telemetry → relay job, announcement, and device registry history → Mac pipeline, jobs, action ledger, and browser spool → browser command/result records → faculty-perception correlates IDs and freshness → faculty-judgement chooses retry or explanation → faculty-action performs a confirmed retry
- **model tier:** Rules and event-time ordering for the first pass; a small background model summarizes the already-correlated timeline. Realtime is reserved for the owner's immediate question.
- **latency:** Return a first causal answer in 1–2 seconds from bounded stores; deeper reconstruction may take 10 seconds and should stream intermediate evidence.
- **cost:** Usually zero beyond local reads; optional summary under $0.002. The dominant expense is bounded event correlation, not model tokens.
- **security:** Event metadata can expose URLs, app names, and snippets. Redact secrets and page bodies, preserve hashes and IDs, and require confirmation before a retry that could repeat an external action.
- **missing:** A shared event envelope with monotonic sequence, wall-clock estimate, source, and confidence; A relay-to-Mac correlation ID propagated into pipeline, browser, and announcement records; A reader that treats delivered as socket-write only and playback as unknown unless the device event exists; A bounded causal query route returning evidence plus explicit unknowns

### "Give me a ranked list of decisions you should not make on my behalf because the evidence is incomplete, including exactly what evidence would make each safe."
- **useful because:** Today uncertainty is mostly exposed only after an action or failure. The owner needs a proactive safety boundary: not a generic disclaimer, but a consequence-ranked list of pending decisions whose observations are stale, single-sourced, contradicted, or missing an owner-heard confirmation. It turns perception into something the owner can use before harm occurs.
- **path:** pendant reality beacon and capture-integrity sentinel provide device evidence → relay records delivery and connectivity evidence → Mac agent supplies live machine, job, pipeline, and permission evidence → browser extension supplies session and command evidence → faculty-perception computes evidence coverage and uncertainty classes → faculty-judgement ranks decisions by consequence and chooses what to ask → faculty-action executes only after the requested evidence and confirmation exist
- **model tier:** Deterministic evidence-policy engine for safety classification; a small background model may phrase the ranked list. Never spend realtime tokens unless the owner asks during a live turn.
- **latency:** Generate on demand in under 2 seconds from bounded recent evidence; refresh after every externally consequential action or link transition.
- **cost:** Near-zero for rule evaluation; optional explanation under $0.002. Costs are dominated by retaining compact hashes and event metadata, not model inference.
- **security:** The list can reveal private app names, destinations, and pending intentions. Store only redacted evidence references by default, require owner authentication to reveal details, and never treat model confidence as authorization.
- **missing:** A consequence taxonomy for actions (financial, communication, deletion, privacy, safety); A machine-readable evidence contract: source, observedAt, freshness deadline, independence, confidence, and what would falsify it; A durable but bounded uncertainty ledger linked to action/job IDs; A policy evaluator that can say 'insufficient evidence' without silently downgrading the action to best effort


## What it asked for

_Nothing._
## Its own summary

Fresh discovery changed the boundary: the exact AI Pendant Agent now has Accessibility and Screen Recording, permissions.ready=true, Safari/browser bridge is online with two tabs, relay is reachable, and the pendant is still absent from the device registry. I recorded that as a live fact. I proposed three owner-facing capabilities: an attention-aware interrupt/defer decision, contradiction detection for stale machine-derived memory, and a cross-surface causal failure timeline. The strongest is the last: it would finally distinguish capture/link/relay/Mac/browser failure from mere absence of playback evidence. I do not need another permission grant. What I still need is product work, not access: a shared event envelope and correlation ID across pendant→relay→Mac→browser, explicit freshness/confidence on every observation, and a causal-query reader that preserves unknowns instead of treating completed or delivered as heard. For the contradiction feature, I additionally need a non-destructive quarantine state for contradicted facts. For attention-aware interruption, I need Mac active-call/audio-route and idle observers plus forwarding of the accepted pendant capture-quality verdict.

**Biggest unknown:** The pendant itself remains unregistered and unobservable; therefore no current claim about physical capture, relay receipt, or playback can be made, even though Mac, browser, and relay diagnostics are live.

