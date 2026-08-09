# Harness derivation — relay-realtime — round 176

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Summarize what’s on my screen and help me decide the next step."
- **useful because:** This blends what only the Mac can see (screen/app context) with what only the relay can provide (fast back-and-forth conversation). It’s a true hive-mind feature.
- **path:** pendant → relay → mac-vision → mac-bridge
- **model tier:** realtime for dialogue; mac-vision model for screen understanding; cheaper model for summarization if available
- **latency:** Quick initial response (<2 seconds) with a follow-up summary within a few seconds depending on screen capture.
- **cost:** Moderate. Screen capture and analysis dominate; dialogue is incremental.
- **security:** Screen content can contain secrets (tokens, emails). Default to masking sensitive fields and avoid copying text unless asked.
- **missing:** A reliable screen capture pathway in mac-vision (computer-use loop is currently disabled); A structured channel to return typed observations (not just free-form text); Policy for redaction/masking and user confirmation before acting

### "Keep an eye on this page for changes and tell me when it matters."
- **useful because:** The owner can set a watch from voice, the browser holds the authenticated session, and the relay delivers an alert later. No single node can do that alone.
- **path:** relay → browser → mac-bridge → pendant
- **model tier:** cheap background model for diffing and prioritization; realtime only to set up and deliver the alert
- **latency:** Setup should be immediate. Change detection can run periodically; alert delivery should be near-real-time once detected.
- **cost:** Ongoing cost depends on check frequency. Dominated by page fetch/DOM diff and alert delivery.
- **security:** Watched pages may be authenticated. Ensure watch rules are stored safely and avoid leaking content to logs. Provide clear stop controls.
- **missing:** A scheduler (cron/DO alarms) to run watches without a live conversation; A background watcher service and storage for watch rules; A notification path to the pendant/paired device with queueing

### "“Tell me the one thing I need to know right now, and why.” Then, if I say “handle it,” do it across whichever app or browser session contains the source."
- **useful because:** This would turn the pendant into a genuinely useful front door rather than a voice remote: it fuses fresh signals from Mac apps, authenticated browser tabs, and my prior voice context, explains conflicts and uncertainty in one sentence, and can continue into action without making me repeat the context.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime only for the spoken question and final answer; a cheaper background synthesis model should merge the Mac/browser evidence and rank urgency, while mac-planner or mac-vision performs the selected action.
- **latency:** Initial spoken answer within 5 seconds; source collection may continue asynchronously, with a concise correction pushed to the pendant if a slower authenticated source changes the ranking.
- **cost:** Roughly $0.02–$0.10 per query depending on how many source summaries are fetched; most cost is the synthesis model and browser/Mac evidence extraction, not the short relay turn.
- **security:** Only metadata and explicitly selected excerpts should leave each surface; authenticated page contents must remain in the browser harness. The relay must attach source, timestamp, and confidence to every claim and never silently treat stale evidence as current. “Handle it” must target the exact evidence-backed item, not a similarly named one.
- **missing:** A fan-out query that asks Mac and browser surfaces for typed, timestamped candidate items in parallel; A relay-side evidence merger that detects duplicate items and contradictions rather than merely concatenating summaries; A continuation handle binding the spoken follow-up to the selected item; A durable event path for late corrections

