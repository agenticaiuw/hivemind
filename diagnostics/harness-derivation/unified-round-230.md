# Harness derivation — unified — round 230

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What did you infer about me recently? Show me each item before you remember it, and forget this one everywhere.”"
- **useful because:** The live context graph already contains inferred entities and even opaque facts, but the owner cannot tell which were extracted versus deliberately entered. A quarantine lets the system be useful without silently accumulating a hidden profile: inferred facts stay pending, are spoken/displayed with provenance, and are promoted only after explicit confirmation or expire automatically. Erasure removes the fact, derived graph relations, relay replica, and evidence capsule while preserving action audit history.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background for extraction and provenance clustering; realtime only to explain one pending fact in the next conversation; deterministic code for promotion/erasure
- **latency:** No added latency to ordinary replies. Pending-fact index updates in under 1 s; owner review is next-conversation or dashboard load.
- **cost:** About $0.001–$0.01 per extracted-fact batch depending on model use; most work is deterministic hashing, indexing, and redacted graph reads.
- **security:** Never send raw audio to the browser. Show only the minimum evidence capsule and redact secrets. Promotion and erase require explicit owner action; off-machine deletion reports requested-and-pending rather than falsely claiming completion. Action/job history is intentionally retained.
- **missing:** fact quarantine store with expiry and provenance links; context-graph promotion plus cascading erase endpoint; relay replica erase worker and pending status; pendant inbox card for pending fact summaries

### "“Make sure I actually heard the answer; if it only reached the relay or got interrupted, recover it without making me hear it twice.”"
- **useful because:** A live pipeline currently reports a response as ready while its delivery state is held_by_relay and explicitly says heard=unknown. This capability turns that dangerous ambiguity into a user-visible contract: correlate relay acceptance, pendant fetch, bridge playback start/finish/interruption, privacy-latch state, and the audio artifact checksum; if proof is missing, queue one resumable recovery at a natural boundary and say 'not yet heard' rather than claiming success.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** deterministic state machine and checksum correlation; background model only to summarize the failure; realtime not needed except for a concise spoken status
- **latency:** Receipt propagation under 2 s after playback event; recovery scheduled within 5 s of a terminal interruption, never barging into active speech.
- **cost:** Negligible model cost for normal operation; under $0.001 per recovery summary. Storage is a bounded metadata ring, not routine audio on SD.
- **security:** Opaque artifact IDs and hashes only across surfaces; no page contents or PCM exposed in the dashboard. A privacy latch cancels recovery and produces a truthful muted result. Deduplicate by event ID and require physical approval for replaying sensitive or off-machine content.
- **missing:** wire firmware playback reporters to the existing audio_delivery_ack_queue; bind live duplex packets to job/artifact IDs; relay recovery state machine with one-shot deduplication; dashboard and pendant wording for unknown/heard/interrupted

### "“Finish this across my logged-in browser and Mac, but stop at the exact point where my physical approval is needed and leave me a proof bundle.”"
- **useful because:** The system can already reach a logged-in Safari tab and a fully trusted Mac, but a blocked plan is currently spoken about and discarded: there is no durable approval handoff that survives a restart or proves what changed. This capability makes the hive act as one bounded transaction: inspect the bound tab, stage browser/Mac changes, show a compact diff and world fingerprint, wait for the pendant's physical nonce, execute only that exact plan, and return receipts plus a resumable handoff if any surface dies.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** planner tier for decomposition; deterministic policy, digest, world fingerprint, lease, and receipt verification; realtime only for the owner's short confirmation exchange
- **latency:** Preview in 3–8 s, physical approval waits up to the existing lease, execution starts within 2 s after approval; no auto-execution after timeout or world drift.
- **cost:** $0.01–$0.08 per complex task, dominated by planner/vision calls; deterministic browser and Mac steps add no model cost.
- **security:** Bind every action to explicit tab URL/session, plan digest, world fingerprint, expiry, and opaque physical nonce. Never pass page secrets to the pendant. Accessibility and Screen Recording are now live on this Mac, but the capability must degrade to browser/API-only inspection when unavailable. Keep an immutable audit receipt; require a new approval after any drift or retry.
- **missing:** implement the relay half of APPROVAL_STORE_CONTRACT; connect physical_transaction_approval_latch events to pending plans; repair orchestrator closeLedger and add relay job leases/requeue; dashboard preview/approval view and browser-session binding

