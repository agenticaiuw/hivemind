# Harness derivation — unified — round 242

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Continue the task I asked for, even if the Mac, browser, or relay went offline—without doing any step twice.”"
- **useful because:** Today an interrupted plan can be inspected but not resumed safely; ordinary ledgers remain falsely open, relay jobs have no expiry lease, and browser lease sweeping is not running. This would make long-running work dependable instead of requiring the owner to reconstruct it manually.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Deterministic policy and receipts first; background model only to explain a blocked resume, never to decide replay safety.
- **latency:** On reconnect, present a concise pending/resume choice within 2 s; no automatic action for unrepeatable or unknown steps.
- **cost:** Near-zero model cost for replay decisions; storage/lease writes dominate. One short background explanation only when blocked.
- **security:** Gate auto-rerun on replaySafety idempotent/additive, not reversibility; require fresh owner approval on irreversible-write/off-machine/uncontained steps; bind the decision to plan digest and world fingerprint; never replay browser sends or messages. A stale lease must expire and requeue rather than duplicate.
- **missing:** orchestrator must close successful ledgers; relay_jobs needs lease_until and a requeue sweep; browser bridge supervisor must actually run its lease sweep; one owner-facing resume/deny control over the next conversation

### "“When I ask whether something got done, tell me what actually happened—not what the agent intended—and point to the evidence.”"
- **useful because:** A spoken promise can currently be phrased as complete without joining Mac receipts, browser results, relay status, and the pendant's physical delivery/hearing state. This gives the owner a single truthful answer with explicit unknowns and no mutation.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Deterministic evidence join and provenance scoring; use the low-cost background tier only to summarize conflicting evidence.
- **latency:** Return a first status in 2 s from cached receipts; fetch missing bounded evidence within 5 s; never wait indefinitely on an offline surface.
- **cost:** Low per query; bounded receipt reads dominate, with occasional cheap summarization.
- **security:** Search only explicitly bound tabs/apps and the named commitment; do not infer completion from intent or speech alone; expose sensitive evidence minimally; report stale/offline sources as unknown; read-only by default.
- **missing:** a durable commitment registry that binds utterance, intended action, and target; joining audio_delivery_ack_queue with Mac job receipts and browser command results; a provenance/conflict contract (completed, partially completed, not evidenced, failed, unknown); owner-facing evidence links or spoken citations

### "“Why did you go quiet, and what should I do now?”"
- **useful because:** When a conversation fails, the owner currently gets a timeout or a generic degraded response. This capability correlates pendant events, audio loss, relay receipts, Mac jobs, and browser health, then gives a short cause and one safe recovery action—without pretending an offline surface is healthy.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Deterministic incident correlation and repair plan; a cheap background model may turn the hypothesis into plain speech. Realtime is used only for the immediate spoken answer.
- **latency:** Speak a first diagnosis within 3 s from the last correlated snapshot; repair is opt-in and resumable; never block the next conversation on a dead surface.
- **cost:** Low: bounded health/event reads dominate; model cost only for a concise explanation.
- **security:** Read-only diagnosis by default; repairs require explicit confirmation and idempotency key; expose no raw audio or page contents; distinguish observed facts from hypotheses; do not run fault injection against production traffic.
- **missing:** a pendant-triggered incident ID and correlation window; a compact owner-facing hypothesis vocabulary with confidence and evidence; repair receipts that join fleet_health_and_repair to the original incident; a policy for when a degraded answer should be spoken versus deferred until the next turn

### "“Make this a standing rule from now on, show me exactly what it changes, and let me revoke it later.”"
- **useful because:** The owner has to repeat preferences, while quiet hours, interruption behavior, transport choice, retention, and routine timezone are scattered policy decisions. This would turn a spoken preference into a versioned rule with a preview of affected behavior rather than silently changing one subsystem.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Planner tier compiles speech into a typed policy proposal; deterministic evaluation simulates affected routines and guards; realtime only acknowledges the result.
- **latency:** Preview within 5 s; no rule becomes active until the owner confirms; revocation should take effect on the next event and be visible immediately.
- **cost:** One planner call per proposed rule; deterministic simulation and storage dominate subsequent use, so recurring cost is negligible.
- **security:** Never infer a permanent rule from casual speech; display scope, exceptions, effective time, and affected surfaces; version every change; require physical approval for rules affecting capture, deletion, external actions, or interruption; keep an audit trail of prior versions.
- **missing:** a typed policy schema spanning focus, routine timezone, transport, retention, and approval behavior; a simulation endpoint that reports which existing modules would change; versioned policy storage with effectiveAt/revokedAt; a pendant/dashboard confirmation and rollback presentation

### "“I replaced or lost my pendant—restore my setup to the new one without exposing my old audio, browser sessions, or private memories.”"
- **useful because:** A wearable is replaceable hardware, but today there is no owner-visible migration boundary. The useful result is a controlled handoff of configuration and pending work while explicitly excluding audio, browser credentials, and erased/private data.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Deterministic migration manifest and cryptographic verification; background model is unnecessary.
- **latency:** Show an inventory in under 5 s; complete local configuration migration in under 30 s; relay reconciliation may remain pending with a clear receipt.
- **cost:** Low; cryptographic manifest exchange and bounded metadata transfer dominate.
- **security:** Require old-device proof when available or an explicit recovery ceremony when it is not; never copy raw audio, browser cookies, page contents, or deleted facts; bind every migrated item to an allowlist and expiry; revoke the old device immediately after cutover.
- **missing:** a device enrollment/revocation protocol distinct from per-action approval; an exportable allowlisted configuration manifest; relay-side device ownership and pending-item reassignment; a physical recovery ceremony for the lost-device case; a migration receipt showing included and excluded classes

### "“Before you act, show me the one concrete change you expect in the real world; if the world differs, stop instead of guessing.”"
- **useful because:** A plan can be syntactically valid yet stale by execution time: a file may have changed, a browser tab may be different, or a relay job may have been claimed elsewhere. This capability turns preview into a world-bound execution contract and stops at the first unexpected observation.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Deterministic world fingerprinting, invariant checking, and transaction control; use a planner only to explain a mismatch.
- **latency:** Preview in 2 s for local state; re-check immediately before each mutating phase; mismatch speech within 2 s and no silent fallback.
- **cost:** Low recurring cost; hashing and bounded state reads dominate.
- **security:** Hash only permitted metadata and redacted page/file state; do not transmit secrets; bind approval to plan digest plus world fingerprint; treat unknown state as stop, not success; preserve the mismatch receipt for audit.
- **missing:** one cross-surface precondition schema for files, browser targets, relay jobs, and pendant state; an execution hook that revalidates immediately before each step; a user-readable mismatch explanation and retry/edit path; transaction integration that can roll back already-completed reversible steps


## What it asked for

_Nothing._
