# Harness derivation — browser-extension — round 257

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-state** — Safari extension is online with one active tab, YouTube video 'Max Hodak: Average Is Not Good Enough' at tabId 52; POST /execute browser_list_tabs succeeded and browser_read_page has returned page text in prior logs.
  - evidence: POST /execute action browser_list_tabs at 2026-08-09T03:36:04Z returned tabCount 1, active tabId 52, URL https://www.youtube.com/watch?v=Xc4klGbq8v8&list=LL&index=4.

## Capabilities it proposed

### "While I have several authenticated pages open, compare them and tell me the answer with a short, source-labeled summary on the pendant; keep the claims and URLs so I can ask 'where did that come from?' later."
- **useful because:** The browser is the only node with access to the owner's logged-in pages. This turns scattered private tabs into a trustworthy answer without copying page bodies into memory, and provenance makes the answer auditable.
- **path:** browser → relay → pendant
- **model tier:** Background model for multi-page extraction and comparison; realtime model only for the final spoken answer and follow-up questions.
- **latency:** Up to 20 seconds for reading 2–6 tabs; under 1 second for follow-up from the retained claim set.
- **cost:** Roughly one background extraction call plus a short realtime turn; browser I/O and context length dominate, not page storage.
- **security:** Read-only browser actions by default. Send extracted claims, not HTML or screenshots, to the relay; persist only host-keyed short claims with existing 24-hour browser TTL and provenance. Owner must explicitly name which open tabs to compare.
- **missing:** A browser action to address multiple existing tab IDs in one bounded job; A comparison/extraction job that emits claim-level provenance and feeds the pendant alert/reply path; A spoken 'source N' follow-up resolver over browser provenance

### "Read the authenticated page I am looking at and explain the obligations, deadlines, fees, and cancellation terms in plain language; then let me ask about one highlighted section by voice, without clicking submit or accepting anything."
- **useful because:** This is a high-stakes browser use case where page access matters more than public search. The owner gets an immediate spoken second opinion before agreeing to something, while the browser remains read-only.
- **path:** browser → relay → pendant
- **model tier:** Background model extracts and normalizes clauses; realtime model handles the owner's short spoken follow-ups against the extracted evidence.
- **latency:** Initial answer within 10 seconds; section follow-ups within 2 seconds if the page evidence is already in context.
- **cost:** One page extraction and a few short realtime turns; costs scale with page length, so extract only labeled clauses and cap claim length.
- **security:** Never submit, accept, or navigate away. Treat financial/legal/health text as sensitive: do not persist raw page text; retain only short claims and URL under the existing browser TTL, and require an explicit owner-supplied per-origin speaking policy before audio output for new origins.
- **missing:** A DOM/selection locator from Safari to identify the highlighted section; A clause-focused extractor with numerical/date preservation and uncertainty labels; A pendant query event carrying the current tab and evidence capsule

### "Fill this authenticated form from information I dictate on the pendant, show me every field and the exact final text, and leave it ready for me to submit myself."
- **useful because:** Dictating into a logged-in form is materially faster and more accessible than typing, yet the owner keeps control of the irreversible send. It combines wearable input, browser session reach, and a clear review artifact.
- **path:** pendant → relay → browser → mac-bridge
- **model tier:** Realtime model parses the dictation and confirms ambiguous fields; a cheaper background validator checks formats and cross-field consistency.
- **latency:** Visible field updates within 3 seconds each; complete review within 15 seconds for a typical form.
- **cost:** A few realtime turns plus browser action calls; browser latency and speech transcription dominate.
- **security:** Only fill explicitly named fields; do not infer secrets or invent values. Redact sensitive values from logs and do not persist page text. Before any future submit, present a verbatim diff and require the owner's separate spoken instruction; this proposal intentionally stops before submission.
- **missing:** Field-label/value extraction that preserves form order and sensitive-field markers; A pendant dictation mode with undo for the last field; A review renderer that can read a concise diff and expose each field on request

