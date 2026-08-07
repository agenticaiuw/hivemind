# Harness derivation — faculty-perception — round 64

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent runtime status 2026-08-07 round64** — Live /ops/status reports relay reachable and mac bridge online; browser extension home-chrome is offline with 5 pending commands. Accessibility and Screen Recording are both ungranted; computer-use loop disabled and vision upload consent false. requiredMissing is empty but permissions.ready=false.
  - evidence: GET /ops/status returned HTTP 200 with agent.permissions, computerUse, browserExtension and relay fields.
- **audio path observation round64** — A recent pipeline run rendered response audio as 24,000 Hz mono PCM (s16le), 75,734 bytes, 1,578 ms, no clipping. A separate realtime pendant input telemetry event reported pcm-s16le mono at 15,625 Hz, 937,500 bytes, uploaded live LTE.
  - evidence: GET /pipeline returned HTTP 200; event pipe_evt_d9e30c71... has TTS 24000 Hz metadata and event pipe_evt_b716... inputTelemetry.sampleRate=15625.
- **offline alert continuity round64** — Pipeline history contains a pendant-originated alert_delivered event where 2 held alerts were surfaced; origin storage was microSD and metadata included last_alert_id=a3 and uptime_s=323.
  - evidence: GET /pipeline returned HTTP 200; pipeline job_27616bb0... event pipe_evt_52b68fd4... status done.

## Capabilities it proposed

### "“When I was offline, catch me up on what I said, what arrived, and what actually got done—merge duplicates, point out anything still unresolved, and let me hear one short correction on the pendant.”"
- **useful because:** Today an offline pendant can hold alerts and the Mac/relay can later process jobs, but the owner has to infer whether a late reply, queued browser command, and local action refer to the same thread. A reconciliation brief would prevent acting twice, expose stale or failed work, and make reconnection feel continuous rather than like a pile of unrelated notifications.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic event correlation and a cheap background model for clustering/summarization; reserve realtime only for the final low-latency spoken correction when the owner asks or presses the pendant.
- **latency:** On reconnect, deterministic merge in under 2 seconds; background summary within 30 seconds; spoken 1–3 sentence correction starts within 500 ms after an explicit listen request.
- **cost:** About $0.001–$0.01 per reconnect batch, dominated by a small background summarization call; most correlation, deduplication, and receipt lookup are local/relay code.
- **security:** The ledger may contain private speech, browser URLs, and action receipts. Keep raw audio on device/relay with short TTL, send only hashed event IDs and minimal excerpts to the model, redact secrets, and require confirmation before replaying or sending any unresolved action.
- **missing:** A durable cross-surface continuity ledger keyed by intent/thread, with event provenance and clock/online-state metadata; A reconciliation worker that joins pendant microSD alerts, relay jobs, Mac pipeline events, browser command receipts, and late acknowledgements; An owner-facing spoken/dash review state for unresolved, duplicate, superseded, and confirmed events; A reconnect trigger and explicit acknowledgement semantics so an alert is not counted as handled merely because it was downloaded

### "“Find the thing I said earlier about this, play me the exact short clip, and show what note, reminder, or Mac action it led to.”"
- **useful because:** The owner currently receives spoken interactions and actions but cannot reliably trace an idea from the pendant to its resulting artifact. This would turn the hive into an attributable personal memory: exact wording, when/where it entered, what the Mac or browser did with it, and whether the result was actually completed—not a guessed summary.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Use local/on-relay full-text and embedding retrieval first; use a cheap background model only to rank ambiguous matches and explain the event chain. Realtime is needed only to play the selected clip immediately.
- **latency:** Return top matches and provenance in under 2 seconds for recent interactions; begin clip playback within 500 ms after selection; deeper archive search may take up to 15 seconds.
- **cost:** Usually below $0.005 per query, dominated by optional reranking; transcript indexing and event joins are deterministic. Storage cost is the main ongoing cost, controlled by a short raw-audio TTL and longer transcript retention.
- **security:** Voice clips, transcripts, notes, browser URLs, and secrets can be highly sensitive. Encrypt clips, keep raw audio on the pendant/relay only for a configurable TTL, redact secret-classified captures from retrieval by default, require explicit opt-in for cross-app joins, and show source/time before exposing a clip aloud.
- **missing:** A searchable interaction ledger with transcript segments, optional encrypted audio pointers, timestamps, connectivity state, and source device; Stable causal links from a spoken utterance to Mac jobs, browser commands, reminders, notes, and receipts; A retrieval API that returns evidence snippets and confidence rather than an unconstrained summary; Pendant controls for selecting, pausing, and deleting a returned clip without relying on Mac permissions


