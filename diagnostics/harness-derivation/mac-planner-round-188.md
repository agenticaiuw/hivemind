# Harness derivation — mac-planner — round 188

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the pendant's bookmark button, tell me what was on my screen and what I was doing at that moment, then save a private, timestamped 'moment card' I can ask for later."
- **useful because:** The owner can mark a fleeting moment without speaking. The worn button supplies the exact human timestamp, the Mac supplies foreground app/browser state, and the relay turns it into a searchable short card. This is much more useful than a bare bookmark because it reconstructs context after the fact.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** Use realtime only to acknowledge the button and speak one sentence; use a cheaper background model to summarize the captured Mac/browser context and index the card.
- **latency:** LED acknowledgement immediately; context capture within 2 seconds of the bookmark; spoken acknowledgement under 1 second; card enrichment within 10 seconds.
- **cost:** About $0.005-$0.03 per bookmark depending on whether a screenshot is summarized; most cost is vision/context summarization, not the short acknowledgement.
- **security:** A bookmark may capture sensitive screen content. Default to redacted metadata (app, URL origin, title, selected text only if explicitly enabled); never capture passwords or page bodies by default. Saving or exposing a card should follow the owner's private-workspace policy.
- **missing:** A live USB-serial event bridge from /dev/cu.usbmodem00096003658* into the Mac agent (LTE is not registered); A typed, read-only semantic screen/context capture that returns a timestamped snapshot and redacts secrets; A relay endpoint to persist and retrieve moment cards keyed by pendant bookmark id

### "Do this across my Mac and browser, and don't just say it worked: verify the final state and tell me in one sentence what changed and what remains unresolved."
- **useful because:** Today a plan can launch apps or enqueue browser commands, but the owner still has to trust a vague success response. A cross-surface transaction would execute the ordered Mac/browser work, inspect the resulting state, and report concrete postconditions—especially valuable for forms, files, and multi-tab work.
- **path:** relay-realtime → mac-planner → browser-extension → browser → dashboard
- **model tier:** Use a cheaper planning/reconciliation model for action decomposition and postcondition comparison; reserve realtime for the owner's spoken request and the final one-sentence receipt.
- **latency:** Preview within 1 second, execute in under 15 seconds for ordinary bundles, verify within 3 seconds after the last action; long jobs should stream progress and finish asynchronously.
- **cost:** Roughly $0.01-$0.05 per bundle; dominant cost is screenshot/page-state comparison when semantic verification is needed.
- **security:** Verification must not leak page bodies, tokens, or unrelated tabs. Keep a per-step touched-resource ledger, redact secrets in receipts, and require the owner's existing destructive-action policy before sending mail, deleting files, or buying. The current FULL_CONTROL_MODE has no live gate, so this needs explicit owner-configured policy rather than assuming today's permissiveness.
- **missing:** A shared transaction id and idempotency contract spanning /execute and browser command/result; Typed postcondition assertions (file exists/hash, URL/title/form state, app state) rather than free-form success text; A reconciliation route that can inspect both Mac and browser state after execution and emit a durable receipt

### "Use the pendant as my physical confirmation: stage a sensitive action on the Mac or in the browser, show me exactly what will happen, and only execute after I press the pendant button within the short validity window."
- **useful because:** This gives the owner a confirmation channel that is physically separate from the screen being acted on. It is practical for mail sends, purchases, deletion, or publishing: the Mac/browser can prepare and preview the exact target while the worn device supplies an intentional, time-bound confirmation.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Use a deterministic policy/transaction service for nonce issuance, expiry, and target hashing; use realtime only to explain the pending action and outcome. No expensive model should decide whether a button press authorizes a different target.
- **latency:** Preview in under 1 second; confirmation nonce valid for 30 seconds; button acknowledgement under 300 ms locally; execute and verify within 10 seconds.
- **cost:** Under $0.01 per action; cryptographic nonce and state handling dominate, with model cost limited to optional spoken summaries.
- **security:** The button must authorize an exact canonical action hash, not a vague intent. Bind nonce to session, target, and expiry; reject replay, stale presses, and changed browser tabs/files. Never speak or persist secret form values. This supplements—not silently overrides—the owner's destructive-action policy.
- **missing:** A USB serial button-event bridge working with the currently attached nRF9160 pendant; A relay-held, single-use confirmation nonce protocol shared by Mac and browser executors; Canonicalization and hashing for ordered Mac/browser actions plus a final-state verification receipt; A local pendant LED state for pending/expired/accepted confirmation that does not conflict with existing recording/inbox meanings

