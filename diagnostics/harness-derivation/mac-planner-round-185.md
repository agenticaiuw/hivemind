# Harness derivation — mac-planner — round 185

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the pendant bookmark, later tell me exactly what I was doing at that moment and reopen the right work context."
- **useful because:** A physical bookmark is the one reliable timestamp in an interruption. This turns it into recovery rather than a vague note: calendar context, active browser page, foreground app, and relevant recent mail/files are reconstructed and the Mac is returned to that state.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for reconstruction and ranking; realtime only for the short spoken answer.
- **latency:** Bookmark acknowledgement under 300 ms; recovery card under 10 s; reopening approved context under 3 s.
- **cost:** About $0.01-$0.04 per recovery, dominated by one background synthesis and optional browser inspection; Mac reads are local.
- **security:** The bookmark timestamp can expose work context and browser URLs. Redact message bodies by default, keep data local to the Mac where possible, and require the owner's existing destructive-action confirmation before opening or mutating anything. Expire raw context after 7 days.
- **missing:** A durable bookmark-to-context correlation route; A local timeline store for browser/app/calendar observations; A deterministic context-reopen plan that does not overwrite the current workspace

### "Before I leave a task, say 'hold this'; when I return, compare the Mac and browser to that point and tell me only what changed that matters."
- **useful because:** It gives the owner a compact continuity check across a real interruption: changed files, browser state, calendar/mail events, and whether an unfinished desktop action succeeded, without forcing them to remember where they stopped.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background model for diff extraction and priority ranking; realtime only to speak the final sentence.
- **latency:** Capture under 1 s; return comparison in under 8 s; no automatic mutations.
- **cost:** Roughly $0.01-$0.03 per comparison; token cost is bounded by selected metadata and snippets, not whole documents.
- **security:** Diff metadata may contain sensitive names/URLs. Hash and summarize files rather than upload contents, redact mail bodies, scope browser inspection to the selected tab/session, and store the checkpoint encrypted with a 24-hour default TTL.
- **missing:** A cross-surface checkpoint schema with file/browser/calendar/mail cursors; A diff service that understands Mac job receipts and browser request IDs; A spoken 'hold this' trigger mapped to the existing pendant bookmark without confusing it with ordinary bookmarks

### "At the start of a meeting, prepare me automatically: alert me on the pendant, gather the relevant email and browser tab, and open a quiet, bounded prep workspace on the Mac."
- **useful because:** The wearable catches attention even when the Mac is hidden; the relay can correlate the calendar event with mail and authenticated browser context; the Mac can stage the actual documents. This is a genuinely multi-node pre-meeting assistant rather than another calendar reminder.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for relevance ranking; deterministic scheduler and local actions do the rest; realtime speaks only if the owner asks follow-up.
- **latency:** Run 10 minutes before an event; pendant alert within 2 s; workspace staged within 15 s; never block calendar use.
- **cost:** About $0.02-$0.06 per meeting, dominated by ranking a small set of mail/tab candidates; local Mac actions are negligible.
- **security:** Authenticated browser pages and email are high sensitivity. Use URL/domain and sender metadata first, snippets only when needed, never upload page bodies by default, isolate a temporary workspace, and apply the owner's existing confirmation rule to sending, deleting, purchasing, or other destructive actions.
- **missing:** Calendar-event trigger with configurable lead time; Relevance join between event attendees/title, Mail, and browser sessions; A Mac workspace staging primitive that opens files without closing or replacing the owner's current apps; An urgent alert payload for the existing pendant inbox

### "When I ask “where did I see this?”, search my recent browser pages, Mac files, mail, calendar, and pendant bookmarks, then give me the answer with the exact source I can reopen."
- **useful because:** People remember a fact but not which surface contained it. Today these sources are isolated. A provenance answer would recover the original page, message, document, or moment instead of producing an uncited guess.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background retrieval and ranking model; realtime only for the concise spoken result.
- **latency:** Under 10 seconds for a 30-day search; source reopening under 3 seconds.
- **cost:** Approximately $0.02-$0.08 per query, dominated by indexing and ranking snippets; full document contents stay local unless explicitly needed.
- **security:** Search indexes can reveal sensitive associations. Keep raw contents on-device, store redacted embeddings or hashes, scope searches by an explicit time window, and speak only the minimum citation needed.
- **missing:** A unified provenance index with source type, timestamp, title, stable locator, and redaction metadata; Mac-side file/document metadata indexing exposed to the relay; Browser history or inspected-page retention with owner-configurable TTL; A source citation payload that the pendant and Mac can both render

