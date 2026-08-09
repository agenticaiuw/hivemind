# Harness derivation — faculty-perception — round 177

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac reachability and privacy-relevant state** — At 2026-08-08T04:44Z, the AI Pendant Agent has verified Accessibility and Screen Recording, inputReachability.status=verified, secureInputActive=false, and automationMissing=[]; Safari is foreground. The browser extension is online with 2 tabs and zero pending commands. Relay is reachable and D1-backed; no pendant is registered in the live device table.
  - evidence: GET /ops/status returned permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browserExtension.online=true, relay.reachable=true and relay store=d1; GET /observe returned foregroundApp Safari, inputReachability verified, secureInput false, and browser sessions.

## Capabilities it proposed

### "“Before you do anything, tell me whether I’m on the right page and what would actually happen if I said yes.”"
- **useful because:** The owner gets a grounded, human-readable pre-action reality check: current foreground app and screen state from the Mac, the exact active browser tab and DOM target from Safari, and the relay's interpretation of the requested action. It prevents acting on a stale tab, wrong account, or a page that only looks right. The answer explicitly separates observed facts from inferred intent and refuses to claim a pendant confirmation when none exists.
- **path:** pendant → relay-realtime → mac-vision → browser-extension → mac-planner → faculty-perception
- **model tier:** Realtime for the short spoken confirmation; use the cheaper Mac/browser observation and deterministic target extraction first, invoking the expensive model only to reconcile ambiguous labels.
- **latency:** 2–4 seconds for normal pages; up to 8 seconds if a screenshot and DOM reconciliation are both needed.
- **cost:** Usually <$0.01: one short realtime turn plus local observation; browser and Mac reads dominate latency, not tokens.
- **security:** Read-only by default. URLs, page text, and screenshots leave the Mac only when the owner asks for relay interpretation; secrets and form values must be redacted. Any actual click, type, submit, or external side effect requires a second explicit confirmation.
- **missing:** A single perception join record that correlates /observe, browser inspection, and the proposed action to one short-lived check ID; A relay voice intent that can request the Mac/browser observations without executing the action; A redaction policy for screenshots and DOM values before relay transmission

### "“Keep me private right now, and tell me if anything you’re about to send would expose what’s on this screen.”"
- **useful because:** The owner gets a live privacy boundary rather than a vague promise: it detects sensitive foreground apps, secure-input fields, private browser tabs, and screen-recording state on the Mac, then reports exactly which proposed relay/browser/action payloads would cross the boundary. It can let harmless local actions proceed while blocking or redacting cloud-bound observations. This is especially valuable because the system can currently see the screen and the browser extension is online, while the relay is reachable and the pendant is absent.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Deterministic local classifiers and route metadata first; use the realtime model only to explain the resulting redaction decision in speech. No background expensive model is needed.
- **latency:** Under 300 ms for a local privacy check; under 2 seconds when a browser DOM classification is required.
- **cost:** Near-zero API cost for local checks; optional short realtime explanation is <$0.005.
- **security:** The privacy service must run on the Mac before any screenshot, DOM, or transcript is sent to relay. Fail closed when classification is uncertain, never upload raw secrets for classification, and require an explicit owner override for a sensitive payload. Privacy decisions themselves should retain only a short-lived hash and reason, not page contents.
- **missing:** A local preflight middleware that intercepts every screenshot, browser read, and relay tool payload; A shared sensitivity taxonomy across Mac foreground apps, browser locators, and relay tool arguments; A pendant-visible privacy state indicator that works offline

### "“Watch this exact page and only tell me when the meaning changes—not when a timestamp, ad, or layout changes—and show me what changed.”"
- **useful because:** This turns the browser plus always-awake relay into a useful personal sentinel: it can monitor a logged-in page the Mac extension can reach, ignore cosmetic churn, detect a material change, and speak a short alert through the wearable. The owner gets a before/after explanation tied to the exact tab and region instead of unreliable keyword alerts. If the browser, Mac, relay, or pendant is unavailable, the alert says which leg is missing rather than pretending it was delivered.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → faculty-perception → faculty-judgement
- **model tier:** Cheaper background model or deterministic hashes for polling and boilerplate removal; invoke the realtime tier only to summarize a confirmed semantic diff for speech.
- **latency:** Polling cadence owner-selected (1–15 minutes); confirmed change summarized within 10 seconds, subject to browser session and relay availability.
- **cost:** Low: local DOM extraction and hashes dominate; one short summary call only on material changes, typically <$0.01 per alert.
- **security:** The monitor must be opt-in per URL/region, preserve session credentials in the browser only, redact secrets before any cloud comparison, and store content-addressed snapshots with bounded retention. The owner must confirm monitors that can trigger external actions; this capability only observes and announces.
- **missing:** A durable watch record containing tab/session/region, extraction rules, and last semantic snapshot; A local boilerplate-resistant diff/classification worker with secret redaction; A relay-to-pendant alert path that carries watch ID, changed region, and delivery uncertainty

