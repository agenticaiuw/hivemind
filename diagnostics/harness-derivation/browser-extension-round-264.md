# Harness derivation — browser-extension — round 264

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser live state** — Safari extension is online with one tab, currently a YouTube page titled “Max Hodak: Average Is Not Good Enough” on Y Combinator; browser_read_page through POST /execute returned page text successfully.
  - evidence: POST /execute with {actions:[{type:'browser_read_page'}]} returned 200 and page content including title, channel, description, and related videos.

## Capabilities it proposed

### "“Read the form I’m looking at, tell me exactly what it will submit, and fill only the fields I dictate—stop with a reviewable draft before submission.”"
- **useful because:** Authenticated browser forms are where the extension is uniquely valuable and where accidental mistakes are expensive. The owner can dictate a few fields from the pendant, have Safari fill them, hear a compact field-by-field diff including hidden defaults and attachments, and retain control of the irreversible submit.
- **path:** pendant → relay → browser → mac-bridge
- **model tier:** Realtime for the short dictate/review conversation; deterministic browser extraction and field mapping on the Mac, with a cheap model for label/value matching.
- **latency:** Read current form in 2–5 seconds; fill in under 5 seconds; spoken review under 10 seconds. Never wait on a background job for the review state.
- **cost:** Low to moderate per invocation: one page extraction, one structured field-mapping pass, and a short spoken summary. Browser interaction and model parsing dominate.
- **security:** Treat every field, checkbox, file, recipient, amount, and hidden value as visible in the review. Redact secrets from relay speech according to the owner's per-origin/category settings. Fill is reversible; submission is not and must remain a separate explicit action. Do not persist page text or credentials.
- **missing:** Structured form/field extraction from browser_snapshot or browser_read_page; A draft object with before/after values and attachment metadata; Pendant dictation-to-field targeting and spoken review rendering; An explicit submit handoff that displays the final payload before browser_click

### "“Compare these two logged-in pages and give me a cited decision matrix—don't change either page.”"
- **useful because:** The browser extension can reach two sessions that the relay and ordinary web search cannot. Comparing an authenticated renewal quote against the current policy, two travel itineraries, or two private dashboards is a high-value task that requires simultaneous tab access, normalization, and provenance rather than a generic page summary.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Cheap extraction/normalization model first; use realtime only to answer the owner's spoken questions about the resulting matrix.
- **latency:** Capture two tabs in 5–10 seconds, normalize in under 15 seconds, then speak a 30–60 second answer with an option to drill into a row.
- **cost:** Moderate: two authenticated page reads and one structured comparison. The dominant cost is context size; send extracted fields and citations, never whole pages.
- **security:** The owner explicitly names the tabs or origins for each comparison. Show source URL, capture time, and the exact supporting claim for every cell. Apply existing host-keyed 24-hour/200-character browser fact limits and don't retain raw page content. No clicks, typing, or submissions are permitted in comparison mode.
- **missing:** A multi-tab capture action that returns stable tab IDs and page metadata; Schema-guided extraction of requested comparison fields; A citation-preserving comparison artifact and spoken renderer; A way to pass the artifact to the relay and later trace each claim

### "“Check my private service dashboard against what my Mac is seeing, and tell me whether I need to act.”"
- **useful because:** Only the browser node can read the owner's authenticated status dashboard, while only the Mac node can inspect local processes, network, and logs. Joining those views can distinguish a provider outage from a local failure and give the pendant one actionable answer instead of two unrelated summaries.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Cheap structured correlation/classification for dashboard claims and local observations; realtime only for the owner's follow-up conversation.
- **latency:** Collect both sides in 10–20 seconds and speak a concise verdict within 30 seconds. If either source is unavailable, say which side is missing rather than guessing.
- **cost:** Moderate: one authenticated page extraction plus a small local health snapshot. Keep model context to normalized indicators and citations, not logs or page bodies.
- **security:** The owner supplies the dashboard origin and the local checks to run; default configuration is empty. Never send raw private dashboard content or unrestricted logs to the relay. Persist only the final short-lived diagnosis with both source references. This mode is read-only and cannot restart services, change settings, or acknowledge incidents.
- **missing:** A browser-to-Mac correlation job that acquires both observations under one request ID; A normalized health-indicator schema and confidence/unknown handling; A local read-only diagnostic bundle exposed by the Mac bridge; A two-source citation and provenance record usable in spoken output

