# Harness derivation — faculty-judgement — round 178

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Tell me which parts of my morning brief were actually downloaded and played, and offer only the unheard items again."
- **useful because:** A generated briefing is not the same as a delivered one. The owner can stop wondering whether a silent commute, dropped link, or interrupted playback caused a missed item; retries resume at the exact unheard item instead of replaying everything.
- **path:** relay-realtime → pendant → mac-planner → dashboard
- **model tier:** background for reconciliation; realtime only for the one-sentence spoken answer
- **latency:** Under 2 seconds for status; retry enqueue under 5 seconds
- **cost:** Usually <$0.01; dominated by no model call when artifact IDs and ACKs are sufficient
- **security:** Expose opaque artifact/item IDs and delivery state, not audio contents. Require owner confirmation before replaying private material aloud; honor the existing sensitivity and provenance gates.
- **missing:** Join scheduled briefing item IDs to generated audio artifact IDs; Persist a durable item-level delivery projection from record_pendant_delivery_event; A dashboard/relay read route for unheard versus played items

### "When my pendant is USB-connected to my Mac, continue a response across a cable drop without replaying sentences, and tell me plainly if anything was lost."
- **useful because:** The hardware is physically testable now even though LTE is unregistered. A cable drop should be a recoverable interruption, not a mysterious half-answer or a full replay; sentence-level checkpoints make the device useful during real movement between desk and room.
- **path:** pendant → mac-planner → relay-realtime → unified
- **model tier:** background for checkpoint reconciliation; realtime only to announce loss or resume
- **latency:** Detect in 1 second and resume within 3 seconds after USB reconnect
- **cost:** <$0.005 per interruption; mostly local state and checksum comparison, with model use only if a short repair summary is needed
- **security:** Persist only opaque artifact IDs, byte offsets, checksums, and sentence boundaries; never cache transcript/audio beyond existing failure-path retention. A checksum mismatch must fail closed and request a fresh artifact.
- **missing:** USB serial transport adapter that reports pendant session generation and reconnect; Sentence-boundary index in the audio artifact manifest; Cross-device cursor reconciliation using the existing delivery ACK queue

### "If my pendant is unavailable, don't pretend my briefing was spoken: leave it in the right fallback and tell me whether it is waiting on the Mac, browser, or pendant."
- **useful because:** The owner currently has several bodies and scheduled jobs, but a routine can finish at the relay or Mac while the only surface they rely on is offline. A truthful fallback prevents silent loss and avoids sending sensitive content to an unintended surface.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** background deterministic routing with a cheap model only to compress the fallback sentence
- **latency:** Preflight under 1 second; fallback placement under 5 seconds
- **cost:** <$0.01 per run; mostly status reads and queue writes
- **security:** Run cross-surface preflight and autonomy policy before any placement. Do not route private audio/text to browser or spoken output merely because the pendant is offline; show sensitivity, evidence, and the exact blocked surface in the dashboard.
- **missing:** A routine completion state that distinguishes generated, queued, delivered, and heard; A single fallback writer that can place a bounded item in the existing pendant inbox or Mac note without duplicating it; Policy rules for which content classes may fall back to which surface

### "When you bring an old briefing item back, tell me only what changed since I last heard it, with the source and timestamp."
- **useful because:** Repeated briefings force the owner to reprocess stale information and make missed items feel like duplicates. A change-only replay would turn the pendant into a useful continuity surface rather than a transcript player.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Background model for semantic diffing; deterministic hashes and timestamps should handle unchanged items without a model call.
- **latency:** Under 3 seconds for a short change summary; unchanged items should be suppressed immediately.
- **cost:** <$0.02 for a typical multi-source briefing; model cost is proportional only to changed source excerpts.
- **security:** Diff only against source-linked material the owner was already authorized to hear. Never infer that a changed private item is safe to speak merely because its earlier version was played; re-run sensitivity and surface policy.
- **missing:** Versioned briefing items with source fingerprints and prior delivery state; A bounded semantic-diff worker that can compare two authorized item versions; Owner-visible evidence showing which source and timestamps produced the change summary

