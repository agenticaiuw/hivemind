# Harness derivation — mac-planner — round 297

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-observability** — The live Mac agent now has Accessibility and Screen Recording trusted for AI Pendant Agent, synthesized input verified, iPhone Mirroring foreground, and 19 apps running. Browser tab inspection through mac_readonly_inspect remains ambiguous between action:browser_inspect and POST /browser/inspect.
  - evidence: mac_readonly_inspect(operation=running_apps) invoked GET /observe at 2026-08-09T04:04:10Z; response reports accessibility.trusted=true, screenRecording=true, eventsPost=true, foregroundApp=iPhone Mirroring; browser_tabs call returned unresolved ambiguity.

## Capabilities it proposed

### "When I mark a moment as “this is broken,” collect a bounded diagnostic packet from the active Mac app and browser, attach the pendant's timestamped marker, and leave me a redacted bug report with exact reproduction context."
- **useful because:** The owner already has a physical bookmark and a Mac that can inspect apps, but today those facts are disconnected. This makes a failure reproducible instead of forcing the owner to remember which tab, app, and state produced it.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background model for normalization and redaction; use the realtime tier only if the owner asks follow-up questions aloud.
- **latency:** Local marker in under 200 ms; diagnostic bundle in 15 seconds. If an app is unresponsive, record the failure and continue with the other surfaces.
- **cost:** Roughly $0.02–$0.08 per report, mostly model normalization of logs/UI text; storage is small plain text/JSON.
- **security:** Collect only allowlisted app metadata, visible UI text, URL, and recent agent receipts—not arbitrary home-directory logs or secrets. Redact tokens and personal content before persistence. Never send a report externally without explicit confirmation.
- **missing:** A bounded, typed Mac diagnostic collector for foreground app/UI state and recent action receipts; A browser evidence endpoint with stable command IDs and result receipts; A report schema that preserves provenance and redaction decisions

### "At the end of a work block, let me mark the moment; later, ask “what changed since then?” and hear only the important differences across my browser, calendar/mail, workspace files, and Mac apps, with links or files opened when I request them."
- **useful because:** This answers the real interruption problem: not restoring every window, but telling the owner what materially changed while they were away. The pendant creates a low-friction baseline; the relay compares it later; the Mac and browser can act on the selected deltas.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model computes a compact delta digest; realtime is reserved for the spoken query and confirmation.
- **latency:** Baseline capture under 2 seconds; comparison in 10–20 seconds; speak a one-sentence result first and continue only on request.
- **cost:** About $0.02–$0.10 per comparison, dominated by summarizing changed page/file/mail metadata; raw snapshots stay local where possible.
- **security:** Persist hashes, titles, timestamps, and redacted summaries rather than full mail/page bodies by default. Respect the owner's destructive-action policy; opening an item is allowed, sending/deleting is never implicit.
- **missing:** A durable baseline/delta store keyed by pendant bookmark ID; A read-only browser tab/page snapshot with stable identity; A bounded workspace change index and Mac app-state snapshot; A relay query that can merge calendar/mail, browser, and file deltas

### "Prepare this browser action but do not send it: draft the reply, fill the form, or stage the purchase, then show me an exact before/after preview on the Mac and read a short summary through the pendant so I can confirm or abandon it."
- **useful because:** The owner can delegate tedious authenticated-browser work without losing control at the irreversible boundary. The pendant is the always-available intent and confirmation surface, the browser holds the private session, and the Mac produces a concrete visual diff instead of asking the owner to trust a model summary.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Realtime model parses the short spoken intent and asks clarifying questions; a cheaper background model extracts fields and computes the preview. No model is allowed to submit without a distinct owner confirmation event.
- **latency:** Draft preview within 10 seconds; spoken summary within 2 seconds after preview is ready; abandon is immediate and must discard staged sensitive fields.
- **cost:** About $0.02–$0.08 per staged action, dominated by page interpretation and preview generation; browser and Mac operations are local.
- **security:** Never submit, buy, send, delete, or publish as part of staging. Keep passwords, payment data, and session tokens inside the browser; redact them from previews and receipts. Confirmation must bind to the exact page, fields, recipient, amount, and expiry, not merely to the original spoken request.
- **missing:** A browser-side staging transaction that can fill fields and roll them back without submission; A deterministic before/after DOM/form diff and screenshot region capture; A confirmation token bound to the staged browser command and a pendant-readable summary; A discard/expiry operation that clears staged sensitive values

### "Let me teach you a workflow once by doing it on my Mac and browser while I narrate from the pendant, then turn that demonstration into a reusable routine that I can invoke by voice, inspect, edit, pause, or delete."
- **useful because:** The owner should not need to repeatedly explain the same multi-app task or learn an automation language. A demonstration captures the real authenticated browser session, Mac state, and spoken intent; the resulting routine can be reused while still exposing exactly what it will do.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime handles narration and ambiguity during the demonstration; a cheaper background model extracts stable steps, parameters, and stopping conditions. Realtime is only needed when the owner invokes or corrects the routine conversationally.
- **latency:** Record with under 300 ms event latency; produce a reviewable routine within 30 seconds after the demonstration; invocation should begin within 3 seconds.
- **cost:** About $0.05–$0.25 per demonstrated workflow and under $0.03 per later invocation, dominated by interpreting UI transitions and generating a concise review.
- **security:** Never record passwords, payment values, cookies, private page bodies, or arbitrary keystrokes by default. Store semantic actions and redacted selectors, not raw session data. Browser routines must expire when page structure or login identity changes; sending, buying, deleting, or publishing requires a fresh explicit confirmation every invocation.
- **missing:** A cross-surface demonstration recorder joining pendant narration, browser command/result events, and Mac action receipts in one ordered timeline; A semantic workflow compiler that converts observed events into parameterized, versioned steps with assertions and safe failure stops; A routine review/editor UI and dry-run simulator; Routine lifecycle storage, versioning, pause/delete, and change detection when an authenticated site changes


## What it asked for

_Nothing._
