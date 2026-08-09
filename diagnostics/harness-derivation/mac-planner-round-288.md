# Harness derivation — mac-planner — round 288

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before I stop for the night, make this project handoff-ready: collect only the files changed since the last handoff, the active browser work, unfinished Mac jobs, and my pendant bookmarks; write a deterministic handoff package and give me the one next action when I resume."
- **useful because:** The owner loses less work across sleep, crashes, and switching machines. This is not a generic backup: it connects the worn device's human markers to the exact desktop/browser artifacts and unfinished job receipts, so a future agent can continue rather than merely summarize.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Cheap background model for deduplication and one-sentence next-action selection; deterministic file hashing, job receipts, browser metadata, and bookmark ordering remain non-LLM.
- **latency:** Preview in under 5 seconds; atomically stage the package in under 30 seconds; resume lookup under 2 seconds.
- **cost:** Typically <$0.02 for deduplication/next-action wording; file hashing and staging dominate. No file contents leave the Mac unless the owner explicitly chooses remote handoff.
- **security:** Default to metadata and hashes, not file contents; allow per-project inclusion rules and redact browser URLs containing tokens. Staging must be atomic and idempotent, with a receipt and rollback of partial output. Resuming a job must never silently repeat a non-idempotent Mac action.
- **missing:** A project-scoped handoff coordinator that joins bookmark events, browser session metadata, and Mac job receipts; A changed-since-handoff index (content hashes plus last successful receipt); A resume planner that consumes the handoff without replaying completed actions

### "When something I asked the pendant to do fails, let me say “show me what went wrong” and get one chronological incident replay: my request, the relay decision, browser or Mac actions, receipts, and pendant link/audio status, with the first failed boundary and a retry that will not duplicate completed work."
- **useful because:** Today each surface has its own logs, so a failure looks like silence or a vague job status. A causal replay would make the system debuggable by the owner and would prevent retrying a purchase, message, or file mutation that already succeeded before the report was lost.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic correlation and idempotency checks first; cheap model to explain the timeline; realtime tier only if the owner asks by voice during an active call.
- **latency:** Surface a failure marker to the pendant within 2 seconds; assemble the replay in under 5 seconds; retry only after the completed-prefix is verified.
- **cost:** Usually <$0.01 for explanation; log correlation and receipt reads dominate. Keep raw audio and page contents out of the replay by default.
- **security:** Redact message bodies, URLs with credentials, and audio. Correlation IDs must be opaque and scoped to the owner. Never infer success from a missing receipt; require an explicit receipt or mark the step unknown. Retries must use job/workbench idempotency keys and show the exact remaining actions.
- **missing:** A cross-surface correlation ID carried from relay intent through Mac and browser commands into pendant QoS; A normalized event timeline schema with explicit succeeded/failed/unknown states; A retry planner that reuses completed-prefix receipts rather than replaying the original plan

### "At any time, let me ask “what did the pendant system share today?” and receive a privacy ledger showing which audio, screen excerpts, files, browser metadata, and action receipts left the Mac or pendant, what was redacted or withheld, and a one-tap command to revoke or delete each retained item."
- **useful because:** The system spans a microphone device, a browser with authenticated sessions, and a Mac with broad automation. An owner-readable data-egress ledger is the only way to know what actually crossed those boundaries, rather than trusting configuration or a vague privacy promise.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic event aggregation and redaction accounting; no expensive model except optional plain-language summarization.
- **latency:** Answer a same-day query in under 3 seconds; deletion/revocation receipts within 5 seconds per item.
- **cost:** Near-zero model cost; bounded ledger storage and aggregation are the main cost. Store hashes and categories by default, not raw content.
- **security:** The ledger itself is sensitive and must be owner-authenticated, encrypted, and redacted. It must distinguish attempted, transmitted, retained, and deleted data, including failed uploads and browser page snippets. Deletion should be best-effort with an explicit residual-retention statement; never claim remote erasure without a relay receipt.
- **missing:** A common egress event schema emitted by Mac, browser bridge, relay, and pendant; Relay-side retention/deletion receipts addressable by event ID; Mac-side accounting for screen capture, file reads, browser snippets, and audio pipeline payloads

