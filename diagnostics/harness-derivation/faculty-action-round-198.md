# Harness derivation — faculty-action — round 198

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Submit this document to the site, but show me exactly what will be uploaded and give me a 30-second undo if the site supports it.”"
- **useful because:** This is the highest-value trust feature for a wearable agent: it turns a vague cross-surface request into a visible, bounded transaction. The Mac resolves the local file, the browser extension holds the authenticated session, the relay coordinates them, and faculty-action proves each postcondition instead of claiming success from a click receipt.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Use a cheap background model for file selection and a structured diff; use realtime only to explain the diff and collect the owner's decision. No expensive model is needed for execution or verification.
- **latency:** Prepare in under 5 seconds; approval summary under 2 seconds after preparation; browser submission under 10 seconds; verification within 3 seconds. The 30-second undo timer begins only after independent postcondition verification.
- **cost:** Roughly $0.01–$0.05 per transaction depending on document inspection; browser/Mac calls dominate latency, not tokens.
- **security:** Never send file contents or form secrets to the pendant. Display filename, byte size, SHA-256, destination origin, fields to be populated, and a redacted content summary. Require the existing physical approval latch for submission. Undo must be offered only when a verified compensating action exists; otherwise say non-reversible before approval. Expire the plan and bind it to the exact file hash, browser origin, and session.
- **missing:** A structured prepare response that returns a human-readable upload diff and exact file hash without exposing secrets; A transaction coordinator that binds Mac file selection, browser session/origin, approval nonce, executor receipts, and verifier evidence; A capability check for whether the submitted site exposes a safe compensating action, rather than promising undo generically

### "“I missed that—play your last answer again.” (Turn the pendant wheel back one click, or use the new second button.)"
- **useful because:** The owner can recover a complete answer without repeating the question or reaching for the phone. This is different from link retry: every byte may have arrived, yet the owner may have been distracted or missed speech. The pendant is the only surface that knows the replay gesture at the moment it is wanted.
- **path:** pendant → relay-realtime → mac-planner → faculty-perception → faculty-action
- **model tier:** No model call for replay. The relay serves the already-generated, content-addressed audio artifact; use a cheap model only if the artifact has expired and a text transcript must be re-synthesized.
- **latency:** Start audible replay within 500 ms when cached at relay; within 3 seconds if the relay must fetch the artifact from durable storage.
- **cost:** Near-zero for cached replay; at most one inexpensive TTS regeneration when the artifact is retained as text but audio has expired.
- **security:** Bind replay to the owner's active conversation and an opaque response ID, not a global last-response key. Never replay another session's audio. Enforce an expiry and a bounded replay count, and record playback start/interruption using the existing delivery acknowledgements. A physical gesture selects replay only; it cannot approve an action.
- **missing:** Firmware integration for the owner's planned rotary encoder/second button and a replay gesture state machine; A relay INBOX index retaining recent response IDs, transcript/audio codec and expiry under 1 KB per entry; A delivery verb that requests an existing response artifact without invoking a new model turn

### "“Stop—this is not what I meant.” (Say it or press the pendant's cancel control while a multi-step task is running.)"
- **useful because:** Cross-surface actions can be locally successful yet globally wrong. A fast interruption boundary prevents the next dependent step, captures exactly what has happened, and tells the owner whether the partial state is reversible. It is safer than blindly undoing or letting a queued browser/Mac workflow continue.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-perception → faculty-action
- **model tier:** Realtime handles the short interruption utterance; deterministic routing stops queued work. A background model may summarize the partial-state evidence after the stop, but is not on the critical path.
- **latency:** Stop dispatch of not-yet-started steps within 250 ms of the pendant event; acknowledge locally within 300 ms; produce a verified partial-state report within 5 seconds.
- **cost:** Usually under $0.01; the dominant cost is fresh Mac/browser verification and any compensating action, not inference.
- **security:** The stop signal must be authenticated to the active operation and monotonic, so a stale replay cannot cancel a later task. It must stop future steps even if it cannot reverse completed ones. Do not expose form secrets in the pendant acknowledgment. Any compensation requires a new approval for a different risk-bearing operation; never auto-delete or send a second mutation just because the owner said stop.
- **missing:** A first-class operation cancellation endpoint that propagates to both Mac job queue and browser command queue; A per-step execution fence so queued dependent steps cannot start after cancellation; A partial-state evidence bundle combining executor receipts with verify_operation_step results and explicit unknowns

