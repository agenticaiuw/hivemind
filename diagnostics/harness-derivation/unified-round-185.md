# Harness derivation — unified — round 185

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Talk to me here even when LTE is unavailable, and keep the same conversation when the link comes back.""
- **useful because:** The pendant and ESP32 bridge are physically attached to the Mac now, while LTE registration is absent. This would make the device genuinely usable today rather than falling silent whenever the modem is unavailable, and would prevent duplicate or lost turns during USB↔LTE handoff.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for turn-taking and audio; deterministic routing for transport selection; background model only for reconciling a recovered turn log.
- **latency:** Button-to-capture under 100 ms; first response audio under 1.5 s on USB; handoff at a turn boundary with no duplicated audio and a visible receipt within 2 s.
- **cost:** Realtime inference cost is the same as a normal conversation; transport coordination adds negligible API cost. USB mode avoids LTE data charges while attached.
- **security:** USB audio and transcripts remain on the bound Mac unless the owner’s relay policy permits upload. Bind each turn to device identity, transport epoch, and monotonic sequence; reject late frames from the previous transport. Require explicit owner policy for whether USB conversations may leave the Mac.
- **missing:** A production USB serial session coordinator joining the accepted usb_fallback_audio_session firmware behavior to the relay conversation state; Transport-epoch/turn-sequence reconciliation and duplicate suppression across /pipeline/audio and /pipeline/events; A relay-visible device/session registration while LTE is unregistered; An end-to-end hardware test using the currently attached nRF9160 and ESP32 instead of assuming an LTE device

### ""Stage that browser action and let me approve it with the pendant button before anything is submitted.""
- **useful because:** The system can plan browser work and the pendant now has an accepted physical_transaction_approval_latch, but the approval loop is not connected: blocked plans are spoken about and discarded. This gives the owner a real, least-surprise boundary for sending, buying, deleting, or submitting while preserving the browser session the Mac cannot otherwise reach.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only to explain the staged action and read the owner's decision; deterministic code validates nonce, digest, expiry, world fingerprint, and replay state; no expensive model is needed to execute.
- **latency:** Stage and speak a concise summary within 2 s; button decision acknowledged locally immediately; browser submission starts within 1 s of a valid approval and receipt returns within 5 s.
- **cost:** One short realtime utterance per stage/decision; deterministic relay and browser calls dominate neither tokens nor compute.
- **security:** Never send page secrets to the pendant. Bind approval to an opaque nonce, plan digest, target tab, expiry, and world fingerprint; one approval must authorize exactly one execution. A cancelled, expired, changed, or replayed nonce must fail closed. Keep approval and execution credentials separately scoped when possible.
- **missing:** A relay implementation of the existing approval handoff store and delivery/readback contract; A delivery path that can present the nonce over the active USB conversation (and later LTE), then record deliveredAt; A caller from the planner/orchestrator into prepare/approve rather than discarding awaitingApproval; A dashboard or spoken pending-state view that lets the owner inspect what is awaiting the physical decision; A browser executor that refuses to submit unless the approved nonce and target binding still match

### ""Show me every fact you inferred about me, where it came from, and forget exactly the ones I name.""
- **useful because:** The owner’s retention rule is not satisfied by a delete endpoint alone: extracted facts are hidden, copied into graph/context structures, and may have relay replicas. A voice-queryable inventory with evidence and a pending cross-surface erase receipt makes inferred memory accountable and lets the owner remove one fact without deleting the action audit trail.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model extracts a plain-language inventory from structured records; deterministic code performs identity resolution, cascade deletion, replication tracking, and audit-safe receipts. Realtime is used only when the owner asks by voice.
- **latency:** Inventory summary under 3 s for up to 50 facts; local deletion acknowledgement under 1 s; off-machine deletion reports requested/pending immediately and settles asynchronously.
- **cost:** Small background summarization call only when rendering unfamiliar facts; ordinary list/delete operations are local and low-cost. No audio needs to be retained.
- **security:** Require explicit confirmation for each destructive fact deletion, never delete job history, redact evidence by default, and distinguish local erased from relay/R2 requested-pending. Bind derived copies by provenance IDs so a similarly worded fact cannot be accidentally removed.
- **missing:** A first-class fact inventory with stable fact IDs, provenance/evidence capsule IDs, and derived-copy links; A cascade erase transaction spanning facts.json/context graph and relay/D1/R2 replicas with requested/pending status; A voice/dashboard presentation route that exposes only facts the owner can recognize, not hidden embeddings or raw secrets; A deletion receipt and retry/reconciliation worker that never touches the action audit trail

