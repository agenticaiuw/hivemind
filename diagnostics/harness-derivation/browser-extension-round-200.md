# Harness derivation — browser-extension — round 200

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Read the page I’m looking at and tell me the one thing I need to know.”"
- **useful because:** This is the single most useful browser capability: the pendant supplies hands-free intent, Safari supplies the owner’s authenticated page, and the Mac/relay turns arbitrary page text into a concise spoken answer. It works on private portals that web search cannot reach, while retaining only a short claim and provenance rather than page content.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Realtime for the short spoken answer; use a cheaper background model only if the page is long and needs extraction before the answer.
- **latency:** 3–8 seconds for read plus answer; stream the first sentence as soon as extraction completes.
- **cost:** About one realtime turn plus a small page-extraction call; dominated by model tokens proportional to the extracted page, not the full HTML.
- **security:** Page text from an authenticated origin leaves Safari for relay processing. Default to an empty per-origin policy and existing redaction; do not persist page text, screenshots, or secrets. Store only a <=200-character claim with URL/evidence and the existing 24-hour browser TTL. This is read-only and needs no confirmation.
- **missing:** A production voice-intent route that binds ‘the page I’m looking at’ to the live Safari tab and invokes browser_read_page; A compact answer/extraction pipeline that can cite the evidence capsule without joining unrelated browser facts; An explicit empty per-origin configuration UI for the owner to populate later

### "“Find the deadline on this logged-in page, make a reminder for it, and tell me exactly what you scheduled.”"
- **useful because:** It closes the loop between authenticated browser knowledge and the owner’s real life: Safari reads a private page, the model identifies a date and title, the Mac creates a reversible reminder, and the pendant confirms the result. The owner no longer has to copy dates from portals into a separate app.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a cheaper structured-extraction model for date/title candidates, then realtime only for the owner-facing confirmation. Never use the expensive tier to parse an entire page unnecessarily.
- **latency:** Under 10 seconds when the page is already open; ask a follow-up only if multiple dates or ambiguous timezone remain.
- **cost:** One small extraction call and one Mac action; usually <$0.02 equivalent, with tokens dominated by the relevant page excerpt.
- **security:** Read only the minimum DOM region needed. Show the proposed reminder title, date, timezone, and source URL before creating it; the reminder creation is reversible and should produce an undo receipt. Do not persist page text; retain only the short claim and provenance under existing browser TTL.
- **missing:** A browser semantic-extraction action that returns candidate dates with DOM section/line evidence instead of raw page text; A typed handoff from browser evidence to create_reminder with an undo link; A timezone/ambiguity response spoken through the pendant

### "“Search all my open Safari tabs for the page about my flight, then tell me the gate and departure time.”"
- **useful because:** The owner often has the right authenticated page open but cannot remember which tab. The extension can inspect every tab the browser session exposes, the Mac/relay can rank matching pages, and the pendant can answer without forcing the owner to hunt visually. This is materially different from reading only the active tab.
- **path:** browser-extension → relay-realtime → mac-planner → pendant
- **model tier:** Use deterministic tab metadata and cheap text matching first; invoke realtime only to resolve the top one or two candidate pages and speak the answer.
- **latency:** Under 12 seconds for up to 20 tabs; return ‘I found two candidates’ rather than silently choosing when confidence is low.
- **cost:** One browser list-tabs plus parallel short reads, then a small ranking call; cost scales with candidate tabs and can stay low by truncating each read.
- **security:** Reading all open tabs is broader than reading the active tab. Ship it disabled until the owner adds an explicit per-origin configuration; exclude origins marked never-read, never persist page text, and retain only the selected claim with URL and 24-hour browser TTL. No mutation occurs.
- **missing:** A browser action that lists tabs and returns bounded text snippets per tab in one command; A per-tab/origin read policy and parallel fan-out with strict truncation; A confidence-aware spoken disambiguation flow on the pendant

