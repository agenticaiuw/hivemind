# Harness derivation — mac-planner — round 256

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-and-observation** — The Mac agent currently has Accessibility and Screen Recording granted for AI Pendant Agent; synthesized input is verified reaching the system. GET /observe reports 20 running apps, foreground Claude, four durable browser sessions, and configured workspace roots. browser_tabs via mac_readonly_inspect remains unresolved because action:browser_inspect and POST /browser/inspect tie.
  - evidence: mac_readonly_inspect operation=running_apps and foreground_app invoked GET /observe at 2026-08-09T00:31Z; response accessibility.trusted=true, screenRecording=true, eventsPost=true.

## Capabilities it proposed

### "When I say “save my place,” capture what I was doing across my Mac, browser, calendar, and pendant, then later let me say “resume my place” and hear a one-sentence orientation plus reopen the exact safe-to-reopen resources."
- **useful because:** The owner loses work at transitions, not because any one app lacks a save button. A durable cross-surface checkpoint would turn an interrupted day into a resumable state: active project and app, browser tabs, relevant next calendar event, and a timestamped pendant bookmark, without pretending unsaved text can be recovered.
- **path:** pendant → relay → mac-vision → browser-extension → mac-planner
- **model tier:** Background model for checkpoint summarization and ranking; realtime only for the spoken resume request.
- **latency:** Checkpoint under 3 seconds; resume orientation under 2 seconds, with reopening happening asynchronously after the sentence.
- **cost:** About $0.01–$0.04 per checkpoint/resume pair; dominated by one short summarization call. Mac and browser inspection are local/bridge calls.
- **security:** Checkpoint contents can include private tab titles, filenames, and calendar subjects. Store redacted metadata by default, never page bodies or passwords; reopening URLs is allowed only for explicitly marked safe domains, while destructive or authenticated mutations remain blocked/confirmed under owner policy.
- **missing:** A durable checkpoint schema and two commands (save_place/resume_place) spanning relay journal, Mac observation, browser tab state, and the existing offline_moment_bookmark event.; A Mac semantic-context read for active document/project identity and selected text; current inspection can provide apps and tabs but not the full editor state.; A resume renderer that turns checkpoint evidence into one short spoken sentence and a separate reopen plan.

### "Start a focus block for this task, and quietly tell me on the pendant when I drift into unrelated apps or tabs; when the block ends, give me the files, links, and one next action I actually touched."
- **useful because:** It converts the pendant from a passive notification speaker into a low-friction attention partner. The Mac can observe app/tab changes, the browser can classify the active page, and the pendant can interrupt without requiring the owner to keep checking a timer. The end report is useful even if the block was messy.
- **path:** relay → mac-planner → mac-vision → browser-extension → pendant
- **model tier:** Cheap background classifier for app/tab relevance and end-of-block synthesis; realtime tier only for the initial spoken command and urgent pendant alert.
- **latency:** Start in 2 seconds; drift classification within 5 seconds; no more than one alert per 10 minutes; end report within 10 seconds.
- **cost:** $0.02–$0.08 per focus block, dominated by periodic batched classification; local observation and tab metadata are otherwise cheap.
- **security:** App names, tab titles, and touched file paths leave the Mac only as redacted metadata. Never capture screenshots, keystrokes, page bodies, or editor contents by default. Focus alerts must be dismissible locally and must not auto-close apps or tabs.
- **missing:** A time-bounded focus-session state machine in the relay with explicit relevance anchors and cooldowns.; A read-only Mac foreground/document identity feed; current running-app and browser-tab inspection is insufficient to distinguish an unrelated VS Code workspace or a tab title with ambiguous wording.; A pendant alert payload that includes session id, urgency, and a local snooze action while reusing the existing offline_alert_inbox rather than creating another queue.

### "Review the change I’m currently working on and tell me, on the pendant, the one highest-risk issue and the one test I should run next; open the relevant diff and authenticated code-review page, but never post a comment."
- **useful because:** This is a genuinely cross-node review loop: the Mac has the local diff and test environment, the browser has the authenticated review/issue context, and the pendant gives a short answer while the owner is away from the screen. It avoids the dangerous half of code-review automation—posting or merging—while still delivering a decision-quality next step.
- **path:** relay → mac-planner → browser-extension → mac-vision → pendant
- **model tier:** Background coding model for diff/test-result analysis and browser-context reconciliation; realtime only to answer the spoken request and read the final two sentences.
- **latency:** Collect context in under 8 seconds; if tests are needed, report immediately and stream a final result when complete; spoken answer under 20 seconds.
- **cost:** $0.05–$0.30 per review, dominated by diff/test output and one coding-model pass; browser and Mac collection are local.
- **security:** Local diffs and private repository metadata are sensitive and should remain on the relay/Mac boundary with redacted logs. Never transmit secrets from environment files, never execute an unrequested mutation, and never post, approve, merge, or push. Running tests requires an owner-configured command policy because the current FULL_CONTROL path bypasses its risk scorer.
- **missing:** A bounded local-review collector that returns git diff/status and test output with secret-file redaction and size limits.; A browser context collector for the currently authenticated PR/issue, limited to visible metadata and review comments.; A cross-node evidence joiner that labels stale or conflicting local-vs-browser revisions before synthesis.; An owner-configured policy entry permitting named read-only review commands; the current empty policy must not be treated as authorization.

