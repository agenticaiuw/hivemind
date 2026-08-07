# Harness derivation — mac-planner — round 144

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-bridge live readiness** — Bridge and relay are online; browser extension is online with one protected AI Pendant Browser Bridge tab, and one controllable Gmail tab exists in the job history. FULL_CONTROL_MODE and planner are enabled, but computer-use loop is disabled, vision upload consent is false, Accessibility and Screen Recording are ungranted, and the new read-only inspection/source tools still return schema-only implementation errors.
  - evidence: GET /ops/status, GET /browser/status, GET /jobs, and direct calls to mac_readonly_inspect in round 144

## Capabilities it proposed

### "“If I have to leave my Mac, keep the task safe and pick it up from my pendant when I’m back: tell me what finished, what is waiting on me, and let me resume from the exact browser page or file without starting over.”"
- **useful because:** Today a long Mac/browser job is split across job records, browser tabs, and spoken interaction. A durable cross-surface task capsule would make leaving the desk safe: the relay can retain a compact checkpoint, the Mac can continue or pause, and the pendant can announce a truthful status and offer resume. This is more than async execution because it preserves evidence, tab/file identity, and the next safe action across a disconnected wearable and Mac.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the cheap background tier to summarize checkpoints and detect completion; use realtime only to answer the owner's live resume/status utterance. Do not spend realtime tokens polling.
- **latency:** Checkpoint writes under 300 ms; pendant status under 2 s when online. Resume may take 2–5 s to reattach the Mac/browser session, with an explicit 'stale checkpoint' result if the tab or file changed.
- **cost:** Low: one small D1/R2 checkpoint write per meaningful step and one compact background summary; realtime cost only when the owner asks. Dominant cost is browser extraction or Mac work, not the capsule.
- **security:** Capsules may contain private URLs, snippets, file paths, and draft text. Encrypt or redact payloads, bind each capsule to the paired device/session, expire stale browser credentials and checkpoints, and never auto-submit a mutation on resume. Resume should reopen/read first and return before/after evidence; sending/deleting remains an explicit owner command under the existing maximum-access policy.
- **missing:** A shared task-capsule schema and lease/heartbeat protocol spanning relay, Mac jobs, and browser sessions; A resume endpoint that validates tabId/sessionId/file existence and returns a typed stale/conflict result; Pendant playback/notification support for compact checkpoint summaries; Dashboard UI for paused, waiting-for-owner, completed, failed, and stale states

### "“When something important changes, tell me once on the best channel—pendant if I’m away, Mac if I’m working—and don’t repeat the same alert in my brief, dashboard, and browser.”"
- **useful because:** The same event can currently surface independently as a page-watch result, a workday brief, a relay message, and a Mac job update. A shared event identity and delivery ledger would prevent duplicate interruptions while still escalating an unacknowledged urgent change. The owner gets one actionable alert with a source and snooze/ack state instead of notification fatigue.
- **path:** browser → mac-bridge → relay → pendant → dashboard
- **model tier:** Use deterministic hashing, severity rules, quiet hours, and delivery state without an LLM. Use a cheap background model only to normalize semantically equivalent page-watch/mail/calendar findings; realtime is reserved for the owner's spoken acknowledgement or follow-up.
- **latency:** Dedup decision under 200 ms after an event arrives; urgent pendant delivery under 2 s; nonurgent items can wait for the next scheduled brief.
- **cost:** Very low for ledger writes and hashes; occasional background normalization dominates. Audio cost is incurred only for an actually delivered pendant alert, not every source event.
- **security:** The ledger contains sensitive event summaries and source URLs. Store only redacted fingerprints plus a short encrypted payload, scope records to the paired owner, and enforce source-specific quiet hours. Never infer that an alert was seen merely because it was delivered; require an acknowledgement receipt, and do not suppress a genuinely new state transition.
- **missing:** A canonical event envelope (source, subject, semantic fingerprint, severity, expiry, sensitivity, deep link); A cross-surface notification ledger with delivery, acknowledgement, snooze, and escalation state; A normalization step for equivalent findings from browser watches, calendar/mail briefings, and Mac jobs; Pendant acknowledgement and quiet-hours controls wired to the ledger

