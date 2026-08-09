# Harness derivation — unified — round 195

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live audio delivery state** — Mac and relay are healthy with Accessibility and Screen Recording granted, but the newest pipeline includes a processing pendant bookmark and an older 24 kHz run whose TTS completed while bridge result reporting failed 500; playback remains unproven (heard=unknown, provesPlayback=false).
  - evidence: GET /ops/snapshot returned ready=true, relay reachable, browser online; GET /pipeline returned job_560f7a08... with 471820-byte 24000 Hz PCM, then 'Failed to report bridge work result (500)' and no device_playback event.

## Capabilities it proposed

### "“Before I trust this call, run a quiet end-to-end audio health check, repair anything safe, and tell me whether the next conversation is reliable.”"
- **useful because:** The live system recently rendered 24 kHz PCM but failed to prove bridge playback. This gives the owner a single honest readiness verdict instead of treating relay success as hearing. It combines read-only diagnosis, bounded fault testing, safe repair, and a final validator, while refusing to claim success when playback is unknown.
- **path:** pendant → relay → mac-bridge → mac-planner
- **model tier:** background for routine checks; realtime only to explain the final verdict during a live conversation
- **latency:** 15–30 seconds for a normal check; up to 2 minutes when running a short injected-loss test. Never block an already active call without explicit request.
- **cost:** Low API cost: mostly local HTTP/tool calls and synthetic audio; one short fault-injection run dominates device time, not model tokens.
- **security:** Synthetic test audio only; no owner speech leaves the device. Repair must be limited to idempotent bridge wake/restart actions, with a receipt and explicit degraded result if playback cannot be proven.
- **missing:** A small orchestration route that sequences incident_diagnostics, fleet_health_and_repair, audio_link_fault_inject, and audio_pipeline_validate; A typed readiness report with HEALTHY/DEGRADED/FAILED and per-direction evidence; A bridge playback acknowledgement that can turn unknown hearing into a measured result

### "“Forget what you inferred about my [person/place/preference], show me every copy first, then erase it everywhere you can and tell me what is still pending.”"
- **useful because:** The owner cannot currently see extracted facts, yet those facts can exist in facts.json, the context graph, evidence capsules, and replicated relay data. A recognizable preview-and-erase flow makes the retention policy real: exact matching records are shown, the owner confirms one target, local derivatives are removed, remote deletion is tracked as pending rather than falsely reported complete, and action history remains intact.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** background for candidate discovery and deduplication; realtime only for the owner's explicit spoken confirmation
- **latency:** Preview within 3 seconds locally; erase receipt within 10 seconds locally. Remote replicas may remain pending and must be surfaced on the next check.
- **cost:** Low-to-moderate model cost for matching natural language to candidate facts; storage and deletion calls dominate, not generation.
- **security:** Require physical_transaction_approval_latch or an equivalent deliberate confirmation for destructive erasure. Never delete job audit history by default. Redact evidence in spoken output; expose full capsules only in the authenticated dashboard. Refuse ambiguous matches rather than broad-delete.
- **missing:** A read-only fact inventory that joins facts.json, context-graph entities/relations, derived copies, and evidence capsules by provenance; A transactional erase operation with a tombstone/idempotency key and remote pending state; A user-facing preview route and a convergence receipt proving local deletion without claiming immediate D1/R2 deletion

### "“Pick up the unfinished thing from before the outage, but do not repeat anything that may already have happened; show me what you will resume and ask only where the evidence is ambiguous.”"
- **useful because:** Today the durable resume engine exists but nothing invokes it safely: ordinary ledgers remain open, every run can look interrupted, and relay jobs can remain processing after a Mac outage. This turns crash recovery into a user-visible capability that prefers idempotent/additive steps, blocks unrepeatable or unknown steps, and gives a concrete handoff instead of silently duplicating emails, browser submissions, or file edits.
- **path:** relay → mac-planner → browser-extension → pendant
- **model tier:** background deterministic planner for ledger classification and handoff; realtime only when the owner asks what is safe to resume
- **latency:** Under 2 seconds to present a dry-run for local ledgers; under 10 seconds to reconcile relay/browser leases. Execution remains stepwise and receipt-backed.
- **cost:** Very low model cost when driven by the existing decision engine; engineering cost is in wiring durable callers, lease expiry, and owner approval delivery.
- **security:** Auto-resume only replaySafety idempotent/additive with valid lease and matching plan/world fingerprints. Any unrepeatable/unknown or irreversible-write step requires deliberate physical approval in a later conversation. Never replay a browser command without its idempotency evidence. Keep audit history even when a task is abandoned.
- **missing:** Call closeLedger on every ordinary orchestrator completion and repair stale inflight semantics; A startup/owner-triggered caller for planResume/resumeLedger that does not execute blindly; relay_jobs lease_until plus expiry/requeue sweep, and a browser supervisor sweep that actually runs; A durable handoff view joining ledger step receipts, workbench context state, relay job status, and browser command lease state; A next-conversation approval inbox using the existing pendant transaction latch

