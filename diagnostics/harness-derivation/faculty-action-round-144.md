# Harness derivation — faculty-action — round 144

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do that.” After I have named an action, stage it, show me a short human summary on the pendant, let me approve with the safe physical gesture, execute it on the Mac or in the authenticated browser, independently verify the postcondition, and tell me whether it succeeded, failed, or is unknown."
- **useful because:** This is the central hand of the system: judgement can decide an action, but today execution, physical consent, and truthful verification are separate seams. It would let the owner use one natural confirmation without trusting an executor's optimistic receipt, including browser actions that no cloud model can reach.
- **path:** relay-realtime → unified → faculty-judgement → faculty-action → faculty-perception → mac-planner → mac-vision → browser-extension → mac-terminal
- **model tier:** Realtime only for the brief spoken summary and confirmation exchange; use the cheaper planner for decomposition and deterministic Mac/browser executors plus faculty-perception verification for the rest.
- **latency:** Stage summary under 2 s; physical approval feedback under 300 ms; execution can take up to 30 s, with a spoken progress update rather than holding the conversation open.
- **cost:** Usually one short realtime turn plus one cheap planning turn; roughly $0.01–$0.05 depending on the action. Mac/browser execution and verification dominate latency, not tokens.
- **security:** The relay must send the pendant only a redacted summary, risk class, expiry, and transaction digest—never credentials or page contents. Require the existing physical transaction latch for consequential actions; reject expired/replayed/mismatched approvals; verification must be read-only and return provenance. If verification is unavailable, report unknown and do not claim success.
- **missing:** A single orchestrator joining the existing physical_transaction_approval_latch, action ledger, executor receipts, and verify_operation_step into one transaction state machine; A narrow correlation field tying action/attempt IDs to verify_operation_step; USB-tether transport for the currently attached pendant, since LTE registration is absent

### "“I’m wearing it but LTE is unavailable—make the pendant work through the Mac that it is plugged into.” Keep button events, short voice notes, pending approvals, and spoken responses alive over USB, and automatically return to the relay path when a registered link appears."
- **useful because:** The hardware is physically present today even though the relay device table has no registered pendant. A USB-nearby mode makes the wearable useful now instead of treating it as absent, while preserving the same queues and approval semantics across transports.
- **path:** pendant → mac-planner → mac-terminal → relay-realtime → unified → faculty-action
- **model tier:** No model for transport and queueing. Use a cheap/background classifier only when a captured utterance needs intent extraction; reserve realtime for the resulting conversation.
- **latency:** Button and LED state under 100 ms locally; USB event delivery under 250 ms; audio response startup under 500 ms where the bridge is available. Link failover should not duplicate an event.
- **cost:** Negligible inference cost for transport. Hardware already attached; engineering cost is a USB serial service and protocol tests.
- **security:** Pair the serial identities and encrypt/authenticate the session; never treat arbitrary serial input as owner consent. Preserve monotonic event IDs, deduplicate on relay receipt, and keep action approval bound to the existing physical latch. Do not persist microphone audio except under the existing upload-failure rule.
- **missing:** A Mac USB serial companion that speaks the pendant and ESP32 bridge protocols; A transport-neutral relay session identity and replay-safe event envelope; A live device-registration/health route (the current /v1/devices/status is 404)

### "“Before I leave for my next meeting, get me ready.” Use my Mac calendar and authenticated browser sessions to assemble a private departure card—meeting time, location or join link, unresolved prep, and the exact next action—then read it through the pendant and let me approve only the prep actions I choose."
- **useful because:** It combines the wearable's interruptibility, the Mac's local calendar and apps, and browser sessions that the relay cannot access. The owner gets a timely, compact briefing and can safely trigger preparation without exposing calendar or private page data to the cloud.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action → unified
- **model tier:** Cheap scheduled/background planner gathers and compresses the card; realtime is used only when the owner asks follow-up questions or gives a final command. Deterministic connectors read Calendar and browser state.
- **latency:** Generate 5–10 minutes before the event in under 5 s; spoken delivery starts within 1 s after button press; selected prep action receipts within 30 s.
- **cost:** One low-cost scheduled planning call, typically <$0.01, plus optional realtime follow-up. Local Calendar/browser reads dominate neither API cost nor privacy exposure.
- **security:** Keep the card local to the Mac/pendant session; send only the minimum redacted speech content. Never scrape unrelated tabs. Each prep action gets its own digest, physical approval, expiry, and independent postcondition verification; ambiguous location or destructive prep must be staged, not executed.
- **missing:** A scheduler that correlates calendar events with browser/session evidence; A privacy-filtered cross-surface briefing projection (calendar + browser); Per-action approval fan-out and verification, rather than one blanket approval

