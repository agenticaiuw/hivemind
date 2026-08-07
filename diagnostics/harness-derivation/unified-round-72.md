# Harness derivation — unified — round 72

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I got interrupted—pick up the task I was doing, tell me what changed while I was away, and continue only after I approve anything irreversible.”"
- **useful because:** Today a spoken task can span a pendant dropout, a sleeping Mac, and late browser evidence without one coherent handoff. This gives the owner one resumable thread: a pendant marker identifies the moment, the relay correlates it, the Mac and authenticated browser contribute late results, and the owner receives a short cited state delta instead of a restart or unsafe duplicate action.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use the realtime tier only to capture the interruption marker and speak the short resume summary. Use a cheaper background model to reconcile receipts, browser evidence, and Mac journal entries; use the local Mac planner for execution and the browser bridge for private tabs.
- **latency:** Marker acknowledgment under 300 ms locally/relay; resume summary within 3 s after all currently available receipts arrive; late evidence may update the ledger asynchronously. No irreversible continuation without an explicit pendant/button or spoken approval.
- **cost:** Approximately $0.01–$0.05 per resumed thread depending on evidence volume; most reconciliation is background/local. Dominant costs are cited page snippets and any realtime speech turn, not the ledger writes.
- **security:** Persist only correlation IDs, hashes, timestamps, action receipts, and minimal cited snippets; never copy secrets or full private pages into the pendant. Bind each thread to the authenticated browser tab/session, expire evidence after a short TTL, redact sensitive fields in dashboard/audio, and require confirmation before sending, deleting, purchasing, or submitting. A duplicated retry must be rejected by idempotency key.
- **missing:** A shared interruption/resumption ledger schema with correlation ID, stage, owner-visible marker, evidence packets, TTL, and idempotency key; A pendant marker event and local acknowledgment that survive a dropped link; Relay reconciliation and a late-evidence notification path to pendant/dashboard; Mac journal and browser evidence adapters that attach receipts to the same correlation ID; A resume endpoint that produces a cited delta and an approval gate

### "“Hold this for me for the next hour, and put it wherever I ask without making it permanent.” (For example, a phone number, tracking code, address, or short spoken note.)"
- **useful because:** The owner constantly encounters small pieces of information while away from the Mac. Today they must repeat them, put them in a permanent note, or trust an ordinary clipboard. This would create a short-lived, typed handoff from the worn pendant to the Mac and private browser, then erase it automatically—useful without turning fleeting sensitive data into memory.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Use realtime only for capture confirmation and the owner’s retrieval command. Use a cheap local/background classifier to type and validate the value; the Mac and browser should perform placement with deterministic actions, not an expensive model call.
- **latency:** Acknowledge capture in under 500 ms; retrieval under 2 s when the Mac/browser is online. If offline, retain a bounded encrypted item on the pendant until expiry or explicit deletion.
- **cost:** Under $0.01 per item in normal use; dominated by occasional speech transcription. Storage and routing are negligible.
- **security:** Treat every item as sensitive by default, encrypt in transit and at rest, never include it in long-term memory or analytics, show the destination before browser insertion, and require confirmation before placing it into a message, purchase, or other irreversible form. Expire by TTL, support immediate wipe, and record only a redacted receipt.
- **missing:** An ephemeral typed-value schema with TTL, sensitivity, provenance, and explicit destination binding; Pendant-side capture/erase and offline encrypted spool; Relay lease/expiry and single-use retrieval semantics; Mac and browser insertion adapters that refuse stale or mismatched values; A compact owner-visible confirmation and wipe control


## Changes it proposed to its own stack

