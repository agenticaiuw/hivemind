# Harness derivation — mac-planner — round 272

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-state-2026-08-09T01:44Z** — Safari is foreground; 15 apps are running. AI Pendant Agent has Accessibility and Screen Recording, synthesized input verified, and secure input is off. Four browser sessions are present. No workbench contexts are open.
  - evidence: mac_readonly_inspect foreground_app returned GET /observe HTTP 200 at 2026-08-09T01:44:01Z; GET /workbench/contexts returned {contexts:[]}.

## Capabilities it proposed

### "Give me a 'what changed since I last checked' briefing across my Mac, authenticated browser sessions, calendar/mail, and iPhone, ranked into only three actions; when I say 'open the first one', take me to the correct surface and preserve the other two as a queue."
- **useful because:** The existing morning brief is a snapshot and browser tabs are isolated from it. This answers the owner's real question—what requires attention now—without making them scan four surfaces, and it can resume the exact web page or iPhone app rather than merely naming it.
- **path:** relay → pendant → mac-planner → browser → iOS → dashboard
- **model tier:** Use a background model for deduplication, change detection, and priority ranking; use realtime only to deliver the short spoken result and interpret follow-up commands. Deterministic adapters should collect sources and launch the selected surface.
- **latency:** Collect in 5–10 seconds and speak a three-item result in under 2 seconds after collection. If iPhone/browser is unavailable, say which source is stale instead of blocking the whole brief.
- **cost:** $0.01–$0.04 per run, mostly the ranking context across source summaries; source reads and action execution are local/relay overhead.
- **security:** Browser and phone sessions can contain private data. Send only redacted titles, domains, sender names, and calendar metadata to the ranker; never upload page bodies or message bodies by default. Opening a selected item is allowed under the owner's browser policy, but sending mail, deleting, or purchasing remains confirmation-required.
- **missing:** A per-source cursor or last-seen ledger for browser sessions and iPhone state; An iOS read adapter for notification/app deltas rather than UI scraping; A unified ranked-action record that survives until the owner consumes or dismisses each item

### "If a Mac or browser action fails while I am away, tell me on the pendant exactly what failed, whether anything changed, and offer the safest idempotent retry; if it succeeds, give me a one-line receipt with the app/page and files touched."
- **useful because:** Today a failed desktop job is easy to miss and a generic status answer cannot tell the owner whether retrying is safe. This makes unattended automation trustworthy: the owner gets a compact spoken outcome, while the Mac receipt remains the audit trail and retries do not duplicate completed work.
- **path:** relay → pendant → mac-planner → browser → dashboard
- **model tier:** No expensive realtime reasoning for the normal path. A background model classifies the receipt into success/partial/failure and drafts one sentence; deterministic code decides retry eligibility from action type and receipt state. Realtime only answers follow-up questions.
- **latency:** Emit a pendant alert within 3 seconds of the final receipt; retry preview within 2 seconds. Never auto-retry an unknown or partial mutation.
- **cost:** Under $0.005 per job outcome for small receipt classification; almost all work is local receipt parsing and notification delivery.
- **security:** Receipts can leak file paths, URLs, or typed text. Redact contents and secrets, retain only app/domain, operation class, and touched-resource hashes unless the owner asks for detail. Retry must be limited to explicitly idempotent reads/opens and require confirmation for sends, deletes, purchases, or arbitrary shell.
- **missing:** A relay push route that subscribes to Mac job receipt completion/failure; A formal idempotency annotation on each Mac/browser action type; A pendant alert payload that can carry a short failure reason plus a retry token

### "When I say “secure my workspace” or press the pendant’s dedicated security control, lock or sign out of every supported Mac, browser, and iPhone session, close sensitive pages, and confirm on the pendant which surfaces were secured; “restore my workspace” should reopen only the previously recorded non-sensitive pages after local authentication."
- **useful because:** The owner cannot currently secure all active surfaces as one action. Browser sessions, Mac apps, and iPhone Mirroring can remain exposed when they walk away. A physical pendant control would make privacy dependable even when the owner cannot reach the laptop quickly.
- **path:** pendant → relay → mac-planner → browser → iOS → dashboard
- **model tier:** Deterministic policy engine for session inventory, locking, and restoration. Use realtime only for spoken confirmation; no model should decide whether an app or URL is sensitive. A background model may suggest classifications but cannot authorize them.
- **latency:** Begin locking within 1 second of the local control event; report completion or unavailable surfaces within 5 seconds. Restoration can take up to 15 seconds and must be explicit.
- **cost:** Below $0.01 per invocation; the cost is device/session integration and local key management, not inference.
- **security:** This feature itself controls sensitive sessions. Require a local device-bound cryptographic credential and an explicit owner policy for which apps may be closed versus merely locked. Never transmit passwords, cookies, page contents, or unlock credentials through the relay. If the pendant is lost, provide server-side revocation.
- **missing:** A device-bound authentication/key store on the pendant or companion Mac; Mac APIs for locking/closing supported applications without indiscriminately killing unrelated work; Browser session suspend/resume with a sensitive-URL policy; An iPhone Mirroring control adapter that can lock or terminate the mirrored session; A relay revocation and lost-device workflow

