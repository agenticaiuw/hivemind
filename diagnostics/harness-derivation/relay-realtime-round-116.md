# Harness derivation — relay-realtime — round 116

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Route this: "Open my project dashboard and summarize what changed""
- **useful because:** The pendant is the fastest way to speak a request, but the work usually happens elsewhere. A reliable routing capability lets me send the request to the right surface (Mac planner, browser session, or server browser) and then report status back without guessing a protocol.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime at relay for intent capture, then a cheaper planner/worker downstream for execution and summarization.
- **latency:** Owner gets immediate acknowledgement (sub-second), then a second response when the downstream agent finishes.
- **cost:** Low at relay (intent packaging); main cost is downstream browsing and summarization.
- **security:** Authenticated pages and personal data should only be accessed via the owner’s logged-in surfaces. Never submit forms or send messages without explicit approval.
- **missing:** relay_route_intent implementation; downstream status callback path to relay; server_browser_actions implementation (for Mac-offline browsing)

### "“Capture the commitments from this conversation and, when it ends, tell me exactly what I promised, who owns each next step, and put the actionable ones where I can find them.”"
- **useful because:** The owner can wear the pendant in a meeting or conversation without opening a laptop, then receive a trustworthy, source-linked commitment list rather than relying on memory. It is genuinely cross-surface: the pendant supplies the live audio and conversational trigger, the relay keeps low-latency utterance context, judgement extracts commitments and uncertainty, and the Mac/browser agents file them into the relevant authenticated app while preserving the original evidence.
- **path:** pendant → relay-realtime → faculty-perception → faculty-judgement → mac-planner → browser-extension → dashboard
- **model tier:** Realtime for turn-taking, start/stop detection, and brief acknowledgements; a cheaper background model for diarization, commitment extraction, deduplication, and confidence scoring after the conversation; Mac/browser planner models only for filing the accepted results.
- **latency:** Immediate acknowledgement under 500 ms; a provisional running list within 2 seconds of each clear commitment; final digest within 30 seconds after the owner says “done” or the conversation ends. Filing can continue asynchronously, with a spoken completion notice.
- **cost:** Roughly $0.02–$0.10 per 30-minute conversation depending on audio transcription and background extraction; realtime tokens and audio egress dominate, while filing is comparatively small.
- **security:** Conversation audio and extracted commitments leave the pendant for relay processing and may contain other people’s private information. Encrypt transport and at-rest artifacts, retain only the transcript spans supporting each item, expose a visible recording indicator, allow instant “discard that conversation,” and never send a commitment to an external app unless its destination is explicit or unambiguous. Do not fabricate speaker ownership: mark uncertain speaker/assignee fields and quote evidence.
- **missing:** A pendant-side conversation capture state with explicit start/stop and recording indicator; Streaming audio ingestion with speaker-turn and end-of-conversation detection; A durable, encrypted evidence store that links each extracted item to short transcript spans; Background diarization/commitment extraction and confidence-aware deduplication; A cross-surface filing adapter for Reminders/Notes/Outlook and authenticated browser destinations; A user-facing commitment ledger and correction flow in the dashboard and by voice


## Changes it proposed to its own stack

### `relay` — Implement relay_route_intent as the single routing API for the voice front door. It should accept an intent label and utterance, pick a target (mac-planner, mac-vision, browser, or server browser), create a job record, and return a job id plus a user-facing acknowledgement. Add a status callback path so downstream agents can update the relay job record and a spoken summary.
- **owner gets:** They can speak a request and trust it will be routed, tracked, and reported back even if they walk away from the Mac.
- effort: Medium: new relay route + job record schema + downstream integration + basic reconciliation of statuses.  ·  risk: Misrouting could cause the wrong app or session to be used. Mitigate with conservative default targets, explicit intent labels, and typed payloads.
- cost: Small per request; the heavy cost is downstream browsing and summarization.  ·  latency: Fast acknowledgement; downstream completion varies by task.
- security: Job records contain sensitive utterances; store minimal text, redact where possible, and enforce access controls.
- depends on: Downstream agents exposing a status update endpoint or tool; relay_job_status to read job records

### `model-routing` — Add a routing policy that keeps the relay as a thin, low-latency layer. If the request requires multi-step planning, authenticated browsing, or long-running work, immediately hand off to a cheaper downstream agent via mac_delegate or server browser and return a job id. Use relay_job_status for follow-up queries instead of keeping context in the relay.
- **owner gets:** They get snappy voice interactions without paying relay costs for long-running tasks, and they can ask "what happened" later.
- effort: Low to medium: policy plus job id handoff and consistent acknowledgements.  ·  risk: If job ids are not consistently returned, the user can’t refer back to tasks. Require job id in the acknowledgement.
- cost: Reduces relay compute; moves cost to more appropriate tiers.  ·  latency: Improves perceived responsiveness.
- security: Less data retained in the relay; store only job ids and short summaries.

### `interaction` — Add an explicit, voice- and button-controlled “public conversation mode” spanning pendant, relay, Mac, and browser. In this mode the pendant locally indicates capture, the relay accepts commands only after an owner voiceprint/wake phrase plus button press, treats all other speech as untrusted quoted content, suppresses spoken secrets and screen-derived private data, and expires the mode automatically when the owner ends it. The Mac/browser surfaces receive a mode flag and must return redacted summaries rather than raw page or screen text.
- **owner gets:** The owner can use the hive in a meeting, café, or shared office without a nearby person accidentally commanding it or hearing private email, browser, or Mac content. They retain powerful assistance while being able to switch to a clearly bounded mode in one gesture.
- effort: Medium-high: local firmware state and LED/button UX; relay session policy and audio classification; Mac/browser redaction hooks; end-to-end tests with overlapping speakers and reconnects.  ·  risk: False rejection could make commands feel unreliable; false acceptance is a privacy failure. Recover with a hard physical exit/start gesture, clear LED state, short-lived mode leases, and a local-only fallback that never performs actions when speaker confidence is low. Avoid claiming biometric certainty; use the voiceprint only as an additional signal.
- cost: Small realtime classification overhead, approximately <$0.01 per active hour; firmware storage and RAM are modest but need measurement against the 211,608 B application budget. No new recurring hardware cost if existing microphone/button/LED suffice.  ·  latency: Owner command authorization should add under 300 ms after the wake phrase; redaction may add 0.5–2 seconds to responses that depend on screen/browser content.
- security: Improves privacy by default in shared spaces, but introduces voiceprint material that must remain device-local or be irreversibly derived. Never upload raw voiceprints; rotate session tokens and ensure a reconnect cannot silently leave public mode.
- depends on: A pendant-local mode state and button/LED indication; A relay session policy propagated to downstream Mac/browser jobs; Screen/page redaction metadata and a safe spoken-response filter; A tested owner-presence/voice-confidence signal


## What it asked for

_Nothing._
## Its own summary

Recorded two new gaps: (1) pendant-led conversation commitment capture that produces evidence-linked owners, next steps, and files them across Mac/browser destinations; (2) a cross-surface public-conversation mode with physical indication, owner-only command acceptance, and suppression/redaction of private output. Both require new device/relay/background and downstream integration work rather than assuming today’s routes are sufficient.

**Biggest unknown:** The exact pendant audio/firmware budget and whether any existing downstream app adapters can create commitment records; those must be inventoried and tested before implementation.

