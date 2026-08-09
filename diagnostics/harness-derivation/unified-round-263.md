# Harness derivation — unified — round 263

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Am I private right now?”"
- **useful because:** The owner gets a plain answer backed by one authenticated convergence receipt, rather than trusting that a local latch, relay queue, browser exposure, or playback path happened to stop. It explicitly distinguishes latched, link-unreachable, and verified-stopped.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic on relay; realtime only to phrase the result over the pendant
- **latency:** under 2 seconds; no model call needed for the verdict
- **cost:** negligible API cost; one read-only convergence check and compact status reads dominate
- **security:** Never expose audio or page contents in the answer. Bind the receipt to latchId and device identity; if any surface cannot be authenticated, say UNKNOWN rather than PRIVATE. No mutation or automatic unlatching.
- **missing:** wire privacy_convergence_check into the owner-facing voice/status path; a stable latchId-to-device identity binding; dashboard rendering for the receipt and its failed surface

### "“Show me everything you inferred about me, and forget this one everywhere.”"
- **useful because:** It makes the owner’s existing retention decision real: extracted facts become inspectable, individually deletable, and traceably removed from derived graph copies and evidence capsules, while preserving action history. Off-machine deletion is honestly reported as requested-and-pending.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background model only to render a recognizable summary; deterministic IDs, deletion scope, and receipts
- **latency:** list under 1 second; local erase under 3 seconds; replicated erase may remain pending
- **cost:** low; CRUD reads/writes and one deletion receipt dominate, with no audio model call
- **security:** Require explicit confirmation for erase; never return raw evidence unless requested. Scope by fact ID, not free-text similarity. Preserve job history but cryptographically link the erase receipt to every deleted derivative; redact relay payloads in dashboard.
- **missing:** a read route for extracted facts with provenance capsules; one cascade-delete operation spanning facts.json, context graph, derived copies, and relay/R2 tombstones; a pending off-machine erase status and retry sweep; dashboard and pendant presentation of fact IDs

### "“The Mac restarted while you were doing that. Tell me exactly what is safe to continue, then continue only the safe parts.”"
- **useful because:** This is the owner-facing recovery behavior missing today: it separates completed, idempotently replayable, approval-required, and unsafe-to-repeat steps, so a crash no longer means either silent loss or accidental duplicate messages/purchases/edits.
- **path:** relay → mac-bridge → pendant → dashboard
- **model tier:** deterministic planner/ledger engine; background model only for a concise explanation
- **latency:** recovery plan under 2 seconds after bridge reconnect; execution begins only after explicit owner confirmation for unsafe steps
- **cost:** low; ledger/workbench reads and a lease sweep dominate, with no realtime model call
- **security:** Gate on replaySafety, not reversibility: auto-resume only idempotent/additive steps with valid leases; ask for physical_transaction_approval_latch or next-conversation approval for unrepeatable/unknown or high-risk steps. Never infer completion from a missing receipt. Add relay job leases and close ordinary ledgers before enabling any automatic scan.
- **missing:** orchestrator closeLedger integration; relay_jobs lease_until and expiry/requeue sweep; startup scan that invokes existing planResume and workbench transaction recovery; a pendant-readable recovery summary and explicit approve/cancel binding; separate approval authority from the AGENT_TOKEN

### "“Keep this conversation local-only until I say otherwise.”"
- **useful because:** The owner can deliberately have a private working mode in which audio, transcripts, browser contents, and Mac observations are prohibited from leaving the local trust boundary. Unlike muting, this preserves the conversation while preventing cloud/relay persistence and browser exposure. Every response carries a machine-verifiable local-only receipt, and the mode survives link loss without silently falling back to cloud processing.
- **path:** pendant → mac-bridge → relay → browser → dashboard
- **model tier:** deterministic policy enforcement; realtime model only if local inference is available, otherwise refuse rather than violate the contract
- **latency:** mode activation under one second; each turn’s boundary check under 50 ms
- **cost:** low recurring cost for policy checks; potentially high local compute cost because cloud inference is disallowed
- **security:** The policy must be enforced before capture upload, not inferred after the fact. Browser snapshots, relay logs, audio spools, and model prompts need explicit deny gates. If any required surface cannot attest enforcement, the pendant must announce LOCAL-ONLY UNAVAILABLE and not capture. Existing bearer-token possession must not count as attestation.
- **missing:** a signed data-residency policy token propagated from pendant to Mac and relay; pre-upload admission gates for audio, transcript, browser, and context extraction; a local model/runtime or an explicit refusal path when cloud inference is required; per-turn deletion of temporary local artifacts and an auditable no-persistence receipt


