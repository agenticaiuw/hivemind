# Harness derivation — browser-extension — round 83

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability and watch quality** — The browser bridge is currently offline with 7 pending commands, while three persisted sessions and two disabled watches still point at old tabs. The UTC watch generated 8 reports from clock churn, demonstrating that raw change detection needs volatility suppression before pendant escalation.
  - evidence: GET /browser/status at round 83: online=false, home-chrome only, pendingCommands=7. GET /browser/sessions: stale time.is/Selenium/httpbin tabs. GET /watches: UTC watch had checkCount=12/changeCount=8, all timestamp changes; watches enabled=false.

## Capabilities it proposed

### "Watch my chosen logged-in browser pages, learn which changes are noise, and alert me on the pendant only when a meaningful change needs me; leave the evidence and a prepared next step on my Mac."
- **useful because:** This combines the browser's private login reach with the always-awake relay and wearable interruption channel. The owner gets timely alerts without being spammed by volatile counters, timestamps, ads, or routine page churn, and can review sourced evidence on the Mac before acting.
- **path:** browser-extension → mac-planner → relay-realtime → unified
- **model tier:** Use a cheaper background model for scheduled extraction, field classification, and change ranking; reserve realtime only to phrase an urgent pendant alert or answer follow-up questions.
- **latency:** Scheduled checks can tolerate seconds to a minute. A high-confidence urgent change should reach the pendant within about 10 seconds of the browser result; normal changes wait for a digest.
- **cost:** Low per check: browser extraction and hashing dominate; use a small model only for ambiguous semantic diffs. Realtime cost is limited to escalations, not every poll.
- **security:** Authenticated page text and URLs stay on the Mac/browser path unless the owner opts into relay delivery; send the pendant only a minimal alert and citation. Never submit forms or send messages automatically. Require a local review for prepared actions.
- **missing:** A watch-change classifier that learns per-field volatility and suppresses known noise while retaining raw before/after evidence; A relay alert policy with quiet hours, severity escalation, acknowledgement, and deduplication keyed to watch report IDs; A Mac review card that links the report to its authenticated tab/session and shows the exact evidence plus a reversible next-step draft

### "When I say “save this for later” while viewing a private webpage, remember the exact passage or control I’m looking at, attach my spoken note and the page context, and bring it back to me through the pendant at the time I choose—even if the page later changes."
- **useful because:** Today the owner can bookmark a URL or dictate a vague reminder, but cannot preserve the precise meaning of something behind a login and reliably return to it later. This would turn a fleeting browser moment into a durable, reviewable memory without requiring the owner to copy sensitive text manually.
- **path:** browser-extension → relay-realtime → mac-planner → unified
- **model tier:** Use a small background model to normalize the spoken note, identify the relevant DOM region, and summarize changes when revisiting. Use realtime only when the owner dictates the note or asks for the reminder conversationally.
- **latency:** Capture should complete within 2 seconds of the spoken command. Reminder delivery can be scheduled; revisit and change comparison may take several seconds when the owner opens it.
- **cost:** Low: one short transcription/normalization call at capture and an occasional background comparison. Storage and browser extraction dominate, not model inference.
- **security:** Private page text must remain encrypted on the Mac unless the owner explicitly enables relay backup. Store a minimal excerpt hash, URL, DOM locator, timestamp, and user note by default; offer explicit inclusion of plaintext. Do not expose captured content in notifications or share it with third parties. Reopening a page may encounter a changed account state, so present evidence and stop before any mutation.
- **missing:** A browser-side anchored-capture primitive that returns the current selection or semantically nearest DOM region with a stable locator, excerpt hash, and screenshot-free fallback; An encrypted cross-surface memory record linking the capture to the owner's spoken note, optional reminder time, browser session, and sensitivity policy; A revisit resolver that reopens the authenticated page, finds the original region or reports it missing, computes a meaningful before/after comparison, and delivers a pendant notification with a Mac review link; A user-facing retention and deletion control for these private page memories, including automatic expiry and revocation of the browser session reference


## Changes it proposed to its own stack

### `browser-harness` — Add an offline-aware browser session lease watchdog. Every browser command is bound to an extension/device epoch and tab lease; when heartbeats disappear, stop delivery and mark queued commands quarantined (not failed). On a new heartbeat, validate the device identity and tab/session affinity, replay only idempotent reads, and require explicit re-planning for clicks/types/selects. Reconcile each command with the cross-surface intent ledger and emit one receipt per step, so stale commands cannot execute after Safari was closed or a tab was replaced. Add a janitor endpoint/job to inspect and safely discard the current 7 orphaned pending commands.
- **owner gets:** The owner will not get a surprise click, duplicate form fill, or action in the wrong logged-in tab after Safari sleeps, restarts, or changes tabs. Long-running browser tasks can resume safely instead of silently timing out, while private sessions remain usable when the extension reconnects.
- effort: Medium: browserBridge command schema/lease metadata, heartbeat epoch persistence, quarantine/replay worker, and dashboard visibility plus tests for disconnect/reconnect and tab replacement.  ·  risk: A reconnect could leave a read task paused or require re-planning more often than desired; recover by preserving the original plan and receipts and offering a resume/discard operation. Never replay mutation actions automatically. Existing stale commands must be quarantined before enabling replay.
- cost: Negligible API cost; small local JSON/D1 state and one lightweight heartbeat/cleanup worker. No new external data.  ·  latency: No added latency while online; reconnect adds one heartbeat/lease validation round (~100–500 ms) before safe read replay.
- security: Improves security by binding commands to device epoch and tab identity; private page contents remain in the browser bridge. Device re-registration invalidates old leases.
- depends on: chg-14accc01 reliable browser command queue with request IDs/idempotency/tab affinity; mac-planner cross-surface intent ledger and step receipts; browser extension heartbeat reporting a stable device identity and tab metadata


## What it asked for

_Nothing._
