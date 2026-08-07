# Harness derivation — faculty-perception — round 112

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live_mac_accessibility** — AI Pendant Agent is online and full-control configured, but Accessibility and Screen Recording are both ungranted; /observe says synthesized UI events are rejected and ui_click/type_text/press_keys can report success while doing nothing.
  - evidence: GET /ops/status and GET /observe at 2026-08-07T17:33Z: accessibility.trusted=false, screenRecording.granted=false, inputReachability.status=failed, uiActionsWillReachTheScreen=false.
- **live_browser_truth** — Safari browser bridge is online with 3 tabs and zero pending commands, but its active tab reports URL https://example.com and title 'Failed to open page'; browser status was refreshed at 17:33:26Z.
  - evidence: GET /browser/status and GET /ops/status, both HTTP 200, device online=true, pendingCommands=0, tabCount=3; active tab title is 'Failed to open page'.
- **audio_pipeline_truth** — Recorded pipeline history contains a successful 24 kHz mono s16le TTS render (75,734 PCM bytes, 1.578 s) accepted by relay, while an older live input run used 15,625 Hz PCM; no physical nRF9160 is currently registered.
  - evidence: GET /pipeline event metadata shows sampleRate=24000 output and inputTelemetry.sampleRate=15625; live device discovery lists only home-macbook-bridge and offline contract-test mobile.

## Capabilities it proposed

### "Tell me whether it actually happened — not whether the agent says it succeeded."
- **useful because:** Today the agent can return a successful UI receipt while doing nothing because Accessibility is missing. This gives the owner an honest spoken result: verified with fresh observation, definitely blocked, or unknown, with the evidence and timestamp. It is the most useful trust boundary for every future action.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime only for the short spoken verdict; deterministic observation and local planner/background work do the verification.
- **latency:** 3 seconds for browser/AppleScript state checks; up to 8 seconds for a fresh vision observation; never claim completion while verification is pending.
- **cost:** Usually <$0.01 beyond the action; vision upload/model calls dominate only when Accessibility/Screen Recording are available.
- **security:** The Mac observation may contain screen contents and browser session data; send only the target app/tab evidence, redact secrets, and require confirmation for destructive actions. If permissions are absent, say unverifiable rather than guessing.
- **missing:** A typed verification contract attached to every action receipt (target predicate, observation source, freshness, confidence).; A relay route that streams verification state to the pendant, not just final action status.; An Accessibility/Screen Recording grant from the owner for visual UI verification; browser DOM and AppleScript verification can work without it.

### "Repair the browser bridge, but do not replay anything; tell me when a real page is usable."
- **useful because:** The owner has repeatedly asked for this and received failure. With the bridge currently online yet showing a 'Failed to open page' tab, the system should distinguish transport health from usable browsing, preserve the pending-command queue, open/reconnect the bridge if needed, and verify a real tab title/URL before claiming recovery.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Cheap deterministic state machine; use the realtime model only to translate the final result into one short spoken sentence.
- **latency:** Heartbeat and inspection in 2 seconds; safe recovery in 10 seconds; never execute or replay queued browser commands as part of repair.
- **cost:** Near-zero model cost; one relay/browser round trip dominates.
- **security:** Read only tab metadata and bridge health by default. Do not expose Gmail contents, click, submit, or clear commands. Require explicit confirmation for any navigation beyond a known bridge/status page.
- **missing:** A read-only browser usability predicate (loaded document, non-error title, stable URL, last successful content observation).; An idempotent bridge reconnect/open-app command that cannot drain pending commands.; A durable repair receipt containing before/after tab identity and queue count.

### "What needs my attention on the Mac right now? Give me the answer without sending my screen to the cloud."
- **useful because:** The wearable can ask anywhere, the Mac can see the foreground app and browser session, and the relay can deliver a concise answer, but there is no privacy-preserving perception path joining them. This would summarize only local, policy-approved facts (foreground app, unread counts, page title, due reminders) and let the pendant speak them while keeping pixels and page contents on the Mac.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Local cheap model or deterministic extractors on the Mac; realtime is only the low-latency conversational wrapper. Cloud receives a redacted fact packet, not an image or raw page.
- **latency:** Under 4 seconds for app/browser/reminder summaries; under 10 seconds if local vision is needed.
- **cost:** No cloud vision cost in the normal path; local inference and one small relay request dominate.
- **security:** A local policy engine must classify sensitive apps/tabs (Mail, Passwords, banking) and return only 'sensitive activity detected' unless the owner explicitly opts in. Every fact needs source, timestamp, and redaction reason so the spoken answer is auditable.
- **missing:** A Mac-local perception endpoint that emits typed, redacted facts with provenance instead of screenshots.; Relay support for encrypted, short-lived perception packets addressed to the current pendant session.; A pendant UI/voice intent for attention-summary requests and an owner-configurable sensitivity policy.

