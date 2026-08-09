# Harness derivation — unified — round 224

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Continue the safe parts of something interrupted while my Mac or browser was down, and tell me what you deliberately left waiting for me."
- **useful because:** Today an outage can leave work half-done, while the existing resume engine is only a human-discovered preview and ordinary ledgers falsely look interrupted. This would recover idempotent/additive work without duplicating unrepeatable actions, and make the boundary audible.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** background deterministic planner; use the expensive model only to explain an ambiguous step after the safety engine refuses to decide
- **latency:** Resume scan on startup under 3 seconds; each safe continuation should begin within 30 seconds of a lease becoming available
- **cost:** Near-zero model cost for replaySafety/riskTier decisions; small background synthesis only for the owner-facing summary
- **security:** Never auto-replay unrepeatable or unknown steps. Require the physical transaction approval latch plus a fresh in-conversation confirmation for irreversible/off-machine work. Preserve an immutable receipt of skip/rerun/blocked decisions.
- **missing:** Wire orchestrator completion to closeLedger so successful plans stop appearing interrupted; Add expiring relay job leases and a requeue sweep; Call planResume at startup and route only idempotent/additive steps into execution; Connect pending approval delivery to the pendant’s staged-transaction state

### "Before you change anything important, show me a compact, human-readable consequence map of the exact files, accounts, browser tabs, and messages it would touch, then let me approve that unchanged plan from the pendant or cancel it."
- **useful because:** The current blocked-plan path can speak that approval is needed but has no reliable owner-facing completion loop. A consequence map makes the scope legible before harm, binds consent to the exact plan and world state, and gives the wearable a physical confirmation path instead of treating the bearer token as approval.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic planner and world fingerprint; background model only rewrites the already-computed diff into plain language
- **latency:** Preview under 3 seconds for local actions; approval remains valid only for a short lease and execution starts within 5 seconds of a valid pendant approval
- **cost:** Low-to-moderate: hashing and state inspection dominate; one short background explanation for complex plans
- **security:** Never include page secrets or form values in the pendant. Bind approval to plan digest, world fingerprint, expiry, and nonce; reject drift, replay, or cancellation. Keep approval and execution privileges separable when possible.
- **missing:** A reachable caller from normal planning into POST /prepare; Relay persistence and delivery for the existing approval handoff contract; A dashboard control that displays the consequence map and pending state; An execution-side authorization boundary distinct from the general agent token

### "For each routine I schedule, tell me whether its intended outcome actually happened—not merely that the routine fired—and quietly retry only idempotent steps or tell me what needs my attention."
- **useful because:** A timer firing is not the same as a result: a briefing may not be delivered, a browser action may fail after dispatch, and a reminder may be created in the wrong account. This gives scheduled work the same accountability a human assistant would have, without duplicating irreversible actions.
- **path:** relay → mac-bridge → browser → dashboard → pendant
- **model tier:** background deterministic verifier using declared outcome checks; use a cheaper model only to summarize ambiguous evidence
- **latency:** Verify within 60 seconds of routine completion; surface failures on the next natural pendant interaction, never interrupting live speech by default
- **cost:** Low: one bounded verification pass per routine; model cost only for ambiguous evidence, with deterministic checks for receipts and state
- **security:** Outcome checks must be explicitly declared per routine and restricted to bound apps/tabs. Do not scrape unrelated pages or infer success from absence of errors. Retries require replaySafety/idempotency checks and irreversible outcomes require approval.
- **missing:** A routine schema for expected outcomes and evidence queries; A post-run verifier joining routine receipts with Mac/browser state; A retry planner keyed on replaySafety rather than generic failure; Owner-facing failure/attention disposition that does not silently discard the result

### "Let me mark a browser tab, app, folder, or named kind of information as “never show this to the model,” and enforce that boundary across screenshots, page reads, logs, receipts, and relayed context until I explicitly remove it."
- **useful because:** The owner should not have to trust that a sensitive page happened not to appear in a prompt. A durable, inspectable exclusion boundary makes privacy predictable across the browser, Mac, relay, and future model calls.
- **path:** browser → mac-bridge → relay → dashboard → pendant
- **model tier:** deterministic policy enforcement before capture/serialization; no model call may override or reinterpret the exclusion
- **latency:** Policy check before every capture/read/receipt under 50 ms locally; changes converge to relay and browser within 2 seconds
- **cost:** Low: policy matching and redaction are deterministic; storage and audit receipts are bounded
- **security:** Fail closed on policy ambiguity, URL changes, iframe/navigation, and unavailable policy state. Keep only redaction metadata and hashes, never secretly retain excluded contents. Require explicit confirmation to remove a boundary.
- **missing:** A shared exclusion-policy format with URL/app/path/entity selectors and precedence rules; Enforcement hooks before browser inspection, Mac screenshots/reads, logs, pipeline context, and relay persistence; A dashboard to list active exclusions and prove they were applied; A pendant gesture or spoken command path for emergency exclusion while offline

