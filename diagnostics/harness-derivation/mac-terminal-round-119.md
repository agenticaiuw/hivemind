# Harness derivation — mac-terminal — round 119

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac executor contract drift and retry waste** — At 2026-08-07T14:47Z, /ops/status reports fullControlMode=true, browser online=false with 11 pending commands, accessibility and screen recording ungranted. /journal reports 120 retained jobs, 143 actions, 24 failures, and repeated malformed run_shell/run_applescript/open_app jobs; browser_navigate signature act_36a2da2b0b8c ran 10 times and failed all 10.
  - evidence: GET /ops/status, GET /journal, and GET /jobs live responses in Round 119

## Capabilities it proposed

### "“Take care of this whole task, even if I walk away or the browser/Mac connection drops. Resume where you left off, and when you’re done tell me exactly what changed, what could not be completed, and show me the evidence.”"
- **useful because:** Today the owner can hand work to separate Mac and browser surfaces, but cannot treat them as one recoverable mission. A dropped bridge, stale tab, or failed Mac action can leave partial work and force the owner to reconstruct state manually. This gives the pendant a dependable, cross-device notion of one task with resumable progress and a truthful final account.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use deterministic state transitions and receipt matching for checkpoints, background model for summarizing completed/failed work, and realtime only for the owner's live conversational updates. Escalate to the planner only when recovery requires interpreting changed page or desktop state.
- **latency:** Immediate acknowledgement from the relay (<1 second); checkpoint updates within 2–5 seconds after each action; recovery may run in the background. Final spoken summary should be available as soon as the mission reaches a terminal state.
- **cost:** Low incremental API cost: most transitions, deduplication, and recovery decisions are deterministic; occasional background summaries dominate model usage. Storage is the main cost, retaining compact checkpoints and receipts rather than repeated screenshots or full prompts.
- **security:** Authenticated browser contents, typed text, and Mac files may cross the relay unless explicitly kept local. Encrypt mission state, minimize captured page/screen data, redact secrets from summaries, bind every action to a device/session lease, and require explicit confirmation only for genuinely irreversible external effects if owner policy later chooses that—not for routine reversible work.
- **missing:** A durable cross-surface mission object with ordered semantic checkpoints, dependencies, and terminal states; A lease protocol allowing relay, Mac, and browser to claim/release one checkpoint without duplicate execution; Checkpoint snapshots that combine browser session identity, Mac job/receipt IDs, and relevant evidence capsules; Recovery policies that distinguish retryable transport loss, stale authenticated state, schema errors, and completed-but-unacknowledged actions; A dashboard and pendant summary that render one mission timeline rather than separate job, browser, and audio histories


## Changes it proposed to its own stack

### `integration` — Add a canonical action-contract adapter at the Mac executor boundary. Normalize planner aliases into the executor schema (e.g. run_shell.command, run_applescript.script, open_app.appName) before dispatch, validate required fields and types, and emit a deterministic contract_error receipt naming the missing field and accepted shape when normalization cannot repair it. Generate planner/tool schemas from the same action registry so aliases cannot drift. Record requested shape, normalized shape, and adapter version in each job receipt; do not block valid arbitrary shell capability or add approval gates.
- **owner gets:** Requests like “open the browser bridge” will actually run instead of silently producing repeated zero-effect failures, and when something genuinely malformed occurs the pendant can explain exactly what needs fixing. The owner also gets reliable evidence about what command was attempted and what the Mac executed.
- effort: Medium: shared action registry, adapter and tests across planner, /execute, receipts, and mac_run_actions; migrate existing action fixtures and add compatibility aliases.  ·  risk: An incorrect alias could dispatch the wrong action or mask a planner bug. Mitigate with explicit per-action allowlisted aliases, normalized-shape receipts, and contract tests; unknown or ambiguous shapes should fail clearly without executing.
- cost: Negligible API cost; saves model retries and wasted planner calls. Small local CPU/storage overhead for validation and receipt metadata.  ·  latency: Adds sub-millisecond local validation; materially lowers end-to-end latency by preventing retries and failed job loops.
- security: No reduction in owner's deliberate FULL_CONTROL_MODE or network reach. Better auditability through requested/normalized payloads; avoid logging secret field values, only names and hashes.
- depends on: A single versioned action registry shared by mac-planner, mac_run_actions, /execute, and receipt serialization; A migration test corpus covering current malformed payloads and valid run_shell/run_applescript/open_app actions

### `model-routing` — Introduce a failure-loop circuit breaker shared by planner and Mac/browser executors. When the same idempotency key/action signature fails repeatedly (for example browser_navigate 10/10 failures or a malformed run_shell payload), stop issuing identical retries, attach the latest receipt and failure class to the next response, and route the recovery decision to a cheap deterministic/background path. Reset only after a changed device heartbeat, changed payload, or explicit owner retry. Preserve FULL_CONTROL_MODE; this is retry control, not an approval gate.
- **owner gets:** The pendant will stop wasting time repeating an action that cannot succeed while the browser is offline or the payload is malformed. It can say “the bridge is offline; I have not kept retrying” and resume automatically when the device comes back.
- effort: Medium: stable action signatures, per-device failure counters with TTL, planner feedback, and heartbeat-triggered reset across local agent and relay.  ·  risk: A transient failure could be mistaken for a persistent one and delay recovery. Use short exponential TTLs, classify transport/device/schema failures separately, and allow an explicit retry phrase or changed arguments to bypass.
- cost: Reduces planner and relay calls during outages; tiny local state overhead. No new paid API dependency.  ·  latency: Faster failure responses; recovery latency unchanged or improved because retries resume on heartbeat instead of blind polling.
- security: Receipts must hash or redact arguments that can contain authenticated URLs, tokens, or typed text. No new authority is introduced.
- depends on: Canonical action-contract adapter and failure classification; Browser heartbeat/device TTL state shared with pending-command queue; Stable idempotency/action signature persisted in job receipts


## What it asked for

_Nothing._
