# Harness derivation — unified — round 184

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before you submit this form, show me the exact amount and recipient; I’ll approve it on the pendant only if the page has not changed."
- **useful because:** Prevents a stale or manipulated browser page from turning an intended purchase, transfer, or booking into a different one. The owner gets a physical, last-moment confirmation bound to the actual browser state rather than a generic approval.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** deterministic for DOM extraction, hashing, and policy; realtime only to explain the compact diff
- **latency:** Under 1 s to capture and hash the bound fields; under 2 s from pendant approval to submit, excluding page/network latency
- **cost:** Near-zero model cost for extraction and digesting; occasional realtime explanation under $0.01 when values are ambiguous
- **security:** Only explicitly bound fields and origin are included in the digest; never send passwords or full page contents to the relay. Require physical_transaction_approval_latch nonce, expiry, origin, action type, and a digest of normalized field values. Abort on any DOM/value/origin change, duplicate nonce, or navigation.
- **missing:** browser DOM field-binding and stable normalization contract; relay persistence/verification of browser-state digest alongside the physical approval nonce; a safe browser submit primitive that refuses to submit unless the digest still matches

### "Tell me when a scheduled task silently failed or never finished, and give me one concise recovery choice on the pendant."
- **useful because:** Today a routine can run, stall, or produce no useful result without the owner knowing. This turns silence into an actionable promise: correlate the routine deadline, relay job, Mac/browser work, and delivery evidence, then surface only a compact failure alert with retry, defer, or inspect choices.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** background deterministic correlator for deadlines and receipts; cheap background model only for a one-sentence explanation
- **latency:** Evaluate within 30 s of a deadline or lease expiry; alert generation under 2 s
- **cost:** Negligible for correlation; <$0.01 per exception for wording
- **security:** Alert only on routines explicitly opted into completion monitoring. Include job IDs and failure class, not page contents or audio. Retry must obey replaySafety and never replay unrepeatable actions automatically.
- **missing:** per-routine expected-completion/deadline and escalation policy; relay job lease expiry/requeue sweep for processing jobs; a single alert payload that can reference evidence without exposing it; pendant action mapping for retry/defer/inspect

### "When you learn a fact about me without me asking you to remember it, ask me to keep or discard it before it enters long-term memory, and let me erase it later with all its copies."
- **useful because:** The owner cannot currently see what the system extracts into facts and the context graph. Quarantining inferred facts makes memory a visible choice, while provenance-linked deletion removes the fact, derived copies, and evidence capsule without destroying the audit trail of actions.
- **path:** relay-realtime → mac-planner → pendant → dashboard
- **model tier:** cheap background extraction and deterministic provenance graph; realtime only when asking for a short keep/discard decision in the next conversation
- **latency:** Quarantine synchronously with extraction; ask at the next natural conversation boundary, never interrupt active speech
- **cost:** Small background-model call per candidate fact; <$0.01 typical, with no call for explicit user-created reminders or notes
- **security:** Do not retain raw audio solely to justify a fact. Store minimal redacted evidence capsule, source turn ID, confidence, and derived-copy IDs. Off-machine deletion is reported requested-and-pending; job history remains untouched.
- **missing:** fact quarantine state machine and owner-facing list/detail/delete routes; provenance edges from facts to context-graph entities and evidence capsules; a non-interrupting pendant prompt/response protocol that works on the next conversation; relay replication and deletion receipts for off-machine copies

### "Revoke only the browser session that is signed into my bank, without shutting down the rest of you."
- **useful because:** Today privacy controls are broad: the owner can latch the pendant, but cannot surgically cut one compromised or misplaced session while preserving ordinary conversation and other work. A per-session kill action would limit damage from a stolen browser tab, stale extension, or unexpected Mac process.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** deterministic policy and token revocation; no model call required
- **latency:** Under 2 seconds from the physical gesture or spoken request to relay revocation; browser/Mac acknowledgement within 10 seconds
- **cost:** Negligible compute and model cost; bounded revocation records in relay storage
- **security:** The pendant must authenticate the revocation with its physical transaction counter. Relay invalidates only the selected session and all descendant command leases; it must not accept a stale browser heartbeat to resurrect it. Show target origin, tab identity, and last-seen time before confirmation.
- **missing:** scoped session identity shared by relay, browser extension, and Mac agent; relay-side revocation list with generation counters; browser and Mac acknowledgement plus non-resurrection behavior; a pendant selection/readback flow for choosing one session

