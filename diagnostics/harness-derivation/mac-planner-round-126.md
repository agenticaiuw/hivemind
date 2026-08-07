# Harness derivation — mac-planner — round 126

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/relay/browser readiness round 126** — Mac agent and relay are reachable, but browser extension is offline with 9 pending commands; Accessibility and Screen Recording are not granted; computer-use loop disabled. Automation grants exist for Calendar/Mail/Notes/System Events, so non-UI scripted reads remain possible.
  - evidence: GET /ops/status HTTP 200 at 2026-08-07T14:04Z: browser.online=false, pendingCommands=9, accessibility.trusted=false, screenRecording.granted=false, automation grants true, macBridgeOnline=true.

## Capabilities it proposed

### "“I’m focusing now.” (press pendant button) — silence routine browser/calendar noise until I press again, but interrupt me for genuinely urgent items; when focus ends, give me one short catch-up."
- **useful because:** The pendant is the only always-present, low-friction intent signal; the relay is always awake; the Mac knows its actual Focus state and local notifications; the browser knows which authenticated page changes matter. Together they provide a reliable interruption boundary instead of another calendar-only meeting mode. It must restore the exact prior Mac state after expiry or a dropped link.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the button acknowledgement and urgent interrupt decision; a cheap background model ranks queued changes and writes the catch-up. Deterministic rules handle TTL, deduplication, and restoring state.
- **latency:** Button acknowledgement under 300 ms; Focus application/restore under 2 s; urgent interrupt under 5 s; catch-up can arrive asynchronously when focus ends.
- **cost:** About $0.001–$0.01 per focus window, dominated by background summarization; routine state transitions and deduplication are local/server compute.
- **security:** Do not transmit page bodies by default—send only source, timestamp, severity, and a short redacted snippet. Never auto-send or submit browser actions. Store the prior Focus configuration and lease expiry, encrypt it, and expire it. Require explicit button press to end early; on relay/Mac failure fail open to the owner's prior notification state, not a permanently muted state.
- **missing:** A pendant-side focus-window button/LED skill with offline acknowledgement and a pending-event bit; A relay focus-lease state machine with TTL, idempotent start/stop, reconnect reconciliation, and urgent-event policy; Mac integration that snapshots and restores the exact Focus/notification state without Accessibility; Browser page-watch results normalized into urgent-vs-queued signals; A small dashboard showing active lease, expiry, queued count, and restoration receipt

### "“Continue this on my Mac.” — hand the current pendant conversation to the Mac as a private, one-time continuation: open the relevant app or authenticated browser tab, place a concise task capsule where I can see it, and let me say “back” to return the result to the pendant."
- **useful because:** Today the owner must repeat the task, find the right app or tab, and reconstruct context when moving from voice to desktop. This creates a secure handoff between the device that heard the intent and the machine that can show and edit the work, without dumping the entire conversation into a document or exposing unrelated private context.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime handles only the short handoff acknowledgement and return command. A cheaper background model compiles the minimal task capsule and extracts the final result; deterministic code handles token expiry, app/tab targeting, and receipts.
- **latency:** Acknowledge the handoff within 500 ms; Mac opens the target within 3 seconds; return a result within 2 seconds after the owner says “back,” excluding long-running work.
- **cost:** Roughly $0.002–$0.02 per handoff, dominated by capsule compilation and result summarization; transport, routing, and local file/UI actions are negligible.
- **security:** Use a single-use, short-lived handoff token bound to the paired pendant and Mac session. Send only the selected task capsule, never the raw transcript by default. Do not copy secrets into clipboard or files; redact sensitive entities and show the capsule destination. Browser actions remain read/draft-only unless separately requested, and the handoff expires if the Mac does not accept it.
- **missing:** A relay handoff protocol that issues one-time capability tokens and tracks accepted/completed/expired states; A compact context-capsule compiler with explicit source references and redaction; A Mac receiver that resolves the capsule into an app, file, or authenticated browser tab and reports a typed receipt; A pendant return event that fetches the result without reopening the microphone; A dashboard view showing active handoffs and allowing revocation

