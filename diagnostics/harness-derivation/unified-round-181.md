# Harness derivation — unified — round 181

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Continue the conversation I was having when the Mac or LTE dropped.”"
- **useful because:** A dropped link should not force the owner to repeat themselves or lose the answer. The pendant can preserve turn boundaries locally over USB today, while the relay and Mac reconcile the same turn when LTE returns, then resume at the next safe boundary instead of duplicating audio or actions.
- **path:** pendant → mac-bridge → relay-realtime
- **model tier:** Realtime for the live turn; background for reconciliation and duplicate detection
- **latency:** Under 300 ms to acknowledge a transport loss locally; reconciliation within 5 s after either link returns
- **cost:** About $0.01–$0.04 per recovered turn if transcription or summarization is needed; usually no extra model call when sequence metadata is sufficient
- **security:** Turn audio and text may leave the pendant only under the existing live-transport policy. Use monotonic turn IDs, transport epoch, and artifact hashes; never replay an unconfirmed action. Require the physical transaction latch for any pending side effect, and expose a concise recovery receipt.
- **missing:** Relay-side transport-epoch reconciliation and a durable turn handoff record; Mac/pendant implementation of the already-accepted USB fallback session sequence contract; A policy for how long incomplete conversational audio may be retained (owner retention answer is still outstanding)

