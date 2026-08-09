# Harness derivation — unified — round 203

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before you do anything sensitive, tell me exactly what will leave my Mac, browser sessions, pendant, and relay, then let me approve the smallest safe version."
- **useful because:** The owner gets a concrete data-egress boundary across authenticated browser tabs, Mac files, relay storage, and pendant audio instead of trusting a vague privacy promise. It turns privacy from a latch that stops future capture into a decision made before a cross-surface action.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic policy and redaction first; use the background tier to summarize only ambiguous fields. Realtime is used only to explain the capsule and collect a short confirmation.
- **latency:** Under 1 s for the egress inventory and redaction preview; under 3 s for a spoken explanation. Any browser/Mac mutation waits for explicit confirmation and can take minutes afterward.
- **cost:** Usually <$0.01 per invocation; deterministic hashing, path classification, and browser target inspection dominate, with model cost only for ambiguous content labels.
- **security:** Never upload raw page contents or audio merely to classify them. Produce a signed egress capsule containing destination, field class, sensitivity, retention, and exact redaction rule. Require confirmation for off-machine, irreversible, or uncontained destinations; record the decision without storing the secret data.
- **missing:** A read-only egress inventory over the actual browser command payloads, Mac action parameters, relay persistence targets, and pendant audio route; A dashboard/pendant rendering for the capsule and a binding from its digest to physical_transaction_approval_latch; A policy engine that can redact or refuse fields before POST /execute or browser submission

### "Stage this task for me to approve later, and when I next talk to you, show me exactly what is still pending, what changed, and let the pendant approve only the unchanged safe plan."
- **useful because:** The owner can deliberately defer consequential work without losing it when the Mac, browser, or relay is offline. On the next natural conversation the system can recover the staged plan, detect world drift, and request one physical approval rather than silently discarding or replaying it.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic staged-plan, digest, lease, and replay-safety checks; background tier drafts the short pending summary; realtime only handles the next-turn spoken confirmation.
- **latency:** Staging and drift check under 500 ms; pending summary under 2 s. Execution begins only after approval and remains asynchronous with receipts.
- **cost:** <$0.01 when no summary rewrite is needed; storage and browser/Mac state inspection dominate, not inference.
- **security:** Bind approval to plan digest, world fingerprint, expiry, and a monotonic transaction nonce. Auto-resume only idempotent/additive steps; require fresh approval for unrepeatable, unknown, irreversible-write, off-machine, or uncontained steps. Never treat a spoken 'yes' as approval if the digest or world moved.
- **missing:** Relay implementation of the existing approval handoff store and delivery/readback path; A next-conversation pending-approval selector that can surface a staged item without unprompted audio push; Orchestrator closeLedger integration and relay job leases/requeue before any automatic resume

### "Run a release gate on the real pendant and bridge before you ship an audio or firmware change, and refuse to call it healthy unless the owner can see and hear the proof."
- **useful because:** The owner gets a single honest answer to 'is it safe to ship?' based on measured hardware evidence: both audio directions, loss and jitter tolerance, timing, clipping, bridge buffering, and a correlated receipt. It prevents a green software build from masking a degraded worn-device experience.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic test orchestration and threshold evaluation; background tier writes the human summary. Realtime is not needed except to answer a live owner question about the result.
- **latency:** A smoke gate in 30 s and a full fault matrix in 3–5 min. No production conversation is interrupted; tests run only when explicitly requested or scheduled.
- **cost:** <$0.05 per full matrix; most cost is device airtime/test runtime and artifact storage, with little model spend.
- **security:** Use synthetic, non-speech fixtures only; never capture room audio. Tag every artifact with firmware, codec profile, bridge identity, and test seed. A failed or incomplete test must be FAILED/UNKNOWN, never silently downgraded to healthy.
- **missing:** A safe trigger that runs the existing on-device selftest fixture and captures pendant plus ESP32 counters; Correlation between audio_link_fault_inject runs, audio_pipeline_validate output, bridge acknowledgements, and firmware identity; A dashboard release-gate report with immutable thresholds and signed receipts

### "When you act in my browser, prove you are still on the exact account and tab I approved; if the tab navigates, logs out, or changes identity, stop and tell me instead of guessing."
- **useful because:** Authenticated browser sessions are the highest-consequence surface: a stale or redirected tab can turn a harmless action into a message, purchase, or disclosure to the wrong place. The owner gets an identity firewall that fails closed on navigation, login, origin, or DOM identity drift.
- **path:** browser → relay → mac-bridge → pendant → dashboard
- **model tier:** Deterministic origin/session/tab binding, challenge markers, and DOM identity checks; background tier only explains a mismatch. Realtime speaks the stop reason when the owner is present.
- **latency:** Check binding before every mutating browser action in under 200 ms; stop immediately on heartbeat or result mismatch. Recovery can wait for the owner and never auto-continue after identity drift.
- **cost:** <$0.005 per action; hashes and extension heartbeats dominate, with negligible model use.
- **security:** Bind a command to browser session ID, tab ID, origin, account fingerprint, URL pattern, and a redacted page identity hash—not page secrets. A redirect, login-state change, extension restart, or stale lease invalidates the command. Do not expose cookies, tokens, or raw page contents to the relay. Require the pendant physical approval again for any rebind.
- **missing:** Extension-provided authenticated account and page identity attestations that exclude secrets; Relay storage and verification of the binding at command claim and result time; A browser action middleware that fails closed before POST /execute and a pendant-visible stop receipt

