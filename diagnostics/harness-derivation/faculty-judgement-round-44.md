# Harness derivation — faculty-judgement — round 44

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Queue anything that needs my approval, and let me safely approve it from the pendant when I have a moment.”"
- **useful because:** Today a useful browser or Mac task stops when confirmation is needed, and the owner must return to the exact screen. This creates a time-bounded approval inbox: the relay keeps the prepared transaction, the Mac/browser preserve evidence and session affinity, and the pendant offers a one-sentence explanation plus approve/edit/reject. Approval is not blind: immediately before execution the Mac/browser re-check the page, recipient, amount, and permissions; if anything changed, it asks again. It turns interruptions into resumable decisions without allowing stale or surprising actions.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → mac-terminal → faculty-perception → faculty-judgement → faculty-action → unified
- **model tier:** Background/cheap model prepares and summarizes packets; realtime is used only when the owner asks a question or speaks an approval. Deterministic validators and the action tier enforce field-level safety; no model is trusted to infer that a changed transaction is equivalent.
- **latency:** Packet creation can take seconds in the background. Pendant inbox should render in under 500 ms from cached relay state; spoken clarification under 1.5 s. Revalidation may take up to 5 s, with a clear 'still checking' state.
- **cost:** Roughly $0.01–$0.08 per packet depending on cross-site extraction and summarization; most cost is background page reading, not the approval utterance. Storage/queue traffic is negligible.
- **security:** Never transmit page secrets or full account contents to the pendant; send only a redacted summary and hashes/evidence references. Approval tokens are single-use, scoped to exact fields, expire (for example, 30 minutes), and bind to owner/session/device. Sending mail, purchases, deletion, or external submission always requires explicit confirmation. If a page, recipient, amount, or authorization changed, invalidate the token. Need durable queue state, encrypted evidence references, push to pendant, typed diff/revalidation, cancellation, and an audit receipt.
- **missing:** durable approval-packet store with expiry and single-use tokens; pendant inbox/approve-edit-reject interaction and push protocol; browser/Mac field-level before/after diff plus revalidation endpoint; cross-surface cancellation and receipt linkage; redaction policy for summaries and evidence

### "“I’m around people—keep helping, but don’t reveal anything aloud or on a screen someone can see.”"
- **useful because:** The owner should not have to choose between privacy and assistance whenever they enter a meeting, shop, or transit. A spoken 'around people' mode would make the whole hive privacy-aware: the pendant stops speaking sensitive text, the relay classifies and redacts queued results, the Mac avoids displaying private summaries in prominent windows, and browser work continues but returns only minimal status cues. The owner can still ask for a discreet answer through a short button/voice interaction, and queued details become available automatically when private mode ends. This is a coordinated behavior change across all surfaces, not a mute switch on one device.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action → unified
- **model tier:** Use deterministic sensitivity labels and policy rules for immediate redaction and routing; use a cheap background model only to summarize non-sensitive status. Realtime is reserved for the owner's short private query. No model should decide that secret content is safe solely from semantics without a policy label or explicit owner override.
- **latency:** Mode changes and output suppression must take effect within 200 ms locally on the pendant and within 1 second at relay/Mac. Status-only responses should be under 1 second; deferred summaries can wait until privacy mode ends.
- **cost:** Negligible per mode switch; approximately $0.005–$0.03 for optional background classification of an unlabelled result. The dominant cost is implementation and testing of redaction/policy enforcement, not inference.
- **security:** Default to withholding when sensitivity is unknown. Do not send sensitive text to the pendant while private mode is active; use opaque notification codes or haptics. Browser screenshots and Mac window content need separate redaction paths. Mode state must be authenticated to the owner's device, logged, and expire or require explicit exit so a forgotten mode cannot hide urgent information indefinitely. Emergency alerts need a configurable, minimal cue rather than spoken detail.
- **missing:** cross-surface sensitivity labels and a fail-closed redaction policy; authenticated privacy-mode state propagated to relay, Mac, browser, and pendant; pendant haptic/status-only output and local suppression that works offline; Mac/browser display and speech interception hooks; owner-configurable emergency cue and automatic expiry rules


## Changes it proposed to its own stack

