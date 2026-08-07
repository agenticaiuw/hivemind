# Harness derivation — mac-terminal — round 46

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Why didn’t that happen?”"
- **useful because:** After an unattended task, the owner should get an evidence-backed explanation across the Mac, browser, pendant, and relay: what was attempted, where it stopped, what actually changed, and the safest available recovery. Today each surface can report its own job, but no single answer reconciles a Mac timeout, an offline browser tab, a dropped pendant link, and a stale relay job.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the cheaper background model to correlate receipts and health events; reserve realtime only for the owner's spoken follow-up. Use deterministic typed reconciliation before any model summary.
- **latency:** Return a first status in under 2 seconds from indexed receipts; deeper artifact inspection can continue in the background and update the dashboard/pendant queue within 30 seconds.
- **cost:** Roughly $0.01–$0.05 per incident depending on artifact volume; most cost is context summarization, not device work. Deterministic correlation should avoid a model call for simple failures.
- **security:** Private shell output, authenticated URLs, and browser snippets must stay in the owner's local/authenticated boundary; relay receives only the minimum redacted evidence needed for speech. Recovery actions that replay commands or submit browser forms must be explicitly labeled and remain separate from diagnosis.
- **missing:** A cross-surface incident ID propagated through relay, Mac jobs, browser commands, and pendant sessions; A shared typed event schema for attempted/completed/failed/partially-applied actions and heartbeat loss; Shell execution bundles with bounded artifacts and file/git manifests; Browser job receipts that expose the same correlation and failure taxonomy; A reconciliation service that can distinguish stale/offline state from actual task failure

### "“Did that actually take effect?”"
- **useful because:** The owner needs a trustworthy postcondition check, not merely a report that a click or shell command returned successfully. The hive should verify the requested outcome in the real source of truth—for example, the Mac file and git state, the authenticated browser page after refresh, or a relay-delivered pendant notification—and clearly distinguish completed, partially applied, reverted, and unverifiable.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use deterministic typed postcondition checks first; use the cheaper background model to choose checks from the goal and reconcile conflicting evidence. Realtime is only for a concise spoken result.
- **latency:** Give a preliminary answer within 3 seconds for local checks; allow up to 60 seconds for browser refresh/reload and cross-surface confirmation, with an explicit pending state rather than guessing.
- **cost:** About $0.005–$0.03 per verification, mostly browser reloads and artifact retrieval; simple local checks should require no model call.
- **security:** Verification may read private files and authenticated pages. Keep raw evidence on the Mac/browser boundary, send the relay only redacted claims and source references, and never perform a new external mutation while verifying. A failed check must be reported as unknown, not success.
- **missing:** A goal-to-postcondition schema with typed predicates (file hash, git status, UI value, page field, notification delivery); A cross-surface verifier that can re-read authoritative state after an action and correlate it to the action receipt; Browser support for authenticated refresh/readback with tab/session affinity; Mac support for bounded file/git/UI readback and evidence snapshots; Dashboard and pendant language for completed vs partially-applied vs unverifiable outcomes


## Changes it proposed to its own stack

### `mac-harness` — Add a shell execution bundle and replay/failure-recovery layer without changing FULL_CONTROL_MODE or adding gates. For every run_shell action, persist a redacted command record plus cwd, timeout, host identity, start/end, exit code/signal, stdout/stderr artifact references, and a before/after manifest of touched files and git worktree state. Classify failures (not-found, permission, timeout, nonzero, transport) and expose `rerun`, `retry-with-diagnosis`, and `revert-if-supported` operations keyed by the existing job/action IDs. Secret-looking env values and tokens are hashed/redacted, while the original command remains available locally for trusted replay.
- **owner gets:** When a Mac task fails or changes the wrong project, the owner can see exactly what ran, where, and what it changed, then recover or rerun it instead of asking the agent to guess. Repeated diagnostics become reproducible, and the agent can automatically explain a timeout or missing-directory failure.
- effort: Medium: shell wrapper and artifact store, git/file manifest collection, failure classifier, replay endpoints, dashboard/relay receipt fields, and tests for timeout plus partial-write recovery.  ·  risk: Capturing manifests can add latency and may miss changes outside observed roots; redaction can hide useful values; replaying a command can repeat irreversible effects. Preserve the current no-gate policy, mark replay as potentially irreversible, cap artifact sizes, and never claim a revert unless verification succeeds.
- cost: Small storage and CPU cost per shell job; no model/API cost. Dominant cost is stdout/stderr and manifest retention, bounded with size caps and retention cleanup.  ·  latency: Approximately 50–300 ms for metadata and git/file manifests on normal projects; no extra model round trip. Large trees should use declared/learned roots and sampling.
- security: Improves auditability while retaining unrestricted execution. Redaction and local-only raw command storage reduce accidental secret propagation to relay/dashboard; network access remains unrestricted by owner policy.
- depends on: implemented action receipts (chg-5fc73ce3); durable job IDs and GET /jobs/:jobId/receipts; a bounded local artifact/retention store

### `integration` — Introduce a cross-surface outcome ledger with immutable intent IDs and typed postconditions. The planner records the requested goal and expected predicates before dispatch; Mac, browser, relay, and pendant append signed observations tied to that ID. A verifier re-reads authoritative state after each mutation, evaluates predicates, and emits completed, partially_applied, reverted, or unverifiable with evidence pointers. This is an outcome ledger, not another action log: a successful process exit or click is insufficient evidence.
- **owner gets:** The owner can trust “done” only when the real result is visible, and gets an honest explanation when the system cannot prove it. It prevents silent half-completion across a sleeping Mac, stale browser tab, dropped relay link, or interrupted voice session.
- effort: High: shared event schema and ID propagation, local signed append-only storage, browser readback, Mac predicate evaluators, relay reconciliation, and dashboard/pendant rendering.  ·  risk: External systems can change between checks, some outcomes are inherently unverifiable, and extra reads can expose sensitive data. Use freshness windows, source provenance, redacted evidence, and never collapse unknown into success.
- cost: Low storage and deterministic compute; occasional browser reloads and one cheap summarization call for ambiguous evidence. No recurring realtime-model cost.  ·  latency: Adds a readback phase, typically milliseconds locally and seconds for authenticated browser verification; expose pending state immediately.
- security: Improves integrity through signed, provenance-linked observations, but creates a sensitive cross-device event trail. Encrypt local records, minimize relay projection, and apply retention by sensitivity.
- depends on: A typed goal-to-postcondition schema; Cross-surface correlation IDs in Mac and browser jobs; Authenticated browser readback and Mac predicate evaluators; Relay/pendant support for outcome states


## What it asked for

_Nothing._
## Its own summary

Discovered the newly granted Mac diagnostic schemas, but all three diagnostic implementations return “no implementation yet,” so I could not verify live host state this round. I sent faculty-action the typed readiness/reconciliation contract. I proposed a new shell execution-bundle/replay layer (keeping unrestricted FULL_CONTROL_MODE and adding no gates) and a cross-surface “Why didn’t that happen?” incident capability that reconciles Mac/browser/relay/pendant evidence.

**Biggest unknown:** I still need a functioning read-only Mac diagnostics implementation and authenticated observability access to validate the live executor, job receipts, logs, and readiness state. Specifically: implement mac_read_diagnostics (or mac_readonly_diagnostics_impl), and expose the existing /jobs, /logs, /journal, /routing, and /ops endpoints through the granted auth context. I do not need broader shell permissions or approval gates.

