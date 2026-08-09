# Harness derivation — faculty-action — round 224

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the pendant's bookmark button, save a private 'moment capsule' containing what I was hearing plus the Mac/browser context I was looking at, so I can ask later, “what was that thing I marked?”"
- **useful because:** The owner gets a reliable bridge between an ephemeral spoken moment and the exact document, app, or web page in front of them; it turns the existing bookmark into a retrievable memory rather than an unexplained timestamp.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Realtime only for the immediate acknowledgment and compact spoken label; background model for indexing, deduplication, and later retrieval.
- **latency:** Acknowledge the press in under 300 ms; capture host/browser context within 2 s; later retrieval under 5 s.
- **cost:** Low per bookmark (one small event plus optional audio already produced); background indexing dominates, not realtime inference.
- **security:** Capsule may contain private page titles, URLs, app names, and audio. Keep raw audio on the existing failure-path/outbox policy, encrypt identifiers, redact secrets/form fields, and require the owner's normal approval before sharing or sending a capsule anywhere.
- **missing:** A correlation envelope joining the pendant bookmark ID, audio artifact ID, Mac observe snapshot, and browser session snapshot.; A read-only Mac/browser snapshot operation that returns title/app/URL and provenance without page contents or credentials.; A retrieval index that can search these capsules by time, spoken label, app, or URL.

### "If a Mac or browser action ends up uncertain, tell me exactly what is known, what was not verified, and give me one safe next move I can approve from the pendant—retry, inspect, undo, or leave it alone."
- **useful because:** Unknown outcomes are the most dangerous failure mode: the owner should not duplicate a purchase, message, or file operation merely because the link dropped. This turns truthful uncertainty into a recoverable decision instead of a dead-end notification.
- **path:** relay → mac-planner → browser-extension → faculty-perception → faculty-action → pendant
- **model tier:** Cheap background model classifies receipts and proposes bounded recovery; realtime model only speaks the concise state and handles the owner's choice.
- **latency:** Surface an unknown state within 2 s of a receipt timeout; each read-only inspection under 3 s; never auto-retry a side effect.
- **cost:** Low-to-moderate; mostly receipt retrieval and one compact model call, with no expensive vision unless the owner selects inspect.
- **security:** Never expose page secrets or message bodies to the pendant. Recovery choices must carry the original operation digest, expiry, and risk class; retry/undo require the existing physical approval latch where applicable. An unknown state must remain unknown until an independent verifier returns evidence.
- **missing:** A recovery-decision protocol that binds retry/inspect/undo/leave-alone to operation ID, attempt ID, expiry, and digest.; A verifier-backed recovery planner that can distinguish reversible from irreversible operations and suppress unsafe retry.; A pendant interaction mapping for selecting among four bounded choices without overloading sw0's active-edge recording behavior (use the forthcoming wheel/second button).

### "When I mark a moment during a call or while reading, quietly make a follow-up card that includes the timestamp, the active app or browser page, and a short reason I spoke; later, show me only the cards that still need a decision or action."
- **useful because:** This is a daily memory-to-action bridge: a two-button pendant gesture captures fleeting intent, while the Mac contributes context and the relay turns it into a small queue of actionable follow-ups instead of an unsearchable pile of recordings.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-judgement → faculty-action
- **model tier:** Realtime model makes the immediate acknowledgment; a cheaper background model extracts a one-line reason, groups duplicates, and ranks cards by unresolved status.
- **latency:** Capture and acknowledge in under 500 ms; card draft within 10 s; daily queue generation under 30 s.
- **cost:** Low: one event and compact transcript per mark; background summarization is the dominant cost.
- **security:** Cards are private by default and may include sensitive conversation context. Store only a short extract plus pointers to raw audio, apply retention/expiry, never send or edit external systems without physical approval, and keep browser contents out of model prompts unless explicitly selected.
- **missing:** A typed follow-up-card schema with source pointers, owner confidence, due/expiry, and unresolved/resolved state.; A local context joiner for bookmark events and Mac/browser snapshots that avoids collecting full page contents.; A review surface that lets the owner resolve, snooze, or route one card through the existing approval and action ledger.

### "Give me a private, human-readable receipt for any important action that I can keep or show later: what I asked, which account or app was used, exactly what changed, when it happened, and independent evidence that the final state was checked."
- **useful because:** Today an action may leave scattered logs and a vague success signal. A portable receipt would let the owner audit a sent message, file change, booking, or browser transaction weeks later without trusting memory or reconstructing the workflow.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Background model formats and redacts the receipt; realtime model only offers a short spoken confirmation or retrieves an existing receipt.
- **latency:** Create a compact receipt within 5 seconds after verified completion; retrieval under 3 seconds; export can be asynchronous.
- **cost:** Low per action: hashes, metadata, and a short generated explanation. Storage and optional redaction inference dominate, not realtime tokens.
- **security:** Receipts can expose account names, recipients, URLs, filenames, or sensitive outcomes. Encrypt at rest, classify sensitivity, omit secrets and page bodies by default, require physical approval before export or sharing, and preserve immutable evidence hashes so a later redaction cannot rewrite history.
- **missing:** A canonical portable receipt schema containing intent, risk class, executor, account/session identifier, action and attempt IDs, before/after evidence references, verifier provenance, timestamp semantics, and redaction policy.; A durable owner-controlled receipt vault with retention, search, export, and revocation; it must distinguish an executor claim from independently verified postconditions.; A Mac/browser adapter that emits stable evidence references without leaking credentials or full private page contents.; A pendant command and haptic cue for saving, retrieving, or exporting one receipt without speaking private details aloud in public.

