# Harness derivation — ios-control — round 10

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Take the address/confirmation code/order number currently visible on my iPhone and put it into the right form on my Mac, but show me exactly what you extracted before submitting.”"
- **useful because:** This turns the phone and Mac into one useful workspace: no retyping from a handheld screen, while an explicit preview prevents OCR mistakes or leaking a code into the wrong field. It requires iPhone Mirroring capture/OCR, relay conversation, Mac/browser session selection, and a confirmation boundary.
- **path:** pendant → relay → mac-bridge → iOS → browser → dashboard
- **model tier:** realtime for the short voice exchange and confirmation; gpt-5.6-luna background/local planner for OCR normalization, field matching, and browser execution
- **latency:** 2–4 s to capture and speak the extracted preview; after approval, 1–3 s to fill the selected form and report success
- **cost:** One realtime turn plus a small local vision/OCR pass; roughly $0.01–$0.05 per invocation, dominated by realtime audio/context, not the browser action
- **security:** Phone screenshot and extracted text cross the Mac/relay boundary; default to local OCR, redact likely OTP/payment values in logs, require spoken or pendant-button confirmation before typing or submitting, and never auto-submit. Abort if mirroring is paused, the Mac is locked, or the target field is ambiguous.
- **missing:** ios_mirroring_inspect read surface with app/window identity and OCR; a relay-to-Mac signed handoff carrying a short-lived extracted payload; field-target preview in the browser harness; confirmation state that binds approval to the exact extracted value and target

### "“Watch my iPhone while it is mirrored and tell me, through the pendant, only when an important notification arrives—read the sender and first sentence, and let me say ‘mute’, ‘open’, or ‘reply’.”"
- **useful because:** The owner can keep the phone in a pocket or on a desk without missing a genuinely urgent message, while avoiding a constant notification stream. The iOS node observes screen changes, the relay applies an owner-defined urgency policy, and the Mac/browser surface performs an approved open/reply.
- **path:** iOS → mac-bridge → relay → pendant → browser → dashboard
- **model tier:** cheap local change detector plus rules for normal notifications; realtime only for speaking an urgent alert and handling the brief voice command; local planner for opening/replying
- **latency:** Detect and announce within 1–2 s of a mirrored notification; command execution within 3 s after confirmation
- **cost:** Near-zero model cost for pixel/OCR diff and allowlist rules; occasional realtime turn, under $0.01 per alert in normal use
- **security:** Notifications can contain private health, financial, or message content. Keep raw frames local, send only the selected sender/snippet, support per-app and quiet-hour allowlists, never announce on speaker without an explicit audio mode, and require confirmation before replying or opening sensitive apps. Stop monitoring when the phone is picked up or mirroring pauses.
- **missing:** ambient iOS screen-diff/OCR watcher keyed to notification regions; local notification urgency policy and per-app redaction; relay event subscription with deduplication and quiet hours; safe ios open/reply actions that refuse when mirroring is not frontmost; owner-facing policy editor

### "“If my phone is unavailable or I pick it up, queue the exact iPhone action I just approved and finish it when mirroring is usable again—tell me if anything on screen changed instead of guessing.”"
- **useful because:** Today an approved tap/type can be stranded by the normal Mirroring pause, or a planner may be tempted to retry blindly. A durable, revalidated handoff lets the owner continue walking or pick up the phone safely: the relay remembers intent, the Mac waits for frontmost pixels, iOS re-inspects the target, and the pendant asks again if the screen no longer matches.
- **path:** pendant → relay → mac-bridge → iOS → dashboard
- **model tier:** realtime for the initial approval and exception prompt; cheap state machine/local planner for waiting and revalidation; vision model only when the target changed
- **latency:** Immediate acknowledgement; resume within 2 s of Mirroring becoming controllable; changed-screen exception within 3 s
- **cost:** Usually no model call while waiting; one local inspection on resume and an occasional realtime prompt, well under $0.01 per queued action
- **security:** Persist only a signed action description and redacted target metadata, never a password or unrestricted tap coordinate. Bind approval to app, visible text hash, and expiry; require reapproval after any mismatch, phone pickup, lock, or timeout. Provide pendant cancel and automatic expiry.
- **missing:** durable pending iOS action queue in relay/Mac bridge; frontmost/readiness event for Mirroring, not just polling; target fingerprint and revalidation API; pendant cancel/confirm event with action hash; receipt visible in dashboard

### "“When I say ‘I’m starting my meeting with Maya,’ put my iPhone and Mac into the right meeting mode, open the matching meeting link, and keep a private pendant channel for urgent interruptions; when I say ‘meeting over,’ restore everything exactly.”"
- **useful because:** The owner gets a genuinely coordinated mode change instead of separately configuring a phone, computer, browser, and audio device while distracted. It can identify the calendar event, open the authenticated meeting page, silence ordinary phone/Mac interruptions, preserve an allowlist for urgent contacts, and reliably restore the prior state.
- **path:** pendant → relay → iOS → mac-bridge → browser → dashboard
- **model tier:** gpt-5.6-luna for event matching and reversible plan construction; realtime only for the two short spoken commands; deterministic local actions for Focus, volume, browser navigation, and restoration
- **latency:** Acknowledge in under 1 s; complete setup in 5–8 s; restoration in under 5 s
- **cost:** Usually one small planner turn plus local actions, approximately $0.01–$0.04; no ongoing inference while the meeting runs
- **security:** Changing notification and communication settings can hide emergencies. Show the exact apps, contacts, and duration before first use; require confirmation for a new policy; preserve and cryptographically bind a pre-change snapshot; never alter emergency bypass settings silently; auto-restore on timeout and provide pendant cancel.
- **missing:** iOS actions for Focus mode, notification policy, and restoration snapshot; calendar-event lookup shared between relay and Mac planner; meeting-mode policy object with urgent-contact allowlist and expiry; browser meeting-link matching across logged-in sessions; transactional multi-surface rollback and a spoken receipt

