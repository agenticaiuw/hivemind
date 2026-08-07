# Harness derivation — browser-extension — round 85

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge reliability** — At 2026-08-07T13:06Z Safari extension is offline, only home-chrome is registered with no tab, and 7 browser commands remain pending. Three browser enqueue grants are schemas only and cannot dispatch commands. Existing browser sessions point to stale tab IDs.
  - evidence: GET /browser/status returned online:false, devices=[home-chrome tabId:null online:false], pendingCommands:7; GET /browser/sessions returned stale tab IDs 320512/230928/229550; describe(browser_enqueue_command), describe(browser_command_enqueue), and describe(browser_enqueue_command_impl) each report no implementation.

## Capabilities it proposed

### "When I’m looking at a private webpage, let me say “save this page for later,” then later ask the pendant “what was that?” and get the exact cited excerpt, page title, and timestamp without reopening or exposing the whole browsing session."
- **useful because:** Today, authenticated browser knowledge disappears when the tab changes or Safari goes offline. This gives the owner a reliable, privacy-preserving memory of a specific decision or fact from a private page, available from the pendant even when the browser is no longer reachable.
- **path:** browser-extension → mac-planner → relay-realtime → unified
- **model tier:** Use deterministic browser extraction and hashing first; use a cheaper background text model only to generate a short label or answer over the saved excerpt. Use realtime only for the owner’s spoken request and response.
- **latency:** Capture should complete within 2 seconds while the page is open; later pendant retrieval should feel conversational, under 1 second for metadata and under 3 seconds if summarization is needed.
- **cost:** Near-zero API cost for capture and exact quoted retrieval; occasional small text-model call for summarization, dominated by a few hundred tokens per saved capsule.
- **security:** Store only the owner-selected excerpt, title, URL origin, timestamp, and a content hash—not a full page or cookies. Encrypt at rest, mark capsules sensitive by default, allow deletion from the pendant, and never send page content to the relay unless the owner explicitly asks for a spoken summary. Do not capture password fields, payment data, or hidden DOM text.
- **missing:** A browser action that extracts the owner’s current selection or a bounded semantic excerpt with locator metadata; An encrypted, per-owner citation-capsule store shared by browser and relay; A pendant/relay retrieval intent that resolves “that page” using recency and spoken context; A retention/deletion API and UI for saved private-page capsules


## Changes it proposed to its own stack

### `browser-harness` — Add an adaptive browser-bridge health controller, distinct from the command queue: track extension heartbeats and per-command latency, mark devices as offline/degraded/stuck, quarantine and deduplicate superseded pending commands by idempotency key, and expose a recovery action that asks the Mac surface to foreground/reload Safari and the Browser Bridge before retrying only safe idempotent actions (such as navigate/read). Preserve stale sessions but require explicit reattachment validation (tabId/windowId/url) before dispatch. Emit one compact recovery receipt with the failed reason, commands discarded, retry count, and current user action needed.
- **owner gets:** The owner stops getting 45-second hangs and repeated navigate failures when Safari is blocked or the extension disappears. The system either recovers quietly, or immediately says “open Safari and enable Browser Bridge,” without replaying seven stale commands or risking duplicate form submissions.
- effort: Medium: browserBridge health state machine and queue compaction, browser session reattachment check, Mac action hook to foreground Safari/reload extension, and receipt/dashboard fields; integration tests for offline, timeout, reconnect, and duplicate idempotency keys.  ·  risk: A reconnect race could discard a command that would have completed; quarantine rather than delete, retain an audit record, and retry only actions explicitly marked idempotent. Never auto-retry browser_type/click/select or any submit/send action. If Safari reload fails, leave the queue paused and provide the exact recovery instruction.
- cost: Negligible API cost; local state and a few heartbeat records. One Mac action round only on recovery. No page content or credentials leave the Mac.  ·  latency: Normal browser actions unchanged. Offline failures become a fast health response (seconds rather than 45 seconds); recovery adds roughly one Mac round plus extension heartbeat.
- security: Improves safety by preventing replay of mutations and requiring tab identity validation. Foreground/reload Safari is local-only; do not expose URLs or page text in relay telemetry beyond minimally necessary metadata.
- depends on: chg-14accc01's request IDs/idempotency and tab/session affinity (retain its result contract); chg-16bc5dee's durable browser runner (use its step classification, do not duplicate its worker); A Mac-side high-level action capable of foregrounding Safari or reopening the Browser Bridge


## What it asked for

_Nothing._
