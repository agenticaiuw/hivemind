# Harness derivation — faculty-perception — round 148

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac input reachability** — At 2026-08-08T02:00:16Z the running AI Pendant Agent (com.aipendant.agent, exact bundle and node path) has Accessibility and Screen Recording granted; inputReachability.status=verified, eventsPost=true, secureInput=false, uiActionsWillReachTheScreen=true.
  - evidence: GET /observe HTTP 200; accessibility trusted=true, screenRecording=true, inputReachability verified at 01:54:26Z.
- **live cross-surface state** — At 2026-08-08T02:00Z Mac bridge and browser extension are online, browser has 9 Safari tabs and 0 pending commands; relay reachable with D1 store; no pendant appears in the live devices inventory.
  - evidence: GET /ops/status and GET /browser/status HTTP 200; devices discovery lists home-macbook-bridge online, cloudflare-contract-test offline, and no nRF pendant.
- **continuity snapshot availability** — The granted read_continuity_snapshot tool is not callable in this live run: resolver returned unresolved (best match GET /ops/snapshot score 0.447), despite /ops/snapshot itself returning HTTP 200. Cross-surface continuity must currently use direct authenticated probes, not the promised single snapshot tool.
  - evidence: read_continuity_snapshot call error in round 148; parallel GET /ops/snapshot and GET /ops/status both HTTP 200.

## Capabilities it proposed

### "Before you tell me what a webpage says, have the cloud reader and my logged-in browser independently check it, and tell me if they disagree."
- **useful because:** The relay can read public pages but has no session, while Safari can see logged-in or personalized state. Comparing two independent observations catches stale pages, login walls, personalization, and relay/browser disagreement instead of presenting one unverified reading as fact.
- **path:** relay-realtime → browser-extension → mac-planner → faculty-perception
- **model tier:** Use a cheap background/text model to normalize and compare page claims; reserve realtime for the one-sentence spoken verdict.
- **latency:** 3–8 seconds for two reads and hash/claim comparison; speak immediately only when both observations agree, otherwise report disagreement.
- **cost:** About $0.01–$0.05 per check depending on page length; browser and relay reads dominate latency, not model tokens.
- **security:** Logged-in browser content must stay on the Mac and never be uploaded to the relay; send only a redacted claim set and hashes. Require confirmation before using a disputed page to drive an action.
- **missing:** relay read_web_page must return a stable content hash and request ID; browser read result must expose a comparable hash plus session/tab provenance; a Mac-side comparator and spoken verdict schema

### "What is my computer actually doing right now, and is anything waiting on me?"
- **useful because:** A live, evidence-labeled spoken status would combine the foreground app, current browser tab, pending browser commands, Mac jobs, relay reachability, and permission state without pretending that a completed job means the owner heard it. It answers the everyday uncertainty that no individual surface can answer honestly.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception
- **model tier:** A cheap deterministic aggregator should produce the facts and confidence labels; realtime only verbalizes the short answer.
- **latency:** Under 500 ms from the Mac and browser, up to 2 seconds if relay job state is needed.
- **cost:** Near-zero model cost for the normal case; one short realtime turn only when spoken through the pendant.
- **security:** Do not include page contents, secrets, or private app names beyond what the owner requested. Mark browser state as observed, Mac job state as reported, and pendant playback as unknown.
- **missing:** a resolved continuity snapshot endpoint/tool (the granted read_continuity_snapshot currently fails resolution); a single typed schema for foreground, browser, jobs, relay, and permission freshness; a policy for what counts as 'waiting on me' rather than merely pending

### "Let me press the pendant once to give you a private one-minute window into my screen, then explain or fix what I am looking at without leaving the window open."
- **useful because:** Screen Recording is now verified for the exact agent binary, but vision upload consent is still false. A physical, time-limited consent gesture would let the owner get real visual help at the moment they need it while making the privacy boundary tangible and automatic.
- **path:** pendant → mac-vision → browser-extension → relay-realtime → faculty-perception
- **model tier:** Realtime vision-language model during the short consent window; no background screen sampling and no model call when the window is closed.
- **latency:** Button-to-first-frame under 1 second; 60-second lease with an on-device countdown and hard expiry.
- **cost:** Roughly $0.02–$0.15 per minute depending on screenshot rate and vision model; screen capture and upload dominate cost.
- **security:** Never upload frames without a fresh physical gesture; show an LED/haptic countdown, redact password fields and secure-input windows, bind the lease to one conversation, and require a second confirmation for destructive actions. Frames must be discarded at expiry.
- **missing:** pendant firmware gesture and lease-expiry indicator (the pendant is not registered today, so hardware verification waits); Mac capture broker that enforces the lease and redacts secure-input regions before upload; relay session token scoped to one visual lease; vision upload consent currently false in /ops/status must become a per-lease signal