### ""Keep this conversation entirely on my Mac unless I explicitly say to send it elsewhere, and prove that nothing was uploaded.""
- **useful because:** Today the owner cannot make a verifiable per-conversation residency choice across pendant capture, relay processing, browser exposure, and Mac logs. A local-only mode would make the wearable usable for private conversations without trusting a hidden transport default, and would return a convergence receipt rather than a promise.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic policy and receipt generation; realtime model only for the conversation itself. No background model is needed.
- **latency:** Latch the residency policy before capture begins (<100 ms); reject any disallowed upload before the first frame leaves the Mac; produce a convergence receipt within 1 s of ending the turn.
- **cost:** Negligible inference overhead; local-only mode can reduce relay and transcription API cost. Storage is bounded metadata, not raw audio.
- **security:** Enforce at the transport boundary, not by deleting after upload. Bind policy to conversation ID and transport epoch, cover relay queues, browser commands, crash journals, and audio spool, and report any pre-policy bytes explicitly. The receipt must be signed or authenticated and distinguish verified absence from an unavailable surface.
- **missing:** A first-class per-conversation data-residency policy carried from the pendant button/voice intent into every transport; Relay and Mac gates that refuse persistence or forwarding when local_only is active; Browser exposure and crash-recovery paths that honor the same policy; A typed receipt that proves capture, relay, queue, and browser convergence, including unavailable surfaces

### ""Before you touch anything, show me the exact external-world changes this plan would cause, including what could be different by the time I approve.""
- **useful because:** Existing planning and approval concepts summarize actions, but the owner cannot see a single, bound before/after preview across a browser tab, Mac files, and relay-held state. A world-diff rehearsal would expose stale pages, changed files, and hidden side effects before the physical approval decision, reducing the chance of approving an action whose target moved.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic snapshot/diff engine; a cheap background model may turn the structured diff into a short spoken explanation, but it must not infer authorization.
- **latency:** Generate a preview within 3 s for up to 20 bound resources; invalidate it immediately when a bound resource changes; spoken summary under 20 s.
- **cost:** Mostly local reads and browser inspection; occasional small summarization call. No action is executed during preview.
- **security:** Read only explicitly bound tabs, paths, and apps. Redact secrets and page contents by default. Treat inability to inspect as unknown, never as unchanged. The approval nonce must include the preview digest and expire on world movement.
- **missing:** A common before/after representation for Mac and browser resources; A read-only browser/Mac snapshot adapter that reports unknown rather than silently omitting state; Preview invalidation on world changes and binding of the preview digest to physical approval; An owner-facing route/card that survives until approval or expiry

### ""Before this leaves my Mac, replace the private names, addresses, and numbers I mark with reversible placeholders, and let me restore them only on this device.""
- **useful because:** Local-only mode is all-or-nothing, but the owner may want relay intelligence without exporting identifying details. Today there is no per-turn, auditable redaction boundary spanning speech text, browser commands, logs, and TTS. A local reversible privacy transform would let the relay reason over a scrubbed conversation while the Mac alone can render the real values.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic local PII policy and placeholder vault; realtime model receives only scrubbed text. A background model may suggest candidates, but owner policy or explicit confirmation must decide what is redacted.
- **latency:** Apply redaction before upload with under 150 ms added to a turn; restore placeholders locally before Mac/browser actions or owner-facing speech; fail closed if the local transform is unavailable.
- **cost:** Low local CPU/storage cost; no extra model call for configured patterns. Optional PII detection adds a small background/realtime cost and must never silently expand the redaction scope.
- **security:** Placeholder mappings remain only on the Mac, encrypted and scoped to a conversation/expiry. Never send mappings or raw audio to the relay. Browser actions must receive restored values only after explicit local authorization, and logs must contain placeholders. A receipt must list categories redacted without revealing values.
- **missing:** A policy editor for owner-selected redaction categories and exact values; A streaming text transform before relay persistence and before browser/job logging; A scoped encrypted placeholder vault with expiry and explicit restore authorization; Tests proving raw values cannot leak through audio transcripts, TTS requests, browser commands, receipts, or crash recovery


## What it asked for

### `c23-7mhg` (context) — current USB serial audio/session integration status
- why: The hardware is physically attached and the accepted usb_fallback_audio_session skill describes intended behavior, but I need to know whether a Mac-side serial reader/writer and framing parser already exist before treating USB conversation continuity as missing work.
- would change: If a working serial bridge exists, I would propose an end-to-end test and wiring only; if not, I would identify the parser/session coordinator as the immediate implementation blocker and avoid claiming the owner can talk locally today.

## Its own summary

This round produced three owner-facing capabilities: (1) USB↔LTE conversation continuity using the physically attached pendant/ESP32, (2) a real physical-button approval loop for staged browser actions, and (3) inspectable, provenance-linked inferred facts with selective cascade erasure. I also queued a context request to establish whether a Mac-side USB serial audio/session bridge already exists. The live system is healthy, but the pendant is a prototype DK with one button/LED and LTE is still unregistered, so I did not claim standalone LTE operation.

**Biggest unknown:** Whether the accepted USB fallback firmware behavior is already connected to a working Mac serial framing/session implementation. That determines whether the first capability is mostly wiring/testing or still needs its core bridge.

