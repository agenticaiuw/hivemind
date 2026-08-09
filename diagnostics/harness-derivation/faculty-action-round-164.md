# Harness derivation — faculty-action — round 164

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do it, and prove every step—or recover safely if one fails.” For any multi-step Mac/browser task, execute a checkpointed saga: prepare, perform one idempotent step, independently verify its postcondition, then continue; on failure or ambiguous receipt, stop, run only a declared compensation, and tell me on the pendant whether it is completed, partially completed, or unknown."
- **useful because:** Today an executor receipt can say a click or send was attempted without establishing what actually happened. This would make the system trustworthy for consequential workflows (messages, purchases, file moves, calendar changes) and prevent blindly repeating a step after a timeout.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use the realtime tier only for the owner's live question and final status; use a cheaper background model to compile the step DAG and compensation plan. faculty-perception performs read-only verification, not the executor.
- **latency:** First reversible step within 2–5 seconds; 1–3 seconds per verify checkpoint. Pause immediately on ambiguity rather than consuming a long retry budget.
- **cost:** Roughly 2–6 cheap planner/verifier calls per workflow plus one realtime response; Mac/browser execution dominates wall time, while verification snippets and receipts dominate tokens.
- **security:** Never claim success from executor receipts alone. Each step carries an idempotency key, expected postcondition, sensitivity class, and compensation. Private/secret evidence stays on the Mac/browser; relay receives hashes or minimal snippets. Irreversible steps still require the existing physical transaction approval latch.
- **missing:** A saga/DAG and compensation schema extending the existing operation record; Action/attempt correlation fields on verify_operation_step; A library of idempotency and compensation adapters for Messages, Calendar, Finder, and browser forms; Owner policy for which risk classes may run automatically versus staged

### "“Watch this logged-in page and act when the condition becomes true—ask me on the pendant only when my approval is needed.” The relay should schedule a condition check, wake the Mac/browser bridge to inspect the live session, prepare the action without submitting it, and deliver a compact preview plus a physical approve/cancel request; after approval, execute once and verify the resulting page state."
- **useful because:** This turns the private browser session into an assistant that can handle deadlines such as appointment openings, ticket releases, price thresholds, check-in windows, or application status changes without the owner repeatedly checking a screen. The browser session never has to leave the owner's machine.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap scheduled/background model for polling and condition extraction; use realtime only for the owner's spoken setup and the approval prompt. Use perception for DOM/state evidence and action for the final submit.
- **latency:** Polling cadence is user-selected (for example 30 seconds to 5 minutes); once a condition matches, notify within 2 seconds and submit within 5 seconds after physical approval.
- **cost:** Background polling can be mostly local and cheap; one model call on state transitions, plus one realtime approval exchange. Mac wakeups and browser inspection are the dominant operational cost, not tokens.
- **security:** Store only a site/field locator, condition, expiry, and session binding—not cookies, passwords, or page contents in the relay. Require a fresh physical approval nonce for every submit, reject stale previews after the page changes, and independently verify URL/field/result after submission. Provide a hard expiry and a one-button cancel path.
- **missing:** A durable relay condition-monitor scheduler with backoff and expiry; Browser-side inspect-only commands that can safely evaluate a narrow condition without leaking full page content; A preview hash binding the prepared action to the exact observed page state; Owner-configurable polling limits and per-site action policy

