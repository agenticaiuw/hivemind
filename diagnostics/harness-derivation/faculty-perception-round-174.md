# Harness derivation — faculty-perception — round 174

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac observability and permissions** — At 2026-08-08T03:26Z, /ops/status and /ops/snapshot report AI Pendant Agent ready=true with Accessibility and Screen Recording granted, all listed automation grants present, browser extension online on Safari x.com tab 1163292 (9 tabs), relay reachable with D1 store and macBridgeOnline=true. Vision loop is enabled/configured but visionUploadConsented=false.
  - evidence: GET /ops/status and GET /ops/snapshot returned HTTP 200; payload fields permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser.online=true, computerUse.loopEnabled=true, visionUploadConsented=false.

## Capabilities it proposed

### "“I’m stuck—look at my Mac and tell me exactly what is blocking me, then fix it if it’s safe.”"
- **useful because:** Now that the exact agent binary has Accessibility and Screen Recording, the system can ground a spoken diagnosis in the live screen instead of guessing from app names or stale job state. It combines a worn voice request, relay continuity, Mac visual control, and browser sessions; it should state the observed blocker and show a before/after result.
- **path:** pendant → relay-realtime → mac-vision → mac-planner → browser-extension
- **model tier:** Realtime for the short spoken exchange; local Mac vision/planner for screenshots and action selection; no cloud vision upload unless the owner explicitly consents (currently visionUploadConsented=false).
- **latency:** 3–8 seconds to inspect; up to 20 seconds for one reversible fix, with spoken progress if longer.
- **cost:** Low API cost when vision stays local; dominant cost is one or two local screenshots and planner turns. Cloud cost only if the owner opts into upload.
- **security:** Screen contents may include secrets. Keep frames on the Mac by default, redact password fields, require confirmation before submit/send/delete/purchase, and return only a concise spoken diagnosis to the pendant.
- **missing:** A hard policy that routes screenshots to the local vision model and refuses cloud upload when visionUploadConsented=false; A compact before/after visual receipt linked to the Mac action ledger

### "“Check whether that web action actually worked, and tell me what the page proves—not what you expected.”"
- **useful because:** Relay job completion currently can mean only that the Mac acted, while browser state and owner-visible outcome can differ. This capability compares the authenticated browser session after execution with the intended change, reports observed evidence or an explicit unknown, and prevents false spoken confirmations.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Cheaper background model for receipt comparison; realtime only to answer the owner’s question. Use local browser inspection first and local vision only when DOM evidence is insufficient.
- **latency:** 2–6 seconds after a job; immediate status if a receipt already contains a browser result.
- **cost:** Usually near-zero model cost for structured browser inspection; occasional local vision inference dominates. No relay web-search call needed.
- **security:** Never read or speak secret form values. Preserve URL/title/locator and a redacted content hash, not raw page text. Confirmation is required for any retry or mutation.
- **missing:** A post-action verification hook that automatically runs browser inspection for browser jobs; A result state distinct from completed: verified, contradicted, or unknown, joined to the action ledger

### "“What on my screen needs my attention right now? Give me the one best next step.”"
- **useful because:** This is a genuinely new wearable-to-desktop affordance: the pendant supplies intent while the Mac sees all open apps and the authenticated browser sees the current session. It turns a noisy desktop into one grounded, prioritized answer without taking action, useful when the owner is away from keyboard or cannot remember which window matters.
- **path:** pendant → relay-realtime → mac-vision → browser-extension → mac-planner
- **model tier:** Local Mac vision plus a cheap local prioritizer; realtime synthesizes one short spoken response. Do not send screenshots to the relay unless explicitly enabled.
- **latency:** 4–10 seconds for a scan of the active display and browser tab; no more than one spoken turn.
- **cost:** Mostly local CPU/model inference; zero external API cost by default. Cost scales with number of displays/windows scanned, so start with active display and active browser tab.
- **security:** Treat screen content as private. Ignore password managers and secure text fields, redact notifications containing likely secrets, retain no screenshots, and ask before opening or changing anything.
- **missing:** A local-only screen triage endpoint that returns ranked attention candidates with source rectangles and confidence; A cross-surface policy for excluding sensitive apps and honoring the owner’s quiet hours

### "“When I say ‘that thing I was looking at,’ reconstruct exactly which screen, browser tab, and voice turn I mean, then show me the evidence without rereading private content aloud.”"
- **useful because:** Today the Mac, browser, relay, and wearable each know fragments of context, but there is no owner-addressable visual referent that survives a turn. This would let the owner point backward naturally—from a pendant utterance or vague phrase—to one grounded moment, even after switching apps, while exposing uncertainty instead of inventing a match. It is a new memory primitive for a wearable mind, not another task runner.
- **path:** pendant → relay-realtime → mac-vision → mac-planner → browser-extension
- **model tier:** Cheap local embedding/indexing for screen and DOM landmarks; realtime only resolves the owner’s short deictic query. Never send raw frames to the relay by default.
- **latency:** Under 2 seconds for the common case; up to 6 seconds when ranking several recent moments.
- **cost:** Low recurring API cost if indexing and matching stay on the Mac; storage and local vision inference dominate.
- **security:** Raw screenshots, page text, and secrets must remain local and expire quickly. Store only redacted thumbnails or hashes, app/tab identity, bounded regions, and confidence. Require confirmation before revealing sensitive matches or taking action.
- **missing:** A local ephemeral visual-reference index keyed to voice-turn/session IDs, browser tab identity, redacted region hashes, and timestamps; A relay protocol carrying a deictic query and candidate confidence without exporting the underlying screen content; An owner-controlled retention and purge policy for visual references

