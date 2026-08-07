# Harness derivation — faculty-action — round 131

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m stepping away—lock everything down.”"
- **useful because:** One physical command would immediately protect an unattended laptop: close or suspend private browser sessions, stop queued Mac work, mute the audio path, and leave a reversible audit trail. It uses the worn object as the trusted trigger instead of relying on a voice phrase that could be overheard.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime interprets the short intent; deterministic relay policy and the Mac agent execute the bounded lockdown; no background model is needed.
- **latency:** LED acknowledgement within 300 ms; local Mac/browser changes within 3 s; relay receipt within 10 s.
- **cost:** <$0.01 per invocation; dominated by one realtime intent turn, not device operations.
- **security:** A false trigger could interrupt work, so require a deliberate long press plus a nonce LED pattern and keep restore reversible. No page contents leave the Mac; relay stores only session IDs, timestamps, and action receipts. Closing tabs must never delete data.
- **missing:** Pendant long-press event over the current USB serial bridge; A named privacy-lock policy spanning Mac jobs and browser sessions; A restore operation that reopens only the sessions closed by this lock

### "“Bookmark exactly where I am; I’ll continue later.”"
- **useful because:** A wearable bookmark would turn an interruption into a resumable work state: the Mac records the frontmost app and reversible document context, the browser bridge records the relevant tab URLs/titles and scroll anchors, and the relay makes a compact spoken resume card. On return, one button or voice command reopens the right tabs and presents the next unfinished step instead of forcing the owner to reconstruct it.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** A cheap background planner normalizes the captured state; realtime is used only when the owner asks for the spoken resume card.
- **latency:** Capture acknowledgement under 1 s; resume card under 15 s; restoration may take up to 30 s and must report partial success.
- **cost:** <$0.02 per bookmark, mostly one small background summarization; storage is a few KB of metadata plus no copied page secrets.
- **security:** Persist opaque tab/session references and local document paths, not page bodies or clipboard contents. Private tabs must be opt-in. Reopening a tab is reversible and must not submit forms or trigger mutations.
- **missing:** A serial bookmark event and timestamped LED confirmation on the pendant; Mac APIs for frontmost app/document context without screenshots; Browser extraction of per-tab URL/title/scroll anchor with session binding; A resume-card schema and idempotent restore job

### "“The action failed—figure out what went wrong and get me to a safe retry.”"
- **useful because:** Instead of a vague failure, the hive would collect a bounded failure packet: the Mac agent's typed step results and stderr, browser tab identity and last safe page state, relay job timeline, and pendant connectivity/LED state. It would classify whether retry is safe, prepare a minimal repair action, and speak one clear next step. This is especially valuable when the owner is away from the Mac and cannot inspect logs.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** A cheaper background model summarizes and clusters failures; realtime only delivers the short spoken diagnosis when requested.
- **latency:** Failure detection under 5 s; evidence packet under 20 s; no automatic retry of irreversible steps.
- **cost:** <$0.03 per failed job; the dominant cost is background diagnosis, with evidence retained locally where possible.
- **security:** Redact tokens, cookies, message bodies, and secret command arguments before relay storage. The repair plan is advisory until the owner confirms; retries must begin from a recorded idempotent checkpoint and never replay a send/purchase/delete step.
- **missing:** A typed failure envelope shared by Mac, browser bridge, relay, and pendant; Automatic secret redaction for stderr and DOM evidence; Checkpoint metadata distinguishing safe replay from irreversible completion; A pendant error-event endpoint and a dashboard failure timeline

### "“Move the information from this logged-in page into my local project, but do not send the page contents through the relay.”"
- **useful because:** The owner could safely combine private browser data with local Mac work: the browser extracts only explicitly named fields, transfers them over the authenticated Mac bridge, and the relay receives only a redacted receipt. Today the system can inspect browser pages or act on the Mac, but cannot enforce this private, field-scoped boundary across both.
- **path:** browser-extension → mac-bridge → relay → dashboard
- **model tier:** A local Mac planner handles field selection and transformation; realtime is unnecessary except for the owner's initial command.
- **latency:** Preview in 5 seconds; local transfer and receipt in 15 seconds.
- **cost:** <$0.02 per invocation; local processing dominates and relay traffic is metadata only.
- **security:** Require an explicit field allowlist, local-only encryption, and a preview before writing. Never expose cookies, surrounding page text, or credentials to the relay; reject selectors that broaden beyond the approved fields.
- **missing:** Field-scoped browser extraction with a local-only destination; A Mac/browser encrypted handoff channel with relay-blind payloads; A redaction and provenance receipt proving which fields moved; Local destination adapters for project files, Notes, and editor buffers

