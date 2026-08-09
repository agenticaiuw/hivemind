# Harness derivation — relay-realtime — round 257

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say “do that on my Mac,” figure out the right tool and route it without me naming apps."
- **useful because:** This reduces friction. The owner speaks naturally, and the system chooses the correct downstream path (quick action vs delegated plan) based on complexity and risk.
- **path:** relay → mac-bridge → mac-bridge
- **model tier:** Realtime makes the routing decision quickly; downstream planning runs in the Mac planner.
- **latency:** Sub-second routing for simple actions; delegated tasks can take longer as the Mac plans them.
- **cost:** Low for simple actions; moderate when delegation invokes a planning turn.
- **security:** Avoid doing destructive actions without confirmation. Prefer reversible actions and safe reads when ambiguity is high.
- **missing:** A resolvable relay routing tool (relay_route_intent remains unimplemented).; An intent enum aligned to actual action types to make resolution reliable.

### "Summarize what you remember about my preferences and what we’re working on right now, briefly."
- **useful because:** It keeps the owner oriented and builds trust by making memory visible. It also exposes when context is missing so the owner can correct it.
- **path:** relay → mac-bridge
- **model tier:** Realtime can read and speak a brief summary; heavier retrieval should be handled by the Mac/local store if available.
- **latency:** A couple seconds is fine; prioritize correctness over speed.
- **cost:** Low; cost dominated by context retrieval and summarization.
- **security:** Summaries may include sensitive preferences. Keep them scoped to the current surface and avoid web-derived facts unless explicitly requested.
- **missing:** Wiring the memory projection into the live conversation context so it can be pulled cheaply and consistently.

### "“Move this conversation to my Mac without making me start over.” The pendant should hand the live voice session to the Mac when it becomes available, preserving the transcript, unresolved referents, pending action, and the exact point reached; the Mac should show the continuation and the pendant should remain the spoken control surface."
- **useful because:** The owner can begin a thought while walking and continue at the desk instead of repeating context or abandoning a half-finished action. This is a genuine pendant–relay–Mac handoff, not just another Mac command.
- **path:** pendant → relay → mac-planner → mac-vision → dashboard-ux
- **model tier:** relay-realtime handles the short handoff acknowledgement; mac-planner reconstructs and continues the task; mac-vision is used only if visual state is required; no expensive model is needed for transcript packaging.
- **latency:** Acknowledge in under 500 ms; transfer the compact session state within 2 s of Mac availability. The owner should be able to keep speaking during transfer.
- **cost:** Usually under $0.01 per handoff; dominated by one Mac-planner continuation call, not the relay acknowledgement.
- **security:** The handoff contains recent speech and possibly page/app state, so it must be bound to the paired Mac and session, expire after a short TTL, and never be visible to another device. Moving a pending action must not silently execute it twice; use an idempotent action/job id.
- **missing:** A relay session-handoff record containing transcript, projected context, unresolved entities, pending job id, and continuation status; A Mac availability subscription/heartbeat and a UI affordance to accept a transferred session; A resumable planner contract that can continue from a partial action receipt rather than starting a new plan

### "“Lock everything down now.” A deliberate pendant gesture should immediately revoke the active relay voice session, invalidate the paired Mac/browser command channel, stop queued execution, and tell me what was successfully stopped. The next interaction must require a fresh physical re-pair."
- **useful because:** The owner has given this system unusually broad access. A worn physical emergency control is the one thing they can reach when the Mac is unattended or a browser session is compromised; software-only logout is unavailable if the owner is away from the keyboard.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard-ux
- **model tier:** No large model is needed for the stop path. The relay performs deterministic revocation; mac-planner and browser-extension acknowledge cancellation; relay-realtime speaks a fixed concise result.
- **latency:** Transmit and persist the revocation in under 1 s when connected, and show an unmistakable local LED/haptic state immediately. If disconnected, latch the physical lockout and deliver it on reconnect before accepting another command.
- **cost:** Negligible per event; one small authenticated control message and acknowledgement fan-out.
- **security:** This is intentionally destructive to active sessions, so the gesture must be physically deliberate (for example a long press plus release), authenticated per device boot/session, replay-resistant, and fail closed when acknowledgements are missing. It should cancel queued commands but not pretend an already-completed external action was undone.
- **missing:** A firmware emergency-lock gesture and latched lockout state; A relay-wide revocation token checked by every voice, job, browser, and Mac command route; Mac/browser agents that cancel or quarantine queued work and return per-channel acknowledgements; A re-pair/unlock flow that cannot be triggered by ordinary voice

### "“Show me exactly what changed while you were working.” For any multi-step Mac or browser job, the relay should collect a compact before/after evidence bundle: changed files, URLs, app state, action receipts, and a plain-language explanation of side effects. The pendant can ask for a spoken summary, while the dashboard exposes the evidence for inspection."
- **useful because:** Today a completion sentence cannot establish whether a long workflow changed the intended thing, especially when the owner was away. This makes remote delegation trustworthy without forcing the owner to watch every click.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard-ux
- **model tier:** Agents collect structured evidence deterministically; a cheaper background model summarizes the evidence. relay-realtime only answers the owner's immediate “what changed?” question from the stored bundle.
- **latency:** Do not delay execution for prose generation. Store evidence incrementally; spoken summary under 1 s when requested, with detailed dashboard evidence available asynchronously.
- **cost:** Low: mostly receipts and hashes; one small summarization call only when the owner requests a narrative.
- **security:** Evidence can contain private URLs, filenames, screenshots, or snippets. Encrypt it, scope it to the owner/session, redact secrets, and apply retention limits. Never claim an unchanged file when the agent lacked permission to inspect it; represent unknown explicitly.
- **missing:** A normalized before/after evidence schema shared by Mac and browser actions; Receipt capture for every action including observation provenance and unknown/unreadable fields; A relay route that indexes evidence by job and a pendant-friendly summary endpoint; Dashboard views for diff/evidence rather than only success/failure


## What it asked for

_Nothing._
