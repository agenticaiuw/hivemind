# Harness derivation — faculty-judgement — round 137

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **pendant-audio-design** — The pendant's LTE-M link is prototype half-duplex in practice; simultaneous 16 kbps uplink and 24 kbps downlink recently dropped 388 uplink packets (~7.8 seconds). Any conversation capture or live audio feature must default to local USB/Mac buffering and only upload after capture, not stream duplex.
  - evidence: get_hardware_spec(network): LTE-M prototype, one TLS WebSocket, 2 kB TLS record limit, measured 388 uplink packets dropped during simultaneous speech.

## Capabilities it proposed

### "“Run my monthly access-resilience check: verify that my important accounts, backups, browser sessions, Mac, and pendant can still be recovered, and tell me exactly what would fail—without exposing any secrets or changing anything.”"
- **useful because:** People discover a dead password, expired session, missing backup, or disconnected wearable only during a crisis. This turns recovery from an assumption into a private, non-destructive drill spanning the browser's logged-in sessions, Mac's local backup/configuration state, relay reachability, and the pendant's USB/offline path.
- **path:** browser-extension → mac-planner → relay-realtime → unified → dashboard
- **model tier:** Background model for monthly checks and evidence summarization; realtime only if the owner asks from the pendant.
- **latency:** A monthly run may take 2–5 minutes; spoken result under 30 seconds, with a detailed report on Mac.
- **cost:** Roughly $0.05–$0.25 per run depending on number of accounts/pages; browser and Mac inspection dominate, not generation.
- **security:** Never read or persist passwords, recovery codes, message contents, or secret values; return boolean/age/health evidence only. Require confirmation for any offered repair. Encrypt the report and expire it quickly.
- **missing:** A redacted account-recovery check protocol (health assertions rather than credential extraction); Mac backup and keychain-presence inspectors that do not reveal values; A pendant USB/LTE connectivity self-test and a signed drill report; A monthly routine that can fan out across browser, Mac, and relay

### "“Audit my privacy across the pendant, relay, Mac, and logged-in browser: show me what sensitive material is stored where, who can reach it, and give me a safe, reversible cleanup plan.”"
- **useful because:** The owner currently has to trust that audio, browser extracts, logs, drafts, and local files disappear when expected. A single, source-cited map makes invisible retention visible and lets them reduce exposure without manually hunting four systems.
- **path:** relay-realtime → mac-terminal → browser-extension → mac-planner → dashboard → pendant
- **model tier:** Background model for inventory, classification, and report writing; use realtime only when the owner asks for an immediate scan from the pendant.
- **latency:** 5–10 minutes for a full scan; a short spoken summary in under 20 seconds, with cleanup requiring explicit approval per category.
- **cost:** $0.10–$0.50 per scan; classification of snippets and file metadata dominates. Keep raw content local where possible.
- **security:** The audit itself is highly sensitive. Classify locally on Mac when possible, send hashes/locations rather than contents, redact secrets before relay storage, and require confirmation before deletion. Never scan or reveal unrelated third-party data.
- **missing:** A unified retention inventory spanning relay objects, D1 pointers, Mac logs/files, browser inspection caches, and pendant flash; Local secret/PII classification with redacted counts and hashes; Preview/undo cleanup transactions across surfaces; A report UI that explains access boundaries and expiration dates

### "“When I tap the pendant at the start and end of a conversation, securely capture that interval, transcribe it on my Mac, and leave me a private summary of decisions, names, and follow-ups—never record outside the two taps.”"
- **useful because:** People lose the details that matter in conversations. A deliberate two-tap boundary gives the owner a reliable memory aid without an always-on recorder: the pendant supplies an unmistakable physical consent boundary, the bridge carries audio, and the Mac creates searchable notes and follow-ups.
- **path:** pendant → bridge → mac-terminal → mac-planner → relay-realtime → dashboard
- **model tier:** Local Mac speech-to-text and a cheaper background summarizer; realtime is unnecessary except to acknowledge the tap boundary.
- **latency:** Tap acknowledgement under 300 ms; transcript within 1 minute of ending; summary within 2 minutes.
- **cost:** $0.02–$0.15 per conversation depending on local versus hosted transcription; audio transfer/storage dominates. Local transcription can make API cost near zero.
- **security:** Require a physical start and stop tap, show a visible LED/audio cue, keep raw audio on the Mac by default with short retention, and warn about local recording-consent laws. Never upload or share without a separate confirmation. Provide an immediate stop/erase gesture.
- **missing:** Pendant firmware start/stop recording state and unmistakable LED/audio cues; ESP32-to-Mac lossless interval capture with timestamps and drop detection; Local transcription plus speaker/decision extraction; A private notes destination and retention/erase controls

