# Harness derivation — faculty-perception — round 66

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-observation-2026-08-07T12:29Z** — Mac foreground app is Claude (com.anthropic.claudefordesktop, pid 55646); AI Pendant Agent is running (pid 25245). Accessibility trusted=false, screenRecording=false, inputReachability=failed; UI actions cannot be trusted. AppleScript automation grants are present for System Events, Finder, Calendar, Mail, Notes, Messages, Safari, Chrome, and others.
  - evidence: GET /observe at 2026-08-07T12:29:41Z returned foreground/runningApps and accessibility/inputReachability fields.
- **fleet-connectivity-2026-08-07T12:29Z** — Mac bridge and relay are reachable/online, but browser extension home-chrome is offline with 5 pending commands and zero attached tabs. Computer-use loop is disabled and vision upload consent is false.
  - evidence: GET /ops/status at 2026-08-07T12:29:41Z returned relay.macBridgeOnline=true, browserExtension.online=false pendingCommands=5, computerUse.loopEnabled=false visionUploadConsented=false.
- **machine-timezone-2026-08-07** — Mac machine-context reports timezone America/New_York.
  - evidence: GET /machine-context HTTP 200 body machine.timezone=America/New_York.
- **pipeline-state-inconsistency-2026-08-07T12:30Z** — GET /pipeline contains a run from nrf9160 created 2026-08-07T07:22Z still marked processing although its sole alert_delivered event is done, and another cloud-relay run marked processing whose relay agent event says reply forwarded after reconnection. A completed 12:00 run reached relay_result done and generated 24 kHz mono PCM (75,734 bytes), but also contains a waiting-for-approval event for a shell command.
  - evidence: GET /pipeline HTTP 200 at 2026-08-07T12:30Z; returned run statuses and event timelines above.

## Capabilities it proposed

### "Before you do anything, tell me what you can actually see and control right now—and warn me if any result could be a false success."
- **useful because:** The owner currently has a dangerous split-brain state: the Mac bridge and relay are online, but the browser is offline, GUI input is unreachable, and the agent explicitly says UI actions may report success while doing nothing. A spoken, cited preflight lets the owner choose a reachable path instead of trusting a phantom completion.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for periodic health snapshots; realtime only to summarize the snapshot during a live request
- **latency:** Under 1 second from cached health; refresh only stale surfaces in parallel, with a 3-second ceiling and explicit unknowns on timeout
- **cost:** Near-zero for cached route reads; roughly one cheap text-model call only when converting a multi-surface snapshot to owner language. Dominant cost is context transfer, not probes.
- **security:** Do not include page bodies, secrets, or private capture values in the snapshot. Report capability state, timestamps, and provenance hashes only. Never imply an action is safe merely because a route is reachable; mark UI receipts untrusted when Accessibility/Screen Recording are absent.
- **missing:** A typed cross-surface observation contract with freshness TTL, provenance hash, and trust level (observable/actionable/receipt-trustworthy) for pendant, relay, Mac, and browser; A planner precondition that consumes this snapshot and blocks claims of completion when the relevant surface is stale or untrusted; A pendant/dashboard card and concise spoken rendering of the preflight result

### "Only interrupt me when I can actually receive it: route an important alert through my pendant, check my Mac's current activity and calendar, wait through a quiet window when appropriate, then escalate until I acknowledge it—or explain exactly why delivery was not possible."
- **useful because:** Today the system can generate speech and queue alerts, but it cannot make a trustworthy, cross-device decision about whether an interruption reached the owner, whether the owner was busy, or whether an unacknowledged alert should escalate. This would prevent both missed urgent information and repeated interruptions at the wrong moment.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background/rules for scheduling, freshness checks, and escalation; realtime only for the brief spoken alert and acknowledgement conversation
- **latency:** Initial routing decision under 2 seconds; delivery acknowledgement window configurable (for example 30 seconds), with escalation bounded by the owner's quiet hours and urgency policy
- **cost:** Usually no model call: event routing, calendar lookup, and acknowledgement state are deterministic. One cheap text call only for summarizing a complex alert. Realtime cost occurs only when the owner answers.
- **security:** Alert content must be encrypted in transit and minimized in relay storage. Calendar/activity signals should be reduced to busy/free and app category, not raw private text. Escalation destinations require explicit setup; never send an alert to another person without confirmation. Keep a tamper-evident delivery/acknowledgement record.
- **missing:** A durable urgency policy and escalation graph shared by relay, Mac, and pendant; A trustworthy pendant delivery acknowledgement primitive (heard/pressed/expired), distinct from audio generation or relay receipt; A Mac activity/quiet-window projection that exposes only busy/free, calendar conflict, and safe-to-interrupt state; A durable alert state machine with deduplication, retry budgets, quiet hours, and owner-visible delivery receipts


## Changes it proposed to its own stack

