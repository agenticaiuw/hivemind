# Harness derivation — mac-terminal — round 135

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I’m busy—queue this. When I next press the pendant button, read me the most important completed result, and let me say ‘open it’ to continue on the Mac or in the exact logged-in browser tab.”"
- **useful because:** This turns background work into a genuinely wearable inbox: the owner does not need to remember which job finished, find the dashboard, or repeat context. The relay ranks finished results, the pendant provides the pickup moment, and the Mac/browser resumes the concrete thread.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for queued research/extraction and ranking; realtime only for the short pickup conversation
- **latency:** Button acknowledgement under 300 ms locally; first spoken result under 2 s if cached; continuation may take 5–20 s depending on Mac/browser work.
- **cost:** About $0.01–$0.08 per queued task for background model/tool work; pickup speech is dominated by realtime audio tokens and is usually <$0.02.
- **security:** Results may contain private browser content and must remain scoped to the originating authenticated session. ‘Open it’ needs a signed job/session reference, not a URL guessed by the model. No mail/send/purchase continuation without the existing explicit confirmation policy.
- **missing:** durable result inbox with priority, expiry, and originating surface/session; pendant button event and tiny spoken-menu protocol over the current USB serial link (and later LTE); resume endpoint that reattaches a result to a Mac job or browser tab with provenance; offline cache of a short title/status so the pendant can announce what is waiting

### "“I’m stepping away.” Lock down my active Mac and logged-in browser work, pause anything speaking aloud, and when I press the pendant again restore only the tabs and jobs I was using—not unrelated sessions."
- **useful because:** A worn device can make walk-away privacy immediate instead of relying on remembering keyboard shortcuts. It also prevents a background result or browser page from being exposed while the owner is away, then restores continuity without reopening every unrelated personal tab.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Realtime interprets the short command; deterministic local/browser actions do the lock, mute, and scoped suspend. Background model is only needed to identify the active task set.
- **latency:** Local mute and lock initiation under 500 ms; browser suspension acknowledgement under 2 s; restore under 3 s for cached tabs.
- **cost:** Near-zero model cost for deterministic mode; <$0.01 when task grouping requires a small planner call. Main cost is implementation and a small encrypted state record.
- **security:** The Mac lock must be a native OS operation, not a simulated UI click. Persist only opaque tab/session IDs and encrypted metadata; never copy page contents into the pendant. Restore must be bound to the same owner/device pairing and must not send queued browser mutations.
- **missing:** paired pendant walk-away/return event protocol with replay protection; Mac native lock/sleep and audio-pause action plus verified completion signal; browser bridge suspend/resume scoped by window/tab/session, not a global queue pause; relay state machine for quiet mode, expiration, and crash-safe restoration

### "“Start meeting mode.” Use the pendant as the control and audio endpoint, identify the meeting I’m currently in from my Mac and calendar/browser context, privately transcribe it while it runs, and when I end it give me only decisions, owners, and deadlines—with drafts saved but nothing sent."
- **useful because:** This is a genuinely cross-device function: the pendant supplies an immediate physical start/stop control and audio path, the Mac supplies the active meeting/window and calendar identity, the browser supplies a logged-in meeting session when needed, and the relay keeps transcription alive across brief link loss. The owner leaves with actionable follow-up instead of a raw transcript.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Realtime for low-latency live transcription only; a cheaper background model performs diarization, decision/deadline extraction, and concise post-meeting summarization.
- **latency:** Start/stop acknowledgement under 500 ms; live captions may trail by 1–3 seconds; a three-item action summary within 60 seconds of stopping.
- **cost:** Dominated by audio transcription duration and background summarization, roughly $0.05–$0.30 per hour depending on model and retention; no model call is needed for button control or context lookup.
- **security:** Recording must be visibly indicated on the pendant and dashboard, with an immediate hardware stop. Meeting audio and transcripts are highly sensitive: encrypt in transit and at rest, expire raw audio quickly, retain extracted actions only by default, and never send drafts without the owner’s existing confirmation.
- **missing:** a pendant meeting-mode button protocol with hardware recording indicator and guaranteed stop; Mac correlation of frontmost meeting app/window, active calendar event, and browser tab/session; relay streaming transcription session with resumable chunks and explicit raw-audio expiry; speaker/decision/deadline extraction pipeline and editable action-item artifact; dashboard review surface for transcript retention and draft ownership

