# Harness derivation — faculty-judgement — round 127

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If something on my calendar, in my inbox, or on a logged-in site changes, tell me what that change now affects and prepare the smallest set of fixes.”"
- **useful because:** A changed flight, moved meeting, or cancelled appointment is not useful as an isolated alert: the owner needs the cascade (conflicting events, stale reminders, forms, travel details) and ready-to-review corrections. The pendant can announce only the consequence; the Mac and browser can gather and stage repairs without silently committing them.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** background for change classification and impact graph; planner only when the cascade is ambiguous; realtime solely for the short pendant announcement
- **latency:** Detect within 5 minutes of a scheduled watch or event; spoken consequence under 5 seconds after the owner asks. Staging fixes may take 1–3 minutes in the background.
- **cost:** About $0.01–$0.05 per meaningful change, dominated by authenticated-page extraction and planner escalation; unchanged watches should be deterministic and free of model calls.
- **security:** Reads private calendar, mail metadata, and logged-in pages. Store hashes and minimal changed fields, not full page copies. Never submit, cancel, or send without confirmation; require confirmation again if a proposed fix changes money, attendance, or a message recipient.
- **missing:** A cross-source temporal impact graph joining calendar events, reminders, browser watches, and pending Mac jobs; A durable change-to-impact evaluator with per-field provenance and deduplication; A review UI/audio protocol for grouped proposed fixes

### "“I’m with people” / “private mode”"
- **useful because:** The pendant is an always-on speaker in the owner's life, so the most dangerous failure is saying a private name, message, or account detail aloud at the wrong moment. This command should immediately hush speech, convert incoming alerts into a discreet button/LED queue, and later let the owner replay or summarize them privately when alone.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic policy and local firmware state for entering, suppressing, and exiting; background model only to summarize queued items; never use realtime to decide whether a secret may be spoken
- **latency:** Mute or switch output within 100 ms locally, including during a dropped relay link. Queue metadata immediately; a later summary can take seconds.
- **cost:** Near-zero for the gate and queue; $0.002–$0.02 when the owner asks for a digest, depending on queued text/audio length.
- **security:** Private text must not be sent to the relay while merely queued on the pendant. Persist only opaque item IDs and urgency locally; encrypt queued content on the Mac. Require an explicit owner gesture or spoken phrase to exit, and never infer privacy from microphone audio.
- **missing:** A firmware-resident privacy latch that gates speaker output and survives link loss; A relay-wide output policy applied to TTS, job notifications, and browser receipts; A private replay/summary queue with encrypted local storage and expiry

### "“Hold this thought.” Later: “What was I in the middle of, and continue it.”"
- **useful because:** People lose the thread when a meeting, phone call, or disconnected wearable interrupts them. The pendant should capture a tiny local marker even without LTE, while the Mac preserves the exact active tab, draft, job, and last spoken intent. On return, the owner gets one prioritized resume card and can continue rather than reconstructing context.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → mac-terminal → dashboard
- **model tier:** firmware stores the marker; deterministic join on request; background model composes a concise resume card; planner only when several threads compete
- **latency:** Local capture acknowledgment under 150 ms and no network required. Reconnection reconciliation under 10 seconds; spoken resume card under 2 seconds once data is available.
- **cost:** $0.00 for marker and deterministic join; roughly $0.005–$0.03 for a generated resume card, dominated by context size.
- **security:** The marker may reference sensitive tabs or drafts. Store an opaque nonce locally, encrypt the Mac-side context, expire unresolved markers after a configurable period, and require explicit confirmation before reopening or editing a sensitive page.
- **missing:** An offline pendant marker event and durable replay protocol over the present USB tether and eventual relay link; A cross-surface active-thread snapshot (tab, draft, job, last action, owner utterance) with expiry; A resolver that ranks interrupted threads and exposes one resumable action without duplicating work

### "“Tell me when you hear a sound I care about—like the doorbell, smoke alarm, or my name—even if I’m wearing headphones or away from the Mac.”"
- **useful because:** The pendant is the one surface physically with the owner and has a microphone; it can notice an important acoustic event that a calendar, browser, or Mac cannot. A local detector can raise an immediate spoken/LED alert, while the Mac/relay can identify the event more accurately and retain an evidence clip only when the owner allows it.
- **path:** pendant → audio bridge → mac-planner → relay-realtime → dashboard
- **model tier:** A tiny on-device classifier for a small owner-selected vocabulary; background Mac model for verification and transcription; realtime only for the alert conversation.
- **latency:** Local alert in under 500 ms from the end of the sound, including while disconnected. Verification and a short explanation within 5 seconds when the Mac is reachable.
- **cost:** Near-zero for local inference; approximately $0.001–$0.02 per verified event, with audio analysis and optional transcription dominating.
- **security:** Always-on audio is highly sensitive. Keep detection features on-device, disable raw recording by default, use a visible listening indicator, let the owner choose classes and quiet hours, and require explicit opt-in before sending an audio snippet to the Mac or relay. False alarms must be dismissible without transmitting audio.
- **missing:** An on-device acoustic-event classifier and model-update mechanism sized for the nRF9160 prototype; A local alert path that works while the LTE link is absent and a reliable USB/ESP32 notification path today; A consented event-evidence protocol between pendant, Mac, and relay with deletion controls; A calibration flow so the owner can enroll their own doorbell and name without uploading continuous room audio

