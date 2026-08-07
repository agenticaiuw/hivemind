# Harness derivation — browser-extension — round 102

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-runtime** — Safari extension is currently offline; /browser/status reports only offline home-chrome and 9 pending commands, while browser session store has three stale sessions (last used 06:26 UTC). No authenticated page action can complete until the real Safari extension heartbeats again.
  - evidence: GET /browser/status => online:false, home-chrome offline, pendingCommands:9; GET /browser/sessions => default/probe sessions last used 06:26 UTC.

## Capabilities it proposed

### "“From the page I’m looking at, make me a concise brief, save it into my active project, and if there are next steps draft them for me—but do not submit or send anything.”"
- **useful because:** This is a genuinely browser-specific workflow: the extension can read the owner’s already-authenticated private page, the relay/pendant can turn a spoken request into a low-friction command, and the Mac can persist the result in the active project. The owner gets a useful, cited record and ready-to-review drafts without copying sensitive content between apps or risking an accidental submission.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use the realtime tier only to resolve the short spoken intent and confirm the target tab; use a cheaper background model for page extraction, summarization, and next-step drafting. The Mac planner performs persistence and returns a receipt.
- **latency:** Acknowledge by voice in under 1 second; page extraction and brief in 5–15 seconds; save and receipt within 3 seconds after extraction. If Safari is offline, say so immediately and leave the request queued rather than pretending it ran.
- **cost:** Typically one short realtime turn plus one background extraction/summarization call; roughly $0.01–$0.08 per invocation depending on page length. Browser and Mac routing dominate latency, not tokens.
- **security:** Private authenticated page text leaves Safari for the local agent and model; minimize payload to the selected tab and redact passwords, payment fields, and session tokens. Never submit, send, purchase, or change account state. Show the exact draft and destination before any future send-capable extension. Store only the cited brief and user-approved drafts, with deletion controls.
- **missing:** A functioning browser command enqueue implementation (all currently granted enqueue schemas still report no implementation); A reliable Safari heartbeat/reconnect path and stale-command expiry; current status is offline with 9 pending commands; A typed orchestration job that chains active-tab extraction → background brief/draft → active-project write, with tab/session affinity and deduplication; A redaction pass for sensitive form fields before page content reaches summarization; A review surface on pendant/dashboard showing citations, draft text, destination, and explicit submit action (submit remains outside this capability)

### "“Using the private sites I’m already logged into, compare my available options, choose the best one by the constraints I give you, and fill every form up to the final submit screen. Read the completed details back to me and leave it waiting for my approval.”"
- **useful because:** The owner cannot get this today without manually copying sensitive information between several authenticated websites. This would turn the pendant into a private, cross-site preparation assistant: it can inspect account-specific offers, reconcile them, and stage a complete transaction while preserving the owner’s control over the irreversible final step.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Realtime handles the spoken constraints, clarification, and final read-back only. A cheaper background model performs structured extraction and comparison; the Mac planner executes deterministic browser steps and maintains the workflow state.
- **latency:** Acknowledge intent in under 1 second; compare 2–5 authenticated sites in 15–45 seconds; stage forms in under 60 seconds where sites permit. Pause immediately on login challenges, CAPTCHA, ambiguous identity, or any final submit screen.
- **cost:** About $0.03–$0.20 per workflow, dominated by background page extraction over several sites and browser round trips; realtime usage is limited to short voice turns.
- **security:** Account pages, personal identifiers, and partially completed forms pass through the local bridge and model; redact secrets and payment credentials, never expose them in spoken output or logs, and keep site/session affinity. No purchase, send, enrollment, or final submission is performed. The dashboard must show every selected option, field value, destination, and source citation before the owner can approve a separate action.
- **missing:** A durable cross-site workflow state machine that can resume across tabs and browser reconnects without replaying mutations; Structured extraction and comparison schemas for account-specific offers, constraints, and provenance; A form-staging layer that can fill and validate fields but marks the final irreversible control as a hard stop; A secure redaction boundary for credentials, payment fields, and personal identifiers before model context or receipts; A dashboard/pendant review protocol that presents the complete pending transaction and supports an explicit owner approval handoff


## Changes it proposed to its own stack

### `browser-harness` — Add an explicit browser-command lifecycle for offline Safari: commands carry createdAt, tab/session affinity, and an expiry; when the extension reconnects, stale or superseded commands are discarded with a visible receipt, while safe read-only commands may be retried once against the current active tab. Expose queue depth and reconnect state to the relay so the pendant can say exactly what is waiting.
- **owner gets:** The owner will no longer hear a request acknowledged and then receive a late result from the wrong page—or wonder whether anything happened after closing the lid. Offline periods become understandable and recoverable instead of silent failures.
- effort: Medium: extend browserBridge queue metadata, reconnect reconciliation, result receipts, and one small status projection in the relay/dashboard; add tests for restart, duplicate polling, stale tabs, and extension reconnection.  ·  risk: A page may change while offline, so automatic retry must be limited to read-only extraction and must require the same session/tab when possible. On mismatch, fail closed with a prompt to select a tab. Recovery is to replay the request explicitly; no mutation is auto-retried.
- cost: Negligible API cost; fewer wasted model calls and fewer 45-second timeout waits. Small persistent queue metadata only.  ·  latency: Immediate offline acknowledgement; reconnect processing adds under a second for queued read-only work, while expired commands return immediately.
- security: Improves security by preventing old commands from executing against a newly opened tab and by expiring sensitive page requests. Preserve existing prohibition on form submission/send actions.
- depends on: A functioning browser enqueue implementation and extension heartbeat/reconnect path; Typed command/session metadata in browserBridge/browserSessions; A durable receipt/status route for queue expiry and retry outcomes


## What it asked for

_Nothing._
## Its own summary

Discovered the new round still has no functioning browser command path: all granted enqueue tools are schemas, Safari is offline, and 9 commands are pending. The browser session store contains only stale probe tabs. I recorded this finding, proposed a new cross-surface capability (voice request → authenticated page brief → active-project save with unsent drafts), and proposed offline command lifecycle handling. I notified mac-planner not to wait on browser actions.

**Biggest unknown:** Whether the real Safari extension can be brought online/reconnected this round, and whether the orchestrator will implement the enqueue endpoint rather than granting another schema.

