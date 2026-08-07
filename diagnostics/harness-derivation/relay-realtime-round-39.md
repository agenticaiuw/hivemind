# Harness derivation — relay-realtime — round 39

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If the connection gets choppy, keep the conversation going: tell me what you missed, ask me to repeat only the important parts, and resume the task without starting over."
- **useful because:** On LTE-M half duplex, packet loss and mismatched audio clocks can cause dropouts. The owner shouldn’t have to repeat everything or lose context when the link glitches mid-command.
- **path:** pendant → relay → mac-bridge → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime at relay for immediate clarification; cheaper judgement/action tiers for reconciliation and resuming work.
- **latency:** Sub-second detection and a one-sentence clarification prompt; resume within a few seconds once a repeat is provided.
- **cost:** Low per invocation; dominant cost is extra ASR/LLM turns for clarification and reconciliation, not downstream actions.
- **security:** May buffer short audio/text fragments and partial transcripts; must minimize retention, redact sensitive content, and clearly signal what was dropped and what is being stored.
- **missing:** Relay-visible counters for packet loss and clock drift (shared across perception/action); A small, durable conversation state record to resume tasks after transient disconnects; A standard schema for "dropped segment" events and partial command reconciliation across agents

### "When the LTE-M link drops words because you are speaking, keep my command intact: tell me briefly that you caught only part, recover the missing span if possible, and ask one targeted clarification instead of making me repeat the whole turn."
- **useful because:** The pendant is half-duplex and a recent run lost roughly 7.8 seconds of uplink during downlink speech. Today the owner can unknowingly issue a truncated command, causing a wrong Mac/browser action or a confusing restart. This makes voice control trustworthy in the exact situation where the wearable is most useful.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Pendant firmware performs packet-loss/turn-boundary markers and retains a short rolling audio ring; relay-realtime performs low-latency loss-aware turn reconstruction and asks the clarification; mac-planner/browser-extension receive only the finalized intent, never a guessed partial command.
- **latency:** Under 300 ms for a loss acknowledgment; up to 2 seconds for reconstruction from the rolling ring; never execute a downstream action until the intent is complete or the owner explicitly answers the targeted clarification.
- **cost:** Usually one realtime turn, roughly $0.01–$0.05 depending on audio duration; materially cheaper than a mistaken Mac/browser action and a full repeated turn. Firmware storage/RAM and LTE retransmission are the dominant implementation costs, not model tokens.
- **security:** The rolling audio ring must be encrypted, short-lived, and erased after finalization; only the finalized transcript/intent crosses to Mac or browser. A guessed reconstruction must never trigger an action. Clarification audio leaves the pendant through the existing relay path.
- **missing:** A pendant-side short rolling audio buffer and packet/sequence-loss markers that fit the nRF9160 memory budget; A relay turn state machine with explicit partial/complete status and targeted clarification responses; An intent handoff field carrying confidence and missing-span metadata to mac-planner/browser-extension; End-to-end tests that inject the observed downlink-induced uplink loss and verify no partial action executes

### "If the Mac planner and browser observer disagree about what is on screen or what I meant, tell me the disagreement in one sentence and offer the two concrete interpretations; do not silently pick one."
- **useful because:** A worn front door can hear an utterance while the Mac is unattended and the browser extension has a private, changing page state. Today downstream agents can act on inconsistent perception without exposing that uncertainty to the owner. This lets the owner resolve only genuine cross-node conflicts, without adding a blanket approval gate.
- **path:** pendant → relay-realtime → faculty-perception → faculty-judgement → mac-planner → browser-extension
- **model tier:** faculty-perception emits typed observations with timestamps and source; faculty-judgement compares them and reduces the conflict to at most two alternatives; relay-realtime speaks the short disambiguation and routes the owner's answer to the already-running planner or browser session.
- **latency:** Detect and speak a conflict within 1 second of receiving competing observations; resume the selected path within 2 seconds of the owner's answer. If there is no conflict, add no conversational round trip.
- **cost:** A small judgement call, roughly $0.005–$0.02, only on conflicting observations; most turns remain unchanged. The main cost is carrying compact, source-stamped observation records rather than resending full page/context transcripts.
- **security:** Disagreement briefs may mention authenticated page contents, so redact secrets and send only the minimum differing fields to the pendant. Preserve source/timestamp provenance for audit. Never resolve a conflict by inventing a value; expire stale observations.
- **missing:** A shared typed observation envelope with source, timestamp, confidence, and scope (Mac UI versus browser tab); A conflict detector and two-alternative reducer in faculty-judgement; A relay response type for clarification that resumes an existing job/session rather than starting a new intent; Redaction rules for authenticated browser observations before they are spoken aloud

