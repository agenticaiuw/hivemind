# Harness derivation — mac-planner — round 298

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-permissions** — Live Mac agent now has Accessibility and Screen Recording granted for AI Pendant Agent; synthesized input reaches screen, automation grants are complete, relay and browser bridge are online.
  - evidence: GET /ops/status at 2026-08-09T04:07Z returned trusted:true, screenRecording granted:true, eventsPost:true, requiredMissing:[]; browser online and relay reachable.

## Capabilities it proposed

### "When I say “save what I’m looking at,” capture the current browser page, the exact selected text or timestamp if available, and turn it into a dated note with a follow-up reminder—without making me switch apps."
- **useful because:** The pendant becomes a one-sentence capture button for research and videos: browser context supplies the source, the Mac makes durable artifacts, and the owner can keep listening or walking. It is materially better than a generic voice memo because the URL, title, selected passage, and due date are attached automatically.
- **path:** pendant voice/button → relay-realtime → browser extension → Mac local agent → Notes and Reminders
- **model tier:** Realtime only for the spoken command and intent extraction; deterministic browser inspection and note/reminder creation afterward, no background LLM required.
- **latency:** Acknowledge in under 1 s; inspect and create the note in 3–8 s. If browser inspection is unavailable, save the spoken memo and report the missing context rather than guessing.
- **cost:** Usually one short realtime turn; roughly $0.01–$0.05 depending on audio duration. Browser inspection, Notes, and Reminders are local and free.
- **security:** Read only the active tab and explicitly selected text; redact passwords/form fields. Creating a reminder is owner-authorized, but sending mail, purchases, or destructive actions remain out of scope. The note should retain the source URL and capture time so it is auditable.
- **missing:** A reliable disambiguated browser-inspect invocation (the current read-only resolver ties action:browser_inspect and POST /browser/inspect); A structured selected-text extraction field from the browser bridge; A small relay transaction that links the pendant utterance, browser snapshot, note ID, and reminder ID

### "Run a “prove the pendant is healthy” check now, using the pendant over USB, and give me one plain-English result plus a saved diagnostic report if anything is wrong."
- **useful because:** The owner currently has physically connected hardware but no LTE registration, so waiting for a production call hides failures. This would exercise the real capture/encode/modem/playback path on the bench, correlate the Mac serial log with relay telemetry, and turn an intermittent audio defect into a reproducible report.
- **path:** pendant USB serial → Mac terminal/agent → relay → pendant audio fixture → Notes or workspace
- **model tier:** No expensive model for the test; use deterministic thresholds. Use a cheap text model only to summarize a failed receipt into one spoken sentence.
- **latency:** Start immediately, finish a normal run in 30–90 s, and stream progress only on failure or timeout.
- **cost:** Negligible API cost; local serial and fixture execution dominate. A failed-run summary is under $0.01.
- **security:** The fixture must use synthetic audio only and never persist microphone content. USB commands must be allowlisted to the diagnostic trigger and bounded read; never expose a general serial shell. Save logs under ~/AI-Pendant-Workspace with redaction of bearer tokens and paths where possible.
- **missing:** A first-class bounded UART diagnostic action that can arm audio_path_diagnostic_fixture, read sequence-numbered output, enforce a timeout, and return exit status; A relay endpoint that accepts the fixture receipt and joins it to pendant pipeline telemetry; A deterministic acceptance evaluator for alias rejection, codec CPU, mic drops, tx starvation, and audible-preamble checks

### "When I finish a meeting, say “close the loop” and have the system collect the meeting’s calendar entry, the notes I made, and the browser tabs I used, then draft three follow-ups and place them in a review note—do not send anything."
- **useful because:** This is the missing bridge between attention and execution: the pendant can mark the end while the Mac knows the calendar and open work, and the browser contributes the actual artifacts. The owner gets a reviewable handoff instead of a vague promise or an automatically sent message.
- **path:** pendant → relay-realtime → Mac Calendar/Notes → browser extension → Mac local agent
- **model tier:** Use a cheap background text model for clustering notes and proposing three actions; realtime is only for the short command and confirmation that a draft was created.
- **latency:** Acknowledge immediately, then produce a draft in 15–45 s. Never block the next interaction while the draft is being assembled.
- **cost:** One small summarization call, about $0.01–$0.05; Calendar, Notes, browser metadata, and draft creation are local.
- **security:** Read only the selected calendar event window and explicitly associated notes/tabs. Do not infer attendees or send messages. The output is a draft note with provenance links and confidence per action; sending or creating external tasks remains a separate owner command.
- **missing:** A durable meeting correlation record that can bind a pendant end marker to one calendar event, a bounded time window, and browser session IDs; Read-only Notes search/export with note identifiers (not only creation); A provenance-preserving planner that cites each proposed follow-up to a note, calendar field, or page before writing the draft

