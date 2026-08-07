# Harness derivation — mac-planner — round 45

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-execution-readiness** — Fresh live state: Mac agent ready=false; Accessibility trusted=false and synthesized events rejected because grant is on a different binary; ui actions report success while doing nothing. Browser extension offline with 2 pending commands. Granted mac_readonly_inspect tool currently returns 'schema but no implementation yet'.
  - evidence: GET /ops/status 200; GET /observe 200; mac_readonly_inspect(accessibility_enabled) error
- **job-receipt-truth** — GET /jobs shows recent browser_navigate attempts correctly failed because extension offline, but also a current execute job stuck processing with no receipts/result. Existing receipts capture failure but do not yet distinguish in-flight, unverified, and verified postconditions.
  - evidence: GET /jobs 200 at 2026-08-07T10:02:49Z: local_ce5882... status processing, receipts []; prior browser jobs failed with offline reason and receipt status failed.

## Capabilities it proposed

### "When I ask you to do something on my Mac, tell me truthfully whether it actually happened—and if the Mac cannot act, keep trying through the right surface and give me a useful fallback instead of claiming success."
- **useful because:** Today the action layer can generate receipts even when Accessibility is untrusted and synthesized input never reaches the screen. This would make pendant commands dependable: the relay gives one durable action ID, the Mac reports readiness and executes, an independent observer verifies the postcondition, and browser/pendant surfaces recover or explain failure.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only for the live spoken acknowledgement; use a cheaper background model for postcondition comparison, retry selection, and durable receipt summarization.
- **latency:** Acknowledge intent in under 1 second; verify ordinary Mac actions within 3 seconds; allow bounded background retries for a disconnected browser, then speak a concise failure/fallback.
- **cost:** Approximately $0.01–$0.05 per action depending on whether a background vision/text comparison is needed; most cost is the realtime acknowledgement and any screenshot/LLM verification.
- **security:** The Mac observer may expose app names, UI text, or screenshots, so redact by default and retain only hashes/structured postconditions. Do not silently retry destructive actions; preserve the owner's maximum-access policy while making retries bounded and observable. Browser session contents must stay local to the browser bridge unless explicitly requested.
- **missing:** Implement the granted mac_readonly_inspect tool (currently schema-only) for running apps, foreground app, accessibility state, UI snapshot, browser tabs, and directory listings.; Add a relay action ledger that correlates pendant request, Mac attempt, independent observation, retry, and final receipt across reconnects.; Add a postcondition observer/adapter for typed Mac actions and browser commands, with explicit attempted/unverified/verified states.; Add browser-extension reconnect reconciliation for the 2 currently pending commands and a bounded retry policy.

### "After I finish a conversation, turn the commitments I just made into a short follow-up queue: draft the emails, calendar changes, and authenticated browser updates on my Mac, then let me review and send or apply each one from the pendant."
- **useful because:** The owner currently has to remember commitments, reconstruct context, find the right app or signed-in web session, and perform each follow-up separately. This would connect the pendant's immediate conversation context with Calendar/Mail, the Mac's desktop reach, and the browser's private authenticated sessions without making the owner repeat the conversation.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only to capture the live conversation and give a brief spoken summary. Use a cheaper background model to extract commitments, resolve people/dates against bounded Calendar/Mail data, prepare drafts, and generate a compact review queue.
- **latency:** Produce the first queue within 10 seconds after the conversation ends; draft individual items in the background. Spoken review of the queue should take under 2 seconds per item, with execution receipts arriving asynchronously.
- **cost:** Roughly $0.02–$0.10 per conversation depending on transcript length and number of drafts; background extraction and bounded source reads dominate, while browser execution is mostly non-model work.
- **security:** Conversation-derived commitments and authenticated web content are sensitive. Keep the raw transcript on the relay only long enough to extract structured items, redact quoted content, and store provenance rather than full text. Email sends, calendar cancellations, purchases, and external form submissions must remain drafts until the owner explicitly confirms that specific item on the pendant; browser credentials never leave the browser bridge.
- **missing:** A commitment schema with provenance linking each proposed follow-up to a transcript span and source record.; A cross-surface draft bundle that can stage Mail, Calendar, local files, and browser-session mutations under one review ID.; Pendant controls for reviewing, skipping, editing, and confirming individual queue items without reopening the conversation.; Browser-bridge support for returning structured previews and applying one confirmed item idempotently.; A relay coordinator that survives Mac/browser disconnects and reports which follow-ups are drafted, applied, or still pending.


## Changes it proposed to its own stack

### `integration` — Implement mac_readonly_inspect as a genuinely read-only observer and wire it into action receipts: before execution record readiness (Accessibility, screen recording, browser connectivity); after execution inspect the relevant app/UI/file/browser state and classify the result as verified, attempted-unverified, or failed. Never convert a computerControl success return into verified without an observation.
- **owner gets:** The owner stops hearing false 'done' confirmations when the Mac cannot inject input, while successful work still completes without extra prompts. They get a clear explanation and a recoverable next step.
- effort: Medium: native macOS inspection adapters plus relay/job schema changes and adapters for open/write/UI/browser actions. Add integration tests with Accessibility denied and browser offline.  ·  risk: Read-only inspection can still reveal sensitive UI text; redact and retain structured evidence by default. Observation may be stale, so include timestamps and app identity. Recovery is to mark unverified and ask for a manual step or retry when readiness changes.
- cost: Low per action for structured checks; optional screenshot/vision verification adds model and storage cost. No hardware cost.  ·  latency: Adds roughly 100–500 ms for structured observations; vision fallback may take 1–3 seconds.
- security: Improves honesty without adding mutation authority. Keep observation data local, redact content, and make browser/session reads explicit.
- depends on: A working mac_readonly_inspect implementation; Relay durable action ledger; Postcondition schemas for each action type

### `relay` — Add an in-flight job watchdog and lease protocol: every execute job gets heartbeat/deadline timestamps; if the Mac process or browser bridge stops reporting, transition processing to stalled (not success), preserve the last observed phase, and let the relay resume or report the exact blocker after reconnect. Attach the same action ID across duplicate retries so receipts are deduplicated.
- **owner gets:** A spoken request will not hang indefinitely or appear mysteriously unfinished. The owner gets a timely 'still running', 'stalled because Accessibility/browser is unavailable', or verified completion, even across a dropped Mac or browser link.
- effort: Medium: job schema migration, heartbeat endpoint/background timer, reconnect reconciliation, and dashboard/pendant status formatting.  ·  risk: A slow legitimate action could be mislabeled stalled; use action-specific deadlines and retain resumable state. Duplicate side effects are possible unless idempotency keys are enforced for actions that support them.
- cost: Negligible API cost; small local/relay storage and timer overhead.  ·  latency: Immediate acknowledgement remains unchanged; watchdog adds no delay and improves timeout behavior.
- security: No new authority. Durable logs should omit command contents where sensitive and expose only status/reason to the pendant by default.
- depends on: Durable action ledger spanning relay and Mac; Postcondition-aware receipt states; Browser bridge reconnect/heartbeat


## What it asked for

_Nothing._
