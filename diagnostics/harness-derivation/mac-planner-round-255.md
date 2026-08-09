# Harness derivation — mac-planner — round 255

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-live** — The AI Pendant Agent currently has Accessibility and Screen Recording, synthesized input is verified, and ui actions should reach the screen. This is a live change from the earlier denied state; the host foreground is loginwindow, with 20 apps running and four browser sessions.
  - evidence: mac_readonly_inspect(operation=running_apps) resolved to GET /observe at 2026-08-09T00:26:57Z and returned accessibility.trusted=true, eventsPost=true, screenRecording=true, inputReachability.status=verified.

## Capabilities it proposed

### "Give me the top world and US headlines from the last 12 hours as three short spoken sentences, and let me ask “why?” about any one of them."
- **useful because:** The owner has asked for this repeatedly, and a news tab is already open. It gives a genuinely hands-free briefing rather than making them read a browser page, while keeping follow-up grounded in the same retrieved articles instead of hallucinating a second answer.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Use the background tier to fetch, deduplicate and rank public headlines; use realtime only to speak the three-sentence digest and answer a follow-up from cached article excerpts.
- **latency:** Under 20 s for collection and synthesis; under 1.5 s to begin playback after the owner asks; follow-up under 3 s.
- **cost:** Roughly $0.01–$0.05 per brief, dominated by article extraction and one short synthesis; follow-ups can reuse cached excerpts cheaply.
- **security:** Public pages only by default; no authenticated session needed. Cite source names and timestamps in the stored note, discard unrelated page content, and do not click or subscribe. The pendant should receive only the short spoken result plus compact source ids.
- **missing:** A scheduled or on-demand browser research job that can reliably collect the last-12-hour window rather than relying on a stale open tab.; A compact article-cache/grounding record shared between the background researcher and realtime follow-up.; A pendant command/event to select a headline index during playback or by voice.

### "If one of my morning or evening routines fails, tell me on the pendant what failed, retry only safe steps on the Mac, and leave me a short recovery note instead of silently marking it complete."
- **useful because:** The owner already relies on scheduled briefs, research, and tidy jobs. A silent failure is worse than no automation: this makes the hive dependable by combining relay scheduling, Mac receipts, and a wearable alert, while avoiding duplicate file changes through an idempotent transaction.
- **path:** relay-realtime → mac-planner → pendant → mac-vision
- **model tier:** Use a cheap background/scheduled model to classify the receipt and draft a recovery action; use realtime only if the owner asks what failed or says retry.
- **latency:** Detect within 1 minute of a failed job; alert delivery when the pendant reconnects; safe retry within 30 s after classification.
- **cost:** Usually under $0.01 per failure; most work is deterministic receipt inspection, with model cost only for ambiguous recovery text.
- **security:** Never retry send-mail, delete, purchase, or other high-impact mutations unattended. Store redacted receipts with command names, touched paths and hashes, not page contents or secrets. A retry must use the existing workbench job id to deduplicate and produce a receipt.
- **missing:** A routine supervisor that correlates scheduled jobs with Mac execution receipts and distinguishes failed, partial and completed.; A policy-configured safe-retry classifier; the current FULL_CONTROL_MODE bypasses risk scoring and must not be treated as an approval policy.; A relay-to-pendant failure alert path with severity and expiry fields.

### "Ten minutes before a calendar meeting, prepare me hands-free: tell me who it is with, open the relevant meeting link and notes on the Mac, and put the three things I need to remember into the pendant inbox."
- **useful because:** This is a concrete hive-only workflow: Calendar knows the appointment, the browser holds the authenticated meeting session, the Mac can stage the working set, and the pendant can brief the owner while they are walking. It reduces the frantic context switch before calls without sending or joining anything automatically.
- **path:** relay-realtime → mac-planner → browser-extension → pendant → mac-vision
- **model tier:** Use a scheduled/background model to match calendar attendees and notes to recent files/tabs; use realtime only for the short spoken briefing or a user-requested correction.
- **latency:** Start preparation 10 minutes before the event; Mac staging under 20 s; pendant alert within 2 s of preparation completion; spoken answer under 3 s.
- **cost:** About $0.01–$0.04 per meeting, dominated by matching/summarizing notes; calendar and deterministic file/tab reads are local.
- **security:** Meeting titles, attendees and notes are private. Redact sensitive bodies in logs; only open the meeting URL and local notes, never click Join, send messages, or alter the calendar without an explicit command. Respect the owner's existing destructive-action confirmation policy.
- **missing:** A meeting-preparation orchestrator that joins calendar events to notes, files and browser tabs with confidence and expiry.; A safe Mac staging plan that can open several resources without stealing focus and returns a receipt.; A pendant alert payload that supports three concise bullets and a meeting-time expiry.

