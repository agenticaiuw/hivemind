# Harness derivation — faculty-action — round 197

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Carry out this whole request across my Mac and browser, but stop and ask me if any target, page, or value changes before committing.”"
- **useful because:** This is the missing end-to-end action primitive: one intent can span browser and Mac steps while refusing to continue when fresh perception no longer matches the approved plan. It turns the agent from a sequence of blind clicks into a bounded transaction, with a clear pause point instead of silently acting on drift.
- **path:** faculty-judgement → relay-realtime → faculty-perception → browser-extension → mac-planner → mac-vision → mac-terminal → faculty-action → unified
- **model tier:** Use the realtime model only to collect and clarify the request; use a cheaper background planner for the dependency graph and a local deterministic executor for each action; invoke realtime again only for an ambiguity or owner-facing interruption.
- **latency:** Initial preview in 2–5 s; each step under 1 s when state is stable; pause immediately on drift. Long workflows run as a relay job and notify through the pendant rather than holding a voice turn open.
- **cost:** Usually one planning call plus cheap per-step checks; roughly $0.01–$0.08 depending on workflow length. Browser screenshots and repeated context dominate cost, so pass hashes and structured state between steps.
- **security:** Never carry secrets from browser pages into the pendant or model context. Require the existing physical approval latch for risky commits, expire the plan quickly, stop on target/value drift, and verify postconditions independently after every externally visible step. Owner must explicitly define which action classes may auto-continue.
- **missing:** A first-class dependency-graph/saga record that stores step preconditions, approved target identities, expiry, and pause reasons; A policy-controlled resume endpoint that cannot skip a failed or unverified predecessor; A compact pendant representation for “paused because state changed” distinct from success or cancellation

### "“Before you send, delete, purchase, or edit anything, show me which exact person, account, tab, file, or record you bound the action to—and refuse if that identity changes.”"
- **useful because:** The most dangerous execution failures are semantically correct actions applied to the wrong target. This capability binds a human target to an immutable, fresh identity across the browser session and Mac filesystem/app, then makes faculty-action refuse execution when the identity or relevant value drifts. It protects against a tab switching, a duplicate contact, a renamed file, or a stale account session.
- **path:** faculty-judgement → faculty-perception → browser-extension → mac-vision → mac-terminal → mac-planner → faculty-action → relay-realtime
- **model tier:** Use a cheap deterministic identity binder for URLs, browser session IDs, file IDs/hashes, account labels, and app bundle IDs; reserve the realtime model for explaining a collision or asking the owner to choose between two identities.
- **latency:** Bind in under 500 ms from fresh state; re-check immediately before mutation and after navigation. If identity is ambiguous, pause rather than spend model time guessing.
- **cost:** Negligible for structured browser/Mac state and hashes; $0.00–$0.02 for rare ambiguity explanations. Screenshot/OCR fallback is the dominant cost and should be opt-in.
- **security:** Do not expose message bodies, form secrets, or private page contents in receipts; store only scoped identity claims and salted hashes. A target mismatch must fail closed. The owner must confirm whether a human-readable label alone is ever sufficient; default is no.
- **missing:** Stable cross-surface identity claims for browser account/session, contact, file, and app record types; A pre-mutation target-lock check in faculty-action that is mandatory for destructive, external-send, and financial actions; A redacted collision explanation that can be rendered through the pendant without leaking private content

### "“If my pendant disappears or the link goes stale while an action is waiting to commit, cancel it—never resume that action later without showing me a new summary and getting a new approval.”"
- **useful because:** A pending action must not become an unattended action merely because the wearer walked away, the pendant lost LTE, or a browser session went stale. This gives the physical device a real safety boundary: connection loss cancels the lease, while ordinary completed work remains truthful and auditable.
- **path:** pendant → relay-realtime → faculty-action → faculty-perception → faculty-judgement → mac-planner → browser-extension → unified
- **model tier:** No expensive model is needed for the watchdog: relay-side deterministic lease and freshness logic handles expiry/cancellation. Use a cheaper planner to reconstruct a new summary only if the owner later asks to retry; realtime is reserved for explaining why the action was cancelled.
- **latency:** Heartbeat/lease expiry within 2–5 s of the configured deadline; cancellation should reach the executor before its next mutating step. Re-prompting on retry can take 2–5 s.
- **cost:** Near-zero model cost; a few D1 writes and one cancellation receipt per lease. Network retries and durable job state dominate, not inference.
- **security:** Fail closed on missing or stale heartbeats, replayed approvals, clock ambiguity, and unknown executor state. Cancellation must be idempotent and distinguish “cancelled before mutation” from “unknown after mutation began.” Never treat an offline queued approval as permission to resume an expired lease. The owner must choose the maximum tolerated stale interval; conservative default is required.
- **missing:** A relay-issued short-lived action lease tied to the pendant session and approval nonce; Executor support for idempotent cancellation at step boundaries, with an explicit unknown state if mutation cannot be stopped; Freshness semantics that cover both LTE pendant contact and browser/Mac executor contact without conflating them

### "“Let me give you a standing, bounded delegation—such as ‘reschedule my own meetings within business hours’—and enforce those limits across every app; ask me only when a request falls outside the delegation.”"
- **useful because:** Today the owner must either approve every low-risk repetition or grant an unsafe blanket instruction. A typed delegation would make the system genuinely useful for recurring life administration while preserving a hard boundary: exact actor, allowed operation, target scope, time window, monetary limit, and maximum frequency are enforced before faculty-action can mutate anything.
- **path:** faculty-judgement → relay-realtime → faculty-perception → faculty-action → mac-planner → mac-terminal → browser-extension → unified → pendant
- **model tier:** Use a cheaper background model to compile the owner's natural-language delegation into a typed policy and to classify incoming requests; use realtime only while the owner creates or changes the delegation. Enforcement itself must be deterministic and local to the action path.
- **latency:** Policy lookup and constraint checks under 100 ms; a new delegation may take 3–8 s because the owner must review its plain-language summary and approve it physically. Out-of-policy requests should pause immediately.
- **cost:** Near-zero per execution after policy compilation; occasional model cost for policy creation or ambiguous classification. The dominant cost is human confirmation, not inference.
- **security:** Default deny, short expiry, explicit revocation from the pendant, and no delegation may authorize secrets, authentication-factor use, irreversible deletion, or a broader target than the owner reviewed. Store only the policy and hashed scope identifiers, never page contents. Every use must expose which rule authorized it and fail closed on stale perception or policy-version mismatch.
- **missing:** A versioned, typed delegation policy schema with operation, target scope, time window, limits, expiry, and revocation fields; A deterministic policy gate inside faculty-action that runs immediately before every mutation and emits an allow/deny reason; A compact pendant flow for reviewing, approving, revoking, and receiving over-limit notifications for policies without showing private content


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct, owner-visible action capabilities: drift-stopping cross-surface transactions, immutable target binding before mutations, and a pendant/session dead-man lease that cancels pending work on stale links. I used the existing plan/prepare/approve/execute, browser/Mac action, job, session, receipt, verifier, and physical-outcome surfaces rather than proposing another generic approval or receipt mechanism. I also asked faculty-judgement to check for overlap.

**Biggest unknown:** The live inventory still does not establish whether /prepare, /approve, job_completion_watch, stable browser/account/file identity claims, or executor step-boundary cancellation already exist in full. I need a complete route/action description for those seams before implementation can be honest; the owner must also choose the conservative stale-lease interval and which action classes may auto-continue.

