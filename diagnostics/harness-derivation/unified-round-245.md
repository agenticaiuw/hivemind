# Harness derivation — unified — round 245

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I ask you to do something that needs a risky Mac or browser action, stage it, tell me exactly what will happen, and let my physical pendant approval release it; if I approve after a restart, continue once without duplicating earlier steps.”"
- **useful because:** This is the system's most important trust boundary: the wearable is the one surface the owner can deliberately touch, while the Mac/browser hold the reach. It turns spoken promises about approval into an actual, replay-safe transaction instead of silently discarding blocked plans.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** realtime for the short spoken preview; deterministic local code for digest/world/replay checks; background for recovery scans
- **latency:** Stage and speak preview in under 1 second; physical approval reflected in under 3 seconds when linked; restart recovery is eventual within 30 seconds
- **cost:** ~$0.002–$0.02 per staged action if speech uses realtime; deterministic execution dominates no model cost
- **security:** Bind approval to plan digest, world fingerprint, nonce and expiry. Never send page secrets to the pendant. Require a fresh physical approval for off-machine, irreversible-write, or uncontained actions; idempotent/additive steps may resume, unrepeatable/unknown steps must ask.
- **missing:** Relay persistence and delivery for the existing approval handoff contract; A caller from orchestrator/bridge into /prepare and /approve; Orchestrator closeLedger integration and relay job leases/requeue sweep; A production trigger that consumes physical_transaction_approval_latch events

### "“Before you hand me a result, prove which surface produced it and whether it actually arrived and was heard; if the browser, Mac, relay, or pendant disagrees, tell me the disagreement instead of saying done.”"
- **useful because:** A successful HTTP/job receipt is not proof that a browser mutation landed or that audio was heard. This gives the owner a single, honest completion state for cross-surface work and prevents confident false completion.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic correlation for receipts and sequence checks; background model only to summarize conflicting evidence
- **latency:** Normal completion under 1 second after final receipt; conflict explanation under 3 seconds
- **cost:** Near-zero for correlation; <$0.005 only when natural-language conflict explanation is needed
- **security:** Use opaque job/artifact IDs, hash and byte-range checks, and least-privilege tab bindings. Do not expose page contents beyond the bound target. Preserve raw audit receipts while redacting sensitive payloads.
- **missing:** A single correlation record joining job, browser command, pipeline artifact and playback events; Bridge-side playback-start/finish receipt ingestion; A typed owner-facing status vocabulary: accepted, applied, delivered, heard, conflicted

### "“If I say ‘lock everything down’ or hold the pendant privacy button, revoke every active browser command and Mac job, stop new execution, and give me one receipt showing what was cancelled and what still needs attention.”"
- **useful because:** The existing privacy latch protects microphone and speaker, but a stolen or unattended session could still continue a browser/Mac action. This is a distinct emergency control plane: the wearable's local signal should halt the system's ability to act, not merely stop audio, and it should be auditable when links return.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic control and receipt correlation; realtime only to confirm the short spoken command
- **latency:** Pendant audio mute and local latch remain immediate; relay cancellation broadcast under 2 seconds when connected; deferred surfaces reconcile on reconnect
- **cost:** Negligible deterministic work; <$0.002 for optional spoken confirmation
- **security:** Require authenticated latch events and monotonic counters; fail closed for new off-device actions while latched. Do not claim cancellation if a non-interruptible action already crossed its commit point; distinguish cancelled, in-flight, completed, and unknown. Clearing the latch must require a deliberate local confirmation.
- **missing:** A relay-wide execution gate checked by Mac/browser workers before claim and dispatch; A cancellation/revocation fan-out for browser commands, relay jobs, and Mac leases; A durable convergence receipt that includes late/offline surfaces; Integration with local_privacy_latch enter/exit events

### "“Let me choose, per conversation, what may leave my Mac: audio only, transcript only, redacted summary, or nothing; show me the effective choice on the pendant before you send anything.”"
- **useful because:** The system spans a wearable, Mac, browser, and relay, but the owner cannot presently express a granular data-egress choice at the moment of use. A visible, per-conversation egress contract makes privacy understandable without disabling the whole product.
- **path:** pendant → mac-bridge → relay → browser → dashboard
- **model tier:** Deterministic policy enforcement; realtime model only when converting a spoken choice into one of the fixed modes
- **latency:** Policy displayed and enforced before capture/upload; mode changes acknowledged within one turn
- **cost:** Negligible policy checks; <$0.002 for optional spoken explanation
- **security:** Default to the most restrictive mode when policy state is missing or stale. Enforce at capture, transcription, browser inspection, relay persistence, and TTS logging—not merely by UI. Produce a signed receipt of the selected mode and destinations.
- **missing:** A per-conversation egress policy object with fail-closed defaults; Enforcement hooks before capture upload, browser snapshots, relay persistence, and logs; A pendant-readable mode indicator and an owner-facing policy editor; Retention-aware handling for already-created derived artifacts


## Changes it proposed to its own stack

### `relay` — Add a cryptographic device-and-surface attestation chain: the relay issues each conversation a nonce, the pendant, Mac bridge, and browser extension independently sign the nonce plus their observed action/audio sequence, and owner-facing receipts show exactly which surface contributed each event. Reject or quarantine results whose attestation is missing, stale, or bound to another conversation.
- **owner gets:** The owner can know whether an answer came from the real pendant/Mac/browser rather than merely trusting a bearer-token job receipt. This makes cross-surface actions and audio delivery auditable after a crash, reconnect, or compromised session.
- effort: High: key provisioning and rotation on pendant firmware, bridge/extension key storage, relay verification, receipt schema, and recovery UX for a replaced Mac or pendant.  ·  risk: Clock skew, lost keys, or offline devices could quarantine legitimate work; recover with nonce windows, explicit re-pairing, and a read-only diagnostic path. Never silently downgrade to unauthenticated receipts.
- cost: Low runtime/API cost; modest relay storage for signed receipt chains and one-time provisioning engineering.  ·  latency: Adds one local signature per event and relay verification; typically milliseconds, with no extra model turn.
- security: Strongly improves provenance and replay resistance, but key compromise requires revocation and re-pairing. Private payloads remain out of receipts; sign hashes and metadata only.
- depends on: A real browser identity attestation capability; Secure key storage/provisioning on the pendant and Mac bridge; A relay receipt schema that joins conversation, job, pipeline, and browser sequence IDs


## What it asked for

_Nothing._
## Its own summary

I discovered the live inventory and recorded three distinct owner-facing capabilities this round: (1) physical approval that actually releases staged risky Mac/browser work and resumes safely, (2) proof-before-speak cross-surface completion with an honest heard/conflicted state, and (3) an emergency “lock everything down” control that revokes active work and blocks new execution. The extracted-fact transparency proposal was correctly rejected as an existing owner policy item, so I did not rephrase it. The new emergency control is especially important because the existing local privacy latch stops audio, not actions.

**Biggest unknown:** Three granted-looking tools are not equally real: privacy_convergence_check and incident_diagnostics are unresolved schemas, while fleet_health_and_repair only weakly resolves to GET /health rather than typed repair. The system still needs real implementations for cross-surface convergence, incident correlation, relay-wide execution gating/cancellation, and the approval handoff loop. I do not need more owner policy context this round; the next useful step is implementing or granting those missing control-plane capabilities.

