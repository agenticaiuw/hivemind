# Harness derivation — relay-realtime — round 10

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Summarize what I missed in my email today.”"
- **useful because:** The owner can get a quick spoken briefing while walking, without opening a laptop.
- **path:** relay: capture the request and confirm scope (e.g., today, unread). → mac-bridge: planner fetches email metadata and drafts a summary. → relay: reads back a short summary and offers to drill down.
- **model tier:** Low-latency realtime model only for the brief live clarification and playback. A cheaper background model should do the email retrieval and summarization via the Mac bridge.
- **latency:** Interactive confirmation under ~2 seconds. Retrieval and summarization can take 10-60 seconds depending on network and mailbox size.
- **cost:** Main cost is background tokens for summarization and the email content processed. Realtime cost is small and limited to a short clarification and reading the summary.
- **security:** Email contains sensitive personal data. Access should require explicit account linking and confirmation of which mailbox to read. Summaries must avoid exposing secrets unless asked. The owner should be able to stop and delete cached summaries.
- **missing:** A secure email connector in the Mac planner (or an OAuth-based integration) with least-privilege scopes.; An explicit confirmation step for first-time access and for reading full message bodies.

### "“Read my upcoming schedule for the day.”"
- **useful because:** A hands-free daily briefing helps the owner plan while commuting or getting ready.
- **path:** relay: capture request, confirm time window (today/next 24h). → mac-bridge: planner queries calendar events and composes a spoken-friendly agenda. → relay: plays agenda and offers to set reminders.
- **model tier:** Realtime only for quick clarification and playback. Background tier for calendar queries and formatting.
- **latency:** Under ~2 seconds for confirmation; 5-30 seconds for calendar retrieval depending on provider.
- **cost:** Background tokens dominate due to event text and formatting; realtime tokens are minimal.
- **security:** Calendar data can include private locations and attendees. Require explicit confirmation before reading sensitive fields. Ensure the owner can exclude calendars and disable storage.
- **missing:** Calendar connector via Mac planner or direct integration.; A reminder mechanism on the pendant or phone if reminders are requested.

### "“Save this idea for later.”"
- **useful because:** Captures thoughts in the moment, then syncs them into a searchable memory or notes system.
- **path:** relay: capture dictation and confirm title/tag if needed. → mac-bridge: stores the note in the memory graph or forwards to a notes app. → dashboard: shows captured notes and allows organizing.
- **model tier:** Realtime for dictation and minimal confirmation. Background tier for storage, tagging, and search indexing.
- **latency:** Realtime capture should feel immediate; storage can complete within a few seconds without blocking the conversation.
- **cost:** Realtime audio tokens dominate during dictation; storage and indexing are cheap.
- **security:** Notes may contain sensitive info. Provide a clear policy for retention and deletion. Require confirmation before exporting to external services.
- **missing:** A standardized notes/memory write API with tagging and privacy controls.; Optional integrations (e.g., Apple Notes, Notion) with explicit user authorization.


## What it asked for

_Nothing._
## Its own summary

Grounded in the real stack, I proposed three useful capabilities: email briefings, schedule readings, and ‘save this idea’ capture. Each uses the realtime tier only for quick clarification/playback and shifts heavy lifting to a cheaper background tier via the Mac bridge, with explicit confirmation for sensitive data. I still need proper connectors (email/calendar/notes) and explicit authorization flows to implement them safely.

**Biggest unknown:** Which integrations the owner actually uses (email provider, calendar, notes) and whether a server-side browser should replace the Mac for web tasks.