### "Put the whole hive in observation-only mode for a period I choose: it may read and explain what it sees, but it must not send, edit, click, speak unsolicitedly, create reminders, or change device state; show me a receipt when every surface has entered and left that mode."
- **useful because:** Per-action approval is too slow when the owner wants a broad period of safety—for example while sharing a screen, testing a workflow, or lending the Mac. A single explicit mode prevents accidental side effects across surfaces while preserving useful read-only help.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic policy gate; no model needed for enforcement or convergence proof
- **latency:** Enter locally immediately and converge across online surfaces within 3 seconds; refuse new mutating work until the mode is cleared
- **cost:** Negligible model cost; heartbeat and convergence receipts are the main overhead
- **security:** Fail closed if any surface cannot attest to the mode. Do not silently queue writes for later. Expiry must be explicit and bounded, with a physical pendant clear gesture and an auditable enter/exit receipt.
- **missing:** A cross-surface side-effect deny policy enforced before Mac, browser, relay, and pendant mutations; An authenticated convergence check covering queued and in-flight work; Mode-aware scheduling so routines cannot bypass it; A clear distinction between read-only observation and data capture/persistence


## Changes it proposed to its own stack

### `memory` — Make extracted facts first-class, provenance-bound records with an owner-facing list and an atomic erase transaction. Each fact must point to its evidence capsule and derived copies; deletion must tombstone/remove the fact, graph projections, facts.json copies, and replicated relay records, while explicitly leaving action/job history intact and reporting off-machine deletion as requested-and-pending until confirmed.
- **owner gets:** The system currently can remember things the owner never asked it to remember, but cannot show the owner the list or reliably forget one item. This gives the owner real control over machine-extracted memory without destroying the audit trail of actions taken.
- effort: Medium-high: define IDs and provenance links, add list/detail/erase routes, implement local atomic deletion and relay tombstones, then test crash/retry convergence.  ·  risk: A partial erase could leave a derived copy or accidentally remove an action receipt. Use a deletion manifest, idempotency key, local transaction, relay acknowledgement, and a reconciliation view; never infer that pending replication is complete.
- cost: Low storage and API cost; background relay retries dominate. No routine audio or SD writes.  ·  latency: Local list/erase acknowledgement under 1 second; remote replica convergence is asynchronous and explicitly shown as pending.
- security: Improves privacy by making hidden memory discoverable and deletable; require owner authentication and do not expose raw evidence beyond the minimum needed to recognize the fact.
- depends on: A provenance schema shared by facts.json and the context graph; A relay tombstone/erase endpoint with durable acknowledgement; An owner-facing memory projection/list view

### `relay` — Replace the single bearer-token authority model for action execution with short-lived, capability-scoped authority epochs. Every queued job, browser command, approval grant, and Mac execution lease carries the epoch and an allowed-surface/effect set; a signed pendant revocation advances the epoch and causes all older work to fail closed before dispatch. Keep immutable receipts for accepted, cancelled, raced, and completed work.
- **owner gets:** A stolen or stale command should not remain capable of acting merely because the Mac or relay has not yet noticed a privacy event. The owner gets a real emergency stop for agency, not just a promise that a queue was cleared.
- effort: High: schema and middleware changes across relay, Mac bridge, browser bridge, approval handoff, and pendant event ingestion, plus race-condition tests around dispatch.  ·  risk: Incorrect epoch propagation could cancel legitimate work or create a false sense of safety. Roll out in shadow mode, reject missing epochs, retain a local emergency deny-all flag, and expose a receipt for every cancellation decision.
- cost: Small metadata overhead per command and one extra signed event; no meaningful model cost.  ·  latency: Adds one local epoch check before dispatch; revocation convergence is bounded by each surface's poll/heartbeat interval.
- security: Major improvement: least authority, replay resistance, and fail-closed revocation. Requires careful key custody and anti-replay counters.
- depends on: A signed pendant-to-relay control event; Durable relay/Mac/browser command leases; A separate execution authorization boundary from the general agent bearer token


## What it asked for

_Nothing._
## Its own summary

This round produced three new recorded proposals: (1) replay-safe continuation of interrupted Mac/browser work with leases and physical approval boundaries, (2) exact consequence-map previews bound to pendant approval, and (3) routine outcome verification rather than merely reporting that a timer fired. A memory erase capability was correctly rejected as an existing duplicate, and the delivery-proof proposal collided with an existing idea.

**Biggest unknown:** The remaining blocker is implementation ownership and live route verification for the newly recorded flows: whether /prepare and approval handoff are actually mounted end to end, whether routine records declare expected outcomes, and whether a durable relay lease/tombstone implementation exists. I do not need another tool grant this round; those are the concrete dependencies still needed.

