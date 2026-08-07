# Harness derivation — mac-terminal — round 81

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask you to do something in Safari, start immediately; if the browser bridge is offline, tell me right away and continue automatically when it reconnects, then give me one completion or failure report instead of making me ask again."
- **useful because:** Today an offline bridge can waste roughly 45 seconds per browser action and leave several duplicate pending commands. This turns a transient laptop/browser state into a transparent background job: the owner gets an immediate explanation, no duplicate retries, and a single spoken result when Safari returns.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** background for queue monitoring, deterministic health/receipt handling, planner only for interpreting the original goal and final summary
- **latency:** Return an offline status within 1–2 seconds by reading bridge health; resume within one heartbeat (target 5–10 seconds) after reconnect; final summary under 3 seconds after actions complete.
- **cost:** Near-zero for health checks, queueing, and receipts; one background-model call only for a final natural-language summary when needed. Avoids repeated planner calls from timeout/retry loops.
- **security:** The queued browser goal and tab/session identifiers remain in the local job store; authenticated page contents stay in the browser bridge and should not be copied into relay notifications. Spoken offline notices must contain only status, not private page data. Preserve existing action receipts and irreversible-action behavior; reconnect must not duplicate an action ID.
- **missing:** A browser-command state machine with offline_pending and resume-on-heartbeat states, keyed by idempotency/action IDs; A fast local browser-health preflight that returns the existing offline reason instead of waiting for command timeout; A reconnect worker that re-polls pending commands and resumes only incomplete actions; Relay/pendant event projection for immediate offline and final completion notices, with deduplication by job ID

### "When you run something on my Mac and it fails, diagnose it locally, try a safe alternative way to accomplish the same goal, and tell me exactly what worked, what did not, and what changed—without making me repeat the request."
- **useful because:** Today a failed shell, AppleScript, app, or browser handoff is usually just a dead-end receipt. The owner has to understand Mac-specific errors and restate the task. A local recovery loop would turn transient app state, wrong working directories, missing utilities, and stale browser connectivity into completed work or a precise explanation.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension
- **model tier:** Use deterministic classification and local diagnostics first; use the background tier for ordinary error interpretation and retry selection; escalate to the planner only when the goal has multiple viable recovery paths. Realtime is used only to tell the owner the concise outcome.
- **latency:** Capture failure context in under 1 second; choose a deterministic retry in under 3 seconds; allow up to 2 alternative attempts for ordinary tasks, with progress returned to the pendant. Do not silently loop.
- **cost:** Usually no extra model call for known exit codes, missing paths, offline bridge, or permission errors. One background call for an unfamiliar failure; planner cost only for ambiguous multi-step recovery. Local diagnostic output is the dominant storage cost, not API cost.
- **security:** The recovery executor retains the owner's deliberate unrestricted shell policy and adds no approval gate. Diagnostic bundles must redact environment secrets, authorization headers, cookies, and full file contents; cap stdout/stderr and never send raw shell output to relay by default. Retries must preserve the original job/action identity and label every mutation, especially when an alternative command could have different side effects. Ask for confirmation only if the original task itself required it; recovery must not invent a broader goal.
- **missing:** A typed failure taxonomy spanning shell exit/timeout, app automation errors, browser bridge state, and Mac permission state; A bounded recovery planner that maps each failure class to alternate commands or surfaces and records why each was attempted; A local diagnostic bundle attached to the job receipt (argv/command fingerprint, cwd, exit code, duration, relevant status probes, redacted stderr); A retry ledger with attempt IDs, effect summaries, and a final owner-readable explanation surfaced through relay_job_status and pendant events

### "Take the file I mention on my Mac, verify that it is the right version, upload it to the matching form in my logged-in browser, and show me the exact file, destination, and fields before anything is submitted."
- **useful because:** The owner cannot currently bridge a local artifact and an authenticated web workflow as one coherent task: finding the correct file, validating it, selecting the right private tab, and presenting a trustworthy pre-submit preview are split across surfaces. This removes a tedious, error-prone handoff while still stopping before the irreversible submit.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension
- **model tier:** Background tier for file inventory, metadata/hash comparison, and deterministic tab/form matching; planner only when the requested file or destination is ambiguous; realtime only for concise status and the review prompt.
- **latency:** Find and validate a candidate within 3 seconds for a named path; identify the matching logged-in tab within 5 seconds; produce a review package within 10 seconds. No upload or submit should happen after the review package until the owner explicitly approves.
- **cost:** No model call for exact paths, hashes, MIME/size, and typed browser metadata. One background call for semantic matching of filenames to fields; planner only for ambiguity. Browser screenshot/DOM extraction and local hashing dominate latency, not tokens.
- **security:** Local files can contain sensitive data, and authenticated pages can contain private account information. Keep the file on the Mac until the browser upload is approved; send only metadata and a redacted field preview to relay. Bind the review to file hash, tab/session ID, URL, and form-field locators so a changed file or navigated tab invalidates it. Never submit automatically.
- **missing:** A local artifact manifest/read-and-hash operation exposed to the planner without returning file contents by default; A browser upload action that accepts a local artifact handle, reports selected filename/hash and target field, and supports a staged-not-submitted state; A cross-surface review capsule joining file hash, destination URL/tab, field values, and screenshot/DOM evidence; An approval-bound commit that revalidates the file and tab immediately before upload/submit


