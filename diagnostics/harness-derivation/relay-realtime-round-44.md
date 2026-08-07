# Harness derivation — relay-realtime — round 44

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Keep working on that after I walk away, then tell me exactly what happened when it’s done."
- **useful because:** This is the everyday “don’t make me babysit it” experience: start something by voice, let the system finish across Mac and browser, and get a clear, evidence-backed completion report later.
- **path:** pendant → relay → mac-bridge → browser → relay
- **model tier:** Realtime for the initial voice handoff; cheaper planner/model on the Mac for long-running work; browser harness for authenticated pages; relay for status fan-in and spoken receipt.
- **latency:** Under a second to acknowledge and hand off; minutes to hours for completion, with updates only when meaningful.
- **cost:** Low at the relay except for transcripts and receipts; most cost sits in Mac planning/execution and browser extraction when pages are large or change frequently.
- **security:** Reads and extracts from authenticated sessions; must store provenance and avoid leaking sensitive content into generic logs. No blocking gates, but every irreversible action must be visible in the receipt.
- **missing:** A durable job runner with resumable steps and idempotency keys; A typed, provenance-aware result receipt that can be spoken and linked back to evidence; Background scheduling/alarms (Worker cron or Durable Object alarms) for retries and timeouts; A browser command queue that preserves session affinity and typed results

### "“Finish that task and tell me the result the next time I press the pendant button—even if I’m away from my Mac.”"
- **useful because:** Today a spoken request can be handed to the Mac or browser, but completion is not a durable, owner-facing conversation. This would turn asynchronous work into a reliable loop: the pendant records that a result is waiting, the owner gets a short spoken outcome on their next interaction, and they can immediately ask a follow-up without remembering a job ID.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the realtime model only for the initial utterance, wake-button response, and final spoken rendering. Use the cheaper Mac planner/browser workers for execution; use a background summarizer for long receipts and citations.
- **latency:** Initial acknowledgement under 1 second; execution can take as long as needed. On the next button press, play a cached result immediately (under 300 ms), then stream detail or a follow-up response.
- **cost:** Roughly one realtime turn for acknowledgement plus one short realtime turn for delivery; background summarization and execution dominate only when the task produces large receipts or page content.
- **security:** Persist only the task capsule, completion summary, and source references—not raw page content or secrets. Encrypt the pending-result queue, bind it to the paired pendant, expire stale results, and require an explicit spoken/button action before reading sensitive content aloud in public.
- **missing:** A durable, per-pendant pending-result queue with ordering, expiry, and unread state; A completion callback from Mac/browser workers to the relay carrying typed result, citations, and failure state; Pendant firmware support for an unread-result LED pattern and button-triggered result retrieval, including offline caching; A relay conversation state that associates a follow-up utterance with the delivered result rather than starting a new unrelated session; A compact privacy classification so the relay can say “I have a sensitive result waiting” without speaking its contents automatically

### "“Stop the task I started a minute ago.”"
- **useful because:** When the owner is away from the Mac, a delegated browser or Mac workflow can continue after circumstances change. Today the pendant has no dependable way to identify and cancel the active downstream work. A physical/voice cancellation path prevents stale searches, runaway workflows, and actions that are no longer wanted.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** No expensive reasoning is needed: relay performs deterministic active-task lookup and cancellation; workers acknowledge and checkpoint. Use the realtime model only if the owner’s spoken cancellation is ambiguous, and use a cheap background model to summarize what was stopped.
- **latency:** Button-based cancellation acknowledgement under 500 ms; worker cancellation propagation under 2 seconds where supported. If a worker cannot stop immediately, the pendant should say that it is stopping and report the last completed step.
- **cost:** Near-zero model cost for button cancellation; occasional cheap summarization. Main cost is a small control message and durable cancellation record.
- **security:** Cancellation must be scoped to the paired owner/device and must never be interpreted as authorization to undo completed external effects. Store an audit receipt distinguishing cancellation requested, cancellation acknowledged, and work already committed.
- **missing:** A pendant long-press gesture and distinct cancel LED/audio acknowledgement; An active-task registry in the relay with owner/device/session binding and task state; A cancellation endpoint and cooperative cancellation tokens in Mac and browser workers; Checkpoint semantics that prevent new actions after cancellation while accurately reporting already-completed actions; A deterministic spoken disambiguation path when multiple tasks are active

