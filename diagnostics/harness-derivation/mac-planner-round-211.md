# Harness derivation — mac-planner — round 211

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-now-live** — The AI Pendant Agent currently has Accessibility and Screen Recording trusted; synthesized events post successfully, so UI-targeted Mac actions can reach the screen. This supersedes the earlier denied-TCC condition.
  - evidence: mac_readonly_inspect(operation=running_apps) invoked GET /observe at 2026-08-08T04:38:06Z: accessibility.trusted=true, screenRecording=true, eventsPost=true, inputReachability.status=verified.

## Capabilities it proposed

### "Start a 25-minute focus sprint on the pendant, keep only the tabs and apps I name usable, and tell me when the sprint ends what I actually finished."
- **useful because:** This turns the wearable into a lightweight interruption boundary rather than another notification channel. The relay owns the timer and intent, the browser extension closes or parks distracting tabs, the Mac agent tracks allowed foreground apps and completed edits, and the pendant gives a quiet start/end cue even if the owner never looks at the screen.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Deterministic scheduler and event ledger; cheap background model only to summarize the completed work at the end; realtime model only to parse the initial spoken command if needed.
- **latency:** Start acknowledgement under 1 s; enforcement on each browser heartbeat or app transition under 2 s; end summary within 10 s of expiry.
- **cost:** Roughly $0.001-$0.005 per sprint, dominated by one short end-of-sprint summary; timers, app/tab matching, and heartbeats are local/deterministic.
- **security:** The extension must not read page bodies merely to enforce focus. It needs only tab URL/title and active status, with an owner-configured allow/deny list. Closing tabs is destructive to unsaved state, so default behavior is park/mute or open a visible warning rather than delete. Work metrics should stay local unless the owner asks for a summary.
- **missing:** A relay-owned focus-sprint state machine with expiry and crash recovery; Browser commands for suspend/restore or mute a tab without destroying its state; A read-only Mac foreground-app transition feed (polling is acceptable initially); A pendant inbox event type for quiet expiry/start acknowledgement

### "I’m leaving the desk—pause anything waiting to act, lock the Mac, and tell me on the pendant when it is safe; resume only when I explicitly say I’m back."
- **useful because:** A single spoken command closes the dangerous gap between a queued browser/Mac plan and the owner physically walking away. The relay freezes new execution, the Mac locks and reports the result, browser sessions stop accepting commands, and the pendant gives a definitive local acknowledgement. This is useful precisely when attention is moving away from the computer.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic policy and state machine; no expensive model after intent classification. Realtime model only maps the short utterance to leave/return.
- **latency:** Freeze new jobs immediately at relay (<200 ms); lock command and receipt within 3 s; pendant acknowledgement within 5 s, with a local timeout/error state if Mac is unreachable.
- **cost:** Below $0.001 per invocation; almost all work is state transitions and one Mac action, not inference.
- **security:** The lock operation is high-impact but explicitly requested by this command. Never auto-resume on network return, timer expiry, or a guessed presence signal. Do not reveal active URLs or app names in the spoken acknowledgement. If the lock fails, the pendant must say so plainly rather than claiming safety.
- **missing:** A relay execution freeze/resume primitive that prevents races with already-polled browser commands; A Mac lock-screen action and verifiable postcondition receipt; A browser bridge state that rejects commands while the desk is locked; A local pendant acknowledgement event that survives a dropped link

### "Run a health check on my pendant and tell me whether the microphone, 24 kHz speaker path, radio framing, and storage queue are healthy; if not, file a repair report with the UART evidence."
- **useful because:** This is the highest-value capability for a device whose failures are otherwise silent: one command converts the shipped diagnostic fixture into an owner-readable verdict and an actionable bug report. The pendant emits synthetic evidence, the Mac is physically connected to both chips and can collect UART output, the relay compares measurements with acceptance thresholds, and the browser/dashboard can show the exact failing stage. It is testable now without LTE registration or microphone access.
- **path:** pendant → mac-planner → relay-realtime → dashboard → browser-extension
- **model tier:** Deterministic parser and threshold evaluator for all measurements; cheap background model only to turn a failed machine-readable result into a short repair report. Realtime model speaks only the final verdict.
- **latency:** Start acknowledgement under 1 s; fixture run 30-90 s; verdict within 5 s of the final UART frame; report upload asynchronously if the relay link is unavailable.
- **cost:** Usually under $0.01 per run; inference is optional and the dominant cost is local serial collection plus a small report.
- **security:** The fixture must never capture or persist microphone content. UART logs can contain identifiers and paths, so redact device IDs, bearer tokens, and filesystem paths before upload. A failed run should not automatically flash firmware or alter settings; repair actions require a separate explicit command.
- **missing:** The already-requested mac_serial_exchange capability, with bounded read/write, port allowlisting for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, timeout, and byte/line limits; A relay route that accepts a signed diagnostic bundle and evaluates the audio acceptance criteria; A stable machine-readable UART schema for fixture phases, sequence loss, decode/encode timing, and queue state; A report destination that links the failure to a firmware commit and exposes it on the dashboard