### "For the next hour, keep this conversation private: do not retain audio, do not use browser contents, and do not let queued work mention it later."
- **useful because:** A permanent privacy latch is too blunt for ordinary sensitive moments, while normal operation exposes data across relay, Mac, browser, and queued jobs. A time-bounded, purpose-scoped privacy lease would let the owner have a private conversation without disabling the whole device or relying on memory that they must undo it later.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic enforcement; realtime only to explain which surfaces were blocked
- **latency:** Local capture/retention policy changes within one audio frame; cross-surface convergence under 5 seconds
- **cost:** Negligible model cost; small signed policy lease and convergence receipts
- **security:** The lease must be fail-closed for retention and browser exposure, have an explicit expiry, survive link loss locally, and report pending off-machine deletion honestly. It must not silently erase the audit trail of actions performed before the lease.
- **missing:** signed scoped privacy-policy envelope understood by pendant, relay, Mac, and browser; capture/queue admission checks that enforce purpose and retention before data is written; automatic expiry and convergence receipt for every surface; owner-visible distinction between blocked, dropped, and already-persisted data

### "Only let my Mac perform this sensitive action while the pendant is physically present and has recently attested it, even if the relay account is compromised."
- **useful because:** A one-time approval protects a single action, but it does not prevent a stolen relay credential from issuing a new action later. Continuous short-lived proximity attestation makes the worn device a second factor for sensitive Mac/browser work without exposing secrets to the pendant.
- **path:** pendant → mac-planner → relay-realtime → browser-extension → dashboard
- **model tier:** deterministic cryptographic verification; no model call required
- **latency:** Attestation refresh every 15–30 seconds; action authorization under 200 ms when a fresh attestation exists
- **cost:** Negligible model cost; small relay records and cryptographic operations
- **security:** Use a device-held signing key and monotonic counter, never raw secrets. Bind the attestation to action class, Mac identity, browser origin where relevant, and a short expiry. USB presence can establish proximity today; LTE-only mode must fail closed unless the owner explicitly chooses another policy.
- **missing:** device key provisioning and signed attestation firmware; Mac bridge verifier and relay challenge service; scoped sensitive-action policy rather than one global gate; clear offline behavior and recovery when USB is unplugged


## Changes it proposed to its own stack

### `browser-harness` — Add a submission guard that records a normalized, field-level digest (origin, URL pattern, labels, values, currency, recipient, and action button identity) at preview time and rechecks it immediately before any submit/click. Return a structured changed-fields diff and refuse on navigation, stale inspection, or missing binding.
- **owner gets:** A page changing underneath an approval becomes a visible refusal instead of a silent wrong purchase or booking.
- effort: Medium: browser inspection normalization, digest persistence, and one guarded submit path; test against navigation, dynamic totals, and currency changes.  ·  risk: False refusals on harmless DOM churn; recover by asking for a fresh preview, never by silently widening the binding.
- cost: No model cost; small digest and field metadata per pending action.  ·  latency: Adds one inspection and hash comparison, typically tens to hundreds of milliseconds.
- security: Improves security; only hashes explicitly selected fields and excludes secrets. Requires origin and expiry binding.
- depends on: physical_transaction_approval_latch; browser inspection result with stable field selectors; relay-side approval record that stores the digest

