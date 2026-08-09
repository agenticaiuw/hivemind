# Harness derivation — faculty-perception — round 168

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-permissions-live** — GET /ops/status at 2026-08-08T03:05Z reports Accessibility trusted, Screen Recording granted, requiredMissing=[] and ready=true for com.aipendant.agent; relay reachable and browser online.
  - evidence: Live GET /ops/status HTTP 200 response: permissions.accessibility.trusted=true, screenRecording.granted=true, requiredMissing=[], ready=true; relay.reachable=true; browser.online=true.
- **browser-capability-attestation** — Safari extension is online with 9 tabs, but its published capabilities array is empty; there are zero pending commands and zero spooled commands.
  - evidence: Live GET /browser/status HTTP 200 at 2026-08-08T03:05Z: online=true, tabCount=9, capabilities=[], pendingCommands=0, spool.spooled=0.
- **pendant-presence-current** — No live nRF9160 pendant is established; currently discoverable devices are Safari on MacIntel online, home-macbook-bridge online, and cloudflare-contract-test mobile offline.
  - evidence: discover(devices) live result lists exactly those three devices; no nRF9160 pendant.

## Capabilities it proposed

### "“While I was away, tell me exactly what happened to my pending request, and separate completed, delivered-to-a-service, and merely attempted.”"
- **useful because:** The current pipeline calls a Mac-side result “completed” even when no pendant playback occurred, and an online browser can still have zero executable capabilities. An evidence-graded replay would stop the owner acting on false completion claims and name the precise missing handoff.
- **path:** relay → mac-planner → browser-extension → dashboard
- **model tier:** background for assembly; realtime only to speak the short answer
- **latency:** Under 2 seconds from the owner’s question; parallel reads dominate, not model time.
- **cost:** About $0.01–$0.04 per invocation if a cheap summarizer is needed; most cases are deterministic field mapping.
- **security:** Return only metadata and redacted snippets; do not expose browser page bodies or credentials. Require confirmation before retrying any action.
- **missing:** A resolved authenticated continuity-snapshot implementation (the granted resolver currently fails to bind); A shared event schema mapping browser postconditions, Mac receipts, relay acceptance, and device playback into evidence grades; A durable correlation ID propagated from request through browser/Mac/relay stages

### "“After you change something in my browser, prove what changed—or tell me that you cannot prove it.”"
- **useful because:** The extension is online today but advertises capabilities=[], and action completion currently does not guarantee a browser postcondition. A verifier would reread the target tab, compare pre/post URL, title, and a redacted content fingerprint, and say ‘not verified’ instead of silently treating a dispatched command as success.
- **path:** browser-extension → mac-vision → mac-planner → dashboard
- **model tier:** background deterministic comparator; realtime only for the owner-facing sentence
- **latency:** 2–5 seconds after an action, including one fresh inspection.
- **cost:** Usually <$0.01: browser inspection and hashing are local; vision/model fallback is the dominant cost and should be opt-in.
- **security:** Never persist page text by default; hash/redact sensitive regions, require confirmation for destructive or authenticated mutations, and classify an empty capabilities array as ‘cannot execute,’ not as success.
- **missing:** A browser command contract requiring a postcondition selector and expected state; A fresh inspection endpoint that returns stable, redacted fields after each command; Extension capability attestation and a signed command/result correlation token

### "“What can you actually reach right now—my Mac, browser, relay, and pendant—and what can’t you do?”"
- **useful because:** The live state is easy to misread: this Mac is fully permission-ready, Safari is online with nine tabs but capabilities=[], the relay is reachable, and no pendant is registered. A single spoken reachability answer lets the owner choose a path that can succeed instead of issuing an impossible command or assuming online means controllable.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** deterministic state synthesis, with realtime only to render the concise spoken answer
- **latency:** Under 1 second using parallel authenticated reads.
- **cost:** Negligible API cost; one compact deterministic response. The cost is maintaining explicit freshness timestamps and capability semantics.
- **security:** Expose only coarse reachability and capability names, not tab URLs, credentials, or machine inventory. Treat stale and unknown as distinct from offline; never infer pendant presence from a Mac-authored snapshot.
- **missing:** A first-class reachability response with per-surface freshness, transport, and capability state; A device-originated pendant heartbeat/registration path (the current registry does not receive one); A browser capability attestation that explains why an online extension currently exposes capabilities=[]

### "“Show me the exact state of my digital life at 3:17 PM yesterday—including what was on screen, which browser session was active, what the relay accepted, and whether the pendant was physically playing anything.”"
- **useful because:** Today the system can inspect current surfaces and retain disconnected, differently-clocked traces, but it cannot reconstruct one trustworthy moment. The owner cannot audit a consequential event, understand a missed handoff, or prove what they saw without manually correlating pipeline timestamps, browser state, Mac receipts, relay records, and device telemetry. A time-indexed reality replay would return an ordered scene with explicit clock uncertainty and ‘unknown’ where no sensor existed, rather than inventing continuity.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard → new-surface
- **model tier:** Background deterministic event joiner and evidence renderer; use realtime only when the owner asks verbally for a short spoken summary.
- **latency:** Initial replay in 3–8 seconds for a bounded 24-hour interval; exact-point queries should return in under 2 seconds after indexes exist.
- **cost:** Usually <$0.03 per replay; storage/indexing and screenshot retention dominate, not model inference.
- **security:** This is an extremely sensitive reconstruction of screens, audio, browser sessions, and actions. Encrypt at rest, redact secrets before indexing, make screenshot/audio retention opt-in with short TTLs, require explicit confirmation for exporting a replay, and show provenance plus uncertainty for every fact.
- **missing:** A shared monotonic event envelope carrying eventId, source clock, relay receipt time, local receipt time, and uncertainty bounds; Periodic privacy-preserving browser/Mac scene checkpoints (content hashes and redacted metadata by default, optional encrypted screenshots); A relay-to-Mac export of durable job and announcement records keyed to the same correlation ID; A pendant-originated playback/transport event stream; without it, the replay must visibly say playback is unknown; A query and dashboard surface that renders a causal timeline rather than merging timestamps naively


## What it asked for

_Nothing._
## Its own summary

Round 168 established three fresh live facts: the exact agent binary is now Accessibility- and Screen-Recording-ready; Safari is online with 9 tabs but advertises capabilities=[] and has no pending/spooled commands; and no nRF9160 pendant appears among currently discoverable devices. I recorded all three. I proposed (1) evidence-graded away-while-you-were-gone replay, (2) browser mutation postcondition verification, and (3) a live reachability answer across Mac/browser/relay/pendant. The USB-local pendant fallback was rejected as an existing proposal, so I did not restate it.

**Biggest unknown:** The granted read_continuity_snapshot still cannot resolve at runtime (nearest matches are GET /ops/snapshot and GET /pipeline), so I still lack one authenticated cross-surface read that can join freshness and event evidence without manually combining routes. I also still need the browser action result schema/postcondition fields from faculty-action; I asked them rather than guessing.

