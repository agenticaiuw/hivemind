# Harness derivation — relay-realtime — round 289

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Be my eyes for what’s happening on my Mac and tell me only the important changes while I’m away."
- **useful because:** This is the kind of thing only a multi-surface assistant can do: the Mac can observe and summarize, the relay can speak it, and the pendant makes it effortless to receive. It cuts down on constant checking and helps the owner focus.
- **path:** mac-bridge → relay → pendant → dashboard
- **model tier:** Mac planner/observation loop for change detection and summarization; relay only for low-latency delivery.
- **latency:** Observation runs in the background; spoken delivery should be under a second once an alert is ready.
- **cost:** Most cost sits on the Mac observation and summarization. Relay cost is a short spoken delivery.
- **security:** Summaries must be scoped to what the owner opted into observing. Sensitive content should be redacted and delivered to the right surface (pendant vs dashboard).
- **missing:** A Mac-side change detection pipeline that can watch sources (files, apps, logs, browser) and produce a prioritized summary.; A delivery mechanism that can queue alerts when the pendant is offline and deliver later.; A way to configure what counts as important (rules, ML ranking, or both).

### "When I say “show me the choices,” have the pendant let me browse a live set of Mac/browser results with the rotary wheel, hear one item at a time, and say “do this one” to carry out the selected action."
- **useful because:** A wearable voice interface is poor at presenting five search results or emails and asking the owner to remember an index. This makes the pendant useful while walking: the relay keeps the active result set, the Mac/browser supplies authenticated content, and a physical wheel provides reliable selection without a phone screen.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** Realtime model only interprets the short spoken commands and generates item summaries; mac-planner performs retrieval and action planning, while browser automation extracts authenticated results.
- **latency:** First list within 3 seconds; wheel-to-next-item audio under 500 ms; action completion may take longer but must stream a short state update.
- **cost:** About $0.01–$0.05 per interaction depending on spoken summaries; Mac/browser calls and Opus audio dominate rather than the realtime model.
- **security:** The relay must bind the result cursor to the owner session and expire it quickly so an old list cannot trigger a later action. Sending an item must use the existing owner policy and produce an explicit target summary; no new confirmation gate is required for reversible actions.
- **missing:** A rotary encoder and second deliberate action button in the pendant enclosure/firmware (the current single button cannot distinguish navigation from stop).; A relay-side cursor/result-set resource with expiry and reconnect recovery.; A low-latency downlink command for wheel events and an audio item-summary cache.

### "After you act on my Mac or in my logged-in browser, tell me not merely that it succeeded but what changed, using a before/after proof: “the draft was sent to Alex with subject X,” or “nothing changed because the page rejected it.”"
- **useful because:** Today a spoken success claim can be detached from reality, especially when the owner is away from the Mac. A before/after evidence bundle lets the owner trust a remote action, distinguishes a blocked workflow from an unchanged page, and makes failures actionable without opening a laptop.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use the realtime model only to turn the final structured evidence into one short spoken sentence. The Mac planner and browser harness collect deterministic state; a slower background model may summarize large diffs for the dashboard.
- **latency:** A terse acknowledgement in 1 second, followed by a verified result within 10 seconds for ordinary UI actions.
- **cost:** Roughly $0.01–$0.08 per completed action. The dominant cost is two page/app observations and optional screenshot or DOM diff storage, not language generation.
- **security:** Evidence may contain private email, page text, or screenshots, so retain only redacted structured fields by default and encrypt short-lived artifacts. The proof must never claim success from an intent receipt alone; require a postcondition observation or report “unverified.”
- **missing:** A transaction wrapper that captures normalized preconditions, action receipt, postcondition, and verification state across Mac and browser jobs.; Mac-side before/after snapshots for non-browser actions (mail, files, reminders) with secret redaction.; A relay spoken-result schema and short-lived evidence store; the dashboard can expose the full diff.

### "If I say “undo that” right after a remote action, reverse the last change on my Mac or in the browser—even if I am no longer looking at the screen—and tell me exactly what was restored and what cannot be undone."
- **useful because:** Remote voice control is dangerous mainly because a mistaken click is hard to repair from a pendant. A short-lived, cross-surface undo journal would make experimentation safe: undo a moved file, reverted reminder, edited draft, or browser form change without making the owner reconstruct the original UI.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime handles only the spoken reference and disambiguation. A deterministic inverse-action engine on the Mac/browser harness performs reversals; a background model can propose an inverse when no static inverse exists, but must label it as unavailable rather than bluff.
- **latency:** Resolve “that” against the last completed action in under 300 ms and start reversal immediately; speak the outcome within 3 seconds.
- **cost:** Usually under $0.01 per undo. Cost is primarily journal storage and occasional Mac/browser verification; model usage is limited to ambiguous natural-language references.
- **security:** The journal must store sensitive arguments encrypted and expire entries after a short window. Never silently substitute a different target when multiple actions match. Non-invertible operations (send, purchase, delete) should return “cannot undo” plus the safest available compensating action, consistent with the owner's maximum-access policy.
- **missing:** An inverse-action vocabulary and durable, encrypted last-action journal shared by Mac and browser execution.; Pre-action snapshots or compensating operations for files, reminders, browser forms, and app state.; A relay endpoint that resolves relative references such as “that” across sessions and returns reversal status to the pendant.

### "When I ask what is on a private page, let me choose the disclosure level—“just counts,” “subjects only,” “read the details,” or “nothing aloud, put it on the dashboard”—and enforce that choice while the authenticated browser session is inspected."
- **useful because:** A worn speaker is easy for nearby people to overhear, and a single spoken answer cannot safely serve a public street and a private room. This gives the owner useful browser and Mac awareness without forcing them to expose full email, health, or work content aloud.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Realtime interprets the terse disclosure command and speaks only the already-redacted result. Browser/Mac workers perform deterministic field extraction and redaction; a slower model may summarize only after the chosen ceiling is applied.
- **latency:** Counts or subjects within 3 seconds; dashboard-only delivery should acknowledge in under 1 second and complete asynchronously.
- **cost:** $0.005–$0.04 per request, dominated by browser inspection and optional dashboard rendering; avoid sending full page text to the realtime model.
- **security:** Disclosure level must be an explicit per-turn ceiling, never inferred upward from context. Redaction must happen before content reaches audio generation or model logs, and dashboard artifacts need short TTLs. If the page cannot be safely field-extracted, say so rather than read raw text.
- **missing:** A structured browser extraction/redaction contract that returns counts, metadata, subjects, and bodies as separate fields.; A relay session disclosure ceiling shared by browser, Mac, transcript, logs, and speech synthesis.; Dashboard-only result delivery and expiry for sensitive page excerpts.


## What it asked for

_Nothing._
## Its own summary

Recorded three owner-facing capabilities: a spoken disclosure ceiling for private browser/Mac reads, a rotary-wheel result browser for wearable selection, and proof-carrying remote actions (with an undo proposal also recorded). The proposals require new cross-surface state and extraction contracts, not merely more model access. A haptic hardware proposal and memory-projection wiring were correctly rejected as duplicates of existing backlog items.

**Biggest unknown:** The main unresolved product decision is which new physical interaction to build first: rotary selection for result sets or another input dedicated to navigation/undo. The current one-button pendant cannot safely provide either without ambiguity.

