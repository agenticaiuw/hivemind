# Harness derivation — faculty-judgement — round 92

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m leaving my desk” — save exactly where I am, tell me what I’m walking away from, and when I return give me a one-sentence restart plan with the right tabs and files ready."
- **useful because:** Leaving mid-task currently scatters context across the Mac, private browser tabs, and the pendant. This creates a durable, privacy-scoped handoff: the pendant confirms the capture, the Mac records the active work surface using granted AppleScript/browser primitives, and the relay keeps it alive across sleep or a dropped link. On return, the owner gets only the next useful action rather than reconstructing their day.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Use the cheap/background model to summarize and rank the captured work state; use realtime only for the short spoken confirmation and return prompt. No expensive model is needed for ordinary capture or restore.
- **latency:** A spoken leaving confirmation in under 2 seconds; background snapshot and summary within 10 seconds. Return brief under 3 seconds, with reopening tabs/files continuing asynchronously.
- **cost:** Typically <$0.01 per leave/return cycle; dominated by one small summarization call. Mac/browser capture and relay persistence are local/low-cost.
- **security:** Capture only titles, URLs, paths, and explicitly selected snippets—not page bodies by default. Keep private-tab data encrypted and TTL-limited; exclude passwords and secrets. Reopening a tab is reversible, but never send, submit, or modify anything. Require a spoken/button confirmation before restoring a potentially sensitive tab on a shared display.
- **missing:** A first-class cross-surface handoff record with owner-selected TTL and redaction policy; A reliable ‘desk departure/return’ trigger from pendant voice/button and optional Mac idle signal; Mac active-app/document capture through the already-granted AppleScript routes, plus browser tab/session snapshot; A restore operation that reopens only the selected reversible tabs/files and reports omissions when a surface is offline

### "“If I don’t hear back from them by Friday, remind me and draft the right follow-up.”"
- **useful because:** The owner can state a conditional intention once instead of remembering to check a thread. The system watches only the named conversation, recognizes a genuine reply rather than any mailbox activity, cancels the pending follow-up when the reply arrives, and otherwise prepares a reviewable draft without sending it.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → unified
- **model tier:** Use a cheap background model for thread matching and draft preparation; use realtime only for the concise pendant notification. Escalate to the expensive tier only when the thread is ambiguous or multiple contacts match.
- **latency:** Reply detection can be scheduled/polled in the background; notify within 5 minutes of the deadline or reply. Draft preparation under 30 seconds after the deadline. No foreground wait.
- **cost:** <$0.05 per active condition per week, mostly authenticated page checks and one short draft generation; near-zero pendant/relay cost.
- **security:** Bind the condition to an explicit account, thread URL/message ID, person, and deadline; do not infer a target from a broad mailbox search. Read-only monitoring by default. Draft but never send; sending remains behind the existing destructive-action confirmation. Store only a normalized reply fingerprint and minimal quoted context with a short retention period.
- **missing:** A durable conditional-watch primitive with deadline, cancellation event, thread identity, timezone, and recurrence policy; Semantic reply detection that distinguishes an actual response from labels, receipts, or automated notifications; A deadline notification and draft-review handoff that survives relay/Mac/browser outages and reports source freshness

### "“Find subscriptions and recurring charges I’m probably not using, show me the evidence, and prepare cancellations—but don’t cancel anything yet.”"
- **useful because:** The owner currently has to remember every service, compare billing evidence across private account pages and local statements, and find each cancellation flow manually. This would turn a vague financial-maintenance task into a sourced review queue: identify likely duplicates or unused services, explain the evidence and confidence, and prepare—but never execute—cancellations for the owner’s approval.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant → unified
- **model tier:** Use a background/cheap model for normalization, duplicate detection, and evidence grouping. Use realtime only to answer a question or read a short review item aloud; never spend the expensive tier on bulk scanning.
- **latency:** Scan and normalize in the background over 5–15 minutes, with progress receipts. Present the first five review items in under 3 seconds when requested. Preparing an individual cancellation packet can take up to 30 seconds.
- **cost:** Roughly $0.10–$0.50 per monthly scan depending on the number of pages and local files; browser reads and local statement parsing dominate, not speech.
- **security:** Treat financial records and account pages as highly sensitive. Require explicit account/domain scope, redact full card and account numbers, retain only merchant/amount/date/evidence hashes, and expire raw captures quickly. Never click a final cancellation or downgrade control automatically; each packet must show the exact service, renewal terms, consequence, and final action target for confirmation. If evidence is stale or a page is inaccessible, mark it unknown rather than infer.
- **missing:** A cross-source recurring-charge ledger that can safely merge local statement rows with browser-verified subscription records while preserving provenance; A semantic classifier for unused/duplicate services with explainable evidence and confidence, not merely name matching; A cancellation-packet compiler that records the reversible steps and stops at the irreversible control; A privacy-scoped review queue with per-item retention and explicit owner approval tokens


## What it asked for

### `t24-vgln` (tool) — conditional_followup_watch
- why: Owner should be able to state a deadline-dependent intention once: monitor one identified private thread, cancel on a genuine reply, and otherwise create a reviewable follow-up draft. Existing page watches detect changes but do not model a condition, cancellation event, deadline semantics, or draft handoff as one durable object.

```json
{
  "accountSessionId": "string",
  "threadId": "string",
  "threadUrl": "string",
  "contactIdentity": "string",
  "deadline": "ISO-8601 timestamp",
  "timezone": "IANA timezone",
  "condition": {
    "kind": "no_genuine_reply",
    "ignoreAutomated": true
  },
  "onDeadline": {
    "action": "draft_followup",
    "send": false,
    "tone": "string"
  },
  "notify": {
    "surface": "pendant",
    "leadMinutes": 0
  },
  "retentionDays": "number"
}
```

## Its own summary

Discovered owner state and live surfaces: the Mac bridge is online, Chrome is offline, and the owner’s current priority remains end-to-end 24 kHz audio. I recorded two owner-facing capabilities: (1) a desk-departure/return continuity handoff across pendant, Mac, private browser, and relay; (2) a genuinely distinct conditional follow-up watch that monitors one identified thread, cancels on a real reply, and otherwise drafts (never sends) a follow-up at a deadline. I also queued the missing `conditional_followup_watch` tool schema. What is still needed is implementation of durable conditional watches, semantic reply matching, source-freshness reporting, and explicit cross-surface handoff records; current routes are connective pieces, not the atomic guarantees.

**Biggest unknown:** Whether the existing browser watch/job implementations can bind to stable message/thread IDs and detect genuine human replies without adding the proposed conditional-watch primitive; Chrome is currently offline, so this cannot be validated live.

