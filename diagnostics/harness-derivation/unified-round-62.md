# Harness derivation — unified — round 62

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live browser reachability** — home-chrome/browser extension is offline with 5 pending commands; no active tab or tab URL is available, so private-page actions cannot currently be verified.
  - evidence: GET /browser/status returned online:false, tabId:null, tabCount:null, pendingCommands:5; GET /ops/status matched this state.
- **live Mac automation readiness** — Mac bridge is online and full-control mode is enabled, but Accessibility and Screen Recording are both untrusted/missing; GUI receipts cannot be treated as reliable until owner grants them.
  - evidence: GET /ops/status returned macBridgeOnline:true, accessibility.trusted:false, screenRecording.granted:false, computerUse.loopEnabled:false.
- **time authority conflict** — Owner memory declares America/Chicago while live Mac context reports a New York timezone; this is unsafe for spoken time and routine scheduling.
  - evidence: discover(owner) remembered timezone America/Chicago; GET /ops/status machine context reports timezone conflict noted by faculty-perception.

## Capabilities it proposed

### "If I tell you to handle something and then walk away or lose connection, keep the request safely queued, resume it on the right machine when it comes back, and give me a short spoken receipt when I return—without ever sending, deleting, or buying without my approval."
- **useful because:** Today the pendant, relay, Mac, and browser each show partial continuity: the live pipeline already records held alerts and bookmarks, while the browser is currently offline with five pending commands and the Mac bridge is online but lacks Accessibility and Screen Recording. This capability turns those fragments into one trustworthy handoff. It is more specific than a generic background job: it preserves the owner's original intent across a dropped LTE link and a sleeping/offline browser, resumes only reversible work, stages irreversible work with exact evidence, and delivers the result back through the pendant.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use realtime only to capture/acknowledge the short voice intent and announce the receipt; use a cheaper background planner for decomposition, retries, evidence reconciliation, and status wording. No model call is needed for queueing, deduplication, or safety gates.
- **latency:** Immediate local acknowledgement under 300 ms when offline; relay enqueue under 2 s when reachable; resume within 30 s of a Mac/browser heartbeat; return a one-sentence receipt on next pendant connection. Destructive steps remain staged until an explicit approval gesture/voice command.
- **cost:** Usually <$0.01 per task: one short realtime turn only if spoken acknowledgement is needed, then inexpensive background planning. Dominant non-API cost is browser automation time and relay storage for evidence/audio.
- **security:** Private-page content must stay on the authenticated Safari lane; public pages may use the relay browser. Store an intent hash, sensitivity class, and minimal evidence rather than raw audio by default. Never replay a non-idempotent step after an uncertain timeout. Require confirmation immediately before sending mail, submitting forms, deleting files, or purchasing; expose before/after evidence and an undo/abort path.
- **missing:** A durable job runner with jobId persistence, retries, and a result stream (the browser router exists but this does not); A single cross-node intent envelope with idempotency key, expiry, approval state, and origin timestamps; Reliable browser extension heartbeat/reconnect and draining of its five pending commands; Mac Accessibility and Screen Recording grants if GUI work is required; Timezone authority/convergence (machine currently reports New York while owner memory says Chicago); A pendant-local offline intent spool and a physical approval/status gesture


## Changes it proposed to its own stack

