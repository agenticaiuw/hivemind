# Harness derivation — mac-terminal — round 176

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Take the table or list on the authenticated page I’m looking at, turn it into a local CSV/Markdown file, and put the result in my project.”"
- **useful because:** The browser is the only node that can read sessions the Mac shell cannot access, while the Mac is the only node that can create and manipulate a useful local artifact. This closes a daily gap without copying credentials or requiring the owner to manually download, clean, and rename data.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → dashboard
- **model tier:** Realtime only to resolve the owner's target and destination; a cheap background model extracts/normalizes the already-captured table and validates row/column counts. Use no expensive model for file writing.
- **latency:** Capture in 2 s, write and validate in under 10 s for ordinary pages; speak a short completion plus path. If the page is paginated, continue in background and report progress through the pendant beacon.
- **cost:** About $0.005–$0.03 per invocation; extraction tokens dominate, and the browser page text can be reduced to a table capsule before model use.
- **security:** Keep page contents on the Mac/relay boundary and never send cookies or DOM scripts to a cloud model. Require the owner to name or confirm the destination when ambiguous. Write atomically to a new file, preserve the source URL/time and row count, and never overwrite an existing artifact silently.
- **missing:** browser action to extract structured table with provenance and pagination cursor; Mac action to atomically create a validated artifact from that capsule; relay correlation that binds browser commandId, local jobId, and output receipt; spoken error when a page changes or pagination cannot be completed

### "“Even with no LTE or relay connection, let the pendant control my Mac over its USB cable: press the button to pause/resume the current job, and tell me locally whether it worked.”"
- **useful because:** The hardware is physically attached today but unregistered with the relay, so the most immediate useful path is currently unavailable by design. A local USB control plane gives the owner a dependable emergency and pause control in airplane mode, during relay outages, or while developing firmware—without pretending a cloud command completed.
- **path:** pendant → mac-terminal → mac-planner → relay-realtime → dashboard
- **model tier:** No model for the button edge, serial framing, job lookup, or pause signal. Realtime is used only if the owner asks a spoken follow-up after reconnection.
- **latency:** Button-to-Mac acknowledgement under 150 ms over USB; LED/local tone under 250 ms. Reconciliation with relay occurs asynchronously when connectivity returns.
- **cost:** Negligible inference cost; one serial protocol and a small local daemon. Main cost is engineering and testing crash/reconnect cases.
- **security:** Bind commands to the physical USB device identity and a per-installation challenge key; never accept arbitrary shell text over serial. Only expose pause/resume/abort of jobs previously created by this owner, reject stale sequence numbers, and persist an acknowledgement with job ID, old state, new state, and monotonic counter. Do not claim pause if the child process cannot actually be signalled.
- **missing:** nRF9160 USB-serial control framing and persistent sequence/ack record; Mac local-agent serial listener for /dev/cu.usbmodem00096003658*; real process-group pause/resume/cancel semantics in run_shell and computer-use jobs; relay reconciliation that merges locally acknowledged controls without replaying them

### "“What did I change today, and where? Give me a trustworthy spoken summary with links or file paths.”"
- **useful because:** The owner currently has separate job history, browser provenance, action receipts, and pendant events, but no cross-surface timeline. A single answer would cover edits made by shell, browser, and local actions, distinguish observed from executed, and let the owner recover an exact artifact or page instead of relying on memory.
- **path:** relay-realtime → mac-planner → mac-terminal → browser-extension → pendant → dashboard
- **model tier:** Cheap background indexer builds normalized event records and hashes; realtime model only summarizes the already-filtered time window when asked. Use deterministic joins for job IDs, receipt IDs, URLs, and paths rather than spending model tokens on bookkeeping.
- **latency:** Incremental indexing costs under 1 s per completed job; a spoken daily summary should return in under 3 s from the local index. Detailed provenance can open in the dashboard afterward.
- **cost:** Near-zero per event; roughly $0.001–$0.01 per spoken query depending on event count. Storage is a bounded local SQLite/JSON index, not cloud transcript retention.
- **security:** Keep raw command strings, page text, and file names local; expose only redacted summaries and exact links/paths requested by the owner. Mark every item as executed, observed, proposed, or failed, and include source timestamps. Do not infer a file changed from a plan or browser observation. Permit deletion by date and avoid indexing secrets in environment variables or page bodies.
- **missing:** append-only normalized event index joining jobId, actionId, receiptId, browser commandId, pendant turn ID, and file/path hashes; instrumentation for shell exit/signal and file before/after metadata; browser provenance events for navigation/read/write and resulting URL; query route that returns a bounded, redacted change set to relay and dashboard

