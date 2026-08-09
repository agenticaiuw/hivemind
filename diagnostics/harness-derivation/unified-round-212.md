# Harness derivation — unified — round 212

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What did you change today, across the Mac, browser, and pendant, and which changes can I undo?"
- **useful because:** A per-job receipt answers only one known job. A daily accountability view groups work by owner intent, separates observed from executed actions, links browser and Mac evidence, and exposes undo availability so the owner can audit the system without knowing internal IDs.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background deterministic aggregation with a cheap summarizer; realtime only for the spoken answer
- **latency:** Recent-day digest under 2 seconds; historical ranges may stream progressively. Never block action execution on digest generation.
- **cost:** Very low: mostly indexed receipt reads; model cost only for optional natural-language grouping.
- **security:** Filter by the owner's authenticated session and redact page contents, secrets, and sensitive parameters. Mark every row as observed/planned/executed/failed, and never infer completion from a plan alone. Undo must be an explicit separate action with existing risk checks.
- **missing:** A cross-surface event index keyed by intent and time; A typed join between Mac job receipts, browser command results, relay jobs, and pendant events; A safe undo link that handles unsupported irreversible steps honestly

### "Warn me before one of my logged-in browser sessions becomes unusable, and tell me which site needs attention without exposing its page contents."
- **useful because:** The browser is the only node holding sessions the Mac and relay cannot recreate. Silent auth expiry turns later actions into confusing failures; a privacy-preserving session watch gives the owner advance warning and a bounded recovery choice.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** deterministic background polling and rule evaluation; realtime only when the owner asks what needs attention
- **latency:** Heartbeat every 5–15 minutes with no effect on active browsing; alert within one polling interval. Recovery should be explicitly confirmed and bounded to the named tab/session.
- **cost:** Minimal API cost; periodic browser heartbeats and small relay state dominate.
- **security:** Store only origin, tab/session binding, last successful probe, and coarse failure class—never page text, cookies, tokens, or screenshots. Do not auto-submit or reauthenticate. Require confirmation before navigation or refresh that could discard unsaved work.
- **missing:** A browser-side authenticated probe that reports session health without page-content capture; A relay scheduler and deduplicated alert state with expiry; A pendant alert payload that names the origin and failure class without secrets

### "Why did my scheduled action not happen, and what will happen if I ask you to run it now?"
- **useful because:** A missed routine currently requires reconstructing leases, Mac reachability, quiet-hour policy, timezone, browser state, and job receipts by hand. The owner needs a plain-language causal explanation and a dry-run that cannot silently duplicate an action.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** deterministic diagnosis from routine leases, job receipts, and policy; background summarization for the spoken explanation
- **latency:** Explain a recent miss in under 2 seconds; dry-run in under 3 seconds. Running it remains a separate explicit confirmation.
- **cost:** Low: read-only joins over routine/job/health records; negligible model spend.
- **security:** Distinguish skipped, leased, failed, expired, and never-delivered states; never claim execution from a queued record. Show the Mac timezone used for resolution and identify any owner-timezone ambiguity. A rerun must get a fresh idempotency key and preserve the original audit record.
- **missing:** A stable routine-attempt record linking schedule fire, lease, policy decision, job, and receipt; A read-only dry-run route that returns the exact planned actions and risk tiers; A repair/rerun control that cannot duplicate an already completed attempt

### "What did the system know, hear, and show at 3:17 PM yesterday, and what changed immediately afterward?"
- **useful because:** Today the owner can inspect current snapshots or individual jobs, but cannot reconstruct a trustworthy historical moment across the pendant, relay, Mac, and browser. A time-indexed reconstruction would make disputes, missed actions, and privacy questions answerable without pretending that later state was true earlier.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background deterministic reconstruction from signed events and snapshots; realtime only to narrate the already-built timeline
- **latency:** Recent windows under 3 seconds; older or sparse windows may return partial results with explicit gaps.
- **cost:** Moderate storage/indexing cost; low model cost because the timeline is assembled before summarization.
- **security:** Require owner authentication and redact audio, page contents, credentials, and unrelated people. Every assertion must carry source, timestamp uncertainty, and a missing-data marker; never interpolate a device state across an outage.
- **missing:** Append-only cross-surface event stream with synchronized monotonic and wall-clock metadata; Periodic redacted state checkpoints for pendant, relay, Mac, and browser; A query that returns evidence intervals and explicit unknown periods rather than a fabricated narrative

