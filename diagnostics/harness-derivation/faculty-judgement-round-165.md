# Harness derivation — faculty-judgement — round 165

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I’m wearing the pendant next to my Mac, make it a local-first voice companion automatically: continue the conversation and play replies over USB even when LTE is unregistered, then reconcile the session and delivery receipts when the relay returns. Tell me explicitly when you switched between local and cloud, without making me reconnect anything."
- **useful because:** The hardware is physically present and testable now, while LTE registration is not. This gives the owner reliable everyday use at the desk and honest continuity instead of a dead pendant or duplicated replies after reconnect.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** Realtime for the live turn only; a cheap background reconciler for reconnect, duplicate suppression, and delivery receipts.
- **latency:** Button-to-first-audio under 700 ms over USB; cloud fallback may be slower but must announce the mode change in one short sentence.
- **cost:** Negligible incremental model cost for local turns; reconnect reconciliation is sub-cent and dominated by relay requests. USB serial framing/authentication and a small local audio/session broker are the engineering cost.
- **security:** The Mac must authenticate the pendant session locally and bind artifacts to one device session; never expose raw PCM or secrets to the relay merely because USB is present. Replayed delivery ACKs must be deduplicated, and a mode change must not cause a second spoken response.
- **missing:** A USB-serial local voice/session broker connecting the live Mac bridge to pendant firmware; A durable local-vs-cloud session identity and artifact handoff protocol; A relay endpoint that accepts offline-replayed session and audio-delivery events and joins them to the originating job; A fail-closed mode indicator spoken/displayed to the owner

### "Before you tell me my day is clear, give me a one-sentence trust verdict: what you actually checked, what was unreadable or stale, and which facts are safe to act on. If a permission or surface is missing, offer the next reachable source instead of silently treating it as empty."
- **useful because:** Today an unauthorised EventKit read can look identical to an empty calendar, and several briefing routes can confidently say nothing is waiting. The owner needs a dependable answer more than a polished false calm.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** A deterministic policy/evidence pass first; use the expensive realtime model only to compress the already-typed verdict into one spoken sentence.
- **latency:** Under 2 seconds for routine checks; no more than one short spoken sentence unless the owner asks for evidence.
- **cost:** Usually no model call; one cheap provenance/evidence summarization call only when sources conflict. Cost is dominated by permission and freshness probes, not generation.
- **security:** Do not speak calendar subjects, mail bodies, or private snippets in a public setting. Return source IDs and freshness metadata to the dashboard, while the pendant receives only the verdict. Fail closed on empty-without-readability evidence.
- **missing:** A unified claim-verdict response that distinguishes empty, unreadable, stale, and conflicting; A corrected EventKit permission/readability probe rather than relying on Automation-TCC; A policy mapping uncertainty classes to spoken, queued, or dashboard-only output; Automatic provenance links from each briefing item to the source and permission evidence

### "When a briefing, reminder, or browser watch asks me to do something, let me say “why this?” or “not this source” and immediately hear the evidence, confidence, and consequence; if I revoke the source, stop future derived suggestions and show me what still remains to remove."
- **useful because:** The system currently can produce receipts and some evidence, but the owner cannot reliably trace a suggestion through evidence to effect, nor know that revoking a source failed to remove copied facts. This turns trust and correction into an everyday interaction rather than a forensic dashboard task.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic provenance graph traversal and revocation first; realtime model only for a short spoken explanation when the graph is ambiguous.
- **latency:** Answer the spoken “why?” in under 1 second from cached typed provenance; revocation must return a completion state and remaining copies within 3 seconds, otherwise say pending.
- **cost:** Near-zero generation for straightforward explanations; occasional small model call for ambiguity. Storage/indexing and cross-store cascade work dominate.
- **security:** Spoken responses must reveal only safe summaries; sensitive evidence requires dashboard confirmation. Revocation must be idempotent, auditable, and fail closed if a downstream copy cannot be located. Never claim deletion when only a tombstone was written.
- **missing:** A durable provenance edge from derived memory facts and context-graph entities back to evidence capsules and source IDs; A cross-store revocation cascade covering facts, graph copies, browser provenance, fleet memory, and audio/drafts; A typed spoken-safe explanation projection with sensitivity-aware redaction; A receipt that distinguishes tombstoned, deleted, unreachable, and still-live copies

### "Let the pendant recognize whether a spoken command is mine or a bystander’s, and use that identity as a hard boundary: anyone may ask for public information, but only my authenticated voice plus the required physical gesture may access private context or stage an external action. If confidence is low, ask me to press the button rather than guessing."
- **useful because:** A wearable is present in rooms where other people can hear and speak. Today the system largely treats any transcript reaching the relay as the owner’s intent, so a bystander, recorded voice, or accidental speech can enter the same action path. This would make the pendant safe to leave listening without turning every room into an implicit control surface.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** A small on-device speaker-verification model for a fast owner/non-owner verdict; realtime model only after the identity gate for the actual request. Deterministic policy evaluates what private data or action class the identity may unlock.
- **latency:** Identity verdict under 150 ms after end-of-utterance; uncertain cases fall back to a physical button and must not incur a dangerous speculative action.
- **cost:** On-device model work and enrollment dominate. Inference adds no per-turn API cost; occasional encrypted model-update or calibration traffic is small. A future microphone/SoC revision may be needed if the current RAM/CPU budget cannot hold a robust verifier.
- **security:** Voice is not sufficient for high-impact actions: replay and impersonation attacks remain possible, so irreversible actions still require the existing physical transaction latch. Store embeddings only locally, never send raw voice for identity, rotate enrollment material, and fail closed on uncertainty or privacy-latch state.
- **missing:** A measured speaker-verification model that fits the pendant’s remaining RAM/CPU budget; A secure local enrollment flow with replay/liveness resistance; An identity claim in the relay request and Mac/browser session protocol; Policy rules that separate public reads, private reads, drafts, reversible actions, and irreversible actions by identity confidence; Dashboard controls for enrollment, revocation, and an audit trail of identity-gated decisions

### "Before speaking anything private, have the pendant locally estimate whether the room is acoustically private. If other voices or a public-noise pattern are present, replace the content with a neutral alert and put the full item on my Mac or in the durable inbox; resume only after a deliberate button press."
- **useful because:** The owner can carry the pendant into meetings, transit, and shared rooms, but the current audio path has no bystander or ambient-privacy gate. A policy that depends only on timing or source sensitivity cannot know whether speaking now will disclose something to people nearby.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** A tiny local acoustic classifier for voice-count/noise/privacy estimation; no cloud model or raw audio upload. Realtime generation is used only after the local gate permits speech.
- **latency:** Local classification in under 100 ms at the audio boundary; a blocked item should become a neutral LED/inbox notification without delaying the conversation.
- **cost:** No recurring API cost. Firmware classifier, calibration tests, and a small local state machine are the main costs; raw PCM stays on-device.
- **security:** The classifier must never retain or transmit ambient recordings. It should fail closed when uncertain, expose only coarse states such as private/uncertain/public, and never override the physical privacy latch or owner confirmation. False positives reduce convenience; false negatives are the safety failure.
- **missing:** An on-device ambient-privacy classifier using only short-lived feature windows; A firmware audio-output gate that can defer an artifact without losing its playback cursor; A signed privacy-state field understood by relay and Mac speech paths; A policy table mapping content sensitivity and ambient state to speak, neutralize, queue, or require button press; Tests against replayed recordings, headphones, vehicles, meetings, and multiple speakers


## What it asked for

_Nothing._
