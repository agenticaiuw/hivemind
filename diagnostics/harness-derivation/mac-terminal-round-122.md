# Harness derivation — mac-terminal — round 122

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac execution truthfulness and fallback** — At 2026-08-07T14:58Z, /ops/status reports browser extension online and fullControlMode=true, but Accessibility trusted=false, Screen Recording=false, computerUse.loopEnabled=false, and visionUploadConsented=false. /observe confirms inputReachability failed and explicitly says ui_click/ui_menu/type_text/press_keys may report success while doing nothing. A recent job attempted to open Browser Bridge successfully, then failed on computer_use_task because the loop was disabled.
  - evidence: GET /ops/status and GET /observe; GET /jobs latest local_1a472fde-eb1f-41d7-8e9f-e141141f7937

## Capabilities it proposed

### "“When you submit something in my authenticated browser, make sure the Mac records it only after the site confirms it, and tell me later exactly what happened—even if the browser or Mac disconnects halfway through.”"
- **useful because:** Today the owner can have browser commands and Mac actions, but not a trustworthy cross-device transaction. This would prevent false local records (such as reminders or notes saying a form was submitted when it was not), survive a dropped bridge, and give the pendant a concise, evidence-backed completion or recovery message.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Use deterministic workflow orchestration and background models for reconciliation; reserve realtime only for the owner's immediate spoken acknowledgement. Use the planner tier only when the site outcome or requested local record is ambiguous.
- **latency:** Immediate acknowledgement under 1 second; browser confirmation normally under 10 seconds; disconnect recovery is asynchronous and may take minutes, with the pendant notifying the owner when reconciled.
- **cost:** Low per invocation when selectors and postconditions are known: mostly relay/database and browser polling. Ambiguous pages may require one planner call and, only when available, a vision call; the dominant cost is screenshot/planner context, not the Mac record action.
- **security:** Authenticated page contents and submission results remain within the browser/relay authorization boundary; only the minimum confirmation and owner-requested record cross to the Mac. Never duplicate a submission after timeout without an idempotency key or explicit site confirmation. Require owner confirmation for irreversible submissions, but allow retries of idempotent reads and record creation.
- **missing:** A durable cross-surface transaction record with idempotency key, state machine, and lease/resume semantics.; Browser-side postcondition adapters that can distinguish a confirmed submission from navigation or transport success.; Relay reconciliation worker that resumes after browser/Mac disconnects and emits a final pendant notification.; Mac-side conditional-write endpoint: create the requested reminder/note/file only when supplied with a verified browser outcome.; Evidence-linked receipts spanning browser command, site confirmation, and Mac write.; A recovery UI showing pending, confirmed, conflicted, and permanently failed transactions.


## Changes it proposed to its own stack

### `model-routing` — Extend the existing readiness-aware action contract with automatic route substitution and postcondition verification, rather than merely reporting readiness. For each planned UI step, derive an alternate execution graph: browser-extension command for browser-owned state, typed Mac action/run_shell for deterministic system state, and computer-use only when Accessibility + Screen Recording + PENDANT_COMPUTER_USE_ENABLED are all true. After each substitute, verify the requested state through the authoritative observer (browser heartbeat/result, /observe, or a command result); mark the original UI step as skipped-with-fallback, not successful. Include route chosen, observer evidence, and remaining unmet capabilities in the receipt and spoken completion summary.
- **owner gets:** A request such as 'check the page and tell me what changed' keeps working when screen control is unavailable, while requests that truly need pixels fail immediately and honestly. The owner gets the result, not a permission diagnosis after a useless retry.
- effort: Medium-high: planner graph representation, route capability registry, postcondition adapters, and receipt/journal fields; no new authority required.  ·  risk: An alternate route may have different semantics or touch a page unexpectedly. Limit substitution to explicitly equivalent read-only/browser-status/system-status operations, preserve session affinity, and require the planner to label any non-equivalent mutation as unavailable rather than silently changing it.
- cost: Small local compute cost; likely reduces planner and vision retries. No additional model call when the capability registry matches a deterministic fallback.  ·  latency: ~100–300 ms for preflight/verification; materially faster than a failed 15-second computer-use attempt.
- security: Uses existing authenticated Mac and browser channels; receipts contain capability metadata and evidence references, so retain current auth and avoid storing page contents unless the underlying action already does.
- depends on: Existing readiness-aware action contract (extend, do not duplicate it).; GET /observe and GET /ops/status.; GET /browser/status, GET /browser/poll, POST /browser/result/:commandId.; Existing typed Mac actions/run_shell and receipt/journal persistence.

### `integration` — Add a durable cross-surface transaction coordinator, distinct from ordinary Mac jobs and browser commands. It should create an idempotency-keyed transaction before submission, persist browser and Mac phases independently, require a browser postcondition receipt before allowing the Mac write, lease/retry after bridge disconnects, and reconcile on startup. A timeout must remain 'unknown/pending' rather than becoming success; duplicate submissions are prohibited unless the site exposes a matching idempotency key. Expose a compact owner-facing state timeline and send the final outcome through the pendant pipeline.
- **owner gets:** The owner can ask one sentence such as 'submit this and remind me when it is confirmed' without risking a false reminder or duplicate submission. They get a truthful answer after interruptions instead of having to inspect browser tabs, Mac jobs, and logs separately.
- effort: High: new relay D1 transaction schema and worker, browser postcondition protocol, Mac conditional-write endpoint, recovery/reconciliation worker, and dashboard timeline.  ·  risk: Sites with weak confirmation signals may leave a transaction pending; fail closed on local writes and surface an explicit conflict. Browser sessions may expire, so preserve the original evidence and ask the owner to re-authenticate rather than replaying.
- cost: Small durable-storage and polling cost per transaction; ambiguous postconditions may require planner/vision calls. This is cheaper than duplicate submissions and manual recovery.  ·  latency: Adds one persistence round trip before each phase and postcondition polling, typically hundreds of milliseconds plus site latency; recovery is asynchronous.
- security: Requires authenticated correlation among relay, browser session, and Mac job. Store hashes/minimal status rather than page bodies; encrypt or restrict evidence references, and never transmit session cookies to the relay or Mac.
- depends on: A new transaction state machine and idempotency-key storage in the relay.; A browser extension result contract that reports authoritative postconditions, not merely command execution.; A Mac conditional-write route that accepts only a verified transaction receipt.; Existing browser command/session, Mac job/receipt/journal, and pendant notification routes.


## What it asked for

_Nothing._
