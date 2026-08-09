# Harness derivation — mac-planner — round 186

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask “Where was I?”, give me one short spoken sentence describing the work I was actually doing on the Mac, the browser tab or document involved, and the next obvious step."
- **useful because:** It turns the distributed system into continuity rather than a collection of commands: the pendant supplies the question, the Mac supplies live foreground/browser state, Calendar/Mail provide urgency, and the relay compresses it into the owner's preferred one-sentence answer. No single node can know all of that.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background summarizer for state compression; use realtime only to answer the spoken question and route an optional open action.
- **latency:** Under 3 seconds for the spoken answer; read-only collection should run in parallel in under 1 second.
- **cost:** Usually one short realtime turn plus a small background summarization call; roughly $0.01–$0.04, dominated by realtime audio.
- **security:** State leaves the Mac only as redacted app/title/URL/calendar/mail metadata. Never include message bodies or secrets by default. Opening a file/tab is a separate explicit command and must follow the owner's configured policy.
- **missing:** A single correlated Mac snapshot joining foreground app, browser tabs, active project and recent calendar/mail context; A relay intent that ranks the snapshot into one next step; An owner-configurable redaction policy for titles and URLs

### "When I press the pendant's bookmark button, attach the Mac's current app, browser tab, project and timestamp to that bookmark; later, when I ask “what did I mark?”, read back the useful breadcrumbs and offer to reopen one."
- **useful because:** The existing offline bookmark records a moment, but today it loses the context that makes the moment useful. This makes a button press at the exact moment of an insight recoverable days later, even though the pendant is currently USB-attached and LTE is not registered.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** No expensive model for capture: deterministic metadata collection and a cheap embedding/index job. Realtime is used only for the later spoken lookup.
- **latency:** Acknowledge the button immediately; enrich and upload within 2 seconds while the Mac link is present. Lookup answer under 3 seconds.
- **cost:** Near-zero capture cost; one small embedding/summarization call per bookmark, about $0.001–$0.01.
- **security:** Store only app identity, URL, project and timestamp by default; redact query strings, mail subjects and document contents. Reopening a URL/file is a mutation and must be independently authorized. Offline queue must inherit the existing bookmark durability and deletion rules.
- **missing:** A bookmark-enrichment event carrying a device bookmark ID for idempotency; A searchable ledger/index over enriched bookmarks; A typed reopen-bookmark action with receipts

### "At the end of a work session, let me say “leave me a handoff”; create a dated Markdown handoff in ~/AI-Pendant-Workspace containing the active project, open browser tabs, today's relevant calendar/mail items, and my dictated next action, then tell me on the pendant where it was saved."
- **useful because:** This is the most useful durable bridge between human sessions: the worn device captures the owner's intent at the moment they stop, the Mac contributes live work context, and the relay makes it searchable and replayable later. It prevents the common failure of remembering that work existed but not how to resume it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Cheap structured extraction and templating; realtime only transcribes the short dictated next action and confirms completion. No large reasoning model is needed.
- **latency:** Stage the handoff in under 5 seconds and speak a one-sentence receipt immediately; file writing can be atomic in the background.
- **cost:** One short realtime turn, roughly $0.005–$0.02; Mac workbench and metadata collection are local.
- **security:** Default to snippets and metadata, not full mail bodies or page content. Never send mail or alter source documents. The handoff path is allowlisted and writes are atomic; the owner can inspect/delete the Markdown afterward.
- **missing:** A relay command that combines dictated text with a live Mac/browser snapshot; A stable project-aware template and deduplication key for repeated handoffs; A pendant receipt event that names the saved handoff without reading its contents aloud

### "Run a pendant health check: from the Mac, arm the USB diagnostic fixture, collect the nRF9160 UART report and audio counters, compare them with the accepted thresholds, and tell me on the pendant exactly what failed and whether it is safe to use."
- **useful because:** The hardware is physically connected now even though LTE registration is not, so this gives the owner a trustworthy pre-flight instead of discovering a broken capture, codec or serial path during a real conversation. It uses both chips and produces a human result, not a raw log.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Deterministic parser and threshold checker; use realtime only to turn failures into one short spoken sentence.
- **latency:** Under 15 seconds from request to result, with live UART collection dominating.
- **cost:** Effectively zero model cost; local serial I/O and parsing dominate.
- **security:** The fixture must generate synthetic audio only and never persist microphone content. Store a bounded redacted diagnostic receipt, not raw UART indefinitely. A failed test must not automatically change firmware or delete logs.
- **missing:** A resolved Mac USB-serial exchange capability for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A versioned parser for the fixture's sequence numbers and counters; A relay route that publishes the signed pass/fail receipt to the pendant inbox

