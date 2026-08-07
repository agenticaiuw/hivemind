# Harness derivation — mac-planner — round 147

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When my pendant is plugged into my Mac, give me a one-button ‘arrive’ routine: restore the work context I was using, tell me my next calendar commitment, and keep the spoken answer under 20 seconds.”"
- **useful because:** This is the first genuinely testable worn-device-to-desktop experience today: a physical button or wake event on the USB-connected pendant becomes a reliable return-to-work ritual, while the Mac supplies private Calendar and Safari state and the relay turns it into a short response. It saves the owner from rebuilding context after every walk-away without opening a microphone.
- **path:** pendant → mac-bridge → browser → relay-realtime → mac-planner
- **model tier:** Use a cheap background model to select and summarize the saved work context; use realtime only for the short spoken response and button interaction.
- **latency:** Button acknowledgement under 300 ms locally; restore/open actions within 5 s; spoken summary within 8 s.
- **cost:** About $0.002–$0.01 per arrival, dominated by one small text summary; no vision or large context resend.
- **security:** Private Calendar and active-tab metadata leave the Mac only as an encrypted, scoped payload; never read page bodies unless the owner enabled that site. USB presence must not itself authorize destructive actions. Ask once when enabling the routine, not on every arrival.
- **missing:** A Mac USB-serial daemon that detects /dev/cu.usbmodem00096003658* and maps pendant button/presence events to a relay session; A durable, owner-selected work-context snapshot (apps, Safari tab IDs, and last-used project) with expiry; Pendant firmware event framing and a local acknowledgement LED/haptic protocol

### "“When a scheduled meeting ends, make me a private wrap-up packet: the event details and attendees, relevant unread mail, the authenticated page I had open for it, three follow-up bullets, and drafts of reminders—but do not send anything.”"
- **useful because:** The system currently helps prepare for a meeting, but the costly failure is afterward: commitments disappear across Calendar, Mail, and logged-in browser tabs. This creates a reviewable artifact on the Mac and a short spoken notification on the pendant without requiring microphone capture or screen recording.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-bridge
- **model tier:** Background text model extracts commitments and drafts; realtime is used only if the owner asks the pendant to read the packet aloud.
- **latency:** Packet available within 2 minutes of event end; pendant notification under 10 seconds after the packet is ready.
- **cost:** Roughly $0.01–$0.04 per meeting, dominated by summarizing bounded mail/page snippets; zero cost when there is no matching event.
- **security:** Keep the packet local by default in a dated folder or Note; include only the matching event, bounded snippets, and explicit tab IDs. Never infer or expose attendees beyond the event scope. Drafts must be visibly labeled unsent and require a separate owner command to transmit.
- **missing:** Calendar event-end trigger and attendee extraction in the routine scheduler; A browser-session matcher that identifies the tabs last used during that event without scraping unrelated tabs; A local packet format with source citations and draft-versus-sent state; Relay notification delivery to the physically connected pendant

### "“If my pendant cable comes loose while you’re doing a multi-step Mac or browser task, stop at the next safe boundary, save exactly where you are, and tell me on reconnect what happened and what remains.”"
- **useful because:** Today the pendant is physically tethered to the Mac but absent from the relay’s registered-device table. A cable drop is therefore a real failure mode, not a hypothetical network edge case. This turns an invisible half-completed browser or desktop task into a recoverable handoff with an honest receipt, rather than forcing the owner to guess whether anything was sent or changed.
- **path:** pendant → mac-bridge → browser-extension → relay-realtime → mac-planner
- **model tier:** No realtime model while disconnected: the Mac bridge records structured state locally. A cheap background model can summarize the receipt; realtime is used only when the pendant reconnects and the owner asks for it.
- **latency:** Detect serial loss under 1 second; persist state before the next action; reconnect summary under 5 seconds.
- **cost:** Under $0.005 per incident; mostly local state writes, with one small summary only on reconnect.
- **security:** A disconnect must never be treated as approval or cancellation. Persist only action types, target app/tab identifiers, hashes and receipts—not page secrets. On reconnect, distinguish completed, skipped, and unknown outcomes; never claim an action failed merely because the link vanished.
- **missing:** Mac serial link watchdog for both the nRF9160 and ESP32 paths, with stable device identity and reconnect detection; An execution checkpoint contract between /execute, browser command IDs, and job receipts; Relay event type for pendant link-loss/reconnect and a local queue for summaries; Firmware sequence numbers so duplicate reconnect events cannot replay a button command

