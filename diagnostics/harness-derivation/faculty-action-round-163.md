# Harness derivation — faculty-action — round 163

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Even if the pendant has no LTE, let me say ‘lock my Mac and put it in Do Not Disturb’ into the pendant and have it execute locally over USB; tell me when it is done.”"
- **useful because:** The pendant and ESP32 are physically on USB today while LTE registration is absent. This gives the owner a reliable local emergency/control path instead of making the wearable useless whenever cellular is unavailable.
- **path:** pendant → relay → mac-bridge → mac-planner → mac-terminal → unified
- **model tier:** Use realtime only to decode the short command; deterministic local policy and Mac agent execute it without a cloud round trip.
- **latency:** Button/audio handoff under 1 s; local command completion and spoken confirmation under 5 s.
- **cost:** Near-zero API cost when tethered; dominant cost is one short realtime turn only if speech understanding is needed.
- **security:** USB session must mutually bind to the paired Mac and reject arbitrary serial hosts. Only allowlisted reversible/local actions by default; sensitive or irreversible actions still require the existing physical approval latch. Never send raw local audio or secrets to the relay when the Mac can interpret it locally.
- **missing:** USB serial transport and pairing protocol between nRF9160 pendant and Mac bridge; local offline intent parser/policy path with explicit allowlist; pendant-visible completion/error protocol and receipt persistence

### "“Undo the last thing you did for me.”"
- **useful because:** The owner can recover from a mistaken action without remembering which app or browser was involved. The system resolves the most recent committed transaction, selects a safe inverse, executes it on the correct surface, and reports ‘undone’, ‘partly undone’, or ‘cannot undo’ rather than silently guessing.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → browser → unified → faculty-perception
- **model tier:** Cheap/background model resolves the ledger and inverse templates; realtime is used only for the short spoken clarification or result.
- **latency:** Identify candidate in under 1 s; reversible undo under 5 s; ask a clarification rather than guessing when multiple candidates exist.
- **cost:** Usually one small planner call; Mac/browser execution dominates, not tokens.
- **security:** Never infer an inverse for money movement, deletion, publication, or message send without explicit confirmation. Require transaction ID or a spoken disambiguation when confidence is low. Verify the inverse postcondition independently and retain both original and undo receipts.
- **missing:** canonical inverse-operation registry for action types; ledger query for the owner’s latest committed action scoped to session and device; rollback executor that can atomically stop before partially reversible steps

### "“When I approve an action on the pendant, show me exactly what happened—even if the browser or Mac goes offline—and read me the final status when the link returns.”"
- **useful because:** Physical approval currently protects consent, but a link drop can leave the owner unsure whether the action ran. This capability gives a durable, truthful outcome across pendant, relay, Mac, and browser: committed, failed-before-run, partially completed, or unknown, with a concise spoken summary and a later retry/inspection path.
- **path:** pendant → relay → mac-bridge → mac-planner → browser-extension → faculty-action → faculty-perception → unified
- **model tier:** Deterministic state machine and receipts handle delivery/replay; use a cheap model to compress verified evidence into speech, reserving realtime for the live conversation.
- **latency:** Immediate pending acknowledgment under 500 ms; final receipt when available; reconnect replay under 2 s.
- **cost:** No model call for state transitions; one inexpensive summarization call only for a complex receipt.
- **security:** Bind approval, executor attempt, browser command, and verification to one nonce and monotonic sequence. Do not claim success from executor acknowledgment alone; verification evidence must come from fresh Mac/browser state. Keep sensitive snippets hash-only by default and expire pending secrets.
- **missing:** durable cross-node transaction state machine with replay cursor; Mac/browser reconnect acknowledgments and idempotent command replay; pendant status patterns/audio cues for pending, verified, unknown, and failed

