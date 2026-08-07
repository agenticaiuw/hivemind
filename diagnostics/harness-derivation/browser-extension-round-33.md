# Harness derivation — browser-extension — round 33

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser availability** — Safari is not currently online; only stale home-chrome is registered, with no tab and lastSeenAt 2026-08-07T09:21:08.821Z. There are 2 pending browser commands, and recent navigate jobs each consumed ~45 seconds before failing offline.
  - evidence: GET /browser/status returned online=false, home-chrome tabId=null/tabCount=null/online=false/pendingCommands=2; GET /jobs showed two browser_navigate failures with durations 45334ms and 45373ms.

## Capabilities it proposed

### "“I’m looking at this private webpage—read the important part, explain the chart or form, and tell me what I should do next.”"
- **useful because:** The browser is the only node that can see the owner’s authenticated Safari page, while the pendant is the only always-present conversational surface. Combining DOM/selection text with a screenshot lets the system explain logged-in dashboards, charts, and confusing forms without asking the owner to copy or expose content. It remains read-only and can cite the exact page and region.
- **path:** browser-extension captures the active tab URL/title, selected text, relevant DOM, and screenshot, preserving tab/session provenance → mac-vision interprets visual-only content such as charts, icons, and layout → relay-realtime gives the low-latency spoken explanation through the pendant → unified/mac-planner keeps a short-lived task capsule so a follow-up like “fill the first field” refers to the same page; browser stops before submission
- **model tier:** Realtime for intent resolution and concise spoken response; route screenshot/chart interpretation to the vision-capable tier only when DOM text is insufficient. No background model is needed for the immediate answer.
- **latency:** 2–5 seconds for text-only pages; 5–10 seconds when a screenshot must be interpreted. Capture should fail fast with a clear offline/tab-closed report rather than waiting 45 seconds.
- **cost:** Typically $0.01–$0.05 per interaction, dominated by vision tokens and retransmitting the screenshot; text-only explanations are much cheaper. Keep the screenshot and DOM capsule ephemeral and send only the active region where possible.
- **security:** Authenticated page text, URL, and pixels leave Safari for the relay/model, so redact passwords, payment fields, tokens, and hidden inputs before upload. Never infer or expose secrets from the DOM. Read-only by default; filling or submitting requires a separate explicit owner request, and submission remains outside this capability.
- **missing:** An implemented browser command enqueue path (the granted wrappers still return implementation errors); Active-tab/selection capture with screenshot clipping and secret-field redaction; A short-lived cross-surface page capsule with provenance and expiry; A fast browser health/preflight signal so an offline extension is reported immediately rather than after the 45-second bridge timeout

### "“Build me a private evidence packet for this problem.”"
- **useful because:** When an order, bill, booking, or account decision is wrong, the owner should not have to manually collect screenshots, timestamps, policy text, and reference numbers from several logged-in pages. The browser can access the private records, the Mac can preserve an auditable local packet, the relay can reconcile the facts, and the pendant can give a concise spoken summary. This is an evidence-preservation workflow, not another page briefing or form-fill feature.
- **path:** browser-extension reads the relevant authenticated pages and captures only explicitly selected regions, URLs, timestamps, reference numbers, and policy passages → mac-planner creates an encrypted local case folder containing immutable source captures plus a machine-readable index and human-readable chronology → mac-vision checks screenshots for missing visual evidence and associates each item with its page region → relay-realtime reconciles contradictions, identifies missing facts, and reports the packet contents through the pendant → unified exposes the packet later for review or export; it never sends it to a merchant, insurer, employer, or agency automatically
- **model tier:** Use a cheaper background model for extraction, normalization, chronology, and contradiction checks. Use realtime only for the owner’s spoken request and final concise explanation; use vision selectively for screenshots that contain information unavailable in DOM text.
- **latency:** Initial capture and indexing: 15–60 seconds depending on page count. Spoken acknowledgement should arrive within 2 seconds, with a completion notification when the packet is ready. Review and export are interactive but need not be realtime.
- **cost:** Roughly $0.03–$0.20 per packet, dominated by screenshot OCR/vision and model processing across several pages. Local storage should hold originals so they are not repeatedly retransmitted.
- **security:** Packets may contain highly sensitive financial, medical, travel, or employment data. Keep originals encrypted on the Mac, use per-case retention and deletion, redact credentials, cookies, hidden inputs, and unrelated account data, and show a manifest before any export. Nothing is uploaded to a third party or submitted as a complaint without a separate owner action.
- **missing:** A browser capture API that can collect selected authenticated pages with stable provenance and redaction; An encrypted, content-addressed local evidence store with retention/deletion controls; Cross-surface case identifiers so browser captures, Mac files, vision findings, and pendant summaries refer to one case; A background extraction/chronology worker and a review/export surface that displays the evidence manifest before sharing


## Changes it proposed to its own stack

### `browser-harness` — Add a browser availability lease and event stream: each real extension heartbeat publishes deviceId, tabCount, active-tab metadata, lastSeenAt, and a monotonically increasing lease expiry; the bridge exposes a cheap readiness check and emits online/offline/stale transitions. POST /execute must consult the lease before enqueueing browser work, fail in a few hundred milliseconds with the specific device/last-seen state when stale, and attach the lease version to queued commands. Relay/mac-planner can then queue private work for the next online transition while routing public URLs elsewhere. Do not remove the existing unrestricted execution policy; this is observability, fast failure, and resumption, not a gate.
- **owner gets:** A spoken request will stop failing mysteriously after 45 seconds. The owner immediately hears “Safari bridge is offline; your private task is queued” and the task can resume when Safari returns, while public research still completes through the relay. It prevents duplicate commands and makes the browser feel dependable rather than intermittently broken.
- effort: Moderate: extend browserBridge.js and status persistence, add transition notifications and a small queued-job resumer, then have relay/mac-planner consume the contract. Requires an extension heartbeat field for lease version and an integration test covering Safari sleep/wake.  ·  risk: Clock skew or missed heartbeats could mark Safari stale while it is usable, or resume a command against a changed tab. Recover by requiring a fresh heartbeat and revalidating tab/session affinity before each step; stale queued read jobs can be retried, while mutation jobs remain paused and are never duplicated. No approval gate is introduced.
- cost: Negligible API cost; a few D1/R2 heartbeat writes and event records. Avoid storing page content in the health stream.  ·  latency: Offline detection drops from ~45 seconds to under 1 second; online work adds one local lease read (tens of milliseconds). Resume latency depends on the extension polling interval.
- security: Store only device/session metadata, not URLs where they could reveal sensitive accounts unless already permitted; hash or classify private origins. Lease tokens prevent old queued commands from targeting a replaced tab.
- depends on: A functioning browser enqueue/result path (currently the granted browser wrappers are still stubs); Extension heartbeat/reporting of a lease version and active-tab identity; The Mac-planner preflight/recovery work should consume this signal rather than implement a second health check


## What it asked for

_Nothing._
