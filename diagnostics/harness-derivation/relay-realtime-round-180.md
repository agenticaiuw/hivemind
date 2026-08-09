# Harness derivation — relay-realtime — round 180

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If that task finishes later, tell me when it’s done and what happened."
- **useful because:** This is the single most useful missing behavior: the owner shouldn’t have to keep asking for status. The system should proactively deliver a short completion result when a long-running Mac job ends, especially when the owner has stepped away from the Mac.
- **path:** relay → mac-bridge → browser
- **model tier:** Realtime for the initial voice; cheaper background model for monitoring and summarizing results.
- **latency:** Immediate acknowledgment in-session, then asynchronous delivery when the job completes; no polling required from the owner.
- **cost:** Low per job if event-driven. The expensive part today is repeated status checks; the goal is to eliminate those.
- **security:** The spoken notification must be truthful and minimal. It should not include sensitive document contents unless explicitly requested. It must not claim success unless the job record says complete.
- **missing:** A working implementation of relay_event_push or an equivalent event pipeline to queue and deliver completion updates; A durable notification queue for offline delivery and replay on reconnect; A reliable mapping from job completion to a concise spoken summary

### "Watch for changes on this page and tell me only when something important changes."
- **useful because:** This becomes a personal monitoring assistant. The owner can point at a page (documentation, a status page, a project page) and get notified when it changes, without leaving a browser tab open or remembering to check.
- **path:** relay → browser → mac-bridge
- **model tier:** Cheaper background model for diffing and importance classification; realtime only for delivering alerts and taking new instructions.
- **latency:** Seconds to minutes is fine; it’s a watcher, not a conversation.
- **cost:** Low to moderate, dominated by periodic fetches and diffing. Cost drops if the system uses conditional requests and only re-checks when needed.
- **security:** Must respect authentication boundaries: public pages can be watched by the relay; private pages require the browser extension on the owner’s Mac and should not exfiltrate secrets. Alerts should summarize, not copy sensitive content verbatim.
- **missing:** Any scheduler/cron or durable watcher registry; Change-diff storage and history; Importance classifier for changes; A delivery path for alerts (inbox/notification queue)

### "When my connection is flaky, keep the conversation going by switching to the best available path and summarize what I missed when it comes back."
- **useful because:** This uses the multi-node nature of the system. If LTE-M is unregistered or down, USB-to-Mac can still carry work; if the Mac is asleep, the relay can still read public web pages. The owner experiences continuity instead of failure.
- **path:** pendant → bridge → relay → mac-bridge → browser
- **model tier:** Realtime for live conversation; cheaper models for retries and summarization.
- **latency:** Fast failover decisions during conversation; summaries can arrive when connectivity returns.
- **cost:** Moderate. The complexity is in coordination and state syncing, not raw tokens.
- **security:** Must avoid replaying or duplicating actions after reconnect. Must not send private data over the wrong channel. Needs clear consent boundaries for what gets buffered.
- **missing:** A unified connectivity state model across pendant/bridge/relay/mac; Retry and idempotency semantics for actions and audio; A safe buffering strategy that respects the SD-as-failure-path rule

### "“I’m heads-down until 3. Don’t interrupt me unless something is genuinely urgent; collect everything else and give me one spoken digest when I’m free.”"
- **useful because:** The owner gets control over attention rather than a stream of isolated alerts. The pendant becomes a deliberate interruption filter across Mac and authenticated browser work, with urgent exceptions still reaching them.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime classifies only incoming events and speaks urgent exceptions; a cheaper background model clusters and summarizes deferred items.
- **latency:** Urgent classification under 2 seconds; deferred digest can be generated in 10–60 seconds when the owner requests it.
- **cost:** About $0.01–$0.05 per digest depending on event volume; classification dominates only when events arrive.
- **security:** Event titles, snippets, and browser-derived metadata leave the Mac/browser for relay summarization. Default to metadata and user-selected sources, encrypt stored digest items, and make the suppression window visible and cancellable from the pendant.
- **missing:** A durable attention-policy store with start/end time and urgency rules; Mac/browser event adapters that emit normalized events; A relay-side deferred-event queue and digest trigger; A pendant gesture or spoken command to cancel/override the policy

### "“When I say ‘remember this for when I’m back at my desk’, capture the thought now, then when my pendant reconnects to my Mac open the right project, place the transcript and relevant links in a dated handoff note, and tell me it’s ready.”"
- **useful because:** A voice memo today is easy to forget. This turns an away-from-desk thought into a usable, context-linked work handoff without requiring the owner to remember to find or paste it later.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Realtime performs capture acknowledgment and intent extraction; a cheaper background model selects project context and formats the handoff note.
- **latency:** Acknowledge capture immediately; produce the desk handoff within 30 seconds of Mac reconnection.
- **cost:** Roughly $0.02–$0.10 per handoff; transcription and context retrieval dominate.
- **security:** The thought and selected project/browser context may be written to local files and relay state. Require explicit project scope in the utterance or show the chosen project in the dashboard; never silently paste into source files or send messages.
- **missing:** A reconnect-triggered job runner (USB serial today, LTE/relay pairing later); A durable handoff record linking memo, project, and browser references; A Mac action for creating/opening a note and inserting content; Context-selection logic that can abstain when project identity is ambiguous

