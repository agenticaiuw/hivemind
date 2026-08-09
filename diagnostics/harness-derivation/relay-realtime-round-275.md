# Harness derivation — relay-realtime — round 275

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say what I’m trying to do, keep me on track across devices—browser, Mac, and voice—by building a single shared plan and updating it as I work."
- **useful because:** It turns the pendant into a continuity layer. You can start a task by voice, then continue on the Mac or browser without re-explaining, and the system can remind you what’s next.
- **path:** relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for capturing intent, then a cheaper planner to maintain and update the plan.
- **latency:** Quick capture (under a second) and then asynchronous updates; plan updates can take seconds.
- **cost:** Moderate: planning and context synchronization are the cost drivers; minimize by storing a compact plan and diffing updates.
- **security:** Plans can reveal sensitive project details. Store minimal steps, avoid secrets, and scope visibility by surface (voice vs browser vs mac).
- **missing:** A shared task/plan representation that all surfaces read and update (likely via the memory store or context graph).; A plan-diff mechanism to update steps without resending full context.; A relay-visible surface capability registry so the relay can see what it can do without probing.

### "When I’m about to say something risky—like sending an email, buying, or deleting—warn me and summarize the impact before it happens."
- **useful because:** This is a safety net that still respects the owner’s preference for minimal friction: a spoken heads-up before irreversible actions.
- **path:** relay → mac-bridge → browser
- **model tier:** Realtime for the spoken warning; downstream agents for action classification and receipts.
- **latency:** Sub-second for the warning; classification can happen as part of planning.
- **cost:** Low to moderate; classification is cheap compared to executing actions.
- **security:** Misclassification could block legitimate work or fail to warn. Keep it advisory (no hard gate), and log the rationale in receipts.
- **missing:** Typed action classification in the planner’s output as metadata (read-only vs reversible vs high-impact) without blocking execution.; A standard place in receipts to attach the risk summary for the relay to speak verbatim.

### "If my pendant is offline, let the Mac act as a temporary voice gateway—capture a quick voice command locally and forward it to the relay when the pendant reconnects."
- **useful because:** It reduces dead-time. You can still use the system when the pendant is charging or out of range by speaking near the Mac.
- **path:** mac-bridge → relay → pendant
- **model tier:** Realtime for voice; local capture on the Mac; background forwarding.
- **latency:** Local capture should feel immediate; forwarding can be delayed until reconnect.
- **cost:** Moderate; audio capture and storage are the main costs.
- **security:** Capturing voice on the Mac is sensitive. Make it opt-in, clearly indicated, and store only transient audio needed to forward.
- **missing:** A Mac-side voice capture and forward feature (new capability) with explicit UI indication.; A relay endpoint for deferred voice commands and a way to associate them with a session when the pendant reconnects.

### "“Save this thought with the page I’m looking at.” While I speak into the pendant, bind the utterance to the exact active browser tab, selected text or page excerpt, URL, and timestamp, then let me retrieve it later by voice even if the Mac is no longer open."
- **useful because:** A fleeting thought becomes useful, searchable context instead of an unlabelled memo. The browser contributes authenticated page state, the pendant contributes the moment and voice, and the relay preserves the association across devices.
- **path:** pendant → relay → browser → mac-planner
- **model tier:** Realtime only for the short spoken acknowledgement and intent extraction; a cheaper background model should normalize the transcript, select a compact page excerpt, and create the durable memory record.
- **latency:** Acknowledge in under 1.5 seconds; page capture and indexing may finish asynchronously within 10 seconds.
- **cost:** About $0.002–$0.02 per capture depending on transcript and excerpt summarization; browser extraction and storage dominate latency, not inference.
- **security:** The page may contain private or authenticated data. Send only the explicitly bound tab excerpt, never all open tabs; redact secrets and provide a spoken “forget that page note” operation. Require confirmation before sharing or exporting a note.
- **missing:** A live-turn browser-tab binding API that identifies the owner’s active tab and selected text; A durable relation from a voice capture to a browser finding and later voice search; A relay-side asynchronous indexer that can complete after the spoken response

### "“Put me back where I was.” After I leave the Mac, let the pendant later reopen the exact working state of a task: the relevant app and browser tabs, document or page positions, unsent draft, and the next safe action, then ask whether to continue or just tell me the checkpoint."
- **useful because:** The owner can walk away mid-task without reconstructing mental state. This is materially different from a job-completion alert: it preserves an intentional, resumable checkpoint of interactive work and makes the wearable the handoff between presence and the Mac.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** Use the realtime model only to recognize checkpoint/resume intent and speak a one-sentence status. Use a cheaper background planner to serialize the app/browser state and propose a continuation action.
- **latency:** Checkpoint acknowledgement under 2 seconds; state snapshot under 5 seconds when the Mac is reachable; resume should report its result within 15 seconds.
- **cost:** Roughly $0.01–$0.05 per checkpoint/resume; most cost is a compact state description and planner call, while screenshots should be captured only when needed.
- **security:** Drafts and authenticated pages are sensitive. Encrypt checkpoints, scope them to the owner, expire them by default, and never submit/send/delete on resume without an explicit spoken confirmation. A stale checkpoint must be reported as stale rather than silently acting on it.
- **missing:** A Mac action to snapshot and restore window/tab/document positions plus unsent text without submitting it; A versioned checkpoint record with freshness and conflict detection; A relay command that can wake or reconnect the Mac and return a structured restore diff

### "“Erase what I just said and everywhere it went.” Let me revoke one recent voice interaction by time or spoken description, removing its transcript, captured audio, browser-derived facts, model context, and downstream job artifacts, then tell me exactly what could not be removed."
- **useful because:** A wearable microphone makes accidental disclosure inevitable unless erasure is as easy as capture. This gives the owner a trustworthy privacy control across the entire hive rather than deleting only one visible memo.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** Realtime model identifies the target interaction and gives immediate acknowledgement; a background deletion worker traverses linked artifacts and returns a precise receipt.
- **latency:** Confirm target in under 2 seconds; begin deletion immediately and deliver a completion or exceptions report within 30 seconds.
- **cost:** Usually under $0.01 per request; the dominant cost is an indexed artifact traversal and secure deletion verification, not model tokens.
- **security:** Deletion itself is high impact: require a deliberate second press or explicit spoken confirmation for broad ranges, preserve only a minimal tamper-evident deletion receipt, and distinguish hard deletion from provider retention that cannot be controlled. Never echo the sensitive content in the confirmation.
- **missing:** Stable correlation IDs linking audio, transcript, prompt context, memory facts, browser findings, jobs, and receipts; Authenticated cascade-delete and retention APIs on relay and Mac/browser stores; A deletion receipt that reports confirmed, pending, and externally retained artifacts


## What it asked for

_Nothing._
## Its own summary

Recorded three cross-surface capabilities: voice notes anchored to the exact active browser context; resumable, versioned Mac/browser work checkpoints; and a cross-hive “erase what I just said” cascade with honest deletion receipts. Each names the missing linkage or API rather than pretending the existing capture, planning, memory, and job routes already provide it.

**Biggest unknown:** Whether the existing capture and browser-inspection records already carry a shared correlation ID; without that, both reliable work handoff and complete privacy erasure require new durable linkage.

