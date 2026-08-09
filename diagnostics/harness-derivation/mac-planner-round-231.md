# Harness derivation — mac-planner — round 231

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I engage the pendant's privacy latch, immediately make every connected surface safe: stop Mac capture/playback, hide or replace sensitive browser tabs, and show me a local confirmation; when I release it, restore only what was active before and give me a receipt."
- **useful because:** The pendant is the one control the owner can reach without looking at the computer. Propagating its local privacy state prevents a browser session or Mac audio/UI from undermining the latch, especially during an unexpected interruption.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic state machine; no LLM required. Use the realtime model only if the owner asks for a spoken explanation.
- **latency:** Local mute immediately; relay fan-out and Mac/browser actions target under 500 ms, with a visible pending/error state if a surface does not acknowledge within 2 seconds.
- **cost:** Near-zero API cost; event fan-out and receipts dominate. Optional notification text is a few cents per thousand transitions.
- **security:** Privacy mode must fail closed locally and must not wait on the network to mute. Browser redaction must avoid destroying tabs or submitting forms; save a signed pre-latch surface manifest and restore only that manifest. Never transmit page contents, microphone buffers or credentials. Exit is local, while remote surfaces report whether they were restored.
- **missing:** Relay fan-out protocol carrying local_privacy_latch enter/exit with monotonic sequence numbers; Mac action handlers for stop capture/mute and reversible window redaction; Browser extension commands to replace sensitive content with a neutral page and later restore a tab manifest; A durable, encrypted pre-latch surface manifest with expiry

### "Give me a one-button “continue this later” handoff: capture the pendant bookmark, the active Safari tab and Mac app, package the relevant files and receipts atomically, and let me resume the same task from the pendant or another machine without repeating completed steps."
- **useful because:** Interruptions are normal. The owner gets a durable continuation point rather than a vague note, duplicate actions, or losing the browser session context that only this Mac can access.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model to produce a short task summary from metadata and receipts; deterministic transaction logic for files, deduplication and resume.
- **latency:** Create a local checkpoint in under 3 seconds; background summary and cross-machine handoff within 10 seconds. Resume must show exact completed and pending steps before acting.
- **cost:** Usually <$0.01 per checkpoint; storage and browser inspection dominate, not inference.
- **security:** Authenticated browser content and local files must stay on the Mac unless explicitly exported. Store hashes and redacted metadata by default, not raw page text. Resume must be idempotent, refuse stale credentials, and expose a precise receipt before any mutation.
- **missing:** A real JSON-schema resume/checkpoint API (the existing mac_resume_capsule request was prose-schema and unresolved); A relay-to-Mac handoff that snapshots browser session identity without copying secrets; A transaction adapter that maps POST /workbench/contexts and mac_workbench_transaction receipts to resumable step IDs; Owner-configurable export policy for files and authenticated-page metadata

### "When I say “do the thing I’m looking at,” have the pendant, relay, Safari and Mac agent complete the smallest safe action on the current page, then read back a tamper-evident proof of what changed—page identity, action, result, and timestamp—without sending me a vague success message."
- **useful because:** Authenticated browser actions are the system's unique reach, but a voice confirmation alone is not trustworthy after a dropped connection or a dynamic-page race. A signed, cross-surface proof lets the owner know whether the intended page was acted on and prevents silent duplicate submissions.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime model parses the short spoken intent; deterministic browser target validation, action execution, idempotency keying and receipt generation do the safety-critical work. A cheap background model may summarize the receipt.
- **latency:** Validate page identity and announce the planned action within 1 second; execute and produce a receipt within 5 seconds. If the browser or relay disconnects, show pending rather than retrying blindly.
- **cost:** <$0.02 per action; most cost is one realtime turn and optional receipt summarization, not browser transport.
- **security:** Never infer a target from stale tab text. Bind each action to tab/session ID, canonical URL, page title hash, and a short-lived nonce; reject navigation or DOM identity changes. Do not expose cookies, tokens, full page bodies, or private message content to the relay. Treat sends, purchases, deletes and permission changes as explicit owner-confirmed classes configured by policy; all other actions still get a durable receipt and idempotency key.
- **missing:** A browser command contract that returns precondition identity, idempotency key, postcondition evidence and a durable receipt rather than only command success; Relay support for correlating pendant utterance, browser command, Mac job and result across reconnects; A deterministic page-target verifier in the browser extension for URL/title/DOM anchor hashes; Owner-configurable action classes and a receipt viewer on the dashboard/pendant inbox

