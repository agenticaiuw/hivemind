# Harness derivation — mac-terminal — round 41

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep working on this across my Mac and logged-in browser, and tell me only when there is a real result, a decision I need to make, or something failed.”"
- **useful because:** This is more useful than a generic background job: a single goal can span a local shell build, authenticated Safari evidence, and public web research. The relay owns durable state while awake, Safari preserves private sessions, the Mac performs unrestricted local work, and the pendant delivers only meaningful transitions instead of progress spam.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use the cheaper background model for decomposition, polling, extraction, and failure classification; reserve realtime only for the owner's spoken interruption or decision. Use the planner model on the Mac for shell/UI execution and Browser Run only for public pages; route private pages to Safari.
- **latency:** Acknowledge on the pendant within 2 seconds, then work asynchronously. Emit only terminal, blocked, approval-needed, or materially changed states; batch routine progress into the dashboard. Resume after relay/Mac reconnect without replaying completed action IDs.
- **cost:** Low-to-moderate per task: background planning and extraction dominate; realtime cost is near zero unless the owner interrupts. Public Browser Run usage and retained artifacts are the main non-model costs.
- **security:** Private page content and shell output remain on the owning Mac by default; relay receives typed summaries and hashes, not raw secrets. Never silently submit/send browser transactions. Keep the owner's unrestricted FULL_CONTROL policy, but label irreversible steps and preserve receipts/undo evidence. Expire artifacts and allow deletion.
- **missing:** durable cross-surface state machine with task/step IDs and lease heartbeats; Mac execution telemetry and crash-safe resume journal (the change proposed this round); browser job runner persistence/retry/result stream; current backend router is not yet a durable runner; relay-to-Mac authenticated event stream and a single pendant notification policy; implementation of the newly granted typed diagnostic/action interfaces, or an explicit fallback to existing mac_run_actions

### "“When something went wrong, show me one trustworthy timeline of what I said, what each part of the system observed and decided, what the Mac and browser actually changed, and the exact point where it diverged—then give me a safe way to continue from there.”"
- **useful because:** Today the owner can receive separate job receipts, browser state, relay events, and Mac results, but cannot reconstruct one causally ordered incident across the pendant, relay, Mac, and authenticated browser. A cross-surface forensic replay would turn mysterious partial completion into an understandable, recoverable outcome without requiring the owner to inspect logs or repeat actions.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use a cheap background model to normalize and correlate already-recorded events; use the expensive planner only to explain contradictions or generate a continuation plan. Realtime is needed only when the owner asks verbally for the explanation.
- **latency:** Create a compact incident record as events arrive with no user-visible delay. On request, show the first timeline within 3 seconds and stream deeper evidence afterward. Continuation should begin only from a verified last-completed step, never from the model's guess.
- **cost:** Low: correlation is mostly deterministic and local; a short explanation may use one background-model call. Storage and retention of event metadata dominate rather than inference.
- **security:** Private URLs, shell commands, page text, and audio identifiers are sensitive. Keep raw evidence on the Mac where possible, send the relay only redacted summaries and hashes, encrypt incident records, apply short retention, and provide owner deletion. Never replay a mutation merely to reproduce it; use receipts, snapshots, browser evidence, and dry-run inspection.
- **missing:** A shared immutable event schema spanning pendant utterance IDs, relay decisions, Mac action receipts, shell processes, browser command IDs, and delivered notifications; Clock-skew correction and causal parent IDs so events can be ordered across disconnected devices; A signed evidence bundle or hash chain proving that the displayed timeline was not silently rewritten; A dashboard incident view with divergence markers, raw-evidence disclosure controls, and a continuation-from-step operation; A planner contract that distinguishes observed facts, inferred causes, and proposed next actions


## Changes it proposed to its own stack

