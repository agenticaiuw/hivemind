# Harness derivation — faculty-action — round 257

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When you say “do that,” carry out the Mac/browser action only if the postcondition can be independently verified; if verification is unknown, stop and tell me exactly what remains unverified, without retrying."
- **useful because:** Prevents silent duplicate sends or false success. The executor acts, faculty-perception verifies fresh state, and the pendant gives a truthful verified/unknown beacon so the owner knows whether to retry.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for planning and verification; realtime only for the spoken acknowledgement
- **latency:** 2–6 seconds for ordinary actions; never hide an unknown result behind a timeout
- **cost:** Low: one planner call plus a small verifier call; dominated by model planning, not transport
- **security:** Never include secrets or page contents in the pendant; bind verification to operation_id and step_id; require physical_transaction_approval_latch for risky actions; unknown must be non-retryable by default.
- **missing:** Verifier correlation fields action_id/attempt_id and an explicit no-retry-on-unknown policy; A relay state machine that persists executor receipt, verifier evidence, and owner-visible outcome

### "What was the last answer? Replay it on the pendant from the beginning, or start at the point I missed."
- **useful because:** The owner can recover an answer they missed without asking the model to regenerate it. The rotary control can choose replay/restart versus resume, while the relay and pendant coordinate the exact stored artifact and playback cursor.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** No model needed for replay; use realtime only to interpret the short spoken command
- **latency:** Under 500 ms to acknowledge; playback resumes from the selected cursor within 2 seconds
- **cost:** Negligible API cost; storage and delivery acknowledgements dominate
- **security:** Use opaque artifact IDs, checksums, expiry, and owner-local audio only; never expose transcript or sensitive content in a haptic/status packet; deduplicate playback events.
- **missing:** Firmware support for the incoming rotary encoder and second button; A relay verb that resolves the last delivered artifact and cursor to a bounded replay request; A pendant playback seek/status protocol

### "Tell me what is on my Mac right now, then safely complete a task across the browser and Mac and show me a compact receipt I can inspect later."
- **useful because:** Combines fresh host/browser presence with an action receipt instead of pretending a stale session is current. It lets the owner ask for a cross-surface task while preserving a human-readable audit trail and a clear boundary when the Mac is locked or unavailable.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background model for summarizing observations and receipts; realtime only for the short spoken response
- **latency:** Observation under 1 second; task completion under 10 seconds when browser is online
- **cost:** Low: read-only observation plus existing executor; summary generation is the main cost
- **security:** Observation must remain read-only; redact URLs, filenames, and form values by sensitivity; destructive actions remain staged behind physical approval; do not infer unlocked state because no source exists.
- **missing:** A first-class compact receipt view that joins observation freshness, browser session identity, action receipt, and independent verification; An explicit unknown lock/wake state surfaced to the owner rather than guessed

### "Warn me on the pendant before its battery becomes unreliable, and defer non-urgent uploads until it has enough charge while never losing an urgent bookmark."
- **useful because:** A wearable that dies silently is worse than one that says it cannot finish. The pendant can prioritize bookmarks and action decisions, while the relay delays bulky audio and tells the owner what was deferred.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** No model for thresholds or queueing; cheap background model only for a natural-language summary
- **latency:** Battery warning locally within 100 ms of a sample; relay policy decision under 1 second
- **cost:** Low API cost; hardware gauge and firmware integration dominate
- **security:** Battery telemetry is low sensitivity; never discard signed decisions or bookmarks due to power policy; preserve crash-safe queue semantics and show deferred/expired states honestly.
- **missing:** A fuel-gauge IC and board integration in the product pendant; Firmware battery sampling, hysteresis, and priority-aware queue policy; Relay fields for estimated charge, deferred reason, and expiry

