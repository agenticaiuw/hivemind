# Harness derivation — mac-planner — round 164

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I walk away or the pendant disconnects while you are working on my Mac, pause safely, remember exactly where you were, and resume automatically when I reconnect—then tell me on the pendant what finished and what still needs me."
- **useful because:** Long Mac/browser tasks stop being fragile when the owner closes the lid, walks out of USB range, or has a transient relay outage. They return to a truthful continuation rather than a half-completed mystery.
- **path:** pendant → mac-bridge → mac-planner → browser-extension → relay-realtime
- **model tier:** Cheap background model for checkpoint classification and resume validation; realtime only for the short pendant status message.
- **latency:** Checkpoint within 2 seconds of disconnect; resume within 10 seconds of reconnect; completion status under 3 seconds after the final action.
- **cost:** Usually <$0.01 per task in background inference; dominant cost is browser/Mac polling and any long-running page work, not model tokens.
- **security:** A disconnect must never be interpreted as permission to continue blindly. Persist only action IDs, completed receipts, and redacted state; revalidate page/session identity after reconnect and stop on changed context. No secrets leave the Mac except through existing authenticated relay paths.
- **missing:** Pendant USB-serial presence/disconnect event and reconnect handshake; Durable checkpoint/resume state machine spanning POST /execute jobs and browser sessions; A Mac bridge watcher that can pause an active job without killing its receipt chain; A bounded resume validator for stale tabs, files, and app state

### "Only treat my private Mac and logged-in-browser requests as mine while my paired pendant is physically connected; if it disconnects, freeze new private actions, show me the exact pending plan, and let me resume when it returns."
- **useful because:** The pendant becomes a continuously present, local proof of the owner's intent. A stolen laptop session, unattended browser, or stale relay command cannot silently keep acting after the owner leaves.
- **path:** pendant → mac-bridge → mac-planner → browser-extension → relay-realtime
- **model tier:** No expensive model for the security decision: firmware/bridge cryptographic verification and deterministic policy. Use a cheap model only to explain a blocked action in plain language.
- **latency:** Presence loss detected and private dispatch frozen in under 500 ms; reconnect attestation under 2 seconds.
- **cost:** Negligible inference cost; small engineering cost for key provisioning, serial framing, and durable key rotation.
- **security:** Use a per-device asymmetric key and nonce challenge, never a reusable bearer token or audio phrase. Keep private action payloads on the Mac; relay sees only capability and attestation state. Recovery must support explicit re-pairing and revocation if the pendant is lost. This is a presence control, not a human confirmation gate.
- **missing:** Firmware attestation and nonce-response over /dev/cu.usbmodem00096003658*; Mac serial-presence daemon bound to the AI Pendant Agent identity; A dispatch policy that labels jobs private/public and freezes only private work on loss; Pairing, revocation, and recovery UX

### "When my meeting ends, make me a follow-up packet: pull the meeting's calendar details, find the relevant unread and recent mail plus any already-open authenticated browser pages, summarize decisions and unresolved promises with citations, and prepare drafts or reminders without sending anything."
- **useful because:** The valuable work starts after the call, when context is scattered across Calendar, Mail, and private tabs. The owner gets a reviewable packet while details are fresh, rather than spending 30 minutes reconstructing the thread.
- **path:** mac-planner → browser-extension → mac-bridge → relay-realtime → pendant
- **model tier:** Cheap background synthesis model for extraction and clustering; realtime model only if the owner asks for a spoken summary or clarification.
- **latency:** Start within 2 minutes of the calendar event ending; initial packet within 5 minutes; drafts/reminders are reviewable before any mutation.
- **cost:** Roughly $0.02–$0.10 per meeting depending on mail/page volume; browser extraction and long context dominate.
- **security:** Read only the event's bounded time window, related mail, and tabs explicitly associated with the meeting. Cite source URLs/message IDs and retain redacted snippets, not whole bodies by default. Drafts/reminders require an explicit review surface; never send or submit.
- **missing:** A meeting lifecycle trigger (calendar end plus grace period); Reliable association of an event with relevant browser tabs and mail threads; A citation-preserving synthesis schema for decisions, owners, dates, and evidence; A reviewable draft/reminder bundle with per-item accept/edit/reject

### "When I put the pendant back on after being away, tell me what changed on my Mac and in my open private browser sessions while I was gone—new files, app changes, page changes, and important notifications—then offer a compact list of things I should act on."
- **useful because:** The owner gets a reliable re-entry brief instead of reopening every app and trying to remember where they left off. It turns the physical pendant's absence and return into a useful boundary for personal continuity without recording a microphone.
- **path:** pendant → mac-bridge → mac-planner → browser-extension → relay-realtime
- **model tier:** Cheap background model compares normalized event snapshots and ranks changes; realtime is used only to read the final brief aloud when the pendant reconnects.
- **latency:** Capture a baseline within 10 seconds of departure, detect return within 2 seconds, and produce the first brief within 20 seconds.
- **cost:** About $0.01–$0.05 per return brief; local snapshotting is the dominant work and model cost scales with the number of changed items.
- **security:** Snapshots remain on the Mac by default and contain hashes, app/page identifiers, and redacted notification text rather than full content. Private browser data is scoped to explicitly paired sessions. The owner can exclude directories, apps, and sites; never infer that absence means deletion.
- **missing:** A Mac-side append-only, privacy-filtered activity journal for app, file, notification, and browser-session changes; Pendant presence transition events over the USB serial link and a departure/return session identifier; Browser bridge support for normalized before/after page fingerprints on already-open authenticated tabs; A relay endpoint that asks the Mac for a bounded delta and sends a short result to the pendant