### "“If you change anything in a logged-in website, make a private checkpoint first so I can say ‘undo that’ from the pendant—even if Safari is no longer in front.”"
- **useful because:** This would make browser automation trustworthy enough for consequential everyday work. The owner gets a durable, human-readable before/after record and a spoken undo path for edits such as preferences, saved filters, addresses, or calendar settings, rather than relying on a vague browser history or hoping the site has its own undo.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Deterministic DOM/state capture and inverse-action generation on the Mac; realtime only to interpret the owner's undo request and read back the result.
- **latency:** Checkpoint before mutation in under 2 seconds; undo dispatch in under 5 seconds when the same session is alive. If the session has changed, report an exact recovery plan instead of guessing.
- **cost:** Moderate storage and parsing cost per mutation; model cost is small if the checkpoint is structured. The expensive part is site-specific inverse-action synthesis and verification.
- **security:** Encrypt checkpoints locally and bind them to origin, session, tab, and a content hash. Do not store passwords, page bodies, or screenshots; retain only affected field/DOM identities and redacted before/after values under the existing browser retention policy. Never silently apply an inverse if the page no longer matches; surface the proposed inverse and its evidence.
- **missing:** Browser mutation interception that captures a structured pre-state; A site-independent inverse-action planner with post-undo verification; Encrypted durable browser checkpoint storage and expiry; Pendant command routing for selecting and confirming a specific undo receipt

### "“Before I close this online account, inventory what I would lose, download the records I’m entitled to keep, and leave the closure page untouched.”"
- **useful because:** Account closure is an irreversible life-admin task that current web search cannot perform because the important details are behind the owner's login. This capability would turn a risky, scattered process into an evidence-backed inventory: subscriptions, files, credits, connected services, retention terms, and an encrypted local export, without crossing the final closure step.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Background extraction and document classification on the Mac; realtime for the owner's questions about one item or a missing export.
- **latency:** Inventory in 1–3 minutes depending on account pages and downloads; speak a short loss summary first, then continue exports as a background job with progress alerts.
- **cost:** Moderate to high: multiple authenticated page reads and potentially large local downloads. Model cost is dominated by classifying export metadata, not by transferring page text to the relay.
- **security:** The owner must name the origin and explicitly start a closure-preparation job. Downloads stay encrypted on the Mac; never upload exports or read their contents aloud by default. Do not click closure, cancellation, delete, or consent controls. Keep only short provenance claims and a local manifest with expiry and a user-visible delete action.
- **missing:** A browser workflow that discovers account-data/export surfaces without submitting destructive controls; Encrypted download quarantine and manifesting on the Mac; A closure-impact taxonomy and duplicate detection across downloaded records; A pendant-friendly progress, exception, and final-review summary

### "“Collect the receipts from this logged-in store, match them to the files on my Mac, and give me a deduplicated expense bundle—don't send or submit anything.”"
- **useful because:** The browser can reach purchase history and invoices that no public search can see, while the Mac can inspect local downloads and produce a usable bundle. This eliminates a tedious, error-prone reconciliation task and leaves the owner with cited records rather than a model-generated total.
- **path:** browser → mac-bridge → relay → pendant
- **model tier:** Cheap extraction, hashing, and reconciliation on the Mac; realtime only for ambiguity resolution such as two receipts with the same amount.
- **latency:** Start speaking a count and obvious duplicates within 15 seconds; finish a month or year in a background job with pendant progress and a final manifest.
- **cost:** Moderate: authenticated page traversal plus local file hashing/OCR where necessary. Keep model context to normalized receipt fields and conflicts.
- **security:** The owner specifies the store and date range. Files remain local and encrypted; the relay receives only totals, conflicts, and provenance unless the owner asks for a specific receipt. Never purchase, refund, email, upload, or alter account data. Every extracted amount retains source URL or local path and capture time.
- **missing:** A browser pagination/export crawler that handles receipt history without destructive clicks; Local encrypted receipt vault with content hashes and duplicate matching; A schema for line items, tax, currency, refund, and provenance confidence; A background job and pendant progress/exception protocol


## What it asked for

_Nothing._
## Its own summary

Safari is no longer empty: it is online with one authenticated-capable tab, and POST /execute browser_read_page works; I read the current YouTube page successfully. I recorded three distinct proposals: (1) authenticated form read/fill with a spoken, cited pre-submit draft; (2) a two-tab private-page comparison matrix with provenance; and (3) cross-surface private-dashboard versus Mac-health incident triage. The page-watch idea was rejected as an existing capability and was not restated. The three recorded ideas deliberately use the pendant for concise decisions, Safari for private sessions, the Mac for local reach, and the relay for coordination.

**Biggest unknown:** The owner still needs to supply the actual first origins and category rules (what may be read, spoken, redacted, or retained), plus—if incident triage is wanted—the local checks and dashboard fields to compare. The browser convenience wrappers remain ambiguous, but the underlying POST /execute route is live and read-only page extraction is working today.