### "Start a time-boxed delegation: “Work on this browser task for 20 minutes, and stop if I press the pendant button.” I should be able to hear progress, cancel from the pendant, and receive either a completed result or a precise checkpoint—not a half-finished mystery job."
- **useful because:** Today the Mac and browser can act, but the owner cannot safely hand off a bounded task while walking away and reclaim it from the one device always on their body. A lease with a hard deadline, wearable cancellation, and a checkpoint makes delegation trustworthy across the relay, browser session, and Mac executor.
- **path:** pendant button/voice → relay → Mac local agent → browser extension → workspace/job ledger
- **model tier:** Cheap text planning for the task; realtime only for spoken start/cancel/progress. Deterministic execution and checkpointing should not consume the expensive conversational tier.
- **latency:** Start acknowledgement under 2 seconds; cancellation reaches every active surface within 1 second; deadline produces a checkpoint within 5 seconds.
- **cost:** Usually one short planning turn, roughly $0.01–$0.05; execution is local. Cost is dominated by any long browser reasoning loop, not the control channel.
- **security:** The lease must carry an owner-visible scope, expiry, touched resources, and cancellation generation. Cancellation must be idempotent and stop queued browser/Mac steps, while preserving only a redacted checkpoint. Never silently continue after expiry or reinterpret a cancel as completion.
- **missing:** A cross-surface lease primitive with expiry and cancellation generation shared by relay, browser commands, and Mac jobs; A pendant event path for cancel/status that remains available while LTE is absent or the Mac link is intermittent; A checkpoint schema that records completed actions, pending action, and reversible cleanup without claiming success

### "Bring the result from the site I’m using into my project: download the authenticated artifact, verify it, put it in the right workspace folder, and open it in my editor with a note showing where it came from and what changed."
- **useful because:** This closes a real browser-to-desktop gap. Today an authenticated browser session can see a result and the Mac can manipulate files, but the owner must manually bridge the two and can lose provenance or accept a truncated download. A verified, atomic handoff makes private browser work become usable project work.
- **path:** browser extension → relay → Mac local agent → atomic workspace → VS Code/editor
- **model tier:** Deterministic browser download and SHA-256 verification; a small model is needed only to infer the destination folder from the owner’s command and to summarize a diff.
- **latency:** Preview destination and source in 2 seconds; complete in under 20 seconds for ordinary files; leave a recoverable staged artifact on timeout.
- **cost:** Near-zero model cost for explicit paths, up to $0.02 for destination/diff summarization. Network transfer and hashing dominate latency, not API spend.
- **security:** Never expose authenticated page contents to the relay beyond the minimum transfer metadata; keep downloads on the Mac. Require an exact-source URL, destination, expected type/size bounds, and hash receipt. Do not overwrite an existing file silently; preserve the old version and provenance.
- **missing:** A browser command that streams or hands off a completed download with content hash and source metadata rather than only page text; A Mac-side atomic browser-download-to-workspace operation that can validate size/type/hash before rename; A provenance sidecar format linking browser session, source URL, download hash, destination, and editor-open receipt

### "If a delegated browser task hits a login, MFA, consent, or CAPTCHA wall, tell me exactly what is blocking it on the pendant, let me take over that browser tab, and resume the same task automatically when I’m done—without repeating earlier steps."
- **useful because:** Authenticated sessions are where automation fails in real life. Instead of a generic error or silently retrying, the browser, Mac, relay, and pendant would form a controlled human-in-the-loop handoff. The owner supplies only the sensitive step and gets the task back at the exact checkpoint.
- **path:** browser extension → Mac local agent → relay → pendant voice/audio → job ledger
- **model tier:** Deterministic blocker classification and checkpoint resume; realtime only to explain the blocker and accept “take over/resume.” Use a cheap model to summarize page labels, never to solve CAPTCHA or handle credentials.
- **latency:** Detect and announce a blocker within 3 seconds; owner takeover should be one spoken command; resume within 5 seconds after the bridge reports control returned.
- **cost:** Usually under $0.01 because the work is local state management; model spend is limited to a short blocker explanation.
- **security:** Credentials, MFA codes, and CAPTCHA contents stay in the browser and are never sent to the relay or model. Pause all automation while owner control is active, bind resume to the same tab/session and checkpoint hash, and invalidate the checkpoint if the page origin changes.
- **missing:** A browser-side semantic blocker event with origin, reason class, tab/session ID, and a safe redacted preview; An explicit takeover/release handshake between browser extension and Mac executor; A resumable action graph whose completed steps are idempotent and whose checkpoint is invalidated on navigation or origin change; Pendant delivery of blocker alerts with a one-command resume/cancel response


## What it asked for

_Nothing._
## Its own summary

Three new end-to-end capabilities were recorded: (1) pendant command “save what I’m looking at” that joins active browser context to a dated Note and optional Reminder; (2) a synthetic, USB-bench “prove the pendant is healthy” run that correlates the accepted audio fixture with relay telemetry and leaves a report; and (3) “close the loop” after a meeting, which binds the pendant marker to Calendar, Notes, and browser artifacts and drafts three cited follow-ups without sending them. The meeting close-loop handoff is the highest-value proposal: it turns a worn-device moment into reviewable work using every node. Live state changed materially: Accessibility, Screen Recording, automation, relay, and browser bridge are all ready now.

**Biggest unknown:** The remaining blocker is not Mac permission. Browser inspection is currently ambiguous between action:browser_inspect and POST /browser/inspect, and there is no first-class selected-text/provenance contract. For the hardware check, a bounded UART diagnostic trigger/read/receipt is still needed; I will not assume the rejected general serial-session capability exists. Notes search/export and a durable meeting-correlation record also remain unverified.