### "“Read the sensitive number I’m looking at, but never let the page, screenshot, or account identity leave this Mac.”"
- **useful because:** The owner could ask for a private value from a logged-in browser page and receive only the minimal answer through the pendant. The browser extension would locate and normalize the value locally; the Mac would enforce that raw DOM, screenshots, credentials, and URL stay local; the relay would receive only a blinded request or redacted result for conversation routing; the pendant would speak the result. Today the system can either read pages or send context, but cannot guarantee this end-to-end minimization.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant → faculty-perception → faculty-action
- **model tier:** Local deterministic extraction and redaction first; use a small background model locally for ambiguous labels. Realtime handles only the short spoken response and never receives the source page.
- **latency:** 2–5 seconds for a structured value; up to 10 seconds for an ambiguous page.
- **cost:** Usually under $0.01, dominated by local browser inspection; no cloud vision or page-text model call for clear fields.
- **security:** The local extractor must fail closed on ambiguity, keep credentials and raw page content on the Mac, prevent relay logs and announcements from storing the value, and require confirmation for account-changing actions. A compromised browser extension remains in scope and needs an attested local channel.
- **missing:** A local-only extraction/redaction protocol with typed value classes and confidence; A relay contract that accepts only a redacted answer token, not source content; A pendant conversation mode that marks the response as private and suppresses durable transcript/announcement storage; A browser-extension attestation or integrity signal

### "“If the network or relay disappears while I’m talking, keep the conversation coherent and finish it when the connection returns.”"
- **useful because:** The owner would get a real interruption-tolerant conversation instead of a silent gap or a duplicate command. The pendant would retain a bounded, encrypted turn journal and local audio-quality verdicts; the Mac would continue locally when reachable over USB, queue only idempotent work, and reconcile sequence numbers after reconnect; the relay would resume from the last acknowledged turn rather than replaying speech or actions. This works across the pendant, Mac, and relay and is impossible today because the pendant is not registered and there is no end-to-end turn sequence/resumption contract.
- **path:** pendant → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime only for the live turn; a cheaper background reconciler handles queued transcripts, duplicate suppression, and replay after reconnection.
- **latency:** Local fallback response under 1 second when USB/Mac is available; reconnect reconciliation within 5 seconds; no more than one spoken replay per turn.
- **cost:** Low cloud cost: retransmit only missing turns and summarize queued work with a small model. Hardware firmware and protocol work dominate.
- **security:** The turn journal must be encrypted and bounded, with explicit expiry; queued commands need idempotency keys and must never execute automatically after an ambiguous disconnect. Audio and transcripts must not spill to the relay until consent and link integrity are restored.
- **missing:** A monotonic end-to-end turn/command sequence protocol shared by firmware, Mac bridge, and relay; Encrypted pendant NVS ring storage for turn metadata and bounded transcript fragments; A USB-local pendant-to-Mac transport and Mac-side offline conversation executor; Relay resume/deduplication semantics keyed by turn ID

### "“Tell me, before I rely on you, whether every part of this answer is current, where it came from, and what could have changed since you checked.”"
- **useful because:** The owner would receive a spoken freshness certificate, not just an answer: each claim would carry its observation time, source surface, session/tab identity, and a bounded volatility class. The Mac and browser would capture volatile facts locally; the relay would combine only the claim summaries; the pendant would speak both the answer and its uncertainty. It would expose stale browser tabs, disconnected devices, and cached Mac state before they become a wrong action. No current route creates this cross-surface claim-level freshness contract.
- **path:** faculty-perception → browser-extension → mac-planner → relay-realtime → pendant → faculty-judgement
- **model tier:** Deterministic timestamps, source/session joins, and volatility rules first; use a small model to cluster claims and explain conflicts. Realtime is only for the concise spoken certificate.
- **latency:** Under 3 seconds for existing observations; up to 8 seconds when a fresh browser or Mac read is required.
- **cost:** Typically under $0.01; fresh observation calls and optional local extraction dominate, with model use limited to claim clustering.
- **security:** Do not expose page contents merely to produce freshness metadata. Keep source URLs and account identifiers local unless needed; sign claim envelopes; distinguish observed, inferred, and user-provided facts; never treat a relay socket write as pendant hearing.
- **missing:** A claim-level envelope with source, observation time, freshness deadline, and uncertainty class; A local joiner for browser, Mac, relay, and device observations with signed monotonic sequence numbers; A spoken rendering policy that cannot collapse unknown into false certainty; A durable but privacy-minimized cache of claim metadata


## What it asked for

_Nothing._
