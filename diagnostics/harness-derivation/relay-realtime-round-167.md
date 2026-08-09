# Harness derivation — relay-realtime — round 167

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "While I am away from my Mac, say: “Find me the best appointment/booking option that fits my calendar, compare the available choices, and book the one I choose.” The pendant should read my calendar, search authenticated browser sessions, speak a short comparison, and complete the selected booking."
- **useful because:** This combines the pendant’s always-available voice, the Mac’s local calendar, and the browser’s authenticated sessions into an errand the owner cannot currently complete from one place. It avoids blindly committing: the owner chooses among concrete options, while the system handles the tedious search and form filling.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Use the realtime relay only for intent capture, constraint extraction, and the spoken choice; use the slower background planner for search/comparison and browser execution, with a small local model for extracting dates, prices, and cancellation terms.
- **latency:** Acknowledge in under 1 second; return an initial shortlist within 30 seconds; booking may take several minutes and must survive a disconnected Mac or pendant via an asynchronous job.
- **cost:** Roughly $0.03–$0.15 per request depending on browser pages and planner turns; browser interaction and repeated page extraction dominate, not the short voice exchange.
- **security:** Calendar and authenticated booking data leave the Mac only as structured results; payment and irreversible booking details must be shown/spoken before commit and require the owner’s explicit selection. Keep an audit record of the chosen option and receipt, and never invent availability or terms.
- **missing:** A durable multi-step task state that stores constraints, candidate options, selected candidate, and commit phase; A calendar-read action exposed to the planner and a browser adapter that can fill and submit authenticated forms; A structured comparison/receipt format and a pendant interaction for selecting one option; A reliable Mac-online/offline handoff for long-running jobs

### "Tell me, through the pendant, whether now is a good time to interrupt me, and if not, wait until the current meeting, call, presentation, or focused task ends, then ask me again with the exact thing you wanted to say."
- **useful because:** The owner should not have to remember to check a laptop or manually set a mode. A worn device can ask at the moment of need, while the Mac can see active calls, full-screen presentations, audio output, and the foreground application. This makes asynchronous hive work usable without embarrassing or disruptive interruptions.
- **path:** pendant → relay → mac-planner → mac-vision → dashboard
- **model tier:** Use a cheap classifier or deterministic rules for presence/interruption state; reserve realtime speech for the brief question and response. Use a background model only to summarize why an alert matters.
- **latency:** State lookup and spoken decision under 2 seconds. Re-check after a meeting or focus state changes without keeping a realtime model alive.
- **cost:** Usually under $0.01 per check if based on local signals; transcription and speech for an actual interruption are the dominant costs.
- **security:** Presence state must stay on the Mac/relay and expose only a coarse label (available, busy, in call), not screenshots or meeting content. The owner must be able to cancel a queued interruption physically; queued messages need expiry so stale information is not spoken as current.
- **missing:** A Mac-side interruption-state provider for calls, meetings, presentation/full-screen mode, focus mode, and foreground work; An expiring priority queue that can wake on Mac state transitions rather than only on polling; A pendant gesture/voice contract for defer, cancel, and “tell me now”; A relay event delivery path that can distinguish a state-change wakeup from ordinary completion alerts

### "Let me give the pendant a command while my Mac is unavailable—“when my Mac comes back, download the document, extract the deadline, and remind me only if it is within a week.” The relay should hold the command, execute it when the Mac reconnects, and tell me exactly what happened or why it stopped."
- **useful because:** The pendant is often away from the Mac, so today a useful command simply disappears when the local agent is offline. This is a durable, conditional handoff rather than a reminder: it can wait for a machine, validate that preconditions still hold, expire safely, and report a truthful result.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Realtime only captures and normalizes the command. A cheap durable worker evaluates readiness and expiry; mac-planner/mac-terminal performs the task when reachable, and a slower model extracts facts from the downloaded document.
- **latency:** Immediate spoken acknowledgement under 1 second; execution starts within 10 seconds of Mac reconnection; completion can be minutes later and must arrive asynchronously.
- **cost:** About $0.01–$0.08 per deferred command; the document fetch and extraction dominate, while storage and readiness checks are negligible.
- **security:** Persist the minimum encrypted command and its expiry, not raw microphone audio. Bind execution to the owner/session, record every attempted action and returned artifact hash, and refuse to execute after constraints or credentials become invalid. No silent destructive actions; the command should declare an allowlist of intended effects.
- **missing:** A durable relay queue and worker triggered by Mac heartbeat/reconnect, with leases, retries, expiry, and crash recovery; A conditional command schema containing preconditions, permitted action types, output requirements, and maximum lifetime; A Mac reconnect handshake that claims queued work and returns typed receipts; A durable notification path to the pendant for completion, failure, and expired work


## What it asked for

_Nothing._
## Its own summary

Recorded three distinct owner-facing capabilities: (1) a cross-surface appointment/booking concierge that compares authenticated browser options against local calendar before the owner selects one, (2) interruption-aware pendant delivery that waits through calls/focus/presentations and asks at the right moment, and (3) durable conditional command capsules that survive an offline Mac and execute on reconnect with expiry and truthful receipts. The first is the highest-value capability: it turns the pendant, Mac, and authenticated browser into one useful agent rather than three disconnected surfaces.

**Biggest unknown:** Whether the existing browser and Mac routers already expose the specific calendar-read, reconnect-claim, state-transition, and structured receipt primitives named in the proposals; the proposals deliberately identify them as requirements rather than assuming they exist.

