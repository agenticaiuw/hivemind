# Harness derivation — unified — round 236

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Fill out this browser form, but stage it first and let me approve the exact submission with the pendant; then tell me what the site accepted."
- **useful because:** It turns the physical approval latch and existing form-preview machinery into a complete safe action. The owner gets useful browser automation without giving the agent silent authority to submit irreversible or external actions.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** planner for extracting fields and explaining consequences; deterministic validation, digest/world binding, nonce replay protection, and receipt correlation; realtime only for the spoken summary
- **latency:** Preview within 5 seconds for a loaded page; approval-to-submit under 3 seconds after the next linked conversation; receipt within 5 seconds or clearly queued.
- **cost:** <$0.03 typical invocation; planner tokens and page extraction dominate, with no model call for digest/approval checks.
- **security:** Never send passwords or page secrets to the relay or pendant. Bind approval to plan digest, page/world fingerprint, expiry, and physical transaction nonce. Require explicit confirmation for external-send, delete, purchase, or off-machine actions; preserve an immutable receipt and make cancellation idempotent.
- **missing:** Implement the relay half of APPROVAL_STORE_CONTRACT and a pending-approval handoff into the next conversation; Connect physical_transaction_approval_latch events to /approve or form-preview approval with a least-privilege credential boundary; A browser result receipt carrying submitted field names (not secrets), server response, and command id

### "If my pendant drops during a conversation, reconnect it and continue from the exact turn without repeating audio or losing what I said."
- **useful because:** A wearable conversation should survive LTE/WebSocket loss as a conversation, not restart cold or replay a response. This is the highest-value end-to-end behavior: the pendant, relay, Mac, and audio receipts jointly know what was heard, what was acknowledged, and what still needs delivery.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** realtime for the active turn only; deterministic state machine for sequence checkpoints, deduplication, lease expiry, and replay; background tier for reconciliation after prolonged outage
- **latency:** Detect loss within 2 seconds, reconnect in 5 seconds when transport returns, and resume at the next unambiguously acknowledged frame without replaying more than one 60 ms packet.
- **cost:** <$0.01 incremental per recovery; storage and receipt writes dominate, not inference.
- **security:** Use opaque conversation/turn IDs, monotonic frame counters, authenticated checkpoints, and bounded retention. Treat relay acceptance, bridge receipt, and audible playback as separate states. Never infer that unacknowledged speech was heard; redact stored transcript/audio and honor the existing SD failure-only rule.
- **missing:** A relay conversation checkpoint store joining uplink capture, model turn, downlink artifact, and audio_delivery_ack_queue states; Firmware/bridge emission of authenticated reconnect and last-played frame checkpoints; A production caller for workbench handoff/reconciliation and a user-visible recovery status instead of a silent restart

### "When I deliberately trigger an emergency alert, tell me exactly who will be contacted, get a physical pendant confirmation, and keep retrying until I receive a delivery receipt or cancel it."
- **useful because:** In a real emergency the pendant is the only surface physically with the owner, while the Mac/browser may hold the contact session and the relay can retry when the Mac is asleep. This combines reach that no single node has and makes the dangerous external action explicit rather than silently firing.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** deterministic routing, contact resolution, nonce/expiry, retries, and receipt state machine; realtime only to read back the concise confirmation; background tier for bounded retry and reconciliation
- **latency:** Local pendant trigger and confirmation feedback under 500 ms; first delivery attempt within 5 seconds; retry with exponential backoff for at most 30 minutes, with a visible pending/failed state.
- **cost:** <$0.02 per incident; SMS/phone/email provider fees and browser/Mac execution dominate, not model inference.
- **security:** Never infer recipients from vague context. Require a configured allowlist, read back recipient and message hash, and require physical_transaction_approval_latch approval for every send. Rate-limit triggers, expire nonces, prevent duplicate sends with idempotency keys, redact message contents in relay logs, and require explicit cancel/expiry handling.
- **missing:** A configured emergency profile with fixed recipients, message templates, and escalation order; An outbound delivery adapter with provider receipts across Mac Messages/browser and relay fallback; A pendant trigger event and relay state machine that distinguishes staged, physically approved, submitted, delivered, failed, and cancelled

