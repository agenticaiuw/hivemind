# Harness derivation — unified — round 193

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **memory provenance conflict** — Live GET /memory/facts contains preference.timezone=America/Chicago with source.origin=machine, while authoritative owner policy says Mac-local routines use America/New_York and owner timezone is unresolved. This must be treated as a conflict, not silently selected.
  - evidence: describe GET /memory/facts returned fct_5a7e59f3... value America/Chicago, origin machine, confidence 0.99; established owner timezone policy.

## Capabilities it proposed

### "When I say “buy this” or “send this,” stage the exact browser action, show me the target and total, wait for my physical pendant approval, execute only that approved action, and tell me the final receipt."
- **useful because:** It turns the pendant’s deliberate approval latch into a real safety boundary for consequential browser work. The browser has private sessions, the Mac can act, and the relay can persist the staged transaction; none alone can provide both exact-target consent and a durable outcome receipt.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** background for staging and receipt reconciliation; realtime only to explain the pending action and collect the spoken request
- **latency:** Stage preview under 2 s; physical approval acknowledgement under 1 s when linked; final receipt within 5 s of browser completion, with resumable reconciliation after outages.
- **cost:** About $0.01–$0.05 per transaction depending on whether a planner is needed; browser execution and D1 persistence dominate latency, not model tokens.
- **security:** Never send page secrets or payment credentials to the pendant or model. Bind the approval nonce to the exact tab/session, action digest, amount/recipient, expiry, and browser result. Require confirmation again if the world or target changes; redact receipts by default.
- **missing:** relay implementation of the approval handoff contract and delivery/readback path; browser action executor that accepts the pendant nonce and returns a signed, target-bound receipt; a clear policy for which action classes may be staged versus always refused

### "Let me ask “what do you remember about me?” and then say “forget that,” with the system showing the exact source and confirming when every derived copy is erased."
- **useful because:** The system currently extracts facts the owner did not explicitly create, while the owner cannot see or individually remove them. This gives the owner a human-recognisable inventory and a trustworthy erase operation instead of silently retaining personal context.
- **path:** relay → mac-planner → browser-extension → pendant
- **model tier:** background for indexing and deletion reconciliation; realtime only for the owner’s spoken lookup and confirmation
- **latency:** Answer a narrow lookup in under 3 s; deletion acknowledgement immediately as requested-and-pending, with off-machine completion reported later rather than falsely claiming instant erasure.
- **cost:** Usually under $0.01 per lookup/erase; storage scans and replicated deletion receipts dominate.
- **security:** Default to redacted evidence and require explicit confirmation for deletion. Erase the extracted fact, context-graph derivatives, evidence capsule, and replicated relay copies, but retain action/job audit history. Use an idempotent erase token and expose partial-failure state.
- **missing:** a provenance index linking each extracted fact to its derived copies and evidence capsule; an owner-facing list route with recognisable summaries and per-item erase controls; a replicated deletion worker and receipt that distinguishes requested, completed, and failed

### "Run my recurring browser tasks only when the right account/session is still present; if the session is expired or the page changed, pause safely and tell me exactly what needs attention instead of retrying blindly."
- **useful because:** Recurring Mac routines can reach private browser sessions, but a saved task can become dangerous when a tab logs out, a recipient changes, or a page layout shifts. This makes unattended routines useful without turning stale browser state into an accidental purchase, message, or deletion.
- **path:** relay → mac-planner → browser-extension → pendant
- **model tier:** background/deterministic for schedule and session checks; planner tier only to explain a blocked change; realtime only when the owner asks for status
- **latency:** Routine start within the existing scheduler interval; session/world validation under 2 s; blocked notice queued for the next natural conversation rather than interrupting speech.
- **cost:** Usually <$0.01 per run because checks and policy are deterministic; planner tokens are only spent on changed-page explanations.
- **security:** Bind each routine to an account/session fingerprint, URL pattern, target identity, and allowed action digest. Never infer a new recipient or approve a changed world. Store redacted failure evidence, expire stale bindings, and require the pendant’s physical approval latch for irreversible steps.
- **missing:** a routine-to-browser binding schema with session/account fingerprints and allowed world changes; a dry-run preflight that compares the current tab/page against the routine’s stored digest; a scheduler-to-pendant blocked-notice path with deduplicated receipts

### "If your memories disagree, tell me which sources conflict and stop using the disputed fact until I resolve it."
- **useful because:** The live memory store currently contains a machine-origin timezone fact of America/Chicago while the owner’s explicit policy says routines use the Mac’s America/New_York zone. Silent precedence can make routines fire at the wrong time. A conflict quarantine makes uncertainty visible and prevents one stale extraction from steering actions.
- **path:** relay → mac-planner → pendant → browser-extension
- **model tier:** deterministic for conflict detection, precedence, and quarantine; background model only to produce a short human-readable explanation
- **latency:** Detect on fact write/use; no more than 1 s added to a routine decision. Queue the explanation for the next conversation, never interrupt active speech.
- **cost:** Near-zero for hashing/field comparison; <$0.01 only when a natural-language explanation is needed.
- **security:** Show provenance, timestamps, origin, and confidence without exposing unrelated private evidence. Do not let a low-confidence or machine-derived fact override an explicit owner decision. Keep an append-only resolution record and allow the owner to retract it.
- **missing:** conflict detection across facts, context-graph entities, and runtime policy values; a quarantine state that makes affected routines/actions refuse or require explicit resolution; an owner-facing resolve/keep/delete operation with provenance-preserving receipts