### "“Let Alex help me with this for the next hour, but only give them what this task needs.”"
- **useful because:** The owner sometimes needs a human to finish a task, but forwarding a whole logged-in browser session or handing over the Mac exposes everything. The pendant can provide a physical, time-limited consent signal; the relay can mint a scoped handoff; the Mac/browser can expose only a redacted task packet and return the result for owner approval.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Deterministic policy for scope, expiry, and revocation; background model for redacting and summarizing the task packet; planner only for ambiguous field-level disclosure.
- **latency:** Create or revoke the handoff in under 2 seconds. The helper’s scoped workspace can take up to 15 seconds to provision.
- **cost:** Usually under $0.02 per handoff; model cost is dominated by redaction of long private pages, while token minting and revocation are deterministic.
- **security:** This crosses the owner’s trust boundary. Require a physical pendant gesture plus an owner-visible scope preview, encrypt the packet, expire it automatically, prohibit credential export and unrelated tab access, log every read/write, and provide an immediate local revoke gesture.
- **missing:** A scoped delegation-token service understood by relay, Mac, and browser bridge; Field-level redaction and a sandboxed helper workspace rather than raw session sharing; Pendant confirmation/revocation protocol and an owner-facing audit trail

### "“Before I choose, show me what each option would do to the rest of my week—without changing anything.”"
- **useful because:** The owner often needs judgment, not execution. A counterfactual planner could combine calendar conflicts, travel time, existing reminders, private account constraints, and unfinished Mac jobs into two or three evidence-backed futures, letting the owner choose before any draft or booking is touched.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Deterministic retrieval and constraint checks first; background model to narrate each scenario; planner only when the alternatives require multi-step interpretation. Never use realtime for the underlying research.
- **latency:** Return a useful first comparison in 10 seconds, with deeper private-page checks in under 2 minutes. No side effect during computation.
- **cost:** About $0.02–$0.10 per comparison, dominated by authenticated-page reads and scenario narration; deterministic calendar-only comparisons should cost almost nothing.
- **security:** Private pages and schedules enter a temporary scenario workspace. Keep scenarios ephemeral by default, cite every assumption, label uncertain forecasts, and require explicit confirmation before converting a scenario into an action plan.
- **missing:** A side-effect-free scenario workspace with snapshot isolation for browser and Mac state; A constraint/impact solver covering time, dependencies, and owner-defined priorities; A compact spoken comparison format with citations and an explicit promote-to-plan step


## Changes it proposed to its own stack

### `integration` — Create a durable event-to-consequence engine. Normalize calendar/mail/browser/job events into versioned entities, compute affected reminders, conflicts, drafts, and pending jobs, and emit one deduplicated impact packet with evidence links and proposed reversible repairs. Keep the engine deterministic; invoke a background model only to phrase or rank ambiguous consequences.
- **owner gets:** When life changes, the owner hears what they must do next—not five unrelated alerts—and can approve a coherent repair plan.
- effort: High: event schema, entity linking, temporal rules, provenance, and a review surface across relay and Mac.  ·  risk: False joins could suggest the wrong repair or hide a real conflict. Recover with evidence-first packets, confidence thresholds, no automatic irreversible actions, and a complete undo/ignore path.
- cost: Low steady-state compute and storage; roughly $0.01–$0.05 only for ambiguous impact summaries.  ·  latency: Seconds for local event joins; up to minutes for authenticated browser refreshes.
- security: Processes calendar, mail metadata, and private pages. Minimize to changed fields and hashes, encrypt packets, and apply per-source retention.
- depends on: A durable event ingress beyond ad-hoc /pipeline/events; A typed entity/provenance store; A review/approval packet UI

### `firmware` — Add a local speaker-privacy latch to the nRF9160 audio state machine: a button gesture or signed server command immediately blocks decoded PCM from reaching the ESP32, persists across reconnects and reboot, exposes only a visible LED pattern, and allows an explicit long-press to clear. Incoming items are represented by opaque counters until the Mac-side encrypted queue is available.
- **owner gets:** The owner can prevent an embarrassing private sentence from being spoken in a room even when LTE, the Mac, or the relay is unavailable.
- effort: Medium firmware plus ESP32 bridge protocol work; test every transition during packet loss, reboot, and active playback.  ·  risk: A stuck latch could make the pendant appear broken. Provide a distinct LED acknowledgment, local status query, watchdog-safe default, and a clearly documented long-press recovery.
- cost: No API cost; negligible RAM (a few bytes of state) and power. Requires firmware/bridge integration and field testing.  ·  latency: Under 100 ms from gesture to speaker mute; no network round trip.
- security: Fail closed for speech output; authenticate remote clear commands and never allow a queued private payload to be decoded locally without the latch being open.
- depends on: A defined button gesture and LED status contract; ESP32 bridge mute command with acknowledgment; Encrypted Mac-side notification queue


## What it asked for

_Nothing._
## Its own summary

Round 127 produced three new owner-facing capabilities: (1) change-impact repair briefs that explain what a calendar/mail/private-page change breaks and stage the smallest reversible fixes, (2) an explicit private-mode latch that suppresses all spoken sensitive output and queues discreetly, and (3) offline “hold this thought” capture that restores the exact interrupted tab/draft/job thread later. I also recorded the concrete integration impact engine and a firmware-local speaker privacy latch. The live facts matter: Safari and the Mac bridge are online, while the cellular device is offline; the pendant audio path is still prototype (15.625 kHz mic capture, 24 kHz playback decode).

**Biggest unknown:** The owner’s preferred privacy-mode gesture, queue expiry, and interruption/replay behavior remain unspecified; those choices determine whether the local latch and resume flow feel trustworthy. The major implementation gap is not another route—it is durable cross-surface event/entity provenance joining calendar, mail, browser, jobs, and pendant events.

