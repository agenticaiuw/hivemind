# Harness derivation — mac-terminal — round 185

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser connectivity** — The Mac agent is online with FULL_CONTROL_MODE true, relay reachable, Accessibility and Screen Recording granted, and Safari extension online with 9 tabs; active tab is X at https://x.com/home. The pendant LTE device remains offline, but the USB-connected hardware is available per system context.
  - evidence: GET /ops/status returned agent.fullControlMode=true, relay.reachable=true, browser online=true/tabCount=9; GET /jobs returned a successful browser_list_tabs receipt.

## Capabilities it proposed

### "I tap the pendant and say “where did I leave off?” Have it give me a 30-second, actionable resumption brief from my Mac, browser, and unfinished AI work."
- **useful because:** This is the highest-value everyday behavior: after walking away, sleep, or a crash, the owner gets the exact next step instead of reconstructing state across Terminal, Safari, and the pendant. It only works as a hive: the pendant supplies the request and audio, the Mac supplies project/job state, Safari supplies authenticated page context, and the relay joins and speaks it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** deterministic collection first; background model summarizes; realtime only handles the spoken request and delivery
- **latency:** Under 3 seconds for collection and a 20–30 second spoken answer; cap browser extraction at the active tab plus one recently relevant tab.
- **cost:** Usually near-zero model cost if receipts, active project, active tab, and recent job records are structured; one short background summarization call when joining heterogeneous evidence dominates.
- **security:** Authenticated URLs and terminal/project names must stay on the Mac/relay boundary and never be sent to an external browser. Return provenance and age for every claim; omit page bodies unless the owner explicitly asks.
- **missing:** A single resume-snapshot endpoint joining GET /jobs/:jobId, GET /journal/:jobId, GET /projects/active, GET /machine-context, and browser active-tab inspection; A compact relay intent/response envelope that carries the pendant turn ID and evidence ages; A background summarizer that refuses to infer a next step when evidence is stale or contradictory

### "When I say “that failed—fix it,” explain the failed Mac command in plain language, show the exact evidence, try one safe recovery with the right project directory, and tell me precisely what changed."
- **useful because:** Today a failed shell action loses exit code, PID, environment provenance, and often the real working directory, so the owner has to debug blind. This turns the Mac from fire-and-forget into a useful recovery partner without adding approval gates or reducing FULL_CONTROL_MODE.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** deterministic receipt/error parser and bounded retry planner; realtime only for the spoken exchange
- **latency:** Parse immediately; first diagnosis under 1 second; one recovery attempt within 10 seconds. Never loop retries.
- **cost:** Most failures need no model call if exit code/signal/stderr/ cwd are typed; a small planner call only for selecting a recovery command. Cost is dominated by the exceptional planner call.
- **security:** Record a redacted environment fingerprint, not secret values; preserve the unrestricted execution policy the owner chose. Recovery must include command, cwd, inputs, and before/after receipts in the spoken and durable result. A recovery that can delete or publish data must be reported as such, not silently guessed.
- **missing:** Shell receipts with exit code, signal, pid, timeout-vs-exit distinction, argv-or-original-command, cwd, and a hashed environment allowlist; A failure classifier that distinguishes missing executable, wrong cwd, permission, timeout, network, and nonzero application result; A one-recovery planner that can query GET /projects/active and recent receipts, then emits a linked POST /execute job with an explicit parentJobId; Boot-time reconciliation that marks jobs interrupted by agent restart instead of leaving them processing forever

### "When the relay or LTE is unavailable but the pendant is plugged into my Mac, let me say “stop that,” “save this,” or “what is running?” and have the Mac act locally, then queue a truthful result for later delivery."
- **useful because:** The hardware is physically present today even though the pendant is not LTE-registered. A dropped WAN link should not make a wearable attached by USB useless: emergency stop/status and durable capture are precisely the actions that must work at the edge. The pendant gives an unambiguous physical request, the USB serial path reaches the Mac, and the relay later reconciles the result rather than inventing success.
- **path:** pendant → Mac USB serial bridge → mac-terminal → mac-planner → relay-realtime
- **model tier:** deterministic local intents for stop/status/save; no cloud model while offline; background reconciliation and optional speech summary when relay returns
- **latency:** LED acknowledgment under 150 ms, local status under 1 second, stop dispatch under 2 seconds; reconnect reconciliation in the background.
- **cost:** No API cost for local intents; a few hundred bytes of serial traffic per event. A short relay summarization call only when queued events are merged after reconnection.
- **security:** Only accept a signed, paired USB device nonce and monotonically increasing intent sequence; reject stale/replayed frames. “Stop” must target a specific active job and report whether it was actually interruptible (current shell cancellation is cooperative). Never transmit terminal output or browser content merely to acknowledge a local intent.
- **missing:** A real framed USB serial protocol between /dev/cu.usbmodem00096003658* (nRF9160) and /dev/cu.usbserial-0287A9CA (ESP32 bridge), with CRC, sequence, and replay protection; A Mac local-intent daemon that maps three bounded intents to GET /jobs, POST /jobs/:jobId/cancel, and POST /capture without contacting the relay; A durable outbox reconciliation route carrying local intent/result IDs into the relay when reachable; A cancellation implementation that passes AbortSignal to child processes, so local “stop” can actually terminate a running shell instead of merely marking it

