# Harness derivation — relay-realtime — round 163

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "While I’m away from my Mac, check a site I’m logged into and tell me what changed."
- **useful because:** It turns the pendant into a real remote assistant for authenticated workflows, not just public web search.
- **path:** relay-realtime → browser-extension → mac-planner → faculty-perception → faculty-action
- **model tier:** Cheaper planner tier for multi-step browsing; only escalate to realtime for clarifications.
- **latency:** A few seconds to a minute depending on login state and page load; owner isn’t waiting in a chat loop.
- **cost:** Moderate; browser automation and page reads dominate, plus any summarization.
- **security:** Authenticated pages can contain sensitive data. Restrict to user-specified domains and avoid exfiltrating raw content; summarize with minimal retention.
- **missing:** A server-side browser is absent; must rely on the owner’s Mac being online; A robust session/watch mechanism for change detection and diffs; A safe way to store watch configuration and minimal diffs

### "If the pendant is connected over USB, use it as a direct bridge to run a quick diagnostic and report what’s wrong."
- **useful because:** This is a practical, testable today feature: when LTE isn’t registered, USB is the reliable path. It helps the owner debug hardware and link issues fast.
- **path:** relay-realtime → mac-planner → mac-terminal → pendant → bridge
- **model tier:** Realtime to guide and interpret; Mac tier to run the diagnostic and parse results.
- **latency:** 1–5 seconds for command dispatch; longer for deeper tests.
- **cost:** Low; a small number of serial commands and logs dominate.
- **security:** Diagnostics can expose device identifiers and firmware details; keep output minimal and avoid writing secrets to logs.
- **missing:** A defined packet transport over USB serial between Mac and pendant; A relay-visible receipt/subscription for diagnostic results; Standard diagnostic command set and parsers

### "“Use my pendant as the physical key for this—approve the waiting Mac or browser action, but don't make me type a password.”"
- **useful because:** The pendant is already on the owner's body and physically tethered by USB today. A deliberate button press can prove physical presence to the relay while the Mac planner or authenticated Safari performs the requested operation. This gives the owner a fast, device-bound way to approve sign-in, payment, publishing, or release actions without exposing credentials to speech or requiring them to return to the keyboard.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Realtime relay interprets the spoken request; mac-planner executes the concrete action; browser-extension supplies the authenticated tab/session. No expensive model is needed for the cryptographic handshake.
- **latency:** Under 1 second from button press to signed approval while USB-tethered; under 3 seconds over LTE/WebSocket. Execution itself remains asynchronous and reports a receipt.
- **cost:** Under $0.01 per invocation; dominated by one short realtime turn, not the physical-key operation.
- **security:** The button press must be a nonce-bound, one-shot challenge response tied to the exact action digest, device identity, and short expiry; never treat an old press as approval and never send passwords or raw private keys through the relay. The owner should explicitly say what is being approved so speech cannot silently broaden scope.
- **missing:** Signed challenge-response firmware primitive on the nRF9160; Relay endpoint that creates and verifies action-bound challenges; Mac/browser executor integration that pauses at an approval point and resumes only after verified pendant proof; USB serial transport registration and pairing for the currently connected pendant

### "“I’m back—put me exactly where I left off, and tell me the one thing I was trying to do.”"
- **useful because:** Today the wearable conversation, Mac actions, and authenticated browser tabs are separate episodes. This would make interruption survivable: the relay reconstructs the owner's last active intent from the voice turn, Mac action receipt, open windows, and browser tab/session state, then restores only the relevant workspace and speaks a one-sentence resumption cue. It is useful when the owner leaves the desk, loses connectivity, or is interrupted mid-task—not merely a completion notification.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** A cheap background summarizer maintains a compact task checkpoint; realtime only resolves the owner's short “where was I?” utterance. mac-planner restores the selected app/window/tab set, while browser-extension verifies authenticated tab identity before touching it.
- **latency:** Speak the recovered intent within 2 seconds; restore a small workspace within 8 seconds. If state is ambiguous, report the ambiguity instead of guessing.
- **cost:** About $0.005–$0.02 per resume, dominated by summarizing a checkpoint; restoration uses existing action execution.
- **security:** Checkpoints may contain private titles, URLs, or draft text, so encrypt them and retain only the latest few per task. Never reopen a sensitive tab based solely on a stale checkpoint; require live tab/session verification and make restoration undoable.
- **missing:** A durable cross-surface task-checkpoint record linking voice session, plan/job, Mac window snapshot, and browser tab IDs; Mac endpoint to snapshot and restore a narrowly scoped workspace without disturbing unrelated work; Relay reconciliation that marks checkpoints stale after tab closure, logout, or conflicting newer actions

