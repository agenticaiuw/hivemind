# Harness derivation — mac-planner — round 286

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac and bridge readiness** — As of 2026-08-09 03:22Z the Mac agent, relay, browser extension, Accessibility, Screen Recording, and Apple automation permissions are all live; iPhone Mirroring is running but there is no /ios/status or /ios/inspect route on the Mac agent. Workbench contexts currently empty.
  - evidence: GET /ops/snapshot returned relay reachable, macBridgeOnline true, trusted accessibility/screen recording, iPhone Mirroring in running apps; GET /ios/status and GET /ios/inspect returned 404; GET /workbench/contexts returned {contexts:[]}.

## Capabilities it proposed

### "When I say “remember this and make it useful,” use what is on my Mac right now—selected text or the active browser page, app, and time—combine it with my pendant bookmark, and create a durable, searchable note with a suggested next action or reminder. Tell me exactly what was captured, without stealing focus or sending anything."
- **useful because:** This turns the pendant's one-button moment marker into an actual memory of the thing the owner meant, rather than a timestamp they must reconstruct later. It uniquely combines worn-device intent, Mac accessibility state, browser sessions, relay reasoning, and durable Mac storage.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the short spoken acknowledgement; a cheaper background text model extracts the page/selection, resolves entities, and proposes the next action.
- **latency:** Acknowledge the bookmark in under 500 ms; capture within 3 seconds; suggestion within 10 seconds. Never wait for a network round trip before recording the local bookmark.
- **cost:** About $0.01–$0.05 per capture depending on whether a background model is needed; latency and cost are dominated by sending page text/selection, not the bookmark event.
- **security:** Page text and selected text may contain secrets. Default to title/URL/selection with redaction, never passwords or form values; show a compact preview before any reminder or external send. The Mac policy must explicitly authorize read_current_context, write_note, and create_reminder; empty policy must stop the mutation.
- **missing:** A resolved mac semantic-context read for selected text, document identity, and active-window identity (the pending mac_semantic_context_read request).; A relay event contract linking offline_moment_bookmark to a Mac capture job.; A redaction-aware note/action composer that can distinguish observation from owner-approved reminder creation.

### "Run this long Mac task overnight, and if it stalls, crashes, or finishes while I am away, tell me on the pendant. In the morning, let me say “resume the overnight job” or “show me what changed,” and continue exactly once from the last verified step instead of duplicating files or actions."
- **useful because:** The owner can delegate work across a sleeping Mac and an always-awake relay without babysitting it. The pendant is the only surface likely to reach them away from the desk; workbench staging and receipts make retrying safe instead of guessing whether a file was already produced.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Background model for plan decomposition and failure summarization; realtime model only parses the short resume/status utterance.
- **latency:** Start immediately, emit failure/completion alert within 30 seconds of a receipt or heartbeat timeout, and resume in under 5 seconds once the Mac is reachable.
- **cost:** Roughly $0.01–$0.08 per overnight task for failure summarization; storage and polling dominate rather than inference.
- **security:** The task may touch private files and arbitrary apps under current FULL_CONTROL_MODE. Require an owner-configured policy class for unattended writes, redact file contents from pendant alerts, and expose an immutable receipt with paths, hashes, and actions. Never resume an unknown job ID or silently widen its scope.
- **missing:** A relay-side job watchdog that consumes Mac receipts and emits a typed pendant alert.; A resume protocol that binds /workbench/contexts and GET /workbench/jobs/:jobId/handoff to one idempotency key and preserves the original policy scope.; A pendant command path for selecting one pending job from the existing alert inbox.

### "From the pendant, let me say “send this on my iPhone” or “reply to that message.” Inspect the mirrored iPhone and the current Mac context, draft the exact action, read it back, and then perform it only when the phone is frontmost and the target is still the same. If mirroring disappears, stop and tell me instead of guessing."
- **useful because:** The phone contains sessions and conversations the Mac/browser cannot reach. This would make the pendant a safe voice control for the real iPhone while using the Mac only as a constrained bridge: inspect, bind the action to evidence, then execute against the correct frontmost target.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** Realtime model for intent and concise read-back; a cheaper vision/text model extracts app, recipient, and draft from the captured mirrored screen. No model should infer a target from stale pixels after the evidence TTL.
- **latency:** Inspect and draft in 2 seconds; require a spoken confirmation for send/delete/purchase; execute within 1 second of confirmation or reacquire evidence.
- **cost:** About $0.02–$0.10 per action, dominated by one or two screen crops and OCR/vision calls; no cost when the phone is unavailable because the bridge should fail closed.
- **security:** Messages, banking and 2FA screens are highly sensitive. Use short-lived capture leases, crop/redact notification content, hash the inspected screen, and never persist raw screenshots. Require confirmation for all sends, deletes, purchases, and authentication changes; refuse if the app, recipient, or frontmost window changes.
- **missing:** A real ios_mirroring_inspect read-only capability returning screen hash/crop/OCR, frontmost app, and evidence TTL.; Typed iOS action execution through the Mac bridge with target binding and stale-evidence refusal.; Relay routing for spoken confirmation and a receipt that includes the evidence hash and resulting iOS state.

