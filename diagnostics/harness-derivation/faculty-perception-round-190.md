# Harness derivation — faculty-perception — round 190

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live perception state 2026-08-08** — The running Mac agent is now fully perception-capable: Accessibility and Screen Recording are trusted, permissions.ready=true, computer-use loop and vision model are enabled, and Safari browser bridge is online with 2 tabs (active tab DoorDash) and zero pending/spooled commands. Relay is reachable on D1, Mac bridge online; no pendant appears in live device inventory.
  - evidence: GET /ops/status and GET /browser/status returned HTTP 200 at 2026-08-08T22:32Z; both report accessibility.trusted=true, screenRecording.granted=true, ready=true, browser online, tabCount=2, pendingCommands=0, and relay reachable.

## Capabilities it proposed

### "“Is that actually done—and if not, what is the next thing I need to do?”"
- **useful because:** Today completion is split across Mac execution, browser command results, pipeline traces, and relay delivery; a green Mac job can still mean the browser never changed and a relay 'delivered' item can still mean nobody heard it. This gives the owner one verdict with explicit observed, stale, and unknown evidence instead of false certainty.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** Deterministic evidence join first; a cheap background model summarizes conflicts, with realtime only for the spoken one-sentence answer.
- **latency:** Under 2 seconds for existing IDs; up to 6 seconds for a cross-surface refresh.
- **cost:** <$0.01 per verdict; mostly local route calls, with model tokens dominating only when evidence is large.
- **security:** Return hashes, titles, statuses, and redacted snippets by default; never upload full page text or screenshots unless the owner explicitly asks. Treat browser content as untrusted. Any suggested retry or mutation requires confirmation.
- **missing:** A shared task identity linking Mac jobs, browser command IDs, pipeline IDs, and relay announcement IDs.; A canonical verdict schema with evidence age and confidence; current completion readers do not represent owner-heard playback.; A relay-side read-only join route or Mac-side joiner that can fetch all four records without inference.

### "“What was I looking at, what changed, and can you get me back to the exact page?”"
- **useful because:** The active Safari session is live now, but a URL alone cannot prove what the owner saw or whether a page changed. A local screenshot/DOM observation, content hash, and browser-session join let the pendant give a trustworthy spoken handoff and reopen the same tab without inventing page state.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-action
- **model tier:** Local deterministic capture and hashing; a small text model extracts a short spoken description. Realtime is used only when the owner asks; no expensive model for passive capture.
- **latency:** Initial answer 2–4 seconds; reopen under 1 second after the capsule is selected.
- **cost:** Near-zero when local; <$0.01 when summarization is needed. Storage is bounded by the existing capsule limits.
- **security:** Redact passwords, payment data, and secret locators before persistence; keep screenshots local, hash redacted content, and require confirmation before reopening or acting on a sensitive page. Login-wall content must be labeled unverified.
- **missing:** Mount the existing browserProvenance routes and connect browser-extension results to evidence capsules on every read.; A stable correlation ID from relay read_web_page when the cloud browser is used.; A user-visible 'observed at' timestamp and stale badge in voice responses.

### "“Watch this page and tell me only when something meaningful changes.”"
- **useful because:** A real browser session can remain open while a price, delivery estimate, appointment slot, or order status changes. The owner should receive one concise, evidence-backed alert rather than repeatedly checking or trusting a stale cached page; the alert must say exactly what changed and when it was observed.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Local DOM/text diff and rules for detection; a cheap background model classifies significance. Realtime is reserved for delivering the alert over the voice channel.
- **latency:** Polling every 30–120 seconds depending on site limits; alert within one poll cycle, spoken in under 2 seconds after detection.
- **cost:** Usually <$0.02/day per watch; browser polling and local hashing dominate, not model inference.
- **security:** Watch definitions are explicit and scoped to one tab/URL/region; never persist full pages by default. Pause on logout or login-wall detection, rate-limit polling, and require confirmation before any follow-up purchase, booking, or message.
- **missing:** A durable watch store with selector, baseline capsule hash, cadence, quiet hours, and expiration.; A browser-extension heartbeat/watch executor that can survive the Mac agent restarting.; A relay announcement dedupe key based on watch ID plus new content hash, and a UI to stop watches.

