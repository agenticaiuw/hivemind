# Harness derivation — relay-realtime — round 147

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Can you check this site and tell me the key updates, even if my Mac is offline?"
- **useful because:** Lets the pendant answer web questions without depending on a nearby Mac, which is perfect when the owner is out and about.
- **path:** relay → browser
- **model tier:** realtime for voice; a cheaper, sandboxed browser runner for the browsing and extraction work.
- **latency:** A few seconds is acceptable for page load and extraction; response should stream if possible.
- **cost:** Moderate. Browser automation and extraction dominate; model cost is small.
- **security:** Only run in a sandbox. Do not log credentials. Restrict actions to read-only unless explicitly allowed.
- **missing:** An implemented server_browser_actions tool with a safe browser environment and result schema.; Policy and limits for allowed domains and read-only actions.

### "Start a wearable session and keep it going after I stop talking—watch for events and update me hands-free."
- **useful because:** This would be the single most useful capability: a persistent assistant that can monitor and summarize relevant changes while the owner moves through their day.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** realtime for the voice front door; cheaper background models for monitoring and summarization.
- **latency:** Voice interactions should stay snappy; monitoring can be eventual but should notify quickly when thresholds are met.
- **cost:** High overall. Persistent monitoring and multi-surface coordination dominate; should use cheaper tiers and event-driven updates.
- **security:** Clear consent and scope for what is monitored. Minimize data retention, encrypt stored summaries, and provide a one-tap stop.
- **missing:** A relay-side event push mechanism and subscription model.; Device skills for local event buffering and session state.; Background scheduling (cron/alarms) and durable subscriptions.; A cross-surface session and notification protocol.

### "“Put me on a phone call with Alex, tell them the short version of what I said, and let me interrupt or stop it from the pendant.”"
- **useful because:** The owner can delegate a real-time call while away from the Mac: the pendant is the consent and interruption surface, the relay keeps the conversation low-latency, and the Mac supplies the telephony and contact access. This is materially different from composing a message because the owner can hear, correct, and abort the live interaction.
- **path:** pendant → relay-realtime → mac-planner → mac-vision
- **model tier:** Realtime relay for turn-taking and interruption; mac-planner for call setup and contact lookup; mac-vision only when the telephony app exposes state visually.
- **latency:** Speech turn recognition and relay response under 700 ms; call-control commands under 1 s; transcript summaries can lag 2–3 s.
- **cost:** Roughly $0.01–$0.08 per spoken minute depending on transcription/synthesis; telephony provider charges dominate any external call.
- **security:** The call audio and transcript leave the pendant and may contain third-party private speech. Require an explicit spoken start command, announce that an AI is participating, provide an always-available pendant stop gesture, and retain only a short-lived transcript unless the owner asks to save it.
- **missing:** A telephony bridge reachable by the Mac or relay; A duplex audio-call stream and interruption protocol; Pendant firmware support for a distinct stop gesture during an active call; A live-call session record with participant disclosure and stop status

### "“When I am in a noisy or public place, keep the answer private: show me a short code on the pendant and send the full answer to my phone or Mac instead of speaking it aloud; switch back when I hold the button.”"
- **useful because:** The owner can use the system around other people without broadcasting private mail, work, navigation, or health information. It uses the worn device as a physical privacy control rather than relying on the owner to remember a setting in an app.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime relay classifies sensitivity and chooses a terse spoken/LED response; a cheaper background path can render the full answer into a paired phone/Mac notification.
- **latency:** Privacy mode must engage within 200 ms of the button gesture; the terse code within 500 ms; full-screen delivery within 3 s.
- **cost:** Negligible model cost for mode selection; notification transport and optional phone integration dominate implementation cost.
- **security:** The code must not reveal the sensitive content to someone observing the pendant. Pairing and device authentication are required; the full answer must not be sent to an untrusted browser tab. If the relay cannot verify the private destination, it must remain silent rather than fall back to speech.
- **missing:** A persistent privacy-mode state shared by pendant and relay; A device-authenticated notification sink for the owner’s phone/Mac; A pendant LED/display or deterministic short-code protocol; Sensitivity classification and redacted spoken-response policy

### "“Start an incident record now. Keep the next five minutes of pendant audio, my Mac’s active window and browser tab, and timestamps together, then give me one private package I can review or share.”"
- **useful because:** A single physical gesture would preserve what actually happened during a confusing support call, software failure, threatening encounter, or lost train of thought. Today those observations live separately or disappear; the owner cannot reliably reconstruct them later.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** No expensive reasoning while recording; relay coordinates timestamped streams. A background model later produces a short chronology and redaction suggestions, with realtime used only for the start/stop acknowledgement.
- **latency:** Start acknowledgement under 300 ms; clock alignment under 1 s; package assembly within 10 s after stop.
- **cost:** Storage and upload dominate; optional post-event transcription/summary is roughly $0.01–$0.10 per five-minute incident.
- **security:** This can capture bystanders and private screens. The pendant must give an unmistakable recording indicator, enforce a hard maximum duration, encrypt each stream to the owner, and default to local deletion after export. Sharing must be a separate explicit action and support redaction before upload.
- **missing:** A pendant-local ring buffer and unmistakable recording indicator; Clock synchronization and a multiplexed incident manifest across audio, Mac, and browser; Encrypted bundle storage/export and retention controls; A post-event review UI with transcript, timeline, and redaction

