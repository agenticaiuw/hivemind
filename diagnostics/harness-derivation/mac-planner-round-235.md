# Harness derivation — mac-planner — round 235

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac accessibility and browser state** — Live observation shows AI Pendant Agent has Accessibility and Screen Recording, synthesized events reach the screen, Safari is foreground, and 3 durable browser sessions are open. mac_readonly_inspect(browser_tabs) is currently unresolved because action:browser_inspect and POST /browser/inspect tie exactly, so tab inspection needs a resolver disambiguation.
  - evidence: mac_readonly_inspect(operation=running_apps) returned GET /observe HTTP 200 at 2026-08-08T22:59:47Z; browser_tabs call returned ambiguous resolution between action:browser_inspect and POST /browser/inspect.

## Capabilities it proposed

### "If a Mac task stops halfway, tell me exactly what finished and give me one spoken command to continue from the first unfinished step."
- **useful because:** A failed automation currently leaves the owner guessing whether files moved, tabs changed, or a message was sent. This turns a partial run into a comprehensible recovery: the relay can speak a bounded receipt through the pendant, while the Mac resumes idempotently instead of repeating completed work.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** background model to summarize the receipt and identify the first unfinished step; realtime only to read the short status aloud.
- **latency:** Receipt should be durable within 2 s of failure; spoken recovery summary within 5 s after the owner asks; resume begins immediately after the command.
- **cost:** Roughly $0.001–$0.005 per failed job for summarization; storage is a few KB per checkpoint.
- **security:** Receipts may contain filenames, URLs, or snippets and must be redacted before reaching the pendant. Never replay a completed send/delete/purchase step; resume only from a recorded idempotent boundary. The owner should be able to discard the capsule locally.
- **missing:** A step-level checkpoint schema shared by POST /execute, browser actions, and mac_workbench_transaction; A relay route that turns GET /workbench/jobs/:jobId/handoff plus GET /jobs/:jobId/receipts into a concise pendant inbox card; An idempotent resume executor that accepts only the unfinished suffix and records a new attempt lineage

### "What changed on my Mac since I left it? Give me the important browser, file, and app changes through the pendant."
- **useful because:** The owner can walk away from an in-progress Mac session and return without reconstructing state. A compact delta is more useful than a full screenshot or a generic briefing: it can say which tabs changed, which files were created or modified, and whether an automation completed, while omitting unchanged noise.
- **path:** mac-planner → browser → relay → pendant
- **model tier:** Cheap background model over structured deltas; realtime only for speaking the resulting short digest.
- **latency:** Capture a baseline on departure or explicit request in under 2 s; compute a delta in under 5 s; speak in under 8 s.
- **cost:** About $0.001–$0.01 per query depending on number of file/tab deltas; no continuous model calls if baselines are structured.
- **security:** Do not upload file contents by default—only names, sizes, timestamps, hashes, and redacted URL origins. Private browsing, password managers, and secure-input apps must be excluded. The baseline is owner-scoped and expires automatically.
- **missing:** A durable per-owner Mac baseline with explicit capture and expiry; A structured browser-tab diff and bounded directory metadata diff rather than UI scraping; A relay query/event that packages the diff into a pendant-sized spoken response

### "Watch this authenticated browser page overnight and wake me only if its status changes; save a redacted before-and-after evidence note on my Mac."
- **useful because:** The browser is the only node holding the owner's authenticated session, while the relay can stay awake after the Mac sleeps and the pendant can deliver a concise alert. This avoids polling the site manually and produces evidence of what changed instead of an unexplained notification.
- **path:** browser → relay → mac-planner → pendant
- **model tier:** Cheap scheduled DOM normalization/diff; realtime model only if the owner asks for an explanation of the change.
- **latency:** Poll at the owner-selected interval; detect and enqueue an alert within 30 s of a change; Mac evidence note within 2 min.
- **cost:** Approximately $0.001–$0.02 per poll depending on page size and diff frequency; no model cost for unchanged pages.
- **security:** Authenticated page content stays in the browser/relay boundary and must be selector-scoped, redacted, and TTL-limited. Never store cookies or submit forms. The owner explicitly chooses the URL, selectors, polling window, and alert threshold; stop on authentication expiry or unexpected navigation.
- **missing:** A browser-session page watcher with selector-scoped snapshots and authentication-expiry detection; A relay scheduler and deduplicated change event feeding the existing pendant alert inbox; A Mac receipt writer that stores only the redacted diff and timestamp

### "Continue the authenticated browser task I started on my Mac after the Mac restarts, without making me log in again or repeat the completed steps."
- **useful because:** The browser is the only node with the owner's live authenticated session, but a Mac restart currently strands the task. A lease-based handoff would let the relay remember the browser session's exact checkpoint and reconnect the returning Mac to it, preserving work across crashes and overnight maintenance.
- **path:** browser → relay → mac-planner → pendant
- **model tier:** Deterministic checkpoint matching and session handoff; use a background model only to explain a mismatch or changed page.
- **latency:** Detect disconnect within 10 s; reconcile a returning Mac within 30 s; never resume until the browser reports the same origin and checkpoint.
- **cost:** Negligible model cost in the normal path; approximately $0.001–$0.01 only for mismatch explanation.
- **security:** The relay must hold an opaque session lease, never cookies or credentials. Bind it to the owner, browser origin, task hash, and expiry. Refuse handoff after navigation, authentication expiry, DOM divergence, or lease timeout. Any submission remains a distinct action requiring the owner's configured policy.
- **missing:** A browser-side resumable session lease that exposes checkpoint identity without exposing cookies; Relay persistence for lease ownership, expiry, and completed-step hashes; Mac reconnect logic that verifies origin/checkpoint before asking the browser to continue

### "Hand this authenticated browser task from my Mac to my phone when I leave, then bring the result back to the Mac when I return."
- **useful because:** The owner should not lose a long-running web workflow merely because they walk away from the laptop. The browser session can remain authoritative while the pendant signals progress, an iOS companion supplies a secure presence/approval surface, and the Mac receives the final artifact instead of forcing the owner to restart.
- **path:** mac-planner → browser → relay → iOS → pendant
- **model tier:** Deterministic task-state transfer; background model only summarizes state changes or conflicts.
- **latency:** Handoff acknowledgement under 3 s; remote progress updates under 15 s; final artifact sync within 30 s of completion.
- **cost:** Usually below $0.005 per handoff; model cost occurs only for conflict summaries.
- **security:** Transfer an opaque task lease, not cookies or raw credentials. Require device binding, expiry, origin checks, and explicit owner confirmation for any external submission. The iOS surface should receive redacted state and never persist page secrets.
- **missing:** A secure iOS companion surface for task state and approval; Browser task leases that can be consumed by more than one owner device without duplicating steps; Relay conflict resolution and artifact synchronization between iOS and Mac


## What it asked for

_Nothing._