### "If I say 'lock down now' on the pendant, close my authenticated Safari tabs, revoke the browser extension session, and tell me what was successfully shut down; if the Mac is offline, queue the revocation until it returns."
- **useful because:** A wearable is the one control surface still available when the owner cannot reach the Mac. One voice command can contain a lost-device or shoulder-surfing incident instead of relying on finding and operating each logged-in site manually.
- **path:** pendant → relay → browser → mac-bridge
- **model tier:** Realtime model recognizes the fixed emergency command and reports results; no expensive planning model should be involved. Background retry handles an offline Mac.
- **latency:** Begin shutdown within 2 seconds and report each result within 10 seconds; retry queued work when the bridge reconnects.
- **cost:** One short realtime turn and several cheap browser/session commands; negligible token cost compared with the value during an incident.
- **security:** This is intentionally high-impact and must require an unmistakable dedicated long-press plus spoken phrase, not ordinary conversational inference. Keep no page contents; retain only action receipts and timestamps. The owner should choose whether 'revoke extension session' also logs out site sessions, since site logout semantics vary.
- **missing:** A pendant emergency command path that works offline and queues a signed intent; A browser/session operation to close all tabs and invalidate the extension session; An idempotent relay job with per-origin completion receipts and retry after Mac reconnect

### "When I say “witness this page,” capture a tamper-evident timestamped attestation of the authenticated page I am viewing—including URL, title, visible claims, and content hash—then let me ask the pendant what exactly was witnessed later without retaining the full page."
- **useful because:** The owner could preserve evidence of what a logged-in service actually showed at a particular moment for a dispute, reimbursement, or support case. This is different from saving a note or ordinary browser provenance: it creates a verifiable snapshot claim without hoarding page contents.
- **path:** browser → relay → pendant → mac-bridge
- **model tier:** Cheap background canonicalizer creates the claim manifest and hash; realtime is only used if the owner asks a spoken question about the attestation.
- **latency:** Under 5 seconds to create the witness receipt; under 2 seconds for later claim lookup.
- **cost:** One bounded page extraction and hash operation; low model cost because the full page is not retained or repeatedly sent.
- **security:** A hash is not proof that every visible pixel was captured, so label the attestation honestly as DOM-visible evidence. Never store HTML, screenshots, credentials, or raw page text; encrypt the manifest and require explicit owner invocation. Redact secrets before persistence.
- **missing:** A browser witness action that returns a stable DOM-visible manifest and content hash; Signed relay-side attestation receipts with a trustworthy clock and exportable verification format; A pendant command to enumerate and explain prior witness receipts

### "For this logged-in checkout or subscription page, tell me the cheapest and most expensive possible outcome under the page’s own terms, without changing the page, and let me compare scenarios by voice before I decide."
- **useful because:** The owner gets decision support from private pricing and contract context that public search cannot access. It turns a confusing dynamic page into an explicit range of commitments without clicking purchase, accept, or submit.
- **path:** browser → relay → pendant → mac-bridge
- **model tier:** Background model extracts prices, dates, and conditional clauses; realtime model handles scenario questions and speaks a concise result.
- **latency:** Initial range within 12 seconds; follow-up scenario answers within 3 seconds while the evidence capsule is warm.
- **cost:** One extraction call plus short follow-ups; costs scale with the number of conditional clauses, not with repeated full-page context.
- **security:** Read-only browser allowlist; never use inferred defaults where the page is ambiguous. Mark estimates versus explicit charges, preserve currency and recurrence, and retain only short claims under existing browser TTL. Do not treat the result as financial advice.
- **missing:** A structured extractor for recurring, conditional, and cancellation charges; A scenario evaluator that cites the exact page claims used in each calculation; A voice-friendly uncertainty and currency presentation on the pendant

### "When an authenticated page shows a code, address, tracking number, or reference number, let me ask the pendant to read back only that specific value and copy it to the app I name, with a final spoken readback before anything is sent."
- **useful because:** Long private identifiers are where browser access and a wearable are most useful: the owner should not have to transcribe them from a screen. Scope-limited extraction reduces exposure compared with reading the whole page aloud.
- **path:** browser → pendant → relay → mac-bridge
- **model tier:** Background DOM extractor identifies candidate labeled values; realtime model confirms the requested label and reads back the short value.
- **latency:** Under 4 seconds to locate and speak a value; under 2 seconds to copy it after confirmation.
- **cost:** A small extraction plus one realtime confirmation; low token use because only the selected value crosses the model boundary.
- **security:** Treat codes and identifiers as secrets by default: never persist them, never include them in ordinary logs, and require an explicit target app and readback before copying. The system must not guess between multiple candidate values.
- **missing:** Label-aware value extraction with secret classification; A secure ephemeral clipboard handoff to a named Mac/iOS app; A pendant confirmation primitive that distinguishes read-only speak from copy


## What it asked for

_Nothing._
