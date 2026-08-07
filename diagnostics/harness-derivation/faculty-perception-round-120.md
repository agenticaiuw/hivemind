# Harness derivation — faculty-perception — round 120

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent permissions** — At 2026-08-07T18:00Z, AI Pendant Agent is online with browser/relay/automation available, but Accessibility and Screen Recording are false; inputReachability failed and UI actions cannot be trusted. Browser extension online with 3 tabs, including Gmail session.
  - evidence: GET /ops/status and GET /observe both returned trusted=false, screenRecording=false, eventsPost=false, uiActionsWillReachTheScreen=false; /browser/status returned online=true.
- **pipeline audio** — A completed cloud relay pipeline generated 24 kHz mono PCM (75,734 bytes, 1.578s) and relay accepted it for a pendant, but current registered devices contain no pendant; this is historical telemetry, not live delivery.
  - evidence: GET /pipeline event meta says sampleRate 24000, pcmBytes 75734, status done; GET /devices lists only home-macbook-bridge and offline contract-test mobile.
- **browser watches** — The page-watch store exists but both existing watches are disabled; UTC watch accumulated 8 changes and several unacknowledged reports, while stable Selenium page has zero changes.
  - evidence: GET /watches returned enabled=false for both watches, UTC reports acknowledged=false for latest two.

## Capabilities it proposed

### "“Is that actually done, or did the system only say it was done?”"
- **useful because:** This would be the single most useful trust feature: reconcile the relay receipt, Mac job/pipeline events, browser result, and registered-device delivery state before answering. It would distinguish completed, accepted-but-not-delivered, waiting-for-approval, stale historical telemetry, and unverifiable—so the owner never hears that a pendant played something when no pendant is registered.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap background reconciliation for receipts; realtime only to phrase the answer when the owner asks.
- **latency:** Under 1 second from cached state; up to 3 seconds for one live status refresh.
- **cost:** Usually <$0.001 per question if state is structured; the dominant cost is occasional Mac/relay reads, not model tokens.
- **security:** Must not expose private browser URLs or snippets in a spoken answer unless relevant; retain source IDs and timestamps, and mark unavailable sources rather than guessing. Any corrective action still requires normal approval.
- **missing:** A cross-surface truth/reconciliation record keyed by job and delivery attempt; A relay device-delivery acknowledgement distinct from relay acceptance; A standard status vocabulary and freshness/expiry policy; A spoken answer path that refuses stale historical pipeline evidence

### "“I plugged the pendant into my Mac—make it usable and prove each part works.”"
- **useful because:** Today the owner can physically connect the nRF9160 and ESP32 boards, yet the relay may still show no pendant. A bring-up flight recorder would identify serial ports, inspect firmware identity, run a safe microphone/playback/button/LED loopback, attempt pairing, and leave a plain-language pass/fail report. It turns an opaque dead wearable into a diagnosable product in one interaction.
- **path:** mac-terminal → mac-planner → relay-realtime → faculty-perception → faculty-action
- **model tier:** Background/cheap model for parsing serial logs and composing the report; realtime only for the owner's spoken start/stop prompts.
- **latency:** Initial detection under 5 seconds; hardware test 30–90 seconds; never silently flash or erase firmware.
- **cost:** <$0.01 per run; dominated by local serial I/O, with negligible model usage.
- **security:** Serial commands must be allowlisted and read-only by default. Firmware flashing, pairing changes, or microphone recording require explicit confirmation. Reports may include device identifiers and audio test metadata, so keep them local unless the owner opts in.
- **missing:** A Mac-agent serial-port inventory and bounded serial read/write route for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A firmware diagnostic protocol with version/capability response and non-destructive test commands; A relay pairing attempt that returns a device-registration acknowledgement; A signed bring-up report joining local serial evidence to relay state

### "“Only interrupt me when it is genuinely urgent—and otherwise hold it until I am free.”"
- **useful because:** The hive currently has independent alerts, browser changes, Mac jobs, and spoken audio, but no shared sense of whether interruption is appropriate. A governor would combine foreground app/meeting state, active audio, browser context, calendar, alert urgency, and pendant connectivity; it would hold low-value notifications, deliver urgent ones once, and explain why it interrupted. This prevents the wearable from becoming another source of noise.
- **path:** faculty-perception → mac-planner → browser-extension → relay-realtime → faculty-judgement → faculty-action
- **model tier:** Rules and a small classifier in the background; realtime only when an urgent alert must be phrased immediately.
- **latency:** Evaluate on each event in under 200 ms from cached state; re-evaluate on context changes within 2 seconds.
- **cost:** <$0.001 per event with rules; model calls only for ambiguous urgency classification.
- **security:** Foreground app names, calendar titles, and authenticated tab metadata are sensitive. Keep raw values local, transmit only an urgency/interruptibility decision, and provide a physical/button override for Do Not Disturb. Never infer safety-critical urgency without a clear source.
- **missing:** A shared interruptibility state with TTL and owner override; Event normalization across browser watches, Mac jobs, relay alerts, and audio playback; A durable hold/merge/deduplicate queue with acknowledgement semantics; Calendar/meeting presence and active-audio adapters; A pendant delivery channel with confirmed receipt, not merely relay acceptance

