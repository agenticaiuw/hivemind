# Harness derivation — relay-realtime — round 170

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say “start a quick checkup,” run a fast diagnostic across the pendant link, Mac bridge, and browser extension, then summarize what’s healthy and what’s broken."
- **useful because:** It gives the owner immediate confidence the system is working before relying on it, and points directly to the failing layer when it isn’t.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** realtime for the spoken interaction; cheaper model for collecting and summarizing diagnostics
- **latency:** Under 5 seconds for a basic pass when all parts are online; longer only when waiting on slow checks.
- **cost:** Low: a handful of status reads and a short spoken summary. Dominant cost is cross-surface coordination.
- **security:** Diagnostic output can leak environment details; keep it high-level unless the owner asks for specifics.
- **missing:** A defined diagnostic contract across surfaces (what to check, how to report); A relay-visible capabilities inventory for its own surface (so the relay can test itself without guessing); Standard status endpoints for bridge and browser extension health

### "“Take care of this across my Mac and browser. If you hit an ambiguity, ask me one sharply specific question on the pendant; otherwise keep going and tell me only the final result or the exact blocker.”"
- **useful because:** Today a delegated job either guesses through ambiguity or ends as an opaque queued task. This would let the owner be away from the Mac while still resolving the one decision that only they can answer, without narrating every intermediate step.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → browser → dashboard
- **model tier:** Use relay-realtime only for the short clarification exchange; mac-planner for planning, mac-vision/browser-extension for execution and inspection; a cheaper background model summarizes receipts.
- **latency:** Immediate acknowledgement under 500 ms; clarification spoken as soon as a typed uncertainty receipt arrives (target under 10 s); final result delivered asynchronously.
- **cost:** One realtime turn per clarification plus normal planner/vision calls; roughly $0.01–$0.08 per task depending on screenshots and number of retries, with clarification tokens dominating relay cost.
- **security:** The question must include the exact app, candidate values, and consequence, never expose credentials or raw page contents. The worker must correlate replies to the job and expire stale questions; execution can continue only on actions already authorized by the original goal. Confirmation is for missing information, not an arbitrary policy gate.
- **missing:** A durable job state machine with a WAITING_FOR_OWNER state and one outstanding question per job; A pendant/relay reply correlation protocol for answering a pending question after the voice session ends; Typed uncertainty receipts from mac-planner/mac-vision/browser-extension; An execution resume endpoint that preserves the existing browser tab/session affinity

### "“Search my open authenticated browser tabs and local Mac documents together for the answer to this question, and read me the answer with which source supports each important fact.”"
- **useful because:** The browser session and local filesystem contain different halves of the owner's private work context. Today no single request can join them: browser access is session-bound and Mac access is local. A spoken, provenance-bearing answer would turn the pendant into a genuinely useful away-from-desk research surface rather than a remote command button.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → mac-terminal → dashboard
- **model tier:** Cheap extraction models run locally on each surface to return bounded snippets and metadata; a background synthesis model joins them; relay-realtime only handles the spoken query and concise answer.
- **latency:** Acknowledge immediately, return a first answer in 5–15 seconds for open tabs and indexed local files, and stream a follow-up only if more sources are still being inspected.
- **cost:** Usually $0.01–$0.06 per query; screenshot OCR and synthesis dominate, while local text extraction should be nearly free.
- **security:** Never upload full documents or page bodies by default. Each surface returns minimal quoted spans, title, URL/path, timestamp, and a sensitivity label; credentials, cookies, and unrelated tabs remain local. The spoken answer must distinguish direct quote, inference, and missing access.
- **missing:** A paired multi-source query route that fans out to the Mac and browser session and merges typed evidence; Local document indexing or bounded file-search on the Mac agent; Browser-extension extraction of the active authenticated tab with explicit tab/session identity; A provenance schema and relay audio formatter for citations short enough to speak


## Changes it proposed to its own stack

### `integration` — Build a transport-arbitration session layer that treats the physically connected nRF9160 USB serial link and the LTE/WebSocket link as two interchangeable legs of one voice session. It should detect USB attach/detach, authenticate the pendant, mirror button/audio state, migrate an active turn without replaying audio, and expose the selected leg plus packet/latency counters in the session receipt. When USB is present it should be the immediate development and home fallback; when it disappears, the session should resume over LTE if registered.
- **owner gets:** The owner can wear or dock the pendant without changing how it behaves. A conversation started at the desk will not die when they walk away, and the hardware that is physically testable today becomes a real end-to-end path instead of a disconnected accessory.
- effort: Medium-high: a relay session coordinator, USB serial framing/authentication on the Mac harness, firmware transport state machine, and migration tests with packet loss and detach at every audio phase.  ·  risk: A migration can duplicate or clip speech, or accidentally bind another serial device. Use monotonically numbered audio frames and session epochs; discard old-epoch packets, drain only acknowledged frames, and fall back to a fresh turn after a failed handoff. Never persist routine audio merely to migrate it.
- cost: No recurring API cost beyond existing voice traffic; engineering cost is substantial. USB serial uses negligible additional power, while LTE remains the existing radio cost.  ·  latency: USB can reduce round-trip latency while docked; attach/detach handoff may add 100–500 ms at a turn boundary. Mid-speech migration should be avoided unless frame continuity is proven.
- security: The Mac must prove possession of the paired pendant before becoming a transport leg; bind credentials to device/session epochs and do not expose raw serial control to arbitrary local processes. Audio remains on the existing relay path.
- depends on: A real USB serial bridge service for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; Pendant registration/identity handshake over USB, since LTE registration is not currently present; Relay session state that supports transport epochs and numbered audio frames; Hardware validation using the already verified 24 kHz, 60 ms Opus framing


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-visible additions: (1) delegated Mac/browser work that pauses only for a sharply specific pendant clarification and then resumes, (2) provenance-bearing answers that join authenticated browser tabs with local Mac documents, and (3) seamless USB↔LTE voice-session migration so the physically connected pendant works today and walking away does not kill a conversation. The transport proposal explicitly builds on verified 24 kHz/60 ms audio and the live USB devices.

**Biggest unknown:** The recorder flagged the first two as near existing backlog themes, so their durable distinction is the missing cross-surface state/evidence protocol rather than the generic ideas. The USB/LTE transport layer is the clearest genuinely new gap, but it still needs a real serial bridge and pendant identity handshake.

