# Harness derivation — unified — round 164

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser readiness** — The Mac agent is healthy and fully ready: Accessibility and Screen Recording are granted for AI Pendant Agent, browser extension is online on Safari tab 1163292 (x.com), relay is reachable, and no browser commands are pending or spooled.
  - evidence: GET /ops/status and GET /browser/status returned ok:true, permissions.ready:true, accessibility.trusted:true, screenRecording.granted:true, browser.online:true, pendingCommands:0, spooled:0.

## Capabilities it proposed

### "“Read the Safari page I’m on, but bind your answer to this exact tab and show me the quoted evidence before I trust it.”"
- **useful because:** A wearable answer is only useful if it is grounded in the page the owner deliberately exposed, not a stale or different browser tab. This creates a short-lived, least-privilege evidence capsule: inspect one bound tab, extract quotes and URL/title, then stream the spoken answer through the pendant while retaining a verifiable receipt.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** background for page extraction and citation selection; realtime only for the owner’s follow-up conversation
- **latency:** First evidence in 2–4 s; follow-up answers under 1.5 s when the capsule is warm.
- **cost:** About $0.01–$0.04 per page capsule depending on length; follow-ups dominate cost only when they require fresh model synthesis.
- **security:** The capsule must bind to an explicit tab/session URL pattern, expire within minutes, redact secrets/forms, and never send full page contents to the pendant. Require a spoken or physical confirmation before inspecting a new tab. Browser commands and extracted quotes need an opaque receipt.
- **missing:** A first-class tab-binding/evidence-capsule record with expiry and digest; A browser inspect response that returns stable quote anchors and a content digest; Pendant playback of the evidence capsule receipt

### "“Fill this web form, show me the exact final values, and only submit after I approve that frozen version with the button on my pendant.”"
- **useful because:** It closes the dangerous gap between a model planning a browser write and the owner knowing exactly what will be sent. The browser stages the form, the relay freezes a digest and world snapshot, the pendant gives a deliberate offline-safe approval, and submission returns a receipt tied to the same digest.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** background/planner for extracting fields and drafting values; realtime only to explain the staged diff or answer a question
- **latency:** Stage and read back in 3–6 s; submission receipt within 2 s after physical approval.
- **cost:** Roughly $0.02–$0.08 per staged form, dominated by field interpretation; no model call for the approval or receipt path.
- **security:** Never transmit passwords or hidden fields into the staged summary. Bind approval to form URL, field digest, action nonce, expiry, and world fingerprint; reject if the page changes. The browser must not submit on a generic approval; only the exact nonce can unlock one submit. Log redacted field names, not values.
- **missing:** Connect physical_transaction_approval_latch to the existing formPreview approval state; A relay implementation of APPROVAL_STORE_CONTRACT and a delivery/readback path; Browser-side staged-form snapshot and submit-by-nonce command; A distinct authorization boundary so approving cannot simply equal possessing the execute bearer token

### "“Keep our conversation alive if I unplug the Mac or the USB cable drops; switch transport only at a turn boundary and tell me if anything was lost.”"
- **useful because:** The pendant is physically testable over USB now but must not duplicate audio or cut a sentence in half when ownership moves between the Mac bridge and LTE. A turn-aware handoff would make the wearable useful while walking away from the Mac instead of silently ending or replaying a reply.
- **path:** pendant → mac-planner → relay-realtime → mac-vision
- **model tier:** realtime for the live conversation; deterministic firmware/relay logic for transport election, sequence checks, and handoff receipts
- **latency:** Detect cable loss in under 1 s; hand off at the next turn boundary in under 3 s; no audible duplicate segment.
- **cost:** Negligible model cost beyond the existing conversation; engineering cost is in transport state and fault testing, not inference.
- **security:** Use monotonic turn/frame counters and an authenticated session nonce so a stale USB stream cannot inject audio after LTE takes ownership. Do not persist raw audio merely because a handoff failed; retain only bounded metadata and use the existing failure-only audio spool. Announce degraded mode audibly and expose a receipt when frames were dropped.
- **missing:** A relay transport-election state machine with turn-boundary ownership and session fencing; Mac bridge unplug/reconnect events surfaced to the relay; Cross-transport sequence reconciliation and owner-facing loss receipt; A policy setting for lte_only / phone_preferred / phone_fallback

