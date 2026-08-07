# Harness derivation — mac-planner — round 51

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-browser-readiness** — Live Mac agent is reachable and relay-connected, but browser extension home-chrome is offline with 3 pending commands; accessibility and screen recording are ungranted, while app automation grants are present. Browser actions have recently failed after ~45 seconds rather than failing fast.
  - evidence: GET /ops/status returned macBridgeOnline=true, browser.online=false, pendingCommands=3, accessibility.trusted=false, screenRecording.granted=false; GET /jobs returned repeated browser_navigate failures with ~45s duration and reason extension offline.

## Capabilities it proposed

### "“Close out my 2pm meeting.”"
- **useful because:** Without opening a microphone or requiring the owner to reconstruct context, the system turns the calendar event and the work already open on the Mac/browser into a durable handoff packet: event details, cited open-tab links, relevant recent mail snippets, and an editable follow-up checklist. The owner gets continuity after a meeting instead of losing decisions and links in transient tabs.
- **path:** relay-realtime identifies the current/most-recent calendar event and sends a compact job to the Mac → mac-planner reads the bounded Calendar/Mail sources and creates a dated Markdown/HTML closeout packet in the owner's chosen workspace → browser-extension contributes only explicitly open-tab titles/URLs and provenance when online; if offline, the packet records that browser capture was unavailable and queues a retry rather than pretending → pendant reads back the packet path and asks whether to leave it open; no microphone capture is used → relay stores the job state and receipt so a later pendant request can retrieve or retry the packet
- **model tier:** Background/cheap model for extraction, deduplication, and checklist drafting; realtime only for the owner's short spoken interaction and final summary.
- **latency:** Initial packet in 5–10 seconds from the command; browser retry can complete asynchronously within 2 minutes. The owner should hear a concise receipt immediately, not wait on tab capture.
- **cost:** Roughly $0.01–$0.04 per closeout, dominated by summarizing mail/tab metadata; retries should be metadata-only and cheaper. No audio transcription cost.
- **security:** Mail/calendar snippets and authenticated tab URLs may be sensitive. Keep raw content on the Mac, redact by default, store only citations and extracted checklist in the relay, and never send or modify external systems without a separate explicit request. Browser-offline state must be visible in the receipt so an incomplete packet is not mistaken for a complete one.
- **missing:** event-scoped context contract (event ID/timezone/attendees and source citations); a Mac packet writer that atomically creates the packet plus a machine-readable manifest and receipt; browser-extension endpoint for an explicit open-tab snapshot with freshness/provenance and an offline queue; relay job schema for partial completion and retry without duplicating packets; a user-configurable destination folder and retention policy

### "“I’m back at my desk—tell me only what changed since I left, and put the things I need to act on in front of me.”"
- **useful because:** Today the pendant, relay, Mac, and authenticated browser have no shared before/after baseline. The owner must remember what was open and manually compare mail, calendar, files, and tabs. A deliberate 'leave' gesture would create a private baseline; a later 'back' gesture would produce a cited delta and surface only newly actionable changes, without pretending a generic daily brief is the same thing.
- **path:** pendant records a leave/back gesture and gives a short local acknowledgement → relay stores the signed baseline lease and expiry, but not raw mail or page contents → mac-planner captures permitted Calendar/Mail metadata, selected workspace file manifests, and Mac app/session identifiers at leave and compares them at return → browser-extension captures authenticated tab identity/title/URL plus freshness when online; if offline, the result explicitly marks browser state as unknown rather than inferring no change → mac-planner opens a generated Delta dashboard or note containing before/after timestamps, citations, changed files/events/messages/tabs, and an action list; relay sends the concise summary to the pendant
- **model tier:** Cheap background model for normalization, deduplication, and prioritization; realtime only for the two brief pendant interactions. Deterministic hashes/diffs should handle most work without an LLM.
- **latency:** Leave snapshot under 2 seconds. Return acknowledgement immediately, with the delta packet in 5–15 seconds; large file or browser inventories can finish asynchronously and update the packet.
- **cost:** About $0.005–$0.03 per return, mostly model-based ranking of changed items; hashes, timestamps, and metadata diffs are local and nearly free.
- **security:** Baseline content can reveal work and personal activity. Keep raw snapshots and file names on the Mac, encrypt the relay lease, use short TTLs, redact message bodies by default, and allow the owner to choose sources and folders. Never expose browser page contents to the relay merely to compute a delta.
- **missing:** a cross-surface baseline schema with source-specific freshness and unknown states; Mac local snapshot/diff storage with retention and exclusion rules; browser tab snapshot plus an explicit offline/unknown result; a small local dashboard/note renderer for cited deltas; pendant leave/back event semantics and relay lease expiry


## Changes it proposed to its own stack

### `relay` — Add a live capability-readiness handshake and fail-fast degradation planner before browser-dependent Mac jobs. At dispatch, consult the latest browser heartbeat and permission state; if the extension is offline, immediately split the plan into runnable Mac-only steps plus a queued browser step, attach an explicit `deferred: browser_offline` receipt, and schedule one bounded retry when heartbeat returns. Do not block or ask for approval: this is observability and routing, not a policy gate. Preserve the original command and deduplicate retries by job/action ID.
- **owner gets:** A browser action currently waits roughly 45 seconds and then fails twice even though the system already knows the extension is offline. The owner would get useful partial work immediately, a truthful “browser part deferred” notice, and automatic completion later instead of repeated dead time and ambiguous failure.
- effort: Medium: relay readiness endpoint/cache, local planner branch for partial plans, browser heartbeat-triggered retry worker, and receipt/status UI changes; add integration tests for offline/online transitions and duplicate suppression.  ·  risk: A stale heartbeat could incorrectly defer a newly recovered browser or retry while the owner has changed tabs. Bound heartbeat freshness, re-check immediately before retry, and mark every deferred/completed step with timestamp and source. Recovery is to rerun the original job from its durable action IDs.
- cost: Negligible relay storage/compute; one cheap retry dispatch per deferred browser step. No model call needed for readiness routing.  ·  latency: Removes the current ~45-second timeout from the critical path; Mac-only work returns in seconds. Deferred browser completion occurs after the next healthy heartbeat.
- security: No new content leaves the Mac. Heartbeat metadata is non-content; browser actions still use existing authenticated bridge and provenance.
- depends on: browser extension heartbeat with freshness timestamp; durable per-action job/receipt IDs; partial-plan result schema understood by pendant and Mac planner


## What it asked for

_Nothing._
## Its own summary

Discovered fresh live state: relay and Mac bridge are online, but the browser extension is offline with 3 queued commands; Accessibility and Screen Recording are not granted. Existing browser jobs waste ~45 seconds before failing. I recorded two new items: an event-scoped meeting closeout packet spanning Calendar/Mail, Mac, browser, relay, and pendant; and a fail-fast capability-readiness/degradation path that performs Mac-only work immediately and retries browser steps when healthy. The latter is routing/observability, not a confirmation gate.

**Biggest unknown:** The newly granted mac_readonly_inspect and mac_read_sources tools have schemas but no implementations, so I cannot inspect actual foreground apps, tabs, directories, calendar, or mail. Implementations for those read-only surfaces—and a browser heartbeat/retry worker—are still needed for reliable end-to-end execution.

