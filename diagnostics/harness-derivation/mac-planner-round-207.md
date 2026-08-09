# Harness derivation — mac-planner — round 207

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility-now-live** — The AI Pendant Agent is currently trusted for Accessibility and Screen Recording; synthesized input posts successfully, secure input is false, and UI actions will reach the screen. The live host has 19 apps, Calendar/Mail/Notes, and 3 browser sessions.
  - evidence: mac_readonly_inspect(operation=running_apps) invoked GET /observe at 2026-08-08T03:19:17Z; response accessibility.trusted=true, screenRecording=true, eventsPost=true, browser.sessions=3.

## Capabilities it proposed

### "When I press the pendant's bookmark button, save exactly what I was doing so I can pick it up later: the time, current Mac app/window, open browser tab, nearby calendar event, and a short label I can speak afterward."
- **useful because:** The existing bookmark survives offline but only says when; this turns an otherwise mysterious moment into a recoverable task marker. It works today with the pendant attached over USB and remains useful when LTE is absent.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Use the realtime model only to normalize an optional spoken label; deterministic joining and file creation should be background/cheap model or code.
- **latency:** Acknowledge the button locally immediately; assemble the card within 3 seconds and never block the owner's current app.
- **cost:** Near-zero if unlabeled (state joins and templating); roughly $0.001-$0.01 only when a spoken label needs model normalization. Mac/browser reads dominate latency, not tokens.
- **security:** The card can expose URLs, app names, and calendar titles. Keep it local by default, redact page text and query strings, and require explicit owner policy before uploading or opening it in another app.
- **missing:** A pendant-to-Mac USB event bridge for offline_moment_bookmark while LTE is unregistered; A read-only semantic window identity operation (app/window title) beyond the current host snapshot; A durable bookmark-card index and retention policy

### "Let me say "save this for tomorrow" while looking at any Mac app or browser page, and have the pendant confirm it; create a dated note/reminder containing a redacted link and context without moving my cursor or changing focus."
- **useful because:** It closes the gap between noticing something and losing it. The owner gets a reliable handoff from wearable intent to a concrete Mac artifact, while the current work stays untouched.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime handles the short utterance and ambiguity; deterministic Mac actions perform the note/reminder creation, with a cheaper background pass only for extracting a concise title.
- **latency:** Under 5 seconds for confirmation and staging; if ambiguity remains, ask one spoken clarification rather than guessing a destination date.
- **cost:** About $0.002-$0.02 per invocation depending on clarification; AppleScript/action execution and browser inspection dominate wall time.
- **security:** Never transmit page body or secrets by default; store only title, origin, URL stripped of credentials/query tokens, and requested date. The owner must explicitly configure which apps/sites may be captured; empty policy means no action.
- **missing:** A cross-surface intent event carrying pendant utterance plus active browser/app identity; A no-focus AppleScript note/reminder writer with receipts; Policy entries for allowed destination apps and URL redaction

### "Keep an eye on today's calendar and unread mail, and when something genuinely urgent collides with what I am doing in the browser, give me one short pendant alert with the exact next action; let me press once to stage that action on the Mac."
- **useful because:** This is the system's highest-value daily behavior: it filters interruption instead of adding another inbox. It combines private Mac context, authenticated browser sessions, and the wearable's attention channel into a single actionable escalation.
- **path:** relay → mac-planner → browser-extension → pendant
- **model tier:** Use a cheap scheduled/background model for ranking and deduplication; reserve realtime only for the spoken one-sentence alert or owner follow-up.
- **latency:** Scan at calendar/mail boundaries and every 10 minutes while the Mac is active; alert within 30 seconds of a high-confidence collision, with immediate local queueing if disconnected.
- **cost:** Roughly $0.01-$0.05 per scan depending on mail volume; Calendar/Mail reads and browser metadata are the main data path, while ranking can use a small model.
- **security:** Mail/calendar and active URLs leave the Mac only if policy permits. Default to metadata/snippets, redact bodies and tokens, deduplicate alerts, expire them after the event, and never execute a consequential action without an owner-configured policy entry.
- **missing:** A scheduler that joins Calendar/Mail reads with browser activity and current foreground app; A compact urgency/collision record format shared with offline_alert_inbox; A one-press relay-to-Mac action token and receipt path

### "When a web action could send, buy, submit, or delete something, prepare it in my authenticated browser session, show me a compact before/after summary on the Mac, and require a physical pendant press that is cryptographically bound to that exact final state before committing it."
- **useful because:** This gives the owner the one thing current automation lacks: confidence that the action being approved is the action actually submitted. A spoken request can do the tedious work, while the wearable becomes a last-mile physical confirmation that cannot be confused with a stale browser tab or changed form.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime interprets the request and explains the final diff; deterministic browser automation, hashing, and commit-token validation do the safety-critical work.
- **latency:** Prepare within 10 seconds for ordinary forms; confirmation must expire after 60 seconds or any page mutation, with a one-sentence pendant prompt.
- **cost:** $0.005-$0.03 per invocation for intent parsing and concise diff narration; browser interaction and screenshot/diff capture dominate.
- **security:** Never transmit passwords or full page bodies. Bind a one-time commit token to origin, account/session, method, destination, and a normalized field diff; invalidate it on navigation or DOM mutation. The physical press confirms only the displayed digest, not arbitrary future actions.
- **missing:** A browser bridge primitive for prepare-versus-commit with a mutation digest; A pendant physical-confirmation event carrying a nonce and monotonic counter; Relay verification that joins browser digest, Mac preview, and pendant confirmation atomically

