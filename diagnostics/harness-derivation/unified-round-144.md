# Harness derivation — unified — round 144

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Buy/book/send this, but make me approve it on the pendant first.”"
- **useful because:** This would be the first genuinely end-to-end safe action: the owner can initiate a consequential task by voice, have the browser use the already-authenticated session, inspect the exact resulting plan, physically approve the staged transaction on the pendant, and hear a receipt. Today the approval primitive exists in firmware and the Mac has planning/execution, but the relay persistence, delivery/readback, and execution handoff are not joined; blocked plans can currently be spoken about and discarded.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use deterministic code for digest/world/replay checks and routing; use the background/planner tier only to turn the spoken goal into a bounded action plan; reserve realtime for the short spoken confirmation and result.
- **latency:** Plan preview in 2–5 s; pending state and physical approval within one natural conversational turn; execution receipt within 10 s after approval, with explicit queued status for slower sites.
- **cost:** Roughly $0.01–$0.08 per invocation depending on planner use; browser and relay work dominate latency, not the approval check.
- **security:** Never send page secrets or contents to the pendant. Bind approval to plan digest, world fingerprint, expiry, nonce and replay counter; require the pendant's physical approval event and refuse if the tab/world changed. Browser actions and irreversible/off-machine actions require confirmation; redact receipts before speaking or storing them.
- **missing:** Implement the APPROVAL_STORE_CONTRACT on the relay, rather than its current schema-only description; A delivery/readback path that marks approval delivered; the pendant cannot receive unsolicited binary pushes, so stage it for the next conversation or use the accepted pending transaction firmware path; Wire prepareAction into the orchestrator/browser bridge and hand the approved nonce to execution; Separate approval authority from the general AGENT_TOKEN; Close ordinary action ledgers and add relay job leases before any resume/retry behavior

### "“Stop everything private right now, and tell me when the whole system is actually quiet.”"
- **useful because:** The pendant's local privacy latch already stops capture and playback even without a link, but the owner still needs a trustworthy system-wide answer: relay jobs must stop persisting audio, browser exposure must be withdrawn, queued Mac work must be held, and the result must distinguish local mute from full convergence. This turns a physical safety action into a comprehensible guarantee rather than a blinking LED.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic state convergence and authenticated receipts; no expensive model is needed except optional realtime wording of the short spoken status.
- **latency:** Local mute is immediate; cross-surface convergence receipt in under 2 s when links are live, otherwise report exactly which surfaces remain unconfirmed and retry on reconnect.
- **cost:** Under $0.005 per check; dominated by a few authenticated state reads and receipt writes.
- **security:** The pendant's local latch remains authoritative and must not be cleared remotely. Use a latch ID and monotonic event counter; stop new capture and playback before querying other surfaces; do not expose transcript/audio contents in diagnostics. A stale or missing surface must produce UNKNOWN, never a false quiet result.
- **missing:** Relay-side cancellation/hold semantics for queued and processing jobs; Browser command revocation and a running lease sweeper; A signed, cross-surface convergence receipt that joins pendant, relay, Mac and browser state; A clear boot policy for the persistent latch and a recovery UX when a surface is offline

### "“Make sure I actually hear every answer; if the link drops, recover it or give me a text fallback.”"
- **useful because:** A relay receipt currently can prove that an artifact was accepted, downloaded, or started, but acceptance is not hearing. This capability closes the last meter: retain encoded downlink packets briefly, correlate pendant/bridge playback acknowledgements with sequence ranges, repair a missing range inside the jitter window, and fall back to a short text/status delivery when repair is impossible. The owner gets fewer answers that silently vanish during simultaneous loss.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Deterministic packet/receipt correlation and recovery; use a cheap background model only to compress a failed spoken answer into a text fallback. No realtime reasoning is needed.
- **latency:** ACK and gap detection within one 60 ms audio frame; repair within 250 ms when buffered; text fallback within 2 s after the retry budget expires.
- **cost:** About $0.001–$0.01 per answer for bounded relay packet retention and an occasional cheap fallback summary; storage and retransmission dominate, not inference.
- **security:** Retain only encrypted, short-lived encoded packets keyed by artifact ID; delete on confirmed playback or expiry. Never write routine audio to the pendant SD card. Bind ACKs to artifact ID, sequence range, checksum and session nonce to prevent replay or cross-session injection. A fallback must say it is a fallback, not claim the owner heard audio.
- **missing:** Firmware/bridge playback ACK frame carrying artifact ID, sequence range, checksum and start/finish/interruption state; Relay packet retention and selective retransmission within the 60 ms framing/jitter budget; A policy for when to stop repair and generate a text fallback; Integration with the existing audio_delivery_ack_queue and 24 kHz duplex congestion guard

