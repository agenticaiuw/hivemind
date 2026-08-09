# Harness derivation — faculty-judgement — round 177

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“The pendant is plugged into my Mac—let me have a normal live conversation now, even though the pendant has no LTE registration.”"
- **useful because:** The hardware is physically present today but currently stranded behind the absent relay registration. A USB-tether mode would make the pendant useful immediately: nRF9160 audio/control over USB serial to the Mac, Mac internet to the relay/model, and the existing ESP32 downlink back to the wearer. It also gives a truthful fallback whenever LTE is unavailable without inventing an offline speech model.
- **path:** pendant → mac-planner → relay-realtime → relay
- **model tier:** Realtime only for the conversational turn; use the existing relay model. The Mac is a transport adapter, not an additional reasoning model.
- **latency:** Target <150 ms one-way transport overhead and preserve the shipped 60 ms Opus framing. First usable response should not wait for LTE registration; connection setup should be under 2 seconds.
- **cost:** No additional per-turn model cost beyond the existing relay conversation. Engineering cost is a USB serial framing/heartbeat and Mac bridge; dominant runtime cost remains realtime inference and 24 kHz codec.
- **security:** USB possession must bind to an authenticated pendant session, with monotonic frame counters and replay rejection. Never expose raw serial control to arbitrary local processes; require explicit local pairing. On relay loss, fail closed and surface 'conversation unavailable' rather than silently buffering speech. Audio leaves the Mac to the relay under the existing policy and should be covered by the owner’s future disclosure policy.
- **missing:** A production USB-serial audio/control transport from the nRF9160 to local-agent; A Mac bridge mode that maps the USB session into the relay realtime session and reconnects without duplicating audio; A session capability/handshake and frame-counter verification; End-to-end hardware acceptance tests using /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA

### "“I’m back—tell me only what changed since I marked that I left.”"
- **useful because:** A physical departure marker is already available, but today it has no semantic consequence. This would turn the pendant into a continuity instrument: leaving creates a compact, privacy-filtered snapshot of the Mac’s active project, browser tabs, jobs, and pending work; returning asks for a ranked delta instead of another generic briefing. It is valuable precisely because the worn device knows the human boundary while the Mac knows the work state.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Background/cheap model compiles and ranks the diff; realtime is used only to answer the return utterance or speak the short result.
- **latency:** Departure capture under 1 second and return response under 3 seconds; if browser is offline, report that source as unknown rather than treating it as unchanged.
- **cost:** One small background summarization call per return, with bounded snapshot text; storage is a few KB per departure/return pair. Most cost is browser inspection only when the extension is online.
- **security:** Snapshot stores digests and titles, not page bodies, secrets, or screenshots. Browser reads remain read-only. A per-pair expiry and a visible delete action are required. Calendar/mail must carry unreadable provenance when permissions return empty; absence is never evidence of no change.
- **missing:** A durable departure/return snapshot store keyed to the existing offline_moment_bookmark record; A Mac adapter exposing foreground app, active project, job and browser-tab digests in one bounded snapshot; A diff/ranking endpoint that distinguishes changed, unchanged, and unreadable sources; A pendant command/event path that asks for the diff after the return marker

### "“Why was the thing I asked for silent or incomplete? Give me one trustworthy timeline, not three different status stories.”"
- **useful because:** Today UART diagnostics, relay pipeline records, Mac job receipts, and pendant playback acknowledgements live in separate worlds. When audio is missing, a job is stuck, or playback was interrupted, the owner cannot distinguish generation failure, transport loss, device rejection, or simply 'not spoken yet'. A single incident timeline would make the system accountable and let the owner decide whether to retry, undo, or file the already-reviewable bug draft.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Cheap background correlation and deterministic classification; realtime only when the owner asks aloud. No model should invent a cause: every conclusion must cite an event or say unknown.
- **latency:** Return a first timeline in under 2 seconds from local records; optionally append delayed UART or offline ACK events when they arrive. Never block the owner’s next conversation on forensic processing.
- **cost:** Negligible model cost for structured correlation; bounded local/relay event storage and one compact dashboard render dominate. Include only excerpts and metrics, not raw audio by default.
- **security:** Use opaque job/artifact IDs and redact UART text, transcripts, and page contents. The spoken response must be safe by default ('generation completed; playback ACK missing') and require dashboard opt-in for sensitive evidence. Correlation must be idempotent across offline ACK replay and must not turn a diagnostic into an automatic retry or external issue submission.
- **missing:** A shared correlation index joining relay job ID, pipeline ID, Mac job/action ID, artifact ID, and pendant device sequence; A read-only incident-timeline endpoint with explicit unknown/gap states and provenance links; A reducer that merges pendant_diagnostics_and_bug_draft output with record_pendant_delivery_event and Mac receipts; A dashboard and compact spoken renderer that distinguish observed facts from inferred hypotheses

### "“When the Mac, browser, and relay disagree, don't pick one silently—tell me what conflicts and ask me only the smallest question that resolves it.”"
- **useful because:** A personal AI should expose disagreement between its bodies instead of laundering one body's stale or partial view into confidence. For example, the browser may show a draft while the Mac receipt says no action occurred, or the relay may retain an old plan after the Mac state changed. This capability would make uncertainty actionable: present the conflicting claims, their freshness and provenance, then ask one narrowly scoped owner question.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Deterministic conflict detection and freshness checks first; use the cheaper background tier to compress the evidence. Realtime is reserved for the final spoken question.
- **latency:** Under 2 seconds when all surfaces are online; otherwise return partial evidence plus explicit missing-surface status rather than waiting indefinitely.
- **cost:** Low: mostly structured comparisons and short summaries. The expensive model is invoked only when conflicts are genuinely ambiguous, not for every action.
- **security:** Never merge contradictory claims into a stronger claim. Preserve source IDs, timestamps, and sensitivity labels; redact private snippets from the spoken path. The resolver must not execute a repair while asking the question. Any subsequent mutation must pass autonomy_policy_evaluate and, where required, physical approval.
- **missing:** A typed conflict record with claim, source, observed_at, freshness, and confidence fields; A cross-surface collector that can compare the same object across relay, Mac, and browser despite their unrelated ID namespaces; A deterministic policy for selecting the minimum owner question and expiring unresolved conflicts; Dashboard and pendant renderers for conflict evidence and the pending question


## What it asked for

_Nothing._
