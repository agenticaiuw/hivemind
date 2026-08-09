# Harness derivation — mac-planner — round 215

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-live-state-2026-08-08** — Mac agent is live with Safari foreground, 14 apps running, Accessibility and Screen Recording trusted for AI Pendant Agent, synthesized input verified, and three browser sessions open. Pendant remains USB-testable but LTE registration is not established.
  - evidence: mac_readonly_inspect(operation=running_apps/foreground_app) resolved to GET /observe at 04:49:43Z and returned foreground Safari, accessibility trusted/eventsPost true/screenRecording true, browser sessions 3.

## Capabilities it proposed

### "If the pendant audio starts failing while it is plugged into my Mac, diagnose it automatically: run the non-recording audio fixture over USB, correlate the pendant counters with the Mac and relay logs, and tell me one concrete fix or that it is healthy."
- **useful because:** The device is physically attached today but LTE is not registered, so this can work now. It converts opaque dropped audio into a trustworthy answer and catches framing, CPU, and transport regressions before a real conversation is ruined.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** background/cheap model for counter classification; realtime is unnecessary except for a live call alert
- **latency:** Start within 2 s of a detected health anomaly and produce a result within 30 s; never interrupt active playback without an explicit diagnostic trigger.
- **cost:** Usually under $0.01 per run; fixture and counter collection dominate, with model use limited to anomaly classification.
- **security:** The fixture must be synthetic and never record microphone content. USB logs may include URLs or tokens from surrounding processes, so redact lines before relay upload and retain only counters and hashes.
- **missing:** a USB-serial supervisor that can arm s16-dbfs without a gesture; a relay correlation job joining fixture telemetry, pipeline events, and Mac job receipts; a user-facing health result that can be queued in the existing pendant alert inbox

### "Start a pendant conversation over USB when I am at my Mac, then hand it to LTE without losing the turn when I unplug it; say which link is active and preserve the spoken reply across the handoff."
- **useful because:** The pendant is connected over USB today but unregistered on LTE. A USB-first mode makes it useful immediately and a handoff prevents the worst failure: speaking into a conversation that silently died when leaving the desk.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** realtime for the active voice turn; background only for handoff reconciliation and telemetry summaries
- **latency:** USB conversation start under 1 s; link-state announcement under 250 ms; handoff without more than one lost audio frame or 2 s of conversational delay.
- **cost:** No extra model call for link changes; roughly $0.01-$0.05 per normal voice turn depending on transcription and response length.
- **security:** USB serial is local and should be treated as trusted only while the approved Mac agent is connected. Authenticate the device session, bind queued audio to a short-lived call ID, erase staged audio after relay acknowledgement, and never silently fall back to an untrusted host.
- **missing:** USB serial transport adapter between the Mac agent and pendant firmware; relay session migration semantics that preserve sequence numbers and staged downlink audio; explicit link-state UI/LED and a reconnect test harness

### "After you do something on my Mac from a spoken request, verify the result on the Mac and in the browser before telling me it is done; if the state is wrong, retry once and report the exact mismatch."
- **useful because:** A successful API receipt is not proof that Safari opened the intended tab, a file was saved, or a shortcut changed state. This gives the owner a truthful spoken result instead of false completion, especially when the Mac is busy or a browser session has gone stale.
- **path:** relay-realtime → mac-planner → browser → pendant → dashboard
- **model tier:** cheap background verifier with deterministic checks first; realtime only to phrase the final one-sentence result
- **latency:** Verification within 2 s for open/type actions and 10 s for multi-step jobs; do not block the initial action unless the request is explicitly transactional.
- **cost:** Under $0.01 when deterministic; $0.02-$0.06 only when a model must compare intended and observed UI state.
- **security:** Verification must redact passwords, secure-input fields, mail bodies, and page content outside the target. Never retry destructive actions automatically; retain an immutable intended/observed receipt and route mismatches to the owner's alert inbox.
- **missing:** a postcondition field in the server-to-Mac plan contract; a read-only semantic verifier for foreground app, URL, file existence, and UI state; retry classification that distinguishes safe idempotent actions from mutations

