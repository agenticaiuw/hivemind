# Harness derivation — faculty-judgement — round 100

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before I leave for an appointment or trip, make sure I can actually get there.”"
- **useful because:** The current system can brief calendars, watch pages, and prepare meetings, but it does not join those facts into a departure decision. This would quietly inspect the next event and any logged-in reservation, check current travel conditions and weather, calculate a leave-by time with uncertainty, identify required tickets/forms/items, and speak one short actionable packet on the pendant. If conditions change, it updates only when the recommendation materially changes, rather than spamming the owner.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → pendant → dashboard
- **model tier:** Use a cheap background model for calendar/reservation extraction, weather/transit normalization, and change detection; use realtime only when the owner asks a follow-up or the departure packet is delivered interactively. Keep deterministic arithmetic for leave-by and buffer calculations.
- **latency:** Initial packet within 60 seconds of a scheduled departure window; material-change alerts within 2 minutes of new evidence. A spoken packet should be 20–30 seconds, with a longer cited version available on the Mac.
- **cost:** Roughly $0.01–$0.05 per event packet depending on web extraction; most polling and normalization should be cached/background work. Realtime cost is limited to owner follow-ups.
- **security:** Reservation pages and calendar details are private and must stay in the authenticated browser/Mac path; send only normalized times, locations, and redacted requirements to the relay. Never book, cancel, check in, or submit a form automatically. Directions or a reminder may be prepared without confirmation; any purchase or message requires confirmation.
- **missing:** departure-window planner with uncertainty-aware leave-by computation; calendar-event and reservation correlation keyed by time/location; weather/transit evidence adapters with freshness and outage handling; a quiet-hours and material-change policy for departure alerts; pendant audio queue item with acknowledge/snooze/replay controls

### "“I lost my pendant—lock it down, keep my private work safe, and help me recover without losing my notes.”"
- **useful because:** A wearable is physically easier to lose than a laptop, yet it may be the doorway to private browser sessions, voice history, reminders, and queued actions. Today there is no single owner-facing recovery action spanning the pendant, relay, Mac, and browser. The owner should be able to trigger a graded lockdown from any surviving surface, preserve useful work, and later re-enroll a replacement without guessing which credentials or jobs are still active.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use deterministic security code for revocation, session invalidation, job cancellation, encrypted backup, and re-enrollment. Use a cheaper background model only to produce the human-readable recovery checklist and summarize what was preserved. Realtime is appropriate only for the owner's spoken emergency command and confirmation.
- **latency:** Immediate local latch on the pendant; relay and browser-session revocation within 30 seconds; Mac recovery inventory within 2 minutes. The owner should hear a one-sentence status and receive a detailed checklist afterward.
- **cost:** Negligible model cost for the lockdown itself; approximately $0.01 or less for an optional generated recovery summary. Storage and key-management infrastructure dominate engineering cost, not inference.
- **security:** The command must require an authenticated surviving device or a pre-established recovery phrase, with a deliberate distinction between 'freeze access' and destructive wipe. Never expose secrets in spoken output. Revoke browser sessions and pending irreversible jobs, retain only encrypted owner-approved notes, record an auditable receipt, and require explicit confirmation before remote wipe or credential rotation. A false trigger should be recoverable by a short re-authentication window.
- **missing:** device identity and attested pendant keypair with server-side revocation; one emergency lockdown endpoint spanning relay, Mac agent, browser sessions, and queued jobs; encrypted, owner-selected pendant-note escrow and replacement-device restore; recovery phrase or surviving-device challenge flow; credential/session inventory and auditable lockdown receipts; firmware behavior for offline lost-mode latch and secure erase after a configurable timeout


## What it asked for

_Nothing._