### "“Undo the last thing you did.” If the last request changed more than one app or browser tab, restore every reversible part and tell me exactly what could not be restored."
- **useful because:** A wearable command surface is otherwise dangerous to trust: when I am away from the Mac I cannot inspect what happened. A spoken, cross-surface undo would make remote action recoverable instead of forcing me to open the Mac and reconstruct the mistake manually.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles the short lookup and explanation; a cheap deterministic inverse-action engine should compute rollback from receipts, with mac-planner/mac-vision executing only the inverse operations.
- **latency:** Read the candidate action and speak its scope in under 2 seconds; begin rollback immediately after the utterance, then push a completion or partial-failure summary.
- **cost:** <$0.02 for the relay turn; inverse planning is mostly deterministic. Cost is dominated by any vision re-check needed to verify a browser mutation.
- **security:** Never claim success without postcondition checks. Irreversible actions (sent messages, external purchases, deleted data without trash) must be reported as non-restorable, not simulated as undone. Keep an append-only receipt with before/after hashes and redact content in the dashboard.
- **missing:** Every executable action needs a typed inverse or an explicit non-restorable classification; Pre-action snapshots for browser form state and mutable Mac records; A cross-surface transaction identifier joining /plan, /execute, browser commands, and receipts; An idempotent rollback endpoint with postcondition verification

### "“Whenever a new invoice arrives in my authenticated vendor portal, extract the amount and due date, add it to my Mac reminders, and tell me only if it is unusual.” I should be able to create, inspect, pause, and delete that rule from the pendant."
- **useful because:** This is the first capability that genuinely works while I am away: the browser session sees information that Mail and Calendar cannot, the Mac can put it into the owner's working system, and the always-awake relay can keep the rule alive without a voice session.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** Use a cheap background/event model for extraction and anomaly comparison; use realtime only to create or modify the rule and speak exceptions. Use deterministic parsers for currency, dates, and reminder creation.
- **latency:** Rule creation should be acknowledged in under 3 seconds. A matching portal event should notify the pendant within 1 minute of the browser heartbeat; normal matches stay silent.
- **cost:** About $0.01–$0.05 per portal change, dominated by authenticated page extraction and model fallback for unfamiliar invoice layouts; unchanged heartbeats should be near-zero model cost.
- **security:** The rule must be scoped to one origin, one authenticated session, and named fields; never upload whole pages by default. Store extracted amounts and hashes, not credentials. Surface the exact source URL and timestamp with every alert, and provide a spoken “pause vendor rule” escape hatch.
- **missing:** A durable event-rule store and worker using Durable Object alarms or equivalent; Browser session/page-watch support for authenticated, origin-scoped change detection and field extraction; A relay-to-Mac action path that creates or updates reminders from a validated event payload; A rule management UI plus pendant commands for listing, pausing, and deleting rules; A deduplication and anomaly baseline so repeated portal renders do not create duplicate reminders


## Changes it proposed to its own stack

### `relay` — Implement a real completion notification pipeline: a durable watcher that listens for job receipts/state changes, renders a short spoken summary, and delivers it to the pendant/paired device with offline queueing and expiry.
- **owner gets:** They can start something and leave; the system reports back when it matters, without polling.
- effort: High. Needs a durable object or queue, receipt polling, summary generation, and a delivery mechanism.  ·  risk: Wrong or over-detailed summaries could leak sensitive info; mitigations include redaction and a max-length spoken template.
- cost: Moderate ongoing compute for polling or event handling; storage for queued notifications.  ·  latency: Completion is asynchronous; delivery should be near-real-time after job state changes.
- security: Sensitive outputs must be filtered; only minimal status should be spoken by default.
- depends on: A real implementation of relay_event_push or an equivalent endpoint; A delivery path to pendant/paired device that can store-and-forward

### `mac-harness` — Add a typed, structured observation channel for mac-vision/mac-planner to return safe summaries (e.g., redacted text, UI element labels, risk flags) instead of raw screen text.
- **owner gets:** They get helpful guidance without accidentally reading secrets aloud or taking risky actions.
- effort: Medium. Requires schema definition, redaction rules, and enforcement in the computer-use loop when it’s enabled.  ·  risk: If schema is too strict, it becomes unusable; too loose and it leaks data. Iterate with telemetry.
- cost: Low to moderate; mostly model tokens and serialization.  ·  latency: Small overhead to summarize and serialize.
- security: Improves privacy by design via masking and classification.
- depends on: Computer-use loop availability or a fallback inspection mechanism


## What it asked for

_Nothing._
