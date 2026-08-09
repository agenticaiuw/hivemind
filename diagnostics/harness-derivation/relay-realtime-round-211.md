# Harness derivation — relay-realtime — round 211

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If I say ‘that’s wrong’ right after you summarize a result, fix the task or roll it back.”"
- **useful because:** Voice-first correction turns the pendant into a real control surface: the owner can recover from mistakes quickly without digging into apps or logs.
- **path:** relay → mac-bridge → mac-harness → pendant
- **model tier:** Realtime for interpreting the correction; mac-planner for choosing a safe rollback or edit; cheaper tier for audit trail.
- **latency:** Under ~2 seconds to acknowledge; rollback execution depends on the job but should be queued immediately.
- **cost:** Low for the voice interpretation and job lookup; moderate if it triggers a new plan and execute cycle.
- **security:** A rollback is a destructive action. Require confirmation for high-impact changes and rely on receipts/audit logs to prove what changed.
- **missing:** A standardized mapping from natural-language corrections to actionable rollback/edit operations; Reliable job receipts rich enough to reconstruct side effects; A safe default strategy when multiple changes are eligible for rollback

### "“I’m away from my Mac. Tell me exactly what I was in the middle of, across my Mac, browser, and pendant, and let me say ‘continue’ to pick it back up.”"
- **useful because:** The pendant currently starts new conversations, but it cannot reconstruct a truthful working set from the other surfaces. This would make the wearable a reliable handoff point: current app and window, active browser tab and page state, unfinished Mac jobs, recent owner-scoped facts, and device connectivity become one short spoken answer. “Continue” would resume the identified reversible workflow rather than forcing the owner to remember which surface held it.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime model only for the short spoken synthesis and disambiguation; a cheaper background planner should gather and normalize the context, while mac-planner performs the resumed workflow.
- **latency:** First answer under 3 seconds when Mac and browser are online; up to 10 seconds for a fresh cross-surface snapshot. Resume acknowledgement under 2 seconds, with asynchronous progress thereafter.
- **cost:** About $0.01–$0.04 per handoff, dominated by one realtime turn; context gathering and job polling should use cheap non-realtime calls.
- **security:** The answer must only include facts scoped to voice and the current owner session, never arbitrary browser page contents. Resuming must be limited to the previously identified workflow and produce an auditable job receipt; destructive or external-send steps should be surfaced as pending rather than silently inferred.
- **missing:** A cross-surface context assembler that joins machine context, browser state, live jobs, and projected memory into a stable checkpoint; A durable checkpoint identity and resume endpoint mapping one spoken ‘continue’ to the exact planner goal and prior constraints; Mac/browser adapters that report the current task, not just raw tabs or installed applications

### "“Don’t just tell me the Mac task finished—verify the result independently and tell me what is actually true.”"
- **useful because:** Planner success is not the same as world-state success: an app may have rejected a save, a browser command may have acted on the wrong tab, or a network request may still be pending. The relay should commission a separate perception pass after an action, compare the observed state with the requested outcome, and speak a calibrated result such as verified, partially verified, or could not verify. This is the single most valuable trust feature because it prevents the owner from acting on a confident but false completion report while away from the screen.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Cheap background perception and deterministic checks first; realtime is used only to explain the verdict in one sentence or ask a narrowly scoped follow-up.
- **latency:** Initial acknowledgement under 2 seconds; verification within 5–15 seconds depending on app/browser state, with an asynchronous pendant update for slower checks.
- **cost:** Roughly $0.01–$0.08 per verified action, dominated by screenshots or page extraction and only occasional model adjudication; deterministic receipts should handle the common case.
- **security:** Verification may inspect private screens and authenticated pages, so retain only hashes, selected evidence, and redacted snippets. Never claim verified from a planner receipt alone. If evidence conflicts, say so and preserve both the requested intent and observed state for audit.
- **missing:** A post-execution verification contract linking requested outcome assertions to concrete observable predicates; A faculty-perception endpoint that can inspect Mac/browser state after execution and return evidence with confidence; A relay-owned verdict record and pendant delivery path that distinguishes complete, partial, failed, and unverified

### "“Pin this thought to whatever I’m currently looking at, and bring it back when I return to that page or file.”"
- **useful because:** A spoken idea is usually lost because the owner cannot type while wearing the pendant. This is not another audio memo: the relay should transcribe the utterance, identify the active Mac document or authenticated browser page, store a short semantic note with that entity and surface scope, and later surface it when that same work context returns. It turns the worn device into a context-aware annotation tool rather than an inbox of orphaned recordings.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Realtime model performs concise transcription/entity clarification; a cheaper background model extracts a title, entities, and retrieval keywords. No expensive model is needed on recall unless the owner asks for a synthesis.
- **latency:** Acknowledge the pin in under 2 seconds; attach it within 8 seconds when the Mac/browser is online. If the target cannot be identified, retain the note as unassociated and say that plainly.
- **cost:** About $0.005–$0.03 per pin, mostly transcription plus a small extraction call; retrieval should be deterministic keyword/entity matching.
- **security:** Page titles, document names, and note contents may be sensitive. Store only the minimum excerpt, encrypt at rest, scope facts to voice/mac/browser, and never attach to a page or file based on a weak match without saying “I’m not sure what you meant.” Browser-originated content must remain a separate low-trust memory tier.
- **missing:** A live-turn call to the existing scoped memory projection/store; A Mac/browser ‘current work entity’ endpoint returning stable document/page identifiers and confidence; An entity-linked pin record plus a trigger that surfaces matching pins when the owner revisits the context


## What it asked for

_Nothing._
## Its own summary

Recorded three non-duplicate owner capabilities: (1) a cross-surface “resume my work” handoff from the pendant, (2) independent post-action verification that reports what is actually true rather than trusting planner success, and (3) context-linked spoken pins attached to the active Mac document or browser page. The first two are especially important when the owner is away from the Mac; independent verification is the highest-value trust feature. I also attempted the known memory-projection wiring change, but the recorder correctly rejected it as already covered.

**Biggest unknown:** The missing pieces are not discoverable this round: a stable current-work entity API across Mac/browser, an outcome-assertion/evidence contract for post-action verification, and a relay-owned checkpoint/resume model. Existing routes can supply raw ingredients, but no observed contract yet joins them into these owner-facing behaviors.

