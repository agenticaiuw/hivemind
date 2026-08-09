# Harness derivation — mac-planner — round 241

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “lock down,” make my whole AI workspace private: latch privacy on the pendant, stop any Mac/browser capture or playback, and report which surfaces actually acknowledged it."
- **useful because:** The existing pendant privacy latch protects the pendant alone; this gives the owner one physical, reliable escape hatch for the entire hive, including an authenticated browser session and Mac automations that may otherwise keep running.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Realtime for the short command and acknowledgement fan-out; no background model needed. The relay should use a deterministic event/state machine, not an LLM, to avoid interpreting privacy state.
- **latency:** Local pendant mute immediately; relay fan-out and acknowledgements within 2 seconds. If Mac/browser are unreachable, the pendant must still remain private and the spoken result must say which nodes are unconfirmed.
- **cost:** <$0.01 per invocation; dominated by one short realtime turn and a few event receipts, not generation.
- **security:** The event must contain no audio or page contents. Mac policy must define what lockdown means (pause capture/playback, cancel queued browser commands, optionally close sensitive tabs) and be owner-configurable. Never claim success from intent delivery; require per-surface acknowledgements and expire stale lockdown state safely.
- **missing:** A relay privacy-state fan-out route carrying a monotonic epoch and acknowledgement deadline; Mac action to cancel/pause in-flight jobs and browser command queues without deleting user data; Browser extension handler that refuses new commands while the epoch is latched; A durable cross-surface privacy acknowledgement receipt

### "What did I actually do during the last hour? Give me a short timeline grounded in my pendant bookmarks, Mac actions, browser pages, and calendar, and mark anything that is only inferred."
- **useful because:** The hive currently produces separate receipts and bookmarks but the owner cannot ask for a trustworthy reconstruction after an interruption or forgotten decision. A provenance-labelled timeline is useful precisely because no single node sees all four streams.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Cheap background model summarizes already-collected structured events; deterministic correlation and provenance labels happen before generation. Use realtime only when answering live.
- **latency:** Under 5 seconds for a one-hour window; bounded to 100 events and a 15-minute fallback if sources are unavailable.
- **cost:** <$0.02 per request; dominated by summarization of event metadata, with no audio transcription unless the owner asks.
- **security:** Default to metadata and page titles, never page bodies, message contents, or raw audio. Redact secrets and mark missing sources explicitly. Browser history and calendar are sensitive, so scope by an explicit time window and do not persist the assembled timeline unless requested.
- **missing:** A relay event schema that accepts signed timestamped bookmarks plus Mac and browser receipts in one ordered stream; A read-only endpoint to query the merged event stream by time range and source; Browser extension emission of page-title/URL transition events with redaction controls; Mac receipt records that include the actual target resource and completion timestamp

### "Before you submit the form I’m looking at, read me exactly what will be sent, which account and site it targets, and any high-risk fields; submit only after I press the pendant button."
- **useful because:** Authenticated browser sessions hold actions the Mac and relay cannot safely inspect alone. This creates a human-verifiable handoff: browser extracts a redacted structured preview, the relay speaks it through the pendant, and a physical confirmation authorizes the final browser click rather than trusting an opaque plan.
- **path:** browser-extension → relay → pendant → mac-planner
- **model tier:** Deterministic browser extraction and field classification first; cheap model compresses the preview into one spoken sentence. Realtime handles the spoken confirmation only; no model should invent or rewrite field values.
- **latency:** Preview in 2 seconds, spoken summary in 3 seconds, and submission within 2 seconds of the physical confirmation. Expire the preview after 60 seconds or any page/form mutation.
- **cost:** <$0.02; one short realtime turn plus browser inspection, with no page-body persistence.
- **security:** Never send passwords, payment card numbers, tokens, or full sensitive field values to the relay; classify and redact them locally, saying only field type and last-four when appropriate. Bind confirmation to URL, origin, form hash, account identity, and exact field hash. Any change invalidates it. Default to preview-only if the browser extension cannot attest the origin.
- **missing:** Browser-side structured form inspection with local redaction and origin/account attestation; A relay confirmation state bound to a form hash and a one-time pendant button event; A browser submit primitive that accepts only an unexpired attested confirmation, not a free-form click; A spoken preview renderer that can say risk categories without leaking values