### "When you act for me, let me ask 'why did you do that?' and receive a tamper-evident, human-readable chain from my words and the evidence you saw to each decision, tool call, and observed outcome—without exposing secrets from the browser or Mac."
- **useful because:** Today the owner can inspect scattered jobs, receipts, and browser results, but cannot reconstruct whether an action was caused by their request, an inferred fact, a stale plan, or an agent mistake. A causal explanation chain makes the system accountable and lets the owner challenge one decision without deleting the underlying audit trail.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic event and provenance graph first; use the background tier to render a concise explanation from already-redacted events. Realtime only answers a live spoken 'why' question.
- **latency:** Return the causal skeleton in under 500 ms; render a spoken summary in under 2 s. Deep inspection can be asynchronous and paginated.
- **cost:** <$0.01 per query; indexing and redaction dominate, with model tokens limited to the selected chain rather than the full history.
- **security:** Store hashes, event types, timestamps, actor/surface, policy decisions, and redacted references—not cookies, raw page contents, secrets, or room audio. Preserve the immutable audit record even if an extracted fact is erased; distinguish explanation from evidence and label missing links instead of inventing reasons.
- **missing:** A cross-surface provenance event envelope with parent IDs, input/evidence references, policy version, model tier, and outcome; Relay indexing and retention of the envelope across pendant, Mac, browser, and job records; Owner-facing redaction and causal-chain rendering, including an explicit UNKNOWN when a surface emitted no receipt

### "If one surface starts behaving inconsistently, quarantine only that surface, keep my conversation and unrelated work alive, and tell me exactly what is frozen, what is safe, and what evidence is needed before it is allowed back."
- **useful because:** A browser lease failure, bridge drop, or stale Mac job should not force the owner to lose an entire conversation or let a damaged surface keep acting. This gives the hive a fault boundary the owner can understand: isolate the suspect node, preserve safe service, and require evidence before reintegration.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic health correlation, capability revocation, and recovery gates; background tier summarizes the incident and safe alternatives. Realtime speaks the short quarantine notice only when it affects the current conversation.
- **latency:** Freeze a suspect surface within one heartbeat or 1 s of a correlated failure; preserve the live voice path within 2 s. Revalidation may take minutes and never silently unfreezes a surface.
- **cost:** <$0.01 per incident; telemetry and receipts dominate, with model use limited to summaries.
- **security:** Fail closed for the affected surface, revoke outstanding leases and staged commands, and preserve immutable evidence. Do not cancel unrelated owner data or erase audit records. Re-enable only after identity, health, and command-lease checks pass; require physical approval for any mutation queued before quarantine.
- **missing:** A cross-surface circuit breaker with per-surface capability leases rather than one global online flag; A revocation protocol understood by relay jobs, browser commands, Mac jobs, and pendant inbox/outbox; A revalidation receipt that proves no quarantined command executed during the outage

### "Let me set where each kind of information is allowed to live, and have the system prove that a task stayed on my Mac or pendant unless I explicitly allowed relay storage or browser exposure."
- **useful because:** The owner currently has retention and deletion rules, but no enforceable per-data residency boundary. A task can cross Mac, browser, relay, and pendant without a single owner-visible proof of where its content was processed or persisted. Residency controls make 'local only' a real guarantee rather than a preference.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic data labels, route enforcement, and receipt verification; background tier explains a violation or proposes a downgraded plan. Realtime is only for a spoken policy change or refusal.
- **latency:** Evaluate a residency policy before dispatch in under 200 ms; reject an incompatible route before bytes leave the permitted surface. Audit queries return in under 1 s.
- **cost:** <$0.01 per task; hashes, policy checks, and receipts dominate, with little model use.
- **security:** Label data classes without copying raw contents. The relay must be able to coordinate opaque handles without seeing local-only payloads. A missing or unverifiable residency receipt is a policy violation, not success. Policy changes require explicit owner confirmation and should not retroactively rewrite history.
- **missing:** A data-label and residency policy attached to plans, browser commands, audio artifacts, and extracted facts; Route enforcement at relay ingress, Mac execution, browser submission, and pendant storage; Signed per-hop receipts proving processing and persistence location, plus a violation/quarantine path


## What it asked for

### `t26-77to` (tool) — browser_identity_attestation
- why: A browser command must fail closed if its approved tab, origin, account, or login state changes. Existing browser heartbeat/poll/result routes carry commands but no least-privilege identity proof.

```json
{
  "type": "object",
  "properties": {
    "sessionId": {
      "type": "string"
    },
    "tabId": {
      "type": "string"
    },
    "commandId": {
      "type": "string"
    },
    "expectedOrigin": {
      "type": "string"
    },
    "expectedUrlPattern": {
      "type": "string"
    },
    "includePageIdentityHash": {
      "type": "boolean"
    }
  },
  "required": [
    "sessionId",
    "tabId",
    "commandId",
    "expectedOrigin",
    "expectedUrlPattern"
  ]
}
```

## Its own summary

This round I confirmed the live surfaces (Safari with four tabs, Mac bridge online, pendant still not LTE-registered) and recorded four owner-facing capabilities: (1) cross-surface data-egress preview with narrow pendant approval, (2) deferred staged actions that resume only when digest/world/replay-safety checks permit, (3) a measured release gate for the real 24 kHz pendant/bridge path, and (4) a browser identity firewall that stops on tab/account/origin drift. I also queued browser_identity_attestation (t26-77to), a least-privilege tool needed to make the fourth capability enforceable.

**Biggest unknown:** The largest remaining product gap is not audio quality; it is wiring the already-written approval and recovery machinery into production: relay persistence/delivery for approval records, orchestrator ledger closure, job leases/requeue, and a next-conversation path for pending approvals. For the new browser firewall, the extension still needs to emit secret-free account/page identity attestations. USB remains bench-only and is not a product transport.

