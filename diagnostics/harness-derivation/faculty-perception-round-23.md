# Harness derivation — faculty-perception — round 23

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-ui-reachability-2026-08-07T10:00Z** — Mac bridge is online, but AI Pendant Agent is not Accessibility-trusted; input reachability probe failed and ui_actions/type_text/press_keys can report success while doing nothing. Screen Recording is also not granted, so mac-vision cannot safely observe the screen.
  - evidence: GET /observe at 2026-08-07T10:00:14Z: accessibility.trusted=false, eventsPost=false, uiActionsWillReachTheScreen=false, inputReachability.status=failed, screenRecording=false; GET /ops/status independently reports ready=false and the same missing permissions.
- **cross-surface-availability-2026-08-07T10:00Z** — At observation time the Mac bridge and relay are reachable, but the authenticated browser extension home-chrome is offline with 2 pending commands; three durable browser sessions remain listed on the Mac, including time.is/UTC and two test forms.
  - evidence: GET /ops/status and GET /browser/status at 2026-08-07T10:00Z: browserExtension.online=false, pendingCommands=2; GET /observe: browser sessions=3 and listed tabs.
- **audio-path-2026-08-07T10:00Z** — A recent cloud-relay response completed the 24 kHz TTS path end-to-end: 164,650 PCM bytes, 3.43 s, 24,000 Hz mono, no clipping, then accepted by relay for pendant download. The same pipeline also shows offline pendant-held alerts/bookmarks surfacing from microSD after reconnect.
  - evidence: GET /pipeline at 2026-08-07T10:00Z: job_165a9c9a... events show TTS done with sampleRate=24000, pcmBytes=164650, clippedSamples=0 and relay_result done; jobs job_27616bb... and job_e8a8... show alert_delivered from pendant-offline-store, and job_cdb... shows bookmark held on microSD.

## Capabilities it proposed

### "Before you do anything on my computer, tell me whether you can actually reach the screen, browser, and pendant right now—and if not, say exactly what is blocked instead of claiming it worked."
- **useful because:** Today the Mac agent can emit successful-looking UI receipts even when Accessibility is not granted, the browser extension is offline with queued commands, and screen observation is unavailable. A cross-surface preflight would prevent silent no-ops and let the owner fix one concrete prerequisite. It uses perception (permission and link evidence), judgement (choose a safe route), and action (only proceed when evidence is sufficient), rather than pretending a receipt proves the world changed.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** deterministic preflight for permissions, heartbeats, session freshness, and device status; background model only to translate the structured result into a concise explanation. Realtime is reserved for the spoken response.
- **latency:** Under 500 ms for local Mac/relay status checks; up to 2 s if a browser heartbeat or pendant link check is needed. Never delay a clearly safe offline note or ask the owner to retry blindly.
- **cost:** Near-zero for deterministic checks; roughly 200–500 background-model tokens only when a human explanation is needed. Dominant cost is not inference but a browser/relay round trip.
- **security:** Expose only capability state and redacted diagnostics (never tokens, URLs from private tabs, or secret captures). Screen screenshots require explicit vision consent. A preflight must not itself click, type, send, or clear pending browser commands; any stale queued command should be surfaced for review.
- **missing:** A shared typed preflight contract consumed by relay voice, Mac planner, browser runner, and dashboard, with evidence timestamps and per-surface states (reachable, authorized, observable, actionable).; A hard guard in action execution that refuses to label UI steps successful when Accessibility/inputReachability is false.; An explicit browser pending-command policy: inspect, retry, or discard only after owner confirmation.; A small pendant/relay status verb so the owner can hear the result without opening the dashboard.