### "When I say I am in public, keep the system useful without speaking private content aloud: summarize incoming results as haptic patterns, show details only on my Mac, and automatically defer anything that would reveal a message, page, or account name until I explicitly unlock private mode."
- **useful because:** A wearable assistant is otherwise unsafe to use around other people. This would let the owner continue receiving action outcomes and reminders discreetly instead of choosing between silence and exposing private information.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-action
- **model tier:** Realtime classification only for the mode switch and urgent alerts; a cheap policy layer enforces output redaction and routes detail to the Mac without sending private text to the pendant.
- **latency:** Mode change acknowledged within 300 ms; all subsequent output policy decisions under 100 ms; deferred detail available on the Mac within 2 seconds.
- **cost:** Very low: mostly deterministic policy checks and compact haptic events; no extra model call for ordinary notifications.
- **security:** The public/private state itself is sensitive. Default to the safer silent mode after reboot or uncertain link state, never transmit message bodies or secrets to the pendant for a haptic-only result, and require a deliberate physical gesture or local Mac action to return to private speech.
- **missing:** A first-class privacy-output policy shared by relay, Mac, browser, and pendant, with explicit silent/haptic/detail channels.; A reliable private-mode state with expiry, crash-safe persistence, and a safe default when the link drops.; A haptic vocabulary that distinguishes success, warning, pending, and blocked-private-detail without revealing the underlying content.; Mac/browser UI affordances that hold the redacted detail until the owner deliberately opens it.

### "If I make the pendant's privacy-panic gesture, immediately stop pending actions, mute spoken output, lock or close sensitive browser sessions, and leave me a private recovery record of what was cancelled—without deleting data or pretending already-completed actions were undone."
- **useful because:** A lost pendant, overheard conversation, or sudden change of surroundings needs one fast, understandable safety response across every surface. Today no single physical gesture can contain the relay, Mac, and browser at once.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-action → faculty-perception
- **model tier:** Firmware handles the local gesture and silence immediately; relay policy fans out bounded cancellation commands; background processing builds the recovery record. No realtime reasoning is needed for the emergency path.
- **latency:** Pendant audio suppression and local pending-state freeze under 200 ms; relay fan-out starts under 1 second; Mac/browser acknowledgments within 5 seconds, with unknown explicitly reported.
- **cost:** Low per invocation; a few authenticated control messages and a compact event record. Browser/session teardown and acknowledgement polling dominate latency.
- **security:** This is deliberately high impact and must be owner-configurable. It must be authenticated, replay-resistant, rate-limited, and idempotent; it may cancel or lock but must never delete files, send messages, or claim an external action was reversed. If the link is down, the pendant must still silence itself and queue the panic event.
- **missing:** A cross-surface panic transaction with a monotonic nonce, expiry, idempotent cancellation semantics, and per-surface acknowledgments.; Relay and Mac/browser handlers that can revoke pending commands and close or lock sensitive sessions without requiring page contents.; A dedicated pendant gesture using the future second button/wheel, distinct from ordinary approval and bookmark gestures.; A recovery report that separates cancelled, completed-before-panic, and unknown operations.


## Changes it proposed to its own stack

### `firmware` — Add a silent end-to-end audio health sentinel spanning nRF9160, ESP32 bridge, and relay: on an explicit diagnostic request (never during normal conversation), the pendant emits a short tagged silence/known fixture, the bridge returns measured packet/decode/playback counters, and the relay stores a timestamped result with link and firmware identifiers. The test must not open the microphone or make audible output unless the owner chooses a sweep.
- **owner gets:** When speech suddenly disappears, the system can distinguish a dead radio, stalled Opus decoder, bridge/I2S fault, or speaker path problem instead of making the owner guess or repeatedly press the button.
- effort: Medium: firmware diagnostic framing and counters, ESP32 response path, relay receipt schema, and a small Mac-triggered diagnostic UI/voice command. Build against the already shipped 24 kHz acceptance numbers.  ·  risk: A diagnostic packet could be mistaken for conversation audio or consume CPU during a call. Gate it behind an explicit request, a nonce, and an idle check; discard stale results and report unknown rather than claiming healthy playback. Recovery is simply rerun after the link is idle.
- cost: Negligible API cost; modest firmware work. No new hardware or meaningful power draw outside an explicit test.  ·  latency: Normal path unchanged. An explicit health check completes in roughly 1–3 seconds.
- security: No microphone recording or content upload; use fixture IDs and counters only. Authenticate requests and bind results to the requested device/session.
- depends on: A relay/device diagnostic request and receipt route; ESP32 bridge firmware support for tagged diagnostic frames; A read-only Mac/relay presentation of the health receipt


## What it asked for

_Nothing._
## Its own summary

This round recorded three cross-surface owner capabilities and one firmware change. The most important is verifier-backed recovery for uncertain Mac/browser actions: no blind retries, exact known/unknown state, and one bounded choice from the pendant. Also recorded bookmark context capsules, follow-up cards, and an explicit silent audio-path diagnostic sentinel.

**Biggest unknown:** The main missing seam is not another executor: it is a shared correlation and recovery protocol. Bookmark/audio IDs, Mac/browser snapshots, operation IDs, attempt IDs, digests, expiry, and verifier provenance still need one durable schema and an owner-facing review/selection surface. The next physical input (wheel/second button) is also needed for safe multi-choice recovery; sw0 must remain active-edge recording.

