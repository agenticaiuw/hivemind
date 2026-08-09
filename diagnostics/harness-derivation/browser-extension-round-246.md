# Harness derivation — browser-extension — round 246

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Check this booking/order against my calendar and tell me if anything conflicts.”"
- **useful because:** The browser can read the authenticated confirmation the owner is already viewing, while the Mac can read Calendar and the relay can reconcile dates, times, locations, and names. Today each node sees only its own surface; this catches double-bookings, impossible travel, duplicate charges, or a wrong date at the moment the owner is looking at the confirmation. The pendant delivers the result without requiring the owner to keep the page open or copy details.
- **path:** browser → mac-planner → relay → pendant
- **model tier:** Use gpt-5.6-luna locally for structured extraction and deterministic date/time normalization, with a small gpt-5.6-luna judgement pass for conflicts; use realtime only to state the result. Do not use the expensive realtime tier to parse a whole page.
- **latency:** 4–8 seconds for one page plus a calendar window; return ‘could not verify’ for missing timezone/location rather than guessing.
- **cost:** One browser read and one local Calendar read plus a compact structured comparison; low token cost because only normalized fields cross surfaces.
- **security:** Never persist confirmation HTML or full calendar entries. Keep only a short, task-scoped conflict claim with URL/title provenance and existing 24-hour browser TTL. Do not assume which origins/categories are acceptable: an empty per-origin policy must be configurable by the owner.
- **missing:** A structured browser extractor that emits typed fields (date, timezone, location, amount, confirmation status) with evidence spans; A cross-surface join that can request a bounded Calendar interval and reconcile timezones/locations; A pendant response template for conflicts that does not read sensitive booking details aloud unless requested

### "“Is this page safe to use, or does anything look suspicious?”"
- **useful because:** A worn-device owner often opens a link in an already-authenticated browser before noticing a look-alike domain, unexpected payment destination, or request for credentials. The browser supplies the exact origin, redirect chain, visible form fields, and page evidence; the Mac checks the connection/domain metadata; the relay compares the signals and speaks a short warning through the pendant. This is a capability no pendant-only or Mac-only node can provide because the browser session is the only place where the real page and login state coexist.
- **path:** browser → mac-terminal → relay → pendant
- **model tier:** Use deterministic origin/redirect/form heuristics first and a cheap background gpt-5.6-luna judgement pass for ambiguous page language. Reserve gpt-realtime-2.1 for the owner's follow-up conversation, not page scanning.
- **latency:** Under 3 seconds for URL/origin checks and under 8 seconds for an ambiguous content verdict; an immediate ‘do not enter credentials yet’ warning should precede deeper analysis.
- **cost:** Low: one page snapshot/read and local metadata checks, with a small extracted-text prompt. Dominant cost is only ambiguous pages sent for model review.
- **security:** Treat this as advisory, never as proof of legitimacy. Do not transmit secrets or form values; redact credential/payment fields before analysis and never persist page text/screenshots. The owner must see the exact origin and redirect chain, and any click/type remains separately requested. Use the empty per-origin configuration rather than inventing an allowlist.
- **missing:** A local certificate/redirect/origin inspection action paired with the browser tab; A redaction-aware page classifier for login/payment/credential requests; A pendant warning event with severity and URL spoken only on request

### "“Put the confirmation I’m viewing into the right place on my phone.”"
- **useful because:** The browser can reach the authenticated confirmation, but the iPhone is where the owner actually needs the resulting boarding pass, reservation, warranty, or appointment. The system should extract the structured artifact from Safari, create the native Calendar/Wallet/Files item through iPhone Mirroring, and report exactly what was created through the pendant. This removes the current manual bridge of screenshots, downloads, and retyping while preserving the authenticated session on the browser.
- **path:** browser → mac-planner → ios-control → relay → pendant
- **model tier:** Use deterministic typed extraction and native iOS actions wherever possible; use a small gpt-5.6-luna pass only to map page fields to an artifact schema. Realtime only speaks the completion summary.
- **latency:** 10–20 seconds for extraction and native app entry; if the page lacks a machine-readable artifact, produce a preview rather than guessing fields.
- **cost:** One browser read plus a short structured extraction and several local iOS actions; inference cost is modest, with UI traversal dominating latency.
- **security:** Never send credentials or page bodies to iOS. Show a preview of title/date/identifier before creating the artifact, preserve source URL and evidence, and make the created local item undoable. Keep page text ephemeral and honor the existing empty per-origin configuration until the owner defines it.
- **missing:** A typed artifact schema and extractor for boarding passes, reservations, appointments, receipts, and warranty records; An iOS action that creates/imports those artifacts through the real native app rather than typing arbitrary page text; A reversible cross-surface receipt linking the created phone item to the browser evidence capsule

