# Harness derivation — browser-extension — round 202

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-live-tabs** — Safari extension is online with four tabs: example.com, YouTube subscriptions, authenticated Discord #general, and X likes; active tab is Discord. browser_list_tabs works through POST /execute and returns provenance/receipts.
  - evidence: POST /execute browser_list_tabs at 2026-08-08T22:45:32Z returned status success, tabCount 4, active tab 3583395 Discord.

## Capabilities it proposed

### "Every weekday morning, check the authenticated sites I have open in Safari, tell me only what is new and actionable, and put urgent items in my pendant inbox without reading the whole page aloud."
- **useful because:** This is the system's highest-value browser capability: it combines authenticated sessions that only the browser can reach, relay scheduling and ranking, and the pendant's offline alert queue. The owner gets a short actionable morning queue rather than manually checking several sites.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Background/scheduled jobs use a cheaper model for extraction and ranking; realtime is used only when the owner asks a follow-up by voice.
- **latency:** Run before the requested morning deadline (typically under 2 minutes for 3-5 tabs); pendant delivery is immediate once the job finishes.
- **cost:** Low-to-moderate: one scheduled browser read per origin plus a small summarization call; cost is dominated by page extraction, not speech.
- **security:** Start with an empty per-origin configuration. Persist only short claims with existing 24-hour browser TTL, 200-character cap, URL and evidence capsule; never HTML or screenshots. Never submit forms or send messages. Urgent alerts require no extra confirmation because they are notifications, not mutations.
- **missing:** Scheduled browser job that snapshots configured authenticated origins and computes a prior-result diff; Owner-supplied origin/category configuration (empty by default); A browser-to-offline-alert-inbox delivery adapter with deduplication

### "I am looking at a thread in Safari; press the pendant button and give me a 60-second brief of the relevant people, decisions, and what I should do next, using my calendar and notes for context."
- **useful because:** It turns a private authenticated page into an immediate, hands-free decision aid. No other node can see the Safari thread and the Mac alone cannot deliver a concise spoken brief through the worn interface while the owner is away from the keyboard.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a small background extraction model for page structure and a realtime model only for the final spoken synthesis or follow-up.
- **latency:** Under 8 seconds from the button press; read page and local calendar/notes context in parallel, then stream a compact answer.
- **cost:** Moderate per invocation: one page extraction, one local-context lookup, and a short realtime synthesis; audio tokens dominate if the answer is allowed to run long.
- **security:** Read-only action allowlist (browser_read_page plus local calendar/notes reads). Do not persist page text; store at most short task-matched claims under existing browser provenance/TTL rules. Speak only the extracted brief, and disclose the source tab title/domain.
- **missing:** A reliable pendant event that addresses the active Safari tab; A context joiner that aligns page entities with local Calendar/Notes without sending raw page text to long-term memory; Streaming response path from relay to the pendant for sub-8-second playback

### "Before I submit this web form, read back the destination, recipient, amount, and unusual fields from Safari, and let me correct anything by voice; do not submit until I say send."
- **useful because:** It catches expensive mistakes in authenticated forms while preserving the owner's maximum-access policy. The browser can see values behind login, the pendant is the only practical place to hear and correct them hands-free, and the relay can produce a precise pre-submit checklist.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Use deterministic DOM extraction and validation first; use realtime only to phrase the checklist and interpret corrections. No background model is needed.
- **latency:** 3-6 seconds to produce the checklist; corrections should update the draft in under 3 seconds. Submission remains an explicit owner command.
- **cost:** Low per attempt: DOM extraction plus a short realtime turn; audio and repeated corrections dominate.
- **security:** Restrict the browser action sequence to read/extract/type; never click submit automatically. Mask secrets and payment credentials in spoken output by default, with owner-configurable categories. Keep a reversible field-change receipt and do not persist raw form values or page text.
- **missing:** Structured form-field extraction with destination/recipient/amount heuristics; Pendant voice correction protocol that targets field names rather than free-form page clicks; A final explicit send command wired to browser_click and a durable pre-submit receipt

