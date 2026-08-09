# Harness derivation — faculty-action — round 186

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I set the pendant down, make the computer stop speaking private responses and pause any pending action; when I pick it up again, restore the session only after I deliberately resume it."
- **useful because:** The owner gets a physical privacy curtain and a safe pause gesture without hunting for a Mac control. A dropped or unattended pendant cannot continue voicing sensitive content or leave a staged action armed.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** background for wear-state policy; realtime only for the immediate state transition
- **latency:** Lock within 500 ms of a stable set-down signal; resume state visible within 2 s of pickup and explicit resume gesture.
- **cost:** Negligible per event; one small realtime event and no model call for the common path. Background model cost only when explaining an interrupted workflow.
- **security:** IMU state is local and should emit only coarse worn/away transitions, never raw motion. Set-down must fail safe: mute speech and invalidate pending approvals. Pickup alone must not authorize anything; require sw1 resume. Missing: IMU firmware integration and relay-to-Mac privacy/pause hooks.
- **missing:** pendant IMU driver and set-down/pickup classifier; relay privacy-curtain event and pending-action invalidation hook; Mac audio/session pause plus browser/job pause integration; owner-configurable stability timeout

### "When I tap the bookmark button, save not just a timestamp but the exact work context I was in—active app, browser URL/title, current relay session, and a short spoken label—so later I can ask what I bookmarked and reopen that context."
- **useful because:** A physical tap becomes a reliable memory of why the owner interrupted themselves. It bridges the pendant's moment to the Mac and browser state that otherwise disappears, without storing a continuous recording.
- **path:** pendant → relay → mac-bridge → browser-extension → dashboard
- **model tier:** realtime for the tiny spoken label; background for indexing and summarizing the captured context
- **latency:** Acknowledge the tap locally in under 100 ms; capture Mac/browser snapshot within 2 s; retrieval should answer in under 3 s.
- **cost:** One short transcription plus a small metadata record per bookmark; no audio upload unless the owner explicitly speaks a label. Storage is a few KB per event.
- **security:** Browser URL/title may contain secrets; redact query strings and allow per-domain exclusion. The device outbox should carry only an opaque bookmark ID and label, not page contents. Reopening must be staged if it would navigate or mutate state. Missing: atomic cross-surface snapshot correlation and a retrieval command.
- **missing:** bookmark event envelope carrying monotonic ID and capture deadline; Mac active-app and browser snapshot endpoint with URL redaction; relay joiner that correlates pendant ID, pipeline/session, and Mac snapshot; query/reopen flow with verification and approval

### "Do this multi-step task across my Mac and browser as one transaction: if a later step fails, automatically undo every reversible earlier step, leave irreversible steps staged, and tell me exactly what is committed versus still pending."
- **useful because:** This is the system's most valuable action capability: the owner can delegate real workflows instead of isolated clicks without fearing half-completed work. It turns the Mac, browser session, relay, and perception verifier into one accountable hand.
- **path:** relay → mac-planner → mac-terminal → mac-vision → browser-extension → faculty-perception → pendant → dashboard
- **model tier:** background planner for decomposition; realtime only for owner clarification and final concise status
- **latency:** Start execution within 2 s; each step may take normal tool latency; emit a durable checkpoint after every step and recover after link loss.
- **cost:** Planner call plus cheap verifier calls per step; dominant cost is browser/Mac execution, not inference. Receipts and checkpoints are small JSON.
- **security:** Classify every step before execution. Require physical approval for irreversible or externally visible actions. Never claim rollback succeeded from executor output alone: faculty-perception must verify each compensation postcondition. If verification is unavailable, report unknown and stop. Missing: dependency-aware compensation graph, per-step pre/post snapshots, and a commit ledger that spans Mac and browser.
- **missing:** compensation graph and idempotency keys in the job schema; precondition/postcondition capture for each step; cross-surface commit ledger with verified/unknown states; rollback executor that can pause at irreversible boundaries; pendant summary protocol for committed, undone, and unknown counts

### "Before anything leaves my Mac or browser, show me a private risk summary: exactly what data, destination, account, and attachments would be transmitted, with secrets detected and removable. Let me approve the cleaned version from the pendant without exposing the content to the relay."
- **useful because:** The owner gets a practical outbound-data firewall instead of hoping an automation did not leak a token, private document, or message to the wrong account. It works across authenticated browser sessions and local Mac files, where the relay cannot see the underlying secrets.
- **path:** mac-terminal → mac-vision → browser-extension → faculty-perception → faculty-judgement → relay-realtime → pendant
- **model tier:** Background model for local classification and redaction suggestions; realtime only for the short risk summary and physical confirmation exchange.
- **latency:** Risk summary within 2 seconds for ordinary text and 5 seconds for a document; never transmit until the local inspection and owner decision are complete.
- **cost:** One local classification pass per outbound action; relay receives only hashes, field labels, and a redacted summary. Cost is dominated by local document inspection, not API tokens.
- **security:** The unredacted payload must remain on the Mac/browser. The relay and pendant receive only a digest, destination identity, sensitivity labels, and proposed redactions. Approval must bind to the exact payload hash, recipient, and account, expiring on any change. Missing: local outbound interception points, secret/PII detector, redaction editor, and hash-bound approval envelope.
- **missing:** Mac and browser outbound inspection hooks for messages, uploads, and form submits; local secret/PII classification and reversible redaction engine; hash-bound redacted-payload approval protocol; post-submit verifier that confirms the approved recipient and payload hash

