# Harness derivation — mac-planner — round 201

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-vision-readiness** — The live Mac agent now reports Accessibility trusted, Screen Recording granted, synthesized input verified, secure input inactive, browser extension online, relay reachable, and vision loop enabled but visionUploadConsented false.
  - evidence: GET /ops/snapshot HTTP 200 at 2026-08-08T02:57:30Z; GET /observe returned the same host state.

## Capabilities it proposed

### "While the pendant is plugged into my Mac over USB, let me use it as a real offline voice terminal: press the button, speak, have the Mac relay the audio to the cloud, and hear the reply back through the bridge even though LTE is not registered."
- **useful because:** This is the highest-value thing that can be exercised today rather than waiting for cellular pairing. It makes the physically connected nRF9160 and ESP32 useful immediately, gives the owner a dependable desk/USB fallback, and tests the same end-to-end audio and relay path that will later run untethered.
- **path:** pendant → mac-planner → relay → browser → dashboard
- **model tier:** Use the realtime voice model for the duplex conversation; use a cheap background worker only for USB link health, packet accounting, and session receipts.
- **latency:** Button-to-listening-state under 250 ms; audio packets forwarded continuously; first spoken response target under 2 seconds after end of utterance.
- **cost:** Normal realtime voice-token cost per utterance; USB transport itself is negligible. A diagnostic/health session should use no model calls.
- **security:** The Mac becomes the pendant's trusted transport and can see raw audio. Pair the serial identities, show an explicit connected LED state, encrypt or discard buffered audio, and ensure a disconnect cannot cause stale audio to be replayed into a later session. No microphone should be opened on the Mac by this planner.
- **missing:** A live serial exchange capability for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A USB transport adapter that converts pendant frames into the existing relay pipeline protocol and routes downlink PCM back to the bridge; A pairing/session handshake that distinguishes this USB pendant from arbitrary serial devices; A small dashboard status view showing serial link, packet loss, and audio direction

### "When I trigger the pendant audio diagnostic over USB, automatically run the full test, collect the pendant and bridge counters plus relay and Mac pipeline telemetry, and hand me one pass/fail report with the failing stage identified."
- **useful because:** Audio failures currently require correlating several logs by hand. A single physical diagnostic trigger would make a broken microphone, serial link, Opus decode, relay stream, or speaker path distinguishable before a real conversation is affected.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** No realtime model is needed for collection; use deterministic checks and a cheap background model only to phrase the final report if desired.
- **latency:** Arm over USB in under 1 second; complete the fixed fixture in under 30 seconds; report immediately after all counters arrive.
- **cost:** Near-zero model cost for deterministic reports; storage is a few KB per run. Optional natural-language explanation costs less than $0.01.
- **security:** The fixture must contain synthetic audio only and must prove that microphone content is not stored. Keep raw serial logs local by default, upload only counters and hashes, and make report retention bounded.
- **missing:** A serial command/response transport between the Mac and both connected chips; A collector that aligns pendant sequence numbers, bridge events, /pipeline telemetry, and Mac timestamps; A deterministic acceptance evaluator for alias rejection, decode/encode duration, drops, underruns, and fixture completion; A dashboard report and downloadable receipt for each diagnostic run

### "When a website asks me to confirm a sensitive action, let the browser show a short challenge, speak the exact consequence through the pendant, and let a physical button press authorize only that one transaction on the authenticated Mac session."
- **useful because:** Today the browser, Mac, relay, and pendant can each reach pieces of this, but there is no trustworthy physical approval channel binding the owner's body to one exact browser action. This would make it possible to approve a purchase, send, publish, or permission grant without leaving the authenticated session exposed to unattended automation.
- **path:** pendant → browser → mac-planner → relay → dashboard
- **model tier:** Use deterministic parsing and policy checks for the challenge; use realtime only to read an already-generated short explanation if the owner asks a follow-up. No model should decide whether the action is allowed.
- **latency:** Challenge creation under 500 ms; spoken summary under 2 seconds; button approval expires after 30 seconds and executes once.
- **cost:** Near-zero model cost when the page supplies structured action metadata; under $0.01 when summarization is needed. The dominant cost is browser integration and secure protocol work.
- **security:** A stolen browser session or replayed button event must not authorize anything. Bind the challenge to origin, tab, action hash, session nonce, and expiry; show the origin and consequence audibly; reject navigation or DOM changes after signing; retain a tamper-evident receipt without storing page secrets.
- **missing:** A browser extension protocol for extracting a canonical action description and pausing exactly one submission; A relay-issued nonce and challenge signature shared among pendant, browser, and Mac; Firmware support for a one-shot approval event distinct from ordinary bookmarking or recording; A Mac executor path that verifies the signed action hash immediately before submission; Owner policy entries defining which action classes may use physical approval

