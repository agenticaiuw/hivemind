# Harness derivation — mac-planner — round 34

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "During a meeting, when I say “mark that,” capture the moment and later give me a sourced follow-up list."
- **useful because:** It turns fleeting spoken decisions into usable work without asking the owner to take notes or lose focus. The pendant supplies the low-friction trigger and timestamp, the Mac supplies the exact document/browser context, and the relay turns the captures into a reviewable follow-up packet after the meeting.
- **path:** pendant → relay → mac-bridge → browser → Mac → dashboard
- **model tier:** Realtime only handles the short “mark that” acknowledgment and records an event. A background cheaper model batches and structures the events after the meeting; a stronger model is used only when reconciling ambiguous owners/deadlines across captured context.
- **latency:** Acknowledge in under 500 ms. Context capture should finish within 2 s without stealing focus. Post-meeting packet within 2 minutes of the calendar event ending.
- **cost:** About $0.01–$0.05 per meeting, dominated by post-meeting transcription/structuring; event acknowledgments and hashes are negligible.
- **security:** The pendant must not continuously record audio. Store only explicit event snippets (or a user-configured short transcript), timestamps, active-app metadata, URL/title, and selected document text. Private page content stays on the Mac unless the owner enables relay analysis. Never send follow-ups; show drafts and source evidence for review.
- **missing:** A pendant-side explicit event trigger with a durable local queue (the pending offline_thought_capture request would cover part of this).; A Mac read-only context snapshot API that returns active app/document/browser tab and bounded selected text without taking focus; the granted inspection/read-source schemas currently have no implementation.; A meeting session coordinator keyed to Calendar event IDs, with start/end detection and post-meeting job scheduling.; A provenance-aware follow-up packet format and dashboard review view.

### "When I enter a meeting, quietly put the whole hive into meeting-safe mode: suppress nonessential pendant interruptions, pause background browser actions, hide sensitive Mac windows and notifications, and restore everything when the meeting ends—while still allowing an urgent alert through."
- **useful because:** Today each surface can interrupt or expose information independently. A coordinated mode would prevent an embarrassing notification, spoken private detail, or automation changing a page while the owner is with other people, without requiring manual toggles across devices.
- **path:** pendant → relay → mac-bridge → browser → Mac → dashboard
- **model tier:** Use a cheap background model only to classify calendar events and alert urgency. Realtime handles only an explicit override or urgent alert explanation; deterministic policy should perform the mode transitions.
- **latency:** Enter safe mode within 5 seconds of a meeting start or explicit command; restore within 10 seconds after it ends. Urgent alerts should reach the owner within 2 seconds.
- **cost:** Under $0.01 per meeting when driven by Calendar events; classification cost is negligible. The main cost is engineering and platform integration, not inference.
- **security:** The mode must be local-first and fail closed: if the relay or calendar is unavailable, do not expose new content or execute browser mutations. Maintain an allowlist of urgent senders/categories, never infer urgency from sensitive message bodies unless enabled, and show a dashboard audit of every suppressed, allowed, paused, and restored action. Restoration must not reopen a window or tab that the owner closed during the meeting.
- **missing:** A shared presence/mode state service with signed, expiring leases and an explicit owner override.; Mac APIs for transactional notification suppression, window privacy/minimization, and restoration snapshots.; Browser job cancellation/pause semantics that preserve session and step state without submitting partial mutations.; Pendant policy enforcement for silent haptics/LED and urgent-only delivery.; A deterministic urgency allowlist and an end-of-meeting reconciliation job.


## Changes it proposed to its own stack

