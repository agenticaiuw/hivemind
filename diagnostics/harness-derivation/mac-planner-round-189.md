# Harness derivation — mac-planner — round 189

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-environment-round-189** — The Mac agent is online and ready: Accessibility and Screen Recording are granted for AI Pendant Agent, synthesized input is verified, Safari bridge is online with 9 tabs, relay is reachable, and computer-use loop is enabled but visionUploadConsented is false. The pendant remains physically USB-connected but LTE registration is still not established.
  - evidence: GET /ops/status 200 at 2026-08-08T02:18Z; GET /observe 200 showed trusted=true, screenRecording=true, eventsPost=true, browser online/tabCount=9, relay reachable, and visionUploadConsented=false.

## Capabilities it proposed

### "When I press the pendant's bookmark button, save what I'm looking at right now and tell me later why it matters."
- **useful because:** A physical bookmark becomes a cross-device context capture: the pendant supplies the exact moment, the Mac supplies the active app and Safari tab, and the relay turns that into a short, retrievable explanation instead of an opaque timestamp. It works today over USB even though LTE registration is absent.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** Use the realtime tier only for the immediate acknowledgement; use a cheaper background text model to summarize the captured page and relate it to the owner's active project.
- **latency:** Button acknowledgement under 300 ms locally; Mac/browser context under 2 s; summary may arrive asynchronously within 30 s.
- **cost:** About $0.01–$0.05 per captured page, dominated by page text extraction and background summarization; no model call for the local event or URL capture.
- **security:** Page text may contain secrets and authenticated content. Default to URL/title plus a short redacted selection; require an explicit per-site policy before sending full page text to the relay. Never capture passwords or form values.
- **missing:** A USB-serial event bridge from the currently connected nRF9160 pendant into the Mac agent (LTE is not registered); A browser command that returns active tab title, URL, and explicitly selected text with redaction; A relay record joining the pendant bookmark sequence number to the Mac/browser context and later summary

### "If you start something on my Mac and it fails or gets interrupted, recover it automatically and tell me exactly what was completed, without duplicating files or actions."
- **useful because:** Today a voice request can cross the relay and Mac but a dropped connection or partial multi-file operation can leave uncertainty. An idempotent recovery contract would let the owner trust unattended work: the pendant reports one concise outcome, while the Mac resumes only the missing steps and provides a receipt.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use a cheap background model to interpret the failure and select a retry branch; reserve realtime for the owner's spoken status query.
- **latency:** Persist a checkpoint before each side effect; detect a lost job within 5 s; retry safe steps within 30 s; speak a one-sentence receipt when done.
- **cost:** <$0.01 per retry decision; storage and hashing dominate, not inference.
- **security:** Never retry sends, purchases, deletions, or submissions automatically. Persist redacted resource identifiers and hashes, not document contents. Browser actions need session affinity and a stale-tab check before resuming.
- **missing:** A durable step-level execution journal shared by relay and Mac, with idempotency keys for browser and desktop actions; A resume protocol that distinguishes completed, in-flight, and unknown outcomes after a crash; A pendant-facing status event type that can say partial, recovered, or needs-owner-confirmation without exposing file contents

### "When an action needs my approval—sending mail, deleting a file, or buying something—show me a short plain-language summary on the pendant and let one deliberate button press approve exactly that action once."
- **useful because:** The owner can approve a consequential action without returning to the Mac or trusting an unattended FULL_CONTROL execution. The relay binds a one-time challenge to the exact Mac/browser plan, the pendant displays or speaks the summary, and the Mac executes only the matching plan. This uses the physical device as an approval surface no single node has.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime only to explain the pending action conversationally; use deterministic code for hash binding, expiry, and approval consumption. No model should decide whether an approval matches.
- **latency:** Challenge creation under 1 s; pendant acknowledgement under 500 ms; approval expires after 60 s; execution receipt under 5 s.
- **cost:** Negligible model cost; typically zero additional inference, with small relay storage overhead.
- **security:** Bind approval to an action-plan hash, target app/domain, resource identifiers, and expiry; consume atomically to prevent replay. Speak redacted summaries and never expose secret form fields. Reject if the Mac/browser state changed after approval. Owner policy must explicitly enable this because the current FULL_CONTROL path has no live gate.
- **missing:** A firmware event for one-time approval/rejection that is distinct from the existing bookmark and privacy-latch semantics; Relay-side atomic approval challenge storage and plan-hash verification; A Mac executor hook that pauses a submitted plan, reports the exact preview, and resumes only on a matching approval token

### "While the pendant is plugged into my Mac, make it a seamless local voice endpoint: pressing the normal talk button should use the Mac's network and speaker path, then automatically return to LTE when the pendant registers, without losing the conversation."
- **useful because:** This makes the hardware genuinely useful today: the pendant is physically present over USB even though it is not LTE-registered. The owner gets the same wearable interaction in the house, with the Mac acting as a transparent transport bridge, and can walk away without manually changing modes or losing queued audio.
- **path:** pendant → mac-planner → relay-realtime
- **model tier:** Realtime for the live voice loop; deterministic routing and buffering decide USB-versus-LTE. Do not spend a background model call on transport selection.
- **latency:** USB button/event to relay under 150 ms; audio continuity across a route change with no more than 250 ms gap; fall back to offline queues if both links fail.
- **cost:** No additional model cost; modest Mac CPU and serial/WebSocket bandwidth. The dominant engineering cost is a duplex framing bridge and transition testing.
- **security:** Pair the USB serial identity to the owner's relay account and encrypt/authenticate the local bridge session. Never expose raw audio to unrelated Mac apps. Clear transient PCM buffers after delivery and preserve the existing privacy latch across route changes.
- **missing:** A Mac USB-serial transport service for /dev/cu.usbmodem00096003658* that understands the pendant's button, Opus uplink, and 24 kHz/60 ms downlink framing; Relay session routing that treats USB and LTE as interchangeable legs with sequence-number continuity and an atomic active-leg switch; A pendant link-state state machine that prefers USB when present, LTE when registered, and store-and-forward when neither is usable