### `context` — Add a signed time-and-locale convergence record to every cross-node job and routine: relay UTC receipt time, pendant monotonic uptime, Mac timezone/offset, browser locale when available, and the owner's declared America/Chicago preference. Before scheduling, speaking a time, or interpreting a deadline, the planner must select the freshest trusted source, detect disagreement, and say “I have conflicting clocks” rather than silently using the Mac value. Persist the resolved zone separately from machine context, with an expiry and an owner-visible correction action.
- **owner gets:** The live system already has a real failure: owner memory says Chicago while the machine reports New York, and repeated “what time is it?” requests have produced routine/pipeline activity. This prevents missed routines, wrong calendar interpretations, and misleading spoken answers when the Mac, relay, LTE pendant, and browser disagree or reconnect after sleep.
- effort: Medium: typed context schema, one convergence reducer, route metadata on jobs/routines, dashboard status card, and firmware/relay timestamp fields; add simulated clock-skew and reconnect tests.  ·  risk: A stale owner preference could override a genuine travel location, or a clock jump could defer a task. Recover by requiring explicit confirmation on zone changes, retaining both raw observations and the chosen value, and never deleting scheduled jobs during reconciliation.
- cost: Negligible API cost; a few hundred bytes of metadata per job and one small context lookup. No new hardware required.  ·  latency: Under 10 ms locally; at most one extra relay context read for a new session, not on every audio frame.
- security: Timezone and location-like data are sensitive. Keep it in the typed private context projection, do not send it to public Browser Run, and redact exact location from receipts.
- depends on: A typed context projection rather than hand-written fleetContext sections; Job/routine provenance fields and an owner-facing correction control; A clear policy for travel/timezone changes (currently requested context is still missing)

### `integration` — Create a cross-surface, one-time approval passport for pending actions. When the relay or Mac prepares an irreversible step, it emits a canonical action digest plus before/after evidence, expiry, target account/tab, and a nonce. The same pending item appears in the dashboard, Mac menubar, and as a short spoken summary on the pendant; approval from any one surface (button gesture plus spoken nonce, dashboard tap, or menubar confirmation) is accepted exactly once by the relay, while edits or changed evidence invalidate it. Every other node receives the final accepted/rejected/expired state, so an offline or stale browser command cannot replay an old approval.
- **owner gets:** The owner should be able to start work through the pendant and approve it wherever they are—without hunting for the right screen—while knowing that “approve” means exactly the reviewed action, not a later mutation. Today the browser is offline with queued commands, Mac GUI receipts are untrusted, and no single approval state spans pendant, relay, Mac, and browser; the owner therefore cannot safely complete a cross-device transaction from the device they happen to have nearby.
- effort: High: define a signed action/evidence envelope and nonce ledger in the relay; add dashboard and menubar pending-action views; add pendant display-free spoken digest plus confirmation gesture; make browser and Mac executors verify the digest immediately before execution; add replay, reconnect, expiry, and changed-page tests.  ·  risk: A stolen or overheard approval could authorize an action, or a digest mismatch could strand a legitimate task. Mitigate with short expiry, device pairing, explicit target/account narration, a second deliberate pendant press for high-impact actions, and a visible cancel-all control; default to expiry rather than execution on any disagreement.
- cost: Low API cost (no model call for verification); modest D1 storage for nonce/evidence hashes and dashboard polling. Hardware cost is none on the prototype, though a production pendant should add a small vibration motor or second confirmation input for reliable tactile approval.  ·  latency: Adds roughly 100–500 ms for relay nonce validation and final state fan-out; no added latency to ordinary conversation.
- security: Improves security by binding approval to exact content, target, freshness, and device pairing. Raw private-page evidence remains on the private browser lane; relay stores hashes and minimal redacted previews unless the owner explicitly requests retention.
- depends on: A durable cross-node job record with idempotency and receipts; A reconnecting browser command queue that can invalidate stale pending commands; A pendant-local confirmation mechanism that survives a dropped link; A shared typed context/evidence envelope rather than per-surface free-form prompts


## What it asked for

_Nothing._
## Its own summary

Round 62 produced two new proposals: (1) cross-node intent escrow that safely queues a spoken request through pendant→relay→Mac/browser across disconnects, resumes idempotently, stages destructive steps, and returns a pendant receipt; (2) signed time/locale convergence to resolve the live Chicago-vs-New-York conflict before routines or spoken times. Fresh live facts recorded: browser offline with five pending commands; Mac Accessibility and Screen Recording missing; relay and bridge reachable; pipeline shows held alerts/bookmarks and 24 kHz TTS delivery.

**Biggest unknown:** Whether the orchestrator’s claimed grants have actually landed: discover(granted) is empty, and the durable runner, cross-node intent envelope, browser reconnect/drain, timezone policy, pendant approval/spool skill, and end-to-end audio acceptance validation remain unobserved.

