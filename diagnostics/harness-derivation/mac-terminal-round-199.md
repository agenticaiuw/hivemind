# Harness derivation — mac-terminal — round 199

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Why did voice fail just now? Run a complete bench-to-relay diagnosis and tell me the one thing I should fix.”"
- **useful because:** Today a dead USB serial capability and fragmented health endpoints force guesswork. This produces a causal answer, not a dashboard: it correlates the nRF9160 and ESP32 UART captures, Mac agent health/jobs, relay routing, and pipeline state, then distinguishes 'pendant never emitted', 'bridge stalled', 'Mac job failed', and 'relay rejected it'. It is the highest-value capability because it turns the system's most frightening failure—silent loss of the owner's voice—into an actionable answer, and it is runnable on the physically connected bench now even though LTE registration is absent.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → faculty-perception
- **model tier:** Background/cheap model performs structured log correlation and causal ranking; realtime tier only speaks the short diagnosis if requested from the pendant.
- **latency:** Under 10 seconds for existing health and bounded log reads; up to 30 seconds when starting a fresh dual-UART capture. Never open the microphone as part of diagnosis.
- **cost:** Roughly $0.01–$0.04 per diagnosis; dominated by log/context tokens, not inference.
- **security:** UART logs and local job output may contain identifiers or command paths, so keep raw logs on the Mac and send only normalized evidence and hashes to relay. No mutation by default; a proposed repair must be separately requested. The current serial tool is unresolved, so the implementation must invoke the existing /execute run_shell capture scripts with explicit output paths and record their receipts.
- **missing:** A bounded, typed host serial reader (the granted mac_usb_serial_diagnostics schema still has no live implementation) or a hardened wrapper around /execute for diagnostics/dual_chip_autocapture.sh; A common event schema joining UART timestamps, pipeline turn IDs, job IDs, and relay routing decisions; A redacted log-correlation worker that can classify causal failure rather than merely list statuses

### "“My Mac restarted. Pick up the work that was in progress, but do not repeat anything that already happened; tell me exactly what you resumed.”"
- **useful because:** The durable ledger and job records exist, but after a restart jobs remain falsely processing, ledgers are never closed, and resume is never automatically submitted. This gives the owner a trustworthy recovery action instead of rerunning a multi-step task and duplicating mail, edits, or browser submissions. The pendant contributes the request and receives a truthful queued/resumed/blocked state; the relay coordinates while the Mac owns execution.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → browser-extension
- **model tier:** Background model reconciles records and constructs a minimal resume set; realtime model only handles the owner's spoken request and concise receipt.
- **latency:** 5 seconds to inspect and classify stale work; execution duration is task-dependent. A resumed action must not be reported complete until its Mac receipt is durable.
- **cost:** $0.005–$0.03 per recovery decision; dominated by ledger/job context. No model call is needed for a clean no-op.
- **security:** Never infer that an interrupted side effect completed. Require idempotency keys for every resumed action, preserve browser provenance, and keep raw command/env data on the Mac. If a step is non-idempotent or its pre-state is unknown, report blocked rather than guessing. The pendant must show stale/queued state, not success.
- **missing:** Boot-time reconciliation that marks processing jobs interrupted and closes the orchestrator ledger; A real jobId↔ledgerId join (planMeta.jobId is currently always null); Execution-context/idempotency wiring on /execute, with captured exit code and durable per-step checkpoints; A relay resume coordinator that submits only GET /ledger/:ledgerId/resume runnable actions and emits receipts back to the pendant

