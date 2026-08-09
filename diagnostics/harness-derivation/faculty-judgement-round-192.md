# Harness derivation — faculty-judgement — round 192

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before I act on anything you told me from the web, tell me whether the underlying page or source has changed—and stop the action if it has."
- **useful because:** The owner should not book, buy, send, or approve from a stale page merely because the assistant's earlier answer sounded confident. This is a real cross-body safety property: the browser has the authenticated page, the Mac prepares the action, the relay coordinates, and the pendant supplies deliberate approval.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-judgement → faculty-action
- **model tier:** background for source snapshots and change detection; realtime only to summarize a detected conflict or ask for physical confirmation
- **latency:** Under 2 seconds for a read-only recheck; under 5 seconds when the browser must wake and inspect the page; never block ordinary conversation on a full crawl.
- **cost:** Roughly $0.001–$0.01 per recheck depending on whether a model must interpret changed fields; browser and hash comparison dominate latency, not tokens.
- **security:** Only store redacted field hashes and source identifiers by default, not page bodies. A changed page must fail closed, not silently refresh into a different transaction. External submission still requires the existing physical approval latch and autonomy policy. Every block must cite the source and changed field.
- **missing:** A durable source snapshot/change-token record joined to the pending plan (the current cross-surface IDs are not a real foreign key); A browser read-only endpoint that returns typed changed fields plus provenance for a plan's source; An executor gate that refuses stale plans before POST /execute or browser submission

### "Make my spoken briefings learn how much I actually absorb: if I miss or interrupt an item, bring back only the useful part later, and stop repeating things I finished hearing."
- **useful because:** Today the system can generate and queue audio but cannot know whether the pendant downloaded, started, finished, or was interrupted. The owner gets either repetition or silent loss. Delivery acknowledgements let the relay adapt future briefings to reality rather than assuming generation equals hearing.
- **path:** pendant → relay-realtime → mac-planner → faculty-perception → faculty-judgement
- **model tier:** background for item-level compression and deduplication; realtime only for a brief interruption response
- **latency:** ACK ingestion under 200 ms; adaptation at the next briefing or within 30 seconds of a missed item; no model call for a clean playback finish.
- **cost:** Under $0.005 per adapted briefing in the common case; the expensive part is optional summarization of interrupted items, not ACK storage.
- **security:** ACKs must contain opaque artifact/item IDs and positions, never transcript or audio. Interrupted private content must not be re-spoken automatically; route it through the existing confidentiality and attention policy. Duplicate events must be idempotent and offline replay must preserve ordering.
- **missing:** A durable join from briefing item ID to generated artifact and source evidence; A policy-aware reducer that turns downloaded/started/finished/interrupted events into a future queue decision; A writer from the Mac/relay briefing scheduler into the existing audio ACK event path

### "When you say you finished something, prove that the intended result exists—not just that a command returned successfully—and tell me what remains uncertain."
- **useful because:** A successful click, AppleScript exit, or queued job is not the same as an email being saved, a reminder existing, or a page actually changing. The owner needs outcome truth, especially when the Mac, browser, relay, and pendant each observe a different stage of the same task.
- **path:** mac-planner → browser-extension → relay-realtime → faculty-perception → faculty-action → pendant
- **model tier:** cheap deterministic checks first; background model only to reconcile conflicting observations into one short owner-facing sentence
- **latency:** Immediate receipt remains fast; verification within 3 seconds for local state and 10 seconds for browser round trips. If verification is unavailable, report 'accepted, not verified' rather than waiting indefinitely.
- **cost:** Usually below $0.002 per action because typed postconditions and hashes avoid model use; ambiguous conflicts may cost $0.01.
- **security:** Verification must be read-only and least-privilege. Never infer success from a screenshot or optimistic UI alone. Sensitive result fields stay local and the spoken response contains status, timestamp, and evidence reference only. Destructive actions require confirmation before execution, independent of verification.
- **missing:** A typed postcondition attached to each prepared action; A read-only verifier registry for Mac and browser outcomes (including negative evidence such as permission-denied or stale session); A durable linkage between relay job, Mac action, browser command, receipt, and verification result

### "When you tell me something important, have the browser, my Mac, and an independent public source check it separately; if they disagree, tell me the disagreement instead of choosing the smoothest story."
- **useful because:** The owner cannot have a trustworthy personal AI while one model can turn a stale page, a permission-shaped empty result, or a plausible inference into a confident sentence. Independent observations from physically different surfaces catch errors no single node can see, especially for travel, account state, deadlines, and device health.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement → pendant
- **model tier:** Cheap deterministic normalization and comparison first; use the expensive realtime model only to explain a genuine conflict in one short spoken sentence. Background models can cluster recurring source disagreements.
- **latency:** Three read-only observations within 5 seconds for an explicit owner question; if one surface is offline, answer with a named missing witness rather than waiting. No quorum is required for low-stakes conversation unless the owner asks for verification.
- **cost:** Typically $0.002–$0.02 per checked claim; browser/Mac reads dominate latency, while model cost is limited to conflict explanation and entity normalization.
- **security:** Sources must be queried with least privilege and independent evidence must not be copied wholesale into the relay. Store claim hashes, timestamps, source IDs, and disagreement spans; redact secrets before cross-surface comparison. Never treat agreement between two derived model summaries as independent evidence.
- **missing:** A typed claim-check request and source-specific observation adapters; A durable claim identity linking the same proposition across browser, Mac, and relay observations; A quorum/conflict evaluator that distinguishes independent agreement, stale agreement, and correlated copies; Owner-facing spoken and dashboard output that names confidence, freshness, and the absent or dissenting witness

