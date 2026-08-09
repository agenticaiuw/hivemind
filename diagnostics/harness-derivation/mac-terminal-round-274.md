# Harness derivation — mac-terminal — round 274

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live USB diagnostic reachability** — The granted mac_usb_serial_diagnostics schema still cannot execute: live inventory has no serial capability and resolver falls back to get_mac_status. The two chips may be physically attached, but this agent cannot read their UARTs through a dedicated bounded tool.
  - evidence: Called mac_usb_serial_diagnostics for /dev/cu.usbmodem00096003658*, /dev/cu.usbserial-0287A9CA with 500 ms/4096 B; response was unresolved, best match action:get_mac_status score 0.225.

## Capabilities it proposed

### ""Finish this even if the Mac sleeps or the browser drops, and tell me on the pendant exactly what happened.""
- **useful because:** A spoken request should become a durable cross-surface transaction, not a ghost job. The pendant records intent and shows truthful state; the relay owns the handoff; the Mac resumes or proves it cannot; the browser contributes authenticated work and evidence. This is the system's single most useful capability because it makes delegation dependable during the interruptions that currently cause the owner to repeat themselves.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the initial acknowledgement and final short answer; a cheaper background worker supervises retries, restart recovery, and evidence collation.
- **latency:** Acknowledge within 300 ms locally and within 2 s over the link; completion can take as long as the task, but a stale heartbeat must be reported within 10 s and never presented as success.
- **cost:** One short realtime turn plus background orchestration; roughly $0.01-$0.05 per ordinary request, dominated by model calls only when recovery or browser interpretation is needed.
- **security:** The relay must persist an opaque intent ID, not raw microphone audio. Browser evidence may contain private authenticated pages and must remain on the Mac/relay with redacted summaries. The owner has chosen maximum Mac access, so confirmation is not the design; instead require idempotency keys, explicit side-effect receipts, and never claim completion without a postcondition.
- **missing:** A durable intent record shared by pendant, relay, and Mac with exactly-once dispatch; Boot-time reconciliation and supervised child processes on the Mac; A browser evidence capsule linked to the same intent ID; Pendant protocol messages for heartbeat, stale, resumed, and terminal evidence states

### ""Run a five-minute health check on the pendant and audio bridge, and tell me whether the wearable path is actually ready—not just whether the Mac sees USB.""
- **useful because:** The chips are physically present now, but a port enumeration result cannot distinguish a booting board, a wedged audio codec, a stale UART, or a functioning end-to-end path. This gives the owner a concrete go/no-go answer before trusting the pendant in daily use, with captured counters and an audible result rather than engineering logs.
- **path:** pendant → mac-bridge → relay → dashboard
- **model tier:** Background deterministic parser and thresholds; realtime is used only to turn the final health verdict into a concise spoken response if the owner asks by voice.
- **latency:** Start feedback within 1 s, collect for 5 minutes maximum, and return a verdict within 2 s of collection ending. A failed or disconnected board should be identified within 10 s, not after the full window.
- **cost:** Near-zero model cost for framing, counters, and thresholds; $0.001-$0.01 only if a model is needed to summarize unusual logs. Main cost is five minutes of USB capture and modest local storage.
- **security:** USB diagnostics must be read-only and restricted to the two known device paths; no arbitrary network upload and no microphone recording. Store hashes and counter summaries by default, with raw UART logs retained locally only until the owner deletes them. The test must clearly label 'USB bench path' and never imply LTE readiness.
- **missing:** A host-side bounded UART reader/framing parser for nRF9160 and ESP32; A firmware diagnostic command that emits version, boot counter, audio-frame counters, CRC/errors, and loopback acknowledgement; A deterministic end-to-end test runner that correlates both UARTs and produces pass/fail thresholds; A relay/dashboard result route and a pendant spoken/LED result message

### ""After you change something in my browser, Mac, or phone, prove the new state to me—don't just say the click ran.""
- **useful because:** Execution success is not the same as the requested outcome: a click can hit a stale tab, a shell can return zero while changing nothing, and an iPhone action can land on the wrong screen. A cross-surface postcondition check gives the owner a trustworthy answer and a useful failure explanation, especially for authenticated browser and mirrored-phone work that the pendant cannot inspect itself.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** Use deterministic snapshots, DOM/accessibility state, and shell exit status first; invoke a cheaper reasoning model only to map the owner's natural-language goal to a postcondition. Reserve realtime for the spoken verdict.
- **latency:** For local actions, verify within 2 s; browser or phone flows within 8 s. If verification is unavailable, say 'unverified' immediately rather than waiting indefinitely or claiming success.
- **cost:** Usually no additional model call and <$0.005 per request; occasional visual or semantic comparison costs $0.01-$0.03 when structured state is insufficient. Storage is a small before/after evidence capsule.
- **security:** Evidence must be minimized and redacted: retain selectors, app/tab identity, hashes and targeted fields rather than whole private pages or screenshots. Never expose authenticated page contents to the pendant or a third party. A mismatch should be reported, not silently repaired; any repair remains subject to the owner's existing maximum-access policy.
- **missing:** A goal-to-postcondition schema with typed checks for Mac, browser, and iOS; Before/after state capture attached to one action/job ID; A browser and iOS verification adapter that returns stable accessibility/DOM evidence; Receipt fields for verified, unverified, mismatch, and evidence expiry; A concise relay protocol for speaking evidence-backed success or mismatch on the pendant

