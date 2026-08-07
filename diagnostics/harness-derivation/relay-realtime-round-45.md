# Harness derivation — relay-realtime — round 45

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “I’m heading out,” save me a resumable snapshot of what I was doing on the Mac and in my authenticated browser; when I later ask “what did I leave?”, tell me what changed and offer to resume the exact next step."
- **useful because:** The owner is usually away from the Mac. Today work is stranded across open apps and authenticated tabs: leaving loses intent, and returning requires reconstructing it manually. A wearable-triggered checkpoint would preserve continuity without interrupting or requiring the owner to remember notes.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use realtime only to recognize the short trigger and answer the later question. A cheaper background model should normalize the Mac/browser snapshot, detect meaningful changes on return, and produce the concise spoken brief.
- **latency:** Acknowledge the trigger on the pendant in under 1 second; capture can complete asynchronously in 10–30 seconds. A later status question should answer from the stored checkpoint in under 2 seconds, with an explicit handoff if resume requires action.
- **cost:** Roughly one inexpensive background invocation per checkpoint and one per return comparison; realtime token cost is limited to the trigger and spoken summary. Dominant cost is authenticated browser/Mac state extraction and encrypted retention, not generation.
- **security:** The snapshot may contain private screen text, URLs, documents, and browser-session metadata. Keep raw data encrypted, retain only the latest checkpoint by default, redact secrets/password fields, and expose deletion from the pendant/dashboard. Resuming mutations should be announced, but reversible actions need no confirmation under owner policy.
- **missing:** A pendant trigger/event for an explicit away checkpoint and a durable encrypted checkpoint store; A Mac snapshot adapter that records active app/window/document identity plus a safe resumable cursor; A browser-extension snapshot adapter that records open authenticated tabs and page anchors without exporting cookies or secrets; A return-time diff worker and a typed resume token understood by mac-planner; A relay conversation lookup that can retrieve and cite the checkpoint over LTE

### "What changed because of me today? Give me a spoken, chronological explanation linking each request I made to the Mac/browser actions, files or messages affected, and the result; let me say “undo the last one” when it is reversible."
- **useful because:** Current receipts can prove that an action ran, but they do not give the owner a comprehensible causal history across relay, Mac, and authenticated browser work. A wearable-friendly explanation restores trust when the owner was away from the screen and makes accidental or surprising changes recoverable without searching logs.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Store structured events without an LLM. Use a cheaper background model to cluster events by spoken request and summarize the daily causal timeline; use realtime only for the owner’s short query and to dispatch an existing undo receipt.
- **latency:** Event append must add less than 100 ms to action completion. A daily or on-demand summary can take 3–8 seconds; the pendant should immediately acknowledge and then speak the result. Undo dispatch should begin in under 1 second.
- **cost:** Negligible per-event storage cost; one inexpensive summarization call per requested timeline (typically cents or less). Realtime cost is limited to interpreting the query and reading a compact summary.
- **security:** The ledger can contain sensitive filenames, message subjects, URLs, and dictated text. Encrypt it, redact secrets and page content by default, enforce per-owner retention/deletion, and expose citations rather than copying full private content into the spoken response. Undo must target an exact receipt and report when a change is not reversible.
- **missing:** A cross-surface event schema carrying request ID, parent intent, actor, target, typed operation, affected-resource fingerprint, result, and receipt/undo reference; Relay correlation that propagates one request ID through planner, Mac, browser, and queued jobs; A durable encrypted causal ledger with retention controls and a compact spoken-summary endpoint; Resource-diff adapters for files, calendar/reminders, and browser mutations; A pendant command parser for exact receipt selection and an explicit non-reversible explanation