### `context` — Add a signed, append-only cross-surface Reality Ledger. Every observation from /observe, /ops/status, /browser/status, /pipeline, relay health, and pendant telemetry becomes a compact record {surface, capability, observedAt, expiresAt, status, trustLevel, provenanceHash}; planners must attach the ledger record IDs to any claim about visibility, control, or completion. A receipt is downgraded to untrusted when its precondition was absent (for example inputReachability.failed), and stale records are rendered as unknown rather than reused.
- **owner gets:** The owner stops hearing confident answers based on contradictory or stale machine state. If the browser disconnected or GUI input was never trusted, the pendant can say so immediately and suggest a reachable alternative; if a result is real, it can cite when and how that was established.
- effort: Medium: define the schema and TTL policy, implement a small relay/D1 or Mac-local ledger writer, add planner validation and dashboard rendering, then test disconnect/reconnect and stale-receipt cases.  ·  risk: Overly short TTLs could cause unnecessary retries; overly long TTLs recreate false confidence. Recover by treating missing/expired records as unknown and allowing explicit re-probe. Keep records metadata-only to avoid leaking page content.
- cost: Negligible storage and probe cost; one compact metadata record per event. Optional cheap summarization call; no realtime call required for ledger maintenance.  ·  latency: Parallel health reads add under ~300 ms when fresh; planner validation is local. Stale refresh may add up to 3 seconds but can return partial truth with explicit unknowns.
- security: Provenance hashes must be non-reversible and records must exclude secrets/page bodies. Ledger access should be scoped by session and redact sensitive capability names where needed.
- depends on: A typed observation schema and trust-level definitions; Planner precondition/claim validation hook; Relay or Mac-local durable metadata store; Owner-facing dashboard/pendant renderer

### `integration` — Add an event-derived pipeline truth reconciler: compute effective state from ordered events (done, blocked-awaiting-approval, failed, delivered) instead of trusting the mutable top-level status. Mark runs with contradictory states as `inconsistent`, preserve both raw and effective status, and emit a compact unresolved-approval/late-delivery observation for judgement and the pendant.
- **owner gets:** The owner will no longer be told that a seven-hour-old pendant alert is still processing, or miss that a supposedly completed job is actually waiting for approval. Spoken updates can distinguish delivered, blocked, and genuinely running work.
- effort: Small-medium: define precedence and terminal-state rules, add a reconciler on read/write, migrate dashboard and relay-job summaries, and cover reconnect/late-event tests.  ·  risk: Out-of-order events can be misclassified. Recover with event timestamps plus a short settling window, and retain raw events for audit; expose `inconsistent` rather than guessing when precedence is ambiguous.
- cost: Negligible compute/storage; no model call needed.  ·  latency: O(events) per pipeline read, likely milliseconds; optional settling delay only for active runs.
- security: Metadata-only; do not copy audio, page content, or secret payloads into the derived status. Preserve existing session scoping.
- depends on: Stable event IDs and timestamps in pipeline records; A shared terminal-state enum consumed by relay_job_status and dashboard; Reality Ledger observation records so derived status carries provenance

### `firmware` — Add a durable pendant alert-delivery handshake: when audio starts, firmware emits `presented` with sequence number; a short button press or voice-side interrupt emits `acknowledged`; timeout emits `unheard`; each event is buffered locally across link loss and replayed idempotently after reconnect. The relay must distinguish generated/uploaded/played/heard/acknowledged rather than treating upload as delivery.
- **owner gets:** The owner gets alerts that the system can prove were heard or honestly reports as missed, instead of silently losing an important message when the link, playback, or attention state fails. It enables safe escalation without duplicate alerts.
- effort: Medium firmware and relay protocol work, plus pendant button/audio event testing under disconnect, reboot, and replay. Requires a small persistent event journal and sequence-numbered acknowledgements.  ·  risk: A button press could acknowledge an alert the owner did not understand; expose a separate repeat/confirm gesture and allow the owner to replay. Power loss can interrupt playback; replay the last unacknowledged alert only under the configured urgency policy, with deduplication.
- cost: Very low API cost. Firmware storage is a small bounded event journal; negligible additional power except the existing playback and radio window. Hardware replacement is not required if the existing button can generate distinct gestures.  ·  latency: Presented/ack events add milliseconds locally and one short uplink when connected; disconnected events are deferred until reconnection.
- security: Use opaque alert IDs and authenticated sequence numbers; do not persist alert text in the journal. Acknowledgement metadata may reveal attention patterns, so retain it only for the owner's configured window.
- depends on: Relay alert state machine and escalation graph; An owner-defined meaning for acknowledged versus merely presented; A durable local event queue with replay and deduplication; Pendant button gesture handling that does not interfere with the existing primary action


## What it asked for

_Nothing._
## Its own summary

Fresh live perception established: Mac bridge/relay are online, but browser extension is offline with 5 pending commands; Accessibility and Screen Recording remain unavailable, inputReachability is failed, and GUI receipts are explicitly untrustworthy. Pipeline records also contradict their event histories: an old pendant alert is marked processing despite delivered, while another run is processing after forwarding, and a completed run contains an unresolved approval. I recorded these facts, informed judgement/planner, and proposed a cross-surface Reality Ledger plus event-derived pipeline truth reconciliation.

**Biggest unknown:** I still cannot observe the pendant's current local radio/audio/storage state or obtain an authoritative continuity snapshot: the requested pendant diagnostics, perception snapshot, and telemetry context have not arrived. I also need the owner to decide whether to reconnect/authorize the browser extension and whether to grant Accessibility/Screen Recording; until then GUI automation must remain classified as non-actionable and browser-private-page perception as unavailable.

