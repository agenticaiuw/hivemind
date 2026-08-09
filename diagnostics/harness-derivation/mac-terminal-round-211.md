# Harness derivation — mac-terminal — round 211

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Take the latest PDF in my Downloads, fill the currently open authenticated web form with it, submit it, and tell me exactly what was sent.”"
- **useful because:** This is a real end-to-end task no single node can do: the Mac owns the local file, Safari owns the authenticated session, and the pendant is the fastest way to ask and receive a concise confirmation while away from the keyboard. It eliminates the fragile today workflow of manually finding an attachment, switching tabs, and wondering whether submission succeeded.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use the realtime tier only to clarify which open form if ambiguous and to speak the final result; use a cheaper background planner for file ranking, browser field mapping, and verification.
- **latency:** 15–30 seconds normally; speak an immediate 'I found the form and candidate file' progress update, then verify the post-submit confirmation page before claiming success.
- **cost:** Roughly $0.01–$0.05 per invocation depending on vision retries; browser and Mac execution dominate latency, not tokens.
- **security:** The file and form contents are sensitive and must remain on the Mac/browser surfaces; do not upload bytes to the relay or model unless the owner explicitly asks. Show the exact filename, destination origin, fields changed, and returned confirmation. Submission is an external side effect and should require the owner's existing confirmation convention, while file discovery and field preview can be automatic.
- **missing:** A typed cross-surface transaction that can pass a local file handle from Mac file_select to an authenticated browser upload without exposing file bytes to the planner; Browser-side post-submit verification and a durable receipt linking filename hash, origin, form fields, and confirmation text; A pendant response template that reads a short success/failure proof rather than narrating page contents

### "“Are both boards healthy right now, and is the audio path actually moving frames? If not, tell me which side failed and what I should do.”"
- **useful because:** The hardware is physically present today, but the system cannot honestly answer this from relay health: the nRF9160 and ESP32 can be USB-enumerated while firmware, UART framing, clocks, or audio acknowledgements are broken. A single spoken diagnostic would turn a five-minute serial-debug session into an actionable answer and would prevent the pendant from claiming wearable continuity when only the bench cable works.
- **path:** pendant → mac-planner → mac-vision → relay → dashboard
- **model tier:** A cheap background parser should classify bounded UART health frames and compare counters; realtime is only needed to explain the diagnosis over audio or ask whether to start a capture.
- **latency:** Under 5 seconds for a bounded 500 ms probe; under 20 seconds if it runs the existing dual-chip capture scripts and waits for correlated counters.
- **cost:** Near-zero model cost for structured counters; at most a few cents if logs need interpretation. Mac serial I/O and firmware diagnostics dominate.
- **security:** USB output can contain device identifiers and debug payloads; keep raw logs local, return only counters, firmware versions, and a redacted failure summary. Never infer LTE registration from USB success. Starting a capture is local and reversible, but flashing or resetting either board must be a separately explicit action.
- **missing:** A real bounded host serial reader/parser capability (the requested schema remains unresolved in the live inventory); A shared health-frame protocol emitted by both firmwares: boot id, firmware version, transport, RX/TX/ACK counters, overruns, and monotonic timestamp; A correlation check joining nRF9160 audio turn IDs with ESP32 bridge frame counters and POST /pipeline audio telemetry; A Mac-side command that runs diagnostics/dual_chip_autocapture.sh without leaving orphan capture processes

### "“Check the authenticated Discord tab, find messages that need my reply, give me a three-line spoken triage, and draft (but do not send) the best reply to the one I choose.”"
- **useful because:** The browser session is already authenticated and reachable, while the pendant is useful precisely when the owner is not looking at the screen. This combines authenticated-page reading, local drafting, and a safe handoff: the owner gets urgency and context by voice, then returns to a prepared draft instead of losing the thread or accidentally sending a message.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Use a low-cost background model to cluster unread messages and extract only actionable threads; use realtime for the spoken triage and for the owner's short choice of thread. Keep the final draft generation cheap unless the thread is unusually complex.
- **latency:** 5–10 seconds for tab inspection and triage; draft within another 5 seconds after the owner names a thread.
- **cost:** A few cents at most per invocation; page extraction and browser round trips dominate, with no need to send full history to the realtime tier.
- **security:** Authenticated message text is private and should stay in the browser/local agent boundary; pass only selected thread excerpts to the drafting model and do not retain them as durable memory by default. Drafting is non-mutating; sending must be a separate explicit browser action that the owner can see and confirm. Include the channel, author, timestamp, and source URL in the spoken/result receipt.
- **missing:** Unread/action-needed detection that understands Discord thread state rather than relying on a page's visible text alone; A draft buffer tied to the browser tab and thread id, so the owner can resume it later without sending; A compact spoken response protocol for selecting a thread by ordinal or channel name and handling stale tabs

