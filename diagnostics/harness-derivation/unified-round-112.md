# Harness derivation — unified — round 112

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make sure I don't lose a conversation when the pendant is about to die.”"
- **useful because:** Today the pendant has no battery gauge and LTE-M bursts are power-hungry, so a low-battery failure can silently lose the owner's spoken request. This would give the owner an early spoken/haptic warning, preserve the in-progress turn, and move only the unfinished work to the Mac/browser instead of forcing them to repeat it.
- **path:** pendant: add a fuel-gauge reading and local warning; checkpoint the current utterance and conversation sequence → relay: receive battery/connection telemetry, retain an encrypted short-lived checkpoint, and coordinate handoff → mac-planner: resume the unfinished intent or transcript and report completion through the relay → browser-extension: if the intent concerns a logged-in page, reattach the authenticated tab and continue only reversible preparation → dashboard: show battery, checkpoint age, and whether any handoff is pending
- **model tier:** Use a cheap background model for checkpoint summarization and handoff classification; reserve realtime only for the warning and the owner's next spoken turn.
- **latency:** Battery warning under 500 ms locally; relay notification within 2 s; Mac/browser handoff can take 10–30 s after the link returns.
- **cost:** Usually <$0.01 per handoff for a short checkpoint; model tokens dominate, and most battery telemetry costs no model call.
- **security:** Checkpoints may contain private speech and logged-in page context. Encrypt in transit and at rest, retain for at most 24 hours, never persist raw audio unless the existing failure-buffer rule allows it, and require confirmation before any irreversible resumed action.
- **missing:** A production battery fuel gauge and firmware telemetry path (the current pendant has no gauge); A durable, sequence-numbered checkpoint protocol across pendant, relay, and Mac; A resume policy that distinguishes safe preparation from irreversible actions; An owner-visible haptic/audio warning and a way to cancel handoff

### "“Let me speak naturally, but make sure secrets and private names never leave the pendant unless I explicitly allow them.”"
- **useful because:** The owner can currently mute or avoid speaking, but cannot rely on the system to distinguish a password, access code, medical detail, or private name before cloud processing. This would let them use the pendant in public and still delegate useful work: the private phrase is replaced locally, while the Mac/browser receives only the minimum task-safe representation.
- **path:** pendant: run a small local privacy classifier/redactor before upload, replace protected spans with stable placeholders, and show a distinct local privacy indication → relay: accept only the redacted audio/transcript plus a signed redaction manifest; reject payloads that claim redaction without device attestation → mac-planner: resolve placeholders only from explicitly authorized local context and keep them out of model prompts where possible → browser-extension: fill protected values directly into the authenticated page through a typed field operation without exposing the value to the relay or model → dashboard: let the owner define categories, inspect redaction events, revoke a category, and test the policy with synthetic phrases
- **model tier:** A compact on-device classifier handles first-pass detection. A cheap background model may audit false positives from synthetic/test data; realtime is used only for the live conversation after redaction, never to decide whether raw content is safe to upload.
- **latency:** Under 30 ms added local latency for common speech chunks; policy updates propagate within 2 seconds. A protected browser fill may take 1–3 seconds but must remain paused at an irreversible submit boundary.
- **cost:** Negligible per-turn API cost for local detection; occasional background policy evaluation is under $0.01 per batch. Storage is limited to encrypted policy metadata and event hashes, not raw private audio.
- **security:** A local classifier can miss obfuscated secrets or over-redact ordinary words. Fail closed for configured secret patterns, never upload raw fallback audio, use signed policy versions and device attestation, encrypt manifests, and require explicit confirmation before a protected value is inserted into a page or action.
- **missing:** A privacy classifier small enough for the pendant's available RAM and fast enough for streaming audio; A formal redaction policy language and signed policy distribution path; A relay protocol that proves raw audio was not uploaded and binds every placeholder to a device-side event; A browser typed-field operation that accepts an opaque protected value without returning it to the model; False-positive/false-negative evaluation using the owner's approved synthetic corpus


