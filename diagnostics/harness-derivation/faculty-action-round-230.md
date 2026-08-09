# Harness derivation — faculty-action — round 230

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Stop the thing you just started—immediately, everywhere."
- **useful because:** A long-running Mac or browser action can become unsafe or simply wrong after it starts. Today the owner has no pendant/voice-level kill path that propagates to every executor and produces a truthful stopped-versus-unknown result. A single abort command would be the most useful action safety capability: it beats waiting for a browser timeout or trying to regain GUI control.
- **path:** relay-realtime → relay → pendant → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** Realtime only to interpret the explicit stop utterance; cancellation propagation and receipt updates should be deterministic code, not an expensive model.
- **latency:** Abort signal fan-out under 300 ms; each executor must acknowledge cancellation or report unknown within 2 s.
- **cost:** Negligible model cost after intent recognition; one small relay event and bounded receipt writes dominate.
- **security:** Stop is fail-safe and must never approve a pending action or start a compensating action. Bind cancellation to the active operation ID, not the most recent job text; if identity is ambiguous, cancel nothing and ask. Mac/browser workers must checkpoint and refuse new steps after the cancel token. If an external side effect already committed, report committed/unknown rather than claiming rollback.
- **missing:** A relay-wide cancellation token endpoint keyed by operation ID; Mac and browser executors that poll/subscribe to cancellation between steps and return a terminal stopped/committed/unknown receipt; Pendant rendering of an active-operation abort acknowledgement (the existing outcome beacon can render the result)

### "Take the value from the logged-in website and paste it into the desktop app, but do not show me the secret or send it through the model."
- **useful because:** The browser may hold an authenticated token, recovery code, address, or other sensitive field that the Mac app cannot reach. Today the owner must manually copy it, exposing it to screens, clipboard history, or the model. A sealed browser-to-Mac handoff lets the owner bridge those two otherwise separate surfaces while preserving a no-secret-to-model boundary.
- **path:** browser-extension → relay → mac-planner → mac-terminal → faculty-judgement → faculty-action → pendant
- **model tier:** The model only selects the already-bound source field and destination locator from typed metadata; a deterministic encrypted channel transfers the bytes. Use the realtime tier only if the owner is speaking live; no background model call is needed.
- **latency:** 2–5 seconds including a physical approval gesture; never wait indefinitely for a stale browser session.
- **cost:** Near-zero inference cost; encrypted payload transfer and two receipts dominate. No plaintext should enter model context or ordinary logs.
- **security:** R2 secret disclosure: require an explicit physical approval using the existing transaction latch, show only site/app names and field labels—not values—and bind source tab, destination app/window, operation digest, expiry, and one-use nonce. The browser extension must redact values from snapshots; relay stores ciphertext only; Mac types directly without clipboard persistence, then independently verifies destination field presence without returning its contents. Refuse cross-origin or unbound destination changes.
- **missing:** A typed secret-handoff command in the browser bridge and Mac agent; An ephemeral encrypted payload channel with memory-only handling and zeroization; A verifier postcondition that can prove destination acceptance without exposing the value

### "Prepare this form everywhere, and tell me exactly which fields still need my eyes."
- **useful because:** Many real tasks span a browser session and a desktop app: gather known values, fill only low-risk fields, stop at ambiguity, and return a compact checklist of unresolved fields. This would turn the system from a single-surface clicker into a safe preparation handoff while keeping final judgment with the owner.
- **path:** browser-extension → mac-planner → mac-vision → faculty-perception → faculty-action → relay-realtime → pendant
- **model tier:** Use a cheaper background model to map typed field metadata and identify missing/ambiguous values; use realtime only for the owner's spoken request. Execution and field checks are deterministic.
- **latency:** Initial inventory under 5 seconds; fill each bound field within 1 second; stop immediately on ambiguity or navigation.
- **cost:** One small planning call per form, then deterministic browser/Mac actions. Cost is dominated by screenshots only when a typed DOM/AppleScript locator is unavailable.
- **security:** Never submit, send, purchase, or disclose a sensitive value as part of preparation. Every write is risk-classified; private fields are not echoed. Revalidate URL, account/session identity, and field labels immediately before each write. Return a digest and unresolved-field list, not raw page contents, and require the existing physical approval latch for any final commit.
- **missing:** A shared typed form model that can represent fields across browser and desktop app; Cross-surface target binding and drift detection between preparation and final approval; A compact pendant-readable unresolved-field summary

### "The Mac app is stuck—move this exact in-progress task to the browser without doing anything twice."
- **useful because:** A task can lose the surface it started on: an app crashes, a browser session becomes available, or the opposite. Today the owner must restart manually, risking duplicate sends or purchases. A lease-preserving executor handoff would keep one operation identity, checkpoint completed side effects, and continue only from an independently verified boundary.
- **path:** mac-planner → mac-vision → browser-extension → relay → faculty-action → faculty-perception → pendant
- **model tier:** Use a cheap background planner to translate executor checkpoints; deterministic code owns lease transfer and deduplication. Realtime is only for the owner's spoken request.
- **latency:** Detect executor loss within 2 seconds; establish the replacement lease within 5 seconds; never issue a replacement step until the prior step's postcondition is verified.
- **cost:** Low inference cost; dominated by one verification call per handoff and bounded receipt storage.
- **security:** The replacement executor receives only the remaining typed plan, not secrets or completed step contents. A single-use operation lease and step IDs prevent duplicate side effects. If verification is unavailable, freeze and report unknown rather than fail over optimistically. Physical approval must not be silently carried across a changed target or account.
- **missing:** A lease-transfer protocol shared by Mac and browser executors; Checkpoint records with idempotency keys and verified postconditions; A takeover route that invalidates the old executor before granting the new one

