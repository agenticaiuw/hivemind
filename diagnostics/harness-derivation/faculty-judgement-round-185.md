# Harness derivation — faculty-judgement — round 185

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Save this page as a source-linked note, but do not copy passwords or private form values.”"
- **useful because:** The owner repeatedly inspects pages and currently has to choose between a brittle raw capture and a note with no citation. The browser can extract the visible claim and URL, the Mac can create a note, and the pendant can confirm the short result while preserving a revocable source link.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background model for extraction and citation normalization; realtime only for the owner’s command and confirmation
- **latency:** 2–5 seconds for a normal page; never block the browser on model synthesis if a deterministic title/URL note is sufficient
- **cost:** <$0.02 per page, dominated by extraction/summarization; zero model cost for title+URL-only fallback
- **security:** Run the existing secret-locator/redaction path before any text leaves the browser. Store a capsule/provenance ID and digest, not raw password fields; require explicit confirmation before including sensitive text. Revocation must invalidate the note’s derived claim, not merely tombstone the source.
- **missing:** Mount the existing browserProvenance routes and wire recordExtraction into the browser bridge; Add capsuleId/source links to memory facts and note records so revocation propagates; A typed browser-to-Mac create-note handoff with idempotency

### "“If I miss a scheduled brief, quietly catch me up later—but only once, and tell me exactly why.”"
- **useful because:** There are already multiple daily briefs at the same time and the owner can be away from the Mac or wearing the pendant without hearing one. A deadline-aware fallback would coalesce missed routine outputs, avoid duplicate interruptions, and make the reason visible instead of silently replaying stale audio.
- **path:** relay-realtime → mac-planner → pendant → dashboard
- **model tier:** background model for coalescing missed items; realtime only when the owner asks for the catch-up
- **latency:** ack/state evaluation within 1 minute of a scheduled deadline; spoken catch-up starts on the next safe attention window
- **cost:** <$0.01 per deadline check; model cost only for a compact coalesced digest
- **security:** Never infer that generated means heard. Respect the owner-configured quiet window and sensitivity policy; do not speak private items merely because they are overdue. Each fallback must carry routine ID, artifact ID, delivery evidence, and a dedupe key.
- **missing:** A scheduler hook that evaluates routine deadlines against delivery ACKs; Durable deduplication across the existing duplicate routines and their generated artifacts; A catch-up state machine with expiry and a dashboard explanation

### "“Forget everything derived from this website or page, everywhere.”"
- **useful because:** The owner currently cannot trust revocation: evidence tombstones do not remove browser-derived facts, context-graph copies, or notes. One command should return a manifest of affected records, revoke the source, remove derived local claims, emit a fleet retraction, and report anything that could not be reached.
- **path:** dashboard → mac-planner → browser-extension → relay-realtime
- **model tier:** background for impact analysis; realtime only for the concise confirmation and final receipt
- **latency:** impact preview in 2 seconds; apply may take up to 10 seconds across Mac, browser, and relay
- **cost:** <$0.02 per invocation; cost is dominated by scanning local stores and relay memory, not generation
- **security:** This is destructive and must require explicit confirmation with a source-scoped impact list. Never delete unrelated records sharing a host; distinguish exact capsule/source IDs from broad-origin matches. Keep permanent tombstones and an auditable receipt without retaining the revoked body.
- **missing:** A cross-store source index linking capsules to facts, context-graph entities, notes, and fleet-memory events; A dry-run/apply/retry endpoint that propagates revocations to Mac, browser, and relay; A real fleet-memory writer and retraction path