## Changes it proposed to its own stack

### `integration` — Add an end-to-end conversation checkpoint envelope shared by pendant, relay, and Mac: monotonically increasing turnId plus audio byte range, transcript confidence, battery/link snapshot, intent status, and last safe action receipt. The relay acknowledges each checkpoint, deduplicates retries, expires abandoned checkpoints after 24 hours, and exposes a single resume endpoint that the Mac planner can consume without replaying an already-committed action.
- **owner gets:** If the pendant loses power or LTE-M midway through a request, the system can tell the owner exactly what was heard and what was completed, then continue from that point instead of duplicating a reminder, browser edit, or other action—or making the owner start over.
- effort: Medium-high: define the envelope and state machine, add durable relay storage and idempotency, implement pendant sequence emission and Mac resume, then fault-inject power/link loss at every boundary.  ·  risk: A faulty resume decision could repeat or skip an action. Make all external actions receipt-bound, default to paused on ambiguity, and provide an explicit discard/resume control. Keep raw audio out of the envelope unless the existing failure-buffer policy permits it.
- cost: Small D1/R2 storage and one short background-model call only when a resume needs summarization; no material realtime API increase.  ·  latency: <100 ms for local checkpoint writes; up to one extra relay round trip before a long-running action is considered durable.
- security: Turn metadata can reveal private intent and browser context; encrypt sensitive fields, enforce per-owner authorization, and TTL-delete checkpoints and audio references together.
- depends on: Define the queued-action resume policy (pending request); Implement the pending task-checkpoint gesture or an equivalent owner cancel/resume control; Use the existing action receipts/undo records as the commit boundary; Add battery telemetry hardware/firmware because the current pendant cannot report charge

### `firmware` — Add a streaming privacy-firewall layer before the pendant's existing audio uplink: a deterministic pattern scanner plus a tiny quantized keyword/entity classifier emits protected-span tokens, substitutes them in the outgoing stream, and writes only a hash/timestamp/redaction reason to the failure buffer. Define a versioned policy ABI so the relay can verify that each uploaded chunk passed the firewall; raw audio is never retained as a fallback for a redacted chunk.
- **owner gets:** The owner could use the pendant around other people without choosing between silence and sending sensitive speech to the cloud. Useful requests would still work, while passwords and other configured secrets would remain on the device by construction rather than by a conversational promise.
- effort: High firmware and protocol work: reserve RAM, implement streaming frame alignment with the existing Opus path, train/quantize and validate the classifier, add signed policy updates, and test adversarial speech, accents, noise, and packet loss. Requires a product MCU with more headroom or an attached secure audio processor if the current 211,608 B budget cannot fit it.  ·  risk: False negatives create a serious privacy failure; false positives make commands frustrating. Start with deterministic owner-defined patterns and an unmistakable local privacy indicator, fail closed for high-confidence secret patterns, and provide a physical abort gesture. Recovery is a policy rollback, never a raw-audio retry.
- cost: No per-turn API cost; likely 1–5 MB additional firmware/model storage and several hundred KB RAM in the production design. A dedicated low-power DSP or secure element may add roughly $2–$8 BOM and a few mA active draw.  ·  latency: Target under 30 ms before encoding; protected spans may delay only the affected frame. Policy verification adds no network round trip.
- security: Improves confidentiality by moving the trust boundary onto the wearable, but introduces model and policy update attack surfaces. Require signed firmware/policies, monotonic versions, rollback protection, and a hardware-visible privacy state.
- depends on: A production pendant memory/power budget rather than relying on the nRF9160 DK prototype; An authenticated policy-update and device-attestation protocol in the relay; A browser opaque-secret insertion primitive so protected values cannot leak back through planning or receipts; Owner-defined categories and explicit retention rules for redaction metadata


## What it asked for

_Nothing._
