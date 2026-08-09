# Harness derivation — mac-planner — round 262

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-live** — The AI Pendant Agent currently has Accessibility and Screen Recording trusted, synthesized input verified, and UI actions will reach the screen; foreground app is Safari with four browser sessions/tabs.
  - evidence: mac_readonly_inspect(operation=running_apps) invoked GET /observe at 2026-08-09T00:48:32Z; response accessibility.trusted=true, screenRecording=true, eventsPost=true, inputReachability.status=verified, foregroundApp=Safari.

## Capabilities it proposed

### "When I tap the bookmark button while looking at something on my Mac, turn that exact moment into an actionable task: capture the page or document I was on, infer what I meant to remember, attach the source, and put the next action on my calendar or reminders. Tell me on the pendant if the capture succeeded."
- **useful because:** The existing bookmark remembers a time; this would remember why. It closes the gap between a fleeting tap and a retrievable, source-linked commitment without requiring the owner to stop typing or dictate a note.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Use the realtime tier only for the immediate success/failure utterance; use a cheaper background model to extract the task and deadline from the captured context. The Mac and browser surfaces provide structured context; the relay correlates the event and sends the result back to the pendant.
- **latency:** Acknowledge the tap locally in under 200 ms; capture Mac/browser context within 2 s; deliver a draft task within 10 s. If extraction takes longer, queue it and announce only that the bookmark was safely captured.
- **cost:** About $0.005–$0.03 per capture depending on page/document text and model tier; dominant cost is background extraction, not the tiny event or Mac observation.
- **security:** The capture may include private page text, selected text, or document names. Default to URL/title/foreground-app metadata and require an explicit per-session 'include page text' setting; redact passwords and form values. Creating a reminder/calendar item should be a visible draft unless the owner's policy explicitly authorizes unattended creation.
- **missing:** A deterministic semantic-context read that returns selected text/document identity and a redacted browser snapshot without resolver ambiguity; A relay event contract carrying the pendant bookmark ID plus Mac/browser capture correlation; A task extraction and deduplication worker that can link the result to an existing reminder

### "Watch this logged-in page for a change I care about—like a new reply, a status moving, or a price crossing a number—and only interrupt me when the change is real. When it happens, show me the before/after evidence in the browser, make a dated follow-up on the Mac, and let me dismiss or snooze it from the pendant."
- **useful because:** Today a browser session can be driven, and the pendant can receive alerts, but neither maintains a trustworthy before/after watch with an owner-visible trail. This turns long-running web work into an asynchronous, bounded service instead of repeated manual checking.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → dashboard
- **model tier:** Use a cheap scheduled/delta model for page comparison and a deterministic DOM/selector check first; reserve the expensive realtime model for ambiguous changes or when the owner asks why it fired. The relay owns scheduling and deduplication, the extension owns the authenticated session, and Mac owns the reminder/follow-up.
- **latency:** Poll only at the owner-selected cadence (5 minutes to daily); detect and enqueue within one interval, deliver a compact pendant alert within 2 s of detection, and defer full explanation until requested.
- **cost:** Roughly $0.001–$0.02 per check when a deterministic DOM hash suffices; model cost dominates only for semantic comparison. Browser traffic and page rendering dominate device resources, not inference.
- **security:** This is privileged access to logged-in pages. Require an explicit target URL/session, allowed selectors or page regions, retention limit for before/after evidence, and an owner-set maximum cadence. Never transmit passwords, tokens, or full page dumps to the relay; encrypt and expire evidence. Creating a reminder is a mutation and must follow the owner's runtime policy, which is currently not configured.
- **missing:** A durable page-watch definition with selector/semantic predicate, cadence, expiry, and last-seen hash; A browser-side authenticated watch runner that can return redacted before/after evidence without exposing session cookies; A relay scheduler and pendant alert action that supports dismiss/snooze state transitions

