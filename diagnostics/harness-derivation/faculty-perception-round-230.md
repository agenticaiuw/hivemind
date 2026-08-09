# Harness derivation — faculty-perception — round 230

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser reachability** — At 2026-08-09T01:04Z the Mac local agent reports Accessibility and Screen Recording granted, all required permissions ready, relay reachable with D1 store and Mac bridge online, and Safari browser extension online with 5 tabs; the focused tab is https://tools.usps.com (USPS Tracking).
  - evidence: read_continuity_snapshot(include=['relay','pipeline']) resolved to GET /ops/snapshot, HTTP 200; returned permissions.ready=true, relay.reachable=true, relay payload store='d1', browser.online=true, tabCount=5, tabUrl='https://tools.usps.com'.

## Capabilities it proposed

### "“Tell me only what needs my attention right now, and interrupt me on the pendant if it is genuinely urgent.”"
- **useful because:** This would be the system’s most useful everyday behavior: it suppresses routine noise, detects failures and expiring opportunities across the Mac, browser, relay, and scheduled work, and chooses a spoken interruption only when the owner’s current context and urgency justify it. Unlike a briefing or continuity digest, it is a continuously evaluated exception policy with an explicit reason for every interruption or suppression.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → unified → dashboard
- **model tier:** background for polling/classification; realtime only to phrase a confirmed urgent alert
- **latency:** Detect within 2 minutes for routine failures and within 10 seconds for browser/session or relay outages; one short spoken alert under 5 seconds
- **cost:** Low: mostly rules and event diffs; occasional cheap classifier call, roughly <$0.01 per evaluation batch; realtime cost only for delivered alerts
- **security:** Must not read page bodies or message contents merely to decide urgency; use titles, deadlines, job states, and explicit owner policy. Mail sends, purchases, deletion, and external sharing remain confirmation-gated. Persist an audit row explaining why an alert was sent or suppressed.
- **missing:** A durable cross-surface exception policy with owner-configurable urgency classes and quiet hours; A live event subscription or bounded polling cursor for browser, Mac jobs, routines, and relay health; A pendant delivery path and device-originated playback evidence; currently no pendant is registered

### "“When I come back to the Mac after it or the relay has been offline, get me back to exactly the work I was doing—without repeating an action or claiming something finished unless you can prove it.”"
- **useful because:** The owner currently has online Mac, browser, and relay state but no reliable causal handoff between them. This creates a resumable work session: it records the last safe checkpoint, open browser target, pending Mac job, and relay reachability, then reconstructs a compact next-step card after reconnect. It is not a digest; it is a replay-safe transaction handoff that prevents duplicate sends and false completion.
- **path:** mac-planner → browser-extension → relay-realtime → pendant → unified → dashboard
- **model tier:** background deterministic state machine; cheap model only to summarize the checkpoint; realtime is unnecessary
- **latency:** Checkpoint updates under 1 second after an action; recovery card available within 3 seconds of reconnect
- **cost:** Negligible model cost for normal operation; occasional small summarization call, under $0.005 per recovery
- **security:** Checkpoint content must redact secrets and page bodies by default, preserve confirmation state for destructive actions, and never replay a side effect without a fresh owner approval. Browser session identifiers stay local to the Mac; relay receives opaque checkpoint IDs and hashes.
- **missing:** A single durable checkpoint schema joining Mac action ledger, browser command/receipt, relay job, and routine run IDs; A compare-and-set resume endpoint that can prove an action was not already committed; A pendant connection and playback/ack channel; today the registry has only the Mac bridge and a missing pendant is not evidence of outage

