# Harness derivation — mac-planner — round 250

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "After a call, tell me in one sentence whether the bad audio was my network, the pendant CPU, or the server, and leave a reproducible report if it was not my network."
- **useful because:** Today a distorted call leaves the owner guessing and engineers without a synchronized trace. The pendant already measures codec and loss counters; the Mac can add USB/bridge and network observations; the relay knows reconnects and packet timing. Correlating those into one post-call verdict turns an intermittent wearable failure into an actionable explanation without recording conversation content.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Deterministic classifier first; use the inexpensive background model only to turn the evidence into a short spoken sentence and a cited report. Realtime is unnecessary after the call.
- **latency:** Generate the verdict within 10 seconds of call end; write the report within 30 seconds. No additional latency during the call beyond compact QoS frames.
- **cost:** Usually under $0.01 per call; most work is counter aggregation and a small report. A model call is only needed for ambiguous evidence.
- **security:** Store counters, timestamps, firmware/build ids, and network metadata, never PCM or transcript. Reports may contain serial/device identifiers, so redact them in spoken output and retain full detail only in the local workspace. Automatic filing is low-impact but network upload should be configurable.
- **missing:** A relay endpoint that joins duplex_audio_congestion_guard QoS frames, websocket lifecycle, and server packet timing into one call record.; A bounded Mac USB/bridge diagnostic read that can correlate bridge underruns with pendant sequence numbers (the existing read-only serial diagnostic is not a general session).; A report template and post-call routine that emits both a short voice result and a local cited artifact.

### "If my Mac task is interrupted or the laptop sleeps, tell me on the pendant what finished, what did not, and let me resume it without doing steps twice."
- **useful because:** Long browser and file jobs currently fail at the worst moment: the owner has no trustworthy boundary between completed and pending work. An atomic workbench receipt plus relay job state can turn an interruption into a clear, spoken recovery choice, while the pendant is the only surface likely to be noticed away from the desk.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic transaction and receipt handling; a cheap background model summarizes the receipt into one sentence. Realtime is used only if the owner asks the pendant for status.
- **latency:** Persist a checkpoint before each irreversible step; detect a lost Mac heartbeat within 15 seconds. Spoken status in under 2 seconds after request; resume planning under 5 seconds.
- **cost:** Pennies or less per job; storage and idempotency dominate, with a model call only for a human summary.
- **security:** Receipts must contain resource names and hashes but not document contents, page bodies, or credentials. Resume must use the same job_id and verify hashes before replaying. Destructive actions remain governed by the owner's runtime policy, and the pendant should offer status—not silently approve them.
- **missing:** A relay coordinator that consumes Mac workbench handoffs and exposes a pending/resume state to the pendant inbox.; A heartbeat and per-step completion protocol from mac-planner to distinguish a clean stop from a crash.; A browser action wrapper that accepts an idempotency key for retries across an interrupted session.

### "When you give me a short morning brief, let me say “show me that” and open the exact supporting email, calendar event, or browser source on my Mac."
- **useful because:** A spoken summary is useful until one item needs verification; today the owner must remember the words and search manually. Stable item ids and source-aware handoff would make the pendant a fast index into the Mac and authenticated browser, while keeping the spoken answer short.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap model to rank and phrase the existing brief. Retrieval by source id and opening the target are deterministic; realtime is only needed for the follow-up utterance.
- **latency:** The brief remains under normal routine latency. Resolve “show me that” in under 3 seconds and open the source within 5 seconds, with a spoken fallback if the Mac/browser is offline.
- **cost:** Under $0.01 per follow-up; token cost is small because the relay sends an item id, not the whole brief or message body.
- **security:** Never speak or transmit full private mail unnecessarily. Bind source ids to the account and expiry, redact snippets in logs, and open the authenticated page/document locally. Sending mail or changing calendar items remains outside this read/open capability.
- **missing:** A briefing schema that preserves opaque source references through summarization and audio delivery.; A relay intent resolver for pronouns such as “that” against the last surfaced item, with expiry and ambiguity handling.; A browser/mac open-source adapter for mail, calendar, and authenticated pages that returns a success receipt.