### "When I unplug or walk away from my Mac, give me a private handoff on the pendant: what I was working on, which tabs or documents matter, and the next concrete step for each—then let me resume that context later with one press."
- **useful because:** The owner loses context exactly when moving between desk, meeting, and elsewhere. A physical departure event can capture the Mac's active work state without requiring them to remember to ask, while the pendant provides a compact spoken handoff and a durable resume point. This is not a crash retry or a bookmark: it is an intentional transition from desktop context to wearable context.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** Use a cheaper background text model to rank active documents, tabs, calendar commitments, and unfinished actions; use realtime only if the owner asks follow-up questions through the pendant.
- **latency:** Detect USB disconnect within 2 s; capture state within 5 s; produce a three-item handoff within 20 s; one-press resume should restore context within 10 s.
- **cost:** Approximately $0.01–$0.04 per departure, dominated by summarizing selected document/tab metadata; no model call is needed for event detection or resume-token validation.
- **security:** The handoff could reveal sensitive tabs or documents aloud. Default to app names and redacted titles, suppress password managers/private browsing, and require an owner-configured list of apps/sites eligible for capture. Resume tokens must expire and be bound to the Mac session.
- **missing:** A reliable pendant USB connect/disconnect event delivered to the Mac agent and relay, including reconnect identity; A Mac context snapshot that can read active document identity, unsaved editor state, and browser tab metadata without collecting page secrets; A durable handoff object with ranked next steps and a pendant resume action that reopens only the approved app, tab, or file set

### "When I reconnect the pendant to my Mac, tell me what changed since I left—files, calendar, mail, and browser work—and open a review view for only the changes that need my attention."
- **useful because:** The owner returns to a moving desktop without scanning every app. The pendant supplies the physical arrival event, the relay compares the saved departure snapshot with current state, and the Mac opens a bounded review rather than blindly restoring a stale workspace.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** Use deterministic diffs for files, calendar, mail metadata, and tabs; use a cheaper background model only to rank and phrase the resulting changes. Realtime is unnecessary unless the owner asks a follow-up.
- **latency:** Detect reconnect within 2 s; collect diffs within 10 s; speak a three-line delta within 20 s; open the review pane within 5 s after the owner asks.
- **cost:** Usually <$0.01 per reconnect; model cost is limited to ranking ambiguous changes. Hashing and bounded metadata reads dominate.
- **security:** Do not read full mail bodies or authenticated page content by default. Redact secrets, exclude private windows and password managers, and make the saved departure snapshot owner-scoped and expiring. Opening a file is reversible; sending or modifying anything remains a separate explicit action.
- **missing:** A paired connect/disconnect lifecycle event with a stable snapshot identifier; A snapshot-diff service spanning workspace files, Calendar/Mail metadata, and browser tabs; A Mac review action that presents a generated change list and can open selected files/tabs without mutating them


## Changes it proposed to its own stack

### `hardware` — Add a low-power NFC tag plus a secure-element-backed pairing flow to the pendant enclosure, with the Mac agent presenting a one-time pairing nonce and the relay issuing a device-bound credential after an NFC tap. Keep the existing LTE/USB paths unchanged; NFC is only for physical proximity and bootstrap.
- **owner gets:** The owner can move the pendant to a new Mac or recover from a reset by tapping it, rather than copying pairing codes or leaving a long-lived secret in a browser. It also gives the owner a clear physical signal that the wearable is paired to this nearby machine.
- effort: Moderate hardware revision and firmware/relay work: NFC antenna/tag or reader integration, secure credential provisioning, Mac Core NFC/USB pairing helper, and recovery UX. Requires threat-model and manufacturing provisioning.  ·  risk: A stolen pendant in proximity to an unlocked Mac could initiate pairing unless the Mac shows a nonce and the owner confirms with the existing button. Recover by revoking the device credential at the relay and requiring a fresh physical tap. Avoid NFC storage of the relay API key.
- cost: Roughly $2–$8 BOM increase depending on NFC controller and secure element; NFC power is near-zero in idle for a passive tag, with brief reader/provisioning power during pairing. No per-use model cost.  ·  latency: Pairing should complete in 5–15 seconds; no effect on live audio after pairing.
- security: Improves physical binding and credential rotation, but adds a proximity attack surface. Use ephemeral nonces, relay-side revocation, secure-element key generation, and explicit owner confirmation.
- depends on: A relay device-credential and revocation endpoint; A Mac pairing helper that can communicate with the connected pendant and display the nonce; Firmware support for NFC identity exchange and secure-element-backed key storage


## What it asked for

_Nothing._
## Its own summary

Round 189 produced four new cross-node capabilities: context-aware physical bookmarking, idempotent recovery of interrupted Mac/browser jobs, exact one-time pendant approval for high-impact actions, and—most useful—a seamless USB-local voice mode that makes the physically connected but LTE-unregistered pendant usable today. Live inspection also established that Accessibility, Screen Recording, synthesized input, Safari bridge, relay, and Mac computer-use are all online; vision uploads remain unconsented.

**Biggest unknown:** The missing USB serial exchange service is still the critical blocker for testing the local voice mode. I still need a real duplex serial bridge for /dev/cu.usbmodem00096003658* (and the ESP32 bridge if required), plus the relay's route-switch semantics; the queued mac_serial_exchange request has not resolved and should not be re-requested this round.

