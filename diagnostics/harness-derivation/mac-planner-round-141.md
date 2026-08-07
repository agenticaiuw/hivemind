# Harness derivation — mac-planner — round 141

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge recovery** — AI Pendant Browser Bridge app opens successfully, but status cannot be checked because computer_use_task is disabled (PENDANT_COMPUTER_USE_ENABLED=1 required); /browser/status still reports online=false with 12 pending commands. No pending browser command was replayed.
  - evidence: POST /execute at 2026-08-07T14:57:13Z: open_app success; computer_use_task failed disabled; GET /browser/status 200 online=false pendingCommands=12.

## Capabilities it proposed

### "If I ask you to do something on a logged-in website while my browser is disconnected, park the request, reconnect the bridge, and continue exactly once when it is safe—then tell me what ran, what was skipped, and why. Never blindly replay the 12 commands already waiting."
- **useful because:** Today the Mac bridge is online but the browser is offline with 12 pending commands, leaving the owner unable to know whether a request is lost, delayed, or about to be duplicated. This makes the pendant/relay, Mac, and private browser act as one reliable system without risking stale or duplicate clicks.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the cheap background model for queue classification and retry/reconciliation; use realtime only to acknowledge the owner and report completion. Use the Mac planner for launching/observing the bridge, and the browser harness for authenticated-page work.
- **latency:** Immediate spoken acknowledgment under 1 second; reconnect polling every 5–10 seconds while the Mac is awake; resume within roughly 30 seconds after a verified heartbeat. No work should be lost across a relay or Mac restart.
- **cost:** Low: mostly D1/R2 state transitions and heartbeat polling. One model call only when reconciling an ambiguous result or summarizing evidence; browser minutes dominate public-page fallback, which must not be used for private sessions.
- **security:** Private URLs, tab IDs, and extracted content stay on the authenticated Safari bridge and relay only receives typed status/evidence. The bridge must quarantine existing pending commands, assign request/action idempotency keys, verify tab/session affinity and a fresh heartbeat, and classify each result as not-started, started/unknown, succeeded, or skipped. No automatic replay of an unknown mutation; preserve the receipt for the owner. No approval gate is added—the owner policy is maximum access—but destructive actions still need explicit intent at the originating request.
- **missing:** A durable offline intent state machine spanning relay, Mac bridge, and browser (parked, bridge_requested, heartbeat_verified, running, unknown, completed, skipped).; A bridge recovery endpoint/heartbeat that can report queue age and quarantine or inspect pending commands without executing them.; Resumable progress events and polling instead of the current single 45-second browser wait.; A durable result stream and Mac job receipt that links the pendant utterance to browser action receipts.

### "When the pendant's UART or audio pipeline starts failing, file a compact bug report automatically: capture the fault window, device counters and firmware version locally, send it when the link returns, put a redacted report and reproduction hint in ~/AI-Pendant-Workspace, and tell me one short sentence—without recording microphone content."
- **useful because:** The owner explicitly wants a pendant that files its own UART bug reports. It turns intermittent wearable failures into actionable evidence instead of asking the owner to reproduce a glitch or remember when it happened. The pendant, relay, and Mac each contribute something no one node can do alone.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Firmware should detect and compress structured faults deterministically. Use a cheap background model on the relay to cluster recurring signatures and write a one-line reproduction hint; realtime is only for the spoken alert. The Mac planner writes the report file and can optionally open it in the editor.
- **latency:** Local fault snapshot in under 100 ms; upload opportunistically within 2 minutes of link recovery; Mac report within 10 seconds after receipt. Never block audio or button handling on report generation.
- **cost:** Negligible model cost for ordinary reports; occasional small summarization call. Network cost is a few KB per incident. Flash/RAM cost is bounded by a ring buffer and fixed-size CBOR records.
- **security:** No microphone PCM, transcript, credentials, or raw UART payload if it may contain secrets. Store only timestamps, error codes, counters, firmware/build ID, radio state, and hashes of bounded diagnostic lines. Redact device identifiers in the Mac copy; retain a local unsent queue with explicit expiry. Alert should say a report was filed, not expose sensitive data.
- **missing:** A firmware diagnostic ring buffer and fault-trigger event with a bounded schema and local expiry.; An authenticated relay ingestion route with deduplication, upload receipts, and backoff when LTE/BLE is unavailable.; A Mac job that receives a typed diagnostic bundle, writes a redacted Markdown/JSON report under ~/AI-Pendant-Workspace/bug-reports, and returns a receipt.; A dashboard view for recurring signatures, firmware versions, and report delivery state.

### "When I say “watch this deadline” about the logged-in page I’m viewing, extract the date, obligation, and source evidence, create a local calendar reminder with a link back to that exact tab, and alert me through the pendant at a sensible lead time. If the page changes or the deadline disappears, tell me instead of silently keeping a stale reminder."
- **useful because:** A date buried in a private portal, order page, reservation, or form is easy to forget. Today the browser, Mac Calendar, relay, and pendant do not share a provenance-linked deadline object, so reminders either require manual copying or become stale without warning.
- **path:** pendant → browser → relay → mac-bridge → dashboard
- **model tier:** Use a cheap background model for date/obligation extraction and confidence scoring; use deterministic Calendar APIs for reminder creation and update. Realtime is only for the owner’s short acknowledgment or a genuinely urgent change.
- **latency:** Parse and show a proposed date in under 5 seconds; create the reminder within 15 seconds after the owner’s utterance. Re-check only at the page’s relevant cadence, not by wasteful polling. Urgent changes should reach the pendant within 1 minute of detection.
- **cost:** Low: one extraction call per request and small periodic checks. Calendar writes and typed page metadata dominate no API cost; page content remains on the private browser path.
- **security:** Keep page text and credentials on the authenticated browser bridge; send the relay only the minimum obligation, date, confidence, source URL, and evidence hash. Never infer a date with low confidence into a reminder without surfacing uncertainty. Calendar creation is a local mutation and should include an undo-linked receipt. Do not expose private page content in spoken alerts.
- **missing:** A provenance-linked deadline object shared between browser evidence, relay schedules, Calendar, and pendant notifications.; A date/obligation extractor that understands page semantics and reports confidence plus the exact supporting passage.; A change detector that distinguishes a moved deadline, completed obligation, and page disappearance.; A Calendar adapter that can update or retract the reminder while preserving the source tab link and receipt.


## What it asked for

_Nothing._
