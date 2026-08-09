# Harness derivation — faculty-action — round 256

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do the thing I just approved, and tell me whether it actually happened.” The system should stage a Mac/browser action, require one deliberate pendant confirmation, execute it, independently verify the postcondition, and give me a truthful haptic result or a retry/cancel state."
- **useful because:** This is the core promise: the pendant is the owner's physical consent, the Mac/browser are the hands, and perception—not an executor receipt—decides whether the world changed. It prevents silent false success for messages, files, and web forms.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use realtime only to interpret the immediate spoken request and render a concise status; use the cheaper background/local planner for action decomposition and faculty-perception for verification.
- **latency:** Stage in under 2 s; confirmation feedback under 300 ms; execute and verify within 10 s for ordinary actions, with an explicit pending state for slower work.
- **cost:** One realtime turn plus one cheap planning/verifier turn; roughly 1–3¢ depending on model and screenshot/evidence size. Mac/browser calls dominate latency, not tokens.
- **security:** The pendant receives only an opaque transaction summary/hash, never page secrets or message contents. Expired, consumed, or digest-mismatched approvals refuse. Verification evidence defaults to hash/minimal snippet and private content stays local; irreversible actions remain approval-gated.
- **missing:** A production orchestration route that joins prepare/approve, POST /execute or browser commands, verify_operation_step, and tactile_action_outcome_beacon under one operation ID; A compact action/attempt correlation field on verify_operation_step; Owner policy data selecting which risk classes may be staged versus require confirmation

### "“If I’m walking, driving, or my hand is moving, don’t let a risky action go through—tell me why and let me confirm later.” The pendant should classify motion locally, have the relay gate high-impact actions, and resume them only after a stillness window and deliberate confirmation."
- **useful because:** A spoken approval while moving is easy to issue accidentally or misunderstand. The owned LSM6DSOX can make physical consent meaningfully safer without opening a microphone or sending raw motion data; the Mac and browser can hold the action until conditions are safe.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** No model for the first gate: firmware feature extraction and a deterministic relay policy. Use a cheap background model only to explain the hold in natural language; realtime is unnecessary.
- **latency:** Local motion classification under 100 ms; relay decision under 500 ms; resume after a configurable 2–5 s stillness window.
- **cost:** Near-zero inference cost; a few relay events and one optional cheap explanation. Hardware already owned; engineering is firmware integration and policy plumbing.
- **security:** Transmit coarse state (still/moving/impact/unknown), not accelerometer traces or location. Unknown must conservatively hold high-risk actions. Never infer driving or identity as a fact; present “motion safety hold.” A physical confirmation remains required after the hold.
- **missing:** Firmware integration enabling i2c2 and LSM6DSOX sampling; A signed motion-state envelope with freshness and monotonic sequence; A policy-router hook that can pause/resume an operation without losing its approval expiry; A small dashboard control for motion-gate policy

### "“Give me a private, glance-free inbox on my pendant: tell me that a reply, reminder, or action result is waiting, let me rotate through compact summaries, and only speak the selected item when I ask.”"
- **useful because:** The pendant can notify without exposing message content in public or requiring a phone screen. The relay owns durable inbox delivery, the Mac/browser supply authenticated events, and the wheel/second button can provide selection once the product input exists.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use background models to summarize incoming items into bounded, redacted cards; realtime only when the owner explicitly asks to hear one. Deterministic firmware handles queueing, expiry, and selection.
- **latency:** Notification haptic under 1 s after an event reaches relay; selection feedback under 150 ms; spoken expansion under 2 s.
- **cost:** Usually fractions of a cent per event with a small background summary; realtime cost only on explicit expansion. Storage is compact metadata, not audio by default.
- **security:** Pendant stores opaque IDs, risk/category, expiry, and redacted summaries—not full message bodies, credentials, or page contents. Sensitive cards require physical confirmation before audio. Queue is bounded and encrypted where available; expired cards are discarded and acknowledged idempotently.
- **missing:** Rotary encoder and second product button integration (the bench currently has two DK buttons but no wheel); An INBOX typed-item schema extending the existing pendant_store manifest; Relay delivery/ack routes for compact cards and a redacted-summary policy; A firmware haptic/menu state machine

