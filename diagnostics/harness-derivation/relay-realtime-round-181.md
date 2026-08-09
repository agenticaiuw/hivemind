# Harness derivation — relay-realtime — round 181

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If the thing I asked the Mac to do finishes while I’m away, tell me the result on my pendant."
- **useful because:** This turns long-running Mac tasks into a hands-free experience. The owner doesn’t have to keep checking a screen to know if something succeeded or needs attention.
- **path:** relay → mac-bridge → browser
- **model tier:** Realtime for the spoken confirmation, cheaper background model for monitoring and summarization.
- **latency:** Immediate spoken confirmation if already complete; otherwise notification when the job transitions state.
- **cost:** Low per invocation; dominated by job-status polling and audio rendering for the spoken notification.
- **security:** Announcing task results could reveal sensitive information aloud. Default to short generic phrasing unless the task was explicitly asked to be spoken verbatim.
- **missing:** A working async event delivery path from relay to device (relay_event_push currently resolves to a description).; A scheduler or durable alarm to monitor job completion without a live session.

### "Keep listening for a moment after I stop, only to catch clipped words, without recording extra audio."
- **useful because:** Clipped last words are a real usability snag. A consent-safe fix improves accuracy without violating the rule that button release ends recording.
- **path:** pendant → relay
- **model tier:** Realtime for speech handling; device firmware for local voice activity tuning.
- **latency:** No added delay; tuning happens locally and affects only capture gating.
- **cost:** Minimal runtime cost; mainly firmware tuning and validation effort.
- **security:** Must not keep recording after consent ends. Only adjust end-of-speech thresholds and allow a second press to resume.
- **missing:** Firmware change to end-of-speech calibration parameters and resume behavior.; A test harness to validate clipping rates under real noise conditions.

### "Check whether my Mac is online and ready before you send a request, and if it’s not, offer a fallback."
- **useful because:** It prevents frustrating failures when the owner is away and the Mac is asleep. The system can choose a safer path: queue a reminder, use web search, or store a note.
- **path:** relay → mac-bridge → browser
- **model tier:** Realtime for quick decision; mac-planner for heavier workflows when available.
- **latency:** Fast: a quick status check and then a route decision.
- **cost:** Low; status checks are cheap, with occasional delegation to mac-planner.
- **security:** Status checks reveal device presence; keep outputs minimal and avoid exposing detailed system info aloud.
- **missing:** A reliable relay-visible Mac presence and readiness signal exposed as a stable endpoint.

### "“I’m away from my desk—tell me what is currently blocking my work, and if it is safe, fix it.” The pendant should combine my spoken context with the Mac’s active app, unsaved state, terminal errors, and authenticated browser state, rank the blocker, and either repair it or tell me the exact next action."
- **useful because:** This is the highest-value experience: the owner gets a remote, truthful operations concierge rather than a voice shortcut. It uses the wearable for intent and interruption, the always-on relay for orchestration, the Mac planner/terminal for local truth and repair, and the browser session when the blocker is web-based.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → mac-vision
- **model tier:** Realtime relay for the short conversation and intent extraction; faculty-perception/mac-vision for evidence; mac-planner/mac-terminal for execution; a cheaper background model for ranking evidence and composing the eventual result.
- **latency:** Initial spoken diagnosis under 5 seconds when the Mac is online; repair may take 30–120 seconds with an interruptible spoken progress update.
- **cost:** Roughly $0.03–$0.20 per invocation depending on whether vision and multi-step planning are needed; screenshots and repeated planner turns dominate.
- **security:** The Mac and browser may expose confidential work. Send only targeted active-window/terminal/browser evidence, retain an auditable evidence and action receipt, and never claim a fix without a post-action verification. Owner policy allows reversible action without a gate; destructive changes must be explicitly surfaced.
- **missing:** A single evidence snapshot API spanning active app, terminal, browser tab, and unsaved indicators; Re-enable and harden the mac-vision computer-use loop for iterative observe/act/verify; A relay orchestration state machine that can correlate perception, repair, verification, and spoken progress; A result contract that distinguishes diagnosed, repaired, partially repaired, and blocked

### "“Make this conversation actionable.” While I speak naturally, the pendant should identify commitments, questions, and follow-ups, then—using my Mac calendar, Reminders, Notes, and authenticated browser—draft a compact action bundle and read it back as one confirmation summary, without forcing me to issue separate commands."
- **useful because:** The owner can turn an unstructured thought into a coherent set of next steps in one interaction, including dates, people, links, and source evidence. The wearable supplies the raw conversation; relay keeps the low-latency dialogue; Mac and browser supply durable destinations and context.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension
- **model tier:** Realtime model extracts tentative entities and asks only essential clarifying questions; a cheaper background model normalizes dates, deduplicates existing reminders, and prepares the action bundle; Mac planner executes after the owner’s single spoken confirmation.
- **latency:** Extraction and a proposed bundle in under 4 seconds after speech ends; destination writes within 15 seconds.
- **cost:** About $0.02–$0.10 per interaction; transcription/context tokens dominate, with browser inspection adding occasional cost.
- **security:** Conversation may contain third-party personal data. Keep raw audio transient after transcription, show each destination and exact text in the spoken read-back, and make writes idempotent so a retry cannot duplicate reminders or notes. No silent external messages.
- **missing:** A structured commitment/action schema with provenance spans and confidence; Cross-destination deduplication and idempotency keys for Reminders/Calendar/Notes/browser writes; A confirmation transaction spanning multiple Mac actions with rollback or explicit partial-success reporting; A durable per-session transcript projection (the requested shared preference/session memory facility is still unavailable)

