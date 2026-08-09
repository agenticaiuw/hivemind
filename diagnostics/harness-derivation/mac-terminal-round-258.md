# Harness derivation — mac-terminal — round 258

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Tell me why the thing I asked for failed, and get it unstuck if you can.”"
- **useful because:** Today a spoken request can span the pendant, relay, Mac shell, and browser, but a failure collapses into a generic failed message. This gives the owner a causal answer: which node lost contact, which exact step failed, whether it changed anything, and an automatic safe continuation when the failure is transient.
- **path:** pendant → relay → mac-planner → browser-harness → mac-bridge
- **model tier:** Realtime only for the short spoken explanation; background/repair classification uses a cheaper model and deterministic probes.
- **latency:** Initial answer under 3 seconds from cached receipts; targeted probes/repair within 30 seconds, with the pendant beacon announcing progress.
- **cost:** About $0.01–$0.04 per incident; most cost is one small realtime explanation, while probes and retry classification are local/deterministic.
- **security:** Command output and browser titles may contain secrets; send only redacted evidence capsules to relay, keep raw stdout/browser content on the Mac, and require explicit confirmation only for a repair that is not idempotent. No new restriction on the owner's full-control policy.
- **missing:** A cross-node incident record keyed by the original turn/job ID; Structured failure taxonomy and a repair planner that can distinguish retryable from already-applied effects; Pendant-facing streaming of causal evidence rather than only final status

### "“Before I leave, tell me whether the pendant, audio bridge, Mac agent, and browser are all actually ready—and tell me the one thing I need to fix.”"
- **useful because:** The owner currently has to infer readiness from unrelated health pages and cannot know whether the two USB-connected chips are producing valid frames. A single spoken readiness verdict turns the live bench hardware into a trustworthy preflight, instead of discovering a dead audio path during an important conversation.
- **path:** pendant → mac-bridge → mac-planner → browser-harness → relay
- **model tier:** Cheaper background/deterministic checks for serial counters, /health, browser heartbeat, and relay reachability; realtime only to summarize the resulting pass/fail matrix.
- **latency:** 5 seconds for the full preflight; cached last-good state may answer immediately, but must show its age.
- **cost:** Under $0.01 per check when deterministic; one short realtime response only when the owner asks for an explanation.
- **security:** Do not upload UART contents or browser page data. Return only bounded counters, firmware identity, transport state, and timestamps. USB diagnostics stay read-only and bench-only.
- **missing:** A host preflight coordinator that invokes bounded diagnostics on both fixed serial ports and correlates frame counters; A common health schema covering nRF9160, ESP32 bridge, local agent, browser extension, and relay; A stale-state rule that refuses to call an old serial heartbeat healthy

### "“Take the report from the authenticated browser session, verify it is complete and unchanged, put it in the active project, and tell me exactly where it landed.”"
- **useful because:** The browser can reach sessions the relay cannot, while the Mac can safely inspect and organize downloaded files; today the owner must manually bridge those surfaces and can mistake a partial download for a finished report. This makes the browser-to-project handoff one dependable spoken operation with source and hash provenance.
- **path:** pendant → relay → browser-harness → mac-planner → mac-bridge
- **model tier:** Cheaper deterministic workflow for browser click/download, filesystem stabilization, SHA-256, and move; realtime only for the owner-facing confirmation or ambiguity.
- **latency:** Under 10 seconds after the download finishes; wait up to 60 seconds for a changing download to stabilize, then report timeout rather than guessing.
- **cost:** Usually under $0.02; browser actions and hashing are local, with a small model call only if the page has multiple candidate reports.
- **security:** Never send report bytes to the relay or model. Keep source URL/title, destination, byte count, and SHA-256 as provenance; refuse to overwrite an existing file unless the owner explicitly names that destination.
- **missing:** A browser command that returns the completed download path and source URL; A filesystem stabilization/hash step exposed as a typed local action; An atomic browser-to-project receipt linking browser command ID, file hash, and destination