### "Once a day, scan my authenticated Discord and social tabs for messages that require a reply, match each person to my calendar and notes, and put a two-line suggested response plus the source link in my pendant inbox; I will approve or edit it by voice before anything is sent."
- **useful because:** The owner currently has to remember which private conversations need follow-up and reconstruct context manually. This would use the browser's authenticated sessions, local Mac context, relay reasoning, and the worn interface together: detect obligations, recover relationship context, and make replying possible while away from the keyboard without silently speaking for the owner.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Scheduled scanning and clustering use a cheaper background model; realtime is reserved for the owner's voice edits and approval. Deterministic extraction should identify message authors, timestamps, mentions, and links before any model call.
- **latency:** A daily scan can finish in 1-3 minutes; each pendant follow-up should start within 5 seconds and produce an editable draft within 10 seconds.
- **cost:** Moderate: authenticated page extraction across configured origins and short per-thread drafting; cost is dominated by reading enough surrounding conversation to avoid an embarrassing out-of-context reply.
- **security:** Ship with an empty origin configuration and require the owner to opt in each origin/category. Never persist page bodies or DMs; retain only short-lived task-matched claims and provenance under existing browser TTL limits. Drafts may be spoken, but sending is a separate explicit approval action and must show the exact text and destination first. Deduplicate alerts and expire stale drafts.
- **missing:** Thread-aware extraction that captures the minimum surrounding context and identifies the reply target; A relationship/context joiner over local Calendar/Notes with strict short-lived redacted intermediate data; A pendant inbox item type for editable drafts, voice substitutions, and explicit approve/send; Browser result handling that can resume the exact source thread and send only the approved text

### "If I say 'lock down my browser' to the pendant, immediately freeze browser automation, close my authenticated Safari tabs, and sign me out of configured sites, then tell me exactly what was closed when I unlock it."
- **useful because:** The pendant is the one control surface the owner can reach when the Mac is unattended or a session may be exposed. Today browser automation and authenticated tabs remain reachable until someone gets to the Mac. A spoken or button-triggered panic action would turn the hive into a practical privacy emergency stop rather than merely an automation system.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** No expensive model is needed for the lockdown path: use a deterministic relay command and an allowlisted browser/Mac action plan. Realtime is only for reporting the receipt or handling an ambiguous site-specific logout.
- **latency:** Freeze new browser commands immediately; close tabs and invoke configured logout actions within 5 seconds; report completion or partial failure within 10 seconds.
- **cost:** Very low per invocation; dominated by extension round-trip latency, not inference.
- **security:** The lockdown command must be available offline as a queued pendant action and fail closed: if the relay is unreachable, stop local browser bridge polling and signal the owner. Use an explicit configured origin/session policy, never invent logout URLs, and record only tab origins/titles and action receipts. This is intentionally high-impact but owner-authorized as an emergency command, with no conversational confirmation.
- **missing:** A pendant emergency command that survives a dropped link and reaches the Mac when connectivity returns; A browser bridge kill switch that rejects queued and future commands; Per-origin logout/close policies and an auditable partial-failure receipt; A Mac-side session scrubber for Safari cookies/local storage where the owner explicitly opts in

### "Watch the private pages I opt into and tell me when two sources disagree about an event, deadline, or status—for example a Discord announcement versus my calendar—then give me the conflicting links and the safest next step on the pendant."
- **useful because:** The owner can already read each source separately, but cannot reliably notice contradictions across authenticated web sessions and local records. This catches moved meetings, changed deadlines, and stale announcements before they cause missed commitments, while preserving the source evidence needed to resolve the conflict.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use deterministic date/entity extraction and a cheap background contradiction classifier; realtime is only needed to explain a conflict when the owner asks by voice.
- **latency:** Periodic checks within 5 minutes of a configured page change; a conflict alert should reach the pendant within 15 seconds of detection.
- **cost:** Low-to-moderate: incremental page reads and structured comparison; cost is mainly repeated authenticated extraction, not generation.
- **security:** Only compare explicitly configured origins and local record types. Retain a short conflict claim with both URLs and timestamps, never the underlying page text. Mark uncertainty rather than presenting inferred contradictions as facts. Do not edit calendars or pages automatically.
- **missing:** Incremental page-change and entity/date extraction for authenticated tabs; A cross-source fact graph that retains provenance and confidence without storing page bodies; Conflict deduplication and resolution-state tracking; Pendant alert payloads that include two source labels and support a spoken 'open source one' follow-up


## What it asked for

_Nothing._
## Its own summary

Three distinct proposals recorded: (1) scheduled authenticated-tab triage that sends only urgent changes to the pendant (the highest-value capability), (2) button-triggered 60-second context brief combining the active private Safari page with local Calendar/Notes, and (3) a voice-correctable pre-submit form checklist that never submits without an explicit send command. I also verified the browser is genuinely usable now: Safari has four tabs and browser_list_tabs plus browser_read_page both succeed through POST /execute; the active authenticated Discord page was read successfully. I broadcast the live state to the other agents.

**Biggest unknown:** The remaining product inputs are owner-supplied, not discoverable: which authenticated origins to automate, which content categories may be spoken, and which may be persisted. The remaining engineering gaps are scheduled browser diffing, structured form-field extraction, pendant event/stream wiring, and a browser-to-offline-alert adapter. The granted browser wrapper itself is still ambiguous, so I currently need to use the already-permitted direct POST /execute path rather than the wrapper.