### `integration` — Add a durable interruption ledger shared by pendant, relay, Mac planner, and browser bridge. On a button press, websocket loss, or explicit “pause,” create a thread record with correlationId, stage, last spoken marker, pending action idempotency keys, and evidence TTL. Make every Mac receipt and browser result append a signed/hash-linked evidence packet. On reconnect, the relay computes a compact cited delta, pushes a notification to the pendant/dashboard, and routes continuation through the existing approval gate; stale or already-applied actions become no-ops rather than retries.
- **owner gets:** The owner can leave mid-task and come back to an accurate “where we stopped / what changed / what is safe next” answer, without repeating work or accidentally sending a duplicate message. It works across the wearable’s intermittent LTE, the sleeping Mac, and private browser tabs.
- effort: Medium-high: shared schema and migrations, relay endpoints and reconciliation worker, Mac/browser adapter changes, pendant event/ack firmware, dashboard thread view, and fault-injection tests for dropped links and late results.  ·  risk: Incorrect correlation could merge two tasks or resume the wrong one; mitigate with owner-visible task labels, per-surface session binding, short TTLs, hash-linked receipts, and default-to-pause on ambiguity. If the relay is unavailable, keep only a bounded local marker and reconcile later.
- cost: Negligible storage/compute per thread; background reconciliation is cheap. Audio notification adds normal speech-generation cost only when the owner asks or a high-priority change arrives.  ·  latency: Local marker immediate; relay resume read usually under 1 s, with up to several seconds for Mac/browser late evidence. Does not add latency to ordinary turns.
- security: Evidence is minimized and scoped to the authenticated session; private browser content remains referenced by hash/snippet rather than copied broadly. Approval is mandatory for irreversible actions. Requires key rotation and replay protection for appended receipts.
- depends on: A durable browser job runner and typed result receipts (chg-16bc5dee / chg-14accc01); A shared typed context projection instead of per-surface prompt hand-writing (chg-a82e0b13); A pendant-local marker/ack skill (requested earlier but not yet granted); A relay push/notification route and Mac journal adapter

### `firmware` — Add an encrypted, bounded ephemeral handoff slot on the pendant: capture one typed value plus provenance and an expiry lease, expose only a redacted spoken confirmation, support explicit wipe and automatic zeroization, and synchronize single-use retrieval with the relay. The relay should mint a destination-bound token; Mac and browser adapters must consume it exactly once and return a receipt without persisting the value.
- **owner gets:** They can safely carry a code, address, or phone number from a spoken moment into the exact Mac or logged-in web field they choose, without creating a permanent note or leaving sensitive data on a forgotten clipboard.
- effort: Medium: firmware storage/crypto and button interaction, relay lease/token endpoints, typed-value extraction, Mac/browser insertion adapters, expiry and offline-reconnect tests.  ·  risk: A stale or mis-typed value could be inserted into the wrong field; default to preview/confirmation, bind tokens to a target session, reject expired tokens, and wipe on mismatch. If synchronization fails, the item remains local until TTL and cannot be remotely guessed.
- cost: Negligible relay/API cost; small flash/RAM reservation and a few milliamps only during radio sync. No recurring model cost beyond transcription/classification.  ·  latency: Adds one short relay round trip to insertion, normally under 2 seconds; local capture acknowledgment is immediate.
- security: Improves privacy versus ordinary clipboard/history, but requires secure key handling, replay protection, zeroization verification, and an explicit policy that ephemeral values never enter long-term memory or logs.
- depends on: A pendant-local encrypted ephemeral spool and erase primitive; A relay single-use lease/token endpoint; Typed-value extraction with confidence and provenance; Destination-aware Mac and browser insertion adapters; Owner confirmation UI on pendant/dashboard


## What it asked for

_Nothing._
## Its own summary

I discovered the live system and recorded two new, non-duplicate items: (1) an owner-facing cross-surface “resume my interrupted task” capability, and (2) the integration change that makes it real via a correlation/idempotency/evidence ledger spanning pendant, relay, Mac, and authenticated browser. The existing pieces (/plan, /execute, job receipts, browser results, Mac delegation) are present, but the connective ledger, pendant marker/ack, late-evidence reconciliation, and resume approval path are not. Current audio hardware remains prototype-constrained: 15.625 kHz capture, 24 kHz decode, ~87% single-core codec load, and measured LTE contention dropped ~7.8 seconds of uplink speech.

**Biggest unknown:** No new grants or skills are visible this round (granted category reports 0). I still need the previously requested pendant marker/ack and fault-injection/validation infrastructure, plus implementation of the ledger adapters. Accessibility/Screen Recording remains owner-blocked; the proposed resume flow intentionally works without it through AppleScript, job receipts, and the browser bridge.

