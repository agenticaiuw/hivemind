# Harness derivation — relay-realtime — round 188

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What’s going on with my Mac right now?"
- **useful because:** Quick, low-friction status readouts keep the owner from interrupting their flow or walking back to the computer.
- **path:** relay → mac-bridge
- **model tier:** Realtime for the spoken summary; no need for a planner.
- **latency:** Under a second when the Mac is online; otherwise a clear offline message.
- **cost:** Very low; one status call.
- **security:** Summaries should avoid reading sensitive content unless explicitly asked.
- **missing:** 

### "Read this page and summarize it for me."
- **useful because:** Lets the owner consume information hands-free without opening a browser or switching devices.
- **path:** relay
- **model tier:** Realtime for conversation; underlying fetch can be done with an existing read-only tool.
- **latency:** A few seconds for fetch and summary; offer a shorter version if interrupted.
- **cost:** Moderate; dominated by web fetch and summarization.
- **security:** Only fetch public URLs unless explicit creds are provided via another trusted surface.
- **missing:** 

### "“I’m away from my Mac. Look at what is currently on my screen and in the relevant browser tab, figure out what I’m looking at, and explain it to me in three spoken sentences; if the screen changes while you investigate, tell me that the answer may be stale.”"
- **useful because:** This would make the pendant a true remote eye and interpreter rather than a voice remote. The relay can keep the conversation live while Mac vision and the browser inspect the exact current UI, resolving references like “this” that the owner cannot describe from across the room.
- **path:** pendant → relay → mac-vision → mac-planner → browser-extension
- **model tier:** Realtime relay for clarification and concise speech; gpt-4.1-mini vision loop for screenshots/OCR; cheaper planner only to select the relevant tab and gather browser text.
- **latency:** Initial spoken acknowledgement under 500 ms; first grounded answer within 8 seconds. Re-check the screen immediately before speaking and mark evidence older than 3 seconds as stale.
- **cost:** Roughly $0.03–$0.15 per request, dominated by 2–5 screenshot vision calls; relay speech and short planner context are minor.
- **security:** Screen pixels and authenticated page text leave the Mac to the relay/model. Require an explicit per-turn scope (current screen/current tab), redact passwords and payment fields in the Mac harness, and never claim freshness without a final timestamped capture.
- **missing:** A live mac-vision computer-use loop (currently disabled) that can return timestamped screenshots and accessibility text without mutating the Mac; A relay conversation context object that binds the owner’s deictic references (“this”, “that tab”) to a specific capture; A freshness/evidence envelope carried through /plan and /execute and rendered in the spoken response

### "“Take this thought from my pendant and turn it into a finished, source-backed answer: search the web, compare the claims against the pages you found, and read me the answer with links and uncertainty—not just a plausible summary.”"
- **useful because:** The owner can dictate anywhere, but today the relay either answers from its own context or hands off actions. This would combine a fleeting spoken idea with fresh browser evidence and make factual uncertainty audible, useful for decisions made while walking or away from the desk.
- **path:** pendant → relay → browser-extension → mac-planner
- **model tier:** Realtime relay for capture, intent clarification, and spoken synthesis; a slower background planner/browser pass for search, page extraction, quote alignment, and contradiction checking.
- **latency:** Acknowledge in under 500 ms; deliver a 20–40 second answer in 15 seconds for ordinary searches, or explicitly say “still checking” and push the result later for multi-page research.
- **cost:** About $0.05–$0.30 per invocation, dominated by browser/page extraction and a verification pass; use a cheap model for extraction and reserve realtime for the final dialogue.
- **security:** Search queries and dictated text are transmitted. Treat page content as untrusted instructions, preserve canonical URLs and quote spans, and disclose when a source was inaccessible or stale. Never silently use an authenticated browser session when public search suffices.
- **missing:** A citation-and-claim data structure with quote spans, retrieval timestamps, and contradiction status; A browser research worker that can follow multiple pages through the existing browser inspection routes and return evidence rather than prose; A relay response format that speaks calibrated confidence and exposes source links through the paired phone or later inbox

