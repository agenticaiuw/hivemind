# Harness derivation — mac-planner — round 291

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac TCC and live UI reachability** — AI Pendant Agent now has Accessibility and Screen Recording, synthesized input is verified landing, secure input is false, and 18 apps are running; foreground is loginwindow. The previously blocked UI automation surface is now operational for this binary.
  - evidence: mac_readonly_inspect operation=running_apps and foreground_app both invoked GET /observe at 2026-08-09T03:40:14Z; response accessibility.trusted=true, screenRecording=true, eventsPost=true, inputReachability.status=verified.

## Capabilities it proposed

### "“Start my next meeting.”"
- **useful because:** The system should turn calendar intent into a coordinated transition instead of merely opening a URL: identify the next event, confirm it is soon, open the right authenticated meeting link in the browser, bring the meeting app forward, and tell the owner through the pendant what was opened and when it ends. If the link is absent, it should say exactly that rather than guessing.
- **path:** mac_read_sources reads the next calendar event → relay planner resolves whether 'next' is immediate and prepares a short spoken status → browser session opens the authenticated meeting URL → mac_run_actions launches or foregrounds Zoom/Teams and restores the prior app if launch fails → pendant delivers the concise confirmation over the live audio path
- **model tier:** background for calendar/link extraction; realtime only for the owner's spoken confirmation
- **latency:** Under 5 seconds when calendar data and browser session are warm; up to 15 seconds for app launch
- **cost:** Low: one background planning call plus a few local actions; dominated by model extraction, not device audio
- **security:** Meeting URLs and calendar attendees leave the Mac only as redacted plan fields; never read mail or meeting content. Opening a meeting is an external side effect and must be an owner-configured routine policy, with a dry-run preview when the event is ambiguous.
- **missing:** A calendar-specific next-event/link extractor that returns structured join URL, start time, end time, and conferencing app; A browser action that can target an existing authenticated session without ambiguous browser_inspect resolution; A pendant status event for 'meeting opened' distinct from ordinary reply audio

### "“Run a complete pendant audio health check and tell me whether it is safe to use.”"
- **useful because:** Today the owner cannot distinguish a dead modem, a bad USB connection, packet loss, or a codec regression without engineering knowledge. A single owner-facing check would exercise synthetic uplink and 24 kHz downlink, measure the shipped acceptance thresholds, attach the receipt to a Mac job, and report a plain-language pass/fail without recording private speech.
- **path:** Mac agent launches the bounded USB diagnostic procedure while the pendant and ESP32 bridge are physically connected → accepted audio_path_diagnostic_fixture emits synthetic sequence-numbered frames and the fixed playback fixture → relay correlates fixture counters with pipeline/job receipts and checks alias rejection, CPU, drops, and underruns → mac_workbench_transaction atomically stores the report and raw logs in a dated workbench folder → pendant announces only the result and the failing metric, if any
- **model tier:** No realtime model for measurement; a cheap background model may translate metrics into a short explanation
- **latency:** 60–120 seconds for a full run, with progress events every 15 seconds
- **cost:** Very low API cost; dominated by the on-device fixture and USB serial transfer, not inference
- **security:** Synthetic data only; no microphone capture. Raw logs should be retained locally with a short TTL. A failed check must not silently change firmware or delete existing logs.
- **missing:** A bounded, receipt-producing USB serial bench runner; current inventory has no serial/USB route and run_shell receipts cannot prove exit status; A parser that turns the fixture's counters into the explicit acceptance criteria; A relay endpoint to attach a diagnostic report to a device and expose historical pass/fail

