# Harness derivation — relay-realtime — round 187

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say something that sounds like a command, route it to the right place and tell me what you’re doing."
- **useful because:** Reduces friction. The owner can speak naturally and the system chooses Mac actions, browser work, or a web search without manual switching.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-judgement
- **model tier:** Realtime for intent detection and confirmation; mac-planner handles multi-step plans.
- **latency:** Under 1 second to confirm the route for simple tasks; complex planning can take longer but should be handed off.
- **cost:** Small per utterance. Cost dominated by planning when tasks are complex.
- **security:** Route safely: don’t execute irreversible actions without confirmation. Keep raw utterances minimal and avoid storing sensitive content unless needed.
- **missing:** A resolvable relay routing tool or enum-based routing schema; A relay capability inventory endpoint so routing isn’t guesswork

### "Read out what’s happening right now with my system, briefly."
- **useful because:** Quick, hands-free status at a glance: queued jobs, failures, connectivity hints, and what’s waiting for review.
- **path:** relay-realtime → faculty-perception → mac-planner
- **model tier:** Realtime for spoken summary; perception/planner for aggregation.
- **latency:** 1-2 seconds for a short summary; longer details only on request.
- **cost:** Low. Dominated by pulling job summaries and any needed snapshots.
- **security:** Status summaries should avoid exposing sensitive document content; focus on counts and labels.
- **missing:** A unified status snapshot that includes relay job records and Mac agent state in one call; A way to request terse vs detailed summaries consistently across surfaces

### ""I just saw something wrong on my computer—find the exact problem, fix it if it is safe, and tell me what you changed.""
- **useful because:** The owner can report a problem from the pendant without walking to the Mac or reconstructing which window, tab, or error they meant. The wearable supplies the utterance and timing; the Mac supplies the live screen, logs, and authenticated state; the relay fuses them into one bounded repair and an audible explanation.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay for the short clarification and final spoken answer; gpt-5.6-luna mac-planner for diagnosis and reversible repair; gpt-4.1-mini mac-vision only when visual evidence is required; no expensive model for receipt summarization.
- **latency:** Acknowledge in under 500 ms, collect live Mac evidence within 5 s, and speak the diagnosis within 10 s. If diagnosis exceeds that, provide a spoken progress update and retain the result for the next button press.
- **cost:** Roughly $0.03–$0.15 per invocation, dominated by planner/vision calls and any screenshot or log context; relay speech itself is the smaller share.
- **security:** Screen images, logs, and browser contents may leave the Mac for model inference. Default evidence should be limited to the implicated app and the last few seconds, with explicit redaction of secrets. Reversible edits can run automatically under the owner's maximum-access policy; deletion, sending, or external publication must be reported before execution. A full action receipt and undo reference must be spoken or available on the pendant.
- **missing:** A correlation window that binds a pendant utterance to the Mac's active app/tab and recent error events; A Mac evidence bundle action (scoped screenshot, focused-window metadata, recent logs); Planner support for diagnosis followed by a validated repair and rollback, rather than a flat action list; A relay-side clarification/receipt protocol that survives the voice turn

### ""Save this thought exactly where it belongs: identify the project from what is open on my Mac, turn my voice into a structured note with action items, and link it to the relevant tab or file.""
- **useful because:** A one-button spoken thought becomes useful project memory rather than an orphaned audio memo. The pendant is available at the moment of insight, while the Mac can identify the active project and write into the owner's existing tools; the owner does not need to remember the thought or later sort it.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Realtime relay for capture acknowledgement and a cheap transcription/normalization pass; background gpt-5.6-luna only for project attribution and structured extraction when the Mac context is available.
- **latency:** Store the utterance immediately in under 1 s; classify and file it within 15 s when the Mac is online. If offline, retain the typed payload and complete filing on reconnection without recording beyond the button-held interval.
- **cost:** About $0.01–$0.06 per note, dominated by transcription and one planner classification call; retries should be idempotent and nearly free.
- **security:** The note may contain confidential work or personal material. Keep raw audio on the existing failure-only path, send only the transcript plus narrowly scoped active-project context, and never attach a whole screen by default. Filing is a local reversible write; external sharing is out of scope and must never be inferred.
- **missing:** A project-context resolver that maps active Mac app/tab/file to a stable project identity; Idempotent structured-note writes with source timestamp, transcript, extracted actions, and backlinks; A relay command to distinguish 'capture now' from ordinary conversational dictation; A reconnect worker that files already-captured notes without duplicating them

