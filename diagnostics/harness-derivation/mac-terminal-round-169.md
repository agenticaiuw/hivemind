# Harness derivation — mac-terminal — round 169

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I’m wearing the pendant next to my Mac, let me say ‘open that document’, ‘run the tests’, or ‘what’s on my screen?’ and have it work even when the pendant has no LTE.”"
- **useful because:** The hardware is physically present today but LTE registration is not. This turns the pendant from a cloud-only button into a useful local computer companion: the owner gets hands-free control and spoken results while the Mac is the nearby transport, with no false claim that the radio is online.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → mac-vision → browser-extension → dashboard
- **model tier:** Realtime for the short spoken command and intent extraction; deterministic Mac actions or the existing computer-use loop for execution; no background model unless a long-running task is explicitly requested.
- **latency:** Button-to-acknowledgement under 250 ms over USB serial; simple action completion under 2 s; screen interpretation under 5 s. Audio playback can continue through the ESP32 A2DP bridge.
- **cost:** Roughly one realtime turn plus any computer-use vision calls; simple commands are cheap, while screen questions dominate tokens and screenshots. No LTE/API cost when the Mac is the transport.
- **security:** USB serial must authenticate the pendant and bind the request to the active Mac session; never expose the local bridge to LAN. Speak a clear local/offline state and do not imply relay delivery. Screen contents and browser sessions stay on the Mac unless the owner explicitly asks for cloud reasoning.
- **missing:** A production USB serial transport joining nRF9160 button/audio frames to relay-realtime/mac-planner; A route that accepts a local pendant turn and returns framed audio plus typed action receipts; Session affinity so the command uses the foreground Mac/browser session instead of an arbitrary cloud session; A local bridge supervisor that reconnects the two currently attached serial devices

### "“If my Mac restarts or the USB cable drops halfway through a task, continue it exactly where it stopped and tell me whether anything was actually done—don’t make me start over or guess.”"
- **useful because:** Long actions currently have a durable job record but no boot reconciliation, no real process cancellation, no retry, and no exactly-once protection on /execute. The owner should be able to trust that a cable drop or laptop restart produces a truthful continuation, not duplicate email/files/browser mutations.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Background/cheaper model for classifying a failed step and selecting a resume point; deterministic execution for replay; realtime only to tell the owner the current state when asked or when the pendant reconnects.
- **latency:** On reconnect, acknowledge state in under 1 s; reconcile jobs in under 3 s; resume safe steps immediately and queue ambiguous side effects for a spoken clarification. Long tasks retain their existing execution time.
- **cost:** Near-zero model cost for clean ledger replay; one small background call only when a failed step needs semantic classification. Main engineering cost is process supervision and durable state, not inference.
- **security:** Never replay a mutation merely because its parent job was incomplete. Persist pre/post state, action idempotency keys, child PID/exit code, and a bounded command fingerprint; browser sessions and shell environment values must remain redacted. The pendant should say ‘unknown whether completed’ rather than claim success.
- **missing:** Boot-time reconciliation of processing jobs and open ledgers, with a deterministic interrupted/resumable state; AbortSignal propagation to child processes with SIGTERM then SIGKILL and captured exit code; Exactly-once action execution connected to the existing executionContext idempotency engine; A resume worker that joins jobId to ledgerId and reports each recovered step to the pendant and dashboard; Browser-side checkpoints for navigation/download/form actions

