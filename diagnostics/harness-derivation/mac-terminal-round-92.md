# Harness derivation — mac-terminal — round 92

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make my Mac ready for AI control, and tell me the one thing I need to fix."
- **useful because:** Today the agent can report that the local agent is up while silently being unable to operate the UI: Accessibility and Screen Recording are missing, computer-use is disabled, and the browser bridge is offline with seven queued commands. A single spoken readiness check would distinguish healthy shell control from unavailable GUI/browser control and guide the owner to the minimal fix instead of repeated failed attempts.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background/status model to correlate /ops/status, /browser/status, and recent /journal failures; reserve realtime only for the one-sentence spoken result. No vision model unless the owner explicitly asks for UI diagnosis.
- **latency:** Under 2 seconds for the status report; remediation guidance can continue asynchronously and post a receipt when permissions or the extension change.
- **cost:** Usually one cheap status call and one short realtime sentence; under roughly $0.01 per check excluding any optional vision. No browser page contents need leave the Mac.
- **security:** Do not read page content or secrets. Opening System Settings is safe, but granting Accessibility/Screen Recording remains an OS-level owner decision; the agent must never claim those grants happened until /ops/status verifies them. Do not auto-retry queued browser writes while the extension is offline; report and preserve them.
- **missing:** A readiness aggregator that turns /ops/status and /browser/status into explicit capabilities (shell/gui/screen/browser) with remediation steps; A verified remediation deep-link/open action for the relevant macOS Privacy & Security panes; A pendant/dashboard card showing the blocking prerequisite and last verification time

### "Restore my work exactly where I left off after my Mac or browser restarts."
- **useful because:** Today the hive can act on individual Mac jobs and browser tabs, but it cannot preserve and reconstruct the owner’s working state across a reboot or dropped session. The owner loses open research tabs, app focus, terminal directories, pending drafts, and the pendant’s unfinished task context. A cross-surface workspace checkpoint would make the system feel continuous rather than like several unrelated agents.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background model only to label and reconcile checkpoint items; use deterministic collectors for app/window metadata, browser session/tab metadata, job receipts, and relay task state. Use realtime only when the owner asks for a spoken restore summary.
- **latency:** Checkpoint capture under 3 seconds when requested or before a clean shutdown; restore should report progress within 2 seconds and finish asynchronously. The pendant should receive a concise completion/failure receipt.
- **cost:** Near-zero model cost for capture; typically under $0.02 for optional reconciliation of ambiguous windows or duplicate tabs. Metadata remains local except the minimum encrypted checkpoint needed by the relay.
- **security:** Never capture page contents, passwords, cookies, microphone data, or unsaved document text by default. Store only app identifiers, window titles where permitted, URLs/tab IDs, paths, cwd, focus, and job IDs; allow per-app exclusion and local encryption. Restoring a browser tab must reattach to the existing authenticated session rather than export credentials. Reopening an app is reversible, but reopening or submitting drafts must never send or mutate anything.
- **missing:** A versioned workspace-checkpoint schema spanning Mac windows, browser sessions/tabs, active jobs, and relay conversation/task state; Local collectors and restore adapters for app focus, terminal cwd, browser tab/session reattachment, and pending job continuation; Crash/shutdown detection with bounded checkpoint retention and encrypted local storage; Conflict handling when a tab, path, app, or job no longer exists, with a human-readable restore report


## Changes it proposed to its own stack

### `integration` — Create a single /readiness contract and dashboard/pendant renderer that fuses /ops/status, /browser/status, relay reachability, permission state, and the last 10 journal failures into four independent booleans: shell, app automation, screen/vision, and authenticated browser. Emit a stable blocker code (for example BROWSER_EXTENSION_OFFLINE, ACCESSIBILITY_MISSING, SCREEN_RECORDING_MISSING) with lastSeen, remediation URL/action, and affected queued job IDs. This is reporting only: it must never block FULL_CONTROL actions or silently retry them.
- **owner gets:** The owner hears one accurate answer—what the Mac can do right now and the single next fix—rather than seeing generic failures after 45-second browser timeouts. It also prevents an offline extension from being mistaken for a dead Mac or relay.
- effort: Small-to-medium: schema, reducer, tests against contradictory states (agent ready=false but requiredMissing empty), and dashboard/pendant presentation.  ·  risk: Stale health data could mislead; include timestamps, a short TTL, and an explicit unknown state. Do not expose URLs, tab titles, or command output in the spoken summary.
- cost: Negligible; all inputs are local status endpoints and existing receipts, reducing expensive planner retries.  ·  latency: Sub-100 ms local aggregation; can be polled or pushed on state transitions.
- security: Read-only metadata only. Permission remediation must open System Settings but never grant privileges automatically. Preserve unrestricted shell policy.
- depends on: GET /ops/status and /ops/snapshot; GET /browser/status; GET /journal and job receipts; Relay health payload; Dashboard and pendant status-event plumbing

### `memory` — Add an encrypted, versioned workspace-checkpoint store distinct from conversational memory. A checkpoint records only resumable handles and metadata: Mac app/window/focus identities, terminal cwd and project/branch, browser session/tab identifiers and URLs, active job IDs with receipt cursors, and the relay task/pipeline identifier. Capture atomically on explicit 'save my workspace', clean shutdown, and detected bridge loss; retain a small ring of checkpoints. Provide a deterministic restore planner that reopens/reattaches what still exists, marks conflicts instead of guessing, and emits a per-item restored/skipped/changed receipt.
- **owner gets:** After a restart or dropped connection, the owner can say 'continue where I left off' and recover their actual working context instead of manually hunting through apps, tabs, and unfinished jobs. This is continuity across the pendant, relay, Mac, and browser—not another single-surface action.
- effort: Medium-high: schema and encryption, Mac app/window and terminal collectors, browser reattachment, relay linkage, atomic checkpointing, restore conflict UI, and crash-recovery tests.  ·  risk: Window titles, paths, and URLs can be sensitive; encrypt locally, omit content and credentials, support exclusions, and expire old checkpoints. A vanished tab or changed file must be reported as a conflict, never silently substituted. Restore should only reopen or focus; it must not submit, send, delete, or overwrite.
- cost: Small local storage and negligible API cost; deterministic restore avoids repeated planner calls. Optional reconciliation can use a cheap model only when identifiers conflict.  ·  latency: Capture under 3 seconds; restore begins within 2 seconds and continues asynchronously.
- security: No cookies, passwords, page bodies, microphone data, or document contents leave the Mac. Relay receives only an encrypted checkpoint reference or explicitly permitted metadata.
- depends on: A durable encrypted local checkpoint store; Mac window/focus and terminal-state collector; Browser session/tab reattachment API with stable identifiers; Relay task/pipeline checkpoint linkage; Per-item restore receipts and dashboard/pendant status presentation


## What it asked for

_Nothing._
