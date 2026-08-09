# Harness derivation — mac-planner — round 270

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac readiness round 270** — Mac agent is fully ready: Accessibility and Screen Recording trusted, synthesized input verified, browser bridge online with Safari on Discord and 6 tabs, relay reachable, pendant pipeline capabilities configured. The earlier TCC blocker is gone.
  - evidence: GET /ops/status HTTP 200 and GET /observe HTTP 200 at 2026-08-09T01:13Z: ready:true, accessibility.trusted:true, eventsPost:true, screenRecording:true, browser online.

## Capabilities it proposed

### "When I ask “what am I looking at, and what should I do next?”, use the pendant, my current Mac window, browser tab, calendar and mail to give me a concise answer, then offer to carry out the next safe step."
- **useful because:** This is the single most useful everyday capability: it turns an arbitrary moment of confusion into grounded situational help instead of making the owner describe the screen, URL, deadlines, and surrounding context manually. It works because the worn voice surface, authenticated browser, Mac vision, and personal sources each contribute facts no node has alone.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime for the short spoken clarification and final answer; a cheaper background model for extracting page/UI facts and ranking calendar/mail context; never send raw mail bodies or screenshots to the realtime model unless needed.
- **latency:** Initial spoken acknowledgement under 500 ms; parallel context collection 2–5 s; answer under 8 s. Any mutation is a separate explicit action after the answer.
- **cost:** Roughly $0.02–$0.10 per invocation depending on screenshot tokens and realtime duration; dominant cost is vision/context input, not the small ranking pass.
- **security:** The browser may contain authenticated private pages and the screen may contain secrets. Redact passwords, tokens and unrelated windows; send only the active window/tab and bounded mail snippets. Mutations must be separately previewed and logged; empty owner policy must stop execution rather than silently click.
- **missing:** A server-side orchestrator that joins the active UI snapshot, browser page semantics, calendar/mail snippets and a short-lived spoken request into one bounded context envelope.; A reliable page/UI redaction and provenance format so the answer can cite which fact came from the screen versus the browser versus mail.; An explicit owner policy entry authorizing the particular follow-up action classes.

### "Keep a watch on one authenticated browser page I name, and when its meaningful content changes, summarize only the delta on my pendant; if it asks for a consequential action, draft the action but do not submit it."
- **useful because:** The owner currently has to remember to revisit dynamic dashboards, queues, and tracking pages. A durable browser watch turns the extension’s authenticated session into an always-on scout while keeping the pendant as the only interruption channel. It is specifically browser-harness work, not a generic work-portal briefing.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** Cheap background model for DOM-to-structured extraction and change classification; realtime only when an urgent delta is actually delivered or the owner asks follow-up.
- **latency:** Poll or push within 1–5 minutes of a page change; notification rendering under 2 s. Batch low-value changes into a digest and suppress unchanged boilerplate.
- **cost:** About $0.001–$0.02 per check when using hashes and extracted fields; model cost is dominated by first-page extraction, not unchanged polls.
- **security:** The watch must be scoped to an explicit tab/session and selector or page fingerprint, with credentials never leaving the browser. Store hashes and redacted structured fields rather than full HTML. Never auto-submit forms, send messages, purchase, or delete; those become a Mac plan requiring explicit owner invocation and policy authorization.
- **missing:** A browser page-watch scheduler with per-session selectors, semantic field extraction, and DOM/change hashes.; A durable diff-to-inbox route that can create an alert record consumed by the existing pendant offline_alert_inbox, including urgency and expiry.; A browser-side confirmation handoff that can return a proposed action to mac-planner without exposing the session cookie.