### "After a failed pendant diagnostic, file a reproducible bug report automatically: include the measured counters, firmware/build identity, exact test fixture, and a redacted serial excerpt, then open the report in VS Code for me."
- **useful because:** The owner explicitly wanted a pendant that files its own bug reports. The hardware fixture can now produce objective measurements, while the Mac is the only place that can persist and open a useful report. This closes the loop from a physical failure to an actionable issue without uploading microphone data.
- **path:** pendant → mac-planner → relay
- **model tier:** Deterministic report generation from fixture JSON; a cheap model may write a one-paragraph summary, but must not alter measurements or invent reproduction steps.
- **latency:** Report staged within 5 seconds after a failed fixture; VS Code opens only after the atomic write succeeds.
- **cost:** <$0.01 per failure; local file transaction dominates, with optional short summarization.
- **security:** Store only synthetic diagnostic data and redacted serial lines. Use an allowlisted workspace path, atomic staging, and a stable failure ID to deduplicate retries. Never auto-submit to an external tracker; opening/editing locally is safe and the owner decides what leaves the Mac.
- **missing:** A machine-readable diagnostic fixture receipt with firmware hash, fixture version, counters, and failure thresholds; A redaction/parser layer for serial output; A deterministic report template and stable deduplication key; A policy entry allowing creation/opening of local reports while external submission remains disabled

### "Tell me which account is currently signed in on the page I’m looking at, and prove it from the site’s own identity UI without exposing the account identifier to the model or storing page contents."
- **useful because:** An authenticated browser session is a distinct security principal that the relay and Mac cannot safely infer. The owner should be able to ask who they are about to act as before an important workflow, without leaking the account name or page body into conversation context.
- **path:** browser-extension → relay → pendant
- **model tier:** Browser-side deterministic extraction and redaction; realtime only speaks a coarse result such as “your work account” or “an unrecognized account.” No model should infer identity from page text.
- **latency:** Under 2 seconds; fail closed when the origin or identity indicator cannot be verified.
- **cost:** Under $0.01, mostly an extension inspection and one short spoken response.
- **security:** Use origin-bound attestation and an allowlisted identity-indicator selector. Never transmit full email addresses, cookies, tokens, or page bodies. Treat an unknown or conflicting identity as a hard warning, not a guess.
- **missing:** Browser extension identity-indicator extraction with origin attestation; A relay route for redacted identity assertions and freshness timestamps; A pendant response format for verified, unknown, and conflicting identity states

### "If my Mac reboots or the pendant link drops while I’m in the middle of a task, tell me exactly what was completed, what was not attempted, and what can safely resume—without repeating a completed side effect."
- **useful because:** The owner should not have to remember whether an interrupted action sent, saved, or only staged something. A cross-node outcome ledger can distinguish committed browser/Mac effects from plans and make recovery safe, which individual job status screens cannot provide.
- **path:** relay → mac-planner → browser-extension → pendant
- **model tier:** Deterministic idempotency and receipt reconciliation; a cheap model formats the bounded result into one sentence. Realtime is unnecessary except for a live spoken query.
- **latency:** Reconcile within 5 seconds of reconnect and answer within 3 seconds. Never retry an unknown side effect automatically.
- **cost:** Under $0.02; mostly receipt reconciliation and a short summary.
- **security:** Receipts must contain resource hashes and outcome metadata, not page bodies or secrets. Unknown outcomes must be reported as unknown. Resume tokens must be single-use, scoped to the original resource and expiry, and never treated as permission to repeat destructive actions.
- **missing:** A shared idempotency key and outcome schema across Mac jobs and browser commands; A reconnect reconciliation worker that queries both receipt streams; A durable owner-visible distinction between committed, staged, failed, and unknown effects; Pendant notification for unresolved outcomes


