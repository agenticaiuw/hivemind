# Harness derivation — faculty-perception — round 235

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-permissions-and-surfaces** — At 2026-08-09T01:43Z the authenticated continuity snapshot reports the exact AI Pendant Agent host fingerprint com.aipendant.agent with Accessibility and Screen Recording granted, requiredMissing/optionalMissing empty, ready=true; browser extension online on Safari with one DoorDash tab and zero pending commands; relay reachable with D1 store and Mac bridge online. No pendant appears in the live device list (only Mac bridge and offline mobile remain established).
  - evidence: read_continuity_snapshot include relay,pipeline returned HTTP 200 /ops/snapshot; body status.permissions and browser/relay payload.

## Capabilities it proposed

### "Before you place an order, send a message, or change a setting, tell me exactly what page or app you are looking at, whether it is fresh, and show me the evidence you used."
- **useful because:** The system can currently act on a stale tab or an untraceable relay browser read. This would turn perception into a hard, owner-visible reality fence: browser session, Mac UI, and relay results must agree before an irreversible action proceeds.
- **path:** browser-extension → mac-vision → mac-planner → relay → dashboard
- **model tier:** Use the cheap background/text tier for URL/content hashing and agreement checks; reserve realtime only for the owner's spoken question and the final concise warning.
- **latency:** 1–3 seconds for browser/Mac snapshots and hashing; if they disagree, stop rather than spend model time guessing.
- **cost:** Usually <$0.01 in text/model cost; dominant cost is one browser snapshot plus optional Mac screenshot/vision step.
- **security:** Evidence must redact secrets and form values, reuse the existing capsule redaction, and never expose page text to the relay unnecessarily. Irreversible actions require explicit confirmation when freshness, URL, login state, or source agreement fails.
- **missing:** A relay read must return a stable request/content hash and a Mac call must mint the existing evidence capsule; the existing relay browser path currently returns neither.; Mount the existing browserProvenance routes and attach the existing capsule/claim links to the action ledger.; A policy gate that blocks mac_run_actions/browser actions when the evidence is stale or cross-surface disagreement is unresolved.

### "Can you actually do this right now, or are you only able to see it? Give me a reachability answer for the pendant, Mac, browser, relay, and the specific action I asked for before you promise anything."
- **useful because:** The live system currently reports a browser heartbeat as online while its capabilities array is empty, and a relay registry that omits the pendant by design. A simple online/offline answer is therefore misleading. This gives the owner a per-surface distinction between observed, readable, writable, and postcondition-verifiable.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** No realtime reasoning for the matrix: deterministic checks and a small text model summarize it; realtime only speaks the result in an ongoing conversation.
- **latency:** Under 500 ms for registry/permission/heartbeat checks, up to 2 seconds if a harmless probe is needed; never execute the requested side effect as a probe.
- **cost:** Near-zero model cost; the work is authenticated GETs and existing capability metadata. A deliberate harmless probe may cost one Mac/browser round trip.
- **security:** Do not infer pendant absence from registry absence alone; mark it unknown unless the device beacon or an explicit live registry check supports it. Never probe by clicking, typing, or sending. Treat browser URL/title as sensitive and return only the minimum needed.
- **missing:** A normalized read-only reachability contract that reports observed/read/write/verified-postcondition separately rather than one online boolean.; The browser heartbeat currently needs to publish actionable capability types, not only online and tab metadata.; A pendant branch backed by the accepted offline-reality-beacon when a pendant exists; today it must honestly say no live pendant evidence.

### "When did that happen? Give me a time I can trust, and tell me which clock and timezone it came from if the Mac, browser, relay, and pendant disagree."
- **useful because:** The Mac has an authoritative America/New_York clock, while the pendant has zoneless digits and no NITZ/GNSS, browser and relay timestamps have their own transport delays, and stored machine facts include a contradictory pinned timezone. Without provenance, the system can confidently misdate reminders, captures, and actions.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic timestamp normalization and skew bounds first; use a cheap text model only to phrase the uncertainty. Realtime is unnecessary unless answering in the live voice turn.
- **latency:** Under 200 ms for existing timestamps; up to 1 second to gather a fresh multi-surface sample. If no shared instant can be established, return unknown rather than estimate.
- **cost:** Negligible model cost; dominated by one authenticated snapshot and optional browser/Mac freshness reads.
- **security:** Do not export raw device identifiers or location assumptions. America/New_York is authoritative only for events resolved on this Mac, not for the owner's physical location. A pendant timestamp without captured timezone must remain zoneless/unknown.
- **missing:** A shared event envelope carrying source clock, capture instant, monotonic sequence, receivedAt, and explicit timezone/uncertainty.; Firmware beacon already supplies monotonic time but needs a relay/Mac correlation handshake; the relay must preserve source timestamps rather than rewriting them.; A presentation layer that labels machine-local time versus device/owner time and refuses silent conversion.

### "Show me exactly what would change if you carried this out, without carrying it out. Include the messages, fields, tabs, files, and side effects you predict, then wait for my approval."
- **useful because:** Today the system can plan and sometimes execute across Mac and browser, but it cannot give the owner a faithful, cross-surface dry run. A reversible action list is not enough when a browser click may submit an order or an AppleScript may alter several records. The owner needs a concrete before/after shadow they can inspect.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a slower, inexpensive planning model to construct the shadow diff; use realtime only to collect the request and read back a short approval summary.
- **latency:** 2–8 seconds for a multi-surface dry run. Never silently execute while generating the preview; approval should be a separate explicit turn/button press.
- **cost:** Typically $0.01–$0.05 for complex plans; browser/Mac inspection and diff generation dominate, not speech.
- **security:** The preview must mark estimates versus observed values, redact credentials and sensitive fields, and refuse to claim a postcondition it cannot verify. Approval must bind to a hash of the exact preview so a changed page or plan cannot be approved accidentally.
- **missing:** A side-effect-free shadow executor for every Mac/browser action type, with structured before/after diffs rather than prose.; A cross-surface plan hash and expiry: invalidate approval when the tab, app state, evidence capsule, or target changes.; A dashboard/pendant rendering of the diff that is legible in a few spoken sentences and supports explicit approve/cancel.

