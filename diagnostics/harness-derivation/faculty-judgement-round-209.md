# Harness derivation — faculty-judgement — round 209

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What did I actually hear from today’s brief, and play only the parts I missed?”"
- **useful because:** The system currently treats generated/queued audio as if it reached the owner. This gives a trustworthy personal inbox based on authenticated downloaded, started, finished, and interrupted events: no duplicate morning brief, no claiming an item was heard when the pendant never played it, and exact continuation after a dropped link or button interruption.
- **path:** relay → pendant → mac → dashboard
- **model tier:** Cheap deterministic delivery reconciler first; use the realtime model only to produce the requested short spoken recap or a missing-item summary.
- **latency:** Under 300 ms for state and receipts; under 2 s for a spoken missing-item summary.
- **cost:** Near-zero for reconciliation; roughly $0.001–$0.01 only when summarization is needed. Storage and receipt queries dominate, not model calls.
- **security:** Expose opaque artifact/item IDs and redacted titles by default. Never infer hearing from download alone. A playback_finished event must be authenticated and deduplicated; spoken content still passes the existing delivery redaction gate.
- **missing:** A durable item-to-artifact and item-to-briefing mapping (the new delivery-event primitive currently accepts only artifact IDs); A query that folds record_pendant_delivery_event events into per-item heard/unheard state; A relay-to-pendant command for replaying only unplayed items without creating duplicates; A user-facing dashboard and concise spoken formatter

### "“I pressed stop. Prove that everything you could have done for me is stopped, and tell me if anything still needs my attention.”"
- **useful because:** A physical stop is only useful if the owner can trust its scope. Today the latch can emit a stop token, but there is no owner-facing, cross-surface reconciliation of relay jobs, Mac actions, browser leases, queued audio, and irreversible steps. This capability turns an emergency gesture into a comprehensible safety result rather than a silent best effort.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic cancellation fan-out and receipt reconciliation; realtime model only turns the final structured result into one short sentence.
- **latency:** Pendant acknowledgement locally is immediate; cross-surface cancellation verdict within 2 seconds, with a later retry report if a surface is offline.
- **cost:** Negligible for cancellation and joins; under $0.002 for optional natural-language formatting.
- **security:** The stop token must be scoped to owner-owned work, monotonic, authenticated, and replay-safe. Never report “stopped” when a destructive action has already committed; distinguish cancelled, committed, unknown, and not-reached. Do not send action payloads to the pendant.
- **missing:** A stop-token consumer on every relay job and Mac/browser lease, with durable cancellation receipts; A canonical operation/attempt join across relay, Mac, browser, and pipeline IDs; A fail-closed status fold that treats an unreachable surface as unknown rather than cancelled; A pendant-safe compact result envelope and dashboard drill-down

### "“Give me the answer only if it is fresh and independently corroborated; otherwise tell me exactly what is missing.”"
- **useful because:** The owner repeatedly asks for current headlines and page facts, but a failed browser action or stale source can currently collapse into a confident answer or an unhelpful failure. A source-quorum mode would make judgement honest: freshness windows, independent-origin checks, contradiction handling, and a short spoken answer that says ‘not enough evidence’ instead of filling gaps.
- **path:** relay → browser → mac → pendant → dashboard
- **model tier:** Cheap deterministic freshness/origin/contradiction evaluator; use the expensive realtime model only after the quorum passes, for compression into the owner's one-sentence spoken reply.
- **latency:** 3–8 seconds for two or three public reads; under 500 ms when cached evidence is still within its declared freshness window.
- **cost:** Usually $0.002–$0.02 per request depending on model compression; browser reads and network latency dominate.
- **security:** Apply existing redaction and origin policy before evidence reaches a model or spoken audio. Treat same-site mirrors as one source, never expose private authenticated pages as public corroboration, and retain only hashes/citations by default. A failed read must be visible in the result, not silently omitted.
- **missing:** A typed freshness-and-independence evaluator with source-specific windows; A contradiction result that preserves both citations rather than selecting one by model confidence; A request mode that requires quorum and fails closed when browser connectivity or evidence is insufficient; A spoken formatter that says what was checked and what remains unknown

