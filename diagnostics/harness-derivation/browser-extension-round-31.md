# Harness derivation — browser-extension — round 31

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge liveness** — Live /browser/status reports Safari absent/offline and two pending browser commands; the only registered device is home-chrome with no tab. /ops/snapshot independently reports browser online=false and pendingCommands=2.
  - evidence: GET /browser/status HTTP 200: online=false, devices=[home-chrome tabId=null tabCount=null], pendingCommands=2; GET /ops/snapshot same browser state.

## Capabilities it proposed

### "“Find the exact information I saw recently—whether it was in Safari, a Mac document, or something I told you—and show me where it came from.”"
- **useful because:** Today the owner must remember which surface contains a fact and manually search each one. This would let the pendant act as a cross-surface provenance finder for private, logged-in pages and local material, returning the exact answer with source links, document paths, timestamps, and quoted evidence rather than an unsupported synthesis.
- **path:** pendant: capture the spoken query and read back a concise answer → relay: route the request, maintain the job, and return the result to the pendant → mac-planner/mac-terminal: search local documents, notes, mail, calendar, and conversation memory without uploading their contents unnecessarily → browser harness: search or inspect the owner's existing authenticated Safari tabs and permitted logged-in sites → dashboard: present ranked matches, quoted evidence, and source-open actions
- **model tier:** Use a cheaper background text model for indexing and candidate ranking; use the realtime tier only for the spoken query and final concise response. Escalate to a stronger model only when sources conflict or the query is genuinely ambiguous.
- **latency:** A simple local lookup should answer in 2–5 seconds; authenticated browser inspection may take 10–30 seconds and should be announced as in progress. The owner should receive partial matches if one surface is unavailable.
- **cost:** Roughly $0.005–$0.03 per lookup depending on how many browser pages require extraction; embedding/index maintenance dominates ongoing cost more than the final answer.
- **security:** Private page text, local files, and spoken memories must remain scoped to the owner's paired devices and be minimized in relay payloads. Store hashes and source metadata by default, not full page contents. Show a source and confidence for every claim, label cross-account ambiguity, and never expose a result to an unpaired pendant or browser device.
- **missing:** A unified provenance-aware search index spanning local Mac sources, browser extraction results, and pendant conversation memory; A browser operation for scoped multi-tab/site search that can return snippets and stable source references without blindly reading every authenticated page; A result schema carrying source type, URL or file path, timestamp, quote, confidence, and sensitivity; Permission-aware context projection so the relay can coordinate the search without receiving raw private contents

### "“While I’m looking at this page, tell me whether it fits my real constraints—my calendar, existing commitments, budget, or preferences—and point out what I should verify.”"
- **useful because:** The owner can ask a generic assistant about a page, but today no single node can combine the exact authenticated page they are viewing with private Mac records and a low-friction spoken answer. This would turn browsing into situated decision support without requiring the owner to copy URLs, screenshots, or account details.
- **path:** browser extension: identify the active Safari tab and extract only the relevant page region, title, URL, and structured facts → mac-planner/mac-terminal: retrieve the minimum relevant calendar, reminders, local files, or preference facts → relay: coordinate the parallel browser and Mac lookups and stream progress while preserving device scoping → pendant: accept the short spoken question and read back a source-linked recommendation → dashboard: show the page evidence, local constraints used, assumptions, conflicts, and an option to open the sources
- **model tier:** Use a small background model for structured extraction and constraint matching; use realtime only for the conversational turn and spoken explanation. Use a stronger model only if the page is unstructured or constraints conflict.
- **latency:** Target 3–8 seconds for a normal page with local data; up to 20 seconds for a complex authenticated page. Return an initial answer with explicit uncertainty if one source is slow.
- **cost:** Approximately $0.01–$0.05 per request; browser extraction and model context size dominate, while local calendar/file retrieval is inexpensive.
- **security:** Only the active tab region and explicitly relevant local facts should be shared. Do not send full authenticated pages or unrelated calendar history to the relay. Treat financial, health, and relationship constraints as sensitive, maintain an audit record of sources used, and make recommendations—not purchases, bookings, or submissions.
- **missing:** A tab-scoped active-page context API with user-selected or semantic-region extraction; A typed constraint/query interface joining browser facts to permission-filtered Mac data; A cross-surface provenance and sensitivity policy that can redact local facts before relay coordination; A pendant-to-active-tab association protocol so a spoken request reliably targets the page the owner is viewing


## Changes it proposed to its own stack

### `browser-harness` — Add a browser-bridge lease and reconciliation layer distinct from the durable job runner: every enqueued browser command gets an expiry, cancellation token, device-generation/heartbeat snapshot, and explicit state machine (queued, leased, delivered, result, expired, cancelled, orphaned). On extension reconnect, perform a handshake that reports device generation, open tabs, and the command IDs it has seen; reclaim commands from dead generations rather than replaying clicks/types. Move currently pending commands that outlive their lease into an owner-visible 'stale browser work' record with the original intent, target URL/tab, and safe recovery options (retry after Safari is online, inspect, or discard). Ensure browser jobs never silently time out after the 45-second wait while leaving actions queued.
- **owner gets:** If Safari sleeps, restarts, or loses its extension connection, the owner will not get phantom failures, duplicate form edits, or invisible work stuck forever. A private-page task can resume safely when the browser returns, while the pendant can say exactly whether it was completed, deferred, or abandoned.
- effort: Medium: browserBridge queue/state machine and extension handshake, D1/local persistence for leases and stale records, plus job/result/dashboard status plumbing and reconnect tests for navigate/type/click.  ·  risk: A crash during the lease boundary can still create ambiguity; default recovery must be inspect/reconcile, never replay a mutating command automatically. Persist idempotency keys and before/after evidence where available, and provide a discard path for stale work. No page data needs to leave the Mac unless the existing result pipeline sends it.
- cost: Negligible API cost; a few local/D1 rows and heartbeat traffic per browser device.  ·  latency: Normal commands unchanged; reconnect adds one handshake round trip. Stale work is surfaced immediately rather than waiting for the 45-second bridge timeout.
- security: Reduces replay risk for authenticated sessions. Keep URLs, tab IDs, and extracted snippets subject to existing local retention policy; do not expose stale command payloads to unrelated devices.
- depends on: chg-14accc01 request IDs/idempotency/tab affinity (already partially present); chg-16bc5dee durable browser runner; A functioning Safari extension heartbeat/reconnect path


## What it asked for

_Nothing._
