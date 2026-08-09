# Harness derivation — mac-terminal — round 180

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""I'm in the middle of something—tell me what deserves my attention now, and ignore the rest.""
- **useful because:** This is the single most useful daily behavior: the pendant becomes an interruption filter instead of another notification source. The always-awake relay combines calendar/mail/notes briefing data with the authenticated browser's currently open work and the Mac's active application, then speaks only time-sensitive, actionable items. The owner can ask while walking without opening apps or losing their working context.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** background for periodic ranking; realtime only for the short spoken answer
- **latency:** Under 3 seconds for an on-demand check; periodic refresh can be every 15 minutes and should not wake the realtime model
- **cost:** Low per check: deterministic freshness/priority filtering first, then a small text-model synthesis; realtime tokens only for the final spoken turn
- **security:** Browser page titles and snippets, active-app metadata, and personal briefing items leave the Mac only to the authenticated relay. Never upload full page text unless the owner asks; return provenance and age for every item. Speaking sensitive content requires the pendant's existing active conversation state.
- **missing:** A Mac route that returns active app/window and notification metadata without page contents; A relay-side priority merger that deduplicates calendar/mail/browser candidates and tracks seen items; A browser inspection mode that emits title, origin, and actionable deadlines rather than arbitrary page text

### ""Save this for me." (while I am viewing a browser page or working in an app)"
- **useful because:** A spoken save action should capture a useful, recoverable artifact rather than a bookmark with no context. The pendant supplies the exact moment and intent; the browser supplies URL/title/selected excerpt; the Mac adds the active project and a short local-context note; the relay stores a deduplicated capsule. Later, "what did I save about that?" can retrieve the page and why it mattered.
- **path:** pendant → browser-extension → mac-planner → relay-realtime
- **model tier:** Cheap text model for metadata normalization and deduplication; realtime only for confirmation and retrieval dialogue
- **latency:** Acknowledge within 1 second, persist within 5 seconds; retrieval under 2 seconds from relay index
- **cost:** Small text embedding/index cost per save; no expensive vision or realtime model unless the page has no usable text
- **security:** Default to URL, title, selection, and a 500-character excerpt; redact secrets and form fields. Authenticated-page content must remain scoped to the owner's relay and be deletable. The device should cache only an opaque save ID while offline.
- **missing:** A browser command for capture-selection/capture-visible-context with explicit redaction; A Mac endpoint for active project and foreground-document metadata; A relay durable capsule index with owner-controlled retention and delete

### ""Start my next meeting.""
- **useful because:** One sentence should turn a calendar event into a coordinated transition: identify the next event, open its authenticated meeting link in the browser, focus the meeting window on the Mac, set audio to a known level, and give the pendant a 20-second spoken briefing with attendees, agenda, and the one document needed. This removes the frantic multi-app ritual that no single node can complete.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Deterministic routine and calendar lookup first; cheap text synthesis for the briefing; realtime only for the spoken interaction
- **latency:** Begin visible actions within 2 seconds and finish setup within 8 seconds; ask once if multiple candidate events exist
- **cost:** Very low: calendar/event parsing and browser/Mac actions are deterministic; only a short synthesis call is needed
- **security:** Opening a meeting link is an external side effect and should be announced before execution unless the owner has enabled a 'start next meeting' routine. Never transmit meeting transcripts or participant data to the relay beyond what is needed for the briefing. Do not auto-unmute or start recording.
- **missing:** Calendar event/link extraction exposed to the planner with timezone and join-link provenance; A routine action bundle that can coordinate browser open, Mac focus, and volume without race conditions; A postcondition check that the intended meeting tab/window is actually active

### ""Did you actually do that?""
- **useful because:** After a spoken multi-step request, the owner needs a single truthful answer, not a vague 'done'. The relay correlates the request ID across Mac job receipts, browser command results, and any resulting state check, then says exactly which steps completed, which failed, and what remains. If the Mac was offline, it says queued rather than implying execution. This is especially valuable while the owner is driving or cannot inspect the screen.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Deterministic correlation and state checks; cheap text model for a two-sentence explanation; realtime only to speak it
- **latency:** Under 1 second from cached receipts; under 5 seconds if a live postcondition check is needed
- **cost:** Near-zero for cached job/command records; small text synthesis only when the result needs explanation
- **security:** Use opaque request IDs and authenticated relay access. Do not speak sensitive command output by default—summarize action and status, with 'read details' as an explicit follow-up. Expire cross-surface correlation records after a configurable retention period.
- **missing:** A shared correlation ID propagated from pendant turn through relay, Mac job, and browser command; A postcondition/readback contract for common actions (window focus, URL, volume, file existence); A relay query that merges Mac GET /jobs/:jobId and browser command provenance into one answer

