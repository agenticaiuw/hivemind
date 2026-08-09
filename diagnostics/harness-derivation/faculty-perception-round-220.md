# Harness derivation — faculty-perception — round 220

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live reachability** — At the latest authenticated continuity read, the Mac agent is permission-ready (Accessibility and Screen Recording granted, automation grants present), Safari browser bridge is online with two tabs but advertises capabilities:[], relay is reachable with D1 and Mac bridge online, and the registered-device list contains no nRF pendant (only home-macbook-bridge online and cloudflare-contract-test offline).
  - evidence: read_continuity_snapshot(include=['relay','pipeline'], since='2026-08-08T00:00:00Z', maxItems=20) resolved to GET /ops/snapshot, HTTP 200; body timestamped 2026-08-09T00:33:30Z and explicitly reports those fields.

## Capabilities it proposed

### "Before you tell me something or act, give me a one-sentence reality receipt: what you observed, where it came from, how fresh it is, and what you could not verify."
- **useful because:** This would make the system trustworthy rather than merely fluent. It would prevent a completed Mac job, a relay socket write, or a browser's untrusted page text from being presented as owner-heard, successfully changed, or still true. It is the single most useful capability because every later answer and action can inherit the same evidence fence.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → relay → pendant → unified
- **model tier:** Use deterministic freshness/provenance joins and a cheap classifier first; escalate only ambiguous contradictions to the realtime model. Do not spend the realtime tier summarizing raw logs.
- **latency:** Under 300 ms for existing receipts and snapshots; up to 2 s when a fresh browser or Mac observation is required.
- **cost:** Usually near-zero model cost when joining existing records; occasional browser/Mac observation dominates latency, not tokens.
- **security:** Receipts must redact secrets and distinguish owner-authorized facts from page text. Never claim playback or mutation success without device-originated evidence. Require confirmation for destructive actions even when a receipt exists.
- **missing:** A relay-to-Mac evidence transport that returns a stable read ID and content hash, then mints the existing Mac evidence capsule.; A common receipt schema joining action ledger, browser provenance, relay jobs, device playback events, and freshness.; A policy gate that refuses unsupported claims instead of merely labeling them untrusted.

### "What can you actually reach right now, and what is blocked? Test the exact Mac, browser, relay, and pendant paths and answer with a live capability map, not a guess."
- **useful because:** Today the Mac agent reports Accessibility and Screen Recording ready, the browser bridge is online but advertises zero capabilities, the relay is reachable, and no pendant is registered. A single honest map would stop the owner from asking for an action that silently falls back, and would expose stale or contradictory health claims before they matter.
- **path:** unified → mac-planner → mac-vision → browser-extension → relay-realtime → relay → pendant
- **model tier:** Deterministic probes and route metadata; a cheap model may compress the result into the owner's one-sentence preference. Realtime is unnecessary unless the owner asks a follow-up.
- **latency:** 500 ms from cached heartbeat/permission state; 3 s when an active probe is needed. Mark each result with observedAt and probe type.
- **cost:** No model cost for the map; active browser/Mac probes and relay requests dominate.
- **security:** Probe read-only endpoints only by default. Do not enumerate private tabs, page contents, or credentials merely to test reachability. Distinguish 'permission granted' from 'surface actually online' and 'route exists' from 'action succeeded'.
- **missing:** A typed read-only reachability endpoint that combines /ops/status, browser bridge state, relay device status, and pendant registration without pretending absent sources are zero.; An explicit browser capability handshake: the live extension currently reports capabilities:[] despite being online.; A pendant registration/heartbeat path that can prove the worn device is present; until then report absent, not offline.

### "Tell me when two parts of you disagree about reality—for example, when a surface says it is ready but cannot perform its advertised operation, or when a job is complete in one store and unfinished in another—and show me the smallest test that would resolve the disagreement."
- **useful because:** The owner should not have to discover silent split-brain behavior after an action fails. A one-time capability map is already stale the moment a bridge loses its session; this is a continuous divergence alarm that catches contradictory state across the Mac, browser, relay, pipeline, and wearable before the contradiction becomes an incorrect answer or missed action.
- **path:** unified → relay-realtime → relay → mac-planner → mac-vision → browser-extension → pendant
- **model tier:** Use deterministic field comparisons, timestamps, and bounded health probes. Use a cheap model only to explain the conflict in the owner's preferred one sentence; reserve realtime for an interactive investigation.
- **latency:** Evaluate on every heartbeat/job transition and within 1 second of a user query. Do not block ordinary conversation on a low-priority probe; emit a pending conflict with an expiry.
- **cost:** Near-zero model cost for detection; bounded read-only probes are the main cost. A model explanation is occasional and short.
- **security:** Expose only conflict metadata and redacted identifiers, never page contents, credentials, or secret memory. A probe must not mutate state or retry an action without confirmation. Do not collapse disagreement into a false winner.
- **missing:** A versioned cross-surface observation record with source, observedAt, expiresAt, and correlation key.; A divergence engine with domain-specific comparison rules for permissions, browser capability handshakes, job completion, and device liveness.; A resolver action that proposes—not silently performs—the smallest safe read-only test and records its result.

