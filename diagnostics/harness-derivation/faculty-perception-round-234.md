# Harness derivation — faculty-perception — round 234

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live mac permissions and browser reachability** — At 2026-08-09T01:39Z the Mac local agent reports Accessibility trusted, Screen Recording granted, all required permissions ready, browser extension online with one Safari tab on doordash.com, and relay reachable with Mac bridge online.
  - evidence: read_continuity_snapshot(include=['relay','pipeline']) resolved to GET /ops/snapshot, HTTP 200; returned status.permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser.online=true, tabUrl=https://www.doordash.com, relay.reachable=true.

## Capabilities it proposed

### "“Before you send, buy, delete, or submit anything, show me exactly what is on my current screen, tell me the precise change you are about to make, and only continue after I confirm on the pendant.”"
- **useful because:** This turns newly verified Screen Recording/Accessibility plus the live Safari bridge into a safety boundary the owner can feel: no silent irreversible browser action based on stale DOM, hallucinated state, or an expired tab. The owner gets a short spoken diff and a durable before/after proof.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** gpt-5.6-luna for planning and concise risk explanation; gpt-4.1-mini for screenshot/vision comparison; realtime only for the spoken confirmation turn
- **latency:** 2–4 seconds to capture and compare the current screen; confirmation waits indefinitely for the owner; under 1 second to speak the proposed diff after capture
- **cost:** About $0.01–$0.05 per guarded action, dominated by one vision screenshot comparison and occasional realtime audio; no model call for simple hash/DOM diffs
- **security:** Screenshots and browser text may contain financial or private data and must stay on the Mac unless explicitly authorized. Never read card numbers or passwords into the relay. Require a fresh pendant confirmation bound to the exact action hash, URL, tab identity, and expiry; fail closed if the tab changes, browser goes offline, or permissions become unready.
- **missing:** A first-class guarded-action transaction joining current screenshot hash, browser command, confirmation nonce, and final receipt; Mac vision capture and browser result need one shared action hash and expiry; A device-originated confirmation event from the pendant (or a clearly labeled Mac fallback while no pendant is registered)

### "“Can you do this right now?” — and then give me a truthful yes/no based on the exact live path: pendant link, relay, Mac permissions, and the browser tab I mean, not on cached capability claims."
- **useful because:** The owner should never hear a confident yes when the browser is stale, the Mac lost Screen Recording, the relay is unreachable, or the pendant is absent. This is a preflight perception layer that converts current reachability into a human answer and selects a safe fallback (spoken explanation, browser action, or explicit inability).
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** No expensive model for preflight: deterministic checks and a small rules engine; use the cheaper text model only to explain a multi-blocker result in natural language.
- **latency:** Under 500 ms from live status checks; if a browser probe is needed, under 2 seconds. It must say “unknown” rather than wait indefinitely.
- **cost:** Near-zero API cost; status probes and a compact cached capability graph dominate, with occasional browser inspection
- **security:** Do not expose tab URLs, permission details, or private app names aloud unless relevant. Treat browser session identity and device presence as sensitive. A positive preflight is not authorization: irreversible actions still need the owner’s confirmation.
- **missing:** A single freshness-bounded preflight endpoint that joins relay, Mac permissions, browser device/tab, and pendant registration; Per-intent requirements (read screen, type, submit, speak, hear) and a route-selection policy; A pendant presence signal; today the registry has no nRF9160 device and the browser/Mac are the only live interactive surfaces

### "“Is the pendant ready to wear today?” — plug it into the Mac and have the system prove firmware identity, audio health, relay connectivity, and capture quality, then give me a pass/fail report with the exact failed test."
- **useful because:** The nRF9160 and ESP32 are physically available for bench work, but no pendant is registered and historical pipeline audio is easy to mistake for live health. A one-command commissioning test would turn an unworn prototype into something the owner can trust before leaving the house, and would catch the dangerous case where audio works locally but the relay path does not.
- **path:** mac-terminal → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Deterministic shell/firmware probes and numeric audio tests; a cheap text model only summarizes failures. No realtime model needed.
- **latency:** 30–90 seconds for USB identification, loopback/audio probes, firmware version, and relay registration check; never report pass while any required test is skipped.
- **cost:** Negligible API cost; test audio and serial I/O run locally. Hardware cost is zero because it uses the connected boards.
- **security:** Serial access must be allowlisted to the exact nRF9160 and ESP32 ports and bounded by read time/byte limits. Never flash or erase firmware without explicit confirmation. Relay registration probes use existing credentials but should redact them from logs. Distinguish “not connected” from “failed.”
- **missing:** A real bounded macOS serial diagnostic action for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; current shell access is not a durable, receipt-bearing serial API; A deterministic commissioning script that checks the offline-reality-beacon frame, capture-integrity metrics, 24 kHz acceptance thresholds, and relay registration separately; A safe firmware-version/read-only command and a dashboard report that preserves raw measurements

