# Harness derivation — mac-planner — round 178

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “hold this for me,” make the next time-sensitive desktop action wait for a physical press on my pendant; after I hear the exact one-sentence preview, pressing the bookmark button commits it, and otherwise it expires."
- **useful because:** This makes the pendant a real, unforgeable confirmation surface for the Mac/browser hive instead of trusting a voice transcript or an accidental retry. It is the single most useful missing behavior: I can authorize a prepared send, purchase, deletion, or browser submission while hands are away from the keyboard, with a clear spoken preview and an expiry.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → relay
- **model tier:** Realtime only for the short preview and confirmation dialogue; deterministic relay state machine for nonce, expiry, and replay protection; no background model call for the commit.
- **latency:** Preview under 2 seconds; button-to-commit acknowledgment under 1 second when USB/LTE is available; if disconnected, retain a pending intent but never commit until the nonce is revalidated online.
- **cost:** About $0.001–$0.01 per invocation, dominated by one short realtime turn; Mac/browser execution is local.
- **security:** The relay must bind a single-use random nonce to the exact serialized action list, target URL/file, account scope, and expiry, and reject stale or altered confirmations. Speak a redacted preview for secrets. Sending mail, purchases, deletion, and authenticated submissions require this physical press; harmless opens can remain immediate. The current FULL_CONTROL path has no live approval gate, so this must be an explicit policy layer rather than assuming the existing executor is safe.
- **missing:** A relay-held pending-action record and nonce verifier shared by /plan and /execute; A pendant event correlation path that can distinguish the owner's next offline_moment_bookmark from an unrelated bookmark; An execution endpoint that accepts the verified nonce and emits an immutable result receipt; Owner-configured action classes and redaction policy, read at runtime

### "While I am working, let me press the pendant once to mark the exact thing I am looking at, then later say “bring back that research” and have the Mac reopen the same Safari tab plus the companion files and notes that were actually present at the mark, not a guessed URL."
- **useful because:** A timestamp alone is not enough when a research thread spans a browser session, VS Code, Preview, and Notes. This turns the worn button into a reliable handoff between attention states: I can leave a thought physically, then recover the concrete working set instead of searching from memory.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → relay
- **model tier:** Cheap background model (or deterministic matching) clusters titles, paths, and timestamps; realtime is used only to answer the spoken retrieval request. The capture itself must not invoke a model.
- **latency:** Capture acknowledgment under 200 ms locally; retrieval summary under 3 seconds; opening the bounded workspace within 2 seconds after the owner confirms the target if multiple marks match.
- **cost:** Less than $0.005 per capture/retrieval in the common case; model cost only when disambiguating several marks or summarizing changed material.
- **security:** Store hashes, app identities, tab IDs, URLs, and file paths by default, not page bodies or document contents. Never persist passwords, selected text, or authenticated page content unless explicitly requested. Reopening a tab can expose private material on screen, so report the target and require an explicit spoken confirmation when the snapshot contains an authenticated URL or secret-scoped file.
- **missing:** A Mac snapshot route that atomically records foreground app, browser tab IDs, open document paths, and timestamps in one capture; Browser-session APIs to reopen an existing tab by durable session/tab identity rather than only navigating a URL; A small relay index that links offline_moment_bookmark IDs to Mac/browser snapshots and expires stale tab identities; A restore planner that computes open/close actions and a receipt without silently overwriting the current workspace

### "Run a pendant clinic from my Mac: I say “check the pendant,” it runs the no-microphone diagnostic over the USB-connected nRF9160 and ESP32 bridge, captures UART counters and the 24 kHz fixture result, files a concise bug report in my workspace, and reads me only what failed."
- **useful because:** The hardware is physically here and testable now even though LTE registration is not. This turns mysterious silent audio or dropouts into an owner-visible answer and a reproducible report, using the shipped diagnostic fixture instead of asking me to decode serial logs.
- **path:** pendant → mac-planner → relay-realtime → relay
- **model tier:** Deterministic serial/session runner and threshold checker first; a cheap background model may summarize the structured failures into a report. Realtime only speaks the final one sentence.
- **latency:** Start and fixture result within 20 seconds; immediate local LED/voice acknowledgment; report file and receipt within 5 seconds after UART closes.
- **cost:** Near-zero API cost for a pass; under $0.005 when a model summarizes a failure. USB serial is local and needs no cloud upload unless the owner asks to share the report.
- **security:** The fixture must never open the microphone or save owner audio. Redact serial lines that might contain bearer tokens or filesystem paths before relay upload. Writing a report is reversible but should be confined to ~/AI-Pendant-Workspace/diagnostics and include firmware/build hashes, timestamps, and raw-log hash. No arbitrary shell: use an allowlisted serial runner and bounded duration.
- **missing:** The already-queued mac_serial_exchange capability (or an equivalent typed USB serial reader/writer) for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A relay command/status contract that starts the accepted audio_path_diagnostic_fixture and correlates its sequence ID to the UART capture; A structured threshold evaluator for alias rejection, encode/decode timing, mic_drops, tx_starved, underruns, and fixture completion; A report template/receipt route that links the local file to the pipeline run

