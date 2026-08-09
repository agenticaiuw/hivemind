# Harness derivation — unified — round 160

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live surfaces and route truth** — Safari browser extension and home-macbook-bridge are online. /ops/snapshot reports computer-use loop enabled but visionUploadConsented=false. Route discovery lists browser inspect/result routes, but describe on those names performed a GET and returned 404, so method/route parity must be verified before treating them as callable.
  - evidence: discover:devices; probe/describe GET behavior for POST /browser/inspect and POST /browser/result/:commandId; GET /ops/snapshot returned 200

## Capabilities it proposed

### ""Finish this web task, but only if the final page proves the exact outcome I asked for; tell me if anything differs.""
- **useful because:** Today a browser command can report success while the site silently changes state, redirects, or partially completes. This gives the owner a consequential-task mode that stages the action, uses the pendant's physical approval, executes in the bound browser tab, and independently checks the postcondition before claiming completion.
- **path:** relay-realtime → browser-extension → mac-planner → pendant → relay
- **model tier:** background for planning and deterministic checks; realtime only for the spoken confirmation and exception
- **latency:** 2-5 seconds to stage and speak the preview; 5-20 seconds for browser execution and verification
- **cost:** Usually <$0.01 per invocation; model planning dominates, while browser checks and receipts are local
- **security:** Bind every action to tab/session URL and a plan digest; never send page secrets to the model; require physical_transaction_approval_latch for off-machine or irreversible actions; if the postcondition is absent or ambiguous, report not proven rather than success.
- **missing:** postcondition schema and evaluator for browser results; relay persistence for approval handoff and delivery; a browser action receipt containing final URL, selected state, and redacted evidence; orchestrator closeLedger integration so completed plans are not misclassified as interrupted

### ""When I ask what happened while I was away, give me one spoken timeline of my pendant, Mac, browser, and relay—with gaps called out.""
- **useful because:** The owner currently has separate job, audio, browser, and device records. A single timeline would make outages and silent failures understandable without opening a dashboard, and would distinguish 'queued', 'executed', 'delivered', and 'heard' rather than collapsing them into success.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** background model to summarize a bounded, redacted event slice; deterministic correlation first
- **latency:** Under 3 seconds for a 15-minute window; up to 10 seconds for a day
- **cost:** <$0.02 for a day summary; event correlation is local and token volume is the main cost
- **security:** Default to redacted metadata and explicit time bounds; only include browser targets already bound to the request; never expose page content or raw audio unless separately requested; retain only opaque IDs in the spoken result.
- **missing:** a typed cross-surface event envelope with one correlation ID and monotonic timestamps; pendant/bridge delivery and playback receipts joined to relay job IDs; a read-only route that merges existing diagnostics, jobs, browser results, and pipeline events; owner-defined retention/deletion policy (currently unanswered)

### ""If my connection drops during a conversation, keep my turn alive and tell me exactly where it resumed—without replaying or duplicating anything.""
- **useful because:** A dropped LTE or USB link currently risks a lost turn, duplicate playback, or an answer that exists only on the relay. This is a user-visible continuity mode: sequence-numbered audio and turn state move between LTE, USB, Mac, bridge, and relay at a turn boundary, then the owner hears only the missing suffix.
- **path:** pendant → relay-realtime → mac-planner → relay → browser-extension
- **model tier:** realtime for active audio and turn handoff; deterministic state machine for replay suppression
- **latency:** Detect within 1 second; resume within 2-4 seconds after a link returns; no extra model turn unless audio is unrecoverable
- **cost:** Negligible incremental model cost when resuming; storage and receipt metadata dominate
- **security:** Use authenticated session and turn nonces, per-frame sequence numbers, bounded encrypted relay buffering, and a hard expiry; never replay a microphone frame or spoken response twice; if continuity cannot be proven, stop and ask the owner.
- **missing:** relay job/audio lease with expiry and requeue; cross-transport handoff protocol that combines usb_fallback_audio_session with LTE ownership; persistent turn manifest recording last captured, transcribed, encoded, delivered, and played sequence; bridge acknowledgement correlation from audio_delivery_ack_queue

### ""My pendant is lost. Revoke it now, preserve anything recoverable, and move my pending work and settings to the replacement without replaying actions.""
- **useful because:** A wearable can be lost, stolen, or physically damaged. Today there is no demonstrated device registry or revocation/recovery ceremony, so pending alerts, offline memos, approvals, and conversation state either remain exposed or become orphaned. This makes replacement survivable without silently trusting a new device.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → relay
- **model tier:** deterministic identity/revocation and state migration; realtime only for spoken status
- **latency:** Revoke within seconds while online; replacement bootstrap in under 2 minutes; offline pendant data recovers when the old device reconnects, if it can
- **cost:** <$0.02 per replacement; cryptographic metadata and migration storage dominate
- **security:** Require owner authentication plus a deliberate physical ceremony on the replacement; immediately invalidate old device keys and pending physical approvals; migrate only encrypted, typed records, never raw browser secrets; preserve an audit trail of what moved and what was discarded.
- **missing:** device identity registry and revocation endpoint (device status discovery currently has no demonstrated /v1/devices/status route); hardware-backed key and monotonic counter provisioning on pendant; encrypted, resumable migration for OUTBOX/INBOX and settings; replacement binding that integrates the existing physical_transaction_approval_latch

