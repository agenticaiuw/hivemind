# Harness derivation — browser-extension — round 17

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser_sessions** — The live Mac agent now exposes durable browser sessions: default session on https://time.is/UTC plus two probe sessions, persisted at /Users/evanliu/AI-Pendant-Workspace/.pendant-browser-sessions.json. Session IDs and tab/window IDs are available for reattachment.
  - evidence: describe('POST /browser/sessions') returned HTTP 200 with sessions default, probe-form2, probe-form and storePath.

## Capabilities it proposed

### "“Every morning, check my logged-in work dashboards and tell me only what changed or needs my attention; keep watching the important pages and alert me when a genuinely urgent item appears.”"
- **useful because:** This uses the browser’s unique reach into authenticated sessions instead of asking the owner to copy private portal data. It turns noisy dashboards into a short actionable briefing and catches changes while the owner is away.
- **path:** browser: maintain named Safari sessions and read selected authenticated pages → mac-bridge: schedule polling, normalize page observations, and retain change receipts → relay: run cheap background comparison and send only high-confidence alerts → pendant: speak a concise alert/briefing and accept “read more” or “open it” → dashboard: let the owner choose pages, selectors/regions, cadence, and urgency rules
- **model tier:** Background/scheduled work should use a cheap slower model (or deterministic DOM extraction plus a small classifier); reserve realtime only for the owner’s follow-up conversation. A stronger model is invoked only when a page materially changes and needs summarization.
- **latency:** Routine checks can complete within 1–3 minutes of the schedule; urgent checks should notify within one polling interval (target 2–5 minutes). Interactive drill-down should feel conversational, under ~2 seconds after cached text is available.
- **cost:** Roughly $0.01–$0.08 per daily page-check batch depending on pages and change volume; DOM extraction and hashes dominate neither API nor latency. Most checks should send only compact diffs, not full pages, to the model.
- **security:** Authenticated page text and screenshots may leave the Mac if sent for summarization; default to local DOM/region extraction, redact secrets/tokens and stable identifiers, encrypt stored diffs, and retain only short-lived evidence. Never submit forms, send messages, or purchase; show the exact proposed mutation for owner-directed execution. The owner should explicitly designate watched pages and sensitive regions.
- **missing:** A durable page-watch scheduler and named browser-session lease/reconnect mechanism; Semantic DOM/region extraction with robust selectors and fallback fingerprints; Change/diff receipts compatible with jobId/parentId/seq/intent-hash/resource-ref/TTL ledger; Urgency classifier, deduplication, quiet hours, and pendant/relay notification routing; Owner-facing setup UI for selecting authenticated pages and redaction/sensitivity rules


## Changes it proposed to its own stack

### `browser-harness` — Build a durable authenticated page-watch layer: named browser sessions with tab/window reattachment, per-watch cadence and quiet hours, DOM-region extraction plus normalized semantic fingerprints, encrypted short-lived snapshots, and append-only change receipts keyed to the shared jobId/parentId/seq/intent-hash/resource-ref/TTL schema. Add selector healing by storing multiple anchors and requiring a large semantic change before alerting. Expose preview/read/diff only; mutations remain explicit browser commands.
- **owner gets:** The owner gets reliable “what changed?” answers even after Safari restarts, tab IDs change, or a portal adds harmless timestamps and ads. Alerts become rare and meaningful rather than repeated screenshots or false alarms.
- effort: Medium-high: browser extension reconnect/reattach protocol, local encrypted store, extraction/diff worker, scheduler integration, and dashboard controls; roughly 2–4 engineer-weeks for a robust first version.  ·  risk: A stale session or healed selector could read the wrong account/page, and a portal redesign could hide a real change. Recover by marking watches degraded, attaching evidence and confidence to each receipt, pausing on low-confidence anchor matches, and offering one-click rebind. Expire credentials/tokens never; store only derived text/diffs.
- cost: Low ongoing API cost: hashes and local diffs are deterministic; estimated <$0.02/day for several watches, with model calls only on meaningful changes. Local encrypted snapshot storage is modest (tens to hundreds of MB depending on retention).  ·  latency: Polling adds configured load; local extraction is sub-second per page, while semantic summarization adds roughly 1–5 seconds only on changes. Reattachment after Safari restart may take several seconds.
- security: Sensitive authenticated content remains on the Mac by default; only redacted diff snippets leave the device. Session IDs and receipts must be encrypted at rest, access-scoped, and excluded from generic model context. Audit every read and provide an immediate disable/delete control.
- depends on: A functioning extension enqueue/result path (currently sessions and commands are available); Persistent watch scheduler in the Mac agent; Shared compact execution/change receipt schema from mac-planner; Dashboard controls for page selection, redaction, and retention


## What it asked for

_Nothing._
## Its own summary

Discovered that durable browser sessions are now live (default and probe sessions with persisted session store), recorded the finding, informed mac-planner, and submitted two build proposals: authenticated portal/page watching with concise urgent diffs, and a browser-harness layer for session reattachment, semantic diffs, encrypted short-lived evidence, selector healing, and shared receipts. Still needed to build: scheduler/watch storage, semantic extraction and redaction, notification routing, and owner setup controls.

**Biggest unknown:** The owner’s first real authenticated workflow and sensitivity/retention preferences remain unspecified; without that, selectors, urgency rules, and redaction defaults can only be generic.

