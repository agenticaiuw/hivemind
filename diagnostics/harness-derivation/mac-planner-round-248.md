# Harness derivation — mac-planner — round 248

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent readiness** — Live Mac agent is fully ready for cross-surface computer use: FULL_CONTROL_MODE and vision loop are enabled, Accessibility and Screen Recording are granted, browser extension is online with two Safari tabs, relay is reachable, and no required permission is missing.
  - evidence: GET /ops/snapshot at 2026-08-09T00:06Z returned ready:true, accessibility.trusted:true, screenRecording.granted:true, browser.online:true, relay.reachable:true, requiredMissing:[]

## Capabilities it proposed

### "When I say “make this safe to leave unattended,” have the pendant and Mac turn the current task into a monitored run: inspect the open browser/Mac state, execute only the already-planned steps, detect a stalled or failed job, and tell me on the pendant exactly what stopped and what remains."
- **useful because:** Today a long Mac/browser task can silently stop while the owner walks away. This would turn the pendant into a reliable handoff point: the owner gets a concise spoken failure or completion report instead of discovering later that nothing happened. It requires the worn trigger, relay job state, Mac executor, and authenticated browser session together.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** background for monitoring and failure classification; realtime only for the owner's spoken command and short result
- **latency:** Acknowledge in under 2 seconds; poll/heartbeat every 10–20 seconds; speak completion or failure within 5 seconds of detection.
- **cost:** About $0.01–$0.05 per monitored run, dominated by one planning call and any browser/Mac vision step; heartbeats and receipts are local/relay I/O.
- **security:** The task may touch authenticated browser data and mutate files. Persist only action metadata, URLs, hashes, and redacted errors; never persist page bodies by default. The owner must explicitly designate a run as unattended, and the configured action policy must authorize each step.
- **missing:** A durable unattended-run supervisor that joins Mac job receipts, browser command results, and relay delivery into one state machine; A pendant notification payload for run-complete/run-stalled/run-failed with retry or cancel affordance; A policy-aware way to resume only the uncompleted suffix after a lost Mac/browser heartbeat

### "Pendant, tell me what is blocking me right now."
- **useful because:** The answer should combine the real foreground app, browser tabs, today's commitments, unread mail, and unfinished Mac jobs into one prioritized obstruction list. It saves the owner from manually checking five surfaces and is useful even when no action is requested: “your next meeting starts in 12 minutes, Safari is on the wrong research tab, and one file operation failed.”
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** A cheap background ranker should assemble and cache the snapshot; realtime should only turn the cached result into a conversational answer.
- **latency:** Refresh on request in under 4 seconds; stale snapshots older than 60 seconds should be labeled as such.
- **cost:** Usually under $0.01: mostly bounded local reads and Calendar/Mail snippets; reserve model spend for ambiguous prioritization.
- **security:** Mail bodies and authenticated URLs are sensitive. Default to redacted snippets, domain/title rather than URL query strings, and retain no raw snapshot beyond a short TTL. Never infer an emergency from a subject alone.
- **missing:** A single read-only obstruction-ranking endpoint that joins local jobs, browser state, Calendar/Mail, and context graph with freshness timestamps; A compact spoken result schema with at most three blockers and a drill-down command; A relay cache invalidation event when a Mac job or browser command changes state

### "When I come back to the Mac, say “catch me up,” and have the pendant give me only the changes that happened since I last left: completed/failed Mac actions, changed browser tabs, new urgent mail or calendar changes, and any offline pendant bookmarks."
- **useful because:** The owner should not need to reconstruct state from timestamps and notifications after walking away. A bounded delta across the worn device, always-on relay, Mac job ledger, and authenticated browser is a genuinely useful return-to-work ritual, especially after a dropped link or an unattended run.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Background workers compute a compact signed delta; realtime speaks it only when requested.
- **latency:** Return the first three items in under 3 seconds; detailed drill-down can follow asynchronously.
- **cost:** Under $0.02 per request when deltas are indexed incrementally; model cost dominates only for grouping unrelated events.
- **security:** Use per-surface cursors and redact message bodies, tokens, query parameters, and private page text. A browser tab title is not proof of its contents. Require local policy authorization before reading Mail or authenticated browser state, and expire the spoken delta from relay storage quickly.
- **missing:** A durable per-owner leave_cursor that is atomically advanced only after the spoken summary is acknowledged; Cross-node event normalization for Mac receipts, browser results, relay jobs, and pendant bookmarks; A delta endpoint that supports redacted summaries and an explicit since-cursor rather than a broad history dump

### "When I ask “is that true?” while looking at a page or document, have the pendant answer from the exact visible evidence, cite the page title and quoted passage aloud, and say “the page changed” rather than silently using an old capture."
- **useful because:** This would make the wearable a trustworthy second reader instead of a generic chatbot. The owner can challenge a claim without picking up the Mac, while provenance and staleness prevent confident answers based on the wrong tab or a stale authenticated page. It needs the browser session, Mac screen/UI state, relay reasoning, and pendant speech together.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Realtime for the short question and answer; a cheaper extraction model can first locate quotations and page identity.
- **latency:** Evidence identity in 1 second and a spoken answer in 4 seconds; reject stale evidence rather than extending latency indefinitely.
- **cost:** Roughly $0.01–$0.04 per question, dominated by one screenshot/DOM extraction and a short reasoning pass.
- **security:** Authenticated page text must not be retained by default. Send only the relevant redacted region, origin/title, capture timestamp, and a content hash; suppress passwords, payment fields, and hidden DOM. Require a clear spoken indicator when the answer is based on screen evidence.
- **missing:** A browser command that returns a bounded, visible-region evidence tuple (text, role, title, URL origin, timestamp, hash) rather than an unconstrained page dump; A Mac screen/UI capture that can be atomically paired with the browser tab identity; A relay response schema carrying quote provenance and a stale-evidence refusal