### "“Translate this conversation for me in real time, privately, and translate my reply back; stop when I tap the pendant.”"
- **useful because:** The worn microphone can stay with the owner while the relay handles low-latency turn detection and the Mac/browser can provide language models or reference terminology. This gives the owner an in-person interpreter without handing a phone back and forth.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime speech recognition/translation for short turns; a cheaper background model can maintain glossary and speaker context. The Mac/browser is used only for language packs, terminology lookup, or fallback computation.
- **latency:** Partial translation within 1.5 s after each speaker turn; stop gesture locally effective within 200 ms; never wait on Mac for the stop path.
- **cost:** Approximately $0.02–$0.15 per conversation minute depending on language pair and speech synthesis; audio bandwidth is the main non-model cost.
- **security:** The system records another person without necessarily knowing their consent and may translate sensitive content. Make recording/translation visibly indicated, auto-delete raw audio, keep only opt-in text, and provide a local-only mode when the network is unavailable.
- **missing:** Duplex speaker-turn detection and streaming translation; A private output path (earbud/phone) or a pendant tactile/text fallback; Language selection and glossary controls accessible by voice; Consent indicator, raw-audio retention policy, and interruption-safe stop handling


## Changes it proposed to its own stack

### `model-routing` — Route long-running monitoring, research, and summarization tasks to cheaper background models, with the relay acting only as a conversational front door and notification presenter.
- **owner gets:** Keeps voice interactions snappy and reliable while still enabling richer capabilities without burning budget.
- effort: Medium to high. Needs a task taxonomy, routing rules, and receipts for results.  ·  risk: Misrouted tasks could be slow or incomplete. Mitigate with receipts and fallback to Mac delegation.
- cost: Potentially large savings by avoiding expensive realtime usage for background work.  ·  latency: Improves voice latency; background tasks become less jittery with proper queues.
- security: Ensure data minimization and strict scoping when tasks leave the device.
- depends on: A queue/scheduler and status reporting across surfaces.

### `interaction` — Introduce a spoken 'session mode' with explicit start/stop commands and scoped permissions (e.g., 'monitor my email for 30 minutes'), plus a one-button pendant stop that always cancels the session.
- **owner gets:** Gives the owner confidence and control: they know what’s being watched, for how long, and how to stop it instantly.
- effort: Medium. Needs UX rules, session state, and consistent cancellation semantics across surfaces.  ·  risk: If stop fails, the system could keep monitoring. Mitigate with timeouts and kill-switch precedence.
- cost: Low to moderate. Mostly state management and messaging.  ·  latency: Minimal for voice; monitoring latency depends on downstream surfaces.
- security: Strongly positive: explicit consent boundaries and easy revocation.
- depends on: Session state shared between relay and devices, and a notification channel.

### `hardware` — Add a low-power coin vibration motor and a protected driver to the nRF9160 pendant, with firmware patterns for acknowledgement, private notification, urgent stop, and recording-active status. Keep the existing LED as a secondary visual indicator rather than the only output.
- **owner gets:** The owner can receive and control the assistant silently in public, in a pocket, or where speech is impossible. Distinct tactile patterns make it possible to know whether a command started, finished, failed, or is still recording without looking at the pendant.
- effort: Hardware spin for a tiny motor, transistor/driver, and board routing; firmware event-pattern table; relay event mapping; enclosure and battery testing.  ·  risk: Motor noise may be audible and vibration can annoy the wearer; provide intensity limits and a disable pattern. Added current can shorten battery life. Recovery is to fall back to LED/audio and expose battery-aware pattern selection.
- cost: Approximately $1–$4 in component and assembly cost per unit, plus a few mA only while pulsing; no model/API cost.  ·  latency: Sub-100 ms local feedback for button and link events; no added conversational latency.
- security: Improves privacy by reducing required speech, but patterns must not encode sensitive content. Firmware update must be signed and pairing state preserved.
- depends on: A defined pendant event vocabulary shared with the relay; A device-authenticated command channel for relay-to-pendant pushes; Battery and enclosure validation


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing proposals: pendant-controlled live phone calls with interruption, silent/private answer mode, bounded incident dossiers, and real-time private translation, plus a hardware change adding tactile feedback. The common missing pieces are duplex audio/session control, authenticated push to the pendant, a private output destination, encrypted retention/export, and (for calls) a telephony bridge. The haptic proposal was recorded despite a low-similarity warning; it may overlap an earlier tactile-feedback item and should be deduplicated by the implementer.

**Biggest unknown:** I could not inspect the backlog this round, so the recorder’s similarity warnings—notably tactile feedback and translation—are the only overlap signals available.

