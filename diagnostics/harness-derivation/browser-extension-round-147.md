# Harness derivation — browser-extension — round 147

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Watch the logged-in pages I nominate and tell me only what materially changed since the last check, with a cited before/after summary on my pendant."
- **useful because:** The browser is the only node that can see authenticated dashboards, while the relay can run unattended and the pendant can deliver an alert without reopening Safari. This turns silent account changes into actionable, low-noise awareness rather than periodic full-page dumps.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → dashboard
- **model tier:** background/scheduled cheap model for polling and diffing; realtime only when the owner asks a follow-up
- **latency:** Scheduled checks every 30–60 minutes; alert delivery under 10 seconds after a detected change; follow-up under 2 seconds if cached evidence is sufficient.
- **cost:** Usually <$0.01 per check for extraction/diff plus relay storage; dominant costs are authenticated browser round trips and occasional model summarization.
- **security:** Must ship with an empty per-origin configuration and require the owner to nominate sites and categories. Store hashes/structured deltas by default, not page text; redact secrets and never speak configured-never-speak categories. Filling or submitting actions are out of scope. Alerts should expire locally and remain on-device only until spoken.
- **missing:** Durable scheduled browser-session runner that can reopen/pin a nominated origin without relying on an already-open tab; Per-origin extraction selectors and owner-supplied sensitivity/retention policy UI; A semantic snapshot/diff format with evidence lineage and alert deduplication; Pendant alert payload support beyond the already-accepted offline_alert_inbox queue

### "Read the private page open in Safari even when its useful information is only visual—charts, canvas dashboards, or rendered PDFs—and explain the exact evidence to me through the pendant."
- **useful because:** DOM extraction fails on many authenticated dashboards and PDFs, while mac-vision can see pixels but cannot independently reach Safari's logged-in session. Combining the browser extension's tab/session with Mac vision gives the owner access to information neither node can obtain alone.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** cheap vision/OCR model for first pass; realtime model only for the owner's spoken question or ambiguity resolution
- **latency:** 3–8 seconds for a viewport capture and OCR; under 15 seconds for chart interpretation; no navigation or mutation unless explicitly requested.
- **cost:** Roughly $0.01–$0.08 per visual page depending on image size; image tokens dominate, with browser and local capture otherwise negligible.
- **security:** Pixel data may contain secrets not exposed by DOM redaction. Apply origin/category policy before sending images to a model; prefer on-Mac OCR and transmit only extracted regions/values. Keep evidence ephemeral and cite tab URL, timestamp, and viewport; never infer that a visual value is safe to speak merely because DOM text was empty.
- **missing:** A browser_snapshot result that returns a screenshot or bounded element image with tab/session provenance; A mac-vision handoff accepting a browser tab capture rather than taking over the whole desktop; Region-aware redaction and chart/PDF evidence objects; Pendant playback of cited visual answers

### "Find an appointment in my logged-in site that fits my real calendar, fill the booking form, and read me the exact proposed time, provider, price, and cancellation terms on the pendant without submitting it."
- **useful because:** This joins three otherwise disconnected facts: the browser has the authenticated booking session, the Mac has the owner's calendar, and the pendant is the fastest place to answer the final human question while away from the screen. It saves the tedious comparison work but preserves the owner's control over the irreversible booking click.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** background planner for searching/ranking slots and extracting terms; realtime tier only to answer the pendant's final spoken question
- **latency:** 30–90 seconds for search and calendar intersection; under 5 seconds to speak the draft; leave the filled form visible for inspection.
- **cost:** $0.03–$0.20 per booking search, dominated by multiple authenticated page reads and terms extraction; local calendar lookup is negligible.
- **security:** Owner must supply an empty, inspectable per-origin policy before first use. Treat health, financial, and identity fields as never-speak/never-store unless explicitly enabled; do not log form values. Never submit, pay, or send; include a deterministic draft hash and the exact destination URL so the owner can inspect what would be committed.
- **missing:** Reliable browser tab/session affinity across a multi-step search and form fill; Calendar free/busy capability exposed to the planner with timezone and travel buffers; Form-field extraction that distinguishes editable draft fields from submit/payment controls; A pendant spoken draft-and-commit interaction that can return the selected draft hash to the browser

