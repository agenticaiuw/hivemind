# Harness derivation — mac-terminal — round 215

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live USB bench reachability** — The granted mac_usb_serial_diagnostics call still cannot execute: live inventory has no serial/USB capability, and resolver nearest matches are generic Mac status routes. The two chips are known physically connected, but no bounded serial health frame has been read this round.
  - evidence: mac_usb_serial_diagnostics returned unresolved; best match action:get_mac_status score 0.226, with no serial capability in the published inventory.

## Capabilities it proposed

### "On my pendant, say: “What in my authenticated work portal needs me today?” and hear only genuinely urgent items, with the source page and a one-sentence next action."
- **useful because:** This is the highest-value everyday capability: it turns an authenticated browser session the cloud cannot reach into a low-friction wearable briefing, without dumping a noisy portal or requiring the owner to open the Mac. It directly fills the previously denied portal request at the correct browser layer.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background model for scheduled page extraction and priority ranking; realtime model only for the short spoken answer and follow-up questions.
- **latency:** Scheduled refresh within 5 minutes of the portal changing; on-demand answer under 8 seconds if the browser heartbeat is healthy, otherwise explicitly say the snapshot age.
- **cost:** Roughly $0.01–$0.05 per refresh depending on page count and model context; on-demand speech response is a small realtime turn. Dominant cost is extracting/ranking changed portal pages, not transport.
- **security:** Page text and URLs remain on the Mac/relay boundary and must not be sent to a generic public search model. Store only short-lived findings with source URL, title, timestamp, and confidence; never persist credentials, screenshots, or whole HTML. The owner should confirm before any suggested portal action is executed.
- **missing:** A browser-harness routine that can declare which authenticated portal hosts/pages are in scope and a last-seen cursor per host; A change-aware extraction job that converts page updates into browser findings and suppresses duplicates; A wearable briefing intent that reads those findings and includes snapshot age and source provenance

### "Run a bench check on the connected pendant and audio bridge, then tell me whether a spoken turn can travel from microphone to Mac and back, with the exact failing link if not."
- **useful because:** The chips are physically present now but have no product transport registration. A bounded test would replace guesswork with a real go/no-go answer before the owner relies on wearable continuity, and would catch one-sided audio, framing, clock drift, or a dead USB endpoint in minutes.
- **path:** mac-terminal → mac-planner → pendant → relay-realtime
- **model tier:** No expensive model for the test itself; deterministic host parser and firmware counters first, with a cheap model only to turn the structured verdict into plain speech.
- **latency:** 30 seconds for enumeration and health frames, 2 minutes for a short loopback audio sample; answer immediately after the last frame or with a named timeout.
- **cost:** Negligible API cost if deterministic. Main cost is engineering a small serial reader/parser and one controlled test utterance; no cloud audio should be uploaded by default.
- **security:** Read-only diagnostics only. Keep captured audio in RAM or delete it after a checksum/sequence test; do not transmit raw microphone data to relay. Record port identity, firmware versions, frame counts, CRC failures, and timestamps, not speech content. Require explicit confirmation for any firmware flash or reset.
- **missing:** A real Mac serial diagnostic/action implementation (the current requested serial schema still does not resolve to a live capability); A shared framed health protocol on both chips: firmware/build ID, transport state, monotonic frame counter, CRC/error counter, underrun/overrun, and loopback marker; A host-side acceptance runner that opens both known ports, correlates counters and deadlines, and emits a machine-readable receipt; A deterministic audio loopback mode that uses a generated tone or fixture signal rather than the owner's microphone

### "When I am in a meeting or focused, let only truly time-critical events reach the pendant; queue everything else and give me a compact catch-up when I am free."
- **useful because:** The pendant should reduce interruption rather than become another notification stream. This combines Mac focus state, authenticated browser changes, calendar timing, and the wearable's tiny output into one attention policy the individual surfaces cannot enforce alone.
- **path:** mac-planner → browser-extension → relay-realtime → pendant → dashboard
- **model tier:** Deterministic rules for Focus/meeting windows, sender/domain allowlists, deadlines, and deduplication; a cheap background model classifies ambiguous event urgency. Realtime is used only when an event actually crosses the interrupt threshold.
- **latency:** Urgent event decision within 3 seconds of a browser heartbeat or Mac state change; nonurgent events become available in a catch-up within 10 seconds of leaving Focus.
- **cost:** Low: most decisions are local rules and incremental browser findings. Model spend is limited to ambiguous changed items, perhaps $0.005–$0.02 per item; no model call for routine suppression or dedupe.
- **security:** Focus state, calendar titles, and portal snippets are sensitive. Keep full content local to Mac/relay, send the pendant only urgency, source label, and a short redacted summary. Never infer an emergency from a single low-confidence page change; expose why an item interrupted and allow a local mute/undo.
- **missing:** A unified attention state with explicit source, expiry, and reason (meeting, Focus mode, manual quiet, emergency override); A browser-change event adapter that emits normalized urgency candidates rather than full page payloads; A pendant catch-up protocol that can page through queued summaries without turning the one LED/button into a gesture system; A policy editor in the dashboard for deadlines, trusted senders, and quiet windows