### "“Check the work I just asked you to do across my Mac and browser, and tell me not only whether it finished, but show me the evidence and any side effects.”"
- **useful because:** Today a spoken “done” is not enough for consequential work. The owner gets a compact audit trail: completed actions, changed files/pages, timestamps, errors, and receipts, all reviewable from the pendant or dashboard.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime reads and verbalizes a precomputed receipt; a cheaper model turns raw action logs into a concise evidence narrative only when needed.
- **latency:** First status in under 2 seconds from cached job state; detailed evidence in under 10 seconds.
- **cost:** About $0.005–$0.03 per spoken audit; storage and receipt extraction dominate rather than inference.
- **security:** Receipts can expose document names, URLs, and command output. Redact secrets and page contents by default, retain hashes/paths and action-level evidence, and provide deletion/retention controls.
- **missing:** A unified immutable receipt schema across Mac and browser actions; Before/after snapshots or hashes for files and structured browser state; A relay endpoint that correlates plan, execution, and browser command receipts; Pendant-friendly navigation for “next evidence” and interruption


## Changes it proposed to its own stack

### `integration` — Implement a first-class USB-tethered pendant session: when the nRF9160 and ESP32 are connected on the known serial devices, a Mac-side bridge registers the pendant as an authenticated relay client, forwards button/audio/upstream and downlink Opus, and exposes the same session/job identity as LTE. Seamlessly fail back to LTE when it later registers, without duplicating a turn.
- **owner gets:** The owner can use the real worn pendant today at a desk or during development instead of waiting for LTE registration, and conversations do not mysteriously fail merely because cellular is unavailable.
- effort: Medium-high: serial framing/bridge daemon, pairing handshake, session migration, and end-to-end hardware tests.  ·  risk: A stale USB peer could impersonate the pendant or duplicate audio. Use a per-device key and monotonic session nonce; reject duplicate sessions and recover by restarting the bridge.
- cost: Negligible API cost; modest Mac CPU. No new hardware cost; USB power is already present.  ·  latency: Lower latency than LTE (typically tens of milliseconds), with serial backpressure handling required for 24 kHz Opus.
- security: USB becomes a trusted local transport only after cryptographic pairing; never accept arbitrary serial data as owner speech or commands.
- depends on: A Mac-side serial bridge service; A device identity/pairing record; The existing 24 kHz Opus and relay voice session protocol

### `interaction` — Add a two-channel conversational state machine that distinguishes “owner still speaking”, “owner waiting for an external job”, and “owner has ended the session”. The relay should keep a resumable job conversation keyed to the pendant press/session, deliver short progress questions only when needed, and let one button press resume the same context rather than starting a new turn.
- **owner gets:** Long tasks stop feeling like abandoned black boxes: the owner can walk away, later ask “what about that?”, answer a clarification, or cancel without reconstructing what they asked.
- effort: High: durable session state, clarification routing, voice interruption handling, and Mac/browser job correlation.  ·  risk: Old context could cause an action against the wrong task. Expire resumptions, speak the task label and last-known state, and require an explicit disambiguating phrase when multiple jobs are active.
- cost: Small storage cost; background polling/event delivery dominates, with realtime inference only on spoken resumes.  ·  latency: Immediate cached acknowledgement; remote job state may take seconds to refresh.
- security: Persisted transcripts and task state need retention limits and encryption; do not include browser secrets in spoken resumptions.
- depends on: A real durable completion/event watcher; The existing job/receipt routes; Pendant inbox delivery and button-interrupt behavior


## What it asked for

_Nothing._
## Its own summary

Recorded five new items. The highest-value immediate change is a first-class USB-tethered pendant session: the physically connected nRF9160 and ESP32 can become a working low-latency voice endpoint today even before LTE registration, with cryptographic pairing and seamless LTE handoff. I also recorded an attention-suppression policy with deferred digest, desk-return project handoffs, unified evidence receipts, and resumable conversational job state. These require durable policy/event storage, cross-surface correlation, and a Mac serial bridge rather than another relay-only refactor.

**Biggest unknown:** Which existing Mac-side serial/audio bridge code is currently running and whether it already exposes a stable device identity/session handshake; that determines whether USB tethering is an integration project or a new bridge service.

