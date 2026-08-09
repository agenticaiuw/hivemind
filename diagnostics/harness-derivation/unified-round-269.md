# Harness derivation — unified — round 269

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Stage this sensitive browser action, tell me exactly what will happen, and only submit it after I physically approve it on the pendant.”"
- **useful because:** Makes the pendant a real consent boundary for logged-in browser actions instead of relying on a bearer-token Mac agent. The Mac/browser can prepare the action, but neither can silently cross the final submit boundary.
- **path:** relay → browser → mac-bridge → pendant → dashboard
- **model tier:** background for staging and world-diff explanation; realtime only for the spoken readback; deterministic code for digest, expiry, and nonce checks
- **latency:** Stage in under 10 seconds; spoken readback in the next turn; submit within 2 seconds after the pendant approval arrives
- **cost:** <$0.01 per staging attempt; dominated by one planner call and browser snapshots, not the approval event
- **security:** Never send page secrets to the pendant. Bind approval to plan digest, browser target, world fingerprint, expiry, and one-use nonce. Refuse if the page changed or the approval is replayed. The current prepare/approve path is structurally incomplete: relay approval persistence and a delivery/readback path are missing, and the owner must initiate the next conversation rather than receive an unsolicited prompt.
- **missing:** Implement the APPROVAL_STORE_CONTRACT in the relay; Expose a conversation-start delivery path that marks deliveredAt before accepting spoken/physical approval; Bind browser command receipts and target tab identity into the plan digest; Use physical_transaction_approval_latch as the final local consent event

### "“Before you continue the interrupted task, show me what already happened, what could safely be repeated, and ask me only about the step that might duplicate an external action.”"
- **useful because:** Turns crash recovery from a hidden engineering primitive into a trustworthy owner-facing handoff. It prevents duplicate messages, purchases, or browser submissions while allowing idempotent local work to continue automatically.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** deterministic ledger/replay classifier and receipt join; background model for concise explanation; realtime only when the owner asks during a live conversation
- **latency:** Recovery inventory in under 3 seconds; safe steps may resume immediately; any approval request waits for the next conversation and physical confirmation
- **cost:** <$0.01 per recovery; dominated by a single explanation call if needed
- **security:** Gate on replaySafety, not reversibility: auto-resume only idempotent/additive steps with a live lease; ask for unrepeatable/unknown steps and block all later steps. Close ordinary ledgers correctly before scanning, distinguish stale processing jobs from interrupted work, and never infer completion from a missing receipt.
- **missing:** Call closeLedger from orchestrator and repair false interrupted-ledger positives; Add relay job lease_until and requeue sweep; Run the existing planResume engine from a controlled owner-facing route; Join ledger steps to browser/Mac receipts and expose a physical approval path for unsafe continuation

### "“Stop the thing you are doing right now.” (or use the pendant privacy-latch press to abort it)"
- **useful because:** A spoken request and a physical latch should stop active Mac, browser, relay, and queued work—not merely stop new audio. This gives the owner a single emergency abort that works when the current task is surprising or unsafe.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic cancellation and receipt fan-out; realtime model only to acknowledge the request and summarize what was actually stopped
- **latency:** Local microphone/playback mute immediately; relay cancellation fan-out under 1 second; final convergence receipt under 5 seconds
- **cost:** <$0.002 per abort, mostly authenticated cancellation calls and status reads
- **security:** The pendant's local_privacy_latch must remain authoritative for immediate capture/playback stop. Cancellation is best-effort for already-committed external effects: revoke unclaimed browser commands, cancel Mac jobs, mark non-cancellable steps as completed/irreversible in the receipt, and never claim rollback occurred without an undo receipt. Require an authenticated latch event ID and deduplicate it.
- **missing:** Relay endpoint that atomically fans out cancellation to the claimed job and its browser/Mac descendants; Mac executor cancellation checkpoints between actions; Browser command revocation that prevents a queued command from being delivered after abort; A single convergence receipt distinguishing stopped, already-completed, and unable-to-undo effects