### "“Compare this month’s utility bill in the authenticated portal with the last six bills in my local folder, explain every material change, and prepare—but do not send—a dispute message if something is wrong.”"
- **useful because:** This gives the owner an outcome they cannot get from any one surface today: the browser can reach the private billing portal, the Mac can inspect the historical local documents, and the pendant can turn the result into a short decision while the owner is away from the screen. It catches silent price or usage changes and produces an actionable draft rather than merely summarizing a page.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Use a background model for OCR/table extraction, normalization, and six-month comparison; use realtime only to ask a clarifying question and speak the final anomaly summary. Use a stronger model only when line-item reconciliation is ambiguous.
- **latency:** 30–90 seconds for portal retrieval, local-document extraction, and comparison; provide a spoken progress update after the portal and local corpus are located.
- **cost:** Approximately $0.05–$0.25 per comparison depending on OCR and number of pages; browser I/O and local document parsing dominate latency.
- **security:** Billing documents and account data stay on the Mac/browser boundary; the relay receives only an anomaly summary and selected evidence references. Do not retain raw bills as memory. Display the portal origin, statement dates, amount deltas, and confidence. Drafting a dispute is non-mutating; sending it or changing account settings requires a separate explicit action.
- **missing:** A private local-document indexing and table-extraction service that can compare PDFs without uploading them to the model; A browser transaction that retrieves the current statement and exposes stable line-item provenance, not just visible-page text; A cross-surface evidence bundle joining each claimed delta to a local file/page locator and statement URL; A draft workspace keyed to the billing account and comparison run, with expiration and no-send-by-default semantics

### "“Before I leave, check my authenticated travel booking and local itinerary files for any contradiction—dates, terminals, names, or baggage—and give me one corrected, offline-readable itinerary with the source for every field.”"
- **useful because:** Travel failures happen at the boundary between a private web booking and stale local files. The browser alone cannot see the owner’s downloaded confirmations and the Mac alone cannot see the current booking. A wearable answer that cites each field and leaves a local offline copy is useful even after the network or browser session disappears.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Background model for document extraction and field-level reconciliation; realtime only for a short spoken warning and one clarification when two bookings compete.
- **latency:** 20–60 seconds; the owner should hear immediately if a contradiction is found, with the complete offline artifact following shortly after.
- **cost:** $0.02–$0.10 per run, mostly document parsing and browser reads.
- **security:** Passport, booking, and identity data remain local. The spoken channel should say only the minimum needed (for example, terminal and time), never read booking codes aloud by default. Encrypt the offline artifact, expire it after the trip, and retain field-level source locators rather than raw page copies.
- **missing:** A local artifact generator with field-level citations and expiry; A reconciler that treats booking portals as current authority while preserving contradictory local evidence; A single offline itinerary format readable by the pendant/phone without reopening the authenticated session; A privacy-aware spoken redaction policy for travel identifiers


## Changes it proposed to its own stack