### "“Watch this specific Safari tab for a meaningful change, and tell me over the pendant only when the change matches my rule.”"
- **useful because:** The owner should not have to keep a tab open mentally or repeatedly ask for status. A bound, expiring watcher can compare only the selected page, suppress cosmetic changes, and deliver a short alert to the pendant; it turns the browser’s private session plus the wearable’s attention into something neither can do alone.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** deterministic hashing/diff first; background model only to classify a candidate change; realtime only for the spoken alert
- **latency:** Poll at the owner-selected interval (15 s minimum); alert within one poll after a qualifying change.
- **cost:** Near-zero when hashes suppress changes; about $0.005–$0.02 per semantic-change classification. Browser polling and relay storage dominate, not inference.
- **security:** Require explicit tab binding, expiry, and an allowlist of URL origins. Do not retain page snapshots by default; keep only redacted diff snippets and a digest. Never watch password, banking, or private-message pages unless the owner explicitly overrides. Provide a pendant privacy-latch kill switch and a visible active-watcher list.
- **missing:** Owner-facing create/pause/stop watcher command with TTL and polling budget; Semantic diff/redaction over browser inspection results; Relay delivery into the existing pendant inbox with deduplication and expiry; A policy that prevents watchers from interrupting active conversation

### "“What am I looking at right now?” — have the pendant describe the Mac screen using a local, redacted visual summary, without uploading the screenshot or exposing unrelated windows."
- **useful because:** The wearable becomes an eyes-free companion for the owner’s actual screen while preserving privacy. Today the computer-use loop can see or act on the Mac, and the pendant can speak, but there is no owner-facing mode that guarantees screenshots stay local and returns only the requested description. This is especially valuable for accessibility, troubleshooting, and checking a visual state while away from the keyboard.
- **path:** pendant → mac-vision → mac-planner → relay-realtime
- **model tier:** A local vision model or deterministic OCR/layout extractor should produce the redacted summary; use the realtime model only for the owner’s spoken question and concise response.
- **latency:** Answer within 2 seconds for OCR/layout summaries and under 4 seconds for local visual interpretation.
- **cost:** Near-zero relay inference cost when local extraction succeeds; optional fallback vision inference would cost roughly $0.01–$0.05 per request and must require explicit opt-in.
- **security:** Screenshots must remain on the Mac by default. Redact passwords, private messages, tokens, and unrelated windows before any summary leaves the device. Require an active pendant conversation or button-triggered request, show a local capture indicator, expire the frame immediately, and log only a redacted provenance receipt. The privacy latch must cancel queued visual requests.
- **missing:** A local-only visual-summary service with field-level redaction and no raw-frame persistence; A pendant request/response envelope carrying a frame nonce and redacted summary receipt; A hard policy boundary preventing the relay fallback from receiving raw screenshots without explicit owner consent; A concise spoken contract for uncertainty and stale-screen timestamps


## Changes it proposed to its own stack

### `mac-harness` — Add a local visual-summary lane that captures one consent-scoped screen frame, performs OCR/layout classification on-device, strips secrets and unrelated windows, and emits only a redacted summary plus frame digest to the relay. The lane must refuse raw-frame upload by default and cancel immediately when the pendant privacy latch is active.
- **owner gets:** The owner can ask what is on the screen without turning every visual question into a cloud screenshot disclosure. It provides a genuinely private eyes-free bridge from the Mac display to the worn pendant.
- effort: Medium-high: local vision/OCR integration, window and secret redaction, consent state, pendant request/response framing, and adversarial privacy tests.  ·  risk: Redaction could miss sensitive content or describe a stale frame. Recover by refusing ambiguous frames, stating capture age, and requiring explicit opt-in for any raw-image fallback; the privacy latch cancels pending work.
- cost: Near-zero API cost on the local path; optional raw-image fallback would incur model charges only after explicit confirmation. Local CPU/GPU use is brief per request.  ·  latency: About 1–4 seconds per request depending on local vision model availability.
- security: Improves privacy by making raw screenshots non-exportable by default, but the redactor becomes security-critical and needs denial-on-uncertainty tests and an auditable digest.
- depends on: A local OCR/vision runtime on the Mac; A structured pendant visual-query envelope; A relay policy that rejects raw screenshot payloads unless explicitly authorized


## What it asked for

_Nothing._
