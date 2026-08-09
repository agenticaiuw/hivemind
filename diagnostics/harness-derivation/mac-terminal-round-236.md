# Harness derivation — mac-terminal — round 236

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Run a five-minute health check on the pendant and audio bridge, and tell me exactly whether either one is healthy.""
- **useful because:** The chips are physically present today but the system cannot yet turn their UART evidence into an owner-readable verdict. This would catch stale firmware, framing loss, clock drift, bridge underruns, and a dead cable before the owner relies on the wearable. It is the single most useful commissioning capability because it closes the gap between 'USB device exists' and 'voice system is trustworthy.'
- **path:** pendant → relay → mac-planner → mac-terminal
- **model tier:** background for parsing and trend comparison; realtime only to speak the final short verdict
- **latency:** Start within 2 seconds; bounded capture for 5 minutes; final verdict within 10 seconds of capture end
- **cost:** Low API cost: one background parse and a short realtime response; Mac cost is two bounded UART readers and local parsing, not model tokens
- **security:** Read-only bench diagnostics only; never transmit raw audio or environment variables. Store counters and firmware/build identifiers, not UART text by default. Require explicit owner request because serial logs can contain paths or debug payloads.
- **missing:** A real serial-port reader/parser on the Mac (the granted serial tool is still unresolved in the live inventory); A stable diagnostic frame contract emitted by both firmwares; A relay endpoint to persist a signed health receipt and compare it with the previous run

### ""My Mac is about to sleep. Save enough context that when I wake it, you can tell me what I was doing and what changed while it was asleep.""
- **useful because:** A laptop sleep currently severs the machine that can see the owner's files and logged-in browser while the pendant remains present. A compact, time-bounded handoff lets the owner continue by voice instead of reconstructing the last task. It is deliberately a snapshot, not an always-on recording: foreground app, active project/session, active browser tab title/host, running job IDs, and pending action receipts, plus a wake-time delta.
- **path:** mac-planner → browser-extension → relay → pendant → unified
- **model tier:** Background model creates and compares compact handoff packets; realtime model only answers the wake question.
- **latency:** Snapshot in under 1 second on sleep notification; wake delta in under 3 seconds; no polling more often than once per minute.
- **cost:** Very low: structured metadata and one small background summary, with no audio or page-body upload.
- **security:** Never save page text, screenshots, cookies, or file contents. Hostnames and app names are sensitive; encrypt the packet at rest, expire it after 24 hours, and let the owner say 'forget the last handoff.' Browser session identifiers stay on the Mac.
- **missing:** Reliable Mac sleep/wake notifications surfaced to the local agent; A compact encrypted handoff record with TTL and explicit provenance; A browser-extension query for current tab metadata that excludes page content; A relay push path and pendant utterance/cache path for the wake-time answer

### ""Why did you say that, and what did you actually use to decide?""
- **useful because:** A wearable answer can sound certain while its underlying browser page, Mac command, or cached state has changed. This gives the owner an evidence capsule on demand: the claim, source page or command receipt, timestamp, freshness, and whether the source was observed directly or inherited from memory. It turns trust from a promise into something inspectable without reading a huge transcript aloud.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → unified
- **model tier:** Background model assembles and ranks evidence; realtime model compresses it into a spoken answer and offers one deeper level only if asked.
- **latency:** First spoken explanation within 2 seconds; source URLs/titles and timestamps streamed afterward; no page reload unless explicitly requested.
- **cost:** Low: mostly existing structured provenance and receipts; model cost is a short evidence-ranking pass.
- **security:** Do not speak secrets, cookie values, full command strings, or raw page text. Redact credentials and filesystem paths, show only host/title and a safe command label by default. Require explicit confirmation before opening a source in the browser or replaying a command.
- **missing:** A unified evidence-link schema joining browser provenance records, Mac action receipts, memory findings, and relay utterance IDs; A redaction layer for shell command/output and browser claims before pendant speech; A pendant query/scroll interaction for 'source one/source two' when multiple claims support an answer

