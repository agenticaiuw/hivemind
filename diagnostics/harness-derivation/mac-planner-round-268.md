# Harness derivation — mac-planner — round 268

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What are the four newest things on my Safari Reading List? Give me the useful one-sentence takeaway for each, and leave an audio version I can play on the pendant."
- **useful because:** This is a repeated owner request that currently fails. It turns a browser-only list into a short, wearable briefing without requiring the owner to stop and read Safari.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheap background model for extraction and one-sentence summaries; use realtime only if the owner asks a follow-up by voice. The relay fetches the list, the Mac bridge/AppleScript reads Safari's Reading List, and the pendant receives the resulting audio.
- **latency:** Under 20 seconds for four items; audio may be generated asynchronously and surfaced as a queued alert.
- **cost:** Roughly $0.01-$0.05 per run depending on article text length; browser extraction and TTS dominate, not the short summary.
- **security:** Reading List URLs and extracted page text leave the Mac for summarization. Redact page bodies by default, keep URLs and summaries in a short-lived job receipt, and never follow authenticated links without the owner's existing browser-session policy.
- **missing:** A bounded Safari Reading List read route in the browser/Mac harness (not just active-tab inspection); A background routine that fetches, summarizes, deduplicates, and hands audio to the existing pendant inbox

### "Take me back to the work I was doing yesterday: reopen the relevant browser tabs, files, and editor workspace, then tell me in one sentence what I was trying to finish."
- **useful because:** The owner loses continuity across Mac sessions and cannot currently ask the pendant to reconstruct a work context. This makes the hive feel like one assistant rather than separate browser, Mac, and voice surfaces.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** A cheap background model builds a compact continuation capsule from recent work signals; realtime only handles the spoken request. The Mac planner executes an explicit open/reopen plan after inspecting current state.
- **latency:** Inspect and produce a plan in 5 seconds; reopen the workspace in another 5-10 seconds; speak the one-sentence orientation immediately, with failures reported per resource.
- **cost:** About $0.01-$0.04 per invocation. The dominant cost is summarizing recent signals, not action execution.
- **security:** Recent filenames, URLs, and editor context are sensitive. Keep the capsule local or encrypted, exclude passwords and page bodies, and do not send mail, delete files, or mutate documents. Opening an authenticated browser tab is allowed only under the owner's browser policy.
- **missing:** A read-only semantic work-context collector for recent Safari tabs, VS Code workspace, Finder files, and the last relevant calendar item; A durable continuation-capsule route that can be requested by voice and resolved into idempotent Mac open actions

### "Is this page or message safe to trust? Use the page I'm looking at, explain the risky claims or suspicious requests in plain language, and tell me what not to click."
- **useful because:** A wearable voice question can turn the browser's authenticated, private context into an immediate safety check without making the owner copy text or accidentally act. It is especially valuable for phishing, payment requests, and urgent-looking work messages.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime handles the short spoken exchange; a cheaper analysis model examines a redacted DOM excerpt, URL, sender metadata, and visible call-to-action. No autonomous click or submission is performed.
- **latency:** Return a spoken risk summary in 3-6 seconds, with a longer analysis available asynchronously if the page is large.
- **cost:** About $0.005-$0.03 per check; DOM extraction and model context length dominate.
- **security:** The browser session is sensitive and may contain private mail or financial pages. Send only the visible/selected region and origin metadata, redact tokens, passwords, and hidden fields, and retain no page snapshot by default. The system must explicitly distinguish suspicious from verified and never claim certainty from URL heuristics alone.
- **missing:** A browser command for bounded visible-region/selection capture with origin and sender metadata; A relay safety-analysis route with evidence citations and a strict no-action output contract; A pendant response mode that speaks the warning while preserving the page unchanged

### "Turn the article I am looking at into a clean Markdown note in my AI-Pendant-Workspace, preserving the source link, a short summary, and three quoted passages, then tell me on the pendant when it is ready."
- **useful because:** The owner can currently read a page or create a file, but cannot fluidly move useful knowledge from an authenticated browser session into their durable editor workspace by speaking to the pendant. This removes the copy-paste boundary while preserving provenance.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Use a background model for extraction, quote selection, and Markdown formatting; realtime only handles the spoken request and completion notice.
- **latency:** Produce a draft in 10-20 seconds for an ordinary article, with a clear failure if the page is inaccessible or too long.
- **cost:** Approximately $0.01-$0.08 per article, dominated by page-text extraction and summarization; file creation and audio are negligible.
- **security:** Authenticated page contents leave the browser only after the owner requests the transformation. Redact credentials and hidden fields, retain the source URL, write only beneath ~/AI-Pendant-Workspace, use a collision-safe filename, and require confirmation before overwriting an existing note.
- **missing:** A browser extraction operation that returns article text and canonical URL rather than only active-tab inspection; A bounded article-to-Markdown transformation with quote provenance and prompt-injection-resistant parsing; A workspace write handoff that detects filename collisions and returns a durable receipt to the pendant

### "Compare this article with my existing notes on the same topic, point out contradictions or outdated claims with links to both sources, and save the result beside the notes."
- **useful because:** The owner gets a useful second opinion at the exact moment they encounter new information. It combines the private browser context with local knowledge instead of producing another disconnected web summary.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** A background model performs retrieval, claim extraction, and contradiction analysis; realtime only accepts the request and speaks a compact verdict.
- **latency:** Return a three-line verdict within 20 seconds and write the detailed comparison asynchronously within one minute.
- **cost:** About $0.03-$0.20 per comparison depending on the number and length of local notes; retrieval and model context dominate.
- **security:** Local notes and authenticated page contents are sensitive. Keep retrieval scoped to an explicit workspace folder, redact secrets, preserve exact citations, and write a new file rather than silently modifying source notes. The analysis must label uncertainty and distinguish contradiction from mere difference in scope.
- **missing:** A scoped local-note retrieval and claim-indexing service; A browser article extraction route with stable source anchors; A comparison pipeline that emits claim-level evidence and a collision-safe local artifact

### "What commitments did I make today across my email, calendar, and notes? List only promises with a person and due date, create reminders for the ones that have clear deadlines, and read me the shortest useful summary on the pendant."
- **useful because:** Important promises are currently scattered across communication and notes. This turns them into an owner-controlled action list rather than another generic daily briefing, while avoiding autonomous message sending.
- **path:** pendant → relay-realtime → mac-planner → mac-vision
- **model tier:** Use a background model for commitment extraction and confidence scoring; realtime speaks the concise result. Reminder creation is deterministic and only happens for high-confidence commitments with an explicit deadline.
- **latency:** Return the spoken summary in 15 seconds; create reminders in the same job and provide a receipt listing every created reminder.
- **cost:** Approximately $0.02-$0.10 per run, dominated by mail/note context and extraction; reminder creation and audio are negligible.
- **security:** Mail and notes can contain sensitive relationship and work data. Restrict reads to the owner's configured account and workspace, redact unrelated bodies, show evidence snippets for each inferred promise, avoid inventing deadlines, and never send or reply to anyone. Reminder creation must remain reversible and auditable.
- **missing:** A commitment-extraction route that joins bounded Mail, Calendar, and Notes reads with evidence spans; A confidence-and-deadline resolver that refuses ambiguous promises instead of guessing; A reminder batch operation with per-item receipts and spoken completion feedback


## What it asked for

_Nothing._
