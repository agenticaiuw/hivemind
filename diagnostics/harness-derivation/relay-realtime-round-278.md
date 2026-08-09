# Harness derivation — relay-realtime — round 278

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Do the complex computer task I described and keep me posted if it needs attention."
- **useful because:** This uses the relay as a low-latency front door, the Mac as the actor, and a background notification path for follow-ups. It’s the kind of multi-surface workflow this system is uniquely built for.
- **path:** relay → mac-bridge → browser → pendant
- **model tier:** Realtime for intake, Mac planner for execution, cheaper background monitoring for status.
- **latency:** Initial acknowledgment under a second; execution can take as long as needed.
- **cost:** Moderate; planning and execution dominate, not the relay.
- **security:** Do not run destructive actions without confirmation. Summaries should be concise and avoid leaking sensitive content.
- **missing:** A reliable post-session completion notification pipeline; A resolvable intent routing tool or a committed plan/execute route from the relay surface

### ""Before you do anything, tell me what you know, what is stale, and what you are guessing; then carry out the request and show me the evidence afterward." Give me a spoken, cross-device evidence trail for every answer and action."
- **useful because:** Today the owner can receive a plausible answer or a job receipt, but cannot reliably distinguish live Mac state, an authenticated browser observation, remembered preference, and model inference. This would make the pendant trustworthy for consequential everyday decisions: each claim would carry source, observed-at time, freshness, and whether it was directly verified; after execution it would summarize the exact evidence and any unresolved uncertainty.
- **path:** pendant → relay → mac-planner → mac-vision → browser → dashboard
- **model tier:** Realtime handles the short spoken explanation and uncertainty negotiation; mac-planner/mac-vision and browser gather evidence; a cheaper background model normalizes and deduplicates the provenance graph.
- **latency:** First spoken scope in under 1.5 s; live evidence in 5-15 s; long evidence normalization asynchronously with a concise pendant update.
- **cost:** Roughly one realtime turn plus existing Mac/browser calls; background normalization <$0.01 per action. Dominant cost is screenshots/page reads, not the provenance formatting.
- **security:** Evidence may include private page text, files, and phone state. Keep raw evidence on the Mac/browser surfaces, send only claims and hashes to relay/dashboard, redact secrets, and require explicit confirmation before exposing sensitive evidence aloud.
- **missing:** A cross-surface provenance record linking claims to observation timestamps and action receipts; A relay endpoint that can answer 'why/what source/how fresh' for a prior turn; Mac/browser adapters that return structured evidence references rather than only prose

### ""I'm concentrating for the next hour. Keep my Mac, browser, and iPhone from interrupting me, but let through only things that genuinely need me; restore exactly what you changed when I say I'm back.""
- **useful because:** The owner is usually away from the Mac and cannot safely manage a consistent focus state across macOS, authenticated browser tabs, and iPhone Mirroring from a single interface. This gives the worn pendant a reversible, time-bounded focus mode with an explicit exception policy and a rollback ledger, rather than a collection of disconnected Do Not Disturb toggles.
- **path:** pendant → relay → mac-planner → mac-vision → browser → ios → dashboard
- **model tier:** Realtime interprets the short command and speaks exceptions; deterministic Mac/iOS/browser actions apply and restore state; a cheap background worker evaluates incoming notifications against the owner's allowlist.
- **latency:** Enter focus in under 3 s and restore in under 5 s. Exceptions should be surfaced within 2 s of detection when the Mac is online.
- **cost:** Usually one realtime turn and a handful of deterministic actions, under $0.02; background filtering is negligible. Cost is dominated by periodic notification inspection if native event hooks are unavailable.
- **security:** This changes notification visibility and could hide an urgent message. Default to a visible pendant indication for suppressed high-priority items, retain only metadata unless the owner asks for content, cap duration, and make restore idempotent. Never silently alter personal focus settings outside the explicit session.
- **missing:** Native Mac notification/focus-state read-write and snapshot/restore actions; iOS Mirroring notification and focus controls exposed to the Mac agent; A relay-held reversible session with expiry and an exception classifier

### ""Ask me one short question whenever my request has two reasonable interpretations, then remember the answer only for this task. Do not make me repeat constraints across the Mac, browser, and phone.""
- **useful because:** A spoken request often becomes ambiguous only after a downstream agent sees the UI: which account, recipient, date, or device was intended. Today the owner must either accept a guessed plan or restate context to another surface. This creates a single, low-latency clarification turn, carries the answer through the whole job, and expires it when the task ends so temporary constraints do not pollute long-term memory.
- **path:** pendant → relay → mac-planner → mac-vision → browser → ios
- **model tier:** Realtime asks and confirms the one necessary question; downstream planners perform deterministic execution; a cheap model detects unresolved slot conflicts and chooses the minimum clarification, never rewriting the owner's words.
- **latency:** Clarification in under 1 s after ambiguity is detected; execution begins immediately after the answer; no extra model call when the request is unambiguous.
- **cost:** Adds at most one short realtime turn ($0.01-$0.05 depending on model); conflict detection can run in the planner's existing call. Savings come from avoiding failed/repeated downstream jobs.
- **security:** Temporary constraints can include recipients and account identities. Bind them to a job/session, encrypt in transit, expire automatically, and do not promote them to persistent memory without a separate explicit request. Read-only questions should never trigger an action.
- **missing:** A shared job-scoped context envelope accepted by planner, browser, and iOS executors; A planner response type that distinguishes 'need one clarification' from failure; Relay session storage and expiry for the clarification answer


## What it asked for

_Nothing._