### "When I say “continue that” on the pendant, resume the exact browser page, Mac project, and unfinished action I was referring to—even after the browser tab, Mac app, or voice session changed—and tell me what will happen before it does anything."
- **useful because:** Today “that” is fragile across surfaces: the pendant, browser session, and Mac planner do not share a durable referent. A spoken handoff capsule would let the owner leave a task, move between devices, and return hours later without reconstructing URLs, tabs, files, or the last completed step.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Cheap background model creates and refreshes the capsule from structured events; realtime model resolves the short spoken reference and answers the owner. Deterministic IDs and state transitions, not an LLM, decide what is safe to resume.
- **latency:** Capture the capsule within 1 second of a stop or explicit “hold that”; resolve a follow-up in under 3 seconds. Loading the browser/Mac state may take up to 8 seconds, with an honest progress response.
- **cost:** Low: mostly structured state and hashes, with occasional small model calls for naming the capsule. Dominant cost is browser/Mac state synchronization, not inference.
- **security:** Capsules may contain sensitive URLs, filenames, and task text. Keep full state on the authenticated relay/Mac boundary, encrypt at rest, expire inactive capsules, and speak only a redacted summary until the owner asks for detail. Never execute a resumed mutation merely because a capsule exists; the owner must explicitly say continue.
- **missing:** A durable cross-surface referent/capsule schema with stable entity IDs, source timestamps, expiry, and last-known state; Event adapters from pendant turns, browser tab/session changes, Mac active project/window changes, and action receipts; A resolver that ranks spoken references such as “that” against recent capsules and returns ambiguity instead of guessing; A resume planner that reconciles stale browser/Mac state against the capsule before producing an execution preview

### "Compare the two things I have open—whether they are browser pages, a Mac document, or both—and tell me the decisive differences with a citation to each source; if I say “use the better one,” act on that choice."
- **useful because:** The owner currently has to manually copy information between the authenticated browser and Mac apps before making a decision. A shared comparison capability turns the devices' different reach into something useful: browser-only facts stay inside the session while Mac-local material remains local, yet the owner hears one grounded answer and can continue hands-free.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Background extraction produces normalized claims and source anchors; a mid-tier model compares them. Realtime handles only the spoken disambiguation and final answer, not full-page reasoning.
- **latency:** Identify the two targets in under 2 seconds; return a first comparison in 10 seconds for ordinary pages/documents, with progressive completion for large sources.
- **cost:** Approximately $0.02–$0.10 per comparison depending on document size. The dominant cost is extracting two source representations; cache by content hash so repeat questions are cheap.
- **security:** Do not merge authenticated browser content into external search or expose local documents to a public model. Preserve per-claim source URLs/page anchors or file paths, redact secrets, and require explicit confirmation before “use the better one” changes a file, form, or browser state.
- **missing:** A cross-surface target picker that maps “these two” to the current browser tabs, focused Mac document, or explicitly named sources; Structured document extraction for local files and browser pages with stable anchors and content hashes; A claim-level comparison format that preserves which source supports each difference and flags disagreement or missing evidence; An execution adapter that turns the selected result into a preview against the originating browser or Mac surface

### "While you work on a long Mac or browser task, give me brief spoken progress at meaningful milestones, tell me when you are blocked, and let me answer a question without losing the task."
- **useful because:** Today a long action is either silent or reduced to a final receipt; the owner cannot tell whether the agent is making progress, waiting on a page, or failed. Milestone narration makes remote work trustworthy from the pendant while preserving the ability to continue asynchronously.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic milestone events and failure classification; a cheap summarizer converts them into short speech. Realtime is reserved for the owner's interruption or answer, not for every progress update.
- **latency:** Emit a concise update within 1 second of each meaningful milestone, never more often than once per 20 seconds unless blocked or failed. Resume the task within 3 seconds after an owner answer.
- **cost:** Low: event-driven summaries are a few tokens per milestone, perhaps under $0.01 for a typical task. The dominant cost is maintaining a resumable task state, not inference.
- **security:** Progress speech must not read shell output, credentials, private URLs, or document contents aloud by default. Send the relay a redacted event class and short summary; retain full evidence in the Mac job record. If the agent needs a consequential choice, state the exact choice and defer the action until the owner answers.
- **missing:** A durable milestone stream separate from final job receipts, with sequence numbers and replay cursors; Adapters from sequential Mac actions, browser commands, waits, and failures into semantic milestones; A pendant speech queue that coalesces stale updates and survives a dropped link without claiming completion; A conversational pause/resume protocol that binds the owner's answer to the waiting task and rejects late answers


## Changes it proposed to its own stack

### `mac-harness` — Implement a boot-time reconciliation and resumable execution journal: mark every previously processing job as interrupted, close each ledger at the last durable step, join ledger.jobId to the job record, and expose a resumable plan whose completed action IDs are skipped while unfinished actions are rerun only when their replay safety permits. Have the relay and pendant report “interrupted at step N” rather than stale running.
- **owner gets:** After a Mac sleep, crash, or agent restart, the owner can say “continue that” and get a truthful continuation instead of a permanently-running ghost job or duplicated side effects. This is especially valuable for browser workflows and long shell tasks that cannot be watched continuously.
- effort: Medium-high: boot reconciliation, ledger closure, job/ledger ID propagation, replay classification, and a continuation route plus pendant status mapping; test crashes between dispatch and receipt.  ·  risk: A side effect may have happened without its receipt, so unsafe actions must remain unresolved rather than blindly repeated. Recover by marking the step needs review, showing its last known evidence, and allowing the existing explicit execute path to rerun only after the owner chooses.
- cost: Negligible API cost and disk overhead; a few kilobytes per ledger/job. Engineering cost is the main expense.  ·  latency: No impact on normal actions beyond writing the already-intended receipt; recovery scan adds under a second at boot for the capped stores.
- security: Improves auditability without adding a gate. Do not copy shell environment or sensitive browser content into the recovery summary; retain action IDs, effect class, timestamps, and redacted error metadata.
- depends on: The existing action ledger must call closeLedger for every orchestrator execution; Propagate planMeta.jobId into the ledger instead of leaving it null; Add a stable replay-safety/idempotency decision for each action type; Add a read-only continuation/status surface consumed by relay-realtime and the pendant


## What it asked for

_Nothing._