### "“Use my logged-in browser and Mac, but never send the contents of private apps or sensitive form fields to the relay or a model. If a task crosses a privacy boundary, pause and ask me on the pendant.”"
- **useful because:** Today the system can act through authenticated sessions, but the owner cannot express a trustworthy boundary between local execution and cloud reasoning. A local privacy firewall would make banking, health, work, and private messages usable without turning the relay into a copy of the screen.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Local deterministic classifiers and browser field metadata decide the first boundary; a cheap background model may summarize only already-redacted labels. Realtime handles only the owner's spoken request and never receives blocked content.
- **latency:** Classification under 100 ms per field/app transition; a boundary prompt under 1 s; blocked actions remain paused until explicit physical confirmation.
- **cost:** Low ongoing inference cost; primarily local classification and a few signed policy events. Engineering cost is in browser/Mac interception and policy testing.
- **security:** Default-deny for secrets, password/OTP/payment fields, and configured private apps. Relay receives opaque field IDs and hashes, never values or screenshots. The owner can inspect and revoke rules; emergency bypass requires a deliberate pendant gesture and is visibly logged.
- **missing:** A local preflight/redaction layer for Mac and browser actions; Sensitive-field/app taxonomy with owner-editable rules; A protocol for redacted action plans and hash-only verification; Dashboard audit view showing what was withheld

### "“If my Mac goes to sleep, loses the browser, or I walk away, keep the task safe and pick it up exactly where it stopped—without repeating a send or purchase.”"
- **useful because:** Current execution receipts do not give the owner a durable, truthful continuation point across sleep, login, browser loss, and relay reconnect. A resumable transaction journal would turn a fragile multi-step task into a bounded workflow with explicit pause, expiry, and recovery rather than duplicate side effects.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic state-machine logic for checkpoints, idempotency, and expiry; use a cheaper model only to explain the recovery state. Realtime is not needed unless the owner asks what is waiting.
- **latency:** Persist a checkpoint before each side-effect; recovery notice within 2 s of reconnect; resume only after fresh presence and postcondition verification.
- **cost:** Minimal model cost; durable journal storage and Mac/browser round trips dominate. One cheap explanation is optional.
- **security:** Every side-effect step needs an idempotency key and an independently verified postcondition. Expired or ambiguous steps stop rather than retry. The journal stores hashes and action class, not secrets or page contents; pending high-risk work requires renewed physical approval.
- **missing:** A durable cross-surface transaction journal with step idempotency keys; A real wake/unlock/presence signal rather than assuming bridge online means owner present; Executor checkpoint hooks before and after side effects; Recovery UX for pendant and dashboard

### "“When I say ‘save this for later’ during a conversation, capture the exact moment and enough local context that I can find it again by asking the pendant—not just a raw audio file.”"
- **useful because:** A bookmark today is a point event, while useful recall needs the linked voice segment, timestamp, active Mac/browser context, and a searchable, privacy-aware index. The worn button knows the moment; the Mac knows what was in front of the owner; the relay makes it durable and the pendant retrieves it hands-free.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Firmware emits a compact bookmark; background processing on the Mac creates transcript/topic/context links and embeddings locally or from redacted text. Realtime is used only when the owner asks for a spoken recall.
- **latency:** Bookmark acknowledgement under 200 ms; local context snapshot under 1 s; searchable indexing within 30 s; spoken retrieval under 2 s.
- **cost:** Low per bookmark if indexing is local; storage and optional embedding generation dominate. No cloud audio upload unless the existing failure-path policy permits it.
- **security:** Capture only on deliberate sw1 event; make app/context sensitivity explicit and redact private windows. Store opaque links on the pendant, retain audio under existing failure-path rules, and require physical selection before speaking sensitive recall.
- **missing:** A cross-surface bookmark envelope linking pendant monotonic time to Mac/browser observation; Local context snapshot and searchable index; A retrieval route that joins bookmark, transcript, and verified app/browser context; A privacy/redaction policy for captured context


