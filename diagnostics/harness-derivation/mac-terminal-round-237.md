# Harness derivation — mac-terminal — round 237

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “finish this when my Mac is available,” carry the current browser or desktop task through sleep, network loss, and reconnect, then tell me on the pendant exactly what completed and what still needs me."
- **useful because:** Today a long task dies or becomes an ambiguous job when the Mac sleeps or the browser disappears. This would make the hive dependable: the relay holds the intent, the Mac resumes only the unfinished step, the browser preserves its authenticated session, and the pendant reports truthful completion without requiring the owner to remember to check.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background planner for checkpoint classification and resume selection; reserve realtime only for the owner's spoken request and the final concise status.
- **latency:** Acknowledge the request in under 1 second; resume within 10 seconds of the Mac/browser heartbeat returning; status delivery within 2 seconds of each step settling.
- **cost:** Low: one short planning call at handoff and one call only if recovery is ambiguous; heartbeats and step receipts are local/relay metadata, not model tokens.
- **security:** The relay must persist only an opaque job/checkpoint ID, not browser secrets or page contents. Resume must require the same browser session and project context, reject stale step IDs, and never claim success without a Mac receipt. An authenticated browser mutation still follows the owner's existing maximum-access policy; the pendant should say 'waiting for you' for a missing login or destructive ambiguity.
- **missing:** A durable cross-surface checkpoint schema containing job ID, step ID, browser session ID, project, replay safety, and last receipt; Mac boot/heartbeat reconciliation that marks interrupted jobs and resumes idempotently instead of leaving processing forever; A relay scheduler that retries only unfinished safe steps and pushes state to the pendant; Browser-session liveness and a typed 'resume from this command/step' operation

### "Run a wearable bench check: verify the pendant button, USB link, ESP32 audio bridge, and relay audio pipeline together, then tell me whether a spoken turn would be heard end-to-end and point to the failing chip if not."
- **useful because:** The chips are physically connected now but not LTE-registered, so this is the one honest way to validate the assembled wearable before trusting it away from the desk. It replaces separate UART guesswork with a deterministic pass/fail report tied to button edges, framed audio counters, acknowledgements, and relay pipeline state.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Use deterministic local scripts and parsers for serial framing, counters, and timing; use a cheap background model only to summarize failures. No realtime model or open microphone is needed.
- **latency:** Start in under 2 seconds and finish the normal health run in 15 seconds; fail a stalled UART or pipeline leg within 2 seconds rather than waiting for a global timeout.
- **cost:** Near-zero API cost; local serial reads and a few authenticated health/pipeline requests dominate. The test can use generated tone/loopback frames and must not record the owner's microphone.
- **security:** Read-only diagnostics only: no firmware flashing, no arbitrary serial writes, no microphone capture, and no upload of raw audio. Logs should retain counters, timestamps, port identity, and hashes, not PCM. Require an explicit separate command for any firmware update.
- **missing:** A bounded host-side serial reader/parser for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A deterministic pendant test mode that emits a signed button-edge and audio-loopback test frame without starting the microphone; An ESP32 bridge loopback/health frame with sequence, CRC, underrun, and acknowledgement counters; A relay endpoint that correlates the two chip streams with POST /pipeline/events and returns a single end-to-end verdict

### "Make this change everywhere: switch me to my focus setup across the Mac, authenticated browser, and pendant, but treat it as one transaction—if any surface cannot reach the requested state, restore the surfaces that did change and tell me exactly which one failed."
- **useful because:** The owner currently gets partial, surprising changes when a multi-surface request succeeds on one machine and fails on another. A real transaction would make the hive feel like one dependable instrument: browser tabs/session, Mac audio or app state, and pendant mode either converge together or return to the previously observed state.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a deterministic transaction coordinator and typed pre/post-state adapters; use a cheap model only to translate the spoken goal into an already-known routine. Realtime is needed only for the initial voice exchange, not orchestration.
- **latency:** Preview the intended state in under 2 seconds; commit ordinary changes within 10 seconds; on any failure begin compensation immediately and report the first failed surface within 2 seconds.
- **cost:** Low model cost after intent parsing. The dominant cost is local state capture and compensation calls; no raw page or audio data needs to leave the devices.
- **security:** State snapshots may include active URLs, window names, and browser session identifiers, so keep them on the relay/Mac with short retention and redact page content. Compensation must compare current state to the recorded pre-state and never overwrite an intervening owner action; report a conflict instead. The owner’s maximum-access policy remains unchanged—this is coordination and recovery, not an approval gate.
- **missing:** A cross-surface transaction coordinator with prepare, commit, compensate, and expired-transaction states; Typed state adapters for Mac settings/apps, browser tabs/session actions, and pendant mode/LED state; A durable transaction record that links each child action, pre-state, post-state, and compensation receipt; A conflict-aware compensation primitive that refuses to revert a surface changed after the transaction and gives the pendant a truthful partial-failure status

