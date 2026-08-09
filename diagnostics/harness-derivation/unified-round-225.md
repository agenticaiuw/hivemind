# Harness derivation — unified — round 225

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What does this system remember about me, show me the source, and forget this one fact everywhere.”"
- **useful because:** The system currently extracts facts into hidden stores the owner cannot inspect. This gives the owner a voice-first, evidence-backed control surface: list only recognisable extracted facts, show provenance, and erase the fact plus derived copies while preserving action audit history.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic retrieval/redaction first; background model only to group or explain evidence, never to decide deletion.
- **latency:** List under 2 seconds; provenance under 3 seconds; deletion receipt under 5 seconds locally, with off-machine deletion explicitly pending.
- **cost:** ~$0.001–$0.01 per request; dominated by optional evidence summarization, not storage queries.
- **security:** Only facts explicitly classified as extracted-memory are mutable; action/job history is excluded. Require physical_transaction_approval_latch for deletion, authenticate relay erase by fact ID and version, and return a receipt distinguishing local-complete from off-machine-pending.
- **missing:** A typed extracted-fact index with stable fact IDs and provenance capsules; A single erase fan-out across facts.json, context graph, relay copies, and derived projections; A pendant spoken list/confirmation flow and dashboard view

### "“I approved that staged action on the pendant—finish it safely, or tell me exactly why it is waiting.”"
- **useful because:** The system can stage and physically approve a transaction, but the relay half of approval persistence and spoken delivery is not closed, while blocked plans are currently spoken about and discarded. This makes approval a real end-to-end affordance: resume only idempotent/additive work, require a fresh next-conversation confirmation for risky work, and never replay an unrepeatable step.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic ledger/replay engine; planner model only for human-readable explanation of a blocked step.
- **latency:** Physical approval acknowledgement under 1 second when linked; execution begins within 2 seconds; stale or ambiguous work returns a reason rather than retrying.
- **cost:** ~$0.001–$0.02 per transaction; model cost only for explanation.
- **security:** Bind approval to plan digest, world fingerprint, nonce, expiry, and replaySafety. Treat idempotent/additive steps as resumable; block unrepeatable/unknown steps. Keep approval separate from execution credentials if possible and preserve receipts.
- **missing:** Relay implementation of APPROVAL_STORE_CONTRACT and delivery/readback bookkeeping; Orchestrator closeLedger calls so completed plans are not falsely interrupted; relay_jobs lease_until and requeue sweep; A pending-approval queue surfaced at the owner’s next conversation

### "“My voice sounds broken—run a safe diagnosis across the pendant, relay, Mac, and bridge, then tell me whether to continue, degrade, or stop.”"
- **useful because:** Voice quality failures span modem loss, relay jobs, codec timing, and bridge playback; no single node can identify the fault. This turns existing read-only diagnostics, pipeline validation, and controlled fault injection into an owner-facing verdict with measured evidence and a safe recommendation.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic checks and thresholds for verdict; background model summarizes the evidence in plain language.
- **latency:** Healthy-path diagnosis under 10 seconds; fault-injection mode explicitly opt-in and under 60 seconds.
- **cost:** ~$0.002–$0.03; dominated by optional summarization and artifact retention.
- **security:** Default read-only; fault injection must require explicit confirmation because it intentionally drops packets. Do not retain raw audio unless the owner asks; redact identifiers in cross-surface reports.
- **missing:** A correlation ID shared by audio runs, relay jobs, and bridge receipts; A stable HEALTHY/DEGRADED/FAILED policy over existing numeric acceptance criteria; Owner-facing recommendation and escalation UI

### "“Why do you believe that? Give me the exact source, timestamp, and what would make it stale.”"
- **useful because:** A unified agent should distinguish observation from inference instead of presenting hidden context as fact. This lets the owner challenge any spoken answer and receive a compact, cross-surface evidence capsule from the pendant event, relay receipt, Mac job, or bound browser tab, with freshness and contradiction status.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic provenance lookup and freshness/contradiction checks; a cheap background model may phrase the capsule, while the realtime model only handles the spoken exchange.
- **latency:** Common claims under 2 seconds; multi-source reconciliation under 5 seconds; if evidence is unavailable, say so rather than fabricate a citation.
- **cost:** ~$0.001–$0.02; mostly lookup, with model cost only for natural-language synthesis.
- **security:** Search only bound browser tabs/apps and authenticated relay records. Redact secrets and page contents by default, expose snippets only after owner request, and never treat model-generated summaries as provenance.
- **missing:** A stable claim/evidence ID attached to spoken assertions; Cross-surface freshness and contradiction scoring; A spoken ‘challenge this claim’ interaction and dashboard evidence viewer

