# Harness derivation — unified — round 227

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live system reachability** — The Mac local agent is healthy at version 0.5.0 on MacBook-Air-6.local, America/New_York; live manifest reports 223 routes (more than the established 116-route snapshot). Safari has 2 online tabs and home-macbook-bridge is online. The pendant/mobile device is not shown as LTE-registered.
  - evidence: GET /health returned HTTP 200; GET /machine-context returned darwin/arm64 and timezone America/New_York; GET /capabilities returned generatedAt 2026-08-09T00:29:07.578Z, routeCount 223; discover devices showed Safari online, home-macbook-bridge online, cloudflare-contract-test offline.

## Capabilities it proposed

### "“What do you currently believe about me, and forget this one fact everywhere.”"
- **useful because:** The system extracts facts the owner never explicitly asked it to remember, but today those facts are not owner-visible or individually erasable. This gives the wearer a trustworthy inspection-and-erasure command: show the exact fact, its source evidence, every derived copy, and complete or honestly report pending off-machine deletion without touching the action audit trail.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** background for indexing and deletion planning; realtime only to disambiguate which displayed fact the owner means
- **latency:** List in under 2 seconds from the pendant; deletion confirmation in under 5 seconds locally, with replicated relay deletion reported as requested-and-pending
- **cost:** Low: one short background model call for fact labels/ambiguity; storage and hashing dominate, not inference
- **security:** Never expose unrelated evidence or raw audio; require an explicit fact identifier or spoken confirmation before deletion; preserve action/job history while deleting the fact, derived copies, and evidence capsule; relay/R2 deletion must be tombstoned and retried
- **missing:** A single owner-facing memory inventory route joining facts.json, context graph nodes, derived projections, and evidence capsules; An authenticated erase transaction that propagates to relay D1/R2 and returns pending replication receipts; A pendant spoken list/selection UX for multiple similarly worded facts

### "“The browser task I started yesterday is still unfinished—find the exact tab and continue only if it is the same page and nothing important changed.”"
- **useful because:** A browser job can outlive a tab, extension reconnect, or Mac restart. Instead of blindly replaying clicks or abandoning the task, the system would locate the bound session, compare page identity and captured evidence, summarize changes, and either continue at the next safe step or hand the owner a precise stop reason.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard → pendant
- **model tier:** background for evidence comparison and task selection; realtime only for the owner’s final ambiguity or confirmation
- **latency:** Locate and fingerprint in 3 seconds; no mutation until the owner hears the changed-page summary and confirms when the page is not identical
- **cost:** Low-to-moderate: browser snapshots and hashing dominate; one small planner call only when several candidate tabs match
- **security:** Bind every continuation to the original job, tab/session identity, URL origin, and evidence capsule; never transfer cookies or page contents to the relay; refuse if login state, origin, totals, recipients, or form fields changed; browser mutation requires the existing approval/physical latch path
- **missing:** A first-class browser continuation record that stores the next step and page identity separately from the expired command lease; A read-only tab fingerprint comparison with field-level changed summaries; A user-facing resume/abort decision that is actually wired to execution rather than merely speaking 'waiting for approval'

### "“What can you safely do for me right now, on this Mac, in my browser, and through the pendant?”"
- **useful because:** The owner should not have to remember which body is online, which tab is logged in, or which action requires physical approval. A live reachability-and-authority answer turns opaque failures into a useful menu: available now, observable but not mutable, staged pending approval, or unavailable with the exact recovery the owner can perform.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic inventory and policy classification first; background model only to phrase a short owner-facing menu
- **latency:** Under 2 seconds for the inventory and under 4 seconds for a spoken summary; refresh only the affected surface after a failed action
- **cost:** Very low: health/capability reads and cached session metadata; model tokens are limited to summarization
- **security:** Do not enumerate secrets, cookie values, or page contents; report capability classes and permission state, not credentials; distinguish reachable from authorized and authorized from safe-to-execute; never imply that a blocked action is queued if no runnable approval path exists
- **missing:** A typed cross-surface authority matrix with freshness timestamps and risk tiers; A capability-to-recovery explanation that maps missing Accessibility/Screen Recording or browser leases to owner actions without pretending to repair them; A pendant-sized spoken menu and dashboard detail view sharing the same signed snapshot