### "“Keep working on this project while I’m away: use my authenticated browser and Mac files, make only progress that is reversible, stop at the first ambiguity, and leave me a spoken morning handoff with exactly what changed and what needs me.”"
- **useful because:** Today the owner can delegate a task or run a routine, but cannot safely leave a multi-surface project in progress across sleep, relay restarts, browser-session changes, and Mac disconnects. This would be a true resumable work session: the browser supplies authenticated context, the Mac edits local artifacts, the relay remains the durable coordinator, and the pendant reports blockers rather than fabricating completion.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** Use a cheap background model for step selection, checkpoint compression, and routine progress checks. Use realtime only when the owner starts the task, resolves an ambiguity, or requests the spoken handoff. Escalate to the expensive tier only for genuinely ambiguous decisions.
- **latency:** A task may run for hours with no conversational connection. Each individual step should begin within 5 s of its predecessor; reconnecting should yield a concise state summary within 2 s. The morning handoff should be generated from checkpoints, not replay the entire transcript.
- **cost:** Approximately $0.02–$0.20 per multi-hour task depending on page volume and number of decisions; browser extraction and model context dominate. Deterministic file operations and checkpointing should cost no inference tokens.
- **security:** The owner explicitly authorizes the project scope at start, but the system must never broaden it. Keep authenticated page content and local files on-device whenever possible. Every step needs a before/after capsule, reversibility classification, source URL/path, and checkpoint ID. Stop on permission prompts, destructive operations, changed page structure, conflicting edits, or uncertain recipient/destination. The pendant must say “stopped for your decision,” never “done,” when the relay or Mac disappears.
- **missing:** durable cross-surface workflow state machine with checkpoint, lease, pause, resume, and stop-on-ambiguity semantics; exactly-once step identity spanning browser command IDs, Mac job IDs, action receipts, and relay retries; reversible local artifact transactions and browser undo/rollback metadata; heartbeat and ownership handoff across relay restart, browser disconnect, and Mac sleep; morning handoff generator that distinguishes completed, attempted, blocked, and unverified work; pendant protocol for queued, checkpointed, blocked, and resumed states

### "“Compare the number or status in this authenticated web portal with the matching local file, and tell me which source is stale—without changing either one.”"
- **useful because:** The browser can see private portal state and the Mac can inspect local project files, but today they are separate observations. The owner needs a trustworthy discrepancy answer before acting: identify matching records, show both timestamps and evidence, explain the conflict, and leave all sources untouched.
- **path:** browser-extension → mac-terminal → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Cheap model or deterministic parsers perform normalization, key matching, timestamp comparison, and arithmetic. Realtime is only for the final spoken explanation when the owner asks.
- **latency:** Under 5 s for ordinary pages and files; paginate or parse larger sources in the background while reporting that comparison is incomplete rather than guessing.
- **cost:** $0.001–$0.02 per comparison; model cost is dominated by irregular table normalization. Most structured CSV/JSON comparisons should be local and effectively free.
- **security:** Do not upload portal credentials, cookies, or full private documents. Return minimal evidence slices, source URLs/paths, observed timestamps, and confidence. Treat absence and stale data as distinct states; never update either source unless the owner explicitly asks afterward.
- **missing:** shared comparison request with source selectors and matching-key hints; browser structured extraction plus local file parser with common provenance format; deterministic diff engine for values, timestamps, and missing records; spoken evidence capsule that can be reopened in the dashboard

### "“Watch this portal page and the corresponding local file together. If either changes in a way that affects the other, alert me on the pendant with the exact conflict; otherwise stay quiet.”"
- **useful because:** A browser watch alone cannot know whether a local draft has become stale, and a file watch alone cannot interpret the authenticated source. Coupling both lets the owner work normally while receiving only actionable cross-source conflicts instead of noisy page or filesystem notifications.
- **path:** browser-extension → mac-terminal → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Deterministic hashes, field extraction, and debounce first; a cheap background model interprets only changed fields. Realtime is not used for monitoring, only for the owner's follow-up question or spoken alert phrasing.
- **latency:** Detect ordinary changes within 30 s, with a quiet-period debounce of 5–10 s. Alert audio should begin within 2 s of a confirmed conflict; suppress repeated alerts until the owner acknowledges or the conflict changes.
- **cost:** Near-zero for hashes and structured fields; approximately $0.001–$0.02 per meaningful change requiring interpretation. The dominant cost is extracting changed authenticated page content.
- **security:** Store only selected fields, hashes, URLs, paths, and timestamps—not continuous page text or file contents. Require explicit pairing of a page and file and an expiry time. Never auto-edit either source. Include confidence and evidence snippets in every alert, and mark monitoring as paused when browser authentication or the Mac disappears.
- **missing:** paired browser/page-watch and local-file-watch subscription model; field-level normalization and change correlation with debounce/deduplication; relay notification policy that routes only actionable conflicts to the pendant; expiry, pause, and owner-acknowledgement state persisted across reconnects


## What it asked for

_Nothing._