### "“Take the one item I’m looking at in my private Safari tab, turn it into a local Mac action, and give me a spoken receipt with the source.”"
- **useful because:** The browser can see authenticated state the relay cannot, while the Mac can act on local apps and the pendant is the only interface always with the owner. This bridges those otherwise isolated powers for a concrete daily task: read the selected record from a private tab, map only the requested fields into a Reminder/calendar/file action, and return the exact source URL/title plus the local result. It avoids exporting page contents to the cloud and makes the handoff auditable.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-terminal
- **model tier:** Browser/local planner handles DOM extraction and field mapping; a cheap background model validates the extracted fields and source; realtime tier speaks only the final receipt or asks one clarification.
- **latency:** 2–8 seconds for inspection and local action, with no more than one clarification turn. Keep the browser session open; do not wait on a cloud crawl.
- **cost:** $0.01–$0.05 per handoff, primarily structured-page extraction and validation; near-zero for a simple field transfer.
- **security:** Authenticated page text, cookies, and credentials remain in the extension/browser. Send to relay only the minimum selected fields, URL, title, and a short-lived provenance token. Never submit a browser form or create an external side effect without an explicit request; local reminder/file creation should retain an undo receipt and exact source.
- **missing:** A first-class browser selection/structured-extraction result (current browser inspection is page-level and capture is screenshot-oriented); A typed, provenance-carrying handoff envelope accepted by the Mac planner, with field allowlisting and expiry; A single receipt that joins browser provenance to the Mac action receipt and is readable by the pendant

### "“I’m about to walk away from the Mac. Make my current work resumable: capture the exact browser context, open files, unsaved local state, and the decision I just made, then let me continue from the pendant later.”"
- **useful because:** Today the browser, Mac planner, and pendant each know fragments of a task, but there is no owner-facing handoff artifact that preserves the *working state* rather than merely a job log. This would let the owner leave without losing the thread: a later pendant request rehydrates the right Safari session, local files/apps, and the last decision, while clearly marking anything that could not be captured. It is not a restart retry or a browser-to-reminder transfer; it is a deliberate human context handoff across surfaces.
- **path:** pendant → browser-extension → mac-planner → mac-terminal → relay-realtime → faculty-perception
- **model tier:** A cheap background model compresses the captured state into a short, local-first handoff card; realtime is used only when the owner later asks to resume it aloud.
- **latency:** Capture in under 5 seconds; rehydration in under 10 seconds, with a spoken summary before any local state is changed.
- **cost:** $0.01–$0.04 per handoff, dominated by summarizing open context. Raw page/file contents stay local and need not be sent to the expensive tier.
- **security:** The card may contain private tab titles, paths, and snippets. Encrypt it at rest on the Mac, retain only explicitly selected snippets, expire it by default, and require the owner’s explicit request before reopening a private tab or modifying files. The pendant should cache only a title, timestamp, and opaque card ID.
- **missing:** A Mac context snapshot action covering foreground app/window, selected browser tab, open local artifact identities, and unsaved-state indicators; A browser extension API that exports a redacted session locator and provenance references without cookies or page credentials; A durable, encrypted handoff-card store shared by relay and Mac, with expiry and conflict handling; A rehydration planner that can report partial restoration honestly instead of pretending the prior context was recovered

### "“I’m leaving the desk—secure this session now, keep only what I explicitly need, and tell me what you changed when I’m away.”"
- **useful because:** A wearable is the one surface that can express the owner’s physical intent while the Mac and browser hold the sensitive state. This would atomically mute or stop local capture, hide/lock selected private browser tabs, pause queued Mac mutations, and leave a concise offline receipt on the pendant; on return, it reports what was actually secured and what could not be changed. It is a physical, immediate privacy boundary that no Mac-only planner can infer reliably.
- **path:** pendant → mac-planner → mac-terminal → browser-extension → relay-realtime
- **model tier:** Deterministic local action plan with a cheap model only for selecting the owner’s saved security profile; realtime speaks the short result if the link is available.
- **latency:** Begin within 500 ms of the pendant event; complete or report each action within 5 seconds. Offline pendant state must still truthfully show queued versus applied.
- **cost:** Near-zero for the normal path; at most $0.005 for profile interpretation. The work is local Mac/browser control, not model generation.
- **security:** This is a high-impact local privacy action, so profiles must be explicit and previewable, never inferred from page text. Keep credentials and raw tab data local; use idempotent actions and an append-only receipt. If the link is down, the pendant must not claim the Mac was secured.
- **missing:** A dedicated second-button or firmware event for 'secure retreat' that does not interfere with the active-edge conversation button; A Mac/browser atomic action bundle with pre-state capture and truthful per-action completion; A local presence/link-loss policy that distinguishes an intentional retreat from a dropped USB/LTE link; A pendant-readable compact receipt for partial completion and later reconciliation