### ""Undo the last change you made on that website, but only if you can prove it is the same account, record, and action—and stop if undo would delete or send anything else.""
- **useful because:** Mac undo explicitly does not cover browser actions, while browser work can change subscriptions, forms, settings, or records. The owner needs a browser-specific compensating action with identity binding, preview, physical approval where needed, and postcondition proof instead of an unsafe generic back button.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → relay
- **model tier:** background planner for site-specific compensation; deterministic identity and postcondition checks; realtime only for the spoken result
- **latency:** 2-4 seconds to inspect and preview; up to 20 seconds for a multi-step compensation
- **cost:** <$0.02; browser inspection is local, with model cost only for ambiguous compensation planning
- **security:** Never infer that navigation equals undo. Bind to the original command receipt, account/session, record identifier, and before/after evidence; require physical approval for deletion, messaging, purchases, or other irreversible compensation; if no safe inverse exists, say so.
- **missing:** browser receipts with before-state and after-state evidence; a catalog or planner for site-specific compensating actions; a browser-side transaction/rollback checkpoint for supported sites; a confirmation path connected to physical_transaction_approval_latch


## Changes it proposed to its own stack

### `browser-harness` — Add a typed browser verification receipt contract: every inspect/result response must carry commandId, bound tab/session, pre-state digest, final URL, redacted evidence selectors, observed state digest, and an explicit proven|not_proven|blocked verdict. Reject receipts that lack tab affinity or that arrive after the command lease.
- **owner gets:** The pendant can honestly say whether a web task was completed instead of trusting a green command response that may have acted in the wrong tab or stopped before the final state.
- effort: Medium: extension result schema, Mac route validation, tests for wrong-tab, stale-lease, redirect, and partial completion.  ·  risk: Existing extension versions may not understand the envelope; negotiate a version and retain the old result as untrusted rather than silently accepting it.
- cost: No meaningful API cost; small local CPU/storage increase for digests and redacted evidence.  ·  latency: Adds under 100 ms locally and one deterministic verification step.
- security: Improves least privilege by binding evidence to a tab; selectors and page text must be redacted before leaving the browser.
- depends on: owner must decide which page fields are safe to expose; browser result route must be inventoried and corrected where the route table/GET probing currently disagree

### `relay` — Create a single cross-surface turn/event envelope keyed by sessionId, turnNonce, and monotonic sequence, with append-only receipts for captured, transcribed, planned, executed, delivered, and played. Add bounded leases and a requeue sweep for relay jobs, and make duplicate sequence append idempotent.
- **owner gets:** When the link or Mac dies, the system can resume the missing part and explain exactly what happened, rather than losing a turn or speaking the same answer twice.
- effort: Large: D1 schema migration, lease worker, receipt joins, USB/LTE handoff integration, and fault-injection tests.  ·  risk: A bad lease could execute work twice; use compare-and-set, expiry, and an explicit unknown state that stops rather than guesses. Expired audio must be discarded, not replayed.
- cost: Low storage and worker CPU; bounded receipt retention required. No extra model calls on a successful path.  ·  latency: Negligible steady-state; 1-2 seconds recovery overhead.
- security: Opaque IDs and redacted metadata only; no raw audio in event history unless the existing failure-buffer policy permits it.
- depends on: usb_fallback_audio_session; audio_delivery_ack_queue; duplex_audio_congestion_guard; orchestrator closeLedger call before any automatic resume

### `memory` — Implement a user-visible data lineage and erasure index: every captured or generated artifact receives an opaque lineage ID, parent/derived IDs, storage locations, sensitivity class, retention deadline, and deletion state. Expose a dry-run deletion graph before confirmation and signed receipts after each surface converges.
- **owner gets:** The owner can finally answer 'where did this go?' and remove one conversation or recording without guessing which copies exist. It converts privacy from a trust claim into a checkable operation.
- effort: Large: instrument capture, pipeline, job, browser, relay, and pendant spool writers; add tombstone propagation, retention sweeps, and a redacted owner-facing view.  ·  risk: Incomplete instrumentation could create false confidence. Unknown/unindexed artifacts must force a not-complete result; migration needs a backfill marker rather than pretending historical data is covered.
- cost: Moderate local/relay storage for metadata; no recurring model cost. Retention sweeps add small background CPU.  ·  latency: Normal operations add one metadata write; deletion planning may take seconds for a large lineage graph.
- security: The index itself is sensitive and must contain opaque IDs and hashes rather than transcripts or page contents; protect it separately from artifact payloads.
- depends on: owner retention/deletion policy; content-addressed artifact inventory; relay tombstone propagation; pendant OUTBOX selective erase and signed receipts


## What it asked for

_Nothing._
