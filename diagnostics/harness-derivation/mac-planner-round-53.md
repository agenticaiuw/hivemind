# Harness derivation — mac-planner — round 53

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac_readonly_inspect and mac_read_sources availability** — Both tools are granted in the schema but currently return 'This tool was granted a schema but has no implementation yet', so I cannot obtain live Mac app/UI/browser/calendar/mail evidence through the intended read-only interfaces.
  - evidence: Parallel calls in Round 53 to mac_readonly_inspect (running_apps, foreground_app, accessibility_enabled, browser_tabs) and mac_read_sources (calendar_today, mail_unread) all returned the same unimplemented-tool error.

## Capabilities it proposed

### "“I’m going into a meeting—keep everything quiet, but don’t lose anything important, and resume my work when it’s over.”"
- **useful because:** A single pendant action would coordinate the whole hive instead of silencing only one device: it prevents spoken/browser interruptions, preserves in-flight work, identifies truly urgent exceptions, and resumes queued results after the calendar event. Today the Mac, relay, and browser each have independent state and can leave stale jobs or notifications behind.
- **path:** pendant → relay → Mac planner → browser-extension → dashboard
- **model tier:** Background/scheduled work uses a cheaper model for event classification and queue reconciliation; realtime is used only for the pendant’s immediate acknowledgement and urgent exception wording.
- **latency:** Immediate pendant acknowledgement under 1 second; quiet-state propagation under 3 seconds; resume reconciliation within 30 seconds of the calendar event ending, with a concise completion receipt on the pendant.
- **cost:** About $0.01–$0.05 per meeting transition, dominated by one background reconciliation/summarization call; ordinary quiet/resume state changes should be deterministic and free.
- **security:** Calendar title/time and job metadata leave the Mac only as typed, minimized facts. Browser page contents remain local to the browser harness unless an already-authorized job needs them. Never auto-send or submit anything while resuming; surface drafts and high-impact actions for the owner. Require an explicit pendant press to enable quiet mode and make expiry visible.
- **missing:** A shared interruption lease/state machine spanning pendant, relay, Mac jobs, and browser jobs, with an expiry tied to a Calendar event.; A typed urgency contract so only predefined urgent events can break quiet mode.; Pause/resume hooks in the durable Mac and browser job runners that checkpoint evidence rather than replaying clicks.; A pendant-local quiet-mode indicator and offline fallback so the mode remains clear during a dropped link.; A dashboard view showing parked jobs, exceptions, and what will resume.

### "“Prepare all of this across my Mac and logged-in browser, but don’t change the real world until I approve one complete preview—and if I approve, apply it as one recoverable transaction.”"
- **useful because:** Today the hive can draft or execute individual Mac/browser actions, but it cannot stage a multi-surface plan and guarantee that the owner sees one coherent before/after diff or recover from a partial failure. This would make complex requests—filing a document, updating a local folder, and preparing a logged-in form—safe to review as a single unit rather than a pile of unrelated receipts.
- **path:** pendant → relay → Mac planner → browser-extension → dashboard
- **model tier:** Use a cheaper background model to assemble the plan, normalize evidence, and generate the diff; use realtime only to answer the owner’s approval question and report success/failure.
- **latency:** Build a preview in under 60 seconds for ordinary jobs; approval acknowledgement under 1 second; commit progress and final receipt within 30 seconds, with immediate failure notification if any participant cannot commit.
- **cost:** Approximately $0.03–$0.15 per transaction, dominated by evidence normalization and final diff generation; deterministic staging, hashing, and rollback bookkeeping should not require model calls.
- **security:** Private browser content stays within the authenticated browser harness except for explicitly selected excerpts. The preview must redact secrets and show exact destinations, recipients, URLs, files, and field values. Approval must bind to a displayed plan hash and expire; never silently commit a changed plan. If rollback is impossible for an external side effect, classify it before approval and require a separate explicit acknowledgment.
- **missing:** A cross-surface transaction coordinator with a plan hash, participant prepare/commit/abort phases, idempotency keys, and durable recovery state.; Mac staging adapters for files, notes, reminders, and drafts, plus snapshot/restore support for mutations that are currently permanent.; Browser staging that can preserve an authenticated draft without submitting it and can verify the target tab/session at commit time.; A single diff renderer and plan-hash approval protocol usable from the pendant and dashboard.; A failure policy that distinguishes reversible local changes from irreversible external submissions and reports partial completion truthfully.


## What it asked for

_Nothing._
## Its own summary

Round 53 produced a new cross-surface capability: Meeting Quiet/Resume. A pendant press creates an expiring interruption lease tied to Calendar; relay suppresses nonurgent voice/browser/Mac notifications, checkpoints in-flight jobs, allows only typed urgent exceptions, then reconciles and resumes work after the meeting with one receipt. Fresh /ops/status confirms relay and Mac bridge reachable, but browser offline with 3 pending commands, Accessibility and Screen Recording absent, and computer-use disabled. The newly granted read-only Mac/calendar/mail tools are schema-only and currently unimplemented.

**Biggest unknown:** I still cannot inspect the actual foreground app, open tabs, calendar, or mail because mac_readonly_inspect and mac_read_sources have no implementation. The next practical unblock is implementing those read-only tools, then adding durable pause/resume hooks and stale-browser-command quarantine for the proposed interruption lease.