## Changes it proposed to its own stack

### `hardware` — Add a real battery fuel-gauge IC (for example MAX17048-class I2C gauge) and a charge-status input to the next pendant revision, with firmware publishing calibrated percentage, voltage, estimated runtime, and charging state to the relay and Mac bench diagnostics.
- **owner gets:** The owner already asks for battery percentage, but the present pendant has no fuel gauge or charging sensor, so the system cannot answer honestly or warn before a call dies. This would make the wearable dependable rather than merely connected.
- effort: Board revision, I2C/power integration, calibration across the cell, firmware driver and relay schema; medium hardware/firmware effort.  ·  risk: Incorrect calibration could give false confidence; mitigate with voltage/percentage uncertainty and low-battery fail-safe warnings. Validate across temperature and charge cycles before enabling automatic claims.
- cost: Roughly $2–5 BOM increase plus PCB area; gauge draw typically tens of microamps, negligible beside LTE/audio peaks.  ·  latency: Battery reads in milliseconds locally; no meaningful call latency impact.
- security: Battery telemetry is low sensitivity, but expose only coarse state by default and do not include location or call content.
- depends on: A pendant revision with accessible battery/I2C wiring and charge-state net; Firmware battery telemetry frame and relay/Mac status route; Calibration and acceptance tests

### `hardware` — Add a physically separate, normally-open microphone power-cut switch on the next pendant revision, with a mechanically obvious state and a GPIO sense line; firmware should report the switch state and refuse capture until power is deliberately restored.
- **owner gets:** The current software privacy latch is useful but cannot prove that the microphone circuit is electrically dead. A real kill switch gives the owner certainty during sensitive conversations and remains effective through firmware crashes, a relay outage, or a compromised Mac.
- effort: New enclosure/control placement, microphone power-domain design, GPIO sensing, boot-time safety default, and validation that switching cannot damage the audio codec; medium hardware and firmware effort.  ·  risk: A bouncing or accidental switch could interrupt a call; debounce and explicit state reporting mitigate this. The design must fail safe on reset and avoid leaving the microphone powered while the UI says off.
- cost: Roughly $0.50–$2 in switch, FET/load-switch, protection, and PCB changes; negligible steady-state draw, with a few microamps of sense leakage.  ·  latency: Immediate local cutoff; reconnect requires codec reinitialization and may add 100–300 ms before capture resumes.
- security: Strongly improves privacy by creating a boundary independent of server, model, Mac, and relay. Report only on/off state; never expose raw audio or switch timing beyond what the owner requests.
- depends on: Next pendant PCB/enclosure revision with a separate microphone power domain; Firmware boot and privacy-state integration; Relay/Mac UI that distinguishes electrically off from software-muted


## What it asked for

_Nothing._
## Its own summary

This round I added three owner-facing capabilities: (1) a provenance-labelled cross-node activity timeline (pendant bookmarks + Mac receipts + browser transitions + calendar), (2) a browser form preview whose origin/form hash is bound to a deliberate pendant confirmation, and (3) automatic local bug-report filing from failed pendant diagnostics, with redacted measurements and VS Code opening. I also proposed adding a real battery fuel gauge and charge-status input to the next pendant revision, because the owner asks for battery percentage and the current board cannot measure it honestly. A whole-workspace privacy fan-out was recorded but flagged as close to existing work; I will not keep rephrasing it.

**Biggest unknown:** The new grants are present as the five Mac tools and four settled device skills, but the missing cross-node pieces are still unimplemented: merged event query, browser structured-form attestation, diagnostic receipt/parser, and battery telemetry. I still need a live inventory/implementation decision for mac_workbench_transaction and the browser inspection schema before claiming any of these are reachable today.