### ""Before I leave, make sure the work I was doing is recoverable: summarize the exact state of my open project, save a restart checklist, and tell me the one next action.""
- **useful because:** The wearable can turn an abrupt physical departure into a reliable handoff. The Mac contributes open files, tabs, diffs, terminal state, and unsent drafts; the relay compresses that into a spoken next step and a durable checkpoint the owner can resume later, preventing lost context rather than merely reporting status.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Realtime relay handles the immediate spoken acknowledgement; a background gpt-5.6-luna planner builds the checkpoint from a bounded Mac snapshot. A smaller deterministic formatter should generate the checklist and receipt.
- **latency:** Acknowledge immediately, snapshot in 3 s, and provide the one-next-action summary within 8 s. Checkpoint persistence must complete before claiming success; otherwise say it is only a draft.
- **cost:** Approximately $0.02–$0.10 per checkpoint, mostly planner context from diffs/tabs and optional summarization; deterministic persistence is negligible.
- **security:** Open documents, code diffs, and browser tabs can contain secrets. Snapshot only the focused project and omit credentials, cookies, and raw terminal environment variables. Saving locally is reversible and should be automatic; the spoken response must distinguish saved checkpoint, failed save, and partial capture.
- **missing:** A scoped workspace snapshot that captures open files, git diff, terminal cwd/command context, browser tabs, and unsent draft status; A durable checkpoint store with versioning and resume links, separate from transient job receipts; A planner schema that identifies the single next action and unresolved blockers with evidence; A pendant-triggered departure/checkpoint gesture or explicit voice intent

### ""Handle this when my Mac is reachable again: use the context I gave you now, finish the task later, and tell me only when it actually succeeded or needs me.""
- **useful because:** Today a worn owner must repeat a request or poll after losing the Mac link. This creates a durable, consent-scoped intent—not merely an audio memo—that can resume across relay, Mac, and browser availability, then deliver a truthful result to the pendant. It is the clearest path to the system being useful while the owner is away from the desk.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay extracts and confirms the intent in one short turn; a cheap background worker retries transport and readiness checks; gpt-5.6-luna plans only when execution becomes possible; mac-vision is invoked only for visual ambiguity.
- **latency:** Acknowledge escrow in under 1 s. Resume within 10 s of Mac/browser availability. Completion delivery should be eventual, with no repeated model calls while a dependency is unavailable.
- **cost:** $0.01–$0.08 per task, dominated by one planner call and any vision/browser step; retries and event delivery should be sub-cent operations.
- **security:** The escrow must expire, show its exact scope, and never broaden from the original utterance. Persist transcript/context encrypted with a redaction boundary; do not retain browser credentials. Reversible local work may proceed automatically under owner policy, but sending, purchasing, deleting, or publishing must enter needs_attention and explain why. Completion must include an execution receipt, not a guessed success.
- **missing:** A durable intent escrow with dependency state, expiry, idempotency key, and retry ownership; A Worker Cron/Durable Object alarm or equivalent background runner (currently absent); A Mac reconnect/availability webhook and browser-session readiness signal; A real completion watcher that maps job state to the pendant inbox/event push; An execution contract separating original intent, planner-generated actions, and observed receipts

### ""Check the authenticated site I was using on my Mac, find anything urgent, and tell me only what needs me—without waking me to every routine update.""
- **useful because:** The owner can act on private web information while away from the Mac, where the current system has no reach: the browser extension depends on the Mac being online and the relay has no authenticated browser execution. This joins the wearable's low-latency request, a secure browser session, relay prioritization, and durable alert delivery.
- **path:** pendant → relay → browser-extension → mac-planner
- **model tier:** Realtime relay handles the request and concise spoken answer; a background browser worker performs retrieval and a cheaper classifier ranks urgency; use the expensive planner only for ambiguous pages or follow-up actions.
- **latency:** Speak acknowledgement in under 1 s; return a first result in 15 s when the session is available. Routine monitoring should run asynchronously and notify only on a high-confidence urgent change.
- **cost:** $0.02–$0.20 per check, dominated by browser execution and page extraction; scheduled checks cost Worker/browser runtime more than model tokens.
- **security:** Authenticated cookies and page contents must remain in an isolated browser vault, never be sent to the relay model wholesale. Require explicit one-time pairing and per-site scopes, redact secrets, log every page/action, and make any external mutation a separate request. Urgency ranking must quote evidence and offer a quiet false-positive policy.
- **missing:** A server-side isolated browser runtime or a secure browser-session handoff that works while the Mac is offline; Encrypted session storage with owner-controlled pairing, revocation, and per-origin permissions; A scheduler/background worker for periodic checks (currently absent); Page-change extraction and evidence-backed urgency ranking; A relay-to-pendant alert path with deduplication and quiet hours