### "Join the private video meeting already on my calendar, stay quiet, and tell me through the pendant only when I am directly addressed or a decision/action is assigned to me; afterward give me a cited action list."
- **useful because:** Today the browser can reach a logged-in meeting site, the Mac can see the calendar and handle local audio, and the pendant can interrupt the owner, but no one coordinates them into an ambient meeting delegate. This would let the owner stay informed while moving away from the screen without recording or summarizing every conversation by default.
- **path:** mac-planner → browser-extension → mac-vision → relay-realtime → pendant → dashboard
- **model tier:** background audio/event classifier and compact summarizer; realtime tier only for a low-latency pendant interruption or the owner's follow-up question
- **latency:** Join within 30 seconds of the scheduled start; address/action detection within 2–4 seconds; post-meeting action list within 2 minutes.
- **cost:** Approximately $0.10–$0.75 per meeting hour, dominated by streaming audio transcription and summarization; browser control and calendar lookup are negligible.
- **security:** This is highly sensitive third-party communication. Default to local processing where possible, no raw audio retention, explicit per-meeting or per-origin policy, visible joined/muted state, and a hard stop at meeting end. Never send chat messages, speak, accept invitations, or make commitments. Store only owner-directed action items with speaker/time citations.
- **missing:** A meeting-aware browser integration that can join a nominated authenticated meeting URL and report participant/session state; Mac audio routing and consent-aware capture of the meeting tab, separate from the pendant microphone; Low-latency speaker attribution and direct-address/action detection with a no-raw-audio retention mode; A scheduled calendar-to-browser handoff that supplies the meeting URL and end time; Pendant interruption payloads that identify the meeting, speaker, and detected action without replaying sensitive audio

### "When a logged-in website stops on a CAPTCHA, passkey, or one-time-code step, alert my pendant with the site and exact next action, let me complete the challenge, and resume the paused task without exposing the rest of the page."
- **useful because:** Authenticated automation currently breaks at the boundary between browser session and human presence. This would make the system useful on real sites with anti-bot and step-up authentication while keeping the secret and biometric decision with the owner.
- **path:** browser-extension → relay-realtime → mac-planner → pendant → dashboard
- **model tier:** cheap background state detector; realtime only for the brief pendant exchange while the owner completes the challenge
- **latency:** Detect a blocked step within 2 seconds; alert within 5 seconds; resume within 10 seconds of the owner completing it.
- **cost:** Under $0.02 per interruption; browser polling and local challenge detection dominate, not model inference.
- **security:** Never read, persist, or repeat OTPs, passwords, or passkey material. Send only origin, challenge type, and a non-secret task identifier. Require an explicit owner-configured allowlist of origins; expire task state after a short timeout; do not auto-submit after resumption.
- **missing:** Extension events for challenge/consent UI state and a reliable resume token; A pendant interaction that acknowledges completion without carrying the secret; Browser task checkpoints that survive a challenge page and prevent duplicate submissions; Origin policy entries distinguishing permitted authentication handoffs from prohibited automation

### "Take the document I name on my Mac, verify its contents and destination against the private portal open in Safari, upload it as a draft, and tell me the exact filename, size, and recipient on the pendant before anything is sent."
- **useful because:** The browser alone cannot safely identify the right local file, and the Mac alone cannot see the portal's authenticated destination. Joining local file provenance, authenticated browser context, and an eyes-free pendant readback prevents the common failure of uploading the wrong sensitive document to the wrong person.
- **path:** mac-terminal → mac-planner → browser-extension → relay-realtime → pendant → dashboard
- **model tier:** cheap local classifier/hash checker and browser extractor; realtime only for the final spoken readback
- **latency:** 10–30 seconds to identify and inspect the file and portal; under 3 seconds for the pendant readback; leave the upload unsent.
- **cost:** Usually below $0.03, dominated by optional document classification; hashing and local metadata inspection are free.
- **security:** Keep file bytes on the Mac unless the owner explicitly enables remote analysis. Speak metadata and destination, never document contents by default. Show a content hash, origin, and destination URL; do not click send/submit. Avoid retaining uploaded copies or extracted sensitive text.
- **missing:** A browser form model that exposes upload controls and recipient context without submitting; A Mac-side file provenance object carrying path, hash, MIME type, and a minimal sensitivity result; A resumable draft-upload operation with an explicit unsent state and cleanup; A cross-surface evidence bundle linking the selected local file to the browser destination


## What it asked for

_Nothing._