### "Let me grant a temporary, spoken capability lease across the pendant, Mac, and browser—such as “for the next hour, let this shopping site search and fill forms, but never submit or send”—and have every node enforce the same scope, expiry, and revoke command."
- **useful because:** The owner currently has to choose between broad automation and not using automation, while the browser, Mac, relay, and pendant do not share one live authorization state. A time-bounded lease would make ambitious assistance safe enough to use in real life without turning permanent permissions into the product.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic policy matching, expiry, and enforcement; a cheap model may translate the owner's spoken scope into a proposed lease, but it must never broaden it. Realtime is only for the spoken grant/revoke exchange.
- **latency:** Speak back the exact lease scope in under 2 seconds, propagate it to all online nodes within 1 second, and revoke locally immediately on the pendant or Mac.
- **cost:** Less than $0.01 per lease for parsing and receipt generation; the dominant cost is implementation and durable policy storage, not inference.
- **security:** Default deny when a node is offline or the lease is ambiguous. Bind leases to exact domains, apps, action classes, and expiry timestamps; prohibit secret extraction and irreversible actions unless separately named. The pendant must show a distinct local state, and every use must produce a receipt. Revoke must work offline and invalidate queued work when the link returns.
- **missing:** A shared lease token and versioned policy format understood by relay, Mac action execution, and browser commands; Enforcement hooks in FULL_CONTROL_MODE and the browser bridge rather than advisory logging; A local pendant lease/revoke state that survives link loss and a dashboard showing active leases and uses; A deterministic spoken-scope parser with preview and conflict handling

### "Give me one emergency stop for the whole hive: a local pendant action or spoken command that immediately halts Mac and browser automation, cancels queued relay work, and returns a signed list of what was stopped, what had already completed, and what still needs manual inspection."
- **useful because:** The current privacy latch protects microphone and playback, but it does not stop a browser command, Mac job, or already-queued relay plan. When an automation starts doing the wrong thing, the owner needs a physical, network-independent brake and a truthful boundary report—not a hope that the current step finishes safely.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No LLM for the stop path; use a signed control frame, cancellation tokens, and deterministic receipts. Use a cheap model only to explain the resulting boundary report.
- **latency:** Pendant-local stop indication under 100 ms; online cancellation propagation under 1 second; final boundary report under 5 seconds. Offline nodes must stop their own queued work immediately and reconcile later.
- **cost:** Negligible inference cost; engineering work is in cancellation propagation and durable receipts.
- **security:** The stop control must be authenticated, replay-resistant, and executable without network access. Cancellation cannot pretend to undo irreversible actions; classify each in-flight step as stopped, completed, or unknown. Clear only after the owner explicitly resumes, and preserve forensic receipts without retaining private payloads.
- **missing:** A cross-node cancellation token carried through relay jobs, Mac plans, and browser commands; Cooperative cancellation points in Mac FULL_CONTROL actions and browser extension execution; Pendant firmware handling for an offline emergency-stop state (distinct from privacy mute); A signed boundary receipt and explicit resume protocol

### "Before I let the hive act, let me say “show me exactly what you would do,” and receive a synchronized dry run across the relay, Mac, and authenticated browser: the exact URLs, files, UI targets, messages, and pendant effects, plus the state assumptions that would make the plan stale; then execute that same immutable plan if I choose."
- **useful because:** A Mac-only preview cannot reveal that a browser tab changed, a relay intent was reinterpreted, or a pendant delivery will be queued. The owner needs one human-readable and machine-replayable preview of the entire cross-node plan, not separate previews that can drift between approval and execution.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic plan compilation, state snapshots, hashes, and diffing; cheap model only to summarize the preview. Realtime is not needed unless the owner requests it by voice.
- **latency:** Preview in under 4 seconds for ordinary plans; execution must begin from the preview hash or refuse as stale; stale detection under 500 ms.
- **cost:** Usually <$0.01 for summarization; browser/Mac snapshots and state hashing dominate.
- **security:** Redact secrets and page bodies while preserving enough structure to identify targets. Treat preview as non-mutating and bind approval to an immutable hash, scope, expiry, and owner session. Never silently refresh a stale preview into a new action.
- **missing:** A relay-level immutable plan object that contains Mac, browser, and pendant steps; Browser dry-run introspection for target state and side-effect classification; Snapshot hashes and optimistic-concurrency checks across all nodes; A single preview receipt and execution endpoint that refuses plan drift


## What it asked for

_Nothing._
## Its own summary

Discovered the live Mac is ready: Accessibility and Screen Recording are granted, browser bridge is online with YouTube active, relay and Mac bridge are reachable, and the pendant remains offline despite USB bench hardware being physically present. Three new cross-surface capabilities were recorded: project handoff packages, causal incident replay with safe retry, and an owner-readable data-egress/privacy ledger. Two tempting ideas (bookmark-to-return anchor and spoken audio health check) were rejected as duplicates of existing backlog/accepted work, so I did not rephrase them. What I still need is implementation support for correlation IDs and normalized event/egress schemas across relay, browser, Mac receipts, and pendant telemetry; semantic document/window identity remains unavailable, and the pending serial bench runner is still missing.

**Biggest unknown:** Whether the existing relay, browser, and pendant event stores already expose stable IDs and retention/deletion receipts that can be joined, or whether a new cross-node event envelope must be added first.

