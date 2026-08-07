# Harness derivation — browser-extension — round 100

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-queue-health** — The live browser bridge is offline and has 9 pending commands. GET /browser/poll nevertheless returns a navigate command created at 09:11, claimed at 13:54 by home-chrome with 13 attempts, despite that device being offline and never having a tab. Existing sessions are stale (last use 06:26).
  - evidence: GET /browser/status; GET /browser/poll; GET /browser/sessions on 2026-08-07.

## Capabilities it proposed

### "“Compare the information across my logged-in accounts, but keep each account’s data separate and tell me exactly which account each fact came from.”"
- **useful because:** People routinely have multiple work, personal, or regional accounts open in the same browser. Today the system can read authenticated pages, but it cannot reliably identify account boundaries or prove that a fact came from the intended identity. This would prevent silent cross-account mixups while making comparisons across private sites genuinely useful through the pendant.
- **path:** browser-extension → mac-planner → faculty-perception → faculty-judgement → relay-realtime → pendant
- **model tier:** Use the cheaper background tier for extraction, account-context classification, normalization, and comparison; use realtime only to answer the owner’s spoken follow-up and read the concise, cited result aloud.
- **latency:** Initial comparison may take 10–30 seconds across several sessions; follow-up questions should respond within 2 seconds from the stored evidence bundle.
- **cost:** Roughly $0.01–$0.08 per comparison depending on page volume; browser actions and evidence storage dominate operational cost, while model cost is limited by extracting only relevant fields.
- **security:** Account labels, URLs, page text, and snippets are highly sensitive and must remain on the owner’s Mac/relay path, with only the minimum cited fields sent to the model. Never infer identity from a display name alone: bind an account fingerprint to origin, session, and stable authenticated markers, mark uncertainty explicitly, and never merge records when identity is ambiguous. No external submission or message sending is part of this capability.
- **missing:** A browser account-context detector that records stable, non-secret identity markers per origin/session without storing credentials; Typed evidence records carrying account fingerprint, origin, tab/session, timestamp, and confidence through the planner; Cross-session comparison and contradiction handling that refuses to merge ambiguous identities; A durable, privacy-scoped evidence bundle that the realtime pendant response can cite; A real browser enqueue/reconnect path and stale-command fencing so private pages are not read or acted on through an offline device


## Changes it proposed to its own stack

### `browser-harness` — Add offline-device lease fencing and queue reconciliation. Every browser command gets an owner device lease tied to a heartbeat epoch, a max age/expiry, and a persisted state machine (queued/claimed/running/expired/requeued/cancelled). The poll endpoint must never hand a command to an offline or stale device, must reject results from an old epoch, and must quarantine commands whose lease expired rather than replaying them blindly. Expose a read-only reconciliation report listing pending, stale, expired, and requeued commands with idempotency keys and safe retry classification; allow an explicit cleanup operation for stale commands.
- **owner gets:** When Safari reconnects after sleep or a crash, old browser actions will not suddenly navigate, type, or click using yesterday's intent. The owner gets a clear account of what was skipped and can resume only the still-current work instead of risking duplicate or surprising private-session actions.
- effort: Medium: browserBridge lease/heartbeat epoch, durable queue state and reconciliation endpoint, extension reconnect handshake, and tests for crash/reconnect/race cases.  ·  risk: A command may be quarantined even though the extension is briefly slow, delaying useful work; conservative expiry and explicit requeue recover it. Old results must be accepted for evidence but never advance a newer command state.
- cost: Negligible API/storage cost; a few small JSON/D1 records per command and occasional reconciliation reads.  ·  latency: No added latency for healthy online execution; reconnect adds one handshake and stale-queue scan.
- security: Reduces replay and cross-device execution risk; keep URLs, typed text, and page evidence out of broad status responses, exposing only hashes/labels unless owner requests details.
- depends on: chg-14accc01 request IDs/idempotency/tab affinity (existing partial implementation); chg-16bc5dee durable browser job runner (still missing); A reliable extension heartbeat/device identity (Safari currently offline; home-chrome stale)

### `browser-harness` — Create an account-boundary ledger for authenticated browser work. For each origin/session, persist a salted account fingerprint derived only from stable visible markers (origin, account label, avatar URL hash, tenant/workspace identifiers), plus confidence and first/last observed timestamps. Require every extracted field and evidence capsule to carry that boundary; when a navigation or tab switch changes the fingerprint, automatically split the work context and emit a contamination warning. Comparisons may join records only through an explicit, auditable relation; raw credentials and full page text never enter the ledger.
- **owner gets:** The owner can safely ask for a comparison across personal and work accounts without accidentally receiving a blended answer or having an action prepared in the wrong identity. They get a clear “this came from Work Acme” trail and a warning when Safari silently switches tenants or accounts.
- effort: Medium-high: extension-visible identity-marker extraction, salted fingerprinting, session/tab boundary propagation through browserBridge and evidence capsules, context-split events, and comparison API support.  ·  risk: Some sites expose no stable visible marker or change labels dynamically, causing an unknown boundary and less useful comparisons; recover by marking the source unclassified rather than guessing. Fingerprints must be non-reversible and deletable with the session.
- cost: Small persistent metadata overhead and one inexpensive classification pass per navigation; no additional browser-minute usage beyond the existing read.  ·  latency: Under 100 ms for local marker hashing; occasional model classification only when a site’s identity markers are ambiguous.
- security: Improves isolation but creates sensitive metadata about account use. Keep the ledger local, encrypt at rest, apply short retention, and exclude marker values from general logs and voice context.
- depends on: A reliable browser command/result path with tab and session affinity; Evidence capsules carrying source provenance; A durable browser job/context store; The proposed cross-account comparison capability


## What it asked for

_Nothing._