### "Run a complete pendant health check from my Mac: exercise the real microphone/uplink and speaker/downlink path, measure packet loss, Opus timing, clipping and underruns, then give me a plain-language pass/fail report and save the raw receipt so the next failure can be compared against it."
- **useful because:** The owner currently has to know which serial commands and logs to use to distinguish a modem problem from an audio regression. One command would make the physically connected pendant testable today and turn vague 'your voice sounded bad' reports into comparable measurements.
- **path:** mac-planner → pendant → relay-realtime → dashboard
- **model tier:** No expensive model is needed for measurement. The pendant diagnostic fixture produces counters; a cheap background formatter turns them into a report. Use realtime only if the owner asks a follow-up question about a failed metric.
- **latency:** Start within 2 s, run a bounded 30–90 s fixture, and return a result immediately after the final acknowledgement. Never leave the microphone open after the fixture or on timeout.
- **cost:** Near-zero inference cost for a normal run; dominant costs are USB serial transfer and a small amount of Mac storage. A failed run may incur one short summarization call, under $0.01.
- **security:** The fixture must use synthetic audio and never retain microphone content. Serial access should be limited to the known pendant port, with a run timeout and an immutable receipt containing counters rather than PCM. The report may expose device identifiers, so redact them in dashboard sharing.
- **missing:** A bounded Mac bench runner that can arm the accepted diagnostic fixture over the physically connected USB serial device and parse its structured completion frame; A receipt schema that stores fixture version, firmware build, timestamps and acceptance thresholds for comparison; A relay/dashboard endpoint to compare the newest receipt with the last known-good run and alert only on regression

### "Find a meeting time with these people without making me babysit it: use my real calendar and the authenticated browser session to propose times, track replies and changing constraints, and only wake me on the pendant when there is a final choice or a conflict I must resolve. After I confirm on the pendant, send the invite and leave an audit trail of what was agreed."
- **useful because:** The owner cannot currently delegate the annoying middle of scheduling: calendar and mail are readable, while the browser has sessions nobody else can reach, but there is no single durable negotiation that combines them. This would turn a spoken constraint into a completed meeting rather than another draft or reminder.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background model to extract constraints and classify replies; use deterministic calendar intersection for availability. Reserve realtime for the brief pendant interaction and an expensive model only when a reply is ambiguous. The browser extension handles the authenticated participant-facing session, while the Mac reads calendar state and the relay owns negotiation state.
- **latency:** Capture constraints and acknowledge in under 2 seconds; produce first candidate times within 15 seconds; poll replies on a bounded cadence (for example every 15 minutes) and wake the owner only on a meaningful state change. Sending happens immediately after explicit pendant confirmation.
- **cost:** Approximately $0.01–$0.08 per negotiation, dominated by reply classification and browser page extraction; deterministic calendar intersection and state transitions are negligible.
- **security:** This can send messages and calendar invitations as the owner and exposes participant names, availability, and authenticated webmail content. Require an explicit recipient list, expiration, maximum number of proposals, and a final pendant confirmation token; redact unrelated mail, never expose session cookies, and retain only the negotiation transcript and final decision. The current FULL_CONTROL_MODE has no effective approval policy, so a runtime owner policy must be added before unattended sending is safe.
- **missing:** A durable negotiation state machine with participant constraints, proposal IDs, reply deadlines, deduplication, and cancellation; A write-capable, allowlisted mail/calendar action that can send a proposal or invitation through the authenticated browser or approved Mac automation while returning a verifiable receipt; A pendant confirmation and conflict-resolution protocol, plus a relay scheduler that survives Mac or browser disconnection; An audit record linking every proposed time, reply evidence, owner decision, and final calendar event


## What it asked for

_Nothing._
## Its own summary

Discovered live Mac state and recorded three owner-facing capabilities: bookmark-to-actionable-task capture, authenticated browser change watches with evidence and pendant snooze, and a synthetic end-to-end pendant health check with regression receipts. The Mac is materially more capable than the older context suggested: AI Pendant Agent has Accessibility and Screen Recording trusted, synthesized input verified, and UI actions reach the screen; Safari is foreground with four browser sessions. I do not need to request Accessibility again.

**Biggest unknown:** The missing semantic context contract remains the key blocker: a deterministic, redacted read of selected text/document identity and the active browser page that can be correlated with a pendant bookmark. Browser inspection is also currently resolver-ambiguous, and there is no durable page-watch runner or bounded USB diagnostic runner/receipt comparison path yet. The owner still needs to choose runtime policy entries for unattended reminder creation and browser watches; FULL_CONTROL_MODE itself is not an approval policy.