### ""Keep working on this while I sleep, and tell me in the morning what changed.""
- **useful because:** The owner cannot currently delegate a multi-hour, failure-tolerant task that survives a sleeping or rebooted Mac, authenticated browser expiry, and a disconnected pendant. This would let them hand off research, a code/test loop, or a browser-based comparison once, then receive a concise morning result with completed work, blocked steps, and links to artifacts rather than babysitting jobs.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Background/cheap models for decomposition, polling, and summarization; realtime only when the owner starts or receives the final spoken report
- **latency:** Acknowledge the handoff in under 3 seconds; resume within 30 seconds of Mac/browser availability; morning report available before the owner's configured wake time
- **cost:** Dominated by the number of background model calls and browser page reads; use deterministic checkpoints and incremental summaries to avoid resending the entire task context
- **security:** The owner must define allowed sites, folders, and mutation scope when delegating. Authenticated browser sessions and local files stay on their respective surfaces; the relay stores only encrypted task state and redacted checkpoints. Expired login, destructive action, or ambiguity must pause and report rather than guess.
- **missing:** A durable task runner with checkpointed steps that survives Mac-agent restarts and browser disconnects; A relay wake/resume queue that can hold work while the Mac sleeps or the pendant is offline; Browser-session lease and reauthentication detection with a clean paused state; A morning briefing record containing artifacts, diffs, failures, and exact evidence

### ""What am I looking at, and what are the two safest next actions?""
- **useful because:** Today the browser inspector can read a page and the Mac can inspect/control applications, but neither produces a unified, grounded explanation of the exact screen state across a foreground Mac app, browser tab, selection, and pending work. This capability would give the owner an on-demand verbal orientation—useful while their hands and eyes are occupied—followed by two concrete, reversible choices backed by visible evidence.
- **path:** pendant → mac-vision → mac-planner → browser-extension → relay-realtime
- **model tier:** Vision/text model only when a visual relationship is needed; deterministic accessibility tree and browser inspection first; realtime for the short spoken answer
- **latency:** Under 4 seconds for orientation and under 2 seconds for a selected follow-up action
- **cost:** Low when accessibility/browser text suffices; vision inference only for canvas, layout, or image content
- **security:** Screen pixels and authenticated page content are highly sensitive. Require explicit per-session screen-sharing consent, upload only the current cropped region when possible, and speak secrets only after the owner asks for the specific field. Keep evidence hashes and discard raw captures by default.
- **missing:** A unified foreground-context snapshot joining Mac accessibility state, active browser tab, cursor/selection, and current agent task; A vision/accessibility grounding layer that can cite screen coordinates and source surface in its answer; A spoken choice protocol that executes only the selected reversible action and confirms the observed result

### ""Make a bug report from what just went wrong, and attach everything the developer needs.""
- **useful because:** When an action fails, the owner currently has to reconstruct the failure from separate Mac jobs, browser state, screenshots, and spoken context. This would create a reviewable issue packet containing the exact request, timestamps, failed step, redacted command/result, browser URL and evidence capsule, relevant Mac logs, and a minimal reproduction—without requiring the owner to remember what happened.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Deterministic evidence collection first; cheap text model for timeline and reproduction steps; vision only if the failure is visual
- **latency:** Collect an initial packet in under 10 seconds; finish optional log collection asynchronously and announce when ready
- **cost:** Mostly local I/O and metadata; model cost is limited to summarization, with no need to resend raw logs after redaction
- **security:** Default to a private local draft, never auto-submit externally. Redact tokens, cookies, environment variables, page secrets, and unrelated windows. Require explicit confirmation before sharing outside the Mac or relay. Preserve provenance so generated claims can be checked against raw evidence.
- **missing:** A failure-triggered evidence collector spanning Mac receipts/logs, browser provenance, screen capture, and the pendant turn; A redaction and size-budget pipeline for logs, screenshots, and command output; An artifact exporter producing Markdown/JSON plus stable local attachments and a user-approved share target


## Changes it proposed to its own stack

### `integration` — Add a user-visible cross-surface transaction record, not just independent job IDs: relay assigns a turnId and step IDs, propagates them through /execute and browser commands, and exposes a compact status object with evidence, postconditions, and age. The Mac agent should perform declared readback checks after actions (for example active URL/window, volume, or file existence), while the browser returns command completion and observed tab state. The pendant speaks only the aggregate state and preserves the turnId offline for later reconciliation.
- **owner gets:** The owner can trust a spoken 'done' or immediately know 'Mac opened it, browser failed to focus the tab' without touching the computer. It prevents the most frustrating failure mode in a wearable assistant: an action that sounds complete but was never executed.
- effort: Medium-high: relay schema, Mac and browser propagation, and a small library of postcondition checks.  ·  risk: Old clients may omit IDs; treat them as uncorrelated rather than guessing. A readback can race with a user's manual change, so report observed-at timestamps and never claim causality beyond the check.
- cost: Negligible storage and network overhead; fewer expensive follow-up model turns because status answers become deterministic.  ·  latency: Adds roughly 100–500 ms for common readbacks; skip readback for purely informational actions.
- security: Correlation metadata must not include command secrets or raw stdout. Keep detailed evidence behind authenticated retrieval and redact sensitive page content.
- depends on: A relay-generated turnId propagated by relay-realtime; Mac /execute and browser command schemas accepting correlation and postcondition fields; A relay read endpoint that merges GET /jobs/:jobId/receipts with browser results


## What it asked for

_Nothing._
