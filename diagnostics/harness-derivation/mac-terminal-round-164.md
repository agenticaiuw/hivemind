# Harness derivation — mac-terminal — round 164

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What happened to everything I asked you to do while I was away? Tell me what completed, what failed, and what is still uncertain.”"
- **useful because:** Today job status, pendant beacons, browser state, and Mac journals are separate and can contradict each other. A single spoken reconciliation would prevent the owner from believing a queued or orphaned action completed, especially after a Mac restart or USB/LTE interruption. This is the highest-value trust feature: one answer about reality across every body.
- **path:** pendant → relay → mac-planner → browser → dashboard-ux
- **model tier:** background for collecting and correlating receipts; realtime only to answer a follow-up question over the pendant
- **latency:** Under 5 seconds for a normal digest; under 1 second to read a cached digest from the pendant
- **cost:** About $0.01–$0.04 per digest if a model is needed; most cost is avoided by deterministic receipt joining and short summaries
- **security:** Only action metadata, statuses, timestamps, and redacted result snippets leave the Mac; never transmit shell environment, tokens, or private browser page contents. Require confirmation before replaying anything; state uncertainty instead of inferring completion.
- **missing:** A durable cross-surface correlation record joining pendant turn/request IDs, relay jobs, Mac job IDs, action receipts, browser command IDs, and ledger entries; Boot-time reconciliation of processing jobs and open ledgers, including explicit orphaned/unknown outcomes; A deterministic status reducer that distinguishes completed, failed, cancelled, queued, stale, and never-confirmed; A compact relay endpoint and pendant cache for the last digest

### "“My pendant is plugged into my Mac but has no LTE—let me talk normally anyway, and keep the same conversation when I unplug it.”"
- **useful because:** The hardware is physically present and testable now, but LTE registration is not. The owner should not lose the core voice experience merely because the radio is unavailable: USB serial can carry control and audio through the Mac, then hand the live turn back to LTE later without duplicate replies or lost recordings.
- **path:** pendant → mac-planner → relay → relay-realtime
- **model tier:** realtime for audio turn-taking and interruption; background model only for deferred transcription/summarization after link loss
- **latency:** First audio within 300 ms of button press; USB transport failover under 1 second; reconnect handoff under 2 seconds
- **cost:** No additional model call for transport; roughly one normal realtime turn cost, with a background transcription fallback only when frames were buffered
- **security:** USB serial is local to the owner's Mac; authenticate the serial peer and bind each stream to a turn nonce. Never silently send buffered microphone audio after the owner has ended a turn. Show link mode and age via truthful_action_status_beacon, and erase abandoned audio buffers after a short TTL.
- **missing:** A Mac serial adapter for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA that exposes framed bidirectional audio/control to the local agent; A relay-realtime transport abstraction that treats USB and LTE as interchangeable legs while preserving turn ID, replay cursor, and acknowledgements; A bounded jitter buffer and codec conversion for the ESP32 bridge, with echo/clock drift handling; A handoff protocol that chooses exactly one response sink when USB and LTE overlap

### "“Run this Mac command, and if it fails, figure out why and recover without making me repeat the request; then tell me exactly what ran.”"
- **useful because:** The current shell path discards exit codes, cannot interrupt a running child, does not retry, and leaves jobs marked processing after a crash. A self-healing execution receipt would turn opaque failures into useful outcomes while preserving the owner's deliberate maximum-access policy.
- **path:** mac-planner → mac-terminal → relay → dashboard-ux → pendant
- **model tier:** cheap deterministic executor and classifier first; background model only for repair planning; realtime is used only if the owner is actively waiting on the pendant
- **latency:** Immediate commands under 2 seconds; one bounded repair attempt within 10 seconds; never spend more than the existing 120-second command timeout without reporting progress
- **cost:** Usually no model cost for exit-code classification; $0.005–$0.03 only when a repair plan needs reasoning. Dominant cost is an extra bounded command attempt.
- **security:** No approval gate is added, matching owner policy. Record command text, cwd, timeout, exit code, signal, stdout/stderr hashes and redacted excerpts; never persist inherited environment values or secrets. Repairs must be tied to the original job and explicitly labeled as additional mutations. Never claim success when the process was killed or the result is unknown.
- **missing:** Execute shell with an abort signal, captured exit code/signal/PID, bounded output, and per-attempt timestamps; A retry/repair state machine with idempotency keys and command-specific recovery policies; Boot reconciliation that marks processing jobs and open ledgers as interrupted/unknown and offers resumable actions; A durable join between jobId and ledger/action receipt, plus a human-readable execution receipt endpoint; A typed diagnostic/repair planner that can use stderr and host state without exposing secrets

### "“After you change something on my Mac or in the browser, prove the requested outcome is true—not merely that the action returned successfully.”"
- **useful because:** A zero exit code or browser click receipt does not mean the owner's goal happened. A postcondition check can catch wrong window, stale tab, failed save, or a command that silently did nothing, and can speak a concise proof through the pendant.
- **path:** mac-planner → mac-vision → browser-extension → relay → pendant
- **model tier:** deterministic checks and DOM/file/app queries first; background model for ambiguous visual or semantic verification; realtime only to narrate a failure while the owner waits
- **latency:** Add no more than 1 second for typed checks and 3 seconds for a visual/semantic check
- **cost:** Near zero for typed checks; $0.005–$0.02 for an occasional screenshot/semantic verifier. Main cost is an extra read after mutation.
- **security:** Verification reads may expose private browser content or files, so send only a redacted predicate result upstream. Keep evidence local by default, with opt-in screenshots. Do not auto-repair based on ambiguous evidence; report unknown.
- **missing:** An action contract carrying a requested postcondition alongside each Mac/browser action; Typed verifiers for file existence/hash, focused app/window, URL/title, DOM state, and saved/downloaded artifacts; A receipt schema storing predicate, evidence source, checkedAt, and true/false/unknown; A cross-surface result presenter that maps verification to the pendant's truthful status beacon