### "“Show me the exact page as it will look after you fill it in, without submitting anything.”"
- **useful because:** A field list and text diff are not enough for forms whose meaning depends on layout, selected options, hidden defaults, or an attachment preview. The owner should be able to inspect a sanitized, local rendering of the authenticated browser page with proposed values overlaid, then approve or revise before any mutation. This lets the pendant mindfully delegate a high-stakes web task without exposing the live session or secrets to the pendant.
- **path:** browser-extension → mac-vision → mac-planner → faculty-perception → faculty-judgement → faculty-action → relay-realtime
- **model tier:** Use deterministic DOM capture and rendering first; a cheap model may summarize visual differences. Realtime is only needed if the owner asks questions about the preview.
- **latency:** Generate a sanitized preview in 3 seconds for a normal form; updates after one owner correction in under 1 second; never submit as part of preview generation.
- **cost:** Low, typically <$0.01; browser capture and local rendering dominate rather than model tokens.
- **security:** Preview must be generated in the browser/local Mac and sent as redacted structure or pixels with secrets masked; never upload credentials, tokens, or private page contents to the relay or pendant. Bind preview to a session, origin, form fingerprint, and expiry. Approval must cover the exact preview hash; any DOM or origin change invalidates it.
- **missing:** A browser-side read-only snapshot-and-overlay operation that can render proposed values without dispatching input or submit events; A secret-redaction policy for screenshots and DOM snapshots, including password fields, tokens, and hidden inputs; A preview hash and invalidation protocol that faculty-action can check before submitting

### "“Watch this page and, when the price or availability changes, prepare the action—but do not submit or send anything until I approve the exact new state.”"
- **useful because:** The owner gets the benefit of persistent attention without granting a standing authorization. The browser keeps the authenticated session, the relay watches while the Mac is asleep, perception detects a real state change rather than polling text blindly, and action prepares a fresh transaction that expires if the page changes again.
- **path:** relay-realtime → browser-extension → mac-planner → faculty-perception → faculty-judgement → faculty-action → pendant
- **model tier:** Use a cheap scheduled/background model or deterministic field comparator for monitoring; use realtime only when notifying the owner or answering a question. Never spend the expensive tier on every poll.
- **latency:** Polling cadence owner-selected (for example 1–5 minutes); stage a notification within 10 seconds of a confirmed change; approval and execution remain interactive.
- **cost:** A few cents per day at ordinary polling intervals, dominated by browser/session wakeups; near-zero model cost with structured comparators.
- **security:** Monitor only an owner-selected origin and locator, with a bounded schedule and automatic expiry. Store hashes/values needed for comparison, not whole pages. A detected change creates a new operation nonce; previous approval can never carry over. Rate-limit and respect site terms; require explicit approval before every mutation.
- **missing:** A durable relay-side watch with schedule, origin/locator, comparator, expiry, and backoff; A browser read-only snapshot operation that can compare a field across sessions without causing side effects; A staging notification that binds the observed change to a new approval transaction and invalidates on further change

