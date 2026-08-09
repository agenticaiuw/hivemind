# Harness derivation — mac-planner — round 169

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser state** — The Mac bridge and Safari extension are online, with Accessibility and Screen Recording granted to AI Pendant Agent; the foreground app is Claude, 18 apps are running, and the browser bridge reports 9 Safari tabs. The pendant is physically USB-connected per system context but no serial-exchange tool is available in this round.
  - evidence: mac_readonly_inspect(operation=running_apps) returned GET /observe at 2026-08-08T01:05:40Z; GET /ops/snapshot returned mac_bridgeOnline=true, browser online=true, accessibility trusted=true, screenRecording granted=true.

## Capabilities it proposed

### "When I press the pendant's bookmark button, remember not only the moment but what I was looking at, and later bring that context back when it becomes useful."
- **useful because:** A timestamp alone is easy to forget. This would turn an interruption into a recoverable thread: the owner can mark a thought while away from the keyboard, then receive a short, relevant reminder and reopen the exact document or tab instead of searching.
- **path:** pendant → mac-planner → browser → relay → dashboard
- **model tier:** background for context matching and summarization; realtime only for the spoken acknowledgement
- **latency:** Button acknowledgement under 1 second locally; capture under 5 seconds; later relevance evaluation in the background, with a 10-second spoken reminder budget.
- **cost:** About $0.01–$0.04 per captured/resurfaced item, dominated by one small summarization/matching call; local metadata capture is free.
- **security:** Capture only app/document identity, URL, title and a redacted text excerpt; never capture page bodies or passwords by default. Reopening a tab/file is an external action and should be represented in the owner's configured policy. The owner needs a delete-this-memory command.
- **missing:** A durable event schema joining the existing offline_moment_bookmark payload to a Mac/browser context snapshot; A background relevance matcher that can subscribe to calendar/mail/browser changes without uploading unrestricted page contents; A pendant alert payload that can carry a context reference and an expiry, rather than only plain alert text

### "Keep my pendant usable when LTE is unavailable: if it is plugged into my Mac, carry the live voice session over the pendant's USB serial connection and the Mac's network, then migrate back to LTE when the radio registers."
- **useful because:** The hardware is physically present now but the pendant is not relay-registered, so the owner otherwise loses the defining experience exactly when testing or indoors. This makes the worn device useful today, and a walk-away transition can happen without restarting the conversation.
- **path:** pendant → mac-planner → relay → browser
- **model tier:** realtime for the active audio session; background for link-quality telemetry and migration bookkeeping
- **latency:** USB audio/control bridge under 100 ms one-way target; migration pause under 2 seconds; no model call solely for transport switching.
- **cost:** Negligible model cost during transport changes; active voice cost remains the existing realtime session. Engineering cost is mostly serial framing, reconnect state and end-to-end testing.
- **security:** Pair the USB serial device to the same relay identity as the pendant and refuse unknown serial descriptors. Do not expose raw microphone data to unrelated Mac apps. Persist only sequence numbers and transport state; encrypted audio must remain in the existing session channel.
- **missing:** A Mac USB-serial bridge for /dev/cu.usbmodem00096003658* and the ESP32 bridge port, with framed duplex audio and reconnect; A relay session transport abstraction that can change between USB-over-Mac and LTE without duplicating or reordering Opus frames; Pendant registration/pairing over USB before LTE registration, plus an explicit owner-visible transport indicator

### "If I unplug the pendant or my Mac is about to sleep, save a tiny handoff of the active conversation and desktop context; when I reconnect, tell me what was unfinished and offer to restore it."
- **useful because:** Cable loss and sleep are ordinary failures today, especially while the pendant is being tested over USB. The owner should not have to remember which question, tab, file or audio response was mid-flight; the system should recover the thread without saving a full recording.
- **path:** pendant → mac-planner → relay → browser → dashboard
- **model tier:** background for compressing the handoff; realtime only to announce recovery over the pendant
- **latency:** Detect disconnect/sleep within 2 seconds; write a local handoff atomically within 1 second; recovery brief under 5 seconds after reconnect.
- **cost:** Roughly $0.005–$0.02 per handoff, usually one short summarization call; most handoffs can be structured metadata without a model.
- **security:** Keep the raw transcript and document excerpts local by default, with a redacted summary uploaded only if the owner enables it. Never restore a tab or type into an app silently; restoration must use the owner's explicit unattended-action policy. Expire stale handoffs and provide deletion.
- **missing:** USB disconnect/sleep/wake event producers joining the pendant serial bridge and Mac agent; A compact encrypted handoff format with sequence checkpoints for audio, relay job, browser session and active Mac job; A reconnect resolver that distinguishes an interrupted action from a merely open session and reports exact receipts before offering restoration

