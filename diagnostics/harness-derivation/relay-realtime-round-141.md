# Harness derivation — relay-realtime — round 141

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Open my work session and resume where I left off."
- **useful because:** The owner can be hands-free and pick up a task across devices. The relay starts the flow; the Mac and browser surfaces restore the session context.
- **path:** relay → mac-bridge → browser
- **model tier:** realtime to interpret the request, then mac-planner for the session restore plan
- **latency:** A few seconds end-to-end; dominated by session lookup and app/browser restore on the Mac
- **cost:** Moderate. Planning and a small set of typed actions; most cost is downstream planning and UI operations
- **security:** Resuming sessions may reopen sensitive tabs or files. Use existing session affinity and receipts; do not invent access control. Keep spoken summary minimal.
- **missing:** A reliable session snapshot/restore contract across Mac apps and browser tabs; Durable job runner to guarantee resume actions complete or fail coherently

### "Check a site for updates and tell me what changed."
- **useful because:** It becomes a lightweight personal watchdog: the owner asks once and hears a concise changelog later, without keeping a Mac open.
- **path:** relay → server_browser → dashboard
- **model tier:** cheaper background model for diffing and summarization; realtime only for the spoken result when the owner asks
- **latency:** Seconds to minutes depending on page complexity; dominated by fetching and diffing
- **cost:** Moderate. Periodic fetches and storage of snapshots; network and storage dominate
- **security:** Fetching authenticated pages must respect session boundaries. Store only what’s needed for diffing; avoid leaking content across users.
- **missing:** server_browser_actions needs an implementation; A scheduler (cron/alarm) to run checks later; Storage for snapshots and a diff format

### "“Connect me to a real person about this.” The pendant should let me dictate a situation, find the relevant contact in my Mac/browser context, draft a short message with the situation and a specific question, send it when appropriate, then keep a live relay open so the reply is spoken back to me and added to the original thread."
- **useful because:** This turns the pendant from a command microphone into a bridge to the people who can actually resolve things. The relay can remain available while the owner is away, the Mac can reach Messages/Mail, and the browser can use an authenticated support or chat session none of the other nodes can access.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime for the initial dictation, intent extraction, and brief spoken updates; background model on the Mac/relay for contact selection, message drafting, and reply summarization.
- **latency:** Acknowledge in under 1 second; draft in under 10 seconds; speak inbound replies within 3 seconds of their arrival.
- **cost:** About $0.01–$0.05 per initiation plus background summarization; browser polling/event delivery and speech audio dominate rather than reasoning.
- **security:** Messages, contact names, and authenticated support content leave the pendant for relay processing. Sending must be explicitly represented to the owner before it occurs, and the bridge must be scoped to one contact/thread so replies cannot be misrouted.
- **missing:** A relay-owned conversation/bridge record with expiration and correlation to one Mac message thread; Mac Messages/Mail send-and-watch adapter and browser chat-session adapter; relay event push plus spoken inbound-status delivery; An explicit send-versus-draft spoken interaction state

### "“Why did that fail, and fix it without me repeating myself.” After I issue a multi-surface request, the pendant should notice a timeout, rejected action, stale browser tab, or disconnected Mac, explain the concrete failure, automatically choose a safe alternate route, retry once, and give me one final spoken result with the receipt and what remains undone."
- **useful because:** Today a wearable owner has no screen and cannot reconstruct which downstream node failed. A self-healing handoff would make the hive feel like one dependable assistant instead of a chain of opaque jobs, especially when the owner is away from the Mac.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime only for failure classification and the spoken explanation; a cheaper background planner should inspect receipts and select a bounded alternate route.
- **latency:** Failure acknowledgement within 2 seconds; one retry within 20 seconds; never loop more than once without reporting.
- **cost:** Usually under $0.02 per failed request; dominated by one additional planner/browser attempt, not speech.
- **security:** Retries can duplicate external side effects. The system must use idempotency keys and distinguish reads/reversible actions from sends, purchases, deletion, or other irreversible work; those remain reported rather than silently retried. Failure metadata and page excerpts may contain private data.
- **missing:** A cross-surface failure taxonomy and idempotency key carried from voice through Mac/browser jobs; A relay watcher for job, heartbeat, and receipt transitions; An alternate-route policy that can retry reads/reversible actions but only explain high-impact failures; A compact spoken receipt format

### "“Give me a private end-of-day debrief.” The worn pendant should collect only the day’s completed voice requests, Mac action receipts, and browser results, have a background model identify unresolved commitments and contradictions, and speak me a 60-second debrief with named follow-ups; I should be able to say “snooze that” or “close it” and have the corresponding Mac/browser task updated."
- **useful because:** A daily debrief is the one place the owner gets value from every node together: the pendant supplies intent, the relay knows the conversation, the Mac knows what changed, and the browser knows authenticated work that never appears in local files. It converts scattered activity into actionable closure without requiring the owner to remember every interaction.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use a cheap background model to cluster receipts and detect unresolved items; reserve realtime for the short spoken summary and follow-up commands.
- **latency:** Generate before the owner asks or within 15 seconds on demand; each spoken follow-up should acknowledge in 1 second and update the source task within 10 seconds.
- **cost:** Roughly $0.01–$0.04 per debrief, mostly background summarization over the day’s receipts; follow-up actions add normal Mac/browser costs.
- **security:** The debrief combines highly sensitive local and authenticated-browser data. Keep raw evidence on the relay/Mac where possible, pass only bounded excerpts to the model, encrypt retention, and expose a “forget this item” command. Updating a source task must identify the exact receipt/thread.
- **missing:** A daily cross-surface evidence export with provenance and retention controls; A durable unresolved-commitment/contradiction store; A spoken debrief trigger and response queue that works after the owner stops talking; Adapters to snooze/close the originating Mac reminder or browser task


## Changes it proposed to its own stack

### `firmware` — Add a pendant-side transaction control channel over the live USB serial link: a short button press emits cancel-current-job, a double press emits repeat-last-status, and a long press emits emergency-stop; the relay maps these to the active Mac/browser job by correlation id and returns a distinct LED pattern for acknowledged, cancelled, and link-lost states. Preserve the event locally until an acknowledgement arrives so a press while the relay is briefly unavailable is not silently lost.
- **owner gets:** With no screen and often no free hands, the owner gets a physical way to stop a runaway action or ask what happened without speaking a full sentence. It is especially valuable for an unattended Mac action and is testable immediately while both chips are USB-connected.
- effort: Medium: nRF9160 button debouncing/state machine and LED patterns, ESP32/serial forwarding, relay correlation and job cancellation/status hooks, plus an end-to-end harness test.  ·  risk: A false press could cancel useful work; require a long press for emergency-stop and make cancellation idempotent. If serial framing breaks, fall back to current voice behavior and show link-lost LED; never infer success without relay acknowledgement.
- cost: No API cost; negligible firmware CPU/RAM and under 1 mA transient LED/button activity. Engineering cost is the serial protocol and tests.  ·  latency: Local button acknowledgement under 100 ms; relay action bounded by existing job cancellation/status latency.
- security: The physical pendant becomes an authenticated control surface. Bind events to the paired device/session and reject stale correlation ids; emergency-stop should not expose task contents over serial.
- depends on: A relay event endpoint that accepts device-originated button events; A durable active-job correlation map shared by voice, Mac, and browser work; Firmware serial framing and acknowledgement support on the currently connected nRF9160/ESP32 pair


## What it asked for

_Nothing._
