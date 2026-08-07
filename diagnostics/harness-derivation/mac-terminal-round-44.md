# Harness derivation — mac-terminal — round 44

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent readiness and browser execution** — Live /ops/status shows fullControlMode and planner enabled, but agent ready=false because Accessibility and Screen Recording permissions are missing; browser extension offline with 3 pending commands. /jobs shows browser_navigate failures wait ~45 seconds before reporting offline.
  - evidence: GET /ops/status and GET /jobs probes at 2026-08-07T10:25Z

## Capabilities it proposed

### "Why can't you do that on my Mac right now—and what should I do?"
- **useful because:** Today a failed browser action only surfaces a generic timeout/error. The owner needs an immediate, actionable explanation that distinguishes the Mac agent, permissions, network/relay, and browser extension, without exposing secrets or asking them to debug logs.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic first: relay/mac status aggregation and rule-based diagnosis; use background gpt-4.1-mini only to turn the structured diagnosis into a concise spoken explanation. Do not spend realtime on this unless the owner is already in a live conversation.
- **latency:** Under 1 second for status aggregation and diagnosis; under 2 seconds including optional background wording. Offline Mac should yield the last-seen timestamp and a clear stale-status answer.
- **cost:** Usually zero model cost for the deterministic path; occasional short gpt-4.1-mini wording call, dominated by the existing status context rather than completion tokens.
- **security:** Return health metadata only (online state, heartbeat age, permission class, queue count, last error code), never URLs, page text, auth cookies, command strings, or bearer tokens. Require no confirmation because this is read-only.
- **missing:** A single authenticated readiness schema shared by Mac agent, browser bridge, and relay; Fast browser preflight/circuit-breaker so diagnosis happens before a 45-second timeout; Pendant/relay intent and spoken response for readiness diagnosis; Dashboard view of last-seen and remediation steps

### "Fix whatever is preventing that Mac task, or walk me through the exact fix from my pendant."
- **useful because:** When the Mac agent or browser bridge is unavailable, the owner currently gets a failure but must diagnose permissions, Safari extension state, and queued work themselves. The owner should be able to ask from the wearable and receive a short explanation plus guided recovery: open the correct Mac settings pane, surface the relevant extension state, and confirm when the task is safe to retry. Security permissions must never be silently changed.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic health classification and typed Mac actions for settings navigation; use the realtime model only for the live spoken interaction and a background model for generating a concise remediation script from structured status. No vision or expensive planner call unless the typed route cannot identify the settings pane.
- **latency:** First spoken diagnosis within 2 seconds. Opening the relevant System Settings pane within 3 seconds. Re-check readiness after the owner changes a permission or enables the extension, then offer retry without automatically repeating an unsafe or non-idempotent task.
- **cost:** Near-zero for health checks and typed navigation; one short realtime turn for the conversation. Background wording is optional and should be under a few cents at most; the dominant cost is live voice, not Mac control.
- **security:** The relay must receive only permission classes, extension heartbeat, queue identifiers, and error codes—not cookies, page text, or command strings. Changing Accessibility, Screen Recording, or browser-extension permissions requires the owner to do it in macOS UI. Any deferred task must display its exact action and require the existing owner policy for high-impact work before retrying.
- **missing:** A typed remediation catalog mapping readiness/error codes to exact macOS settings destinations and browser-bridge recovery steps; A Mac endpoint that reports remediation progress and re-checks permissions/extension heartbeat after the owner acts; A relay intent that binds the spoken recovery session to the failed job without replaying it; A dashboard card showing the failed job, why it stopped, the owner action required, and whether retry is safe


## Changes it proposed to its own stack

### `browser-harness` — Add a synchronous browser preflight and circuit breaker in the Mac/browser bridge: before enqueueing any browser_* action, consult the latest heartbeat/status, return a typed OFFLINE result immediately when no extension has polled recently, and mark queued commands as blocked_until_online rather than letting them time out after ~45 seconds. On the next heartbeat, retry each command with its original session/request id and emit one receipt linking the preflight failure, retry, and final result. Expose a compact readiness object (extension age, pending count, required Mac permissions) for relay and pendant status queries.
- **owner gets:** Browser requests fail honestly in seconds instead of leaving the owner waiting nearly a minute, and a spoken Mac-status answer can say exactly whether the issue is Safari/extension, Accessibility, or Screen Recording. When the owner reopens the bridge, work resumes instead of being lost or duplicated.
- effort: Small-to-medium: bridge heartbeat freshness/circuit-breaker, queue state transition and receipt linkage, plus one status projection consumed by relay/mac-planner.  ·  risk: A stale heartbeat could be misclassified as offline; use a conservative freshness window and retain manual retry. Retrying a write could duplicate effects, so only auto-retry commands carrying an idempotency key; otherwise require planner reissue. Existing pending commands need a migration state.
- cost: Negligible API cost; saves repeated planner calls and long failed execution attempts. Local implementation only.  ·  latency: Offline response under 100 ms instead of ~45 s; online path adds one local status check, typically <50 ms.
- security: No new data access. Status exposes only extension/permission health, not page contents; preserve existing auth and session affinity.
- depends on: A browser heartbeat/status endpoint with timestamp and pending-command visibility; Stable idempotency keys and receipt linkage across browser retries; Relay/mac-planner status projection


## What it asked for

_Nothing._
