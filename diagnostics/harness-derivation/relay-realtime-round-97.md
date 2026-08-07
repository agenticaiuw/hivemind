# Harness derivation — relay-realtime — round 97

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Are you connected, and is my pendant listening right now?"
- **useful because:** Owners need a quick, reliable answer about whether they can talk to the pendant and whether the system is actively capturing audio. Today, signals are split across Mac routes, pipeline history, and device lists, and the relay lacks an authoritative snapshot.
- **path:** pendant → relay → mac-bridge
- **model tier:** realtime for the spoken response; a cheaper backend model is unnecessary for presence checks
- **latency:** Under 300ms for the response when state is available; otherwise a fast fallback probe.
- **cost:** Very low per invocation. Dominated by a single relay read and optional heartbeat update.
- **security:** Presence and session metadata are sensitive; keep bearer-protected and avoid exposing identifiers beyond what the owner needs to hear.
- **missing:** Relay-side status/heartbeat endpoint and storage for last-seen timestamps; A consistent semantic definition of 'listening' across relay audio pipeline and pendant capture states

### "If I lose signal or walk away while you are handling something, keep the work safe, and when my pendant reconnects say what happened since I left, what is waiting for me, and let me resume, pause, or undo it by voice."
- **useful because:** Today a dropped LTE link leaves the owner uncertain whether a Mac/browser task ran, partially ran, or is still active. This gives a worn, away-from-screen owner a trustworthy recovery conversation: a compact delta rather than a replay, explicit pending/failed/completed state, and voice-controllable resume/pause/undo across the relay, Mac, and private browser session.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles only the reconnect greeting, state-delta compression, and short voice commands; a cheaper background model prepares the durable job summary and groups receipts while disconnected. Mac-planner/mac-vision and browser-extension perform the work; relay remains the authoritative conversation front door.
- **latency:** On reconnect, emit a cached safety/state banner immediately (<500 ms), then stream the concise spoken delta within 2 s. Resume/pause/undo acknowledgement should be under 1 s after the command; detailed evidence can follow asynchronously.
- **cost:** About one realtime turn per reconnect (roughly normal short-utterance cost), with background summarization usually pennies or less per disconnected job. Dominant costs are audio uplink/downlink and any resumed browser/Mac execution, not the heartbeat.
- **security:** The relay must not speak private page contents until it has a current authenticated pendant session and should reveal only job names/status first, with details on request. Persist encrypted job receipts and a disconnect-time watermark; bind resume/undo to the original owner/session and make commands idempotent. A lost heartbeat must never be interpreted as permission to take new high-impact actions.
- **missing:** An authoritative pendant session/heartbeat lease with reconnect sequence numbers and last-heard timestamps; Durable per-job checkpoint and event journal spanning relay, Mac planner/vision, and browser tabs, including safe resume/undo capability; A reconnect delivery protocol that queues a small spoken state delta and accepts voice resume/pause/undo commands offline until uplink returns; A lifecycle-aware audio queue and dashboard view for missed summaries and receipts


## Changes it proposed to its own stack

### `relay` — Add a relay-side self-inventory endpoint and heartbeat snapshot, e.g. GET /v1/relay/status returning: relay build/version, time, connected session id, last spoken turn, current audio pipeline id/status, and last-seen timestamps for pendant, mac bridge, and browser as known to the relay. Include a lightweight heartbeat that the pendant and mac bridge can ping so faculty-perception can rely on a single authoritative snapshot.
- **owner gets:** When the owner asks "are you there? is my pendant connected? did you hear me?" the system can answer immediately and accurately, without guessing from Mac routes or stale pipeline events. It reduces confusion and prevents duplicated actions.
- effort: Medium. Define a small schema, wire to existing relay state, store last heartbeat timestamps in a durable object or in-memory plus periodic refresh, and expose a GET route.  ·  risk: If implemented incorrectly, it could expose internal state. Keep it bearer-protected, minimal, and redact tokens/session secrets. If heartbeat storage fails, degrade to current best-effort probes.
- cost: Low. One small read route and optional heartbeat writes. Minimal bandwidth.  ·  latency: Improves responsiveness by avoiding Mac round trips for presence checks.
- security: Must be access-controlled. Only return what’s needed for presence and session health.
- depends on: A small relay storage primitive (Durable Object or KV) for last-seen timestamps, or an existing equivalent state store.

### `relay` — Add a relay-owned connection lease and resumable handoff journal. Each pendant session gets a monotonic connectionEpoch and lastAckedEvent; heartbeat, disconnect, reconnect, and audio-delivery acknowledgements append compact events to a durable per-owner journal. Every delegated Mac/browser job references the epoch and emits typed checkpoints (accepted, started, waiting, completed, failed, undoable). On reconnect, atomically claim the unspoken delta, generate a short spoken summary, and expose voice commands resume/pause/undo that operate by idempotency key. If the lease is stale, the system may report status but must not start new work.
- **owner gets:** Walking out of LTE range or away from the Mac would no longer make the owner guess whether an action happened. On putting the pendant back on, they get one reliable spoken account and can recover without opening a dashboard; stale connectivity cannot accidentally authorize fresh actions.
- effort: Medium-high: Worker Durable Object or equivalent per-owner lease/journal, event schemas and idempotency propagation through Mac/browser bridges, reconnect audio protocol, and a small dashboard/debug view. Requires coordinated changes in pendant firmware, relay, Mac planner/vision, and browser extension.  ·  risk: Duplicate reconnect delivery, races between undo and a late completion, journal growth, or a reconnect during a partially submitted browser form. Recover with monotonic sequence numbers, compare-and-swap claim, bounded retention, typed checkpoint semantics, and receipts that distinguish reversible from already-committed effects.
- cost: Small Durable Object/storage and heartbeat overhead; roughly one tiny write per heartbeat/checkpoint plus one short summary model call per reconnect. No meaningful new realtime cost while connected.  ·  latency: Heartbeat adds negligible uplink traffic. Reconnect status can be spoken from cached journal state in under 500 ms; detailed reconciliation may take seconds.
- security: Strengthens security by making the lease explicit and refusing new work under a stale session. Journal and spoken summaries must be encrypted/scoped to the owner; never include private browser content in the initial reconnect banner.
- depends on: Pendant firmware heartbeat and reconnect sequence numbers; Durable cross-surface job checkpoints and typed receipts; Mac/browser bridges propagating idempotency keys and checkpoint events; Relay audio queue with delivery acknowledgements


## What it asked for

_Nothing._
## Its own summary

I discovered the current toolset and confirmed new grants exist, but relay_route_intent and server_browser_actions are still schemas with no implementation. I also observed the mac bridge is online while the browser is offline, and the latest voice run is stuck transcribing. I proposed a relay-side status/heartbeat snapshot and an owner-facing capability to answer "are you connected/listening?" without guessing from Mac signals.

**Biggest unknown:** There is still no authoritative relay-side snapshot of session and capture state, and no implemented routing/status tool for the relay to safely hand off intents and report progress without inventing protocol.