### "Protect my meeting: while I’m in a calendar event or on a call, collect only genuinely urgent mail, browser alerts, and Mac notifications, suppress the rest, then give me one three-item spoken digest when the event ends—without losing links or sender context."
- **useful because:** Today each surface interrupts independently, and the pendant cannot know whether an alert is worth breaking a meeting for. This would make the hive act as one interruption filter: calendar establishes the protected interval, Mac/browser provide event candidates, relay ranks them, and the pendant delivers one controlled digest at the boundary.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** A small background classifier/ranker for candidate alerts; realtime only for an urgent spoken alert or the post-meeting digest.
- **latency:** Enter protected mode within 5 seconds of calendar/call detection; urgent ranking within 30 seconds; digest within 60 seconds of the event end.
- **cost:** $0.01–$0.05 per protected interval; most work is local metadata collection and batched ranking.
- **security:** Notification text, sender names, meeting titles, and browser alert metadata are private. Keep full bodies local where possible, redact secrets and page contents, expire the holding buffer after delivery, and require an owner policy defining what counts as urgent. Never auto-reply, dismiss, or send mail.
- **missing:** A cross-surface protected-interval state machine keyed to Calendar events and detected call state, with explicit start/end and grace periods.; A Mac notification metadata reader and browser alert/event feed; current calendar/mail reads and browser tabs do not expose all incoming notifications.; A durable, expiring alert-batch schema that preserves source links and sender context while reusing the pendant's existing alert inbox for delivery.; An owner-configurable urgency policy and a post-event digest route; without those, ranking is arbitrary and suppression is unsafe.

### "Save this unfinished web form so I can resume it later, restoring the fields and attachments exactly—but never submit it or expose passwords and payment details."
- **useful because:** Browser sessions disappear or expire, and an unfinished application or reimbursement form can take hours to reconstruct. The browser can identify form controls and the Mac can retain local attachments while the relay tracks a resumable draft; the pendant provides a spoken reminder and status without requiring the owner to keep the page open.
- **path:** browser-extension → relay → mac-planner → pendant
- **model tier:** Background deterministic form/attachment mapper; no expensive model unless the owner asks for a human-readable summary.
- **latency:** Capture in under 5 seconds; restore in under 10 seconds after the authenticated session is available.
- **cost:** Under $0.01 per save/restore, mostly local storage and browser bridge calls.
- **security:** This handles extremely sensitive data. Encrypt drafts locally, exclude password/payment/SSN fields by type and heuristic, never send field values to the relay, bind a draft to origin and account, expire it automatically, and require explicit confirmation before restoring into a live page. Submission must be technically unavailable, not merely discouraged.
- **missing:** A browser extension primitive to enumerate, classify, encrypt, and restore form controls and file inputs without page-body upload.; A local encrypted draft vault with origin/account binding, expiry, attachment references, and deletion receipts.; A relay index containing only redacted draft metadata and an existing pendant alert/inbox record for reminder status.; A browser-side restore mode that refuses submit/navigation side effects and reports fields it could not safely restore.

### "Before I submit a web form, tell me on the pendant what personal or confidential data is leaving, who receives it, and whether the destination is new or suspicious; let me cancel, but never rewrite or submit the form for me."
- **useful because:** The owner can currently click through a logged-in browser with no cross-surface privacy check. A browser hook can inspect the pending form locally, the relay can compare the destination against the owner's known sites and policy, and the pendant can provide a last-second warning when the Mac screen is elsewhere.
- **path:** browser-extension → relay → pendant → mac-planner
- **model tier:** Deterministic local field classification and domain policy first; a cheap model only for ambiguous labels, with realtime speech for the warning.
- **latency:** Warning within 500 ms of a submit attempt; cancellation must happen before navigation; spoken summary under 8 seconds.
- **cost:** Near-zero for known field types and domains; under $0.01 for occasional ambiguous classification.
- **security:** Raw field values must stay in the browser and never be sent to the relay or model. Send only categories, destination origin, and policy matches. The extension must fail closed on unknown high-sensitivity fields, provide a visible browser explanation, and preserve the owner's ability to override locally. This is a safety warning, not surveillance or automatic blocking of ordinary navigation.
- **missing:** A browser submit interception hook with a pre-navigation pause and a local cancel path.; A privacy classifier that emits categories (identity, health, financial, credentials, internal) without exporting values.; A relay-maintained destination trust/policy registry and a compact pendant warning protocol with a cancel action.; A tested timeout/failure policy so a relay outage never silently permits a high-sensitivity submission.


## What it asked for

_Nothing._
## Its own summary

This round produced three new cross-node capabilities: Save/Resume My Place (durable Mac+browser+calendar+pendant checkpoint), Focus Block with drift alerts and an end-of-block action report, and a read-only code-review capsule that joins local diff/tests with the authenticated browser PR and speaks the highest-risk issue plus next test. I also re-probed the Mac: Accessibility and Screen Recording are now granted, synthesized input is verified, 20 apps are running with Claude foreground, and four browser sessions are present. The browser-tab inspection tool still cannot resolve because two live capabilities tie.

**Biggest unknown:** Whether the relay already has a durable checkpoint/session primitive and whether the browser bridge can expose authenticated PR metadata without page-body capture. The remaining concrete gaps are semantic Mac document/workspace identity, browser-inspection disambiguation, bounded git diff/test collection, and explicit owner-configured policy entries for unattended read-only review commands.

