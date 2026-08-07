# Harness derivation — browser-extension — round 79

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-command delivery liveness** — At 2026-08-07T12:48Z /browser/status reported online=false with home-chrome only and pendingCommands=6, yet /browser/poll returned command browser_fc12217f... claimedBy home-chrome attempts=7 with action type navigate and empty params. A browser_navigate /execute waited >20s and the jobs record shows the normal 45s timeout.
  - evidence: GET /browser/status, GET /browser/poll, GET /jobs, and POST /execute browser_navigate probes in round 79

## Capabilities it proposed

### "“Remember the private page I’m working on, and let me resume it later—even if Safari or my Mac restarted—without exposing its contents in the voice transcript.”"
- **useful because:** Today a logged-in browser task is stranded when Safari closes, a tab is replaced, or the Mac reboots. The owner should be able to leave a research or form workflow and resume from the pendant with the exact page, position, and next safe step, while keeping private page text out of relay logs and spoken history. This is more than page watching: it is privacy-preserving cross-device continuity for an in-progress authenticated task.
- **path:** browser-extension → mac-planner → relay-realtime → unified → dashboard-ux
- **model tier:** Use the cheaper background model to maintain a compact semantic bookmark and redact sensitive fields; use realtime only when the owner asks to resume by voice; use Mac-local planning for tab reattachment and local encrypted storage.
- **latency:** Resume acknowledgement under 2 seconds when Safari is online; reattach and restore the tab/scroll/form draft within 10 seconds. If offline, acknowledge locally and resume when the heartbeat returns.
- **cost:** Low per resume: one short realtime turn plus a background extraction; dominant cost is the initial private-page semantic bookmark, not subsequent pointer-based resumes. Local encrypted state avoids repeated page-text context charges.
- **security:** Never send raw page text or form values to relay logs by default. Store an encrypted, redacted bookmark on the Mac keyed to a browser session and tab identity; retain only URL origin, title hash, DOM/semantic anchors, scroll position, and a hash of draft fields. Require explicit owner confirmation before restoring or altering any sensitive form field. Expire bookmarks and invalidate them on logout or session mismatch.
- **missing:** A browser-resume protocol that can reattach a semantic bookmark to a new tab after restart, with anchor validation and bounded fallback search; Mac-local encrypted storage for redacted private-page bookmarks and a restore-status API; Relay/unified routing that can resolve “that page/task” to a bookmark without injecting page contents into the voice transcript; A privacy-aware dashboard showing bookmark age, origin, expiry, and whether a draft is present


## Changes it proposed to its own stack

### `browser-harness` — Make browser command delivery liveness-aware and self-healing: bind each queued command to a registered device with a heartbeat lease and tab/session intent; never let an offline or stale device claim/retry it. On enqueue, check the lease and return a typed browser_unavailable result immediately (instead of waiting 45 seconds). Add command TTL/attempt limits, explicit requeue to a live device, and a cleanup endpoint/worker for the six currently pending commands. Preserve the original URL/action and device target in the receipt so a malformed retry cannot become an empty navigate.
- **owner gets:** When Safari is closed or the extension is disconnected, the owner gets an immediate honest answer instead of waiting nearly a minute, and commands will not disappear into a phantom Chrome device. When Safari reconnects, still-valid work can resume safely without duplicate navigation or stale actions.
- effort: Medium: bridge queue schema and enqueue/claim logic, heartbeat lease checks, expiry sweep, typed failure receipts, and dashboard/job status display; extension protocol needs no behavior change beyond its existing heartbeat.  ·  risk: A transient heartbeat gap could reject a command that would have succeeded; mitigate with a short grace lease and automatic requeue. Expiry must never execute an old form-fill or navigation after intent is stale. Existing pending commands need migration and explicit failed/expired states.
- cost: Negligible API cost; one small periodic sweep and heartbeat metadata in D1/local state.  ·  latency: Offline requests fail in milliseconds rather than 45 seconds; online requests remain unchanged, with at most one lease check.
- security: Improves isolation by preventing an unintended device from claiming commands and makes target-device affinity auditable; no page data leaves the existing browser bridge.
- depends on: A durable browser job/queue representation (chg-16bc5dee); Request IDs, idempotency, and tab/session affinity (chg-14accc01); A heartbeat/status source for registered browser devices

### `browser-harness` — Add a privacy-preserving resumable-task bookmark layer, distinct from page watches: on an owner-marked in-progress browser task, capture only encrypted origin/title hash, tab/window identity, semantic anchor candidates, scroll position, draft-field presence (not values), and an expiry. On resume, validate the current authenticated session, reattach or navigate to the origin, relocate the anchor, and return a typed confidence result (restored / needs owner review / session missing) without copying page text into relay logs. Bind bookmarks to the originating device and invalidate them on logout, tab replacement, or expiry.
- **owner gets:** They can pause a private research or form workflow and continue later after Safari or the Mac restarts, without having to explain the task again or leak the page into voice history. The system tells them honestly when it cannot safely restore the exact place instead of silently operating on the wrong page.
- effort: Medium-to-large: encrypted local bookmark store, browserBridge resume/anchor protocol, session validation, restore confidence and dashboard controls, plus unified routing for references such as “that page.”  ·  risk: DOM changes may move an anchor or a login may expire; safe recovery is to stop with a review-needed result, never guess. A compromised Mac could still access the encrypted bookmark while unlocked, so use OS keychain storage and short TTLs.
- cost: Small background extraction cost at task pause; resume is mostly local and pointer-based, reducing repeated page-context token spend. No new hardware cost.  ·  latency: Pause adds under a second; online resume should complete in seconds, while offline resume queues rather than blocking the pendant conversation.
- security: Raw authenticated content and form values remain on the Mac; relay receives only bookmark metadata and restore status. Session and origin binding prevent replaying a bookmark into another account.
- depends on: A durable browser session store exposed by GET /browser/sessions; Reliable browser command IDs and typed results from POST /execute and POST /browser/result/:commandId; A Mac-local encrypted persistence and a unified reference resolver


## What it asked for

_Nothing._
## Its own summary

Fresh live checks found a concrete browser-harness defect: the bridge reports no online browser and six pending commands, but /browser/poll still lets offline home-chrome claim a stale navigate (attempt 7, empty params), while /execute waits 45 seconds before failing. I recorded and proposed a liveness-aware queue fix: heartbeat leases, target-device binding, fail-fast offline errors, TTL/attempt limits, safe requeue, and cleanup/typed receipts. I also notified mac-terminal and unified.

**Biggest unknown:** Whether Safari 26.5.2 is currently open with the AI Pendant extension enabled; the live registry has lost Safari and only shows offline home-chrome. To perform any authenticated-page task, the owner still needs to open Safari, enable the extension, and leave at least one target tab open. Engineering-wise, the exact queue persistence/expiry implementation remains unverified.

