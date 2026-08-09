# Harness derivation — faculty-action — round 156

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “do it,” make the change on my Mac or in my logged-in browser, then tell me only after you independently prove the requested result happened—and give me a one-tap/one-press undo if it is reversible."
- **useful because:** This is the core trustworthy hand: the pendant starts the intent, the relay preserves it, Mac/browser executes it, and perception verifies the postcondition instead of mistaking an executor receipt for reality. The owner gets fewer silent failures and can safely delegate multi-step work while away from the screen.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception
- **model tier:** Realtime only for the short spoken acknowledgement; background/local planner for execution and verification.
- **latency:** Acknowledge within 1 s; complete ordinary actions within 15 s; verify immediately and retain an undo window for 30–120 s.
- **cost:** Usually one cheap planner call plus local Mac/browser work; verification is read-only and should avoid model calls unless visual interpretation is needed. Dominant cost is multi-step planning, not transport.
- **security:** Never send page secrets or screenshots to the relay by default; verifier returns hashes/minimal snippets. High-risk or irreversible actions remain staged behind the existing physical approval latch. A failed or ambiguous verification must be reported as unknown, never success.
- **missing:** A first-class action_id/attempt_id correlation field shared by executor receipts and verify_operation_step; A durable undo-window coordinator that can invoke existing job undo routes after verification; A policy mapping action classes to auto-run versus physical approval

### "Use my pendant as a physical-presence key: if it is connected over USB or LTE and I deliberately confirm on it, allow a sensitive Mac/browser action; if the pendant disappears or the confirmation expires, stop and leave the action staged."
- **useful because:** A stolen browser session or unattended Mac should not be enough to send a message, publish, or approve a consequential change. The wearable gives the owner a physical boundary that the Mac and browser cannot manufacture, while still allowing ordinary low-risk automation.
- **path:** pendant → relay → mac-planner → browser-extension → unified
- **model tier:** No expensive model is needed for the cryptographic/presence check; use realtime only to explain what is waiting or why it was blocked.
- **latency:** Presence and nonce validation under 500 ms when USB-connected; under 3 s over LTE; expiry configurable, default 60 s.
- **cost:** Negligible inference cost; engineering is protocol and firmware integration. USB serial is testable now even before LTE registration.
- **security:** Use challenge/response with monotonic counter and expiry, never transmit form secrets or page contents to firmware. Disconnect, replay, digest mismatch, and timeout must fail closed. This complements rather than replaces physical_transaction_approval_latch.
- **missing:** A presence-attestation protocol over the existing USB serial links and later LTE; A relay/device-status route that reports connection freshness and challenge state; Binding of action risk classes to required pendant presence

### "Fill in and submit a sensitive web form for me without ever showing or sending the secret to the AI: use the credential already stored on my Mac, tell me exactly which site and fields will receive it, let me approve on the pendant, and leave a local proof of what was submitted."
- **useful because:** The owner currently has to choose between tedious manual form entry and handing an AI access to passwords, payment details, or identity data. This makes the browser a controlled local hand: the Mac/extension handles secrets, the relay carries only a redacted intent, and the pendant is the physical approval boundary.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → faculty-perception
- **model tier:** Cheap local planner and browser automation for field mapping; realtime model only for the brief spoken summary. Secrets never enter model context.
- **latency:** Preview in 2 seconds, owner approval within 60 seconds, submission and local receipt within 5 seconds after approval.
- **cost:** Low inference cost; most work is local DOM/Keychain integration and a verifier. No secret-bearing cloud request should be made.
- **security:** Strict origin binding (scheme, registrable domain, and frame), field-label and value-class allowlists, no screenshots or DOM values containing secrets uploaded, clipboard forbidden, one-use approval nonce, and fail closed on redirects, autocomplete ambiguity, or changed fields. Submission of an irreversible form still requires the existing physical approval latch.
- **missing:** A browser-extension primitive for local secret-provider access that returns only typed field metadata and a redacted submission receipt; A Mac-local Keychain/credential broker with origin and field-purpose policy; A verifier that can attest the final origin, field names, and value fingerprints without returning values; A pendant preview format that fits site, action, and field summary without exposing the secret