### "“Take the document I’m looking at in Safari, save a copy into the right project folder, remember where it came from, and remind me if that source changes.”"
- **useful because:** The owner currently has separate browser sessions, Mac filesystem actions, project context, and watches. They cannot safely turn a private authenticated page into a local, provenance-preserving project artifact with a future change alert in one request. This would make the browser's unique session reach and the Mac's local storage reach useful together without sending page credentials to the cloud.
- **path:** browser-extension → mac-planner → mac-terminal → relay → pendant → dashboard-ux
- **model tier:** background model for document identification and metadata extraction; deterministic Mac/browser actions for download, hashing, and watch registration; realtime only for a spoken clarification
- **latency:** Acknowledge immediately; complete ordinary downloads within 15 seconds; return a durable receipt even if the browser or Mac disconnects
- **cost:** Usually $0.01–$0.05 for extraction/classification; storage and watch polling dominate ongoing cost, not model inference
- **security:** The authenticated page stays inside the browser extension. Transfer only the selected artifact or an explicitly approved download to the Mac over a local authenticated channel; redact cookies, tokens, and unrelated tab content. Show source URL, timestamp, local path, and content hash before creating a watch. Never silently upload the document to the relay.
- **missing:** A local browser-to-Mac artifact handoff protocol that streams a selected download without exposing browser session secrets; A provenance manifest binding source URL, tab/session identity, retrieval time, content hash, local path, and project entity; A content-change watcher that can compare authenticated re-fetches and notify without leaking document contents; A user-visible artifact receipt and conflict policy when the source changes or the destination file already exists

### "“Find the thing I saw recently—whether it was a Safari tab or a file on my Mac—and show me the exact source and the shortest path back to it.”"
- **useful because:** Today browser history/session state and local project files are separate worlds. The owner cannot use the pendant as a trustworthy memory of an item that crossed those boundaries. A local cross-surface index would answer from current evidence, not hallucinated conversation memory, and give a reopenable destination.
- **path:** pendant → browser-extension → mac-planner → relay → dashboard-ux
- **model tier:** Local deterministic indexing and lexical/embedding retrieval first; background model only to disambiguate a vague description; realtime only for the spoken answer
- **latency:** Under 2 seconds for recent items; under 8 seconds for a cold index query
- **cost:** Near-zero for local retrieval; occasional $0.005–$0.02 background disambiguation. Storage/indexing is the main local cost.
- **security:** Keep page titles, URLs, file names, and embeddings on the Mac by default; do not upload page bodies or paths to the relay. Respect browser session boundaries and exclude private windows or explicitly marked folders. Return evidence and confidence, not inferred personal facts.
- **missing:** A local encrypted index spanning browser tab metadata/download provenance and selected Mac project files; A common item identity with source URL, local path, timestamps, and content hash; A privacy/retention policy and exclusion controls exposed to the owner; A typed reopen/focus action that can return to the exact Safari tab or Finder file

### "“Undo the last thing you changed, wherever you changed it, and leave everything else alone.”"
- **useful because:** The current undo path is action-type-specific and cannot span a Mac mutation, a browser command, and a relay job as one owner-visible operation. The owner cannot safely recover from a mistaken multi-surface request without manually reconstructing what happened. A causal, minimal rollback would make maximum-access automation survivable.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard-ux
- **model tier:** Deterministic causal ledger and compensating actions first; background model only when a human-readable rollback plan is ambiguous; realtime to report exactly what could and could not be reverted
- **latency:** Under 3 seconds to identify the last causal chain; under 15 seconds for bounded compensations; immediately report irreversible portions
- **cost:** Usually no model cost; $0.005–$0.03 for ambiguous compensation planning. Snapshot storage and verification are the dominant costs.
- **security:** No new approval gate is implied. Rollback must be scoped to the exact causal chain, preserve unrelated edits, and refuse to pretend irreversible sends/deletes were undone. Store pre/post hashes and redacted receipts locally; browser rollback must never expose session cookies or page contents.
- **missing:** A causal transaction ID propagated from pendant turn through relay, browser commands, Mac jobs, and action receipts; Pre-state snapshots or inverse operations for supported file, browser, and app actions; A dependency-aware compensator that orders inverse actions and marks irreversible effects explicitly; A final verifier proving the restored predicates and a durable rollback receipt


## What it asked for

_Nothing._
## Its own summary

This round produced four owner-facing capabilities: (1) a cross-body “what happened while I was away?” reconciliation digest joining pendant, relay, Mac, and browser receipts; (2) USB-local pendant conversation with seamless LTE handoff, now testable against the physically connected nRF9160 and ESP32; (3) self-healing shell execution with exit codes, bounded repair, crash recovery, and truthful receipts; and (4) postcondition verification that proves a Mac/browser mutation achieved its requested outcome. The recorder accepted all four, while warning that shell recovery is close to an existing backlog item, so it should be treated as an extension rather than a separate roadmap promise.

**Biggest unknown:** The pending USB serial diagnostics capability has not arrived, so I still cannot verify the live serial framing, port ownership, baud/codec behavior, or whether the local agent can safely multiplex control and audio on the two connected chips. I also still lack confirmation that the ledger routes are live despite their names appearing in the established route contract. I need those facts before claiming the USB handoff can run today rather than merely being implementable.

