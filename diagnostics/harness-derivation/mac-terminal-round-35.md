# Harness derivation — mac-terminal — round 35

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent readiness and browser dependency** — Live /ops/status reports fullControlMode=true and relay reachable, but browser extension offline with 2 pending commands; accessibility and screen-recording are not granted, so computer-use loop is not ready. A recent browser_navigate job failed after 45s solely because extension was offline.
  - evidence: GET /ops/status HTTP 200 and GET /jobs HTTP 200 live responses in this round

## Capabilities it proposed

### "“If the computer or browser is unavailable, figure out another safe way to finish this, or keep trying until it is available, and tell me exactly what remains.”"
- **useful because:** Today a task can fail because one dependency is offline, leaving the owner to diagnose the Mac, reopen Safari, and repeat the request. The owner should get one resilient outcome: the system distinguishes an unavailable surface from a failed step, chooses a viable alternate surface when one exists, parks the rest when it does not, and resumes without duplicating completed work.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic readiness checks, dependency planning, receipt/idempotency handling, and retry scheduling for most of the workflow; use a cheap background model to explain a failure or select among known fallback plans; reserve realtime only for the owner's brief spoken update and any clarification.
- **latency:** Readiness and fallback selection under 500 ms; speak the blocker immediately instead of waiting for a timeout. Recovery may take minutes or hours, but the owner need not stay present; notify on completion or when human input is genuinely required.
- **cost:** Usually near-zero model cost for preflight, state transitions, and retries. Occasional background explanation/planning call, roughly $0.001–$0.02 depending on context; the dominant cost is repeated browser/vision execution, which should be avoided through typed receipts and step-level idempotency.
- **security:** Fallbacks must not export authenticated page contents to the relay or substitute a weaker surface for a sensitive action without an explicit policy match. Keep credentials and private DOM on the Mac/browser, send only task state and redacted receipts upstream, and require confirmation only for genuinely irreversible external effects—not for retries or reversible local work.
- **missing:** A cross-surface dependency graph describing which steps require browser, GUI permissions, shell, relay, or pendant presence; A durable state machine with parked, waiting-for-device, resumed, partially-complete, and terminal-failure states; Step-level idempotency keys and receipts shared by Mac, browser, relay, and faculty-action so recovery cannot repeat mutations; A readiness heartbeat and wake/resume signal from the browser bridge and Mac agent to the relay; A fallback planner that is constrained to approved equivalent routes and can explain why no equivalent exists; A single owner-facing completion/blocker protocol delivered both as a pendant utterance and a cited Mac dashboard record

### "“Don’t just tell me you did it—verify from the actual destination that it took effect, and tell me what you checked.”"
- **useful because:** Current completion receipts describe what the Mac agent attempted, but an attempted click, sent request, or local mutation is not proof that the destination accepted it. Independent postcondition checks would catch stale tabs, dropped network requests, UI false positives, and actions that partially applied before the owner relies on them.
- **path:** mac-planner → browser-extension → mac-vision → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic postcondition probes and source comparison first; use a cheap background model only to reconcile conflicting evidence or summarize the verification. Realtime is only needed to speak the short result.
- **latency:** Verification should begin immediately after each mutating step and complete within 2–5 seconds for local/browser state; allow a bounded wait for remote systems, then report pending verification rather than claiming success.
- **cost:** Minimal model cost when selectors, file hashes, process state, or API responses are deterministic. Occasional background reconciliation, roughly $0.001–$0.02; browser/vision calls dominate when a destination has no structured observable state.
- **security:** Verification may read sensitive destination state, so keep authenticated content on the originating Mac/browser and send only a redacted assertion plus evidence hash to the relay. Never treat an optimistic UI toast or local receipt as verified; for high-impact external actions, surface the exact evidence and distinguish accepted, observed, and unknown.
- **missing:** A typed postcondition schema for shell, GUI, browser, and relay actions, including acceptable evidence sources and freshness limits; Independent verification recipes that are separate from the action command and can reattach to the correct tab/session; A cross-surface evidence bundle linking before-state, action receipt, after-state, timestamp, and source locator/hash; Conflict handling when the Mac says success but the browser or remote destination still shows the old state; Owner-facing language and dashboard fields that clearly separate attempted, accepted, observed, and unverifiable outcomes


## Changes it proposed to its own stack

### `mac-harness` — Add a dependency-aware preflight and parked-job coordinator before execution. Each job declares required surfaces (shell, browser bridge, accessibility, screen recording, relay); the Mac agent snapshots readiness, immediately returns a typed blocked/parked receipt when a dependency is offline or permission-missing, and subscribes to bridge heartbeats to resume idempotently when readiness returns. Surface the exact blocker, age, retry count, and next action in /jobs and relay status, rather than spending tens of seconds timing out.
- **owner gets:** A request involving Safari or screen control would no longer silently burn 45 seconds and fail; the pendant could say “Safari bridge is offline—open Safari and enable the extension; I’ll continue automatically,” then finish the work when the Mac becomes ready.
- effort: Medium: capability requirement metadata, readiness snapshot, parked state machine, heartbeat-triggered resume, idempotency linkage, and receipt/dashboard fields.  ·  risk: A stale heartbeat could resume work unexpectedly or duplicate a mutation. Mitigate with idempotency keys, per-step receipts, lease expiry, and resume only from the last confirmed step; preserve the existing no-gate maximum-access policy.
- cost: Negligible API cost; avoids wasted planner retries and long failed computer-use calls. Small local state growth for parked jobs and readiness history.  ·  latency: Adds tens of milliseconds preflight; removes 30–120 second dead-end waits and enables immediate completion after bridge recovery.
- security: No new authority; readiness metadata may reveal local permissions/device state, so expose only to paired relay and redact paths/details from spoken summaries.
- depends on: durable job lifecycle with explicit parked/resume states; browser heartbeat/command queue; typed action receipts and idempotency keys


## What it asked for

_Nothing._
## Its own summary

Fresh discovery completed. Live Mac status: full-control shell is enabled and relay is reachable, but the browser bridge is offline with 2 pending commands; accessibility and screen-recording permissions are missing, so mac-vision is not ready. A recent browser job spent 45 seconds before failing solely on the offline bridge. I recorded this finding and proposed a new dependency-aware preflight/park/resume coordinator that reports blockers immediately and resumes idempotently after heartbeat recovery. The granted diagnostic interfaces exist in the schema but have no implementation, and the typed-action name is not discoverable; therefore I could not run local read-only diagnostics or inspect its contract. Still needed: implement the diagnostic backend and expose the typed action tool under a discoverable name; operationally, enable the browser extension and (if GUI automation is desired) Accessibility/Screen Recording permissions.

**Biggest unknown:** The exact local-agent job lifecycle and typed-action contract remain unavailable because the granted diagnostic/tool interfaces are unimplemented or not discoverable; I cannot verify how parked/resumed jobs should integrate until those contracts are exposed.

