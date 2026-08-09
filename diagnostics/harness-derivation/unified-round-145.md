# Harness derivation — unified — round 145

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser readiness** — The live agent is healthy and ready; Accessibility and Screen Recording are now granted for AI Pendant Agent, browser extension is online with 9 Safari tabs, relay is reachable, and pending browser commands/spool are zero.
  - evidence: GET /ops/status returned ready:true, accessibility trusted, screenRecording granted, browser online, relay reachable; GET /health returned version 0.5.0; GET /browser/inspections returned inspections:[]

## Capabilities it proposed

### ""Give me a trustworthy end-of-day account of what the pendant, Mac, browser, and relay did for me today—and call out anything that was promised but not proven.""
- **useful because:** Today evidence is fragmented across jobs, browser commands, audio pipeline records, and device receipts. This produces one owner-readable audit that distinguishes relay acceptance from actual playback and distinguishes a claimed completion from evidence. It is the highest-value trust feature: the owner can wear the device without having to believe it blindly.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for collection and deterministic joins; realtime only to answer a follow-up question
- **latency:** Initial report 5–15 seconds; incremental updates under 2 seconds after a job closes
- **cost:** <$0.01 per report when deterministic joins suffice; <$0.05 only if a model must summarize contradictory evidence. Storage and route reads dominate, not tokens.
- **security:** Redact page contents, message bodies, audio, and secrets by default; expose only metadata, hashes, timestamps, and citations. Browser bindings must remain tab-scoped. Require explicit confirmation before showing sensitive evidence or exporting the report.
- **missing:** A durable cross-surface event index keyed by job/turn/artifact IDs; A typed join route that combines relay jobs, Mac receipts, browser results, audio_delivery_ack_queue records, and pendant events; Owner-facing contradiction and missing-proof taxonomy

### ""Read this private browser page to me, but do not let its contents be stored, sent to another app, or remain in the relay after you answer.""
- **useful because:** The browser is the only node with some authenticated sessions, while the pendant is the only node that can give a private spoken result. A privacy-scoped read would let the owner use those sessions without turning the relay into a copy of their account. It is meaningfully cross-surface: browser acquisition, relay transformation, pendant playback, and post-delivery erasure all have to agree.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** realtime for short extraction and speech; deterministic policy/redaction checks before and after the model
- **latency:** 10 seconds for a normal page; 2 seconds to acknowledge refusal or policy violation
- **cost:** $0.01–$0.08 per page depending on transcription/summarization length; browser extraction and secure deletion dominate engineering cost.
- **security:** Default deny for passwords, payment pages, private messages, and downloads. Bind to an exact tab/session, send only the minimum selected DOM text, encrypt in transit, keep a memory-only relay buffer with TTL, and return a verifiable deletion receipt. Require physical_transaction_approval_latch for any action beyond reading.
- **missing:** A no-persistence relay execution mode with enforced TTL and deletion receipt; Browser-side field classification and minimum-text extraction; A pendant playback receipt linked to the ephemeral request; A policy surface for owner-selected domains and prohibited data classes

### ""What of my voice, browser pages, and actions is still retained right now? Show me the retention locations and let me erase only this conversation everywhere.""
- **useful because:** The privacy latch stops future capture, but it does not tell the owner what already crossed the pendant, bridge, relay, Mac, or browser, nor provide scoped deletion. A retention map plus authenticated erase receipt turns privacy from a gesture into something inspectable and actionable across the whole hive.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic inventory, policy filtering, and deletion receipts; background model only summarizes the resulting inventory
- **latency:** Inventory in under 3 seconds; scoped erase request acknowledged in under 1 second and converged within 30 seconds
- **cost:** <$0.01 per inventory/erase; disk scans and receipt signing dominate, not model inference.
- **security:** Require local_privacy_latch or physical confirmation for erase of audio; never reveal raw page/audio contents in the inventory; bind erase to an exact conversation/artifact set; use authenticated tombstones and report surfaces that could not be reached instead of claiming deletion.
- **missing:** A cross-surface retention manifest with artifact class, location, expiry, and hash; Idempotent scoped deletion/tombstone routes on relay, Mac, browser spool, and pendant OUTBOX/INBOX; A signed convergence receipt that distinguishes erased, pending, and unreachable; Dashboard UI for selecting a conversation without exposing its contents

### ""Let this sensitive browser action run only while I am physically holding the pendant; if it leaves my body or the link changes, stop before the next irreversible step.""
- **useful because:** A one-time approval proves consent at one moment, but it cannot express “I am continuously present while this sensitive workflow runs.” This capability makes the worn device a physical presence boundary for browser and Mac actions: useful for payments, account changes, and high-consequence forms without granting a remote session an unattended window.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic policy and heartbeat enforcement; realtime model only interprets the owner's request and explains stops
- **latency:** Presence loss detected within 250 ms and blocks the next action; normal action authorization adds under 100 ms
- **cost:** Near-zero model cost after setup; engineering cost is protocol and browser/Mac enforcement, plus hardware test coverage.
- **security:** Presence must be cryptographically bound to a specific staged transaction and device counter, not inferred from network reachability. Fail closed on USB disconnect, LTE ambiguity, stale heartbeats, reboot, or pendant privacy latch. Never expose secrets to the pendant; require a fresh physical hold for rearming.
- **missing:** A short-lived, signed presence lease emitted by pendant firmware; Relay enforcement that binds the lease to one transaction and monotonic epoch; Browser and Mac executors that check the lease before every mutating step, not just at plan start; A visible dashboard state showing held, expiring, stopped, and why


