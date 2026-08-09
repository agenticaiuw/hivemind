# Harness derivation — faculty-perception — round 233

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser permissions and continuity** — At 2026-08-09T01:13Z, the Mac local agent reports accessibility.trusted=true, screenRecording.granted=true, requiredMissing=[] and ready=true. Browser extension is online in Safari on discord.com with 6 tabs and zero pending commands. Relay is reachable and Mac bridge online. No pendant is present in the live device list.
  - evidence: read_continuity_snapshot include relay,pipeline resolved GET /ops/snapshot HTTP 200; payload status.permissions and status.browser; discover(devices) lists only home-macbook-bridge, cloudflare-contract-test, and Safari browser.

## Capabilities it proposed

### "“Look at what is on my screen right now, tell me what matters, and if I say ‘do it,’ carry out the next safe step and show me exactly what changed.”"
- **useful because:** This turns the newly working Accessibility/Screen Recording grants into a dependable wearable-to-screen loop: the owner can ask while away from the keyboard, get a grounded answer about the active Safari/app state, and approve a reversible action without guessing what the agent saw. Every answer and mutation is tied to a screenshot/content hash and an action receipt instead of a model claim.
- **path:** pendant (voice request and spoken confirmation when connected) → relay-realtime (low-latency intent and confirmation) → mac-vision (screen capture and visual grounding) → browser-extension (DOM/tab inspection when the target is Safari) → mac-planner (reversible action and receipt) → dashboard (before/after evidence)
- **model tier:** Realtime for the short voice exchange; a cheaper background model for screen summarization and deciding whether DOM evidence or pixels are required. No expensive model for receipt formatting.
- **latency:** Initial answer 2–4 s; reversible action 1–3 s after explicit approval; never auto-submit/send/purchase. Accessibility and Screen Recording are now live, so this is testable today on the active Safari tab.
- **cost:** Roughly $0.01–$0.08 per interaction, dominated by vision tokens and any realtime audio; DOM-only browser inspection is materially cheaper than a screenshot.
- **security:** Screens may contain secrets; redact passwords/payment fields before persistence and keep evidence capsules local. Require explicit confirmation for send/delete/purchase/account changes. A stale screenshot must be rejected rather than acted on.
- **missing:** A shared correlation contract that attaches the existing local evidence capsule/content hash to the relay voice turn and the Mac action ledger; A mounted browser-provenance route so grounded claims are visible to the dashboard; A policy gate that classifies actions as reversible versus confirmation-required

### "“Watch this browser tab for a meaningful change—price, deadline, reply, or availability—and tell me only when the change is real, with the old and new evidence.”"
- **useful because:** The owner can delegate slow monitoring without leaving a page open mentally. The extension sees authenticated Safari state, the Mac stores a redacted before/after capsule, and the relay can notify the wearable even while the Mac is unattended. A semantic diff plus source hash prevents noisy ‘page changed’ alerts and lets the owner verify what triggered the interruption.
- **path:** browser-extension (authenticated tab observation and bounded snapshots) → mac-planner (scheduled watcher, local redaction, semantic diff) → relay (durable notification while the Mac is idle) → pendant (spoken alert and optional acknowledgement when connected) → dashboard (old/new evidence and watch health)
- **model tier:** Cheap background model only when a hash/DOM diff crosses a threshold; deterministic selectors, hashes, and numeric extraction handle the common path. Realtime is used only to explain an alert if the owner asks by voice.
- **latency:** Polling every 5–15 minutes according to the owner’s policy; alert within one poll. Setup under 5 s. No need for a low-latency model during monitoring.
- **cost:** Usually near-zero model cost; occasional semantic diff costs roughly $0.001–$0.01 per changed page, dominated by rendered text length.
- **security:** Never persist full authenticated pages by default; redact secrets and cap evidence. Watch definitions must be scoped to a tab/origin and revocable. Require confirmation before following links or changing a site. If the browser goes offline, report unknown rather than claiming no change.
- **missing:** A durable watcher scheduler and lease keyed to extensionId/tabId so two workers cannot duplicate alerts; A relay-to-local evidence bridge carrying capsuleId and contentHash; the existing Mac capsule schema should be reused; A semantic assertion schema (what counts as meaningful) with explicit owner confirmation at setup

