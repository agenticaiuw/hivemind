# Harness derivation — unified — round 271

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I approved that staged action on the pendant—finish it now, but only if the exact plan and files are still the ones I approved.”"
- **useful because:** The physical approval latch exists, and the Mac approval verifier already binds a grant to plan digest, world fingerprint, nonce, expiry, and delivery. The missing end-to-end loop means a deliberate offline approval currently has nowhere durable to land and no safe continuation on the next conversation. This would turn the pendant’s one physical gesture into a real, replay-resistant action without allowing an unsolicited interruption.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** deterministic verifier/executor; realtime model only phrases the pending/accepted/refused status
- **latency:** On reconnect, receipt and revalidation under 2 s; execution starts only after the next owner interaction or explicit dashboard action
- **cost:** <$0.005 per approval/resume; D1 writes and cryptographic digest/world checks dominate, not model tokens
- **security:** Persist the approval record by transaction nonce with TTL, monotonic counter, plan digest, world fingerprint, and cancel state. Revalidate before execution; refuse changed plan/world, expired nonce, duplicate counter, or missing spoken delivery. The pendant receives no secrets and never submits. Keep approval and execute credentials separated when possible.
- **missing:** relay implementation of APPROVAL_STORE_CONTRACT and an inbox delivery frame; consumer that binds physical_transaction_approval_latch events to /approve; next-conversation or dashboard continuation that invokes the verified runnable steps; relay_jobs lease_until/requeue sweep and orchestrator closeLedger prerequisite

### "“Continue the conversation exactly where it stopped—don’t repeat audio I already heard, and tell me what was completed.”"
- **useful because:** A relay, Mac restart, browser outage, or audio link loss can leave text/action state and physical playback at different boundaries. The owner needs one honest continuation that joins durable work handoff with device playback acknowledgements, skips already-heard ranges, and clearly labels anything that was only generated versus actually heard.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** deterministic reconciliation for sequence ranges, receipts, and idempotency; background model summarizes the recovered turn only when needed
- **latency:** Recovery verdict under 2 s; resume audio begins at the next unacknowledged 60 ms frame within 1 s after confirmation
- **cost:** <$0.01 per recovery; storage reads and range reconciliation dominate, with optional short summary generation
- **security:** Use opaque turn/artifact IDs, monotonic frame ranges, checksums, and deduplication. Never infer that acceptance means hearing. Preserve the audit trail; expose only the owner’s conversation. Require confirmation before replaying potentially sensitive audio after a long outage.
- **missing:** a cross-surface join between workbench handoff, relay job state, pipeline audio, and device playback receipts; an idempotent resume endpoint that selects the first unacknowledged frame range; a durable turn-boundary record shared by relay and Mac after crashes

### "“I was offline for a while. Give me one trustworthy digest of what changed, what is still pending, and what needs my decision—without replaying old notifications.”"
- **useful because:** The relay, Mac, browser, and pendant can each retain partial history, but the owner currently has to ask each surface separately and cannot distinguish completed work from queued or merely attempted work. A causal offline-gap digest would make reconnection useful instead of noisy: deduplicate events, collapse superseded states, and surface only decisions and failures.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic event compaction and state joins first; background model only turns the compact result into natural language
- **latency:** First compact status under 2 s from cached cursors; full digest under 8 s; no unsolicited interruption—deliver on the next conversation or button request
- **cost:** <$0.01 per digest; event reads and deduplication dominate, with model cost limited to a short final summary
- **security:** Scope by owner/session and a caller-provided since cursor; redact browser page contents and secrets; distinguish observed, attempted, completed, and pending. Keep an immutable audit reference behind each sentence and require confirmation before taking any suggested action.
- **missing:** a durable per-surface acknowledgement cursor and causal event IDs; a reducer that merges relay jobs, Mac receipts, browser results, pendant inbox, and audio acknowledgements without double-counting; an owner-facing digest view and a next-conversation delivery hook