### "When I latch privacy on the pendant, immediately pause every pending Mac and browser automation, revoke any browser handoff token, and tell me when nothing can still act on my behalf."
- **useful because:** The existing local privacy latch protects the pendant's microphone and speaker, but a queued Mac job or authenticated browser session could continue acting while the owner believes privacy is engaged. This gives the physical latch authority over the whole hive: one local gesture stops remote agency, even in a dead zone, and the system reports any action that was already committed.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** No model call for the stop path: a signed, idempotent revocation event and deterministic cancellation fan-out. Use the inexpensive background tier afterward to summarize what was cancelled versus already committed.
- **latency:** The pendant LED/state change is immediate. Relay-side cancellation should reach Mac and browser workers within 1 second when connected; the local latch must remain safe and effective while offline, with reconciliation on reconnect.
- **cost:** Negligible per event; cost is durable revocation state and cancellation delivery, not inference.
- **security:** This is a high-authority safety control and must be authenticated, replay-resistant, and monotonic until locally cleared. Cancellation cannot undo an email already sent or a file already deleted, so the receipt must distinguish committed from prevented actions. Do not log sensitive URLs or page contents in the spoken acknowledgement.
- **missing:** A relay-wide revocation epoch checked before every Mac/browser action, including already queued jobs.; A cancellation endpoint and acknowledgement protocol for the Mac job queue and browser sessions.; A firmware-to-relay signed privacy-latch event path that works after reconnect and reconciles missed revocations.; A dashboard and pendant status record showing cancelled, committed, and unknown-in-flight actions.

### "When I give the pendant an instruction with no connection, queue it as a time-limited intent and execute it exactly once when the Mac/browser and relay reconnect, after checking that the facts it depended on are still true."
- **useful because:** Offline capture today can preserve a moment or audio, but it cannot preserve an actionable commitment. This would let the owner use the pendant in a subway or on a walk for real work, without either losing the instruction or blindly replaying a stale action hours later.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a small deterministic intent envelope and fact checks; reserve the expensive model for parsing the original utterance and resolving genuine ambiguity. Never infer permission to perform a new high-impact action from a stale offline command.
- **latency:** Local acknowledgement under 200 ms. On reconnect, validate prerequisites in under 5 seconds and either execute once or ask the owner; no repeated retries after an uncertain commit.
- **cost:** A few cents at most for an offline utterance parse and reconnect validation; durable queueing and hash checks dominate engineering, not API usage.
- **security:** Persist only an encrypted, expiry-bounded intent and minimal redacted context on the pendant/relay. Require an explicit owner policy for sends, purchases, deletions, or external messages. Bind execution to account, target, and precondition hashes so a changed browser page or recipient cannot silently receive a stale action.
- **missing:** A compact encrypted actionable-intent record and firmware queue distinct from the existing voice-memo/bookmark payloads.; Relay-side exactly-once state machine with expiry, deduplication, and precondition validation.; Mac/browser executor support for idempotency keys and an explicit stale-context result.; A clear pendant interaction for “queued”, “executed”, “expired”, and “needs me”, using the existing single LED/inbox semantics.

### "Let me say “undo what you just did” and have the hive identify the last completed Mac/browser actions, reverse every safe one, and explain the exact irreversible remainder."
- **useful because:** Receipts and job status can tell the owner what happened, but they do not turn that knowledge into recovery. A spoken undo across multiple surfaces would make automation tolerable in daily use: it can close tabs, restore moved files, revert created notes, or stop a queued job while plainly identifying actions that cannot be reversed.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic inverse-action registry and receipt matching; use a small model only to resolve “that/just did” when several actions are plausible. High-impact inverses should be presented as a plan, not guessed.
- **latency:** Resolve the target and produce an inverse preview in under 2 seconds; execute reversible inverses within 5 seconds. The owner should hear an immediate acknowledgement while the receipt reconciliation completes.
- **cost:** Usually below $0.01; the main work is maintaining inverse metadata and durable before-state snapshots, not inference.
- **security:** Before-state snapshots must be encrypted and minimized. Never claim success without a verified postcondition. Deleting or sending cannot be magically undone; distinguish restored, cancelled, and irreversible. The owner’s existing destructive-action policy must govern any inverse that itself has side effects.
- **missing:** A cross-surface action ledger joining Mac receipts, browser command ids, and relay jobs in causal order.; Inverse metadata and bounded before-state capture for each supported Mac/browser action.; A spoken target disambiguation protocol and a deterministic postcondition verifier.; A retention policy for recovery snapshots that avoids storing private page bodies or document contents.


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate recorded capabilities: post-call audio fault attribution with a local evidence report; pendant-visible, idempotent recovery for interrupted Mac/browser jobs; and source-linked follow-up for morning briefs (“show me that”) that opens the exact email, event, or authenticated page. The interrupted-job recovery is the highest-value addition: it prevents both lost work and duplicate side effects across pendant, relay, Mac, and browser.

**Biggest unknown:** The still-missing semantic Mac context read and relay correlation layer are the main blockers for high-quality cross-surface handoffs. I also still lack a reliable browser restore/idempotency adapter; Accessibility remains owner-controlled and unavailable, so these designs must use existing AppleScript/browser bridges or wait for that grant.

