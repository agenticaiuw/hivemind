# Harness derivation — unified — round 75

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I interrupt you or the signal drops, keep my spoken request intact, continue from the last confirmed words, and tell me plainly if anything was lost."
- **useful because:** The current measured LTE-M call loses speech under simultaneous traffic (388 uplink packets, about 7.8 seconds). A wearable conversation that silently drops the owner's words is unsafe for reminders, transactions, and long instructions. This turns loss into a recoverable, honest interaction rather than a guess.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime only for detecting turn-taking and producing the short recovery prompt; a cheaper background model can reconstruct or summarize buffered segments after the link recovers. Deterministic firmware/relay code should handle sequence numbers, buffering, and loss detection.
- **latency:** Normal speech remains realtime. On detected loss, 200–500 ms local acknowledgement ('I missed part of that') and at most 2 seconds to replay/recover a buffered segment; never proceed with an irreversible action until the relevant utterance is confirmed.
- **cost:** Near-zero incremental API cost for packet accounting and deterministic recovery; occasional retranscription costs one small background inference. Dominant cost is additional LTE airtime/storage, bounded by a 10–20 second encrypted ring buffer per turn.
- **security:** Audio remains sensitive: encrypt the local ring and relay object, short-retain and delete after confirmed transcription, expose a pendant privacy latch, and require confirmation before any action whose intent was reconstructed. Never send a guessed transcript as an approved command.
- **missing:** Pendant sequence-numbered encrypted uplink ring buffer and local loss marker; Relay selective retransmit/late-segment assembler and explicit confidence state; A spoken confirmation protocol integrated with Mac/browser action gates; End-to-end audio acceptance thresholds and owner's interruption policy

### "When I walk away from my Mac, keep working on safe preparation, but automatically pause before any private or irreversible step and resume only when my pendant proves I’m back; then give me one spoken handoff of what changed while I was gone."
- **useful because:** The owner currently has no trustworthy boundary between unattended background work and actions that should happen only in their presence. This would let the system make progress without silently sending, purchasing, deleting, or exposing private data while the owner is away, and would make returning to an in-progress task understandable rather than requiring a dashboard hunt.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic policy and cryptographic presence/session checks for pause and resume; use a cheap background model to summarize completed safe preparation. Reserve realtime for the short spoken return handoff and only when the pendant is present.
- **latency:** Presence loss should gate the next risky step within 1 second. On return, resume handshake within 2 seconds and produce a concise handoff within 5 seconds. No risky action proceeds during uncertainty or link loss.
- **cost:** Negligible inference cost for policy and event handling; one small summarization call per unattended task. Main engineering cost is presence lease, key rotation, and consistent risk classification across Mac and browser.
- **security:** Presence must not be inferred from Wi-Fi or an open browser tab alone. Use a short-lived pendant challenge-response key, invalidate leases on disconnect, and bind approval to the exact action hash. Treat a stolen/unlocked Mac as untrusted; never include private page contents in the return notification until the pendant re-authenticates. Owner-configurable safe-action classes are required.
- **missing:** Pendant-backed cryptographic presence challenge and local privacy state; A shared risk/action hash understood by relay, Mac executor, and browser bridge; Pause/resume state transitions that preserve prepared artifacts without replaying completed steps; A concise handoff renderer that cites receipts and distinguishes prepared, blocked, and completed work


## Changes it proposed to its own stack