### "Let me say “make this a private work session” and have the pendant, relay, Mac, and browser coordinate a temporary privacy boundary: stop audio capture after the command, suppress nonessential notifications, pause browser observation, and automatically restore the prior state when I end the session."
- **useful because:** The existing privacy and alert mechanisms act on isolated surfaces. This would give the owner one dependable mode that actually covers the whole hive during a confidential conversation, instead of remembering which Mac, browser, relay, and pendant switches were changed.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use deterministic state transitions and a cheap background reconciler; realtime is only needed to understand the spoken mode command and confirm status.
- **latency:** All surfaces acknowledge entry within 1 second; restoration completes within 2 seconds of the end command or a bounded timeout.
- **cost:** Under $0.01 per transition; most work is state coordination and crash recovery, not inference.
- **security:** A dropped link must fail closed for capture and observation, while never leaving the owner unable to exit locally. Store only mode state and prior settings, encrypt the coordination record, and show a clear local LED/state indicator. Never infer privacy from calendar titles alone.
- **missing:** A cross-surface lease with monotonic generation, expiry, and crash-safe restoration; Relay commands to the existing pendant privacy latch and alert inbox, plus browser observation pause/resume; Mac hooks that suspend screenshot/browser polling and notification-affecting routines without killing unrelated apps; A local exit path on the pendant that works offline and a reconciliation routine for stale leases


## Changes it proposed to its own stack

### `mac-harness` — Enable the already-configured vision computer-use loop for the AI Pendant Agent, with an explicit runtime toggle and redacted screenshot pipeline: capture the foreground window only when a delegated task needs visual grounding, send the minimum crop to the vision model, and attach the resulting action/observation pair to the Mac job receipt.
- **owner gets:** The Mac currently reports Accessibility and Screen Recording both granted, UI events reaching the screen, and the vision loop enabled, but visionUploadConsented is false. Turning this on would let the agent recover from unfamiliar layouts instead of guessing coordinates or abandoning tasks, while keeping ordinary text/API tasks screenshot-free.
- effort: Medium: wire the consent setting into the existing computer-use loop, add crop/redaction rules and a per-job toggle, then test Safari, Finder, and a login page without submitting credentials.  ·  risk: Screenshots can expose private documents, messages, or authenticated pages; stale visual context can cause a wrong click. Recover by defaulting to no capture, recording the exact screenshot hash and action in the receipt, stopping on confidence loss, and never treating a screenshot as authorization to submit or purchase.
- cost: Vision inference adds roughly $0.01–$0.10 per visually grounded step depending on image size and model; no hardware cost.  ·  latency: Adds roughly 1–3 seconds per visual observation. Text/API paths are unchanged.
- security: High sensitivity: screenshots leave the Mac only for opted-in jobs. Redact password fields and known sensitive regions, enforce a short retention window, and expose a visible active-capture indicator.
- depends on: Owner must explicitly enable visionUploadConsented for the AI Pendant Agent; Use the existing accessibility/screen-recording grants and computer-use loop rather than requesting permissions again; Add a policy entry that names which delegated jobs may capture screenshots

### `hardware` — Add a small secure-element-backed companion board to the pendant or its USB dock, with a physical approval button and one monochrome status display that can show origin, action class, and expiry for a signed browser/Mac challenge.
- **owner gets:** The owner would be able to approve a sensitive action while looking at a trustworthy local display rather than trusting an audio-only summary or a browser page that automation may have altered. It also makes the pendant's state legible when the Mac is asleep or the browser is not foregrounded.
- effort: High: board revision, secure-element provisioning, display and button firmware, USB protocol changes, relay challenge binding, and a full replay/tamper test suite.  ·  risk: A display can be spoofed by a compromised host if its contents are not signed; a new button can be pressed accidentally; added hardware increases failure points and size. Recover with signed short labels, nonce-bound approvals, expiry, deliberate press timing, and fallback to deny when verification fails.
- cost: Roughly $8–$20 in components and assembly per unit, with tens of milliwatts while displaying and near-zero when asleep; secure-element provisioning is the larger operational cost.  ·  latency: Adds under 300 ms for challenge rendering and button confirmation; no effect on ordinary audio when asleep.
- security: Improves physical authorization only if the secure element protects the device key and the display receives the signed challenge directly. Requires key rotation, revocation, and a lost-device recovery procedure.
- depends on: A signed cross-surface challenge protocol between relay, browser, Mac, and pendant; A typed one-shot approval event in pendant firmware; The owner choosing which action classes may be physically approved; The existing serial/USB transport and browser bridge must carry challenge metadata


## What it asked for

_Nothing._