### "“Keep my plan true, not merely recorded.”"
- **useful because:** The hive would maintain a declared desired state across services—for example, a calendar appointment, a local project checklist, and a logged-in reservation—and periodically reconcile observed state. It could repair harmless drift automatically, prepare changes for review, and tell the owner when an external change makes the plan impossible. Current routines and watches report activity, but they do not maintain a cross-device invariant.
- **path:** relay → browser-extension → mac-bridge → dashboard → pendant
- **model tier:** Background model evaluates drift and proposes repairs; deterministic adapters perform only explicitly permitted reversible updates; realtime is reserved for spoken escalation.
- **latency:** Routine reconciliation within 10 minutes of a change; urgent contradiction surfaced within 60 seconds when a session is online.
- **cost:** <$0.05 per reconciliation cycle, dominated by authenticated page reads and occasional background reasoning.
- **security:** Desired states need scopes, expiration, and per-field permissions. Never silently change external commitments, send messages, or purchase; retain before/after evidence and require confirmation for consequential repairs.
- **missing:** A desired-state schema spanning browser entities and Mac files/apps; Cross-surface identity matching and conflict resolution; A drift detector that distinguishes external change from stale observation; Repair policies with field-level approval and expiration

### "“Tell me when the thing I started has actually reached the outside world.”"
- **useful because:** For actions spanning the Mac and browser, the owner should receive a final, externally verified outcome rather than a local success message: the relay records the commit receipt, the browser re-reads the resulting confirmation page or message status, and the pendant gives a short completion signal. This closes the dangerous gap between 'the click happened' and 'the service accepted it.'
- **path:** pendant → relay → mac-bridge → browser-extension → dashboard
- **model tier:** Deterministic verification first; a cheap background model interprets ambiguous confirmation pages. Realtime only speaks the final one-sentence result.
- **latency:** Verification within 10 seconds of commit; ambiguous cases escalated within 30 seconds.
- **cost:** <$0.03 per action, mainly one authenticated re-read; no model call for structured confirmations.
- **security:** Verification must be read-only and bound to the same tab/session and idempotency key. Do not infer success from a toast alone. Store hashes/snippets rather than full private pages and require owner confirmation if the result is ambiguous.
- **missing:** Post-commit verification contracts per browser action; A service-side correlation ID visible in receipts and confirmation pages; Read-only browser reattachment after a mutation; Pendant completion/error event protocol


## Changes it proposed to its own stack

### `integration` — Add a cross-surface failure envelope and recovery coordinator. Every Mac/browser step emits a typed checkpoint with action class (replayable, inspect-only, irreversible), redacted evidence pointers, and an idempotency key. The relay joins those events with job receipts and pendant connectivity, freezes only the unsafe suffix after a disconnect or error, and exposes one repair/continue decision rather than allowing a whole workflow to replay.
- **owner gets:** When something breaks, the owner gets a trustworthy answer—what completed, what did not, and the one safe way forward—instead of duplicated messages, half-filled forms, or guessing whether a retry is dangerous.
- effort: Medium-high: shared schema in local-agent and relay, browser adapter changes, recovery state machine, redaction tests, and dashboard timeline.  ·  risk: A bad checkpoint classification could either replay an irreversible action or unnecessarily stop work. Default unknown steps to frozen; preserve current receipts and allow manual recovery. Roll out in observe-only mode first.
- cost: Negligible API cost; small D1 event volume and a few KB per failed job.  ·  latency: Adds under 100 ms per step for event emission; diagnosis is asynchronous.
- security: Positive if redaction is correct: fewer raw logs in relay. Requires strict filtering of cookies, authorization headers, DOM secrets, and shell arguments.
- depends on: typed action result schema in the Mac agent; browser command IDs and tab affinity; redaction library shared by relay and Mac; owner-confirmed policy for unknown/irreversible steps


## What it asked for

_Nothing._
