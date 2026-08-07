# Harness derivation — unified — round 41

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Start this from my pendant, and if anything changes while I’m away, tell me exactly what changed before you continue.”"
- **useful because:** A real cross-surface walk-away workflow: the pendant captures the owner’s intent and approval, the relay keeps a durable task capsule while the Mac sleeps or loses connectivity, and the browser/Mac re-attach to the same tab and checkpoint. It is safer than merely running a background job because it detects semantic drift (changed price, recipient, appointment, or form values) and pauses with a concise before/after diff delivered to the pendant.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the realtime model only for the initial spoken intent, ambiguity questions, and short drift alert. Use a cheaper background model for step planning, page-diff normalization, and completion receipts; deterministic code should enforce checkpoints and idempotency.
- **latency:** Initial acknowledgement under 1.5 s; normal checkpoint comparison under 3 s after reconnect; drift alert can arrive asynchronously within 30 s. The owner can walk away without holding a live session open.
- **cost:** Roughly $0.01–$0.05 per ordinary task depending on page extraction; most work is deterministic browser snapshots and a small background summarizer. Realtime cost is limited to a few short utterances and one alert.
- **security:** Private page text and before/after diffs remain on the Mac/relay unless explicitly sent to the model. Never log secrets or full form values. Any irreversible submit, send, purchase, or deletion requires an explicit pendant confirmation against the current fingerprint; if the page, account, or target changes, refuse to continue and retain the prior evidence.
- **missing:** A durable task-capsule/checkpoint schema shared by relay, Mac, and browser, including semantic fingerprints and expiry; Browser reattachment that can return a typed current snapshot and bounded before/after diff for a tab; A pendant confirmation protocol that binds approval to the current snapshot hash, not merely to a spoken task id; Offline/reconnect handling and a dashboard showing paused, drifted, and completed capsules

### "“When I say something that commits me to a date, person, or promise, check my private sources and tell me if anything disagrees before I rely on it.”"
- **useful because:** This gives the owner a personal consistency check that no single surface can provide: the pendant captures a spoken commitment in the moment; the relay preserves it; the Mac searches local Calendar/Mail/Notes; and the authenticated browser checks relevant private portals. It reports contradictions such as a meeting actually scheduled for Thursday, a promised delivery already canceled, or a reply sent to a different recipient—without silently editing anything.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only transcribes the short spoken commitment and asks a clarification when the person/date/object is ambiguous. A cheaper background model extracts entities and compares normalized commitments with local and authenticated-source evidence; deterministic code handles dates, provenance, and conflict severity.
- **latency:** Acknowledge the capture in under 1.5 seconds. Run the private-source reconciliation asynchronously in under 2 minutes, then deliver a short pendant alert and a cited dashboard card. No action is taken automatically.
- **cost:** About $0.01–$0.04 per check; most work is local deterministic date/entity matching and bounded page reads, with a small background summarization call only for ambiguous conflicts.
- **security:** Commitments and evidence are highly private. Keep raw audio and source text on the pendant/Mac where possible, send only minimized entity queries to the relay/model, encrypt the durable record, apply a short default retention, and let the owner delete it. Never contact anyone or alter a calendar/task; any suggested correction must be a draft requiring explicit approval. Distinguish a true contradiction from stale or low-confidence evidence and show source timestamps.
- **missing:** A commitment object and evidence graph distinct from ordinary reminders or page watches, with expiry and confidence; A local Mac connector that searches Calendar, Mail, Notes, and reminders by extracted entities and timestamps; A browser connector that can query owner-approved authenticated portals for the same commitment; A conflict-ranking and citation UI/audio format that can state exactly which sources disagree without leaking their contents aloud


## Changes it proposed to its own stack

