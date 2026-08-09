# Harness derivation — unified — round 205

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When a Mac, browser, or relay interruption cuts off something you asked me to do, tell me exactly what finished and safely continue only the replay-safe remainder when I next reconnect."
- **useful because:** Today an interrupted run can be mistaken for an untouched run, while completed ledgers are falsely reported as interrupted. The owner gets either duplicate actions or a dead end. This would make recovery truthful and safe across the pendant, relay, Mac, and browser.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for reconciliation; realtime only to explain the result over voice
- **latency:** Initial recovery summary under 2 seconds after reconnect; actual resumed work proceeds asynchronously with a spoken update before any non-replay-safe step.
- **cost:** Usually <$0.01 per recovery using deterministic ledger/workbench checks; model cost only for ambiguous owner-facing explanation.
- **security:** Auto-run only replaySafety idempotent/additive steps with valid leases; unrepeatable/unknown steps remain blocked for the next conversation. Close ordinary ledgers first so successful plans are not misclassified. Do not expose browser contents beyond bound receipts; require the existing physical transaction approval latch for off-machine or irreversible work.
- **missing:** Call closeLedger from the orchestrator and preview paths; Relay job lease_until plus expiry/requeue sweep; A production caller that invokes planResume and workbench handoff after reconnect; A next-conversation presentation of blocked steps

### "Show me every personal fact you inferred about me, where each came from, and let me erase one fact everywhere it was copied without deleting my action history."
- **useful because:** The system extracts facts into facts.json and the context graph, but the owner cannot see or individually remove them. This is the clearest privacy defect: remembering is happening without a recognisable review and erase surface.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for indexing and provenance; realtime only for the owner's spoken list or confirmation
- **latency:** List within 3 seconds for up to 50 facts; deletion acknowledgement within 5 seconds, with off-machine deletion explicitly reported as pending until confirmed.
- **cost:** <$0.01 for list/delete orchestration; storage and replication dominate, not model inference.
- **security:** Require explicit confirmation for each erase, authenticate the owner session, erase the extracted fact, derived projections, evidence capsule, and relay replicas but preserve job history. Redact sensitive evidence by default and never infer a timezone or identity from missing device data.
- **missing:** Typed list/delete routes for extracted facts and derived copies; A provenance index from fact to evidence capsule and relay replica; An asynchronous off-machine erase state and receipt; A dashboard or pendant-readable review surface

### "Before you submit anything in my browser, tell me the exact site, signed-in account, destination, and irreversible consequence, and let me cancel from the pendant without exposing page contents to it."
- **useful because:** A browser action can be aimed at the wrong account or destination even when the action itself is syntactically valid. The owner needs a compact, trustworthy preflight rather than discovering the mistake after submission.
- **path:** pendant → relay → browser-extension → mac-bridge → dashboard
- **model tier:** deterministic browser inspection and policy first; background model only to compress a long consequence summary
- **latency:** Preflight under 1 second for bound tabs; cancellation reaches the bridge before dispatch, and no action is sent until the preflight is acknowledged.
- **cost:** Near-zero model cost for structured metadata; occasional <$0.01 summary for complex forms.
- **security:** The browser extension supplies only origin, account label, target, action class, and a redacted consequence digest. Page contents and credentials stay in the browser. Physical cancel/approve events are nonce-bound and single-use; stale or changed tabs refuse.
- **missing:** A browser identity attestation primitive (already requested, still unavailable); A redacted structured browser preflight route; A dispatch gate that binds the preflight digest to the eventual command; An owner-facing cancellation receipt

### "Give me a morning privacy-and-reliability briefing: whether capture is latched off, whether any pending action or browser command can still run, and whether the last spoken answer was actually played."
- **useful because:** The owner currently has to ask several systems separately. A single compact briefing exposes the safety state that matters before wearing the pendant out of the house, without pretending relay acceptance means the owner heard audio.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic aggregation; background model only to phrase anomalies
- **latency:** Under 2 seconds from the Mac/relay; if a surface is offline, say which evidence is stale rather than waiting indefinitely.
- **cost:** <$0.005 per briefing; mostly read-only route calls.
- **security:** Use authenticated convergence and delivery receipts; do not include raw audio, page contents, or sensitive job parameters. An unknown or stale state must be reported as unknown, never healthy.
- **missing:** A unified owner-facing read model joining privacy_convergence_check, pending approval/command state, and audio_delivery_ack_queue; A routine/scheduled trigger and a concise pendant-safe rendering; Staleness thresholds per surface

