# Harness derivation — mac-terminal — round 111

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-ui-reachability** — Live /observe reports Accessibility trusted=false and inputReachability.status=failed because synthesized events from com.aipendant.agent are not accepted; consequence explicitly says UI actions report success while doing nothing. /ops/status reports ready=false. This is a current operational blocker, not merely a policy concern.
  - evidence: GET /observe and GET /ops/status at 2026-08-07T14:22:45Z

## Capabilities it proposed

### "When my browser is offline, queue only the browser work I explicitly asked for, and when it reconnects tell me what was skipped, what ran, and why—never replay stale commands blindly."
- **useful because:** The live Mac state has an offline browser extension with 10 pending commands, while one browser_navigate idempotency key has failed 9/9 times. Today the owner cannot distinguish waiting work from dead work or know whether reconnecting will replay obsolete actions. A cross-node intent queue makes deferred browser automation dependable and understandable.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the cheap background model for queue compaction and retry classification; use realtime only to acknowledge the pendant request and report completion. Browser extension executes, relay persists, Mac planner supplies context and verifies receipts.
- **latency:** Immediate acknowledgement under 1 second; reconnect reconciliation within 5 seconds of browser heartbeat; no repeated model call for each retry.
- **cost:** Near-zero model cost for persistence and deterministic retry policy; occasional cheap-model classification (well under $0.01 per queued batch). Storage is small per intent/receipt.
- **security:** Persist intent metadata, target session/tab, expiry, and redacted parameters—not page secrets or full authenticated content. Require explicit owner intent for mutations, bind execution to the original browser session where possible, expire intents (for example 30 minutes), deduplicate by intent id, and report every skip/failure. Never replay a navigation/type/click after its precondition or page identity changed.
- **missing:** A durable browser-intent record distinct from low-level pending commands; Heartbeat-triggered reconciliation with TTL, page/session preconditions, and dead-letter outcomes; A browser receipt that distinguishes queued, expired, skipped, attempted, succeeded, and unverifiable; Pendant/relay summary of deferred browser work

### "My Mac actions stopped taking effect—walk me through fixing the AI Pendant Agent permission, open the right setting, and verify that typing/clicking really works before you continue."
- **useful because:** The current agent is not ready: Accessibility is granted to a different binary, the input probe fails, and UI actions falsely report success. The owner needs a short recovery flow rather than a cryptic failure or repeated no-op actions.
- **path:** pendant → relay → mac-planner → dashboard-ux
- **model tier:** Deterministic local checks and a cheap text model for concise guidance; realtime only for the spoken interruption and confirmation. No vision model until Screen Recording is granted and the owner explicitly consents.
- **latency:** Detect on the next action (<100 ms local preflight), open System Settings immediately, and verify within 2 seconds after the owner returns to the agent.
- **cost:** No meaningful API cost; local permission checks plus one harmless input probe. Optional realtime turn is only a few seconds of speech.
- **security:** Never attempt to alter macOS privacy permissions programmatically or infer sensitive screen contents. Open only the Accessibility settings pane, state exactly which signed binary needs enabling, and require the owner to perform the grant. Verification should be a zero-delta probe or a reversible no-op, not typing into an arbitrary foreground app. Do not upload screenshots unless separately consented.
- **missing:** A stable deep-link/open action for the Accessibility privacy pane; A signed-binary identity check that explains the mismatch between the granted binary and the running AI Pendant Agent; A safe post-grant verification action whose receipt is based on observed input reachability, not merely API return; A pendant-sized remediation state and dashboard checklist

### "When I ask the pendant to do something on my Mac or in my browser, make sure the intended real-world result happened—not merely that a command returned—and tell me the evidence or the exact point where verification failed."
- **useful because:** Today a UI action can report success while macOS ignores it, and browser commands can fail repeatedly while remaining queued. The owner needs outcome-level certainty: for example, confirmation that a reminder exists, a document was actually saved, or a browser form produced the expected post-submit state. This is more useful than a transport receipt and prevents silent no-ops.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard-ux
- **model tier:** Use deterministic semantic verifiers and cheap background reasoning for expected-state extraction and evidence comparison; reserve realtime for the owner's spoken request and concise result. Use the Mac planner only for ambiguous recovery, not every verification.
- **latency:** Acknowledge intent immediately; verify simple outcomes within 1–3 seconds and multi-step outcomes within 10 seconds. If verification cannot complete, report `unverified` rather than claiming success and continue asynchronously when appropriate.
- **cost:** Usually no additional model call: local app/API readback and browser DOM/session inspection dominate. Cheap-model use for ambiguous expected-state matching should remain below $0.01 per invocation; realtime is not used for background verification.
- **security:** Verification must inspect only the target app/session and redact secrets from evidence. Never treat a matching screenshot alone as proof for destructive or externally visible actions; require a semantic readback such as an object ID, saved-file stat, sent-message record, or post-submit confirmation. Keep evidence hashes and short summaries rather than raw page content. Retries must be idempotency- and precondition-aware to avoid duplicate sends or purchases.
- **missing:** A per-intent expected-outcome schema separate from low-level action receipts; Typed verifier adapters for common Mac actions (Reminders, Calendar, files, volume) and browser outcomes (URL/state/DOM assertions); Independent postcondition evidence stored with the job and exposed to relay_job_status and the pendant; A bounded recovery policy that can retry or compensate only when the verifier declares the operation safe and idempotent


## Changes it proposed to its own stack

### `mac-harness` — Add a capability-aware preflight and result contract for every UI-dependent Mac action. Before ui_click/ui_menu/type_text/press_keys/computer-use steps, consult the existing read-only observation state (Accessibility trust, inputReachability, screen recording, foreground app). If reachability is false, do not invoke the action as successful: return `blocked_unreachable` with the exact missing permission/binary mismatch and suggested recovery (`Enable Accessibility for AI Pendant Agent`), and let the planner choose a non-UI fallback (typed shell/AppleScript) where semantically safe. If the state changes during a multi-step job, stop subsequent UI steps and mark the job `partial_unverified`, preserving per-step evidence rather than emitting false success receipts. Add a startup/periodic permission-drift probe and expose these states to relay and pendant summaries.
- **owner gets:** The owner currently hears that typing/clicking succeeded even when macOS drops every synthesized event. This prevents silent no-ops and lets the agent either use a reliable fallback or clearly say what needs fixing, instead of leaving the owner to discover that nothing happened.
- effort: Medium: normalize /observe reachability into an executor preflight, add typed receipt states and planner fallback handling, then test permission drift and mid-job loss. No new model required.  ·  risk: Some workflows that previously ran through despite bad receipts will now stop or choose a different path; recovery is explicit retry after the permission probe turns healthy. AppleScript/shell fallbacks can have different semantics, so they must be labeled as fallback and retain command/result evidence.
- cost: Negligible API cost; one local observation read per UI job and a small receipt payload. A periodic local probe is CPU-negligible.  ·  latency: Adds roughly tens of milliseconds to UI jobs; avoids wasting up to 25 computer-use steps on actions that cannot reach the screen.
- security: Read-only permission metadata is retained; no new privileges or gates. Existing FULL_CONTROL_MODE remains unchanged.
- depends on: The existing GET /observe reachability fields and durable per-action receipts; A planner/relay contract that understands blocked_unreachable and partial_unverified states


## What it asked for

_Nothing._