### `interaction` — Add a single 'decision packet' protocol shared by relay, Mac, browser bridge, and pendant. A packet contains intent, exact proposed mutations, redacted human summary, evidence references, risk class, expiry, required confirmation strength, and a content hash. The pendant can approve/reject/edit a constrained field; the action tier must revalidate the hash and live page state, consume the token once, and emit a receipt or invalidation reason. Treat approval as a capability scoped to this packet—not as a general session permission.
- **owner gets:** The owner can deal with important decisions while walking or away from the Mac without losing the work already done, while stale or changed transactions fail safely instead of silently going through.
- effort: Medium-high: shared schema and durable store, relay push/ack, browser and Mac adapters, pendant UI/audio affordances, validators, expiry tests, and crash/retry/idempotency tests.  ·  risk: A bug could approve the wrong field or replay an approval. Recover with cryptographic packet hashes, single-use server-side consumption, strict allowlists, visible spoken readback, automatic expiry, and a complete receipt. If any adapter is unavailable, leave the packet pending rather than executing.
- cost: Small storage and queue cost; one cheap background summarization call per packet and occasional realtime clarification. No significant pendant power cost beyond brief push/listen activity.  ·  latency: Cached inbox is subsecond; revalidation adds roughly 1–5 seconds before execution. This is preferable to forcing the owner back to a desktop.
- security: Improves least privilege by replacing broad 'logged-in session' authority with an exact, expiring, auditable capability. Requires encrypted packet/evidence storage and redaction so sensitive page content never rides to the pendant.
- depends on: durable cross-surface job/event persistence; pendant push and local approve/reject input; browser command queue with tab/session affinity; typed before/after evidence and live revalidation; receipt/undo and cancellation primitives

### `hardware` — Add a physically latched privacy control to the pendant: a two-position slider that electrically gates the microphone and drives a visible/tactile local state, plus a separate 'social/private' input that keeps the mic available but forces all output to haptic/status-only. Firmware must expose both states to the relay and refuse to claim the microphone is private unless the hardware gate is actually closed.
- **owner gets:** The owner gets a trustworthy way to prevent accidental listening or public playback, independent of cloud connectivity, model behavior, or a frozen app. They can remain assisted in public without exposing a private email, calendar item, or browser page.
- effort: Medium hardware spin and firmware work: add a latching switch and input/gate path, update enclosure/PCB, implement state reporting and boot/reconnect tests, and add relay/Mac/browser policy handling for the soft mode.  ·  risk: A misleading indicator or switch bounce could create false confidence. Use fail-closed electrical gating, a distinct tactile detent, an always-visible local indicator, debounce/self-test, and make the relay treat unknown state as private. The social mode must not be confused with physical mic-off.
- cost: Roughly $1–$4 in components and PCB/enclosure changes at prototype volume; near-zero steady-state power for the mechanical gate and a few mW for an indicator when active. No per-use model cost.  ·  latency: Physical mic gating is immediate; soft privacy propagation should be under one second when connected and remain effective locally while disconnected.
- security: Strongly improves microphone consent and prevents sensitive audio from leaving the device. The hardware state should be signed/attested in status messages, with no raw audio retained during either privacy mode.
- depends on: pendant firmware state/event channel; relay policy propagation and authenticated device state; Mac/browser output interception and redaction; owner-configurable emergency cue policy


## What it asked for

### `s5-fiiv` (skill) — decision_packet_inbox
- does: Maintains a small, redacted queue of pending approval packets received from the relay; announces only packets that are not expired, lets the owner cycle items and approve/reject with the physical button or voice wake, gives a short local readback of the exact action, and sends a signed one-use response when connectivity returns. It never executes an external action locally.
- must be on-device because: The owner needs to inspect or reject a pending action during a dropped link, and a physical control must remain available even when speech/network is unavailable. The server still owns validation, expiry, and execution; the pendant supplies durable local intent and an unmistakable human gesture.
- trigger: Server push when connected; physical button long-press to open/abort; wake-word/voice command; reconnect event to flush queued responses.
- storage: Encrypted append-only queue in pendant flash, capped at 16 packets × roughly 1 KB metadata/readback each (<20 KB), with consumed/expired tombstones pruned after acknowledgement.
- RAM budget: About 8–12 KB working memory: one decoded packet, queue index, audio/UI state, and signing/transport buffers. Keep evidence and model work off-device; this is comfortably below the 211,608 B application RAM budget.

## Its own summary

Round 44 produced a genuinely new cross-surface capability: an expiring, redacted decision-packet inbox. Mac/browser prepare exact mutations and evidence; relay persists and pushes a packet; the pendant can read back and approve/reject while away; action revalidates live state and consumes a single-use token before execution. I recorded the shared packet protocol change and queued a pendant-local decision_packet_inbox skill (small encrypted offline queue, physical abort/approval, no local execution). I still need the orchestrator to provide durable cross-surface event/job persistence, pendant push and button-response plumbing, browser/Mac field-level revalidation, and the current audio acceptance criteria so this can be implemented rather than merely specified. I also need explicit owner interruption/notification preferences and a security/redaction policy; those were previously requested but remain unavailable.

**Biggest unknown:** Whether the existing receipt/cancel infrastructure can support a cryptographically scoped, expiring approval token with live field-level revalidation, or whether that persistence and protocol must be built from scratch.

