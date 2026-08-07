# Harness derivation — unified — round 132

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Use my pendant over USB right now, even if LTE is unavailable: let me press the button, speak, and hear your answer through the paired headphones, then resume on LTE automatically when it returns.”"
- **useful because:** The hardware is physically on this Mac today but unregistered with the relay, so the owner gets a usable wearable now instead of waiting for carrier registration. The Mac can terminate the serial audio path, the relay/realtime model can answer, and the ESP32 can keep Bluetooth playback; reconnecting must not duplicate or lose a turn.
- **path:** pendant → mac-planner → mac-terminal → relay-realtime → new-surface
- **model tier:** Realtime only for the live turn; deterministic transport/session state on Mac and relay; background tier for diagnostics and reconciliation.
- **latency:** Button-to-listening under 250 ms locally; first spoken audio under 1.5 s. LTE recovery may take seconds but must be silent and resumable.
- **cost:** Realtime audio/model cost dominates, roughly one normal voice turn; USB framing and local relay are negligible. No browser minutes consumed.
- **security:** USB audio and transcripts stay on the owner's Mac unless explicitly sent to relay; pairing must bind the expected serial IDs, reject arbitrary USB devices, and show a distinct LED pattern for local-only mode. Never upload SD failure buffers automatically.
- **missing:** A Mac USB-serial audio daemon that speaks the existing pendant framing; Transport/session arbitration between USB and LTE with sequence numbers and duplicate suppression; ESP32 playback control exposed as a tested local route; A local realtime ingress that can hand the turn to the cloud relay without pretending the pendant is LTE-registered

### "“Research this for me across the public web and my logged-in tabs, keep going if my Mac sleeps, and leave one cited answer plus a short audio version; never submit or send anything.”"
- **useful because:** Today public research can run on the always-awake relay while Safari is the only place that can see the owner's private accounts, but there is no single handoff that waits for Safari, merges both evidence sets, and delivers a useful result. This turns a spoken request into a resilient overnight investigation rather than a failed login or a half-finished Mac job.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → dashboard-ux
- **model tier:** Background tier for crawling, extraction, and synthesis; planner only for ambiguous private-page steps; realtime only to accept the initial request and announce completion.
- **latency:** Acknowledge in under 2 seconds; public leg starts immediately; final brief within the requested deadline or by next morning. Audio should be ready before the owner asks for it.
- **cost:** Background model and public Browser Run dominate; private Safari actions consume Mac time, not realtime tokens. One synthesis call plus TTS per task; cache unchanged sources to avoid repeat cost.
- **security:** Private evidence never leaves the relay unless the owner explicitly authorizes it; merge should happen on the Mac or redact sensitive fields before upload. Keep URL/title/snippet provenance, stop at login walls, and require confirmation for any click/type/submit that changes state.
- **missing:** Durable cross-backend research job with a jobId and resumable checkpoints; A privacy-preserving merge protocol for relay public evidence and Mac private evidence; Audio queue delivery and completion notification to the pendant; A planner contract that distinguishes read-only extraction from mutation

### "“Review the change I’m working on, run the relevant tests, and tell me through the pendant what is actually proven; if something is wrong, prepare a patch but do not apply it.”"
- **useful because:** The owner can currently ask the Mac to run isolated commands, but cannot get a trustworthy, spoken engineering verdict tied to the exact workspace diff and test evidence. This combines the worn trigger, Mac terminal/editor state, relay job tracking, and optional browser context into a safe review loop that leaves the working tree untouched unless explicitly approved.
- **path:** pendant → mac-terminal → mac-planner → mac-vision → relay-realtime → dashboard-ux
- **model tier:** Deterministic shell collection and test execution first; background model for summarizing logs; planner tier only when selecting tests or drafting a nontrivial patch.
- **latency:** Acknowledge immediately; first status within 3 seconds; completion depends on tests. Spoken result must be one short sentence with an option to hear failures and evidence.
- **cost:** Local shell/test execution dominates time; background synthesis is a small call. Planner escalation only for ambiguous repositories, so ordinary reviews avoid expensive realtime/planner usage.
- **security:** Read-only by default: capture git diff/status, lock workspace root, and run an allowlisted test command. Draft patches in a temporary worktree or unified diff; never write the owner's tree, send code, or push without explicit approval. Include commit/file hashes and test exit codes in the receipt.
- **missing:** Workspace-aware read-only diagnostics and patch generation with temporary worktrees; A typed evidence receipt linking each claim to command output and file revision; Pendant notification/streaming for long-running test progress; A Mac policy that can distinguish safe test commands from mutating shell actions