### "“When I’m on a sensitive site or discussing something private, automatically keep the relay and browser evidence local, and tell me when a request would leave the Mac.”"
- **useful because:** The owner should not have to remember which surface can see a logged-in tab. A local policy can recognize configured sensitive origins/apps (banking, health, private messages), block cloud model uploads and durable relay announcements, and give a short spoken warning before an exception. This makes the wearable safe to use in the exact moments where its convenience is most valuable.
- **path:** browser-extension (origin/tab sensitivity signal and local redaction) → mac-vision (active-window/app classification, now that Screen Recording is granted) → mac-planner (local policy enforcement and audit receipt) → relay-realtime (receives only an allow/deny envelope unless explicitly overridden) → pendant (local warning/confirmation when connected) → dashboard (policy state and blocked-transfer audit)
- **model tier:** Deterministic local rules first; a small local model for ambiguous app/window classification. Realtime is used only after the local gate permits content to leave the Mac.
- **latency:** Under 100 ms for origin/window policy checks; under 500 ms for a warning. The gate must fail closed if policy state is unavailable.
- **cost:** Near-zero API cost for normal checks; occasional local classification has no API charge. Any cloud call requires explicit override and costs the ordinary voice-turn amount.
- **security:** The policy engine itself must not upload the sensitive URL/title or screenshot. Store only a hashed origin and decision metadata. Explicit overrides should expire after one turn, be spoken back, and be visible in the audit log. A fail-open bug would defeat the feature, so test relay/network failures and extension reconnects.
- **missing:** A local preflight gate that all browser captures, voice forwarding, and relay announcements must pass; An owner-editable sensitivity policy with safe defaults and an emergency ‘local only’ button; A redacted, append-only decision receipt that proves what was blocked without retaining private content

### "“Before I send this message or submit this form, check it for secrets, personal data, and unintended commitments; tell me exactly what you found and let me approve a redacted version.”"
- **useful because:** The owner gets a final, wearable-accessible safety check at the point of no return. It combines the authenticated browser session with local screen/DOM perception and does not require trusting a cloud model with the draft. It can catch API keys, account numbers, private names, dates, prices, and language that accidentally commits the owner before a send or submit.
- **path:** pendant (voice request and spoken approval) → browser-extension (inspect the actual draft and perform only the approved edit/submit) → mac-vision (verify the visible target and detect non-DOM content) → mac-planner (local deterministic scanner, diff, and action receipt) → relay-realtime (short-lived intent routing only) → dashboard (redaction diff and submission receipt)
- **model tier:** Deterministic local scanners and structured-field rules first; a small local classifier for ambiguous commitment language. Realtime handles only the concise explanation and approval exchange. Never send the draft to a background cloud model by default.
- **latency:** 300–800 ms for ordinary text, up to 2 s for a long form. Submission remains blocked until the owner explicitly approves the exact redacted diff.
- **cost:** Near-zero API cost for local scanning; occasional local model inference only. Cloud cost is limited to the normal short voice turn if the owner asks for an explanation.
- **security:** The scanner must not persist raw drafts or secrets; retain only redaction categories and hashes. Fail closed if the browser target changes after inspection. Treat ‘send’, ‘submit’, ‘publish’, and ‘reply’ as confirmation-required even when the content appears safe. Never let the relay receive the secret-bearing draft unless the owner explicitly overrides local-only mode.
- **missing:** A browser pre-submit interception hook that can pause a real form/send operation before the site consumes it; A local sensitive-data and commitment-language scanner with test fixtures and false-positive controls; A transaction token binding the inspected DOM/content hash to the one permitted browser mutation, expiring within seconds