### "Before anything leaves my pendant or Mac, show me exactly which fields will be sent to the relay, let me block a field class permanently, and prove the transmitted payload obeyed that rule."
- **useful because:** The owner currently has privacy latches and deletion policies, but no field-level egress control. This would let them permit useful coordination while preventing categories such as raw audio, page text, location, or inferred facts from crossing a chosen boundary.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** deterministic policy enforcement and hashing; realtime only for explaining a blocked transmission
- **latency:** Policy decision inline in under 20 ms; preview under 1 second. A blocked payload must fail closed rather than delaying until a model decides.
- **cost:** Low runtime cost; modest metadata storage for policy versions and signed transmission receipts.
- **security:** Fail closed on unknown fields and policy-version mismatch. Store hashes and schemas, not prohibited contents. Policy changes require explicit owner confirmation and are versioned so every relay receipt identifies the rule that allowed it.
- **missing:** A shared typed egress schema for pendant, browser, Mac, and relay messages; Enforcement hooks before serialization/transmission on each surface; Signed policy-version and field-hash receipts that can be audited without retaining the data

### "Let me ask a question about a past conversation and get the smallest answer supported by the exact audio, transcript, and action evidence—without reopening or broadly searching my history."
- **useful because:** Current memory and job views are organized by records, not by a tightly bounded question over one conversation. The owner needs forensic usefulness without granting the system a license to search all personal data or hallucinate from a summary.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** background retrieval constrained to one conversation and time interval; realtime only for the final short answer
- **latency:** Under 4 seconds for a bounded conversation; refuse or ask for a narrower interval when the scope is ambiguous.
- **cost:** Moderate retrieval and transcription lookup cost; low generation cost because evidence is prefiltered and capped.
- **security:** Require an explicit conversation/time binding, return citations and confidence, and never search unrelated browser tabs or Mac files. Raw audio remains local unless the owner explicitly requests playback. Deletion must invalidate the evidence index as well as the transcript.
- **missing:** Conversation-scoped evidence manifests linking audio segments, transcript spans, and resulting actions; A least-privilege retrieval route with hard scope and result limits; Evidence-aware answering that cannot cite summaries without their underlying source span


## Changes it proposed to its own stack

### `integration` — Add a durable intent-correlation index that assigns one opaque intentId at request intake and attaches it to relay jobs, Mac ledgers/receipts, browser commands/results, routine attempts, and pendant event receipts. Expose a read-only timeline query with explicit states (planned, dispatched, completed, failed, unknown) and source provenance.
- **owner gets:** The owner can ask what happened and receive one truthful timeline instead of manually joining unrelated IDs; failures and partial completion become visible rather than sounding like success.
- effort: Medium: schema migration plus adapters at intake and each receipt writer, followed by backfill where correlation is provable. Start with new events and mark historical joins unknown.  ·  risk: A bad join could falsely attribute an action. Use opaque IDs, append-only links, confidence/provenance, and never merge solely on timestamps or similar text. If the index is unavailable, execution continues and the timeline says unindexed.
- cost: Small D1/local JSON metadata overhead; negligible model cost.  ·  latency: Under 10 ms on writes if append-only; timeline reads may be 100–500 ms.
- security: The index must inherit existing bearer/session authorization and redact sensitive params; it should store hashes and labels, not page contents or secrets.
- depends on: A stable intent ID generated before POST /plan or job creation; Adapters for /jobs receipts, /journal, /browser/result, pipeline events, and pendant delivery receipts; Retention and redaction rules aligned with the owner's action-history versus fact-erasure policy


## What it asked for

_Nothing._