### "When I press the pendant button twice, bookmark my exact working set—open apps, windows, files, browser tabs, and the unfinished sentence or form—and later let me say 'restore my desk' to reopen it without overwriting anything that changed."
- **useful because:** The owner can deliberately create a recoverable work checkpoint before commuting, rebooting, or switching projects. It preserves momentum across the physical and digital boundary while keeping later changes safe and reviewable.
- **path:** pendant → mac-bridge → mac-planner → browser-extension → relay-realtime
- **model tier:** Deterministic Mac/browser state capture and restore; a cheap model names and summarizes the checkpoint. No realtime reasoning is needed unless the owner asks a spoken question.
- **latency:** Capture in under 3 seconds after the button gesture; restore preview in under 5 seconds and apply in under 15 seconds for a normal workspace.
- **cost:** Under $0.01 per checkpoint; storage and browser tab metadata dominate, with no need to resend document contents.
- **security:** Store references and hashes rather than copying private files or form values. Never auto-submit forms or overwrite files. Restore must report missing/changed resources and open them read-only or as a copy where possible.
- **missing:** A pendant gesture/event protocol distinct from voice capture; Mac workspace snapshot covering windows and cursor/document positions without requiring Screen Recording; Browser tab/session snapshot with safe form-state redaction; Conflict-aware restore planner and a local checkpoint store

### "Find every draft or note I have about this project across Mail, Notes, local files, and my open private browser tabs, compare them with the latest source I point to, and prepare a conflict report plus synchronized draft edits for my review—without sending or publishing anything."
- **useful because:** The owner stops losing time to contradictory copies of a plan. The system identifies stale commitments and lets them review one coherent set of edits across otherwise disconnected Mac and browser surfaces.
- **path:** pendant → relay-realtime → mac-planner → mac-bridge → browser-extension
- **model tier:** Background model performs extraction, entity matching, and diff generation; realtime only handles the owner’s short selection of the project/source and reads the conflict summary.
- **latency:** Source scan begins within 5 seconds; a normal project packet in under 2 minutes; each proposed edit remains reviewable before application.
- **cost:** Approximately $0.05–$0.30 depending on document count and browser page size; extraction and context transfer dominate.
- **security:** Search only user-selected folders, accounts, and tabs; redact secrets and unrelated messages before synthesis. Preserve per-field citations and never silently replace originals. Applying edits must be a separate, explicitly reviewable action.
- **missing:** A bounded cross-source search over Mail, Notes, local files, and authenticated browser tabs; A shared project/entity matcher with provenance and freshness scoring; A multi-document patch format that previews edits and supports per-field accept/reject; A Mac UI or pendant-delivered review protocol for conflicts too large to read aloud


## Changes it proposed to its own stack

### `hardware` — Replace the prototype-only presence assumption with a production pendant security path: add a small secure element (for example, an ATECC608-class device) on I2C, provision a non-exportable device key at manufacture, and expose nonce-signing to the nRF9160 firmware over a narrow command. The Mac bridge challenges it over the existing USB serial connection before dispatching private browser/Mac work.
- **owner gets:** The owner's worn device can prove that it is physically present without putting a reusable secret in the laptop, relay, or firmware image. Losing an unlocked Mac or a copied session no longer leaves private automation running unattended.
- effort: Medium hardware spin plus firmware driver, manufacturing provisioning, bridge attestation protocol, and revocation/re-pair UX. Prototype first with the nRF9160's protected key storage, then validate the secure element before productizing.  ·  risk: A failed challenge could strand private automation; recover with an explicit re-pair flow and public/read-only fallback. Physical extraction, supply-chain provisioning mistakes, and USB impersonation remain threats and need manufacturing tests.
- cost: Approximately $0.50–$2 BOM increase in volume, negligible steady-state power, plus one I2C peripheral and a few KB of firmware/driver space.  ·  latency: Approximately 50–300 ms per private-job session attestation; cache only a short-lived bridge session, not a permanent authorization.
- security: Material improvement: private keys never leave the secure element. Requires key revocation, per-owner pairing records, nonce freshness, and clear handling when the pendant is absent.
- depends on: Pendant firmware nonce-signing command; Mac USB-serial presence daemon on /dev/cu.usbmodem00096003658*; Private/public job labeling in the Mac dispatch path; Pairing and revocation storage in the relay


## What it asked for

_Nothing._
## Its own summary

Round 164 produced four new, owner-visible directions: disconnect-aware checkpoint/resume across Mac and browser jobs; pendant-presence authorization for private automation; post-meeting follow-up packets with sourced drafts/reminders; and a secure-element hardware path to make presence proof real rather than bearer-token-based. I also sent faculty-action the exact current routes and the important limitation: mac_readonly_inspect and mac_read_sources are granted schemas but currently return no implementation. The live device inventory confirms Safari (3 tabs) and the Mac bridge are online, while the mobile test device is offline.

**Biggest unknown:** Whether the orchestrator will implement the granted read-only Mac tools and the USB serial pendant/bridge watcher. Until those exist, I can dispatch actions through /plan and /execute, but cannot truthfully inspect current UI/mail/calendar state or react to physical disconnects.

