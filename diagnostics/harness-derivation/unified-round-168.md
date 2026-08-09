# Harness derivation — unified — round 168

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Save this browser task so I can continue it later, even if the browser or Mac goes offline, and tell me exactly what was saved without exposing page secrets."
- **useful because:** Safari is online with nine tabs, yet repeated inspection failures show that a live tab is not durable state. A redacted continuation capsule would let the owner resume a research or shopping task instead of losing the tab context when the bridge dies.
- **path:** browser-extension → mac-bridge → relay
- **model tier:** Background model only when summarizing owner-selected content; deterministic capture, redaction, hashing, and replay otherwise.
- **latency:** Capture receipt in under 2 seconds; restore should be resumable within 5 seconds after the browser returns.
- **cost:** <$0.005 for metadata-only capture; up to $0.02 if the owner explicitly requests a model summary of selected page text.
- **security:** Bind capsule to an exact tab/session and owner command; default to URL/title/selection hashes, not cookies, DOM, passwords, or full page text. Encrypt relay storage, expire capsules, and require confirmation before replaying any mutating browser action.
- **missing:** A durable relay route for redacted browser continuation capsules with expiry; An extension command to export a bounded, owner-selected state snapshot and later acknowledge restoration; A typed join between browser command/result receipts and the capsule ID

### "Before my scheduled brief runs, verify whether its time zone is actually mine; if the Mac zone and my declared personal zone disagree, warn me and do not silently fire it at the wrong local time."
- **useful because:** The system currently has an authoritative Mac zone of America/New_York while the owner memory says America/Chicago, and routines are already firing at 07:00/07:30. Silent zone substitution can make a morning brief arrive an hour early and trains the owner not to trust the pendant.
- **path:** relay → mac-bridge → pendant
- **model tier:** Deterministic timezone and schedule evaluation; cheap background model only to phrase a concise spoken warning.
- **latency:** Check at scheduler claim time; warning delivery within one minute, with no delay for routines whose zone is explicitly resolved.
- **cost:** Near-zero API cost; one small state read per routine run and an optional short TTS sentence.
- **security:** Do not infer location from IP or GNSS. Store only an explicit IANA zone declaration and provenance (owner vs Mac). A mismatch must default to hold-and-ask, never silently change the schedule.
- **missing:** An owner-confirmed personal IANA timezone (the current Chicago memory conflicts with the Mac's New York authority); A routine scheduler gate that records the zone used for each firing and can hold one run; A pendant inbox event for the warning when the Mac is unavailable

### "Make my scheduled research brief arrive once with citations and a playable audio version; if the pendant was offline, tell me that it is queued rather than silently generating a duplicate edition."
- **useful because:** The owner already schedules a daily LTE-M research brief with audio, but a completed job, a stored note, and actually hearing it are different facts. Joining source provenance, job identity, and audio delivery would prevent duplicate spoken editions and make offline recovery trustworthy.
- **path:** relay → mac-bridge → browser-extension → pendant
- **model tier:** Background model for the research summary; deterministic job/idempotency and delivery reconciliation; realtime only when the owner asks for status.
- **latency:** Research remains background-speed (minutes); status and queued/played answer under 1 second; no duplicate TTS generation during reconciliation.
- **cost:** Existing scheduled research cost plus <$0.01 for metadata reconciliation; avoid re-running the expensive model when a matching job already has a receipt.
- **security:** Keep source URLs and bounded excerpts, not credentials or arbitrary browser state. Bind citations to the job digest, sign delivery receipts, and never auto-send external messages. Retain only the owner's configured brief history and expiry.
- **missing:** A stable content digest/idempotency key shared by routine, briefing, TTS, and audio delivery; A join record connecting POST /briefing output to pipeline and pendant playback receipts; A scheduler recovery rule that marks offline audio as queued and later surfaces exactly once

### "Show me a private, plain-language record of what data left my pendant in the last hour, which surface received it, why it was sent, and when each copy expires—without revealing the audio or page contents."
- **useful because:** The owner can currently verify that capture is stopped, but cannot audit the positive history of disclosure across pendant, relay, Mac, and browser. A compact provenance view would make the system trustworthy after a sensitive conversation or unexpected outage.
- **path:** pendant → relay → mac-bridge → browser-extension
- **model tier:** Deterministic event classification and redaction; background model only to summarize the already-redacted manifest.
- **latency:** Under 2 seconds for a one-hour manifest; spoken answer under 10 seconds; no work on the audio hot path.
- **cost:** Under $0.01 per query; metadata only, with bounded event records.
- **security:** The manifest must contain hashes, data classes, destinations, purpose, retention deadline, and receipts—not raw audio, transcripts, cookies, or page text. Encrypt it, authenticate the owner query, and support immediate deletion of the manifest independently of payload deletion.
- **missing:** A signed data-disclosure event emitted at every pendant-to-relay, relay-to-Mac, and browser handoff; A retention ledger that records expiry and deletion receipts across surfaces; An owner-facing redacted query and spoken renderer for the joined manifest

### "From the pendant, revoke only my browser session and cancel every queued browser action now; leave the conversation and Mac work alone, then give me a receipt proving the browser is no longer exposed."
- **useful because:** The existing privacy latch protects microphone and playback, but a compromised or unwanted browser session is a different risk. The owner needs a physical, offline-safe way to cut browser reach without shutting down unrelated work.
- **path:** pendant → relay → browser-extension → mac-bridge
- **model tier:** Deterministic revocation and lease invalidation; realtime only to state the result.
- **latency:** Local pendant indication immediately; browser lease invalidation within 2 seconds when connected; queued commands must be rejected thereafter.
- **cost:** Near-zero model cost; bounded state writes and one authenticated convergence receipt.
- **security:** Bind revocation to a specific browser identity/session, not a global Mac kill switch. Invalidate pending commands and replay tokens, preserve an audit receipt, and never transmit page contents during revocation. If disconnected, retain the revocation nonce and apply it before any later browser reconnect.
- **missing:** A firmware event and durable nonce for browser-only revocation; Relay storage and enforcement of a browser-session revocation epoch; A browser bridge handler that rejects queued/in-flight commands and reports convergence


## Changes it proposed to its own stack

### `interaction` — Add a cross-surface 'why did this happen?' explanation contract: every owner-visible action and audio artifact carries a compact causal chain linking the spoken request, plan/job, browser or Mac effects, and delivery outcome, with explicit gaps instead of inferred success.
- **owner gets:** When something goes wrong, the owner can ask one question and receive an honest chain such as requested → planned → executed → delivered, rather than a confident sentence assembled from disconnected status records.
- effort: Medium-high: define an immutable correlation schema, instrument relay/Mac/browser/pendant events, and add a spoken/dashboard renderer.  ·  risk: Event gaps or clock skew could produce incomplete chains; show unknown rather than inventing causality, and preserve existing job behavior if instrumentation fails.
- cost: Small metadata overhead per action; no meaningful model cost unless the owner requests a natural-language explanation.  ·  latency: No hot-path delay beyond appending metadata; explanation query may take 1–3 seconds.
- security: Redact parameters and content, expose only owner-authorized surfaces, and retain configurable expiration for causal records.
- depends on: The existing action/job and audio receipt identifiers must be propagated across relay, Mac, browser, and pendant; A durable correlation index must be added without storing raw audio or page contents


## What it asked for

_Nothing._
