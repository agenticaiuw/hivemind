# Harness derivation — mac-terminal — round 147

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-browser-recovery** — Live Mac agent is in FULL_CONTROL_MODE with browser extension online and 3 tabs, but Accessibility and Screen Recording are untrusted/missing; a recent browser_read_page failed due to frame access and a subsequent retry succeeded.
  - evidence: GET /ops/status returned fullControlMode:true, browserExtension.online:true, accessibility.trusted:false, screenRecording.granted:false; GET /jobs showed failed then completed browser_read_page for the same tab.

## Capabilities it proposed

### "“When the pendant or bridge misbehaves, file a complete bug report for me.”"
- **useful because:** The wearable is physically attached over USB today, and the owner already wants a pendant that files its own UART bug reports. A Mac collector can capture the serial window, correlate it with relay/Mac job receipts and firmware version, have the browser open a prefilled GitHub issue, and speak a one-sentence report link—turning an opaque failure into an actionable issue without manually reconstructing logs.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** background for log clustering and report drafting; realtime only for the spoken completion sentence
- **latency:** Capture immediately; draft in under 30 seconds after a crash; no need to keep the voice turn open.
- **cost:** About $0.01–$0.05 per incident, dominated by background log summarization; serial capture and metadata are local.
- **security:** UART may contain tokens, transcripts, or private data. Redact secrets locally before upload, keep raw logs on Mac with short retention, and require confirmation only at the final GitHub issue submission; draft creation is safe.
- **missing:** A USB-serial reader for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA with crash-window buffering; A crash/event correlation schema joining UART timestamps to /jobs receipts and relay pipeline IDs; A browser action that drafts a GitHub issue with attachments but does not submit it; Local redaction and retention controls

### "“That CI failure email is urgent—find the failing code, explain it, and prepare the smallest fix for review.”"
- **useful because:** The current authenticated Gmail view already shows repeated buckymatch CI/Data Age Monitor failures, but today the browser and Mac do not close the loop. This capability would follow the email link in the browser, inspect the matching local repository and recent git history on the Mac, run targeted tests, then leave a patch/diff and a cited spoken diagnosis. It combines private browser evidence with local execution that neither surface can provide alone.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** background for extraction, test-output summarization, and patch drafting; realtime only to acknowledge and deliver the result
- **latency:** Initial diagnosis in 1–2 minutes; patch preparation may run asynchronously with a durable job receipt.
- **cost:** $0.03–$0.20 per incident depending on test output and planner escalation; shell/tests are local and free.
- **security:** Private email and source code stay on the Mac/relay only as needed. Never paste repository secrets into prompts; do not push or send anything. Show the exact diff and test commands before any future submission.
- **missing:** Authenticated Gmail link extraction that preserves message/thread provenance; Repository locator and branch/worktree mapping for the linked project; A durable Mac shell job that can run tests and capture stdout/stderr plus artifacts; Diff/result packaging and spoken completion callback

### "“If Safari cannot read a page, recover automatically and tell me what actually happened.”"
- **useful because:** A live job just failed because the browser extension lacked access to a frame, while the next attempt succeeded. The owner currently gets an opaque failure. A cross-surface recovery ladder could detect frame/permission failures, reopen or focus the page in Safari via the Mac, retry with a safe text/readability route, and return a truthful one-sentence result (or the precise missing permission) instead of making the owner repeat the request.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Deterministic error classifier and recovery ladder first; background model only to summarize recovered page content; realtime for status speech
- **latency:** Detect and retry within 5 seconds; at most two recovery attempts, then report the exact failure.
- **cost:** Near-zero for deterministic retries; $0.005–$0.03 if content summarization is needed.
- **security:** Retries must remain in the same authenticated tab/session and never silently navigate to lookalike domains. Read-only recovery needs no approval; any click/form action remains a separate explicit command.
- **missing:** Stable browser error taxonomy (frame denied, stale tab, extension offline, permission missing); Mac fallback adapter using Safari automation/read-only AppleScript or URL focus; A result contract that distinguishes recovered, partial, and failed states and sends it to the pendant; Permission health check for Accessibility/Screen Recording

