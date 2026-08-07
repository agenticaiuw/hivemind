# Harness derivation — faculty-action — round 120

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **device availability** — The live device discovery currently reports home-macbook-bridge online and Safari on MacIntel online, but no registered pendant; this conflicts with the system's statement that nRF9160 and ESP32 chips are physically connected over USB serial. Any action feature must support an unregistered local-tether state or reconcile the registry before claiming pendant reachability.
  - evidence: discover(devices) returned only Safari on MacIntel, home-macbook-bridge, and offline cloudflare-contract-test; system note lists /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA as physically connected.

## Capabilities it proposed

### "Do this for me, safely: carry out my spoken goal across my Mac and logged-in browser, and use a physical button press on the pendant as the final confirmation whenever the action would send, submit, delete, or buy. Then tell me exactly what happened."
- **useful because:** This is the clearest path from a voice decision to a trustworthy real-world action: the Mac/browser can reach private sessions, while the worn button is a deliberate confirmation channel that cannot be triggered by an accidental spoken phrase. Receipts make the result auditable.
- **path:** pendant → relay-realtime → unified → faculty-judgement → faculty-action → mac-planner → browser-extension → dashboard
- **model tier:** Realtime for the short spoken goal and confirmation prompt; background/cheap model for plan validation and receipt summarization.
- **latency:** Under 2 seconds to show the pending confirmation on the pendant after planning; under 10 seconds for reversible actions, with long browser jobs continuing asynchronously.
- **cost:** ~$0.01–$0.05 per invocation; realtime turn dominates, while receipt and precondition checks should use a cheaper model.
- **security:** Private page contents stay in the browser/Mac boundary. The relay receives only a redacted action summary and nonce. Require a fresh short-lived nonce, visible LED/button state, state hash precondition, and explicit confirmation for send/delete/purchase; never treat a stale button press as approval.
- **missing:** pendant registration and button/LED command path; physical confirmation firmware skill; action lease and state-proof verification; planner-to-action protocol that carries irreversible checkpoints; browser and Mac adapters exposing before/after state hashes

### "Save what I am looking at for later."
- **useful because:** A single phrase should turn the owner's current private Safari context into a portable handoff capsule: URL, title, selected or salient text, timestamp, and a short spoken label. It uses the browser's authenticated reach and the pendant's physical presence, then remains useful even when the browser tab is gone or the pendant link drops.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-action → dashboard
- **model tier:** Realtime only for intent recognition and a one-sentence confirmation; a cheaper background model extracts and labels the page.
- **latency:** Capture acknowledgment in 1 second; capsule enrichment within 15 seconds and available as a queued audio item later.
- **cost:** ~$0.005–$0.02 per save; extraction and summarization dominate, and should be cached by page fingerprint.
- **security:** The capsule can contain sensitive logged-in content. Store encrypted locally by default, retain the minimum excerpt, attach source URL/time, and ask before syncing beyond the Mac. Never include passwords, tokens, or hidden form fields.
- **missing:** one command to bind a request to the active Safari tab; local encrypted capsule store and deduplication; pendant button/LED acknowledgment and offline queue; cross-surface handoff route from browser bridge to Mac notes/files and relay audio queue

### "Undo the last thing you did, but only if it is still safe."
- **useful because:** The owner should be able to recover from an action without remembering which app or tab it touched. A receipt-aware inverse can verify that the world still matches the post-action snapshot, refuse if another change occurred, and explain precisely what it would restore.
- **path:** pendant → relay-realtime → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension → dashboard
- **model tier:** Realtime for resolving “last thing” and speaking the result; deterministic checks and inverse execution should not consume a large model.
- **latency:** Safety check and spoken yes/no within 3 seconds; inverse may run as an asynchronous job when multiple surfaces are involved.
- **cost:** ~$0.003–$0.02; state verification is deterministic, with model cost only for ambiguous receipt selection.
- **security:** Never undo based solely on recency. Require an immutable receipt, before/after snapshots, idempotency key, and unchanged-state proof; destructive inverses still require confirmation. Redact private content from spoken receipts and expire old undo leases.
- **missing:** per-action inverse descriptors for AppleScript/browser operations; before/after state hashes and verification route; dependency-aware undo for multi-step jobs; a physical or spoken confirmation policy for destructive inverses

### "Lock my private Mac and browser when I walk away, and unlock them only when my pendant is back with me and I tap its button."
- **useful because:** The owner's browser contains authenticated accounts and the Mac holds private notes, mail, and files. A wearable presence-and-tap authorization would protect those surfaces without relying on remembering to lock them, while avoiding the dangerous behavior of unlocking from voice alone.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** No expensive model for presence or locking; realtime only for exceptional spoken status questions.
- **latency:** Lock within 5 seconds of confirmed absence; unlock within 1 second of a valid local tap and presence proof.
- **cost:** Near-zero API cost. Hardware/security integration dominates.
- **security:** Never use proximity alone to unlock. Require a cryptographic pendant identity, recent local button tap, replay-resistant challenge, and owner-configured grace period. Revoke the device credential when lost; keep private page contents off the relay.
- **missing:** secure pendant identity storage or secure element; BLE/UWB or equivalent presence signal in addition to USB tethering; Mac login/session-lock integration and browser tab redaction/locking; credential rotation and lost-device revocation route; owner-visible audit log of lock/unlock events