### "“If the site logs me out, pause here and tell me exactly what I need to re-authenticate; after I log back in, continue from the verified step without repeating or double-submitting anything.”"
- **useful because:** Authenticated browser sessions expire at the worst moment. Today an agent can leave a half-completed task ambiguous or repeat a mutation after re-login. A resumable handoff would preserve the operation's step boundary, let the owner handle authentication privately in the browser, and continue only after fresh postconditions prove what already happened.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → faculty-perception → faculty-action → pendant
- **model tier:** Deterministic state machine and receipts on the critical path; a cheap model can explain the re-authentication request. No model should receive credentials or decide whether a prior mutation occurred.
- **latency:** Detect an auth wall within 2 seconds; notify immediately; after re-authentication, revalidate in under 5 seconds before resuming the next step.
- **cost:** Low; browser polling and verification dominate. No additional model call is needed for ordinary resumes.
- **security:** Never capture or transmit passwords, MFA codes, cookies, or page secrets. Pause with a cryptographically bound operation/step cursor. On return, require origin/session revalidation and independent verification of the last step; if evidence conflicts, enter unknown and require a new approval rather than retrying. Expire abandoned cursors.
- **missing:** A browser auth-wall detector that reports only redacted reason/origin, never credentials; An idempotent step cursor and resume protocol shared by relay, Mac, and browser queues; A duplicate-submission guard that binds retries to prior verified state and operation hash


## Changes it proposed to its own stack

### `firmware` — Integrate the existing LSM6DSOX and DRV2605L on i2c2 with a small rotary-encoder/second-button input protocol: wheel detents select among pending replayable response IDs or staged action summaries; sw1 short press selects/replays, long press cancels; haptic patterns distinguish selection, pending, verified, unknown, and cancelled. Persist only opaque IDs and cursors in the existing INBOX/OUTBOX manifest.
- **owner gets:** The pendant becomes usable without a screen or spoken re-query: the owner can recover a missed answer and make an unambiguous choice among pending actions while wearing it. Haptics provide private feedback that works in a pocket and matches the jewellery form factor.
- effort: Medium firmware work: enable i2c2, add sensor/DRV2605L drivers and debounce/state machines, then integrate the owner's planned encoder hardware and test offline queues. No new chip is needed for IMU/haptics; the encoder and second button are still procurement/mechanical work.  ·  risk: False detents or sensor bus faults could select the wrong item. Default every ambiguous gesture to no-op, require a deliberate sw1 hold for approval, reject stale IDs, and watchdog/reinitialize i2c2. If the encoder is absent, retain current two-button behavior.
- cost: About $5–$15 for an encoder and button if not already purchased; negligible incremental power while idle, with short haptic bursts adding tens of millijoules per interaction.  ·  latency: Local feedback under 100 ms; no network round trip for selection. Replay still depends on relay availability.
- security: The pendant receives opaque IDs and redacted labels only; it never receives page contents or secrets. Physical selection is not approval unless it follows the existing transaction latch gesture.
- depends on: Owner's rotary encoder and second-button hardware/mechanical design; Existing physical_transaction_approval_latch and tactile_action_outcome_beacon firmware work; Relay support for the replayable response-ID index; i2c2 devicetree enablement and driver integration


## What it asked for

_Nothing._
## Its own summary

Recorded four non-duplicate items this round: (1) proof-carrying document submission with exact upload diff, physical approval, independent verification, and conditional undo; (2) owner-initiated replay of the last answer using the planned wheel/second button; (3) authenticated stop-now interruption that fences future Mac/browser steps and reports verified partial state; and (4) firmware integration of the existing IMU/haptic hardware plus planned encoder for private, screenless selection and replay. What I still need is not another generic action route: I need the encoder/second-button mechanical choice, a relay response-artifact index and replay verb, an operation cancellation fence spanning Mac jobs and browser commands, and a structured prepare/diff plus compensating-action capability. I also need faculty-perception to return fresh evidence for each partial step so action can distinguish verified, unknown, and merely receipt-backed outcomes.

**Biggest unknown:** Whether the owner's planned rotary encoder and second button have a selected electrical/mechanical part and event protocol; without that, firmware can integrate the existing IMU/DRV2605L but cannot honestly finalize the gesture mapping.