### "Let me ask, “What did you do on my behalf about the rent email?” and get a chronological, source-linked answer covering what I said on the pendant, what the Mac changed, what Safari showed or submitted, and what is still unresolved."
- **useful because:** Today the system can perform work across surfaces but cannot answer forensically what happened to one real-world matter. A single trace would prevent duplicate replies, expose an unnoticed failure, and let the owner correct the agent with facts rather than memory. This is a cross-surface capability: no individual node has the complete story.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension
- **model tier:** Deterministic correlation and redaction first; a background model turns the trace into a short answer; realtime only handles the spoken query.
- **latency:** Return a bounded 60-second spoken answer within 4 seconds for the last 7 days; older searches can run in the background and notify the pendant.
- **cost:** Low when correlation uses indexed IDs, timestamps, URLs, and action types; one short summarization call dominates cost for a multi-step matter.
- **security:** Search must be owner-scoped and preserve source boundaries. Do not expose full email or page bodies by default; speak snippets with links and timestamps. Sensitive browser fields and shell environments stay local unless explicitly requested.
- **missing:** A durable cross-surface matter ID that can be attached to a voice turn, Mac job, browser command, capture, and relay event; An indexed event store with normalized timestamps, causal parent IDs, and explicit success/failure/unknown states; A provenance query endpoint that returns source excerpts and redaction metadata rather than an opaque summary; A retention and deletion control for matter traces

### "Before I send this, let me ask the pendant “have I already sent something like it?” and get a duplicate-risk answer across Mail, authenticated Safari pages, and previous Mac actions without opening or editing anything."
- **useful because:** Duplicate messages, payments, forms, and support requests are a costly failure mode that no single surface can detect. The system should compare the owner’s intended subject/recipient/amount and semantic content against recent sent evidence, while making clear when it cannot prove absence.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal
- **model tier:** Deterministic candidate retrieval and exact field matching first; a background model compares only capped, redacted candidate text; realtime speaks the confidence and evidence.
- **latency:** Under 5 seconds for a 30-day search; return immediately with “not enough evidence” rather than waiting indefinitely for an authenticated tab.
- **cost:** Low for structured fields and hashes; model cost is limited to a few candidate snippets and only for semantic similarity.
- **security:** Never crawl all private content indiscriminately. Require an explicit scope (mail, current browser origin, or Mac action history), keep credentials and unrelated messages out of the prompt, and distinguish “no match found” from “not searched.” No mutation is allowed in this capability.
- **missing:** A consented, read-only Mail search adapter and a browser-side sent-action/evidence index; Canonical normalization for recipient, amount, subject, URL, form target, and content fingerprint across Mail, Safari, and Mac receipts; A temporal duplicate query with explicit search coverage and confidence, including an auditable list of matches; A pendant response format that can speak uncertainty without collapsing it into yes/no

### "Do not tell me an action is done until you independently verify its intended outcome—for example, confirm the form's success receipt, the file's expected contents, or the calendar event's actual fields—and tell me what could not be verified."
- **useful because:** An action receipt currently proves that a command or click ran, not that the owner’s goal happened. Independent outcome verification prevents the most dangerous false confidence: a submitted form that was rejected, a file written to the wrong project, or a calendar event with the wrong time. The pendant gets a truthful spoken result while Mac and Safari provide the observables.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension
- **model tier:** Deterministic verifier with typed predicates and fresh reads; background model only translates ambiguous page/file evidence; realtime delivers the verdict.
- **latency:** Verification within 2 seconds for local files and 5 seconds for browser outcomes; if an external confirmation is delayed, say “dispatched, not verified” and schedule a background check.
- **cost:** Usually no model call when predicates are typed (file exists, URL/status/title matches, event fields equal); exceptional semantic page verification costs one small background call.
- **security:** Verification must be read-only and bound to the exact action ID, target tab, path, or event. Never treat a similar page or stale screenshot as proof. Do not leak private page contents; return only the predicate result and minimal evidence. Require explicit expiry for delayed checks.
- **missing:** An owner- or planner-supplied outcome predicate attached to every mutating action; Fresh postcondition readers for files, browser submissions, Calendar/Mail, and shell-generated artifacts; A verifier ledger that records expected predicate, observation timestamp, evidence hash, and verified/failed/unknown state; Pendant and relay vocabulary that separates accepted, executed, verified, and contradicted


## What it asked for

_Nothing._