### "“What information about me left the pendant or Mac in the last day, where did it go, and what is still waiting to be deleted?”"
- **useful because:** The owner has a privacy latch and deletion rules, but no way to audit the actual boundary crossings: audio chunks, transcripts, browser evidence, inferred facts, and action parameters can travel through different surfaces. A spoken, time-bounded outbound-data ledger would make the system accountable in the way a privacy setting alone cannot. It would show destination, category, purpose, retention state, delivery receipt, and any replication or deletion still pending—without exposing the content itself.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic receipt aggregation and redaction; use the realtime model only to answer a natural-language follow-up such as “only audio” or “just browser data.”
- **latency:** A 24-hour summary in under 3 seconds from indexed receipts; drill-down to one transfer in under 2 seconds.
- **cost:** Low: mostly compact receipt reads and local aggregation; no model call for the default report.
- **security:** The report must not become a second leak: show hashes, categories, destinations, timestamps, and retention state, never raw transcripts, page contents, tokens, or audio. Bind each row to authenticated delivery receipts and distinguish attempted, accepted, physically played, and deletion-requested. A missing receipt must be reported as unknown, never success.
- **missing:** A tamper-evident cross-surface outbound-data ledger covering pendant, relay, Mac, and browser transfers; A common taxonomy for content class, destination, purpose, retention deadline, and deletion state; A relay endpoint that can return deletion-pending and replication status without returning sensitive payloads; A pendant-sized spoken summary mode with a dashboard drill-down

### "“Keep my voice and page contents local, but still let you send calendar times and task status; tell me whenever a request crosses that boundary.”"
- **useful because:** Today privacy is mostly an emergency latch and after-the-fact deletion. The owner cannot express a durable, per-data-class boundary that still permits useful automation. This would let the system remain helpful while refusing or redacting sensitive classes before they leave the originating surface, with an audible explanation rather than a silent failure.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic policy enforcement and redaction; background model only for classifying ambiguous fields, which must default to deny.
- **latency:** Policy decision within 100 ms for each outbound event; ambiguous classification may defer the action rather than blocking conversation indefinitely.
- **cost:** Low recurring cost for policy checks; occasional background classification for unknown fields, dominated by local parsing rather than generation.
- **security:** Default-deny for unknown content; enforce the policy at the source and again at the relay; never rely on the model to honor a prompt-only rule. The owner must be able to inspect and revoke policies, and every allow/deny/redaction must enter the outbound-data ledger.
- **missing:** A versioned owner-editable data-class policy with allow, redact, local-only, and deny outcomes; Source-side field classification for microphone audio, transcript, browser page content, calendar metadata, and task status; Relay enforcement that rejects disallowed payloads even if a Mac or browser client is compromised; A clear spoken explanation and dashboard simulator showing what each policy would permit

### "“Answer this only from information that is still fresh, and tell me exactly what became stale before you act.”"
- **useful because:** The system can already read browser pages, Mac state, relay receipts, and evidence capsules, but it does not give the owner a single freshness contract. This capability would prevent a confident action based on yesterday’s tab, an expired evidence capsule, an old calendar projection, or a stale device state. It would speak the uncertainty boundary first and refuse mutation when the required evidence is outside its freshness budget.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic freshness checks, timestamps, TTLs, and dependency closure; use a cheaper background model only to summarize conflicts after the safety verdict is fixed.
- **latency:** Freshness evaluation under 500 ms for cached evidence and under 3 seconds when a live browser or Mac read is required; stale required evidence means immediate refusal, not a timeout disguised as success.
- **cost:** Low: timestamp and provenance evaluation dominates; model use is optional summarization only.
- **security:** Never silently substitute the Mac timezone or current state for an untrusted timestamp. A freshness claim must name its source, capture time, TTL, and clock basis. If clocks disagree or provenance is missing, classify as unknown and block mutation.
- **missing:** A cross-surface freshness contract with per-data-class TTLs and dependency propagation; A clock/provenance verifier that distinguishes Mac-local time, relay time, browser capture time, and zoneless pendant digits; An execution guard that revalidates freshness immediately before mutation and records the verdict; Owner-configurable strict versus best-effort freshness modes


## Changes it proposed to its own stack

### `dashboard-ux` — Add a first-class “Beliefs & evidence” panel backed by the existing memory projection, context graph, and evidence-capsule records. Each extracted fact gets a stable human-readable label, confidence/source timestamp, an expandable evidence capsule, a list of derived copies, and separate Forget/Keep controls. Forget creates a durable erase transaction and shows local completion versus relay/R2 requested-and-pending; it must not delete job history.
- **owner gets:** The owner can finally see what the system inferred about them and remove one mistaken or unwanted belief without wiping useful action accountability.
- effort: Medium: UI plus a server-side erase transaction and projection invalidation; reuse existing evidence revocation and memory routes rather than inventing another store.  ·  risk: A partial erase could leave a derived copy or falsely claim completion. Use a tombstoned erase manifest, idempotent retries, and a visible pending state; if evidence cannot be located, refuse instead of silently deleting only one copy.
- cost: Low API cost; mostly local reads, hashing, and replication bookkeeping.  ·  latency: Initial list under 2 seconds from cached projection; individual local erase under 5 seconds, remote completion may remain pending.
- security: High privacy benefit, but the panel itself must redact unrelated evidence and require explicit confirmation for deletion. Preserve action/audit history as mandated.
- depends on: A typed inventory joining GET /memory/projection, context-graph routes, and GET /evidence; An authenticated idempotent erase route with relay/R2 pending receipts; Existing evidence revocation and audio-retention deletion semantics


## What it asked for

_Nothing._