### "“Before you commit this plan, prove that every surface agrees: the booking page, my calendar, the reminder, and the confirmation email must describe the same person, time, timezone, and location; stop and ask me if any one disagrees.”"
- **useful because:** Today the system can act across browser, Calendar, Mail, and Reminders, but it cannot establish that a multi-surface workflow produced one coherent real-world commitment. This would catch the costly failures a single success receipt misses: wrong timezone, stale booking tab, duplicate appointment, mismatched attendee, or a confirmation email that contradicts the calendar.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic extraction and normalization first; a cheaper text model resolves ambiguous names/locations only. Realtime is used only to explain a conflict and ask the owner.
- **latency:** 10–20 seconds for a full cross-surface consistency check; under 2 seconds for a previously indexed commitment. It must fail closed on missing evidence, not infer agreement.
- **cost:** $0.01–$0.06 per new commitment, dominated by parsing an email or page; repeated checks use local structured state at near-zero cost.
- **security:** Email, calendar, and booking details are sensitive and must remain on the Mac by default. Speak only the minimum conflict aloud. Bind the check to exact URLs, message IDs, calendar event IDs, and capture times; require confirmation before any write. Never silently convert a device-less timestamp into the Mac timezone.
- **missing:** A commitment object that links browser evidence, Calendar/Mail/Reminders identifiers, normalized time/location/party fields, and source freshness; Read-only AppleScript adapters for the relevant apps plus browser evidence capture in one transaction; A contradiction classifier with explicit UNKNOWN/CONFLICT/AGREE states and a user-visible diff; A pendant confirmation protocol for committing only the verified plan when the pendant is present

### "“Before this message or upload leaves my Mac, inspect the exact recipient, destination, attachment, and sensitive fields, then read me only the risks and wait for my approval.”"
- **useful because:** The browser and Mac can already type and submit, but the owner cannot get a single, destination-aware privacy check across Mail, web forms, uploads, and the browser session. This catches wrong-recipient, hidden-attachment, account-switch, and secret-leak failures before they become irreversible.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Local deterministic inspection and redaction classifiers first; a small model summarizes risk categories. Realtime only speaks the short risk report and collects confirmation.
- **latency:** 1–3 seconds for a page or message; up to 8 seconds for a document/attachment scan. Submission remains blocked until an unexpired approval is bound to the exact content hash and destination.
- **cost:** Usually <$0.02 per check; local hashing and redaction dominate, with model cost only for ambiguous document classification.
- **security:** The checker must not upload secrets to the relay. Keep raw content local, return only classifications and minimal snippets, and treat password fields, financial data, health data, and private attachments as high risk. Do not rely on DOM labels alone; verify the visible destination and active account. Require explicit confirmation for every changed hash, recipient, or destination.
- **missing:** A pre-submit interception hook spanning browser commands, AppleScript Mail, and file uploads; Local content classification/redaction that produces a stable redacted-content hash and risk manifest; A confirmation token bound to destination, account, attachment hashes, and expiry, enforced by the action executor; A spoken pendant confirmation and durable receipt of the final submitted bytes


## What it asked for

_Nothing._
## Its own summary

Discovered and verified a major state change: the exact AI Pendant Agent now has Accessibility and Screen Recording, all required permissions are ready, Safari/browser bridge is online on a live DoorDash tab, and relay/Mac bridge are reachable. The nRF9160 pendant is still absent from the live registry. Recorded three owner-facing proposals: (1) confirmation-bound guarded screen/browser actions with before/after evidence, (2) a live-path preflight that answers whether the requested action is possible now, and (3) a non-destructive USB commissioning report proving firmware, audio, capture, and relay health before wear. A duplicate provenance-bridge proposal was correctly rejected by the recorder rather than restated.

**Biggest unknown:** There is still no authenticated, device-originated pendant presence or playback fact: the registry has no nRF9160 and relay 'delivered' remains bytes-to-socket, not heard. The next useful build is to exercise the newly granted screen permissions in a real guarded action and separately add the bounded serial commissioning path; neither can honestly be claimed operational yet.

