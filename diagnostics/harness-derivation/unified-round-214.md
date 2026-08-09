# Harness derivation — unified — round 214

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Stage this change, read me exactly what will happen, and only carry it out after I approve it on the pendant."
- **useful because:** This would turn the existing physical transaction approval latch into a real end-to-end safety boundary: the owner can safely ask the system to act in logged-in browser sessions or on the Mac without trusting a spoken 'I'll wait for approval' that currently dead-ends. The owner gets a digest, affected targets, expiry, and a deliberate button confirmation before execution, followed by a receipt.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for the spoken summary and disambiguation; deterministic planning, digesting, expiry, and receipt validation should run locally/relay-side.
- **latency:** Under 2 seconds to produce the staged summary; approval-to-execution under 3 seconds when Mac/browser are online. Pending approvals survive link loss and expire rather than guessing.
- **cost:** About $0.002-$0.01 per request for a short summary, dominated by one low-latency turn; deterministic approval and receipt work is negligible.
- **security:** Never send page secrets or form contents to the pendant. Bind approval to plan digest, world fingerprint, nonce, expiry, and owner session; reject plan/world changes and replay. Require explicit confirmation for off-machine, irreversible, or uncontained actions. Persist only the approval envelope and audit receipt. The current /approve path uses the same bearer credential as /execute, so privilege separation is still needed.
- **missing:** Relay implementation of APPROVAL_STORE_CONTRACT and delivery/readback state; A production path from staged approval to the physical_transaction_approval_latch event; Close the approval loop on the next owner conversation when unprompted pendant push is unavailable; A distinct approval/execution authorization boundary; Receipt correlation from pendant approval through Mac/browser execution

### "Continue the task I started before the Mac, browser, or relay went down — do not repeat anything that already succeeded, and ask me only where repeating could have a side effect."
- **useful because:** The system already records enough step-level evidence to distinguish completed, safely replayable, and unsafe work, but today it leaves the owner to find a ledger ID and manually POST returned actions. This capability would make interruption survivable across the actual hive: the relay remembers the job, the Mac/browser handoff reports what landed, and the next conversation resumes only idempotent/additive steps while surfacing unrepeatable ones.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Background/deterministic for ledger classification, handoff reconciliation, and replay; realtime only to explain the one or two steps needing a decision.
- **latency:** A status answer in under 1 second from relay records; safe resume begins within 5 seconds after the Mac/browser returns. No automatic replay while the owner is actively speaking.
- **cost:** Under $0.001 for deterministic recovery; at most $0.01 for a concise explanation when a model is needed.
- **security:** Gate replay on replaySafety (idempotent/additive), not merely reversibility. Require a live lease and fresh approval for irreversible/off-machine/uncontained or unrepeatable steps. Fix false interrupted records by closing ordinary ledgers, expire stale inflight steps, and add relay job lease_until/requeue. Never infer success from a missing receipt.
- **missing:** Production caller that invokes planResume and executes only its runnable decisions; Orchestrator closeLedger integration; Relay job lease_until and requeue sweep; A user-facing resume command and compact handoff view; Reconciliation of Mac/browser receipts with ledger step IDs

### "Move this conversation to my Mac and browser without losing context, then let me continue there while the pendant stays available for alerts."
- **useful because:** The pendant is excellent for capture and short replies, while the Mac/browser are the only places with a full screen, keyboard, and logged-in sessions. A signed handoff would let the owner start hands-free, continue a research or form task on-screen, and keep the same task identity and history instead of starting over or dictating sensitive page content through the pendant.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime for a brief handoff confirmation; deterministic context/session transfer and browser navigation; background model only to compress a long transcript into the handoff summary.
- **latency:** Under 3 seconds from spoken request to the target tab being opened and acknowledged. If the Mac/browser is offline, retain one expiring handoff and offer it on reconnect rather than duplicating a session.
- **cost:** Usually under $0.002, dominated by optional transcript compression; transport, token binding, and receipt checks are deterministic.
- **security:** Use a single-use, expiring handoff token bound to session, target app/tab, and conversation digest. Do not put page secrets or full transcript in URLs or pendant payloads. Require confirmation before navigating to a new origin or exposing private content. Revoke the token after browser acknowledgement and record which surface received it.
- **missing:** A cross-surface handoff token and acknowledgement protocol; A relay route that binds conversation/session context to a Mac/browser target; Browser extension support for adopting a handoff without leaking page contents; Mac/relay offline queue with deduplication; Owner-visible handoff and revoke controls

