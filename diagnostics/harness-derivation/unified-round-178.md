# Harness derivation — unified — round 178

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do this across my browser and Mac, but don’t commit anything until I physically approve it on the pendant; then prove the final result.”"
- **useful because:** This would turn the pendant’s approval latch from an isolated gesture into the system’s safest high-value action: stage a real multi-surface change, show exactly what will happen, require a nonce-bound physical approval, execute once, and verify the postcondition. Today a blocked plan can be spoken about and discarded, while browser/Mac execution and receipts are separate.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for planning and postcondition extraction; realtime only for the short approval/readback conversation
- **latency:** Stage preview in 2–5 s; physical approval response under 1 s when USB is attached; final receipt within 10 s or remain visibly pending
- **cost:** Roughly 1 planner call plus a cheap verifier call per transaction; dominant cost is the planner’s multi-surface context, not the receipt writes
- **security:** The relay must bind plan digest, world fingerprint, expiry, and physical transaction nonce; browser secrets/page contents must never be sent to the pendant; execution must be single-use and refuse if the world changed. Requires owner confirmation for off-machine, irreversible, or uncontained steps.
- **missing:** A production relay implementation of the existing approval handoff contract; A delivery path that stages approval on the pendant and returns its signed decision; A caller from orchestrator/bridge into prepare/approve; Postcondition schemas for browser and Mac actions; Close-ledger and job-lease fixes so a committed action is not mistaken for an interrupted one

### "“I was away or disconnected—tell me only what I missed, replay the important parts in order, and let me ask follow-up questions about the original evidence.”"
- **useful because:** A status page tells the owner that jobs exist; it does not restore the meaning of a missed interaction. This would build a bounded, spoken timeline from relay jobs, audio pipeline events, pendant inbox items, Mac receipts, and browser results, preserving source links and uncertainty instead of inventing a summary. It is especially valuable after the pendant is offline or the Mac bridge has slept.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → dashboard
- **model tier:** background for clustering and summarization; realtime for the owner’s follow-up questions against the retained evidence
- **latency:** First 3-item spoken digest within 3 s of reconnect; deeper evidence fetches within 8 s; no audio replay unless explicitly requested
- **cost:** One cheap summarization call per reconnect window, then small retrieval calls; storage and receipts dominate, not model inference
- **security:** Use a since/until window and source allowlist; redact page text and audio by default; retain opaque IDs and hashes rather than raw content where possible; the owner must explicitly request sensitive evidence playback. Never treat an unverified relay acceptance as proof the owner heard audio.
- **missing:** A durable cross-surface event join keyed by turn/job/artifact IDs; A compact spoken-digest queue with acknowledgement and deduplication; A query API that can fetch correlated browser results, Mac receipts, audio delivery acknowledgements, and pendant inbox records in one bounded window; Retention/deletion rules from the owner, which are still an open decision

### "“Continue the conversation we were having before the link dropped—don’t make me repeat myself, and tell me if you’re unsure what was actually heard.”"
- **useful because:** The current context resume is deliberately cold-start only, and audio delivery/relay acceptance are separate records. This capability would resume a live turn at a safe boundary using compact turn checkpoints, not retained room audio: recover the last owner utterance/transcript, assistant generation state, interruption point, and whether playback started or finished; ask one narrow clarification when evidence is incomplete.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** realtime for the resumed conversation; background for compact checkpoint compaction and stale-session cleanup
- **latency:** Reconnect classification under 500 ms; checkpoint retrieval under 2 s; no automatic speech until the pendant explicitly starts the resumed turn
- **cost:** Small retrieval plus one normal realtime turn; background compaction is inexpensive. The dominant cost is the resumed model context, bounded to the last few turns
- **security:** Never retain pre-press room audio; store transcript/checksum/turn metadata only under the owner’s retention policy. Bind checkpoints to a session and monotonic turn IDs, expire them, and refuse to resume across an ambiguous or privacy-latched boundary. Clearly distinguish “relay received,” “transcribed,” “played,” and “heard” (the last is never claimed without device evidence).
- **missing:** A durable turn-checkpoint record shared by relay and Mac; A reconnect-time session selector that handles simultaneous stale sessions; A compact transcript retention/deletion policy, which the owner has not specified; A pendant command to explicitly accept/resume a checkpoint at a turn boundary

### "“Fill in the sensitive parts of this form for me, but never show my passwords, recovery codes, or payment details to the model—and make me physically approve the final submission.”"
- **useful because:** Today the agent can drive browser actions, but a safe boundary for secrets is missing: either the model must see sensitive values or the owner must do the whole form manually. This capability would let the owner delegate tedious authenticated forms while keeping secrets inside a local vault/browser process and requiring the pendant for the irreversible submit.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** background for field classification and form planning; realtime only for clarification and the final approval conversation
- **latency:** Populate non-sensitive fields in 3–8 s; secret-field injection under 1 s locally; submission only after explicit physical approval
- **cost:** One planner call per form plus cheap local field matching; model cost is dominated by page interpretation, while vault/browser integration is the engineering cost
- **security:** The model and relay must receive field labels/types and opaque completion status, never secret values, DOM values, screenshots containing secrets, or clipboard contents. The browser extension should inject from an OS-secured vault directly into the bound tab, clear transient values where possible, bind approval to URL/origin/form digest/amount/recipient, expire it quickly, and refuse if the page changes. Payment, account recovery, deletion, and external-message submission require the physical latch; every receipt must say planned/injected/submitted, never claim success from a click alone.
- **missing:** A local secret-provider interface backed by the owner’s chosen macOS vault or browser password manager; A browser-extension primitive for origin-bound secret injection without returning values to the agent; A redacted form schema and digest that survives ordinary dynamic-page changes but detects security-relevant changes; A pendant approval payload that includes human-readable risk summary plus opaque form nonce; A post-submit verification path that can prove server acceptance without capturing sensitive response bodies


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: (1) a complete staged multi-surface transaction with pendant approval and postcondition proof, (2) a spoken missed-interaction digest reconstructed from bounded cross-surface evidence, and (3) safe conversation continuation after link loss with explicit uncertainty about what was heard. I also attempted a bridge hardware improvement; it was correctly rejected as a duplicate of the existing PSRAM/jitter-buffer bridge proposal rather than being restated. The most useful immediate build is the first capability, because the approval latch currently has no production loop around it.

**Biggest unknown:** The owner’s retention/deletion policy for transcripts, evidence, and reconnect checkpoints remains unspecified, as does the owner’s personal timezone distinct from the Mac’s America/New_York zone. The approval transaction also still needs the relay persistence/delivery implementation and a real postcondition join before it can be trusted.