### "For the next hour, let me authorize only calendar and reminder changes from my pendant, while blocking messages, purchases, and file deletion everywhere. Tell me when the temporary permission expires."
- **useful because:** The owner gets a bounded delegation window instead of approving every safe action individually or granting the agent a permanent policy. The pendant sets the scope, the relay enforces it consistently across Mac, browser, and iPhone, and expiry removes the authority automatically.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** No realtime model for enforcement; use a cheap background model only to turn the owner’s spoken scope into a reviewable policy summary. Require deterministic policy evaluation for execution.
- **latency:** Acknowledge the policy within 1 second; enforce every action before execution with no model round trip.
- **cost:** Low API cost after setup; engineering cost is policy propagation, capability checks, and audit storage.
- **security:** Default deny outside the selected action classes; bind the lease to the pendant identity and a monotonic counter; show the exact allowed/blocked classes and expiry; never let a natural-language parser silently broaden scope; destructive classes remain blocked unless explicitly included in a separate approval flow.
- **missing:** A signed, expiring capability lease understood by relay, Mac, browser, and iOS executors; Deterministic action-class enforcement before every executor call; A pendant interaction for reviewing, shortening, and cancelling the lease; Dashboard audit view showing policy changes and blocked attempts

### "Use my saved login to complete this website task, but do not show or send my password, payment details, or private form values to the relay or model."
- **useful because:** The owner can automate authenticated websites without turning the cloud relay into a holder of credentials or sensitive page contents. The browser and Mac perform secret-handling locally while the relay receives only intent, redacted progress, and a result.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime interprets the spoken goal; local deterministic browser automation performs secret insertion; background model summarizes only redacted state.
- **latency:** Under 5 seconds for a normal form; pause immediately when a sensitive field or unexpected domain appears.
- **cost:** Low per-action API cost; implementation cost is a local secret broker, DOM field classification, and redacted receipts.
- **security:** Credentials never enter relay logs, model context, pendant packets, screenshots, or browser command payloads; require domain/origin binding, user confirmation for payments or sends, and fail closed on ambiguous fields; receipts contain hashes and field labels only.
- **missing:** A Mac-local Keychain/credential broker callable by the browser executor without returning values to the model; Secret-field classification and screenshot redaction before browser evidence leaves the Mac; Origin-bound credential-use leases and a redacted receipt schema

### "Pause this task on my Mac and continue it on my iPhone later, with the exact step, browser session, pending approvals, and expiry preserved."
- **useful because:** The owner can leave the desk without abandoning a half-finished task or restarting it dangerously. The Mac hands off only a resumable checkpoint; the browser session remains where it is, and the pendant can cancel or resume the lease.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** Background model creates a concise checkpoint summary; deterministic executors restore the session and verify the checkpoint before continuing.
- **latency:** Checkpoint creation under 2 seconds; resume acknowledgement under 3 seconds.
- **cost:** Moderate engineering cost and negligible ongoing model cost; durable checkpoint storage and cross-device session binding dominate.
- **security:** Do not copy page secrets or private field values into the checkpoint; bind it to device/session identity, expiry, and a monotonic version; refuse resume if the page, app, or form has changed; destructive steps require fresh physical approval on the new surface.
- **missing:** A portable checkpoint format covering executor step, browser session, verified postconditions, and approval state; Cross-device session binding between Mac, iPhone, relay, and pendant; Resume-time freshness verification and conflict refusal; A user-visible checkpoint list with cancel and expiry


## Changes it proposed to its own stack

### `model-routing` — Add an outcome-first router: routine verified receipts and short status summaries use a cheap background model; only ambiguous intent, sensitive-risk summaries, or verifier-unknown states escalate to realtime. Preserve the exact executor/verifier evidence and never let a summarizer upgrade unknown to success.
- **owner gets:** The pendant answers routine “did it happen?” questions quickly and cheaply, while difficult or uncertain actions get the expensive attention they deserve instead of every action consuming realtime tokens.
- effort: Moderate: add routing rules at the existing policyRouter seam, with tests for verified, cancelled, failed, and unknown outcomes.  ·  risk: A cheap summary could omit a caveat; enforce a fixed schema and require the words verified/failed/unknown from the receipt, with realtime fallback on schema violation.
- cost: Reduces realtime usage substantially; adds negligible background-model cost.  ·  latency: Verified status under 1 second; unknown escalations may add 1–3 seconds.
- security: No new data access; redact sensitive evidence before summarization and retain raw evidence only in the protected ledger.
- depends on: verify_operation_step correlation with operation_id and attempt_id; truthful_action_status_beacon; Existing local-agent/policyRouter.js and actionLedger.js


## What it asked for

_Nothing._
