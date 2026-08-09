# Harness derivation — ios-control — round 9

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **ios-local-reachability** — The Mac bridge is online while ios-brain-pairing-probe is offline; therefore iPhone Mirroring capabilities should be implemented and tested as Mac-local capture/event actions, not as an independent network device or LTE path.
  - evidence: devices discovery in Round 9: home-macbook-bridge online; ios-brain-pairing-probe offline. System constraint: Mirroring capture/events are Mac-local.

## Capabilities it proposed

### "“Read whatever is on my iPhone right now, give me the one-sentence gist, and if I say ‘do it,’ carry out the safe next step.”"
- **useful because:** The pendant can turn a glance at a real iPhone screen into a voice conversation and then hand the approved outcome to the Mac/browser. This is the highest-value iOS feature: it bridges a private mobile surface that the relay and browser cannot reach alone.
- **path:** pendant → relay → mac-planner → ios-control → browser-extension
- **model tier:** gpt-5.6-luna for screen interpretation and planning; gpt-4.1-mini for OCR/region extraction; gpt-realtime-2.1 only for the spoken turn
- **latency:** 3–5 seconds to capture and summarize; under 2 seconds for the confirmation handoff; no action if the phone is locked, mirrored pixels are absent, or owner is actively using it
- **cost:** About $0.01–$0.05 per invocation depending on screenshot reasoning; dominant cost is vision context, not OCR or relay transport
- **security:** Screen pixels may contain messages, health, or financial data and must stay local until the owner explicitly asks for relay use; redact password/payment fields, show a short-lived evidence hash, and require pendant confirmation before any send/delete/purchase or external browser action
- **missing:** A first-class iPhone Mirroring inspect/capture tool that returns screenshot plus OCR/accessibility bounds; A relay-owned conversational continuation token tying the capture to the owner’s spoken approval; A safe-action classifier that refuses ambiguous icon-only screens and destructive actions

### "“Put the thing I’m looking at on my iPhone into my Mac workspace, with a link or screenshot and a note saying why I saved it.”"
- **useful because:** It solves the everyday phone-to-computer handoff without hunting for share sheets or retyping URLs. iOS supplies the private current context; Mac and browser make it durable and searchable; the pendant provides the hands-free trigger.
- **path:** pendant → relay → ios-control → mac-planner → browser-extension
- **model tier:** gpt-4.1-mini for OCR/URL extraction and classification, gpt-5.6-luna only when the screen is ambiguous; realtime model only for the request/confirmation
- **latency:** Up to 6 seconds; if URL extraction fails, save a timestamped screenshot and ask one clarification rather than guessing
- **cost:** $0.005–$0.03 per save; screenshot upload and vision extraction dominate, while local file write is negligible
- **security:** Never upload the whole screen by default; crop to the detected content region, remove notification banners and account identifiers, and ask before saving private messages or health screens. Use the owner-approved workspace ~/AI-Pendant-Workspace and avoid silently sharing outward
- **missing:** iOS Mirroring crop/selection capture with stable window coordinates; A local Mac receipt writer that records source time, app, URL, and evidence hash; A privacy redaction pass for notifications and sensitive regions

### "“When my iPhone shows a two-factor code or an urgent notification, tell me what it says through the pendant, but never type or send anything unless I explicitly approve.”"
- **useful because:** It makes the phone a quiet, private notification sensor while the owner’s hands are occupied. The relay can speak the result, the iOS node can inspect the mirrored window, and the Mac/browser can optionally complete a non-destructive next step after approval.
- **path:** ios-control → mac-planner → relay → pendant → browser-extension
- **model tier:** gpt-4.1-mini for bounded OCR and notification classification; gpt-5.6-luna for intent resolution; realtime model for the short spoken alert only
- **latency:** Poll only on an explicit user request or a narrowly scoped temporary watch; alert within 5 seconds of a changed mirrored screen; automatically expire watches after 10 minutes
- **cost:** $0.002–$0.02 per inspection; repeated watches cost mainly screenshot/OCR calls, so local perceptual hashing should suppress unchanged frames
- **security:** OTP codes and notifications are highly sensitive: process locally, do not persist plaintext, never expose them in logs or relay job history, and require explicit approval plus fresh screen evidence for any autofill or submission. Mirroring is unavailable while locked or paused by phone use; report that honestly
- **missing:** A local iOS screen-change watch with perceptual hashing and bounded OCR; Ephemeral encrypted notification delivery to the pendant; A strict OTP data-loss-prevention policy and approval gate before browser autofill

