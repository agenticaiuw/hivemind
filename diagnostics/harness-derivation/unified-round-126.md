# Harness derivation — unified — round 126

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Mark this moment.” While I’m speaking, have the pendant create a durable, timestamped marker; the Mac captures the active app/window and authenticated browser tab, the relay stores the audio/transcript and provenance, and later I can ask “what was that moment?” to retrieve the exact context and continue the task."
- **useful because:** A single button press turns fleeting thoughts, decisions, or meeting moments into a retrievable evidence bundle. No other node can know both the physical instant and the private screen state; together they can.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** background for transcription/indexing; realtime only for the immediate spoken acknowledgement
- **latency:** LED acknowledgement under 150 ms; marker receipt under 3 s; indexing may finish in the background
- **cost:** ~$0.01–$0.05 per marker depending on transcription length; storage dominates only for retained audio
- **security:** Audio and private tab metadata leave the device to the authenticated relay; redact secrets and page bodies by default, retain source hashes and require confirmation before sharing a marker. Button gesture must be unambiguous.
- **missing:** pendant marker gesture and bounded local buffer; Mac active-window and browser-tab snapshot API; relay marker index with audio/transcript retention policy; spoken/dashboard retrieval by time, project, or quoted phrase

### "“Send this page to my pendant.” From the currently authenticated Safari tab, extract the readable article or task (not passwords or form fields), create a short spoken summary plus a listen-later audio item, and deliver it through the relay/Mac-to-ESP32 audio bridge; the pendant button pauses, resumes, or skips items and the browser keeps the source citation."
- **useful because:** It lets the owner leave the desk without losing the exact private webpage they were reading. Browser authentication supplies access, the Mac supplies the bridge, and the worn device supplies an interruption-free listening and control surface.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** background/cheap model for extraction and summary; realtime only for the spoken confirmation and button commands
- **latency:** Acknowledge the handoff in under 2 s; begin playback within 10 s for a normal article; long pages continue processing in background.
- **cost:** ~$0.01–$0.08 per page for extraction, summary, and speech; audio storage and transfer are the dominant variable costs.
- **security:** Read only the active authenticated tab and explicitly exclude password inputs, tokens, and editable form controls. Keep source URL and citation private; require confirmation if the page contains a sensitive category or if any action beyond reading is requested.
- **missing:** a browser command to package the active tab as a citation-bearing reading item; a durable audio queue shared by relay and Mac; pendant playback controls and queue state; source-aware retention and deletion for generated audio

### "“Explain that.” During a conversation or meeting, press and hold the pendant for one sentence; have the Mac transcribe the captured snippet, search the open browser context and the public web for the referenced term, and speak a concise explanation back through the bridge without interrupting the meeting audio. Save the cited explanation only if I say “keep it.”"
- **useful because:** The owner can resolve an unfamiliar name, acronym, or claim hands-free at the exact moment it matters. The pendant hears the utterance, the Mac can inspect private context, the browser can research, and the relay coordinates a low-latency answer.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** realtime for transcription, disambiguation, and one-sentence response; background model for optional cited research expansion
- **latency:** Capture ends on release; first answer within 5 s, with a short fallback if browser research is slow. The meeting audio path must resume without a gap longer than one frame.
- **cost:** ~$0.02–$0.10 per explanation; web fetches and speech generation dominate, while short realtime transcription is modest.
- **security:** Capture is explicitly gesture-gated and should not continuously monitor. Private tab text must be limited to relevant visible context, never passwords/forms; do not store the snippet or answer unless “keep it” is spoken. Public search queries can leak terms, so offer a local/private-context-only mode.
- **missing:** gesture-gated snippet capture with audio-path ducking and restoration; Mac/browser context disambiguation endpoint; a cited low-latency answer route and explicit keep/discard persistence; meeting-safe echo cancellation and output ducking


## Changes it proposed to its own stack

