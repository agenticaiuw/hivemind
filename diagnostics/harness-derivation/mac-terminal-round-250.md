# Harness derivation — mac-terminal — round 250

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live_tool_resolution_round250** — The granted mac_usb_serial_diagnostics and mac_read_diagnostics schemas still do not resolve against live inventory; serial inspection has no implementation, and bundled Mac diagnostics currently score below resolver threshold. Safari and home-macbook-bridge are online, but hardware chips cannot be queried through a dedicated tool this round.
  - evidence: mac_usb_serial_diagnostics returned unresolved (best action:get_mac_status 0.226); mac_read_diagnostics returned unresolved (best GET /health 0.443). discover(devices) reported Safari online and home-macbook-bridge online.

## Capabilities it proposed

### "When I press the pendant button during something I'm doing, freeze the exact task, capture what the Mac and authenticated browser were showing, and let me say 'continue that' later from the pendant without starting over."
- **useful because:** This is the core hive advantage: the worn device can interrupt at the moment intent changes, the Mac can preserve local application state, the browser can preserve an authenticated session that the relay cannot reach, and the relay can keep a durable checkpoint while every surface is disconnected. Today an interrupted browser or shell workflow usually becomes a vague reminder rather than a resumable task.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Use the cheap planner for checkpoint extraction and deterministic resume; reserve realtime only for the short spoken command and final status. No background frontier model is needed.
- **latency:** Button acknowledgement and local checkpoint enqueue under 300 ms; Mac/browser checkpoint under 3 s; spoken resume decision under 2 s. Long-running work continues asynchronously.
- **cost:** About $0.01–$0.05 per checkpoint/resume depending on planner calls; storage and browser screenshot bytes dominate, so prefer structured tab metadata and small state capsules over screenshots.
- **security:** Authenticated browser URLs, foreground app names, and task text leave the Mac only as encrypted/minimized metadata; never copy page bodies by default. Resume must bind to the original browser session and reject a changed origin or stale action plan; local destructive actions remain subject to the owner's existing maximum-access policy and should be visibly reported.
- **missing:** A checkpoint protocol joining pendant event sequence, Mac jobId, browser commandId, and relay taskId; A Mac hook that snapshots active app/window and local-agent execution context on the existing sw1 marker; Browser-session checkpoint/restore with origin and tab identity validation; A resumable executor that uses ledger step state and records whether each step was actually completed

### "Why did you tell me that? Give me the exact browser page, Mac command or file, and the moment I asked that you relied on—then let me open the evidence on the Mac."
- **useful because:** The hive can currently act across surfaces, but its explanations are not a portable proof. This makes trust tangible: the pendant supplies the originating turn, the browser supplies authenticated page provenance, and the Mac supplies command/file receipts. The owner gets a short spoken answer plus an inspectable evidence bundle rather than an unsupported assertion.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use a cheap provenance joiner and deterministic evidence ranking; use realtime only to summarize the top two sources aloud. No expensive model is needed unless sources conflict.
- **latency:** Spoken source list within 2 s for recent work; bundle materializes within 5 s. Opening a source on Mac should be one action.
- **cost:** <$0.01 for joins and hashing; up to $0.03 for conflict summarization. Storage is small JSON capsules and hashes, not copied page contents.
- **security:** Do not export authenticated page bodies, secrets, or shell environment. Keep source URLs and redacted snippets local to the browser/Mac where possible; relay stores hashes, timestamps, origin, and claim IDs. Opening evidence must preserve the browser session and mark whether a source is still live or only a historical snapshot.
- **missing:** A common evidence schema linking voice turn ID, browser provenance record, Mac action receipt, and file hash; A relay query that traces a spoken claim across browser and Mac stores with freshness/conflict status; Dashboard evidence viewer and one-step Mac open action; Pendant response format for concise citation plus 'open it' follow-up

### "Is my pendant and audio bridge healthy right now? Run a bounded bench check on both USB devices, correlate their counters and timing, and tell me whether recording and playback are trustworthy."
- **useful because:** The chips are physically connected today, but the system cannot answer the most basic practical question: whether the wearable path is healthy before the owner relies on it. A single spoken check would exercise both nRF9160 and ESP32 logs, detect missing/stalled frames or clock drift, and report a concrete pass/fail instead of asking the owner to inspect raw UART files.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Use deterministic shell scripts and a small parser for framing, counters, CRC, and timing; use the realtime model only to turn the structured result into a short spoken explanation. No browser or frontier reasoning is required.
- **latency:** Start acknowledgement under 300 ms; capture for 5–10 s; summary within 2 s after capture. It must be read-only and bounded.
- **cost:** Negligible model cost (<$0.01); local CPU and a few kilobytes of timestamped UART logs dominate.
- **security:** Read-only USB access only, fixed known ports or the existing autodiscovery scripts, bounded bytes/time, and no LTE claim. Keep logs local by default; relay receives only aggregate health and a short failure excerpt. Never say wearable/LTE is healthy when this is only a USB bench result.
- **missing:** A real host serial reader/framing parser or a safe typed wrapper around the existing dual-chip capture scripts; A health contract for nRF9160 and ESP32 counters, CRCs, timestamps, and audio latency; A Mac action that returns structured exit code and bounded parsed output rather than opaque shell text; A dashboard history of bench checks and a clear USB-bench-versus-wearable status label

