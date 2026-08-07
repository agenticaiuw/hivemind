# Harness derivation — faculty-perception — round 43

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-execution-readiness** — At 2026-08-07T11:14:36Z the Mac agent is reachable and full-control mode is enabled, but it is not execution-ready: Accessibility trusted=false and Screen Recording granted=false. /observe independently reports eventsPost=false, uiActionsWillReachTheScreen=false, and says UI actions may report success while doing nothing. Browser home-chrome is offline with 3 pending commands. Relay and Mac bridge are reachable/current.
  - evidence: GET /ops/status and GET /observe responses at 2026-08-07T11:14:36Z
- **pendant-audio-and-offline-buffer** — The latest pipeline history contains a completed relay response rendered as 24,000 Hz mono PCM, 164,650 bytes / 3,430 ms, with zero clipped samples; separate nRF9160 events show held alerts surfaced from microSD and an offline moment bookmark retained until reconnect. This validates the audio path and offline capture path, but does not imply Mac GUI readiness.
  - evidence: GET /pipeline at 2026-08-07T11:14Z: pipeline job_165a9c9a... TTS done (24000 Hz, clippedSamples=0), plus nRF9160 alert_delivered and bookmark events with storage=microSD.

## Capabilities it proposed

### "“Do it, but tell me the truth if anything could not actually reach the screen or my account.”"
- **useful because:** Today the Mac can return a successful-looking GUI receipt even when Accessibility input is rejected, while the browser can be offline with commands queued. This gives the owner an honest, cross-device answer rather than a plausible fiction: completed, queued, blocked-before-start, or outcome-unverified, with the exact evidence and a safe retry path.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic preflight/receipt reconciliation by default; reserve realtime for the spoken acknowledgement and a cheap background model for explaining ambiguous evidence.
- **latency:** Preflight under 500 ms when bridge/browser are reachable; pendant gets an immediate blocked/queued acknowledgement under 1 s. Reconciliation can finish asynchronously after reconnect.
- **cost:** Usually near-zero model cost (typed status checks and hashes); occasional explanation under $0.01 using a small background model. Dominant cost is storage/telemetry, not inference.
- **security:** Do not upload page contents or screenshots merely to prove readiness. Store permission state, device/session IDs, action IDs, timestamps, and minimal result hashes. Require confirmation before retrying any non-idempotent action; never convert an unverified GUI action into success.
- **missing:** A shared readiness-attestation schema consumed by relay, Mac action runner, browser bridge, and pendant; An outcome state machine that distinguishes accepted-by-host, delivered-to-UI, observed-effect, queued, and unverified; Pending-command reconciliation and duplicate suppression after browser/LTE reconnect; Dashboard and spoken status rendering for blocked versus completed work

### "“When I come back online, tell me what I missed while I was away—and separate what definitely happened from what you only inferred.”"
- **useful because:** The owner currently gets disconnected alerts and individual job histories, but not a trustworthy, chronological handoff across the pendant's offline period, relay delivery, Mac activity, and authenticated browser changes. This would turn a loss of connectivity into a recoverable timeline instead of scattered late notifications.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic event correlation and hashes for the timeline; use a cheaper background model only to summarize clusters and label inferences. Realtime is only for the short spoken handoff when the pendant reconnects.
- **latency:** On reconnect, acknowledge within 1 s and make the first concise handoff available within 5 s; deeper correlation can continue in the background.
- **cost:** Typically below $0.01 per reconnect; storage/indexing dominates. Model use is limited to summarizing already-correlated event records, not reprocessing raw audio or page contents.
- **security:** Keep raw offline audio on the pendant until upload is authorized by existing policy; send only event metadata and derived transcript snippets needed for correlation. Private browser URLs/content stay local to the Mac. Clearly mark inferred links, redact secrets, and require confirmation before turning any inferred event into an action.
- **missing:** A durable cross-surface event ledger with monotonic device sequence numbers, server receipt times, and reconnect epochs; A correlation protocol joining pendant offline records, relay delivery, Mac jobs, and browser session events without duplicate replay; A local Mac summarizer that can inspect private browser state while returning only cited, sensitivity-filtered facts; A reconnect handoff UI/audio queue with explicit definite/inferred/unknown labels and acknowledgement tracking


## What it asked for

_Nothing._
## Its own summary

Recorded a new cross-surface capability: an evidence-labeled reconnect timeline that reconstructs what happened during pendant/LTE absence from pendant, relay, Mac, and browser events, separating definite facts from inference. It requires a durable event ledger, reconnect correlation, privacy-preserving local summarization, and a spoken/dashboard handoff.

**Biggest unknown:** Whether the existing offline pendant records expose stable sequence IDs and timestamps sufficient to correlate them deterministically with relay and Mac/browser events.

