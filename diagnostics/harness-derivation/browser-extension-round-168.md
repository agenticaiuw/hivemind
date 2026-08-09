# Harness derivation — browser-extension — round 168

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Every morning, privately check the authenticated pages I choose, compare them with yesterday, and tell me only what changed enough to matter.”"
- **useful because:** This is the browser's unique superpower: it can inspect logged-in Gmail, X, and future portals that the relay cannot reach. A configurable per-origin watch turns noisy authenticated pages into a few actionable spoken deltas, even when the owner never opens a screen.
- **path:** browser → relay-realtime → pendant → dashboard
- **model tier:** Background model performs DOM extraction, yesterday-vs-today diff, and priority ranking; realtime is used only when the owner asks a follow-up or the pendant speaks an urgent alert.
- **latency:** 5–20 seconds per origin in a scheduled background run; under 2 seconds to speak a cached urgent delta on the pendant.
- **cost:** Roughly $0.01–$0.08 per daily run depending on page count and extracted text; browser execution and relay storage dominate more than model tokens.
- **security:** The owner must explicitly configure origins and selectors/categories; ship empty by default. Keep raw authenticated text on the Mac, persist only redacted hashes, titles, timestamps, and owner-approved excerpts, and never send page bodies to the cloud unless requested. Do not submit, send, or mutate anything.
- **missing:** A scheduled browser page-watch worker using the existing extension command path; Per-origin extraction/redaction/retention configuration UI; A durable yesterday snapshot/diff store with deletion controls; Pendant alert routing for high-priority deltas

### "“Use the account pages I’m already logged into plus public sources to answer this question, and show me exactly which private page and public source support each conclusion.”"
- **useful because:** Today the relay can search public information or reason over pasted text, but only the browser can combine private account facts with current public evidence. This would make questions about bills, subscriptions, benefits, orders, and account settings answerable without the owner copying sensitive pages into chat.
- **path:** browser → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** A cheaper background model extracts and redacts page evidence and public citations; the realtime tier answers only the final conversational question and can quote the evidence on demand.
- **latency:** 15–45 seconds for a multi-page investigation; under 3 seconds for follow-up questions against the cached evidence.
- **cost:** About $0.03–$0.20 per investigation, driven by authenticated page extraction, public search, and evidence-grounded synthesis.
- **security:** Private evidence stays local by default and is represented in the relay by opaque evidence IDs plus redacted snippets. The dashboard shows every origin consulted and lets the owner delete the investigation. Never infer or expose secrets not needed for the answer; no account mutation or submission.
- **missing:** A browser evidence capsule format that binds quoted claims to tab URL, timestamp, and DOM range; A local-only joiner for authenticated extraction and web_search results; A citation-aware answer contract that refuses unsupported claims; An owner-visible privacy ledger for page origins and retained snippets

### "“What am I looking at in Safari right now? Give me the important parts, explain any jargon, and remember only the specific paragraph I point to if I say ‘keep this.’”"
- **useful because:** The owner can ask this hands-free while reading a private page, with no screenshots, copy/paste, or tab hunting. It is the clearest daily bridge between the worn microphone/speaker, the authenticated browser session, and the reasoning relay; the Mac alone cannot safely speak a private page into the owner's ear with this interaction context.
- **path:** pendant → relay-realtime → browser → mac-planner → dashboard
- **model tier:** Realtime handles the short spoken question and concise answer; a cheaper model locally extracts page structure and selected text first, escalating only ambiguous sections to realtime.
- **latency:** 1–3 seconds from button/voice cue to extraction, then 2–6 seconds for a spoken answer; ‘keep this’ must return an immediate confirmation and queue persistence asynchronously.
- **cost:** About $0.005–$0.04 per question, mostly realtime speech and answer tokens; extraction is local and should be near-zero API cost.
- **security:** Only the active tab and explicitly selected DOM region leave the Mac. Do not persist page text unless the owner says ‘keep this’; saved capsules retain origin, timestamp, and exact selection with a visible delete action. Redact passwords, payment fields, and hidden inputs before model access.
- **missing:** A reliable active-tab browser_read_page/snapshot action with selection-range support; A voice intent that binds a pendant utterance to the current browser session; Local sensitive-field redaction before extraction; A user-visible saved-snippet store with origin and retention controls