### "Let me hand a half-finished task from the Mac to the browser or from the browser to the Mac by saying “continue this there,” preserving the exact draft, selected item, and next safe step without making me repeat the context."
- **useful because:** The owner should not have to restart work because the current surface is inconvenient—voice while walking, browser session for an authenticated page, and Mac for files or applications. This is a true handoff of live work, not merely a new reminder: it carries the exact point reached and clearly identifies anything that cannot transfer.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic checkpoint extraction for structured fields and a small background model only to summarize unstructured UI state. Realtime handles the short spoken handoff request; it should not re-plan the entire task.
- **latency:** Capture the current checkpoint within 3 seconds and make the destination ready within 8 seconds; never silently submit or send a draft during transfer.
- **cost:** Low-to-moderate: local snapshots dominate; one small model call only when UI state is not structured. No repeated full conversation context should be sent.
- **security:** Never transfer cookies, tokens, passwords, or page bodies. Transfer opaque browser-session references and user-visible draft data only when the destination is authorized. Mark every field as exact, inferred, or unavailable; require the owner to explicitly request the final submit step.
- **missing:** A portable task-checkpoint format with draft fields, focused control, selection, next-step intent, provenance, and sensitivity labels; Mac and browser adapters that can export/import checkpoints without credentials or hidden page state; A relay handoff route with expiry, destination binding, and duplicate rejection; A pendant phrase/status path that reports transferred, destination-ready, blocked, and expired states


## Changes it proposed to its own stack

### `mac-harness` — Add an automatic, content-addressed preflight journal for every run_shell, write_file, move_path, delete_path, and browser download mutation. Before dispatch, resolve the touched paths, save only bounded metadata plus encrypted copies of small overwritten/deleted files and reversible rename records, and attach the snapshot ID to the action receipt. Expose a single recovery operation that can reconstruct the exact pre-action state even after the job has finished or the agent has restarted; do not gate execution or change FULL_CONTROL_MODE.
- **owner gets:** If an agent edits or deletes the wrong thing, the owner can say “put my files back before that action” from the pendant instead of hunting through Trash, shell history, or an incomplete undo list. It turns maximum access from a one-way risk into something recoverable.
- effort: Medium-high: filesystem preflight and atomic snapshot store, path-sensitive size/privacy policy, receipt linkage, crash recovery, and restore tests across shell and browser downloads.  ·  risk: Snapshots can contain secrets and can become stale if files change concurrently. Use encrypted-at-rest storage, strict retention/size caps, record the file hash and inode/mtime, and refuse silent overwrite during restore when the current hash differs; report a conflict to the pendant. Failed preflight must not block the original action under the owner's maximum-access policy.
- cost: Disk use bounded per job (for example 256 MB with LRU retention); negligible model cost and one extra local stat/hash pass. Encryption adds modest CPU cost.  ·  latency: Typically 50–300 ms for metadata and small files; large files should use copy-on-write/APFS snapshots or deferred hashing so normal actions remain fast.
- security: Improves recoverability but creates a high-value local store. Encrypt with a key held by the Mac agent, redact known credential paths by default from snapshot content while retaining metadata, and make restore receipts explicit.
- depends on: A durable action receipt that records the original submitted action and actual rewritten action separately; A restore endpoint that can be invoked by a pendant command and checks current content hashes; Boot-time reconciliation so snapshots for interrupted actions are not orphaned; A Mac filesystem watcher or APFS-aware snapshot implementation