### `mac-harness` — Implement the already-granted mac_readonly_inspect and mac_read_sources contracts as real bounded adapters. Add a meeting-context snapshot endpoint that atomically returns foreground app, browser tab metadata, accessibility UI summary, and redacted Calendar/Mail references, with source timestamps and a hard byte/token cap; expose an explicit capture_event operation that records only a user-triggered timestamp plus context hashes.
- **owner gets:** The owner can say “mark that” without the Mac stealing focus, and later see exactly which page or document the note referred to. It also makes workday briefs and browser follow-ups grounded in current state instead of guesses.
- effort: Medium: native macOS adapters for Calendar/Mail/accessibility/browser bridge, schema validation, redaction and tests across Safari/Chrome; then relay job integration.  ·  risk: Accessibility and browser APIs may return stale or sensitive content. Fail closed to metadata-only, show freshness and source, and keep the event locally queued if the bridge is unavailable. Do not use arbitrary shell or microphone capture.
- cost: No meaningful per-event API cost; implementation is engineering work. Background summarization remains the dominant ongoing cost.  ·  latency: Snapshot target under 2 seconds; metadata-only fallback under 300 ms.
- security: Read-only scopes, explicit user trigger, local-first storage, redaction by default, and no continuous audio. URLs and snippets must be treated as sensitive and TTL-limited.
- depends on: A durable relay job/event queue; Browser tab/session affinity from the existing browser bridge; Pendant explicit event trigger/offline queue

### `hardware` — Replace the prototype's single-button interaction with a dedicated, textured “mark” button (or a distinct double-click gesture) and add a tiny confirmation vibration/LED pattern. Keep the event payload to button timestamp and a monotonic sequence number; the Mac/relay attach context later.
- **owner gets:** The owner can mark a decision in a meeting silently and reliably, even when speech would be disruptive or the network is down. Tactile confirmation prevents uncertainty and avoids continuous microphone recording.
- effort: Low-to-medium hardware revision plus a small Zephyr input/event-queue firmware path; validate accidental-press resistance and pocket ergonomics.  ·  risk: Accidental marks or confusing the control with the existing button. Use a recessed/textured switch, configurable long-press, and local undo for the last event. If vibration is unavailable, use LED only.
- cost: Roughly $1–$4 in switch/actuator and PCB/enclosure changes at prototype volume; a few mW only during confirmation, negligible standby impact.  ·  latency: Local confirmation under 100 ms; queued event survives link loss.
- security: Improves privacy by making capture explicit and non-audio. Store only bounded event records, not speech.
- depends on: A durable pendant event queue and retry protocol; Mac meeting-context snapshot implementation; Relay meeting session coordinator

### `integration` — Add a signed, expiring cross-surface Presence Policy Lease. Calendar/explicit owner commands create a lease containing mode, start/end, allowed urgency classes, and restoration snapshot IDs; relay, Mac, and browser must acknowledge it before changing behavior. Every suppression, pause, delivery, and restore emits an idempotent receipt, and a crash-safe reconciler resolves leases that expire while a node is offline.
- **owner gets:** The owner gets one dependable privacy boundary instead of three loosely coordinated do-not-disturb switches. A laptop crash or lost pendant connection will not leave browser automation running forever or notifications permanently suppressed.
- effort: Medium-to-high protocol and adapter work across relay, Mac notification/window controls, browser job runner, and pendant policy handling; requires failure-injection tests for disconnects and overlapping meetings.  ·  risk: A stale lease could suppress an important alert or fail to restore the owner's workspace. Use short expiries, explicit emergency override, immutable pre/post snapshots, and a visible recovery control. Never auto-submit or delete anything during reconciliation.
- cost: Negligible runtime/API cost; durable receipts and snapshot metadata add modest storage. Engineering complexity is the principal cost.  ·  latency: One coordination round adds roughly 100–500 ms locally; event-driven transitions still complete within seconds.
- security: Signed scope-limited leases prevent one surface from impersonating another; sensitive window contents remain local, while the relay receives only mode and urgency metadata by default.
- depends on: A browser runner with pause/resume and idempotent receipts; Mac notification/window-control adapter; Pendant policy update channel; Calendar event or explicit-command trigger


## What it asked for

_Nothing._
## Its own summary

Proposed a new cross-node capability: explicit “mark that” meeting moments. A tactile pendant event is queued locally, the Mac captures bounded foreground/browser/document context without taking focus, and the relay produces a sourced follow-up packet after the calendar event—without continuous audio or automatic sending. Also proposed implementing the currently granted but nonfunctional mac_readonly_inspect/mac_read_sources contracts and a dedicated tactile mark control on the pendant. What I still need is not another permission: the missing implementations are the blocker, especially the read-only Mac context snapshot, durable event/job queue, and pendant explicit-event firmware path.

**Biggest unknown:** Whether the browser bridge can expose the active tab's selected/visible text and stable session identity through a bounded read-only API; without that, meeting marks can retain only app/title/URL metadata rather than precise evidence.

