# Harness derivation — relay-realtime — round 66

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What happened to that thing I asked you to do earlier?"
- **useful because:** The owner can get a quick, accurate status update even if the Mac is asleep, without repeating the original request or waiting for a full planner round-trip.
- **path:** relay → mac-bridge
- **model tier:** Realtime relay for the spoken request; relay_job_status for the cheap status read. No planner needed.
- **latency:** Under a second when the job record exists; the response is pre-sized for voice playback.
- **cost:** Very low. Single status lookup dominates; no expensive planning or browser automation.
- **security:** Contains task metadata in job records. Ensure records are scoped to the owner and not exposed cross-tenant. Relay must speak the returned 'spoken' string verbatim to avoid misreporting.
- **missing:** A consistent way to reference the job from voice (better disambiguation using recent job summaries, which may require a small, privacy-scoped index).

### "“Compare what’s in my open browser tab with the relevant file or app on my Mac, and tell me only what conflicts or is missing.”"
- **useful because:** The owner often has the authoritative web session in one place and drafts, exports, or local app state on another. Today they must manually copy both into one context and reconcile them; neither a Mac-only agent nor a browser-only agent can see the whole discrepancy.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Use relay-realtime only to capture the spoken request and deliver the concise answer; have browser-extension and mac-planner perform parallel read-only collection, and use a cheaper background synthesis model to compare normalized evidence. Escalate to mac-vision only when the relevant Mac app has no structured read path.
- **latency:** Start speaking an acknowledgment within 300 ms; collect both sources in 3–8 seconds; deliver a short spoken conflict list, with a dashboard transcript containing source snippets and timestamps. No mutation or confirmation should be needed because this is read-only.
- **cost:** Roughly one realtime turn plus two small downstream reads and a compact synthesis, about $0.02–$0.08 per invocation depending on whether vision is needed; the dominant cost is vision fallback and large page/document extraction.
- **security:** The browser side may contain authenticated private data and the Mac side may contain unrelated files. Scope collection to the explicitly named/open tab and a planner-selected file/app, show both source identities in the dashboard, redact secrets from spoken output, retain only normalized claims and short citations, and never send full page contents to the realtime model unless required.
- **missing:** A cross-surface compare intent and evidence envelope with source IDs, timestamps, snippets, and confidence; A browser-extension read API that returns the active tab’s visible/semantic content with stable citations; A Mac planner read operation that can identify and extract the relevant local document/app state without changing it; A relay fan-out and bounded synthesis worker that joins the two evidence sets and streams only conflicts/missing fields to the pendant; Dashboard UI for reviewing citations and correcting which local source was selected

### "“I’m leaving now. When I come back, tell me what changed on my Mac and in my open browser work since I left.”"
- **useful because:** The pendant is worn away from the desk, so the owner currently returns to an unexplained pile of changed tabs, files, notifications, and drafts. A before/after delta is more useful than a generic notification stream and requires both the authenticated browser and unattended Mac state.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime model only for the departure/return utterances and the final spoken digest. A cheap background diff worker should normalize snapshots and rank changes; mac-planner and browser-extension provide structured observations, with mac-vision as a fallback for visible UI changes.
- **latency:** Departure capture should finish in under 2 seconds and return a first spoken digest within 5 seconds of reconnect or the owner’s question. The system may compute diffs in the background while the owner is away.
- **cost:** Approximately $0.01–$0.05 per departure/return pair for snapshots, structured diffs, and a small synthesis; vision fallback and storing large document hashes are the main cost drivers.
- **security:** Snapshots can expose private work and authenticated pages. Keep raw content on the originating Mac/browser where possible, send hashes/metadata and only changed excerpts, encrypt snapshots with per-owner keys, expire them after a configurable window, and make the spoken response omit sensitive content unless the owner asks for detail. The feature must not infer that an email or file was read merely because it changed.
- **missing:** A pendant departure/return marker protocol that survives LTE disconnects and reconnects; A durable snapshot store with per-surface scope, content hashes, timestamps, retention, and explicit baseline IDs; Mac and browser observers that can report meaningful state changes (new/closed tabs, file edits, app notifications, draft mutations) without taking action; A cross-surface diff/ranking worker that distinguishes owner-caused navigation from substantive changes and emits cited deltas; A reconnect-triggered relay briefing path and dashboard controls for selecting watched surfaces and retention

### "“Where did that answer come from? Read me the exact sources and show them on my Mac.”"
- **useful because:** A spoken answer assembled from an authenticated browser page, a local file, and planner reasoning is currently hard to audit: the owner cannot tell which source was used or whether it was stale. Provenance lets them trust useful automation without needing to remember the original request.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Have downstream readers attach structured provenance while collecting data; use a cheap synthesis model to build a source chain. The realtime model only answers the short spoken provenance question and hands a cited source bundle to mac-planner to open the exact locations.
- **latency:** Speak the first source names within 1–2 seconds; open the cited browser tab/file on the Mac within 5 seconds when online. If the Mac is away, provide the citations verbally and queue the display handoff for reconnect.
- **cost:** About $0.01–$0.04 per query, dominated by source extraction and optional excerpt summarization; provenance IDs and hashes are cheap.
- **security:** Citations can reveal private URLs, filenames, or message subjects aloud. Speak redacted labels by default, require an explicit follow-up for sensitive excerpts, keep raw source text at its origin, and use signed short-lived citation tokens so a stale or forged citation cannot open an unrelated resource.
- **missing:** A provenance envelope required on every browser/Mac read and every synthesis claim, including source identity, timestamp, excerpt offsets, and confidence; A claim-to-source graph that survives relay handoffs and compact context windows; Relay voice endpoint for querying the last answer’s provenance without resending the full conversation; Mac/browser deep-link actions that open the cited exact tab, file range, or app record and report whether it still matches the cited hash; Dashboard source-chain view with stale-source and unsupported-claim indicators


## Changes it proposed to its own stack

### `relay` — Stop listing tools in the 'granted' category unless they are discoverable and describable via the standard tool registry. Instead, record grants as capability flags (e.g., 'intent-routing-enabled') and map them to concrete tool names that exist in the 'tools' category. Add a small validation step that fails the build if a granted tool name cannot be discovered/described.
- **owner gets:** It prevents silent routing failures where the relay thinks it can do something (like intent routing or server-side browser actions) but cannot actually call it. That keeps voice interactions reliable and avoids the pendant getting stuck mid-command.
- effort: Medium. Mostly wiring and validation in the orchestrator/tool registry plus a migration for existing grants.  ·  risk: Low. The main risk is temporarily hiding a capability until the registry is corrected; mitigate with a console warning and fallback behavior.
- cost: Low API cost; a one-time validation call per deploy. No new runtime cost for the owner.  ·  latency: None at runtime; failures are caught at build/deploy time.
- security: Positive. Reduces the chance of calling an unintended or spoofed tool by name.
- depends on: A single source of truth for tool names and their schemas (the 'tools' category).


## What it asked for

_Nothing._
## Its own summary

Discovered the current tool registry and grants. Confirmed relay_job_status is real and usable for voice-friendly status checks. Found a mismatch: 'relay_route_intent' and 'server_browser_actions' appear in grants but are not discoverable/describable in the tools registry, meaning they may not be callable despite being 'granted'. Proposed a relay-level capability (voice job status) and a change to enforce registry consistency so the owner gets reliable routing.

**Biggest unknown:** Whether intent routing and server-side browser automation are truly available as callable tools, or only noted as granted flags. If they exist, they need to be added to the tools registry; if not, they should be removed from grants and re-requested with a concrete schema.

