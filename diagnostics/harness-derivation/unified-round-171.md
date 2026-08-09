# Harness derivation — unified — round 171

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio pipeline validation** — The latest completed pipeline job_309f5663-e01a-4f8a-b798-319c7c18313f has a stored output WAV with a valid RIFF/WAVE header, mono 16-bit PCM at 24,000 Hz (header bytes show 0x5dc0), but no stored input WAV. The validator tool currently cannot perform its requested checks: it fetches raw bytes and returns 404 for input; its directions=['both'] mapping incorrectly calls the route with /both.
  - evidence: GET /pipeline and audio_pipeline_validate calls for job_309f5663-e01a-4f8a-b798-319c7c18313f input/output

## Capabilities it proposed

### "“What did I miss while I was offline or not wearing the pendant?” Give me one spoken, prioritized digest of actions, alerts, commitments, and failures since my last acknowledgement, and let me say “handle the safe ones.”"
- **useful because:** The owner currently has to know which surface to query after a link drop or sleep. This turns fragmented relay receipts, Mac jobs, browser results, pendant inbox items, and commitment evidence into a single honest recovery moment, while separating observed facts from actions that still need approval. It is the highest-value cross-surface behavior because it preserves continuity when the owner was physically absent.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for digest construction; realtime only to answer the spoken follow-up
- **latency:** Initial digest within 5 seconds of the next conversation; safe-action execution remains explicit and can take longer.
- **cost:** About $0.01–$0.05 per digest depending on event volume; deterministic grouping and receipt joins dominate, with a small background model call for concise wording.
- **security:** Only query events since an owner acknowledgement cursor; redact page contents and secrets by default; bind every item to a provenance receipt and require fresh physical approval for off-machine, irreversible, or unrepeatable actions. “Handle the safe ones” must never authorize browser submission or messaging.
- **missing:** A durable cross-surface acknowledgement cursor and digest record; A typed join that correlates pendant inbox, relay jobs, Mac receipts, browser command results, and commitment evidence; A safe-action batch planner that uses replaySafety and riskTier, not reversibility alone; Relay-side persistence for approval handoff and a next-conversation delivery path

### "“Am I private right now?” Return a short spoken answer and a verifiable receipt proving the pendant mic/playback, relay persistence, queued jobs, Mac capture, and browser exposure are all stopped; if they disagree, name the exact surface instead of saying yes."
- **useful because:** A physical latch gives immediate local protection, but the owner cannot currently know whether buffered audio, a relay job, or a browser/Mac capture path remains active. A read-only convergence answer makes privacy a checkable state rather than a reassuring LED.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** realtime for the short answer; deterministic checks and signing do the actual work
- **latency:** Under 1 second when the link is healthy; return partial evidence within 3 seconds if a surface is unreachable.
- **cost:** Near-zero model cost for normal checks; one short realtime turn only when the owner asks.
- **security:** The receipt must be authenticated, freshness-bound to a latch ID, and fail closed: unreachable or unknown is not private. Do not include audio, page contents, or tokens. A mismatch should offer only safe local actions unless the owner explicitly confirms repair.
- **missing:** An authenticated pendant-origin latch state and monotonic event counter exposed to the verifier; A single cross-surface privacy state schema with freshness/unknown semantics; A relay endpoint that signs the convergence receipt and records no raw audio

### "“Are any of my devices or accounts disagreeing about this?” Compare the bound browser pages, Mac state, relay records, and pendant events for one topic, identify contradictions with citations, and tell me which source is authoritative without changing anything."
- **useful because:** Today each surface can report a locally plausible state while the owner has no way to notice that they conflict—for example, a browser form still open after a Mac job failed, or a relay receipt claiming delivery while the pendant never played it. A contradiction report prevents confident but wrong answers and makes the hive behave as one instrument.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background deterministic reconciliation first; realtime only to explain the resulting contradiction briefly
- **latency:** Under 4 seconds for up to 20 bound records; return a partial result with explicit unknowns when a surface is unavailable.
- **cost:** Usually under $0.03; hashes, timestamps, and typed state comparison should do most of the work, with a small model call only for human wording.
- **security:** Search only owner-bound tabs/apps and explicitly named records; redact page contents and secrets; preserve source timestamps and do not silently choose a winner. This is read-only and must never trigger a repair or submission.
- **missing:** A typed cross-surface state vocabulary with conflict and unknown outcomes; A provenance-preserving join keyed by job, commitment, artifact, or conversation ID; An owner-configurable authority map for categories such as calendar, browser submission, relay delivery, and physical playback