### `integration` — Create a tamper-evident cross-surface execution ledger. At intent creation, assign one traceId and hash-chain events for pendant utterance/gesture, relay plan and jobId, each Mac actionReceipt/actionId, browser commandId/tabId/result, approval checkpoints, audio briefing delivery, and final outcome. Persist only event metadata plus redacted content hashes by default; sign each terminal receipt with the relay key. Add GET /jobs/:jobId/timeline and dashboard/voice rendering that can answer 'what did you do, what evidence proves it, and where did it stop?' across retries and dropped links.
- **owner gets:** Today Mac receipts and browser command IDs are separate islands: after a long task or a connection drop, the owner cannot reliably distinguish completed work from merely planned work. A single spoken request would yield one concise, auditable completion/failure story with direct evidence and safe retry boundaries, without retaining private page contents or audio unnecessarily.
- effort: Medium: shared event schema and hash-chain in relay + adapters in local-agent executor/browser bridge + one dashboard timeline view + voice summarizer; roughly 1–2 engineering weeks, then fault-injection tests for duplicate and out-of-order events.  ·  risk: Clock skew, retries, or a crashed writer can create gaps; mark gaps explicitly rather than claiming continuity, use idempotent event IDs, and verify chain on read. A compromised Mac could report false receipts, so label events by signer/source and never treat an unsigned client event as proof. Recovery is append-only repair events, not mutation.
- cost: Small D1 metadata growth (roughly 1–5 KB per action); negligible model cost when queried, with a cheap structured summarizer preferred over realtime. Optional evidence snippets remain opt-in and short-retention.  ·  latency: <100 ms per event locally/relay; final spoken summary adds one structured retrieval and can be generated asynchronously for long jobs.
- security: Improves auditability while reducing data exposure if payloads are hashed/redacted. Requires relay signing-key rotation, per-owner authorization on timeline reads, and explicit separation of secret URLs/content from hashes.
- depends on: chg-5fc73ce3 receipt infrastructure (implemented but currently Mac-local); chg-14accc01 browser request IDs/tab affinity/typed results; durable job runner from chg-16bc5dee; a typed context projection so the summarizer receives only task-relevant facts

### `relay` — Add a pipeline reconciliation/watchdog that derives terminal status from immutable events rather than trusting the last writer. It should detect runs stuck in processing after a late/offline-forwarded response, distinguish delivered-to-relay from downloaded-by-pendant and played-to-owner, close or quarantine stale runs with an explicit gap, and surface the resulting state in job receipts and spoken status.
- **owner gets:** Live data already contains a run that says 'Realtime plan ready' and 'response forwarded after the connection came back' while the pipeline remains processing. The owner can therefore be told a task is still running when it actually finished—or miss that audio was never played. Accurate completion and delivery states prevent duplicate commands and false reassurance.
- effort: Small-to-medium relay change: event reducer, idempotent watchdog cron, pendant playback acknowledgement, and dashboard/voice labels; about 3–5 days plus offline/reconnect tests.  ·  risk: A watchdog could close a genuinely slow job prematurely. Use generous timeouts by stage, never infer played from uploaded, and quarantine ambiguous runs for explicit owner review. Recovery is a late event that reopens/reconciles the trace, never deletion.
- cost: Minimal D1 writes and one scheduled Worker invocation; no extra model call unless the owner asks for a narrative.  ·  latency: No hot-path impact; acknowledgements add one tiny control message after playback.
- security: Delivery metadata is less sensitive than audio, but job IDs and timestamps still require owner authorization. Do not expose raw audio or transcript in watchdog alerts.
- depends on: POST /pipeline/events event schema; POST /pipeline/audio delivery path; GET /pipeline reducer/read model; pendant playback acknowledgement event; the cross-surface execution ledger proposed this round


## What it asked for

_Nothing._
## Its own summary

Round 75 produced three concrete additions: (1) a tamper-evident execution timeline joining pendant intent, relay jobs, Mac receipts, browser command IDs, approvals, audio delivery, and outcome; (2) loss-aware interruption recovery that preserves buffered speech and refuses to guess on irreversible actions; and (3) a pipeline watchdog/reconciler so late or offline-forwarded audio cannot remain falsely stuck in 'processing.' Fresh probes confirm the browser extension is offline with 5 pending commands, while the relay and pipeline are healthy. The pipeline already demonstrates the state bug: a response is marked ready and forwarded after reconnection but its run remains processing.

**Biggest unknown:** The owner-facing audio contract is still unspecified: acceptable interruption recovery, end-to-end delivery/playback thresholds, privacy-latch behavior, and whether a phone companion is acceptable. The authenticated browser cannot execute until its extension heartbeats again. GUI automation remains blocked until the owner manually grants Accessibility/Screen Recording to the AI Pendant Agent binary; AppleScript, typed Mac actions, and browser-free paths remain available.

