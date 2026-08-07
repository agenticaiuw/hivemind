# Harness derivation — unified — round 81

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“While I’m away from my Mac, capture this thought on the pendant; when the Mac is reachable, file it into my AI-Pendant-Workspace with the time, location-free provenance, and a short searchable title, then tell me exactly where it went.”"
- **useful because:** This is a genuinely wearable-to-desktop workflow: the pendant is the only always-with-owner capture surface, the relay can hold it while the Mac sleeps or the LTE-M link drops, and the Mac is the only node that can safely organize the workspace. It turns fleeting spoken thoughts into durable, reviewable notes without pretending the pendant can run filesystem automation.
- **path:** pendant → relay → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime model only for the initial short capture confirmation and title suggestion; a cheaper background model should normalize/transcribe and classify the note, while the Mac agent performs deterministic file creation. No browser or expensive realtime turn is needed after capture.
- **latency:** Pendant acknowledgement under 500 ms with a local receipt; relay durable acceptance under 2 s when connected; filing may wait until the Mac reconnects and should normally complete within 1 minute. If the link is unavailable, preserve the capture and say it is queued rather than claiming success.
- **cost:** Roughly $0.001–$0.01 per note depending on audio transcription/model use; storage and relay invocations dominate only at high volume. Mac filing is local and free.
- **security:** Voice content leaves the pendant over LTE-M to the relay unless an offline-only mode is selected. Do not infer or store location. Workspace writes are reversible but should use atomic create-with-unique-id and receipts; never overwrite an existing note. Any secret-like content needs sensitivity marking and should not be echoed in spoken confirmation. Mac filesystem access remains bounded to ~/AI-Pendant-Workspace.
- **missing:** A durable pendant capture spool with sequence numbers and retry/ack semantics; A relay note-ingest endpoint that returns an immutable receipt and deduplicates retries; A Mac-side workspace filing action with atomic writes and a completion receipt; A compact transcription/title pipeline and a user-visible queued/ filed state; An explicit retention and deletion policy for captured audio versus derived text


## Changes it proposed to its own stack

### `integration` — Add an append-only capture-to-action ledger shared by pendant, relay, and Mac. Each voice capture or requested action gets a monotonic device sequence, relay receipt, SHA-256 payload hash, current owner-visible state (captured, uploaded, transcribed, filed, failed), and parent/child links when one capture creates multiple Mac/browser actions. Retries must reuse the same event ID; the Mac filer commits its filesystem write and receipt in an idempotent outbox transaction. Expose a compact reconciliation endpoint so reconnecting pendants and the dashboard can show the first missing state rather than replaying or claiming completion.
- **owner gets:** The owner stops wondering whether a spoken note or computer action happened twice, vanished during LTE-M loss, or was filed without confirmation. A single short receipt can say exactly what was accepted and what remains queued, even after a crash or reconnect.
- effort: Medium-high: protocol schema and migration, relay durable store, small firmware sequence/ack changes, Mac outbox/reconciliation, and failure-injection tests across reconnect and power loss.  ·  risk: A schema or clock mistake could strand events or create false completion. Recover with append-only records, versioned envelopes, bounded replay, and a repair command that never performs an irreversible action. Filesystem writes remain temp-file-plus-rename and duplicate-safe.
- cost: Negligible model/API cost; modest relay durable-storage and log volume (small metadata per event, audio retained separately under an explicit TTL).  ·  latency: One metadata acknowledgement adds tens of milliseconds on a live path; filing latency is unchanged except during reconciliation. Audio payloads should not wait for the full ledger commit before local acknowledgement.
- security: Hashes provide integrity, not secrecy. Encrypt sensitive payload metadata at rest, redact spoken text from general logs, and keep the ledger scoped to the owner's bearer identity. Never put secret note contents in dashboard URLs or spoken receipts.
- depends on: A durable capture spool and relay note-ingest contract (not yet granted); A Mac workspace filing action with atomic receipt (not yet granted); A documented retention policy for raw audio and derived text; Existing /pipeline/events, /jobs/:jobId/receipts, and Mac action receipt infrastructure

### `hardware` — Design the production pendant with a hardware-backed device identity and tamper-evident capture path: a secure element for per-device keys and monotonic counters, encrypted external QSPI storage for a bounded local event journal, and a physical privacy circuit that cuts microphone power independently of firmware. Bind every uploaded audio/event envelope to the secure-element signature and counter; the relay rejects cloned or replayed envelopes and the owner can revoke one pendant without rotating the whole fleet.
- **owner gets:** The owner can trust that a spoken thought or approval came from the pendant they are actually wearing, survives a dropped connection without silently disappearing, and is truly private when the mute control is engaged—even if firmware crashes or the relay account is compromised.
- effort: High: select and qualify a secure element and QSPI part, redesign the pendant PCB and power domains, add manufacturing provisioning and revocation service, implement encrypted journal wear-leveling and signed envelopes, and validate recovery under brownouts and flash failure.  ·  risk: Added parts and provisioning complexity could make units harder to manufacture; flash wear or a lost key could strand queued captures. Recover with bounded ring storage, key escrow only for device replacement (never plaintext audio), signed firmware migrations, and a factory reset that explicitly destroys the old identity.
- cost: Approximately $2–$6 additional BOM per unit, plus provisioning/revocation infrastructure; QSPI adds a few milliamps only during writes, while the secure element's standby draw is negligible. No per-request model cost.  ·  latency: Signature generation and journal commit add tens of milliseconds to event acknowledgement, but the pendant can acknowledge locally before LTE-M upload. Microphone mute is immediate in hardware.
- security: Substantially improves authenticity, replay resistance, and local privacy. It creates a high-value device key, so provisioning, revocation, backup, and physical teardown procedures must be treated as security-critical. Encrypted storage protects queued content at rest but does not replace retention controls.
- depends on: A versioned signed event-envelope protocol shared by firmware and relay; Relay-side device enrollment, revocation, and replay-counter validation; The product pendant hardware replacing the current nRF9160 DK prototype; A documented policy for queued audio retention and device replacement


## What it asked for

_Nothing._