### `model-routing` — Add a local shell-result triage stage that classifies a completed Mac action as success, expected-noise, retryable infrastructure failure, or owner-decision failure using exit status, stderr, receipt timing, and the actual rewritten action. Store the full output locally, send the relay only a bounded evidence excerpt and classification, and invoke a model only for the last category or when the classifier is uncertain.
- **owner gets:** Routine commands stop producing noisy or expensive explanations, while genuine failures arrive with a useful diagnosis instead of “Failed.” It also prevents credentials or giant test logs from being copied into every voice turn.
- effort: Medium: capture exit code and signal, add a bounded classifier and redaction layer, preserve raw local logs, and teach the relay to request the full output only by job ID when needed.  ·  risk: A bad classifier could hide a meaningful warning or mislabel a failure. Keep the raw receipt, include confidence and reason codes, never suppress nonzero exits, and provide a pendant phrase such as “show me the full error” to escalate.
- cost: Reduces model tokens substantially on successful shell work; small local CPU and disk cost for parsing and retention.  ·  latency: Adds under 20 ms for ordinary commands and makes owner-facing status faster by avoiding a model round trip.
- security: Less sensitive output leaves the Mac. Redaction must be conservative and preserve line/column references so the owner can request local full output.
- depends on: Capture shell exit code and terminating signal instead of flattening exec errors; Record submitted versus rewritten actions in the receipt; Bound and redact stdout/stderr before relay publication; Expose GET /jobs/:jobId/receipts or a dedicated local tail operation to fetch full output on request

### `integration` — Create a cross-surface causal ledger that assigns one intent lineage and monotonic step sequence to every pendant utterance, relay decision, Mac action, browser command, and resulting state observation. Unlike the existing per-job logs, it must preserve causality across child jobs and emit a compact, human-readable diff on demand: requested, actually dispatched, observed, compensated, and still unknown.
- **owner gets:** When something feels wrong, the owner can ask “what did you do because I said that?” and receive one trustworthy answer instead of searching separate Mac jobs, browser commands, and pendant status. It also makes partial success and stale completion claims visible.
- effort: Medium: define lineage/step IDs, propagate them through relay and browser bridges, persist append-only events, and build a local summarizer with gap detection.  ·  risk: The ledger could expose URLs, filenames, or spoken intent. Store sensitive fields locally or hashed, redact page text and audio, cap retention, and mark missing observations as unknown rather than infer success. Clock skew across devices must be handled with sequence numbers, not wall time alone.
- cost: Small local storage and relay bandwidth; low model cost because summaries can be generated from structured events and only ambiguous gaps need a model.  ·  latency: Adds sub-10-ms metadata work per step; owner-facing history should answer in under 2 seconds from local structured data.
- security: Improves accountability but creates a concentrated activity history. Encrypt at rest, scope queries to the owner’s authenticated session, and support deletion by lineage.
- depends on: A propagated lineage ID in POST /plan, POST /execute, browser commands, and pendant status events; An append-only event schema with sequence and observation confidence; A query endpoint that returns causal gaps and compensation history; Separate redaction rules for command strings, URLs, filenames, and speech-derived intent


## What it asked for

_Nothing._
## Its own summary

This round produced four non-gating improvements: (1) durable cross-device “finish when my Mac is available” checkpoints across relay, Mac, browser, and pendant; (2) encrypted pre-action filesystem snapshots so arbitrary FULL_CONTROL work is recoverable; (3) an honest USB bench verdict for the now-connected nRF9160 + ESP32 without opening the microphone; and (4) local shell-result triage that keeps routine output off the model path while preserving full local evidence. The bench idea was recorded with a similarity warning, so the real missing value is the bounded serial/parser and correlation layer, not another generic pipeline endpoint. I still need implementation of the checkpoint/reconciliation protocol, snapshot/restore store, and host serial framing parser; no additional permission or tool request is needed to specify them.

**Biggest unknown:** Whether the two live USB devices currently emit any stable health/frame protocol on the listed ports. The granted serial diagnostic call is available in principle, but the system has no host-side parser or product serial transport; until that is implemented, bench readiness remains unmeasured.

