# Harness derivation — mac-terminal — round 45

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent readiness** — Live /ops/status reports fullControlMode and relay reachable, but agent ready=false while requiredMissing=[]; Accessibility trusted=false and Screen Recording granted=false. Browser offline with 3 pending commands. This is an ambiguous readiness state that can cause silent GUI job failures.
  - evidence: GET /ops/status returned HTTP 200 with agent.ready=false, permissions.accessibility.trusted=false, permissions.screenRecording.granted=false, browser.online=false, pendingCommands=3.

## Capabilities it proposed

### "“Is my Mac ready to do that, and if not, fix whatever is stopping it?”"
- **useful because:** Today the system can report a confusing ready=false with no requiredMissing items, while Accessibility and Screen Recording are visibly unavailable and the browser has stranded commands. A spoken readiness check would prevent the owner from asking for a GUI/browser task that cannot complete, and could repair safe prerequisites or explain exactly what the owner must approve.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** deterministic health aggregation first; background gpt-4.1-mini only to turn blockers into a concise spoken explanation; realtime only for the follow-up conversation
- **latency:** Under 500 ms for local /ops/status plus browser heartbeat; under 2 seconds if a remediation plan is generated. No model call when status is unambiguous.
- **cost:** Near-zero for deterministic checks; roughly 2k prompt tokens only when explanation/remediation is needed, dominated by the background model call.
- **security:** The relay should receive statuses and capability names, not paths, tokens, or page contents. Opening System Settings is reversible, but changing permissions remains OS-controlled and must be explicitly described; never claim a permission was fixed unless the next health poll verifies it.
- **missing:** A typed readiness schema distinguishing blockers, degraded capabilities, stale browser commands, and owner-action-required permissions; A safe remediation planner that can open the relevant System Settings pane and then re-poll /ops/status; Browser queue reconciliation: inspect, retry, or expire the 3 pending commands by request ID; A pendant/relay intent such as readiness_check and a dashboard remediation view

### "“I started this with the pendant—finish it on my Mac exactly where we left off, and if the browser or Mac drops out, resume safely when it returns.”"
- **useful because:** Today a conversation, a browser tab, and a Mac job are separate surfaces. Losing connectivity or switching from voice to desktop can force the owner to repeat the goal, lose intermediate evidence, or accidentally perform a step twice. This would provide a single resumable work item spanning the pendant, relay, authenticated browser, and Mac, with a verified handoff rather than a fresh interpretation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use deterministic state-machine and idempotency handling for checkpoints, leases, reconnects, and duplicate prevention. Use background gpt-4.1-mini only to summarize the checkpoint when the owner asks what remains; use realtime only for the live handoff conversation.
- **latency:** Voice acknowledgment under 1 second. Reconnect reconciliation under 3 seconds after a surface heartbeat. No model call for checkpointing or retries.
- **cost:** Usually negligible: local/relay state transitions and receipts dominate, with no LLM call. A checkpoint explanation costs roughly 1–3k background prompt tokens when requested.
- **security:** Persist only task state, action IDs, redacted evidence references, and capability scopes in the relay; keep authenticated page contents and secrets on the Mac/browser. Every side-effecting step needs an idempotency key and a lease owner. On uncertain completion, pause and show the last verified before/after state instead of retrying blindly.
- **missing:** A cross-surface task envelope with immutable goal, step graph, checkpoint IDs, capability scope, and evidence references; Distributed leases and idempotency keys shared by relay, Mac executor, and browser bridge; Reconnect protocol that distinguishes queued, running, completed, failed, and outcome-unknown steps; A dashboard/pendant resume control and concise checkpoint receipt format; Crash-consistent local persistence for the active envelope and a reconciliation test suite for duplicate or partial actions


## Changes it proposed to its own stack

### `integration` — Add a machine-readable Mac capability health contract and reconciliation loop. /ops/status should emit per-capability states (available, degraded, blocked, stale), blocker codes, observedAt, remediation kind, and a monotonic health revision. The relay/mac-planner should heartbeat browser state, reconcile pending command IDs, and only then derive an overall readiness summary; dashboard and pendant consume the same typed result.
- **owner gets:** The owner gets an honest answer about what the Mac can do right now instead of a generic failure after a long task. Stale browser work is surfaced and recoverable, while missing Accessibility or Screen Recording is explained before GUI automation begins.
- effort: Medium: route/schema changes, browser queue reconciliation, one shared reducer, dashboard card, and pendant intent wiring; likely 2–4 engineering days plus failure-mode tests.  ·  risk: A bad reducer could report the Mac ready when it is not, or repeatedly retry stale browser commands. Recover with revisioned snapshots, bounded retries, expiry, and preserving raw status receipts for diagnosis. No action should be silently discarded.
- cost: Negligible API cost; fewer failed planner calls and retries should reduce spend. Small local JSON/D1 storage for health snapshots and command reconciliation.  ·  latency: Adds one local status aggregation and usually one browser heartbeat; target under 500 ms and no LLM call on the happy path.
- security: Expose only capability state, blocker codes, and timestamps to relay/dashboard; keep filesystem paths, browser URLs, and auth details local. Health receipts should be redacted and access-controlled.
- depends on: mac-agent /ops/status remains available; browser command queue exposes request IDs and expiry/ack state; shared typed context projection so readiness facts are not copied into per-surface prompts

### `integration` — Add a cross-surface outcome-verification stage after execution. For eligible tasks, the Mac executor and browser bridge each publish independent typed observations tied to the same action ID; a deterministic verifier compares the expected postcondition against both observations (for example, browser confirmation plus local notification/history). If observations disagree or one surface is unavailable, mark outcome-unknown and present the evidence instead of reporting success. Store compact hashes and source locators, not duplicated page contents.
- **owner gets:** The owner gets a trustworthy answer that something actually happened, rather than a confident report that a click or command was sent. This is especially valuable when a browser submission, Mac automation, or network timeout leaves the real-world outcome uncertain.
- effort: Medium to high: define postcondition contracts for common actions, add observation adapters to Mac and browser surfaces, implement a deterministic verifier, and expose disagreement receipts in the dashboard and pendant.  ·  risk: Some legitimate actions have no observable confirmation or produce delayed state, causing false 'unknown' results. Recover with action-specific verification windows, explicit eventual-state polling, and a manual 'check again' path; never convert uncertainty into success.
- cost: Small storage and polling cost; deterministic verification avoids extra model calls. Optional background summarization is inexpensive and only used for complex evidence.  ·  latency: Adds roughly 0.5–5 seconds depending on confirmation polling; immediate voice acknowledgment can say 'sent, verifying' while the background verifier runs.
- security: Keep authenticated evidence local where possible; send only typed outcomes, redacted snippets, hashes, and source metadata to the relay. Do not expose private page content merely to achieve a second opinion.
- depends on: Cross-surface task envelope with shared action IDs and checkpoints; Typed observation adapters for Mac and browser; Action-specific postcondition definitions; Durable receipts and dashboard presentation for outcome-unknown states


## What it asked for

_Nothing._