### "After I ask you to do something online or on my Mac, let me ask “did it really happen?” and get an evidence-backed answer: the final state in the browser or app, what changed, and a link or receipt I can inspect."
- **useful because:** Today an action receipt can say that a command was attempted, but that is not the same as the outside world accepting it. This capability closes the most important trust gap: the owner can distinguish 'the Mac clicked Send' from 'the message appears in Sent', or 'the file was moved' from 'the destination contains the expected bytes'. It should verify state after execution rather than merely replaying logs.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → pendant
- **model tier:** Use deterministic read-back checks first; use a background model only to reconcile mismatched evidence and explain it. Realtime is reserved for the owner's short spoken question and answer.
- **latency:** Begin verification immediately after an action; common checks under 5 s, with a clear pending state for sites that settle asynchronously. Spoken answer under 2 s once evidence arrives.
- **cost:** Usually under $0.01 per verification; browser/app read-back is the dominant work, with model use only for ambiguous comparisons.
- **security:** Verification may read sensitive pages, mail folders or files. Scope each check to the resource named in the action, redact content in logs, and return a proof summary rather than copying private bodies to the pendant. A failed verification must never auto-retry a potentially duplicating external action.
- **missing:** A first-class postcondition/verifier attached to each Mac and browser action, with typed predicates such as file hash, URL/state marker, Sent-folder presence, or visible success status.; A cross-surface evidence record that binds the original intent, action receipt, verification timestamp and redacted observed state.; Browser and Mac read-back routes that can target the exact tab/app/resource without relying on a fragile screenshot.

### "Let me define a personal 'truth check' such as “is the contractor invoice paid?” and have the hive inspect the right sources, reconcile conflicting evidence, and answer with what it found, when, and what is still unknown."
- **useful because:** The owner often needs a current fact spread across an app, a browser session and local records, not a summary of one source. This turns the pendant into a question-answering instrument for real-world state: it should say 'confirmed', 'conflicting', or 'not verifiable' instead of confidently guessing from stale memory.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Use deterministic source selection and extraction where possible; use a cheaper background model to reconcile records. Realtime only speaks the concise result and handles clarification.
- **latency:** Common checks under 10 s, with progressive status if a site is slow; first spoken answer under 3 s when enough evidence exists.
- **cost:** About $0.01–$0.08 per query depending on number of sources; browser reads and authenticated app inspection dominate.
- **security:** Truth checks can expose financial, health or work data. Require explicit source scopes, minimize excerpts, retain provenance hashes rather than raw content, and never mutate a source while checking it. The spoken response should avoid secrets by default.
- **missing:** A user-defined claim schema with source scopes, freshness windows and acceptable evidence predicates.; A cross-source reconciliation engine that labels evidence age, authority and contradiction rather than averaging text.; Stable browser/app semantic reads and a compact provenance store shared with the relay and pendant.

### "When I say “I am driving” or “I am in focus mode,” have the pendant and Mac enforce a temporary attention contract: only urgent items interrupt me, everything else is queued, and after the window ends I get a short catch-up grouped by what changed."
- **useful because:** The owner should not have to manually manage the same interruption policy on every surface. This makes a spoken mode change span the wearable, relay, Mac notifications and browser work without losing information, and it ends with a useful digest instead of an unread pile.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Use deterministic policy routing and event queues; use a cheap background model to group the deferred items at the end. Realtime only acknowledges the mode and speaks urgent alerts or the final digest.
- **latency:** Mode change acknowledged in under 1 s; urgent routing under 2 s; end-of-window digest within 30 s.
- **cost:** Near-zero for routing; roughly $0.01–$0.03 for a grouped catch-up, depending on queued items.
- **security:** The mode must be local and fail closed if the relay is unreachable. Do not infer driving from microphone or location without explicit opt-in. Queue encrypted metadata, suppress message bodies on the pendant, and never silently discard deferred alerts.
- **missing:** A cross-surface attention lease with explicit start, expiry and emergency override semantics.; Mac/browser notification interception and event normalization, not just a pendant inbox.; A durable deferred-event store that can deduplicate alerts and produce an end-of-window digest.


## What it asked for

_Nothing._
## Its own summary

This round produced three new owner-facing capabilities: (1) a last-minute calendar meeting preparer that stages notes/meeting links on the Mac and delivers three bullets to the pendant, (2) receipt-aware routine recovery that alerts on failures and retries only policy-approved idempotent work, and (3) a grounded last-12-hours world/US news brief with source-linked follow-up. The browser-tab handoff idea collided with an existing parked-context capability and was intentionally not rephrased. Live discovery also found Accessibility and Screen Recording are now granted and input reachability is verified, despite the older denied context; I recorded that finding.

**Biggest unknown:** The semantic Mac context read is still unavailable/queued, and browser inspection is currently ambiguous between two equally scored implementations. Those gaps prevent reliable document identity, selected-text capture, and stable browser-session handoff. I still need a real semantic context capability and an unambiguous browser-inspection route; I did not re-request the already-queued tool.