### "Before you send anything off my Mac, show me exactly which pieces of my screen, files, browser state, or voice would leave the device, and let me approve a reusable redaction rule such as “never send names or order numbers.”"
- **useful because:** The system can act across a private browser, Mac, relay, and pendant, but the owner currently cannot see the boundary of data leaving the Mac for a specific action. A field-level egress preview makes privacy concrete without requiring the owner to understand model context or browser internals.
- **path:** mac-planner → browser-extension → relay → pendant
- **model tier:** deterministic classification and redaction first; background model only for ambiguous fields; realtime only to explain a pending preview
- **latency:** Preview in under 2 seconds for ordinary pages/files; blocked ambiguous fields remain pending rather than delaying unrelated work.
- **cost:** Usually <$0.02 per preview; deterministic scanning dominates, with model cost only for ambiguous text classification.
- **security:** The preview itself must not leak the sensitive data it describes. Keep raw values local, send only labels/hashes to the relay, require physical approval for new or broadened egress, and make rules revocable and scoped by app/site/action.
- **missing:** a structured egress manifest emitted by Mac and browser actions; local field-level redaction before relay/model transmission; a durable owner policy store with scope, expiry, and approval receipts

### "Let me ask “what would happen if you ran that now?” and receive a concrete dry run showing the current browser page, files, messages, and side effects, without changing anything."
- **useful because:** Today a plan preview is not a trustworthy cross-surface simulation: a browser page, Mac filesystem, relay state, and pendant delivery can all change between planning and execution. A no-mutation rehearsal lets the owner inspect the actual current world before authorizing a consequential action.
- **path:** browser-extension → mac-planner → relay → pendant
- **model tier:** deterministic probes and action classifiers; planner tier only to summarize differences and likely side effects
- **latency:** Under 5 seconds for one browser tab and local workspace; longer scans return progressive evidence without executing.
- **cost:** <$0.02 for a typical dry run; filesystem/browser probes dominate, not model generation.
- **security:** Every probe must be read-only and bound to explicit tabs/paths. Do not execute JavaScript with side effects, send form data, open external links, or transmit page contents unnecessarily. Show uncertainty where a side effect cannot be proven.
- **missing:** a cross-surface read-only simulation contract with explicit probe permissions; browser and Mac adapters that report predicted side effects and current-world fingerprints; a plan-to-dry-run digest so the later execution cannot silently diverge


## Changes it proposed to its own stack

### `relay` — Add expiring claim leases and a requeue sweep to relay_jobs, then have the Mac agent close ordinary action ledgers and invoke the existing replay-safety resume planner only for idempotent/additive steps. Surface one owner-facing pending-job summary on the next conversation instead of silently leaving jobs processing for 24 hours.
- **owner gets:** A Mac sleep, browser disconnect, or relay restart would no longer strand an action or make a completed plan look interrupted forever. Safe work can continue once; unrepeatable or unknown work remains blocked and is clearly explained, so the owner gets recovery rather than duplicate sends or silent loss.
- effort: Medium: schema migration for lease_until/claimedBy, periodic sweep, closeLedger calls in orchestrator, and a guarded startup/next-conversation resume trigger using existing planResume decisions.  ·  risk: A bad lease could duplicate an unrepeatable external action. Mitigate with replaySafety gating, idempotency keys, receipt adoption, lease expiry longer than the executor heartbeat, and mandatory blocking on unknown/inflight states. Recover by cancelling the lease and presenting the staged job for explicit approval.
- cost: Negligible storage and one periodic D1 query; no meaningful model cost unless a blocked summary needs generation.  ·  latency: Recovery after a crash becomes bounded by the lease interval (target 1–5 minutes) instead of the current 24-hour TTL; normal jobs are unchanged.
- security: No new authority; leases prevent stale workers from acting, while approval remains bound to the exact plan and world. Audit every requeue and resume decision.
- depends on: orchestrator must call closeLedger for completed plans; relay_jobs lease_until migration and requeue sweep; existing actionLedgerVerify replaySafety and planResume wired to a real trigger

### `context` — Create a causal action capsule for every owner-visible result: a compact, signed chain linking the owner utterance, selected model decision, exact data sources, policy checks, physical approvals, mutations, and observed receipts. Expose the capsule as a human-readable “why did you do that?” answer without exposing hidden prompts or unrelated private content.
- **owner gets:** When the system acts through several bodies, a final receipt says what happened but not why. The owner should be able to audit a surprising reminder, browser action, or pendant response in one place and distinguish an explicit instruction from an inferred memory or stale routine.
- effort: High: define a redacted causal schema, emit events from relay/Mac/browser/pendant, sign and correlate them by action ID, and build a spoken plus dashboard renderer.  ·  risk: Over-logging could create a new sensitive archive or falsely imply causality when evidence is missing. Keep capsules bounded, redact values, mark inference versus observation, expire content on policy, and report gaps rather than inventing explanations.
- cost: Small storage and hashing overhead per action; <$0.01 for rendering a normal explanation, with larger cost only for complex summaries.  ·  latency: Negligible on execution if event emission is asynchronous; explanation retrieval under 2 seconds from local/relay indexes.
- security: Improves accountability but increases metadata sensitivity. Encrypt relay capsules, separate owner-facing evidence from model internals, and require explicit consent before including private page/file excerpts.
- depends on: stable cross-surface action IDs and receipts; provenance links from memory facts and policies to decisions; redacted event schemas on relay, Mac, browser, and pendant


## What it asked for

_Nothing._