### "“Use my pendant today even when LTE is not registered.” When the nRF9160 and ESP32 are connected over their known USB serial ports, the Mac should provide a local transport that discovers both chips, forwards button/audio/status traffic to the relay, and exposes the same durable outbox/inbox semantics as the eventual LTE path; switching between USB and LTE must not duplicate or lose an action."
- **useful because:** The hardware is physically on the owner's desk now, but the device table has no registered pendant. This would make the wearable testable and useful immediately—button capture, downlink speech, approval LEDs/audio, queued memos, and action status—without pretending an LTE path exists.
- **path:** mac-planner → mac-terminal → relay-realtime → unified → faculty-action
- **model tier:** No expensive model for transport. Use a cheap/background process for serial framing, health, and queue draining; use realtime only for spoken interactions and action summaries.
- **latency:** Button/status events should reach the relay in under 150 ms over USB; reconnect and queue reconciliation within 3 seconds. Audio remains on the already-verified 24 kHz path.
- **cost:** Negligible API cost; one persistent local process and serial I/O. Engineering cost is in framing, reconnection, and end-to-end test fixtures rather than inference.
- **security:** Bind ports by USB identity rather than glob order, authenticate the local bridge, and keep credentials out of serial logs. Preserve monotonic IDs and checksums across transport changes; never execute an action merely because a queued serial frame was replayed. Require the existing physical approval latch for consequential actions.
- **missing:** A real serial-port/device-identity probe and framed nRF9160↔Mac and ESP32↔Mac protocol; A local bridge registration/heartbeat route that is distinct from LTE device registration; Crash-safe duplex queue reconciliation between pendant_store and relay jobs; An end-to-end USB test harness using the physically connected devices, without flashing firmware

### "“Fill out this form using my saved details, but keep every secret on the browser and show me exactly what will be disclosed before it is sent.” The Mac/browser node should resolve private identity, payment, and account fields inside the existing browser session, while the relay receives only field categories and redacted values; the pendant presents a short disclosure summary and the owner can approve or edit the disclosure set before submission."
- **useful because:** The owner could use private logged-in services without handing passwords, card numbers, or identity data to the relay or model context. It makes the hive materially safer than asking a general assistant to copy secrets through chat, while still saving the tedious work of form completion.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → faculty-perception → faculty-action
- **model tier:** Use a cheap local planner for field classification and deterministic browser automation; use realtime only to explain the disclosure summary and collect the owner's spoken edits. Never send raw secret values to a model.
- **latency:** Preview in 3 seconds after the page is inspected; local field filling under 2 seconds; submit only after the owner's deliberate confirmation.
- **cost:** Low inference cost; classification and redaction should be local/deterministic. Browser inspection and secure local storage dominate implementation cost, not API tokens.
- **security:** The browser extension must enforce an allowlist of secret field types and origin binding, with no raw values in relay logs, screenshots, receipts, prompts, or crash reports. A changed origin or form structure invalidates the preview. Submission needs a fresh physical approval nonce and an explicit expiry.
- **missing:** A browser-local secret-field broker that exposes write-only handles rather than values; Origin- and form-schema-bound disclosure manifests; A pendant rendering/audio vocabulary for categories such as identity, address, payment, and medical data; A secure local vault integration and redacted verification result

### "“Undo the last thing you did for me.” The system should identify the most recent completed action from the owner's spoken/session context, present the exact inverse and its scope, and execute that inverse on the correct Mac or browser surface—without guessing when the original result is ambiguous."
- **useful because:** An owner should not need to remember whether an action happened in Safari, Finder, Calendar, or Messages, nor reconstruct how to reverse it. A trustworthy conversational undo would make proactive automation feel recoverable instead of risky.
- **path:** unified → relay-realtime → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension
- **model tier:** Use a cheap model to retrieve and rank recent reversible actions; use realtime for the short clarification/confirmation exchange. Deterministic inverse adapters perform the actual undo; perception verifies the postcondition.
- **latency:** Identify the candidate in under 1 second; show scope in under 3 seconds; complete and verify a reversible undo within 5 seconds after confirmation.
- **cost:** One inexpensive retrieval/planning call and one verification call per undo; implementation effort is primarily inverse adapters and safe conflict handling.
- **security:** Never infer an inverse for an unknown or irreversible action. Bind the inverse to the original operation receipt and current resource version, warn if another application or person changed it, and require confirmation for destructive inverses. Keep message/file contents private in receipts.
- **missing:** A typed inverse-action registry for existing Mac and browser action kinds; Resource version/precondition capture at execution time; A concise owner-facing scope renderer on the pendant; Conflict detection when the original object has changed

