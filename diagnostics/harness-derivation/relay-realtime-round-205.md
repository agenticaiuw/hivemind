# Harness derivation — relay-realtime — round 205

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I start a task, keep an ear on it and warn me if it stalls or needs my input."
- **useful because:** Completion notifications are not enough. A task can hang, fail early, or wait for a login/permission. Early warnings save time and prevent silent failure.
- **path:** relay → mac-bridge → browser → pendant
- **model tier:** background model for monitoring; realtime only to confirm the watch was started
- **latency:** Immediate confirmation, then alerts within seconds to a couple minutes depending on polling interval and urgency.
- **cost:** Low to moderate; dominated by periodic status checks and occasional short alert generation.
- **security:** Alert content may expose sensitive app or document names; keep summaries minimal unless the owner asks for detail. Ensure alerts are delivered only to the owner’s paired session/device.
- **missing:** A real job-monitoring mechanism with stall heuristics (status age, no progress receipts, repeated errors); A relay-to-pendant alert delivery implementation (could reuse the existing inbox concept); A small policy layer to decide when to alert vs. wait

### "Run a spoken hardware self-test: "Check whether my pendant audio is healthy right now.""
- **useful because:** The owner can diagnose the actual worn device from anywhere in seconds instead of guessing whether silence comes from the microphone, LTE/USB link, Opus path, bridge, or speaker. It turns the currently attached, testable hardware into a trustworthy daily instrument and reports concrete measurements, not a generic online/offline answer.
- **path:** pendant → relay → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime relay interprets the short request and speaks the result; mac-terminal performs the hardware probe and parses measurements deterministically; no expensive model is needed for signal analysis.
- **latency:** 20 seconds for a full test; speak an early "testing" acknowledgement within 500 ms and stream a concise result when complete.
- **cost:** <$0.01 per invocation; dominated by one short realtime turn, with shell probes and serial capture essentially free.
- **security:** The probe reads device diagnostics and may access the USB serial endpoints, but does not modify owner files. It must redact serial identifiers from spoken/dashboard output and clearly distinguish stale LTE health from the live USB-attached test.
- **missing:** A Mac allowlisted hardware-test action that can flash/run the audio probe, capture serial output, and return structured metrics; A relay result schema for measured audio/uplink/bridge health rather than prose; A pendant button/LED convention for a test-in-progress state

### "Let me say "Make this ready for tomorrow's client call" and have the hive prepare, but not send, everything it can find."
- **useful because:** One natural request would turn scattered preparation into a reviewable package: calendar details and local project context from the Mac, relevant authenticated browser pages, and a short spoken briefing on the pendant. The owner gets a useful deliverable while away from the desk without delegating the judgment or risking an external send.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Realtime handles intent and clarifying one missing constraint; mac-planner and browser harness do the long multi-step collection; a cheaper background summarizer produces the packet; relay only speaks the headline and review link.
- **latency:** Acknowledge in under 1 second; preparation may take 1–3 minutes. The owner should receive a completion alert and be able to ask for a spoken three-item summary.
- **cost:** Roughly $0.05–$0.30 depending on browser pages and document volume; model summarization and authenticated page extraction dominate.
- **security:** Browser sessions and local documents leave their originating surfaces only as narrowly scoped excerpts. No message, calendar invite, upload, or external send is allowed in this mode. The dashboard must show every source and generated artifact, with explicit expiry and a prominent discard control.
- **missing:** A cross-surface preparation job that can fan out to Mac files/calendar and the authenticated browser session; A durable artifact bundle with source citations and a review-only state; A relay notification path that can announce the finished bundle while the voice session is over; A deterministic no-send policy enforced by the executor

### "When I say "What am I looking at?", have the pendant and Mac jointly identify the thing in front of me and tell me only what helps me act next."
- **useful because:** The pendant alone has no camera and the Mac alone cannot know what the owner is pointing at. A coordinated mode would use a deliberate phone/desktop or browser capture, voice context, and local visual analysis to answer practical questions such as which cable, menu, document, or error is in view—without making the owner narrate it.
- **path:** pendant → relay → mac-vision → mac-planner → browser-extension
- **model tier:** Realtime relay keeps the dialogue short; mac-vision handles image grounding; mac-planner performs a follow-up read or reversible action only when requested. Use a small vision model for ordinary frames and escalate only on ambiguity.
- **latency:** First acknowledgement under 700 ms; visual answer within 5 seconds; allow a follow-up correction such as "the other one" without restarting capture.
- **cost:** $0.01–$0.08 per frame, dominated by vision inference; local capture and relay transport are negligible.
- **security:** Capture is strictly button- or spoken-command initiated, never ambient. Frames are ephemeral by default, not added to memory, and browser credentials/face-like content are blurred or excluded from dashboard logs. Any action inferred from the image remains a separate spoken request.
- **missing:** A real camera source and capture contract reachable by the relay while the pendant is worn; A mac-vision endpoint that accepts an image plus the owner's utterance and returns grounded regions/confidence; A low-bandwidth image transport and retention policy; A relay dialogue state that can bind one captured frame to several follow-up questions


## Changes it proposed to its own stack

### `hardware` — Add an opt-in clip-on camera/audio sensor node that pairs with the pendant over BLE and exposes a single still-frame capture on button hold; relay forwards only that frame and the current utterance to mac-vision, then erases it after the answer. Keep the nRF9160 pendant as the consent/control device rather than trying to make it process images.
- **owner gets:** The owner could ask what a cable, screen, label, or physical object is while away from the Mac and get an answer grounded in what they are actually seeing. This is the missing physical sense that makes the hive useful outside a desk; no current node can observe the owner's environment.
- effort: High: select and power a camera-capable BLE companion, implement authenticated pairing and still capture, add relay image transport, and integrate mac-vision grounding. Prototype first with a phone camera source before committing to custom hardware.  ·  risk: A camera creates severe privacy and accidental-capture risk. Require a deliberate button hold, a visible camera LED on the companion, no continuous buffer, encrypted transport, short TTL, and an immediate discard command. Recovery is simply disabling the paired node; voice operation remains unchanged.
- cost: Prototype $20–$60 in parts and roughly 50–200 mW while capturing; production clip-on likely $30–$100. Per-use vision inference costs about $0.01–$0.08 and dominates recurring cost.  ·  latency: Still capture adds 0.5–2 seconds and vision 1–4 seconds; target under 5 seconds total, with an immediate spoken acknowledgement.
- security: New camera frames and BLE pairing keys are sensitive. Store no frame on the pendant SD, relay, or dashboard by default; use per-request encryption, scoped retention, and audit only metadata.
- depends on: A camera-source contract and frame TTL policy; A mac-vision image-plus-utterance endpoint; A relay dialogue state for follow-up questions; A deliberate physical-consent UX that does not conflict with the single pendant button


## What it asked for

_Nothing._