### "“Before you rely on something you remember about me, check whether it is still true; if you cannot verify it, ask instead of acting.”"
- **useful because:** A hidden remembered fact can become wrong while still looking authoritative. This gives the owner a freshness guarantee: every consequential use of a remembered preference, identity, address, account state, or commitment is classified as verified, stale, contradicted, or unknown, with the smallest available evidence and an explicit question when evidence is missing.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** deterministic freshness and provenance engine first; background model for entity matching and contradiction summaries; realtime only for the short owner-facing question
- **latency:** Routine conversational facts use a cached verdict under 100 ms. Evidence checks run in the background; an action waits up to 5 s for a bound browser/Mac check, then fails closed.
- **cost:** Usually under $0.005 per verification; browser/Mac reads dominate, with model cost only for ambiguous entity matching.
- **security:** Checks only explicitly bound apps, tabs, files, or services. Never treat a search result as proof of identity. Sensitive facts require fresh owner confirmation; evidence snippets are redacted and retained only as provenance references.
- **missing:** fact freshness metadata and invalidation rules; provenance bindings from extracted facts to allowed browser/Mac evidence targets; contradiction resolver and owner-question state; action gate that refuses stale facts instead of silently using them

### "“Fill out this form, but never show the site, relay, or model my secret; tell me exactly which fields were filled and let me approve the final submission on the pendant.”"
- **useful because:** The browser and Mac can reach logged-in sites, but ordinary automation risks turning a credential or private value into model context, screenshots, logs, or relay payloads. A secret-preserving fill mode keeps values in a local protected broker, sends only field labels and masked diffs to the planner, and makes submission a physically approved transaction. The owner gets useful automation without surrendering the secret to the hive.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** deterministic local field matching and redaction; planner tier only for non-secret page structure; realtime for the approval summary
- **latency:** Preview in 2–6 s; local filling under 1 s per page; submission begins only after physical approval and a final DOM/world check.
- **cost:** $0.005–$0.03 per form, mostly optional vision/planning; secrets remain local and are not sent to a model API.
- **security:** Use explicit tab/session binding, field allowlists, local encrypted secret handles, zeroization after fill, screenshot redaction, and no clipboard fallback. Never infer a secret from page text. Any DOM drift, navigation, or masked-value mismatch invalidates approval and requires a new nonce.
- **missing:** local secret-handle broker integrated with Safari extension; field sensitivity classifier and screenshot redaction; browser action primitives that accept local secret handles without returning values; final-submit binding to physical_transaction_approval_latch


## Changes it proposed to its own stack

### `firmware` — Complete the existing PLAYBACK_REPORT_CONTRACT on the nRF9160/ESP32 path: assign every downlink artifact an opaque job/artifact ID, emit fetch/start/finish/interrupted/failed events with monotonic sequence and checksum, and persist only a bounded metadata ring. Correlate the bridge's actual DAC start/stop rather than treating relay acceptance as hearing.
- **owner gets:** The owner stops hearing confident but false claims that an answer was delivered. A response can be replayed once if it was interrupted, and privacy-latch or power loss produces an honest 'not heard' state.
- effort: Medium: firmware event hooks plus relay correlation and tests; no new audio codec work.  ·  risk: Dropped telemetry can leave state unknown; the UI must say unknown, never infer heard. Event duplication is handled by event IDs and monotonic sequence. Recovery is safe because replay is opt-in or one-shot deduplicated.
- cost: Under 4 KB nonvolatile metadata; no routine SD audio writes. Negligible API cost.  ·  latency: One small metadata event per playback transition; no measurable audio-path delay.
- security: Opaque IDs and hashes only; no PCM or transcript leaves the device. Privacy latch suppresses all reports except state transition.
- depends on: existing audio_delivery_ack_queue (s9-vtxc); relay artifact/job binding; duplex audio congestion guard (s15-rzms)

### `context` — Add a provenance-and-freshness gate between context-graph reads and action planning. Every extracted fact gets source capsule IDs, allowed verification bindings, observedAt, expiresAt, and a contradiction status. The planner must request a deterministic verifyFact operation before using any fact whose freshness window has elapsed; no evidence or conflicting evidence becomes an owner question, not a guess.
- **owner gets:** The system will stop acting on stale memories—old addresses, preferences, account states, or commitments—and will tell the owner why it paused instead of quietly doing the wrong thing.
- effort: Medium: schema migration, verifier, planner hook, and tests for stale/contradictory facts.  ·  risk: Over-conservative pauses could annoy the owner; ship configurable freshness classes and a clear 'use once anyway' confirmation that is recorded. Evidence targets may disappear, so unknown must remain distinct from false.
- cost: Small metadata growth in the graph; verification reads are usually free, with occasional browser/Mac automation cost.  ·  latency: No delay for fresh facts; expired facts add one bounded verification read or a spoken clarification.
- security: Improves privacy by narrowing evidence access to pre-bound targets and storing hashes/references rather than copied page contents.
- depends on: context-graph provenance fields; commitment_evidence_query; explicit fact classes and expiry defaults; planner integration that can return needs-owner-input


## What it asked for

_Nothing._