### "Let my pendant be the cryptographic authority for sensitive actions: if the pendant did not sign this exact action, the Mac, browser, and relay must refuse to send it."
- **useful because:** Today the physical latch can express consent, but the broader execution path still relies on the shared agent credential. A stolen or confused relay token should not be able to send a message, publish a form, or change a setting without the owner's device-rooted authorization.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** deterministic cryptography and policy enforcement; no model required except optional natural-language explanation
- **latency:** Under 100 ms for local signature verification and under 1 second for relay/Mac verification; key provisioning is a one-time ceremony.
- **cost:** Negligible per action; modest engineering cost for key storage, attestation, and verifier libraries.
- **security:** Private keys must be non-exportable and rotate/revoke safely. Sign a canonical action digest, recipient/origin, expiry, nonce, and policy tier—not raw secrets. Refuse downgrade, replay, stale-world, and unsigned actions. Recovery must require an explicit owner ceremony, never a server override.
- **missing:** Hardware-backed key generation or protected key storage on the pendant; A common canonical action-envelope and signature verifier in relay, Mac, and browser paths; Device attestation, revocation, and recovery flow with audit receipts

### "Give me a personal continuity vault: after a crash, battery loss, or transport change, resume my unfinished conversation or task with the minimum private context needed, and show me exactly what was restored."
- **useful because:** The system has separate conversation, job, browser, and audio records, but the owner cannot ask one question and get a trustworthy answer about what survived an interruption. A bounded, owner-visible continuity capsule would prevent both lost work and accidental replay while preserving privacy.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** deterministic capsule assembly, sequence reconciliation, and replay guards; background model only to summarize restored context after policy filtering; realtime only when speaking the restoration summary
- **latency:** Restore decision in under 2 seconds locally and under 5 seconds across relay; never replay an external action without a new approval.
- **cost:** <$0.01 per recovery; bounded encrypted metadata storage dominates, with summarization optional.
- **security:** Store only minimal encrypted checkpoints, with per-surface provenance and expiry. Separate 'heard', 'delivered', 'executed', and 'approved'; do not infer completion. Redact sensitive page/audio content and require fresh approval for unrepeatable actions.
- **missing:** A single continuity-capsule schema joining conversation, job, browser, and audio sequence state; Owner-facing restore/forget controls and per-capsule retention policy; Startup and reconnect callers that reconcile capsules instead of merely exposing raw handoff records


## Changes it proposed to its own stack

### `interaction` — Add a cross-surface 'explain before act' mode that renders the exact data flow of a planned action: what leaves the pendant, which relay/Mac/browser receives it, what is persisted, and the concrete stop/cancel point. Require the owner to choose a data-flow scope before execution, and make the selected scope part of the action digest.
- **owner gets:** The owner can currently approve an action without being shown the complete path their words and page data will take. This gives them a meaningful choice between local-only, relay-allowed, and browser-site-allowed execution instead of a vague confirmation.
- effort: Medium: add a deterministic data-flow manifest to plans, dashboard/pending speech rendering, and enforcement hooks at relay, Mac, and browser boundaries.  ·  risk: If a connector is omitted, the system could overstate privacy. Unknown destinations must block execution and be shown explicitly; manifests need versioning so a changed route invalidates approval.
- cost: Near-zero API cost; one extra manifest and hash per plan. Engineering work is the main cost.  ·  latency: Adds roughly 100–300 ms for manifest construction and display; no model call required.
- security: Improves least-privilege and prevents approval of an action whose data path changed. Must avoid leaking secret page content into the manifest.
- depends on: A canonical action envelope and digest shared by prepare/approve and physical approval; Route-level data classification for relay, Mac, and browser actions; A real pending-approval delivery path


## What it asked for

_Nothing._
## Its own summary

Recorded three non-duplicate capabilities this round: (1) physically approved browser form submission with exact-plan binding and acceptance receipt, (2) loss-resilient conversation continuation from authenticated audio/turn checkpoints, and (3) a deliberately triggered emergency alert with pendant confirmation, bounded retries, and delivery receipts. The proposed extracted-fact inspection/erasure capability was correctly rejected as an existing owner-retention requirement, so I did not rephrase it.

**Biggest unknown:** The three proposals still need implementation inventory: whether /prepare and /approve are actually mounted and whether a relay approval store exists; which firmware/bridge checkpoint events are available beyond the shipped audio acknowledgement primitive; and what emergency recipients, channels, templates, escalation order, and cancellation policy the owner wants. I still need those owner decisions and a live route/source check before claiming any of these are buildable end to end.