### "Forget the last thing I said everywhere: remove it from the relay transcript/context, any queued Mac or browser job, and derived receipts, then tell me exactly what was erased and what could not be erased."
- **useful because:** The owner wears the microphone while moving between private contexts. Today clearing a conversation or deleting a job is surface-specific; a spoken request cannot reliably remove the same utterance and its derivatives from the relay, Mac planner, and authenticated browser queue. This gives the owner a practical, auditable privacy control without requiring them to find a dashboard.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** relay-realtime detects the explicit forget command; a deterministic deletion coordinator fans out to relay storage, Mac job/context records, and browser command queues; no model should decide what to delete. A cheaper background verifier can reconcile deletion receipts.
- **latency:** Acknowledge immediately, complete relay deletion within 500 ms, and return a cross-node receipt within 5 seconds. If a downstream node is offline, mark deletion pending and retry rather than claiming success.
- **cost:** Low token cost (mostly deterministic storage operations), approximately <$0.01 per request; durable deletion receipts and retry state are the main infrastructure cost.
- **security:** Require an unmistakable spoken phrase and bind deletion to the active owner/session; do not expose deleted content in the receipt. Browser history or third-party server logs cannot be promised deleted, so the receipt must distinguish local deletion, cancellation, and external retention. Encryption and authenticated node-to-node deletion are required.
- **missing:** A cross-node deletion protocol with idempotent tombstones and per-node acknowledgments; Relay storage and context-graph provenance linking an utterance to derived intents, jobs, and receipts; Mac and browser handlers that cancel queued work and purge only the linked artifacts; A concise spoken and dashboard receipt that reports complete, pending, and externally-uncontrollable deletion


## Changes it proposed to its own stack

### `relay` — Add a cross-node glitch-tolerant conversation protocol: the relay emits structured events (start, partial, missing_segment, repeat_request, resume) with sequence numbers and source timestamps, and writes a small durable state snapshot per voice run. Perception/judgement can reconcile partial commands and resume the intended task.
- **owner gets:** When the pendant uplink drops or half-duplex collisions happen, the assistant can recover gracefully, ask for only what’s missing, and continue the same task instead of restarting.
- effort: Medium. Requires a state schema, event emission, and coordination with perception/judgement, plus minimal storage writes.  ·  risk: Mis-reconciliation could resume the wrong task; mitigate with explicit confirmation when confidence is low and an easy way to cancel.
- cost: Small additional storage and logging; extra tokens only when a glitch occurs.  ·  latency: Tiny overhead for event logging; faster recovery than re-running entire workflows.
- security: Stores partial transcripts; must cap retention, encrypt at rest, and avoid logging sensitive payloads by default.
- depends on: Shared telemetry counters from audio/bridge for packet loss and clock drift; A minimal durable state store for voice-run snapshots


## What it asked for

### `s13-eg4f` (skill) — uplink_health_ping
- does: Periodically (during an active conversation) measures uplink health using lightweight counters: packet loss, jitter proxy, and buffer underruns, and reports a compact summary to the relay.
- must be on-device because: Only the pendant and its modem see real-time radio behavior and buffer states; the server can’t reliably infer it from transcript gaps alone.
- trigger: During an active voice session; also on button press to start a quick preflight check.
- storage: A tiny rolling window of the last few health samples (e.g., 10–20 entries) in RAM; no persistent storage required.
- RAM budget: Very small: a few structs and counters; well under 10 KB.

## Its own summary

Recorded three new owner-facing capabilities: loss-aware voice turn recovery for half-duplex LTE-M drops; explicit cross-node disagreement disambiguation between perception/planner/browser state; and a coordinated spoken “forget everywhere” operation with per-node deletion receipts. Each names the missing firmware, relay, Mac, browser, and faculty changes rather than pretending today’s stack supports them.

**Biggest unknown:** Whether the existing context/job/browser records retain enough provenance to link one spoken utterance to every derived artifact; that determines how complete coordinated deletion can be.

