# Harness derivation — mac-planner — round 174

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the pendant's bookmark button while it is USB-connected to my Mac, remember what I was doing right then — the active app, browser tab, calendar context, and timestamp — and later let me ask, "What was that moment?""
- **useful because:** The existing offline_moment_bookmark records only that a moment happened. This makes the physical button a zero-friction cross-node memory marker: the pendant supplies intent at the instant it matters, the Mac supplies private desktop context, and the relay turns them into a searchable, cited memory without requiring speech or interrupting work.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Use the realtime model only for an owner's spoken lookup or ambiguous matching; use a cheap background worker to merge the bookmark, Mac observation, browser tab metadata, and calendar event into a ledger record.
- **latency:** USB event acknowledgement under 300 ms; context collection within 2 s; spoken lookup under 2 s when indexed.
- **cost:** About $0.001–$0.01 per lookup/merge depending on whether semantic matching is needed; most events are deterministic and need no model call.
- **security:** Desktop title, URL, and calendar metadata are sensitive. Capture only on an explicit button event, redact query strings and page bodies by default, encrypt in transit, and keep browser contents out unless the owner explicitly asks. Lookup should cite the captured sources and allow deletion.
- **missing:** A live USB-serial exchange service for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A relay event schema linking offline_moment_bookmark IDs to Mac/browser/calendar observations; A durable searchable moment ledger and retention/deletion controls

### "Run a complete pendant audio check from my Mac, and tell me in plain language whether the microphone, radio path, decoder, and speaker all passed — without recording or retaining my voice."
- **useful because:** The pendant is physically attached over USB today, and audio_path_diagnostic_fixture already emits synthetic, non-private test traffic. A Mac-triggered end-to-end report would turn that low-level fixture into something the owner can run before a call and distinguish a bad radio link from a codec/clock/playback failure instead of guessing.
- **path:** mac-planner → pendant → relay-realtime → mac-vision → unified
- **model tier:** Cheap background rules classify counters and compare acceptance thresholds; realtime is unnecessary except to answer a follow-up question about a failed component.
- **latency:** Start within 1 s of the request and finish a normal run in 15 s; failure report should be available immediately after the fixture receipt.
- **cost:** Near-zero model cost for pass/fail; at most $0.001 for rendering a concise explanation. USB serial and a few kilobytes of synthetic frames dominate no API spend.
- **security:** The fixture must be synthetic and must never open the microphone. Authenticate the USB device identity, bind each receipt to a nonce, and expose counters rather than raw PCM. A failed test may reveal connectivity or device identifiers, so keep reports private.
- **missing:** A USB serial command/receipt bridge for the live pendant and ESP32 bridge; A relay endpoint that accepts the fixture's timestamped counters and correlates both directions; A versioned acceptance-threshold profile matching the shipped 24 kHz/60 ms path

### "If I long-press the pendant while it is on my desk, immediately put my Mac into privacy mode: mute audio input and output, stop active screen sharing, hide or lock sensitive windows, and tell me on the pendant what actually succeeded."
- **useful because:** A wearable privacy control is useful precisely when the Mac UI is covered, an app is frozen, or the owner needs both sides silenced at once. The local_privacy_latch already protects the pendant's microphone and speaker; this is the missing cross-node extension that makes the physical gesture protect the surrounding computer too, with a receipt instead of a false assumption.
- **path:** pendant → mac-planner → mac-vision → relay-realtime → unified
- **model tier:** No model is needed for the deterministic emergency path. Use a cheap background classifier only to choose which configured sensitive apps to hide; realtime may narrate the result if the owner asks.
- **latency:** Pendant local mute immediate; Mac mute/lock commands dispatched within 500 ms over USB or relay; receipt within 2 s. If disconnected, local latch still works and the Mac action is explicitly reported as not attempted.
- **cost:** Effectively $0 API cost for the emergency path; one short model call (under $0.005) only for a user-defined, ambiguous app policy.
- **security:** This is high-impact local control and must be an explicit owner-configured policy, not an inferred default. Never claim screen sharing stopped without querying it. Keep the USB command authenticated and replay-protected; preserve a minimal local audit receipt but no screen contents. Recovery must be a local gesture, not network-dependent.
- **missing:** A firmware-to-Mac USB event bridge with authenticated command framing; A typed Mac privacy action bundle that can query and control input/output, screen sharing, window visibility, and lock state; Owner-configured sensitive-app and recovery policy; A compact receipt path from Mac back to pendant

### "When I plug the pendant into my Mac, restore the exact work session I left last time — the project files, app windows, browser tabs, and unfinished server task — and give me one spoken summary of what was restored and what could not be recovered."
- **useful because:** The pendant is the owner's physical continuity token: plugging it in should make a desk usable again without reconstructing context from memory. This is more than opening a fixed workspace because it must reconcile the last durable server state with the Mac's actual files, apps, and authenticated browser sessions, and report discrepancies honestly.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Use deterministic state reconciliation and a cheap background model for naming unresolved conflicts; reserve realtime for the spoken summary or an ambiguous conflict question.
- **latency:** Detect insertion within 2 s; restore a normal session within 20 s; speak a concise receipt as soon as each phase completes.
- **cost:** Usually under $0.01 per restore; model cost is only for conflict wording. Desktop launch and browser session startup dominate latency.
- **security:** The pendant must be an authenticated continuity token, not an automatic unlock credential. Never restore secrets into an untrusted window; redact private tab titles in the spoken receipt; require the owner-configured policy for destructive conflict resolution. Keep a durable manifest of intended versus completed actions.
- **missing:** Authenticated USB insertion/event detection and device identity; A durable cross-node workspace manifest with file hashes, app state, browser session IDs, and server job IDs; A reconciliation engine that can distinguish safe reopen from destructive overwrite; A Mac wake/launch hook that runs before the owner asks

