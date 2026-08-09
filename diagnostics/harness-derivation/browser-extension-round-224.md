# Harness derivation — browser-extension — round 224

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What am I looking at, and what should I do next?”"
- **useful because:** This would turn the authenticated Safari session into the owner's fastest way to understand a confusing page: the extension supplies the live DOM and selection context, the relay answers in one short spoken sentence, and follow-up questions stay anchored to that exact page element without storing page text. It is the strongest browser-only capability because no public-web tool can see the owner's logged-in screen.
- **path:** browser → relay-realtime → pendant → mac-planner
- **model tier:** Realtime for the first answer and follow-ups; a cheaper background model only if the owner asks for a long page digest.
- **latency:** 2–4 seconds for a focused selection; up to 8 seconds for a full page. The extension should return a compact DOM/selection capsule rather than a screenshot by default.
- **cost:** Roughly $0.01–$0.05 per focused question, dominated by realtime model input tokens; much less than sending the whole page or an image.
- **security:** Authenticated content leaves Safari for relay processing, so the UI must visibly show the active origin and provide a one-tap stop. Do not persist page text or screenshots; persist only an optional short claim under the existing browser-fact TTL/provenance rules. The owner already allows browser reading without asking, but the empty per-origin configuration must remain inspectable.
- **missing:** A reliable browser_read_page/snapshot enqueue resolution (the current wrappers are ambiguous despite Safari being online); An extension command that captures the current selection plus a stable DOM element identifier; A short-lived conversation context keyed to tabId/origin and invalidated on navigation

### "“Save this browser task so it can finish itself when my Mac wakes up, and tell me exactly where it stopped.”"
- **useful because:** Long authenticated workflows currently die when Safari closes, the Mac sleeps, or a page navigates. This would create a resumable handoff: Safari records only the origin, tab identity, task goal, completed reversible steps, and an undo/verification receipt; the relay holds the queue while asleep; mac-planner resumes when the bridge returns; the pendant reports 'waiting', 'resumed', or 'needs you' in one sentence.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** Background/cheap model for checkpoint normalization and restart planning; realtime only for the owner's spoken status query or an ambiguity that needs clarification.
- **latency:** Checkpoint under 1 second after each reversible action; resume within 10 seconds of Mac wake. Never replay an action without re-reading the page and matching the expected origin/state.
- **cost:** About $0.002–$0.02 per checkpoint/resume, mostly small planner calls; browser I/O and Mac wake dominate latency, not tokens.
- **security:** Never persist credentials, cookies, page bodies, or screenshots. Bind checkpoints to origin, tab/session, and a short expiry; invalidate on material DOM mismatch. Filling may resume, but sending, purchasing, deleting, or submitting must stop with a preview, consistent with owner policy.
- **missing:** A durable browser-task checkpoint schema and resume worker; A browser-side DOM/state fingerprint plus post-action verification receipt; A Mac wake/reconnect event that drains pending browser checkpoints; A pendant status event that can distinguish waiting, resumed, and blocked

### "“Before I send this, check that the form says what I think it says.”"
- **useful because:** For an authenticated form, the browser extension can extract labels and current values while mac-vision independently inspects the rendered page. The relay compares the two views, calls out mismatched recipients, amounts, dates, attachments, or hidden truncation, and the pendant speaks only the discrepancies. It prevents the most expensive browser mistake without blocking ordinary browsing, and stops before submission.
- **path:** browser → mac-vision → relay-realtime → pendant → mac-planner
- **model tier:** Realtime multimodal comparison only at the owner's explicit pre-submit request; deterministic field normalization and checksum comparison should happen locally/cheaply first.
- **latency:** 3–6 seconds for a normal form, under 10 seconds for a complex page. No action is submitted by this capability.
- **cost:** Approximately $0.02–$0.10 per audit, dominated by multimodal input if a screenshot is needed; most simple forms should use extracted fields only.
- **security:** This handles highly sensitive authenticated data. Send only the selected form's fields and a tightly cropped screenshot when needed; redact passwords and tokens before relay; retain only an audit receipt containing field names, hashes, origin, and timestamp, not values. Make the origin and exact action target audible before any later submit action.
- **missing:** A browser action that returns a structured form-field map with labels, values, and submit target; A mac-vision capture API that can crop to the active form and return visual text/geometry; A deterministic field canonicalizer and discrepancy report shared by browser and vision tiers; A user-facing handoff from audit receipt to a later explicit submit command

