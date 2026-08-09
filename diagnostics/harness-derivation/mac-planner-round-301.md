# Harness derivation — mac-planner — round 301

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-and-browser-state** — AI Pendant Agent currently has Accessibility and Screen Recording trusted, synthesized input verified, and 19 apps running; browser has four durable sessions, with the default Safari tab on YouTube. mac_readonly_inspect browser_tabs is unresolved because action:browser_inspect and POST /browser/inspect tie, so active-tab reads need a deterministic route selection.
  - evidence: mac_readonly_inspect operation running_apps/foreground_app returned GET /observe HTTP 200 at 2026-08-09T04:17:23Z with accessibility.trusted=true, screenRecording=true, eventsPost=true, and four browser tabs; browser_tabs call returned an ambiguity error.

## Capabilities it proposed

### "When I press the pendant's bookmark button during a meeting, turn that moment into a concrete follow-up task with the meeting name, timestamp, current browser page, and a link, then put it in Reminders and tell me what was created."
- **useful because:** It converts an in-the-moment physical cue into an actionable artifact without making the owner stop to dictate details. The pendant supplies the only reliable moment signal, Calendar identifies the meeting, the browser supplies the page being discussed, and the Mac creates the task.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background for correlation and task drafting; realtime only for the brief spoken acknowledgement
- **latency:** Acknowledge the button within 1 s; create the task within 10 s. If Calendar/browser correlation is ambiguous, create a clearly marked uncategorized task rather than guessing.
- **cost:** Low: one small event correlation plus optional short model call; dominated by background model inference, not realtime audio.
- **security:** The bookmark event, calendar title, URL, and task text leave the Mac only to the relay. Redact page body by default and send URL/title only. Creating a Reminder is a local mutation and should follow the owner's explicit routine policy; ambiguous meeting identity must not silently attach to a different meeting.
- **missing:** A relay event consumer that joins offline_moment_bookmark records to the nearest active Calendar event; A browser context read that returns the active tab title and URL deterministically (browser inspection currently has an ambiguity between action and route); A named Mac routine/action for creating a Reminder with a durable receipt and source metadata

### "Before I leave, let me ask 'is my pendant ready?' and get a spoken answer based on a real end-to-end test: verify the USB-connected pendant and audio bridge, run the synthetic audio fixture, check packet loss/underruns and storage, and tell me whether a real call is safe."
- **useful because:** The owner currently has to trust that yesterday's firmware and today's cable, bridge, codec, and storage are all healthy. This turns the shipped diagnostic fixture into a one-command confidence check that catches silent failures before the pendant is worn away from the Mac.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Deterministic checks and threshold evaluation; use the cheap background tier only to phrase the result. Realtime is unnecessary except for the final spoken response.
- **latency:** USB presence and basic checks in 2 s; full fixture in under 30 s. Return partial results if the pendant is offline or LTE is unregistered, never wait indefinitely.
- **cost:** Near-zero API cost. The dominant cost is the 24 kHz fixture's measured CPU time and a short local diagnostic run.
- **security:** The fixture must generate synthetic audio only and never read or retain microphone content. Store counters and pass/fail, not raw PCM. USB paths are trusted bench paths only; the result must explicitly say 'USB bench verified' rather than implying LTE readiness.
- **missing:** A bounded Mac bench runner that invokes the existing serial diagnostic hooks and parses sequence/counter output into structured fields; A health aggregation route combining pendant fixture, ESP32 bridge presence, microSD status, and last duplex QoS counters; A policy/versioned threshold table for packet drops, underruns, decode time, and storage free space; A spoken result adapter that can deliver a concise pass/warn/fail receipt to the owner without opening a microphone

### "When I say 'send this to my phone,' take the page I am currently viewing in the authenticated browser, strip trackers, open it in the real iPhone through iPhone Mirroring, and leave a short note on the Mac with the title, source URL, and time sent."
- **useful because:** It bridges the browser session that only the Mac can reach to the owner's real phone without asking them to copy a URL or expose browser credentials to the relay. It is useful when leaving the desk, and the resulting note makes the handoff auditable.
- **path:** browser → mac-planner → ios → relay → dashboard
- **model tier:** Deterministic extraction and URL normalization; cheap background model only if the owner asks for a one-sentence summary. No realtime model is needed.
- **latency:** Read active tab and launch on the phone within 5 s. If iPhone Mirroring is unavailable, save the normalized URL locally and report that the phone handoff did not occur.
- **cost:** Negligible API cost; local browser and iPhone Mirroring operations dominate latency.
- **security:** Never transmit page body, cookies, or authenticated headers to the relay. Only the normalized URL and visible title should cross the local boundary. Opening a URL on the phone is an external side effect and must be covered by the owner's explicit handoff policy; tracker stripping must not alter signed/authenticated URLs incorrectly.
- **missing:** A deterministic active-tab context route that resolves without the current browser_inspect ambiguity; An iPhone Mirroring adapter that targets the mirrored device rather than the Mac's default browser; A URL-normalization policy with a reversible local handoff record; A local note/receipt schema that links the browser tab id to the iPhone-open result