### "“Queue this action for later, but make it impossible to send unless I explicitly release it—or cancel it from the pendant before the deadline.”"
- **useful because:** The owner could safely prepare a consequential email, purchase, upload, or form while attention is elsewhere, without trusting a Mac process to fire immediately. The relay would hold an exact action escrow; the pendant would provide a physical release/cancel control even if the Mac or browser is temporarily disconnected. This is different from one-shot approval: the owner gets a deliberate cooling-off window and a durable cancel path.
- **path:** relay-realtime → pendant → browser-extension → mac-planner → dashboard
- **model tier:** Deterministic escrow state machine, expiry and nonce checks; planner tier only creates the initial bounded action plan. No realtime model is needed after staging.
- **latency:** Staging in under 5 s; pendant cancel/release acknowledged within 1 s when linked; expiry and cancellation remain durable offline and reconcile on reconnect.
- **cost:** $0.005–$0.03 per staged action, dominated by planner inference and short-lived relay storage.
- **security:** Store a digest and minimal redacted parameters, never credentials or full page secrets. Bind the release/cancel token to plan digest, browser world fingerprint, expiry, device counter and single-use state. Default to cancel on expiry or world change. Never infer release from silence, speech ambiguity, or a Mac reconnect.
- **missing:** A durable relay escrow record and worker that never executes before release; A release/cancel protocol using the accepted physical transaction approval latch, with explicit distinction between release and cancel; Browser/Mac executors that revalidate tab identity and world fingerprint immediately before release; An owner-visible countdown and immutable audit trail

### "“For the next conversation, answer me using my open tabs and Mac, but do not retain the question, page contents, audio, or action history anywhere.”"
- **useful because:** The owner currently has a privacy stop, but no affirmative, scoped ‘ephemeral session’ that still permits useful work. This would let the pendant answer a sensitive question from authenticated browser/Mac context while making retention behavior explicit: no relay transcript, no routine audio spool, no browser result archive, and automatic destruction of temporary state at session end or timeout.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Deterministic no-retention policy enforcement and deletion receipts; use realtime only for the conversation itself, with no background summarizer or memory writer.
- **latency:** Session activation in under 1 s; normal conversational latency; end-of-session erasure receipt in under 2 s when surfaces are online, otherwise clearly marked pending.
- **cost:** Similar to an ordinary conversation, plus small bounded metadata and deletion checks; under $0.01 extra per session.
- **security:** The policy must be fail-closed: if a surface cannot attest to no-retention, refuse to expose its contents. Prevent model-memory, browser-spool, job-log, audio-card and Mac temporary-file writes; scrub secrets from diagnostics. A session nonce, expiry and authenticated deletion receipt are required, but the receipt must contain no sensitive content.
- **missing:** A propagated ephemeral-session policy understood by relay, Mac executor, browser bridge and pendant; No-store/no-log hooks for pipeline, browser results, action receipts and temporary files; A deletion/convergence verifier that distinguishes deleted, never-created and unknown; A clear physical start/end gesture or spoken confirmation bound to the session nonce

### "“Show me exactly what would change if you did that—files, tabs, messages, and settings—without doing anything yet.”"
- **useful because:** The owner cannot currently get one trustworthy, cross-surface dry run. A Mac plan, browser inspection, and action receipt each describe only their own surface, and the existing approval machinery is difficult to reach. This capability would produce a before/after diff and explicit unknowns for a spoken request, so the owner can make an informed decision before any mutation or browser submission.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic state collection, diffing and risk classification; planner tier only decomposes ambiguous requests. Spoken rendering can use realtime, but the diff itself must not be model-invented.
- **latency:** Simple Mac/browser previews in 3 s; multi-surface previews in 8 s; never execute as a side effect of preview timeout or partial results.
- **cost:** $0.005–$0.04 per preview, mostly planner inference for ambiguous goals; reads and hashing are inexpensive.
- **security:** Read only by construction. Bind every diff row to a surface, timestamp, path/tab identity and hash; mark inaccessible state as unknown rather than guessing. Redact credentials and sensitive page text. Require a fresh physical approval for any later execution, and invalidate the preview if the world fingerprint changes.
- **missing:** A typed cross-surface preview schema with before/after/unknown and risk fields; Read-only browser and Mac inspectors that return stable hashes and tab/session identity; A spoken-friendly diff renderer with a dashboard expansion for full detail; A handoff from preview digest to the existing physical transaction approval flow


## What it asked for

_Nothing._
## Its own summary

Round 144 produced three distinct proposals: (1) an end-to-end voice-initiated browser transaction that is staged, physically approved on the pendant, executed, and receipted; (2) a system-wide privacy stop with authenticated convergence instead of merely a local mute LED; and (3) reliable spoken delivery with packet-range ACKs, bounded retransmission, and an honest text fallback. Discovery also confirms the ESP32 bridge is still prototype hardware, SBC-only at 44.1 kHz stereo, with a known 44 kB-buffer starvation limit.

**Biggest unknown:** I still need an implementation-level inventory of the relay approval and audio-recovery seams: whether the existing prepare/approval modules are actually mounted and persisted in the live server, what exact pendant↔bridge frame fields can be extended for playback ACKs, and whether relay jobs can be cancelled/leased rather than left processing. I also still need the owner's product decisions (standalone-without-phone requirement, talk-time/standby/size/thermal targets) before recommending a production bridge or transport.