### "“Find me the best appointment slot that works with my calendar, fill everything in, and stop before the final confirmation.”"
- **useful because:** The owner currently has to shuttle between an authenticated booking site and Calendar manually. Safari can reach the private scheduling portal, while the Mac can read calendar conflicts and the pendant can resolve only the genuinely ambiguous choices. The system should propose a ranked slot, populate the reversible fields, read back the exact appointment details, and leave the final confirmation untouched.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** Cheap/background planning for slot enumeration and conflict filtering; realtime only when the site presents ambiguous choices or the owner needs a spoken decision.
- **latency:** 15–45 seconds for one booking site, with incremental spoken progress if the portal is slow.
- **cost:** $0.03–$0.15 per booking search, dominated by browser steps and calendar extraction; most ranking can be deterministic.
- **security:** Appointment details and calendar data are sensitive. Keep page text transient, retain only the selected slot and provenance if the owner asks. Bind every fill to the expected origin and re-read it after navigation. Never click the final booking/confirm control without an explicit owner command.
- **missing:** A browser workflow primitive that can enumerate candidate slots and expose the final confirmation target; A calendar conflict adapter available to the browser planner; A structured spoken disambiguation event from Safari to the pendant; A durable preview containing the exact appointment, timezone, provider, and cancellation terms

### "“Use the thing I’m looking at to find the related notes, calendar events, and files on my Mac, then tell me what matters.”"
- **useful because:** A browser page and the owner's local records currently live in separate worlds. This would let the owner select an invoice, person, project, or product in Safari; the relay would resolve that entity against local Notes, Calendar, and files; and the pendant would speak a short, provenance-backed answer. It is useful precisely because it combines the browser's private login with Mac-local context that neither surface can independently correlate.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** A cheap local/entity-normalization pass first, followed by realtime only to synthesize the small set of matched records into the owner's one-sentence answer.
- **latency:** 5–12 seconds for a focused selection; return partial matches if a local index is large.
- **cost:** $0.01–$0.06 per lookup; indexing and local search should dominate, with only compact matched snippets sent to the realtime model.
- **security:** The page selection may contain private identifiers. Send only the selected text and origin, not the whole page; search local records on the Mac; return claims with source labels and short TTLs. Never silently persist a new association between a web identity and a local person or project.
- **missing:** A browser selection-to-entity event carrying origin, selected text, and a stable page reference; A Mac-local semantic search/index over Notes, Calendar, and files exposed to the planner; A provenance-preserving join format that distinguishes page evidence from owner-authored records; A pendant response format that names which sources matched without speaking sensitive raw text

### "“Find duplicate subscriptions and accounts I’m paying for, explain the evidence, and prepare the cleanup without changing anything yet.”"
- **useful because:** The owner cannot get a trustworthy answer by searching public web or looking at one logged-in site. Safari sessions can inspect the private account pages, while the Mac can correlate local receipts, mail, and files; the relay can cluster merchants and renewal dates; the pendant can give a compact list of duplicates and next actions. It should prepare navigable cleanup steps and drafts, but never cancel or delete on its own.
- **path:** browser → mac-planner → relay-realtime → pendant
- **model tier:** Background model for clustering and evidence normalization; realtime only for the owner’s query and for explaining one disputed match.
- **latency:** Minutes rather than seconds for a batch across several sites; provide an initial result as each origin completes and a final consolidated report later.
- **cost:** $0.10–$0.60 per batch, dominated by authenticated browser navigation and document extraction; clustering itself is cheap once normalized records exist.
- **security:** This exposes financial and account data. Keep raw pages and receipts transient, store only merchant, amount, renewal date, masked account label, source URL, and evidence hashes with short browser TTLs. Require explicit confirmation before cancellation, deletion, or contacting a vendor; preserve an undoable action receipt for any draft or navigation.
- **missing:** A user-configurable set of origins supplied by the owner at runtime, initially empty; A cross-origin extraction schema for merchant, plan, amount, renewal, cancellation path, and account label; A local mail/file connector that returns receipt metadata without uploading full documents; A batch browser orchestrator with per-origin failure isolation and an evidence-backed deduplication report


## What it asked for

_Nothing._