### `relay` — Introduce a completion-watch record for opted-in routines: expected deadline, terminal evidence predicates, replaySafety policy, and escalation state. A sweeper marks jobs missing evidence as overdue, links the relevant Mac/browser receipts, and emits one deduplicated pendant alert with retry/defer/inspect actions.
- **owner gets:** The system stops pretending a routine succeeded merely because it started; missed news, failed uploads, and hung browser tasks become visible without noisy status spam.
- effort: Medium-high: schema, lease expiry/requeue, evidence predicate evaluator, and alert deduplication.  ·  risk: An incorrect deadline could create nuisance alerts or unsafe retries; default to inspect-only and require explicit per-routine retry policy.
- cost: Low storage and background CPU; no realtime model calls for normal cases.  ·  latency: Up to the configured sweep interval, target 30 seconds after deadline.
- security: Keeps evidence references opaque and does not expose browser content in pendant alerts.
- depends on: relay_jobs lease_until and requeue sweep; routine completion contract; offline_alert_inbox; audio_delivery_ack_queue

### `memory` — Add a provenance-preserving fact quarantine store: candidate facts remain pending, carry source turn and derived-copy IDs, and can be accepted, rejected, or erased as a single tombstone transaction across facts.json/context graph/relay replicas. Keep action history separate and immutable.
- **owner gets:** The owner can finally see and control what the system inferred about them, instead of discovering an invisible memory only when it affects a later answer.
- effort: Medium: store and UI/API state machine, graph edge tracking, redacted evidence capsule, and asynchronous off-machine deletion receipts.  ·  risk: A missing provenance edge could leave a derived copy behind; block final deletion until every known copy is acknowledged or explicitly reported pending.
- cost: Small persistent metadata; background calls only for candidate extraction and summarization.  ·  latency: No impact on conversation response; review occurs at the next natural turn.
- security: Reduces retention by default; never stores raw audio solely for memory provenance.
- depends on: owner-facing fact list/detail routes; context-graph provenance edges; relay deletion receipt; non-interrupting next-turn pendant prompt

### `integration` — Create a signed, expiring privacy-policy envelope with independently enforced fields: capture_allowed, browser_exposure_allowed, retention_allowed, queued_job_allowed, and expiry. Require every write/admission path to evaluate it before persistence, and have the pendant, relay, Mac, and browser return a convergence receipt naming each surface's effective state.
- **owner gets:** The owner can invoke a private interval and trust that it is enforced consistently, rather than hoping one global mute also stopped browser exposure and queued persistence.
- effort: High: policy schema, admission hooks, offline pendant cache, relay propagation, expiry, and convergence tests.  ·  risk: A missed admission hook could create false privacy confidence; ship fail-closed for unknown policy states and expose incomplete convergence prominently.
- cost: Low storage and cryptographic overhead; no routine model cost.  ·  latency: One local policy check per capture/queue/browser admission; propagation under seconds when connected.
- security: Strongly improves privacy if fail-closed; adds signed policy state and explicit pending deletion semantics.
- depends on: local_privacy_latch; privacy_convergence_check; relay policy propagation; capture and browser admission hooks

### `hardware` — Provision a per-pendant signing key and monotonic attestation counter, with a challenge-response protocol over the existing USB serial path first and LTE path later. Bind each attestation to device identity, transport, action class, and a 30-second expiry; reject rollbacked counters.
- **owner gets:** Sensitive Mac and browser actions can require the pendant to be physically present, so a stolen relay token alone cannot authorize them.
- effort: High: secure key storage choice, firmware signing path, Mac verifier, relay challenge endpoint, clock/expiry handling, and recovery after reset.  ·  risk: Lost or reset key could strand sensitive actions; provide a deliberate re-enrollment ceremony and never silently fall back to bearer-token-only authorization.
- cost: Small firmware and relay overhead; hardware cost depends on whether protected key storage is available on the current board.  ·  latency: Tens of milliseconds locally; up to one round trip when the relay must issue a challenge.
- security: Adds a meaningful second factor and replay resistance; requires careful key lifecycle and revocation.
- depends on: physical_transaction_approval_latch; USB fallback audio/session transport; scoped sensitive-action authorization; device identity provisioning


## What it asked for

_Nothing._
