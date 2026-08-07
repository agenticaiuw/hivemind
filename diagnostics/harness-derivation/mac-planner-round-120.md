# Harness derivation — mac-planner — round 120

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do this when I’m no longer using the Mac, and tell me on the pendant when it’s finished.”"
- **useful because:** The owner can hand off a multi-step desktop task without interrupting active work. The system waits for a safe idle/focus boundary, detects when the original plan is stale, replans against current Mac state instead of blindly typing into the wrong app, and delivers a concise completion or failure receipt to the worn device.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the cheaper background planner for scheduling, state comparison, and retries; reserve realtime only for the pendant’s short acknowledgement and final spoken notification. Use vision only if Accessibility/Screen Recording are later granted; otherwise use AppleScript and read-only inspection.
- **latency:** Acknowledge the handoff immediately (<2 s); poll state every 30–60 s while deferred; start within one idle boundary; completion notification within 5 s of the final receipt. No microphone needs to remain open on the Mac.
- **cost:** Low per handoff: mostly local inspection and a background model call only when a plan becomes stale; realtime cost is limited to two short utterances. Dominant cost is any vision-based replan, which should be avoided unless required.
- **security:** The Mac state fingerprint may contain app names, URLs, and file paths, so keep raw details local and send only a redacted status to relay. Never transmit page contents merely to decide idleness. Since owner policy is maximum access, this is not a blocking approval gate; it must still expose the exact action receipt and support cancel/undo where available. Browser work must pause when its bridge is offline rather than accumulating unbounded retries.
- **missing:** A first-class deferred-job state with wake conditions (idle, focus change, meeting end, browser online); A compact local state fingerprint and plan-version/precondition contract for POST /execute; A scheduler that can replan stale jobs and bound browser pending-command retention; A relay push event that links the final Mac receipt to a pendant notification; Owner-configurable quiet hours and an explicit ‘run now’ / ‘cancel’ pendant gesture

### "“I’m leaving the Mac. Save exactly where I am, and when I come back—or ask from the pendant—put me back into that work without losing anything.”"
- **useful because:** Today a Mac task is tied to the machine’s transient UI state. After sleep, a crash, or moving away, the owner must reconstruct the work manually. This would create a crash-safe, privacy-preserving continuation capsule: what was open, the relevant browser tabs, selected document locations, unsaved draft identity, and the last confirmed action. The pendant could give a short spoken ‘you were here’ summary, while the Mac could restore the workspace and detect conflicts before touching files or tabs.
- **path:** mac-planner → mac-vision → browser-extension → relay-realtime → pendant → dashboard
- **model tier:** Use a local deterministic checkpoint builder for app/window/tab/document metadata and hashes. Use a cheaper background model to summarize and reconcile checkpoints. Use realtime only for the pendant’s short retrieval request and spoken summary; use vision only for apps whose state cannot be represented through AppleScript or structured inspection.
- **latency:** Checkpoint in under 2 seconds when the owner presses a pendant button or says a leave-taking phrase. Spoken recall in under 3 seconds from the relay. Workspace restoration in under 10 seconds, with any conflict surfaced before mutation.
- **cost:** Near-zero model cost for capture and restore; one small background summarization call per checkpoint or only when requested. Storage is small encrypted metadata plus optional local-only document hashes. Vision fallback is the dominant cost and should be exceptional.
- **security:** Never upload document contents, passwords, cookies, or page secrets. Store sensitive locators and browser session identifiers only on the Mac; relay receives an opaque capsule ID and redacted summary. Restore must be conflict-aware: if a file, tab, or draft changed since capture, open a comparison instead of overwriting. Provide retention expiry and one-button deletion from the pendant/dashboard.
- **missing:** A crash-safe checkpoint capsule format spanning Mac workspace, browser session, and the current pendant task; A local browser adapter that exports/restores tab identity without exposing authenticated page contents; Conflict detection and merge presentation for changed files, drafts, or navigations; A relay endpoint for opaque capsule retrieval and pendant notification; A restore executor that can reopen safe context while refusing to overwrite changed work

### "“Only let my pendant unlock or resume sensitive Mac work when I’m physically near it.”"
- **useful because:** The owner could safely hand off drafts, account pages, and other private work to the Mac without making the relay a standing remote-control key. Physical pendant proximity becomes a presence signal: the relay may prepare work while the owner is away, but restoration or sensitive continuation waits until the pendant is nearby and the Mac verifies the same paired device.
- **path:** pendant → mac-planner → relay-realtime → browser-extension → dashboard
- **model tier:** No realtime reasoning is needed for proximity verification. Use firmware and local Mac cryptographic checks for the common path; use a background model only to explain why a capsule is waiting or summarize what will resume.
- **latency:** Presence verification under 1 second when the pendant arrives; resume notification under 3 seconds. Remote preparation remains asynchronous and must not block on the pendant.
- **cost:** Negligible model cost. Requires a small BLE presence protocol and key storage; relay storage remains opaque identifiers and status only.
- **security:** Use rotating authenticated BLE challenges, not RSSI alone, and bind keys to the pendant and local Mac. Do not treat proximity as approval for irreversible actions; it only unlocks restoration of a previously prepared context. Revocation, lost-pendant reset, replay protection, and a local-only fallback are mandatory. Browser cookies and page contents remain on the Mac.
- **missing:** A pendant-to-Mac authenticated BLE presence channel with rotating challenges; Per-capsule sensitivity classes and a local resume policy; Mac secure key storage and pairing/revocation UI; Relay support for prepare-while-away versus resume-when-present states; A pendant gesture to deny or discard a waiting sensitive capsule


## Changes it proposed to its own stack

### `mac-harness` — Add a local plan-validity envelope around every /execute job: capture a redacted state fingerprint (foreground app, running-app set, browser online/session IDs, relevant path existence, and a monotonically increasing machine-context version) at plan time; before each mutating step compare it, mark the job stale on mismatch, and enqueue a background replan rather than executing stale coordinates. Add explicit deferred_until / wake_condition / quiet-hours fields and a bounded browser-offline backoff that expires old commands with receipts.
- **owner gets:** Tasks handed off from the pendant will stop acting on yesterday’s screen or a different document. The owner can keep working uninterrupted and receive a truthful “deferred, replanned, completed, or expired” result instead of a silent failure or wrong-app action.
- effort: Medium: local state fingerprint module, job schema migration, scheduler/backoff loop, and receipt/dashboard fields; no new model is needed for the common case.  ·  risk: A false mismatch can defer a task unnecessarily; recover by allowing a ‘run now’ command and recording the compared fields. A missed mismatch is mitigated by checking before every mutating step, not only at job start. Browser commands must be idempotent or expire rather than replay blindly.
- cost: Negligible API cost; local JSON/D1 writes and periodic inspection. Background replans add a small text-model call only on actual drift.  ·  latency: Adds tens to hundreds of milliseconds per step for local comparison; deferred work starts at the next wake boundary rather than immediately.
- security: Keep raw URLs, file paths, and window titles local; relay receives only state class and receipt IDs. Fingerprints need TTL and deletion with the job.
- depends on: The existing /execute job tracker and receipts; A scheduler capable of wake conditions and bounded retries; A relay event mapping job receipts to pendant notifications; Browser bridge heartbeat/offline status (currently browser is offline with 9 pending commands)


## What it asked for

_Nothing._
