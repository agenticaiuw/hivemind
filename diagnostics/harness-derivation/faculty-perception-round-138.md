# Harness derivation — faculty-perception — round 138

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac observability** — At 2026-08-08T01:22:53Z, AI Pendant Agent com.aipendant.agent has Accessibility and Screen Recording trusted; input reachability is verified, synthesized events reach the screen, secure input is false, and automationMissing is empty. Relay is reachable and browser extension is online with 9 tabs and 0 pending commands.
  - evidence: GET /observe and GET /ops/snapshot returned HTTP 200 with accessibility.trusted=true, inputReachability.status=verified, screenRecording=true, relay.reachable=true, browserExtension.online=true, pendingCommands=0.
- **device registry and browser liveness** — Current device discovery shows Safari on MacIntel online (9 tabs), home-macbook-bridge online last seen 2026-08-08T01:22:46.727Z, and cloudflare-contract-test mobile offline since 2026-07-31. No nRF9160 pendant is present in the currently discoverable devices.
  - evidence: discover(category=devices) returned exactly those three items; GET /ops/snapshot relay payload also reports macBridgeOnline=true.

## Capabilities it proposed

### "Before you do anything, tell me what is actually visible and actionable right now—on my screen and in my authenticated browser—and separate observed facts, private content you withheld, and guesses."
- **useful because:** The system can now verify screen reachability and read authenticated Safari, but it does not provide one owner-facing perception answer. This prevents acting on stale tabs, hidden login walls, or model assumptions and makes the Mac/browser combination useful even without a pendant.
- **path:** mac-vision → browser-extension → mac-planner → relay-realtime → unified
- **model tier:** Use the cheap local perception path for screenshot/accessibility and browser metadata; reserve realtime only to phrase the short spoken answer. No background model is needed unless the owner asks for interpretation.
- **latency:** 2–5 seconds for a bounded screen/browser snapshot; under 1 second if only metadata is requested.
- **cost:** Near-zero API cost for Mac accessibility and extension reads; occasional vision inference dominates, roughly one low-cost image call per request.
- **security:** Screen and authenticated tabs may contain credentials, payment, health, or private messages. Redact sensitive regions before any relay/model upload; default to local-only observations and require explicit confirmation before exposing private text or taking action.
- **missing:** A first-class perception endpoint joining GET /observe, GET /browser/status, and typed browser inspection results with region-level redaction and confidence.; A stable schema distinguishing observed, withheld, stale, and inferred fields.; A relay voice tool that can request this bounded snapshot without copying full screen contents into conversation context.

### "What changed in this exact authenticated page since the last time you showed it to me? Show only the changed fields, say when each observation was captured, and tell me if the comparison is impossible."
- **useful because:** A one-shot, provenance-backed diff is more useful than rereading a whole page and safer than pretending a stale tab is current. It combines Safari's private session with the Mac evidence store while making missing history or changed tabs explicit.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → unified
- **model tier:** Local deterministic normalization and hashing first; use a cheaper text model only to summarize changed regions. Realtime is unnecessary except for a spoken result.
- **latency:** 1–3 seconds for an already-open tab; up to 5 seconds if a fresh authenticated read and local capsule are needed.
- **cost:** Usually no external API cost; a small summarization call is the dominant cost when changes are nontrivial.
- **security:** Keep page bodies and hashes on the Mac by default. Never send credentials, payment details, or redacted regions to the relay. Bind the comparison to tab/session and reject a URL-only match.
- **missing:** A mounted browser provenance route and a direct one-shot compare API over existing evidence capsules.; A capture call that always records tab/session generation and a normalized semantic hash for authenticated browser reads.; A spoken result formatter that reports unavailable baseline, revoked capsule, or tab mismatch instead of inventing a diff.