### "When my pendant reconnects, let me ask 'what happened while you were offline?' and hear a complete, deduplicated catch-up: every held alert, bookmark, and reply, with when it occurred, whether it was already surfaced, and an option to acknowledge each item or replay its audio."
- **useful because:** Today the pendant can surface held alerts and bookmarks, but the owner cannot reliably inspect the full offline interval, distinguish newly delivered items from repeats, or acknowledge/replay them as a coherent catch-up. This is uniquely cross-device: the pendant owns offline capture on microSD, the relay owns delayed delivery, and the Mac/dashboard can reconcile job and audio records; no single node can reconstruct and present the whole continuity story.
- **path:** pendant → relay → mac-planner → dashboard → unified
- **model tier:** Deterministic event ledger and deduplication first; use a cheap background model only to produce a short spoken grouping such as alerts, bookmarks, and completed replies. Realtime is used only for the live question and playback control.
- **latency:** The first spoken summary should begin within 2 seconds of reconnect or the question; event reconciliation can continue in the background. Replay starts as soon as the selected audio object is available.
- **cost:** Near-zero inference for event joins, hashes, and acknowledgement updates; approximately 300–800 background-model tokens for a natural-language spoken summary. Storage and audio transfer dominate cost, not model calls.
- **security:** Offline content may contain private speech, links, or secrets. Encrypt or access-control the microSD event index and relay objects, retain only configured TTL, and show sensitive-item titles only after explicit owner request. Acknowledge must be idempotent and must never delete the source until retention and replay policy permit it.
- **missing:** A durable continuity event schema shared by nRF9160 offline storage, relay D1, Mac pipeline, and dashboard: event ID, origin, capture time, delivery time, surfaced time, acknowledgement state, content/audio references, and sensitivity.; Clock-skew and reconnect ordering rules, plus content hashes/idempotency keys so an alert forwarded twice is presented once.; Pendant commands for list, acknowledge, and replay-by-event, with resumable audio download and a bounded local index.; A spoken catch-up intent and dashboard timeline that can filter unacknowledged, newly arrived, or audio-backed events.


## Changes it proposed to its own stack

### `integration` — Add a read-only preflight/evidence envelope to every cross-surface job. Immediately before execution, snapshot Mac permission/input reachability, screen-observation availability, browser extension heartbeat and pending-command count, relay/pendant link state, and relevant session freshness. Attach the envelope and its timestamp to the job; after execution, require a postcondition observation (or explicitly mark unverifiable) before a receipt can say completed. Keep the existing action APIs, but make the envelope mandatory input to planner and dashboard.
- **owner gets:** The owner gets an honest answer when the machine cannot be acted on: 'browser offline, 2 commands waiting' or 'Accessibility missing; nothing was changed' instead of a misleading success. When it does work, the receipt says what was observed afterward, not merely what the agent attempted.
- effort: Medium: typed schema, Mac/relay collectors, job persistence, planner integration, and dashboard rendering; one to two implementation cycles.  ·  risk: Status can become stale between preflight and click, or a postcondition may be impossible for actions like sending an email. Recover by timestamping every field, distinguishing observed/assumed/unverifiable, and using idempotency plus the existing undo path. Never block reversible non-UI work solely because screen observation is unavailable.
- cost: Negligible API cost; a few hundred bytes per job in D1 and occasional status requests. No hardware cost.  ·  latency: Adds roughly 100–500 ms for local checks and up to one heartbeat round trip; postcondition checks may add 0.5–2 s only for UI jobs.
- security: Improves safety by preventing false success. Must redact private URLs, tokens, screenshots, and secret capture values from shared envelopes; retain only capability booleans, timestamps, and reason codes.
- depends on: A shared typed context/preflight contract across relay, Mac planner, browser runner, and dashboard; A hard action-layer rule preventing success receipts when uiActionsWillReachTheScreen=false; An explicit policy for browser pending commands and unverifiable postconditions


## What it asked for

_Nothing._
## Its own summary

Fresh perception is complete. At 10:00Z the Mac bridge and relay are online, but Accessibility/input reachability and Screen Recording are unavailable, so UI actions and screen-based verification are not trustworthy. The browser extension is offline with two pending commands. Conversely, the 24 kHz mono TTS response path completed end-to-end with no clipping, and pendant-held alerts/bookmarks were surfaced after reconnect. I recorded these three facts and proposed a cross-surface deterministic preflight plus postcondition evidence envelope that prevents false success receipts.

**Biggest unknown:** I still lack direct live pendant/firmware diagnostics and the continuity-event retention/acknowledgement semantics. Those are needed to know whether the pendant can truthfully announce preflight failures and whether held alerts/bookmarks can be deduplicated and acknowledged safely. I also need the pending action-layer confirmation of whether an existing hard gate already blocks UI actions when reachability is false.