### "For this conversation, let me say 'off the record' and receive a receipt proving that no transcript, inferred fact, browser content, or audio fallback copy will be retained after the session is cleared; if any surface cannot honor it, refuse to enter that mode instead of pretending."
- **useful because:** The existing privacy latch stops the pendant's microphone and speaker, but it does not express a memory boundary for a conversation that the owner deliberately chooses to have. The owner needs a way to speak privately while still using the assistant, with a verifiable cross-surface guarantee rather than a verbal promise.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic policy enforcement and deletion receipts; realtime model only to acknowledge the mode
- **latency:** Enter mode and return a compact receipt within one turn; clear local state immediately at session end and report replicated erasure asynchronously.
- **cost:** Low ongoing cost; one bounded metadata receipt per session, with no model inference required beyond normal conversation.
- **security:** The mode must be fail-closed: disable transcript persistence, fact extraction, browser evidence capture, audio SD fallback, and relay retention for the bound session. Keep only a non-content tombstone needed to prove deletion, never raw text or audio. If a browser tab or relay replica cannot comply, do not claim privacy.
- **missing:** A session-scoped retention policy propagated from pendant to relay, Mac, and browser; A non-content deletion/convergence receipt covering transcript, derived facts, evidence capsules, queued jobs, and replicated audio; A way to prevent fact extraction and browser capture before data is written; Owner-visible mode entry/exit and refusal indicators


## Changes it proposed to its own stack

### `model-routing` — Add an audio-aware response budgeter at the relay that consumes the live 24 kHz pipeline counters and audio_delivery_ack_queue state before and during a spoken turn. It should choose a response chunk duration and pacing that fits the shipped 60 ms Opus framing and current decode headroom, stop queuing additional speech after a failed/interrupted playback acknowledgement, and resume only at a turn boundary. It must not resample the 24 kHz downlink or write routine audio to SD.
- **owner gets:** When the bridge or link is marginal, the owner should hear one coherent answer rather than overlapping, delayed, or endlessly queued speech. The system would adapt what it sends to what the pendant actually heard, while preserving the tested 24 kHz quality path.
- effort: Medium: relay-side pacing state machine, acknowledgement correlation, bounded queue policy, and replayable integration tests against the fault injector.  ·  risk: Overly conservative pacing can make replies feel slow; incorrect acknowledgements could truncate speech. Use hysteresis, turn-boundary-only changes, explicit timeout states, and a deterministic fallback to the current known-good 60 ms profile.
- cost: Small relay CPU/state cost; no additional model call when counters are healthy.  ·  latency: Adds at most one acknowledgement window (~60–200 ms) on degraded links; no added latency on healthy links.
- security: Transmit only opaque artifact IDs and counters, not raw audio beyond the existing audio path; retain the existing delivery receipt privacy boundaries.
- depends on: audio_delivery_ack_queue; audio_path_diagnostic_fixture; duplex_audio_congestion_guard; live relay access to pendant/bridge acknowledgements


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities and one stack change: (1) safe cross-surface interrupted-work recovery gated by replaySafety, (2) owner-visible inferred-fact review and deletion with provenance and replica erasure, (3) browser submission preflight showing origin/account/destination/consequence with pendant cancellation, (4) privacy/reliability morning briefing, plus an audio-aware relay response budgeter. The staged-approval integration proposal was correctly rejected as an existing physical_transaction_approval_latch/approvalHandoff item rather than rephrased.

**Biggest unknown:** Browser identity attestation is still unavailable, so the browser preflight cannot honestly identify the active account yet. Other concrete blockers are the missing extracted-fact delete/provenance API, relay implementation of the approval store, orchestrator closeLedger calls, and relay job leases/requeue. I did not re-request the already-pending attestation request.