### "Why did that interaction fail? Reconstruct one causal timeline across my spoken request, relay job, Mac action, browser command, and (when present) pendant audio/health telemetry; label every gap instead of filling it in."
- **useful because:** Today each surface can show a fragment and several 'completed' states are not proof of delivery or hearing. A bounded incident replay would let the owner distinguish wrong target, stale browser, relay timeout, Mac refusal, lost audio, and genuinely unknown outcome.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified
- **model tier:** Deterministic event joins, timestamps, IDs, and status precedence should do almost all work; use a cheap summarizer for the final spoken explanation. Realtime is only needed if the owner asks during a live conversation.
- **latency:** Under 2 seconds for a recent job; up to 8 seconds when correlating browser and audio artifacts.
- **cost:** Negligible for joins; one short summarization call is the main API cost. Storage is bounded by retaining only event metadata and hashes, not page/audio bodies.
- **security:** Incident records can reveal private URLs and spoken content. Store redacted metadata and content hashes, enforce per-session authorization, and clearly distinguish relay-sent, Mac-executed, browser-observed, and pendant-played. Never claim heard without a device-originated playback event.
- **missing:** A canonical correlation envelope shared by voice turn, relay job, Mac job, browser command, and audio artifact.; A read-only incident endpoint that joins existing pipeline, job, browser, and permission records without scraping.; A pendant-originated health/playback event when hardware is eventually registered; current registry has no nRF9160 device.; Retention policy for incident metadata long enough to diagnose failures while deleting payload bodies. 

### "Show me a no-side-effect preview of what you are about to change: the exact app/tab, fields or files touched, expected visible result, permissions used, and the ways it could fail—then wait for my approval."
- **useful because:** The owner can currently approve an action in prose without seeing a grounded account of its actual target or blast radius. A cross-surface dry run would make computer use understandable before anything changes, especially when the active Safari tab or foreground app is not what the model assumed.
- **path:** mac-vision → browser-extension → mac-planner → relay-realtime → unified
- **model tier:** Use deterministic inspection and action manifests locally; use a cheap text model only to turn the manifest into plain language. Realtime is optional for speaking the preview.
- **latency:** 1–3 seconds for metadata and browser state; up to 5 seconds for an ambiguous UI target that needs vision.
- **cost:** Usually no external API cost; one small vision call is the dominant cost for visually ambiguous targets.
- **security:** The preview itself can expose private field values. Show labels, types, and redacted previews rather than secrets; keep raw screenshots local; require explicit confirmation bound to the exact manifest hash and target fingerprint.
- **missing:** A dry-run interpreter for every Mac/browser action that resolves concrete targets without mutating them.; A signed, human-readable action manifest with target fingerprint, touched-resource list, permission set, and manifest hash.; A confirmation protocol that expires when the foreground app, tab generation, or target fingerprint changes.

### "If my screen or browser is private, keep the answer off the pendant: tell me only that private content is present and put the useful detail in a local, redacted view I can open."
- **useful because:** A wearable speaker is an inherently public output channel. The owner needs the system to notice that Safari, Messages, Mail, payment, or a secure-input field is visible and automatically choose a private Mac surface rather than reading sensitive material aloud.
- **path:** pendant → mac-vision → browser-extension → mac-planner → relay-realtime → unified
- **model tier:** Local deterministic app/domain and accessibility-region classification; no model call for common sensitive apps. Use a small local classifier only for uncertain page regions, never relay raw content.
- **latency:** Under 200 ms for app and secure-input checks; under 1 second for a browser-region classification.
- **cost:** Near-zero API cost; small local implementation and a bounded redacted notification payload.
- **security:** False negatives could leak private content, so uncertain classification must fail closed. The relay must receive only a category and redacted summary; the local Mac view must require the owner's normal unlock. Do not persist screenshots.
- **missing:** A system-wide output policy that can select pendant speech versus local-only display per utterance.; Region-level sensitivity labels from Safari/accessibility and a conservative unknown state.; A local redacted notification or dashboard surface and a relay response type meaning 'withheld for privacy' rather than an empty answer.

### "Describe the controls and state around where my cursor is, without sending my screen away from the Mac, and let me ask follow-up questions about that exact view."
- **useful because:** The owner can wear the device and ask about an unfamiliar or changing interface, but today perception and conversation are separate and raw screen context is either unavailable or too private to share. A local accessibility-grounded view would provide useful spatial help without uploading a screenshot.
- **path:** mac-vision → mac-planner → relay-realtime → pendant → unified
- **model tier:** Local accessibility-tree extraction and geometry first; use a compact local vision model only when the tree lacks labels. Realtime should receive only the redacted structured scene and answer briefly.
- **latency:** Under 1 second for accessibility-only views; 2–4 seconds when local vision is required.
- **cost:** No relay/API cost for structured views; local vision inference is the main compute cost and can be rate-limited to explicit requests.
- **security:** Never transmit raw screen pixels by default. Exclude secure-input and sensitive regions, replace them with typed placeholders, and expire the scene after one conversational turn. Require confirmation before describing content from private apps.
- **missing:** A local scene representation with stable element IDs, bounds, roles, labels, and sensitivity classifications.; A cursor/active-element query and a short-lived scene token that binds follow-up questions to the same observed state.; A relay tool contract accepting only the redacted scene, not a screenshot or full accessibility tree.