### "When I walk away and the pendant loses its USB connection, preserve a tiny handoff of what I was doing — active project, browser page, next unfinished action, and any unsaved draft name — and read it back when the pendant reconnects, without copying document contents."
- **useful because:** Today the pendant, relay, and Mac are separate at exactly the moment the owner leaves the desk. This would make USB disconnect a useful transition rather than a silent failure, while keeping sensitive document bodies local.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Deterministic local collection and event correlation; a cheap background model may compress the handoff to one sentence. No realtime reasoning is needed.
- **latency:** Capture within 2 s of disconnect; persist before the Mac sleeps; speak the handoff within 3 s of the next authenticated pendant connection.
- **cost:** Low API cost; dominated by local project/browser correlation and one short summarization call.
- **security:** Only names, titles, URLs, and bounded metadata leave the Mac; never document bodies or unsaved text. The handoff must expire after a short owner-configured TTL and be encrypted at rest. Do not infer an unfinished action from keystrokes without a visible confidence label.
- **missing:** A Mac serial-disconnect event source that is distinct from generic process failure; A bounded project/active-document metadata collector that avoids reading contents; A relay handoff record keyed by device session and expiry; A reconnect delivery path that distinguishes a new handoff from a replay

### "For anything you tell me over the pendant, let me ask 'show me why' and have the Mac open a compact evidence card: the exact Calendar/Mail/browser/project sources, timestamps, and which parts were inferred versus directly observed."
- **useful because:** A spoken answer is hard to trust or act on when the owner cannot inspect its basis. This creates a physical-to-desktop path from audio claim to inspectable evidence without dumping private source contents into the conversation.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use deterministic source IDs and timestamps; use the background tier only to write the short explanation. Realtime should only recognize the follow-up phrase.
- **latency:** Acknowledge 'show me why' in under 1 s and open the evidence card within 5 s. If a source expired, say so rather than reconstructing it from memory.
- **cost:** Low: mostly local indexing and one small explanation call. Storage and source bookkeeping dominate, not inference.
- **security:** Evidence cards must default to snippets and metadata, not full mail bodies or authenticated page content. Every source access needs a local audit record and a redaction policy. Never fabricate provenance for model-generated claims; mark unsupported claims explicitly.
- **missing:** A provenance graph that attaches source spans and observation timestamps to relay answers; A Mac evidence-card surface that can open without exposing full source data to the relay; A pendant follow-up correlation ID connecting a spoken question to the last answer; A redaction-aware source preview for browser and Mail

### "When I press the pendant button and say 'scan this,' use the real iPhone camera through iPhone Mirroring to read the QR code or barcode in front of me, tell me what it contains over the pendant, and offer to open the resulting link on the Mac without transmitting the camera image to the relay."
- **useful because:** The pendant has no camera and the relay cannot see the physical world, but the owner's real phone can. This makes a physical handoff—event ticket, package, product, Wi‑Fi label, or document—usable hands-free while keeping the image local to the Mac/iPhone path.
- **path:** pendant → relay → mac-planner → ios → browser
- **model tier:** Use on-device/iPhone barcode and QR decoding where possible; background model only for a non-URL payload explanation. Realtime is unnecessary except for the spoken result.
- **latency:** Start the scan within 2 s and return a decoded value within 8 s. Stop after a bounded timeout and tell the owner no code was found.
- **cost:** Minimal API cost; local camera control and decoding dominate. No image upload should be required.
- **security:** Camera frames must stay on the Mac/iPhone path and be discarded after decoding. Opening a decoded URL is a consequential external action and needs an owner policy; display the normalized destination and distinguish arbitrary text from URLs. Never scan continuously—the pendant press is the sole trigger.
- **missing:** A reliable iPhone Mirroring camera-control and frame-read adapter; A local QR/barcode decoder callable by the Mac agent without arbitrary shell exposure; A pendant command/result correlation for the spoken scan request; A safe URL preview/open policy for decoded destinations


## What it asked for

_Nothing._
## Its own summary

Discovered live state and produced three non-duplicate owner capabilities: (1) pendant bookmark during a meeting becomes a Calendar/browser-linked Reminder task, (2) a spoken “is my pendant ready?” runs the synthetic end-to-end fixture and reports real health thresholds, and (3) “send this to my phone” hands the active authenticated browser page to the real iPhone via Mirroring with an auditable local note. I also recorded that Accessibility and Screen Recording are now genuinely granted and input posting is verified. A workspace-wide privacy proposal collided with an existing backlog item and was not repeated.

**Biggest unknown:** The active browser context path is still ambiguous: action:browser_inspect and POST /browser/inspect tie in resolution. I still need a deterministic browser active-tab/title/URL read, plus a bounded USB diagnostic runner and structured health aggregation. For the three capabilities, the remaining gaps are the relay bookmark-to-calendar join, iPhone Mirroring targeting, and explicit owner policies for local mutations.