### "Treat these sites and apps as private: automate them on my behalf when I ask, but never send their page text, screenshots, form values, or audio-derived secrets to the model, relay, pendant, or logs."
- **useful because:** The owner can currently choose privacy mode for the device, but cannot express a durable, origin-specific boundary that still permits useful automation. This would let the Mac/browser click and submit within a sensitive session while the model receives only typed intents, opaque element handles, and success/failure receipts—not the contents being handled.
- **path:** browser-extension → mac-planner → relay-realtime → dashboard → pendant
- **model tier:** Deterministic policy enforcement and redaction at the browser/Mac boundary; realtime model only sees the owner's intent and sanitized action outcomes.
- **latency:** Policy checks and redaction under 20 ms per browser/Mac event; sensitive actions still require the existing deliberate approval path. A blocked data flow must fail closed, not wait for the model.
- **cost:** Negligible per-event compute; under $0.001 per task for policy evaluation, with no model tokens spent on quarantined content.
- **security:** The boundary must be enforced before screenshots, DOM text, clipboard data, accessibility values, browser results, and logs enter relay/model storage. Use origin/app/path policies, deny-by-default for unclassified sensitive surfaces, opaque handles with one-time use, and auditable receipts that contain no secret values. The owner must be able to test the policy and revoke it; policy edits affecting protected origins require explicit confirmation.
- **missing:** A policy store with origin/app scopes and fail-closed defaults; Browser and Mac adapters that redact before relay serialization and logging; Sanitized action/receipt schemas that prove completion without returning content; Dashboard policy editor and a local self-test that attempts a canary secret; Relay retention enforcement for any accidentally received sensitive payload


## Changes it proposed to its own stack

### `memory` — Make extracted-memory writes go through a surfaced-fact gate: before committing a new inferred fact, assign a stable fact ID, store a human-readable summary plus evidence capsule pointer, classify whether it can be shown back to the owner, and refuse persistence when it cannot. Maintain a local tombstone that propagates to relay/R2 replicas; never delete job history or action receipts as part of a fact erase.
- **owner gets:** The owner stops accumulating invisible conclusions about themselves. Anything retained can be recognized, traced, and removed later; anything too opaque to explain is not retained at all.
- effort: Medium-high: refactor fact extraction/persistence, add stable IDs/evidence links, and implement replicated tombstone handling and a review projection.  ·  risk: A classifier or projection bug could suppress useful memory or expose a sensitive summary. Recover with an append-only audit of rejected writes, explicit owner review, and a migration that marks legacy facts as unknown rather than silently presenting them as trustworthy.
- cost: Negligible storage and API cost; modest background work for indexing and tombstone retries.  ·  latency: Adds roughly 10-50 ms deterministic validation to extraction; no impact on live audio.
- security: Improves privacy by default, but evidence pointers must be access-controlled and tombstones must not reveal deleted content to relay logs.
- depends on: Stable fact/evidence schema; Owner-facing fact listing and deletion surface; Relay/R2 replicated erase protocol


## What it asked for

_Nothing._
## Its own summary

This round produced three new owner-facing directions plus one implementation change: (1) end-to-end physical approval for staged Mac/browser actions, (2) safe cross-surface crash recovery that replays only idempotent/additive steps, and (3) a signed pendant→Mac/browser conversation handoff; I also proposed a surfaced-fact memory gate that refuses opaque inferences and propagates erasure tombstones. The highest-value item is crash recovery: the system already has the decision engine and handoff records, but no production caller, so today an interrupted task simply strands the owner. The physical hardware is currently bench-connected but not LTE-registered; Mac permissions and browser bridge are live.

**Biggest unknown:** The remaining architectural unknown is not hardware: it is whether the live browser extension and relay have any undocumented session/handoff or approval-delivery hooks beyond the routes already observed. Before implementation, inventory those exact handlers and establish the relay-side persistence/lease contracts. I still need a production approval store and delivery path, ledger close/resume wiring plus relay job leases, a cross-surface handoff token protocol, and typed fact/evidence deletion routes.