### "Before I go offline, say “pack this trip”; package the selected browser research, local documents, calendar details, and important mail into an encrypted field kit I can search and hear from the pendant without a live connection."
- **useful because:** The owner can leave the Mac or lose LTE without losing the context they deliberately prepared. The kit is bounded and intentional, unlike a full mirror of personal data, and can answer small questions offline.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model selects and compresses only the explicitly chosen material; deterministic encryption, manifesting, and local playback handle delivery.
- **latency:** Pack in under 30 seconds for a bounded 25-item kit; offline lookup under 2 seconds; wipe on expiry.
- **cost:** About $0.03-$0.12 per kit for summarization, with no ongoing inference cost during offline use.
- **security:** This creates a portable sensitive cache. Require explicit owner initiation, encrypt per-kit with a device-bound key, display item count and expiry, prohibit mail attachments/passwords by default, and securely delete on expiry or cancellation.
- **missing:** An explicit selection protocol spanning browser tabs and Mac files; Encrypted manifest and key handoff to the pendant's existing storage/retry mechanisms; Offline text-to-speech or pre-rendered answer cards within the pendant's actual storage limits; A relay command to expire and revoke a kit on every surface

### "When I ask “what is the safest next step?”, inspect the current browser page, related local files and mail, and the recent Mac action history, then give me a cited risk-aware recommendation without taking the action."
- **useful because:** The system can currently act, but it cannot reliably combine the live authenticated page with the owner's local context and explain why a proposed next step is safe. A read-only decision pass would be valuable before purchases, account changes, or destructive edits.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Judgement model for synthesis; perception and retrieval should be cheaper deterministic/background workers; realtime only speaks the final recommendation.
- **latency:** Under 12 seconds, with a visible evidence list before any optional action plan.
- **cost:** Approximately $0.03-$0.15 per recommendation depending on page and local-context size; no cost if the owner declines after the read-only pass.
- **security:** Authenticated pages and local files may contain secrets. Use field-level redaction, never transmit passwords or payment data, preserve source URLs and timestamps, and keep this capability strictly read-only until a separately requested action.
- **missing:** A browser-page semantic extraction route for the currently selected tab; A Mac action ledger query with resource-level redaction; Evidence-linked judgement output with confidence and conflicting-source reporting; A distinct read-only mode that cannot accidentally enqueue an executor plan


## Changes it proposed to its own stack

### `integration` — Add a USB-tethered pendant session bridge: the Mac agent reads the nRF9160 serial event stream and forwards bookmark, privacy, QoS, and staged-reply events to the relay over the existing authenticated connection, with sequence numbers, reconnect replay, and an explicit 'USB-local' transport label. Downlink audio/control may be sent back over the same serial path while LTE registration is absent.
- **owner gets:** The worn pendant becomes useful today on the owner's desk instead of waiting for LTE registration. A button press, alert, or diagnostic result can reach the same voice/desktop system with clear local status, and a dropped network does not silently lose events.
- effort: Medium: serial framing/parser, transport adapter in the relay bridge, replay cursor, and a small dashboard status indicator; test against both live USB device paths.  ·  risk: Malformed or stale serial frames could trigger duplicate alerts or replay old audio. Use monotonic sequence numbers, device boot IDs, bounded buffers, and discard unacknowledged downlink audio on reboot; recover by reconnecting and resynchronizing state.
- cost: Negligible API cost while USB-local; roughly 1-2 weeks engineering. No hardware purchase and no meaningful additional power beyond the already-connected boards.  ·  latency: Button/event delivery should be tens of milliseconds locally; audio latency depends on the Mac-to-relay websocket but avoids LTE setup delay.
- security: USB serial is a privileged local channel. Bind the session to the authenticated Mac agent and device identity, encrypt relay traffic, expose transport state, and never treat USB presence alone as permission for destructive Mac actions.
- depends on: A real mac_serial_exchange or equivalent serial read/write capability (currently requested but not available); A relay transport adapter that accepts device-scoped sequence-numbered events; The existing pendant firmware event framing and Mac bridge authentication


## What it asked for

_Nothing._
