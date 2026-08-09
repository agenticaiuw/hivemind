# Harness derivation — mac-terminal — round 190

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""What exactly happened to the thing I asked you to do?" — Give me one spoken answer that joins the pendant request, the Mac actions, browser evidence, and any failure or partial completion, with timestamps and confidence."
- **useful because:** Today the owner must infer truth from scattered job, receipt, browser, and LED states. This would be the single most useful everyday behavior: after any hands-free command, the owner can ask once and get an honest causal account, including 'it never ran' versus 'it ran and the site rejected it'.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for receipt joining and summarization; realtime only to speak the already-built summary
- **latency:** Under 2 seconds when records exist; no fresh Mac round trip unless the owner explicitly asks for live status.
- **cost:** Usually one cheap background summarization call, roughly $0.001–$0.01; dominant cost is context if raw stdout/page text is resent, so pass hashes, excerpts, and structured receipts first.
- **security:** Browser titles, URLs, shell paths, and failures can be sensitive. Keep raw bodies local, send redacted structured fields and evidence hashes to relay, and say when confidence is based on a stale cache. No mutation or confirmation is needed because this is read-only reporting.
- **missing:** A join key linking jobId, ledgerId, action receipt IDs, browser command IDs, and pendant turn ID; A compact evidence-capsule join route that redacts raw stdout/page text; A spoken receipt formatter with explicit partial/unknown states

### ""Stop that now." Make a pendant button press or spoken command terminate the currently running Mac shell or computer-use process immediately, then tell me whether it was killed, had already finished, or could not be reached."
- **useful because:** The current cancel signal is only checked between steps; a 120-second shell or computer-use action keeps running after the owner says stop. This gives the owner a real emergency brake for runaway UI automation, stuck scripts, or an accidental long command.
- **path:** pendant → relay → mac-planner → mac-vision → dashboard
- **model tier:** deterministic control path; no LLM required for kill, with realtime only for the spoken acknowledgement
- **latency:** Issue the kill in under 300 ms after a live link; report the final process state within 2 seconds. If the Mac is unreachable, persist the cancel intent and report queued/unconfirmed rather than claiming success.
- **cost:** Near-zero API cost; a small local process supervisor and one relay event dominate implementation, not model tokens.
- **security:** This is intentionally powerful but scoped to the owner’s active agent job, never arbitrary PIDs. Use process groups so descendants are killed, record signal and final exit state, and make the pendant LED distinguish killed from unreachable. Do not infer completion from a lost connection.
- **missing:** Run shell and computer-use actions under a tracked process-group supervisor with PID/start-time identity; A relay command route carrying a job-scoped cancel intent and delivery receipt; An abort path that calls killpg/Windows equivalent and settles the action ledger with interrupted status

### ""Keep an eye on this authenticated page and only interrupt me if a change affects my work." Watch the browser session, compare a meaningful page change against the current Mac project/session, and send the pendant a short alert with the exact changed evidence and a quiet digest for everything else."
- **useful because:** The browser can see logged-in pages that the relay cannot, while the Mac knows which project and files are active. Combining them avoids noisy 'page changed' alerts and catches the rare change that actually matters, without requiring the owner to keep a tab open in their attention.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** background model for change classification and local-project relevance; deterministic page hashing/diffing and relay delivery; realtime only when the pendant alert is requested
- **latency:** Poll or event-deliver within 1–5 minutes depending on site support; classify in under 10 seconds; alert immediately only above the owner’s configured relevance threshold.
- **cost:** Low ongoing cost: deterministic DOM/text hashes most cycles, one cheap background classification per substantive diff (roughly $0.001–$0.02). The dominant cost is authenticated page polling and occasional long page context.
- **security:** Never export cookies, form fields, or full private pages. Keep snapshots in the browser/local Mac, transmit only redacted diff spans and evidence hashes, and require explicit opt-in per URL/session. Alerts should disclose stale/offline state and never claim a page was checked while Safari was disconnected.
- **missing:** A browser watch definition that stores redacted structural/text diffs rather than only latest page text; A Mac relevance adapter exposing active project/session metadata without uploading files; A relay priority classifier and pendant alert queue with quiet-hours/digest semantics