### "Before my next meeting, tell me whether my calendar, recent mail, and open browser work disagree—for example, a meeting moved but the old conference tab is still open, or a promised document is not ready—and give me one concrete repair action."
- **useful because:** The owner currently receives separate snapshots, not a check for contradictions between them. Catching stale links, moved meetings, missing attachments, and conflicting commitments before the meeting prevents the kind of failure that no single app can see.
- **path:** relay → pendant → mac-planner → browser → dashboard
- **model tier:** Use a background reasoning model for entity matching and contradiction detection over aggressively redacted metadata; use deterministic rules for dates, URLs, attachments, and open tabs. Realtime only delivers the short warning and accepts the repair command.
- **latency:** Run on demand in under 15 seconds, or automatically 10 minutes before a calendar event. Speak only high-confidence conflicts; uncertain matches become a quiet dashboard suggestion.
- **cost:** Approximately $0.02–$0.08 per run, dominated by cross-source reasoning over calendar/mail/browser metadata. Most extraction is local and bounded.
- **security:** Mail subjects, attendee names, and URLs are sensitive. Keep raw bodies on the Mac; send the model only redacted structured facts and hashes. Repairs such as sending mail or changing calendar events must remain explicit owner actions, never automatic.
- **missing:** A normalized cross-source entity model linking calendar events, mail threads, documents, and browser tabs; A local metadata extractor for mail attachments and open-page state without uploading bodies; A contradiction confidence score and suppression ledger to avoid repeatedly warning about the same conflict; Repair actions for calendar links, attachments, and browser tabs


## Changes it proposed to its own stack

### `hardware` — Replace the prototype's single LED-only status channel with a tiny two-line low-power e-paper or memory-LCD strip on the product pendant, driven over the currently free I2C bus, plus a fuel-gauge IC on the battery rail. Reserve the display for durable, glanceable state: unread alert count, privacy latch, queued audio, connection/profile, and the short job receipt; keep LED patterns for immediate attention. Define a strict redaction mode so message text never appears unless explicitly enabled.
- **owner gets:** The current one LED cannot distinguish recording, staged audio, inbox alerts, privacy, and failures; the owner has to remember blink codes or ask aloud. A glanceable display would make the pendant understandable in a meeting and a real battery percentage would prevent silent failure during LTE bursts.
- effort: Product hardware revision: display module, fuel gauge, enclosure/optical design, I2C driver, display refresh scheduler, and firmware state arbitration. Prototype on the live DK with an external 2-line memory LCD before committing to e-paper; validate readability, shock, and sleep current.  ·  risk: Display burn-in/ghosting, added power draw, and accidental disclosure in public. Recover by keeping the existing LED-only fallback and making all display writes nonessential; if the display driver faults, disable it and preserve audio/privacy behavior. Never show secrets by default.
- cost: Roughly $8–$25 BOM increase for display, flex/connector, and fuel gauge; display refresh adds short bursts (typically milliamps for tens of milliseconds), while the fuel gauge is microamp-scale. Firmware RAM impact likely 2–8 KB for a small framebuffer/state cache.  ·  latency: A status update can lag by 100–500 ms due to refresh; no impact on the real-time audio path if rendered from a low-priority work queue.
- security: A visible display creates shoulder-surfing risk, especially for browser/mail labels. Default to icons, counts, and redacted domains; require an explicit owner setting before rendering text, and make privacy latch blank it immediately.
- depends on: A product enclosure rather than the current nRF9160 development kit; A chosen display with a low-power driver and an I2C address that does not conflict; A battery fuel-gauge IC and battery design; A firmware status-arbitration layer that gives privacy/audio errors priority over routine alerts

### `hardware` — Build the product pendant around a directional/open-ear or bone-conduction transducer with a physically separate microphone enclosure and an optional wired/low-power ambient-noise reference microphone. Add a hardware audio route switch so agent speech can be sent to the private transducer without changing the shipped 24 kHz Opus transport; retain the current speaker as a fallback.
- **owner gets:** The owner could hear the agent while still hearing traffic, coworkers, or a conversation, and would not need to hold a phone to their ear. Separating the microphone and playback paths would also make speaking in public less awkward and reduce acoustic echo.
- effort: New acoustic and enclosure design, transducer driver, mechanical fit testing, echo-cancellation tuning, and firmware routing. The current prototype has one full-duplex I2S peripheral, so the product board may need a codec or a carefully selected digital amplifier with a shared bus; this must be validated with the existing 24 kHz/60 ms path.  ·  risk: Bone conduction can be uncomfortable, leak sound, or sound poor for some users; open-ear audio can reduce situational awareness if levels are excessive. Provide a conventional speaker fallback, hard volume limits, and a local mute/privacy state. Recover from driver failure by reverting to the existing output path.
- cost: Approximately $15–$40 additional BOM and substantial acoustic engineering; active playback power may rise by roughly 10–50 mW depending on transducer and level. No extra model/API cost.  ·  latency: No intentional network latency. Driver and acoustic processing should stay below 10 ms; keep all routing outside the Opus encode/decode critical path.
- security: Private audio is less exposed than an open speaker, but leakage remains possible. Display no content and default to a conservative volume cap; privacy latch must cut both microphone capture and all playback routes.
- depends on: A product enclosure replacing the current nRF9160 development kit; A transducer/codec architecture compatible with full-duplex I2S; Acoustic echo and feedback measurements against the verified 24 kHz path; A hardware privacy/audio-route control integrated with the existing local privacy latch


## What it asked for

_Nothing._