## Changes it proposed to its own stack

### `firmware` — Integrate the owned LSM6DSOX on i2c2 as a low-rate local safety classifier: sample accelerometer/gyro, derive still/moving/impact/unknown with hysteresis, sign a compact sequence-numbered state envelope, and never export raw motion vectors. Add a safe default that high-risk approvals pause on unknown or motion.
- **owner gets:** The pendant can prevent an accidental send or purchase while the owner's hand is in motion, without recording or transmitting their movements.
- effort: Moderate firmware work: enable i2c2, driver/config, bounded classifier, signing/sequence plumbing, and bench tests; no new hardware.  ·  risk: False motion holds could delay an urgent action; false stillness could weaken the gate. Recover by defaulting unknown to hold, showing a distinct haptic pattern, and allowing explicit later retry. Sensor/I2C faults must not brick recording/audio.
- cost: No API inference cost; existing sensor and negligible incremental power at low duty cycle. Engineering and test cost only.  ·  latency: Under 100 ms local classification; negligible impact to 24 kHz audio if sampling is scheduled outside codec-critical work.
- security: Improves consent safety while reducing data exposure: only coarse signed state leaves the pendant; no location or raw IMU stream.
- depends on: A relay policy hook for motion holds; Signed state envelope verification on relay; Owner-configurable risk policy

### `interaction` — Define an INBOX card protocol over the existing typed pendant store: opaque card ID, category, expiry, sensitivity, redacted summary, checksum, replay/ack state, and optional audio artifact ID. Add rotary selection and second-button actions (next, hear, dismiss) while preserving the current sw0 recording and sw1 bookmark semantics until the product controls exist.
- **owner gets:** Important replies and action outcomes become privately discoverable through a vibration and a small physical control, instead of requiring the owner to unlock a phone or expose message content aloud.
- effort: Moderate integration across relay, firmware, and Mac/browser event adapters; rotary hardware and enclosure integration are still needed.  ·  risk: A summary could leak sensitive information or a queue could become noisy. Mitigate with redaction tiers, bounded queue/expiry, sensitivity-specific haptics, and explicit physical selection before speech.
- cost: Low ongoing model cost if summaries are generated in background; compact metadata uses little flash/SD and no extra audio unless requested.  ·  latency: Sub-second haptic delivery when online; local selection under 150 ms.
- security: Keep full content off the pendant by default; encrypt/authenticate cards and make acknowledgements idempotent.
- depends on: Rotary encoder and product second button; INBOX schema amendment to existing pendant_store; Relay card delivery and acknowledgement routes


## What it asked for

_Nothing._
## Its own summary

Round 256 produced three recorded capabilities: (1) a cross-surface trustworthy action loop where pendant consent, Mac/browser execution, independent postcondition verification, and haptic outcome form one operation; (2) a local LSM6DSOX motion-safety hold for consequential actions; (3) a private typed inbox of redacted cards selectable with the future wheel/button. I also recorded firmware and interaction changes. Live discovery now shows Accessibility and Screen Recording granted, Mac input reachable, Safari bridge online with zero pending commands, but the nrf9160 pendant still offline. /observe confirms the Mac is currently at loginwindow, so host presence is not equivalent to an unlocked user session.

**Biggest unknown:** The actual operation orchestration contract is still unclear: /prepare, /approve, and /execute appear in the inventory, but describing them yielded 404 GET responses, so I still need a working, documented POST contract that can correlate approval, execution, verification, and outcome. Separately, the motion gate needs i2c2 firmware integration and the product still needs a rotary encoder/second button. I do not need Accessibility permission anymore; that grant is now live.