### "“Bookmark what I’m looking at.”"
- **useful because:** A physical button press should capture the moment, not just a timestamp. The pendant can mark the instant even offline; the Mac can immediately enrich it with the foreground app, window title, selected text when safe, active browser URL, and a screenshot or document path, then the relay makes one searchable moment card. This turns fleeting research and interrupted work into something recoverable without requiring the owner to speak or stop typing.
- **path:** offline_moment_bookmark records the durable timestamp/event on the pendant and queues it across a dropped link → mac_readonly_inspect reads foreground app, browser session, and UI snapshot now that Accessibility and Screen Recording are verified → relay joins the pendant event to the nearest Mac observation by monotonic timestamp and redacts passwords/secure-input fields → mac_workbench_transaction writes a small Markdown/JSON moment card atomically into the owner's workbench → later voice query searches the captured cards and the pendant can read back the title and link
- **model tier:** Cheap background model for OCR/summary only when the owner asks; no model is needed to capture structured state
- **latency:** Capture acknowledgement under 300 ms locally; Mac enrichment within 2 seconds; deferred enrichment if the link is down
- **cost:** Near-zero for structured captures; optional screenshot OCR is the dominant cost and should be opt-in
- **security:** Screen contents may contain secrets. Default to app/title/URL only, redact secure-input and password fields, and make screenshots/selected text explicit owner policy. Never upload the raw screenshot automatically; store locally and expire it.
- **missing:** A real relay event joiner between pendant bookmark timestamps and Mac observations; A semantic UI snapshot/selected-text reader with deterministic redaction; current ui_snapshot is host-state oriented; A local searchable moment-card index and retention controls; A pendant-to-Mac event transport while LTE is unregistered (USB is currently bench-only, so live capture needs the registered relay path)

### "“Check this message and send it if it looks right.”"
- **useful because:** This would be the system's highest-value everyday action: catch wrong recipient, missing attachment, stale quoted text, accidental secrets, and an inconsistent tone before an irreversible send. The Mac can inspect the actual draft in Mail or a logged-in browser, the relay can reason over a redacted representation, and the pendant can give the owner a compact diff and require an explicit spoken/button confirmation. It is useful precisely because no single node can both see the private draft and safely obtain confirmation away from the screen.
- **path:** mac_readonly_inspect captures the foreground app, draft window identity, selected text and attachment metadata with redaction → browser session inspection handles webmail drafts that Mail cannot access, without exposing cookies to the relay → relay planner checks recipient/subject/body/attachments against the owner's stated intent and produces only a redacted issue list → pendant speaks the proposed changes and waits for a deliberate confirmation event → mac_run_actions applies only the approved edits and clicks Send in the correct app; a receipt records exactly what was sent
- **model tier:** Realtime only for the short confirmation conversation; background model for draft linting and secret detection
- **latency:** 2–5 seconds for inspection and linting; confirmation waits indefinitely; send action under 2 seconds after confirmation
- **cost:** Moderate per use, dominated by one background reasoning call over the redacted draft; no cost when no message is selected
- **security:** Message contents and recipients are extremely sensitive. Keep raw body on the Mac, send the relay only a minimized/redacted view, never auto-send, show exact recipient and attachment names, and make the confirmation token single-use and bound to a content hash. If secure input or redaction is uncertain, refuse to send.
- **missing:** A deterministic semantic draft reader for Mail and browser webmail with attachment metadata and content hashing; A redaction/secret scanner that runs locally before any model call; A pendant confirmation protocol tied to a displayed or spoken content hash; A send-specific action receipt that proves the final body/recipient set, not merely that a click occurred

### "“Put these files in my travel pack so I can retrieve them from the pendant, then delete the pack after I get home.”"
- **useful because:** The owner should be able to leave the Mac without losing access to the exact documents needed on the road. The Mac would select and encrypt the files, the relay would hold only ciphertext with an expiry, and the pendant would expose a tiny, searchable manifest and deliver one requested file or a spoken summary. This is a genuinely cross-node capability: the Mac has the files, the relay survives sleep, and the pendant is the only interface away from the desk.
- **path:** Mac reads a user-selected file set and creates an encrypted, content-addressed pack → relay stores ciphertext, expiry, and a manifest while the Mac is offline → pendant requests a manifest or one item over its registered link and presents it through the existing audio path → Mac or relay records retrieval receipts and automatically destroys the pack at the owner's expiry condition
- **model tier:** Background model only for optional manifest descriptions; no expensive realtime inference is needed
- **latency:** Pack creation under 10 seconds for ordinary documents; manifest response under 2 seconds; individual retrieval limited by LTE and file size
- **cost:** Low model cost; storage and cellular transfer dominate. Large files should be opt-in and metered
- **security:** End-to-end encryption with keys held by the owner's devices, never plaintext in the relay; explicit file list and expiry; no silent inclusion of Downloads or browser caches; deletion requires verifiable tombstone receipts but must tolerate an offline device
- **missing:** An end-to-end encrypted pack primitive spanning Mac, relay, and pendant; Pendant manifest browsing and bounded file delivery, distinct from spoken reply audio; A key agreement and revocation design for a lost pendant or sleeping Mac; A durable expiry/deletion coordinator that works when one node is offline

