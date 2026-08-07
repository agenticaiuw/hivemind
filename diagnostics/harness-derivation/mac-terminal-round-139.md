# Harness derivation — mac-terminal — round 139

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Start this from my pendant and keep it alive across the Mac, Safari, and relay—even if I walk away or the USB link drops; tell me only when it needs me or is truly finished.”"
- **useful because:** This is the single most useful cross-node behavior: a spoken/button goal becomes a durable, resumable run. The pendant supplies intent and attention; Mac shell and Safari perform private work; relay persists the run and later delivers a short spoken/haptic outcome. Today the Mac and Safari are online, receipts exist, and the pendant/bridge are physically USB-attached, but there is no truthful end-to-end continuity when the owner leaves or the link disappears.
- **path:** pendant → mac-planner → browser-extension → mac-terminal → relay-realtime → unified
- **model tier:** background for decomposition, deterministic workers for typed Mac/browser steps, realtime only for the initial spoken request and urgent interruption
- **latency:** Acknowledge locally in under 500 ms; durable handoff under 2 s; background steps may run for minutes; completion or blocked-state notification within 10 s of the event.
- **cost:** About one background/planner call per ambiguous goal plus cheap deterministic worker turns; the expensive part is only initial decomposition and exception recovery, not polling.
- **security:** Private Safari DOM, shell output, and audio status stay on the Mac/relay encrypted channel; never send raw page contents in a notification. Persist step-level redacted evidence and require explicit owner confirmation only at the already-defined irreversible browser boundary (not for normal reversible work).
- **missing:** A durable cross-surface run record with step dependencies, wake conditions, and resumable checkpoints; Mac USB serial ingress for pendant button/events and ESP32 playback egress; Relay event ingestion and reconnect/deduplication keyed by device event and run ID; A worker that can reattach Safari tab IDs and classify a run as waiting, blocked, failed, or done; Pendant notification policy for terse haptic/audio outcomes

### "“If something you ran on my Mac fails, figure out the cause, try the safest alternative automatically, and tell me in plain language what changed—don't make me repeat the whole task.”"
- **useful because:** Arbitrary FULL_CONTROL shell is intentionally trusted and unrestricted, but a failed command currently leaves the owner with a raw error and a manual restart. A recovery loop turns the existing power into a reliable assistant: preserve the failed argv, cwd, exit code, stderr, and partial effects; choose a known alternate (path discovery, tool substitution, retry after transient network/UI failure); then continue the browser or Mac plan without losing context.
- **path:** mac-terminal → mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** deterministic failure taxonomy and retry recipes first; background model for diagnosis and alternate-plan selection; realtime only to explain an unresolved blocker
- **latency:** Capture failure immediately; deterministic retry in 1–3 s; one background diagnosis under 10 s; never spin indefinitely—stop after two alternate plans and notify.
- **cost:** Most failures cost no model call; only unfamiliar stderr invokes a small background diagnosis. Receipts and stderr indexing are local storage costs, not token costs.
- **security:** Shell remains maximum-access and ungated per owner policy. Store command, cwd, environment names (not secret values), exit status, and redacted stderr; never upload credentials or full environment to relay. Automatic alternatives must be limited by an explicit plan budget and report irreversible side effects honestly.
- **missing:** Structured shell result fields (argv/command, cwd, exit code, stdout/stderr, duration, timeout) in the job receipt; Failure taxonomy and idempotency/side-effect hints for shell and AppleScript actions; A retry planner that can inspect prior receipts and revise only the failed suffix; Persistent local stderr snippets linked to the relay job and a user-visible recovery explanation

### "“I may have several things running. Decide which result deserves to interrupt me on the pendant, bundle the rest into one later digest, and let me ask ‘what did I miss?’ to hear the exact outcomes.”"
- **useful because:** Current jobs, browser commands, pipeline events, and receipts can all finish independently, but they have no shared attention policy. The owner should not receive five noisy completions or miss a blocked private-site task. Relay can rank urgency while the Mac contributes real evidence and the pendant provides the only attention channel; a spoken query can recover the full receipt trail on demand.
- **path:** relay-realtime → mac-planner → mac-terminal → browser-extension → pendant → unified
- **model tier:** deterministic ranking from job state, deadline, blocked/failed status, and owner quiet hours; background model only to summarize multiple receipts; realtime for the spoken ‘what did I miss?’ query
- **latency:** Rank each event under 100 ms; urgent blocked/failed alert under 2 s; digest generation under 5 s; spoken recall under 3 s.
- **cost:** Near-zero model cost for ranking; one background summary per digest window. Storage is a compact event index and redacted receipt references.
- **security:** Notifications reveal only minimal labels until the owner asks on the authenticated pendant channel. Do not speak page titles, shell output, or account data in public mode; retain source job IDs and let the owner expand privately. Quiet hours and urgency overrides must be explicit and auditable.
- **missing:** A shared attention inbox that deduplicates events from Mac jobs, browser commands, and relay pipeline; Priority policy using deadlines, blocked state, failure, reversibility, and user quiet hours; Pendant haptic/audio notification protocol with acknowledgement and replay cursor; A spoken query that resolves ‘what did I miss?’ to unread event IDs and their receipts; Cross-node event IDs and monotonic cursors so reconnects do not duplicate alerts