### "“Make my pendant a physical privacy key: when I tap it near my Mac, unlock my private AI session and browser workspace; when I tap again or walk away, freeze the session, mute capture, and hide sensitive tabs.”"
- **useful because:** The owner gets an unmistakable physical boundary between private and shared computer use instead of trusting a forgotten browser tab or software toggle. The pendant is something they already carry and can use without finding a menu.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic firmware and local policy engine; no model call is needed except optional natural-language status.
- **latency:** Unlock or lock in under 1 second while connected by USB/BLE; offline lock must happen locally.
- **cost:** Near-zero per-use API cost. Hardware cost is approximately $5–$15 for a secure element and proximity radio in a product revision.
- **security:** Use a hardware-backed key and rotating challenge-response, never transmit the owner’s identity as plain text, and make lock local and fail-closed. Require explicit enrollment and provide a physical emergency lock gesture.
- **missing:** Secure element and proximity transport on the pendant; Mac login/session-lock integration; Browser extension commands to hide or suspend sensitive tabs; A signed policy binding one pendant to one Mac account

### "“If I hold the pendant button for five seconds, start a private safety check-in: tell me whether my Mac, relay, and wearable are reachable, and if I do not cancel within a minute, send my chosen contact a prewritten message with my last known location and status.”"
- **useful because:** A worn button is useful when the owner cannot safely unlock a phone or speak. It provides a simple escalation path that works across the pendant, Mac, and always-awake relay, while a countdown prevents accidental alerts.
- **path:** pendant → relay-realtime → mac-planner → unified → dashboard
- **model tier:** Deterministic event routing and templates; use a background model only to summarize device status. No realtime model is required.
- **latency:** Local acknowledgement immediately; reachability verdict within 10 seconds; escalation within 60 seconds after the cancel window.
- **cost:** Under $0.05 per check-in excluding carrier messaging; location lookup and outbound SMS/push dominate.
- **security:** Never activate from an ordinary voice phrase. Require physical hold plus visible/haptic confirmation, encrypt contact and location data, expire location history, and require owner setup and periodic test mode. This must clearly state it is not an emergency-services guarantee.
- **missing:** A local pendant long-hold event and cancellation gesture; A relay escalation service with idempotency and delivery receipts; Mac and phone-independent location acquisition, with honest accuracy labels; Owner-managed trusted contacts and a non-production test mode

### "“Create a temporary, least-privilege handoff for this task: give my collaborator only the selected files, links, decision history, and next step, then revoke the link automatically when the task is closed or expires.”"
- **useful because:** The owner can hand work to another person without sending an entire folder, exposing unrelated browser sessions, or forgetting an old share link. The pendant can confirm the exact handoff while the Mac gathers local evidence and the relay enforces expiry.
- **path:** pendant → mac-planner → mac-terminal → browser-extension → relay-realtime → dashboard
- **model tier:** Background model assembles and summarizes the handoff; deterministic policy controls scope, expiration, and revocation. Realtime is used only for spoken confirmation.
- **latency:** Draft in under 60 seconds; owner confirmation by pendant tap; revocation should occur immediately when expiry or closure is observed.
- **cost:** $0.05–$0.30 per handoff depending on document summarization; storage and link delivery are minor.
- **security:** Default to no external sharing until confirmed. Show recipients, exact artifacts, sensitive-field redactions, expiration, and revocation status. Never include passwords, cookies, private browser content, or secrets. Log an immutable but redacted audit receipt.
- **missing:** A scoped artifact manifest joining Mac files, browser citations, and task state; Relay-hosted expiring links with revocation and recipient authentication; Pendant confirmation of the exact manifest hash; Automatic closure signals and verified revocation across cached copies