## Changes it proposed to its own stack

### `integration` — Implement a real completion-notification path by connecting job completion events to the existing offline alert inbox pattern. If relay_event_push remains schema-only, add a relay route that emits a typed alert payload for the browser-extension inbox, and have the Mac/relay bridge translate job events into those alerts.
- **owner gets:** They get reliable spoken completion cues without polling, even if the Mac goes to sleep or connectivity is spotty.
- effort: High. Needs event wiring, payload contracts, and testing across relay, Mac bridge, and pendant inbox behavior.  ·  risk: Medium. Risk of duplicate or missed notifications; mitigate with idempotent job receipt IDs and retry policies.
- cost: Moderate. Background monitoring costs scale with active jobs; keep polling minimal and prefer push from job receipts.  ·  latency: Completion latency depends on backend event availability; should be near-real-time when events exist.
- security: Alerts must avoid leaking sensitive content; speak only sanitized status lines and require confirmation for high-risk follow-ups.

### `relay` — Build a durable cross-surface Intent Escrow, not another job list: on pendant release, persist a normalized intent, evidence references, allowed action envelope, expiry, and idempotency key; a Durable Object alarm retries only the unmet dependency (Mac offline, browser unavailable, or planner failure), and completion is accepted only from an execution receipt whose observed state matches the requested outcome. On reconnect, the escrow hands the same intent to the Mac planner and emits one pending/completed/needs-attention event to the pendant inbox.
- **owner gets:** The owner can ask once while walking away and trust that the work will either finish later or clearly come back as needing them. They stop losing tasks merely because the Mac was asleep, and they hear a truthful outcome instead of having to poll or repeat themselves.
- effort: High: new Durable Object/alarm state machine, reconnect hooks from Mac and browser, idempotent planner handoff, receipt verification, expiry UI/voice wording, and firmware inbox integration.  ·  risk: A stale or duplicated escrow could act at the wrong time. Recover with short expiries, immutable original utterance, idempotency keys, cancellation, visible pending records, and receipt-gated completion. If verification fails, stop and report needs_attention rather than retrying mutations blindly.
- cost: Low steady-state storage and alarm cost; roughly one background Worker invocation per dependency transition plus the existing planner/model call. No new hardware cost.  ·  latency: Immediate escrow acknowledgement; deferred execution latency becomes availability-bound. Normal online tasks add under 200 ms for persistence, while offline tasks wait safely rather than burning retries.
- security: Adds durable storage of user intent and scoped context. Encrypt it, redact secrets before persistence, bind it to the owner's session, and enforce expiry and cancellation. Never persist browser cookies or credentials.
- depends on: Cloudflare Durable Object or Cron alarm wiring (currently absent); A Mac/browser availability callback; A stable receipt schema with observed-state verification; The existing pendant inbox/event delivery path


## What it asked for

_Nothing._
## Its own summary

Recorded five non-duplicate proposals. The strongest is Intent Escrow: a pendant request survives Mac/browser outages, resumes only when dependencies return, and reaches the owner only with a verified receipt. I also recorded evidence-linked remote repair, structured project capture, departure checkpoints, and authenticated browser access while the Mac is offline. The changes require new connective behavior rather than pretending existing /plan and /execute already provide durable intent, dependency retries, evidence correlation, or cloud browser reach.

**Biggest unknown:** Whether the existing browser watch/session machinery already supports authenticated execution and scheduling; I was explicitly told not to discover further this round, so I marked those as missing requirements rather than asserting absence.