### "For the next ten minutes, let me point you at things on my screen and answer questions about them, but do not retain the screen contents after the session—even if the relay or browser goes offline."
- **useful because:** The owner currently has to choose between useful visual help and broad, unclear persistence. This would make perception a bounded consent session: the pendant starts and ends it, the Mac/browser enforce the scope, and relay buffering cannot turn a temporary glance into durable memory.
- **path:** pendant → mac-vision → browser-extension → relay → dashboard
- **model tier:** Use the realtime tier only for the live conversational session; use no background model after expiry. Redaction and deletion should be deterministic, not delegated to a model.
- **latency:** Under 1 second to confirm session state; normal visual-answer latency thereafter. Expiry and revocation should take effect locally even during a relay outage.
- **cost:** Incremental cost is one vision request per owner question, usually $0.01–$0.05; the hard part is enforcement and deletion, not inference.
- **security:** This must be fail-closed: no screenshots, capsules, snippets, browser claims, relay announcements, or prompt caches survive the deadline. A local revocation tombstone may remain as metadata, but never the body. The pendant should provide an unmistakable active indicator and a physical cancel path.
- **missing:** A consent-session token propagated from pendant/Mac to browser and relay, with monotonic expiry and revocation that works offline.; A no-retain storage class enforced by evidence capsules, browser provenance, pipeline traces, model context, relay queues, and audio capture—not merely a UI promise.; A deletion receipt proving each surface discarded the body, without returning the body itself.

### "What exact words did you hear me say, and which words actually caused the action? If the pendant audio, transcript, and Mac/browser action do not match, stop and ask me to correct it."
- **useful because:** A successful action can still be based on a misheard name, amount, date, or recipient. The pendant knows capture quality, the relay has the transcript, and the Mac/browser has the concrete action, but today there is no owner-visible alignment showing how one caused the other. This catches the most dangerous perception error before it becomes an external commitment.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic sequence and field alignment first; a cheap text model can explain one mismatch. Realtime handles only the live correction conversation, not archival analysis.
- **latency:** Under 1 second for a normal low-risk command; up to 3 seconds before a send/order/payment action. A mismatch blocks execution until corrected.
- **cost:** Usually under $0.02 per command; the main cost is one transcript/intent alignment call and, only on uncertainty, a repeat capture.
- **security:** Do not retain raw audio by default. Keep only bounded hashes, quality metrics, transcript spans, and action-field mappings; redact names/payment details in dashboard views. Never infer that a clear capture means the transcription is correct.
- **missing:** A shared utterance sequence ID and immutable mapping from audio-quality verdict to relay transcript to Mac/browser action ledger step.; A field-level alignment result (recipient, amount, date, target) with a strict mismatch policy before execution.; A pendant correction interaction that can request a repeat locally while offline, then reconcile the corrected sequence after reconnect.


## Changes it proposed to its own stack

### `model-routing` — When /ops/status reports permissions.ready=true and browser extension online, route ambiguous visual requests to the Mac vision loop instead of declaring the surface inaccessible; require a read-only screenshot/DOM observation first, then pass the resulting evidence capsule to judgement and action. If the browser capability list is empty, keep browser writes disabled even though the heartbeat is online.
- **owner gets:** The owner now has Accessibility and Screen Recording granted, so the system can genuinely inspect the Mac UI. This turns previously blocked visual questions into answers while preventing an online-but-non-actionable browser bridge from being mistaken for control.
- effort: Small routing/policy change plus one integration test covering permissions ready, browser online with empty capabilities, and a stale screenshot.  ·  risk: A screenshot can contain secrets or the wrong app; enforce redaction, active-window/URL checks, and confirmation before writes. Recover by falling back to AppleScript/read-only browser inspection and saying unknown.
- cost: One vision call only for genuinely ambiguous visual tasks; otherwise zero additional model cost.  ·  latency: Adds roughly 1–3 seconds only when visual ambiguity exists.
- security: Screen content leaves the Mac only through the existing consented vision path; do not upload captures when a DOM or AppleScript read suffices.
- depends on: Existing granted Accessibility and Screen Recording permissions; Existing GET /ops/status or GET /ops/snapshot permission state; Existing mac-vision loop and browser inspection routes; Evidence capsule redaction before judgement/action


## What it asked for

_Nothing._
## Its own summary

Discovered and recorded a fresh live fact: the exact AI Pendant Agent now has Accessibility and Screen Recording granted and reports permissions.ready=true; Safari browser heartbeat is online but advertises zero capabilities; relay is reachable with D1 and Mac bridge online; no live pendant evidence is present. Proposed three owner-facing perception capabilities: cross-surface evidence/freshness fence before actions, a per-surface observed/read/write/postcondition reachability answer, and clock/time provenance that refuses silent conversion across Mac/browser/relay/pendant clocks. Also proposed routing visual ambiguity through the now-authorized Mac vision loop while keeping browser writes disabled when capabilities=[]; informed faculty-judgement.

**Biggest unknown:** The pendant remains genuinely unobserved: no registry/heartbeat/beacon evidence exists, so I cannot establish whether firmware is physically present or what its current offline state is. The next missing contract is not another diagnostic read but a live device-originated beacon correlation and a browser capability publication; until then, online status must not be treated as ability or proof.