### "“Before you submit anything important, prove that the page I’m seeing is the page you’re about to act on—and stop if the screenshot, browser state, or destination disagree.”"
- **useful because:** A browser DOM can be manipulated, a screenshot can be stale, and a logged-in tab can silently navigate between perception and action. The owner needs a cross-surface pre-action safety proof, not merely a confirmation dialog: Mac vision, the browser session, and the relay must agree on the same tab, origin, target region, and current content before an irreversible click or form submission.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic origin/tab/region/content-hash comparison first; a cheap model handles only semantic target matching. Realtime is used solely to explain a mismatch to the owner.
- **latency:** 1–3 seconds for a preflight; hard stop immediately on disagreement.
- **cost:** Usually <$0.01 per preflight; local screenshot and DOM hashing dominate, with model use only for ambiguous target semantics.
- **security:** Never expose credentials or full page contents to the relay. Treat every page and DOM string as untrusted. Require explicit owner confirmation for purchases, messages, deletion, or permission changes; retain only redacted hashes and the decision receipt.
- **missing:** A single preflight object binding browser command ID, tab/window identity, URL origin, screenshot hash, DOM/region hash, and intended action.; A browser-extension response that returns a fresh screenshot and DOM snapshot atomically rather than as separately timed observations.; A faculty-action gate that refuses execution when any hash, origin, focus, or freshness check fails, plus a durable owner-readable mismatch explanation.


## Changes it proposed to its own stack

### `context` — Install a provenance-and-freshness gate at the context projection boundary: machine-derived preferences (especially timezone) cannot enter the high-confidence Owner block merely because their kind is 'preference'. Every projected fact gets source origin, observedAt, expiry policy, and a conflict marker; machine facts that contradict live /machine-context are demoted to a diagnostic section until explicitly confirmed by the owner. The gate should also attach an evidence timestamp to browser and Mac state claims.
- **owner gets:** The owner stops hearing confidently wrong persistent facts such as the pinned machine-written America/Chicago timezone, and spoken answers can say “observed 12 seconds ago” versus relying on stale memory. This prevents wrong actions before they happen.
- effort: Medium: projection filter, conflict tests against /machine-context, migration for existing pinned machine facts, and dashboard badges.  ·  risk: A legitimate machine fact may be demoted and make an answer less convenient; recover by showing the conflict and offering one-tap confirmation. Never silently delete owner-origin facts.
- cost: Negligible API cost; a few local reads per projection and small metadata overhead.  ·  latency: 10–50 ms locally; no model latency if implemented as deterministic filtering.
- security: Improves privacy by keeping sensitive browser evidence out of generic context unless explicitly linked; provenance metadata remains local.
- depends on: A reliable source.origin field on every memory fact; GET /machine-context and GET /memory/projection; A write path for the owner to confirm or correct a conflicted fact

### `interaction` — Add a two-phase perceptual commit protocol for consequential browser actions. Phase 1 captures an atomic browser-extension snapshot and a Mac screenshot, creates a redacted content-addressed preflight record, and asks faculty-judgement to compare intended target, origin, focus, and freshness. Phase 2 permits faculty-action to execute only against that exact snapshot nonce; any navigation, tab switch, DOM mutation, or timeout invalidates the nonce and forces a new observation. The pendant voice response should name the specific failed invariant instead of saying generic 'I couldn't do that'.
- **owner gets:** The owner gets protection against acting on a page that changed underneath them or against a visually convincing but semantically different control, while routine low-risk actions remain fast and automatic.
- effort: High: atomic browser snapshot protocol, nonce invalidation in the extension, screenshot/DOM comparison, action-gate integration, and dashboard receipts.  ·  risk: Over-blocking on harmless dynamic pages could be annoying; recover with a low-risk policy mode and a clear one-phrase confirmation. Never allow bypass for destructive or financial actions.
- cost: Small local storage and hashing cost; occasional semantic comparison model call, under $0.02 for ambiguous preflights.  ·  latency: Adds 1–3 seconds before consequential actions; no effect on ordinary reads.
- security: Strongly reduces confused-deputy and stale-page risk; hashes and redacted regions leave the Mac, while raw screenshots remain local.
- depends on: A browser extension API for atomic screenshot+DOM capture; Stable evidence capsule and browser provenance linkage; A faculty-action execution gate that accepts and enforces a preflight nonce


## What it asked for

_Nothing._
## Its own summary

Fresh live discovery changed the picture: the exact AI Pendant Agent now has Accessibility and Screen Recording, permissions.ready=true, vision loop enabled, and Safari bridge online on a live DoorDash tab; relay is reachable on D1 and Mac bridge is online, while no pendant is registered. I recorded this as verified. I proposed three owner-facing capabilities (cross-surface truthful task verdict, exact browser handoff with evidence, and meaningful-change watches) plus a context-layer provenance gate to stop stale machine facts poisoning prompts. The recorder flagged the first and third as close to existing ideas, so their genuinely new value is the explicit cross-surface evidence join and the missing watch executor/dedupe contract—not the generic wording.

**Biggest unknown:** The pendant path remains unobservable: no registered nRF9160, no device heartbeat, and no device-originated playback confirmation. I still need a real cross-surface correlation contract (one task/artifact ID joining Mac job, browser command, pipeline, relay delivery, and evidence capsule), a relay browser-read ID/hash bridge into the existing Mac capsule store, and the firmware/relay playback event that distinguishes bytes sent from audio actually heard. I also need an inventory/implementation decision for the newly possible Accessibility-backed passive observation, with privacy and owner confirmation boundaries.

