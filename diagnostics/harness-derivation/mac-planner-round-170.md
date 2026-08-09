# Harness derivation — mac-planner — round 170

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-and-screen-recording** — Live /observe at 2026-08-08T01:08:34Z reports AI Pendant Agent trusted, synthesized events posting successfully, Screen Recording true, and ui actions will reach screen. Foreground is Claude; 18 apps running. This supersedes the earlier denied-TCC premise for this Mac agent binary.
  - evidence: mac_readonly_inspect operation=running_apps and foreground_app both resolved to GET /observe, HTTP 200; accessibility.trusted=true, eventsPost=true, screenRecording=true.

## Capabilities it proposed

### ""Make sure every promise I make today actually gets finished.""
- **useful because:** This is the single most useful missing behavior: the pendant turns an underspecified spoken commitment into an owned task, the Mac gathers calendar/mail evidence, the browser checks authenticated work context when relevant, and the relay follows up until there is evidence of completion—not merely a reminder that can be ignored.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only for extracting the commitment and speaking the next question; background cheap model for deduplication, due-date inference, evidence ranking, and follow-up scheduling.
- **latency:** Acknowledge in under 2 seconds; initial evidence scan under 15 seconds; follow-up checks run asynchronously and only interrupt during an owner-configured window.
- **cost:** Roughly $0.01–$0.05 per commitment over its lifetime; most cost is periodic browser/mail/calendar evidence checks, not the initial realtime turn.
- **security:** Mail and authenticated browser pages may contain sensitive data and must remain redacted in relay summaries. Never mark complete from a draft or ambiguous page; require explicit owner confirmation for external sends, purchases, deletions, or irreversible changes. An empty owner policy must stop unattended browser mutations.
- **missing:** A durable commitment object with provenance, due/soft-due dates, evidence requirements, and state transitions; A scheduler that can re-check browser sessions and Mac sources without keeping raw page contents; A compact pendant interaction for confirm/defer/dismiss beyond the existing alert inbox; A browser page-watch adapter for authenticated, site-specific success evidence

### ""I just saw something important on my screen—save enough context that I can ask you about it later.""
- **useful because:** A short moment-bookmark currently records time, but not what made the moment important. This would let the owner press the pendant while the Mac is showing Claude, a document, or a browser session; later they can ask 'what was that?' and receive a redacted, source-linked reconstruction instead of a timestamp with no meaning.
- **path:** pendant → mac-vision → mac-planner → browser-extension → relay → dashboard
- **model tier:** No realtime model for capture. Local Mac extraction and a cheap background model produce a short title, selected UI text/OCR, active app/tab identity, and hashes; realtime is used only when the owner later asks a question.
- **latency:** Button acknowledgement under 300 ms. Capture bundle under 3 seconds, with a pending state if screen extraction is slow. Later answer under 4 seconds when the bundle is local.
- **cost:** Under $0.01 per bookmark when OCR/text extraction is local; $0.01–$0.03 only when a background model must summarize an image.
- **security:** Screen contents can include passwords and private messages. Redact secure-input/password fields, store a short-lived encrypted bundle rather than an always-on recording, and expose exact source/app/time in the dashboard. Never capture microphone audio; the button event is the sole trigger.
- **missing:** An event bridge from offline_moment_bookmark to a Mac capture request while the pendant is USB-attached today; A redacting screen/document capture endpoint with bounded retention and per-bundle deletion; A query API that retrieves one bookmark's evidence by spoken reference; A clear LED/inbox state for capture success versus capture unavailable

### ""I submitted that form—tell me whether it really went through, and keep checking until you know.""
- **useful because:** Browser automation today can click or type, but the owner still has to wonder whether a network error, redirect, or stale tab silently lost the result. The relay can ask the authenticated browser session for a confirmation page, have the Mac capture a receipt artifact, and use the pendant to report success, failure, or unresolved status without exposing the whole page.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Realtime for the initial spoken status and concise result; cheap background model or deterministic rules for page-state comparison, retry timing, and receipt extraction.
- **latency:** First verdict in 3–8 seconds; retry checks every 30 seconds for up to 10 minutes, then place a non-urgent alert in the existing pendant inbox.
- **cost:** Approximately $0.005–$0.03 per verification; browser polling and receipt storage dominate, while model use can be avoided for deterministic selectors.
- **security:** The browser must keep session cookies local. Send only a redacted status, origin, timestamp, and receipt hash to the relay. Never retry a non-idempotent submission automatically; verification may read, but any resubmission requires an explicit owner command and the configured policy entry.
- **missing:** A per-submission correlation id and idempotency-aware verifier; Site adapters that declare success/failure selectors without uploading page bodies; A durable receipt record with expiry and a pendant-readable status; A retry scheduler that distinguishes safe GET verification from mutation