### "“If two parts of my digital life disagree, stop and tell me what conflicts instead of choosing one silently.”"
- **useful because:** The current system can see a live Safari USPS page, Mac state, scheduled routines, and relay state, but each surface can report a different reality. A contradiction alarm would compare independent observations (for example browser tracking versus a reminder or a completed job versus a still-pending relay delivery), identify the exact fields and timestamps that disagree, and ask one focused question. This prevents confident but wrong actions.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → unified → dashboard
- **model tier:** deterministic normalization and timestamp comparison first; cheap model only for human-readable conflict wording
- **latency:** Evaluate immediately after a browser result, job receipt, routine completion, or relay reconnect; explain in under 2 seconds
- **cost:** Near-zero for structured comparisons; occasional <$0.002 wording call; no realtime call unless the owner asks by voice
- **security:** Compare metadata and explicitly authorized fields, not arbitrary private page contents. Keep both observations, source, timestamp, and freshness; never overwrite either source. Destructive action is blocked until the owner resolves the conflict.
- **missing:** A normalized observation record with source, capturedAt, freshness, and confidence across browser, Mac, and relay; A conflict-resolution interaction that records the owner’s choice without rewriting the underlying evidence; A connected pendant path for immediate spoken escalation; the current live fleet has no pendant

### "“When I say I’ll do something, turn it into a private commitment that can verify completion from the right surfaces and remind me only when the evidence says I still owe it.”"
- **useful because:** Today the system can create reminders and execute isolated browser or Mac actions, but it cannot distinguish a casual statement from a promise, define what would count as completion, or verify that completion later. This capability would turn spoken intent into a bounded commitment contract: the owner’s wording, deadline, acceptable evidence, escalation policy, and a reversible reminder. For example, after “I’ll submit this USPS claim by Friday,” the browser can verify the submission state and the Mac can retain the deadline without the system falsely treating a reminder creation as success.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → dashboard
- **model tier:** realtime extracts the owner’s intent during the conversation; background model and deterministic rules monitor evidence and deadlines; no realtime model for routine checks
- **latency:** Create the draft contract during the same turn; verify evidence within 30 seconds of a relevant browser or Mac event and at scheduled checkpoints
- **cost:** Low: one short realtime extraction and mostly deterministic checks; roughly $0.01–$0.03 per created commitment depending on follow-up checks
- **security:** Commitments must remain private and default to local storage. The system must ask before creating commitments inferred from ambiguous speech, never submit forms or send messages as proof without confirmation, and show the exact evidence and timestamp behind a “done” or “still owed” state.
- **missing:** A commitment-contract store with immutable intent, deadline, evidence predicates, owner-confirmed completion, cancellation, and escalation policy; Browser and Mac evidence adapters that can evaluate predicates without retaining unnecessary page contents; A pendant transport and playback acknowledgement for timely spoken reminders; the current fleet has no registered pendant; A policy separating owner-stated commitments from model-inferred ones

### "“If this task needs choices or detail, move it from my voice to a private decision board on the screen, let me choose there, and then tell me exactly what changed.”"
- **useful because:** A wearable voice channel is excellent for intent but poor for comparing options, reviewing long text, or confirming nuanced edits. Today the browser and Mac can be driven separately, but there is no coordinated voice-to-screen handoff with a bounded decision state. This would create a temporary private board tied to the spoken turn, populate it from the authenticated browser session or Mac data, accept explicit choices, and return a concise spoken receipt of the resulting change.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → unified → dashboard
- **model tier:** realtime handles the handoff and short clarification; background model prepares comparisons and summaries; deterministic action executor applies only the selected operation
- **latency:** Open the board within 2 seconds, reflect selections under 500 ms, and speak the final receipt within 3 seconds of confirmation
- **cost:** One small realtime turn plus cheap background summarization, approximately $0.01–$0.05 per handoff; browser and Mac execution dominate latency, not tokens
- **security:** The board must be origin-bound, ephemeral by default, and inaccessible to other tabs or users. Selection is not execution: destructive actions, purchases, messages, and submissions require a separate explicit confirmation. Receipts must include target, before/after summary, and whether the action actually committed.
- **missing:** A relay-issued handoff token binding one voice turn to one browser/Mac decision board; A browser-extension surface for rendering and returning structured choices, rather than only executing commands; A shared action receipt contract across relay, browser, and Mac; A connected pendant path for the spoken completion; none is registered today


## What it asked for

_Nothing._