### "When I press the pendant’s moment button, make a private incident packet containing the exact pendant timestamp, the active browser URL/title, a redacted screenshot of the current Mac window, and the nearest calendar event; later let me say “show me the moments from Tuesday” and open the matching packet."
- **useful because:** A moment bookmark currently records that something happened, but not what the owner was seeing or why it mattered. This creates a searchable, privacy-bounded external memory for debugging, research, difficult conversations, and fleeting ideas without continuously recording the owner.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** No model for capture; use deterministic metadata and screenshot redaction. A cheap background model may label packets and resolve a date query. Realtime is only for spoken retrieval or confirmation.
- **latency:** Button acknowledgement locally immediately; metadata and screenshot committed within 3 s; retrieval answer under 5 s and opening the packet under 2 s.
- **cost:** Near-zero model cost for capture; storage is the dominant cost, roughly a few MB per hundred redacted screenshots. Optional labeling costs cents per batch.
- **security:** Capture only on the explicit moment button, never ambiently. Exclude password fields, secure input, unrelated windows, and page bodies unless the active page is explicitly allowed. Encrypt at rest, retain a configurable TTL, and show a visible LED/inbox state when a packet is queued. Opening a packet is read-only; sharing/export requires a separate policy entry.
- **missing:** A relay ledger schema that atomically joins the offline_moment_bookmark event with Mac/browser observations using a clock offset and correlation id.; A redaction service that produces a screenshot plus provenance manifest without retaining the unredacted image.; A date/semantic retrieval endpoint and a Mac open-packet action that can present the selected evidence safely.

### "Let me say “rehearse this before I do it” while looking at a real authenticated web workflow, and have the system build a private, non-submitting simulation of the next steps: show the expected page transitions and resulting calendar/files/messages, narrate risks through the pendant, and leave me a reversible draft I can approve later."
- **useful because:** Today the owner must either trust a consequential click sequence or manually duplicate it in a test environment. A cross-surface rehearsal would make unfamiliar forms, scheduling changes, purchases, and account workflows understandable before anything is sent. It is not an approval gate bolted onto execution; it is a separate capability that produces a concrete forecast and draft artifact without touching the real account.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** A background reasoning model builds a structured state-transition graph from the current page and the requested goal. A cheap deterministic simulator handles form validation, date arithmetic, and file diffs. Realtime is used only to narrate the rehearsal and answer a short spoken question.
- **latency:** First spoken summary in 2 seconds; a five-to-ten-step rehearsal in under 15 seconds; a larger workflow may take up to 60 seconds while emitting progress to the pendant.
- **cost:** Approximately $0.05–$0.30 per rehearsal, dominated by screenshots/DOM snapshots and the reasoning pass; deterministic previews and cached page schemas keep repeated steps cheap.
- **security:** The simulator must never submit, send, purchase, delete, or navigate destructive endpoints. It needs an isolated browser context or request-interception sandbox, synthetic form values by default, and explicit marking of any transition that cannot be simulated. Authenticated page content remains on-device or in an encrypted short-lived workspace. Drafts must record source URL, assumptions, predicted side effects, and expiry; only a later owner command may execute a reviewed plan under the owner’s configured policy.
- **missing:** A browser harness that can fork an authenticated session into a non-committing isolated context or intercept and replay requests without side effects.; A typed state-transition and side-effect model shared by browser actions and Mac actions, including confidence and unknown effects.; A durable draft/rehearsal artifact with assumptions, predicted diffs, expiry, and a handoff from pendant speech to mac-planner execution.; A deterministic network and UI recorder that can replay a workflow without storing passwords or unrestricted page history.

