# Harness derivation — mac-terminal — round 279

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask “why didn't that work?”, give me one timeline from my button press through relay, Mac job, and USB device logs, and identify the first missing acknowledgement rather than making me repeat the story."
- **useful because:** Today each surface has a partial truth: the pendant knows a press, the relay knows a turn, the Mac knows a job, and the chips emit UART logs. A single causal answer would turn silent failures into an actionable diagnosis while the hardware is actually on the desk.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background for timeline assembly and correlation; realtime only to summarize the already-built incident when the owner asks
- **latency:** Capture events continuously with sub-second append; answer in under 3 seconds from indexed records. Do not stream raw audio or UART indefinitely.
- **cost:** Low ongoing storage cost; one short background correlation invocation per incident, dominated by log parsing rather than model tokens.
- **security:** UART may contain identifiers and Mac job output may contain sensitive paths or command text. Keep raw logs local, send only hashes, timestamps, state transitions, and redacted excerpts to relay; require explicit opt-in before including command stdout in a spoken answer.
- **missing:** A correlation record carrying one turn/request ID across pendant event, relay delivery, Mac job, and serial capture; A bounded local UART capture/indexer that tags nRF9160 and ESP32 lines with monotonic timestamps; A read-only incident query and redaction layer

### "Run a five-minute desk check and tell me whether the pendant, ESP32 audio bridge, Mac agent, and relay can complete a real speak-and-act turn, with the exact failing link and a copy-paste recovery command."
- **useful because:** The chips are physically connected now but not LTE-registered. A bounded bench test can validate the USB reality without pretending it proves wearable operation, preventing hours of debugging the wrong layer before I wear it.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** cheap background model for deterministic checks and parsing; escalate to realtime only if the owner is simultaneously speaking to the pendant
- **latency:** Start within 2 seconds, finish within 5 minutes, with progress after each phase: enumerate, UART health, audio loopback, authenticated relay round trip, cleanup.
- **cost:** Near-zero model cost if implemented as a fixed state machine; one short summarization call only on failure. Storage is capped, timestamped diagnostics under 1 MB per run.
- **security:** Never upload raw microphone/audio or unrestricted UART. Use generated tones and synthetic text, redact bearer tokens and paths, and make relay execution a separate explicit phase because the device is not LTE-registered.
- **missing:** A real host serial runner and framing parser (the granted schema is unresolved; current workaround is existing dual-chip capture scripts through run_shell); A generated-tone audio loopback assertion between ESP32 and pendant; A test-only relay echo endpoint and a cleanup/rollback phase; A single structured bench report route

### "When I say “I have to go,” freeze the thing we were doing into a resumable handoff: save the exact conversation turn, browser page and form state, Mac project/window context, pending actions, and what still needs my decision; later I can press the pendant and hear the shortest truthful resume briefing before continuing."
- **useful because:** Today a dropped conversation or a sudden interruption loses the owner's place across bodies. This would make the system feel continuous rather than like several unrelated assistants, especially when the owner is moving away from the Mac or the link disappears.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** cheap background model to compress the handoff and extract unresolved decisions; realtime only for the spoken resume briefing
- **latency:** Capture a durable handoff in under 2 seconds after the phrase or button event; resume briefing under 1 second from cached state. Browser/Mac restoration may take up to 10 seconds and must report each unavailable surface honestly.
- **cost:** One short summarization call per handoff, usually a few cents or less; storage is compact metadata plus references, not screenshots or audio by default.
- **security:** A handoff may contain authenticated URLs, draft text, or private conversation content. Keep sensitive page contents and screenshots local, encrypt the handoff store, expire stale browser credentials and drafts, and require an explicit physical button press before reopening or submitting anything.
- **missing:** A first-class resumable-handoff object with immutable source references, unresolved-decision fields, expiry, and partial-availability status; A browser freeze/restore primitive that preserves a tab plus unsent form state without submitting it; A Mac context checkpoint and restore operation for project, window, and focused document; Pendant-side indexing of handoff IDs and a compact offline spoken summary; A cross-surface resume transaction that can restore in dependency order and never claim a step succeeded merely because the checkpoint existed

