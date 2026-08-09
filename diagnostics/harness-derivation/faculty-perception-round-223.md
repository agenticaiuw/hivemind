# Harness derivation — faculty-perception — round 223

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live_mac_and_browser_continuity** — At 2026-08-09T00:42:43Z the live Mac snapshot reports Accessibility and Screen Recording granted for AI Pendant Agent, permissions.ready=true, browser extension online with 5 Safari tabs and 0 pending commands, active tab DoorDash Newark menu, relay reachable with D1 store and mac bridge online, but no pendant device is present in the returned registry context.
  - evidence: read_continuity_snapshot include relay,pipeline invoked GET /ops/snapshot HTTP 200; response body status.permissions and browser/relay payload.

## Capabilities it proposed

### "When you read something from the web for me, show me exactly which page and passage you relied on, and warn me if it changed or cannot be verified."
- **useful because:** Voice web answers currently lose their origin on the relay path. This gives the owner traceable answers: URL, capture time, content hash, a short redacted excerpt, and whether the browser session or relay fetched it. It makes a spoken answer auditable rather than persuasive.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Use deterministic hashing, redaction, and capsule linking; use a cheaper text model only to select a concise spoken citation. Realtime is used only for the live answer.
- **latency:** Add 300-800 ms to a web answer when a capsule is already available; up to 2 seconds to mint and persist one after a relay fetch.
- **cost:** Usually <$0.002 per citation; storage and hashing dominate, not model tokens.
- **security:** Do not persist raw page text by default; redact credentials, tokens, and private fields before hashing/storing. Logged-in browser pages require an explicit owner policy. Relay-fetched text must not be retained indefinitely in announcements.
- **missing:** Relay response fields for stable read ID, source URL, capture timestamp, and content hash; A Mac call that mints the existing evidence capsule from relay output; Mounting the existing browserProvenance routes; Expiry/deletion enforcement for relay announcement text

### "While I am away, tell me only what actually changed in my open browser and Mac work, what is still pending, and what needs my decision."
- **useful because:** The live snapshot now proves the browser and Mac are online, but it is a truncated export and does not produce a causal change report. A perceptual diff would turn five tabs, jobs, receipts, pipeline traces, and UI changes into a short actionable handoff without pretending that 'completed' means heard or seen.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic event/diff engine for URLs, titles, accessibility labels, job states, receipts, and pipeline stages; cheap summarizer only for the final spoken digest.
- **latency:** Generate incrementally in the background; first spoken handoff under 2 seconds after reconnection, with no need to re-scan every source synchronously.
- **cost:** <$0.005 per digest in normal use; background polling and bounded local storage dominate.
- **security:** Store only redacted metadata and hashes by default, never page bodies or typed values. Mark every item as observed, inferred, or unknown; never claim a Mac-completed job was played on a pendant. Ask before exposing private tab titles aloud.
- **missing:** A persistent cross-surface cursor/watermark rather than count-capped source reads; Mac UI/browser snapshot diff records with redaction; A spoken-digest policy (quiet hours, urgency, private-tab handling); A real pendant online/played signal when hardware is deployed

### "After you click or type, prove the real-world result—not just that the command ran—and tell me exactly what postcondition you observed."
- **useful because:** A browser command receipt or Mac job completion is not the same as a submitted order, sent message, saved setting, or changed document. This gives the owner a perception-backed outcome: before/after observation, target identity, timestamp, and an explicit unknown when the external effect cannot be witnessed.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay → dashboard
- **model tier:** Deterministic postcondition checks first (URL/state/accessibility labels, browser result, job receipt); use the cheap model only to map a declared goal to observable postconditions. Realtime explains the result in a live turn.
- **latency:** 1-3 seconds after a reversible action; up to 10 seconds for a site that needs polling. Stop after a bounded retry window and report unknown.
- **cost:** <$0.005 normally; polling and an occasional vision comparison dominate. No expensive model call when a declared selector/state check is sufficient.
- **security:** Never infer success from a toast alone for payments, messages, or destructive actions. Do not capture secret fields in before/after evidence. Require confirmation if the postcondition indicates an irreversible side effect or a recipient mismatch.
- **missing:** A goal-to-postcondition contract attached to each action plan; A browser result schema that includes stable target, before/after state, and observation timestamp; Mac-vision accessibility/screenshot diff records joined to action ledger steps; Relay-side outcome receipt that preserves the observation without page contents