### "Let me make conditional promises from the pendant: “If the flight is delayed, move dinner to tomorrow and tell Alex,” or “When the invoice is paid, archive the thread and create the follow-up.” Keep the promise pending, monitor the relevant calendar/mail/browser evidence, and execute the smallest matching Mac/browser action only when the condition is proven. Read me the proposed consequence before any external message is sent."
- **useful because:** The owner can delegate decisions that depend on future facts instead of repeatedly checking systems or forgetting a promise. This is not a reminder: it is a durable, evidence-bound commitment spanning the pendant's spoken intent, the relay's always-on monitoring, authenticated browser sessions, and Mac actions.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for capturing the short promise; background model for condition extraction, evidence comparison, and consequence planning. Realtime is used again only when a consequence needs a spoken confirmation.
- **latency:** Store the promise immediately; evaluate low-frequency conditions within 2 minutes and urgent changes within 15 seconds; execute only after fresh evidence and confirmation where required.
- **cost:** Approximately $0.02–$0.15 per active promise per day depending on polling and page complexity; most cost is authenticated evidence retrieval, not model inference.
- **security:** Promises may trigger consequential messages or file changes long after they were spoken. Require explicit expiry, scope, recipient, and maximum action count; never infer a recipient from stale context. Redact monitored content, retain evidence hashes rather than raw pages, and require confirmation for sends, purchases, deletions, or calendar changes.
- **missing:** A durable conditional-intent record with condition, evidence source, expiry, consequence, and idempotency key.; Relay monitoring over calendar/mail/browser evidence with change detection and proof attached to each trigger.; A Mac/browser execution path that refuses stale evidence and emits a user-readable consequence preview.

### "Give me one interruption decision for all my surfaces: “Do not disturb me unless it is urgent or can save me five minutes.” Use my current Mac app/window, browser activity, calendar, mail priority, iPhone mirrored state, and pendant conversation state to decide whether to speak now, queue a compact alert, or wait for a natural break. Let me override the rule with one phrase."
- **useful because:** Today each surface can interrupt independently and cannot know that the owner is presenting, typing a sensitive message, or already speaking through the pendant. A cross-surface interruption budget would make the system feel considerate rather than like several assistants competing for attention.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** A small background classifier handles urgency and interruption cost; realtime is reserved for the actual alert and override phrase. Deterministic rules should handle meetings, secure-input screens, active calls, and privacy latch states.
- **latency:** Classify within 1 second for incoming events; queue non-urgent alerts without model work; reevaluate immediately when foreground app, calendar state, or pendant call state changes.
- **cost:** Under $0.01 per event when rules decide; $0.02–$0.05 for ambiguous priority classification. Most savings come from suppressing unnecessary model and TTS calls.
- **security:** The arbiter sees sensitive cross-device state. Keep raw mail/page text local where possible, publish only urgency features, and make the mode visible and reversible. Privacy latch must dominate every other rule; never expose notification content while the owner is in a protected state.
- **missing:** A shared interruption-state protocol with priority, expiry, suppression reason, and delivery surface.; A real iPhone Mirroring state/evidence reader and a Mac semantic window reader.; A relay arbiter that merges calendar, mail, browser, Mac, iPhone, and pendant events instead of each producer delivering independently.

### "At the end of a workday, tell me which commitments I actually kept, which are at risk, and which disappeared across email, calendar, browser work, Mac files, and pendant bookmarks. For each one, show the evidence trail and offer one concrete next action; do not turn every unfinished item into a task."
- **useful because:** The owner currently has fragments of intent in speech, mail, calendar, browser sessions, and files but no cross-surface accounting of outcomes. This would close the loop between what he said, what he did, and what still matters, reducing the mental cost of remembering promises without creating a noisy task list.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model after the workday; realtime only when the owner asks a follow-up or accepts a next action. Deterministic matching should establish timestamps and receipts before any model judges completion.
- **latency:** Generate in under 60 seconds on request or on a scheduled boundary; incremental evidence ingestion should be asynchronous and never interrupt the owner.
- **cost:** Approximately $0.05–$0.30 per daily review, dominated by summarizing cross-source evidence; incremental event matching can use a cheaper model or rules.
- **security:** This is a sensitive behavioral record. Store evidence references and hashes rather than full content, redact recipients and message bodies by default, allow per-source exclusion and deletion, and never infer that a commitment was kept solely because a file or page was opened.
- **missing:** A cross-surface commitment ledger with provenance, confidence, status transitions, and explicit owner corrections.; Connectors that turn browser receipts, Mac action receipts, calendar/mail events, and pendant bookmarks into common evidence records.; A review UI/voice format that distinguishes proven completion, likely completion, at-risk, and unknown without silently creating tasks.


## What it asked for

_Nothing._