### "Start a long Mac task from my voice, then let me leave the desk: send milestone updates to the pendant, let me ask its current stage, and let a button cancel or pause the job safely without reopening the Mac session."
- **useful because:** Today a Mac job is effectively invisible once the owner walks away. This makes the wearable the control surface for long-running browser, file, and research work while preserving the Mac's ability to perform the actual task.
- **path:** pendant → relay-realtime → mac-planner → browser → dashboard
- **model tier:** background model for milestone extraction and compact summaries; realtime only for the owner's short status questions
- **latency:** First acknowledgement under 500 ms, milestone delivery within 2 s of a state change, status answers under 1 s, and cancellation acknowledgement under 2 s.
- **cost:** Usually below $0.02 per job; cost is dominated by occasional summarization, while most updates are deterministic receipts.
- **security:** The pendant must receive redacted progress, never raw page contents or secrets. Cancellation must be idempotent and distinguish pausing from destructive termination. Require an explicit job lease and expire it when the owner cannot be authenticated.
- **missing:** a durable job-to-pendant subscription with compact milestone events; firmware handling for job-status and cancel commands through the existing alert/inbox mechanism; pause/resume checkpoints in the Mac planner and browser harness; a lease and idempotent cancellation protocol spanning relay and Mac

### "Whenever a consequential Mac or browser action finishes, give me a one-sentence spoken receipt naming exactly what changed, where, and until when it can be undone; let me say "undo that" from the pendant during the valid window."
- **useful because:** The owner should not have to trust a silent browser or Mac mutation. A wearable receipt makes remote actions legible while the Mac supplies exact state and the relay supplies a bounded undo path.
- **path:** pendant → relay-realtime → mac-planner → browser → dashboard
- **model tier:** deterministic receipt formatter; realtime model only for ambiguous natural-language references such as "that last purchase"
- **latency:** Receipt within 1 s of completion; undo dispatch within 2 s; no model call for ordinary receipts.
- **cost:** Near-zero for deterministic receipts; at most $0.01 for resolving an ambiguous reference.
- **security:** Never speak secrets, full email bodies, credentials, or payment details. Require explicit identity binding for undo, make the expiry and scope audible, and refuse undo when the underlying operation is no longer safely reversible.
- **missing:** a common receipt schema carrying touched resources, reversibility, and expiry; Mac/browser adapters that expose compensating actions rather than only success/failure; pendant delivery and voice resolution for receipt IDs; a durable policy for which action classes may be announced aloud

### "Let me ask the pendant whether this Mac and its browser session are still the trusted machines I paired, and warn me if the agent, USB bridge, browser session, or relay identity changed before any action is sent."
- **useful because:** The system crosses a wearable, USB-connected hardware, a Mac with authenticated browser sessions, and a relay. Today the owner has no spoken, end-to-end indication that all four links still terminate at the intended devices.
- **path:** pendant → mac-planner → browser → relay-realtime → dashboard
- **model tier:** deterministic attestation and policy evaluation; no expensive model call needed
- **latency:** Answer in under 2 s from a cached healthy state; perform a fresh challenge in under 5 s when requested.
- **cost:** Negligible API cost; cryptographic challenge traffic and occasional dashboard storage dominate.
- **security:** Use hardware-backed or provisioned device keys where available, short-lived nonces, and no raw browser cookies or URLs in attestations. A failed check must prevent the requested action and surface a clear local LED/error state.
- **missing:** device identity keys and challenge-response support in pendant and bridge firmware; relay-held pairing records and rotation/revocation workflow; Mac agent and browser extension attestation endpoints; a pendant-visible trust result and action precondition


## Changes it proposed to its own stack

### `mac-harness` — Add a supervised USB serial session manager for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA that exposes framed device events to the relay, reconnects idempotently, timestamps every frame, and records a receipt without ever opening the microphone.
- **owner gets:** The pendant and audio bridge are physically attached now; this is the shortest path to a usable desk conversation and automatic audio diagnosis instead of waiting for LTE registration.
- effort: Medium: serial framing, reconnect state machine, device identity handshake, and a small relay adapter; then a hardware smoke test.  ·  risk: A bad framing parser could hang or flood the Mac, and stale device paths could target the wrong USB device. Require VID/PID/serial identity, cap buffers, and expose a kill switch; recover by closing and reopening the port.
- cost: Negligible API cost; approximately $0-$30 if a powered USB hub/cables are needed, otherwise no hardware spend.  ·  latency: Adds under 20 ms framing latency; reconnect recovery target 2 s.
- security: USB becomes a privileged local control channel. Authenticate the board identity and restrict commands to the pendant/bridge protocol; redact raw logs before relay upload.
- depends on: relay session migration semantics from the USB-first conversation proposal; the existing audio_path_diagnostic_fixture firmware trigger; a documented serial framing protocol


## What it asked for

_Nothing._