### `mac-harness` — Make every run_shell execution a resumable command session rather than a one-shot exec: launch with a captured process group and generated session id; persist argv-equivalent tokenization (or the exact command plus an explicit shell marker), cwd, a redacted environment fingerprint, pid, start/finish times, exit code/signal, bounded stdout/stderr tails, and the job/ledger join. On timeout or cancellation, terminate the process group and record the actual outcome. On agent restart, reconcile sessions whose pid is gone as interrupted and offer an automatic retry only for commands classified idempotent by the planner. Preserve FULL_CONTROL_MODE and unattended execution; this is observability and recovery, not a gate.
- **owner gets:** When a long Mac task fails today, the owner gets 'Failed' without an exit code, cancellation does not stop the running process, a restart leaves it falsely processing forever, and retries can duplicate side effects. This would make 'what happened?' answerable and would recover ordinary transient failures without asking the owner to rediscover where the task stopped.
- effort: Medium-high: replace exec with a spawned process-group runner, extend receipts/job records, close and join ledgers, add boot reconciliation, and add idempotency metadata plus tests for timeout, SIGTERM, restart, and output caps.  ·  risk: A bad termination implementation could kill unrelated descendants; scope process groups and record before signaling. Automatic retry could duplicate a mutation; default retries to read-only/idempotent commands and expose a clear non-retried state rather than guessing. On upgrade, old jobs without pid/exit fields should be marked legacy-interrupted, never rerun automatically.
- cost: No meaningful API cost; modest local disk growth for capped tails and receipts, likely tens of KB per job. CPU overhead is negligible versus the command itself.  ·  latency: Negligible for normal commands; cancellation becomes prompt instead of waiting up to 120 seconds, and restart recovery becomes immediate.
- security: Do not persist raw environment values; record names plus a hash and redact token-like command arguments. The exact command remains available to the trusted local job record because the owner deliberately allows full control. Process-group control increases power but does not change authorization.
- depends on: Fix orchestrator ledger closure and populate planMeta.jobId so job and ledger records join; Add exit code/signal and pid fields to action receipts; Replace exec with spawn/execFile-compatible process-group handling while retaining shell-command compatibility; Boot-time reconciliation of pendant-jobs.json and interrupted ledgers; A small idempotency classification attached to each action, without introducing an approval gate

### `new-surface` — Add an owner-facing 'evidence packet' surface shared by pendant, Mac, and browser: a short-lived, encrypted, append-only bundle containing normalized claims, source locators, timestamps, hashes of local files, and the exact action/draft state. It should render as a concise spoken answer on the pendant, a readable local artifact on the Mac, and clickable source evidence in the browser. It must support expiry and revocation, and never require raw private page/document content to pass through the relay.
- **owner gets:** Today the agent can perform pieces of a task but cannot give the owner one durable answer that proves where each important fact came from after a browser session changes or a local file moves. This lets the owner trust decisions about bills, travel, forms, and messages without keeping sensitive pages open or asking the model to remember private documents.
- effort: High: define a cross-surface evidence schema, implement local encrypted storage and expiry, add browser source anchors and local-file hashes, add pendant speech rendering, and make every action/draft receipt reference packet claims.  ·  risk: Source locators can go stale and hashes prove identity, not truth; show stale/unsupported status rather than silently presenting old evidence. Encryption-key loss should degrade to an expired packet, never plaintext recovery. Keep raw content local and cap packet size.
- cost: Low inference cost after extraction; moderate local storage and engineering cost. Packets should be kilobytes, with raw documents excluded.  ·  latency: Adds under a second for packet assembly; source extraction remains the dominant time.
- security: Improves privacy by keeping raw content off the relay, but creates a sensitive local store. Use per-packet keys, OS keychain protection, short TTLs, and explicit deletion receipts.
- depends on: A browser provenance API that returns stable page/field anchors; A local file identity/hash API and encrypted short-lived artifact store; A relay protocol for claim summaries and packet IDs without raw content; Pendant speech and button controls for 'source', 'next evidence', and 'forget this packet'


## What it asked for

_Nothing._
## Its own summary

Fresh discovery confirms Safari is online with four authenticated-capable tabs and the Mac bridge is online, but the granted USB serial diagnostic schema still has no live implementation. I recorded four concrete advances: (1) cross-surface local-PDF upload into an authenticated form with proof, (2) a bench health answer correlating nRF9160 and ESP32 audio counters, (3) supervised/recoverable shell sessions that preserve full-control operation while fixing exit status, cancellation, restart recovery, and job-ledger joins, and (4) voice triage plus unsent drafting for an authenticated Discord thread. The most useful is the first: it joins a local file, authenticated browser, and wearable conversation into one task.

**Biggest unknown:** The live route inventory does not expose the concrete browser action names or a real serial reader, so I still need implementation of a bounded Mac serial/health-frame reader and typed browser file-upload/draft primitives. I do not need another serial-tool request; the existing grant is unresolved. I also need the cross-surface transaction/receipt layer to keep sensitive bytes local and prove what was submitted.