### "“Emergency privacy.”"
- **useful because:** A single deliberate gesture on the worn device would immediately lock the Mac, mute its playback, cancel uncommitted approvals, and stop pending browser commands. The owner gets a physical panic cord for the entire personal-AI system, even when speech, display, or network is unavailable.
- **path:** pendant → mac-bridge → mac-planner → browser-extension → relay → unified
- **model tier:** No model call: a device-local signed emergency command and deterministic Mac/relay handlers.
- **latency:** Lock and cancellation signal within 1 second over USB or the next available link; relay-side revocation occurs asynchronously.
- **cost:** No per-use API cost; engineering is dominated by reliable process cancellation and session revocation.
- **security:** The gesture must be hard to trigger accidentally but must not require cloud reachability. Use a device-held key and monotonic nonce; never transmit captured audio or page contents. Recovery requires a separate deliberate unlock gesture and should not silently resume cancelled work.
- **missing:** device-local emergency command firmware; Mac bridge emergency endpoint that kills or suspends action process groups; relay-wide revocation fanout for pending transactions and browser commands; explicit recovery/unlock ceremony

### "“Give me a private work window for the next hour.”"
- **useful because:** The owner could delegate a bounded, inspectable period in which the system performs only pre-approved routine work—sorting a defined inbox, preparing drafts, or updating a task list—then automatically stops and presents a digest. This turns the hive into useful background labor without granting open-ended autonomy.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal → faculty-judgement → faculty-action → faculty-perception
- **model tier:** A cheaper background model schedules and classifies routine items; realtime is used only to establish or end the window. Sensitive sends remain staged for physical approval.
- **latency:** Window activation under 2 seconds; individual routine items may run asynchronously; digest on expiry or immediately on request.
- **cost:** Background model cost scales with item count; use batching and deterministic filters to keep it low. Mac/browser execution dominates wall time.
- **security:** The window must carry an explicit expiry, scope, risk ceiling, and destination allowlist. No sending, deleting, purchasing, or external publication without renewed approval. Store only hashes and summaries in relay records where possible.
- **missing:** time-bounded delegation token understood by every node; policy evaluator that enforces scope and risk ceiling per action; automatic expiry/revocation across queued Mac and browser work; owner-visible digest of attempted, completed, and blocked items

### "“Make this decision auditable.”"
- **useful because:** For a consequential action, the system would preserve a compact evidence packet: what the owner asked, which policy allowed it, what changed on the Mac/browser, and what independent perception observed afterward. The owner could later ask for a human-readable audit trail without exposing page secrets to the pendant.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-action → faculty-perception → unified
- **model tier:** Deterministic event and hash recording first; a cheap model renders the packet into plain language only when requested.
- **latency:** No noticeable delay for normal actions if evidence is recorded asynchronously; audit rendering under 3 seconds.
- **cost:** Low storage and occasional summarization cost; evidence capture is the dominant implementation work.
- **security:** Default to hashes, typed metadata, and minimal snippets. Encrypt sensitive evidence at rest, enforce retention limits, and require explicit confirmation before revealing private content. Audit records must be append-only so they cannot falsely certify a failed action.
- **missing:** canonical cross-node event schema with provenance and retention policy; append-only encrypted audit store; redaction layer shared by Mac, browser, relay, and perception; owner-facing audit query and export


## Changes it proposed to its own stack

### `firmware` — Add a USB-tethered control transport to the nRF9160 firmware: a framed, authenticated CBOR channel over its existing USB serial connection, with monotonic request IDs, explicit local-only mode when LTE is unregistered, bounded request/receipt queues, and a fail-closed allowlist. The Mac bridge becomes the executor only; the pendant never receives page contents or credentials. Include button/audio status signaling and crash-safe replay of receipts.
- **owner gets:** The connected pendant should remain a useful physical control and confirmation device today, even with no LTE registration. The owner gets dependable local commands and knows whether they completed instead of hearing silence.
- effort: Firmware transport, Mac bridge pairing, and integration tests; moderate-to-high (several days) because framing, replay, and fail-closed behavior must be tested across disconnects.  ·  risk: A malformed or replayed USB frame could trigger an action; mitigate with pairing keys, counters, allowlists, and requiring the existing physical approval latch for risky actions. Recover by dropping the USB session and replaying only idempotent requests.
- cost: No per-invocation API cost; roughly 1–3 KB firmware flash and a small RAM queue. No added hardware or meaningful power draw while USB-connected.  ·  latency: Local control should be materially faster than LTE, typically sub-second command handoff.
- security: Expands the attack surface to the USB host, so authenticate the Mac bridge and make local-only mode explicit; never upload command audio or sensitive state by default.
- depends on: USB serial pairing key provisioning; Mac bridge support for framed CBOR requests and receipts; owner approval of the local allowlist and risky-action behavior


## What it asked for

_Nothing._
