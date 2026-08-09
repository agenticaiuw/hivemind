# Harness derivation — unified — round 206

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Prepare this message, but don't send it until I physically approve the exact recipient, text, and expiry on the pendant.""
- **useful because:** It turns the pendant's physical approval latch into a real end-to-end safety boundary for consequential communication: the owner can dictate hands-free, inspect a compact digest, and approve offline without trusting a browser prompt or accidental replay.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** deterministic digest/recipient binding and policy checks; background model for drafting; realtime only for the spoken readback
- **latency:** Draft in 2-5 seconds; stage and render the approval card within 3 seconds; send within 2 seconds after the signed pendant approval arrives.
- **cost:** One short background generation plus a small realtime readback; browser/Mac execution dominates latency, not tokens.
- **security:** Never put message secrets or page contents on the pendant; show recipient, channel, truncated content hash, and expiry only. Bind approval to a plan digest, browser tab/session, world fingerprint, and monotonic nonce; reject edits, expiry, duplicate nonce, or changed recipient. Sending always requires the physical approval, even if the Mac is already authenticated.
- **missing:** Relay implementation of the existing approval handoff store and delivery path; A browser command type that stages but cannot submit the message; A compact pendant approval frame/readback and signed decision ingestion; A privilege boundary so staging credentials cannot silently execute

### ""When I say 'take care of this later,' make it a durable handoff: tell me what is waiting, resume only safe steps after a restart, and ask me on the pendant before anything risky.""
- **useful because:** A spoken commitment currently becomes either a vague reminder or a dead Mac job. This would preserve intent across relay sleep, Mac/browser outages, and conversation changes while refusing to replay unrepeatable actions or silently cross an approval boundary.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** deterministic ledger/replay-safety engine and lease handling; background model only to summarize the handoff; realtime for the next-conversation prompt
- **latency:** Capture the handoff in under 1 second; recovery scan under 3 seconds after Mac startup; no automatic execution of risky or unrepeatable steps.
- **cost:** Low: metadata-only ledger and one short background summary; relay storage and lease sweeps dominate operational cost.
- **security:** Auto-resume only idempotent/additive steps, never unrepeatable/unknown ones. Close ordinary ledgers, expire stale leases, and require the existing physical transaction approval for irreversible/off-machine/uncontained actions. The pendant must retain a bounded decision across link loss and reject replayed nonces.
- **missing:** A production caller for planResume/resumeLedger and a startup recovery scan; closeLedger integration in orchestrator and a relay job lease_until/requeue sweep; Relay-backed approval persistence plus next-conversation delivery (not unprompted push); A user-visible handoff view showing completed, skipped, blocked, and awaiting-approval steps

### ""Export a private, readable snapshot of what you know about my preferences and active work, then let me import it onto a replacement relay without exposing secrets or raw audio.""
- **useful because:** The hive is distributed across Mac, relay, browser, and pendant, but there is no owner-controlled portability boundary. A signed, redacted snapshot would make replacement or relay loss survivable without copying browser credentials, action history, or audio by accident.
- **path:** mac-planner → relay-realtime → browser-extension → pendant
- **model tier:** deterministic field allowlist, redaction, signing, and import validation; background model only to produce a human-readable summary
- **latency:** Export in under 5 seconds for a normal snapshot; validate/import in under 10 seconds, with no live action during import.
- **cost:** Low token cost for optional summary; storage and encryption overhead are small (typically tens of KB), dominated by relay transfer.
- **security:** Never export secrets, cookies, page contents, raw audio, or job history by default. Encrypt to a one-time owner-held key, show a manifest and hashes before import, require physical pendant approval for import, reject stale schema/downgrade/replay, and make import additive unless the owner explicitly chooses replacement.
- **missing:** A typed export manifest and allowlist separating preferences, active projects, and memory from secrets/audit/audio; An owner-held encryption/key exchange flow and signed import receipt; Relay storage with versioned snapshot retention and a pendant approval frame; A browser/Mac preflight that proves cookies and credentials were excluded

### ""If I lose trust in the system, let me press the pendant once to revoke every session everywhere, prove that capture and browser access are stopped, and give me a recovery code later.""
- **useful because:** The existing privacy latch stops local capture/playback, but it does not revoke Mac, browser, or relay credentials. This would give the owner a true cross-surface emergency shutdown rather than relying on a reachable dashboard or bearer-token cleanup.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** deterministic security control and convergence verifier; no model call required except optional owner-facing explanation
- **latency:** Pendant-local mute immediately; relay and Mac/browser revocation fan-out within 5 seconds when connected; disconnected surfaces must fail closed on their next network action.
- **cost:** Minimal runtime cost; a small revocation epoch and bounded receipt history, with negligible model spend.
- **security:** The pendant event must be authenticated and replay-resistant, with a local physical confirmation pattern to prevent accidental activation. Relay must invalidate all session/token epochs, the Mac agent must reject old credentials, and the browser extension must close or quarantine controlled sessions. Recovery must be a separate, owner-held ceremony and never spoken aloud by default.
- **missing:** A relay-wide revocation epoch and session invalidation endpoint; Mac-agent and browser-extension enforcement of the revocation epoch, including offline fail-closed behavior; A signed pendant emergency-revoke event and durable local state; A cross-surface convergence receipt proving which nodes have stopped and which are unreachable; A recovery ceremony that does not reuse the revoked bearer token


## What it asked for

_Nothing._