### "“Ask me for Face ID on my iPhone before you release this sensitive action, then finish it on the Mac.”"
- **useful because:** The owner gets a physical, device-bound approval for high-risk actions without speaking a password or exposing a secret to the relay. The iPhone supplies biometric presence, the relay holds the pending intent, and the Mac/browser executes only the exact approved action.
- **path:** pendant → relay → ios-control → mac-planner → browser-extension
- **model tier:** gpt-5.6-luna for intent binding and action review; gpt-4.1-mini for deterministic receipt validation; realtime only for the short approval conversation
- **latency:** 15 seconds for the owner to review and authenticate; action starts within 2 seconds of a valid device-bound receipt
- **cost:** $0.01–$0.04 per approval; cryptographic verification and local iOS work dominate neither cost nor latency
- **security:** Never treat a mirrored tap or spoken ‘yes’ as biometric proof. The iPhone must create a signed, single-use approval bound to the exact normalized action, target, and expiry; no raw biometric data leaves the phone. Destructive or financial actions still require a plain-language summary before Face ID.
- **missing:** A small iOS companion app or system-level approval surface capable of signing a Face ID-gated nonce; Relay support for action-bound approval receipts and replay protection; Mac/browser executors that verify the receipt immediately before committing

### "“Turn my iPhone into a temporary camera for this question, describe what it sees through the pendant, and delete the image when you’re done.”"
- **useful because:** The pendant has no independent visual reach, while the owner’s phone is already the camera they carry. This creates an on-demand visual sense for labels, objects, forms, and surroundings, with the relay speaking the answer and the Mac taking an optional follow-up action.
- **path:** pendant → relay → ios-control → mac-planner
- **model tier:** gpt-4.1-mini for local image description and OCR; gpt-5.6-luna only for ambiguous reasoning; realtime for the spoken answer
- **latency:** 2–6 seconds from capture to answer; camera session expires after one request or 60 seconds
- **cost:** $0.01–$0.08 per request depending on image resolution and reasoning; image tokens dominate
- **security:** Default to on-device processing, no gallery persistence, visible camera indicator, explicit start/stop, and automatic deletion. Never inspect people, screens, or documents continuously without a fresh owner request; redact faces and sensitive text before any relay upload.
- **missing:** An iOS companion app with an explicit camera session and local capture API; On-device redaction/deletion guarantees and a signed deletion receipt; A relay image-input path and Mac handoff for optional actions

### "“When I’m on a phone call, give me a private pendant-side running brief of what matters, and after I hang up make the draft follow-up on my Mac without sending it.”"
- **useful because:** It turns an inaccessible mobile call into an actionable, hands-free workflow: iPhone captures/transcribes locally, the pendant provides discreet summaries on demand, and the Mac turns the agreed points into a draft. The owner never has to switch surfaces or lose the thread.
- **path:** ios-control → pendant → relay → mac-planner → browser-extension
- **model tier:** On-device iOS speech recognition for the transcript; gpt-4.1-mini for rolling extraction; gpt-5.6-luna for the final structured follow-up; realtime only for requested spoken summaries
- **latency:** Under 3 seconds for an on-demand ‘what did I miss?’ summary; final draft within 10 seconds after hang-up
- **cost:** $0.02–$0.10 per call depending on transcript length; local transcription avoids most network cost
- **security:** Calls are extremely sensitive: default to on-device transcription, no cloud transcript retention, visible recording consent state, per-contact allowlist, and no automatic recording where unlawful. Draft only; sending always needs explicit confirmation.
- **missing:** An iOS call/audio integration with lawful recording and local transcription controls; An ephemeral encrypted transcript stream to the relay and post-call Mac handoff; A retention policy and consent UX for all call participants


## Changes it proposed to its own stack

### `mac-harness` — Make iPhone Mirroring a first-class local leaf node with a signed, ephemeral capture lease: ios-control requests a named capture (screen/window id, crop, OCR/accessibility, timestamp, privacy labels), mac-planner returns a receipt and pauses all mutation until a relay approval nonce arrives. Relay routes the nonce and final result directly to the owner’s pendant, while the Mac remains the only process that touches pixels/events.
- **owner gets:** The owner can ask the pendant about the exact iPhone screen in front of them and safely continue on Mac or Safari without pretending the iPhone is independently reachable. It remains honest when the phone is locked, on another Space, or mirroring has paused.
- effort: Medium-high: define capture lease/nonce protocol, local OCR/crop service, relay correlation, and explicit frontmost-window checks; then test pause/resume and owner phone pickup.  ·  risk: Stale screen could cause wrong action; mitigate with short TTL, screen hash immediately before mutation, foreground requirement, and refusal on changed evidence. Recovery is a new capture, never blind retry.
- cost: No hardware cost; roughly $0.005–$0.03 per vision interpretation, with local OCR and hashes cheap.  ·  latency: Adds ~200–500 ms for lease and evidence verification; avoids long blind retries and should complete in 3–5 s for a read.
- security: Pixels remain on Mac by default; relay receives only redacted crop/summary unless owner asks otherwise. Nonces prevent replay and approval is scoped to one screen hash and one action.
- depends on: An ios_mirroring_inspect tool or equivalent local capture endpoint; Relay support for ephemeral approval/correlation tokens; A privacy classifier/redactor for notification, OTP, and payment regions


## What it asked for

_Nothing._