### "“Use the logged-in site to do this, but do not send page contents, credentials, or personal records to the relay or model; tell me only the minimum result and require my pendant for the final step.”"
- **useful because:** The browser is the only node that can reach private sessions, but today a browser task can expose page text to the planning path without an owner-verifiable data boundary. A local data diode would let the system act on banking, health, travel, and work sites while returning only an approved schema (for example, availability, total, or success/failure). The pendant's deliberate approval would be bound to the exact final state, not to a vague request.
- **path:** browser-extension → mac-planner → relay → pendant
- **model tier:** Local deterministic extraction and policy enforcement first; background model only for an explicitly permitted, redacted summary. Realtime is unnecessary except for the owner's conversation.
- **latency:** Under 5 seconds for read-only results; final submission remains stepwise and waits for physical approval. A page that cannot be safely reduced to the approved schema must stop rather than fall back to raw extraction.
- **cost:** Low recurring token cost because raw page content stays local; engineering cost is primarily policy testing and browser-extension enforcement.
- **security:** The relay must receive neither DOM text nor screenshots for protected targets. Maintain per-origin data classes, redact logs and receipts, bind an output hash to the page/session and final action, and fail closed on unrecognized fields or navigation. Physical_transaction_approval_latch is required for side effects; local_privacy_latch must be able to abort the flow.
- **missing:** A browser-extension local extraction sandbox that returns typed fields rather than arbitrary page text; A destination and field-level egress policy with fail-closed enforcement before relay submission; A cryptographic receipt proving the returned fields came from the bound tab and that the approved final state was unchanged; A protected-target test suite covering navigation, screenshots, clipboard, logs, and error messages

### "“I’m traveling in [place/time zone]. Keep my Mac-timed routines predictable, but speak and label personal times in my declared local zone until I clear it.”"
- **useful because:** Today the system correctly refuses to infer a pendant timezone, but it offers no explicit travel handoff. The owner should not have to choose between silently shifting routines and receiving misleading ‘this morning’ times. A declared travel capsule would preserve Mac-zone firing as the invariant, add the owner's temporary local zone only for presentation and relative-time interpretation, and make every spoken time identify which zone it uses.
- **path:** pendant → mac-planner → relay → browser-extension
- **model tier:** Deterministic state and timezone conversion; no expensive model required except natural-language confirmation.
- **latency:** Immediate acknowledgement and under 1 second for conversions. The capsule should expire or require renewal, never silently persist forever.
- **cost:** Negligible API cost; implementation is state, conversion, UI labels, and receipt tests.
- **security:** Location is sensitive: store only the declared IANA zone and expiry, not coordinates. Require explicit owner confirmation to set or clear it. Never infer it from IP, browser locale, or pendant clock. Routine execution must remain bound to the Mac zone unless separately edited.
- **missing:** A durable, authenticated travel-zone capsule shared by Mac and relay; Owner-facing labels that carry source zone on spoken and browser-visible times; Expiry/renewal and conflict handling when a capsule disagrees with an existing routine or calendar zone; Tests proving zoneless pendant timestamps remain null instants rather than being backfilled

### "“Give this one task permission to use only the named app and tab for the next ten minutes, then revoke it automatically; show me exactly what authority it had.”"
- **useful because:** The current system has one broad bearer credential and broad agent control, so approval records audit an action but do not create a least-privilege boundary. A scoped delegation passport would let the owner safely hand off a bounded task across relay, Mac, and browser, with origin/app/action limits, expiry, revocation, and a final authority receipt. It is useful even when the task is reversible because it limits what a compromised or mistaken planner can reach.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Deterministic policy engine and token verifier; background model may translate the owner's request into a proposed scope, but must never widen it.
- **latency:** Scope preview in under 2 seconds; token issuance after physical confirmation in under 1 second; revocation should propagate within 2 seconds.
- **cost:** Low token cost; the main cost is implementation and exhaustive negative testing of scope escapes.
- **security:** Use audience-bound, nonce-bearing, short-lived capabilities rather than the global AGENT_TOKEN. Bind to exact browser session/tab, Mac action classes, destination origins, and maximum side-effect count. Deny by default on navigation, clipboard, screenshots, shell, or new tabs unless separately granted. Physical_transaction_approval_latch authorizes issuance, and local_privacy_latch revokes all active passports. Store only hashes and redacted receipts.
- **missing:** A least-privilege capability-token verifier shared by relay, Mac executor, and browser extension; Per-command scope enforcement and automatic revocation at every boundary, not only at plan creation; A pendant-readable scope summary and revocation event path; Adversarial tests for confused deputy, tab replacement, origin changes, retries, and expired-token replay


## What it asked for

_Nothing._
## Its own summary

I discovered the newly available grant set and recorded three non-duplicate capabilities: (1) a one-command audio readiness check that diagnoses, safely repairs, fault-tests, and validates the 24 kHz path; (2) owner-controlled preview-and-erase for inferred facts with provenance and pending remote deletion; and (3) safe interrupted-task recovery keyed to replaySafety rather than reversibility. Live state is healthy at the Mac/relay permission level, but the latest pipeline still has a 500 while reporting bridge work and no device_playback event, so hearing remains unproven.

**Biggest unknown:** I still need a real bridge/device playback acknowledgement correlated to a pipeline or job ID, plus typed implementations for remote fact-erasure convergence and durable resume orchestration. Without those, I can diagnose and report, but cannot honestly prove audio was heard, that an inferred fact was erased off-machine, or that a recovered action will not duplicate an unrepeatable side effect.

