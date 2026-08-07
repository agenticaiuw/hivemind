# Harness derivation — faculty-perception — round 87

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live browser control channel** — At 2026-08-07T13:38Z the Chrome extension device home-chrome is offline (no tab/window/url, last seen 13:24Z), yet the Mac agent reports 9 pending browser commands. There is no live browser surface to acknowledge or execute them, so queue freshness/expiry and offline reconciliation remain unestablished.
  - evidence: GET /browser/status returned online:false, devices:[home-chrome online:false], pendingCommands:9; GET /ops/snapshot independently reports browserExtension.online:false and pendingCommands:9.

## Capabilities it proposed

### "When my browser reconnects, reconcile anything that was queued while it was offline, discard or quarantine stale work, and tell me exactly which actions are still safe to resume before doing any of them."
- **useful because:** Today the system can retain browser commands while Chrome is offline but cannot give the owner a trustworthy, cross-device answer about what those commands are, whether they are stale, or whether reconnecting will cause unexpected authenticated actions. This turns a hazardous silent replay into a reviewable recovery moment.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic queue/session validation and a cheap background model for summarizing held commands; reserve realtime only for the owner's live spoken approval or clarification.
- **latency:** On extension reconnect, produce a compact reconciliation within 1–3 seconds; do not replay anything until the owner approves held or destructive items.
- **cost:** Usually near-zero model cost for metadata checks; roughly $0.001–$0.01 only when a cheap model must summarize several held commands. Storage and relay event costs are negligible.
- **security:** Queued commands may target logged-in private sites and may contain destructive actions. Keep payloads local/relay-authenticated, bind each command to its original browser session/tab, enforce TTL and idempotency, quarantine destructive or context-changed actions, and require explicit confirmation before replay. Never infer approval from reconnect alone.
- **missing:** Offline queue reconciliation with enqueue age, TTL, session/tab binding, and action-risk classification; A reconnect handshake that returns command inventory and fresh tab identity before replay; A review receipt/voice prompt for held commands with explicit resume, discard, or re-plan choices; An owner-visible policy for how long reversible versus destructive commands may remain queued

### "Did that reply actually reach my wearable and finish playing, or was it only accepted by the relay? Give me a short, evidence-backed answer and tell me where it stopped."
- **useful because:** The current pipeline can report that the Mac rendered 24 kHz PCM and that the relay accepted it, but those facts do not establish that a physical pendant received, decoded, and played the audio. The owner needs delivery truth rather than a misleading success receipt, especially when the pendant is absent or offline.
- **path:** relay-realtime → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic telemetry correlation and state classification; use the inexpensive background model only to turn a multi-stage receipt into one short spoken sentence.
- **latency:** Return a receipt within 1 second after a device acknowledgement; if no acknowledgement arrives, mark it unresolved after a bounded timeout rather than claiming success.
- **cost:** Near-zero model cost when telemetry is typed; small relay storage/event cost per audio segment. No realtime inference is needed unless the owner asks follow-up questions.
- **security:** Receipts must contain opaque job/audio IDs, timestamps, device identity, codec/sample-rate, and delivery state without exposing audio contents. Do not claim physical playback from relay upload alone. Preserve a short-lived audit trail and allow deletion.
- **missing:** A device-side playback lifecycle protocol with received, decoded, started, completed, interrupted, and failed acknowledgements; Relay correlation of Mac render/upload IDs to device playback IDs, including timeout and duplicate detection; A typed owner-facing receipt endpoint that distinguishes rendered, relay-accepted, downloaded, and physically-played states; A real registered pendant to generate and verify the final playback acknowledgement


## Changes it proposed to its own stack

### `browser-harness` — Add an offline-queue reconciliation layer to the existing browser command queue: when home-chrome is offline, freeze commands rather than allowing blind replay; stamp each command with enqueue age, originating session/tab identity, and destructive/reversible class; expire or require fresh owner confirmation after a configurable TTL; on reconnect emit a compact review receipt listing 9 held commands and their intended targets before any replay.
- **owner gets:** The current bridge has 9 commands waiting behind an offline extension. This prevents an old click or form fill from happening unexpectedly when Chrome reconnects, while giving the owner one clear way to resume only still-relevant work.
- effort: Moderate: queue schema/migration, reconnect state machine, TTL policy, dashboard/voice summary, tests for offline/reconnect and duplicate delivery.  ·  risk: A legitimate long-running command could expire or be held; recovery is explicit resume/requeue from the review receipt. Must not silently discard commands.
- cost: Negligible API cost; small D1/local JSON metadata and one reconnect status event.  ·  latency: No impact while online; reconnect adds a brief reconciliation step before replay.
- security: Improves safety by preventing stale authenticated actions; session/tab binding and destructive-action reapproval are required.
- depends on: Existing browser command queue with request IDs/idempotency and tab/session affinity (chg-14accc01); GET /browser/status and POST /browser/heartbeat; Owner-facing review/approval surface for held commands


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: home-chrome is offline (last seen 13:24Z) while the Mac agent retains 9 pending browser commands; no tab/window/URL context exists. I recorded this and proposed an offline-queue reconciliation change that freezes, ages, session-binds, and revalidates commands before replay. The Mac bridge itself is online. Accessibility and Screen Recording are still unavailable, so UI-action receipts remain untrustworthy. I still need the owner to reconnect/authorize Chrome or explicitly choose a stale-command retention policy; only the owner can grant the TCC permissions.

**Biggest unknown:** The contents, age, and reversibility of the 9 queued browser commands are not exposed by the status snapshot, so I cannot establish whether any are still wanted or safe to replay.

