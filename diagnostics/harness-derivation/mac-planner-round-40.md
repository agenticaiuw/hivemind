# Harness derivation — mac-planner — round 40

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If my Mac or browser is unavailable, tell me what you last verified, how stale it is, and keep my task ready to resume when the device comes back.”"
- **useful because:** Today an offline Safari bridge turns an attempted task into a long failure, and the owner has no reliable distinction between 'not checked,' 'checked earlier,' and 'changed since last check.' This gives them a useful, honest answer immediately while preserving enough structured state to continue later without starting over.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model to normalize and summarize previously captured evidence; use realtime only for the owner's spoken question and a short freshness explanation. No model call is needed for the basic availability/staleness lookup.
- **latency:** Availability and freshness response under 1 second from relay/D1; resume automatically on the next verified Mac/browser heartbeat. Evidence capture runs asynchronously and must never block ordinary desktop use.
- **cost:** Low: mostly D1 metadata and compact encrypted evidence capsules; occasional background summarization, roughly cents or less per resumed task depending on captured page volume. Avoids repeated failed realtime turns.
- **security:** Never claim current truth from stale evidence. Every field needs source, capture time, expiry, and sensitivity labels; authenticated page contents remain encrypted and bound to the owner's device/session. The pendant should receive only the minimum summary, not private page text by default. Resumption of mutations must remain a separate explicit job step, with no automatic replay of irreversible actions.
- **missing:** A durable, typed evidence-capsule format shared by Mac and browser, including freshness/expiry and source bindings; A relay-side availability ledger consuming Safari-extension and Mac heartbeats; A resumable task state machine that records completed versus unverified steps and can re-plan after reconnect; Mac/browser hooks to emit compact read-only snapshots without scraping arbitrary UI; Pendant response/audio support for concise stale-state notices and reconnect notifications

### "“I need this ready by [time]; do the highest-value parts first across my Mac and logged-in browser, and give me a useful partial result if anything is blocked.”"
- **useful because:** Today a multi-surface task can spend its whole window waiting on one unavailable browser dependency, leaving the owner with nothing. Deadline-aware decomposition would let the pendant, relay, Mac, and browser work in parallel, prioritize the deliverable's critical path, and return a clearly labeled partial package rather than a binary success or failure.
- **path:** relay-realtime → faculty-judgement → mac-planner → browser-extension → mac-vision → pendant → unified
- **model tier:** Use a cheaper background model for decomposition, dependency ordering, and progress replanning; use realtime only to clarify an ambiguous deadline or report a concise checkpoint.
- **latency:** A plan and first executable work should begin within 2 seconds; progress checkpoints at meaningful milestones or when remaining slack drops below a threshold; final/partial receipt at the requested deadline.
- **cost:** Low-to-moderate background inference per task, dominated by one initial decomposition and occasional replans; desktop/browser execution and compact receipts dominate storage, not model cost.
- **security:** The planner must not infer permission to submit or send merely from a deadline. Separate read, draft, and mutation steps; disclose which sources were reached, which were unavailable, and what was not verified. Private browser content stays on the authenticated browser path.
- **missing:** A dependency-aware task graph with critical-path/slack tracking and partial-deliverable contracts; A shared progress event stream from Mac and browser to relay and pendant; A scheduler that can reserve Mac/browser work without starving owner-interactive use; A result schema for partial completion, blockers, freshness, and next-resumable step


## Changes it proposed to its own stack

