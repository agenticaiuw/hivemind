# Harness derivation — relay-realtime — round 145

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Use the USB-connected pendant as the primary audio path when LTE is down, and keep my session going."
- **useful because:** The hardware is physically connected today. A robust USB fallback makes the system usable even before relay registration and LTE reliability are solved.
- **path:** pendant → mac-bridge → relay-realtime → faculty-perception
- **model tier:** Realtime for conversation; Mac bridge for audio transport and framing.
- **latency:** Interactive audio must stay under a few hundred milliseconds round-trip.
- **cost:** Mostly local; network cost only for relay transcription and responses.
- **security:** Device binding and authentication required to prevent rogue USB devices. Audio data should be encrypted on transport where possible.
- **missing:** Serial framing protocol and authentication binding; Transport multiplexer in relay to switch between USB and LTE; Reconnect and session resume logic

### "Summarize what changed across my open tabs and accounts, and draft responses, but don’t send anything."
- **useful because:** It reduces cognitive load: the owner gets a concise brief and ready drafts without risk of unintended actions.
- **path:** browser-extension → mac-planner → unified → faculty-judgement
- **model tier:** Mac planner for orchestrating; browser sessions for authenticated reads; cheaper model for summarization.
- **latency:** Seconds to produce a brief; longer if many pages.
- **cost:** Dominated by authenticated page reads and extraction.
- **security:** Never submit forms or send messages without approval. Keep extracted data local; minimize data sent to relay.
- **missing:** Durable browser job runner; Page watch definitions and semantic diffing; Provenance for extracted fields

### "“When I tell you to hold something for later, preserve the exact intent and relevant state, then continue it automatically when the Mac or my authenticated browser becomes available; tell me what changed when it is actually done.”"
- **useful because:** The owner can speak once while away from the desk without losing the task or having to reconstruct context. Unlike a generic reminder, the system carries the original conversational intent, browser session state, and Mac evidence across an interruption and returns a useful outcome.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles only the short acknowledgment and intent extraction; a cheaper background planner performs continuation, with browser and Mac agents doing the actual work.
- **latency:** Acknowledge in under 1 second; resume within 30 seconds of a surface becoming available; final result is asynchronous.
- **cost:** Roughly one short realtime turn plus one background planning call per held task; dominant cost is continuation context and browser/Mac execution, not the acknowledgment.
- **security:** Persist only an encrypted intent envelope and references to already-authorized sessions; browser cookies and private Mac content must remain on their owning surface. The owner should be able to inspect and delete the envelope and its result.
- **missing:** Durable relay task envelopes keyed to a spoken intent, with reconnect-triggered continuation; A completion/result channel that can deliver a bounded digest to the pendant; A cross-surface context snapshot format distinguishing facts, assumptions, and stale state

### "“During a conversation, quietly watch for questions about my project and give me a one-sentence answer or a private correction through the pendant, using the latest files, browser tabs, and notes on my Mac.”"
- **useful because:** The owner gets an always-available private aide in meetings or hallway conversations: it can retrieve the answer without making them unlock a computer, while keeping the aid discreet and grounded in their current project rather than generic chat knowledge.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** A low-latency realtime model detects an address/question and manages the brief response; faculty-perception or a cheaper background retrieval pass gathers evidence from Mac and authenticated browser surfaces; realtime speaks only the compressed answer.
- **latency:** Detect and acknowledge within 700 ms, retrieve within 4 seconds, and speak a response under 8 seconds. If evidence is unavailable, say so rather than hallucinating.
- **cost:** One realtime turn per detected question and one retrieval/planning call when needed; cost is dominated by transmitting a compact evidence set, not continuous audio if local VAD filters silence.
- **security:** This is sensitive social and workplace audio. Audio should be VAD-segmented and discarded after transcription unless explicitly saved; never send bystanders' speech to third parties unnecessarily. Require an explicit physical button gesture to arm meeting mode, show armed state on the LED, and offer an immediate disarm gesture.
- **missing:** A device-local arm/disarm mode and VAD boundary marker; A Mac/browser retrieval endpoint that returns current project facts with source and freshness; An audio downlink queue that can deliver a private answer without interrupting an active owner utterance

### "“Before I rely on that answer, show me the smallest proof: which Mac file, browser page, or action receipt supports it, what is stale or contradictory, and let me challenge one source by voice.”"
- **useful because:** The owner can distinguish a grounded result from a plausible guess while wearing the pendant. This is especially valuable when browser sessions, local files, and recent actions disagree; today the owner must manually inspect several surfaces and cannot audit a spoken answer in place.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a cheaper background evidence assembler to collect typed citations and detect contradictions; realtime handles the owner's short challenge and speaks a compact provenance explanation. Use vision only when a source is visual and cannot be represented as text.
- **latency:** Initial answer remains low latency; provenance arrives within 3 seconds, with a maximum two-source spoken explanation and a dashboard link for the full evidence graph.
- **cost:** One additional evidence-ranking call per answer that requests proof; vision fallback is the expensive path. Typical cost is modest because only source snippets, hashes, timestamps, and receipts are passed, not full histories.
- **security:** Citations can leak private filenames, URLs, or snippets. Redact secrets and expose only sources the owner is authorized to view; keep full evidence on the originating Mac/browser and send the relay signed references plus minimal excerpts.
- **missing:** A cross-surface provenance graph linking spoken claims to source snapshots and action receipts; Typed freshness, contradiction, and authorization metadata on Mac and browser results; A pendant-friendly challenge protocol and dashboard view for drilling into cited evidence


## Changes it proposed to its own stack

### `hardware` — Add a low-power bone-conduction or open-ear earpiece path to the ESP32 audio bridge, with a hardware mute/arming switch and independent volume control, while retaining the existing pendant speaker path for ordinary replies. The relay should advertise the output channel and privacy state to downstream agents.
- **owner gets:** The owner could receive private answers, warnings, and meeting assistance while walking or talking to other people without broadcasting the pendant's response or reaching for a phone. They could still use the existing speaker when privacy is not needed.
- effort: Prototype with a BLE bone-conduction module or wired transducer, add bridge codec routing and a small authenticated channel-state message; then validate intelligibility and battery impact in real wear tests.  ·  risk: BLE pairing loss or acoustic leakage could make the owner miss a response. Recover by falling back to the existing speaker and a distinct LED pattern; never silently assume the private channel is working.
- cost: Approximately $20–$80 for a prototype transducer/module, plus bridge firmware work. Expect tens of mW while active and negligible draw while muted; exact draw requires measuring the chosen part.  ·  latency: Adds under 100 ms of local audio routing latency; no model/API cost.
- security: A new wireless audio endpoint creates a pairing and eavesdropping surface. Use authenticated bonding, explicit mute state, and do not transmit private audio until the endpoint confirms encryption and readiness.
- depends on: ESP32 bridge firmware must expose authenticated output-channel state; Relay audio pipeline must select output per utterance and know whether the private path is confirmed; A physical arming/mute gesture must be defined for the one-button pendant


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: durable spoken intent envelopes that resume across Mac/browser availability, private in-conversation project assistance, and voice-challengable provenance for answers. Also recorded a hardware change adding a confirmed private audio channel with explicit mute/arming. The key missing work is not another planner: it is cross-surface state/provenance contracts, device-local arm/VAD behavior, reconnect-triggered continuation, and authenticated audio-channel state.

**Biggest unknown:** Whether the existing relay audio path can already target separate playback channels and retain enough per-utterance identity to implement these without a new protocol; the current inventory does not expose that detail.