### "“When a logged-in site asks for a verification code, finish the sign-in for me: tell me which site and account it is for, retrieve the one-time code from the approved private source, enter it, and never save or speak the code.”"
- **useful because:** Authenticated browser automation currently dies at the exact point real services demand human verification. This would make the private browser genuinely dependable for the owner without exposing codes in cloud prompts or requiring phone-to-Mac copying.
- **path:** browser → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Local Mac logic detects the MFA form and extracts the code from an owner-approved local source; realtime only explains the site/account and reports completion. No model should infer codes from broad page text.
- **latency:** 5–20 seconds after the challenge appears; code retrieval and entry should be one bounded browser job.
- **cost:** Under $0.01 per challenge when local; occasional realtime narration is the dominant API cost.
- **security:** Per-origin and per-source allowlists must be explicit and empty until configured. Keep codes in process memory only, mask them in logs, delete immediately after use, and refuse to read codes from unapproved origins. Show the destination and account on the pendant before entry; never send a code to the relay or persist it.
- **missing:** A local MFA challenge detector and one-time in-memory code broker; Browser DOM targeting for OTP fields with post-entry verification; Per-origin approved-code-source configuration; Redacted audit receipts proving only destination and outcome

### "“Look at the private chart or canvas in my active Safari tab, explain the trend and anomalies aloud, and tell me which exact visual region supports each claim.”"
- **useful because:** DOM extraction cannot see canvas charts, maps, scanned statements, or visual CAPTCHA-adjacent instructions. Combining the authenticated browser's screenshot with Mac vision and the pendant gives the owner an eyes-free way to understand private visual information without uploading the whole screen to a cloud service.
- **path:** browser → mac-vision → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Mac vision performs local crop/OCR/chart interpretation; realtime produces a short spoken explanation only after receiving structured measurements and a redacted crop. Use a cheaper background model for multi-chart comparison.
- **latency:** 3–8 seconds for a single crop and under 20 seconds for a multi-panel dashboard.
- **cost:** About $0.02–$0.15 per visual query, dominated by vision tokens if a crop must leave the Mac; local OCR reduces cost substantially.
- **security:** Capture only the active tab and owner-selected rectangle, mask passwords/notifications, and retain neither screenshot nor OCR by default. The dashboard records the crop bounds and claim provenance, not the private image. Never click or mutate based solely on visual interpretation.
- **missing:** A browser_snapshot result that returns a bounded image or crop, not just DOM text; Local redaction of browser screenshots and notification overlays; Structured chart/region provenance linking spoken claims to pixels; A Mac-vision-to-relay handoff for authenticated browser captures

### "“Start this multi-step task in my logged-in browser, remember exactly where you stopped if Safari or my Mac goes away, and let me resume it later from the pendant without repeating completed steps.”"
- **useful because:** Authenticated workflows are fragile today: a tab closes, a session expires, or the Mac sleeps and the owner loses all progress. Checkpointing the browser state and evidence lets a long task survive interruptions and makes the wearable a true continuation device rather than a one-shot remote control.
- **path:** browser → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** A background/local planner decomposes and checkpoints the workflow; realtime is only for spoken status and ambiguity. The checkpoint stores typed step state and receipts, not a replaying model transcript.
- **latency:** Checkpoint after every successful step in under 1 second; resume discovery under 3 seconds, with human-readable status on demand.
- **cost:** About $0.01–$0.10 per multi-step task, mostly planner calls; checkpoint writes are negligible.
- **security:** Bind checkpoints to origin, account fingerprint, and tab/session, encrypt locally, expire them, and discard page text by default. On resume, revalidate the current page and show the next intended action; never blindly replay a stale click or submit a changed form. Keep the owner's maximum-access policy, but expose every step and receipt.
- **missing:** A browser workflow state machine with durable checkpoints and idempotent step identifiers; Session/tab reattachment and recovery after extension or Mac restart; Page-state validation and safe re-planning on resume; Pendant commands for task status, pause, and resume


## What it asked for

_Nothing._
## Its own summary

This round produced three distinct proposals: authenticated morning change triage, evidence-linked private+public research, and hands-free “what am I looking at?” page explanation with explicit keep-this selection. I also verified the real browser path: POST /execute with an actions array works, and Safari is online with 9 tabs (authenticated Gmail and X; X is active). The enqueue wrapper itself only reports what it would call, so direct execution should use /execute.

**Biggest unknown:** The owner still needs to choose the first 3–5 origins and per-origin rules (what may be read, spoken, retained, or never touched). Implementation still needs local sensitive-field redaction, evidence capsules/citations, active-tab selection extraction, and a scheduled watcher; none should be hardcoded to guessed sites.

