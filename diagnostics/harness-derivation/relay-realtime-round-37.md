# Harness derivation — relay-realtime — round 37

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working on that task after I leave, and tell me exactly what happened when it’s done."
- **useful because:** The owner can start something from the pendant, then walk away. They still get a clear, spoken outcome later without needing to keep the Mac awake or stay in the loop.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime for the initial voice exchange; cheaper planner/executor for the job itself; relay status tool for the final spoken result.
- **latency:** Fast response at start (under a second to acknowledge). Completion can take minutes; status check is quick and works even if the Mac is asleep after handoff.
- **cost:** Low for the relay status check; main cost is the Mac planning/execution and any browser automation when it’s online.
- **security:** Only report what the job status tool says. Don’t fabricate completion. For browser work, ensure the bridge is online and authenticated; avoid sending data off-device unnecessarily.
- **missing:** Durable job runner that persists and resumes work across relay restarts; Unified job IDs across pendant/relay/Mac for reliable references; A notification path to the pendant when a job completes (push or poll)

### "Keep watching this authenticated browser page for a meaningful change, and tell me on the pendant as soon as it happens—include what changed and a link, but stay silent on cosmetic changes."
- **useful because:** The owner can delegate a condition-based watch while away from the Mac, something a one-shot browser action or reminder cannot do. The relay can notify immediately over the worn pendant, while the browser session can reach sites the relay cannot.
- **path:** pendant → relay → browser → dashboard
- **model tier:** Use the relay-realtime model only for the initial spoken setup and final concise notification. Use a cheaper background classifier for page snapshots/diffs; use deterministic DOM/text normalization before invoking a model, and mac-planner only if the owner asks for a follow-up action.
- **latency:** Initial setup response under 1 second. Poll or event checks may be minute-scale depending on the site; notification within one check interval, with a short retry/backoff for transient failures.
- **cost:** Low per watch check: browser execution and storage dominate; invoke the background model only for ambiguous semantic diffs. A typical watch should cost substantially less than a realtime turn, but exact cost depends on interval and page size.
- **security:** Authenticated page contents, cookies, and extracted diffs leave the browser device/session boundary and are retained only for the active watch and short audit receipt. Require explicit confirmation when creating a watch on a sensitive origin, redact secrets from diffs, bind each watch to the owner's device/session, expire it automatically, and provide a one-button stop command. Never perform mutations as part of checking.
- **missing:** A durable browser-watch service with per-watch leases, origin/session binding, and Cloudflare Durable Object alarms or an equivalent scheduler; Browser harness support for repeatable authenticated snapshots, change normalization, and typed extraction without exposing cookies; A relay-to-pendant push notification path with deduplication, quiet hours, and offline retry; Semantic diffing plus a compact receipt containing timestamp, changed fields, and deep link; Owner controls in the dashboard and spoken commands to list, pause, resume, and cancel active watches

### "Finish this task across my Mac and my signed-in browser even if one side drops offline; if a step fails, recover or continue from the last verified step and tell me exactly what remains."
- **useful because:** Today a spoken request handed to one downstream surface can strand the owner halfway through a multi-system task, especially because the pendant is worn away from the Mac. A durable, resumable workflow would make the hive behave like one agent rather than disconnected one-shot tools.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use realtime only to capture the goal and report state changes. A cheaper planner should compile the goal into a typed workflow; deterministic state checks and receipts should drive retries. Escalate ambiguous recovery decisions to the realtime front door only when the owner is waiting.
- **latency:** Acknowledge acceptance immediately. Resume within seconds after a node reconnects; individual external operations may take tens of seconds. Report failures promptly rather than holding the voice turn open.
- **cost:** Planner cost once per workflow plus low-cost state checks; retries and browser/Mac execution dominate. Persisting compact checkpoints is cheaper than resending the entire conversation on every turn.
- **security:** Workflow state may contain private app and browser data. Encrypt checkpoints, scope credentials to the existing session, redact values from spoken notifications, and make recovery idempotent. Since owner policy allows trusted execution, do not add approval gates; instead expose a clear action log and an unconditional cancel button.
- **missing:** A durable workflow/saga runner with checkpoints, idempotency keys, dependency-aware retries, and explicit compensating actions; Typed adapters that can verify postconditions on both Mac and authenticated browser sessions; A reconnect protocol for the pendant, relay, Mac agent, and browser extension with exactly-once status delivery; A compact cross-surface state model so the planner need not resend full history; Dashboard and spoken controls for inspect, pause, cancel, and resume

### "When I press the pendant, bookmark what I was doing; later show me the nearby Mac and browser activity, the relevant transcript, and a short explanation of what this moment was about."
- **useful because:** A physical bookmark works when the owner is away from the Mac and cannot type or open an app. Joining the pendant's timestamp with Mac activity and authenticated browser context creates a personal timeline and makes interruptions recoverable, rather than merely storing an isolated voice note.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use firmware for an immediate timestamp/LED acknowledgment and the relay for the short spoken confirmation. A background model can summarize the correlated activity; deterministic timestamp correlation and redaction should happen first. Realtime is unnecessary for later timeline queries unless the owner is actively asking by voice.
- **latency:** Button acknowledgment under 200 ms locally. Capture and correlation can complete asynchronously within a few seconds after nodes report. Timeline lookup should answer in under 3 seconds for a recent bookmark.
- **cost:** Small storage and event-ingestion cost; background summarization only when a bookmark is opened or requested. Correlation and indexing should be deterministic and cheap.
- **security:** This deliberately joins sensitive microphone, application, and browser history. Encrypt records, default to a short retention period, keep raw audio optional and deletable, redact credentials and page secrets, and make the bookmark private to the paired owner/device. Do not transmit ambient audio unless the owner explicitly starts a voice capture.
- **missing:** A firmware bookmark event and durable local queue that survives a dropped LTE link; Relay ingestion for signed bookmark events with monotonic timestamps and deduplication; Mac and browser activity adapters that emit privacy-filtered foreground/app/page events; A time-correlated encrypted event store and retention/deletion controls; A background summarizer and dashboard/voice query surface for bookmark retrieval


## Changes it proposed to its own stack

### `integration` — Add a durable, cross-surface job runner with unified job IDs, receipts, and completion notifications. The relay hands off work, the Mac/browser execute when available, and the relay can always answer "what happened" from a shared job store. Completion triggers a small notification to the pendant with a ready-to-speak summary.
- **owner gets:** They can ask for something, leave, and still get a reliable outcome later. No more guessing whether something finished, failed, or never started because a bridge was offline.
- effort: Medium to high. Needs a shared job store, lifecycle state machine, retry rules, and small notification plumbing.  ·  risk: Duplicate execution or phantom completion if idempotency and receipts aren’t correct. Mitigate with idempotency keys, receipts, and explicit state transitions.
- cost: Moderate. Storage and a few extra API calls per job; cheapest tier should do most of the work.  ·  latency: Improves perceived latency by acknowledging quickly and finishing asynchronously. Adds minimal overhead to status checks.
- security: Job data may include sensitive content; encrypt at rest, minimize stored payloads, and redact summaries. Tie access to device pairing.
- depends on: Durable storage for job state (e.g., Durable Object or D1); Notification mechanism to pendant (push or periodic poll); Idempotent action receipts across Mac and browser harnesses


## What it asked for

_Nothing._