### "“Check whether the private page I’m viewing agrees with the local file and calendar entry I’m working from, and tell me exactly where they disagree.”"
- **useful because:** The browser has authenticated truth, while the Mac has local documents and calendar context; today neither can perform a provenance-preserving cross-source consistency check. This catches stale amounts, dates, and names before the owner sends or commits something, and it gives a useful answer even when no action should be taken. The pendant makes the request hands-free and receives a compact discrepancy list with links back to each source.
- **path:** pendant → browser-extension → mac-planner → mac-terminal → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** Cheap background model extracts typed claims and compares them; faculty-judgement ranks discrepancies by consequence. Realtime speaks only the short list and asks for clarification if the sources are ambiguous.
- **latency:** Under 12 seconds for one page plus up to three local sources; no writes unless the owner separately asks to reconcile.
- **cost:** $0.02–$0.08, dominated by structured extraction from private-page and local-document context. Raw artifacts remain on the Mac/browser whenever possible.
- **security:** Never upload full authenticated pages or documents. Extract only requested fields, source URL/path, timestamps, and claim hashes; preserve provenance locally. Treat disagreement as uncertainty, not permission to edit either source. Expire extracted claims and redact secrets.
- **missing:** A typed claim-extraction contract shared by browser and Mac readers, including units, dates, entity identity, and confidence; A local comparison engine that can align claims across HTML, files, and calendar records without sending raw content to relay; A provenance-aware discrepancy receipt consumable by the pendant and traceable back to each source; A spoken disambiguation flow for two records that appear to refer to different entities


## Changes it proposed to its own stack

### `mac-harness` — Implement a bounded bench-only dual-UART diagnostic runner in the Mac agent. It should discover only the two known USB device classes, open each at 115200, read a caller-specified byte/time budget, parse the project's existing diagnostic frame markers, and return per-port presence, bytes, timestamps, CRC/frame counts, and explicit termination reason. Store raw output locally with a hash and join the diagnostic receipt to the /execute job. Do not expose USB as a wearable transport.
- **owner gets:** The chips are physically connected today, but the newly granted serial tool still resolves to nothing. The owner cannot tell whether a failed voice test is firmware, cable, bridge, or relay without manually running scripts. This makes the bench truthful and usable now while preserving the product boundary that USB is only for flashing/testing.
- effort: Medium: a small host reader plus framing parser, route/action registration, tests for disconnect, timeout, partial frame, and oversized output.  ·  risk: A buggy parser could mislabel a healthy frame or hold a serial device open. Enforce hard read/byte limits, close descriptors in finally blocks, and keep the existing shell-script fallback. No LTE or production path depends on it.
- cost: No meaningful API cost; approximately 1–2 engineering days. Negligible Mac CPU/power during a short test.  ·  latency: Presence result in under 1 second; bounded capture up to the requested read window.
- security: Allowlist the two USB paths/classes, never return raw environment variables or unrestricted filesystem data, and retain raw logs only locally with a content hash.
- depends on: A live Mac-agent route/action registration (the current inventory has no serial capability); A documented frame format or parser shared with firmware diagnostics; The existing /execute job and receipt schema for provenance


## What it asked for

_Nothing._
## Its own summary

Produced three owner-facing cross-node capabilities and one concrete Mac-harness change. The strongest is a spoken causal voice-path diagnosis using the physically connected nRF9160/ESP32 bench plus relay/Mac pipeline evidence. I also specified exactly-once restart recovery and a private Safari-to-local-Mac action handoff with provenance. The USB diagnostic runner is still not callable: the granted schema resolves to no live inventory capability, so the existing dual-UART capture scripts remain the fallback until a Mac-agent action/route is implemented. I told mac-planner this explicitly.

**Biggest unknown:** The actual UART framing emitted by the live firmware and whether the existing capture scripts produce parseable health/counter frames; the serial tool cannot establish this because no implementation exists in the live capability inventory.