### "After you change something in my browser or Mac, show me a plain-language proof of exactly what changed, and let me ask later which changes came from me versus the agent."
- **useful because:** Today an action receipt can say that a job completed, but not establish the before/after fact an owner cares about. A proof-carrying transaction would preserve a redacted before-state fingerprint, the exact action, an after-state fingerprint, URL/app identity, and timestamp, then speak only the useful delta on the pendant. It makes automation auditable without requiring the owner to watch the screen.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** Deterministic state fingerprints and diffing first; cheap model only converts a structured diff into one short sentence. No realtime model is needed for storage or verification.
- **latency:** Verification within 2 seconds of each action; spoken result within 4 seconds; historical queries under 5 seconds.
- **cost:** Under $0.01 per transaction; storage and hashing dominate, with one optional small summarization call.
- **security:** Never store raw passwords, tokens, page bodies, or screenshots by default. Use field-level redaction and salted hashes, retain only the minimal diff, and let the owner delete a transaction history. A hash proves consistency, not truth, so the receipt must name its evidence source and limitations.
- **missing:** A shared transaction receipt schema with before/after evidence and redaction metadata; Browser and Mac adapters that can produce stable semantic fingerprints rather than UI coordinates; A relay query that can compare receipts across browser, Mac, and pendant events; A dashboard and pendant summary path for owner-readable diffs

### "Before I click or submit on this page, tell me from the pendant whether the page, domain, and requested permissions look suspicious, and explain the warning in one sentence."
- **useful because:** The browser can see authenticated page state that the pendant cannot, while the relay can correlate the URL, certificate/origin metadata, navigation history, and requested permissions. This gives the owner a just-in-time safety check before a phishing link, OAuth grant, download, or payment form is acted on—without granting the agent permission to submit anything.
- **path:** pendant → browser-extension → relay-realtime → mac-planner → dashboard
- **model tier:** Deterministic checks for origin changes, punycode, mixed content, permission scope, download type, and known-unsafe indicators; a small background model may explain a structured finding. Realtime is used only when the owner asks aloud.
- **latency:** Basic verdict under 500 ms from browser metadata; richer page explanation under 3 s; never block ordinary browsing unless the owner explicitly enables a blocking policy.
- **cost:** Usually near zero for deterministic checks; $0.001-$0.005 for an optional explanation of a complex permission or form.
- **security:** Page content and URLs can be sensitive. Send only origin, permission names, form field types, and redacted labels by default—not credentials or full page text. The result must be advisory, not a guarantee; the agent must never silently click through a warning or submit a form.
- **missing:** A browser security-observation event that exposes origin transitions, permission requests, downloads, and form field classes; A local URL/origin reputation and IDN/mixed-content checker; A relay policy that separates advisory warnings from any optional owner-enabled block; A pendant alert type that can interrupt audio with a short warning and restore the prior audio state

### "Let me mark a browser tab or Mac window as private from the pendant, and guarantee that its text, URL, screenshot, and action history never leave this Mac until I explicitly release it."
- **useful because:** The current privacy latch protects the pendant's microphone and speaker, but it cannot express that one work tab or document must remain local while other automation continues. This gives the owner selective privacy instead of an all-or-nothing shutdown: the assistant can still act on ordinary tabs and answer, while the marked surface is excluded from perception, model context, logs, receipts, and spoken summaries.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** Local deterministic tagging and enforcement; no model call for the privacy decision. The relay only receives an opaque surface identifier and state transition, never the protected content.
- **latency:** Apply locally in under 200 ms; relay acknowledgement under 2 s; release and re-synchronization must require an explicit owner command and complete before observation resumes.
- **cost:** Negligible API cost; the main work is local filtering, lifecycle handling, and testing crash/reconnect cases.
- **security:** The guarantee must hold across browser heartbeats, screenshots, UI snapshots, action receipts, crash recovery, and queued relay events. Protected content should be excluded before serialization, not redacted after upload. The pendant needs a clear local LED/inbox state, and the owner must be able to clear the mark locally if the network is down.
- **missing:** A Mac-local exclusion broker consulted before every browser observation, Mac observation, action receipt, and journal write; A browser extension command to tag a tab by opaque session identity without sending its URL; A relay-side opaque privacy state with fail-closed reconnect behavior; A persistent local protected-surface manifest and a way to recover it after browser or agent restart


## What it asked for

_Nothing._
## Its own summary

I established that the Mac is materially more capable than the old record: Accessibility and Screen Recording are now trusted, synthesized input is verified, Safari is foreground, and the pendant agent can reach the screen. I produced three non-duplicate capabilities: a pendant-controlled focus sprint, a spoken walk-away safety lock that freezes Mac/browser execution, and an end-to-end pendant health check using the shipped diagnostic fixture and the two physically connected serial chips. The first bookmark-context idea collided with an existing capability and was intentionally not restated.

**Biggest unknown:** The blocking missing seam is still bounded serial exchange for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; I cannot run or verify the health check without it. Separately, browser inspection remains resolver-ambiguous between action:browser_inspect and POST /browser/inspect, and the proposed focus/safety flows need explicit relay freeze/resume primitives rather than more Mac actions.