### "If I unplug the pendant or walk away from my Mac during a voice conversation, keep the conversation alive and hand the audio route over cleanly instead of dropping or replaying anything; when I reconnect, hand it back and tell me which route is active."
- **useful because:** Today the Mac, ESP32 headphone bridge, and pendant are separate audio islands. A real wearable should let the owner leave the desk without losing the conversation, while avoiding duplicate audio, stale replay, or a microphone left open on the abandoned route.
- **path:** pendant → mac-planner → relay-realtime → mac-vision → unified
- **model tier:** Deterministic route arbitration and packet sequence handling do the handoff; use realtime only if the owner asks for an explanation of a degraded transition.
- **latency:** Detect USB/bridge loss within 500 ms, select the surviving route within 2 s, and resume speech with no more than one bounded audio frame of duplication.
- **cost:** Negligible model/API cost; engineering cost is in synchronized route leases, buffering, and hardware transition testing.
- **security:** The old route must be muted and its capture disabled before the new route is declared live. Route leases need authenticated device IDs and monotonic epochs to prevent two microphones transmitting at once. Never persist conversation audio merely to bridge a handoff.
- **missing:** A relay-owned audio route lease and epoch protocol spanning Mac, ESP32 bridge, and pendant; USB attach/detach telemetry and a Mac audio-device control adapter; A short RAM-only cross-route jitter buffer with duplicate suppression; Owner policy for whether a handoff is automatic or only allowed during an active call

### "When a desktop task I asked for fails, have the pendant tell me why in one sentence and keep a compact, private recovery packet — the exact action, app state, browser session, and error — so I can say "retry that" or "show me what went wrong" later."
- **useful because:** A failed automation currently leaves the owner to reconstruct what the Mac did. This would make failures recoverable across the wearable and Mac: the pendant gives immediate feedback away from the screen, while the relay keeps enough structured evidence to retry or explain without retaining a screen recording or full page contents.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Rules extract action and error fields; a cheap background model summarizes unusual failures. Realtime is reserved for the owner's follow-up conversation and should not be used to collect diagnostics.
- **latency:** Failure classification and a short pendant notification within 1 s of the receipt; recovery packet persisted within 3 s; retry planning under 2 s for deterministic actions.
- **cost:** Usually below $0.005 per failure; most packets are structured JSON and need no model call.
- **security:** Packets may contain filenames, URLs, and app titles. Redact credentials, page bodies, and typed secrets; encrypt at rest; set a short retention period; make retry idempotent and never silently repeat an irreversible action. This complements receipts but stores the causal state needed to recover.
- **missing:** A typed failure envelope emitted by every Mac/browser action, including pre-state, post-state, and error class; A bounded redacted recovery-packet store with owner deletion and TTL; A relay-to-pendant notification path for failure summaries; A retry planner that checks whether the original preconditions still hold


## Changes it proposed to its own stack

### `hardware` — Add a small secure element (for example an ATECC608-class device) on the pendant's currently free I2C bus, with a unique device key used to authenticate USB-serial commands and relay event frames. Keep the key non-exportable and require signed nonces for bookmark, diagnostic, and emergency privacy commands.
- **owner gets:** The owner can safely use a worn physical control to affect the Mac without an untrusted USB process impersonating the pendant. It makes the promised desk-side privacy action and moment bookmarks trustworthy rather than merely convenient.
- effort: Moderate hardware revision and firmware integration: I2C driver, provisioning fixture, nonce/signature protocol, and Mac-side verification. Prototype breakout wiring is straightforward; production provisioning and recovery need careful design.  ·  risk: A lost or mis-provisioned key could strand the pendant. Provide a factory re-provisioning path and a visible unpaired LED state; retain an authenticated software fallback only for development hardware.
- cost: Roughly $0.50–$2 per unit plus provisioning/test time; under 10 mW active and negligible sleep draw depending on the chosen chip.  ·  latency: Typically adds tens of milliseconds to a command handshake, acceptable for bookmarks and diagnostics; emergency local mute remains immediate and does not depend on the secure element.
- security: Strongly improves device identity and replay resistance. It does not itself authorize Mac actions: the owner-configured Mac policy must still decide which signed commands are permitted and record receipts.
- depends on: A defined pendant↔Mac USB command framing protocol; Owner-configured Mac privacy/action policy; A relay event schema that carries device identity and nonce receipts


## What it asked for

_Nothing._
## Its own summary

This round produced four non-duplicate deliverables: (1) a cross-node USB moment lookup concept (pendant bookmark + Mac/browser/calendar context + relay memory), (2) a private end-to-end audio check that turns the existing synthetic diagnostic fixture into an owner-readable pass/fail report, (3) a pendant-triggered Mac privacy mode with honest per-action receipts, and (4) a hardware change adding a secure element on the pendant's currently free I2C bus so those USB commands cannot be spoofed. I also asked relay-realtime for the event contract needed to join signed pendant events to Mac context.

**Biggest unknown:** I still need a working authenticated USB-serial exchange path for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; mac_serial_exchange remains unavailable, so I cannot test the live boards from this Mac. I also need the real POST contract for relay event ingestion (the route is listed, but the available description probe performed GET and returned 404), plus the owner's explicit policy for which Mac privacy actions may run unattended. Accessibility/Screen Recording TCC remains owner-blocked, so window-level hiding and screen-share verification cannot be honestly promised yet.

