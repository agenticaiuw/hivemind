# Harness derivation — faculty-judgement — round 150

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make my scheduled briefs self-healing: don’t tell me a brief was delivered unless I actually heard it, and recover quietly if I missed it.”"
- **useful because:** Today a routine can be marked completed at generation or acceptance while the pendant is offline, audio is never played, or playback is interrupted. This gives the owner one trustworthy contract: generated, downloaded, started, finished, or explicitly recovered—never a false ‘done’.
- **path:** relay → mac-planner → pendant → dashboard
- **model tier:** background for routine generation and reconciliation; realtime only for the short recovery sentence
- **latency:** Normal routine path unchanged; ACK reconciliation within 30 seconds of reconnect, with at most one short spoken recovery prompt at the next safe attention window.
- **cost:** Usually <$0.01 per routine beyond existing generation; dominant costs are existing TTS/audio generation, not reconciliation.
- **security:** Only opaque artifact IDs, delivery states, and short status text cross surfaces; no raw audio needs to leave the existing path. Recovery must be idempotent and must not duplicate audio. Require confirmation before changing a routine or sending an external message.
- **missing:** A durable routine-to-artifact-to-delivery join (routine IDs currently have no playback foreign key).; A worker that consumes record_pendant_delivery_event and transitions routine status to heard/missed/interrupted.; A repair policy: one retry, then pendant inbox/dashboard note, with owner-configurable quiet hours.

### "“Let me teach you how dense my spoken briefings should be—when I say ‘too long’, ‘too vague’, or ‘just right’, make the next ones measurably better.”"
- **useful because:** The system currently has fixed word and item caps, but no durable, owner-visible learning loop. A one-sentence correction after hearing a brief should change future length and ordering without requiring an expensive model every time.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Realtime classifies the tiny spoken feedback; background updates a bounded preference and evaluates the next briefing against it.
- **latency:** Feedback acknowledgement under 1 second; preference update under 5 seconds; visible effect on the next scheduled briefing.
- **cost:** <$0.005 per feedback event; most work is deterministic classification and preference storage.
- **security:** Store only the preference (‘shorter’, ‘more detail’, ‘fewer items’, ‘more actionable’) and source briefing ID, not the feedback audio or transcript by default. Never let learned density override quiet hours, sensitivity, or external-action confirmation.
- **missing:** A writer from the Mac/relay into shared fleet memory (the existing fleet memory has schema and readers but no production writers).; A stable briefing preference key and bounded decay/undo operation.; A physical or spoken feedback binding to the exact delivered artifact using delivery ACK/item correlation.

### "“If something you told me changes afterward, tell me it was corrected—not as a new unrelated alert, but as a correction to the exact sentence I heard.”"
- **useful because:** A page watch can detect churn, but the owner currently receives no semantic supersession of a prior spoken claim. This prevents stale flight/order/status information from remaining trusted merely because the original briefing sounded finished.
- **path:** browser-extension → mac-planner → relay → pendant → dashboard
- **model tier:** Cheap deterministic diff and provenance lookup first; background model only when changed text needs a concise correction; realtime only to speak an urgent correction.
- **latency:** Detect on the existing watch interval; correction draft within one watch tick; urgent correction arbitration under 2 seconds after classification.
- **cost:** <$0.01 for a normal correction; model cost only for ambiguous changed text. Browser reads and TTS dominate.
- **security:** Correction must cite the original source and changed source, redact sensitive content before speech, and never infer that a change invalidates unrelated claims. External mutations are never triggered automatically; dashboard can review or dismiss the correction.
- **missing:** A durable link from a delivered briefing item to its browser provenance/source IDs.; A supersedes relation and correction state (drafted, spoken, acknowledged, dismissed).; A watch scheduler hook that emits semantic change events into attention_arbitrate rather than an unlabelled notification.

### "“When my instruction is genuinely ambiguous, show me the two plausible interpretations and what each would change, then let me choose instead of silently guessing.”"
- **useful because:** The current system can ask for approval, but approval after an unstated interpretation is not informed consent. This capability turns ambiguity into a small, concrete fork: the owner sees the consequences, chooses one, and the chosen branch is carried consistently across the Mac, browser, relay, and pendant.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Realtime detects and explains the ambiguity in one short sentence; background models may construct branch previews; deterministic policy evaluates each branch before presentation.
- **latency:** Under 3 seconds for a read-only fork; mutation remains paused until the owner chooses.
- **cost:** <$0.02 for difficult multi-step forks; most simple forks use deterministic templates and existing previews.
- **security:** Neither branch may mutate state while being previewed. Branches must carry separate evidence and policy verdicts, redact sensitive details before speech, and expire when source state changes.
- **missing:** A typed ambiguity/fork object with branch IDs, assumptions, consequences, evidence references, and expiry.; A branch-aware preview executor for Mac and browser actions.; A pendant response protocol that binds the owner’s spoken choice to the displayed fork without treating speech alone as authorization for irreversible actions.; A receipt showing the rejected branch was never executed.