### "Before acting in a website or sending a message, verify that the browser is using the account and workspace I intended—not merely the right URL—and stop if the identity, organization, permission level, or environment differs."
- **useful because:** Wrong-account actions are among the most costly failures an automation can make. The owner gets an identity boundary that catches personal/work, production/test, and similarly named organizations before a click becomes an external side effect.
- **path:** browser-extension → mac-vision → mac-planner → faculty-perception → relay → pendant
- **model tier:** Cheap local rules and page-state inspection for normal checks; background model only when the account or workspace label is ambiguous.
- **latency:** Identity check under 500 ms from a page snapshot; block immediately when expected identity is absent or contradictory.
- **cost:** Near-zero for known domains using local selectors and cached account fingerprints; occasional model classification for unfamiliar sites.
- **security:** Never send passwords, cookies, or full page content to the relay. Store only salted account/workspace fingerprints and visible identity labels. Treat an unknown identity as deny-by-default, and require a fresh physical approval if the owner explicitly overrides it. Missing: per-site identity declarations, browser account fingerprinting, and an action gate before submit/navigation.
- **missing:** owner-maintained identity/workspace expectations per domain; browser-side account and organization fingerprint extraction; pre-mutation identity gate integrated with planner and browser commands; safe override envelope bound to the inspected tab and expiry

### "Remember commitments I make in conversation, then watch my calendar, mail, and task surfaces for the right moment to prepare a follow-up draft with the original promise and evidence. Never send it automatically; let me approve or dismiss it from the pendant."
- **useful because:** The owner gets an assistant that closes loops instead of merely recording notes: promises made while walking become timely, grounded follow-ups when the relevant meeting or deadline arrives.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-judgement → faculty-perception
- **model tier:** Background model extracts commitments and schedules watch conditions; realtime only captures a commitment during a live exchange.
- **latency:** Capture in the current turn; evaluate triggers hourly or on calendar/mail events; draft in under 10 seconds once triggered.
- **cost:** One small extraction call per likely commitment and cheap scheduled checks; no continuous transcript retention. Mac-side indexing dominates.
- **security:** Store only the commitment, due window, parties, and source reference—not whole conversations. Email/calendar content stays on the Mac. Drafts are never sent without explicit approval bound to recipient, body, and attachments. Missing: commitment schema, event watchers, provenance links, and pendant inbox presentation.
- **missing:** durable commitment records with source and confidence; calendar/mail/browser watcher and deduplication service; local evidence retrieval and draft generation; pendant inbox with approve/dismiss/snooze gestures


## Changes it proposed to its own stack

### `firmware` — Enable i2c2 and integrate the owned LSM6DSOX plus DRV2605L into a low-power gesture/status service: classify stable set-down, pickup, and deliberate sw1 confirmation locally; drive distinct haptic patterns for pending, success, failure, and unknown; publish only signed coarse events with monotonic counters.
- **owner gets:** The pendant becomes understandable and safe without looking at a tiny LED: it can tell the owner whether an action is waiting, completed, failed, or cannot be verified, and setting it down immediately creates a privacy boundary.
- effort: Moderate firmware work: devicetree/CMake integration, I2C drivers, calibration, a small classifier, haptic pattern table, event framing, and bench tests over the currently connected USB serial hardware. No new parts.  ·  risk: False set-down or pickup transitions could mute or resume at inconvenient times; require stability hysteresis and sw1 resume. I2C faults must degrade to LED/audio status without blocking recording. Do not flash until separately approved.
- cost: No meaningful API cost. Existing hardware; roughly 1–3 mA average sensor overhead depending on accelerometer duty cycle, plus brief motor pulses.  ·  latency: Local gesture decisions under 100 ms; haptic acknowledgement under 150 ms. Small periodic sensor work consumes some CPU but should be far below the measured audio budget if interrupt-driven.
- security: Improves safety by making pending actions physically observable and refusing pickup-as-approval. Signed monotonic event counters prevent replay; raw motion never leaves the pendant.
- depends on: relay privacy-curtain and pause hooks; physical_transaction_approval_latch amendment for haptic semantics; bench firmware build/flash approval and device identity provisioning


## What it asked for

_Nothing._