### "Tell me when my commitments contradict each other across Calendar, Mail, the browser, and my Mac files—for example, a meeting promises a deliverable whose deadline or owner differs elsewhere—and let me resolve the contradiction from the pendant."
- **useful because:** The owner currently has to remember and manually compare disconnected sources. A contradiction, rather than another summary, is the high-value signal: it catches impossible schedules, conflicting dates, and promises that silently disagree before they become failures. The pendant can deliver the one discrepancy that matters, while the Mac and browser provide the evidence and actions.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** background model for periodic cross-source reconciliation; realtime only for the owner's short question and spoken resolution dialogue
- **latency:** On-demand answer within 15 seconds; scheduled reconciliation within 2 minutes of a relevant source change; spoken alert under 3 seconds once a contradiction is confirmed.
- **cost:** Approximately $0.02–$0.10 per reconciliation, dominated by extracting and comparing small cited records; incremental event filtering should avoid rescanning everything.
- **security:** Compare structured metadata and minimal redacted snippets by default. Do not upload full mail bodies, private browser pages, or files unless the owner explicitly asks. Every contradiction must retain source citations and timestamps. Creating a reminder, editing Calendar, sending Mail, or changing a file requires the owner's configured automation policy; resolution suggestions must never imply that a change already happened.
- **missing:** A normalized commitment record with subject, actor, due time, confidence, source citation, and last-observed timestamp; Incremental change feeds from Calendar/Mail plus bounded, authenticated browser and Mac-file observations; A contradiction engine that distinguishes a true conflict from synonyms, superseded promises, and tentative language; A pendant interaction payload for presenting two short alternatives and recording the owner's chosen resolution; A cross-surface action planner that can apply the selected resolution and return receipts from each affected surface

### "After I use the pendant, tell me exactly what information left my Mac, which model or surface saw it, and what was retained—without making me inspect logs."
- **useful because:** The owner cannot currently answer the basic privacy question, “what did that interaction disclose?” A concise, source-linked receipt would make the hive understandable and let him revoke or delete retained material instead of trusting an opaque voice system.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** No model required for collection; use a cheap background model only to turn the structured ledger into a short human-readable explanation
- **latency:** Receipt available within 5 seconds of a session ending; pendant summary under 20 seconds; deletion status updated within 30 seconds.
- **cost:** Near-zero for structured logging; about $0.005–$0.02 for an optional explanation.
- **security:** The ledger itself is sensitive and must be encrypted, access-scoped to the owner, and redacted when displayed. It must distinguish content from metadata, include retention expiry, and support deletion receipts. The audit path must not capture additional content merely to explain what was captured.
- **missing:** A tamper-evident cross-node egress ledger covering pendant, relay, Mac, browser, and model calls; Per-payload classifications for raw audio, transcript, URL, page text, file content, and derived memory; Owner-facing retention and deletion controls that propagate to every node and return verifiable receipts; A compact pendant-readable privacy summary format

### "When you say a task is done, prove it across every surface involved: show me the resulting Calendar, browser, file, or message state and tell me what remains uncertain."
- **useful because:** Receipts today can say an action ran without proving the intended outcome. The owner needs completion evidence, not optimistic execution: a sent draft should be visibly sent, a file should contain the requested change, and a browser action should be verified in the authenticated session.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background model for comparing requested postconditions with observed state; realtime only for the final spoken result
- **latency:** Verification within 10 seconds for ordinary tasks, with a clear pending state for long-running work; never claim success before the relevant observation arrives.
- **cost:** Approximately $0.01–$0.06 per task, dominated by bounded verification and one short explanation; many checks can be deterministic.
- **security:** Verification must use read-only observations and preserve sensitive content minimization. Never infer success from a UI click or HTTP 200 alone. If verification cannot be performed, report “unverified,” not success. Any corrective action remains a separate owner-policy decision.
- **missing:** A typed postcondition language for files, Calendar, Mail, browser pages, and application state; Read-after-write observation adapters for each surface, including authenticated browser state; A join between action receipts and subsequent observations with timestamps and resource identity; A pendant response schema separating succeeded, failed, partially verified, and unknown


## What it asked for

_Nothing._
