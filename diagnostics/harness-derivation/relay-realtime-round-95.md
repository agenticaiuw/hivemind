# Harness derivation — relay-realtime — round 95

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “bookmark this moment,” save what I just said together with what was on my Mac and in my browser, so later I can ask “what was I looking at when I said that?” and get the exact context back."
- **useful because:** The owner moves between being away with the pendant and working at the Mac. A spoken bookmark would preserve fleeting ideas and the surrounding work context instead of forcing them to stop, copy URLs, or reconstruct which tab and app mattered. This depends on the wearable capturing the intent, the relay anchoring time, and the Mac/browser surfaces contributing context that no single node can see.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime model only detects the short bookmark utterance and acknowledges it; a cheaper background model later indexes and summarizes the captured transcript/context. Retrieval can use the slower model unless the owner asks for an immediate answer.
- **latency:** Acknowledge in under 500 ms. Capture a context bundle opportunistically within 3 seconds; later retrieval should answer within 5 seconds, with partial results if the Mac or browser is offline.
- **cost:** About one realtime turn for detection/acknowledgment, then roughly $0.01–$0.05 per indexed bookmark and retrieval depending on transcript length and screenshot/OCR use. Storage and browser/Mac polling dominate operational cost, not the spoken acknowledgment.
- **security:** The bundle may include private page titles, URLs, visible text, window names, or audio. Keep it encrypted, retain only an explicit rolling window around the bookmark, redact passwords/form fields, show the owner exactly which surfaces were captured, and provide deletion by bookmark. Never capture arbitrary screen content without the bookmark trigger.
- **missing:** A relay endpoint that atomically creates a bookmark and returns a capture token; Mac-side snapshot provider for active app/window and a bounded text or screenshot capture; Browser-extension hook that reports the active tab and bounded page metadata for that token; Encrypted durable bookmark storage with retention and deletion; A retrieval route that searches bookmarks and cites each contributing surface

### "While I’m looking at a page in my authenticated browser, let me ask the pendant “does this match anything in my project?” and have you compare that page with my local project on the Mac, then tell me the relevant conflicts, files, and next step without making changes."
- **useful because:** This turns the pendant into a bridge between information trapped behind browser sessions and work stored locally. Today the browser can inspect a page and the Mac can inspect files, but neither surface alone can answer whether the two contexts agree. It is especially valuable when the owner is away from the keyboard and wants a quick, grounded answer rather than a generic summary.
- **path:** pendant → relay → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime handles intent recognition and a short progress/answer turn only. Browser extraction and local-project search run on a cheaper background planner; realtime synthesizes only the compact, cited result returned by both surfaces.
- **latency:** Acknowledge immediately, return an initial answer in 8–15 seconds, and stream “browser read / local search / comparison” milestones so the owner is not left guessing. If either surface is offline, explicitly return the side that was available rather than inventing a comparison.
- **cost:** Approximately $0.03–$0.15 per comparison, dominated by sending page excerpts and local search results to the comparison model. Avoid screenshots and full repositories by default; use bounded, cited excerpts and cache hashes for unchanged content.
- **security:** Authenticated page content and private source code leave their respective surfaces and meet at the relay/model. Minimize data to selected excerpts, redact secrets and credentials, enforce same-owner session binding, retain no raw page/source by default, and include source citations so leakage or mistaken matches are visible. Read-only by default; any requested edit must be a separate explicit action.
- **missing:** A single correlation/job API that binds one spoken request to a browser extraction and a Mac-terminal project search; A browser command for bounded semantic/text extraction with URL and page-section citations; A Mac planner/terminal command for scoped project search that returns file/line citations without executing mutations; A relay comparison worker that merges two typed result sets and streams progress to the pendant; A compact spoken-result protocol plus dashboard trace showing exactly what page and files were compared


## Changes it proposed to its own stack

### `relay` — Implement the granted-but-unimplemented relay_route_intent and server_browser_actions tools as first-class relay capabilities, wired to the existing routing and job/receipt system. relay_route_intent should create or attach to a relay job, forward intent and context to the appropriate downstream surface (mac-planner or mac-vision), and return a job reference. server_browser_actions should run sandboxed browser sessions in the relay environment when the Mac is offline, with read-only extraction by default and explicit mutation actions logged with receipts.
- **owner gets:** When they speak, the relay can route tasks explicitly and reliably, and still help even if the Mac is sleeping. This makes the pendant feel dependable: "open that doc", "check a page", or "search this" can progress without guessing or waiting for another device.
- effort: Medium. Needs backend plumbing, job lifecycle integration, and browser sandbox integration. No major UI work.  ·  risk: Routing mistakes could send work to the wrong surface; browser automation could mutate state. Mitigate with intent labels, allowlisted actions, receipts, and conservative defaults (read-only).
- cost: Adds relay compute and potential browser runtime costs; dominated by external browser session time and extraction volume.  ·  latency: Improves perceived responsiveness because routing happens immediately; browser runs add variable latency but avoids waiting for Mac availability.
- security: Browser sessions handle sensitive data; enforce origin allowlists, session isolation, and strict logging. Do not invent authentication; rely on existing auth flows.
- depends on: Durable job runner or equivalent reliable job persistence (currently noted as missing).; Receipt/undo system already partially shipped; extend for relay-initiated actions.

### `hardware` — Add a coin-size low-power vibration actuator with a dedicated tactile acknowledgement pattern, plus a hardware microphone-disconnect switch whose state is readable by firmware and reported to the relay. Keep the existing button/LED as fallback; vibration patterns should distinguish acknowledgment, completed work, and failure without speech.
- **owner gets:** The owner can use the pendant in meetings, transit, or public places without playing audio aloud or staring at an LED. They can feel that a request was accepted or completed, and the physical mic switch gives an immediate, trustworthy way to stop listening.
- effort: Moderate enclosure/PCB revision, a haptic driver, switch debounce and firmware patterns, and relay handling for the offline/privacy state. Validate skin-contact comfort and false presses in daily wear.  ·  risk: Added power draw, thickness, and vibration could be annoying or wake the owner. Use short capped pulses, configurable intensity, and a hardware-safe fallback to LED-only. If the switch state is ambiguous, default to mic-off and expose the state in every voice-run receipt.
- cost: Roughly $2–$6 in components and PCB/enclosure changes at prototype volume; approximately 5–20 mA only during brief vibration pulses, with negligible average draw if patterns are capped.  ·  latency: No network latency; local acknowledgment can happen immediately. Privacy-state propagation should be best-effort and must never delay the physical mic cutoff.
- security: Strongly improves privacy because microphone disconnection is physical rather than model-controlled. Firmware, relay, and dashboard must treat mic-off as authoritative and avoid claiming that audio was captured while it was off.
- depends on: Firmware support for a persistent microphone/privacy state; Relay voice-run records carrying device privacy state; A documented haptic pattern/state protocol for pending, success, and failure; Battery and enclosure validation on the nRF9160 pendant


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing gaps: time-indexed spoken context bookmarks spanning pendant/Mac/browser, authenticated-page versus local-project comparison with cited results, and discreet trustworthy pendant feedback/privacy via haptics plus a physical microphone cutoff. Each proposal names the cross-surface work and missing pieces rather than assuming today’s wiring.

**Biggest unknown:** Whether the backlog already contains a near-duplicate of the newly recorded proposals; the proposal tool flagged similarity, but I did not re-open or re-discover anything this round per instruction.