### "“What happened across my pendant, browser, and Mac while I was away? Give me one trustworthy timeline.”"
- **useful because:** Today evidence is split across UART behavior, relay pipeline events, browser commands, and Mac job receipts. The owner cannot reconstruct a failure or missed task without manually inspecting four surfaces. A cross-surface event ledger would join those streams by correlation ID and time, distinguish requested/completed/failed/unknown, attach the original evidence, and leave a short spoken postmortem plus a detailed local report.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Deterministic event join and status calculation first; background model only for the short narrative; realtime only for delivery.
- **latency:** Recent timeline in under 5 seconds; historical reconstruction under 30 seconds.
- **cost:** Usually under $0.02, mostly background summarization; event joining is local/relay-side.
- **security:** Do not send raw email/page text to the narrative model by default. Store sensitive event payloads locally, expose source links and hashes, and redact credentials from UART and shell output.
- **missing:** A shared correlation-ID/event envelope across pendant, relay, browser, and Mac; An append-only timeline query with explicit unknown and superseded states; Evidence references from UART offsets, browser tab/DOM records, and Mac receipts; A local report export and pendant-friendly summary formatter

### "“Save the report I’m viewing in Safari into my workspace, verify it, and tell me exactly where it landed.”"
- **useful because:** The browser may hold an authenticated report that the Mac filesystem cannot reach directly, while the pendant is the natural place to request the handoff. The system should transfer the chosen private page or download through the browser session, write it into ~/AI-Pendant-Workspace with a deterministic name, compute a hash and source metadata, and speak a completion receipt. This is more trustworthy than copying a URL and hoping the local download matches.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Deterministic transfer, hashing, naming, and metadata; background model only to choose a filename or summarize when requested.
- **latency:** Small files in under 10 seconds; larger downloads continue asynchronously with a durable receipt.
- **cost:** Negligible model cost; local transfer and hashing dominate.
- **security:** The browser session may contain private documents. Restrict the destination to an owner-approved workspace, never expose raw contents to the relay unless requested, preserve source URL/tab identity, and report partial or hash-mismatch results truthfully.
- **missing:** A browser command to export the current authenticated response/download as bytes; A Mac-side receive endpoint with atomic write, hash verification, and collision-safe naming; A provenance sidecar format linking file hash to tab, URL, timestamp, and account/session; A durable cross-surface completion receipt

### "“When the pendant notices I’m back at my Mac, restore the work context I left there and tell me what needs attention.”"
- **useful because:** The pendant is physically attached to the Mac today, but reconnection is treated as transport rather than presence and context. A local link event could trigger a private handoff: restore the last unfinished Mac job, reopen only the relevant browser tabs, surface failed actions and pending drafts, and speak a compact status. It would make the worn device the continuity key between away-from-Mac and at-Mac work without requiring the owner to remember what was left open.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** Deterministic USB/link and job-state reconciliation; background model only to rank attention items; realtime for the spoken handoff.
- **latency:** Detect link and produce a status in 3 seconds; restoration may continue asynchronously.
- **cost:** Near-zero model cost for state reconciliation; under $0.01 for optional ranking.
- **security:** Presence must not unlock accounts or perform irreversible actions. Keep the handoff local while USB-connected, require an explicit owner gesture/phrase for opening sensitive tabs, and never infer presence from a stale heartbeat.
- **missing:** A reliable pendant USB connect/disconnect event with identity verification; A resumable context snapshot covering unfinished jobs, browser tabs, and drafts; A safe tab restoration contract that preserves session affinity without replaying commands; A local-vs-relay presence state machine and truthful spoken status


## What it asked for

_Nothing._