### "Read whatever is currently in front of me on the Mac, one short piece at a time, and let me skip or revisit pieces with the pendant button."
- **useful because:** The owner could consume a long email, private webpage, terminal result, or document while walking, cooking, or unable to look at the screen. The Mac has reach into private sessions and the pendant supplies an always-available physical navigation control.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay-realtime → faculty-perception → faculty-action
- **model tier:** Cheap extraction/chunking model for ordinary text; realtime only for spoken control and ambiguous references.
- **latency:** First chunk in under 2 seconds; next/previous controls under 300 ms locally once queued.
- **cost:** ~$0.002–$0.02 per document depending on OCR and summarization; cache chunks by document fingerprint.
- **security:** Read only the explicitly foreground source; never sweep unrelated tabs or hidden fields. Keep extracted text on the Mac unless the owner asks for relay delivery, encrypt the queue, and expire it after playback.
- **missing:** foreground-app and selection extraction across Safari, Notes, Mail, terminal, and PDFs; pendant playback queue with next/previous/repeat button events; text-to-speech output path and interruption handling; screen-reading permission or equivalent accessibility-free adapters; source boundary and sensitive-field redaction

### "If my pendant is lost or stolen, revoke it immediately, stop it receiving queued audio or commands, and tell me the last trustworthy place and time it was seen."
- **useful because:** A wearable is an authorization device as well as an audio endpoint. The owner needs a single emergency action that prevents a found device from replaying private queued material or approving work, even when the pendant is offline.
- **path:** pendant → relay-realtime → mac-planner → faculty-perception → faculty-action → dashboard
- **model tier:** Deterministic security workflow; no model needed except a short spoken explanation.
- **latency:** Credential revocation and queue quarantine within 2 seconds when the Mac or relay is reachable; apply the quarantine on the pendant's next connection.
- **cost:** Negligible API cost; durable credential and event storage dominate.
- **security:** The emergency command must be available from the authenticated Mac/dashboard and require strong owner authentication, but must not reveal the bike-lock secret or other sensitive memories. Last-seen data must be coarse by default and tamper-evident.
- **missing:** device credential lifecycle and revocation list; pendant-side boot-time quarantine and queue wipe; last-seen attestation with trustworthy clock/source; a Mac/dashboard emergency control and recovery enrollment flow; separate recovery credential that does not depend on the lost pendant


## Changes it proposed to its own stack

### `firmware` — Add a USB-serial tether mode for the physically attached nRF9160/ESP32 pair: the Mac bridge can issue a nonce-tagged `prepare_confirmation` command, the pendant renders distinct pending/accepted/expired LED states, and only a debounced physical button event matching the nonce emits `confirmation_commit`; every event is ACKed with monotonic sequence and persisted until delivered. This mode must be disabled when LTE/relay mode is active unless explicitly selected.
- **owner gets:** They can use the pendant as a real, dependable action key today while it is attached to the Mac, instead of waiting for LTE registration; accidental voice commands cannot send or delete anything, and a dropped USB read cannot silently lose a confirmation.
- effort: Moderate firmware work across nRF9160 serial protocol and ESP32 bridge, plus Mac bridge adapter and a small simulator test matrix; no flash should occur without owner approval.  ·  risk: A stale or duplicated serial packet could approve the wrong operation; bind every event to a short-lived nonce, sequence, operation digest, and expiry, and fail closed. Recover by expiring the pending state and requiring a new preparation.
- cost: No recurring API cost; roughly $0–$20 if a USB test jig is needed. Negligible additional power while tethered.  ·  latency: LED pending state under 100 ms; button ACK under 250 ms; relay confirmation remains network-limited in LTE mode.
- security: Improves authorization by making confirmation local and nonce-bound; do not transmit page content, secrets, or raw audio over this protocol.
- depends on: pendant registration or a local USB device registry; the pending physical-confirmation policy and action lease; Mac bridge serial transport to /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; device-side monotonic event storage

### `hardware` — Add a small secure-element-backed identity and presence subsystem to the pendant: per-device signing key, monotonic anti-replay counter, challenge-response over USB today and BLE/UWB presence later, plus a tamper-evident lost-device quarantine flag. Keep private audio and page data out of the secure element; it stores only keys, counters, and state.
- **owner gets:** The pendant can become a trustworthy personal key for privacy and recovery, rather than merely another unauthenticated serial endpoint. If it is lost, the owner can revoke it without exposing queued commands or private audio.
- effort: High: board revision or secure-element daughterboard, bootloader integration, Mac/relay credential lifecycle, and recovery UX. Prototype over the existing USB serial chips before committing to a board change.  ·  risk: Bad provisioning or a corrupted counter could permanently strand the owner. Include an offline recovery credential, atomic counter updates, factory-reset enrollment, and a clearly documented replacement flow.
- cost: Approximately $2–$8 per device for a secure element and supporting parts; negligible runtime API cost and low power draw.  ·  latency: Challenge response adds tens of milliseconds locally; presence decisions depend on BLE/UWB sampling and should not block ordinary audio.
- security: Substantially improves resistance to replay, stolen-pendant use, and forged confirmation packets; requires careful key backup policy so private keys never leave the device.
- depends on: a defined device credential lifecycle; Mac and relay lock/revoke endpoints; pendant firmware update and bootloader path; owner recovery enrollment and audit UI


## What it asked for

_Nothing._