### "“I was away from the Mac. Give me the trustworthy timeline of what happened while I was gone.”"
- **useful because:** A single chronological, causally ordered account would bridge the hive's biggest perceptual gap: relay arrival time, Mac acceptance, browser change, local approval wait, audio rendering, and (when present) pendant receipt are currently separate records with different clocks. The owner would get events grouped by one job, clock-skew warnings, gaps explicitly labeled unknown, and no false claim that a queued item was heard.
- **path:** relay-realtime → mac-planner → browser-extension → mac-terminal → faculty-perception → faculty-judgement
- **model tier:** Deterministic event join and clock normalization first; cheap summarizer only for the final human-readable timeline.
- **latency:** Under 2 seconds for a cached day; under 10 seconds if local logs and relay records must be fetched.
- **cost:** <$0.005 per timeline; mostly local parsing and a small summary.
- **security:** Timeline may reveal private tab titles, messages, and machine activity. Default to redacted event labels, require explicit expansion for URLs/content, and retain raw evidence locally with bounded retention.
- **missing:** A common event envelope with source clock, monotonic sequence, causation/job ID, and observed-vs-recorded time; Clock-offset measurement between Mac, relay, browser extension, and pendant; A gap/contradiction detector (for example relay accepted audio but no registered pendant); A user-facing timeline route and exportable evidence bundle

### "“Before you change anything, show me the likely side effects and let me try the whole action in a rehearsal.”"
- **useful because:** The owner can currently approve or undo some actions, but cannot see a realistic preview of cross-surface consequences before execution. A rehearsal would run read-only planning against the actual browser session, Mac state, relay queue, and available rollback receipts; it would show changed fields, notifications, generated files, and failure branches, then discard the rehearsal. This is materially safer than discovering side effects after approval.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Small background model for scenario narration; deterministic adapters and dry-run APIs do the state simulation. Realtime is only for the owner's interactive questions.
- **latency:** Simple actions under 3 seconds; multi-step browser/Mac rehearsal under 15 seconds.
- **cost:** $0.005–$0.03 per rehearsal, dominated by one planning call and browser/Mac reads.
- **security:** A rehearsal must not mutate accounts, send network requests with side effects, create real reminders, or leak private page data into prompts. Use isolated browser transactions or mocked submissions, label every result as predicted versus observed, and require fresh confirmation after the rehearsal.
- **missing:** A dry-run contract for every action adapter, including side-effect declarations; Browser transaction snapshots or isolated form-submit simulation; Mac action simulators for reminders, files, messages, and scripts; A structured predicted-diff format with confidence and rollback coverage; A guarantee that preview reads cannot themselves trigger account mutations

### "“Handle this, but keep anything private on my Mac and tell me exactly what—if anything—left the device.”"
- **useful because:** The owner cannot currently delegate a mixed task while controlling data locality. A privacy-boundary planner would classify each input and step, keep sensitive browser text, messages, and audio on the Mac, send only minimized claims or redacted fields to the relay/model, and produce a plain-language data-travel receipt. It makes cross-surface delegation usable for private work rather than forcing an all-or-nothing trust decision.
- **path:** browser-extension → mac-terminal → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Local deterministic classifier and redactor first; a cheap model may summarize already-redacted content. Realtime receives only the minimum needed for conversation.
- **latency:** Classification and redaction under 300 ms per artifact; under 3 seconds for a task-level data-flow receipt.
- **cost:** <$0.005 per task; dominated by optional local/model redaction, not network transfer.
- **security:** The boundary engine itself must not log raw sensitive values. Default-deny unknown destinations, prevent prompt-injection from changing locality rules, cryptographically label redacted artifacts, and require explicit confirmation before any private content crosses to the relay or browser.
- **missing:** A typed sensitivity/retention label on every browser, Mac, audio, and relay artifact; Local redaction and minimization adapters before planner calls; A policy engine that enforces destination and model restrictions per field; A tamper-evident data-flow receipt exposed to the owner; Relay/model APIs that accept and preserve field-level locality labels

### "“Do this wherever it is safest and cheapest, but don't interrupt me or run down the wearable.”"
- **useful because:** The hive has multiple execution surfaces but no owner-visible scheduler that weighs battery, network reachability, Mac availability, latency, privacy, and whether the pendant is actually connected. A resource-aware planner would defer expensive work to the Mac, use the relay only when necessary, avoid generating audio that cannot be delivered, and resume when the right surface returns—without making the owner micromanage routing.
- **path:** relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic policy and queueing for placement; cheap background model only for estimating task cost or urgency.
- **latency:** Placement decision under 100 ms from cached telemetry; wake/resume within one scheduled polling interval.
- **cost:** <$0.001 per decision; savings come from avoiding unnecessary realtime calls, audio rendering, and retries.
- **security:** Do not silently defer urgent tasks or infer battery state from stale telemetry. Expose the placement rationale, enforce deadlines, preserve cancellation, and never route private data to a less-trusted surface merely because it is available.
- **missing:** A common resource/availability telemetry schema for Mac, relay, browser, pendant, and audio bridge; A durable priority/deadline queue with pause/resume and cancellation; Cost and energy estimates per action/model/audio render; A policy evaluator that combines privacy, urgency, connectivity, and delivery feasibility; A user-facing explanation of why work was placed or deferred


## What it asked for

_Nothing._