### "“If the pendant drops or its battery dies, continue this exact conversation on my Mac without making me repeat myself.”"
- **useful because:** The wearable is the best microphone and attention surface, but it is not reliable enough to be the only endpoint. A relay-held, encrypted turn handoff would let the owner continue naturally through the Mac while preserving the pending question, partial transcript, response state, and audio position.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** deterministic session handoff and sequence reconciliation; realtime model only for the next spoken turn if the handoff has incomplete transcript audio
- **latency:** Detect loss in under 3 seconds and expose a ready continuation on the Mac within 5 seconds; no duplicate response or replayed audio
- **cost:** <$0.01 per handoff; dominated by session-state storage and, only when needed, one short reconciliation inference
- **security:** Encrypt handoff state, bind it to the authenticated owner session and device identities, expire it quickly, and never expose raw buffered audio beyond the active turn. Use monotonic turn IDs and idempotent acknowledgements so reconnects cannot duplicate a command or response.
- **missing:** A relay session-handoff record containing transcript checkpoint, model response checkpoint, audio sequence, and expiry; A Mac/browser takeover control that proves the destination is the owner's authenticated surface; Cross-device sequence reconciliation and duplicate-audio suppression; A pendant event that marks transport loss without treating a temporary packet gap as a handoff

### "“Before anything leaves my devices or is entered into a website, tell me what data is being sent and enforce my private/public rules automatically.”"
- **useful because:** The owner needs a destination-aware privacy boundary, not just a local mute. It would prevent accidental disclosure through browser forms, messages, research uploads, relay persistence, and model context while still allowing explicitly permitted actions.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic data-label policy engine and redaction; background model only to classify ambiguous content, never to override a deny rule
- **latency:** Policy decision under 100 ms for known labels; ambiguous content pauses for an owner-facing explanation and confirmation rather than silently delaying or allowing
- **cost:** <$0.005 per guarded action; classification cost only for novel text or page fields
- **security:** Default deny for unknown destinations and sensitive labels. Show destination, fields, retention, and whether content crosses off-machine boundaries. Keep the policy engine local where possible; transmit only a redacted decision capsule to the relay. Never treat model classification as authorization.
- **missing:** A common egress-event envelope for pendant, Mac, browser, and relay writes; Owner-editable data labels and destination policies with deny/allow/ask semantics; Browser field interception and Mac action preflight hooks; A redaction engine that preserves task utility without leaking protected values; An audit view showing what was blocked, allowed, or owner-approved

### "“Tell me when you are no longer sure what is true, and stop acting until the uncertainty is resolved.”"
- **useful because:** Today the system can combine stale browser state, interrupted jobs, missing receipts, and partial audio into a confident answer. An owner-visible uncertainty barrier would prevent the most dangerous failure: a plausible claim or external action built on contradictory cross-surface evidence.
- **path:** relay → pendant → mac-bridge → browser → dashboard
- **model tier:** deterministic contradiction and freshness checks; background model to explain the conflict; realtime only to speak a concise hold message
- **latency:** Detect contradictions during evidence collection in under 500 ms; block an external action immediately; explain the specific missing proof within 3 seconds
- **cost:** <$0.003 per guarded decision; mostly hashes, timestamps, and receipt joins
- **security:** Never let a language model downgrade a hard contradiction. Bind each assertion to source, timestamp, and receipt provenance. Distinguish unknown, stale, conflicting, and completed-but-unverified. Require explicit owner confirmation before proceeding from an unresolved state.
- **missing:** Cross-surface freshness and contradiction schema; Evidence quorum rules for browser, Mac, relay, and pendant outcomes; Planner integration that turns uncertainty into a hold rather than a best guess; A pendant-visible uncertainty state that does not masquerade as a successful reply


## What it asked for

_Nothing._