### "Tell me when something stored as my preference contradicts authoritative machine evidence, and show me the exact fact and provenance before suggesting a correction."
- **useful because:** The system currently injects machine-written preferences as if they were owner intent. A stale, high-confidence timezone preference can silently distort every routine and projection. The owner should be warned without the system silently rewriting personal memory.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Deterministic provenance and conflict comparison; use a cheap model only to phrase the conflict. Realtime is sufficient for a spoken warning.
- **latency:** Under 300 ms during context assembly; no separate user-visible wait.
- **cost:** Pennies or less per conflict check; comparison and bounded projection reads dominate, not inference.
- **security:** Expose only the conflicting fact, source origin, confidence, and affected uses. Never delete or rewrite a personal fact automatically. Require owner confirmation for correction.
- **missing:** A conflict detector comparing projected facts with authoritative machine/context sources; A provenance-aware context gate that prevents machine-origin facts from being labeled owner intent; A review route with affected-use previews and explicit accept/reject

### "Before you speak aloud, check whether the current browser or Mac context is private; if it is, summarize safely, switch to a discreet channel, or ask me to confirm."
- **useful because:** A wearable speaker can expose a page title, message, order, medical detail, or account state to people nearby. The system currently knows the browser tab and has speech output, but does not make the privacy decision at the boundary where text becomes sound.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Local deterministic classifiers for app/site sensitivity, visible labels, login/payment fields, and owner-declared privacy zones; use realtime only to answer a confirmation question. Do not send page bodies to a model for ordinary checks.
- **latency:** Under 200 ms for normal speech gating; under 1 second when a screenshot or accessibility tree is needed.
- **cost:** Near-zero for local rules; occasional vision classification under $0.01. The dominant cost is a one-time owner policy setup.
- **security:** Classification should happen locally and retain only a sensitivity label. Never log the private text used for classification. Confirmation must be required for high-risk content, and silence must be the safe fallback if the pendant state is unknown.
- **missing:** A shared sensitivity taxonomy and owner-configurable privacy zones; A speech-output policy gate integrated before TTS/audio enqueue; A discreet output path such as haptic/display or Mac-only notification; Private-tab and sensitive-field signals from the browser extension

### "When I use words like “this morning,” “near me,” or “my timezone,” tell me which clock, location, and provenance you are applying—and stop if the request needs my physical location rather than the Mac's."
- **useful because:** The system has an authoritative Mac timezone but no pendant timezone or owner-location signal, while machine-derived preferences can disagree with the Mac. This prevents silently converting a local machine fact into a claim about where the owner is or what they intend.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic scope and provenance resolver; use realtime only when the owner must answer an ambiguity. No model call when the request is explicitly Mac-local.
- **latency:** Under 100 ms for explicit Mac-local requests; ask one concise clarification when physical location or owner timezone is required.
- **cost:** Negligible; the main cost is one extra conversational turn when location scope is genuinely unknown.
- **security:** Do not infer location from IP, browser tabs, or stale memory. Treat the Mac timezone as authoritative only for Mac-resolved operations. Physical location and owner timezone require explicit owner input or a trusted device signal.
- **missing:** A typed distinction among machine-local time, owner timezone, and physical location in intent/context schemas; A provenance rule preventing machine facts from satisfying owner-location questions; An explicit owner timezone/location preference flow with expiry and revocation


## What it asked for

_Nothing._