### "Erase this piece of private content everywhere you stored or derived it, and show me a deletion receipt listing every store checked, every copy removed or tombstoned, and any copy you could not reach."
- **useful because:** Today a page excerpt can enter relay announcements without its URL, relay audio retention is unscheduled, and several Mac stores are count- or byte-capped rather than time-retained. The owner has no honest way to revoke a sensitive recording, browser read, or generated speech across the whole hive. A verifiable privacy burn is more useful than a retention setting because it answers the concrete question: is it gone?
- **path:** unified → relay-realtime → relay → mac-planner → browser-extension → pendant
- **model tier:** Deterministic content-addressed lookup and deletion/tombstone operations; no realtime model is needed except to identify ambiguous natural-language targets before asking confirmation.
- **latency:** A bounded delete sweep in under 5 seconds for reachable stores; return partial completion immediately with a retryable receipt when a surface is offline.
- **cost:** Low API cost; storage scans and durable tombstone writes dominate. No expensive model call should be required.
- **security:** Always require explicit confirmation, except for content the owner has already designated for automatic expiry. Authenticate every deletion per surface, preserve minimal tombstones to prevent resurrection, and never include the secret body in the receipt. A failed or offline deletion must be reported as failed, not implied complete.
- **missing:** A cross-surface content identity scheme linking browser capsules, relay announcements/audio, Mac recordings, jobs, and pendant buffers without storing raw secret text in the index.; Authenticated delete/revoke endpoints on every store, including a scheduled relay announcement/audio sweep that actually runs.; A durable deletion ledger with retry state and a final receipt distinguishing removed, tombstoned, unreachable, and unknown.

### "For this task, use my strict evidence rule: do not call it done until the required surfaces agree, and stop with a specific unresolved reason if they cannot. Let me save different rules for different kinds of actions."
- **useful because:** The owner needs more than a generic confirmation prompt. Sending a message, changing a file, reading a private browser page, and speaking through a wearable have different proof requirements. A per-domain evidence contract would let the owner choose, for example, visual confirmation for browser mutations, an application receipt for file changes, and device playback evidence for speech—without forcing the same brittle rule everywhere.
- **path:** unified → faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime → pendant
- **model tier:** Compile owner rules into deterministic gates and evaluate receipts mechanically. Use a cheap model only to translate a natural-language rule into a proposed policy; require owner confirmation before activating it.
- **latency:** Policy lookup under 20 ms; gate evaluation under 500 ms after each stage. If evidence is missing, return immediately with a pending state rather than waiting indefinitely.
- **cost:** Negligible recurring model cost after policy compilation; evidence checks and retries are the dominant operational cost.
- **security:** Policies must be scoped by action, surface, and data sensitivity, with deny-by-default for ambiguous matches. Never let a model weaken a saved rule. Require explicit confirmation to change or disable a strict policy, and keep an audit trail without retaining private content.
- **missing:** A versioned owner policy store with scopes, precedence, expiry, and an explanation of which rule blocked an action.; A typed evidence contract language mapping action classes to acceptable proof, freshness bounds, and quorum requirements.; Action and judgement gates that enforce the contract before reporting success, rather than only displaying receipts afterward.


## Changes it proposed to its own stack

### `memory` — Add a non-destructive authority-check before contextProjection emits pinned preferences: compare machine-origin facts against the live authority that resolves that domain (for timezone, /etc/localtime), mark mismatches as contested, exclude them from the ## Owner head, and surface the exact stale value plus its origin for owner confirmation. Never delete or rewrite the fact automatically.
- **owner gets:** The owner currently receives America/Chicago as a high-confidence pinned preference even though this Mac resolves to America/New_York; the stale machine fact has been used 5,374 times. This prevents wrong scheduling, 'this morning' interpretation, and quiet-hour behavior without silently changing something that belongs to the owner.
- effort: Moderate: authority adapters for timezone first, then calendar/account/device domains; projection filtering and a small diagnostic record. Existing memory provenance already supplies source.origin and confidence.  ·  risk: A legitimate travel or remote-machine preference could be hidden. Recovery is straightforward: retain the contested fact, show it in the diagnostic view, and allow an owner-confirmed override with explicit scope (machine vs owner).
- cost: Negligible API cost; one local comparison per projection and a bounded diagnostic entry.  ·  latency: Under 10 ms locally for timezone; other adapters may require cached reads, never a blocking cloud call for ordinary prompts.
- security: Improves safety by preventing machine-injected values from masquerading as owner intent. Do not expose secret fact values in diagnostics; expose provenance and conflict reason only.
- depends on: A stable authority registry identifying which source wins for each fact domain.; A projection hook that can suppress contested machine-origin facts without deleting them.


## What it asked for

_Nothing._