### "“Before you do anything sensitive, tell me which account, website, and visible destination you are actually about to use—and let me approve it from the pendant.”"
- **useful because:** A browser session can be authenticated yet still be the wrong account, tab, tenant, or destination. This capability makes the wearable a human-readable authorization boundary: Mac vision and the extension inspect the visible origin and account label, the relay speaks a compact risk summary, and only an explicit pendant confirmation releases the action. It protects against the most damaging class of ‘the action succeeded, but in the wrong place’ failures.
- **path:** pendant → relay-realtime → mac-vision → browser-extension → mac-planner
- **model tier:** Local deterministic checks for origin, account labels, destination fields, and action scope; realtime only renders the summary and receives confirmation. No cloud vision required.
- **latency:** 1–3 seconds for the preflight; confirmation window remains open for 30 seconds.
- **cost:** Negligible API cost; local DOM inspection and optional screenshot OCR are the dominant work.
- **security:** Do not speak full account identifiers, payment data, or secret values; use masked labels and origin registrable domains. Treat visible text as untrusted. Require a fresh, one-time confirmation bound to a hash of the exact planned action and tab.
- **missing:** A cryptographically bound pendant confirmation token for a specific browser action and tab state; A policy engine classifying sensitive actions and extracting masked account/destination facts from DOM plus local vision; A browser-side commit gate that refuses execution when the page hash or tab changes after approval


## Changes it proposed to its own stack

### `mac-harness` — Make the newly-ready Mac agent automatically run a local-only visual preflight before any computer-use action: confirm Accessibility and Screen Recording readiness, capture a redacted before frame, execute only the planned reversible step, capture an after frame, and attach an observed outcome plus confidence to the existing action ledger and relay job receipt. If visionUploadConsented is false, never upload frames.
- **owner gets:** The owner gets honest answers grounded in what actually appeared on screen, and can hear “I could not verify it” instead of a confident but wrong completion.
- effort: Medium: wire /ops/status permission state, local vision loop, action ledger, and job receipts; no new device hardware.  ·  risk: Visual misinterpretation could cause a wrong reversible action; mitigate with allowlists, confirmation for irreversible actions, and fail-closed when confidence is low. Recover by using the existing undo/receipt path.
- cost: Near-zero API cost in local-only mode; local CPU and two screenshot inferences per action.  ·  latency: Adds roughly 1–4 seconds per action.
- security: Improves privacy by enforcing the already-observed visionUploadConsented=false state and redacting sensitive fields; screen data stays on the Mac.
- depends on: Local vision loop must honor visionUploadConsented=false; A result-verification field in the existing action ledger/job receipt

### `context` — Add a privacy-aware perception firewall shared by Mac vision and the browser extension. It should classify tabs/windows into owner-approved visual zones (for example: ordinary, private, financial, credentials), attach a signed sensitivity label to each observation, and make every screenshot/OCR/visual-reference request fail closed for disallowed zones while still permitting narrowly scoped DOM metadata or high-level action checks.
- **owner gets:** The owner can finally use screen-grounded AI without choosing between total blindness and exposing an entire desktop. They can ask for help while banking, messaging, or using passwords, confident that forbidden surfaces are not being captured or remembered.
- effort: High: needs a shared policy format, browser extension enforcement, local capture interception, audit receipts, and a recovery UX when a task crosses zones.  ·  risk: Misclassification could either leak sensitive pixels or block legitimate help. Recover with an unmistakable blocked response, per-site owner overrides, short-lived approvals, and no automatic fallback to cloud vision.
- cost: Small local CPU/storage cost for classification and receipts; no additional API cost if all perception stays on-device.  ·  latency: Adds under 200 ms to normal capture; policy re-evaluation on navigation may add up to a second.
- security: Strongly improves privacy: the relay receives only a policy result and redacted metadata, never blocked pixels or page bodies. Policy changes themselves should require explicit owner confirmation.
- depends on: Local-only visual preflight and the visual-reference index proposed above; Browser extension access to a signed, per-tab sensitivity label; A capture interception point before mac-vision or any future cloud vision upload


## What it asked for

_Nothing._
## Its own summary

Established live truth this round: the exact AI Pendant Agent binary is now Accessibility- and Screen-Recording-ready; all listed automation permissions are granted, Safari’s browser bridge is online on x.com with 9 tabs, the relay is reachable on D1, and the local vision loop is configured but visionUploadConsented=false. I recorded that finding. I proposed three owner-facing cross-surface capabilities (screen-grounded safe recovery, post-action proof rather than assumed completion, and one prioritized attention item) plus a concrete local-only before/after verification change. I do not need another TCC permission grant. The continuity tool grant is unusable as resolved: its call fails because the resolver cannot match it, while the nearest real route GET /ops/snapshot works directly.

**Biggest unknown:** The pendant itself is still not registered or observable; no claim about wearable delivery or hearing is justified. The system still needs either (1) the continuity tool’s resolver mapped to GET /ops/snapshot plus pipeline/relay joins, and (2) an actual pendant registration/heartbeat before pendant-side reality can be established. Separately, cloud visual inspection requires an explicit owner choice because visionUploadConsented remains false.

