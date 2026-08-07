# Harness derivation — unified — round 55

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Prepare this in the browser, and only submit it when I physically approve it on my pendant.”"
- **useful because:** The owner can delegate an entire authenticated transaction without trusting voice recognition, a Mac focus state, or a stale browser tab. The browser extension gathers the private page and stages the form, the Mac prepares local files or calculations, the relay keeps the job alive, and the pendant reads a compact before/after digest. A deliberate long-press on the device is the final presence-bound approval; walking away, a dropped call, or an ambiguous spoken 'yes' cannot submit by itself.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the cheaper background model for page extraction, form preparation, and evidence summarization; use realtime only to explain the pending transaction over audio. Deterministic relay/browser code enforces the approval token and commit gate.
- **latency:** Stage within 5–15 seconds for ordinary pages; approval response under 1 second after the pendant long-press, subject to browser round-trip. If the link is unavailable, retain the staged transaction and do not guess or submit.
- **cost:** About $0.01–$0.08 per staged transaction depending on page complexity; most cost is extraction and document drafting. Approval and commit are deterministic and essentially free.
- **security:** The relay must never receive raw secrets it does not need, and the approval token must be single-use, short-lived, bound to transaction hash, browser session, and pendant identity. Show target, recipient/account, changed fields, and attachments in the spoken/readable digest; require a second confirmation for money movement, deletion, or external sending. Encrypt staged evidence and expire it. A compromised browser extension must not be able to manufacture a valid pendant approval.
- **missing:** Pendant firmware support for a signed, transaction-hash-bound long-press approval and a clearly distinguishable haptic/LED/audio acknowledgement; A relay protocol and durable transaction store for prepare→review→approve→commit states with idempotent commit and receipts; Browser bridge support to freeze the exact tab/form revision and reject approval if any field, URL, recipient, or attachment changes; Mac bridge support to provide local attachments/calculations as cited artifacts without exposing unrelated files; Dashboard and recovery UI for inspecting, editing, expiring, or cancelling staged transactions

### "“While I was away, tell me exactly what the whole system observed and changed, in order, and prove which parts are still uncertain.”"
- **useful because:** Today activity is split across relay jobs, Mac actions, private browser tabs, and pendant interactions, so the owner cannot reconstruct a trustworthy account after an unattended job or link drop. This capability produces one tamper-evident causal timeline: pendant interaction anchors, relay transitions, Mac commands, browser tab revisions, artifacts, and delivery receipts are joined, with explicit gaps and conflicts rather than a confident invented summary. The owner can ask from the pendant and open the cited evidence on the Mac.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic event normalization, hashes, and causal-link checks first; use a cheaper background model to summarize the verified timeline. Use realtime only when the owner asks through the pendant and needs a short spoken answer.
- **latency:** Timeline updates should be appended in under 2 seconds after each receipt; a spoken reconstruction should begin within 2 seconds and complete in 5–10 seconds. If a surface is unreachable, report the gap immediately rather than waiting indefinitely.
- **cost:** Approximately $0.005–$0.03 per reconstruction; storage/indexing and hashing dominate, while model cost is limited to summarization of already-filtered events.
- **security:** Audit records may expose private URLs, mail metadata, file names, and voice-derived text. Encrypt per-owner, minimize payloads, redact secrets before indexing, enforce retention/erasure, and distinguish signed device/bridge receipts from model claims. A missing or invalid receipt must be visible and must never be silently synthesized.
- **missing:** A shared append-only event envelope with source identity, monotonic sequence, wall-clock timestamp, causal parent, payload hash, sensitivity label, and receipt status; Relay-side durable event journal and reconciliation service that detects duplicates, gaps, clock skew, and contradictory state transitions across Mac and browser; Mac and browser harness hooks that emit before/after artifact references for every action, not merely a success string; Pendant firmware support for a local interaction anchor and offline receipt queue; A dashboard/evidence viewer that can reveal the exact cited artifact or mark it unavailable, with owner-controlled retention and deletion


