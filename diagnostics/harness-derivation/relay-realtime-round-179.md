# Harness derivation — relay-realtime — round 179

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Summarize what I was doing and pick it back up."
- **useful because:** This turns the system into a true personal assistant: it can resume context across surfaces, not just repeat tasks, and it reduces the cost of re-explaining after interruptions.
- **path:** relay → mac-bridge → browser
- **model tier:** Unified/faculty tiers for cross-surface reasoning; cheaper background for building the summary.
- **latency:** A quick spoken summary in a few seconds; deeper context reconstruction can run in the background.
- **cost:** Moderate; dominated by reading history and synthesizing a concise summary.
- **security:** Cross-surface summaries can combine sensitive content. Use strict scoping and avoid sharing data across accounts or apps without confirmation.
- **missing:** A shared preference/session memory projection (already requested and queued); A standard way to serialize and restore session state across Mac/browser/relay; A context budget strategy so the relay doesn’t resend large histories every turn

### "If I get cut off, turn my last request into a safe plan and keep it moving without me babysitting it."
- **useful because:** This is a step beyond simple notification: it preserves intent mid-conversation and hands it off reliably, so the owner doesn’t have to reissue the request after a disconnect or audio glitch.
- **path:** relay → mac-bridge → browser
- **model tier:** Realtime to capture intent; mac-planner for execution; cheaper background for monitoring and retries.
- **latency:** Intent capture immediate; execution follows normal Mac/browse timing; progress updates only when state changes.
- **cost:** Low to moderate; dominated by planning and occasional status checks.
- **security:** If intent capture is wrong, the system could do unintended work. Require reversible actions by default and a confirmation fallback for high-impact steps.
- **missing:** A durable intent handoff record at the relay (so a dropped voice session doesn’t lose the plan); A reliable completion notification path (current relay_event_push unresolved); A background monitor that can retry or escalate when the Mac is asleep

### "Give me an evidence-based answer to “is that actually done?” by reconciling the Mac action receipt, browser state, and relay delivery state, and tell me what is proven, what is only claimed, and what still needs checking."
- **useful because:** A spoken “done” is not trustworthy when a Mac action succeeded but a browser save failed, or a result never reached the pendant. This is the single most useful trust feature: one answer assembled from every substrate rather than the last model's narration.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheap background evidence reducer over structured receipts; realtime relay only verbalizes the final three-level verdict.
- **latency:** Under 3 seconds when receipts exist; if live inspection is required, say “checking” immediately and return within 15 seconds.
- **cost:** <$0.01 for receipt-only checks; $0.03–$0.15 when a live browser or Mac inspection is needed; inspection latency dominates.
- **security:** Do not infer success from intent or model text. Bind every claim to job/action IDs and timestamps, redact page contents and file data, and distinguish stale evidence from current evidence.
- **missing:** A normalized receipt schema shared by Mac, browser, and relay; A reconciliation endpoint that can request a final live inspection when evidence is stale; A truth-status vocabulary (proven/claimed/unverified/failed) carried into spoken replies; Correlation of delivery acknowledgements with execution receipts

### "Let me say “hand this off until I’m back” and have the pendant, relay, Mac, and authenticated browser coordinate a resumable work packet: preserve my constraints, continue across disconnections, and give me a compact spoken digest of changes when I reconnect."
- **useful because:** Today a dropped Mac link or ended voice turn turns an active task into a fragile one-shot request. A resumable work packet is the first genuinely wearable-to-machine workflow: I can leave the desk without losing intent or context.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Realtime only captures and confirms the packet; a cheaper background planner/worker executes and summarizes; vision is invoked only for UI ambiguity.
- **latency:** Acknowledge handoff in under 2 seconds; survive hours offline; deliver a digest within 10 seconds of the next connection.
- **cost:** $0.02–$0.10 per handoff depending on planner turns; storage and retries dominate infrastructure, not model tokens.
- **security:** Encrypt packet contents at rest, bind browser-session references rather than copying cookies, preserve an explicit constraint and expiry list, and never silently broaden the requested scope after reconnect.
- **missing:** Durable relay work-packet state with lease/heartbeat and retry semantics; A real scheduler/background worker (currently absent); Mac agent resume checkpoints and browser tab/session affinity; Pendant reconnect synchronization and digest delivery; Conflict handling when local files or web pages changed while offline

### "While a long Mac or browser job is running, let me press and say a new urgent request; suspend the old job at a safe checkpoint, handle the urgent request first, then resume the old job and tell me exactly what was preserved."
- **useful because:** A wearable front door must remain responsive: today an in-flight delegation competes with the next voice turn or forces me to wait. Preemption lets the pendant act as an always-available assistant without corrupting files, tabs, or the original plan.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay classifies urgency and acknowledges immediately; Mac planner owns checkpointing and resume; a cheap background worker reconciles receipts after each interruption.
- **latency:** Acknowledge and request the first urgent action within 2 seconds; checkpoint within 5 seconds for reversible actions; resume automatically after urgent completion.
- **cost:** $0.01–$0.05 for interruption and receipt synthesis, plus existing planner cost; checkpoint metadata is the main implementation cost.
- **security:** Never kill an action mid-write or mid-send. Require agents to expose safe-point boundaries, record before/after state, and explicitly report if the urgent task forced abandonment. Preserve browser session affinity and do not leak one task's context into another.
- **missing:** A job state machine with pause/resume/cancel and safe-point semantics; Planner-produced checkpoints for Mac and browser actions; Relay arbitration that binds each voice turn to a job without losing the prior job; Receipt stitching that marks the interruption interval and resumed step

### "When I leave my Mac, let me ask the pendant about a page I had open—“what changed since I looked?”—using a redacted, expiring snapshot from the authenticated browser session, without keeping cookies or requiring the browser to stay online."
- **useful because:** The browser holds private sessions the relay cannot reach once the Mac sleeps, yet the owner is often away wearing the pendant. A deliberately limited snapshot gives useful continuity without pretending the relay has a cloud browser or copying credentials.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Cheap background snapshot/diff extractor on the Mac; realtime relay answers only the spoken question and escalates to the Mac when a fresh snapshot is available.
- **latency:** Snapshot on tab change within 3 seconds; spoken diff under 2 seconds while cached; clearly say “snapshot stale” rather than fabricate a live answer.
- **cost:** <$0.01 per snapshot/diff in normal use; storage and redaction dominate, with no browser automation call unless explicitly requested.
- **security:** Never persist cookies, tokens, arbitrary page HTML, or hidden form values. Extract only user-approved fields, encrypt at rest, attach tab origin and expiry, delete on logout/session change, and make sensitive domains opt-in.
- **missing:** Browser-extension snapshot schema with field-level redaction and origin/session binding; Relay storage and diff endpoint with TTL and deletion guarantees; A pendant query route that distinguishes cached snapshot from live browser inspection; Mac sleep/reconnect synchronization and explicit stale-state wording


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: evidence-backed “is it actually done?” reconciliation across Mac/browser/relay receipts; resumable work packets that preserve intent across disconnections; and expiring, redacted browser-session snapshots that let the pendant answer what changed after the Mac goes away. A fourth recorded proposal adds cross-job urgent preemption with safe checkpoints. The clarification-question idea and USB desk transport were rejected as existing backlog items, so I did not count or rephrase them.

**Biggest unknown:** The precise schemas and live behavior of the existing receipt, watch, and browser-inspection routes remain insufficiently inventoried; implementation should verify those before treating the proposed missing endpoints as truly absent.

