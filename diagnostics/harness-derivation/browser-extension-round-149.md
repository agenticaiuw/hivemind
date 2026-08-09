# Harness derivation — browser-extension — round 149

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before you submit this checkout, application, or message, read me exactly what will be sent from the logged-in browser, point out unusual fields or totals, and let the pendant button approve or cancel.”"
- **useful because:** The browser is the only node with authenticated sessions, while the pendant is the only trustworthy physical presence signal. This turns risky web actions into an understandable, auditable handoff without exposing credentials or requiring the owner to return to the screen.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model for field normalization and anomaly comparison; use realtime only for the short spoken preview and approval dialogue. The browser performs no submit until an explicit pendant approval token arrives.
- **latency:** Preview in 2–4 seconds after the form is ready; approval-to-submit under 1 second. A stale preview (page mutation, timeout, navigation) must invalidate approval and regenerate.
- **cost:** Usually <$0.01 per preview; dominated by sending a compact field manifest, not page HTML. No model call is needed for ordinary low-risk forms if deterministic diffing finds no anomalies.
- **security:** Never persist raw page text or secrets; redact passwords, tokens, payment numbers, and hidden fields before leaving the Mac. Speak only a field summary and destination origin. Show the exact outbound values and irreversible consequence; owner policy explicitly stops before submit. Missing: a browser action that extracts a typed form manifest and computes a mutation fingerprint, a relay approval-token route bound to command+origin+fingerprint, and firmware mapping the existing physical button to one-time approve/cancel while preserving offline alert behavior.
- **missing:** browser form-manifest extraction with secret redaction; origin/form fingerprint and stale-preview invalidation; pendant approval/cancel protocol; relay approval token bound to browser command

### "“When I’m on a logged-in dashboard, tell me what changed since the last time I looked, and alert me only if the change needs me to act.”"
- **useful because:** A page can change without email or a notification, and only the browser can see behind the owner’s login. Hashing a redacted semantic snapshot lets the always-awake relay detect meaningful changes while the pendant delivers a short alert even when the Mac link later disappears.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception → faculty-judgement
- **model tier:** Cheap scheduled/background model (or deterministic DOM diff first) classifies changed regions and urgency; realtime is used only when the owner asks for the explanation. The relay retains hashes and compact extracted facts, not page bodies.
- **latency:** Poll only during owner-configured windows, with a 1–5 minute interval; alert generation under 10 seconds of a detected change. Stop polling on logout, tab close, or heartbeat loss.
- **cost:** <$0.02 per changed page per day with deterministic diffing; model cost is only for novel/ambiguous changes. Dominant cost is authenticated page extraction, not speech.
- **security:** Per-origin rules must be supplied by the owner and start empty; redact secrets and categories marked never-store before hashing or speaking. The alert must include origin and timestamp so it cannot be mistaken for current state. Missing: durable browser watch definitions, semantic redaction-before-diff, relay scheduling, and a compact alert payload delivered to the already accepted offline_alert_inbox.
- **missing:** owner-configured per-origin watch definitions; redacted semantic snapshot/delta engine; relay scheduler and deduplication; browser logout/session-expiry detection

### "“Turn the deadline, appointment, or renewal date on the page I’m viewing into a reminder, and include the exact source and what I need to do.”"
- **useful because:** The browser can see dates hidden behind login; the Mac can create a durable reminder; the pendant can immediately read back the extracted date and let the owner correct ambiguity. This prevents missed renewals without storing the private page itself.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic date/entity extraction first; use a cheap background model only when the page has multiple candidate dates. Realtime speaks the proposed reminder and asks one concise correction question.
- **latency:** Extract and present a reminder proposal within 3 seconds; creation after owner’s spoken/button confirmation within 1 second. If timezone or date is ambiguous, do not silently create it.
- **cost:** <$0.005 for ordinary pages; model cost only for ambiguity. Mac reminder creation and browser read dominate latency, not inference.
- **security:** Persist only title, date, action, origin, and a short quoted citation selected after redaction; never retain full page text or account identifiers. Browser session data remains in Safari. Missing: a browser extraction contract that returns candidate dates with DOM citations, an ambiguity-aware reminder intent, and a correction/confirmation path from pendant to Mac action.
- **missing:** candidate date extraction with source locators; timezone/ambiguity resolver; pendant correction and confirmation event; reminder provenance field and expiry policy

