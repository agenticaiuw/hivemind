# Harness derivation — browser-extension — round 135

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser** — Safari is online with 3 tabs; the authenticated Gmail inbox is open and readable. Inbox shows 2 new Primary messages and multiple recent GitHub Actions failures for evan1liu/buckymatch, including Data Age Monitor and Frontend Production failures.
  - evidence: POST /execute browser_list_tabs and browser_read_page at 2026-08-07T18:22:54Z; tab 901464 https://mail.google.com/mail/u/0/#inbox

## Capabilities it proposed

### "Read aloud the part of the private webpage I am currently focused on, and let me say 'next', 'back', or 'summarize this' while I browse; keep the browser page and pendant synchronized without submitting or sending anything."
- **useful because:** Makes authenticated Safari pages usable while walking, cooking, or looking away from the screen. It is not a generic page summary: the extension contributes the owner's current selection/focus, while the pendant supplies low-friction navigation and speech.
- **path:** browser-extension → relay-realtime → pendant → mac-planner
- **model tier:** realtime for short focus-to-speech turns; background model for optional section summaries
- **latency:** Focused text readback begins within 1 second; next/back navigation within 500 ms where the extension is online.
- **cost:** <$0.01 per short focus readback; audio generation and repeated long-page summarization dominate.
- **security:** Only the focused DOM text and origin should be sent, not the entire page. Never echo password fields, payment fields, hidden inputs, or clipboard contents. Navigation is reversible; form submission remains outside this capability.
- **missing:** Extension events for DOM focus, text selection, and semantic next/previous regions; A low-latency pendant audio queue with interruption support; A browser command that targets the focused element/region rather than a CSS selector

### "Save the private report I am viewing as a verified local brief: download it in Safari, have my Mac check the file type and extract its key tables, then leave a cited text and short audio version in my workspace for the pendant."
- **useful because:** Bridges the only place private documents are accessible (logged-in Safari) with the only place that can safely inspect and persist files (the Mac), producing something the owner can consume later without reopening the account.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** background model for table extraction and citation; realtime only when the owner asks to hear the finished brief
- **latency:** A normal report should become a local brief within 2 minutes; audio should be ready within 30 seconds afterward.
- **cost:** $0.01–$0.05 per report, dominated by OCR/table extraction and audio synthesis for long documents; local parsing should be free.
- **security:** Keep the downloaded source and extracted text on the Mac by default; send only bounded excerpts or hashes for model work. Detect and exclude credentials/PII. Do not upload the report or share it, and ask before opening external links from it.
- **missing:** A browser download-to-local-agent action with completion receipt; A local document/table extraction pipeline with source offsets; A workspace-to-pendant audio queue and citation manifest

### "Keep my authenticated browser task alive while I am away: detect when the private tab is about to expire or has been logged out, reopen the same page on Safari, and tell me on the pendant exactly what I need to do; never type or expose my password."
- **useful because:** Long-running private work currently dies silently when a session expires. The browser can detect the auth boundary, the Mac can restore the tab and preserve a task snapshot, and the pendant can alert the owner without leaking credentials or requiring them to watch Safari.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** background watcher for session signals and tab restoration; realtime only for the brief spoken alert
- **latency:** Detect within one polling interval (under 30 seconds); restore the prior non-sensitive URL within 5 seconds; alert immediately when human login is required.
- **cost:** <$0.01 per day for a few watched tabs; model calls only when the page state is ambiguous, with browser polling and URL restoration dominating reliability rather than cost.
- **security:** Never inspect or transmit password fields, cookies, tokens, or autofill values. Do not bypass MFA or CAPTCHA. Store only origin, URL path, task label, and a redacted snapshot. Restoring a page is reversible; any login or submission remains manual.
- **missing:** An auth-boundary detector that distinguishes session expiry from ordinary page errors; A redacted task checkpoint tied to a tab and window, with safe URL restoration; A pendant alert path for browser events that are not responses to a current voice turn

### "Reconcile a charge across my logged-in Gmail, merchant account, and local files: show me which receipt, order, and downloaded document refer to the same transaction, flag discrepancies, and leave a cited discrepancy report without contacting anyone."
- **useful because:** Owners routinely have the evidence split across private browser sessions and local downloads. No single node can correlate those sources while preserving citations and avoiding accidental financial action.
- **path:** browser-extension → mac-planner → mac-terminal → relay-realtime → pendant
- **model tier:** background model for document/entity matching; realtime only to answer a follow-up or read the conclusion
- **latency:** Under 3 minutes for three sources; under 10 seconds for a spoken result once evidence is collected.
- **cost:** About $0.02–$0.08 per reconciliation, dominated by OCR and long-email/document extraction; browser and local reads are otherwise cheap.
- **security:** Keep raw financial pages and files on the Mac where possible; send only bounded excerpts and hashes for matching. Mask account numbers and payment tokens. Never dispute, refund, purchase, or send a message automatically.
- **missing:** Cross-origin transaction entity matching with confidence and citations; A local document index that can associate downloaded files with browser records; A redacted, owner-readable discrepancy report format shared with the pendant

### "Give me a pendant panic command that immediately hides and freezes my private Safari work: blur or close selected sensitive tabs, cancel queued browser actions, and erase the temporary page snapshots, then tell me exactly what was stopped."
- **useful because:** A wearable is present when the owner notices someone looking over their shoulder or loses the Mac. Today browser actions and captured private context can outlive the moment the owner wants privacy. A physical, low-latency kill switch is meaningfully different from ordinary browser automation.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** No model for the emergency path; deterministic firmware/relay/extension actions. Use a cheap background receipt summarizer afterward if desired.
- **latency:** Local button acknowledgement under 250 ms; Safari tab hiding/cancellation under 2 seconds while online; queued cleanup receipt within 10 seconds.
- **cost:** Negligible per invocation; relay storage cleanup and a small receipt generation are the only ongoing costs.
- **security:** This must be fail-closed and deterministic, with no model interpretation. Persist only a minimal audit receipt. Define whether close means close, navigate to a blank page, or hide the window; never claim remote cleanup succeeded if the Mac is offline.
- **missing:** A dedicated pendant emergency button/gesture mapping; An authenticated cancel-and-redact browser command that supersedes queued work; Extension support for immediate tab hide/close and acknowledgement

### "While I am reading a private dashboard, build a time-stamped evidence pack of the exact values and screenshots behind my spoken question, then let me hand that pack to my Mac for a local calculation or chart without uploading the whole page."
- **useful because:** The owner can currently read a private page or run Mac work, but cannot reliably preserve the exact evidence behind a conversational claim and pass only the necessary fields onward. This enables auditable decisions from authenticated dashboards while keeping the source private.
- **path:** browser-extension → relay-realtime → mac-planner → mac-terminal → pendant
- **model tier:** Realtime for selecting fields from the current question; background model for normalization and chart generation.
- **latency:** Evidence capture within 3 seconds; local calculation or chart within 30 seconds; pendant can read back the result immediately.
- **cost:** Roughly $0.01–$0.05 per pack, mostly screenshot/vision extraction and chart narration; local calculations are effectively free.
- **security:** Bind each field to URL, tab, timestamp, and DOM/screenshot region. Send selected fields rather than full HTML. Redact secrets and reject hidden inputs. Store packs with explicit expiry and never publish them.
- **missing:** A claim-scoped browser evidence-pack format with field-level provenance; A handoff route from browser result to local Mac computation; A compact pendant-readable citation and expiry representation


## What it asked for

_Nothing._