### "Before anything on my Mac or in my browser sends data to another person or service, show me on the pendant a compact “what leaves this device, where, and why” summary; let me approve the exact digest, and block the send if the content or destination changes."
- **useful because:** The owner cannot currently see or control the real data boundary of automation: a browser upload, email, form, or API call can include hidden attachments, tracking parameters, or stale fields. This gives a wearable, last-moment egress decision without exposing the whole private payload to the model.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → faculty-perception
- **model tier:** Local deterministic inspection and hashing first; a cheaper model may summarize already-redacted metadata. Realtime is only for the short approval dialogue.
- **latency:** Inspect and present a summary in under 2 seconds; block immediately on mismatch; preserve a pending transaction for 2 minutes.
- **cost:** Low API cost; CPU/storage for local hashing and destination/attachment inspection dominate.
- **security:** Content stays on the Mac. The relay receives only destination, data classes, byte counts, and hashes. Must cover browser uploads, email attachments, clipboard, and common API calls; unknown channels fail closed for protected action classes. Approval is one-use and origin-bound.
- **missing:** A Mac-local outbound-egress interception layer for browser and approved AppleScript actions; A canonical redacted manifest schema for destination, content classes, attachments, and hashes; Browser and Mail adapters that can pause before commit and resume only with the matching approval nonce


## Changes it proposed to its own stack

### `interaction` — Add an owner-facing “unknown, not failed” recovery loop: when Mac/browser execution finishes but independent verification cannot establish the postcondition, pause all dependent steps, preserve the exact action and evidence provenance, and ask the pendant whether to retry, inspect, or cancel. Never automatically retry potentially duplicating an external side effect.
- **owner gets:** Today an ambiguous network/UI result can lead either to a false success or a dangerous duplicate submission. The owner gets an honest status and a safe next choice, especially for messages, purchases, and form submissions.
- effort: Medium: state-machine changes in action ledger/job runner plus a compact pendant prompt and verifier result schema.  ·  risk: Adds pauses to workflows and may leave a legitimate action staged. Recover by exposing the original job, evidence hashes, and explicit retry/inspect/cancel choices; retries require idempotency or renewed confirmation.
- cost: Low API cost; mostly local state and one verification call. No hardware cost.  ·  latency: Adds at most one verification round; ambiguous cases intentionally wait for owner input.
- security: Improves safety by preventing blind retries and false completion; evidence must remain redacted and sensitivity-tagged.
- depends on: verify_operation_step; truthful action status and receipt correlation; existing physical_transaction_approval_latch for retry of high-risk actions

### `integration` — Create a durable, owner-readable “data boundary ledger” that records every approved outbound operation as a tamper-evident local record: destination, purpose, content-class manifest, digest, pendant approval nonce, and independent post-send evidence—without storing raw secrets or message bodies by default.
- **owner gets:** When the owner later asks “what did you send and to whom?”, the system can answer from evidence rather than memory or an executor log. It also makes unexpected data exposure discoverable and supports revocation or incident review.
- effort: High: requires interception adapters, a signed local ledger, retention controls, and read-only query/UI on the Mac and pendant.  ·  risk: Incomplete instrumentation could create false confidence. Every record must state coverage and unknowns; if an operation bypasses an adapter, it must be marked unobserved rather than clean.
- cost: Small local storage and hashing cost; no raw payload transmission and minimal inference cost.  ·  latency: A few milliseconds for manifest/hash creation; adapter pauses are bounded by the approval timeout.
- security: Improves auditability but creates sensitive metadata. Encrypt at rest, restrict queries, redact destinations where appropriate, and provide owner-controlled retention/deletion.
- depends on: The outbound egress interception capability; The existing physical approval latch; Independent postcondition verification


## What it asked for

_Nothing._
## Its own summary

Recorded three non-duplicate actions: (1) cross-node “do it and prove it” execution with independent postcondition verification and reversible undo; (2) pendant physical-presence attestation for sensitive Mac/browser actions, using the USB-connected hardware now and LTE later; (3) an interaction change that treats unverifiable outcomes as UNKNOWN, halts dependent steps, and asks retry/inspect/cancel rather than duplicating side effects. I also asked faculty-perception to standardize action_id/attempt_id provenance.

**Biggest unknown:** I still need the owner’s policy data, not an invented default: which action-risk classes may run automatically, which require the existing physical approval latch, and the preferred expiry/undo windows. Engineering-wise, the missing seams are shared action/attempt correlation, a durable undo-window coordinator, and a challenge-response presence protocol over USB/LTE. No further permission request is needed this round.