### "“At the end of the day, give me a private, chronological replay of what the pendant, Mac, and browser actually did on my behalf: observations, actions, outcomes, and anything uncertain, with links back to the source.”"
- **useful because:** The owner cannot currently audit the whole hive as one continuous history. Mac receipts, browser results, relay events, and pendant telemetry are separate, so a missed or surprising action is hard to reconstruct. A daily replay would make the system trustworthy without requiring the owner to watch it operate, and it would clearly distinguish observed facts, attempted actions, confirmed outcomes, and unknowns.
- **path:** pendant → mac-bridge → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Use a cheap background model to order and summarize structured events; use realtime only if the owner asks the pendant to read the short replay.
- **latency:** Generate in under 60 seconds after the selected day closes; interactive drill-down under 3 seconds from cached records.
- **cost:** About $0.01–$0.05 per day, dominated by summarizing event metadata; source payloads remain local and need not be resent to the model.
- **security:** Default to local storage and redact message bodies, page secrets, tokens, and raw audio. Each item needs provenance, retention, and sensitivity labels. The replay must never imply success when only dispatch was recorded; show unknown outcome explicitly.
- **missing:** A cross-surface append-only event schema with causal IDs linking pendant events, relay turns, Mac jobs, browser commands, and receipts; A local event index and compaction policy that can answer ‘what happened today’ without uploading private payloads; A dashboard/tiny pendant-readable renderer for fact/action/uncertainty categories and source drill-down; Clock synchronization and monotonic sequence handling across the pendant, Mac, browser bridge, and relay

### "“If I ask the pendant and Mac about the same thing, treat it as one task: merge the conversations, avoid duplicate actions, and show me one status and one final answer.”"
- **useful because:** Today each surface can start work independently, so a hurried voice request followed by a desktop request can produce duplicate browser mutations, conflicting drafts, or two contradictory answers. A shared task identity would make the hive feel like one assistant rather than several agents, especially when the owner changes surfaces mid-task.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-bridge → dashboard
- **model tier:** Use deterministic normalized intent/entity matching first; invoke a cheap model only for ambiguous matches. Realtime handles only the live spoken acknowledgement.
- **latency:** Detect a likely duplicate within 1 second; merge before any second irreversible browser or Mac action; final status under the originating task’s existing deadline.
- **cost:** Usually near-zero for deterministic matching; under $0.01 for ambiguous intent resolution.
- **security:** Never merge across accounts or unrelated private contexts merely because wording is similar. Match using session owner, target entities, and a short time window; retain an audit trail showing why two requests were joined. Merging must not silently broaden permissions.
- **missing:** A durable task/case identifier shared by relay turns, Mac jobs, browser sessions, and pendant events; An idempotency and intent-fingerprint service that can claim, merge, or supersede work before execution; Cross-surface status and conflict semantics for ‘already done’, ‘in progress’, and ‘needs clarification’; A user-visible task history in the dashboard and a compact spoken status on the pendant