### "“Watch what I’m about to paste and stop me if it would move a secret or private record into the wrong app.”"
- **useful because:** Clipboard mistakes are cross-surface failures: the browser may hold an authenticated destination, the Mac knows the source app, and the wearable is the only practical place to warn while the owner is moving quickly. A local guard can identify secrets and destination risk without uploading clipboard contents, then allow a one-shot paste only after explicit confirmation.
- **path:** mac-planner (clipboard provenance, local classification, and enforcement) → mac-vision (active destination app/window verification) → browser-extension (destination origin and focused field) → pendant (spoken warning and one-shot approval) → relay-realtime (optional intent transport, receiving only a risk code) → dashboard (blocked/allowed paste receipts without content)
- **model tier:** Local deterministic classifiers for credentials, financial identifiers, and destination allowlists; a small local model only for ambiguous text. Realtime is unnecessary unless the owner asks why a paste was blocked.
- **latency:** Under 100 ms on each clipboard/focus transition; approval must expire within 10 seconds or when the destination changes.
- **cost:** No routine API cost; local scanning is bounded to clipboard size and can be capped at 64 KB.
- **security:** Never send clipboard contents to relay or persist them. The guard must fail closed when focus cannot be identified, and it must distinguish a trusted local vault from an untrusted web form. Emergency bypass should be visible, one-shot, and logged only as a category/hash.
- **missing:** A low-level clipboard/focus interception service in the Mac agent; A destination risk policy mapping apps, origins, and fields to allowed data classes; A transaction-bound paste action that verifies the same destination is still focused

### "“Show me everything this system has sent off my Mac recently, what source it came from, and let me revoke any still-live copy.”"
- **useful because:** Today the owner cannot reliably answer what page text, voice, screenshot, or browser claim crossed into the relay, nor connect it to a later announcement or action. A tamper-evident outbound ledger would make the system auditable: source capsule, destination, purpose, redaction class, timestamp, and retention state. Revocation would propagate to local evidence and relay-held artifacts where deletion is possible, and clearly mark immutable receipts where it is not.
- **path:** mac-planner (single outbound interception point and local ledger) → browser-extension (source tab/capsule linkage) → relay (receipt, retention, and revocation status) → relay-realtime (explain a specific transfer on voice request) → pendant (short spoken privacy report) → dashboard (timeline, filters, and revoke controls)
- **model tier:** No expensive model for ledgering or revocation. Use deterministic joins and hashes; a cheap summarizer can turn a selected set of records into plain language.
- **latency:** Under 20 ms added to each outbound request by queueing metadata locally; a report in 1–2 s; revocation status within 5 s or explicitly unknown if the relay is unreachable.
- **cost:** Negligible API cost; bounded local metadata storage, with content hashes and redacted labels rather than bodies.
- **security:** The ledger must be append-only and locally protected, but must not become a second store of sensitive content. Record hashes, capsule IDs, destination, and classification only. Relay deletion must be honest: current announcements are not actually swept, so the report must distinguish deleted, withheld, expired-read, and physically retained.
- **missing:** A mandatory outbound interception/join point for voice, browser, screenshot, and announcement paths; A signed receipt protocol linking local capsule IDs/content hashes to relay records; A real relay revocation/deletion contract, including truthful handling of announcement and audio retention


## What it asked for

_Nothing._
## Its own summary

Discovered a major state change and recorded it: the exact AI Pendant Agent now has Accessibility and Screen Recording, required permissions are empty, the Safari extension is online on an authenticated Discord tab with six tabs, and the relay/Mac bridge are reachable. I proposed three owner-facing capabilities: (1) the most useful, a grounded voice-to-screen inspect/approve/act loop with evidence and receipts; (2) proof-backed semantic monitoring of an authenticated browser tab; and (3) a fail-closed privacy circuit breaker that keeps sensitive browser/app content local. The attempted scoped-pendant-auth change collided with an existing proposal, so I did not restate it.

**Biggest unknown:** There is still no live pendant in the registry, so the voice/wearable and device-originated playback portions cannot be hardware-verified. What is needed next is a real relay-to-local evidence bridge (capsuleId/contentHash), a durable watcher scheduler, and a local preflight privacy gate. The Mac-side screen loop and browser inspection can now be tested immediately because TCC permissions are live.

