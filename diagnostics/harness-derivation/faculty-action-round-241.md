# Harness derivation — faculty-action — round 241

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser reachability** — As of 2026-08-09T01:14:17Z, AI Pendant Agent has Accessibility and Screen Recording granted, synthesized input verified, Safari is foreground, and the Safari extension is online with 1 pending command and staleForMs 4697. This supersedes the older denied/unavailable snapshot for this live host.
  - evidence: GET /observe and GET /browser/status both returned HTTP 200 with these fields.

## Capabilities it proposed

### "Make the change, and don't stop until you can prove it is true—or tell me exactly what blocked it."
- **useful because:** Today an action receipt can mean only that a click or command ran. This capability makes the system complete the loop: Mac/browser execution, an independent fresh postcondition check, bounded repair when safe, and a truthful pendant outcome. The owner gets one answer—verified, blocked, or unknown—instead of silently trusting an executor.
- **path:** relay-realtime → faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension
- **model tier:** Use the realtime model only to interpret the spoken goal and communicate; use the cheaper local planner for the step graph and repair attempts, with perception verification after every mutation.
- **latency:** First action within 2 seconds; each verification under 1 second; at most 3 automatic reversible repairs or 30 seconds total before asking the owner.
- **cost:** One low-cost planner call plus 1–3 small verification calls; dominant cost is any browser vision fallback, avoided when typed app/file/browser postconditions suffice.
- **security:** Never treat executor receipts as proof. Each step carries an expected postcondition and sensitivity; private/secret evidence stays hashed or on-device. Irreversible steps remain staged behind the existing physical transaction approval latch. On timeout, report unknown rather than retrying blindly.
- **missing:** A durable step graph that links executor action IDs to verify_operation_step calls and records repair attempts; A policy table defining which reversible failures may auto-repair; default must be stage-for-approval; A relay-to-pendant compact status envelope for verified/blocked/unknown plus the existing tactile beacon

### "Do this later when it won't interrupt me, but ask again if anything important changed."
- **useful because:** A deferred action should not execute merely because its timer fired. This capability waits for an owner-approved quiet window, rechecks the Mac calendar and browser/session state immediately before acting, compares the original plan with fresh context, and uses the pendant for a compact reauthorization only when risk or context changed. It prevents an innocuous request made yesterday from becoming a surprising action today.
- **path:** relay-realtime → faculty-judgement → faculty-action → faculty-perception → mac-planner → browser-extension
- **model tier:** A background/local planner owns waiting, calendar polling, and typed diffs; realtime is used only for the initial request and an exception conversation. Browser extraction and state comparison stay on the Mac.
- **latency:** No polling more often than every 5 minutes; preflight within 2 seconds of the eligible window; reauthorization response can remain pending for 24 hours without losing the job.
- **cost:** Low: scheduled local checks and one planner call at execution time. Costs rise only if a changed context requires a new browser inspection or owner dialogue.
- **security:** The job stores a minimal intent digest, not page secrets or message contents. Calendar titles and browser fields are sensitivity-labeled. If the deadline, target, session, or risk tier changes, execution pauses; the pendant's deliberate approval is required for any newly risky or irreversible step. Expired jobs are cancelled, never silently run late.
- **missing:** A durable deferred-job record with eligible window, deadline, intent digest, context fingerprints, and reauthorization state; Typed calendar quiet-window and context-diff reads exposed to faculty-perception; A relay scheduler that can wake the Mac agent and route a changed-context approval to the pendant

