# Harness derivation — browser-extension — round 266

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the pendant and ask “what needs me online?”, scan the authenticated pages I already have open, find concrete deadlines or actions, and tell me the top three with the exact page links."
- **useful because:** This is the browser node's highest-value job: it can see logged-in pages no other node can. It turns an arbitrary open Safari state into an on-demand, wearable briefing without inventing a site allowlist or requiring a scheduled portal integration.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Realtime for the short spoken answer; a cheaper background browser extraction pass for each tab, with mac-planner only normalizing dates and deduplicating actions.
- **latency:** 8–20 seconds for up to six open tabs; speak an interim “scanning” acknowledgement after 1 second.
- **cost:** About $0.02–$0.08 per invocation; browser extraction and one realtime turn dominate, not storage.
- **security:** Only inspect currently open tabs and persist no page body. Return short claims with URL/provenance, using the existing 24-hour/200-character browser-finding limits. Ship an empty per-origin policy and expose every extracted claim in the dashboard before any local action.
- **missing:** A reliable browser action dispatch path that resolves browser_list_tabs/browser_snapshot/browser_read_page; A relay intent that starts an authenticated multi-tab scan from a pendant button/voice event; A deadline/action extractor that emits claim-level provenance rather than page text

### "Copy the verification code from the logged-in page I have open into the waiting app on my iPhone, but do not press the final submit button."
- **useful because:** Today the owner must context-switch between an authenticated Safari session and an iPhone app. The browser can read the code while the Mac/iPhone facet can place it in the real app; the pendant provides one spoken request and the system leaves the irreversible final tap to the owner.
- **path:** browser → mac-planner → ios → pendant → relay
- **model tier:** A low-cost extraction model identifies a short-lived code and its field; mac-planner coordinates the deterministic iPhone Mirroring actions. Realtime is used only for the brief pendant confirmation.
- **latency:** Under 15 seconds after the page and app are already visible; fail closed if the code is expired, ambiguous, or more than one candidate exists.
- **cost:** Roughly $0.01–$0.04 per invocation; OCR/page extraction and one planner turn dominate.
- **security:** Treat codes as ephemeral secrets: never persist in browser findings, logs, transcripts, screenshots, or spoken audio. Require the owner’s explicit request for each transfer, target the currently foreground app, mask the value in receipts, and stop before submit/continue. If the page is not HTTPS or the target field is unclear, do nothing.
- **missing:** A browser_read_page/browser_snapshot action that reliably returns page text or a targeted field; An ios-control action exposed through mac-planner for secure type/paste with secret redaction; A transient secret handoff channel between browser and iOS facets that is excluded from memory and receipts

### "On the appointment page I’m viewing, find the earliest slot that does not conflict with my Mac calendar, fill the form through the review screen, and tell me exactly what will be booked without submitting."
- **useful because:** This combines the browser’s authenticated reach with the Mac’s private calendar and turns a tedious search into a reviewable result. Neither node alone can safely choose a slot: the browser cannot see calendar conflicts, and the Mac cannot access the logged-in booking page.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** A cheap browser extraction pass enumerates available slots and form fields; mac-planner performs deterministic Calendar conflict checks; realtime only reads back the selected slot and asks whether to proceed, while submission remains a separate owner action.
- **latency:** 15–30 seconds for up to 30 slots; show progress if the portal is slow. Stop at the final review screen.
- **cost:** About $0.03–$0.10; portal extraction plus calendar lookup dominate, with no need to send full page text to the model.
- **security:** Use only the currently open page and an explicit empty-to-start origin configuration. Do not persist appointment details or form values beyond the task receipt; redact health/legal fields by default. Never click the final booking/submit control. Display the exact date, timezone, attendees, cost, and cancellation terms on the dashboard and pendant.
- **missing:** A structured browser form-field/option extractor and a stable way to identify the final submit control; A calendar availability query exposed to mac-planner without returning unrelated event contents; A cross-surface task state that carries candidate slots and provenance while excluding sensitive form values from logs