### "Let me ask "what did the system change while I was away?" and get a private, chronological answer covering browser submissions, Mac file/app changes, calendar/mail mutations, and pendant events, with proof links and a way to undo each reversible item."
- **useful because:** Today the hive can perform work across surfaces, but the owner cannot obtain one trustworthy account of its side effects. This makes automation auditable after sleep, travel, or a dropped connection instead of requiring memory of which agent acted.
- **path:** relay → mac-planner → browser-extension → pendant → dashboard
- **model tier:** Use deterministic event normalization and receipt joins first; use a cheap background model only to summarize the selected interval, with realtime reserved for spoken follow-up questions.
- **latency:** A 24-hour report in under 5 seconds; a single event lookup under 1 second from cached receipts.
- **cost:** Near-zero for indexed receipts; $0.002-$0.01 for a natural-language summary. Storage/indexing dominates, not inference.
- **security:** The ledger is highly sensitive. Keep raw values local, store hashes and redacted descriptors by default, partition by account/session, and require explicit scope for mail, browser, and file history. Never claim success without a receipt from the target surface.
- **missing:** A common append-only event envelope with actor, target surface, before/after digest, and causal job ID; Browser and Mac adapters that emit receipts for successful mutations, not only plans; A user-facing query/export surface and per-event undo linkage

### "When I say "hand this off," turn the current browser page or Mac task into a complete package for a named person: collect only the relevant evidence, draft the message and next steps, check the calendar for a handoff slot, and leave it ready for my final approval without sending."
- **useful because:** The owner often needs to transfer work, not merely save it. This joins the authenticated page, local files, calendar availability, and wearable intent into a usable handoff package while preserving the crucial boundary that nothing is sent automatically.
- **path:** pendant → relay → browser-extension → mac-planner
- **model tier:** A cheaper background model extracts and structures evidence; realtime is used only to clarify the recipient or explain the draft when ambiguity remains.
- **latency:** Draft in 15 seconds for a single page and under five local files; ask one clarification if the recipient or evidence scope is uncertain.
- **cost:** $0.01-$0.08 depending on evidence volume; browser/file reads and redaction are the dominant cost.
- **security:** Default to metadata and explicitly selected evidence, redact secrets and unrelated mail, never infer a recipient from a private page without confirmation, and require final owner approval before any send or calendar mutation.
- **missing:** A cross-surface evidence selector with provenance and redaction controls; A draft-only composer that can target Mail/Notes/calendar without sending; A relay job contract that carries pendant intent, browser provenance, and Mac artifact links


## Changes it proposed to its own stack

### `integration` — Add a local USB pendant event daemon that reads the already-connected nRF9160 serial device, validates bookmark/alert events, and publishes signed events to the relay with a monotonic sequence and replay-safe receipt. It should operate while LTE is unregistered, queue locally when the relay is unreachable, and never open the microphone.
- **owner gets:** The pendant is physically usable today but currently cannot reliably hand its offline bookmark and alert events to the Mac/relay. This makes the wearable useful in the real no-LTE state instead of waiting for cellular registration.
- effort: Medium: serial framing/parser, reconnect loop, event schema, launch-agent lifecycle, and a small integration test against both USB devices.  ·  risk: Malformed serial input or duplicate reconnects could create duplicate bookmarks/alerts; use sequence numbers, idempotency keys, bounded queue, and a visible diagnostic log. Do not send raw audio or arbitrary serial commands.
- cost: No API-model cost; approximately 1-2 days engineering and negligible CPU/storage on the Mac.  ·  latency: Under 250 ms from USB event to relay enqueue in the normal case; offline queue is immediate.
- security: USB events are local but should be authenticated per device/session; no microphone data should cross this bridge. The relay should receive only typed events and timestamps.
- depends on: A concrete mac_serial_exchange capability or equivalent local serial reader (currently requested but not available to this agent); A documented pendant event frame/schema; An idempotent relay event endpoint such as POST /pipeline/events


## What it asked for

_Nothing._
## Its own summary

This round established a material state change: the AI Pendant Agent now has Accessibility and Screen Recording, synthesized input is verified, and the Mac currently exposes Calendar, Mail, Notes, three browser sessions, and 19 running apps. I recorded that finding and submitted three new cross-surface capabilities: bookmark-to-context cards, focus-preserving “save this for tomorrow,” and urgency collision alerts with one-press staging. I also proposed the USB pendant event daemon that makes the physically connected, LTE-unregistered pendant useful today. The strongest capability is the urgency collision alert: it filters private Calendar/Mail/browser context into one actionable wearable interruption rather than another inbox.

**Biggest unknown:** The concrete USB serial event bridge and pendant frame schema are still missing; mac_serial_exchange remains unavailable. Browser inspection is also currently ambiguous between action:browser_inspect and POST /browser/inspect, so a deterministic browser-tab read path is needed before implementing these flows. Owner-configured unattended-action policy is still unspecified; proposals should stop rather than assume authorization.