### "“What is this number, warning, or button I’m looking at?”"
- **useful because:** Text extraction alone loses layout and meaning. A browser selection or current focus can be sent with a tightly cropped screenshot to Mac vision, while the pendant supplies the question and receives a concise answer. This is the only way to interrogate authenticated charts, canvases, and visually encoded warnings without handing the page to a public service.
- **path:** pendant → relay-realtime → browser-extension → mac-vision → mac-planner → faculty-perception
- **model tier:** Use local Mac vision for the crop and DOM/accessibility metadata; realtime handles only the spoken question and answer. Escalate to an expensive model only when local vision confidence is low.
- **latency:** Answer in under 4 seconds for DOM text/accessibility data and under 8 seconds for a screenshot crop. The extension should return immediately with an acknowledgment if capture is slow.
- **cost:** Near-zero API cost for DOM/accessibility queries; <$0.02 for occasional local/remote vision fallback. Bandwidth is bounded by a small crop, never the whole tab.
- **security:** Keep capture local to the Mac by default, redact password/payment fields and cross-origin frames, and disclose the page origin in the spoken answer. Do not save screenshots after the answer. Missing: a browser action for focused-element/selection plus screenshot crop, a low-latency Mac-vision endpoint accepting that evidence, and a pendant utterance correlation ID.
- **missing:** focused element and selection capture; cropped screenshot plus DOM/accessibility bundle; Mac vision question endpoint; ephemeral evidence deletion and confidence response

### "“If I lose my Mac or browser connection, preserve the exact place I was in each important authenticated page and restore it on another trusted device without copying the page contents to the relay.”"
- **useful because:** Today an authenticated browser session is stranded in Safari: the wearable can ask about it only while that exact tab and Mac are alive. A privacy-preserving continuation token would let the owner resume a form, document, or dashboard at the same section after a crash or device handoff, without exposing page text or credentials to the cloud.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception
- **model tier:** No expensive realtime model is needed for capture or restore. Use deterministic browser/session logic; use a cheap model only to label a human-readable location such as heading and step number.
- **latency:** Checkpoint in under 500 ms on navigation/focus changes; restoration under 3 seconds after a trusted browser reconnect. If the origin rejects restoration or the session expired, report that plainly rather than guessing.
- **cost:** Negligible API cost; storage is a few hundred bytes per checkpoint. Engineering cost is in secure device binding and origin-specific restoration adapters.
- **security:** Store only origin, tab identity, URL fragment where safe, scroll/focus coordinates, and a salted content hash; never store cookies, form values, screenshots, or page text. Encrypt and bind the token to the owner’s registered devices, expire it quickly, and invalidate on logout. Missing: encrypted continuation-token storage, extension checkpoint events, trusted-device handoff, and per-origin restoration support.
- **missing:** encrypted device-bound continuation tokens; extension navigation/focus checkpoint events; trusted-device handoff protocol; origin-specific restoration adapters

### "“When I press and hold the pendant, immediately make every browser session private: stop page polling, mute spoken output, clear transient captures, and tell me when it is safe again.”"
- **useful because:** The owner may enter a sensitive room or lose control of the Mac while authenticated tabs are open. A physical, offline-capable privacy action is faster and more reliable than finding Safari controls or speaking a command that could itself be overheard.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → faculty-action
- **model tier:** Firmware and local Mac logic only; no model call. The relay records only an opaque privacy-state transition and resumes ordinary work after an explicit release.
- **latency:** Local mute and capture stop within 200 ms; Safari polling cancellation within 1 second. The pendant must work even when the relay is unreachable, with a visible LED state.
- **cost:** No per-use API cost. Small firmware and extension protocol change; the expensive part is reliably cancelling in-flight browser commands and proving transient buffers were discarded.
- **security:** The action must be fail-closed: no new browser command, page extraction, audio playback, or relay speech while latched. Do not claim deletion until the Mac acknowledges cancellation and buffer shredding. Missing: a pendant privacy latch, browser poll suppression/command cancellation, relay privacy-state propagation, and an auditable local wipe receipt.
- **missing:** offline pendant privacy latch; extension command cancellation and poll suppression; relay-wide speech/capture mute state; verifiable transient-buffer wipe receipt

### "“If a logged-in site needs me to re-authenticate, approve a sign-in, or solve a challenge, alert me on the pendant, pause exactly where I was, and continue only after I finish it.”"
- **useful because:** Authenticated automation silently fails when a session expires or an approval challenge appears. The browser can detect the challenge, the pendant can reach the owner away from the screen, and the Mac can resume the original task without asking the cloud to handle credentials or challenge answers.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception → faculty-action
- **model tier:** Deterministic browser challenge detection and local state machine; realtime is used only to explain which origin needs attention. Never send challenge contents to a model. A cheap classifier may distinguish a login page from an ordinary navigation using DOM metadata only.
- **latency:** Detect within 1 second of navigation and alert within 3 seconds. Resume within 2 seconds after the extension reports successful authentication, with the original task’s state revalidated first.
- **cost:** Near-zero model cost; browser polling and local state persistence dominate. Optional speech is a few cents per extended interaction at most.
- **security:** Do not capture, persist, or transmit passwords, OTPs, security keys, CAPTCHA images, or challenge answers. Bind the pause/resume state to origin, tab, and a content hash; invalidate it if the page or intended action changes. Missing: challenge detectors, an encrypted paused-task state, pendant notification metadata, and a local resume handshake.
- **missing:** origin-aware login/MFA/challenge detection; encrypted paused-task state; pendant challenge notification payload; post-authentication state revalidation and resume handshake


## What it asked for

_Nothing._