### `firmware` — Add a local “moment marker” state machine to the pendant: a long press snapshots the last 8 seconds of encoded mic frames into a bounded ring, emits one framed marker event over the existing USB/UART or LTE transport with monotonic timestamp and sequence number, then immediately resumes live audio. The relay acknowledges receipt and the Mac/browser collectors attach current context asynchronously; never block the audio thread or attempt transcription on the nRF9160.
- **owner gets:** They can capture a decision or insight even when the conversation moves too quickly to repeat it, and the marker survives a dropped link long enough to be indexed when the Mac reconnects.
- effort: Medium firmware plus relay event schema and a small Mac context collector; test ring-buffer overwrite, button bounce, reconnect, and power loss.  ·  risk: A stuck button or noisy UART could create repeated markers; debounce, one-marker-per-press, sequence deduplication, and a visible LED pattern recover safely. The ring is intentionally bounded so it cannot fill RAM.
- cost: No per-use model cost on-device; roughly 8–20 kB RAM/flash depending on frame duration and metadata. Relay transcription/storage costs apply only when the owner retains a marker.  ·  latency: <150 ms local LED/event acknowledgement; context attachment and transcription are asynchronous and may take seconds.
- security: Local audio is retained briefly only in volatile memory; relay must encrypt markers, apply short default retention, and omit page contents unless explicitly requested.
- depends on: a marker event contract between firmware, relay, Mac, and browser; a retrieval surface for marker provenance

### `hardware` — Replace the prototype pendant’s single-button/single-LED UI with a production interaction module: two tactile buttons plus a low-power haptic actuator and RGB status indicator, while retaining the existing I2S full-duplex audio and USB service path. Define distinct gestures for mark, private/mute, playback navigation, and approval; use haptics for acknowledgements and errors when audio output is unavailable or socially inappropriate.
- **owner gets:** The owner can control and trust the assistant discreetly in a meeting, on a street, or with headphones disconnected. They no longer have to guess whether a long press registered from one ambiguous button and one tiny LED.
- effort: High: industrial design, GPIO/I2C allocation, waterproof wearable enclosure, firmware gesture/accessibility work, and a production electrical redesign; validate accidental-press resistance and one-handed operation.  ·  risk: More controls can cause accidental actions or confusion; require distinct press durations, haptic patterns, lockout after ambiguous gestures, and a spoken/visual configuration tutorial. If the haptic or RGB module fails, the current audio/LED path remains usable.
- cost: Roughly $3–$12 added BOM in small volume plus enclosure redesign; haptic pulses are tens of milliwatts and negligible relative to radio/audio peaks. No per-use API cost.  ·  latency: Local acknowledgement can be under 100 ms, substantially faster than relay confirmation; no network latency added.
- security: A dedicated private/mute control reduces accidental recording and output disclosure. Firmware must make privacy state fail-closed across reboot and visibly/haptically distinguish muted from active.
- depends on: production pendant constraints and enclosure design; a stable gesture/event contract shared with relay, Mac, and browser; local privacy and output-mute state semantics


## What it asked for

_Nothing._
## Its own summary

This round produced three new cross-surface owner capabilities and one implementable firmware change. The strongest is “Mark this moment”: a long press captures a bounded recent audio window, while the Mac and authenticated browser snapshot active context and the relay makes the moment searchable with provenance. I also proposed browser-to-pendant page handoff with citations, and gesture-gated “Explain that” for meeting terms. The firmware change defines the local marker ring and non-blocking event protocol. Today the Mac bridge and Safari are online; the pendant is physically USB-connected but not LTE-registered, so USB-tether testing is the immediate path.

**Biggest unknown:** The end-to-end audio acceptance criteria and the exact Mac/browser APIs for active-window/tab snapshots remain unspecified. I still need those contracts, plus a durable marker/audio queue and retrieval surface; without them the proposals are connective designs rather than runnable owner experiences.