### `hardware` — Replace the prototype’s single LED-only feedback with a production pendant input/output package: a low-power coin haptic motor plus a distinct confirm/cancel gesture (for example, short press confirms the displayed capsule hash and long press rejects), while retaining the existing button and adding a small RGB/status LED only if enclosure power permits. The relay sends a signed, truncated task-fingerprint challenge; firmware renders a pattern and will emit a confirmation token only for that challenge, with a timeout and no audio requirement.
- **owner gets:** The owner can safely approve or reject a changed browser transaction while walking, in a meeting, or when the speaker is muted—without unlocking a screen or saying a sensitive command aloud. A vibration pattern makes “paused because the page changed” different from ordinary completion, reducing accidental approvals.
- effort: Production enclosure/electrical redesign, haptic driver and button gesture firmware, signed challenge/response protocol in relay and Mac/browser bridges, accessibility testing for users who cannot feel or press the chosen gesture, and end-to-end fault-injection tests.  ·  risk: False or missed gestures could block work or, worse, be interpreted as approval. Default must be fail-closed; require a deliberate hold-plus-release for irreversible actions, expire challenges quickly, and show a receipt. If the motor fails, fall back to spoken/screen confirmation rather than silently proceeding.
- cost: Approximately $2–$8 incremental BOM (motor, driver, optional RGB LED, enclosure changes) and roughly 5–20 mA only during a short haptic pulse; negligible steady-state draw. No per-call model cost; a small background-model cost remains for semantic diffs.  ·  latency: Local feedback under 100 ms; signed confirmation round trip typically under 1 s on an available link. Hardware wake/pulse adds negligible delay.
- security: Improves security by binding physical presence to an exact current snapshot hash. Must use a device key or secure element in the production design; do not treat a button event or BLE/NFC replay as approval, and never encode sensitive form data in LED/haptic patterns.
- depends on: Durable cross-surface task capsule and semantic fingerprint service; Browser/Mac typed current-snapshot endpoint; Production pendant secure-key and power-budget decision; A documented irreversible-action approval policy

### `dashboard-ux` — Add a single owner-facing preflight panel and spoken preflight response generated from live /ops/status: show which surfaces are online, which permissions block which action class, pending browser commands, and whether vision consent is available. Before a task starts, the relay/Mac planner should automatically downgrade to a safe read-only route or ask one precise repair question (for example, reconnect Chrome or enable Accessibility), rather than accepting work that will later stall.
- **owner gets:** Today the Mac bridge is online but the browser is offline, Accessibility and Screen Recording are untrusted, vision upload consent is false, and three browser commands are pending. The owner should hear “I can read Mac apps, but your logged-in browser is disconnected; reconnect it?” instead of experiencing a silent failure or an opaque queued job.
- effort: Define capability-to-precondition mapping, implement a signed compact status projection for pendant speech and dashboard, add stale-command reconciliation, and test fallback paths (read-only, local-only, queued). Do not expose raw paths, tokens, or private tab text.  ·  risk: Status can become stale between preflight and action; include timestamps, short leases, and re-check immediately before each irreversible step. Avoid permission prompts that disclose sensitive app names in public audio; offer a private dashboard detail view.
- cost: Negligible model cost for deterministic checks; occasional cheap summarization for a human sentence. No hardware cost.  ·  latency: Adds under 300 ms for a local status check; avoids much longer failed runs.
- security: Reduces accidental execution under missing permissions and makes privacy/consent state explicit. Keep detailed permission diagnostics local to the Mac and send only a capability summary to the relay/pendant.
- depends on: Typed capability/precondition registry across relay, Mac, and browser; Browser heartbeat and pending-command reconciliation; Owner privacy policy for spoken readiness alerts


## What it asked for

_Nothing._
## Its own summary

Discovered the live fleet and added three new items: (1) a cross-surface task capsule that revalidates browser/Mac state after interruption and pauses on semantic drift, (2) production pendant haptic/physical approval bound cryptographically to the current task fingerprint, and (3) an owner-facing live preflight/readiness panel and spoken fallback. Live evidence: Mac bridge and relay are reachable, but Chrome is offline with 3 pending commands; Accessibility and Screen Recording are not trusted; vision upload consent is false; overall agent readiness is false. The pendant pipeline is already surfacing held offline alerts, so the next step is to extend that proven path to drifted task capsules rather than invent another notification queue.

**Biggest unknown:** The orchestrator still has not surfaced the requested production pendant constraints, audio acceptance criteria, authoritative timezone, queued-action resume policy, or the implementation tools/permissions needed to wire the capsule and physical approval end to end. The browser’s reconnect behavior and exact owner privacy boundary also remain unspecified.