### "If I correct you once, make that correction stick everywhere: stop repeating the wrong fact, mark earlier answers that depended on it, and ask me again only when the new fact is uncertain."
- **useful because:** Today a correction can disappear into one conversation while stale copies remain in Mac memory, browser-derived findings, relay context, and future spoken briefs. The owner should not have to win the same argument with the system repeatedly or know which body retained the error.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → pendant
- **model tier:** Deterministic propagation and dependency invalidation first; background model only to identify semantically equivalent claims and draft a concise clarification request.
- **latency:** A direct correction should suppress the old claim immediately on the local surface and propagate within 2 seconds when connected; dependency review may continue in the background. Never delay the owner's acknowledgement on a full graph scan.
- **cost:** Usually under $0.005 per correction; semantic matching of old claims is the dominant model cost and can be bounded to recent claims.
- **security:** A correction is not automatically proof: distinguish owner assertion from independently verified fact, preserve the old value as a revocable audit tombstone, and do not expose sensitive prior values in spoken confirmations. Propagation must be idempotent and scoped by claim identity, not broad keyword deletion.
- **missing:** A durable cross-surface claim/dependency graph linking facts, evidence capsules, briefs, and actions; A correction event writer reachable from voice, Mac, and browser surfaces; Fan-out invalidation/retraction into Mac memory, relay fleet memory, browser provenance, pending briefings, and action plans; A compact owner review showing what was suppressed, what was rechecked, and what remains uncertain

### "When you are blocked or uncertain, ask me the one question that most reduces the chance of a wrong outcome—not a list of everything you could not infer—and remember my answer only for the scope I choose."
- **useful because:** The owner currently gets either confident guesses or sprawling clarification requests. A judgment layer should rank missing information by consequence, ask one precise question through the pendant, and avoid turning a temporary answer into a permanent preference or permission.
- **path:** faculty-judgement → faculty-perception → relay-realtime → pendant → mac-planner → browser-extension
- **model tier:** Deterministic risk and dependency ranking first; realtime model for phrasing a single spoken question; background model for clustering unresolved questions over time.
- **latency:** Under 1 second to decide whether clarification is necessary and which missing field matters most; one spoken question under 5 seconds. The system must proceed read-only when the owner is unavailable rather than repeatedly interrupting.
- **cost:** Under $0.005 per clarification in the normal case; semantic dependency ranking is the main model expense and should be cached per plan.
- **security:** Questions must reveal the minimum context needed and never read secrets aloud to elicit an answer. Answers need explicit scope, expiry, and provenance; 'yes' to one action must not become blanket permission. External side effects remain gated by autonomy policy and physical approval.
- **missing:** A typed uncertainty/dependency representation on plans and claims; A risk-weighted question selector that can compare missing fields and deadlines; A scoped answer store with expiry and explicit owner visibility; A relay-to-pendant question/answer correlation that survives a dropped link without replaying stale questions


## Changes it proposed to its own stack

### `integration` — Make every prepared cross-surface action carry a durable action envelope: relayJobId, localJobId, browserCommandId/actionId, evidence refs, typed postconditions, expiry, and verification status. Persist the mapping in the relay and Mac stores; after execution, run only read-only postcondition checks, emit a verified/accepted/unverified/contradicted receipt, and block downstream actions when a required postcondition is contradicted. Reuse the existing actionIdFor idempotency and the routine lease implementation as patterns rather than creating another ledger.
- **owner gets:** The pendant can finally say 'the reminder exists' or 'the page did not change' truthfully, instead of treating a successful command as success. Failures become recoverable and understandable across the bodies.
- effort: Medium-high: schema migration plus bridge propagation, typed verifier adapters for a small initial set (reminders, files, browser page fields), and postcondition tests. Start with one end-to-end reminder and one browser form flow.  ·  risk: Old jobs lack envelopes and must be labeled unverifiable. A bad verifier could falsely block a successful action, so fail closed to 'unverified' and preserve the raw receipt. Mapping data is sensitive operational metadata and needs local encryption/access controls.
- cost: Negligible storage and one extra read per action; occasional background model reconciliation only for conflicting observations.  ·  latency: Adds 0.2–3 seconds to actions that request verification; no impact when the owner explicitly asks for fire-and-forget execution.
- security: Improves safety by preventing optimistic completion claims; must keep postcondition reads least-privilege and avoid copying sensitive page values into relay receipts.
- depends on: A durable relay-job-id to Mac-job-id mapping (currently telemetry-only); Typed postconditions in POST /plan and POST /preview; Read-only verifier adapters for existing Mac/browser routes; Lease/requeue for orphaned relay jobs so verification is not lost after a crash


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities and one implementation change. (1) A stale-source firewall rechecks authenticated browser evidence before any prepared action and fails closed on changed fields. (2) Delivery-aware briefings use the pendant's downloaded/started/finished/interrupted ACKs to avoid repeating unheard items and compress recoveries. (3) Verified outcomes distinguish command acceptance from the intended result, with a durable cross-surface action envelope and typed postconditions. The most useful is verified outcomes: it stops the system claiming 'done' when only a click or process exit occurred. I also discovered the live owner projection still contains a timezone conflict (owner memory says America/Chicago while authoritative Mac routine policy is America/New_York); that must remain explicitly unresolved rather than silently chosen.

**Biggest unknown:** The implementation still needs a durable relay↔Mac↔browser ID mapping, typed postconditions and read-only verifier adapters, plus relay job leases/requeue. I do not need another orchestrator permission to design these; I need those code paths wired. The stale-source proposal is close to the existing physical-approval cluster, so its distinct value is specifically precondition freshness and changed-field fail-closed behavior, not another approval latch.