### "“Save the important part of this private page for my walk, and alert me if it changes before I leave.”"
- **useful because:** Safari can read a private reservation, delivery, or appointment page while the Mac is awake; the relay can schedule a recheck; and the pendant can carry the short, expiring result when the Mac link is gone. This makes authenticated web access useful away from the desk without storing the page itself.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use a background/scheduled cheap model for semantic extraction and change comparison; use realtime only when the pendant alert is actually requested or urgent.
- **latency:** Initial capture under 10 seconds; scheduled rechecks should be invisible, with an alert within one polling interval after a material change.
- **cost:** One extraction now plus low-cost scheduled comparisons; dominant cost is re-reading changed pages, so use hashes and bounded selectors before invoking a model.
- **security:** The owner supplies an explicit origin and category rule; default empty. Never store page text or screenshots. Persist only the short claim, old/new hashes, URL, expiry, and provenance; deliver through the existing offline alert inbox with an expired-state indicator. Never alert on a page that the rule marks never-speak.
- **missing:** A browser watcher that stores bounded selectors/hashes and re-reads an authenticated page on a schedule; Semantic diffing that distinguishes meaningful changes from timestamps/ads; A relay-to-offline-alert payload with expiry and source label

### "“If my private travel page changes or my flight is disrupted, work out what it affects on my Mac, prepare the messages and calendar changes, and tell me the complete proposed plan on my pendant.”"
- **useful because:** Today the browser can read a private page and the Mac can act, but neither can reason across a changing authenticated travel record, the owner’s local calendar, and downstream communications as one incident. This would turn a disruption into an actionable plan instead of a buried alert: identify the affected event, calculate conflicts, prepare exact drafts and reversible calendar edits, and speak the impact while the owner is away from the screen.
- **path:** browser-extension → relay-realtime → mac-planner → mac-terminal → pendant
- **model tier:** Background/scheduled model watches and normalizes the authenticated travel record; a stronger non-realtime planner assembles the cross-app impact graph and drafts changes. Realtime is used only to explain the final plan or answer follow-up questions on the pendant.
- **latency:** Detect and assemble a plan within 2 minutes of a material page change; spoken impact summary under 15 seconds. Drafts and calendar edits remain staged until the owner explicitly asks to apply them.
- **cost:** Low recurring watch cost using selector/hash checks, with a larger model call only on a material change. An incident costs roughly one page extraction, one local calendar/mail scan, and one concise planning call; changed-page frequency dominates.
- **security:** This crosses an authenticated origin with private calendar and communication data, so the owner must explicitly configure origins and categories; ship empty rather than guessing. Keep raw page and mail bodies ephemeral, redact addresses/booking identifiers from logs, persist only the incident claims, affected event IDs, draft hashes, and provenance under short browser TTL. Show every proposed message recipient, calendar mutation, and reason; never send messages or apply changes as a hidden side effect.
- **missing:** A cross-surface incident graph joining browser claims to local calendar/mail entities without copying full documents into relay context; A staged multi-app transaction that can prepare drafts and reversible calendar patches, then apply or discard them as a unit; A scheduled browser watcher with material-change classification and deduplication; An owner-facing pendant summary protocol for multi-item plans and follow-up selection


## What it asked for

_Nothing._
## Its own summary

Round 200 produced three new recorded capabilities: hands-free multi-tab search across authenticated Safari pages, private-page capture with scheduled semantic change alerts delivered to the offline pendant inbox, and page-deadline extraction into a Mac reminder with provenance. I also verified the browser bridge is operational now: POST /execute must use params (not top-level url), navigation created Safari tab 3032326, and browser_read_page returned live text plus an evidence capsule. I informed mac-planner of the exact working action shape.

**Biggest unknown:** The owner’s actual authenticated origins and retention/speech preferences remain intentionally unspecified. I still need the owner to populate the empty per-origin policy (first sites, never-speak categories, never-persist categories). Engineering-wise, the biggest missing pieces are semantic multi-tab fan-out and scheduled authenticated-page watching; neither can be honestly tested until an owner-approved private origin is open in Safari.