### "“When I arrive at my desk, restore the work state I left yesterday, but only the things I marked as safe.”"
- **useful because:** The owner should not have to reconstruct a project from memory after travel, sleep, or a reboot. A marked work state would restore browser tabs in their authenticated sessions, selected files, relevant app windows, and the last unfinished action, while refusing unmarked or sensitive surfaces. The pendant supplies the physical continuity signal and can offer a one-button resume; the Mac performs the restoration and the relay keeps the plan through downtime.
- **path:** Mac captures an owner-marked state across apps, browser sessions, files, and pending jobs → relay stores a signed, redacted state manifest and waits through Mac sleep → pendant announces that a resumable state exists and accepts a local confirmation → Mac restores only the allowlisted surfaces, verifies each result, and reports omissions instead of pretending completion
- **model tier:** Cheap background model for naming and deduplicating state; realtime only for the short resume interaction
- **latency:** Offer within 1 second of the desk-arrival signal; restore in under 20 seconds for a normal project
- **cost:** Low inference cost; local snapshotting and browser/app launch time dominate
- **security:** Never persist cookies, passwords, secure-input text, or arbitrary screen images. State must be explicitly marked safe per app/resource, signed to prevent replay, and revocable. A failed restore must not close the owner's current work.
- **missing:** A reliable owner-controlled arrival/presence signal; current pendant has no IMU or proximity sensor; A state manifest schema that can represent browser tabs, app documents, and safe-to-reopen boundaries; Transactional restore with per-surface verification and non-destructive conflict handling; A pendant confirmation event bound to the specific signed manifest

### "“Answer this using my private files, but do not send the files off my Mac.”"
- **useful because:** The owner should get the benefit of the relay's reasoning without choosing between blindness and data leakage. A local Mac retrieval tier would search and quote only the minimum passages, redact secrets, and return a verifiable evidence bundle; the relay would reason over that bundle and the pendant would speak the answer with citations back to filenames and locations. The owner could finally use private context in voice conversations without uploading their whole drive.
- **path:** Mac performs local indexing and retrieval over explicitly selected folders, producing minimal quoted spans and hashes → relay receives only the bounded evidence bundle and answers or asks for a narrower retrieval → pendant speaks the answer and lets the owner request the source name or next evidence span → Mac records a local audit of exactly which passages were released and supports immediate revocation/deletion
- **model tier:** Background local embedding/retrieval; realtime relay reasoning only after the evidence bundle is minimized
- **latency:** First answer in 3–8 seconds for indexed folders; under 1 second for a repeated query
- **cost:** Moderate one-time local indexing; per-query model cost is small because context is bounded. No raw-document egress
- **security:** The local index itself is sensitive and needs encryption, folder-level policy, and retention. Evidence must be length-limited, secret-scanned, and tagged with a release reason. Hashes must not be treated as proof of harmless content; the owner needs a visible local audit and a kill switch.
- **missing:** A Mac-local retrieval/index service with folder policies and encrypted storage; A relay protocol that accepts evidence bundles rather than raw files and preserves provenance; A secret/redaction scanner whose decisions are visible and overridable only by explicit owner action; A voice command and pendant control for narrowing, revoking, or deleting a released evidence bundle


## What it asked for

_Nothing._
## Its own summary

Round 291 produced four owner-facing proposals: coordinated “start my next meeting,” a full pendant audio health check, physical-button bookmark enriched with Mac context, and (highest-value) draft lint + explicit pendant confirmation before sending messages. Fresh live fact: Accessibility and Screen Recording are now granted to AI Pendant Agent, synthesized input is verified, and secure input is off; the Mac is genuinely UI-automatable now. I still need a deterministic semantic UI/draft reader with local redaction, a pendant↔Mac bookmark event joiner, a bounded USB diagnostic runner with exit-code receipts, and a browser action resolver that removes the current browser_inspect ambiguity. The owner must also define policies for screenshots, selected text, and unattended meeting opening; I did not assume them.

**Biggest unknown:** Whether the existing /prepare and /approve routes can be safely bound to a content-hashed, one-use pendant confirmation, and whether any live route already exposes structured Mail/browser draft contents without scraping.