### "Before sending an email, deleting a file, buying something, or submitting a form, show me the exact preview on the Mac and let me approve it with a deliberate press on the pendant; reject approvals that are stale, for a different browser tab, or for a different action."
- **useful because:** The owner can already ask for automation, but today FULL_CONTROL_MODE has no approval gate at all. This makes the pendant a physically present, auditable confirmation device while the Mac/browser remain the actors. It is the safest way to make high-impact automation genuinely usable without making every harmless action tedious.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** No model is needed for approval verification; realtime only explains the preview if the owner asks. Use a deterministic signed action digest and a short-lived nonce.
- **latency:** Preview in under 2 seconds; approval-to-execution under 1 second; expire the nonce after 60 seconds.
- **cost:** Negligible model cost; local signing, relay storage and one Mac/browser round trip dominate.
- **security:** The pendant must never approve by mere connection or accidental button edge. Bind the nonce to action arguments, target app/tab, account scope and expiry; display a human-readable diff; record receipt and rejection. Sensitive preview fields must be redacted according to owner policy.
- **missing:** A firmware/server challenge-response protocol using a pendant-held key; A Mac/browser execution seam that accepts and verifies the signed action digest; An explicit owner policy table defining which action classes require physical approval

### "When I ask “prove that,” take the claims in the last spoken answer, show the exact supporting email, calendar event, file, or browser page on the Mac, and speak only the source names and any disagreement you found."
- **useful because:** A short spoken answer is useful but hard to trust when it mixes live browser data, mail, calendar and model inference. This creates an on-demand evidence trail across the surfaces the owner actually uses, without dumping private content into the pendant audio stream.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic source IDs and excerpts first; a cheap model can classify disagreements. Realtime is only for the concise spoken result.
- **latency:** Under 4 seconds for up to five sources; opening the selected source is a separate action.
- **cost:** About $0.002–$0.01 per verification, mostly small excerpt classification; local source reads are free.
- **security:** Never read full mail or page bodies aloud by default. Keep evidence local where possible and send only hashes, titles and short redacted excerpts to the relay. Opening an authenticated page must preserve tab/session affinity.
- **missing:** Claim-to-source IDs carried through the answer pipeline; A local evidence panel that can render redacted excerpts and disagreements; A browser/Mac command to open the exact cited source with session binding

### "Let me say “hand this off to my Mac” while wearing the pendant: keep the conversation alive if the Mac is asleep or disconnected, queue the exact plan and its required context, then execute it automatically when the Mac returns and tell me whether the result matches the original intent."
- **useful because:** Today a dropped Mac link turns a useful spoken plan into a dead end, and retrying risks duplicating side effects. This makes the wearable and relay a real always-available front end while the Mac is an eventually connected executor, with intent preservation rather than a vague retry.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles the initial spoken command; background work validates and compacts the plan. Execution should be deterministic, with a model used only to explain mismatches.
- **latency:** Immediate spoken acknowledgement offline; execute within 5 seconds of Mac reconnection; reconciliation under 3 seconds after receipt.
- **cost:** One short realtime turn plus a small background validation call, roughly $0.005–$0.02; durable relay storage is the main non-model cost.
- **security:** Plans must be immutable, idempotency-keyed and scoped to the original Mac/browser session. Never execute a plan whose context changed materially; produce a diff and route high-impact steps through physical approval. Encrypt queued context and expire it.
- **missing:** A relay durable intent queue with idempotency and context expiry; Mac reconnect/capability negotiation and plan receipt acknowledgements; A reconciliation protocol that compares expected versus actual side effects


## What it asked for

_Nothing._
## Its own summary

I discovered the live grants and devices: the Mac bridge is online, Safari has 9 tabs, and the pendant/bridge are usable over USB even though LTE is not registered. I recorded four hive-native capabilities: (1) “Where was I?” continuity from live Mac/browser/calendar/mail state, (2) bookmark enrichment that binds the existing pendant bookmark to app/tab/project context, (3) a dictated end-of-session Markdown handoff written atomically into ~/AI-Pendant-Workspace, and (4) a USB pendant health check against the shipped 24 kHz/audio acceptance thresholds. The recorder flagged the first three as close to prior ideas, so I will not rephrase them again; their genuinely new deltas are the correlated live-state join, bookmark-ID idempotency/search, and atomic dictated handoff. The health-check proposal is also close to existing clinic work and should be treated as connective wiring, not a fresh standalone feature.

**Biggest unknown:** The missing live seam is USB serial exchange: I still cannot arm/read /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA from this agent. I also still need a typed correlated Mac snapshot (foreground/document/browser/project), a searchable enriched-bookmark index, and a relay-to-pendant receipt route. Accessibility remains owner-blocked, so these should use AppleScript/browser bridge/serial rather than assuming UI snapshots.