### "“I’m about to leave. Watch the exact document and app state I’m working on, and when I next press the pendant, tell me what changed since this moment—who changed it, what changed, and whether I need to act.”"
- **useful because:** This creates a useful handoff across time and distance without requiring the owner to remember a filename or keep a Mac window open in their head. It turns the pendant into a continuity sensor for one explicitly selected work item, not an ambient surveillance system.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** Cheap background/diff worker for accessibility-tree, document metadata, and browser snapshots; realtime relay only on the next button press to summarize material changes and ask a focused follow-up.
- **latency:** Capture baseline in under 3 seconds; subsequent checks can be opportunistic. On press, answer in under 2 seconds if the latest snapshot exists, otherwise report that no fresh observation is available.
- **cost:** Approximately $0.01–$0.08 per check, mostly Mac/browser diffing; use hashes and accessibility metadata before paying for vision, with a vision call only for ambiguous visual changes.
- **security:** The owner must explicitly choose the app/document and the watcher must stop on app close or scope change. Store hashes and minimal diffs by default, not continuous screenshots; authenticated content stays on the Mac unless needed for the spoken answer.
- **missing:** A durable watch worker or alarm facility (Cloudflare Cron/Durable Object alarm or Mac launch agent), since no scheduler/background worker exists today; A scoped watch-registration protocol that binds one pendant session to one app/document/tab and expires safely; Semantic diffing across macOS accessibility trees, file revisions, browser DOM, and screenshots, with author attribution where the source provides it

### "“While I’m away from the desk, listen to the audio of the meeting running on my Mac and give me a low-latency spoken translation or whisper only the decisions and action items through the pendant; stop immediately when I press the button.”"
- **useful because:** The pendant currently carries the owner’s voice to the relay, but it cannot make a remote Mac meeting audible or useful while the owner is moving around. This would let the owner stay informed without carrying a laptop, and the physical stop gesture gives an unambiguous end to capture.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** A streaming speech/translation model for low-latency partials; a cheaper rolling summarizer for decisions and action items. Relay should forward only the selected mode (translation or decisions) to the pendant, not raw meeting audio.
- **latency:** Under 1.5 seconds from a spoken phrase to its translated/filtered audio; stop forwarding within 250 ms of the pendant button event. Reconnect with sequence numbers after transient Mac or relay loss.
- **cost:** Approximately $0.10–$0.60 per 30-minute meeting, dominated by continuous audio transcription/translation; decision-only mode can reduce cost with larger rolling windows.
- **security:** This is highly sensitive third-party audio. Require an explicit physical start and stop, display a recording LED on the Mac, encrypt transport, avoid persistent raw-audio storage, and expose participant/meeting scope. The system must say when packets were missed rather than fabricate a translation.
- **missing:** A Mac-side capture source for the selected meeting application/system-audio stream, with OS recording disclosure and a hard stop endpoint; A relay WebSocket stream distinct from the existing turn-based audio pipeline, with backpressure, sequence numbers, and mode switching; A pendant downlink mixer/ducking mode so translated speech does not collide with an active owner turn; Per-session retention controls that discard raw meeting audio while retaining only the owner-requested translated snippets or action items


## Changes it proposed to its own stack

### `context` — Introduce a small shared preference store for notification style (short vs detailed), verbosity, and privacy level, so all agents don’t need the full history every turn.
- **owner gets:** Consistent behavior across devices without repeating preferences in every conversation.
- effort: Medium. Needs a minimal schema and read-through cache.  ·  risk: Stale preferences. Mitigate with versioning and TTL.
- cost: Low; reduces repeated context transmission.  ·  latency: Minimal; cached reads are fast.
- security: Store only non-sensitive preferences; keep secrets elsewhere.
- depends on: A memory projection or key-value store accessible to relay and Mac


## What it asked for

_Nothing._
## Its own summary

Recorded four new owner-facing capabilities: (1) a remote, evidence-grounded “what am I looking at?” answer using a final timestamped Mac/browser capture; (2) source-backed dictated research with claim/quote alignment and spoken uncertainty; (3) an explicitly scoped work-item change watcher that reports material changes on the next pendant press; and (4) a physical-start/stop remote meeting interpreter or decision whisper. The largest missing pieces are not ordinary routing: a live mac-vision capture loop, evidence/freshness envelopes, citation/claim verification, durable scoped watch execution, Mac meeting-audio capture, and a streaming relay with interruption/backpressure and strict retention controls.

**Biggest unknown:** Whether existing /watches and pipeline routes already expose enough implementation to support scoped change watching or streaming meeting audio; the recorder accepted the proposals but warned those routes may be connective rather than absent.

