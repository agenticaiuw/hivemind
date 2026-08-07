# Harness derivation — unified — round 74

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “save this,” preserve the exact thing I just heard and the evidence behind it: create a private, searchable note containing the recent pendant audio, transcript, timestamp, and any Mac/browser sources that informed the answer, then give me a one-sentence receipt."
- **useful because:** It turns fleeting voice interactions into trustworthy records without making the owner repeat context. The pendant supplies the moment and confirmation, the relay durably stores/transcribes it, and the Mac/browser contribute the exact logged-in page or document evidence—something no single surface can assemble reliably.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** Realtime only for the short confirmation and intent boundary; a cheaper background model performs transcription cleanup, source linking, and note summarization.
- **latency:** Acknowledge on the pendant within 500 ms; make the searchable note available within 10 s after capture. Keep the rolling audio local until the explicit “save this” trigger.
- **cost:** About $0.01–$0.05 per saved moment, dominated by transcription and background summarization; storage is negligible per note but audio retention must be bounded.
- **security:** Audio and authenticated-page excerpts leave the pendant only after explicit owner speech/button confirmation. Redact secrets, preserve source URLs and hashes rather than whole pages where possible, encrypt clips, and require confirmation before sharing or sending any note.
- **missing:** A bounded local pre-trigger audio buffer and explicit save gesture; A durable note schema joining audio, transcript, timestamp, and source evidence; A Mac/browser context snapshot API that returns active-tab/app provenance; A retention and deletion control for captured clips

### "Let me ask the pendant about a private account without sending the page to the cloud: have the relay recognize the request, let the Mac/browser read the already-open authenticated page locally, return only the minimum answer or a redacted structured result, and show me a receipt of what fields were accessed."
- **useful because:** Today a voice request about a logged-in page either cannot be answered when the browser is unavailable or risks shipping sensitive page content through the relay. This would make the pendant useful for private accounts while keeping raw email, health, finance, and work pages on the owner's devices.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** Realtime handles intent and a brief spoken response; a cheaper local Mac planner performs page extraction and redaction. The relay should route and validate, not summarize raw private content.
- **latency:** Acknowledge intent in under 500 ms and return a small structured answer in 3–8 s, depending on the local browser response.
- **cost:** Near-zero relay model cost for the normal path; local extraction dominates. A fallback cloud model must be opt-in and clearly marked, with roughly $0.01–$0.05 per invocation.
- **security:** Raw DOM, screenshots, cookies, and page URLs stay on the Mac. Use a typed field allowlist, redact secrets and query parameters, attach an access receipt, expire the result quickly, and require explicit confirmation before any mutation or external send.
- **missing:** A relay routing contract that distinguishes private-page queries from ordinary cloud questions; A local-only browser extraction endpoint returning typed, redacted fields rather than page text; A policy engine for field-level sensitivity and explicit cloud-fallback consent; A user-visible access receipt spanning pendant, relay, Mac, and browser


## Changes it proposed to its own stack

### `integration` — Add a signed cross-surface evidence envelope for any answer or saved voice moment. The relay assigns an interactionId; the Mac planner and browser bridge contribute active-app/tab URL, timestamp, selected text hash, and action/job receipt; the relay stores only the envelope plus bounded excerpts and exposes a dashboard timeline and pendant lookup by interactionId. Reject stale or mismatched tab/session contributions instead of silently merging them.
- **owner gets:** When the owner later asks “what was that based on?”, they get an auditable answer tied to the exact page and moment, rather than an unverifiable transcript or a stale browser tab. It also makes saved voice notes genuinely useful for follow-up.
- effort: Medium: shared schema, signing/validation in relay and Mac bridge, browser metadata hook, dashboard timeline, and retention tests.  ·  risk: Clock skew, browser tab closure, or partial uploads could make evidence incomplete; mark each field unavailable and show confidence rather than fabricating. Recover by retaining the raw job receipt and allowing the owner to discard the note.
- cost: Low API cost; roughly a few hundred bytes of metadata per interaction, with excerpts/audio dominating storage and subject to existing retention controls.  ·  latency: Under 100 ms for envelope assembly; background summarization remains asynchronous.
- security: High-value provenance metadata and possibly sensitive URLs are centralized. Encrypt at rest, hash content instead of copying it by default, redact query parameters, and enforce per-owner access checks.
- depends on: A bounded explicit-save audio capture path; A durable interaction/receipt identifier shared by pendant, relay, Mac, and browser; Browser bridge metadata hook for the currently attached tab; Retention and deletion controls for captured evidence

### `relay` — Introduce a private-data execution lane between relay, Mac, and browser. A request marked private_page is handed to the local agent with a field-level allowlist and no raw-page return path; the Mac emits a signed redacted result plus accessed-field receipt, and the relay rejects payloads containing DOM, screenshots, cookies, or unapproved fields. Make cloud fallback an explicit owner approval, not an automatic retry.
- **owner gets:** The owner can safely ask the pendant about logged-in accounts from anywhere and receive a useful answer without their private page silently becoming cloud prompt data. If the browser is offline, they get an honest unavailable receipt rather than a hallucinated answer.
- effort: Medium-high: typed request/response schema, local extraction and redaction, relay validation, receipt persistence, dashboard display, and adversarial secret-leak tests.  ·  risk: Over-redaction may make answers incomplete; return missing-field reasons and offer a local retry. Misclassification could expose data; default ambiguous requests to private mode and fail closed. Browser disconnects should produce a durable no-access receipt.
- cost: Minimal relay compute and storage; local planner/extraction work dominates. No cloud-token cost unless the owner explicitly approves fallback.  ·  latency: Adds roughly 100–300 ms for policy validation and receipt signing; local browser extraction remains the main delay.
- security: Substantially reduces raw private-data egress, but makes the Mac agent a high-trust boundary. Use per-request nonces, authenticated bridge responses, field allowlists, redaction tests, and short-lived receipts.
- depends on: Field-level sensitivity policy and cloud-fallback consent; A local browser endpoint that returns typed redacted fields; Signed cross-surface interaction receipts; Browser reconnect/error handling


## What it asked for

_Nothing._
## Its own summary

Round 74 produced and recorded a new cross-surface capability: explicit “save this” captures the recent pendant moment plus transcript and Mac/browser evidence, with a signed interaction envelope tying source tabs, timestamps, hashes, and receipts together. I also recorded the integration change required to make that provenance durable. Fresh probes show the relay and Mac bridge are reachable, the browser extension is offline with 5 pending commands, computer-use remains disabled by missing Accessibility/Screen Recording, and the pendant audio prototype still captures at 15,625 Hz while playback is 24 kHz/60 ms Opus and LTE-M drops packets under duplex load.

**Biggest unknown:** No new grants appeared in discover:granted this round. To advance the owner's explicit 24 kHz end-to-end audio goal, the system still needs authoritative product/acceptance thresholds, link-governor and fault-injection validation, and the owner's privacy/retention policy for saved audio and authenticated-page evidence. The browser context contribution also cannot be tested until the extension reconnects.