### "Make a private incident report for that failed action, with the evidence I need but none of the secrets."
- **useful because:** When automation fails, the owner currently has to reconstruct what happened from scattered logs, browser state, and receipts. A redacted incident bundle would make support, dispute, and recovery practical without copying passwords, message bodies, or page contents into a report.
- **path:** faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension → relay → pendant
- **model tier:** A cheaper background model can summarize typed receipts and redact known sensitive classes; deterministic policy must decide inclusion and hashing. Realtime is unnecessary unless the owner asks verbally.
- **latency:** Generate a compact report within 10 seconds of a terminal failure; evidence capture must stop at the operation's declared scope and expiry.
- **cost:** Low model cost; storage and hashing of bounded screenshots/receipts dominate. Default to hashes and small snippets, never full captures.
- **security:** The report is private by default and must have an explicit export destination and expiry. Redaction must occur before model context and before relay persistence. Include provenance, timestamps, operation/step digests, and verified versus unknown states; never infer success from a missing error. Exporting externally is R2 and needs physical approval.
- **missing:** A redaction-aware evidence bundle schema spanning Mac, browser, and relay receipts; A bounded capture/export route with sensitivity labels and retention expiry; Owner-visible report retrieval and deletion controls

### "Show me every pending action that could still affect the outside world, in one short queue, and let me cancel selected ones without opening the Mac."
- **useful because:** Pending work is currently fragmented across relay jobs, browser commands, and local Mac execution. The owner cannot reliably see whether an old action is still live or cancel one specific operation from the pendant. A unified external-effects queue would make delayed automation legible and controllable.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** No expensive model is needed for queue construction; deterministic aggregation classifies live leases and expiry. Realtime only answers the owner's selection phrase.
- **latency:** Queue refresh under 500 ms from cached receipts; cancellation fan-out under 300 ms, with unknown surfaced within 2 seconds.
- **cost:** Negligible inference cost; bounded relay state and small pendant summaries.
- **security:** Expose only human-readable summaries, risk class, target digest, expiry, and state—not page contents or secrets. Selection must bind to an opaque operation ID and current digest. Cancellation is always safe and must never approve. Expired or unverifiable entries are shown as unknown until independently closed.
- **missing:** A unified operation index across relay, Mac, and browser jobs; A pendant-friendly list/selection protocol (the future wheel/extra button is the right input); Cancellation endpoints for each executor and a signed terminal-state receipt


## Changes it proposed to its own stack

### `firmware` — Add a cancellation state machine to the pendant protocol: accept only a signed, operation-bound abort envelope, persist its nonce and monotonic counter in the existing inbox, reject expired/replayed/mismatched envelopes, and render an unmistakable cancel acknowledgement through the accepted tactile_action_outcome_beacon. The firmware must never treat a cancel packet as approval, and it must fail closed if the operation ID is absent.
- **owner gets:** When the owner says stop, the pendant gives a dependable local acknowledgement even if the Mac/browser link is briefly delayed; a mistaken or stale packet cannot silently approve anything.
- effort: Medium: protocol schema, bounded inbox record, replay protection, and integration with the existing outcome renderer; no new hardware, but i2c2/DRV2605L is needed if the accepted haptic implementation is not yet wired.  ·  risk: A malformed or stale packet could create false confidence. Mitigate with signed envelopes, expiry, operation binding, and a distinct unknown pattern. Recovery is to show unknown and leave the executor in its existing fail-safe state.
- cost: Negligible runtime cost; tens of KB firmware/storage at most, no component purchase. Haptic driver adds minimal I2C/power use only while rendering.  ·  latency: Local acknowledgement under 100 ms after receipt; no effect on audio path.
- security: Improves safety by adding a non-approving abort path; replay and cross-operation injection must be rejected.
- depends on: A relay cancellation-token route and executor cancellation polling; Existing physical_transaction_approval_latch envelope/monotonic-counter conventions; Existing tactile_action_outcome_beacon firmware integration


## What it asked for

_Nothing._
## Its own summary

Recorded four new action proposals. The strongest is a cross-surface emergency stop: an explicit stop utterance fans out a cancellation token to the active Mac/browser operation, with stopped/committed/unknown receipts and no accidental approval. Also recorded a sealed browser-to-desktop secret handoff that keeps values out of model context and clipboard history, a safe cross-surface form-preparation mode that stops at unresolved fields, and the pendant firmware change needed to receive operation-bound abort envelopes and acknowledge them locally.

**Biggest unknown:** The action layer still lacks three concrete primitives these proposals depend on: a relay cancellation route keyed by operation ID, executor-side cancellation checkpoints with terminal receipts, and a typed secret/form locator channel between browser extension and Mac agent. I also need confirmation that the accepted tactile outcome beacon is actually wired in firmware; the proposal recorder could not find it in the observed route inventory, though the orchestrator says the device skill is accepted.