### "Before I wear a new firmware build, certify it: flash the pendant and audio bridge, run the exact record/playback and button/link tests, compare the measured results with the last known-good build, and give me a signed 'safe to wear' report with the failures and rollback path."
- **useful because:** Today the owner can flash components and inspect logs, but cannot know whether a build is wearable-ready as one coherent system. This joins the Mac's flashing and test control, both chips' USB telemetry, the relay's protocol expectations, and the pendant's real button/audio path into a release decision that is meaningful to the person who will wear it—not merely a successful compile.
- **path:** mac-planner → pendant → relay-realtime → dashboard
- **model tier:** Deterministic test runner and result comparator do nearly all work; use a cheap model to summarize regressions and realtime only for the final spoken verdict. Do not spend the expensive tier on raw UART logs.
- **latency:** Flash and qualification may take 2–5 minutes; provide immediate stage progress on the pendant and a final report within 10 seconds of the last test. A failed stage must stop and preserve logs for diagnosis.
- **cost:** Under $0.05 in model calls; local USB I/O and retaining two bounded test traces dominate. Keep full traces on the Mac and send only hashes, metrics, and failures to the relay.
- **security:** Require an explicit owner command to flash because it changes firmware, but do not add a general execution gate. Verify image hashes, board identities, and signed test manifests; never label a USB bench result as LTE-qualified. Store rollback image metadata locally and report exactly which build was tested.
- **missing:** A typed firmware-flash and dual-board test runner with board identity and image-hash capture; A shared qualification manifest defining button edge, audio frame, CRC, latency, reconnect, and power-fail tests; A structured UART parser and baseline/regression store for both chips; A signed report format understood by relay and dashboard, with rollback image references; A Mac/pendant progress channel that distinguishes flashing, testing, failed, and certified states

### "Show me the before-and-after of a cross-device task: record the Mac app, browser session, relay job, and pendant state before you act, do the work, then tell me exactly what changed and what stayed untouched."
- **useful because:** The owner currently gets per-action results, not a single world-level delta. This would make a multi-surface request legible: which browser fields were filled, which local files changed, which relay records were created, and whether the pendant actually acknowledged the result. It is especially valuable when a long task partially succeeds.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Use deterministic snapshots, hashes, and action receipts for the diff; use the cheap model only to group changes into owner language. Realtime speaks a compact summary, with the dashboard holding detail.
- **latency:** Capture baseline under 1 s; do not delay dispatch for expensive analysis; produce the first delta immediately on completion and finalize any asynchronous browser/Mac observations within 5 s.
- **cost:** Usually <$0.02, dominated by local snapshot storage and browser structured state. Avoid screenshots and page bodies unless a visual diff is explicitly requested.
- **security:** Hash or redact secrets, cookies, tokens, and page content. Scope snapshots to the task's touched apps, tabs, paths, and relay records; preserve the existing maximum-access execution policy. Mark unknown state explicitly rather than claiming unchanged.
- **missing:** A cross-surface snapshot schema with scope, timestamp, freshness, and redaction rules; Mac file/app/window and relay record snapshot adapters; Browser structured-state snapshot and post-action diff adapter; A durable correlation ID joining pendant turn, job, browser command, and receipts; Dashboard and spoken rendering for changed/unchanged/unknown results


## What it asked for

_Nothing._
## Its own summary

Round 250 produced three non-duplicate capabilities: (1) a cross-surface pause/resume checkpoint that lets a pendant button freeze Mac plus authenticated-browser work and resume later, (2) a portable evidence/provenance answer that traces spoken claims to browser records, Mac receipts, files, and the initiating moment, and (3) a bounded dual-chip USB bench-health command that correlates nRF9160 and ESP32 counters/timing before the owner trusts recording or playback. I also verified the Mac bridge and Safari are online. The previously granted serial diagnostic tool still has no live implementation, and the bundled Mac diagnostics schema also failed live resolution this round. One shell self-healing proposal was correctly rejected as an existing backlog item rather than rephrased.

**Biggest unknown:** The actual USB serial frame format, enumeration state, and health counters of the two connected chips. Existing capture scripts are present, but no resolved typed serial reader/parser can inspect them, so I cannot honestly report hardware health yet. What I still need is implementation of a bounded read-only serial capability (or a structured wrapper around the existing capture scripts), plus the nRF/ESP health contract.