### ""When I say I'll take care of something, remember the commitment, watch for evidence that I did it, and only remind me if it is genuinely still open.""
- **useful because:** Spoken commitments disappear into conversation today. This would turn an intent into a bounded, inspectable obligation and later reconcile it against signals the Mac and browser can actually observe—an outbound email, a changed file, a completed job, or a browser confirmation—rather than nagging from a timer. The owner gets fewer forgotten promises without creating a task for every casual thought.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Background model extracts the commitment, evidence predicates, and expiry; realtime model handles the brief capture and any final reminder.
- **latency:** Capture acknowledgement under 1 second; evidence checks are scheduled/background; reminder response under 2 seconds.
- **cost:** Low recurring cost: structured predicate checks and one small background extraction, with realtime used only for the spoken acknowledgement/reminder.
- **security:** Commitments may contain sensitive people, projects, or deadlines. Encrypt them, retain only until completion/expiry, do not inspect unrelated pages or mail, and require the owner to confirm ambiguous evidence before marking done.
- **missing:** A commitment record with explicit subject, evidence predicates, expiry, confidence, and owner-visible provenance; Mac and browser evidence adapters that report only narrow completion signals rather than full content; A reconciliation worker that can distinguish completed, contradicted, expired, and still-unknown states; A pendant query that answers the current open commitments without exposing a large task list

### ""Before you send anything outside this Mac, tell me exactly what data is leaving, where it is going, and what will remain here.""
- **useful because:** The current system can act through a logged-in browser, relay, and cloud models, but the owner cannot see the boundary between local observation and data transmission in one place. A short, non-blocking departure receipt would make an action intelligible: destination, fields or file classes, retention, and the redaction applied. It preserves the owner's maximum-access policy while preventing accidental surprise.
- **path:** mac-planner → browser-extension → relay → pendant → unified
- **model tier:** Cheap deterministic classifier builds the receipt; realtime speaks it only when the owner asks or when the departure is unusually broad.
- **latency:** Receipt generated alongside planning with less than 200 ms overhead; spoken explanation under 2 seconds.
- **cost:** Low: hashes, labels, and destination metadata dominate; no extra model call for routine local-only actions.
- **security:** The receipt itself must not echo secrets. Treat destination, filename, browser host, and redaction policy as sensitive metadata; encrypt and expire it. This is transparency, not a confirmation gate, so it must not block the owner's deliberate actions.
- **missing:** A data-flow inventory attached to every Mac, browser, relay, and model step; Structured sensitivity labels for shell output, files, page claims, audio, and credentials; A redaction-aware receipt endpoint joinable to job/action IDs and a pendant-friendly summary format

### ""For the next hour, let the Mac finish this one browser task without asking me again, but stop the moment the goal is met, the site changes, or the hour expires.""
- **useful because:** Today delegation is either a one-shot action or an effectively open-ended planner job. The owner needs a bounded lease: one goal, one site/session, explicit success and stop conditions, an expiry, and a live revocation path from the pendant. That enables genuinely useful unattended work without silently turning a temporary instruction into standing authority.
- **path:** pendant → relay → mac-planner → browser-extension → unified
- **model tier:** Background model compiles the natural-language goal into a constrained execution lease; realtime model handles only the spoken start/stop and exceptions.
- **latency:** Lease creation under 2 seconds; stop-condition evaluation after every browser/Mac step; revocation reaches the worker within 500 ms when connected.
- **cost:** Moderate implementation cost, low inference cost: mostly deterministic lease and step accounting, with a small model call for goal compilation.
- **security:** Lease scope must include exact host/session, allowed action classes, data destinations, expiry, and success criteria. Never widen it silently. Persist revocation durably so reconnect cannot resurrect authority; speak a failure rather than claiming completion.
- **missing:** A first-class expiring delegation/lease record with scope, stop conditions, and revocation sequence; Browser and Mac executors that enforce the lease between every step and emit a terminal reason; Pendant-side lease status and cancel control that works offline by queueing a revocation intent; A durable exactly-once join between lease, job, browser command, and final receipt


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: (1) a five-minute dual-chip bench health verdict (the highest-value commissioning feature), (2) a sleep/wake handoff that preserves compact Mac/browser work context without page contents, and (3) an on-demand 'prove it' explanation linking spoken claims to browser provenance and Mac receipts. The live serial diagnostic grant still does not resolve: the inventory has no serial capability, so the bench check needs a real host-side UART reader and diagnostic frame contract rather than another schema wrapper.

**Biggest unknown:** Whether the local agent or browser surfaces already emit reliable Mac sleep/wake events and complete browser provenance routes; those need a targeted live inventory/route check before implementation. The other hard blocker is a real serial reader/parser for /dev/cu.usbmodem* and /dev/cu.usbserial-*.

