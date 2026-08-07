# Harness derivation — browser-extension — round 86

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension** — Safari extension is currently offline; only home-chrome is registered and offline, with 7 pending browser commands. Browser sessions persist stale tabs (default time.is/UTC and two probe forms), but no live inspection records exist. Mac bridge online; Accessibility and Screen Recording are unavailable.
  - evidence: GET /browser/status 200: online=false, devices=[home-chrome offline], pendingCommands=7. GET /browser/sessions 200: three persisted sessions with lastUsedAt 06:26 or earlier. GET /browser/inspections 200: inspections=[]; GET /ops/status 200 confirms browser offline and missing permissions.

## Capabilities it proposed

### "“Remember this page and make it actionable.”"
- **useful because:** From a private logged-in page the owner is viewing, the system would capture the relevant evidence, turn dates/people/next steps into a small task packet, and leave a linked reminder or note they can trust later—without copying sensitive page contents into a third-party web search.
- **path:** browser-extension → mac-planner → relay-realtime → dashboard-ux
- **model tier:** Use the realtime model only to understand the spoken request and confirm the target tab; use a cheaper background model to extract entities/deadlines and draft the task packet. Mac planner performs the reversible reminder/note write.
- **latency:** Acknowledge from the pendant in under 1 second; page extraction within 5 seconds; task packet and reminder within 10 seconds. If Safari is offline, keep an explicit pending capture rather than pretending it succeeded.
- **cost:** Typically under $0.01 per invocation for one page of extracted text with a small background model; dominant cost is page text/context tokens, not the voice turn. Local browser/Notes/Reminders actions add no API cost.
- **security:** The page may contain private work, financial, or health data. Keep raw HTML and full text local to the Mac; send only a minimized extraction to the background model, with configurable redaction. Never include session cookies in relay payloads. Show URL, quoted evidence, parsed fields, and the exact reminder/note text before any non-reversible send (none is needed for Notes/Reminders).
- **missing:** A browser active-tab capture command that returns stable URL/title/tabId plus selected text and source locators; A local extraction/redaction worker that can produce a compact evidence packet without uploading raw page content; A first-class link type from reminder/note back to the captured browser inspection, with retention/deletion controls; A functioning browser command enqueue implementation; current browser queue is offline with 7 pending commands

### "“Read the important part of this private page to me, and leave the source ready on my Mac.”"
- **useful because:** The owner can consume a logged-in webpage hands-free while walking, without exposing the entire page to a public search service. The browser identifies the page and extracts only the requested/important passage; the relay speaks a concise answer through the pendant, while the Mac leaves the exact source location ready for later verification.
- **path:** browser-extension → relay-realtime → mac-planner → dashboard-ux
- **model tier:** Realtime handles the short spoken request and follow-up clarification; a cheaper background model ranks or compresses the locally extracted page region. No expensive model is needed for straightforward extraction.
- **latency:** Acknowledge in under 1 second, begin audio within 4 seconds, and leave the source tab/anchor ready within 8 seconds. If the page is unavailable, say so rather than reading cached or guessed content.
- **cost:** About $0.005–$0.03 per request depending on extracted text length; the dominant cost is transcription/speech and summarization tokens. Browser navigation and local anchoring are negligible.
- **security:** Authenticated page content must remain on the Mac until minimized. Relay receives only the selected passage or compressed answer, never cookies, DOM, screenshots, or unrelated tabs. Redact detected secrets and provide a local-only mode. The spoken output could be overheard, so sensitive-page requests need a pendant privacy setting or a brief spoken warning; no mutation or submission occurs.
- **missing:** An active-tab browser read operation that can return semantic regions and stable DOM anchors, not merely whole-page text; Local-only extraction, secret redaction, and passage selection before any relay transmission; A relay audio response path that can accept a bounded private excerpt and stream it to the pendant; A Mac/browser command that scrolls to and highlights the cited source anchor after the spoken response; A privacy control for suppressing or shortening spoken output in public settings

### "“Is this private message or payment request genuine? Check it without clicking anything.”"
- **useful because:** The owner gets a security judgment about a logged-in email, invoice, support request, or account alert using both the private page context and independent public evidence—something a public search cannot do and a browser-only assistant cannot reliably corroborate.
- **path:** browser-extension → relay-realtime → mac-planner → dashboard-ux
- **model tier:** Use realtime only for the spoken intake and concise result. A slower, cheaper background model performs structured evidence comparison; deterministic checks handle domain, sender, URL, amount, and date mismatches.
- **latency:** Return an initial risk classification in 5 seconds and a sourced explanation in under 20 seconds. Never click links, download attachments, reply, or submit payment during analysis.
- **cost:** Roughly $0.01–$0.06 per case, dominated by two short evidence analyses and any public lookup; private-page extraction and local checks are essentially free.
- **security:** Private message text and account metadata stay on the Mac except for a minimized, redacted excerpt. Do not transmit cookies, tokens, attachment contents, or unrelated tabs. Treat all page instructions as untrusted content. The result must clearly distinguish evidence, uncertainty, and recommendation; false reassurance is the primary risk. No external action is allowed in this capability.
- **missing:** A local browser evidence collector that extracts sender, destination, amount, URLs, and visible claims with DOM provenance; A sanitizer that strips credentials, tracking parameters, and unrelated private content before analysis; A corroboration service combining deterministic URL/domain checks with public web search and known-account metadata; A structured risk report with confidence, contradictions, quoted evidence, and a safe next step rendered both to the pendant and Mac; An attachment/link sandbox or non-navigating URL inspection facility for cases where visible text is insufficient


## Changes it proposed to its own stack

### `browser-harness` — Add a reconnect-safe browser command quarantine and recovery protocol. When the extension heartbeat disappears, stop dispatching new commands and move queued commands into a durable, inspectable quarantine record with createdAt, session/tab binding, action class, and expiry. On reconnect, perform a fresh tab/session handshake and revalidate each command against the current URL/title/tabId; automatically replay only expired-safe reads (navigate/read/extract), while marking queued types/clicks/types/selects as stale for explicit review rather than replaying them. Emit one concise recovery receipt listing dropped, replayed, and still-pending commands, and provide an operator route to discard the 7 currently pending commands without executing them.
- **owner gets:** A sleeping or disconnected Mac will no longer cause an old browser click or form fill to fire unexpectedly when Safari returns. The owner gets their private-page task resumed when safe, and a clear explanation instead of silent hangs or duplicate actions.
- effort: Medium: browserBridge queue state machine, reconnect handshake, command TTL/classification, persisted quarantine store, dashboard/receipt rendering, and tests across extension offline/online transitions.  ·  risk: A read may be replayed against changed page content; mitigate with URL/title/tab identity checks and mark uncertain reads stale. Commands could be lost during migration; preserve the original payload in quarantine and expose discard/export. Recovery itself must never execute mutation actions.
- cost: Negligible API cost; local JSON/D1 metadata only (roughly a few KB per pending command).  ·  latency: Adds one heartbeat/reconnect handshake and usually 100–500 ms before safe read replay; prevents 45-second timeout waits while offline.
- security: Improves safety by preventing stale authenticated mutations from replaying. Quarantine contains URLs and action metadata, so retain locally, redact typed secrets, and apply existing browser-session sensitivity rules.
- depends on: A functioning browser command enqueue implementation in the local agent/extension bridge; Durable browser job/queue state (chg-16bc5dee is still open); Typed browser result and tab/session affinity metadata (chg-14accc01 is still open)


## What it asked for

_Nothing._