### "If I hold the pendant button for five seconds, lock everything down: stop queued Mac/browser work, revoke active relay and browser-session tokens, and tell me when it is safe again."
- **useful because:** The pendant is the one surface physically with the owner, while the Mac and browser may be unattended elsewhere. Today losing a pendant, suspecting an exposed session, or needing an immediate stop requires finding another device and manually coordinating several systems.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** No model is needed for the local trigger or revocation fan-out. Realtime only confirms completion or explains any surface that failed to respond; a background worker can reconcile stragglers and retry safely.
- **latency:** Local button recognition and LTE alarm should happen immediately; relay should acknowledge within 2 seconds and issue revocations/stop signals in under 10 seconds. The pendant must show a distinct red/amber LED state even if the network is unavailable.
- **cost:** Near-zero inference cost. Requires durable revocation state and push/reconciliation requests; small storage and Worker execution cost dominate.
- **security:** This is intentionally destructive to sessions and queued work. The gesture must be hard to trigger accidentally (long hold plus LED pattern), be idempotent, and never expose secrets in speech. Re-authentication should be required to restore sessions; preserve only minimal audit metadata. If LTE is unavailable, store a signed local panic event and apply it on reconnection.
- **missing:** Firmware long-hold detection, unmistakable LED feedback, and a signed offline panic record; Relay-wide epoch/token revocation and an idempotent emergency-stop endpoint; Mac agent handling that cancels queued/reversible jobs and refuses new work under the revoked epoch; Browser extension/session invalidation that does not require exporting cookies; Dashboard recovery flow with re-pairing and a surface-by-surface health report


## Changes it proposed to its own stack

### `relay` — Add a lightweight, typed “handoff receipt” that the relay emits whenever it routes an intent, including: normalized intent label, target surface, minimal arguments, a hash of the spoken acknowledgement, and a correlation id. Store it in a small durable log so later status tools can reconcile what the owner heard with what was actually queued or executed.
- **owner gets:** When the owner asks “did you do the thing?”, the system can answer with confidence and avoid mismatches between what was promised and what was queued. It also makes cross-surface debugging safer without adding approval gates.
- effort: Medium: schema definition, durable storage, and wiring in the relay’s routing path. Requires careful token budgeting but not heavy model work.  ·  risk: If the schema is wrong or too verbose, it could leak private arguments. Recovery is to rotate the schema version and purge stored receipts.
- cost: Low per request; a small write to a durable store per routed intent. Storage grows with usage but can be capped with TTL.  ·  latency: Tiny; should not noticeably affect the spoken acknowledgement.
- security: Sensitive: must minimize stored arguments and redact secrets by default. Include only what is necessary for reconciliation.
- depends on: A stable routing decision point in the relay; A durable storage mechanism for receipts (Durable Object or D1)

### `model-routing` — Introduce a “context lease” mechanism: the relay requests a small, time-limited context bundle for a task (facts, permissions, relevant recent actions) with a token budget and expiry. Downstream agents reuse the lease id instead of resending the full context every turn; they can fetch missing pieces lazily using the lease.
- **owner gets:** Makes the system feel snappier and cheaper. The owner gets fast, consistent responses without paying repeatedly for the same context being retransmitted between surfaces.
- effort: High: requires a context service, lease issuance, and changes in how mac-planner and browser harness fetch context.  ·  risk: Cache incoherence or stale context could cause wrong decisions. Mitigation is strict TTLs, explicit invalidation on state changes, and provenance timestamps.
- cost: Medium upfront; reduces ongoing token and API costs by avoiding repeated context payloads.  ·  latency: Improves typical latency by cutting repeated context transfer; slight overhead to acquire a lease.
- security: Leases must be scoped per owner and per task, and must enforce least privilege; leaked lease ids would be sensitive.
- depends on: Typed context service (replaces hand-written per-surface prompt sections); Lease storage and invalidation strategy


## What it asked for

_Nothing._
## Its own summary

Recorded three new cross-node capabilities: an explicit wearable-triggered away checkpoint and resumable return brief; a causal, owner-readable ledger linking spoken requests to Mac/browser effects with precise undo; and a pendant long-hold emergency lockdown that revokes relay/browser access and stops Mac work even when the owner is away. Each names the firmware, relay, Mac, browser, storage, and recovery changes required rather than assuming today’s wiring.

**Biggest unknown:** Whether the existing Mac/browser agents can expose safe active-work/resource fingerprints and idempotent cancellation hooks without collecting full screen contents or browser cookies.

