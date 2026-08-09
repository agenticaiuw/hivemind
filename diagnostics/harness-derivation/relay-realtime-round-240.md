# Harness derivation — relay-realtime — round 240

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Tell me what’s going on with my system right now, and keep it short unless I ask for details."
- **useful because:** A quick spoken status check is ideal for a wearable. It saves opening the Mac and lets the owner decide whether to dig deeper.
- **path:** relay → mac-bridge
- **model tier:** realtime for the spoken summary; cheaper tier for assembling a longer report if requested
- **latency:** Quick status should be <1s when cached; a detailed follow-up can take longer.
- **cost:** Low; dominated by a small number of status reads.
- **security:** Status can reveal sensitive info (apps, network, calendar). Keep summaries high-level and avoid reading content unless asked.
- **missing:** A unified status aggregator that composes Mac status, job state, and device health into a single spoken summary

### "“Take care of this end to end while I’m away from my Mac. Use my open browser session and Mac apps, make the routine choices from what you know about me, and interrupt me only if the next step is genuinely ambiguous or consequential.”"
- **useful because:** Today the pendant can hand off a goal or a short action list, but the owner still has to manage the boundary between planning, browser state, Mac state, and follow-up. This would turn a spoken goal into a durable, resumable piece of work that progresses across all reachable surfaces and asks one focused question only when it cannot safely infer the answer.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** relay-realtime for intent extraction and concise clarification; mac-planner for the long workflow; mac-vision only when semantic UI state is needed; browser-extension for authenticated page state; cheaper background model for checkpoint reconciliation and final summarization.
- **latency:** Acknowledge in under 1 second; first action within 3 seconds; checkpoint updates asynchronously. A clarification should arrive only at a true branch, not during every action.
- **cost:** About $0.03–$0.15 per ordinary workflow depending on planner turns and screenshots; browser and vision observations dominate, not the short relay exchange.
- **security:** The workflow can act in authenticated sessions and mutate files or web data. It must preserve the owner’s maximum-access preference while recording a typed action trail and exact checkpoint evidence; the owner should be able to say stop or undo the current reversible checkpoint. Secrets stay on the Mac/browser surfaces and are not copied into the spoken prompt.
- **missing:** A durable cross-surface workflow/checkpoint coordinator that can pause and resume a POST /plan or POST /execute job when a clarification is needed; A standard handoff envelope carrying goal, memory projection, current browser evidence, Mac state, checkpoint, and pending question; A real completion/clarification delivery path to the pendant, beyond the currently unresolved event-push promise

### "“Before I submit this, tell me whether it matches what I intended.”"
- **useful because:** The owner often needs a second set of eyes rather than another automation. The system should combine the authenticated browser’s actual form/page, the Mac’s visible app state, and the spoken intent, then report mismatches such as wrong recipient, amount, attachment, date, or environment before submission. This is a new evidence-and-intent comparison, not a generic page read or action confirmation.
- **path:** pendant → relay → browser-extension → mac-vision → mac-planner
- **model tier:** relay-realtime extracts the intended constraints; browser-extension supplies DOM/text evidence; mac-vision supplies rendered-state evidence when the DOM is insufficient; a slower judgement model compares them and returns a short spoken verdict with cited fields.
- **latency:** Under 4 seconds for text/DOM checks and under 8 seconds when a screenshot or vision pass is required; no mutation occurs while checking.
- **cost:** Roughly $0.01–$0.06 per check; vision screenshot analysis is the dominant cost.
- **security:** Evidence may contain private mail, financial, or health data. Keep raw evidence on the owning surface, pass only selected fields to judgement, redact secrets, and retain a short-lived receipt. This is a read-only preflight and should not block ordinary browsing.
- **missing:** A cross-surface intent-vs-evidence schema with field extraction and confidence; A browser action that can pause exactly before a submit and expose the candidate mutation without clicking it; A relay response format that can speak a concise mismatch list and link it to the pending job

### "“Show me proof that it really happened everywhere I asked.”"
- **useful because:** A spoken “done” is not enough when a Mac file, a browser account, and the relay can disagree or one surface can silently fail. The owner should receive one concise spoken result plus a durable receipt showing the before/after evidence for each requested surface, and a clear distinction between completed, observed, and merely queued.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime relay gives the immediate one-sentence answer; mac-planner and browser-extension perform the requested work; a cheaper background verifier compares postconditions and assembles the evidence receipt; mac-vision is used only when rendered UI is the only proof.
- **latency:** Immediate acknowledgement under 1 second; ordinary verification under 10 seconds; long verification can finish asynchronously and alert the pendant.
- **cost:** About $0.02–$0.10 per request, dominated by a second browser/Mac read or screenshot rather than generation.
- **security:** Receipts can contain private page text and filenames. Store hashes, selected fields, and redacted evidence by default, with raw captures expiring quickly. Never claim success from an action response alone; require an observed postcondition or explicitly say unverifiable.
- **missing:** A postcondition/verifier schema attached to each planned action, rather than a free-form goal only; Cross-surface receipts that correlate Mac, browser, and relay evidence under one job; A spoken distinction between queued, executed, observed, and verified, delivered after the voice session


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: a durable cross-surface task executor that pauses only for genuine ambiguity, an intent-versus-evidence preflight before submission, and proof-backed verification that distinguishes queued/executed/observed/verified. The first and third are especially important because the owner can walk away from the Mac; all three require connective work between existing plan/execute, browser, Mac, job, receipt, memory, and event surfaces. The live memory-projection wiring proposal was rejected as already in the backlog, so I did not count it.

**Biggest unknown:** The exact durable handoff and postcondition schemas do not exist yet; the existing job receipts and pipeline events need to be inspected and extended rather than treated as sufficient.