### "“Keep an eye on the authenticated page I left open, finish the routine when it can, and interrupt me through the pendant only when it needs a decision or something genuinely failed.”"
- **useful because:** The browser has sessions nobody else can reach, the Mac can act, the relay can stay awake, and the pendant is the only channel that can reach the owner while they are away. Today these are separate polling and action pieces; this would turn them into a reliable delegated worker instead of a chat reply that dies when the tab or USB link changes.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Cheap background model for polling/diffing and deciding whether a page change is actionable; deterministic browser and Mac actions for known routines; realtime only for the brief spoken escalation and the owner's answer.
- **latency:** Poll at 30–60 s without model escalation; deliver a pending-decision alert within 2 s of detecting a blocker; resume within 3 s after the owner answers. No continuous vision unless the page actually changes.
- **cost:** Low: most polls are DOM/state diffs; one small model call on changed content, with realtime cost only for escalations. Browser screenshots and private page text are the dominant token/data cost.
- **security:** Keep authenticated page content on the Mac/browser unless the owner explicitly permits relay reasoning; redact tokens, cookies and unrelated tabs from diffs. Bind each watch to a specific browser session/tab and show the source URL in the pendant alert. Never submit irreversible forms or purchases without an explicit owner response.
- **missing:** A durable watch-to-routine state machine with blocker/completion semantics, not just raw browser polling; Per-watch tab/session affinity and a private, redacted diff extractor; A relay-held escalation queue with retry and deduplication, linked to the pendant's offline outbox; An answer protocol so a spoken pendant response resumes the exact browser watch step; A quiet-hours/urgency policy that suppresses normal completions but wakes for blockers

### "“Where was that thing I looked at earlier—the page, file, or message I was just reading—and put me back there.”"
- **useful because:** People lose work across Safari tabs, desktop windows, and project folders constantly. A wearable should recover the owner's recent visual context by meaning, not require them to remember a title or manually search history. This is a genuinely cross-surface ability: the Mac observes local context, the browser supplies private tab/session metadata, the relay resolves the spoken reference, and the pendant returns the result while away from the keyboard.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → mac-vision → browser-extension → dashboard
- **model tier:** Cheap background indexing of redacted foreground-app/tab/file metadata; realtime model only resolves the owner's vague spoken reference and, if necessary, compares a few candidate screenshots or text snippets.
- **latency:** Return the top three candidates in under 2 seconds and open the selected one in under 1 second. Indexing runs opportunistically and should never slow foreground work.
- **cost:** Low when using titles, URLs, paths, and timestamps; screenshot/text comparison is the expensive fallback. Most indexing is local and incurs no cloud token cost.
- **security:** Keep a local encrypted index with per-application privacy exclusions and retention limits. Never upload full browser history, private messages, or screenshots by default. Require an explicit spoken confirmation before opening a sensitive page or file on a shared display.
- **missing:** A local, time-decayed context index spanning foreground apps, Safari tabs, files, and browser sessions; A semantic resolver that can search that index without sending its raw contents to the relay; A stable Mac deep-link/open-context action that restores the exact tab, window, scroll position, or file selection; A pendant response format for disambiguation candidates and an offline-safe ‘last known context’ cache

### "“While I’m walking, read me the important parts of the page or document I left on my Mac, let me say ‘save that’ or ‘skip it’, and have the exact place stay queued until I’m back.”"
- **useful because:** This makes the wearable a continuity surface rather than a remote control. The browser keeps the authenticated session and the Mac keeps the file; the pendant provides a private, eyes-free review and durable intent when the owner is away. The owner can turn a research or work session into a short spoken triage without exposing credentials or manually copying links.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Background model extracts a short local summary and candidate highlights; realtime model handles the owner's spoken save/skip/follow-up commands. Use deterministic local extraction for ordinary text and vision only for layout-heavy pages.
- **latency:** First spoken excerpt within 3 seconds, next excerpt under 1 second, and each save/skip acknowledged within 300 ms. Queue intents offline and reconcile on reconnect.
- **cost:** One small summarization call per changed document, with browser text extraction keeping most turns cheap. Vision and long PDFs are the dominant cost; cache summaries by content hash.
- **security:** Authenticated page text and local documents remain on the Mac by default. Redact passwords, forms, cookies, and unrelated tabs before any model call. Saving must store a pointer/content hash, not duplicate private content into relay memory; deletions and retention need owner control.
- **missing:** A Mac-side read-aloud cursor that can extract and chunk a private tab/document without changing the user's page; A durable spoken annotation/save queue tied to URL or file identity plus content hash and selection offsets; A relay/pendant protocol for streaming short excerpts and accepting save/skip intents with exactly-once delivery; A local destination integration (notes, project context, or task list) that records the saved excerpt and provenance

