# Harness derivation — unified — round 48

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Don’t interrupt me unless it’s urgent; queue everything else and catch me when I’m free.”"
- **useful because:** Today each node can finish work, but the owner still gets badly timed spoken output. This gives one attention policy across the worn device, always-on relay, Mac, and authenticated browser: low-value receipts wait, urgent items escalate, and nothing is lost when the owner is in a conversation or meeting.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic state/risk rules and a cheap background model to classify urgency and summarize queued receipts; reserve realtime only for an urgent spoken escalation or the owner's live question.
- **latency:** State changes and queueing under 200 ms. Urgent escalation under 2 s after a verified trigger. Catch-up brief under 5 s when the owner asks or the pendant becomes idle.
- **cost:** Usually <$0.01 per queued item using background summarization; realtime cost only for a true escalation. Dominant cost is context if raw job logs are resent instead of compact receipts.
- **security:** Private browser-derived text must remain on the relay/Mac path and be redacted in dashboard notifications. Calendar/meeting state is sensitive and should be opt-in. Never infer urgency from message content alone for destructive actions; escalation may speak only a title/safe abstract until the owner asks for details.
- **missing:** A shared attention-policy state machine and event schema (pendant speaking/listening, Mac focus/meeting, browser-sensitive tab, owner availability, quiet hours).; A relay-side durable notification queue with urgency, expiry, deduplication, and receipt pointers rather than copied private payloads.; A pendant delivery mode that can acknowledge queued/urgent state with the single LED and button without interrupting audio; product hardware should add a discreet haptic motor for reliable urgent escalation.; Mac/browser adapters that publish focus and active-task state and consume the same queue.; An explicit owner policy UI and spoken commands: quiet, urgent-only, catch up, and forget.

### "“Before I share this, tell me what private or dangerous information is in it, make a safe redacted version, and let me approve it from the pendant.”"
- **useful because:** The owner can currently prepare browser transactions and review changes, but has no cross-surface data-loss guard that understands secrets and personal information before content leaves a private page. This would protect them when moving text from authenticated browser tabs into email, tickets, chat, documents, or external forms.
- **path:** browser → mac-vision → mac-planner → relay → pendant → dashboard
- **model tier:** Use deterministic detectors for credentials, payment data, personal identifiers, private URLs, and account-specific content; use a cheaper background model only to classify ambiguous prose and suggest redactions. Realtime is needed only when the owner is speaking through a live approval flow.
- **latency:** For ordinary text under 10,000 words: scan and produce a redaction diff in under 3 seconds. The browser must remain blocked at the final submit boundary until the owner approves or cancels. Pendant confirmation should complete within 2 seconds after the diff is ready.
- **cost:** Usually <$0.02 per scan; deterministic detection dominates little, while ambiguous-content classification and long-document summarization dominate API cost. Keep original content local to the Mac/browser whenever possible.
- **security:** The scanner itself handles highly sensitive data and must not send raw page text to third-party models by default. Store only hashes, detector categories, and the approved output. Require explicit confirmation for every external destination, show destination/domain and exact before/after diff, and fail closed if the scan or approval channel is unavailable.
- **missing:** A local Mac/browser redaction engine with detector plugins and confidence scores.; A destination-aware policy registry distinguishing private, trusted, and external origins.; A browser submit gate that can pause a final send/submit and expose an exact diff without duplicating credentials into relay logs.; A compact approval protocol from pendant to relay/Mac, including nonce, expiry, destination binding, and replay protection.; Dashboard UI for source, destination, detected categories, proposed redactions, and approval history.


## Changes it proposed to its own stack

### `interaction` — Add a relay-owned Attention Broker between jobs and all output surfaces. Every result becomes a compact receipt reference with urgency, expiry, sensitivity, required-attention class, and dedupe key. The broker consumes pendant audio/button state, Mac focus/meeting signals, browser sensitive-tab state, and explicit owner modes (normal, quiet, urgent-only, catch-up). It either delivers, queues, or escalates; queued items survive reconnects and are rendered identically in dashboard, menubar, and pendant catch-up. Keep payloads in their source store and pass opaque receipt IDs across surfaces.
- **owner gets:** The owner can wear the system all day without being talked over, losing a completion, or exposing private browser details in a notification. Saying “catch me up” gives one ordered, concise spoken queue regardless of which node did the work.
- effort: Medium-high: D1 schema and broker, event adapters in relay/Mac/browser, policy UI, reconnect tests, and pendant firmware acknowledgement states. Pilot with receipts and LED only before adding haptics.  ·  risk: Incorrect urgency could annoy or hide something important. Default to queue, never discard before expiry, show queue count on dashboard, and provide a physical-button catch-up/ack path. If broker is unavailable, preserve existing direct delivery and mark the receipt uncoordinated.
- cost: Negligible storage/index cost; background summarization <$0.01 per catch-up batch. No realtime call for queueing. A production haptic motor is roughly $1–3 BOM and tens of mW only during pulses.  ·  latency: Adds <200 ms routing for ordinary outputs; catch-up summarization adds 1–5 s depending on queue size.
- security: Improves privacy by keeping sensitive payloads behind source-side ACLs and sending only redacted titles/opaque IDs to notification surfaces. Requires careful policy that calendar and active-tab state are not logged broadly.
- depends on: Durable job receipts and undo records; Typed cross-surface context/attention event schema; Mac focus/meeting and browser-tab sensitivity adapters; Owner-configurable quiet-hours and urgency policy; Optional production pendant haptic actuator


## What it asked for

### `s8-4s4r` (skill) — attention_queue_indicator
- does: Offline-safe delivery indicator for the shared Attention Broker. It shows queued versus urgent receipts using LED patterns, records a short local acknowledgement/deferral gesture, and on reconnect sends only the queue event and opaque receipt IDs. It never stores private receipt text.
- must be on-device because: The owner needs a reliable indication and acknowledgement while the link or server is unavailable; LED/button timing must remain local and must not depend on a round trip or spoken interruption.
- trigger: Relay push when connected; local button gesture; link loss/reconnect event; and a server-scheduled queue refresh.
- storage: Small ring buffer of up to 32 opaque 64-bit receipt IDs plus urgency/expiry/ack flags and policy mode, under 1 KB in flash/NVS; erase IDs on acknowledgement or expiry.
- RAM budget: ~4–8 KB for ring buffer, event state, timers, and BLE/cellular message framing; comfortably below the 211,608 B application RAM budget, but audio buffers and Opus CPU remain the dominant constraints.

