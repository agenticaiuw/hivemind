# Harness derivation — unified — round 238

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Finish this even if my Mac or browser drops: when I reconnect, tell me exactly what completed, ask me only about unsafe steps, and continue the safe remainder.”"
- **useful because:** This is the single most useful missing behavior: a task becomes dependable rather than a one-shot attempt. It uses the relay, Mac, browser, and pendant together, while refusing to replay an unrepeatable action or silently duplicate a send.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic ledger/resume engine first; background model only to summarize the handoff; realtime only for the owner's short status conversation.
- **latency:** Resume decision under 1 s after reconnect; spoken status under 2 s; no model call for the safety decision.
- **cost:** About $0.001–$0.01 per interrupted job, dominated by an optional summary model call; deterministic resume is negligible.
- **security:** Never replay replaySafety=unrepeatable or unknown. Require the existing physical_transaction_approval_latch and next-conversation approval for riskTier irreversible-write/off-machine/uncontained. Bind continuation to plan digest, world fingerprint, lease and idempotency key; show every skipped, rerun and blocked step to the owner.
- **missing:** closeLedger on ordinary orchestrator completion so successful jobs are not falsely marked interrupted; relay job lease_until and expiry/requeue sweep; a production caller that invokes planResume and a durable relay implementation of approvalHandoff; a reconnect/status path that surfaces the handoff on the pendant's next conversation

### "“Show me everything you have inferred about me from this conversation, where each item came from, what copies exist, and let me erase just this one everywhere.”"
- **useful because:** The owner currently cannot see extracted facts although the system can store them. This makes memory honest and controllable: a fact is either recognisable, evidenced and deletable, or it should not persist.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic listing, provenance and deletion cascade; use a cheap background model only to render human-readable labels, never to decide what gets erased.
- **latency:** List in under 2 s locally; acknowledge an erase immediately with local completion and a clearly pending off-machine replication state.
- **cost:** <$0.01 per request; storage/indexing and deletion receipts dominate, not inference.
- **security:** Require explicit confirmation for deletion, scope it to the selected fact plus derived copies and evidence capsule, and preserve job history. Redact raw evidence by default. Relay/R2 deletion must return requested-and-pending until independently acknowledged; never claim instantaneous erasure.
- **missing:** typed fact/provenance listing endpoint; cascade tombstones linking facts to graph entities, derived projections and evidence capsules; relay/R2 erase queue with per-copy receipts and retry status; dashboard and pendant readout for the pending deletion state

### "“Before an important call, test the whole wearable audio path; if it is degraded, tell me whether to proceed, switch profile, or wait—and prove afterward whether the words reached the speaker.”"
- **useful because:** A green relay response is not proof the owner heard anything. A deliberate preflight plus post-call delivery evidence turns audio from hope into a measurable service, especially when simultaneous uplink/downlink loss is present.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic fixture, fault profile and threshold evaluation; background model may turn counters into a short explanation. Do not put a test on every response hot path.
- **latency:** Normal preflight 5–15 s; degraded verdict in under 20 s; post-call receipt updates asynchronously and speaks only on request.
- **cost:** <$0.02 per preflight including relay traffic; storage of compact counters is the main recurring cost.
- **security:** Synthetic audio must be unmistakable and never contain owner speech. Keep fixtures and counters, not raw audio, unless the owner explicitly requests capture. Fault injection must be opt-in and never run during a live call. A fallback recommendation must not silently change profile without confirmation.
- **missing:** one orchestrator that invokes the existing diagnostic fixture and validator as a single owner-facing run; persistent call-level correlation between pipeline ID, pendant playback start/finish and bridge acknowledgement; a policy translating measured loss/jitter/CPU/clipping into proceed/fallback/wait; a compact dashboard/pendant result with a durable receipt

### "“Before I rely on that answer, tell me what you could not observe, which surfaces were stale or inaccessible, and exactly how that uncertainty could change the answer.”"
- **useful because:** Today the hive can produce a confident-sounding result while silently missing the browser session, pendant state, an offline relay, or a permission-gated Mac surface. The owner needs an explicit boundary of knowledge, not merely a health light: a signed, time-bounded negative report saying what was checked, what was unreachable, and which conclusions are therefore unsafe to make.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic evidence/freshness computation across surfaces; use the background tier only to phrase the impact in plain language. Realtime is needed only when the owner asks during a live conversation.
- **latency:** Return the machine-readable observation boundary in under 2 seconds from cached heartbeats; mark live probes separately rather than blocking longer. Spoken summary under 3 seconds.
- **cost:** <$0.005 per request; most cost is a few authenticated health/receipt reads and bounded retention of freshness attestations.
- **security:** Do not reveal browser URLs, page contents, tokens, or private audio in the report. Prove freshness and source identity with signed per-surface attestations; distinguish 'not observed' from 'observed false'; never let an uncertainty summary authorize an action. Require confirmation before probing a sensitive app or page.
- **missing:** a cross-surface observation-boundary record with source identity, timestamp, scope and freshness expiry; browser and Mac attestations that state capability/permission coverage without exposing content; pendant link and sensor-state attestations that survive reconnect and clearly report offline gaps; a planner contract that consumes unknowns as constraints instead of treating missing evidence as success; owner-facing rendering that attaches the uncertainty boundary to every consequential answer, not only explicit diagnostics