### "“Let me review something on whichever device is convenient, then approve that exact version from my pendant—even if I switch to my Mac or browser—and make every surface agree on what I approved. If anything changed, stop and show me the difference instead of guessing.”"
- **useful because:** Today review state is fragmented: a draft or browser action can be inspected in one surface while the spoken interaction, Mac job, and browser tab have separate state. The owner cannot safely approve one immutable artifact from the pendant and have the Mac/browser prove they executed that same artifact. A cross-surface approval certificate would bind the reviewed content, sources, target, and intended mutation to one version; stale or altered state becomes a visible conflict rather than a silent mismatch.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic canonical serialization, cryptographic hashes, and signature/nonce validation; no model is needed for the safety decision. A cheap background model may render a concise diff. Use realtime only to explain the conflict or capture the owner's spoken approve/edit/reject choice.
- **latency:** Certificate creation and validation under 300 ms locally; cross-device approval acknowledgement under 2 s online. A conflict response should be immediate and must never wait for an LLM.
- **cost:** Low: small signed payloads and ledger writes; occasional background diff summarization is the dominant model cost. No recurring cost for unchanged approvals.
- **security:** The certificate may contain private URLs, file paths, draft text, and account identifiers. Store a redacted hash plus encrypted artifact, bind it to the paired owner/device and intended target, expire it after a short TTL, and use a one-time nonce to prevent replay. Approval must never authorize a different tab, file, origin, or changed payload; mutations remain under the owner's existing maximum-access policy but are cryptographically constrained to the reviewed version.
- **missing:** A canonical artifact format covering browser fields, Mac files, and planned action lists; A signed approval-certificate service with one-time nonce, target binding, TTL, and replay detection; A precondition verifier in the Mac executor and browser bridge that compares current state to the certificate before mutation; A pendant approve/edit/reject protocol and dashboard diff view; Conflict receipts that can be returned to the relay and spoken without exposing the full private artifact


## Changes it proposed to its own stack

### `browser-harness` — Add an explicit browser-surface readiness and recovery state machine. When the extension heartbeat reports only its own protected extension page, classify the browser as connected-but-not-user-tab-ready; preserve the last usable tab/session, expose the reason, and let a queued job wait for a real web tab instead of attempting browser_snapshot and producing a misleading failure. On recovery, revalidate origin, tabId, and session affinity before continuing.
- **owner gets:** The owner should not see a failed task merely because Safari briefly foregrounded the bridge's own protected page. Long-running logged-in work would pause honestly, resume when a usable tab returns, and explain exactly what the owner needs to do—open or return to the site—without losing the task.
- effort: Moderate: heartbeat state, queue wait/resume transition, tab revalidation, and dashboard/pendant status text.  ·  risk: A stale tab could be mistaken for the intended private page. Require origin and session checks, expire the saved tab after a short TTL, and fail closed with a clear status when identity changes. No page mutation occurs during recovery.
- cost: Negligible; local state and a few relay/job records. No model call needed.  ·  latency: Heartbeat-driven recovery within one polling interval; typically under 2–5 s. No added latency for ready tabs.
- security: Improves security by preventing actions against the wrong tab and by treating protected extension/local pages as non-controllable rather than bypassing browser protections.
- depends on: GET /browser/status; POST /browser/heartbeat; GET /browser/poll; GET /browser/sessions; POST /browser/result/:commandId; The existing job receipts and tab/session affinity work


## What it asked for

_Nothing._
## Its own summary

Round 144 established a live Mac/browser gap and produced two new actions. Live state: relay, Mac bridge, and browser extension are online; FULL_CONTROL_MODE/planner are enabled; browser has a usable Gmail tab in job history but the current extension tab is protected; computer-use is disabled because vision upload consent is false; Accessibility and Screen Recording remain ungranted. The newly granted mac_readonly_inspect and mac_read_sources schemas still have no implementation, so they cannot yet provide truthful desktop/source reads. I proposed (1) cross-surface task capsules that preserve browser/file evidence and resume state across Mac, relay, browser, and pendant, (2) a deduplicated notification ledger with one best-channel alert and escalation, and (3) a browser readiness/recovery state machine that waits through protected extension pages and safely revalidates the intended tab before resuming. The first two were noted as connective work because their primitives exist; the third was recorded as a new change.

**Biggest unknown:** Whether the orchestrator will implement the granted read-only inspection/source tools and whether the owner will manually grant Accessibility/Screen Recording. Without those, UI snapshots and true current foreground/tab inspection remain blocked; browser and AppleScript paths still work for permitted operations.