### ""Make this whole computer task atomic: if any step fails, put every touched local file, app setting, and browser tab back exactly as it was, then tell me what was rolled back.""
- **useful because:** The owner can currently undo only a small handful of action types. A multi-step task can leave half-created files, changed settings, and navigated authenticated tabs after a late failure. Atomic execution would make ambitious commands trustworthy without adding an approval gate.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** deterministic transaction coordinator; background model only to summarize the rollback report
- **latency:** Checkpoint preparation under 1 second for normal tasks; rollback starts immediately on failure and reports within 5 seconds plus filesystem-specific completion time.
- **cost:** No per-request model cost beyond a short summary. Storage is the dominant cost: local copy-on-write snapshots or app-specific state journals, bounded per active transaction.
- **security:** Snapshots may contain secrets from authenticated tabs and private files. Keep them on the Mac, encrypt at rest, expire them quickly, and send only action names and hashes to the relay. Never pretend rollback succeeded if an external side effect (email, purchase, remote server write) cannot be reversed.
- **missing:** A transaction coordinator spanning shell, typed Mac actions, and browser commands; Pre-state adapters for files, app settings, window/tab state, and browser session navigation; A commit/rollback protocol that settles one durable outcome in the action ledger and gives the pendant a truthful result

### ""Do this privately on my Mac; do not send my files, page contents, or command output to the relay or a hosted model." Then let the pendant still control the task and hear the result."
- **useful because:** Today the owner cannot express a reliable data-residency boundary while retaining the hive's reach. This would make the system usable for confidential work: the Mac and browser do the reasoning locally, while the relay receives only an opaque task ID, progress state, and a redacted spoken result.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** local Mac model for planning, browser interpretation, and summarization; realtime relay only transports intent and a deliberately redacted response
- **latency:** Initial acknowledgement under 1 second; local planning under 10 seconds for ordinary tasks; no cloud fallback unless the owner explicitly changes the mode.
- **cost:** Cloud token cost near zero in private mode. The expense is local model storage/RAM and slower inference; a small local model can handle deterministic tasks, escalating only with explicit consent.
- **security:** This must be an enforceable routing mode, not a prompt instruction. Block raw page/file/stdout uploads at the relay boundary, audit every outbound field, scrub crash logs and telemetry, and clearly say when a requested task cannot be completed locally. Browser cookies remain in Safari and never enter the model context store.
- **missing:** A Mac-local planner/model runtime with browser and shell tool access; A hard outbound data-residency contract enforced before serialization, not after model planning; A pendant/relay privacy-mode state machine and receipt proving whether any sensitive payload left the Mac

### ""Keep working while I step away, but pause if someone else touches the Mac and resume only when I am back." Use the pendant as my presence key, the Mac as the local activity sensor, and preserve the task exactly across the pause."
- **useful because:** A hands-free agent is most useful during interruptions, yet today a running task cannot distinguish the owner leaving from another person taking the keyboard. This enables long jobs without exposing an unlocked authenticated browser or letting automation continue under an unknown user.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** deterministic presence and pause/resume state machine; background model only for task continuation after a genuine state change
- **latency:** Detect lock/activity/presence changes within 1 second; pause before the next destructive step; resume within 3 seconds after authenticated return.
- **cost:** Negligible model spend. The cost is local event monitoring and a small durable task checkpoint; no continuous cloud inference.
- **security:** Presence must not be inferred from Wi-Fi or an open tab alone. Bind a short-lived cryptographic presence lease to the pendant button/link, expire it on disconnect, and treat any ambiguity as paused. Do not transmit screen contents merely to determine presence; record only state transitions and task IDs.
- **missing:** Mac lock/unlock and input-owner event hooks exposed to the agent; A pendant-bound presence lease and relay heartbeat distinct from ordinary connectivity; Pause/resume checkpoints that prevent browser or shell actions from running after lease expiry


## What it asked for

_Nothing._
## Its own summary

Produced three distinct cross-surface capabilities: (1) a single spoken, evidence-backed causal receipt joining pendant turn, Mac job, browser evidence, and partial/unknown states; (2) a real emergency stop that kills the active process group rather than merely setting a cooperative abort flag; and (3) relevance-filtered authenticated browser watches corroborated against the active Mac project, with quiet digests and high-priority pendant alerts. The live Mac bridge is online and Safari has nine tabs; /jobs confirms browser actions and /routing currently reports no sampled token usage. The granted mac_read_diagnostics schema still fails resolver matching in this run, so I could not obtain fresh host process/audio facts.

**Biggest unknown:** Whether the browser watch and evidence-joining primitives already exist under routes not exposed by the summaries; their implementation needs a complete route/action inspection before engineering begins. For the emergency stop, the key unknown is whether the current Mac process launcher can expose and reliably kill descendant process groups without replacing the owner-approved FULL_CONTROL surface.