### "“Put the pendant in interpreter mode: translate each side of this conversation as we speak, play the translation privately in my headphones, and keep a transcript I can review later.”"
- **useful because:** The owner could communicate across a language barrier without handing over a phone or repeatedly invoking an app. The pendant supplies the natural turn trigger and private audio, the Mac/ESP32 handles the currently attached audio hardware, and the relay provides fast translation plus a durable, reviewable transcript. It must handle alternating speakers rather than translating isolated commands.
- **path:** pendant → mac-planner → relay-realtime → dashboard-ux → new-surface
- **model tier:** Realtime speech recognition/translation for the live exchange; background tier for transcript cleanup, speaker-turn labeling, and optional summary after the conversation.
- **latency:** Translation audio should begin within 700 ms of each utterance ending; tolerate a few seconds during network loss by showing a clear queued state rather than fabricating translation.
- **cost:** One realtime bidirectional audio session dominates cost; post-session cleanup is a small background call. No browser usage unless the owner explicitly asks to look up terminology.
- **security:** Interpreter mode is an explicit, visible session with a spoken and LED indication; do not retain raw audio by default. Store encrypted translated text only after the owner enables transcript retention, and provide a local delete gesture. Warn before sending sensitive conversation audio to the relay.
- **missing:** A dedicated bilingual turn-taking protocol with language selection and barge-in handling; Pendant/Mac USB audio transport (the pendant is currently not LTE-registered); Per-session transcript consent and encrypted retention controls; Realtime translation output format compatible with the 24 kHz playback path

### "“If I say ‘I need help’ or hold the button, start a discreet safety session: tell my chosen contacts where I am through my phone, keep a live check-in timer, and let me cancel it by voice or button.”"
- **useful because:** A wearable should help when reaching for a phone is unsafe or impossible. The pendant can detect the deliberate trigger and provide local feedback, the Mac/phone can supply location and messaging reach, and the relay can keep the session alive and record delivery receipts. This is a coordinated safety primitive, not a normal reminder or browser action.
- **path:** pendant → mac-planner → relay-realtime → iOS → dashboard-ux → new-surface
- **model tier:** Deterministic trigger, location, timer, and delivery state; realtime speech only for interpreting the short cancellation/confirmation exchange; no planner needed.
- **latency:** Local alarm state and cancellation window under 300 ms; contact notification within 10 seconds when a companion link exists; retry and visibly escalate when it does not.
- **cost:** Negligible model cost; SMS/push/location-provider charges dominate. Keep the relay heartbeat lightweight and avoid continuous audio unless the owner explicitly enables it.
- **security:** Require deliberate hold or an unmistakable phrase, never infer an emergency from ordinary speech. Encrypt location, use an allowlisted contact set, show a countdown and cancellation path, and require owner setup plus periodic contact verification. Do not expose safety-session data in general memory or browser logs.
- **missing:** A phone companion permissioned for precise location and emergency messaging; A pendant-local long-hold detector and unmistakable cancel feedback; Relay durable safety-session state, retries, and delivery receipts; A setup flow for contacts, countdown, retention, and jurisdiction-specific emergency limitations


## What it asked for

### `s13-u35s` (skill) — usb_fallback_audio_session
- does: When USB serial is present and LTE is unavailable, expose the existing microphone/button/audio framing to the Mac as a local conversation transport. Maintain monotonic frame and turn sequence numbers, pause LTE retries while USB owns the session, and hand ownership back only at a turn boundary so audio is not duplicated.
- must be on-device because: The pendant must detect physical USB presence and continue capturing/playing when the modem is unregistered or the relay is unreachable; a server cannot sense or arbitrate this physical link.
- trigger: Button press while the USB serial link is detected, or a transport-loss event during an active turn.
- storage: Persist only a crash-safe last turn/sequence watermark and transport owner in a tiny settings/NVS record (well under 4 KB); audio remains RAM/SD failure-buffer policy.
- RAM budget: About 8–12 KB for serial ring buffers, frame metadata, and arbitration state; fits the 211,608 B application RAM only if buffers are bounded and no second Opus codec instance is added.

## Its own summary

Fresh discovery confirms the owner’s Mac bridge is online and Safari has 3 tabs, while the pendant is not relay-registered; the physically connected USB path is therefore the most immediately valuable frontier. I recorded three new cross-surface capabilities: USB-local wearable conversation with automatic LTE recovery, privacy-preserving public+authenticated research that survives a sleeping Mac, and spoken evidence-backed code review with a non-mutating patch draft. I also queued a pendant-local usb_fallback_audio_session skill, budgeted at 8–12 KB RAM, to arbitrate USB/LTE at turn boundaries. The first capability is the strongest near-term candidate because it makes today’s attached hardware useful without waiting for registration.

**Biggest unknown:** The exact existing nRF9160 USB serial framing and whether the current Mac harness can already ingest pendant PCM and return 24 kHz playback; that determines whether USB fallback is a small integration or a new firmware/audio bridge. I still need an end-to-end USB loopback test and a measured audio acceptance result, not another architecture proposal.