### `integration` — Add a cross-node browser readiness preflight and recovery handshake before any browser job is dispatched. The relay should query extension presence/polling, tab/session affinity, URL privacy class, and relay public-browser budget; return a typed decision (run locally, run on relay, queue-until-Safari-online, or impossible) within ~1 second. For authenticated/private URLs, do not spend relay budget or wait through the current ~45-second timeout: persist the job as blocked_on_owner_device, notify the pendant and Mac with the exact recovery step (open Safari/enable bridge), and automatically resume when the extension heartbeat returns. For public URLs, route immediately to the relay backend when policy allows. Include the preflight decision and recovery timeline in the existing receipt.
- **owner gets:** A request will not silently burn nearly a minute and then fail because Safari is offline. Public work can still finish while the Mac sleeps, and private work tells the owner exactly what to fix and resumes without re-explaining the task.
- effort: Medium: shared readiness endpoint/heartbeat, URL privacy classification reuse, durable blocked state and wake-up subscription, plus pendant/Mac status notification.  ·  risk: A stale heartbeat could misroute a private page or wake a job unexpectedly. Use short leases, re-check immediately before navigation, never send owner-private URLs/content to relay, and keep blocked jobs cancellable.
- cost: Low API cost; avoids expensive failed browser turns and unnecessary relay browser-minute consumption. Small D1 state and heartbeat traffic.  ·  latency: Adds <1s preflight when healthy; removes the current ~45s failure path. Resume latency is approximately the next extension heartbeat.
- security: Improves privacy by making the private/public routing decision explicit before dispatch; authenticated content remains local-Safari only.
- depends on: browser extension heartbeat/status endpoint; durable browser job runner or equivalent blocked-job persistence; existing origin router and receipt schema

### `interaction` — Add a cross-node 'stop that' control for active Mac/browser jobs. The relay assigns each dispatched job a cancellation channel; the pendant's long press (or a spoken stop command) publishes a high-priority cancel, the Mac executor checks it between actions and aborts queued steps, and the browser bridge calls its tab-level abort. Receipts must distinguish completed, stopped, and unknown-in-flight effects, and the next spoken response should identify the last confirmed action.
- **owner gets:** When an automation starts doing the wrong thing, the owner can stop it from the pendant instead of finding the Mac, waiting for a timeout, or accepting that today's jobs are non-cancellable. This is an emergency brake, not an approval gate.
- effort: Medium: cancellation token/channel in relay and local job records, cooperative checks in Mac/browser executors, one-button gesture firmware mapping, and receipt/status propagation.  ·  risk: Cancellation can arrive during an irreversible OS or web operation, so it cannot promise rollback. Mark the action as unknown-in-flight, take a fresh state snapshot where possible, and never automatically retry a stopped mutation.
- cost: Negligible API cost; a small persistent job/cancellation record and one lightweight event stream.  ·  latency: Stop acknowledgement under 1 second when connected; action boundary may add up to the current action duration.
- security: A stop signal only reduces effects and should require the active job's unguessable token; do not expose job details over unauthenticated channels.
- depends on: durable job identity and status records; Mac executor cooperative cancellation hooks; browser bridge tab abort support; pendant gesture/event transport


## What it asked for

### `t13-ysut` (tool) — mac_readonly_inspect_impl
- why: The granted mac_readonly_inspect schema currently returns 'no implementation yet', so I cannot verify foreground app, running apps, or browser tabs before planning non-interfering actions. This is needed to make the proposed browser preflight and cooperative execution real rather than blind.

```json
{
  "operation": "running_apps | foreground_app | accessibility_enabled | ui_snapshot | browser_tabs | list_directory",
  "path": "string, required only for list_directory; approved absolute path",
  "limit": "integer 1..200",
  "max_elements": "integer 1..500"
}
```

## Its own summary

I found a concrete integration failure: GET /jobs contains two browser_navigate attempts that each waited about 45 seconds before failing because the browser extension was offline; both receipts are non-reversible failed steps and jobs report no cancellation. I proposed (1) a cross-node browser readiness preflight/recovery handshake that fast-fails, routes public work to relay, queues private work until Safari returns, and resumes automatically, and (2) a pendant/Mac/browser emergency stop channel for active jobs with honest stopped/unknown-in-flight receipts. I also alerted browser-extension about the repeated timeout defect.

**Biggest unknown:** The granted mac_readonly_inspect tool has no implementation, so I still cannot inspect foreground apps or live browser tabs to validate readiness and avoid interfering with the owner. I queued a request for its implementation. The preflight also still needs a real extension heartbeat/status signal and the executor cancellation hooks.

