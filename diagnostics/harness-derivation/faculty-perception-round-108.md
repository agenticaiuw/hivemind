# Harness derivation — faculty-perception — round 108

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac agent accessibility** — At 2026-08-07T15:00:55Z, AI Pendant Agent reports Accessibility trusted=false, Screen Recording=false, inputReachability failed, and UI actions will not reach screen; AppleScript automation has no missing grants.
  - evidence: GET /observe returned accessibility.trusted=false, screenRecording=false, inputReachability.status=failed, uiActionsWillReachTheScreen=false; GET /ops/status returned automation grants and permissions.ready=false.
- **live browser bridge** — At 2026-08-07T15:00:44Z, Safari browser bridge is online with one tab and zero pending commands; foreground app is AI Pendant Browser Bridge.
  - evidence: GET /ops/status returned browserExtension.online=true, pendingCommands=0, Safari on MacIntel lastSeenAt 2026-08-07T15:00:44.693Z; GET /observe foregroundApp is AI Pendant Browser Bridge.
- **live pendant presence** — Devices discovery currently shows only home-macbook-bridge online and cloudflare-contract-test mobile offline; no pendant device is registered.
  - evidence: discover(devices) returned exactly Safari on MacIntel, home-macbook-bridge online, cloudflare-contract-test offline; no pendant entry.

## Capabilities it proposed

### "“What is actually connected and usable right now?” Give me a short, evidence-backed live state report across my Mac, browser, relay, and pendant, explicitly separating live observations from stale history and telling me which actions are safe to trust."
- **useful because:** Today the system can report success while UI actions do nothing, and recorded pendant audio can look like a live wearable. A freshness-aware perception quorum would prevent the owner from relying on false availability: it would say browser is live, AppleScript is usable, GUI input is not, and no pendant is connected, with timestamps and sources.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → unified
- **model tier:** Use a cheap background/state-classification model (or deterministic reducer) for every check; reserve realtime only to phrase the already-verified result in the owner's one-sentence voice response.
- **latency:** 2–5 seconds for parallel probes; under 1 second when a recent observation snapshot is within its TTL. No need to invoke an expensive model for unchanged state.
- **cost:** About $0.001–$0.01 per report if classification is deterministic or a small text model; network and Mac probes dominate latency, not tokens.
- **security:** Private browser URLs/titles and local permission state must stay in the authenticated relay and not be sent to third-party models. Redact page contents; report capability/status rather than secrets. This is read-only and needs no confirmation.
- **missing:** A typed perception snapshot endpoint that fans out to /ops/status, /observe, /browser/sessions, relay health/device registry, and pipeline freshness, then applies per-field TTLs.; A device-registry read route exposed to the perception service (the current local agent has no GET /v1/devices/status route).; A provenance schema distinguishing live device telemetry from recorded /pipeline history, with monotonic observation timestamps and explicit unknown/absent states.; A small dashboard/voice formatter that exposes contradictions (for example browser online but Accessibility false) rather than collapsing them into one ready flag.

### "“For my last request, show me the chain of custody across the relay, Mac, browser, and pendant: what each node observed, which handoff was acknowledged, where execution stopped, and the safest exact point to resume.”"
- **useful because:** Today a distributed request can produce a success receipt even when GUI input never reached the screen, while the relay, browser, and local agent each retain different fragments of truth. The owner cannot obtain one tamper-evident, causal explanation of what really happened or resume without repeating an already-completed step. This would be a proof-carrying handoff timeline, not another job runner or page watcher.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action → unified
- **model tier:** Deterministic event correlation and hash-chain validation should do the core work; use a small background model to summarize the timeline. Use realtime only when the owner asks verbally for the explanation.
- **latency:** Under 3 seconds for an existing request; up to 10 seconds to reconcile late acknowledgements from sleeping nodes.
- **cost:** Under $0.01 per lookup; storage and signature verification dominate, with no expensive model required unless a natural-language summary is requested.
- **security:** Events may contain private URLs, account names, and action arguments. Encrypt event payloads at rest, expose redacted summaries by default, bind records to the owner's authenticated session, and require confirmation before using a recovered checkpoint to perform an external side effect.
- **missing:** A shared, append-only event envelope with requestId, parentEventId, node identity, monotonic sequence, observedAt, action intent, precondition, result, and evidence hash.; Mutual acknowledgement protocol between relay, Mac bridge, browser extension, and future pendant, including explicit negative acknowledgements and expiry.; A reconciliation service that detects impossible sequences (for example receipt without input reachability) and marks a request indeterminate instead of successful.; A checkpoint catalog describing which steps are idempotent and which require fresh owner approval before resume.


## Changes it proposed to its own stack

### `context` — Add an Observation Lease / Truth Ledger beneath faculty-perception. Every cross-surface fact is stored as a typed observation with source, observedAt, expiresAt, probe status, and evidence class (live, cached, historical, absent, or unknown). A reducer refuses to promote historical pipeline/audio records into current device state, preserves contradictory facts (e.g. browser online while Mac UI input is unreachable), and emits a machine-readable safe-to-trust matrix for faculty-judgement. Re-probe only expired fields and retain the last failure reason instead of silently treating missing data as healthy.
- **owner gets:** The owner gets honest answers about what can be relied on now. It stops the particularly dangerous case where a stale pendant recording or a success receipt is mistaken for a connected, functioning wearable or a completed GUI action.
- effort: Medium: schema, TTL reducer, parallel probe adapter, and tests for stale/contradictory/absent observations; integrate with relay and voice formatter.  ·  risk: An overly short TTL could make the system seem unavailable during a transient network failure; recover by reporting 'unknown—last seen at...' and retrying, never by guessing healthy. Existing status consumers need a compatibility projection.
- cost: Negligible storage; roughly $0.001–$0.01 per on-demand report if a small classifier is used, otherwise probe costs only.  ·  latency: Parallel probes add about 2–5 seconds on expired fields; cached unexpired snapshots return sub-second.
- security: Store only status metadata and redacted evidence hashes; do not copy private page contents or secrets into the ledger. Keep it bearer-authenticated.
- depends on: Expose authoritative relay device registry and delivery acknowledgments.; Define retention/acknowledgment semantics for continuity events and pipeline history.; Add a typed observation snapshot route consumable by faculty-judgement and unified.


## What it asked for

_Nothing._
## Its own summary

Fresh reality established: the Mac bridge and Safari browser bridge are online (one tab, zero pending commands), but the AI Pendant Agent is not UI-safe: Accessibility and Screen Recording are false, input reachability failed, and GUI receipts cannot be trusted; AppleScript automation is granted. Device inventory still has no registered pendant, only the online Mac bridge and an offline test mobile. I recorded these facts and proposed an observation-lease truth ledger plus a live cross-surface “what is actually connected and usable?” report that preserves stale, absent, and contradictory states.

**Biggest unknown:** I still need an authoritative relay/device-registry read and delivery acknowledgements, plus the pending 24 kHz audio implementation and continuity-retention semantics. Until a real pendant registers, all wearable claims remain design-time only. For Mac GUI control, only the owner can grant Accessibility and Screen Recording to the exact AI Pendant Agent binary; I will not re-request that grant.