### "When you use my information to answer, let me ask “why do you know that?” and get a compact, source-by-source provenance view across the pendant, relay, Mac, browser and personal sources; let me revoke one source or erase one derived fact without deleting unrelated memory."
- **useful because:** The owner cannot currently distinguish a fact read from Mail, inferred from a browser page, remembered from a prior conversation, or guessed by a model. Provenance and selective revocation make the hive trustworthy enough for sensitive work: the owner can correct one stale source without wiping useful history, and can see exactly which surfaces received the data.
- **path:** relay-realtime → pendant → mac-planner → browser-extension → mac-vision
- **model tier:** Deterministic provenance manifests and cryptographic identifiers do the core work; a cheap model compresses the explanation into plain language. Realtime only speaks the short answer on request.
- **latency:** Normal answer adds less than 300 ms when provenance is already attached; a full multi-source trace under 3 seconds; revocation acknowledgement under 2 seconds.
- **cost:** Less than $0.01 per lookup in normal use; storage and indexing of manifests dominate, with occasional model cost for natural-language compression.
- **security:** Provenance itself can reveal sensitive URLs, message subjects, or private memories. Keep raw values local, return redacted labels by default, encrypt manifests, and make deletion cryptographic and auditable. Revocation must propagate to relay caches, browser-derived records, Mac drafts, and pendant inbox entries rather than merely hiding a UI row.
- **missing:** An end-to-end provenance envelope attached to every observation, inference, generated artifact, and spoken answer.; A cross-node deletion/revocation protocol with tombstones, cache expiry, and proof of completion.; An owner-facing provenance query and correction surface reachable by short pendant speech plus a detailed Mac view.; A memory model that distinguishes observed facts, owner assertions, inferences, and actions instead of storing one undifferentiated text record.

### "Let me grant a spoken, time-limited delegation such as “for the next 20 minutes, use this browser tab to gather prices and make a draft, but do not buy, message, or change my account,” and have the same delegation follow the task across the browser, Mac and relay until it expires."
- **useful because:** The owner currently faces a bad choice between broad unattended control and manually supervising every harmless step. A delegation is understandable in human terms—goal, surfaces, duration, and prohibited effects—and travels with the task, so a reconnect or handoff cannot accidentally widen authority. It lets the hive do useful bounded work without pretending that a global policy is sufficient.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision
- **model tier:** Deterministic policy evaluation enforces scope, expiry, surface and action classes; a cheaper model translates spoken language into a structured delegation and asks a clarification only when the boundary is ambiguous. Realtime handles the spoken confirmation and expiry notice.
- **latency:** Parse and confirm in under 2 seconds; policy check below 50 ms per action; revoke propagation to all nodes under 1 second when connected.
- **cost:** Under $0.01 per delegation outside the initial speech interaction; the main cost is durable audit storage and occasional language parsing.
- **security:** A delegation must be deny-by-default, bound to a specific task/session and browser tab, carry an absolute expiry, and be revocable locally from the pendant even offline. Secrets, purchases, outbound communication, account/security changes, and destructive filesystem actions remain prohibited unless separately named. Every attempted violation should be visible in a receipt, not silently skipped.
- **missing:** A cross-node delegation token format carrying principal, goal, allowed surfaces, allowed action classes, forbidden classes, expiry, and revocation version.; Enforcement in both browser command execution and Mac FULL_CONTROL execution; today FULL_CONTROL_MODE bypasses the risk scorer, so this cannot be implemented as a prompt convention.; A local pendant revocation flag that the relay and Mac honor on reconnect, plus an append-only decision ledger.; A structured natural-language delegation parser that reports uncertainty instead of broadening scope.


## What it asked for

_Nothing._
## Its own summary

Round 270 produced three distinct hive-native capabilities: active-moment situational guidance, authenticated browser semantic change watches, and explicit pendant-triggered evidence packets. Live discovery also established that the Mac is fully ready now: Accessibility and Screen Recording are trusted, input posting is verified, Safari bridge is online, relay is reachable, and the pendant pipeline is configured. I no longer need TCC permission work.

**Biggest unknown:** The remaining product gap is orchestration rather than Mac reach: whether the relay has a durable correlation/diff/retention layer that can join a pendant bookmark with simultaneous Mac and browser observations, and whether a semantic browser page-watch API exists beyond the low-level polling routes. The previously queued semantic-context read request remains the most useful missing tool; do not build new Mac control primitives until that is answered.

