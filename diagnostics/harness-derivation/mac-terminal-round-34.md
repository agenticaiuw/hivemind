# Harness derivation — mac-terminal — round 34

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser execution health** — The live Mac agent reports browserExtension.online=false, two pending browser commands, and browser_navigate jobs that wait about 45 seconds before failing; no fast preflight currently prevents duplicate offline attempts.
  - evidence: GET /ops/status at 2026-08-07T09:51Z reports online false and pendingCommands 2; GET /jobs shows two failed browser_navigate jobs with ~45,3xx ms durations and identical offline-extension error.

## Capabilities it proposed

### ""If something I ask needs Safari, just do it—or tell me immediately what is offline and use another route when possible.""
- **useful because:** The live Mac agent currently spends roughly 45 seconds attempting browser actions even when the extension is known offline, and repeats the same failed job. A fleet-aware preflight would make the system feel dependable: detect extension reachability first, route public pages to the relay/browser backend, and give a concise spoken recovery instruction for private pages instead of burning a long job.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for preflight classification and fallback planning; realtime only to tell the owner the short result or request that they open Safari
- **latency:** Health check under 500 ms; public-page fallback under 2–5 s to begin; authenticated-page offline response under 1 s. Do not spend 45 s on an impossible browser action.
- **cost:** Usually deterministic health checks and routing: near-zero model cost. One background call only when intent/fallback is ambiguous (roughly a few thousand input tokens, dominated by context); no realtime call unless speaking to the owner.
- **security:** Never send authenticated URLs, cookies, page text, or session identifiers to the public fallback. Classify origin and session binding before routing; private pages must remain on the Safari bridge. Record which backend was selected and why, but redact URLs/query strings in the spoken receipt unless the owner asked for them. Fallback should remain read-only unless the original action explicitly permits mutation.
- **missing:** A single fleet preflight endpoint/contract exposing browser online state, last heartbeat age, pending-command count, and whether a requested URL is public or session-bound; A relay public-browser execution adapter and a planner rule that refuses to use it for authenticated sessions; A fast-fail/idempotent browser job state so an offline attempt is not duplicated or left pending; Pendant-friendly error/result event carrying a one-sentence recovery instruction

### "“What am I looking at, and what should I do next?”"
- **useful because:** Today the owner must manually explain which document, browser task, meeting, and deadline they mean. This capability would turn the pendant into a genuinely ambient second set of eyes: it combines the Mac’s active application/window and selected text, the browser’s authenticated tab context, the next calendar commitment, and the owner’s current spoken goal into one cited, privacy-aware answer—without requiring them to touch the laptop or recite context.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Use deterministic local collection and filtering first; use a background reasoning model to reconcile the compact evidence and propose next steps. Use realtime only to speak the short answer and handle a follow-up.
- **latency:** Button-to-first spoken acknowledgement under 300 ms; evidence collection under 2 s; answer under 5 s. If screen/browser evidence is unavailable, say exactly which source is missing rather than hallucinating.
- **cost:** One background call per explicit request, with a compact evidence packet (roughly 1–3k input tokens and a short completion); deterministic Mac/browser reads dominate neither API cost nor latency. No periodic model polling.
- **security:** Selected text, window titles, calendar details, and authenticated page content can be highly sensitive. Collection must be explicit per request, local-first, with source-level opt-outs and redaction of passwords, payment data, and hidden tabs. Never transmit raw screenshots or page text to the relay unless the owner has enabled visual context; attach source URL/window and timestamp to every claim. Speaking aloud must omit sensitive details when headphones are not connected, and the owner must be able to say “forget that snapshot.”
- **missing:** A cross-surface 'situational snapshot' contract with typed fields, timestamps, confidence, and sensitivity labels for active Mac UI, selected text, browser tab/session, calendar horizon, and recent pendant utterance; A Mac bridge read path for active window/selection and a browser bridge read path for the foreground authenticated tab, both returning bounded provenance rather than raw unrestricted dumps; A local privacy filter and per-source consent state, including an audio-output safety mode for spoken answers; A relay request that correlates the pendant press, snapshot ID, reasoning trace, and cited answer, plus a dashboard card showing exactly what evidence was used; A pendant interaction for explicit capture, cancellation, and deletion of the snapshot

### "“Keep working, but only interrupt me if it truly matters; otherwise collect everything and tell me at a good time.”"
- **useful because:** The owner cannot currently express one interruption policy that follows work across the pendant, relay, Mac jobs, and authenticated browser sessions. This would let background work continue without turning every completion or failure into noise, while still surfacing a genuinely urgent deadline, failed irreversible step, or required owner decision at the right moment.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Deterministic event aggregation and deadline/severity rules first; use a background model only to resolve ambiguous urgency or cluster related results. Realtime is reserved for a genuinely urgent spoken interruption.
- **latency:** Events classified locally in under 200 ms; non-urgent items batched into the next digest. Urgent delivery under 2 s after a qualifying event, subject to quiet hours and availability.
- **cost:** Near-zero model cost for typed job/browser events and fixed urgency rules; occasional background clustering call (short context, dominated by event metadata) and no call per routine completion.
- **security:** Notification content can reveal private mail, browser pages, or work details aloud. Store policy and urgency decisions locally/relay-authenticated, redact summaries by default, and require an explicit owner setting for audible interruptions. Never let an urgency classifier authorize a mutation; it can only notify or defer. Preserve source links and event IDs for review.
- **missing:** A shared interruption-policy object with quiet hours, channels, severity thresholds, deadline windows, and per-source sensitivity rules; Normalized event envelopes from Mac jobs, browser watches, relay jobs, calendar deadlines, and pendant connectivity, with deduplication and causal links; A durable notification queue supporting defer, snooze, bundle, acknowledge, and escalation, synchronized between relay, pendant, and Mac dashboard; A deterministic urgency evaluator with an auditable reason code and a safe fallback of 'defer, do not interrupt' when evidence is incomplete; Pendant controls for 'quiet now', 'tell me at [time]', and 'why did you interrupt me?'


