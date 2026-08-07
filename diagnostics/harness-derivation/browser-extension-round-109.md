# Harness derivation — browser-extension — round 109

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability round 109** — Safari extension is currently offline (only home-chrome listed, offline; pendingCommands=10), while three persisted browser sessions reference stale Safari tabs from earlier. Browser work cannot execute until extension polling resumes; sessions need liveness validation before reuse.
  - evidence: GET /browser/status 200: online=false, home-chrome offline, pendingCommands=10. GET /browser/sessions 200: default/probe-form/probe-form2 with old tab IDs and lastUsedAt hours earlier.

## Capabilities it proposed

### "“If my Mac or Safari is temporarily unavailable, keep my logged-in browser task queued and finish it when the browser comes back—then tell me exactly what you found or prepared.”"
- **useful because:** Today a queued authenticated task simply times out when Safari stops polling, even though the owner’s login and session may still be recoverable later. This would make the pendant’s promise reliable across sleep, lid-close, Safari restarts, and brief extension outages, while still stopping before sends/submits/purchases.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use the cheap background model for retry classification, session liveness checks, and extraction diffs; use realtime only when the owner asks for an update or approval. Escalate to the full planner only when tab reattachment or the next step is ambiguous.
- **latency:** A health check every 1–5 minutes while a task is pending; resume within one polling interval after Safari returns. Spoken status should be immediate from the relay job record, without waiting for a browser round trip.
- **cost:** Low: mostly D1/job polling and one background classification per outage/resume. Dominant cost is the eventual authenticated extraction; no model call is needed for repeated offline checks.
- **security:** The relay must retain task intent but never copy cookies or page secrets. Reattach only to the same registered Safari device/session, validate URL/origin before continuing, and redact extracted private fields in status updates. Automatically perform only reads and reversible fills; stop and present a signed preview before any irreversible action. Notify the owner when a task resumes after an outage.
- **missing:** A durable browser job state machine with retry/backoff and an explicit WAITING_FOR_BROWSER state (the existing durable-runner proposal is broader but not yet live); A bridge watchdog/launch or wake hook on the Mac that can restore Safari polling, plus a way to distinguish stale tab IDs from a valid reattached tab; Session reattachment and origin validation when a tab/window is recreated; A resume notification linked to the pendant and a compact failure reason after a retry budget expires

### "“When a private website needs me to complete a CAPTCHA, 2FA, consent prompt, or other human-only step, tell me exactly what is blocking you, let me complete it in Safari, and continue the task automatically afterward.”"
- **useful because:** Authenticated browser work commonly fails at the boundary no automation should cross. Today the owner gets a timeout or a vague failure and must reconstruct the task. A pendant-directed handoff would preserve the exact step, reduce repeated navigation, and keep the owner in control of security challenges without exposing credentials to the model.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use a cheap background model or deterministic page heuristics to classify a blocked step and summarize the visible blocker; use realtime only to converse with the owner while they resolve it. Resume with the existing planner, not the expensive model, unless the post-challenge page is materially different.
- **latency:** Detect and notify within one browser result (seconds). Pause indefinitely or until an owner-configured expiry; after the owner completes the challenge, verify the page changed and continue within one polling interval.
- **cost:** Low: one classification at a blocker and one verification extraction. The dominant cost is only the original browser task; no repeated model calls during the pause.
- **security:** Never read, transcribe, or store OTP values, CAPTCHA answers, password fields, or recovery codes. The extension should return only blocker type, page origin, and a redacted instruction. Require the owner to perform the challenge in Safari. Resume only after origin/session identity and a page-state transition are verified; stop before irreversible submission and preserve a receipt of the handoff.
- **missing:** A first-class HUMAN_HANDOFF browser result and resumable step state, distinct from ordinary timeout/failure; Extension-side redaction and blocker detectors for password, OTP, CAPTCHA, passkey, consent, and native-dialog states; A pendant notification/acknowledgement channel that can wake the owner and mark the handoff resolved; A post-handoff verification probe that proves the challenge completed without capturing its secret contents; A durable pause/resume contract in the browser runner with an expiry and owner cancellation path


## Changes it proposed to its own stack

### `browser-harness` — Implement a Browser Continuity Coordinator between the durable job runner, Mac bridge, and Safari extension. It should turn command timeout into WAITING_FOR_BROWSER rather than FAILED; consume heartbeat/status transitions; invalidate tab IDs after a configurable stale interval; ask the Mac bridge to foreground/relaunch Safari and enable the extension when allowed; then reattach by origin/session identity, run a read-only probe, and resume from the next idempotent step. Persist an outage timeline and retry budget, and emit one pendant notification on resume or permanent expiry. Never replay a fill/click step unless its receipt proves it did not complete.
- **owner gets:** Closing the laptop or a Safari extension hiccup would no longer lose a private-page task or force the owner to start over. The owner gets a truthful “waiting / resumed / expired” result and avoids duplicate form edits or clicks.
- effort: Medium-high: coordinator state machine, heartbeat event handling, Mac bridge wake/foreground hook, session/origin reattachment, idempotency tests, and dashboard/pendant status text.  ·  risk: A recreated tab can show the wrong account or an interstitial; origin plus title/content probe must fail closed into WAITING_FOR_BROWSER. Duplicate mutation is the main risk, mitigated by receipts and only replaying explicitly idempotent read steps. Recovery is manual cancel/retry from the job record.
- cost: Negligible storage and polling cost; one cheap background classifier only for ambiguous reattachment. No browser page data needs to leave the Mac beyond existing extraction results.  ·  latency: Adds no latency while online. Recovery takes one heartbeat plus a probe (typically seconds), rather than a 45-second timeout per action.
- security: Preserves cookies on Safari; coordinator stores only device/session IDs, origin, hashes, and receipts. Mac wake/foreground must be scoped to the registered owner device and logged.
- depends on: Durable browser job runner / retry state (chg-16bc5dee backlog); Existing browser request IDs, tab affinity, and typed receipts (chg-14accc01 and chg-5fc73ce3); A Mac bridge action to wake or foreground Safari and a heartbeat transition event; A browser session reattachment primitive that verifies origin/account before resume


## What it asked for

_Nothing._
## Its own summary

Fresh live discovery found Safari is offline (home-chrome is also offline) with 10 pending browser commands, while persisted sessions point at stale tab IDs. I recorded the finding and alerted mac-planner. I proposed a cross-surface Browser Continuity Coordinator: preserve authenticated jobs as WAITING_FOR_BROWSER, have the Mac bridge recover Safari polling, validate a recreated tab’s origin/account, resume only idempotent steps, and report truthful waiting/resumed/expired status to the pendant. This builds on existing /execute, browser health/session routes, job status, heartbeat/poll/result, and receipts, but requires the missing coordinator and Safari wake/reattach primitives.

**Biggest unknown:** Whether the real Safari bridge can be programmatically foregrounded/re-enabled by the Mac harness, and how to prove a recreated tab is the same logged-in account without exposing page secrets. Browser usefulness remains blocked until Safari polls again.