### "“For the next conversation, keep everything ephemeral: do not remember, index, or expose it to the browser, and prove when the temporary boundary has ended.”"
- **useful because:** The existing privacy latch stops capture/playback, but it does not give the owner a deliberate, scoped mode for speaking while the system is listening yet preventing derived facts, evidence capsules, browser exposure, and routine retention. A time- and turn-bounded ephemeral conversation would let the owner use the assistant for sensitive topics without trusting an invisible deletion promise afterward.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic policy enforcement and deletion receipts; realtime model only acknowledges entry/exit and answers within the session
- **latency:** Enter boundary locally within one button action; enforcement receipt under 1 s; exit/convergence proof under 3 s; no model round trip required to stop persistence
- **cost:** <$0.01 per session; dominated by bounded metadata and deletion verification, with no background extraction/indexing during the session
- **security:** The boundary must be enforced before microphone frames are accepted, not inferred after transcription. Relay must reject durable audio/evidence writes and browser commands while active; Mac must avoid context-graph/facts extraction and redact logs. Keep only a minimal tamper-evident session receipt (timestamps, policy version, sequence counts), never content. On exit, verify capture, playback, queues, browser exposure, and derived-memory writes are stopped or absent; require explicit confirmation before extending the boundary.
- **missing:** a signed ephemeral-session policy token propagated from pendant to relay and Mac/browser; write-path enforcement in capture, pipeline, evidence, facts/context-graph, browser spool, and job logging; a bounded session TTL with crash-safe default-deny behavior and a convergence receipt distinct from the existing privacy latch; dashboard and spoken controls to start, extend, end, and inspect the boundary

### "“Tell me what you tried to do but could not do because a permission, device, browser session, or link was unavailable—and what I can safely do about each.”"
- **useful because:** Today failures are scattered across Mac jobs, browser commands, relay status, and pendant link state; the owner often hears a vague failure or waits indefinitely without knowing whether anything happened. A bounded blocked-work report would distinguish not-started, partially completed, and completed actions, explain the exact missing capability, and offer a safe recovery path without rerunning side effects blindly.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic receipt/status correlation and health diagnosis; background model summarizes and groups failures, with realtime only for the spoken answer
- **latency:** Cached report under 2 s; correlated evidence and repair plan under 6 s; no automatic repair or rerun without owner confirmation
- **cost:** <$0.01 per report; reads and correlation dominate, with model generation limited to a short grouped explanation
- **security:** Expose only the owner's jobs and redact URLs, page contents, tokens, and file data. Label evidence versus hypothesis. Repairs must be dry-run first, idempotent where possible, and separately confirmed; never treat a permission prompt or stale lease as authorization to execute the original action.
- **missing:** a durable blocked/outcome taxonomy shared by relay, Mac, browser, and pendant; correlation of job receipts with browser command leases, health snapshots, and audio/device state; owner-facing repair plans that link each blocked item to an explicit confirmation and a post-repair revalidation receipt


## Changes it proposed to its own stack

### `relay` — Add an expiring lease and requeue sweep to relay_jobs, with attempt number, lease owner, lease_until, and a durable handoff marker. A worker claims with compare-and-set, renews while active, and stale processing rows return to queued only when the prior worker's lease has expired. Emit one owner-visible transition receipt so a restarted Mac can continue rather than silently waiting up to the 24-hour TTL.
- **owner gets:** If the Mac, browser bridge, or network dies mid-task, the owner gets completion or an explicit retry instead of a job that appears stuck for a day. It is the prerequisite for honest approval continuation and offline-gap summaries, not a background refactor.
- effort: Schema migration, D1 and memory-store parity, claim/renew/requeue paths, bounded sweep, and crash-injection tests across relay and Mac bridge. Reuse the existing routine lease pattern and integrate with workbench handoff and receipt IDs.  ·  risk: A lease shorter than a legitimate long action can duplicate work; a late worker can race a requeued worker. Require fencing tokens/attempt IDs at every completion, idempotency keys for side effects, and only requeue jobs whose lease is expired. Preserve old rows with a migration default and provide an operator-visible dead-letter state after bounded attempts.
- cost: Negligible model cost; a few D1 columns and periodic reads/writes. Sweep frequency controls small relay CPU/storage overhead.  ·  latency: Recovery becomes seconds-to-minutes (configured lease) instead of the current 24-hour TTL; normal claims add one conditional write and renewal traffic.
- security: Bind leases to authenticated worker identity and never accept completion from a stale attempt. Do not expose secrets in handoff markers; receipts should contain opaque IDs and redacted status only.
- depends on: relay_jobs schema migration; Mac bridge completion fencing and idempotent receipt handling; orchestrator closeLedger so completed plans are not falsely classified as interrupted; workbench handoff integration


## What it asked for

_Nothing._
## Its own summary

Discovered live devices: Safari and home Mac bridge online, iOS probe online, nRF9160 pendant offline. Recorded three cross-surface capabilities: replay-safe physical approval continuation, exact audio/work continuation after interruption, and an offline-gap digest. Also recorded relay job leases/requeue with fencing, which is a direct prerequisite for reliable recovery. A fact-inventory/erase proposal and haptic-feedback hardware proposal were correctly rejected as already present in the backlog; I did not rephrase them.

**Biggest unknown:** The remaining blockers are implementation ownership and live route verification: relay approval persistence/delivery, the next-conversation continuation hook, cross-surface event cursors, and relay lease schema/fencing. I still need those pieces built and tested; I do not need another owner-policy request this round.

