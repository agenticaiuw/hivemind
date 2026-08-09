# Harness derivation — unified — round 143

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If the pendant or browser failed, tell me exactly what happened, whether my request completed, and fix only the safe parts.”"
- **useful because:** Today failure evidence is split across health, jobs, browser commands, and audio runs. A single owner-facing incident answer would prevent repeated commands and distinguish ‘not delivered’ from ‘executed but not heard’, then offer bounded repair rather than guesswork.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for correlation and explanation; realtime only if the owner asks during a live call
- **latency:** Under 5 seconds for an existing incident snapshot; repairs may take up to 30 seconds and must return a receipt.
- **cost:** About $0.01–$0.05 per diagnosis depending on evidence volume; repair calls are deterministic and dominate no model cost.
- **security:** Redact page contents, audio, tokens, and message bodies. Query only the bound job/session and require explicit confirmation for any repair that changes state. Never infer success from a missing receipt.
- **missing:** A typed owner-facing orchestration route that joins incident_diagnostics, fleet_health_and_repair, audio_pipeline_validate, and relay job records; A repair-plan confirmation gate and durable incident ID across reconnects

### "“Stage this browser action, show me what will change, and let me approve it from the pendant—even if the Mac or browser restarts—then execute only if the page is still the same.”"
- **useful because:** The system already has a physical transaction latch and a strong plan/world-digest approval engine, but the relay persistence and delivery loop are absent. Completing that loop makes the pendant a real consent boundary instead of speaking ‘waiting for approval’ and discarding the plan.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** planner/background to prepare and summarize; deterministic code enforces digest, expiry, nonce, and replay rules
- **latency:** Stage in under 3 seconds; approval remains valid for a bounded TTL and execution should begin within 2 seconds after the signed pendant event.
- **cost:** Roughly $0.01–$0.04 for planning/summarization; persistence, digest checks, and execution are deterministic.
- **security:** Persist only opaque transaction metadata and redacted labels, never page secrets. Bind approval to plan digest, world fingerprint, expiry, and monotonic nonce. Require a fresh physical approval for off-machine, uncontained, irreversible-write, and unrepeatable actions; refuse on any mismatch.
- **missing:** Implement the APPROVAL_STORE_CONTRACT in the relay and speak/read back pending approvals on the next conversation (unprompted push is unavailable); Wire physical_transaction_approval_latch events to /approve and execute only after evaluateApprovalGrant succeeds; Close ordinary ledgers and add relay job leases/requeue before any resume behavior

### "“Keep my conversation alive when I unplug the USB-connected pendant, and hand it back cleanly when LTE returns—no duplicated audio or lost turn.”"
- **useful because:** The hardware is physically testable over USB today but is not LTE-registered. A transport handoff lets the owner use the real pendant now and later move between USB/Mac and standalone relay operation without restarting a conversation or hearing duplicate playback.
- **path:** pendant → relay → mac-bridge → mac-planner
- **model tier:** realtime for active audio and turn-boundary arbitration; background for session reconciliation and receipts
- **latency:** USB takeover under 250 ms; LTE handoff only at a turn boundary, with no duplicated frames and at most one deferred turn.
- **cost:** Low model cost during transport handoff; deterministic framing and relay session state dominate. Realtime audio remains the main usage cost.
- **security:** Use monotonic transport epoch, turn sequence, and frame sequence; reject stale frames from the previous owner. Keep raw audio on the active transport only and expire abandoned session buffers. Surface a local LED/state receipt when handoff is deferred.
- **missing:** A Mac bridge transport adapter for the accepted usb_fallback_audio_session skill; Relay session ownership/lease and a turn-boundary handoff protocol; current relay jobs lack a lease_until; A typed end-to-end receipt correlating USB capture, relay processing, and pendant playback

### "“Erase this conversation everywhere it was stored, then prove to me what was deleted and what could not be reached.”"
- **useful because:** The privacy latch can stop capture and exposure, but it does not give the owner a verifiable cross-surface deletion operation. A single request should remove relay artifacts, Mac pipeline/audio records, browser-bound results, and local receipts where policy allows, then report explicit residuals instead of claiming privacy.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for scope explanation; deterministic deletion planner and receipt verifier for execution
- **latency:** Preview in under 3 seconds; deletion and verification within 30 seconds for a bounded conversation.
- **cost:** About $0.01–$0.03 for explanation; storage scans and receipts are deterministic.
- **security:** Require physical privacy-latch state or explicit confirmation for deletion. Use an immutable deletion receipt containing hashes and scopes, not the deleted content. Never delete unrelated jobs or browser data outside explicit bindings; report inaccessible third-party retention honestly.
- **missing:** A cross-surface deletion manifest with explicit artifact bindings and retention-policy outcomes; Deletion endpoints for relay pipeline artifacts, Mac audio/job records, and browser result payloads; A read-only post-deletion verifier that distinguishes deleted, expired, inaccessible, and retained-by-policy