### ""The connection dropped while you were doing that—tell me exactly what happened on every device and recover only the parts that are safe to retry.""
- **useful because:** Today a pendant, relay, Mac action, and authenticated browser session can each know a fragment of an interrupted operation, but the owner cannot obtain one causally ordered account of what happened or distinguish completed work from an unsafe retry. This capability would make dropped links recoverable instead of forcing the owner to guess, duplicate a submission, or manually audit several surfaces.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic state reconciliation and receipts first; use the cheaper background model only to explain the causal timeline in plain language. Reserve realtime for the owner's spoken recovery question.
- **latency:** Return a first state report in under 5 seconds; safe reconciliation may continue in the background for up to 2 minutes and then leave a durable unresolved item in the pendant inbox.
- **cost:** About $0.01–$0.04 per interrupted operation, dominated by reconciliation and browser verification; deterministic receipt matching should avoid most model calls.
- **security:** Never replay a browser mutation or external send without an idempotency key and an owner-configured policy entry. Keep raw browser contents and audio on their originating device; relay receives event ids, hashes, statuses, and redacted explanations. An ambiguous state must be reported as ambiguous, not guessed complete.
- **missing:** A shared operation id propagated from pendant intent through relay plan, Mac actions, and browser commands; A tamper-evident event ledger with per-surface acknowledgements and causal ordering; Idempotency keys and resumable checkpoints for browser and Mac mutations; A reconciliation engine that can classify complete, partial, safe-to-retry, unsafe-to-retry, and unknown states; A pendant interaction for accepting one safe recovery step without replaying the entire plan

### ""Before you change anything across my Mac and browser, show me the exact resulting state—including what the pendant will tell me—and let me compare it with reality afterward.""
- **useful because:** The current preflight can classify desktop actions, but it cannot simulate a multi-surface outcome or prove that the resulting browser page, files, receipts, and pendant message agree. This would give the owner a state-level preview and a postcondition diff, not merely a list of clicks.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Deterministic planners and snapshot differencing do the work; a cheap background model explains only genuinely ambiguous visual or semantic differences. Realtime is unnecessary unless the owner is speaking through the pendant.
- **latency:** Preview in under 8 seconds for ordinary Mac/browser plans; postcondition diff within 10 seconds of completion, with slow sites continuing asynchronously.
- **cost:** Approximately $0.005–$0.03 per plan, mostly local snapshot storage and browser inspection; model cost is avoidable for structured pages and files.
- **security:** Simulation must not submit forms or mutate state. Browser snapshots stay local and are redacted before any explanation leaves the device. A mismatch must halt further dependent actions and be surfaced as a mismatch, never silently repaired.
- **missing:** A sandbox or shadow execution mode for browser and Mac plans; Typed postconditions covering files, app state, browser DOM/status, relay receipt, and pendant delivery; Cross-surface snapshot IDs and a diff viewer understandable from the pendant; A plan compiler that emits a spoken pendant preview as well as desktop actions


## Changes it proposed to its own stack

### `mac-harness` — Ship a foreground-safe visual evidence capture path that uses the now-live AI Pendant Agent TCC grants: atomically collect the active app/window identity, browser session URL/title, accessibility tree text, and a redacted screenshot into a short-lived bookmark bundle, addressed by a nonce from the pendant and never by polling microphone or keystrokes.
- **owner gets:** When the owner presses the real pendant button, the system can recover what they were looking at even if they have already switched apps, making a fleeting screen moment queryable later without asking them to reproduce it.
- effort: Medium: implement capture/redaction/retention and the USB event bridge; exercise against Claude, Safari, Calendar, and Mail. Accessibility and Screen Recording are now live for AI Pendant Agent, so this is no longer blocked on TCC.  ·  risk: Private screen content could be over-collected or retained. Fail closed on secure input, redact password roles, cap bundle lifetime, provide immediate delete, and record only the requested button-triggered instant. Recovery is deletion of the bundle and disabling the capture policy.
- cost: Negligible API cost for deterministic extraction; roughly 100–500 KB per bundle locally, with no required relay upload. Small engineering cost for redaction tests.  ·  latency: Button acknowledgement remains local; capture target under 3 seconds and can return a pending inbox item.
- security: Improves security versus screen scraping by making capture explicit, nonce-bound, redacted, and short-lived; still needs an owner-configured policy entry because FULL_CONTROL_MODE currently has no enforced approval gate.
- depends on: offline_moment_bookmark event forwarding; a real redacting screenshot/accessibility capture route; owner-selected retention and upload policy


## What it asked for

_Nothing._