### "“Use my private identity for this form.” Fill only the requested identity fields from my encrypted vault, show me the exact field mapping, and require a deliberate pendant button gesture before the browser receives any secret; never speak or place the secret in model context."
- **useful because:** The owner can complete legitimate logged-in forms without repeatedly hunting for passwords or exposing them to a cloud model. The pendant becomes a physical presence key, the browser remains the only component that sees the secret, and the Mac/relay can explain what happened without copying sensitive values.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** A small background/local planner maps labels to pre-approved field types; deterministic browser code performs insertion. Realtime is used only if the owner asks by voice; no secret-bearing prompt should reach it.
- **latency:** Field preview under 2 seconds; after button confirmation, insertion under 1 second; abort immediately on tab or origin change.
- **cost:** Near-zero per use after vault and browser integration; occasional <$0.01 local mapping call. Storage and cryptographic operations are local.
- **security:** This must not be a generic password dump. Store typed values in the system keychain or hardware-backed vault, bind each approval to origin/tab/form hash and short expiry, redact values from logs/screenshots/transcripts, and invalidate approval if DOM or destination changes. Sending, purchasing, or submitting remains separate and confirmation-gated.
- **missing:** hardware-backed or keychain-backed typed identity vault with field-level consent; pendant challenge/response gesture tied to a specific tab, origin, and form hash; browser content-script insertion that never returns secret values to relay or model; redacted field-mapping preview and audit record without raw values

### "“Review what I changed.” Read the active project and git diff on my Mac, inspect related authenticated issue or documentation tabs if needed, explain the three riskiest changes through the pendant, and let me approve a precise patch plus tests without ever silently committing or pushing."
- **useful because:** The owner gets a code-review loop while away from the keyboard: the Mac has filesystem and test reach, the browser has private issue context, and the pendant gives a concise spoken risk review and an explicit physical approval moment. It is more useful than merely running a shell command because the result is tied to the actual diff, issue context, patch, and test evidence.
- **path:** pendant → mac-terminal → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Cheaper background model gathers diff, issue context, and test output; realtime handles only the short spoken explanation and approval conversation.
- **latency:** Initial diff inventory under 5 seconds; risk review under 30 seconds for a normal project; patch/test cycle under 2 minutes, with progress delivered asynchronously.
- **cost:** Usually $0.03–$0.20 per review, dominated by diff/issue context and patch reasoning; test execution is local and has no API cost.
- **security:** Never upload whole repositories by default: send only changed hunks and explicitly selected issue excerpts. Respect secret scanning and .gitignore boundaries. Approval must bind to a content hash of the exact patch and test plan; a changed working tree invalidates it. Commit, push, and issue changes remain separate actions.
- **missing:** project-aware diff/test inventory with secret and generated-file redaction; browser-to-diff correlation for the selected issue or pull request; patch proposal artifact containing exact hunks, content hash, and test commands; pendant spoken risk summary and physical approval bound to that artifact; local test runner receipts that distinguish passed, failed, skipped, and not-run


## Changes it proposed to its own stack

### `integration` — Build a USB commissioning and audio-calibration session spanning both live boards: the Mac opens the nRF9160 and ESP32 serial ports, commands a timestamped 24 kHz test stream, has the bridge return buffer-underrun/PLL/resampler counters, and records a signed health artifact (firmware hashes, sample-rate path, latency, packet loss). On failure it automatically selects a safe low-rate profile and leaves a repair recipe instead of claiming the audio path is healthy.
- **owner gets:** The owner gets a truthful ‘my pendant audio is ready’ check and a concrete diagnosis before wearing it. It directly protects the requested 24 kHz superwideband path from silent SBC underruns, clock drift, or a disconnected USB board.
- effort: Medium-high: serial framing and test mode on both firmwares, a Mac harness session, and a small dashboard/voice result. Must be tested against the current nRF9160 DK and HUZZAH32, then redesigned for the eventual product board.  ·  risk: A test tone could leak to headphones or interfere with an active conversation; require an explicit test command and always restore the prior stream. Serial reset or a bad fallback profile could leave either board boot-looping, so keep a bootloader-recoverable profile and make calibration idempotent.
- cost: No per-call API cost; roughly 1–2 seconds of local CPU/USB time per test and negligible storage for a small artifact. Future hardware needs a timestamp/counter path and perhaps a better clock source.  ·  latency: Adds no steady-state latency; commissioning takes about 2–5 seconds. A safe fallback may add 60–120 ms audio buffering but is preferable to silence.
- security: USB serial commands must be restricted to the paired boards and authenticated with a nonce; artifacts should omit raw audio and store only counters/hashes. Do not expose firmware flashing through the voice surface.
- depends on: USB serial enumeration and framing for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; a firmware diagnostic opcode on both boards; Mac-side typed serial diagnostic executor; truthful action-status reporting so a failed test cannot produce a success receipt


## What it asked for

_Nothing._