### "“Queue this for my Mac and do it when it comes back online.”"
- **useful because:** The pendant is often used away from the Mac, so a useful request currently dies or becomes a note when the Mac is offline. This gives the owner a real handoff: capture intent now, execute automatically on the first authenticated Mac reconnect, and report success or failure back to the pendant.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Realtime handles only intent capture and a brief acknowledgement. A cheaper background planner validates and normalizes the task capsule; the Mac planner executes on reconnect and a cheap summarizer prepares the completion notice.
- **latency:** Capture and acknowledgement under 1 second while offline. Start execution within 10 seconds of a healthy Mac heartbeat; delivery of the result follows the pending-result channel rather than requiring the owner to watch the Mac.
- **cost:** One short realtime turn at capture and one at result delivery; idle queue storage and heartbeat traffic are negligible. Execution/model cost occurs only when the Mac reconnects.
- **security:** Queued requests may contain private paths, accounts, or commands. Encrypt capsules, bind them to the paired Mac and pendant, show a clear queued-task count, expire capsules, and classify tasks so a reconnect cannot silently repeat a previously committed action. Preserve owner’s no-confirmation preference for reversible work while recording receipts.
- **missing:** A durable offline-intent queue with explicit ordering, expiry, and idempotency keys; Mac reconnect/heartbeat event that claims queued capsules exactly once; A planner preflight that detects stale assumptions before execution and returns a typed blocked/stale result; Integration with the durable pending-result delivery and cancellation protocols; A visible dashboard view for queued, claimed, completed, and expired requests


## Changes it proposed to its own stack

### `integration` — Add a durable completion-event protocol spanning relay, Mac planner, computer-use/browser workers, and pendant: each delegated request receives a signed task capsule containing the owner’s original utterance, response style, sensitivity class, and callback endpoint. Workers publish typed completion/failure events with concise summary, evidence references, and retryability; the relay stores an ordered unread queue and exposes only the next capsule to the pendant when its button is pressed. A follow-up utterance carries the capsule ID so the relay can continue the task conversation instead of losing context.
- **owner gets:** They can say “handle this” while walking away and trust that the result will still reach them later, without monitoring a dashboard, memorizing job IDs, or repeating the original request.
- effort: Medium-high: protocol/schema and durable storage in the Worker, callback instrumentation in Mac/browser workers, pendant retrieval/acknowledgement firmware, and end-to-end offline/reconnect tests.  ·  risk: Duplicate callbacks, out-of-order completion, or stale sensitive results could confuse or expose the owner. Use idempotency keys, sequence numbers, expiry, explicit acknowledgement, encrypted storage, and a recovery path that replays only unacknowledged capsules.
- cost: Small Worker storage and callback overhead; one short realtime synthesis per delivered result. No continuous model polling should be added.  ·  latency: No added latency to execution; first spoken result after button press should be near-instant from cached summary, with detail fetched afterward.
- security: Creates a new durable store for potentially sensitive outcomes, so pair it to the device identity, encrypt at rest/in transit, classify sensitivity, and avoid storing raw authenticated page contents by default.
- depends on: A durable relay queue or Durable Object storage; Typed completion callbacks from Mac and browser execution surfaces; Pendant firmware button/LED result retrieval and acknowledgement; A stable task/capsule identifier propagated through plan and execute APIs


## What it asked for

_Nothing._
## Its own summary

Recorded four new, cross-surface proposals: durable spoken completion delivery, a signed task-capsule completion protocol, pendant-driven cancellation, and queue-until-Mac-reconnect execution. Together they cover work initiated while the owner is away, without requiring dashboard monitoring or remembered job IDs.

**Biggest unknown:** Which existing Mac/browser worker lifecycle hooks can emit authenticated completion, cancellation, and reconnect events; implementation should inspect those surfaces rather than assume current job APIs provide them.