### ""Put everything back the way it was before you started—including the browser, Mac settings, files, and phone—and show me exactly what you restored.""
- **useful because:** Today undo is fragmented: some Mac actions have partial undo, shell mutations are permanent, browser state is separate, and phone changes have no shared rollback. The owner needs a single temporal rewind for an agent session, especially when a long delegated task has several individually reasonable but collectively wrong changes. This is a new owner-visible guarantee, not another approval gate or job-status beacon.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** Use deterministic state snapshots and inverse operations for the ordinary path; use a cheaper reasoning model to resolve conflicts and explain anything that cannot be restored. Realtime is only for the pendant's confirmation and final explanation.
- **latency:** Capture a compact pre-state before the first mutation in under 1 s; offer a restore preview within 3 s; apply a confirmed rewind in under 15 s for local/browser state, with explicit progress for phone or large files.
- **cost:** Typically <$0.01 per session for metadata and inverse planning; storage is dominated by referenced file/browser snapshots, with content copied only when necessary. No continuous model spend is required.
- **security:** Snapshots can contain private files, authenticated URLs, and phone state. Keep them encrypted on the Mac, retain only the minimum fields needed for inversion, expire them automatically, and never send raw snapshots to the relay or pendant. Rewind must be explicit and report partial restoration honestly; destructive inverse operations need a recoverable quarantine rather than deletion.
- **missing:** A cross-surface session snapshot format covering Mac process/settings/files, browser tabs and form state, and mirrored iPhone state; A durable inverse-operation journal for arbitrary run_shell and UI actions, including preconditions and conflict detection; Browser and iOS restore adapters with a safe quarantine for files and reversible settings; A local encrypted snapshot store with retention and garbage collection; A relay protocol and pendant interaction for preview, confirmation, progress, and partial-restore explanation

### ""Use my logged-in browser to answer this, but keep the page contents on my Mac and tell the cloud only the minimum answer.""
- **useful because:** The browser has sessions nobody else can reach, while the relay is the convenient always-awake voice surface. Today the owner must either trustfully ship sensitive page text into a model path or forgo the capability. A local semantic boundary would let the system act on authenticated data without turning the relay into a copy of the owner's private browsing history.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Run extraction, filtering, and redaction on the Mac with a local model or deterministic selectors; use realtime only to clarify the question and speak the minimized result. The relay should never receive page HTML, screenshots, or raw form values.
- **latency:** Return a short answer in 3-10 s for a structured page; allow up to 30 s for local semantic extraction. If the local boundary cannot prove that sensitive content stayed local, fail closed with a useful explanation.
- **cost:** $0-$0.01 per request depending on whether a local model is available; network cost is a few hundred bytes for the task and redacted answer rather than page-sized payloads.
- **security:** Treat URLs, DOM text, screenshots, cookies, and form values as local secrets. Enforce an explicit output schema and byte/field budget, redact identifiers and secrets before relay transmission, log only hashes and provenance, and make the owner able to inspect exactly what crossed the boundary. This is data minimization, not an action approval gate.
- **missing:** A browser-side local extraction worker that can answer typed questions without exporting page content; A declarative redaction/output schema with byte, field, host, and sensitivity limits; A relay protocol carrying only a query ID, minimized result, confidence, and provenance hash; A dashboard audit view showing local inputs and the exact fields released; A local model/runtime or deterministic fallback for pages whose structure is not known

### ""While I'm in this meeting, keep a private running record of decisions and promises, then prepare the follow-ups without sending anything.""
- **useful because:** The pendant is physically present for spoken context, the Mac can see the meeting window and authenticated work tools, and the relay can turn a long session into a durable handoff. Today those surfaces cannot jointly maintain a private, time-indexed decision record and stage concrete follow-up drafts. This would prevent the owner from losing commitments while keeping external side effects unsent until they review them.
- **path:** pendant → relay → mac-bridge → browser → iOS → dashboard
- **model tier:** Use a background transcription/summarization model for the meeting, with realtime only for interruptions or a spoken query. Deterministic extraction should identify names, dates, and action items before a cheaper model drafts follow-ups.
- **latency:** Show recording/transcription state locally within 500 ms; surface a new decision or promise within 10 s; produce a structured private digest and staged drafts within 2 minutes after the meeting ends.
- **cost:** Approximately $0.05-$0.30 per hour depending on audio transcription and summarization; keep audio local and send only selected transcript spans or extracted claims to any remote model.
- **security:** Meeting audio and participant data are highly sensitive. Require an explicit start/stop indication, local encrypted storage, participant/privacy labeling, automatic expiry, and no automatic sending. Drafts must carry source timestamps and uncertainty; the owner reviews before email, calendar, or task creation.
- **missing:** A local meeting audio capture/transcription path that does not open the microphone implicitly; A time-aligned decision/promise schema with source snippets and confidence; Cross-app adapters for the meeting window, browser work tools, and phone notifications; A private draft workspace linked to calendar/mail/task actions but isolated from send/commit operations; Pendant controls for pause, mark important, and stop with unmistakable local feedback


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct owner-facing capabilities: (1) durable cross-surface delegation that survives link/Mac/browser interruptions and reports truthful terminal state; (2) a five-minute, read-only dual-chip bench health check usable today to distinguish USB presence from a functioning audio path; and (3) evidence-backed postcondition verification after Mac/browser/iPhone actions, so a successful dispatch is not mistaken for a successful outcome. I also confirmed the supposedly granted USB diagnostic tool is still unresolved against the live inventory and recorded that finding, then asked mac-planner to check for existing verification routes.

**Biggest unknown:** There is still no callable bounded serial/UART reader or host framing parser in the live inventory, so I cannot directly establish whether either physically attached chip is emitting healthy frames this round. The durable transaction and postcondition proposals also need an authoritative check against the full route/action manifest to avoid colliding with less-visible existing implementations.

