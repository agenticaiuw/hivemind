# Harness derivation — faculty-action — round 242

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Stop everything the pendant is doing right now.”"
- **useful because:** A genuinely immediate escape hatch: it stops spoken playback, cancels not-yet-started Mac/browser jobs, and revokes pending approvals across the hive, even if the link is currently down. This is safer than making the owner hunt for the right app or wait for speech to finish.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime only to acknowledge the interrupt; cancellation propagation and reconciliation use the relay/background tier.
- **latency:** Local pendant mute/cancel indication under 100 ms; relay fan-out under 1 s when connected; queued revocations reconcile on reconnect.
- **cost:** Negligible model cost; dominated by one relay event and cancellation receipts per active job.
- **security:** The stop command must be authenticated and monotonic, but must not require model interpretation. It may cancel benign work but must never approve or execute anything. Any job already committed is reported as committed rather than falsely undone. No audio or page contents leave the device.
- **missing:** A signed, monotonic global-stop/revoke event understood by relay, Mac executor, browser bridge, and pendant; A cancellation endpoint that can mark queued jobs revoked and return per-step terminal state; ESP32 playback mute plus nRF9160 local stop handling for the currently active stream

### "“I missed that—say the last answer again.” (or turn the new wheel one click left)"
- **useful because:** The owner can recover a perfectly delivered answer without repeating the request or reopening an app. A wheel/button is the right physical input because sw0 already starts recording and sw1 bookmarks moments; this makes the planned product input materially useful.
- **path:** pendant → relay → mac-planner
- **model tier:** No model for selection or replay; relay stores compact response metadata and replays the already-generated audio artifact. Use a cheaper background model only if a response has expired and must be regenerated.
- **latency:** A local acknowledgement immediately; replay begins within 500 ms when the artifact is cached, otherwise state “expired” within 1 s.
- **cost:** Zero inference cost for cached replay; storage and cellular egress dominate. Regeneration, when explicitly allowed, costs one background completion.
- **security:** Persist only opaque response ID, codec/rate, checksum, expiry, and playback cursor—not transcript or sensitive page contents on the pendant. Reject expired, consumed, or digest-mismatched replay records. Wheel input must never approve a pending external action.
- **missing:** Rotary encoder and second product button plus firmware input driver/debouncing; A relay inbox verb for replay metadata and a bounded replay policy; A pendant playback seek/restart command and an explicit expired-artifact response

### "“Take me back to where I left off.”"
- **useful because:** The pendant becomes a physical resume control, not just a microphone: it resolves the owner's last intentional bookmark into the relevant Mac app, file, browser tab, or queued work, reopens it, and tells them what could not be restored. This is especially valuable after sleep, travel, or a dropped link when the owner cannot remember which window mattered.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background/cheap model ranks candidate resume records; realtime is used only for a short disambiguation if there are multiple recent bookmarks. Execution is deterministic after selection.
- **latency:** Show the candidate within 1 s; reopen the selected app/tab/file within 3 s; never silently choose among conflicting private contexts.
- **cost:** Usually no inference if there is one candidate; occasional small ranking completion. Mac/browser operations and file/app launch dominate latency.
- **security:** Resume records contain potentially sensitive app names, paths, URLs, and timestamps. Keep full details on the Mac/relay, send only a redacted label to the pendant, require physical confirmation before opening a private browser session, and verify the postcondition after each reopen. Never infer the owner's physical timezone from the pendant clock.
- **missing:** A durable bookmark-to-context correlation record tying sw1 events to foreground app, browser session/tab, file, and active relay job; A disambiguation UI using the planned rotary wheel and second button; A safe reopen transaction with independent app/browser postcondition verification and a no-op when the source is stale

### "“Undo the last thing you did for me.”"
- **useful because:** The owner gets a real recovery path after an accidental send, edit, move, or setting change—not merely a report that it happened. The system would identify the exact committed operation, present the compensating operation and its limits, require the pendant’s physical approval, execute it on the correct Mac/browser surface, and independently verify the resulting state. If no safe inverse exists, it says so rather than pretending.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background model classifies the ledger entry and drafts a candidate inverse; realtime is unnecessary except for the owner’s short request and confirmation. Deterministic executors perform and verify the inverse.
- **latency:** Candidate inverse in 2 s; confirmation remains pending until the owner explicitly approves; execution and verification within 5 s for local/browser operations.
- **cost:** Small background completion per undo request; dominant costs are Mac/browser execution and any external API operation.
- **security:** Undo must be scoped to one immutable operation ID, expire quickly, and refuse when intervening state changes make the inverse unsafe. Never delete or alter data without physical approval. The pendant receives only a redacted summary and digest, not page contents or secrets. A verified “cannot undo” outcome is preferable to a fabricated success.
- **missing:** A first-class inverse/compensation schema in the action ledger, including pre-state digest, post-state digest, and whether an inverse is safe; Executor support for compensating operations across Mac and browser surfaces; A commit protocol that binds the inverse to the original operation and independently verifies its postconditions