### "“Why didn’t that happen?” The system should reconstruct a private, chronological incident report across pendant, relay, Mac, and browser: the owner's request, routing decision, each attempted step, link/device availability, the last trusted evidence, and the exact next recovery choice. It should answer in plain speech and offer one safe repair, rather than merely saying a job failed."
- **useful because:** Today failures are split across device status, relay jobs, browser commands, and Mac receipts. The owner cannot tell whether nothing was attempted, a browser session was unavailable, or an action happened but was not verified. Cross-node forensics would turn opaque failures into recoverable situations.
- **path:** unified → relay-realtime → faculty-perception → faculty-action → mac-planner → browser-extension
- **model tier:** Use a background model to normalize receipts into an event graph; use realtime only to answer the owner's question and speak the one recommended recovery. Perception supplies fresh state when historical evidence is insufficient.
- **latency:** Historical reconstruction under 2 seconds; one fresh probe under 4 seconds; never block the owner on an open-ended diagnostic loop.
- **cost:** One cheap summarization call per incident and occasional fresh probes; storage of compact hashes/timestamps is small. The dominant cost is implementing consistent event envelopes across nodes.
- **security:** Redact page contents, message bodies, credentials, and audio from the report unless explicitly requested. Clearly distinguish observed, inferred, and unknown facts. A recovery action must be separately authorized and must not be inferred from the diagnosis.
- **missing:** A shared cross-node event envelope with causal/request/attempt IDs and monotonic timestamps; A privacy-aware receipt projection that joins Mac/browser/device records without copying secrets; A recovery catalogue mapping failure classes to safe owner-visible repairs; Fresh availability and postcondition probes for each participating surface


## Changes it proposed to its own stack

### `relay` — Add a durable execution-cursor ledger that records operation_id, step_id, idempotency key, prepared-state hash, executor receipt, independent verification receipt, and compensation status. On reconnect or retry, the relay must resume only from the last verified checkpoint; a step with an unknown result is quarantined until faculty-perception rechecks it, and no blind replay is allowed. Expose the cursor state to relay_job_status and to the pendant's status channel.
- **owner gets:** A dropped connection or Mac restart will no longer make the owner wonder whether a message was sent twice, a file was moved, or a form was submitted. The system can honestly say “done,” “not done,” or “unknown—needs your choice,” and recover without duplicate side effects.
- effort: Medium-high: schema migration, atomic writes, idempotency adapters, retry/quarantine logic, and integration tests across Mac and browser executors.  ·  risk: A bad verifier or stale hash could quarantine safe work or falsely permit continuation. Recover by requiring fresh verification, retaining immutable receipts, and offering a manual owner-selected retry/compensate path; never delete an unknown cursor automatically.
- cost: Low storage and negligible API cost; verification calls add roughly 1–2 cheap calls per checkpoint. No hardware cost.  ·  latency: Adds about 0.5–2 seconds per checkpoint for persistence and verification; avoids much longer duplicate-action recovery.
- security: Improves auditability and prevents replay. Hashes and sensitivity labels should be stored instead of private page contents; secrets remain in the browser or Mac.
- depends on: verify_operation_step must accept operation/attempt correlation; Existing actionLedger and approvalHandoff should be extended rather than bypassed; A declared idempotency/compensation contract for each executor action


## What it asked for

_Nothing._
## Its own summary

Recorded four non-identical deliverables this round: (1) checkpointed, independently verified action sagas with compensation; (2) condition-triggered browser workflows that prepare but require fresh physical approval; (3) USB-tethered pendant operation so the physically connected nRF9160/ESP32 can work before LTE registration; and (4) the durable relay execution-cursor ledger needed to resume safely after disconnects. I also asked faculty-perception and mac-planner to identify the concrete verification and serial gaps. What remains needed from the owner/system is not another broad permission request: a real serial identity/framing probe, a USB bridge registration path, operation/attempt correlation in verification receipts, idempotency/compensation adapters, and the owner's risk-policy table. Accessibility/Screen Recording remains owner-controlled and is not required for the AppleScript/route-based portions.

**Biggest unknown:** Whether the currently connected USB devices expose an existing framed protocol and stable identities that can be used without firmware changes; no trustworthy serial probe or device table entry has been observed yet.