### "After you do something on my Mac or iPhone, verify it in the logged-in website and tell me whether the outside service actually accepted it—not merely whether the local click succeeded."
- **useful because:** Local automation can report that a button was clicked while the service rejected the request, timed out, or silently changed a field. The browser is the only node that can independently inspect the authenticated confirmation state, giving the owner a trustworthy end-to-end answer from the pendant.
- **path:** pendant → relay → mac-planner → ios → browser → dashboard
- **model tier:** Use a cheap deterministic verifier for expected confirmation markers and key-value comparisons; reserve realtime for a concise spoken result and escalate to the stronger planner only when the site presents an unfamiliar confirmation state.
- **latency:** Verify within 10 seconds of the local action, with a second poll after 5 seconds for asynchronous services. Say “still processing” rather than guessing.
- **cost:** Approximately $0.01–$0.05 per verification; most cost is one browser read and optional delayed poll, not generation.
- **security:** Carry only an action fingerprint and expected fields into the browser verifier, never the full local transcript. Persist a short claim with URL, timestamp, and outcome—not page text, screenshots, tokens, or form secrets. If the page cannot prove acceptance, report unknown and never infer success from a redirect.
- **missing:** A durable correlation ID shared by Mac/iOS action receipts and the follow-up browser job; A browser verifier that can compare expected fields against a confirmation page while excluding secrets; A relay workflow that schedules a delayed browser poll and sends a compact verified/failed/unknown alert to the pendant

### "Tell me whether this problem is my account or the service: inspect the logged-in error page in Safari, check the same service from my Mac’s network, and give me the next best recovery step."
- **useful because:** A single browser screenshot cannot distinguish a revoked account, a regional outage, a stale session, or a local network failure. Combining authenticated page evidence with an independent Mac check prevents the owner from repeatedly retrying the wrong fix.
- **path:** browser → mac-terminal → mac-planner → relay → pendant
- **model tier:** A small classifier compares page error markers with a deterministic Mac connectivity/HTTP probe; use realtime only to explain the diagnosis and one next step.
- **latency:** 5–15 seconds, with a second probe after 10 seconds when the service is intermittent.
- **cost:** About $0.005–$0.03 per invocation; network probes are cheap and the browser page read is the main variable.
- **security:** Do not transmit credentials, cookies, or full page contents to the relay. Redact account identifiers from the spoken answer and persist only a short diagnosis, service host, and timestamp if the owner asks for history. Never attempt password reset or account recovery automatically.
- **missing:** A browser-to-Mac diagnostic correlation job that can compare an authenticated error with an unauthenticated network probe; A small allowlisted network probe action on mac-terminal that returns status class and timing without response bodies; A reusable diagnosis vocabulary surfaced in the pendant alert and dashboard

### "Compare the form I’m looking at in Safari with the matching document on my Mac, flag any disagreement, and fill only the fields that match—leaving anything uncertain for me."
- **useful because:** Copying data between a local document and an authenticated web form is error-prone, especially for dates, names, and account numbers. The browser supplies the real field schema while the Mac supplies the owner’s private source document; a field-level comparison catches silent mistakes before submission.
- **path:** browser → mac-planner → mac-terminal → pendant → relay → dashboard
- **model tier:** A low-cost extraction model produces normalized field/value pairs from the local document and page; a deterministic comparator marks exact, format-equivalent, conflicting, and missing values. Realtime only summarizes conflicts.
- **latency:** 10–25 seconds for one document and one form; stop immediately when a conflict is found in a high-risk field.
- **cost:** Approximately $0.02–$0.07 per form; local extraction is cheap, while the browser read/write loop dominates.
- **security:** Keep source values on the Mac wherever possible and pass only hashes plus field decisions to the coordinator. Never persist account numbers, government IDs, or document text; mask them in receipts and spoken output. Fill is reversible, but never submit. Require an explicit owner request naming the source document and target page.
- **missing:** A field-level browser form read/write API with stable field identities and a guaranteed no-submit mode; A local-document extraction action that can return typed values without uploading document contents; A transient comparison record with per-field provenance and automatic secret redaction


## What it asked for

_Nothing._
## Its own summary

Discovered Safari on MacIntel is online with 1 tab, but the granted browser wrappers still cannot execute: browser_list_tabs is ambiguous and browser_enqueue_command_implemented is unresolved. I recorded three cross-surface capabilities: on-demand authenticated-tab triage from the pendant, ephemeral Safari-to-real-iPhone verification-code transfer that stops before submit, and calendar-aware appointment-slot selection that fills to review without booking. I also notified mac-planner that the resolver needs an exact live browser action contract. What I still need is a callable read-only browser path (list/snapshot/read/navigate) and a transient, redacted handoff for browser-to-iOS secrets; without the first I cannot inspect the currently open authenticated page.

**Biggest unknown:** The URL and content of Safari's live tab remain unknown because action dispatch fails before the extension is called.