## Changes it proposed to its own stack

### `relay` — Add a first-class ephemeral job class: encrypted in-memory buffers only, hard TTL, no D1 persistence, no job recall, and a signed deletion/expiry receipt emitted to the owner-facing audit stream. Reject the job if any downstream component cannot honor the no-persistence contract.
- **owner gets:** Private browser reads and sensitive spoken answers can be useful without silently becoming permanent copies on the relay.
- effort: Medium: worker request path, streaming buffer limits, downstream capability handshake, receipt signing, and fault-injection tests.  ·  risk: A crash can lose the answer; the system must say that clearly. Any accidental persistence is a privacy failure, so default to refusal when the contract is uncertain. Recover by treating the request as failed and retaining only a minimal redacted error receipt.
- cost: Negligible storage cost; modest CPU for encryption and receipt signing; no model cost beyond the requested response.  ·  latency: Adds roughly 10–50 ms for policy negotiation and receipt creation.
- security: Strongly improves data minimization, but requires key rotation, memory scrubbing, and tests proving no fallback to ordinary job persistence.
- depends on: A typed ephemeral execution route; Browser minimum-text extraction and classification; Cross-surface retention manifest

### `context` — Introduce a cross-surface artifact identity envelope: every turn, audio artifact, browser command, Mac action, and relay job receives a monotonic turn epoch plus opaque artifact ID, with parent/child links and no raw content in the index. Make audio delivery acknowledgements, action receipts, and browser results publish into this envelope.
- **owner gets:** The owner gets one answer to “what happened?” instead of separate, contradictory stories from the relay, Mac, browser, and pendant.
- effort: High: shared schema, adapters at existing routes, migration for old records, bounded retention, and contradiction handling.  ·  risk: Incorrect joins could attribute another person's or another turn's action to this one. Recover by refusing to join when epochs or bindings disagree and showing “unlinked” evidence.
- cost: Small metadata overhead (roughly hundreds of bytes per event); no meaningful inference cost.  ·  latency: Usually under 5 ms per event; report generation remains background work.
- security: Opaque IDs and redacted metadata reduce exposure, but the index itself is sensitive and needs access control, retention limits, and deletion propagation.
- depends on: audio_delivery_ack_queue; A typed cross-surface join route; A retention manifest and tombstone protocol

### `hardware` — Add a small secure element with monotonic counter and protected signing key to the pendant revision, wired over I2C; use it to attest physical-presence leases, transaction approvals, privacy-latch transitions, and transport epochs. Keep raw audio and page contents out of the secure element; it stores only keys, counters, and compact state hashes.
- **owner gets:** The pendant becomes a trustworthy physical boundary rather than a button whose approval can be replayed or forged by a compromised Mac, browser extension, or relay. Sensitive actions can fail closed even when the connected computer is not trustworthy.
- effort: Medium-high hardware revision plus firmware driver, provisioning flow, relay verification, and recovery procedure for counter loss. Prototype can be exercised over the currently USB-connected pendant before a board spin, but production assurance needs the actual secure element.  ·  risk: Bad provisioning or counter rollback could strand approvals; recover with a factory enrollment ceremony and a clearly documented device replacement path. Added I2C failure must not prevent ordinary audio or privacy latch operation.
- cost: Roughly $0.50–$2 BOM increase in volume, under 10 mW active and negligible standby depending on part; adds board area and manufacturing provisioning work.  ·  latency: Typically 10–100 ms for a signature, so use it at lease issuance and approval boundaries, not every audio frame.
- security: Substantially improves anti-replay and device authenticity, but creates a new root of trust requiring key backup policy, secure provisioning, and explicit replacement semantics.
- depends on: A signed presence-lease protocol; Relay verification and epoch binding; Pendant firmware integration with physical_transaction_approval_latch


## What it asked for

### `c21-a8c8` (context) — owner retention and deletion policy
- why: The proposed cross-surface retention map and scoped erase feature need a policy for default audio/page retention and whether deletion should include failed-upload SD buffers, relay receipts, and browser history.
- would change: Until answered I will design conservative defaults: no raw browser/page persistence, audio retained only under the existing failure-buffer rule, metadata retained briefly for receipts, and erase requiring physical confirmation. The owner's answer would change TTLs, deletion scope, and confirmation requirements.

## Its own summary

Round 145 produced three distinct owner-facing capabilities: (1) a cross-surface end-of-day trust report that separates claims from proof, (2) an ephemeral private browser-to-pendant read with enforced non-persistence and deletion receipt, and (3) a cross-surface retention map with scoped erase receipts. I also proposed two stack changes: an enforced relay ephemeral-job class and a shared opaque artifact/turn identity envelope. Live discovery shows the Mac agent, browser bridge, relay, Accessibility, and Screen Recording are all currently ready; browser has 9 online Safari tabs and no pending commands. I still need the owner's retention/deletion policy (queued as c21-a8c8); until then I recommend conservative defaults: no raw page persistence, audio only retained under the existing failure-buffer rule, short metadata TTLs, and physical confirmation for audio erasure. Implementation still needs typed cross-surface joins, retention manifests/tombstones, and the relay's no-persistence execution path.

**Biggest unknown:** Whether the owner wants deletion to cover failed-upload pendant buffers and audit metadata, and what default retention periods are acceptable.

