# Harness derivation — mac-planner — round 25

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac_readonly_inspect availability** — The granted mac_readonly_inspect tool currently returns 'This tool was granted a schema but has no implementation yet' for foreground_app, running_apps, browser_tabs, and accessibility_enabled. It cannot currently report real Mac state.
  - evidence: Four parallel calls to mac_readonly_inspect in Round 25 returned the same implementation error.
- **Mac/browser operational state** — Mac local agent is ready with Accessibility and Screen Recording granted, but computer-use loop is disabled and vision upload consent is false. Browser extension is offline with one pending command; relay is reachable and mac bridge online.
  - evidence: GET /ops/snapshot returned version 0.5.0, ready:true, computerUse.loopEnabled:false, visionUploadConsented:false, browserExtension.online:false, pendingCommands:1, relay.macBridgeOnline:true.

## Capabilities it proposed

### "“The last automation may have been interrupted—inspect what it actually finished, safely continue the rest, and tell me exactly what remains.”"
- **useful because:** This turns crashes, sleep, and lost browser links into recoverable work rather than duplicate actions or silent partial completion. It is narrower and more dependable than asking the agent to blindly rerun a prior goal.
- **path:** Mac local agent ledger and filesystem/app inspection → Browser bridge for tab/session reconciliation when a browser step was involved → Relay for the completion summary and unresolved-item alert → Pendant for a concise spoken status; Mac workbench for evidence and repair details
- **model tier:** Background/cheap deterministic reconciliation first; use a slower reasoning model only for ambiguous evidence or explaining conflicts. Realtime is unnecessary except for the owner's follow-up conversation.
- **latency:** Initial status in under 5 seconds; deterministic continuation within the normal task duration; ask the owner only when state cannot be distinguished safely.
- **cost:** Usually near-zero model cost because hashes, receipts, and preconditions resolve most steps locally. A few cents at most for an ambiguous multi-step repair summary; storage/network overhead is dominant only for screenshots or browser evidence.
- **security:** Task manifests can expose private paths, URLs, and snippets. Keep raw evidence on the Mac, redact spoken summaries, expire manifests, and require explicit confirmation only if a repair would cross an irreversible boundary; do not silently submit or send.
- **missing:** Crash-recoverable action ledger with stable step IDs and precondition fingerprints; Reconciliation endpoint that can inspect unfinished jobs and produce a repair plan; Browser bridge support for reattaching the original tab/session and returning evidence; A Mac workbench view showing completed, skipped, unresolved, and proposed steps


## Changes it proposed to its own stack

### `integration` — Add a durable, crash-recoverable action ledger for every multi-step Mac/browser plan. Before execution, persist a plan manifest with stable action IDs, target fingerprints (path/app/tab), and intended outputs. After each step, write an observed receipt (including hashes or UI evidence) and a commit marker. On restart or reconnect, reconcile unfinished plans against current state: mark already-completed steps as done, safely replay only steps whose preconditions still hold, and surface a compact repair plan for ambiguous steps. Keep this observational and compatible with FULL_CONTROL_MODE—no new approval gate—while preserving the existing result receipts and undo endpoints.
- **owner gets:** If the Mac sleeps, the agent crashes, or the browser bridge disconnects halfway through a filing, cleanup, or organization task, the owner gets continuation instead of duplicate files, duplicate submissions, or having to remember what happened. They can say “continue” and receive an exact list of completed, skipped, and unresolved steps.
- effort: Medium-high: durable schema and migration, precondition/fingerprint adapters for files/apps/tabs, startup reconciliation, and integration tests for sleep/reconnect/crash at every step.  ·  risk: A stale fingerprint could falsely classify a step as complete or replay a mutation. Recover by treating ambiguous matches as unresolved, preserving the manifest and evidence, and never inferring completion from a missing error alone. Existing FULL_CONTROL policy remains unchanged.
- cost: Small local storage and hashing overhead; background reconciliation uses a cheap model or deterministic code, with no realtime-model call unless the repair explanation is ambiguous.  ·  latency: A few milliseconds of local ledger I/O per action; resume adds a short reconciliation pass before execution.
- security: Manifests may contain paths, URLs, and snippets; encrypt or redact sensitive values at rest and apply existing retention. No data needs to leave the Mac for deterministic reconciliation.
- depends on: Existing action receipts and durable job store; Typed result metadata for browser tabs and file operations; A startup/reconnect hook in the Mac agent

### `mac-harness` — Finish the implementation behind the granted mac_readonly_inspect interface for running apps, foreground app, accessibility state, UI snapshots, browser tabs, and approved directory listings. Route it through bounded native APIs/Accessibility and the existing Safari/Chrome bridge, returning typed timestamps and explicit unavailable reasons rather than an implementation error. Add a heartbeat and stale-data marker so planners know whether a snapshot is current.
- **owner gets:** The agent can then see what is actually on the Mac before acting, avoid stealing attention from the foreground app, recover interrupted work, and answer “what’s open?” or “which tab is this?” without opening a microphone or using mutation-capable automation.
- effort: Medium: implement six read-only adapters, normalize their result schema, add tests and a small health check; browser-tab inspection depends on the extension reconnect path.  ·  risk: UI snapshots and tab titles can contain sensitive content, and stale state can mislead planning. Default to metadata/redaction, include capture time and source, keep raw screenshots local, and return unavailable rather than guessing.
- cost: Negligible local CPU/storage; screenshots may add transient memory but no model/API cost unless a caller explicitly asks for visual interpretation.  ·  latency: Metadata reads under 200 ms; UI snapshot/browser extraction likely 0.5–2 s depending on app and bridge.
- security: Read-only access still exposes private screen/tab data. Enforce approved-app/path scope, redact by default, and avoid sending raw snapshots to the relay unless explicitly requested.
- depends on: Native implementation for the already-granted mac_readonly_inspect schema; Browser extension heartbeat/reconnect to clear the current offline/pending-command state


## What it asked for

_Nothing._
## Its own summary

Round 25 produced a new crash-recovery capability and integration design: durable step manifests, precondition fingerprints, observed receipts, commit markers, and reconciliation so interrupted Mac/browser work can safely continue without duplication. I also verified the live Mac state: the agent is ready with Accessibility/Screen Recording and broad automation grants, but computer-use is disabled, vision upload consent is false, and the browser extension is offline with one pending command while the relay remains reachable. The granted mac_readonly_inspect tool is not implemented at all, so I recorded and proposed finishing that bounded read-only inspection surface. I still need the inspection adapters implemented and the browser bridge heartbeat/reconnect path to clear stale pending commands; I do not need another permission request for the existing maximum-control policy.

**Biggest unknown:** Whether the browser extension's pending command is recoverable or stale, and which browser/session it belongs to; the browser peer has been asked for its view and has not replied yet.

