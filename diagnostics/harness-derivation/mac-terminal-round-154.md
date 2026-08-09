# Harness derivation — mac-terminal — round 154

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Keep my AI costs under $25 this month without me micromanaging it.”"
- **useful because:** The Mac currently reports routing with zero persisted usage (GET /routing), while authenticated Safari is live on the actual billing page showing a $10.63 balance and auto-reload enabled. A relay-resident budget governor would combine the real billing balance, model-routing telemetry, and scheduled/background work: use deterministic/local actions first, downgrade non-urgent work, pause queued background jobs near the owner's limit, and tell the pendant exactly what was deferred. This turns an invisible spend surprise into a controllable personal budget.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** background for periodic budget reconciliation and routine reprioritization; deterministic for thresholds and routing changes; realtime only when the owner asks or a hard budget event needs immediate speech.
- **latency:** Normal checks under 2 seconds from cached ledger; authenticated billing refresh may take 5–10 seconds; an urgent pendant alert should begin within 1 second of a threshold event.
- **cost:** Usually <$0.01/day: most decisions are arithmetic and cached reads. One small background model call only when classifying whether queued work is deferrable; browser page reads and Mac route reads dominate latency, not tokens.
- **security:** Billing balance, usage and monthly limits leave Safari only to the local agent/relay; never send payment methods or full billing DOM upstream. Budget policy must be explicit and reversible: pausing work is allowed, cancelling or changing auto-reload requires a separate owner request.
- **missing:** A durable usage ledger that records model/route, estimated tokens, actual provider cost when available, and routine/job attribution; A browser extraction recipe for the billing balance and reset period with sensitive payment fields excluded; A relay scheduler and policy evaluator that can pause/defer background jobs without touching interactive work; A model-router hook that accepts a remaining-budget/defer decision

### "“Turn what I just did into a button I can press next time.”"
- **useful because:** Today the system can execute Mac actions and authenticated Safari actions, but the owner cannot promote a successful multi-surface session into a reusable, inspectable routine. A recorder would collect the actual receipts, browser session/tab bindings, shell cwd, and the owner's final spoken description, replace volatile values with named inputs, test a dry run, then expose the result as a pendant-triggered routine. This is the difference between an assistant that performs a task once and one that compounds the owner's time.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** planner/background: one planning call when publishing the routine; deterministic replay thereafter. Realtime only handles the short capture/publish conversation.
- **latency:** Capture is passive. Publishing should take under 5 seconds after the owner says the name; replay starts within 2 seconds and reports each step's receipt.
- **cost:** Near zero for replay. One planner call (roughly 2–5k tokens) to parameterize and label a captured workflow; storage and browser/Mac calls dominate only for large receipts.
- **security:** Never store raw shell environment, credentials, page passwords, or unrestricted DOM in a routine. Persist redacted action templates and provenance. A routine containing send/delete/publish steps must remain explicitly marked as irreversible and require the existing owner confirmation semantics at invocation; replay must refuse if the tab origin or target fingerprint changed materially.
- **missing:** A capture session that groups POST /execute jobs across Mac and browser by a user turn and records the original intent before action rewriting; A template compiler that identifies volatile values (dates, paths, tab IDs, recipients) and produces typed parameters; A routine version/rollback store with dry-run and per-step provenance; A pendant trigger mapping and a dashboard editor for parameters and dangerous steps

### "“That failed while I was away — tell me why, and retry it safely if the world is still the same.”"
- **useful because:** The live Mac agent currently flattens shell failures (losing exit code), cannot interrupt a running shell, has no automatic retry, leaves ledgers open, and leaves jobs stuck as processing after a restart. A failure-rescue capability would give the owner a truthful answer instead of “failed,” then retry only the failed step after checking cwd/project branch, browser tab/session fingerprint, network reachability, and whether any earlier step already succeeded. The pendant can deliver the concise result while the relay preserves the full diagnostic bundle.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic for process status, exit code, precondition comparison, retry budget, and idempotency; background model only to summarize stderr and propose a repair; realtime only for the owner's spoken question.
- **latency:** Status and precondition check under 1 second; safe retry begins within 2 seconds; diagnostic summary under 5 seconds, with long-running commands streamed asynchronously.
- **cost:** <$0.01 for deterministic recovery; at most one small background summarization call (1–2k tokens) for unfamiliar stderr. No realtime model needed unless the owner is actively speaking.
- **security:** The diagnostic bundle must redact inherited secrets and never upload raw environment or full command output by default. A retry needs an explicit idempotency key and records whether the failed step may have partially mutated state; browser retries must require the same origin/tab generation and Mac retries the same project fingerprint. Never claim success from a stale receipt.
- **missing:** Spawn run_shell with argv/exitCode/pid/signal and a real abort signal, while retaining the original submitted action before rewrites; Boot-time reconciliation that closes interrupted ledgers and joins ledgerId to jobId; A retry coordinator that classifies retryable failures, applies bounded backoff, and resumes only unsettled steps; Cross-surface precondition fingerprints for cwd/git state and Safari tab/session generation; A redacted failure-diagnostic endpoint and pendant/relay notification payload