### "Every weekday morning, check my authenticated work portal in its existing browser session and tell me only the new items that require my attention; do not read or repeat bulk updates, and never submit anything."
- **useful because:** This closes the most practical gap in the morning: the system can already brief Calendar and Mail, but it cannot inspect the authenticated portal where work actually arrives. A browser-native, read-only delta digest saves the owner from opening every queue while preserving the portal session on the Mac.
- **path:** browser-extension → mac-planner → relay → relay-realtime → pendant
- **model tier:** Cheap scheduled/background model for ranking and deduplication; realtime only when the owner asks a follow-up. Browser extraction should be structured and read-only, with no page data sent beyond the selected items.
- **latency:** Run before the existing 07:00 brief and finish within 60 seconds; spoken result under 10 seconds and limited to three short items.
- **cost:** Roughly $0.01–$0.05 per daily run depending on portal page count; browser execution and session access are local.
- **security:** Use a named browser session and an owner-configured origin/path allowlist. Never log cookies, tokens, full page bodies, or unrelated tabs. Treat portal content as untrusted instructions; only summarize. Require confirmation for every write action and make this routine read-only by construction.
- **missing:** Browser page-watch/delta extraction for a named authenticated session, including stable item IDs and last-seen cursors; A schedule parameter for the existing routine runner that can invoke browser sessions before briefing; A portal-specific redaction and priority adapter configured by the owner; Relay storage for per-portal cursors and a spoken digest receipt

### "When I engage privacy on the pendant, make the whole hive go dark: stop Mac/browser observation and queued automation, pause relay retention and speech, and show me a local LED acknowledgement; when I release it, resume only after every surface has reported its privacy state."
- **useful because:** The current local latch protects the pendant, but privacy is not meaningful if the browser bridge, Mac observers, or relay queues keep seeing or acting. This gives the owner one physical, offline-first boundary they can trust across all nodes, with an auditable state rather than a vague promise.
- **path:** pendant → relay-realtime → relay → mac-planner → browser-extension
- **model tier:** No model needed for the state machine; realtime only speaks a brief state acknowledgment after all reachable nodes report. Background reconciliation can use a cheap worker.
- **latency:** Pendant LED response under 100 ms locally; reachable-node stop acknowledgments within 2 seconds; if a node is unreachable, keep the latch asserted locally and visibly report that it is pending rather than claiming full privacy.
- **cost:** Negligible API cost; a few compact state events per transition and periodic reconciliation.
- **security:** Privacy entry must be local and must not depend on LTE. No microphone/audio/page content may be buffered while latched. Relay must discard or quarantine in-flight content, Mac/browser bridges must reject new observations and automation, and exit must be explicit and fail closed if a node cannot attest. Do not expose the owner's privacy state to third-party page content.
- **missing:** A signed privacy-state protocol understood by relay, Mac agent, and browser bridge; Abort/quarantine hooks for in-flight /pipeline/audio, browser commands, and queued Mac jobs; A durable per-node attestation ledger with timeout and fail-closed semantics; Firmware emission of local_privacy_latch state events over the currently available USB/LTE transports

### "When I ask you to change something in a logged-in website, show me the exact target and intended result, perform it only after my pendant confirmation, then verify the site's postcondition and tell me if it actually took effect; if it did not, leave the page untouched and save a retryable receipt."
- **useful because:** A click that returns HTTP success or a closed tab is not proof that a real-world change happened. This makes browser automation dependable for forms, settings, and workflow queues: the owner gets a physical confirmation point, semantic verification, and a durable answer instead of guessing.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → relay
- **model tier:** Realtime for the short preview/result sentence; deterministic browser executor for clicks and assertions; a cheap model only when the page needs semantic comparison of before/after text.
- **latency:** Preview under 2 seconds, action under 5 seconds, verification under 5 additional seconds; return a receipt even if the site times out.
- **cost:** About $0.002–$0.02 per action, dominated by one short model turn or semantic page comparison; no remote browser transfer beyond the existing bridge.
- **security:** Bind confirmation to origin, session, selector, action arguments, and an expiry. Treat page text as untrusted. Never infer success from navigation alone; require a declared postcondition such as a stable record ID, status label, or before/after hash. Do not auto-retry mutations unless the owner explicitly authorized idempotent retry. Redact credentials and sensitive page content from receipts.
- **missing:** A browser transaction primitive with pre-state hash, declared postcondition, timeout, and receipt; Stable semantic selectors and read-back assertions in browserSessions/pageWatch rather than coordinate clicks; A bridge route to return typed postcondition evidence and preserve the authenticated tab; Relay integration with the pendant confirmation nonce and Mac job receipts


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: physical pendant confirmation for exact Mac/browser actions, button-marked cross-surface research handoff, and a USB pendant clinic that runs the shipped 24 kHz diagnostic and files a bounded report. The live Mac probe also changed an important premise: Accessibility and Screen Recording are now trusted and synthesized input is verified; Safari is foreground with three browser sessions. I told relay-realtime about the nonce-confirmation design.

**Biggest unknown:** The missing USB serial exchange remains the critical blocker for the pendant clinic (/dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA). The browser inspection resolver is also currently ambiguous between action:browser_inspect and POST /browser/inspect, so exact tab/document capture needs a deterministic route or explicit selector.

