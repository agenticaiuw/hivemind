# Harness derivation — unified — round 104

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If the connection drops after I ask you to do something, keep the request traceable across the pendant, relay, Mac, and browser, and later tell me whether it was completed, partially completed, or never started—with evidence and a safe resume option."
- **useful because:** Today a spoken request can be lost in LTE contention, a queued browser command can remain offline, or a Mac receipt can claim success while UI events were rejected. The owner needs one honest answer instead of guessing or repeating a potentially destructive action.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use realtime only to capture/acknowledge the short intent; use a cheaper background planner for execution, reconciliation, and evidence summarization.
- **latency:** Local pendant acknowledgment under 500 ms; relay durable intent under 2 s when online; background reconciliation within 30 s of a node returning; spoken catch-up under 5 s.
- **cost:** Low-to-moderate: one short realtime turn for capture, then mostly local Mac/relay work; background model calls only for ambiguous reconciliation or a concise summary.
- **security:** Persist only an intent ID, redacted command summary, node receipts, and hashes—not raw audio by default. Never auto-resume sends, purchases, deletes, or other irreversible actions; require the existing owner confirmation gate and show before/after evidence. A stale browser session or false UI success must be marked uncertain, not upgraded to success.
- **missing:** A cross-node durable intent journal with monotonic sequence numbers and an explicit state machine (captured, accepted, started, step receipts, blocked, completed, uncertain, expired).; A pendant-local short command/receipt spool that survives a dropped WebSocket and replays deduplicated IDs when LTE-M returns.; A relay reconciler that joins Mac job receipts, browser request IDs/tab affinity, and transport acknowledgments, including the known offline browser queue.; Truthful UI verification: accessibility-free Mac actions must not report completed when synthesized UI events were rejected; classify these as unverified and request owner recovery.; A resume endpoint that can continue only from the last verified idempotent checkpoint, never replaying irreversible steps.

### "Make me a private, cited export of everything relevant to this request across my Mac files, logged-in browser pages, pendant conversation, and relay history—redact secrets, show me the manifest first, and give me an encrypted file that expires unless I keep it."
- **useful because:** The owner currently has information scattered across devices and authenticated tabs, with no trustworthy way to see exactly what was collected or take it elsewhere. This provides a deliberate, auditable data handoff rather than another opaque briefing.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a background model for selection, deduplication, and citation writing; use realtime only to confirm scope and announce completion.
- **latency:** Manifest preview within 10 seconds for ordinary scopes; export within 1–3 minutes; pendant acknowledgment under 500 ms.
- **cost:** Moderate background inference for classification and redaction; storage and encryption are the dominant non-model costs. Do not resend raw files or audio to the model when hashes/local extractors suffice.
- **security:** Default to local Mac extraction for files and browser bridge extraction for private pages; relay receives only selected encrypted payloads and metadata. Secrets, credentials, tokens, and private memory facts require explicit inclusion and should be excluded by default. Bind the approval to a manifest hash, encrypt per-owner key, log every source and redaction, and auto-delete the relay copy and download after a short TTL.
- **missing:** A cross-surface export manifest schema with source URL/path, timestamp, citation locator, sensitivity, content hash, and redaction reason.; A Mac-side local packager and browser-side authenticated extractor that stream selected content without exposing whole tabs or workspace.; Relay envelope encryption, one-time download/QR handoff, expiry and verified deletion receipts.; Dashboard review UI for approving individual sources/redactions before packaging.


## Changes it proposed to its own stack

### `mac-harness` — Add a truthful execution-verification layer that separates dispatch acceptance from world-state completion. Every Mac or browser step gets states queued, dispatched, transport-acknowledged, observed-confirmed, rejected, or unknown. For UI actions, require an independent postcondition (AppleScript/API readback where available, browser DOM/value readback, or explicit accessibility observation when the owner later enables it); if synthesized events are rejected or accessibility=false, emit unknown/recovery-needed rather than success. Reconcile the browser's offline pending-command queue by requestId/idempotencyKey, attach the result to the originating job, and expose a single evidence timeline to relay_job_status and the dashboard.
- **owner gets:** The owner stops hearing “done” when nothing changed, avoids repeating an action that may actually have happened, and can recover an offline browser or disconnected Mac job from a precise last-known state.
- effort: Medium-high: executor and browser bridge result schemas, postcondition adapters, queue reconciliation, durable tests, and dashboard timeline UI.  ·  risk: Some legitimate actions have no observable postcondition and will become unknown more often; recover by allowing an owner-confirmed observation or an explicit 'accepted but unverifiable' outcome. Never silently downgrade unknown to success.
- cost: Negligible API cost; mostly local I/O and occasional background summarization. No raw screen/audio data needs to leave the Mac.  ·  latency: Adds roughly 100–800 ms for local readback; browser verification may take one extra round trip. Irreversible actions remain gated, not delayed by model inference.
- security: Improves safety by preventing false completion. Store minimal evidence (selectors, hashes, URLs, timestamps), redact page content, and preserve the existing confirmation policy.
- depends on: A durable browser job runner with persistence/retry and result streaming (chg-16bc5dee is still incomplete).; Cross-node intent IDs and receipt reconciliation proposed above.; A per-action postcondition contract for existing mac_run_actions and browser_run_actions.