### "“I’m back at my Mac—tell me what changed in the browser, active project, and files since I last walked away, and only surface changes that affect what I should do next.”"
- **useful because:** Today context is scattered across browser tabs, project state, downloads, and Mac activity, so returning from a break requires reconstructing the situation manually. A time-bounded cross-surface delta would make the pendant a continuity device rather than a request/response button, especially when work changed while the owner was away.
- **path:** pendant → relay → mac-planner → browser-harness → mac-bridge
- **model tier:** Deterministic collectors and hashes first; a cheaper background model ranks actionable deltas. Realtime is used only for the short spoken briefing when requested.
- **latency:** Use a cached departure snapshot for an answer in under 2 seconds; a full rescan may take up to 15 seconds and must announce which surfaces were unavailable.
- **cost:** Usually $0.01 or less: local metadata/diffs dominate, with a small ranking call only when there are many changes.
- **security:** Keep file contents and authenticated page text on the Mac/browser surfaces; send only redacted change summaries and provenance. Never infer that an unchanged inaccessible surface is unchanged; say unavailable and include snapshot age.
- **missing:** A durable departure/return snapshot that joins active project identity, browser tab/session fingerprints, and selected filesystem metadata without storing sensitive contents; Browser-side change fingerprints for authenticated pages and downloads; A cross-surface delta/ranking endpoint with explicit unavailable and stale states

### "“For every important thing you just told me, let me ask ‘how do you know?’ and hear the exact source, timestamp, and whether it was observed directly or inferred.”"
- **useful because:** The owner cannot currently distinguish a live observation from stale machine context, browser text, memory, or model inference. Proof-carrying answers would make the system trustworthy in daily use: one follow-up exposes the evidence chain instead of forcing the owner to guess whether a confident sentence was actually checked.
- **path:** pendant → relay-realtime → mac-planner → browser-harness → mac-bridge
- **model tier:** Deterministic provenance collection and claim-to-evidence linking; realtime only verbalizes the selected evidence chain. No expensive model call is needed to retrieve sources.
- **latency:** Answer the provenance question in under 1 second from the claim cache; if rechecking is necessary, say so and complete within 10 seconds.
- **cost:** Near-zero incremental API cost; storage and local indexing dominate. Realtime speech is a short response only.
- **security:** Evidence may contain private filenames, URLs, or page text. Redact sensitive values in the spoken capsule, retain raw evidence locally, and enforce source-specific retention. Never fabricate a source for an inference.
- **missing:** A claim ledger shared across Mac, browser, relay, and pendant turns; A typed distinction among observed, reported-by-device, inferred, and stale evidence; A spoken claim identifier and retrieval route that survives reconnects and maps to browser provenance, job receipts, and machine snapshots


## Changes it proposed to its own stack

### `mac-harness` — Add a bounded bench-health action that opens only the four fixed USB serial paths, reads framed health/counter records for a caller-specified short interval, validates CRC and freshness, and returns structured per-chip status; keep arbitrary run_shell available unchanged for the owner's trusted full-control workflow.
- **owner gets:** They can know whether the physically connected pendant and audio bridge are alive before relying on them, instead of staring at raw UART logs or discovering failure mid-conversation.
- effort: Medium: host serial reader/framing parser, fixed-port discovery, timeout handling, and one authenticated route/action; firmware must expose a small stable health frame on both chips.  ·  risk: A stale or malformed frame could be mistaken for health; enforce age and CRC, report unknown on ambiguity, and retain raw logs only locally for debugging.
- cost: No per-call model cost; roughly 1–2 weeks engineering. No hardware cost.  ·  latency: 300 ms–3 s depending on requested read window; cached last-good status can answer instantly with age.
- security: Read-only fixed-device access; do not expose UART payloads or environment secrets to the relay.
- depends on: Stable framed health/counter messages in nRF9160 and ESP32 firmware; A real implementation behind the currently unresolved mac_usb_serial_diagnostics schema


## What it asked for

_Nothing._
## Its own summary

This round produced three new owner-facing capabilities and one stack change: cross-node causal failure recovery, a truthful full-stack readiness preflight, authenticated-browser report handoff with hash/provenance, and a bounded USB bench-health action. I also tested the granted USB diagnostic schema: it is still unresolved in the live inventory, so it cannot read either chip yet. Current discovery shows Safari and the home Mac bridge online; the cloudflare contract-test mobile is offline.

**Biggest unknown:** Whether the nRF9160 and ESP32 are emitting a stable framed health/counter protocol, and whether the orchestrator will implement the unresolved USB diagnostic action. I still need that host serial implementation plus the firmware frame contract; for the other proposals, the missing pieces are a cross-node incident record, browser download-path reporting, and true process-group termination with post-stop receipts.