## Changes it proposed to its own stack

### `browser-harness` — Add an offline-aware command lifecycle between the existing browser queue and job receipts. Before dispatching any browser_* action, read bridge liveness and, when offline, immediately persist a typed `waiting_for_browser` result (with health timestamp and no 45-second action timeout). Keep the original job/action id and park it rather than enqueueing duplicates. On POST /browser/heartbeat or the poll loop, claim parked actions atomically and resume incomplete IDs; write one receipt transition (`waiting_for_browser` → `running` → `completed|failed`). Emit a compact relay event for the transition so the pendant can speak the status, while `/jobs/:id` remains the source of truth.
- **owner gets:** Safari tasks stop burning time and generating duplicate commands when the extension is closed. The owner hears the real reason immediately, can walk away, and receives one trustworthy completion or failure instead of repeated timeout noise.
- effort: Medium: browser queue state transition and atomic claim, executor preflight, heartbeat hook, receipt schema extension, and relay event projection; add crash/reconnect and duplicate-action tests.  ·  risk: A reconnect race could run an action twice or resume a stale private-page goal. Preserve stable action IDs, claim leases, and terminal receipts; on crash, recover only unexpired waiting/running leases and report ambiguous actions rather than replaying them blindly. This changes timing/status, not authorization or the owner's maximum-access policy.
- cost: Negligible storage and health requests; materially fewer planner retries and browser round trips. No additional model call is required for the state machine.  ·  latency: Offline response falls from the observed ~45 seconds to about 1–2 seconds; reconnect adds at most one heartbeat interval (target 5–10 seconds).
- security: No new data access. Keep page contents in the browser bridge; relay receives only job ID, state, and sanitized error. Retain existing receipts and authenticated session affinity.
- depends on: A durable browser job runner/queue (chg-16bc5dee) or equivalent command persistence; Existing browser heartbeat/poll/result routes and action receipts (chg-14accc01, chg-5fc73ce3); A relay event path that can deduplicate notifications by job ID

### `dashboard-ux` — Turn the existing /ops/snapshot permission state into a live 'Mac reachability' panel and machine-readable preflight: show Accessibility, Screen Recording, browser bridge, and relay states separately with the exact blocked surfaces (for example mac-vision unavailable while shell remains usable), last-seen timestamps, and deep links/actions to open the relevant System Settings pane. Attach the same compact preflight summary to failed job receipts and expose it to the relay, without preventing any action.
- **owner gets:** The owner can understand why a visual or browser task failed and fix only the missing permission, instead of hearing a generic failure or repeatedly retrying a capability the Mac cannot currently provide. Shell and other working surfaces remain available.
- effort: Small to medium: normalize /ops/snapshot permission fields, add a dashboard card and typed failure metadata, and map common macOS settings destinations; test stale/offline transitions.  ·  risk: Permission details can become stale or expose local app names. Timestamp every observation, limit relay speech to the relevant missing capability, and never claim readiness from cached data without labeling it. Opening settings should be an ordinary reversible Mac action, not an approval gate.
- cost: No model cost; one lightweight status poll and a small UI/event payload.  ·  latency: Adds milliseconds to failures and makes diagnosis faster; no impact on successful actions.
- security: Read-only permission metadata is local; do not transmit host fingerprints or full application lists to the relay. Deep links should remain on-device.
- depends on: GET /ops/snapshot; GET /ops/status; GET /browser/status; mac_read_diagnostics; mac_execute_typed_actions


## What it asked for

_Nothing._
## Its own summary

Discovered the live Mac state and built two concrete additions past the existing receipt work: (1) browser actions should fast-fail into a durable waiting_for_browser state, resume on heartbeat without duplicate action IDs, and notify the pendant once; live evidence is 45-second offline failures and 5 pending browser commands; (2) expose a permission/reachability panel and typed failure context distinguishing shell availability from unavailable mac-vision/browser surfaces. I do not need another permission or tool to specify either change. I have asked browser-extension and relay-realtime about their reconnect/event semantics; their replies can refine implementation next round.

**Biggest unknown:** Whether the browser bridge already has an atomic claim/lease or reconnect mechanism hidden behind its heartbeat/poll routes; without that, resume safety needs to be added in the durable browser runner.