### "Before you use a logged-in page, tell me exactly what private data it exposes to you and let me approve only the smallest useful slice."
- **useful because:** Today the browser bridge can reach authenticated tabs, while relay models and Mac automation have different trust boundaries. The owner cannot inspect or approve the boundary at the moment of use. A wearable approval lets them safely ask for help with mail, orders, or accounts without granting a broad session dump.
- **path:** pendant → browser-extension → mac-vision → relay-realtime → faculty-perception → faculty-action
- **model tier:** A deterministic local classifier identifies fields and sensitivity; realtime gives the short spoken preview; no cloud model receives content before approval.
- **latency:** Preview in under 1 second; approval expires after 30 seconds or one action.
- **cost:** Near-zero for local classification; under $0.01 for an approved short summary, with no cost for rejected requests.
- **security:** Default deny. Redact passwords, payment details, tokens, and message bodies; bind approval to exact tab, locator, and one action; log only hashes and sensitivity classes; require a second physical gesture for sending, purchasing, or deletion.
- **missing:** a browser-side field/region sensitivity classifier; a pendant-originated scoped approval token with expiry; a Mac-to-relay policy gate that enforces the approved selector rather than trusting model text; a spoken preview format that never quotes secret values

### "When I return to my Mac, show me only what materially changed while I was away—across browser tabs, files, scheduled work, and relay messages—and group each change by what I need to do."
- **useful because:** Existing logs are split by surface and their retention semantics differ, so the owner cannot get a bounded, deduplicated change report that distinguishes an observed change from an unfinished action. This would turn absence into a useful, privacy-preserving return brief rather than a noisy history dump.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Use deterministic diffs, fingerprints, and status joins first; use a cheaper text model only to cluster and phrase changes; realtime only for the spoken digest.
- **latency:** Precompute during idle; first spoken result under 2 seconds after the owner asks.
- **cost:** Small local CPU/storage cost; roughly $0.01 per digest for clustering, dominated by optional text summarization.
- **security:** Keep page bodies and file contents on the Mac; send only redacted titles, hashes, timestamps, and action states. Respect per-source retention and explicitly label unknown coverage when a source was offline.
- **missing:** a durable monotonic handoff watermark shared by relay, Mac, and browser; content-aware but local diffing for browser regions and files; a return-brief joiner that separates changed, completed, failed, and untouched items; a pendant trigger that marks the owner's departure/return without guessing location

### "Give me a physical privacy mode: when I double-press the pendant, cut the microphone and all screen/browser observation everywhere, and tell me when every surface is actually quiet."
- **useful because:** Software indicators are not enough when the owner is wearing an always-available assistant. A hardware-triggered kill state would stop capture at the source, revoke Mac vision and browser reads, cancel queued observations, and provide a verifiable all-surfaces privacy boundary rather than a promise from one process.
- **path:** pendant → mac-vision → browser-extension → relay-realtime → mac-planner → faculty-perception
- **model tier:** No model is needed to enforce the kill state; use deterministic state propagation and a short realtime acknowledgment only after every surface reports quiescent.
- **latency:** Pendant microphone cutoff immediately; Mac/browser/relay revocation and spoken confirmation within 1 second, or explicitly report which surface did not confirm.
- **cost:** Negligible per use; modest firmware and protocol work, with no inference cost.
- **security:** The pendant must enforce mic disable locally even when offline. The relay must reject new audio and observation leases; Mac must stop screen capture and browser polling; queued frames must be deleted. Recovery should require a deliberate physical gesture, and the owner must be warned if any node is unreachable rather than told privacy is active globally.
- **missing:** a firmware-local privacy latch and visible/haptic state; a signed revocation broadcast understood by relay, Mac vision, and browser extension; per-surface quiescence acknowledgments and a timeout state; a startup default that preserves the latch across reconnect and reboot


## What it asked for

_Nothing._
## Its own summary

Established fresh live facts: the exact AI Pendant Agent binary now has Accessibility and Screen Recording, input reachability is verified, browser extension and Mac bridge are online, relay is reachable on D1, and no pendant is registered. Proposed three owner-facing capabilities: two-witness webpage truth checks (cloud reader vs logged-in browser), a live evidence-labeled 'what is my computer doing?' answer, and a physical one-minute pendant consent lease for private screen help. The granted continuity snapshot tool remains unresolved even though /ops/snapshot works directly, so I recorded that defect and notified faculty-action of the verified action preconditions.

**Biggest unknown:** There is still no live nRF9160 pendant to verify any device-originated playback or physical consent behavior; the next concrete dependency is resolving the continuity-snapshot tool or exposing its schema under the actual /ops/snapshot route.