### "“Package this task so another agent can finish it tomorrow without asking me the same questions.”"
- **useful because:** Today work is split across Mac jobs, authenticated Safari tabs, relay state, and spoken context, but there is no owner-visible delegation contract. This would capture the goal, acceptance tests, unresolved questions, exact browser session/tab provenance, project/cwd state, artifacts already produced, deadline, and a bounded next-step plan. Tomorrow’s agent can continue from evidence rather than hallucinating what “that thing” meant, and the pendant can announce only blockers that truly require the owner.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for assembling and compressing the handoff; deterministic for collecting receipts, session IDs, paths, timestamps, and acceptance checks; realtime only to ask one concise clarification before sealing it.
- **latency:** Seal in under 5 seconds for a completed job; a live handoff may continue asynchronously and notify the pendant when a blocker or completion appears.
- **cost:** Usually <$0.01: receipts and browser evidence are already structured. One background summarization call (2–4k tokens) only when the owner asks for a human-readable brief.
- **security:** Redact inherited shell environment, credentials, payment data, and private DOM. Handoffs need expiry and audience scope; an authenticated Safari session reference must not itself grant access. Preserve evidence hashes and mark stale state rather than silently reusing it.
- **missing:** A first-class handoff record and lifecycle (draft, sealed, claimed, blocked, completed, expired); A collector joining job receipts, journal entries, browser evidence capsules, active project, and conversational intent; A claim/lock protocol preventing two agents from performing the same next step; A pendant command and dashboard view for listing blockers and accepting or abandoning a handoff

### "“Remember that correction and apply it automatically next time, but show me what you learned.”"
- **useful because:** The system records receipts and outcomes, yet a correction such as “use the project branch, not the archive,” “never read billing aloud,” or “summarize errors in one sentence” does not become a transparent, testable preference. A cross-surface preference compiler would extract only an explicit correction, show the proposed rule and examples, version it, and apply it in Mac planning, browser extraction, relay speech, and routines. The owner gains compounding usefulness without opaque model memory silently changing behavior.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** realtime for acknowledging the correction; background for proposing a normalized rule and checking conflicts; deterministic for matching, versioning, rollback, and applying a rule.
- **latency:** Acknowledge immediately; present the proposed rule within 3 seconds; applying an existing rule adds effectively no model latency.
- **cost:** <$0.01 per correction, dominated by a small background extraction call (under 1k tokens). Matching and enforcement are local deterministic operations.
- **security:** Only explicit owner corrections become durable preferences; never infer sensitive traits from passive behavior. Store scope, source turn, confidence, and expiration. Redact page content and secrets from examples. Every applied rule should be visible and undoable from the dashboard or pendant voice.
- **missing:** A typed preference schema with scope (Mac/browser/voice/routine), precedence, examples, expiry, and provenance; Conflict detection and a preview showing how the rule would alter the next plan; A shared preference reader in planner, browser extraction, and speech formatting paths; A one-sentence pendant command to disable or roll back the last learned rule