### "“Before you send, upload, paste, or submit anything, show me exactly what data would leave my Mac or browser, who would receive it, what was redacted, and let me permit only this one transfer.”"
- **useful because:** The current action boundary is about whether an operation is risky, not about the actual information crossing from a private browser or Mac into a relay, model, site, or third party. The owner gets a concrete privacy decision based on payload and destination instead of trusting a vague action label.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic destination and payload classification/redaction; a cheap background model may propose a human-readable summary, but it cannot override the policy or invent permission.
- **latency:** Preview in under 1 second for known payloads; under 3 seconds when extracting structured fields. No transfer begins until the preview is committed.
- **cost:** Usually <$0.01; classification and hashing dominate, with no model call for ordinary structured data.
- **security:** The preview itself must not leak more than the proposed transfer. Hash and tokenize sensitive values, preserve exact values only in the local approval context, bind approval to destination, payload digest, expiry and one-use nonce, and fail closed when browser identity or destination is unknown.
- **missing:** a Mac/browser egress interception point covering uploads, paste, form submission, email/message and relay/model requests; typed data-classification and redaction policy with owner-editable categories; a one-transfer physical or dashboard approval bound to the exact destination and payload digest; receipts proving what bytes were actually sent, including a refusal when the operation changed after approval; browser identity attestation; without it, page-bound approvals must remain blocked

### "“For any important answer, give me a compact provenance card: which words, files, pages, device events, and timestamps support it, what was inferred versus directly observed, and let me challenge one link without losing the rest of the conversation.”"
- **useful because:** The owner cannot currently distinguish a fact read from a browser, a device measurement, a remembered inference, or a model guess. A provenance card makes the hive auditable at the moment it matters and allows one bad source to be corrected without erasing unrelated history.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic source graph, hashes, timestamps and contradiction detection; background model only compresses the card into speech and never changes evidence links.
- **latency:** Attach a compact card in under 500 ms when evidence is already indexed; build a cross-surface card in under 3 s. Detailed expansion is on demand.
- **cost:** <$0.01 per card; indexing and bounded evidence storage dominate. No raw audio or full page capture is required by default.
- **security:** Use least-privilege, redacted evidence snippets and content hashes. Separate owner-visible provenance from secret page contents. Preserve the original claim and correction history; never silently rewrite an answer after a source changes. Require confirmation before opening sensitive evidence.
- **missing:** a common evidence-envelope schema linking claims to source surface, timestamp, scope, digest and observation/inference type; provenance capture in relay speech, Mac jobs, browser results and pendant events; a contradiction/correction operation that marks one edge disputed without deleting audit history; a privacy-preserving dashboard and pendant rendering for cards too large to speak; retention and owner controls for evidence capsules consistent with the extracted-fact deletion policy


## Changes it proposed to its own stack

### `integration` — Wire a reconnect supervisor that closes ordinary ledgers, scans only genuinely open/inflight work, claims a relay job with an expiring lease, runs planResume, and emits a pendant/dashboard handoff containing completed, skipped, rerun and blocked steps. Route unsafe continuation through the existing physical transaction approval latch and next-conversation delivery rather than an impossible unsolicited prompt.
- **owner gets:** A Mac crash or browser outage stops being a silent half-finished task or a duplicate action. The owner gets a truthful answer and safe continuation instead of starting over from memory.
- effort: Medium-high: closeLedger integration, relay schema/migration and requeue sweep, reconnect trigger, and approval delivery wiring; add crash/fault-injection tests around each ledger phase.  ·  risk: A bad lease or stale world fingerprint could duplicate an external action. Default to blocked on unknown replay safety, expire leases conservatively, require idempotency keys, and provide a dry-run handoff before execution.
- cost: Negligible storage and relay reads; one small D1 lease update per active job. Optional summary speech adds <$0.01 per recovery.  ·  latency: Adds under 1 s deterministic recovery work after reconnect; unsafe jobs wait for the owner's next deliberate approval.
- security: Improves safety only if plan digest, world fingerprint and physical nonce are enforced; never treat possession of the bearer token as owner approval.
- depends on: orchestrator must call closeLedger; relay_jobs needs lease_until and expiry/requeue; approvalHandoff must persist in the relay and receive a real delivery path; existing planResume must be invoked by production code


## What it asked for

_Nothing._
## Its own summary

Round 238 produced four recorded items: outage-safe replay/continuation, an integration change to wire it into production, owner-visible inferred-fact erasure, and a preflight/post-call audio proof capability. The recorder flagged the first two as close to existing resume work and the memory item as close to the existing memory-transparency backlog; the audio item is also connective rather than a wholly new primitive, but all four identify concrete missing wiring rather than restating a shipped component. Discovery confirms the live Mac bridge and Safari are online, while the pendant is still not LTE-registered.

**Biggest unknown:** I still need implementation—not another concept—for three gaps: a production caller for planResume with closeLedger correctness and relay leases; a typed fact/provenance cascade with off-machine deletion receipts; and a single call correlation ID joining pipeline, bridge playback, and delivery acknowledgement. Browser identity attestation and the owner's mandatory-confirmation policy remain unavailable as previously noted, so I will not assume either.