### "“I’ve lost control of my devices—lock every session now.”"
- **useful because:** A physical pendant action is available even when the Mac screen, browser, or phone cannot be reached. One event should immediately lock the Mac, obscure authenticated Safari tabs, stop any pending browser command, and invoke the iPhone's lock/home path; the relay should record a short incident receipt and the pendant should confirm locally even if the network is down. This is a genuinely cross-node safety action, not something the browser or Mac can guarantee alone.
- **path:** pendant → relay → mac-planner → browser → ios-control
- **model tier:** No model is needed for the immediate lock fan-out. Use the realtime tier only to explain status afterward; background reconciliation can use a cheap model, if at all.
- **latency:** Local pendant acknowledgement under 500 ms; Mac/browser/iPhone fan-out within 2 seconds, with retries and an explicit list of surfaces that did or did not lock.
- **cost:** Negligible inference cost; local serial/BLE or network fan-out dominates. Requires a durable incident receipt but no page content.
- **security:** This is intentionally high-impact and must be a dedicated physical gesture that cannot be triggered by accidental audio. It should fail closed, preserve no page text, cancel queued browser mutations, and never claim a surface locked until its receipt confirms it. Recovery is owner-controlled re-authentication; do not silently delete sessions or data.
- **missing:** A firmware panic gesture and local offline command path distinct from ordinary alert playback; A relay broadcast with delivery acknowledgements and idempotency; Mac/browser/iOS lock primitives with receipts and cancellation of queued actions; A pendant-visible status code for partial completion


## Changes it proposed to its own stack

### `browser-harness` — Make browser actions tab-addressed and fail closed on identity mismatch. Before every browser_read_page/click/type/snapshot, resolve the requested tabId and return an error if the extension replies with a different tabId, URL, or title; never substitute the active tab. Include requestedTab and observedTab in the receipt, and require a fresh list_tabs after navigation before allowing a follow-up action.
- **owner gets:** Today a read requested for the DoorDash tab returned the active YouTube page instead, with a successful receipt. A spoken answer could therefore confidently describe the wrong logged-in page. This change makes browser assistance trustworthy: wrong-tab or closed-tab conditions become an explicit, recoverable message instead of a plausible lie.
- effort: Medium: thread tabId through browserBridge/browserPage and add a result validator plus regression tests for two tabs, navigation, and extension races.  ·  risk: Some existing flows that implicitly use the active tab will start returning a clear mismatch error; recover by refreshing tab inventory and retrying against the observed tab only. No page mutation is introduced.
- cost: Negligible runtime/API cost; modest engineering/test cost.  ·  latency: Adds one local tab-resolution/validation step, generally under 100 ms; a recovery retry may add one browser round trip.
- security: Positive: prevents cross-tab leakage between authenticated origins and makes provenance honest. It does not create an origin policy, so the owner's explicit per-origin configuration remains separate.
- depends on: Existing POST /execute browser_* action path and browser result provenance; Existing GET /browser/inspect and tabId-bearing browser receipts


## What it asked for

_Nothing._
## Its own summary

The browser is live again: Safari has two tabs (DoorDash and YouTube), and authenticated/page reads work through POST /execute. I found a concrete correctness failure: requesting DoorDash by tabId returned the active YouTube page with a successful receipt. I recorded a tab-addressed, fail-closed browser-harness change and warned mac-planner. I also recorded two new cross-surface capabilities: checking a viewed booking/order against Calendar, and a pre-credential phishing/safety check using browser origin/content plus Mac metadata, relay judgement, and pendant warning. One attempted current-tab voice Q&A proposal was correctly rejected as already existing.

**Biggest unknown:** The owner still has not supplied the first allowed authenticated origins or spoken/persistence sensitivity rules; keep that configuration empty rather than inventing it. Technically, the urgent missing pieces are strict requestedTab/observedTab enforcement, a redaction-aware typed page extractor, and local redirect/certificate metadata inspection. Direct /execute is currently the reliable browser path; the many enqueue wrapper grants remain unnecessary.