## Changes it proposed to its own stack

### `integration` — Build a redacted cross-surface recovery drill: a monthly routine fans out health assertions to the browser bridge, Mac agent, relay, and USB-connected pendant, signs each result with timestamp/device identity, stores only pass/fail plus remediation class, and produces a human-readable failure map. Add synthetic test accounts/pages and a pendant loopback challenge so the drill proves the path rather than merely checking process liveness.
- **owner gets:** They learn before an emergency whether the thing they rely on can actually recover, without handing the system their passwords or dumping private content into a report.
- effort: Medium-high: new assertions and a test harness on four surfaces, plus a small redacted report UI.  ·  risk: A false green check could create dangerous confidence; every assertion needs a known limitation and periodic synthetic canary. A failed drill must not mutate accounts or trigger notifications.
- cost: <$0.10 monthly in model/API cost; engineering/storage cost is the main impact.  ·  latency: Runs in background; report generation under a minute after checks complete.
- security: Improves security by proving recovery while minimizing data. Requires strict no-secret logging, encrypted short-retention results, and owner-only access.
- depends on: A cross-surface health-assertion schema; Pendant loopback/self-test over its live USB serial connection; Browser and Mac inspectors that return metadata/booleans, never secret values

### `firmware` — Add a physically bounded conversation-capture state machine to the pendant: double-press starts, double-press ends, long-press aborts and erases the current buffer; LED patterns and a short haptic/audio cue confirm each transition. Persist only an encrypted ring-buffer session id and byte count locally, and emit start/stop/drop events over USB serial so the Mac can reject incomplete recordings.
- **owner gets:** They can deliberately remember a real conversation without an always-on microphone, and they get an immediate, trustworthy signal that recording is or is not active.
- effort: Medium: button debounce/state machine, cues, encrypted metadata, UART events, and serial test coverage.  ·  risk: Accidental capture or missed stop; mitigate with unmistakable cues, a hard maximum duration, automatic expiry, and long-press erase. Hardware audio path currently has packet-loss risk under duplex contention.
- cost: Negligible API cost; under ~10 KB firmware storage and a few KB RAM, no new hardware. Audio transport may increase Mac/bridge bandwidth use.  ·  latency: Tap acknowledgement should be local under 300 ms; no network dependency.
- security: Improves consent and privacy by making capture opt-in and locally abortable; does not itself guarantee legal consent from other participants.
- depends on: Owner-approved recording policy and retention defaults; ESP32 bridge timestamp/drop markers; Mac local transcription and encrypted note storage

### `hardware` — Revise the pendant around a secure-element-backed proximity identity and a distinct emergency control: add a low-power BLE/NFC presence channel, a tamper-resistant key slot, haptic feedback, and a mechanically distinguishable long-hold button path. The firmware should be able to lock privacy and emit an emergency event without a network round trip.
- **owner gets:** The pendant becomes a trustworthy physical boundary and safety control: one tap can protect private work, and one deliberate hold can request help even when the owner cannot operate a screen.
- effort: High: board revision, secure-element provisioning, enclosure/button redesign, firmware state machine, and Mac/relay enrollment flows.  ·  risk: False emergency activation, lost-device exposure, or dependence on a new radio. Mitigate with enrollment revocation, local confirmation, test mode, fail-closed privacy lock, and a hard distinction between lock and escalation gestures.
- cost: Approximately $10–$25 added prototype BOM and a few milliwatts average draw; no per-use model cost.  ·  latency: Privacy lock and emergency event can be local in under 1 second; remote notification still depends on relay/carrier availability.
- security: Substantially improves authentication and privacy, but creates a high-value physical credential that needs revocation and secure provisioning.
- depends on: Signed pendant identity enrollment; Relay event idempotency and delivery receipts; Mac privacy-session integration; Owner-managed trusted contacts and emergency policy


## What it asked for

_Nothing._