### "I missed that—play your last answer again."
- **useful because:** The owner can miss a response because of traffic, movement, or a dropped earbud even when delivery succeeded. A pendant-local repeat control gives immediate recovery without repeating the question or spending another model turn. The rotary encoder coming in the product direction supplies selection without overloading sw0/sw1: turn/press to choose the last one of up to three responses, then a deliberate press replays it.
- **path:** pendant → ESP32 audio bridge → relay-realtime → faculty-action → mac-planner
- **model tier:** No model call for replay. The relay stores only a compact index and the existing audio artifact; firmware handles selection and playback locally, with a cheap relay lookup only when the artifact is no longer cached.
- **latency:** Start playback under 150 ms when cached; under 2 seconds after a relay fetch. Keep a 3-item local index and resume from the beginning unless the owner explicitly scrubs.
- **cost:** Near-zero inference cost; storage and LTE transfer dominate only when the requested artifact is not already on the bridge/pendant failure-path cache.
- **security:** Replay is read-only and never executes an action. Expired or private artifacts require the same delivery authorization as the original; do not expose transcript text to firmware. Deduplicate playback acknowledgements and delete fetched copies under the existing audio retention policy.
- **missing:** A rotary encoder and second deliberate button in the jewellery enclosure (the current DK's sw0/sw1 are already spoken for); A tiny pendant/bridge replay index that references existing artifact IDs, codec/rate, expiry, and checksum; A relay read route that fetches an already-delivered artifact by opaque ID and enforces the existing audio delivery acknowledgement and offline retry rules

### "Show me exactly what you would change, let me inspect the likely result, and then apply that same change only if the world has not changed."
- **useful because:** The owner gets a genuine preview of a multi-surface action rather than a vague confirmation. The system constructs a read-only rehearsal from the current Mac/browser state, identifies affected records and postconditions, then pins a short-lived state fingerprint. After physical approval it refuses to execute if the target changed, preventing stale-tab edits, wrong-recipient messages, or applying a file operation to a moved file.
- **path:** relay-realtime → faculty-judgement → faculty-perception → faculty-action → mac-planner → mac-vision → browser-extension
- **model tier:** A cheaper local planner creates the typed rehearsal and diff; perception gathers current state; realtime only explains the preview and asks for approval. No expensive model call is needed during the final commit unless the fingerprint has changed.
- **latency:** Preview in 3 seconds for typed app/file/browser targets; approval-to-commit under 2 seconds; state pin expires after 60 seconds or any detected relevant mutation.
- **cost:** One planner call and bounded read-only inspections; screenshots/vision are the dominant cost and should be used only where typed locators cannot express the target.
- **security:** The rehearsal must not mutate, send, or submit. Secrets and private page values are represented by hashes and redacted labels. The physical approval binds to the exact rehearsal digest, target scope, and expiry; any mismatch becomes a safe abort with a compact explanation.
- **missing:** A typed dry-run representation with affected-target summaries and expected postconditions; A short-lived cross-surface state fingerprint covering app/file/browser targets; An executor commit gate that accepts the approved rehearsal digest and rejects stale or broadened plans

### "Before you do it, tell me if the different places you checked disagree with each other."
- **useful because:** Important actions often span surfaces whose facts drift independently: a browser shows one price or recipient, Mail shows another, and a local file or calendar contains a third. This capability builds a cross-surface contradiction report before execution instead of choosing whichever source was inspected last. The owner can resolve the disagreement deliberately, while harmless agreement proceeds without a conversation.
- **path:** faculty-perception → faculty-judgement → faculty-action → mac-planner → mac-vision → browser-extension → relay-realtime → pendant
- **model tier:** Use a low-cost structured comparison model for normalized fields and provenance; reserve realtime for explaining a conflict and collecting the owner's choice. No model is needed when typed values agree exactly.
- **latency:** Under 4 seconds for up to five sources; conflicts remain staged until resolved, with no automatic retry that could hide a disagreement.
- **cost:** Small comparison call plus read-only source inspections. Browser vision is the main variable cost and is avoided for typed fields.
- **security:** The report carries source labels, timestamps, and hashes rather than raw private content by default. A conflict cannot be resolved by silently trusting a newer-looking page; source authority must be explicit per field. Sending, purchasing, deleting, or editing remains behind the existing physical approval boundary.
- **missing:** A normalized fact schema with field-level source authority and freshness rules; A contradiction detector that preserves provenance across Mac, browser, and relay observations; A pendant-friendly conflict choice protocol that returns the selected source or explicit cancellation


## What it asked for

_Nothing._