### "“Forget this conversation everywhere.” Show me exactly which copies exist on the pendant, relay, Mac, and bound browser, delete only the selected records, and return a signed deletion receipt listing any copy that could not be removed."
- **useful because:** The owner currently cannot verify whether a spoken exchange survives in relay jobs, browser state, Mac artifacts, audio pipeline files, or pendant failure storage. A scoped erasure operation would make the privacy boundary operational instead of trusting undocumented retention behavior.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic inventory and deletion; realtime only for confirmation wording
- **latency:** Inventory within 5 seconds; deletion and receipts may continue asynchronously but must report each surface separately.
- **cost:** Low model cost; storage enumeration, secure deletion, and receipt signing dominate.
- **security:** Require an explicit scope and fresh physical confirmation; never infer that “this” means all history. Preserve only a minimal tombstone and deletion receipt, not content. If a browser or relay copy is unreachable, report it as not verified rather than claiming deletion.
- **missing:** A cross-surface retention inventory keyed to conversation/artifact IDs; Typed deletion operations for relay, Mac, browser, and pendant outbox/inbox records; A signed, append-only deletion receipt with unknown/unreachable outcomes; An owner-defined retention and legal-hold policy

### "“Before you do that, show me the world after it succeeds and after it fails.” Produce a counterfactual preview of every Mac, browser, relay, and pendant state change, including what can be undone, what cannot, and what evidence would prove completion—without executing anything."
- **useful because:** Current planning and approval surfaces describe individual actions but do not give the owner a unified before/after model. For a multi-surface request, the owner should understand consequences and completion criteria before committing, especially when one surface can succeed while another remains stale.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background planner for the counterfactual graph; realtime only when the owner asks for a short spoken summary
- **latency:** Under 6 seconds for a plan of up to 20 steps; no side effects during preview.
- **cost:** Approximately $0.02–$0.08 for complex plans; deterministic state fingerprints and action metadata reduce model work.
- **security:** Preview must be read-only and must not fetch unrelated page contents or secrets. Mark assumptions and unknown external effects explicitly. Bind the eventual execution to the preview digest so a changed world invalidates it.
- **missing:** A cross-surface effect graph and state-diff schema; Dry-run adapters for browser submissions, Mac actions, relay delivery, and pendant playback; A completion-evidence contract tied to each predicted effect; Digest invalidation when the world or plan changes


## Changes it proposed to its own stack

### `relay` — Ship a crash-recovery coordinator for action jobs: close ordinary ledgers when plans settle, add lease_until/claimedAt expiry and a requeue sweep to relay_jobs, then on Mac/browser reconnect evaluate each interrupted step with the existing planResume engine. Auto-retry only replaySafety=idempotent or additive steps; mark unrepeatable/unknown steps awaiting the next spoken conversation and physical_transaction_approval_latch. Emit one recovery receipt per decision and never infer success from a lost connection.
- **owner gets:** A dead Mac, browser bridge, or modem currently leaves work appearing unfinished or stuck for hours and gives the owner no trustworthy answer. This makes safe work recover itself after an outage and turns risky work into a clear, resumable question instead of silently duplicating a message, purchase, or edit.
- effort: Medium-high: ledger close integration, D1 schema/migration and sweep, reconnect trigger, decision receipts, and end-to-end fault tests across relay, Mac, and browser.  ·  risk: A false idempotency classification could repeat an external action; default unknown to blocked and require approval. Lease expiry could requeue a genuinely running job, so use a heartbeat grace period and idempotency keys. Recovery is observable and cancellable, with no automatic execution for browser submissions or communications.
- cost: Small relay storage and one periodic D1 sweep; background planner/model cost near zero because planResume is deterministic.  ·  latency: Normal jobs unchanged; after reconnect, safe recovery begins within one lease sweep (target under 60 seconds).
- security: Improves auditability; preserves least privilege by separating recovery decisions from approval and binding every retry to the original plan digest, world fingerprint, and idempotency key.
- depends on: orchestrator closeLedger call; relay_jobs lease_until schema and requeue sweep; startBrowserBridgeSupervisor invocation; relay implementation of approvalHandoff storage; physical_transaction_approval_latch delivery path


## What it asked for

_Nothing._
