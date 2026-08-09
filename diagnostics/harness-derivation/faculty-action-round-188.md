# Harness derivation — faculty-action — round 188

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I tap the pendant while you're speaking, save that exact moment as a useful note I can find later—not just an audio bookmark."
- **useful because:** A tap should preserve the sentence that mattered, even when the owner cannot stop and dictate. The pendant marks the playback cursor; relay resolves the spoken segment; Mac attaches it to the current app/browser context and files a searchable note with a short transcript and source/time, while retaining the original audio pointer for audit.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for transcript extraction and context joining; realtime only for immediate haptic/audio acknowledgement
- **latency:** acknowledge tap locally under 150 ms; create note within 10 s; if Mac/browser is offline, queue metadata and finish later
- **cost:** Usually <$0.01 per bookmark; transcription/context extraction dominates, with no model call for a silence or duplicate tap
- **security:** The note may contain private spoken content and current browser title/URL. Keep raw audio on the existing failure-path store, redact secrets from URLs, require the existing physical confirmation only if filing crosses a sensitive destination, and expose/delete the pending item from the dashboard.
- **missing:** A playback-segment index mapping response artifact IDs and timestamps to transcript sentences; A relay-to-Mac context snapshot join keyed by bookmark ID; A pendant gesture/firmware amendment that emits bookmark cursor and response ID (sw1 today, rotary/second button in product)

### "Where did that thing go? Show me the complete trail of what you asked the Mac or browser to do, what actually changed, and what is still uncertain."
- **useful because:** Today receipts are fragmented across relay jobs, Mac journals, browser commands, and postcondition checks. A single owner-facing trace prevents silent failures and makes the system accountable: it can name the exact step, timestamp, destination, evidence, and whether the result was verified or merely reported by an executor.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action → dashboard
- **model tier:** background aggregation and summarization; realtime only to answer a live trace query
- **latency:** Return the first timeline in under 2 s from stored receipts; run fresh verification asynchronously and update within 10 s
- **cost:** <$0.005 per query when receipts exist; fresh browser/Mac verification and summarization dominate
- **security:** Traces can expose private message recipients, URLs, filenames, and snippets. Scope results to the owner's authenticated session, default to hashes and labels, reveal content only on explicit request, and never treat an executor receipt as proof without independent verification.
- **missing:** A stable operation/step correlation ID propagated through plan, execute, browser commands, and relay jobs; A read-only trace aggregator joining /jobs/:jobId/receipts, /journal/:jobId, browser results, and verify_operation_step provenance; A UI/voice vocabulary for verified, executor-reported, pending, and unknown

### "Before you do something consequential, tell me if the world disagrees with what I just asked—for example, if the file changed, the recipient is different, or the browser session is stale—and ask only the one correction needed."
- **useful because:** The most dangerous failures are obedient actions against an outdated assumption. A cross-surface precondition challenge would compare the owner's intent with fresh Mac/browser state, identify the smallest contradiction, and pause before mutation rather than making the owner discover it afterward.
- **path:** relay-realtime → faculty-judgement → faculty-perception → faculty-action → mac-planner → mac-vision → browser-extension → pendant
- **model tier:** background model for extracting and comparing preconditions; realtime only for the short spoken contradiction and answer
- **latency:** Check cheap preconditions in under 2 seconds; if a fresh browser/Mac read is needed, speak a provisional pause within 1 second and resolve within 8 seconds
- **cost:** <$0.01 per consequential action; state reads dominate, with model cost only when intent or contradiction is ambiguous
- **security:** Precondition reads may expose private file names, page contents, or recipients. Return a minimal contradiction (e.g. 'the recipient is not Alex') rather than raw content; require the existing physical approval for the eventual mutation; never infer consent from silence.
- **missing:** A typed precondition schema shared by judgement, perception, and action; A read-only, freshness-bounded snapshot API for Mac and browser state; A dialogue protocol that can amend one precondition without discarding the entire action plan

### "Send this task to a person I choose for a one-time approval, without giving them my account session, and tell me when they approve, reject, or let it expire."
- **useful because:** Some actions need another human's judgment but the browser session and credentials must remain on the owner's Mac. The system should package a redacted proposal, let the other person approve through an expiring channel, then return the decision to the owner for deliberate physical confirmation before execution.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension → faculty-judgement → faculty-action → dashboard
- **model tier:** background model for redaction and concise proposal writing; realtime only for owner interaction and urgent decision updates
- **latency:** Create a shareable proposal in under 5 seconds; deliver decision events within 30 seconds; never block the owner's Mac session while waiting
- **cost:** <$0.02 per delegation; secure relay storage and notification delivery dominate, with model cost for redaction only
- **security:** The proposal may contain confidential files, recipients, or intended effects. Encrypt payloads to the invited approver, default to metadata-only previews, use single-use expiring tokens, log every view/decision, prevent forwarding from granting authority, and require the owner's existing physical approval after a positive response. The delegate never receives credentials or direct browser control.
- **missing:** An authenticated delegate identity/invitation and notification channel; A redaction/approval artifact format with expiry, revocation, and audit trail; Relay enforcement that a delegate decision is advisory and cannot directly execute an owner action