### "“For anything sensitive—sending a message, buying something, changing a password—stage it on the Mac, show the exact summary on my iPhone, and let me approve or reject it there while the pendant reads me the result.”"
- **useful because:** The iPhone becomes a physically separate, glanceable confirmation surface instead of trusting a noisy voice command or a hidden Mac dialog. The owner can approve a precise recipient, amount, and content, while the relay, Mac, browser, and iOS node enforce that only the reviewed action executes.
- **path:** pendant → relay → mac-bridge → iOS → browser → dashboard
- **model tier:** deterministic staging and receipt logic with gpt-5.6-luna only to compose the human-readable summary; realtime for concise spoken status
- **latency:** Summary displayed on the iPhone within 2–4 s; execution and spoken receipt within 3 s after the on-phone approval
- **cost:** One local planning pass, generally $0.005–$0.03; no model calls needed for the approval or execution itself
- **security:** The iPhone display is not a cryptographic authenticator by itself while mirrored. Bind approval to a nonce, target app, visible summary hash, expiry, and current phone session; require a deliberate on-phone control, never infer approval from screen presence; redact secrets and expire on phone pickup, lock, or app change.
- **missing:** a dedicated iOS confirmation screen/action rather than arbitrary coordinate taps; signed cross-device approval nonce and summary hash; sensitive-action classifier and staging adapter for mail, browser, purchases, and settings; receipt verifier that refuses execution after any target/content drift

### "“When I pick up my phone and Mirroring pauses, keep a private timeline of what the Mac and pendant were waiting on; when I’m done, tell me what changed, what was blocked, and which approvals expired.”"
- **useful because:** Phone pickup is normal, but today it silently breaks the multi-device loop. This gives the owner a trustworthy return point: no duplicate actions, no forgotten staged work, and no claim that something happened while the phone was unavailable.
- **path:** iOS → mac-bridge → relay → pendant → dashboard
- **model tier:** deterministic event ledger and state diff locally; gpt-5.6-luna only to turn the diff into a short personalized catch-up; realtime for the spoken summary
- **latency:** Pause/resume markers within 1 s; catch-up available within 2–3 s after Mirroring resumes
- **cost:** Near-zero while idle; one brief summarization call on resume, roughly $0.005–$0.02
- **security:** The ledger may reveal message snippets or sensitive intent. Store event types and redacted hashes by default, retain raw text only with opt-in, encrypt and expire entries, and let the owner clear the timeline from the pendant. Never imply a queued action completed unless a receipt exists.
- **missing:** Mirroring lifecycle events for pause, resume, lock, and phone pickup; cross-surface event ledger that correlates relay, browser, Mac jobs, and iOS state; resume reconciliation that checks receipts and invalidates stale approvals; owner-configurable retention and redaction policy; spoken catch-up route that distinguishes blocked, completed, and expired


## Changes it proposed to its own stack

### `relay` — Add an iOS-control edge node contract: a small Mac-local iPhone Mirroring worker holds the only Accessibility/Screen Recording access, exposes signed inspect/action receipts to the relay, and maintains a short-lived capability lease. The relay can address this node directly rather than routing every iPhone request through mac-planner; mac-planner remains the fallback for multi-app reasoning. The worker must report locked/off-Space/frontmost/paused state and refuse unsafe pointer actions.
- **owner gets:** The pendant can ask for and safely complete phone tasks even when the general Mac planner is busy or unavailable, with clear spoken progress and no blind taps. This is the closest path to the owner's requested independent iOS node without pretending the iPhone can physically leave the Mac.
- effort: Medium-high: a persistent local worker, relay authentication/lease protocol, iOS action receipts, and integration tests for lock, phone pickup, Space changes, and stale approvals.  ·  risk: A routing bug could send an action to the wrong mirrored app or replay an old approval. Mitigate with app/window identity, visible-text hashes, expiry, idempotency keys, frontmost enforcement, and mandatory reinspection. Recover by cancelling the lease and falling back to manual phone use.
- cost: Negligible runtime API cost; one always-on local process using modest CPU/RAM. No new hardware. Development is the main cost.  ·  latency: Removes a planner hop: typically 200–700 ms faster for inspection/action requests; vision/OCR remains the dominant delay.
- security: Improves isolation by keeping pixels and input local, but introduces a new relay-facing authority. Use mutual authentication, least-privilege operation enums, per-action approval tokens, encrypted receipts, and no raw screenshot upload by default.
- depends on: ios_mirroring_inspect tool or equivalent local inspect endpoint; relay event push/command subscription; durable approval and pending-action state; Mac worker lifecycle launch and health reporting


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct owner-facing capabilities: reviewed extraction from the mirrored iPhone into a Mac/browser form; urgency-filtered iPhone notification alerts through the pendant; and durable, revalidated iPhone actions that survive Mirroring pauses without blind retries. I also recorded the relay/worker isolation change needed for an independent iOS-control node and reported concrete gaps to mac-planner. Live ops confirms the relay and Mac bridge are online, browser is online, Accessibility/Screen Recording/Automation are trusted, but /observe currently reports loginwindow foreground (locked), so iPhone interaction must remain refused rather than guessed.

**Biggest unknown:** The exact iOS Mirroring inspect/action surface is still missing: app/window identity, OCR or screen capture payload, frontmost/readiness, pause/lock state, and a safe action receipt. Without that, the proposed flows can be designed but not run end-to-end.