### "When you answer a question about something on my Mac or in my browser, let me ask “why?” and hear the exact sources and evidence behind that answer, with links or file paths I can open."
- **useful because:** It turns the agent from an opaque assistant into an accountable one. For a recommendation or summary, the owner can distinguish observed facts from inference and immediately revisit the underlying email, calendar event, browser page, or workspace file.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a low-cost structured extraction model to build a provenance graph; use realtime only to answer the short spoken “why?” follow-up. Do not use the expensive model merely to repeat stored citations.
- **latency:** Attach provenance during the original answer with under 2 seconds additional latency; answer a “why?” request in under 1 second from stored evidence.
- **cost:** Approximately $0.005-$0.02 per answer; the dominant cost is extracting stable claims and source spans, not citation lookup.
- **security:** Citations can expose private URLs, mail subjects, file names, or snippets. Redact sensitive spans by default, preserve source permissions, and never send raw page bodies to the pendant. A provenance record must expire or be deleted with its source snapshot.
- **missing:** A claim-level provenance graph linking spoken claims to source IDs and exact spans; Stable, permission-aware source references for Mac files, Calendar/Mail records, and browser pages; A spoken citation formatter that can distinguish observation, inference, and uncertainty

### "Watch for a contradiction between what I have scheduled, what I have committed to in recent mail or notes, and what I am currently doing in the browser; if you find one, tell me the smallest correction that prevents me from missing it."
- **useful because:** The owner currently gets separate calendar, mail, notes, and browser assistance, but no system checks whether those sources disagree. Catching “meeting moved but the deliverable is still due,” “I promised a reply during a blocked slot,” or “the active task conflicts with the next appointment” is a high-value intervention that no single surface can see.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Use a background model to normalize commitments and detect conflicts; use realtime only for a high-confidence alert and one-sentence corrective suggestion. Low-confidence conflicts should be silently logged rather than interrupting.
- **latency:** Reconcile after source changes within 1 minute; alert delivery under 2 seconds once a high-confidence conflict is found; never interrupt more than once per conflict cluster.
- **cost:** Approximately $0.02-$0.08 per reconciliation cycle, dominated by extracting commitments from recent mail/notes and comparing them with calendar and browser state.
- **security:** Mail and browser context are sensitive and must remain local or relay-redacted. Do not infer commitments from private content without an explicit source scope. Alerts need urgency, deduplication, quiet hours, and an audit trail so the owner can see why an interruption happened.
- **missing:** A commitment/obligation data model with confidence, deadline, source, and owner status; Incremental change watchers for Calendar/Mail/Notes and the active browser tab; A cross-source contradiction detector with deduplicated alert state; A relay-to-pendant alert payload that includes a compact explanation and expiry

### "Give me a private end-of-day account of where my attention actually went: combine the Mac apps and browser tabs I used, calendar time, and the moments I marked, then show me three patterns and one change for tomorrow."
- **useful because:** A calendar report says what was planned, while app and browser history show what happened. Joining those with the owner's deliberate pendant bookmarks produces an honest, low-effort reflection without recording microphone audio or requiring manual journaling.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Use a cheap scheduled summarization model; realtime is unnecessary except when the owner asks follow-up questions by voice.
- **latency:** Generate after the owner's configured day-end time in under 2 minutes; keep the spoken version to one short sentence with the detailed report available on the dashboard.
- **cost:** Approximately $0.01-$0.04 per daily report; the main cost is summarizing the event stream, not data collection.
- **security:** App and browser history can reveal sensitive behavior. Keep raw events on the Mac, upload only coarse intervals and selected domains/titles, allow per-app exclusion, and automatically delete raw detail after the retention period. Never infer health, emotion, or productivity as fact.
- **missing:** A privacy-preserving Mac/browser activity timeline with app/domain exclusions; A joiner for calendar intervals, browser/app intervals, and offline_moment_bookmark events; A scheduled reflection route with configurable retention and a dashboard export; A distinction between owner-marked moments and automatically observed activity


## What it asked for

_Nothing._