### `hardware` — For the production pendant, replace the prototype nRF9160-DK audio arrangement with a cellular/audio architecture that has independent DSP headroom and a proper 24 kHz microphone path: a modem SoC plus a low-power application/audio MCU (or a cellular SoC with a genuinely separate audio DSP), digital mic/codec clocked for 24 kHz, larger DMA/ring buffers, and a hardware fuel gauge. Keep the single-button interaction, but add a hardware mute/recording latch and expose audio/link/battery telemetry to the relay. Retain the ESP32 bridge only if its SBC/A2DP constraints remain acceptable; otherwise use a modern Bluetooth audio controller that supports the negotiated sample rate.
- **owner gets:** They get intelligible two-way wideband speech without the current 87%-CPU ceiling and 7.8 seconds of uplink loss during agent speech, plus trustworthy battery and mute behavior on an all-day wearable rather than a development board.
- effort: High: product board, RF/audio coexistence, enclosure, power design, firmware port, and measured end-to-end audio validation. Prototype first with an external audio MCU and current modem before committing to a custom RF board.  ·  risk: More components and RF certification complexity; clock drift, power draw, or Bluetooth interoperability could regress. Recover with an A/B prototype, retain the current narrowband firmware fallback, and gate rollout on packet-loss, latency, battery, and acoustic tests.
- cost: Engineering and certification dominate. Rough prototype BOM increase $20–$60 over the DK-like arrangement; likely additional 10–40 mW average depending on DSP/modem duty cycle, partially offset by shorter encode contention and better buffering. API cost unchanged.  ·  latency: Dedicated DSP should reduce encode/decode contention and jitter; larger buffers may add 20–60 ms unless tuned adaptively. LTE-M half-duplex remains a transport constraint, so this does not replace a link-aware bitrate governor.
- security: Hardware mute must be electrically enforceable and visibly indicated; fuel/audio telemetry should be authenticated and avoid storing raw audio except the existing failure-buffer policy. New firmware and boot chain require signed updates.
- depends on: An explicit 24 kHz end-to-end acceptance target and product audio compatibility decision.; Measured audio-path validation and fault injection across modem, relay, bridge, and headphones.; A link-aware duplex governor and truthful delivery receipts before claiming wideband reliability.

### `hardware` — Add a secure element to the production pendant and bridge, with a device-unique non-exportable key, monotonic counter, and signed attestation for conversation/export receipts. Have the pendant sign the initial capture hash and the bridge/relay append authenticated handoff records, so a later export can prove which device captured it, whether bytes were altered, and whether the pendant's local deletion/expiry command was acknowledged.
- **owner gets:** They can hand a sensitive dossier or incident record to someone else and know it is the exact one the pendant captured—not a silently edited transcript—and can verify that an expired copy was actually revoked from the system’s custody.
- effort: Medium-high hardware and firmware revision: secure-element driver, key provisioning, signed-counter protocol, relay verification, and recovery for device replacement.  ·  risk: Lost or damaged hardware could make old signatures harder to verify, and a bad counter protocol could brick attestation. Recover with an owner-held recovery key, rotation certificates, and a non-attested readable mode clearly labeled as such.
- cost: Approximately $0.50–$2.00 BOM increase plus provisioning and certification work; negligible runtime/API cost, with a few hundred bytes per signed receipt and modest I2C energy.  ·  latency: Usually under 100 ms per signature; batch receipt signing to avoid affecting live audio. No audio bytes should be synchronously signed.
- security: Strengthens provenance and deletion claims, but introduces key-management and supply-chain responsibilities. Keys must be generated on-device, never logged, and revocable; signed metadata must avoid embedding raw speech or secret content.
- depends on: The cited export capability and its manifest hash/redaction protocol.; A defined owner recovery/rotation policy.; Relay-side receipt verification and a dashboard trust indicator.


## What it asked for

_Nothing._
## Its own summary

I discovered the live state: Mac bridge online, browser offline with zero tabs, no new granted tools this round, and the owner’s priority remains shipping 24 kHz audio. I recorded two concrete next steps: (1) a cross-node intent/receipt continuity capability so dropped requests are deduplicated, resumed only from verified checkpoints, and reported honestly; (2) a truthful Mac/browser verification layer that distinguishes dispatch from observed completion and reconciles offline browser commands. I also proposed the production-hardware path needed for real 24 kHz duplex audio: separate DSP headroom, a native 24 kHz input path, hardware mute, fuel gauge, and better audio bridge.

**Biggest unknown:** The authoritative 24 kHz acceptance criteria and product audio compatibility target are still unavailable, so hardware and latency recommendations cannot yet be gated against measurable pass/fail thresholds. The durable browser runner and cross-node journal are also still missing; current receipts remain Mac-local and UI success can be unverifiable.