### "“Freeze everything.” Immediately invalidate every pending approval and queued Mac/browser mutation, cancel cancellable jobs, stop new execution leases, and give me a compact list of what was stopped, what had already committed, and what remains unknown."
- **useful because:** Today an owner can cancel individual jobs only if they know which job to name. A wearable emergency stop would provide a single, dependable way to halt a mistaken chain or a compromised session across the relay, Mac, and browser.
- **path:** pendant → relay-realtime → unified → faculty-action → mac-planner → browser-extension → mac-terminal → faculty-perception
- **model tier:** No model is needed for the stop path; use deterministic revocation and cancellation. Use a cheap model only to summarize the resulting receipts after the stop is complete.
- **latency:** Local pendant acknowledgement under 200 ms; relay lease revocation under 1 s; cancellation fan-out under 3 s. The summary may follow asynchronously.
- **cost:** Near-zero inference cost for the emergency path; small background summarization cost only when there are many affected operations.
- **security:** This gesture must be fail-safe and authenticated, but must not be confused with ordinary approval. It should invalidate approval nonces monotonically, revoke browser command leases, and survive a relay/Mac reconnect. It cannot undo an already committed external action, so the owner must receive committed versus unknown status honestly.
- **missing:** A cross-surface execution lease registry with revocation broadcast; A pendant emergency gesture distinct from the existing approval gesture; Executor guarantees that queued work checks revocation before every mutating step

### "“Give me a private audit of everything you did for me this week.” Return a chronological, searchable account of spoken requests, approvals, Mac/browser mutations, verification evidence, reversals, and unresolved outcomes, with sensitive values redacted and a one-command revoke/delete control."
- **useful because:** The owner currently has scattered job receipts and logs, not an intelligible account of what the whole hive did. A weekly audit would make delegated agency inspectable, reveal silent failures, and let the owner remove sensitive history without losing harmless operational metadata.
- **path:** unified → relay-realtime → faculty-perception → faculty-action → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Use deterministic event joining and redaction first; use a cheaper background model to write the human summary. Realtime is only needed if the owner asks follow-up questions.
- **latency:** Generate on demand within 10 s for a week of activity; spoken answers to a specific audit question under 2 s.
- **cost:** Usually <$0.02 for summarization; storage/indexing and local redaction dominate implementation cost, not inference.
- **security:** Raw page contents, credentials, message bodies, and audio must not enter the audit by default. Store typed event metadata and hashes locally, encrypt the index, enforce retention periods, and make deletion verifiable. A redaction mistake is more dangerous than an omitted detail, so the system should label evidence classes explicitly.
- **missing:** A unified append-only event schema across relay, pendant, Mac, browser, approvals, and verification; Local encrypted audit index with field-level retention and deletion receipts; A dashboard or spoken query surface over the joined event stream


## Changes it proposed to its own stack

### `browser-harness` — Add a privacy-preserving browser transaction receipt at the browser bridge: for every mutating command, record the authenticated origin, tab/session id, normalized locator, pre-action field/value hash, post-action field/value hash, URL hash, and whether the tab remained the same; expose that receipt to faculty-perception for independent verification without returning page contents.
- **owner gets:** When the assistant changes something in a logged-in site, the owner can hear exactly which site and field changed and can distinguish “submitted,” “wrong tab,” and “unknown” without leaking the page to the relay or trusting a vague success message.
- effort: Medium: extend browser command/result schemas and local receipt persistence, then adapt verify_operation_step to consume the typed evidence. No new model is required.  ·  risk: A locator or hash could still reveal sensitive structure, and SPA navigation can make pre/post matching ambiguous. Default to hashes and redacted labels, expire receipts, and report unknown rather than guessing. Existing undo remains the recovery path where supported.
- cost: Negligible API cost and storage (hundreds of bytes per action); engineering and compatibility tests are the main cost.  ·  latency: Adds under 100 ms locally for hashing and receipt persistence; no extra model turn.
- security: Improves least-privilege and auditability, but must never persist raw passwords, tokens, full page text, or form values. Bind receipt to the browser session and command nonce to prevent replay or cross-tab confusion.
- depends on: A typed action/attempt correlation field shared with verify_operation_step; Existing authenticated browser bridge session and action ledger


## What it asked for

_Nothing._