### `mac-harness` — Add a non-blocking execution telemetry and recovery journal around every FULL_CONTROL shell/action dispatch. Record start/heartbeat/finish, argv or shell text hash plus redacted command label, cwd, exit code, signal, timeout, stdout/stderr byte counts and tail, CPU/memory/disk pressure, and whether the process is still alive. Persist large output as a content-addressed local artifact and expose a compact live event stream plus a resume recipe to the relay. On timeout or Mac disconnect, classify the failure (transient transport, process timeout, missing permission, missing binary, nonzero exit), retain the exact receipt, and let the planner retry only when its recipe says that retry is safe; never gate execution.
- **owner gets:** When a long task fails or the laptop sleeps, the owner gets an honest answer—what ran, how far it got, and whether it can continue—instead of a generic failure or duplicated side effects. The pendant can announce a one-line status while the dashboard opens the full output and undo evidence.
- effort: Medium: local-agent journal/artifact store and SSE or polling endpoint, relay ingestion and planner retry schema, dashboard status view, and tests for crash/reconnect/timeout. Reuse existing action receipts and jobs rather than adding approval logic.  ·  risk: Command output may contain secrets; redact known tokens and restrict relay upload to requested artifacts, with local-only default. A bad retry classification could duplicate an irreversible shell command, so retry is advisory and only for explicitly idempotent recipes; recovery is manual otherwise. If journaling fails, execution still proceeds and the receipt marks telemetry incomplete.
- cost: Low API cost; mostly local disk and a small D1 event record per action. Large stdout stays on the Mac unless explicitly requested.  ·  latency: Negligible dispatch overhead for metadata; live updates add no model call. Failure diagnosis may save repeated planner turns.
- security: Improves auditability without reducing the owner's deliberate unrestricted access. Requires careful redaction, artifact TTL, and authenticated relay-to-Mac event transport.
- depends on: existing actionReceipts.js and /jobs receipts; authenticated Mac-agent observability transport; a durable relay job/result stream

### `integration` — Make the granted Mac diagnostic/action interfaces real adapters instead of schema-only tools. Implement mac_read_diagnostics as a fixed-query adapter backed by the local agent's authenticated status routes, mac_readonly_diagnostics_impl as an exact-command compatibility adapter for the already-proven read-only commands, and mac_execute_typed_actions as a typed-to-existing-action translator that preserves FULL_CONTROL_MODE and emits the same action receipts. Return an explicit capability-unavailable error only when the local agent is offline; do not pretend a tool ran.
- **owner gets:** The hive can currently be granted a tool that always returns 'no implementation yet', so the pendant and relay cannot reliably inspect battery/network/agent health or perform simple Mac controls. Real adapters make routing truthful and let the system choose a fast status path instead of spending a planner turn on a shell command.
- effort: Small to medium: wire schemas to existing local-agent routes, map typed actions to mac_run_actions, add contract tests and a capability-health field. Keep arbitrary shell available as the owner requires.  ·  risk: A bad adapter mapping could report stale status or mislabel an action. Include source timestamp, route, and raw error class; fall back visibly to the existing action path rather than silently dropping work.
- cost: Negligible API cost; fewer planner/model turns for routine checks. Small local implementation and test cost.  ·  latency: Faster routine checks (one typed call rather than planning a shell command); no impact on unrestricted shell execution.
- security: No new privilege beyond the existing Mac agent token and FULL_CONTROL policy. Typed calls should inherit the same authenticated transport and receipt/audit trail.
- depends on: local-agent authenticated route contract; existing get_mac_status and mac_run_actions tool implementations; action receipt wrapper


## What it asked for

_Nothing._
## Its own summary

Recorded a new cross-surface forensic replay capability: the owner can ask why a task went wrong and receive a causally ordered, evidence-backed timeline across pendant, relay, Mac, and authenticated browser, plus a safe continuation point. It requires a shared event schema, causal IDs, clock correction, integrity-protected evidence bundles, and a dashboard incident view.

**Biggest unknown:** Whether current Mac, relay, pendant, and browser event records retain enough stable IDs and timestamps to build the causal chain without firmware and schema changes.