### "Keep working on a multi-step task even when my Mac sleeps or disconnects: pause at a verified checkpoint, let the relay wait or do only safe cloud work, then resume on the Mac exactly where it stopped and tell me what changed while it was away."
- **useful because:** Today a laptop disconnect turns an ongoing task into an ambiguous failure. The pendant and relay can remain present, but they cannot hand a partially completed browser/Mac workflow back and forth with a truthful checkpoint.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model for checkpoint validation and plan compression; realtime only when the owner asks for a live status or gives a new instruction
- **latency:** Checkpoint after every externally visible step in under 500 ms; detect Mac loss within 10 seconds; resume within 5 seconds of reconnecting, with spoken status if the owner is wearing the pendant.
- **cost:** Low: durable state-machine records dominate; model calls only when compressing a long plan or resolving a changed page. No continuous realtime inference while paused.
- **security:** The relay must not replay Mac-local mutations or browser submissions without the Mac's fresh attestation. Encrypt checkpoints, expire authenticated browser references, and distinguish verified completion from merely dispatched work. Owner must be able to discard a paused task from the pendant.
- **missing:** A portable checkpoint format containing step preconditions, observed postconditions, idempotency keys, and a safe-to-run-on-relay classification; Mac reconnect handshake that reports which checkpoint side effects actually occurred; Relay-side dormant task storage and wake notification, without pretending it can access Mac-only sessions; Browser action resume that revalidates URL/page identity before continuing; Pendant controls for pause, discard, and truthful progress summaries

### "When a website asks for a one-time code, let me say “use the latest code” to the pendant; read the matching message from my real iPhone through Mac mirroring, fill only the waiting browser field, and erase the code from every transcript and log afterward."
- **useful because:** This is a daily moment where the owner must shuttle a code between devices. The browser session, real phone, Mac control, and wearable voice are each present but cannot perform this narrowly scoped handoff without exposing the secret to ordinary history.
- **path:** pendant → mac-bridge → browser → iOS → dashboard
- **model tier:** deterministic extraction first; a small model only to identify the currently focused OTP field and match the newest message. No realtime model is needed unless the owner is speaking live.
- **latency:** Under 5 seconds from the spoken request; fail closed if there are multiple plausible codes, the browser target changed, or the message is older than a configurable window.
- **cost:** Near-zero per use with local OCR/accessibility and structured DOM; occasional small-model extraction costs cents at most.
- **security:** The code is a high-sensitivity ephemeral secret. Keep it in memory only, never send it to the relay or LLM, never place it in Mac shell history, redact action receipts and screenshots, verify the exact origin and focused field, and require a physical press if confidence is not unambiguous. Delete the value immediately after submit or timeout.
- **missing:** A local-only iOS message reader over the existing Mac iPhone Mirroring surface; Browser-side OTP-field identity and origin binding; An in-memory secret channel between iOS reader and browser executor with zero durable plaintext; A scrubber that guarantees OTP values do not enter speech transcripts, job records, screenshots, or model context


## Changes it proposed to its own stack

### `mac-harness` — Add a command-attempt envelope around every run_shell execution: capture start/finish monotonic timestamps, numeric exit status, signal, effective cwd, a redacted environment fingerprint, stdout/stderr byte counts plus capped excerpts, and the pre-dispatch action hash. On failure, classify only deterministic transport/process failures and offer a generated next attempt; never silently rerun a mutation. Persist the envelope beside the job and join it to the action ledger via the real jobId. At boot, mark envelopes with no finish as interrupted and expose a recovery choice.
- **owner gets:** When a Mac action fails, the owner can see whether it was a missing executable, permission, timeout, wrong directory, or dead host—and can retry the safe fix instead of guessing. It also makes the pendant's “failed” light correspond to a verifiable process result rather than a vague exception.
- effort: Medium: replace exec with a child-process API that retains exit metadata, add redaction/fingerprinting, thread jobId into ledger creation, and add interrupted-envelope reconciliation. No access policy change.  ·  risk: Capturing command text or output can expose secrets; redact known token patterns and cap excerpts. A bad retry classifier could repeat a mutation, so retries are suggestions/explicit actions and default to no automatic rerun. If the agent crashes, an envelope may remain unknown rather than falsely completed.
- cost: Negligible CPU and disk; bounded per-attempt metadata and at most a few KB of excerpts. No model call for collection; optional cheap classifier only after failure.  ·  latency: Under 10 ms bookkeeping per command; no extra latency on success beyond child startup.
- security: Improves auditability without adding gates. Environment is fingerprinted, not copied; sensitive stdout is redacted and locally retained only under existing workspace policy.
- depends on: A small typed child-process execution wrapper that preserves current FULL_CONTROL_MODE semantics; Passing planMeta.jobId/current jobId into openLedger; Boot reconciliation for unfinished envelopes; A user-visible retry action that requires an explicit owner request for mutations


## What it asked for

_Nothing._
