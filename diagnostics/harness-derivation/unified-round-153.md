# Harness derivation — unified — round 153

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the pendant's marker button, save a private, searchable checkpoint of what I was looking at and doing: the bound browser tab, active Mac app/document, timestamp, and my spoken label—but never raw audio or page secrets. Later, when I ask “what did I mark?”, tell me the exact checkpoint and let me reopen it."
- **useful because:** The existing marker records that a moment happened, but not what the moment meant. This turns a physical tap into a reliable bridge between the worn device, the browser session, the Mac, and the relay without making the owner repeat context or store room audio.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** Deterministic capture and binding on pendant/Mac/browser; background model only when the owner later asks for a natural-language summary; realtime model only for the spoken label.
- **latency:** Marker acknowledgement under 300 ms locally; state capture and durable receipt under 2 s; later lookup under 2 s.
- **cost:** Near-zero model cost for capture; roughly $0.001–$0.01 only when summarization is requested, dominated by text extraction.
- **security:** Capture must be explicitly owner-triggered, bind only the focused tab/app, redact passwords/tokens and page bodies by default, and retain hashes/URLs plus an encrypted owner-approved excerpt. Reopening a tab should require the browser session binding and never transmit secrets to the relay.
- **missing:** A marker payload extension carrying task/session nonce, monotonic counter, and signed browser/Mac fingerprints; A browser inspection operation that returns metadata with secret redaction rather than full page content; A retention/deletion policy for checkpoint excerpts (owner context is still unknown)

### "Move my live conversation between the pendant-on-USB and the relay without losing my place: if LTE drops, continue through the Mac; if USB disappears, hand the next turn back to LTE, preserving turn IDs, unplayed audio, and the transcript exactly once."
- **useful because:** Today each transport can be alive while the conversation is effectively stranded at a boundary. Seamless migration would make the device dependable in a house, office, or walk outside: the owner does not repeat a request or hear duplicated speech after a link change.
- **path:** pendant → mac-planner → relay-realtime → browser-extension
- **model tier:** No model for transport negotiation or deduplication; realtime model only continues the conversation after a confirmed handoff, with the transcript and turn state supplied by the session store.
- **latency:** Detect failure in 2 s; announce a short handoff cue within 500 ms; resume capture/playback at the next turn boundary within 3 s.
- **cost:** No extra model cost for healthy handoffs; at most one additional short realtime turn after an ambiguous transport failure, dominated by duplicated-token prevention and audio retransmission.
- **security:** Each transport must prove possession of the same session nonce and monotonic sequence; buffer only encrypted, bounded transcript/audio; never fork two active speakers; require a local privacy latch to suppress migration while latched.
- **missing:** A relay session-migration protocol with per-direction sequence windows and an exactly-once turn commit; A Mac USB bridge adapter that speaks the accepted usb_fallback_audio_session framing; A durable bounded handoff buffer and explicit owner policy for what may be replayed after a disconnect; A bridge acknowledgement correlated with physical playback

### "Before you use my browser or Mac context to answer me, show me a compact privacy receipt: exactly which tab, app, fields, and files were consulted, what was redacted locally, and whether anything was sent to the relay. Let me say “don't use that source” and continue with the rest."
- **useful because:** The owner can wear a microphone while logged into sensitive sites. A source-level receipt makes cross-surface assistance understandable and lets him correct exposure immediately instead of trusting an invisible context pipeline.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** Deterministic source selection, redaction, hashing, and receipt generation; realtime model verbalizes the receipt only when needed, while background processing can maintain an audit index.
- **latency:** Local policy decision and redaction under 250 ms; spoken receipt under 1 s before an answer; dashboard audit query under 2 s.
- **cost:** No model cost for policy/receipt; under $0.001 per event for compact relay indexing, with model cost only if the owner requests a prose explanation.
- **security:** Default-deny for passwords, payment fields, private messages, and unbound tabs/apps. Send hashes and field classes rather than raw values; encrypt receipts; honor the privacy latch and make “don't use this source” an immediate session-scoped exclusion.
- **missing:** A shared source manifest and redaction engine used by both browser and Mac harnesses; A relay route for append-only, owner-readable provenance receipts with bounded retention; A pendant interaction for source exclusion during a spoken session; An owner retention/deletion policy (still unresolved)

### "Tell me whether this is still my pendant and my Mac before accepting a sensitive command. If the USB pendant identity, relay identity, browser session, or Mac bridge identity does not match the trusted pairing, quarantine the command, explain which link is untrusted, and let me re-establish trust with a deliberate physical ceremony."
- **useful because:** The owner should never have to guess whether a stale bridge, substituted USB device, or confused browser session can act as him. This gives a clear answer before a sensitive action and prevents split-brain sessions from producing duplicate audio or unauthorized commands.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic cryptographic attestation and policy; realtime model only explains the resulting trust state in natural language.
- **latency:** Healthy attestation under 300 ms; quarantine immediate; re-pairing under 30 s with physical confirmation.
- **cost:** Negligible model cost; small relay storage and cryptographic handshake overhead.
- **security:** Use device-bound keys and monotonic counters, never transmit private keys, and do not treat the shared AGENT_TOKEN as proof of device identity. Quarantine must fail closed and preserve only a redacted diagnostic receipt.
- **missing:** A real device identity/key attestation protocol spanning nRF9160, ESP32 bridge, Mac bridge, browser extension, and relay; Protected key storage or secure element on the physical devices; A pairing/revocation store and owner-visible trust dashboard; A recovery path when the owner has lost the trusted device