## Changes it proposed to its own stack

### `hardware` — Add a low-power secure element with device-unique key and monotonic counter, plus a clearly tactile two-stage approval control (or force-sensitive long-press-capable button) and a distinct haptic actuator to the production pendant. Firmware signs transaction-hash-bound approval/cancel events inside the secure element; the current single LED remains a secondary status signal. Keep the prototype path compatible by using its one button/LED and server-issued nonce, but mark those events lower-assurance until the secure element exists.
- **owner gets:** The owner can approve a sensitive browser action by touch and know that the approval was generated by the pendant they are wearing, even if the Mac UI is hidden, the voice link is noisy, or a browser tab was hijacked. Haptic feedback makes approval and cancellation unambiguous in a pocket or noisy room.
- effort: Moderate hardware spin and firmware/relay protocol work: select and qualify an I2C/SPI secure element, add the actuator and enclosure control, provision keys, and implement signed nonce/counter verification plus manufacturing/recovery procedures.  ·  risk: Provisioning or secure-element failure could strand approvals; retain a cancel/retry path and factory recovery, never silently fall back to submit. A false long press must be rejected with timing/debounce and require an explicit pending state. Prototype and production assurance levels must be visible in receipts.
- cost: Roughly $2–$8 incremental BOM depending on secure element, actuator, and enclosure revision; negligible per-approval API cost. A few mA only during haptic feedback and brief signing; otherwise sleep current remains near baseline.  ·  latency: About 50–200 ms for signing and relay verification; no meaningful impact on ordinary conversation.
- security: Strongly improves transaction authenticity and replay resistance, but introduces key provisioning, secure boot/firmware update, and lost-device revocation requirements. Do not store browser credentials or page contents on the device.
- depends on: physical_transaction_approval_latch protocol; durable prepare→approve→commit transaction state machine; browser revision/hash binding and idempotent commit receipts


## What it asked for

### `s10-j9l4` (skill) — physical_transaction_approval_latch
- does: When a staged transaction is pushed to the pendant, the device enters a clearly marked pending state. A deliberate 1.5-second hold of the single button followed by release emits exactly one approval event containing the staged transaction nonce; a short press cancels. The LED uses a distinct slow-double-flash pending pattern and a rapid flash for approved/cancelled. It never submits anything itself; it only emits an offline-safe, replay-resistant approval/cancel event when linked, or retains the decision until reconnect.
- must be on-device because: The important property is physical presence and an intentional gesture on the object the owner is wearing. A server, voice model, browser tab, or Mac cannot honestly provide that guarantee. It must also work during a transient audio/voice disconnect and survive a dropped link without turning uncertainty into submission.
- trigger: Server push of a staged transaction plus a button hold/release event on the pendant; no periodic schedule.
- storage: One pending record and a small append-only decision queue in flash: nonce (32 B), hash (32 B), expiry/counter/status (~32 B), plus up to 16 queued decisions (~2 KB). Clear records after receipt or expiry.
- RAM budget: ~8–12 KB worst case: state machine, queue, nonce/hash buffers, and transport framing. No crypto-heavy page data or audio buffering. Reuse existing button/LED and link tasks; budget must be validated against the 211,608 B application RAM, with a compile-time guard.

## Its own summary

This round added a genuinely new cross-surface capability: prepare an authenticated browser transaction across browser/Mac/relay, but require a physical, transaction-hash-bound pendant approval before commit. I also queued the pendant approval-latch firmware skill and proposed a production secure-element plus tactile/haptic control change. Still needed: the durable prepare→review→approve→commit protocol, browser revision binding/idempotent commit receipts, Mac artifact isolation, and production pendant hardware/secure-key provisioning. No further context is required this round; the current device is only a prototype with one button and one LED, so prototype approvals must be clearly lower assurance until the hardware exists.

**Biggest unknown:** Whether the production pendant can add a secure element and haptic/two-stage control; without that, the prototype can demonstrate the workflow but cannot provide strong physical-presence assurance.

