# Harness derivation — browser-extension — round 59

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser command delivery** — The live browser queue contains a navigate command claimed twice by the offline stub device home-chrome (attempts=2, claimedBy=home-chrome), while /browser/status says home-chrome offline and Safari is absent; four commands are pending. Device fencing/reclaim is not functioning and can strand or misroute authenticated work.
  - evidence: GET /browser/status => online:false, only home-chrome offline, pendingCommands:4; GET /browser/poll => command browser_fc12217f-842e-4751-8697-c6c71706bd52 status processing, claimedBy home-chrome, attempts 2.

## Capabilities it proposed

### "“If Safari goes offline while you’re checking my logged-in pages, keep the task alive and tell me when it resumes—without doing any step twice.”"
- **useful because:** This is the browser's unique value made dependable: the relay can remain awake, the Mac can run the durable task, and Safari can provide private sessions when available. The owner gets a truthful completion report instead of a silent timeout, while acknowledged reads are not repeated and irreversible actions are never replayed automatically.
- **path:** pendant: announce pause/resume and concise completion receipt → relay: retain task state, wake/retry notifications, and deliver a durable job event → mac-planner: split the request into typed browser steps and reconcile receipts → browser-extension: execute only on a healthy, device-fenced Safari session and return cited page evidence → dashboard: show queued, stale-device, resumed, and completed steps with timestamps
- **model tier:** Use a cheaper background text model for job decomposition, retries, and evidence reconciliation; use realtime only if the owner asks a live follow-up through the pendant. Browser extraction can use the existing planner and deterministic selectors before escalating to a larger model.
- **latency:** A healthy step should feel interactive (under 45 seconds, existing bridge limit). On disconnect, notify within one minute, then resume on the next Safari heartbeat; final report arrives asynchronously rather than holding the voice turn open.
- **cost:** Low per task: mostly Mac/relay storage and browser bridge calls; background model calls dominate, with realtime avoided unless conversational intervention is needed. No public Browser Run budget should be spent on owner-private pages.
- **security:** Only the paired Safari device may access logged-in pages; never fail over private work to a public browser. Persist minimal URL/title/snippet evidence with retention controls. Auto-replay reads only; pause before submit/send/purchase and surface the exact pending action.
- **missing:** Device-fenced lease/reclaim and stale-command quarantine; Durable browser job runner with step-level receipts and resume semantics; Relay-to-Mac durable job event delivery and pendant notification integration

### "“Give the Mac and my pendant only the parts of this logged-in page they need, keep the rest inside Safari, and let me revoke that handoff later.”"
- **useful because:** Today an authenticated browser read tends to become an all-or-nothing page extraction. The owner should be able to use Mac planning and pendant conversation without leaking unrelated private content from the logged-in tab. This creates a deliberate, revocable privacy boundary for multi-surface work: Safari proves and selects the source, the Mac acts on a minimal projection, and the pendant speaks only the approved facts.
- **path:** browser-extension: identify the authenticated source and produce a field/region-level projection with URL, timestamps, and sensitivity labels → mac-planner: request only named fields for the current task and perform reasoning/actions over that projection → relay: hold an encrypted, expiring handoff token and route revocation/status events → pendant: read back exactly what was shared and offer a one-phrase revoke command → dashboard: show active handoffs, fields shared, recipients, expiry, and revoke history
- **model tier:** Use a cheap background model or deterministic rules for field selection, redaction, expiry, and audit formatting; use realtime only for the owner's live request or spoken revoke. Escalate ambiguous semantic redaction to a stronger model only after showing the candidate fields.
- **latency:** Initial field inventory in a few seconds for a normal page; handoff under 10 seconds. Revocation should take effect within one relay heartbeat and be acknowledged on the pendant.
- **cost:** Low: browser extraction and relay metadata dominate; model cost is limited to ambiguous field classification. No need to send full page HTML or screenshots to the cloud.
- **security:** The browser extension must be the only component allowed to read the full page. Share tokens should be scoped to recipient, fields, task, and expiry; encrypt projections in transit and at rest; redact secrets such as passwords, tokens, payment numbers, and hidden form values by default. Revocation must prevent future reads and invalidate cached projections, while acknowledging that already spoken audio cannot be unspoken.
- **missing:** A field-level browser extraction and redaction protocol rather than whole-page results; Relay-managed scoped handoff tokens with expiry, revocation, and recipient binding; Pendant command and dashboard UI for inspecting and revoking active private-data handoffs; Cache/audio retention hooks that delete revoked projections where technically possible


## Changes it proposed to its own stack

### `browser-harness` — Add device-fenced browser command delivery and recovery: every command carries a target device (default the last healthy authenticated Safari device), poll claims require a live heartbeat lease for that exact device, and a command claimed by an offline/stale device is atomically returned to queued after a short lease. Persist attempt history and terminal reason, deduplicate result posts by commandId/action idempotency key, and expose a reconnect/replay endpoint that resumes only unacknowledged steps without repeating acknowledged mutations. Quarantine unknown or never-seen registrations such as home-chrome instead of allowing them to claim work.
- **owner gets:** A browser task will not silently disappear into a dead laptop/extension or get executed in the wrong browser. If Safari briefly sleeps or the Mac bridge restarts, the pendant can truthfully resume the research and report exactly which pages were read, rather than leaving four invisible pending commands or duplicating a form fill.
- effort: Moderate: extend browserBridge command schema and poll transaction, heartbeat lease checks, durable attempt/result journal, and a small recovery worker; add crash/reconnect tests for stale claims, duplicate results, and Safari-vs-unknown-device routing.  ·  risk: A too-short lease could replay a slow navigation; a too-long lease delays recovery. Mitigate with action-specific lease durations and idempotency keys, and never auto-replay irreversible submit/send actions. If recovery fails, leave the job queued with an explicit stale-device error rather than dropping it.
- cost: Negligible API cost; a few D1/local JSON records per browser step and a lightweight periodic sweep.  ·  latency: Normal commands gain one heartbeat/lease validation (milliseconds). Recovery waits for the next healthy heartbeat plus lease expiry; no added latency for a healthy Safari.
- security: Improves isolation by preventing an untrusted or stale extension registration from claiming authenticated commands. Device IDs and URLs remain sensitive and should be retained only under existing browser-job retention.
- depends on: A durable browser job/result journal (the remaining half of chg-16bc5dee); The existing browser heartbeat and typed action/idempotency records


## What it asked for

_Nothing._
## Its own summary

Discovered and recorded a live, previously unaddressed browser reliability/security defect: four pending commands exist while the only registered device is offline, and a command is still processing under the never-seen home-chrome stub (attempts=2). Proposed a device-fenced lease/reclaim/quarantine layer with exactly-once result reconciliation, plus a cross-surface capability for pausing and resuming authenticated Safari work without duplicate steps. Told mac-planner to avoid private browser routing while offline.

**Biggest unknown:** The exact durable storage and heartbeat implementation currently used by browserBridge are not exposed in this harness, so I cannot determine whether lease recovery can be added locally or requires relay/D1 changes. Still needed: durable browser job runner, device-fenced command leases, and relay-to-pendant job-event delivery.