### "“Before you send it, check that the file on my Mac and the version in the signed-in browser agree, and tell me exactly what differs.”"
- **useful because:** The system can currently act through either the Mac or an authenticated browser, but it cannot establish that two independently reachable sources refer to the same current artifact. This capability prevents the especially costly failure of sending an old local draft, wrong attachment, or stale portal value. It returns a compact, cited diff and can proceed with the owner's stated action after reporting discrepancies; it is a truth check, not a generic approval gate.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** faculty-perception extracts structured facts from the local file and live browser page; faculty-judgement aligns versions and explains conflicts; relay-realtime only narrates the result. Use a cheaper background model for large document diffs.
- **latency:** Under 5 seconds for metadata and short text; up to 20 seconds for two long documents, with progressive spoken status.
- **cost:** Roughly $0.01–$0.08 depending on document size; browser and Mac reads dominate token volume, so transmit hashes/structured fields before full text.
- **security:** Read only the explicitly named local path and active authenticated tab; redact secrets from model context where possible. A mismatch must never be silently resolved by choosing the newer-looking source. Preserve source citations and hashes in the action receipt so the owner can audit what was compared.
- **missing:** A common typed-artifact extraction schema for Mac files and browser pages (identity, version, timestamp, fields, hash); A relay-side comparison job that can request both reads in parallel and retain source citations; Mac read-file/document extraction action and browser extraction of the corresponding structured fields; An execution precondition hook that reruns the comparison immediately before sending


## Changes it proposed to its own stack

### `relay` — Expose a relay capability manifest route (e.g., GET /v1/capabilities) and a durable subscription endpoint for device/job events.
- **owner gets:** The relay can finally be introspected and reliably wired up, which reduces invisible failures and makes features like delivery receipts and notifications actually dependable.
- effort: Medium; a new route plus a durable object or queue subscription path.  ·  risk: Incorrect capability reporting could mislead routing; mitigate with strict versioning and integration tests.
- cost: Low ongoing cost; a small manifest payload and occasional subscription traffic.  ·  latency: Minimal; manifest is fetched infrequently.
- security: Manifest must not leak secrets; event subscriptions must be authenticated and scoped.
- depends on: Durable job runner or event source for job/device updates

### `integration` — Define a USB serial transport contract for pendant <-> Mac bridge: frame format, message types (diagnostic, audio control, health), and receipt semantics.
- **owner gets:** Makes the tethered mode predictable and debuggable today, even without LTE registration.
- effort: Medium to high; requires firmware and Mac harness changes plus test fixtures.  ·  risk: Protocol mismatch could lock up the bridge; mitigate with version negotiation and safe fallbacks.
- cost: Low; mostly engineering time.  ·  latency: Improves; fewer retries and clearer errors.
- security: Must authenticate or at least validate message origins and avoid executing arbitrary commands.
- depends on: Agreement between firmware and mac-harness on protocol versioning

### `model-routing` — Add a cheap background planner tier for long-running monitoring, with a strict handoff from realtime after acknowledgement.
- **owner gets:** Keeps voice interactions snappy while still handling work that takes minutes or hours.
- effort: Medium; requires job state machine and model selection logic.  ·  risk: Handoff failures could drop tasks; mitigate with receipts and retries.
- cost: Reduces cost by moving work off the expensive realtime tier.  ·  latency: Improves perceived latency in voice sessions.
- security: Background tier must respect the same data minimization and access controls as foreground.

### `relay` — Add a cross-surface provenance graph, not another receipt: every plan, Mac read/action, browser inspection, model claim, and resulting mutation gets a parent/child edge with source hash, tab/window identity, timestamp, and freshness expiry. The relay exposes a single “explain this action/answer” lookup and the executor can revalidate expired evidence before continuing.
- **owner gets:** When the owner asks “why did you send that?” or “which version did you use?”, the pendant can answer with the exact browser page, local file, and intermediate decision rather than a vague success message. It also lets the system detect that an otherwise valid plan is now based on stale evidence.
- effort: Medium-high: shared event schema and persistence in the Worker, adapters in Mac planner and browser bridge, plus a compact spoken explanation formatter.  ·  risk: Graph growth and partial writes could produce misleading explanations. Use immutable append records, bounded retention, explicit unknown edges, and never claim provenance when an adapter failed to report it. Recover by falling back to the existing action receipt.
- cost: Low storage and API overhead; roughly 1–3 KB of metadata per action, with no extra model call unless the owner asks for an explanation.  ·  latency: Adds under 100 ms to ordinary action submission if edges are batched; explanation may take 1–3 seconds to summarize.
- security: Provenance itself contains sensitive URLs, filenames, and snippets. Encrypt at rest, scope queries to the owner/device, redact content while retaining hashes, and expire raw evidence sooner than metadata.
- depends on: A durable relay event store that accepts correlated plan/execute/browser events; A shared correlation ID propagated by POST /plan, POST /execute, browser inspection, and GET /jobs/:jobId; Mac and browser adapters emitting typed evidence rather than only final success text


## What it asked for

_Nothing._
