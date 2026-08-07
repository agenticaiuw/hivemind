# Harness derivation — unified — round 105

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “pin this” during a conversation, save the exact moment and its surrounding exchange, then later let me ask “what did I pin?” and get a short cited recap or open the corresponding note on my Mac."
- **useful because:** The pendant is present at the moment an idea happens, the relay can preserve it despite leaving the conversation, and the Mac can turn it into a durable, editable artifact. Today those surfaces can each handle pieces, but the owner cannot reliably recover a fleeting thought with evidence.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime only for detecting the explicit low-latency “pin this” utterance and acknowledging it; use deterministic transcript/time-window capture and a background model (gpt-4.1-mini) to summarize later. Escalate to planner only when the recap is ambiguous or spans multiple pins.
- **latency:** A local pendant acknowledgement within 300 ms; relay receipt within 2 s when online. Deferred note creation and summarization may take 5–15 s and must survive the owner walking away.
- **cost:** About $0.001–$0.01 per deferred recap depending on transcript length; deterministic pin receipt and retrieval should be free. Storage is small text plus optional short audio clip, dominated by retention policy.
- **security:** Pinned moments may contain private speech. Encrypt in transit and at rest, attach sensitivity and retention metadata, never expose unrelated conversation, and require confirmation before sharing or sending a pin externally. The spoken acknowledgement must not repeat the captured secret.
- **missing:** A durable pin marker schema linking pendant monotonic time, relay job/session, transcript span, and Mac note URI; An offline-safe event/receipt path and replay deduplication for the explicit marker; A retrieval route that returns cited transcript/audio offsets and the linked Mac artifact; A retention/deletion control for pinned audio separately from ordinary failure-buffer audio

### "Move the reply I’m hearing from the pendant to my Mac headphones (or back) without restarting it, repeating words, or losing my place."
- **useful because:** The owner should be able to walk from a noisy room to the Mac, change listening hardware, and continue the same answer naturally. Today the pendant, relay, and Mac can each deliver audio, but they do not share a playback cursor or acknowledge the exact handoff point.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Deterministic state transfer for playback position and device capability negotiation; use the realtime tier only if the owner gives a spoken, ambiguous destination such as “move this somewhere quieter.” No model is needed to copy PCM/Opus frames or resume at a cursor.
- **latency:** A handoff acknowledgement in under 300 ms and audible continuation within 1 s. If the destination is unavailable, keep the original stream playing and say so rather than silently dropping it.
- **cost:** Negligible model cost. Relay metadata is a few hundred bytes per active response; audio transfer is already paid for by the response stream, though a short overlap buffer may add under 100 kB per handoff.
- **security:** Only paired owner devices may subscribe to a response stream. Do not make a private reply available to an unpaired browser or nearby Bluetooth device; expire handoff tokens after the response ends and erase discarded audio according to the existing retention policy. Moving output must not imply permission to share content.
- **missing:** A playback-session protocol with responseId, codec, frame sequence, sample offset, and acknowledged cursor; Pendant and Mac clients that report buffered/played sequence numbers and atomically pause or resume; Relay fan-out or short-lived retransmission storage for the overlap window; A visible dashboard control and a spoken fallback when the destination device is offline


## Changes it proposed to its own stack

### `integration` — Add a cross-surface interaction ledger with one opaque interactionId minted at the pendant press/voice-start and propagated through audio chunks, relay jobs, planner decisions, Mac/browser actions, TTS, and delivery receipts. Store only hashes and typed references by default; each node appends an immutable event with monotonic and wall-clock timestamps, source surface, status, and parentId. Expose a bounded causal timeline endpoint and have the dashboard/pending voice reply resolve it into one human-readable receipt. Use the same ledger to implement the proposed “pin this” marker without re-uploading the whole conversation.
- **owner gets:** When a job is late, a browser is offline, or a reply arrives after reconnect, the owner can ask “what happened?” and receive one trustworthy answer rather than disconnected Mac, relay, and pendant statuses. A pinned moment can point to the exact exchange and resulting note, while unrelated speech stays out of view.
- effort: Medium-high: define an event schema and idempotency rules, add propagation to relay and local-agent job records, add pendant marker packets, and build one read-only timeline/receipt view. Migrate existing receipts by assigning synthetic interaction IDs where possible.  ·  risk: Clock skew, duplicate reconnect events, or leaked opaque identifiers could produce misleading timelines. Use monotonic sequence numbers per device, server ordering only for presentation, strict event-size limits, authenticated writers, and explicit “unknown ordering” labels. Never infer success from a queued event; terminal state requires a receipt from the acting node.
- cost: Negligible model/API cost; D1/R2 writes grow by a few hundred bytes per event. Retain metadata longer than audio but apply owner-configurable deletion and hash sensitive payloads rather than storing transcripts in the ledger.  ·  latency: Under 5 ms local append and under 50 ms relay overhead per batched event; batch nonterminal telemetry so it cannot compete with LTE-M audio. Receipt lookup should be under 300 ms from the relay.
- security: The ledger becomes a sensitive map of the owner's actions and conversations. Encrypt transport/storage, scope reads to the owner's session, redact secret values, separate event metadata from transcript/audio, and require confirmation before displaying or exporting sensitive evidence.
- depends on: A durable request ID and idempotent browser/Mac job queue; Typed action receipts with terminal success/failure states; An offline-safe pendant event spool and replay deduplication; A dashboard endpoint for causal timeline queries


## What it asked for

_Nothing._
## Its own summary

Discovered the live state and recorded two new items. Capability: “pin this” captures an exact conversational moment across pendant → relay → Mac and retrieves a cited recap. Integration change: a cross-surface interaction ledger propagates one interactionId through audio, planning, actions, TTS, and receipts so late/offline work and pins have one causal timeline. The proposed LE Audio bridge was correctly rejected as already covered by the backlog. Current Mac relay is online, but browser is offline with 10 queued commands; computer-use is disabled because Accessibility and Screen Recording are still missing (automation grants are present).

**Biggest unknown:** The exact production 24 kHz audio acceptance thresholds and pendant/companion product constraints remain unanswered; implementing the pin capability also needs a durable offline event spool, marker schema, and transcript/audio retention policy. Browser workflows remain blocked until the extension heartbeat returns.