## Changes it proposed to its own stack

### `hardware` — Add a normally-closed, physically visible microphone power-cut control to the eventual pendant: a slide/shutter or guarded switch that removes microphone bias at the hardware boundary, with a GPIO sense line so firmware and the relay can report its state. The software privacy latch remains the conversational control, but this control must dominate it: if open, no capture path can power up, regardless of firmware, modem, or relay state.
- **owner gets:** The owner can know—and physically enforce—that the pendant cannot hear them, even if firmware crashes, the relay is compromised, or the single LED is ambiguous. This turns privacy from a status claim into a property the wearer can verify by touch and sight.
- effort: Prototype on the DK with a load switch/MOSFET and a GPIO sense; then design into the product audio front end and enclosure. Requires firmware boot/self-test, latch-state reconciliation, and a dashboard/voice state that refuses to claim listening when the hardware switch is unknown.  ·  risk: A badly chosen switch can add mic noise, leakage, or a pop when reopening; an open switch makes voice unavailable until deliberately restored. Recover by defaulting to capture-disabled on disagreement, debouncing and ramping mic bias, and exposing a clear hardware-fault state. It must not be presented as secure against a physically modified device.
- cost: Prototype roughly $1–$4 in switch/load-switch/indicator parts and a few PCB traces; negligible steady-state power, with only leakage in the microamp range. Product enclosure and certification cost dominate.  ·  latency: Privacy cut is immediate at hardware response time; reopening may need tens of milliseconds for mic bias stabilization and calibration.
- security: Strongly improves fail-closed privacy and reduces reliance on bearer-token or relay honesty. It does not authenticate the owner or protect already-captured audio, so retain the existing latch and deletion/retention rules.
- depends on: owner product decision on whether a tactile privacy control is acceptable; final microphone and enclosure design rather than the provisional nRF9160 DK; local_privacy_latch firmware integration; privacy_convergence_check reporting hardware-switch state

### `interaction` — Introduce explicit contract badges for every owner-facing response: LOCAL-ONLY, CLOUD-PROCESSED, STORED, or NOT-VERIFIED. The badge is generated from signed provenance at capture and delivery boundaries, not from model narration, and the pendant speaks a short warning whenever the requested contract cannot be met.
- **owner gets:** The owner can tell at a glance whether an answer was private, sent off-device, retained, or merely claimed to be safe. This prevents the most dangerous failure mode in a multi-surface assistant: a fluent answer hiding an unknown data path.
- effort: Add provenance fields to pipeline and browser events, propagate them through relay receipts and Mac jobs, define a small policy evaluator, and render/speak the badge. Requires integration tests that deliberately drop the relay or browser bridge.  ·  risk: Badge drift or missing provenance could create false confidence. Fail closed to NOT-VERIFIED, never infer LOCAL-ONLY from link absence, and retain the raw audit record separately from user content.
- cost: Small storage and bandwidth increase for signed metadata; negligible model cost. Implementation spans relay, Mac, browser, and pendant firmware.  ·  latency: Single-digit milliseconds for local evaluation; signing and receipt propagation may add tens of milliseconds.
- security: Improves data-boundary transparency but does not itself encrypt or prevent capture; it must be paired with admission gates and the privacy latch.
- depends on: a signed cross-surface provenance envelope; local-only policy enforcement; audio and browser pipeline event schema changes; owner-facing dashboard and pendant rendering


## What it asked for

_Nothing._