### "“When I walk away from my Mac, let me ask ‘what was I looking at?’ and get the exact tab, document, and unfinished thought I left behind—without making me reconstruct the context.”"
- **useful because:** The existing handoff carries model context, not a durable human-facing workspace bookmark. The owner loses the referent behind ‘that tab’ or ‘the thing I was editing’ when moving between pendant, Mac, and browser. This would make the wearable a true continuation of the owner’s work rather than a separate conversation.
- **path:** pendant → mac-planner → browser-extension → relay → dashboard
- **model tier:** Cheap deterministic capture of foreground app, active tab, selection/title, and pending job; realtime only to answer the owner’s spoken referent; background summarization for an unfinished-work sentence.
- **latency:** Capture on focus change within 2 seconds; spoken recall within 3 seconds when the Mac/browser are reachable; stale context must be labeled rather than guessed.
- **cost:** <$0.005 per context snapshot; occasional background summarization dominates.
- **security:** Never capture page bodies, form fields, passwords, or private tab contents by default. Store a short redacted locator and digest, with per-origin opt-out and explicit expiry. The owner must be able to delete the bookmark and all derivatives.
- **missing:** A durable cross-surface workspace-context record, distinct from provider prompt context handoff.; Foreground/tab identity capture with sensitive-origin suppression.; A spoken referent resolver that asks a clarifying question when multiple tabs match.; Deletion propagation across Mac, relay, and browser stores.

### "“If one source keeps contradicting the others, quarantine it from my decisions and tell me what you stopped trusting until I fix or re-authorize it.”"
- **useful because:** Conflict detection can identify disagreement, but the system today has no durable notion that a source has become unreliable. Repeated stale calendar data, a broken browser session, or a drifting page should not continue influencing plans merely because it remains reachable.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Deterministic rolling reliability scores and contradiction rules; background model only clusters equivalent claims; realtime speaks only a concise quarantine notice when it changes an imminent decision.
- **latency:** Update after each corroborated observation; decision-time lookup under 100 ms; owner notice within the normal attention arbitration window.
- **cost:** <$0.002 per observation; storage and deterministic comparison dominate.
- **security:** Quarantine is fail-closed for consequential actions but never silently deletes evidence. The owner can inspect, override, or revoke a source-specific quarantine. Do not infer unreliability from a single disagreement or from a permission-denied empty result.
- **missing:** A durable source-health/contradiction ledger with time decay and provenance links.; Typed source-scoped policy that prevents quarantined claims entering plans or spoken briefings.; A reauthorization and recovery workflow requiring fresh corroboration.; A clear distinction between unavailable, stale, contradictory, and malicious-looking sources.


## Changes it proposed to its own stack

### `integration` — Make scheduled briefing delivery a state machine keyed by one durable briefingItemId: routine run creates item; audio artifact references it; pendant ACK events advance downloaded/started/finished/interrupted; a reconciler marks missed only after expiry and creates exactly one catch-up inbox item. Persist the join and idempotency key across relay and Mac, and expose the full chain in the owner receipt.
- **owner gets:** The owner can ask ‘did I hear my brief?’ and get a truthful answer, with one recovery instead of duplicated or silently lost audio.
- effort: Medium: schema migration, relay/Mac join, ACK consumer, and tests for offline replay and duplicate events.  ·  risk: A bad timeout could nag after a delayed playback or duplicate a recovery. Fail closed to a dashboard/inbox status, dedupe by artifact and event IDs, and require explicit retry policy.
- cost: Negligible storage and compute; avoids duplicate TTS/audio generation in the common retry case.  ·  latency: No added generation latency; reconciliation is asynchronous.
- security: Keep content out of delivery telemetry; use opaque IDs and existing redaction before any spoken recovery.
- depends on: record_pendant_delivery_event; audio_delivery_ack_queue; relay job lease/requeue work; a durable routine-to-artifact foreign key

### `memory` — Add a bounded ‘briefing feedback’ preference writer with explicit provenance: feedback event references the heard briefing item, stores one of a small enum (shorter, longer, fewer_items, more_actionable, correct), decays after 30 days, and is removable as one preference. Inject it into briefingTriage policy calculation instead of changing hardcoded defaults.
- **owner gets:** The pendant gets better at the way this owner actually listens, without silently accumulating a transcript or making every briefing depend on a large model.
- effort: Small-to-medium: event schema, fleet-memory writer, policy projection, and a dashboard edit/delete control.  ·  risk: A misheard ‘too long’ could distort future briefs. Require a clear feedback phrase or dashboard confirmation, cap one update per item, and show the active rule in each briefing receipt.
- cost: A few bytes per event; tiny classifier call only when speech is ambiguous.  ·  latency: Sub-second acknowledgement; next brief computation adds only deterministic preference lookup.
- security: Persist enum plus item ID, never raw voice; preference is local/scope-limited and cannot authorize disclosure or external action.
- depends on: a production writer for shared fleet memory; audio item correlation token; briefingTriage policy seam; owner-visible provenance/revocation


## What it asked for

_Nothing._