### "“Notice the repetitive things I keep doing across my browser, Mac, and pendant, then propose a safe one-command routine that would eliminate the friction.”"
- **useful because:** The system currently records jobs, receipts, browser commands, and device events, but the owner must recognize repeated workflows manually. A friction compiler would turn real repeated behavior into a reviewable routine with an explanation of the observed sequence, estimated time saved, and explicit reversibility—without silently automating anything.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → dashboard
- **model tier:** background model over sampled, redacted execution traces; realtime only to explain or accept a proposed routine
- **latency:** overnight or on-demand analysis; under 2 seconds to show an already compiled proposal
- **cost:** <$0.10 per analysis window; trace summarization dominates, so run weekly or after a threshold of repetitions
- **security:** Analyze action types and digests rather than raw page contents; exclude secrets and sensitive destinations by default. Never compile destructive, financial, or message-sending steps into auto-run without a physical approval requirement and a preview.
- **missing:** A cross-surface trace join for relay, Mac, and browser IDs; A deterministic workflow normalizer that groups equivalent actions while preserving provenance; A routine proposal store with preview, owner approval, versioning, and rollback

### "“Keep my pendant’s speech intelligible when the connection or Mac load changes, and tell me afterward if you degraded it.”"
- **useful because:** The owner should not have to understand Opus framing, CPU saturation, packet loss, or USB contention. A closed-loop audio governor would measure those signals, choose among validated profiles at an utterance boundary, preserve speech before fidelity, and give a truthful post-call quality receipt.
- **path:** pendant → relay-realtime → mac-planner → ESP32 audio bridge → dashboard
- **model tier:** deterministic firmware/relay controller; no expensive model needed except an optional human-readable explanation
- **latency:** profile decision within one utterance boundary; recovery from an underrun within 1 second where the link permits
- **cost:** negligible API cost; engineering cost is hardware measurement, profile negotiation, and acceptance testing
- **security:** Only signed, allowlisted codec profiles may be selected. Never transmit raw diagnostic audio by default; retain counters and opaque artifact IDs. A degraded mode must fail closed rather than produce clicks or unexpected loud output.
- **missing:** A negotiated profile protocol spanning nRF9160, ESP32 bridge, Mac USB path, and relay; Live counters and control hooks for packet loss, queue depth, underruns, and CPU budget; A profile transition receipt and rollback path tested against the 24 kHz acceptance criteria

### "“Give me a complete, readable export of what this system remembers about me, where each item came from, when it expires, and let me revoke selected items everywhere.”"
- **useful because:** The owner currently cannot inspect one coherent inventory: facts, capsules, graph entities, browser provenance, audio, and relay memory have different stores and deletion semantics. A provenance-aware personal export would make the system governable by the person wearing it, not just by internal APIs.
- **path:** dashboard → relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** background deterministic aggregation with a cheap summarizer for the readable view; realtime only for spoken navigation of the export
- **latency:** preview under 5 seconds locally; full export may stream asynchronously and notify when complete
- **cost:** <$0.05 per export; storage scan and redaction dominate, not model inference
- **security:** Export is owner-only and must redact secrets by default while preserving their existence and source metadata. Generate a signed manifest and immutable receipt; revocation must distinguish exact records from broad-origin matches and require confirmation for destructive scope.
- **missing:** A unified inventory schema linking facts, graph entities, capsules, notes, audio, and relay events; Cross-store export and revocation orchestration with source-level provenance; A durable policy for retention, sensitive fields, and export formats


## What it asked for

_Nothing._
## Its own summary

Round 185 produced three distinct owner-facing capabilities: source-linked safe page notes, deadline-aware missed-brief catch-up, and a source-scoped 'forget everywhere' cascade. The delivery-status idea was correctly rejected as already present in the backlog, so I did not rephrase it. The live device inventory confirms the Mac bridge is online while the cloudflare test device is offline; the owner’s stated timezone (Chicago) still conflicts with the Mac-authoritative routine zone (New York), so I will not silently use either for personal location.

**Biggest unknown:** I still need the owner’s explicit disclosure and interruption policy (what may be spoken aloud, quiet windows, trusted destinations) and implementation work for the missing cross-store provenance/revocation links, fleet-memory writer, browser provenance mounting, and routine-to-delivery-ACK join. The owner’s prior preference requests were declined, so these remain policy decisions rather than facts I can infer.