### "Ask me one precise clarification when my words could refer to several current items, then continue from the item I meant without making me repeat the whole request."
- **useful because:** A wearable conversation lacks a screen and people naturally say “that one” or “send it.” Today the system can act on the wrong active job or force the owner to restate context. A bounded clarification would prevent costly mistakes while preserving momentum.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime model only for resolving the ambiguity; deterministic candidate ranking and policy checks should avoid model calls when there is one clear referent.
- **latency:** One spoken clarification within 1 second; resume the chosen task within 3 seconds of the answer.
- **cost:** <$0.01 per ambiguous turn; most turns should resolve locally from active item IDs and recent provenance.
- **security:** Speak only opaque labels or minimally redacted descriptions until the owner selects one. Never use a spoken “yes” as consent for an external side effect; selection identifies an item, while existing physical approval remains required.
- **missing:** A shared active-item registry spanning relay jobs, Mac jobs, browser commands, and audio items; A compact candidate labeler that can be spoken safely; A clarification response path that binds the next utterance to one candidate with expiry and idempotency


## Changes it proposed to its own stack

### `integration` — Make scheduled briefings delivery-aware: when a routine creates multiple briefing items, assign stable item IDs before synthesis, attach them to the audio artifact manifest, and reconcile pendant downloaded/played ACKs against those IDs. At the next routine run, suppress already-played items, surface interrupted/unheard items as a bounded review list, and mark a run 'generated-but-not-heard' rather than 'completed' when no playback ACK exists. Use an idempotency key per routine+item+date and preserve the owner's America/Chicago preference as an unresolved display timezone while keeping Mac execution in its authoritative zone.
- **owner gets:** A daily brief will stop claiming success when it merely rendered text. The owner gets fewer duplicate briefings, truthful catch-up, and a clear distinction between 'the system made it' and 'I heard it.'
- effort: Medium-high: routine/job schema and artifact metadata changes, ACK projection, and one catch-up UI/voice path; hardware ACK behavior already accepted.  ·  risk: Late or duplicated ACKs could incorrectly suppress an item. Require monotonic device sequence plus event-id deduplication, expire stale cursors, and provide an explicit 'replay this item' action. If timezone remains unresolved, never silently move routine firing times.
- cost: Negligible storage and compute; occasional short model call only for a catch-up sentence.  ·  latency: No impact on synthesis; adds sub-second reconciliation and up to one network round trip for catch-up.
- security: Improves disclosure safety by preventing unattended replay; store opaque IDs and provenance links, not raw private content in the delivery projection.
- depends on: record_pendant_delivery_event must be wired to the real POST /pipeline/events path; Stable item IDs in POST /briefing and audio artifact manifests; A durable relay job lease/requeue so a routine cannot be marked complete after a crashed handoff; Owner decision on display timezone versus Mac routine timezone

### `hardware` — Add a low-power, non-recording e-ink status strip to the pendant or its clip: show a short item number/source glyph, unread count, privacy state, and USB/LTE link state. The relay signs a compact status packet; the Mac and pendant update it without sending audio or page content. It must retain the last safe status through a link drop and blank on the existing privacy-panic latch.
- **owner gets:** The owner could glance at what is waiting, whether a response was actually delivered, and whether the pendant is private or disconnected without making the device speak sensitive content in public. It also gives the one-LED device a durable status channel instead of overloading blink patterns.
- effort: High: enclosure/clip redesign, display driver, signed status packet, power and weather testing, and a privacy-safe rendering contract.  ·  risk: A visible display can expose information to bystanders. Default to opaque item numbers and icons, require an explicit local reveal mode, blank on panic, and never render source text or credentials. Added hardware can reduce battery life and durability.
- cost: Roughly $8–$25 in components and a few mW average depending on refresh frequency; engineering and enclosure work dominate.  ·  latency: Status changes appear within one link round trip; e-ink refresh is hundreds of milliseconds but does not affect audio.
- security: Adds a new physical disclosure surface, so signed packets, opaque identifiers, conservative defaults, and panic blanking are mandatory.
- depends on: A signed compact status-envelope format shared by relay, Mac, and firmware; Owner choice of whether opaque status is acceptable in public; Mechanical redesign with a display-visible privacy indicator


## What it asked for

_Nothing._