### "“What went wrong while I was away, and is anything still stuck?”"
- **useful because:** The owner currently has to inspect unrelated pipeline, job, browser, Mac, and pendant records. A concise spoken outage digest would distinguish a failed action from a late-but-completed one, identify stale leases and held alerts, and give one safe next step instead of hiding failures behind “waiting.”
- **path:** relay-realtime → mac-bridge → browser-extension → pendant
- **model tier:** Background model for clustering and summarizing evidence; deterministic rules for severity and stale-state detection
- **latency:** Initial answer in under 2 s from bounded recent records; deeper evidence can arrive asynchronously with a receipt
- **cost:** Usually under $0.01 per query; most work is deterministic joins over existing receipts
- **security:** Redact page contents, command parameters, audio, and secrets by default. Only report bound app/tab names and opaque IDs. Any suggested repair must be dry-run first and require explicit confirmation for mutation.
- **missing:** A durable owner-acknowledgement cursor so “while I was away” has a reliable boundary; A typed cross-surface incident summary route that joins evidence without exposing raw payloads; A policy for retention/deletion of incident evidence (still awaiting the owner's answer)

### "“Tell me, without guessing, whether privacy mode is actually closed everywhere.”"
- **useful because:** A latched LED alone cannot prove that queued relay work, browser exposure, Mac capture, playback, and pending jobs have all stopped. The owner needs a truthful spoken verdict with explicit unknowns, especially after link loss or reboot, rather than false reassurance.
- **path:** pendant → relay-realtime → mac-bridge → browser-extension
- **model tier:** Deterministic verification and policy engine; no language model needed except optional spoken phrasing
- **latency:** Local pendant mute state within one frame; authenticated convergence verdict within 1 s when links are reachable, otherwise say UNKNOWN
- **cost:** Negligible API/model cost; one bounded verification request and compact receipt per check
- **security:** The pendant’s local latch is authoritative for mic and speaker. The relay must not claim browser/Mac silence without fresh receipts. Bind the verdict to latchId, device boot epoch, and observed timestamps; do not include audio or page contents.
- **missing:** A production owner-facing route that combines the already-granted privacy_convergence_check with Mac/browser capture and queued-job receipts; A clear degraded verdict vocabulary (CLOSED, PARTIAL, UNKNOWN) surfaced on the pendant; A local USB receipt path so this remains verifiable while LTE is unregistered

### "“For the next ten minutes, use that signed-in tab only to answer the exact field I name—don’t read the rest of the page or expose its contents.”"
- **useful because:** The owner can currently ask for browser work, but cannot create a narrow, expiring data boundary around a privileged tab. This would let the pendant answer a concrete question from a logged-in page while preventing accidental narration, persistence, or action outside the named field.
- **path:** pendant → relay-realtime → browser-extension → mac-bridge
- **model tier:** Deterministic browser extraction and policy enforcement; a cheap background model may resolve the owner’s field label, but never receives the full page
- **latency:** Under 2 seconds for a field read; refusal immediately if the tab, field, origin, or expiry does not match
- **cost:** Typically below $0.01 per request; no model call when a declared selector/schema matches
- **security:** The extension must return only the selected value plus origin, selector/schema ID, timestamp, and redacted hash—not DOM, screenshots, cookies, or page text. Bind the capability to an exact tab/session and origin, expire it automatically, log an auditable receipt, and require physical confirmation for any write or submit.
- **missing:** A browser capability-token route that binds origin, tab/session, allowed field schema, expiry, and read-only scope; An extension-side structured-field extractor with refusal on ambiguous or off-schema matches; Pendant speech that reports provenance and expiry without exposing sensitive surrounding content

### "“Before you use a logged-in site, tell me which account, origin, and tab you are about to touch—and refuse if any of them changed.”"
- **useful because:** Today a browser session is reachable, but the owner has no spoken, per-action identity check that the privileged tab is still the intended account. A changed tab or account can turn a harmless request into an action on the wrong person’s data.
- **path:** pendant → browser-extension → relay-realtime → mac-bridge
- **model tier:** Deterministic identity and origin attestation; no model call
- **latency:** Under 500 ms before an action is planned; hard refusal on stale or unverifiable attestation
- **cost:** Negligible; signed metadata and one short receipt per browser session
- **security:** Never transmit cookies, tokens, page text, or screenshots. Attest only origin, tab ID, account label supplied by the page’s trusted identity surface, extension version, and timestamp. Treat labels as untrusted until the owner confirms; require physical approval for writes.
- **missing:** A signed browser-session attestation primitive tied to extension installation and tab identity; A Mac-side account/origin verifier that can distinguish navigation and login changes; A pendant-readable confirmation frame and stale-attestation refusal path

### "“Stop the thing you are doing right now—everywhere—and prove that it stopped.”"
- **useful because:** A cancel request today can target a relay job, but it does not guarantee that a claimed Mac job, browser command, queued audio, or pending follow-up has also stopped. The owner needs one emergency stop that propagates over USB or relay and returns a per-surface receipt, without relying on the model to remember every job ID.
- **path:** pendant → mac-bridge → browser-extension → relay-realtime
- **model tier:** Deterministic cancellation fan-out and receipt correlation; no model call
- **latency:** Local pendant stop within one audio frame; Mac/browser cancellation attempted within 1 s; verdict must say STOPPED, PARTIAL, or UNKNOWN
- **cost:** Negligible API cost; bounded cancellation fan-out and one signed receipt
- **security:** Bind the stop to a conversation epoch or explicit emergency-stop nonce so it cannot cancel unrelated future work. Cancel is best-effort for already-committed external effects; report those separately. Never claim browser or Mac stopped without a fresh acknowledgement.
- **missing:** A cross-surface cancellation token and epoch registry; Mac and browser handlers that cancel in-flight work and acknowledge it idempotently; A pendant USB command/receipt path that works while LTE is unregistered; A durable distinction between cancelled, already-committed, and unreachable


## What it asked for

_Nothing._
## Its own summary

Recorded three distinct owner-facing capabilities: transport-epoch conversation continuation across pendant/Mac/relay, a cross-surface “what went wrong while I was away?” digest, and an authenticated privacy-closure verdict that reports UNKNOWN rather than guessing. I also attempted the approval-loop integration change; the recorder correctly identified it as an existing proposal, so I did not restate it. Current live discovery shows Safari online, the Mac bridge online, and the LTE/mobile device offline; the pipeline contains a real 24 kHz TTS result and also a real dead-end “Waiting for your approval on the dashboard” event.

**Biggest unknown:** The owner’s retention/deletion policy and intended personal timezone remain unanswered context. Technically, the largest missing pieces are relay-side transport reconciliation, an owner-ack cursor for outage digests, and a USB-verifiable privacy receipt; no additional discovery tool is needed this round.