### "“What changed across my open work since yesterday, and show me only changes that matter?”"
- **useful because:** The owner should not have to remember which browser tabs, Mac files, jobs, and pendant notes changed while they were away. A bounded, provenance-linked change digest would turn the hive into a continuity surface rather than separate tools, without requiring Accessibility or screen recording.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for clustering and prioritization; deterministic collectors produce the change set
- **latency:** Initial digest within 10 seconds; incremental updates within 2 minutes of a bound artifact changing.
- **cost:** About $0.02–$0.08 per digest depending on the number of bound artifacts; collection is primarily local and deterministic.
- **security:** Only inspect owner-selected tabs, projects, jobs, and folders. Do not infer changes from unbound apps. Redact secrets and page bodies by default; preserve source URI/path, timestamp, and content hashes for provenance.
- **missing:** A durable owner-defined watch set spanning browser sessions, Mac project paths, relay jobs, and pendant markers; A normalized change-event schema with deduplication and source-specific redaction; A spoken/dashboard digest renderer with links back to the exact evidence

### "“When you tell me something important, let me ask ‘why?’ and hear the exact sources, timestamps, and uncertainty behind that answer.”"
- **useful because:** Today the owner receives a fluent answer but cannot reliably distinguish retrieved evidence, inference, and stale memory. Provenance-on-demand would make the pendant trustworthy for decisions: the first response stays short, while a follow-up exposes the bounded evidence trail across browser, Mac, relay, and prior conversation.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** realtime for the short spoken answer and follow-up; background for source normalization and stale-evidence checks
- **latency:** Normal answer unchanged; “why?” response under 3 seconds when evidence is cached and under 10 seconds when sources must be re-read.
- **cost:** Roughly $0.01–$0.05 per evidence explanation; source collection is mostly deterministic.
- **security:** Expose only sources already authorized for the original request. Redact credentials, private page fields, and raw audio. Label model inference separately from quoted evidence, include freshness, and refuse unsupported certainty.
- **missing:** A provenance envelope attached to every model claim, including source binding, retrieval time, freshness, and confidence type; A cross-surface evidence normalizer for browser inspections, Mac reads, relay receipts, and context memory; A compact spoken citation format plus dashboard expansion for full details


## Changes it proposed to its own stack

### `relay` — Add durable lease_until/claimedBy to relay_jobs with an expiry/requeue sweep, and make the Mac worker renew and settle the lease with an idempotent completion receipt. In parallel, close ordinary action ledgers when a plan settles so only genuinely interrupted work is resumable.
- **owner gets:** A Mac sleep, browser crash, or dropped link will no longer strand a request for 24 hours or make completed work look unfinished; the owner gets one eventual outcome instead of duplicate actions or repeated manual retries.
- effort: Medium: schema migration, claim/renew/requeue paths, worker lifecycle hooks, and crash-injection tests across relay and Mac bridge.  ·  risk: A lease shorter than the real task could cause duplicate execution. Use fencing tokens and idempotency keys; on uncertainty mark the job needs-owner-review rather than replaying unrepeatable actions.
- cost: Negligible storage and request overhead; no additional model calls. Tests and migration are the main engineering cost.  ·  latency: Adds one periodic renewal request during long jobs; requeue after a bounded lease expiry, not immediately.
- security: Lease tokens must be unguessable and scoped to the job; stale workers must be rejected. Receipts should contain metadata only, not browser secrets or audio.
- depends on: The existing durable action ledger and planResume decision engine; Relay routine lease implementation as the template; A typed worker completion/receipt path for POST /execute jobs

### `context` — Make every cross-surface result carry a signed provenance envelope: claimId, source binding, retrievedAt, freshness deadline, evidence hash, and claim kind (observed, quoted, inferred, or unresolved). Store only the envelope and redacted locator by default, and make the spoken agent answer from envelopes rather than opaque text blobs.
- **owner gets:** When the pendant says “why?”, it can immediately distinguish what was actually seen from what the model guessed, reveal stale evidence, and let the owner inspect the exact supporting source instead of trusting a fluent explanation.
- effort: Medium: shared schema, adapters for browser/Mac/relay/context sources, model prompt contract, and fixtures for stale/missing evidence.  ·  risk: Incorrect adapters could make weak evidence look authoritative. Default unknown/unresolved, require source hashes, and refuse citation when the source no longer matches.
- cost: Small storage increase for metadata; modest background processing; no extra realtime model call for ordinary answers.  ·  latency: Negligible on ordinary answers; cached envelopes make follow-up provenance faster.
- security: Improves least-privilege disclosure by retaining locators and hashes rather than raw private content; source access remains scoped to the original binding.
- depends on: A cross-surface evidence normalizer; Bounded browser/Mac/relay source permissions; A spoken follow-up command for provenance lookup


## What it asked for

_Nothing._