### "“For anything you tell me aloud, let me ask ‘how do you know?’ and get the exact source, timestamp, confidence, and what would change your mind.”"
- **useful because:** The owner can currently get provenance for some actions and evidence capsules, but spoken briefings are detached from claim-level evidence. This would make the pendant a trustworthy thinking partner rather than an uninspectable narrator: every sentence has a durable, redacted claim reference, and uncertainty is visible when the owner challenges it.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** A cheap deterministic claim linker and evidence reducer; use the realtime model only to explain conflicting evidence in the owner's requested level of detail.
- **latency:** No added latency for normal speech beyond attaching claim IDs; an explanation should begin within 1 second and complete within 3 seconds.
- **cost:** Near-zero for claim references and source lookup; roughly $0.001–$0.01 only for conflict explanation or compression.
- **security:** Claim references must be opaque and scoped to the owner. Spoken explanations must apply the existing redaction policy and never reveal withheld snippets by default. Preserve source revocations: a revoked source must make the claim say unavailable, not silently substitute a new justification.
- **missing:** A claim-level envelope in generated text and audio-item metadata; A durable join from spoken sentence to evidence capsule, memory fact, action receipt, or tool result; A reducer that reports source age, confidence, conflicts, and revocations without leaking raw private content; Pendant utterance handling for ‘how do you know?’ that binds to the currently playing claim

### "“When I correct you, remember the correction, show me where you applied it, and never silently fall back to the old assumption.”"
- **useful because:** The current memory system stores preferences and observations, but it does not treat an owner correction as a durable override with scope, expiry, or conflict handling. The owner should not have to correct timezone, identity, routine, or task interpretation repeatedly—and should be able to see when an old assumption is still influencing a decision.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Cheap deterministic contradiction/override evaluator; use the realtime model only to interpret an ambiguous correction or summarize competing assumptions.
- **latency:** Under 500 ms to record and acknowledge a correction; under 1 s to apply it to the next judgement.
- **cost:** Near-zero for typed memory events and projection; occasional $0.001–$0.01 interpretation call.
- **security:** Corrections may contain sensitive personal information. Store the minimum normalized assertion, preserve the owner's wording only in an explicitly requested note, scope it to affected surfaces, and provide one-step revocation with provenance.
- **missing:** A first-class correction/override event with scope, confidence, supersedes, and expiry; Writers from pendant, Mac, and browser into the existing fleet-memory and local-memory paths; A conflict resolver that refuses to choose silently when two owner assertions overlap; Prompt and policy projections that carry the active correction and its source reference


## Changes it proposed to its own stack

### `integration` — Make reconciliation requests dispatch by their declared domain and return a provenance-backed structured result, rather than falling through to the generic intent resolver. Unsupported domains must be reported as unsupported; read-only reconciliation must never resolve to POST /briefing or claim it inspected anything.
- **owner gets:** When the owner asks whether briefings are duplicated, permissions conflict, or audio was heard, they get a real answer about that question instead of a low-confidence generic briefing route. This is the difference between a trustworthy judgement layer and a confident wrong turn.
- effort: Small-to-medium: explicit domain dispatcher, per-domain read adapters, schema tests, and a fail-closed resolver branch.  ·  risk: Existing callers may depend on generic intent resolution; preserve a versioned compatibility path and return an explicit unsupported result rather than silently changing behavior.
- cost: Negligible API cost; a few read calls per reconciliation.  ·  latency: Adds one routing step; roughly tens of milliseconds before the underlying reads.
- security: Improves safety by preventing an unintended side-effecting POST resolution; preserve source scoping and redaction.
- depends on: reconcile_personal_state; cross_surface_preflight; GET /briefing/triage/runs; GET /briefing/policy; GET /browser/status; GET /pipeline

### `memory` — Add a correction ledger that is separate from ordinary facts: each owner correction records the superseded assertion, scope (surface/task/domain), effective time, expiry or permanence, confidence, and a provenance link. Every projection must emit an ‘active override’ or an explicit conflict instead of silently flattening competing facts.
- **owner gets:** After saying “that is wrong,” the owner gets lasting behavioral change and can verify exactly which old belief was displaced. This prevents repeated mistakes without turning every casual utterance into permanent memory.
- effort: Medium: extend the existing fact/event schemas, add writers at voice and Mac/browser capture points, implement conflict-aware projection, and add a correction history view.  ·  risk: A mistaken correction could suppress useful context. Require a short spoken acknowledgement for broad or permanent overrides, keep narrow defaults for ambiguous corrections, and make revocation immediate.
- cost: Minimal storage and model cost; deterministic projection dominates.  ·  latency: A few milliseconds for lookup; no added speech-generation round trip.
- security: Corrections inherit sensitivity classification and source revocation. Do not copy raw correction audio into prompts unless explicitly requested.
- depends on: POST /memory/facts; GET /memory/projection; POST /context-graph/entities; POST /context-graph/relations; explain_action_provenance


## What it asked for

_Nothing._
