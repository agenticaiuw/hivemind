# Harness derivation — mac-planner — round 52

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-readiness** — Live Mac bridge is online and full-control enabled, but agent ready=false because Accessibility trusted=false and Screen Recording granted=false; computer-use loop disabled and vision upload consent false. Browser extension is offline with 3 pending commands. Automation grants are present and relay reachable.
  - evidence: GET /ops/status HTTP 200 at 2026-08-07T10:25Z

## Capabilities it proposed

### "“Can you handle this on my computer?” — before acting, tell me which surfaces are actually available, use the best available route, and if something is unavailable, keep working with a degraded plan and tell me exactly what remains."
- **useful because:** Today the relay can report a Mac bridge as online even though Accessibility and Screen Recording are missing, while browser commands sit pending offline. The owner needs one honest answer instead of a silent failure or a misleading 'done': a live preflight, capability-aware routing, durable retry, and a completion receipt that distinguishes completed, deferred, and impossible steps.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheap background model for periodic health classification and retry planning; use realtime only to answer the owner's immediate spoken question. The relay performs deterministic checks and routes steps; the model summarizes the result and chooses among already-declared routes.
- **latency:** Initial preflight under 1 second from cached health, with a live refresh bounded to 3 seconds. Reconnect/retry in the background with exponential backoff and quiet hours; speak immediately with the usable subset and later deliver a concise completion receipt.
- **cost:** About $0.001–$0.01 per request depending on whether a model is needed; most preflights are deterministic and free. Costs are dominated by any later vision/browser extraction, not health checks.
- **security:** Do not transmit page contents or screenshots merely for health checks. Report permission state without exposing tokens. Retrying must preserve request IDs and tab/session affinity, and should not duplicate mutations. Keep the owner's maximum-access policy: this is observability and routing, not a new approval gate. Opening System Settings to remediate permissions or changing browser state should be an explicit, separately logged action.
- **missing:** A typed cross-surface readiness schema (surface, capability, freshness, reason, remediation, retryability) emitted by Mac bridge, browser bridge, and relay.; A router that computes a degraded execution plan from that schema and persists per-step state across reconnects.; A browser reconnect/queue worker that can safely reconcile the current 3 pending commands and classify them as stale, retryable, or completed.; A dashboard and pendant receipt format showing completed/deferred/blocked steps and the exact missing permission or offline dependency.; An optional deterministic Mac remediation flow that opens the relevant Privacy & Security panes and rechecks readiness; it must not claim permissions were granted automatically.

### "“Do this when it won’t interrupt me.” Let the pendant capture the request, the relay understand my current interruption policy, and the Mac wait for a safe moment—such as not presenting, not in a call, and not typing—before carrying out the desktop work, then tell me what happened."
- **useful because:** Today a request is either acted on immediately or handled by coarse background scheduling. The owner cannot express a useful temporal constraint tied to their actual computer context: avoid stealing focus while presenting or composing, but act as soon as the risk passes. This would make hands-free delegation safe to use throughout the workday without requiring the owner to remember a later command.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Use deterministic Mac signals and calendar/Focus state for safety classification; use a cheap background model to interpret the natural-language constraint and compile it into predicates. Reserve realtime for the initial spoken capture and completion announcement.
- **latency:** Acknowledge capture in under 1 second. Evaluate context on a 5–15 second heartbeat while pending, execute within 2 seconds after the safe window opens, and announce completion promptly. Allow an owner-defined expiry so stale work does not run hours later.
- **cost:** Typically under $0.005 per request: one small interpretation call plus inexpensive heartbeat/state checks. The dominant cost is the requested desktop/browser work, not waiting for a safe context.
- **security:** The Mac should expose only coarse signals (foreground app category, call/presentation state, keyboard activity, Focus mode), not keystrokes or screen contents. Never infer that a sensitive operation is safe solely from inactivity; preserve the owner’s existing maximum-access execution policy while logging why the predicate passed. Pending plans need encrypted storage, expiry, and cancellation from the pendant/dashboard.
- **missing:** A shared interruption-policy vocabulary and compiler (predicates such as presenting, in-call, typing, focused-app, quiet-hours, and deadline).; A Mac context sampler that reports coarse, privacy-preserving activity and presentation/call state to the relay with freshness and confidence.; A durable constraint-aware scheduler that wakes on context changes rather than polling blindly, supports expiry/cancel, and resumes only unfinished idempotent steps.; A pendant command and receipt format for “when safe,” including current wait reason and a one-tap/one-button cancel path.; Integration with Calendar/Focus and the Mac/browser job ledger so a plan can be deferred without being mistaken for failed or completed.


## Changes it proposed to its own stack

### `integration` — Add a cross-surface execution ledger with a readiness snapshot attached to every plan. Before dispatch, the relay records each step's required capability (e.g. calendar-read, accessibility-ui, screen-capture, authenticated-tab), current provider health, freshness, and fallback. The Mac bridge and browser bridge heartbeat these typed capabilities; when a link or permission changes, the ledger re-plans only unfinished steps and emits a receipt with completed/deferred/failed plus remediation. Use idempotency keys and provider leases so reconnecting browser commands cannot be replayed blindly.
- **owner gets:** A request will stop disappearing into an offline browser queue or failing after several opaque retries. The owner gets useful partial results immediately, and later a truthful notification when the unavailable part becomes possible—without repeating actions that already happened.
- effort: Medium-high: define a shared schema, add bridge heartbeats and lease/ack handling, persist step state in D1/local job storage, add degraded planner and dashboard/pendant receipt rendering, then test crash/reconnect and stale-command cases.  ·  risk: Incorrect completion acknowledgements could cause skipped or duplicated mutations. Recover with provider-side idempotency keys, before/after receipts, expiry on leases, and a reconciliation pass that marks ambiguous steps for review rather than replaying them. Health data can become stale; every snapshot needs timestamp and TTL.
- cost: Negligible storage and heartbeat overhead; roughly a few hundred bytes per step plus periodic pings. Model cost can decrease because deterministic routing replaces repeated planner calls; extraction/vision costs remain unchanged.  ·  latency: Adds tens to a few hundred milliseconds for cached preflight; avoids long waits by dispatching usable steps immediately and moving unavailable work to background retry.
- security: Health metadata must exclude page contents, credentials, and screenshot data. Ledger entries should carry sensitivity labels and be visible in audit logs. No new blocking policy is introduced; the owner’s existing maximum-access setting remains effective.
- depends on: Shared typed readiness schema across Mac and browser bridges; Durable job/step ledger with idempotency and reconciliation; Browser reconnect worker and Mac permission-state reporting; Receipt support in relay, dashboard, and pendant


## What it asked for

_Nothing._
## Its own summary

Discovered live state and recorded it: Mac bridge/relay are online, but readiness is false because Accessibility and Screen Recording are not granted; computer-use is disabled and browser extension is offline with 3 pending commands. Proposed a new cross-surface capability and integration: capability-aware preflight, degraded routing, durable per-step execution ledger, idempotent reconnect/retry, and truthful pendant/dashboard receipts distinguishing completed, deferred, and failed work. This is observability/routing, not an approval gate, so it respects the owner’s maximum-access policy. I also informed mac-terminal of the readiness findings.

**Biggest unknown:** The newly granted mac_readonly_inspect tool has no implementation yet, so I could not independently inspect foreground apps, running apps, browser tabs, or local permission UI beyond /ops/status. The next needed infrastructure is the typed readiness heartbeat/ledger and a safe browser queue reconciliation path; separately, the owner must grant Accessibility and Screen Recording if they want GUI/vision actions to become ready.