## Changes it proposed to its own stack

### `integration` — Complete the already-accepted physical_transaction_approval_latch path end to end: persist approvalHandoff records in the relay, deliver a pending approval only at the owner's next pendant conversation (never an unsolicited push), mark deliveredAt from the actual spoken readback, accept the signed nonce from the physical hold, and pass the unchanged plan/world digest to /approve. Also close ordinary orchestrator ledgers and add a relay job lease/requeue sweep so stale plans cannot be approved or replayed.
- **owner gets:** The owner can safely say “prepare this, but do not do it until I hold the pendant,” and the action will actually wait, be physically approved, execute once, or expire. Today the code says it is waiting for approval but no dashboard/relay path can complete that promise.
- effort: Medium-high: relay persistence and delivery, pendant event ingestion, approval route wiring, orchestrator close call, and lease tests across outage/reconnect cases.  ·  risk: A bug could execute a changed or duplicated action. Keep planDigest/world fingerprint/expiry/replay guard mandatory, reject stale or missing deliveredAt, and default to blocked on uncertainty. Recovery is refusal plus an owner-visible receipt; never auto-execute an ambiguous step.
- cost: No meaningful model cost; small D1/storage and relay traffic increase. Test and implementation time is the dominant cost.  ·  latency: Approval becomes available in the next natural conversation; once held, execution starts within one relay round (roughly sub-second to a few seconds depending on Mac).
- security: Improves least-privilege physical consent, but the current single AGENT_TOKEN still means approval and execution share authority; introduce a separate approval capability/token before treating it as a strong boundary.
- depends on: physical_transaction_approval_latch firmware delivery; relay implementation of shared/approvalHandoff APPROVAL_STORE_CONTRACT; a real pendant spoken-readback delivery receipt; orchestrator closeLedger call; relay_jobs lease_until and requeue sweep

### `interaction` — Add a spoken “source lock” interaction that is enforced before context retrieval: the owner can name a tab/app/file as excluded for the current turn or session, and the browser/Mac harnesses return a signed refusal receipt if a later plan attempts to read it. Show the compact source manifest before answers that use more than one surface.
- **owner gets:** He can use the system around private browser sessions without having to trust that an invisible planner will remember a verbal boundary. Saying “not that tab” becomes an enforceable control, not a conversational suggestion.
- effort: Medium: shared policy state, browser and Mac preflight hooks, pendant phrasing, and receipts; no new model capability required.  ·  risk: Overblocking could make answers incomplete, while underbinding could leak a source. Default to exclusion on ambiguity, scope locks to session/turn with explicit expiry, and report missing evidence rather than silently substituting another source.
- cost: Negligible model cost; bounded relay state and receipt writes.  ·  latency: Adds under 100 ms for policy checks and possibly one short spoken confirmation.
- security: Reduces accidental disclosure; source URLs/app names may themselves be sensitive, so receipts should hash or classify them unless the owner requests details.
- depends on: shared source manifest/redaction engine; browser inspection metadata with tab/session binding; Mac action preflight hook; owner retention/deletion policy

### `integration` — Add a cross-surface causal-consistency gate before reporting any completed action: assign one transaction ID at the relay, require the Mac/browser executor receipt, and independently reconcile the resulting external state through a bound read-only observation. If the receipt and observed state disagree, mark the transaction ambiguous and stop follow-up actions rather than claiming success.
- **owner gets:** The owner gets an honest answer to “did it actually happen?” instead of a Mac success message that may have been swallowed by a browser, network, or external service. Ambiguity becomes visible and recoverable before a second action compounds it.
- effort: High: transaction propagation through relay, Mac, browser, and observation routes; external-state adapters; timeout and ambiguity UX.  ·  risk: Some services expose delayed or incomplete state, causing false ambiguity. Use service-specific settling windows, retain raw evidence only under the owner’s retention policy, and never auto-retry non-idempotent actions after ambiguity.
- cost: Low model cost; extra read-only observation calls and receipt storage dominate.  ·  latency: Adds a settling delay from hundreds of milliseconds to several seconds for actions requiring external verification.
- security: Observation must be least-privilege and bound to the exact tab/app/resource; redact secrets and avoid treating a screenshot or page text as proof without origin/session binding.
- depends on: A shared transaction ID across /execute, browser commands, and relay jobs; Read-only bound observation adapters; A typed ambiguity state in job receipts; Owner retention/deletion policy


## What it asked for

_Nothing._