### "Move this meeting from my Mac to the pendant, and move it back when I say so."
- **useful because:** The owner should be able to leave the desk without losing a live conversation: the browser session stays authenticated on the Mac, the relay preserves the voice session, and the wearable becomes the microphone/speaker. This is a genuinely distributed handoff, not a Mac shortcut.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Realtime for the live audio bridge and handoff utterances; deterministic local state machines for mute, participant, and session transfer.
- **latency:** A handoff should complete in 2 seconds and never drop more than 500 ms of audio; returning to the Mac should be one spoken command.
- **cost:** Realtime audio dominates, roughly normal voice-session cost; handoff control traffic is negligible.
- **security:** Require an explicit spoken confirmation before exposing meeting audio on the pendant. Keep meeting media on the approved path, show mute state on both surfaces, and never infer consent from mere proximity.
- **missing:** A relay session-transfer protocol with sequence numbers and rollback if the target does not acknowledge.; Mac browser/meeting adapters that expose current call, mute, and participant state without scraping arbitrary pixels.; Pendant and ESP32 bridge firmware for duplex low-latency audio with a hard local mute.; A registered, paired pendant and an end-to-end audio QA harness.

### "While I’m presenting, keep routine notifications off my Mac but alert me on the pendant only when something I marked urgent arrives."
- **useful because:** Today the Mac, browser, relay, and wearable have no shared interruption policy. The owner gets either noisy desktop alerts or misses important ones. This would use the foreground presentation state on the Mac, authenticated browser/mail/calendar sources, the always-awake relay, and the pendant’s private haptic/audio channel to route—not merely summarize—interruptions.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic policy evaluation and event filtering; a cheap background model may classify message urgency, while realtime is reserved for the spoken urgent alert.
- **latency:** Urgent event delivery under 3 seconds; routine suppression immediate and reversible.
- **cost:** Near-zero model cost for explicit sender/subject rules; background classification costs a few cents per day at most.
- **security:** Do classification locally where possible. Do not read message bodies into the relay by default. Require explicit setup for allowed urgent senders/categories, and make emergency override and mute state visible.
- **missing:** A Mac presentation/co-presence signal that is reliable without Accessibility (meeting APIs, frontmost app, or calendar/Focus integration).; A local notification interception/router with per-source policy and deduplication.; A relay event subscription and pendant haptic/audio alert protocol with acknowledgement and escalation.; An owner-facing policy editor and audit log.

### "Run a private end-to-end check: speak a synthetic phrase through the pendant, reach the Mac and browser, and tell me exactly which link failed—without touching my real tabs or sending anything."
- **useful because:** The owner currently cannot know whether a failure is the pendant, audio bridge, relay, Mac planner, or browser session. A single safe canary would exercise the complete hive with synthetic data and produce a human-readable fault boundary, turning an opaque “failed” into an actionable answer.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Deterministic canary protocol; no expensive model call except optional speech-quality scoring.
- **latency:** A full test under 15 seconds, with per-hop results streaming to the pendant and dashboard.
- **cost:** Pennies or less per run; synthetic audio upload and one temporary browser canary dominate.
- **security:** Use a dedicated non-authenticated local canary page and nonce-bound synthetic phrase. Never inspect or navigate the owner’s real tabs, never persist audio beyond the test TTL, and require explicit confirmation before testing a live wearable microphone.
- **missing:** A registered pendant/bridge test endpoint and loopback audio checksum in firmware.; Relay canary sessions with hop-by-hop acknowledgements and expiry.; A browser extension sandbox tab that reports DOM readiness without accessing existing tabs.; A typed diagnostic report that maps failures to pendant, USB bridge, relay, Mac, or browser.


## Changes it proposed to its own stack

### `integration` — Make the action runner attach an explicit verificationState to every receipt. When /observe reports uiActionsWillReachTheScreen=false or permissions.ready=false, receipts for ui_click, ui_menu, type_text, press_keys, and vision steps must be 'unverified' and must not emit completion events to the relay; only AppleScript/browser/API actions with independent postconditions may be 'verified'.
- **owner gets:** The owner stops hearing confident lies such as 'done' when the Mac could not interact with the screen. Spoken responses become honest and actionable: 'I could not verify that' instead of silently losing a request.
- effort: Medium: receipt schema, executor gate, pipeline event mapping, and tests for Accessibility-off and browser-success cases.  ·  risk: Existing automations may appear to fail where they previously reported success; recover by offering a safe retry after the owner grants permissions or by routing through AppleScript/browser APIs.
- cost: Negligible API cost; fewer unnecessary vision/retry calls.  ·  latency: Adds one local permission/postcondition check, typically under 100 ms.
- security: Improves safety by preventing unverified side effects from being represented as completed; no new data leaves the Mac.
- depends on: Owner may optionally grant Accessibility and Screen Recording; the feature must remain correct without those grants.; A typed postcondition field for browser and AppleScript actions.


## What it asked for

_Nothing._
## Its own summary

Fresh perception this round: the Mac agent and Safari bridge are online, but Accessibility and Screen Recording are still false; /observe explicitly warns that UI actions can report success while doing nothing. Safari has 3 tabs and zero pending commands, yet the active tab is literally titled “Failed to open page.” The relay is reachable, but there is still no registered nRF9160 pendant. Recorded pipeline history proves 24 kHz mono output exists, while an older input path was 15,625 Hz. I recorded these facts and proposed three new cross-surface capabilities: evidence-backed spoken completion, a non-replaying browser usability repair flow, and privacy-preserving local attention summaries. What I still need is not another probe: the owner must grant TCC to the exact AI Pendant Agent binary if visual UI control is desired, and the pendant must register before wearable delivery can be verified. I also still need authoritative relay delivery/ack semantics and the outstanding 24 kHz implementation context when the orchestrator returns it.

**Biggest unknown:** Whether any physical pendant can currently be registered and tested end-to-end, plus whether relay acknowledgements mean delivered-to-device or merely accepted-for-download.