### "“Forget everything you learned about this one topic or task everywhere—on the pendant, Mac, browser workbench, and relay—and show me a proof that it is gone without exposing the content again.”"
- **useful because:** The owner cannot currently issue a single scoped erasure across the hive. Deleting a capture, job, or note in one surface may leave derived summaries, browser extracts, receipts, or relay audio elsewhere. A verifiable, topic-scoped erasure command is essential for safely using the system with sensitive work or personal situations.
- **path:** pendant → mac-bridge → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Use deterministic encrypted-index lookup and deletion; use a cheap model only to resolve the owner’s natural-language topic into candidate task IDs, then require exact scope display before execution.
- **latency:** Show candidate scope within 3 seconds; complete deletion and produce a cryptographic deletion receipt within 30 seconds.
- **cost:** Under $0.01 per request; dominated by indexed lookups and storage deletion, not model tokens.
- **security:** The proof must contain identifiers, counts, timestamps, and storage locations—not deleted text. Never broaden a fuzzy topic match silently; preserve only a minimal tombstone/hash needed to prevent resurrection and explain that limitation. Relay and browser caches must honor the same deletion ID.
- **missing:** A shared data-lineage graph from raw events to summaries, audio, notes, browser extracts, and model prompts; Authenticated delete fan-out across Mac storage, browser session caches, relay D1/R2, and pendant flash queues; A deletion receipt protocol with tombstones that prevent replay or rehydration from offline queues; A scope-preview UI and pendant confirmation gesture for destructive erasure


## Changes it proposed to its own stack

### `mac-harness` — Ship a small signed USB pendant gateway inside AI Pendant Agent: open the nRF9160 and ESP32 serial devices by stable USB identity, decode framed button/presence/audio events, emit link-up/link-down/sequence events to the local /pipeline and relay, and expose a read-only status record with device path, firmware version, last sequence, and reconnect count. Keep it independent of Accessibility and microphone permissions.
- **owner gets:** The owner can wear and test the actual pendant today while attached to this Mac, instead of seeing a stale ‘no pendant registered’ state and having no way to know whether a button press or cable drop was received. It unlocks real arrival actions, reconnect recovery, and short spoken notifications without opening a mic.
- effort: Medium: serial framing, device discovery, reconnect supervision, and one relay event contract; test against both live USB paths and simulated disconnects.  ·  risk: Bad framing could generate duplicate commands or flood the relay. Use sequence numbers, bounded buffers, and treat unknown frames as telemetry only; recover by closing and reopening the port. Do not send raw audio or serial payloads upstream by default.
- cost: Negligible API cost; approximately 1–3% CPU while connected and no meaningful power increase. No new hardware required.  ·  latency: Local events can be acknowledged in under 100 ms; relay delivery adds normal network latency.
- security: USB presence is device telemetry, not authorization. Restrict to the two known VID/PID/serial identities, redact payloads in logs, and authenticate relay events with the existing bearer/device pairing.
- depends on: A documented framed serial protocol for nRF9160 button/presence events and ESP32 audio-bridge control; Relay event endpoint accepting pendant link and button telemetry; Firmware sequence numbers and a reconnect-safe command acknowledgement


## What it asked for

_Nothing._
## Its own summary

Round 147 produced four non-duplicate records: (1) one-button pendant arrival that restores work context and reads the next commitment, (2) automatic post-meeting wrap-up packets spanning Calendar, Mail, and the authenticated Safari context, (3) cable-loss recovery with checkpointed Mac/browser receipts and reconnect summaries, and (4) the enabling Mac-harness USB gateway for the live nRF9160 and ESP32 serial devices. Live inspection confirms Safari bridge online with 3 tabs, Mac bridge/relay reachable, but Accessibility and Screen Recording are still unavailable and the pendant is still absent from the relay device table. I also informed faculty-action and browser-extension about the USB and checkpoint contracts.

**Biggest unknown:** The actual framed serial protocol and firmware sequence/ack semantics for the physically connected nRF9160 and ESP32 are not exposed. The newly granted read-only inspection tools are schema-only (no implementation), so I could not verify running apps or tabs through those tools; /ops/snapshot remains the live source of truth. I still need the firmware/USB gateway contract and relay event shape before these can run end-to-end.