### "When my command is ambiguous, have the pendant ask one useful multiple-choice question based on what is actually open—such as “I found two Safari tabs and three matching files; do you mean A, B, or C?”—then continue automatically after my answer without restarting the task."
- **useful because:** Today ambiguity either causes a risky guess or forces the owner to repeat a long request on the Mac. A context-grounded clarification turn would make the system feel like one agent: the pendant sees the owner's intent, the Mac/browser enumerate real candidates, and the relay asks only the smallest question needed.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** A cheap deterministic candidate ranker should construct options; realtime should phrase the one clarification and interpret the answer.
- **latency:** Offer options within 3 seconds; accept a button/voice selection and resume within 2 seconds.
- **cost:** Under $0.01 for ordinary cases; model spend is limited to ranking and phrasing three candidates.
- **security:** Candidate labels must not expose private filenames, message subjects, or sensitive URLs in public audio. Speak redacted labels and show full details only on the Mac. Never execute the action until the answer maps unambiguously to one candidate.
- **missing:** A clarification protocol that pauses a server plan with a stable plan token and resumes its exact step; Candidate enumeration APIs that return redacted labels and stable IDs for files, browser tabs, and UI elements; A pendant response grammar for numbered choices and cancellation that works offline until the link returns

### "At the end of a call, have the system give me a private “commitment check”: identify promises or follow-ups I made in speech, match them against Calendar, Reminders, Mail, and open Mac work, and ask me to confirm only the missing commitments before creating them."
- **useful because:** Important promises disappear because they are buried in conversation, while blindly creating reminders creates noise. This turns the pendant conversation into a bounded personal assistant: relay extracts candidate commitments, the Mac checks existing commitments, and the owner confirms only genuinely missing ones.
- **path:** pendant → relay → mac-planner → unified
- **model tier:** Background extraction and deduplication with a cheap model; realtime only asks the final confirmation question.
- **latency:** Produce candidates within 30 seconds after call end; speak the confirmation in under 5 seconds when requested.
- **cost:** About $0.02–$0.08 per call, dominated by transcript extraction and Calendar/Mail/Reminder matching; deduplication can be local.
- **security:** Conversation transcripts and mail are sensitive. Process locally where possible, retain only confirmed commitments, redact names and message bodies from relay logs, and never create or send anything without explicit confirmation. Distinguish “I should” from a promise addressed to another person.
- **missing:** A commitment extractor that outputs evidence spans, due-date uncertainty, addressee, and confidence rather than plain reminders; A read/write reconciliation layer across Calendar, Reminders, Mail, and Mac jobs with idempotent commitment IDs; A post-call pendant confirmation flow that survives a dropped link and queues the owner's yes/no response


## Changes it proposed to its own stack

### `integration` — Add an explicit read-only browser-state adapter with one unambiguous operation for the active tab list and one for a single tab snapshot, then make mac_readonly_inspect dispatch to those operations instead of choosing between action:browser_inspect and POST /browser/inspect by fuzzy score.
- **owner gets:** “Catch me up” and unattended monitoring should never silently use the wrong tab or fail because two equivalent browser readers tie. The owner gets dependable answers about the authenticated page currently open.
- effort: Small-to-medium: publish typed operation metadata, route active-tab reads through the browser extension, and add freshness plus redaction fields to the response.  ·  risk: A browser session can disappear between listing and reading; return a stale marker and retry once. Never fall back to broad page capture when the typed read fails.
- cost: Negligible API cost; one bounded browser inspection per request.  ·  latency: Adds roughly 100–500 ms for a deterministic extension round trip, but removes fuzzy-resolution retries.
- security: Improves security by making redaction and scope explicit; default to URL origin/title and require a separate authorization for page text.
- depends on: browser extension's active-tab inspection route must publish a distinct capability name; A typed JSON-schema dispatch contract for read-only browser operations


## What it asked for

_Nothing._
## Its own summary

Discovered and verified that the Mac is now fully ready: Accessibility, Screen Recording, synthesized input, relay, vision loop, and browser extension are live. Recorded three new cross-node capabilities: unattended monitored runs with pendant failure reporting, a spoken “what is blocking me?” snapshot, and a return-from-absence delta (“catch me up”). Also proposed a deterministic browser inspection adapter because browser_tabs currently ties between two live capabilities and fails resolution. What is still needed is not Mac permission: it is the durable cross-node event/cursor layer, unattended-run supervisor with suffix-only recovery, pendant result notification schema, and an explicit typed browser read adapter. Current live foreground is loginwindow; Safari exposes YouTube and Google News sessions.

**Biggest unknown:** Whether the relay already has an unlisted durable event stream/cursor and unattended supervisor. Existing routes expose jobs, receipts, browser polling, journal, and workbench handoff, but no discovered route yet atomically joins those events or advances a per-owner return cursor.