### "“When you act on my behalf, let me ask ‘why did you do that?’ and hear a compact, evidence-linked explanation of what I said, what each node observed, which alternatives you rejected, and exactly what changed.”"
- **useful because:** Today the owner can inspect individual Mac jobs and receipts, but cannot reconstruct the cross-node causal chain from pendant intent through relay routing, planner choice, Safari evidence, shell actions, and final outcome. A causal explanation would make this novel system understandable and correctable without forcing the owner to read logs or trust an opaque model. It is especially valuable when the result is surprising, incomplete, or wrong.
- **path:** pendant → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action → mac-planner → mac-terminal → browser-extension
- **model tier:** Deterministic event linking and redaction first; a cheap background model compresses the linked trace into spoken language; realtime is used only when the owner asks interactively.
- **latency:** Answer a why-question from already-linked events in under 3 seconds; build the causal record during execution with no more than 100 ms per event.
- **cost:** Low: event linking and hashes are local/relay work; one small background summarization call per explanation, with no planner call when a cached explanation exists.
- **security:** The explanation must not expose raw private page content, credentials, or unrestricted shell output. Store source references, snippets hashed or redacted, confidence, and sensitivity labels; expand sensitive evidence only over the authenticated owner channel. Preserve the distinction between observed facts, model inferences, and actions actually executed.
- **missing:** A durable causal-trace schema connecting one owner utterance to routing decisions, observations, plans, action receipts, retries, and outcomes across nodes; Typed provenance edges with source, timestamp, confidence, sensitivity, and model-vs-device attribution; A redaction-aware explanation compiler and spoken query resolver for ‘why’, ‘what did you see?’, and ‘what changed?’; A correction path that lets the owner mark an observation or inference wrong and propagates that correction to the active run without rewriting immutable history


## Changes it proposed to its own stack

### `mac-harness` — Replace the opaque run_shell receipt payload with a streaming, structured command envelope while keeping FULL_CONTROL_MODE and maximum access unchanged. Record command hash plus argv/string, resolved cwd, start/finish monotonic times, timeout flag, exit code, bounded stdout/stderr tails, signal, and a side-effect hint; emit redacted progress events to /thinking and /journal, and attach the envelope to the existing actionReceipt and undo records. Add a local command fingerprint catalog so repeated successful commands bypass planner interpretation and known transient failures can retry without a new expensive model call.
- **owner gets:** When a Mac task fails or runs long, the owner can hear exactly whether it is still running, timed out, or failed and why, and the agent can recover instead of asking them to repeat the request. It also makes the existing unrestricted shell trustworthy through observability rather than gates.
- effort: Medium: executor/computerControl result normalization, stream plumbing, redaction, receipt schema migration, and a small local fingerprint store; no hardware changes.  ·  risk: Command output may contain secrets and streams may be truncated; redact common credential patterns, cap bytes, and retain the full result only locally. Schema migration must tolerate old jobs; recover by treating old receipts as unstructured. Do not infer success from text when exit code is absent.
- cost: Negligible storage and CPU; lowers planner calls on repeated commands and therefore token spend.  ·  latency: Near-zero for short commands; streaming adds small I/O overhead and makes long commands visibly responsive.
- security: No new authority and no approval gate. Better auditability, but redaction must be tested against shell output and environment leakage.
- depends on: Existing actionReceipt/job journal schema; A bounded local event stream for /thinking and /journal; A deterministic command fingerprint/repair registry


## What it asked for

_Nothing._
## Its own summary

Round 139 produced three new cross-node capabilities and one implementation change. The highest-value proposal is durable pendant→Mac/Safari→relay continuity with reconnect-safe checkpoints and truthful blocked/done delivery. I also proposed automatic, bounded Mac-shell failure recovery and a shared attention inbox that ranks multiple completions so the pendant interrupts only when warranted. Live evidence: Mac agent and Safari extension are online, relay is reachable, FULL_CONTROL_MODE is on, receipts/journals exist, and recent jobs still identify browser reads as unlinked evidence. I additionally proposed structured shell telemetry, though the recorder flagged it as somewhat close to prior ledger work; the three capabilities remain the substantive output.

**Biggest unknown:** The exact USB serial protocol and firmware state for the physically attached nRF9160 pendant and ESP32 bridge remain unknown. Without that, I cannot specify the concrete event framing, reconnect semantics, or whether button/audio round-trips can be tested today. Also unknown is whether existing receipt/journal schemas can carry cross-node run IDs without migration.