### "“Before you tell me this is done, prove it with the smallest evidence packet I can inspect.”"
- **useful because:** A completed receipt currently proves that an action returned success, not that the owner's intended outcome is true. This capability would let each task declare an observable acceptance test—file hash or git diff, browser field/value and timestamp, calendar/reminder existence, or a screenshot region—and return a compact, source-linked proof packet. The pendant hears the conclusion; the dashboard exposes the exact evidence and whether it is live, stale, or only inferred.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic for declared checks, hashes, timestamps, and provenance; background only to translate a natural-language acceptance test into typed checks; realtime only for the spoken verdict.
- **latency:** Simple checks under 2 seconds; browser or multi-step verification under 8 seconds; never block speech indefinitely—announce verifying and deliver the packet asynchronously.
- **cost:** <$0.01 for deterministic checks; one small planner call (1–3k tokens) only when converting an unfamiliar acceptance phrase. Storage is bounded by hashes, snippets, and optional cropped evidence.
- **security:** Evidence must be least-privilege and redact secrets, payment fields, and unrelated DOM. A proof packet must distinguish observed from inferred and carry observedAt, source, and content hash. Do not claim proof when a browser tab changed or a Mac command was rewritten; surface the mismatch.
- **missing:** An acceptance-test schema and verifier registry spanning filesystem, git, reminders, and browser DOM/evidence; A planner hook requiring every mutation-capable task to declare or ask for an acceptance test; A compact evidence-packet endpoint with source links, hashes, freshness, and redaction metadata; A dashboard/pendant presentation that says verified, not verified, stale, or unable to verify


## Changes it proposed to its own stack

### `integration` — Ship a USB-local pendant session adapter in the Mac agent. It opens the live nRF9160 serial device (/dev/cu.usbmodem00096003658*) and ESP32 audio bridge (/dev/cu.usbserial-0287A9CA), translates the existing pendant frame protocol into the same pipeline/events and action-result envelopes used by the relay, and advertises a transport preference (USB-local > LTE > offline spool). It must bind each frame to a device nonce and turn ID, persist an append-only reconnect cursor, and refuse duplicate replay. This is a local transport, not a second assistant: the relay still owns durable conversation state and Mac/browser execution.
- **owner gets:** The pendant is physically on the owner's desk today but has not registered with LTE, so the owner cannot actually use the wearable loop. This would make button-to-speech, spoken results, and truthful action status work immediately over USB, then hand off to LTE later without changing how the owner speaks or losing a turn when the cable is pulled.
- effort: Medium-high: serial framing/baud discovery, two-device lifecycle, audio clock buffering, protocol adapter tests, and relay/local-agent transport arbitration. A vertical slice can support button events and TTS/status before full duplex audio.  ·  risk: Incorrect framing or reconnect cursors could duplicate a command or lose audio. Keep a bounded local cursor and require relay acknowledgement before dropping frames; on ambiguity report queued/unknown, never completed. USB device paths can change, so identify by USB serial descriptors and allow a configured fallback. Recover by falling back to the existing offline store and LTE transport.
- cost: No per-request API cost for transport; roughly 1–2 weeks engineering. Existing Mac CPU/USB power only; the ESP32 audio bridge adds its already-present USB draw.  ·  latency: Button and action-status events should be under 100 ms locally; audio adds serial buffering (target <250 ms one way). Handoff may cost 1–3 seconds while reconnecting.
- security: USB is a local physical trust boundary but still use the existing bearer/session authentication and device nonce; do not log raw microphone frames or relay credentials. Keep serial diagnostics redacted.
- depends on: A serial protocol definition and framed CRC/turn-id contract for both attached boards; A local-agent transport interface that can be selected ahead of relay polling; An implementation of the already accepted audio_link_truth_and_recovery and truthful_action_status_beacon behaviors over the USB adapter; Pairing the current USB device identity to this owner’s local agent


## What it asked for

_Nothing._
## Its own summary

Produced four non-duplicate proposals. Most useful: a USB-local pendant session adapter so the physically attached boards work now despite no LTE registration, using the existing relay pipeline envelopes with exactly-once reconnect cursors. Also proposed a cross-surface routine recorder (“turn what I just did into a button”), a budget governor grounded in the live authenticated billing tab and /routing telemetry, and failure rescue with exit codes, precondition fingerprints, bounded retries, and crash reconciliation. Live checks confirmed Safari/browser online, Mac bridge and relay reachable, full control enabled, and current billing balance $10.63 with auto-reload on; /routing still has no usage samples.

**Biggest unknown:** The actual nRF9160/ESP32 serial framing and audio protocol, plus the local-agent transport hook that can feed USB events into the existing pipeline. I still need that protocol/interface fact (and an implementation-grade serial diagnostic path) before the USB proposal can be executed. The other missing work is durable: usage attribution/budget ledger, routine parameterization compiler, and retry/crash-reconciliation coordinator.

