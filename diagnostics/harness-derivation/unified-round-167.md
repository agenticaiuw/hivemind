# Harness derivation — unified — round 167

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “prepare that purchase/form/email but don’t send it,” stage the exact browser action, tell me what will happen, let me approve it with the pendant’s physical hold, then execute only that unchanged action and tell me the result."
- **useful because:** This is the single most useful missing trust loop: the owner can delegate consequential browser work without granting a blanket remote-control authority, and a link drop cannot turn a draft into an accidental send.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** background for staging and summarization; realtime only for the short spoken readback
- **latency:** Stage in under 5 s; physical approval acknowledgement under 1 s; execute and report within 15 s, otherwise remain visibly pending.
- **cost:** Roughly $0.01–$0.05 per invocation depending on browser planning; browser execution and relay storage dominate, not model tokens.
- **security:** The staged plan must bind a digest, world fingerprint, expiry, nonce and physical approval; never send page contents to the pendant. Any changed page, expired lease, duplicate nonce or missing delivery receipt must refuse rather than guess. The owner must explicitly opt into which browser origins are allowed.
- **missing:** Wire shared/approvalHandoff.js persistence into the relay APPROVAL_STORE_CONTRACT; Call prepareAction from the live planner and consume physical_transaction_approval_latch events; Add a real relay job lease/requeue sweep; Provide the pending approval readback during the owner’s next conversation; unsolicited pendant push is unavailable

### "Run a private end-to-end check when I ask: confirm the pendant mic, USB bridge, relay, TTS and speaker are all connected, play a short test tone only after I authorize it, and tell me exactly which segment failed if they are not."
- **useful because:** The owner currently cannot distinguish a dead microphone, stalled bridge, relay loss, codec regression or silent speaker without engineering interpretation. A deliberate, bounded test makes the wearable diagnosable before an important conversation and avoids storing real speech.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** deterministic checks and background analysis; realtime is unnecessary except for the optional spoken verdict
- **latency:** Read-only preflight under 2 s; authorized fixture round trip under 8 s; abort immediately on privacy latch or unexpected audio.
- **cost:** <$0.005 per run; most cost is device airtime and fixture transport, not inference.
- **security:** No room audio or page data; use a fixed synthetic fixture and discard it after checks. Playback requires explicit confirmation because it makes sound. Respect local privacy latch, report modem/link identifiers minimally, and never claim speaker delivery without the physical playback receipt.
- **missing:** A callable orchestration route that sequences the already-shipped audio diagnostic fixture across both chips and relay; ESP32 bridge acknowledgement correlated to fixture sequence numbers; A pendant-local authorized-test state that blocks microphone capture and real TTS during the fixture

### "If I unplug the pendant from my Mac during a conversation, keep the same turn alive over LTE (or resume locally when I reconnect), without repeating my words or dropping the reply; tell me plainly when transport changes."
- **useful because:** The pendant is physically testable over USB today but is intended to work away from the Mac. A turn-boundary handoff makes that transition feel like one device instead of two incompatible sessions, especially when the owner walks out the door mid-question.
- **path:** pendant → mac-planner → relay → mac-vision
- **model tier:** deterministic transport/session state machine; background model only for recovery wording, not routing decisions
- **latency:** Detect link loss in under 500 ms, choose the alternate path at the next frame/turn boundary, and resume within 2 s; never duplicate audio to both paths.
- **cost:** <$0.005 per handoff; modem airtime and bridge keepalive dominate.
- **security:** Bind frames to a session epoch and monotonic turn/sequence numbers; invalidate the old transport before accepting the new one. Do not replay captured PCM after a privacy latch or across sessions. Surface a brief audible/LED transport-change cue without exposing network identifiers.
- **missing:** Relay-side transport ownership and epoch arbitration for USB versus LTE; A Mac bridge heartbeat carrying the pendant’s last committed frame and turn sequence; A reconnect protocol that can request only the missing response suffix, not retransmit the owner’s entire utterance; LTE registration and a tested modem path; the device is currently unregistered, so USB is the only live path

### "When I say “remember this” or “forget that” aloud, show me the exact memory change, let me approve it on the pendant, and make the change with a provenance trail, expiry, and a one-press undo—not just a transcript or an unreviewed model belief."
- **useful because:** The owner should control what this hive mind carries forward. Today context-graph mutation routes exist, but there is no owner-facing, provenance-preserving voice ceremony that distinguishes a durable fact from a transient conversation and makes correction safe.
- **path:** pendant → relay → mac-planner → dashboard-ux
- **model tier:** background model extracts a candidate fact and explains it; deterministic code handles diff, approval, expiry, provenance and rollback
- **latency:** Candidate preview within 3 s of the utterance; physical approval response under 1 s; commit under 2 s. If approval is unavailable, retain only an ephemeral candidate and do not mutate memory.
- **cost:** <$0.01 per invocation; model extraction dominates, with small context-graph writes.
- **security:** Never persist raw audio by default. Bind approval to an exact normalized diff and source conversation ID; encrypt sensitive fields, redact secrets from previews, enforce per-memory retention/expiry, reject stale world/schema versions, and make deletion produce a tombstone rather than silently recreating the fact.
- **missing:** A memory proposal/diff and provenance data model on top of the existing context graph; A physical approval event path and next-conversation spoken delivery for memory changes; A durable rollback/tombstone mechanism with owner-configurable expiry; A dashboard view that clearly separates candidate, approved, active, expired and deleted memories

