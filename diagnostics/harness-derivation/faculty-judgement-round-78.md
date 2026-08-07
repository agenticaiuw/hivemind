# Harness derivation — faculty-judgement — round 78

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep private things private: when I say a secret, personal number, or anything in 'private mode', let me continue using the pendant and my Mac/browser without sending that content to the cloud or putting it in ordinary memory. Later, show me exactly what was withheld and let me explicitly reveal it if needed."
- **useful because:** The owner already has a secret accidentally captured in persistent state. A wearable is present for intimate speech, while the relay and models are the least appropriate places to retain it. This gives the owner a usable privacy boundary instead of requiring them to remember which surface is safe; it also lets private information participate in a local Mac/browser task through opaque references without exposing the value.
- **path:** pendant → relay-realtime → unified → mac-planner → browser-extension → dashboard
- **model tier:** Use on-device rules/classifier for wake-word/private-mode boundaries and obvious patterns; use the expensive realtime model only for the non-sensitive remainder. Use a cheap background model on the Mac to classify local text when the owner explicitly asks for review. Never send suspected secret spans to a model for classification.
- **latency:** Private-mode entry and local redaction must be immediate (<100 ms); ordinary speech keeps current streaming latency. A local Mac review of withheld spans can take seconds, but must never block the safe action path.
- **cost:** Negligible API cost for rule-based redaction and opaque handles; occasional cheap background classification on local Mac text. Main cost is implementation and encrypted local storage, not inference.
- **security:** False negatives could leak secrets, while false positives could make tasks frustrating. Default to withholding uncertain high-entropy spans and say 'I withheld a private-looking value.' Store only encrypted local ciphertext plus a hash/handle; relay receives redaction markers, not plaintext. Reveal must require an explicit spoken confirmation and show destination, exact value, and retention. Never log raw audio/transcript around a private span.
- **missing:** A pendant-local redaction/secret-span detector with a small encrypted ring buffer and explicit private-mode latch; A relay transcript protocol that carries typed redaction markers and opaque handles without reconstructing plaintext; A Mac-side encrypted vault/bridge that can substitute a handle into an approved local or browser action; A dashboard audit view and reveal workflow with retention/deletion controls; Cross-surface privacy acceptance tests, including dropped-link recovery and accidental secret utterances

### "Give me a genuinely private way to use the pendant: when I say 'private', I can dictate a secret or sensitive detail, have it used in one local task on my Mac or in a specific browser tab, and be certain it never entered the cloud transcript, ordinary memory, logs, or receipts."
- **useful because:** Today a secret can be accidentally captured into persistent personal state, and there is no end-to-end guarantee that a sensitive spoken span stays off the relay. The owner needs a practical privacy boundary that still permits useful local work, rather than having to avoid speaking sensitive information near the wearable.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → dashboard
- **model tier:** Use deterministic on-device boundary detection and redaction; do not send suspected sensitive spans to a classifier. Use a local Mac process for any optional classification or task preparation. Realtime inference handles only the redacted remainder.
- **latency:** Private-mode activation and redaction under 100 ms; local handle substitution under 250 ms. The owner should not wait for cloud inference before the secret is protected.
- **cost:** Near-zero incremental API cost; encrypted local storage and IPC are the dominant engineering costs. Optional local classification uses no cloud tokens.
- **security:** Fail closed on ambiguity: withhold rather than transmit. Use one-time, destination-bound handles with expiry, encrypted local plaintext, no raw values in logs or receipts, and explicit confirmation showing the exact destination before reveal. Physical clear must delete the pending envelope. Test dropped links, retries, replays, and malicious browser commands.
- **missing:** Pendant firmware support for pre-transmission redaction and a private-mode latch; A relay protocol that transports withheld spans only as opaque handles and never persists recoverable plaintext; Mac-local encrypted handle resolution restricted to one approved action; Browser-extension support for destination-bound handle substitution; An audit/deletion UI that reveals metadata without revealing values by default; End-to-end security tests and an owner-configurable retention policy


## Changes it proposed to its own stack

### `interaction` — Create a privacy-envelope protocol spanning pendant, relay, Mac, and browser: the pendant emits transcript chunks with local `public`/`withheld(handle)` labels; the relay forwards only public text and maintains no recoverable plaintext; the Mac agent can resolve a handle only inside a user-approved local action; browser commands carry handles plus a destination and expiration, never values; `/capture` stores only encrypted local envelopes and hashes. Add a visible audit stream showing each withheld, substituted, revealed, expired, and deleted envelope, with reveal requiring destination-specific confirmation.
- **owner gets:** The owner can speak naturally near the pendant without turning every secret into cloud memory, while still using a private value in a local form or browser workflow. They get a concrete answer to “what did you keep, where did it go, and who saw it?” rather than a privacy promise.
- effort: Medium-high: protocol/schema changes across firmware, relay, Mac bridge, and browser extension; local encrypted storage; test matrix for streaming interruption and retries.  ·  risk: A lost handle, classifier false positive, or expired envelope could interrupt a legitimate task; recover by offering local re-entry and an explicit override. A protocol bug could leak plaintext, so fail closed, redact logs, and add canary tests that assert secrets never occur in relay payloads.
- cost: No meaningful per-request API increase; modest local CPU/storage. Engineering cost is cross-surface integration and security review.  ·  latency: No added latency for ordinary speech; <100 ms local marking. Handle resolution adds one local IPC round trip (target <200 ms) before a Mac/browser action.
- security: Strongly improves least-privilege and retention. Requires encrypted-at-rest key management, replay-resistant one-time handles, destination binding, expiration, and no plaintext in receipts, logs, analytics, or model context.
- depends on: A pendant-local redaction/private-mode primitive; A typed relay transcript schema supporting withheld spans; A Mac-local encrypted handle resolver; Browser command schema accepting destination-bound opaque handles; Owner disclosure-boundary and retention policy


## What it asked for

### `s8-1520` (skill) — local_privacy_envelope_latch
- does: On the pendant, a long-press or spoken private-mode command marks subsequent audio/transcript spans as withheld before transmission. It detects obvious secret-like patterns locally, emits only redaction markers and one-time opaque handles, gives a distinct haptic/audio acknowledgement, and exits on explicit release or timeout. If the link drops, it keeps the latch state and never flushes withheld plaintext.
- must be on-device because: The security boundary is defeated if raw audio or transcript reaches the relay first. This must run before radio transmission and continue offline; the server cannot retroactively un-send a secret.
- trigger: Pendant button long-press, explicit private-mode voice command, or local high-confidence secret-pattern event; timeout/release exits. A physical stop/clear gesture must immediately discard the current withheld buffer.
- storage: Encrypted flash ring buffer for at most 8 withheld envelopes, each capped at 2 minutes or 32 KiB compressed audio, plus hashes/metadata and a 24-byte one-time handle. Auto-delete after 24 hours unless explicitly exported; no plaintext metadata beyond local encrypted storage.
- RAM budget: Target 18–28 KiB: streaming pattern state 4 KiB, envelope metadata 4 KiB, crypto buffers 8–16 KiB, haptic/UI state 2 KiB. No local speech model; use deterministic matching/VAD to stay well below the 211,608 B application RAM budget.