### "“Before you act on my behalf, tell me in one sentence what the other agents are about to do, and after they finish give me one combined answer—not three competing updates.”"
- **useful because:** The hive currently has multiple surfaces that can observe, plan, and act. The owner should experience one accountable assistant, not duplicated browser clicks, contradictory voice messages, or a Mac job that the pendant reports differently from the dashboard. A cross-agent intent lease and final synthesis would make delegation trustworthy at the moment it matters.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal → mac-vision → browser-extension → dashboard
- **model tier:** Cheap deterministic coordinator for leases, deduplication, and state aggregation; realtime model only compresses the final status into a spoken sentence. Use no expensive model for identical observations or already-known receipts.
- **latency:** Pre-action spoken plan under 500 ms for known actions; concurrent observations coalesce within 1 s; one final result within 2 s of the last receipt.
- **cost:** Usually below one realtime turn because coordination is deterministic. Savings come from suppressing duplicate model calls and repeated screenshots, not from adding inference.
- **security:** Every side effect needs an owner-visible intent ID, acting surface, target, and expiry. A lease must prevent two agents from executing the same mutation while still allowing independent read-only observations. Receipts should redact shell environments, page secrets, and private content; stale leases must expire safely rather than silently replay.
- **missing:** A shared intent/lease registry across relay, Mac, and browser agents; Canonical action IDs and causal parent IDs propagated into /execute, browser commands, pipeline events, and pendant acknowledgements; A reducer that turns heterogeneous receipts into one success/partial/failure/unknown outcome; A single owner-facing notification policy with deduplication, urgency, and replay protection


## Changes it proposed to its own stack

### `integration` — Ship a launch-on-login pendant companion daemon that claims /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, performs the faculty-action versioned HELLO/CRC handshake, routes button/audio frames to the local-agent pipeline, and reconnects independently when either serial device disappears. It should expose a single localhost session endpoint to mac-planner and persist a tiny last-turn cursor so reconnect cannot replay audio or lose the owner's utterance.
- **owner gets:** The owner can plug in the real pendant today and use it as a dependable local voice remote instead of manually starting firmware tools or silently falling back to a nonfunctional LTE path. Cable pulls, sleep, and replugging become a brief reconnect rather than a dead conversation.
- effort: Medium-high: native serial framing, launchd lifecycle, audio timing, and integration tests against both physical boards; requires the accepted firmware HELLO/CRC protocol and relay-realtime local-session support.  ·  risk: Serial contention or a bad reconnect could steal the port from flashing/debugging or duplicate a turn. Use exclusive-open with an explicit developer override, monotonic frame sequence numbers, and a dead-letter capture for malformed frames; recover by restarting only the daemon, never reflashing automatically.
- cost: No per-request API cost for transport; roughly 1–2 weeks engineering. Existing Mac hardware and boards; no new component cost.  ·  latency: Adds under 50 ms framing/IPC overhead; reconnect detection target under 1 s.
- security: Local-only Unix-socket/loopback endpoint, device identity plus CRC/replay protection, and no forwarding of raw serial frames to LAN. Audio remains private to the Mac unless selected for relay reasoning.
- depends on: Accepted truthful_action_status_beacon and audio_link_truth_and_recovery firmware behaviour; Faculty-action USB versioned CRC framing/HELLO implementation; A local pipeline session route that can carry typed turn IDs and audio cursors


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities and one concrete integration change: (1) local USB pendant mode so the physically attached pendant works without LTE, (2) crash/cable-drop continuation with truthful exactly-once recovery, (3) authenticated-browser delegated watches that alert the pendant only for blockers, and (4) a launch-on-login serial companion daemon joining both live boards to the local pipeline. The first capability was flagged as close to an existing focus-routine idea, so its differentiator is explicit: general spoken local commands plus audio and screen results, not one configured routine. I also asked faculty-action for the exact USB framing entry point.

**Biggest unknown:** The exact HELLO/CRC frame schema, turn/audio cursor protocol, and ownership rules for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA are still missing. I do not need another generic Mac diagnostic grant; I need that protocol contract and then a physical end-to-end test with the two boards.