### "Let me ask the pendant “what private data left my Mac today?” and get a trustworthy, source-by-source report of what the relay, browser extension, and models received, with controls to revoke future sharing or erase retained copies."
- **useful because:** Today the system can act across authenticated browser sessions and local apps, but the owner cannot independently audit the boundary between private Mac/browser data and cloud processing. A spoken, inspectable data-flow ledger makes the whole hive governable rather than merely powerful.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic collection and redaction accounting; a cheap background model may summarize the ledger. Realtime is needed only for the owner's conversational query.
- **latency:** Return a bounded day-level summary in under 3 seconds; detailed source expansion within 10 seconds. Revocation should take effect before the next capture or browser command, even if the relay is temporarily unreachable.
- **cost:** Usually under $0.01 per query; the dominant cost is durable event accounting and encrypted local storage, not inference.
- **security:** The ledger itself can reveal sensitive URLs, recipients, and topics, so keep raw records on the Mac and expose redacted aggregates by default. Use cryptographic event hashes and monotonic timestamps so the report cannot silently omit transfers. Revocation must stop future collection locally; deletion requests must distinguish local data, relay data, and third-party model retention and report what cannot be recalled.
- **missing:** A Mac-local egress ledger covering relay payloads, browser command/result payloads, screenshots, audio, and model calls; Relay and browser-extension receipt hooks that record schema-level data categories and retention deadlines without copying content into the ledger; A revocation/forget protocol propagated from pendant to Mac, relay, and extension, with honest per-surface completion status; A dashboard and pendant query surface for redacted data-flow reports

### "When something goes wrong—lost audio, a failed browser action, a Mac job that stopped, or a relay reconnect—let me ask the pendant “why did that fail?” and get a causal timeline with the exact boundary where it broke and the safest recovery, without exposing raw private content."
- **useful because:** The system spans several failure-prone links, but today an owner sees disconnected symptoms and has to reconstruct them manually. A privacy-preserving causal trace would turn failures into recoverable events instead of silent lost work.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic event correlation and health counters first; a cheaper background model produces the explanation. Realtime only delivers the short spoken answer.
- **latency:** Capture failure evidence immediately; produce a concise diagnosis within 5 seconds of the query and a deeper report within 30 seconds.
- **cost:** Under $0.02 per diagnosis; event storage and correlation dominate, with model use limited to summarization.
- **security:** Store hashes, error classes, timing, and redacted identifiers by default—not page bodies, audio, credentials, or file contents. Ensure traces cannot be rewritten after the fact. Recovery suggestions must be separated from automatic execution and must never replay a non-idempotent action solely because it previously failed.
- **missing:** A shared monotonic event envelope across pendant audio/QoS, relay jobs, Mac receipts, and browser commands; Failure hooks that preserve precondition, transport, timeout, and postcondition state at every boundary; A causal-correlation service with retention and redaction controls; A spoken diagnosis and dashboard timeline view

### "Let me designate a trusted person and say “hand this off” from the pendant: package only the selected task, ask that person through an authenticated channel, show me exactly what will be shared, and let them complete it without giving them my Mac, browser cookies, or unrelated files."
- **useful because:** The owner often needs another human to finish a task, but the current hive is optimized for the owner and cannot safely delegate a bounded piece of work across its authenticated surfaces. This creates a human-in-the-loop escape hatch without exporting the owner's whole digital workspace.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic package construction, capability scoping, recipient authentication, and audit receipts; background model may draft a concise handoff. Realtime only handles the spoken request.
- **latency:** Show the proposed share manifest within 3 seconds; recipient delivery within 10 seconds; every recipient action returns a receipt asynchronously.
- **cost:** A few cents per handoff for encrypted storage, notification delivery, and optional summarization; no continuous model cost.
- **security:** Use end-to-end encryption and recipient-bound keys. Never share browser cookies, session tokens, raw mailbox contents, or unrelated filesystem paths. The owner must see and approve the exact manifest, expiry, recipient, and allowed operations. Recipient access must be revocable, time-limited, and fully audited; the Mac remains the execution boundary for any local action.
- **missing:** A relay-mediated delegation protocol with recipient identity, capability scopes, expiry, and revocation; A Mac export broker that materializes only an approved manifest into an isolated handoff bundle; A browser redaction/export layer that can provide page evidence without session credentials; Recipient authentication, notification delivery, and a two-sided receipt ledger


## What it asked for

_Nothing._
