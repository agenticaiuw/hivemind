# Harness derivation — relay-realtime — round 56

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What happened to the thing I asked you to do earlier?"
- **useful because:** This matches how people actually speak to a wearable: short, vague, and time-shifted. It lets the owner check progress even if the Mac is asleep, without re-describing the task.
- **path:** pendant → relay → mac-bridge
- **model tier:** relay realtime for the spoken status; backend record lookup only, no planning
- **latency:** Under a second when the relay has a matching record. If not found, quickly say it’s unknown and offer to start a new request.
- **cost:** Cheap: a single relay record lookup dominates. No Mac round trip.
- **security:** Status text may include task titles or partial content. Keep it concise, avoid leaking sensitive payloads, and never claim completion unless the record says done.
- **missing:** A consistent job reference strategy across mac_run_actions/mac_delegate and relay records so vague references reliably resolve; A typed, minimal spoken status format across surfaces (already partly covered by relay_job_status, but should be standardized for other long-running work too)

### "“Compare the document I’m looking at in my browser with the matching file on my Mac and tell me what differs.”"
- **useful because:** While away from the desk or moving between devices, the owner can get a trustworthy spoken discrepancy check across two sources that no single node can see. It is useful for invoices, contracts, tickets, and forms where a stale or mismatched copy is costly.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Relay-realtime handles the short spoken request and final concise answer; browser and Mac agents perform parallel extraction with a cheaper background model; a shared comparison worker normalizes text, tables, totals, dates, and identifiers. Realtime is not used for document parsing.
- **latency:** Acknowledge in under 500 ms; return a short answer in 5–15 seconds for already-open pages/files, with a longer job and completion notification if OCR or file search is needed.
- **cost:** Roughly $0.01–$0.08 per invocation depending on OCR and document length; dominant costs are document extraction and model comparison, not the voice turn.
- **security:** Read-only by default. Authenticated browser content and selected Mac file contents leave their respective devices only for this explicitly requested comparison; redact secrets and retain only hashes, cited spans, and a short receipt. Do not open unrelated tabs/files. Tell the owner when one side is unavailable or stale rather than silently comparing different documents.
- **missing:** A cross-surface comparison job contract accepting a browser tab plus a Mac file/document reference and returning typed cited fields; Browser extraction that can identify the current document and export bounded text/table data; Mac read-only document extraction with stable file identity and observedAt timestamps; A relay fan-in/orchestrator for parallel results, mismatch classification, and spoken plus durable receipts; A user-visible way to select or disambiguate the matching Mac file when multiple candidates exist


## Changes it proposed to its own stack

### `model-routing` — Align the relay's tool registry with the 'granted' inventory: if a tool is granted by the orchestrator (e.g., relay_route_intent, server_browser_actions), it must be discoverable via the tool discovery/describe path used by agents. If a tool is not actually available, remove it from 'granted' to avoid a false affordance.
- **owner gets:** The owner gets fewer silent failures and less confusing behavior when they ask for something and the relay appears to have a tool but actually cannot call it. This reduces latency and misroutes in live voice.
- effort: Low to medium: update discovery metadata or tool wiring; add a validation step in startup that cross-checks granted tools against callable tool definitions.  ·  risk: If wired incorrectly, the relay could lose access to a legitimately available tool. Mitigate with a health check that exercises describe() for each granted tool and logs discrepancies.
- cost: Small API cost for periodic validation; negligible runtime cost.  ·  latency: Slight increase at startup/health-check; no added latency during normal voice turns.
- security: Improves security posture by preventing phantom tool calls or accidental routing to unintended surfaces.
- depends on: A canonical source of truth for tool availability (or a handshake response from the orchestrator that includes callable tool definitions).

### `integration` — Add a read-only Cross-Surface Evidence Bundle protocol. A relay request creates a correlation id and asks the browser bridge and Mac bridge for bounded, typed observations (document identity, title, URL/path, selected text/table fields, observedAt, freshness TTL, content hash, and source citations). The relay waits for both or records an explicit unavailable side, then emits one immutable comparison receipt; raw content expires while hashes/citations remain. This is a data contract and fan-in service, not an execution gate.
- **owner gets:** The owner can ask a natural spoken question about two devices and receive an answer that is visibly grounded in the exact page and file observed, instead of an opaque model guess or a comparison of stale copies.
- effort: Medium: define the bundle schema and correlation lifecycle, add bounded extractors on both bridges, implement freshness and redaction, and add tests for missing, changed, and duplicate documents.  ·  risk: One source may change during extraction, extraction may misidentify a matching file, or sensitive content may be over-collected. Mitigate with observedAt/hash fields, bounded source selection, explicit confidence and ambiguity in the receipt, short retention, and a spoken fallback asking which source to use. No mutations are performed.
- cost: Small relay/storage overhead; approximately 1–5 KB metadata per receipt plus transient extracted text. Model/API cost is dominated by the eventual comparison, not the protocol.  ·  latency: Parallel bridge reads add little latency; typical already-open sources should complete in seconds. Timeouts must produce a partial, clearly labeled result rather than blocking indefinitely.
- security: Improves least-data handling by sending only selected bounded fields and retaining provenance instead of whole documents. Requires authenticated bridge channels, per-request correlation isolation, and redaction before relay persistence.
- depends on: Browser bridge must expose bounded read-only extraction of the active/selected tab; Mac bridge must expose bounded read-only extraction with stable file identity; A comparison/fan-in worker and receipt schema


## What it asked for

_Nothing._