### "Before you rely on something you remember about me, check it against my current authorized calendar, browser and Mac state; if it conflicts, ask me which version is true and record the resolution instead of silently choosing."
- **useful because:** Stale personal facts are more dangerous than missing facts: they can cause the agent to schedule, send or say the wrong thing. The current graph has entities and relations but no cross-surface freshness or conflict ceremony.
- **path:** relay → mac-planner → browser → pendant
- **model tier:** deterministic freshness and conflict detection first; background model only to summarize competing evidence; realtime only for the owner’s brief question
- **latency:** Check bounded evidence in under 4 s before an action; never delay ordinary conversation unless a conflicting fact would affect the requested action.
- **cost:** <$0.02 when a conflict requires summarizing several sources; most invocations are cheap hash/timestamp comparisons.
- **security:** Only inspect explicitly bound browser tabs/apps and authorized calendars/files. Return evidence candidates, not page contents. Treat source timestamps as evidence rather than truth, retain the owner’s resolution and provenance, and require physical confirmation before a conflict changes a durable fact or triggers an external action.
- **missing:** Typed freshness/confidence/provenance fields and conflict relations in the context graph; A bounded cross-surface evidence join with source authorization and redaction; A pendant question/answer flow that survives a dropped link and binds the chosen resolution to the competing evidence

### "Fill a password, payment detail or one-time code into the exact authorized browser field without showing the secret to the model, relay, pendant or logs; let me approve the destination and field, then prove only that the field was filled—not what the secret was."
- **useful because:** The owner needs automation that is actually safer than copying secrets through chat. Today browser planning, inspection and physical approval can coordinate an action, but there is no isolated secret-injection boundary or receipt proving a secret never entered model context.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** deterministic browser-side secret injection and destination matching; background model may describe the non-secret field and origin but must never handle the value
- **latency:** Destination/field preview under 3 s; injection immediately after physical approval; receipt within 2 s, with no secret-bearing retry.
- **cost:** <$0.01 per invocation; secure vault access and browser extension IPC dominate, not inference.
- **security:** Use OS Keychain or an owner-selected vault, origin and field binding, one-shot expiring handles, clipboard-free injection, redacted logs, no relay persistence of values, and refusal on iframe/origin/field changes. Never transmit the secret to the pendant. The physical approval must cover the exact origin, field identity and expiry.
- **missing:** A browser-extension privileged field-injection primitive that accepts only an opaque vault handle; A vault/Keychain adapter and secret-use audit record containing hashes/metadata only; A relay protocol that transports handles, not values, and ties them to physical_transaction_approval_latch; A non-secret browser receipt for successful field focus/injection


## Changes it proposed to its own stack

### `relay` — Implement the missing approval and execution spine: persist approvalHandoff records in relay storage, add relay_jobs lease_until with expiry/requeue, correlate physical approval nonce to the unchanged plan digest, and expose a single state machine from staged → delivered → approved/cancelled → executed/refused. Close ordinary orchestrator ledgers so completed work is not misclassified as interrupted.
- **owner gets:** A deliberate pendant approval should actually cause exactly one requested browser/Mac action—or clearly refuse. Today the code can prepare and reason about this, but the relay half and production caller are absent, so “waiting for approval” can become a silent no-op.
- effort: Medium-high: relay schema/store migration, orchestration wiring, integration tests with dropped Mac/browser and duplicate approval events.  ·  risk: A lease or correlation bug could duplicate an external action. Recover with idempotency keys, immutable plan/world digests, physical nonce replay rejection, and refusal on uncertainty; migrate schema backward-compatibly and keep the current manual path until soak-tested.
- cost: Negligible storage; one small D1 row/update per staged action and lease sweep. No additional model cost.  ·  latency: Adds tens to hundreds of milliseconds for persistence and approval verification; avoids 24-hour stuck processing after Mac failure.
- security: Improves least-privilege auditability but does not itself create a separate approval credential; that remains a follow-up boundary decision. Never persist page secrets or form contents in relay approval records.
- depends on: physical_transaction_approval_latch firmware delivery; A real pendant delivery/readback path during the next conversation; Owner-defined retention/deletion policy for approval and execution evidence


## What it asked for

_Nothing._
## Its own summary

Three distinct user-facing capabilities were recorded: (1) staged browser/Mac action with unchanged-plan physical pendant approval and truthful completion, (2) private synthetic end-to-end audio preflight, and (3) USB-to-LTE conversation handoff without duplicate frames. I also recorded the concrete relay change that makes physical approval real: persist approval state, add job leases/requeue, correlate nonce/digest, and close ledgers. The away-report idea was correctly rejected as an existing capability, so I did not count or restate it.

**Biggest unknown:** The remaining blockers are product/policy and hardware integration rather than discovery: the owner’s retention/deletion policy and personal timezone are still unanswered (already requested; I will not re-ask), LTE registration is still absent, and the relay approval persistence plus pendant delivery/readback path are not yet implemented. Accessibility/Screen Recording remain owner-granted TCC permissions and cannot be fixed from this agent.