### "“Do this across my browser and Mac as one operation; if any part fails, leave everything as it was—or show me the exact partial result and the one-step recovery.”"
- **useful because:** Today a browser submission and a Mac-side write can each succeed independently, leaving the owner with a half-completed task and no unified recovery. A cross-surface transaction would make composite actions trustworthy: stage all effects, execute in dependency order, verify each receipt, compensate successful reversible steps on failure, and expose an explicit partial state when compensation is impossible.
- **path:** relay → mac-bridge → browser → dashboard → pendant
- **model tier:** Deterministic transaction coordinator and receipt verifier; planner model only decomposes the request and explains an unrecoverable partial outcome.
- **latency:** Preview under 3 seconds; execution begins after approval and reports each committed boundary within 2 seconds; compensation starts immediately on failure.
- **cost:** ~$0.003–$0.03 per operation; dominated by planner context and browser/Mac verification, not the coordinator.
- **security:** Each step needs an effect scope, idempotency key, compensation rule, and before/after fingerprint. Never claim rollback for email, messages, external submissions, or other unrepeatable effects. Require physical approval for the whole transaction when any step is off-machine or irreversible; retain an immutable audit trail without retaining secrets.
- **missing:** A durable cross-surface transaction manifest with commit barriers and compensation states; Browser receipts that expose success/failure and reversible scope, joined to Mac action receipts; A coordinator that can pause before an external side effect and resume without replay; Owner-facing partial-commit and recovery controls

### "“For this conversation, show me exactly where my words and files went, what was retained, and erase the temporary copies when we finish.”"
- **useful because:** The owner has a physical privacy latch, but no owner-facing inventory of conversation data crossing pendant, relay, Mac, browser, caches, and queued jobs. A per-conversation data-flow receipt makes privacy observable rather than a promise and distinguishes deleted, retained-for-audit, and deletion-pending records.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic data-lineage and retention accounting; no model is needed to decide what exists or whether deletion completed.
- **latency:** A live retention summary under 3 seconds; final receipt within 5 seconds of conversation end; remote deletion may remain explicitly pending.
- **cost:** ~$0.001–$0.01 per conversation; storage indexing dominates.
- **security:** Receipts must contain hashes, classes, destinations, and retention states—not raw audio or secrets. Deletion must preserve action accountability while removing conversational payloads, and remote replicas must report pending rather than falsely claiming completion.
- **missing:** Per-conversation lineage IDs attached to audio, transcripts, relay rows, browser commands, and Mac artifacts; A retention class and expiry on every temporary artifact; A convergence receipt covering deletion and remote replication

### "“For this conversation, allow only these apps and tabs, observe rather than act unless I approve, and make the boundary impossible to cross silently.”"
- **useful because:** The owner needs a temporary, explicit security boundary for real-world use—such as banking, healthcare, or a confidential meeting—that spans the pendant, relay, Mac, and authenticated browser. This is stronger than muting audio: it constrains what the agent may see, where it may send data, and which action classes are permitted until the boundary expires.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic policy enforcement and capability checks; realtime model only interprets the owner’s spoken scope into a reviewable policy.
- **latency:** Boundary acknowledgement under 1 second; every attempted out-of-scope read or action rejected locally before dispatch.
- **cost:** ~$0.002–$0.02 per boundary; mostly policy evaluation and receipt storage.
- **security:** Default deny, short expiry, explicit target bindings, and a physical pendant confirmation for changes. The relay must enforce the boundary rather than trusting model instructions. Log rejected attempts without logging sensitive content.
- **missing:** A signed conversation-scoped capability lease shared by relay, Mac, and browser; Pre-dispatch enforcement for reads as well as writes; A pendant-visible active-boundary state and expiry warning; A deterministic policy editor with preview of allowed and denied operations


## What it asked for

_Nothing._