## Changes it proposed to its own stack

### `integration` — Add an end-to-end audio contract and invariant checker across pendant capture, relay upload, Mac transcription, TTS, and pendant playback: every segment carries source sample rate, target rate, resampler/version, duration, and sequence number; normalize capture to the agreed 24 kHz superwideband target (or explicitly mark 15,625 Hz narrowband), reject silent metadata coercion, and surface a one-line diagnostic when a run mixes rates.
- **owner gets:** The current history proves the output is 24 kHz but a live pendant input segment is 15,625 Hz. The owner can otherwise believe the 24 kHz path is complete while speech quality and duration drift vary by direction. A visible invariant makes audio quality explainable and catches regressions before they become mysterious conversations.
- effort: Medium: schema/version update in relay and pipeline events, one resampler/validation path, pendant playback metadata display, and fixtures for live LTE plus offline microSD.  ·  risk: A strict checker could reject legacy segments or increase CPU/battery use during resampling. Roll out warn-only, retain original bytes, and fall back to the existing decoder while recording a mismatch event; later make rejection strict once all firmware versions report metadata.
- cost: Negligible model cost; small CPU and flash overhead. Resampling may add a few percent pendant DSP work and modest LTE bytes if the target rate is higher.  ·  latency: Typically under 20 ms per second of audio on the Mac; pendant-side resampling may add a small buffering delay (target under 100 ms).
- security: No new data class; metadata could reveal device state, so keep detailed diagnostics authenticated and redact from spoken output unless asked.
- depends on: A definitive 24 kHz capture/playback contract; Firmware and relay schema versioning; A retained per-segment continuity/event record

### `memory` — Create a causality-preserving interaction ledger rather than only pipeline/job histories: assign each spoken utterance a durable interaction ID at capture, propagate it through relay transcription, planner decisions, Mac/browser actions, notes/reminders, receipts, and pendant playback, and expose a retrieval endpoint that returns a bounded evidence chain with timestamps and confidence. Keep raw audio as an encrypted expiring blob while retaining owner-controlled transcript/index records.
- **owner gets:** They could ask “what did I say that caused this reminder?” and get the exact evidence and outcome instead of trusting a reconstructed story. It makes the pendant useful as a searchable external memory and makes automation errors auditable.
- effort: High: schema propagation across firmware, relay, local agent, browser bridge, and dashboard; encrypted audio lifecycle and retrieval UI; migration for old events without IDs.  ·  risk: A propagation bug could incorrectly link unrelated actions or expose private speech. Use append-only links, never infer a causal link without an explicit confidence/source marker, provide deletion by interaction ID, and default ambiguous results to “unlinked.”
- cost: Small database/index growth; raw audio storage dominates and should use short TTL. No required model spend beyond optional embedding/reranking.  ·  latency: Capture and action paths add only metadata overhead; retrieval may take 1–2 seconds for recent events and longer for archive search.
- security: Significant privacy surface. Encrypt at rest and in transit, isolate secret-classified captures, enforce per-surface authorization, and never speak a clip aloud without a local user gesture.
- depends on: A stable interaction ID generated on the pendant or relay; Cross-surface event schema with provenance and confidence; Owner-configurable raw-audio retention and deletion semantics


## What it asked for

_Nothing._
## Its own summary

Established three fresh facts: relay and Mac bridge are reachable; browser extension is offline with five queued commands; computer-use remains disabled because Accessibility/Screen Recording are false. The audio pipeline renders 24 kHz output correctly, but a live pendant input event is 15,625 Hz, so the end-to-end contract is not yet proven. I recorded these facts and proposed (1) a cross-surface reconnect reconciliation brief joining pendant-held alerts, relay jobs, Mac pipeline events, and browser receipts, and (2) an audio provenance/invariant checker with explicit resampling metadata.

**Biggest unknown:** Authoritative pendant-side capture/playback observability and the exact continuity acknowledgement rules: I can see relay/Mac pipeline records, but cannot yet establish whether the pendant has normalized capture to 24 kHz, whether playback actually consumed the 24 kHz PCM, or when a held alert is semantically acknowledged rather than merely downloaded.