## Changes it proposed to its own stack

### `interaction` — Add a perception firewall that runs immediately before every computer or browser mutation. It snapshots foreground app, secure-input state, input reachability, browser lease age, active tab identity, and a compact target fingerprint; if secure input is active, the browser lease is stale, or the target has changed, it pauses and reports the exact reason instead of clicking or typing. After execution it re-observes the target and records whether the intended postcondition is visible.
- **owner gets:** The owner gets fewer dangerous misfires: no typing into a password field during secure input, no action on a tab that changed while thinking, and a concrete explanation when the system refuses rather than silently doing the wrong thing.
- effort: Moderate: one preflight wrapper around mac_run_actions/browser execute plus a postcondition observer and typed refusal receipts; Accessibility and Screen Recording are now verified live, so this can be exercised today.  ·  risk: A stale or overly strict fingerprint could pause harmless work. Recover by offering a fresh re-observation and requiring explicit confirmation for a retry; never auto-retry a changed target.
- cost: Minimal; metadata reads are local. Vision/postcondition checks add a low-cost model call only for ambiguous UI states.  ·  latency: Adds about 100–400 ms for metadata and 1–3 s when vision is needed.
- security: Improves safety by keeping secure-input and sensitive-region checks local; postcondition snippets must be redacted before relay logging.
- depends on: GET /observe currently reports verified input reachability, secureInputActive=false, and screenRecording=true; GET /browser/status reports tab identity, lease age, and pending commands; browser command results need a normalized target fingerprint and postcondition field

### `integration` — Add a USB commissioning mode that turns the physically connected nRF9160 + ESP32 bridge into a temporary, explicitly labeled local pendant: the Mac agent discovers both serial identities, opens a local audio/control proxy, mints a least-privilege ephemeral relay credential, and exposes a visible 'USB test device' state with teardown on unplug. The mode must never masquerade as an LTE-registered pendant or reuse the admin relay key.
- **owner gets:** The owner can test the real worn-device audio and conversation loop today while the pendant is absent from the relay registry, and can immediately tell whether a failure is firmware/audio, Mac USB, or cloud delivery instead of relying on stale recorded telemetry.
- effort: High: serial discovery and lease management, firmware USB framing, relay credential/registration path, ESP32 audio routing, and a small status surface. It should be tested against the actual chips rather than simulated history.  ·  risk: A stale USB lease or wrong serial device could route audio to the wrong hardware. Require VID/PID and challenge-response identity, show the device name prominently, revoke the ephemeral credential on unplug/timeout, and keep LTE registration semantics separate.
- cost: No recurring API cost beyond normal relay traffic; modest engineering effort and potentially a USB serial framing/firmware update. No new hardware required.  ·  latency: Local audio/control should add under 100 ms; cloud voice latency remains unchanged.
- security: Improves security by eliminating admin-key reuse and limiting commissioning credentials to the Mac, device pair, and short lease. USB audio and transcripts remain local unless the owner starts a cloud session.
- depends on: A real serial-device discovery and health reader for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A relay endpoint for ephemeral nrf_pendant commissioning credentials with revoke/expiry; A firmware USB commissioning protocol and explicit local-device identity; A status/UI surface that distinguishes USB test mode from relay-online pendant state


## What it asked for

_Nothing._
## Its own summary

Established fresh live state: AI Pendant Agent now has Accessibility and Screen Recording, input reachability is verified, secure input is off, browser extension is online with 9 tabs and zero pending commands, relay and Mac bridge are reachable, and no nRF9160 pendant is registered. Proposed four owner-facing capabilities/changes: bounded observed-vs-withheld screen/browser briefing (most useful), a pre-mutation perception firewall with postcondition re-observation, authenticated-page one-shot diffs, and cross-node causal incident replay. Sent the verified preflight facts to faculty-action.

**Biggest unknown:** The granted read_continuity_snapshot tool still does not resolve to an implementation (resolver score below threshold); I can reach the nearest raw route GET /ops/snapshot, but there is still no single authenticated cross-surface continuity/incident read. A canonical correlation envelope and pendant-originated playback/health events remain missing, and the pendant itself is absent.