## Changes it proposed to its own stack

### `firmware` — Wire the already-owned DRV2605L and LSM6DSOX on i2c2, then make physical_transaction_approval_latch tactile and motion-aware: a short, distinct haptic pattern for pending/approved/cancelled/expired; suppress pending prompts when the pendant is stationary on the desk; replay one queued pattern when it is picked up; require a deliberate sw1 press while worn for approval. Persist only state, nonce hash, and pattern ID—never action contents.
- **owner gets:** The owner can safely approve or cancel in a pocket without looking at a single LED, and a forgotten pendant on a desk cannot silently approve an action. Status remains perceivable in a noisy room or while the Mac screen is out of sight.
- effort: Medium: enable i2c2 devicetree, add DRV2605L/LSM6DSOX drivers and calibration, implement a small state machine and bench-test gesture thresholds against the two-button firmware.  ·  risk: False motion classification could delay a legitimate approval or produce an unexpected vibration. Default to fail-closed (no approval), expose a fallback LED/audio cue, and provide a physical cancel gesture; recover by disabling motion gating while retaining haptic status.
- cost: No new hardware purchase; roughly 1–3 mA only during short haptic bursts and <1 mA IMU duty-cycled. Firmware flash/RAM increase is modest but must fit the 211,608 B application RAM budget.  ·  latency: Pending/approval haptic starts under 100 ms; pickup replay adds at most one event-loop tick. I2C work must not block the 24 kHz audio path.
- security: Improves human-presence assurance but is not cryptographic proof; approval still requires the existing nonce, expiry, monotonic counter, and relay verification. Do not send IMU traces or action contents off-device.
- depends on: physical_transaction_approval_latch (s10-j9l4); i2c2 devicetree integration; A calibrated definition of worn/picked-up versus desk-stationary; Existing audio/LED fallback for haptic hardware faults

### `browser-harness` — Add opaque browser object handles and capability-scoped mutations: inspection returns typed fields (recipient, amount, title, domain, selected state) plus a handle, while page text, cookies, tokens, and unrelated tabs remain local. An action may mutate only the handle and field values explicitly authorized in its plan; handles expire on navigation, logout, or a short TTL, and the browser re-checks the bound DOM identity immediately before submission.
- **owner gets:** The owner can ask the system to act in a logged-in browser without handing the model an entire private page or risking that a stale tab, hidden field, or navigation causes the wrong submission. It preserves convenience while making 'what exactly will be changed?' precise.
- effort: High: extension protocol, content-script isolation, structured field extraction, navigation invalidation, and a pre-submit revalidation path across browser-extension, Mac planner, and relay.  ·  risk: A faulty locator or page redesign could reject safe actions or, worse, bind a handle to the wrong element. Fail closed on identity mismatch, require the existing physical approval for submission, and retain a compatibility path that only drafts rather than submits.
- cost: Low per-action API cost; engineering and browser compatibility are the main costs. No hardware cost.  ·  latency: Adds roughly 100–500 ms for handle validation and one fresh DOM read before a mutation; avoids expensive retries and uncertain duplicate submissions.
- security: Materially reduces data leaving the browser and prevents bearer/session material from entering model context. Handle IDs must be unguessable, single-use where possible, and scoped to one browser session and action digest.
- depends on: A browser-extension structured inspection/mutation protocol; Fresh pre-submit verification via faculty-perception; Stable operation and action-digest correlation across relay, Mac, and browser; Existing physical approval latch for consequential submits


## What it asked for

_Nothing._
## Its own summary

Round 188 produced three non-identical additions. (1) A tap-to-save-spoken-moment workflow joins pendant playback cursor, relay transcript, Mac/browser context, and a searchable note; it needs a segment index and bookmark correlation. (2) A cross-surface 'where did that go?' operation trace is the highest-value proposal: it joins relay jobs, Mac journals, browser results, and independent postcondition verification, clearly separating verified, executor-reported, pending, and unknown. (3) Firmware integration of the already-owned DRV2605L and LSM6DSOX adds tactile status and fail-closed worn-presence gating to the existing physical approval latch without touching the 24 kHz audio path. All three were recorded; the recorder flagged only close conceptual neighbors, not duplicates.

**Biggest unknown:** The owner still has not specified which trace details may be spoken/displayed by default (URLs, filenames, recipients, or snippets), and the pendant is not LTE-registered, so firmware work is bench-testable over USB but not yet end-to-end cellular verified. The main implementation dependency is a stable operation/step ID propagated across planner, relay, browser, and verifier.