## Changes it proposed to its own stack

### `mac-harness` — Add a structured shell execution ledger alongside the existing job receipt without changing FULL_CONTROL_MODE: record argv/tokenized command form, resolved cwd, start/end timestamps, timeout, exit code, signal, stdout/stderr byte counts plus bounded redacted tails, environment/network classification, and a stable command fingerprint. Emit lifecycle events at start, timeout, completion, and failure; link each shell record to the originating pendant request, planner trace, jobId, and undo status. Add a deterministic retry recommendation (never automatic retry for unknown side effects) and expose a compact GET job detail for the dashboard and spoken receipt.
- **owner gets:** When an unattended Mac command fails or changes something permanent, the owner can currently learn that a job failed but not reliably what ran, where it ran, how long it waited, or whether retrying is safe. This gives a trustworthy answer to “what happened?” and prevents blind duplicate commands, while preserving the owner's deliberate maximum-access policy.
- effort: Medium: typed ledger schema, executor instrumentation, redaction/fingerprint utility, job-detail endpoint, dashboard rendering, and tests for timeout/nonzero/signal paths.  ·  risk: Command text may contain secrets; redact common token/key/password patterns and cap tails, with an opt-out only for explicit owner debugging. Ledger writes must be append-only/idempotent so a crash cannot falsely report completion. Do not infer reversibility from the fingerprint; retain the existing action receipt as authority. Recovery is to fall back to the current job record if ledger writing fails.
- cost: Negligible API cost; local JSON/SQLite append and a few KB per command. Add retention/rotation to prevent the ledger growing without bound.  ·  latency: Usually under 5 ms per command for event writes; dashboard reads become cheaper than scanning full logs. No extra model latency.
- security: Improves auditability without adding a gate or reducing shell capability. Store only redacted output and hash/fingerprint of sensitive command material; protect the ledger with the same local-agent auth as jobs.
- depends on: Existing job IDs, trace IDs, and receipt linkage; A bounded local retention/rotation policy; Dashboard support for a shell-specific execution timeline

### `model-routing` — Create a deterministic 'receipt compiler' for completed/failed Mac jobs: consume typed job/receipt fields and render concise spoken and dashboard variants (success, partial, timeout, offline dependency, retry-safe/unsafe), with model escalation only when the owner asks a follow-up that requires interpretation. Add a token-budget guard that strips full traces and large output from the planner context, retaining IDs, effect, evidence, and next action.
- **owner gets:** A simple request such as “prepare a concise completion receipt” currently consumed a background model call with about 2,163 input tokens for 34 output tokens. The owner gets faster, cheaper, more consistent answers for routine Mac work, while nuanced questions can still escalate to the model.
- effort: Small to medium: define receipt templates and status taxonomy, implement compiler in relay/local agent, add routing metric, and test partial/failed/undo cases.  ·  risk: Templates could omit an important caveat or misstate a partial result. Require explicit unknown fields and say “I could not verify” rather than guessing; retain a one-tap/voice path to request full job evidence. Existing raw receipt remains available.
- cost: Near-zero model cost for routine receipts; saves repeated background calls and context tokens. Small local CPU/storage overhead.  ·  latency: Typically sub-100 ms locally instead of ~1.3 s model round trip.
- security: Less sensitive command/output text is sent to models. Keep raw evidence behind authenticated local-agent access and redact it from spoken output by default.
- depends on: Typed shell execution ledger and existing action receipts; Stable job status/effect vocabulary; A routing hook that can identify receipt-only requests


## What it asked for

_Nothing._
## Its own summary

Discovered live fleet state and proposed three non-gating improvements: (1) browser health preflight with public/private fallback and fast failure, motivated by two current offline browser commands each spending ~45 seconds; (2) an append-only structured shell execution ledger for observability and safe retry judgment while preserving FULL_CONTROL_MODE; (3) deterministic Mac job receipt compilation to avoid a ~2,163-token model call for a 34-token routine receipt. Shared the browser finding with unified and recorded it.

**Biggest unknown:** The newly granted Mac diagnostics interfaces exist in the schema but have no implementation and return an error, so I cannot independently verify host state through those tools. I do not need another permission grant; the missing implementation (or an equivalent read-only diagnostic path) is what remains. Separately, the browser extension is genuinely offline and needs Safari/bridge recovery before authenticated browser work can succeed.