### "“Translate this conversation as it happens, and let me answer in their language.” The pendant should capture my speech, the Mac/browser should provide the remote call audio or page text, and the relay should produce low-latency translated speech in both directions while preserving speaker turns."
- **useful because:** This gives the owner an always-available interpreter for a call or authenticated web meeting while they are away from the keyboard. No single node can do it: the pendant supplies consented speech and playback, the Mac/browser reaches the call audio and session, and the relay keeps turn-taking and translation responsive.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** A low-latency speech translation model for the active exchange; a cheaper background model for terminology adaptation and a short glossary learned from the session.
- **latency:** First translated phrase within 1.5 seconds of a turn, with incremental chunks under 700 ms; tolerate 3–5 seconds when the owner requests a polished translation.
- **cost:** Approximately $0.05–$0.30 per minute depending on two-way audio transcription and translation; audio streaming and translation tokens dominate.
- **security:** Call audio and translated speech may be highly sensitive. Require an explicit physical start gesture, show recording/translation state on the one LED, do not persist raw call audio by default, redact logs, and stop immediately on release or a second cancel gesture. Browser credentials remain on the Mac.
- **missing:** A Mac audio-capture and injection bridge that can select one call/tab without recording unrelated system audio; Incremental streaming speech-to-speech translation with speaker-turn/VAD metadata; Pendant firmware support for a clearly distinct translation-active LED pattern and cancellation gesture; Browser integration exposing the selected meeting tab’s media stream while respecting site permissions; A relay stream multiplexer that keeps original and translated turn IDs aligned


## Changes it proposed to its own stack

### `relay` — Add a relay-visible capability inventory route (e.g., GET /capabilities) that lists the relay’s own tool and endpoint schema, plus a stable Mac presence/readiness field sourced from the bridge when connected.
- **owner gets:** Fewer mysterious failures. The voice agent can reliably decide whether to route a request to the Mac, offer a fallback, or say it will try later.
- effort: Medium. Requires wiring a new route, defining a schema, and integrating bridge signals.  ·  risk: Schema drift between relay and Mac. Mitigate with versioned schema and compatibility checks.
- cost: Low ongoing cost; primarily one extra read endpoint. Implementation time is the main cost.  ·  latency: Improves routing speed by avoiding unnecessary Mac round trips.
- security: Presence info is sensitive. Expose only coarse states (online/asleep/offline) and protect with existing auth.
- depends on: Access to bridge status as a stable signal

### `interaction` — Add a physical ‘handoff token’ protocol: a press-and-release on the pendant creates a signed session token; the relay binds the next spoken turn, the Mac evidence snapshot, browser inspection, every downstream action, and the final audio receipt to that token. A second deliberate press can pause or cancel the handoff, and reconnecting over USB or LTE resumes from the last verified step.
- **owner gets:** Long tasks stop feeling like a fragile voice call. The owner can walk away, regain the thread later, and know exactly which device saw what and which action actually happened—without repeating the request or trusting an ambiguous ‘done’.
- effort: Medium-high: firmware gesture/state changes, relay Durable Object/session state, signed token verification, and Mac/browser adapters for pause/resume and receipts.  ·  risk: A lost or duplicated token could attach the wrong conversation to an action; expire tokens, bind them to device/session identity, reject replays, and make resume idempotent. Recovery is a spoken ‘what is this handoff doing?’ plus a fresh physical press.
- cost: Low per-task API cost; approximately $0.01–$0.05 extra storage/coordination per active handoff. No routine audio-card writes.  ·  latency: Adds under 200 ms to session setup; resume avoids re-planning and is faster overall.
- security: Improves auditability and replay resistance, but creates a durable linkage between voice, screen evidence, and actions; encrypt records, minimize retention, and expose deletion by token.
- depends on: A relay-side Durable Object or equivalent state store (no scheduler is required, but durable session state is); A real pendant announce/status transport over today’s USB serial path and eventual LTE path; POST /execute and browser actions returning idempotent step receipts; An implemented completion/status push path rather than the currently unresolved relay_event_push promise


## What it asked for

### `s24-ddk1` (skill) — eos_tuning_and_resume
- does: Adjust end-of-speech detection thresholds based on measured noise floor to reduce clipping, and allow a second button press to resume the same turn without creating a new recording.
- must be on-device because: It must operate at capture time on-device and must respect the consent boundary at button release.
- trigger: Button press and release; optional second press to resume.
- storage: No persistent audio; small persistent calibration settings in flash (a few hundred bytes).
- RAM budget: Tiny; a few kilobytes for running statistics and state.

## Its own summary

Recorded four proposals. The strongest is a remote blocker resolver: pendant speech plus Mac/terminal/browser/vision evidence, followed by verified repair and truthful status. I also recorded one-turn conversion of free speech into a deduplicated action bundle, a physical handoff-token protocol for pause/resume/auditable cross-device work, and real-time bilingual interpretation through the pendant and browser/Mac audio. Each names the missing cross-surface work rather than pretending existing routes already provide it.

**Biggest unknown:** Whether the relay can obtain durable per-session state and a real pendant status/announce transport today; both are needed for resumable handoffs and reliable asynchronous spoken outcomes, and the granted relay_event_push remains only a described side-effect route.