### "“Let me know silently when it’s done.” — after I hand a long Mac or browser task to you, give the pendant a distinct haptic pattern for completed, needs-attention, or failed, and let a button press replay a one-sentence status."
- **useful because:** The owner should not need to keep checking the Mac or open the microphone while walking, in a meeting, or listening to something else. A tactile receipt turns asynchronous work into an ambient signal, while keeping potentially sensitive content off the pendant speaker until explicitly requested.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** No realtime model is needed for completion classification. Deterministic receipt mapping handles completed/attention/failed; a cheaper background model produces the optional one-sentence spoken status.
- **latency:** Haptic notification within 2 seconds of a terminal receipt; button status replay begins within 500 ms.
- **cost:** Under $0.001 per event; almost entirely device and relay computation, with optional status summarization costing a fraction of a cent.
- **security:** Haptics reveal only a coarse state, not task content. Do not speak sensitive details without the explicit replay press. Bind notifications to the paired device, deduplicate receipt IDs, and expire stale notifications so a later owner does not receive misleading signals.
- **missing:** Pendant firmware haptic pattern queue with persistence across link loss and bounded flash use; Relay subscription that converts Mac/browser terminal receipts into device notifications; A stable receipt taxonomy shared by /jobs receipts, browser results, and failures; A button event to request the latest status and a delivery acknowledgement


## Changes it proposed to its own stack

### `integration` — Implement a cross-surface Focus Lease protocol, not another briefing: FocusLease {leaseId, owner, startedAt, expiresAt, priorMacNotificationState, deliveryPolicy, queuedEventIds, version}. The relay is authoritative for lease state; pendant start/stop events are idempotent and can queue offline. Mac applies the lease through a non-Accessibility notification/Focus integration, reports applied/restored receipts, and reconciles after reconnect. Browser watchers publish only normalized severity events; the relay deduplicates them and releases a single catch-up bundle on restore. Expiry, crash, and duplicate button presses must converge to the saved prior state.
- **owner gets:** One press creates a dependable, temporary interruption boundary across the devices the owner already uses, and one short catch-up replaces a pile of notifications. It remains safe if the Mac sleeps, the radio drops, or the owner forgets to end focus.
- effort: Medium: protocol and relay state machine, Mac Focus adapter and restore tests, browser event adapter, pendant event persistence, plus dashboard visibility.  ·  risk: A stale lease could suppress an important alert or fail to restore notifications. Use a hard maximum TTL, urgent bypass rules, visible pendant expiry indication, persisted prior-state snapshots, and a reconciliation job. If state is uncertain, restore notifications rather than keep them muted.
- cost: Negligible storage/compute; roughly <$0.001 per transition. Background catch-up summarization is the only model cost.  ·  latency: Sub-second relay state change; 1–2 seconds for Mac apply/restore; no impact on ordinary conversation.
- security: Lease metadata and event IDs may leave the Mac; page content stays local unless explicitly requested. Treat notification titles/snippets as sensitive, redact by default, and delete queued events at lease expiry plus retention window.
- depends on: A real pendant offline event/LED skill (offline_attention_window_toggle is still pending); A relay-side lease endpoint and reconnect reconciliation; A Mac Focus adapter that works without Accessibility permission; Browser watcher output in a typed severity/event schema

### `firmware` — Add a durable notification mailbox on the pendant for typed external receipts. It stores at most 8 compact records (receipt ID, coarse state, timestamp, retry count), renders three distinct haptic patterns, acknowledges delivery to the relay, survives a dropped link, and exposes a single-button 'latest status' request. It must never store transcript text or page content, and must coalesce duplicate receipt IDs.
- **owner gets:** Long-running work can finish without the owner staring at the Mac or listening continuously; the pendant quietly tells them whether to continue walking, check something, or review a failure.
- effort: Small-to-medium firmware change plus relay protocol and integration tests; requires validating haptic actuator timing and flash wear limits on the actual pendant.  ·  risk: A missed or repeated vibration could cause confusion. Use sequence numbers, a bounded mailbox, explicit delivery acknowledgements, a periodic expiry, and a neutral pattern when state is unknown.
- cost: Negligible API cost. Firmware power impact is limited to short haptic pulses and occasional radio packets; no new hardware assumed until the pendant actuator spec is verified.  ·  latency: Terminal receipt to haptic target under 2 seconds while connected; queued delivery on reconnect.
- security: Only coarse status leaves the Mac. No transcript, notification title, URL, or file name is stored on the pendant.
- depends on: A shared terminal receipt taxonomy across Mac jobs and browser commands; Relay-to-pendant notification delivery and acknowledgement route; Actual pendant haptic actuator/storage limits and offline event queue implementation


## What it asked for

_Nothing._