### "“Show this secret only when I’m physically holding the pendant.”"
- **useful because:** A physical possession boundary lets the owner unlock a password, recovery code, or private document on the Mac without sending the secret through the relay or pendant. The Mac releases it only to the explicitly selected local destination after a signed, one-time pendant gesture, making the wearable a useful security key without pretending it is a credential store.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** No model should see or transform the secret. A small background classifier may identify the requested destination, but the release policy and nonce checks are deterministic.
- **latency:** Pending request under 1 s; local release within 2 s after physical approval; fail closed on stale link or ambiguous destination.
- **cost:** Near-zero inference cost; dominated by local keychain/API integration. No secret egress or model-token cost.
- **security:** The pendant must receive only an opaque challenge and display-safe label. Secrets stay in the Mac Keychain/password manager or the explicitly authorized local field. Use one-time nonce, expiry, counter, destination binding, and audit receipt; refuse replay, changed destination, or link downgrade. This is not a replacement for OS login or a secure element.
- **missing:** A Mac-local secret-provider adapter with destination binding and no clipboard fallback; A signed pendant challenge/approval protocol that can be verified locally by the Mac; Browser field injection into an explicitly selected secure field without exposing value to the relay

### "“If anything changes while you’re working, stop and ask me before continuing.”"
- **useful because:** The owner can delegate a long, consequential task without worrying that a changed webpage, file, price, recipient, or calendar state will be silently treated as the original plan. The executor snapshots the relevant state, detects meaningful drift before each step, pauses with a concise delta, and resumes only after a fresh physical approval.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Cheap background comparison for structured state diffs; realtime only communicates the pause. No model is allowed to decide that a sensitive drift is harmless.
- **latency:** Drift check before each mutation under 300 ms for local state; pause notification under 2 s; no automatic continuation after timeout.
- **cost:** Small structured-diff calls per mutation; dominated by extra browser/Mac reads, not generation.
- **security:** Define per-field sensitivity and hash private values rather than transmitting them. Treat missing, stale, or unverifiable observations as drift. A physical approval must bind to the new state digest and exact next step, and the old approval must never carry forward.
- **missing:** A precondition snapshot and drift detector shared by Mac and browser executors; A step-level pause/resume protocol that invalidates approvals on digest change; Compact pendant rendering for changed fields without leaking private content


## Changes it proposed to its own stack

### `integration` — Add a read-only macOS lock/wake presence source owned by the Mac bridge: subscribe to lock/unlock and sleep/wake notifications, persist only last event type and timestamp, and expose freshness plus unknown when the bridge was offline. The relay should use it as a prerequisite for deferred resume, never as proof that an action is safe.
- **owner gets:** The hive can stop pretending an absent Mac is merely idle. Deferred work can wait for the owner’s machine to wake and can explain “paused because the Mac is locked/offline” instead of silently retrying or claiming success.
- effort: Small-to-medium bridge daemon and route addition, plus launch-at-login installation and tests for sleep, lock, reconnect, and stale timestamps.  ·  risk: Notification loss or daemon restart could produce stale state; represent stale/unknown explicitly and fail closed. A lock state is not an identity or authorization signal, so it must not approve actions or expose session contents.
- cost: Negligible API cost; a tiny local state record and occasional heartbeat.  ·  latency: Wake/lock updates available within roughly one event-delivery interval; no impact on foreground actions.
- security: Improves privacy by preventing work against an unattended session, but must not collect screen contents, keystrokes, or account credentials.
- depends on: A Mac bridge-owned read-only presence route; Deferred-job policy that treats stale/unknown as a pause, not a false boolean


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: an immediate cross-hive stop/revoke control, replay of the last delivered answer via the planned wheel/button, and bookmark-based “take me back to where I left off” with fresh context verification. Also recorded a Mac lock/wake presence integration so deferred work can fail closed instead of guessing. Still needed: signed global-stop propagation and cancellation receipts across relay/Mac/browser/pendant; rotary encoder plus second-button hardware/firmware; bookmark-to-context correlation and deterministic replay metadata; and a read-only Mac lock/wake source. The owner’s manual TCC grant remains the blocker for deeper GUI/browser control.

**Biggest unknown:** Whether the existing relay and Mac job protocols already have a canonical cancellation/revocation event and whether the future rotary input has been procured; neither was observable from this round’s live inventory.

