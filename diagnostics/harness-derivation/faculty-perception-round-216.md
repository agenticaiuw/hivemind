# Harness derivation — faculty-perception — round 216

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live_mac_reality_2026-08-09** — At 2026-08-09T00:21Z the Mac agent is healthy and ready: Accessibility, Screen Recording, and all listed automation grants are true; browser extension online with 2 Safari tabs and zero pending commands; relay reachable with D1 store and mac bridge online. No pendant appears in live devices, so pendant delivery remains unknown.
  - evidence: GET /ops/status and read_continuity_snapshot(include=['relay','pipeline']) both returned HTTP 200; /ops/status payload reports permissions.ready=true, browser online, relay reachable, and devices discover lists only home-macbook-bridge and cloudflare-contract-test.

## Capabilities it proposed

### "When I ask 'did that really happen?', give me a one-sentence verdict and the exact evidence chain—what was attempted, what the Mac/browser/relay actually observed, and what remains unverified."
- **useful because:** Today a completed Mac job can be mistaken for a heard answer, a stale context fact can outrank live OS state, and browser reads can lack provenance. This gives the owner a fast truth verdict instead of confident fiction, with explicit unknowns rather than silently filling gaps.
- **path:** pendant → relay → mac-planner → browser-extension → unified
- **model tier:** background for assembling and scoring evidence; realtime only to speak the already-computed verdict
- **latency:** Under 2 seconds for a recent action; up to 8 seconds when joining a scheduled run, browser evidence, and relay history.
- **cost:** About $0.005–$0.03 per query; most work is deterministic joins and freshness scoring, with a small model call only for the spoken compression.
- **security:** Evidence may include URLs, mail/calendar metadata, and action parameters. Redact secrets before the model; require confirmation before exposing sensitive details aloud. Never infer pendant playback from relay socket delivery.
- **missing:** A provenance-join endpoint that accepts a run/job/action identifier and returns bounded records from pipeline, action ledger, browser provenance/evidence, relay receipts, and permission snapshots.; A contradiction scorer that compares machine facts against live OS observations and marks stale machine-origin preferences as suspect.; A stable relay browser-read identifier/content hash and Mac capsule bridge for cloud-only reads.; A real device-originated played event (already separately accepted as audio_delivery_ack_queue) so owner-heard can move from unknown to verified.

### "What is on my screen right now, and what should I know before I act on it?"
- **useful because:** The browser extension exposes a live Safari tab and the Mac now has Screen Recording and Accessibility, but the system does not currently produce a bounded, provenance-stamped description of the owner's actual visible scene. This would turn 'I’m looking at this' into grounded context while separating browser DOM facts from pixels and marking login walls or stale captures.
- **path:** pendant → mac-vision → browser-extension → relay → unified
- **model tier:** Realtime for the short spoken description; a cheaper vision model for a one-frame caption and deterministic browser inspection for titles/URLs.
- **latency:** 1–3 seconds from button press; capture expires after 15 seconds and is never reused as current state.
- **cost:** Roughly $0.01–$0.05 per request, dominated by one image tokenization; browser inspection and freshness checks are local.
- **security:** Screen pixels can contain passwords, financial data, and private messages. Require an explicit first-use consent, redact known secret fields, keep the frame in memory only, and speak only a short summary. Never upload the frame to the relay unless the owner explicitly asks.
- **missing:** A read-only current-screen capture route on the Mac agent with a 15-second freshness lease and redaction metadata.; A join record linking captureId to browser tabId/windowId and the voice turn without persisting raw pixels.; A relay/pendant request path that can ask for the snapshot while offline-safe fallback says the screen could not be checked.

### "What changed since I last looked at this page or document? Show me only the meaningful changes, and tell me whether the comparison is trustworthy."
- **useful because:** The owner can read pages, edit files, and receive briefings, but cannot obtain a cross-surface, time-anchored diff that distinguishes actual content changes from a different tab, login wall, truncation, or stale capture. This would prevent acting on an old price, policy, schedule, or draft while making uncertainty audible.
- **path:** browser-extension → mac-planner → mac-vision → relay → pendant → unified
- **model tier:** Background deterministic hashing and structural diff first; a cheaper text model summarizes only the changed regions; realtime speaks the final short result.
- **latency:** Under 3 seconds for a cached capsule pair; up to 10 seconds when recapturing a live browser page and local document.
- **cost:** About $0.005–$0.04 per comparison; hashing and region matching are local, with model cost proportional only to changed text.
- **security:** Snapshots may contain private documents or authenticated pages. Keep full bodies on the originating Mac, send only redacted changed segments and hashes to the model, enforce capsule expiry/revocation, and require confirmation before comparing or quoting sensitive sources aloud.
- **missing:** A user-facing comparison route that accepts two evidence references or a source plus 'last seen' and returns changed regions, confidence, and failure reasons.; A relay browser capture contract that emits a stable capture ID, content hash, source URL, and capture timestamp, then bridges into the existing Mac evidence-capsule store.; Document adapters that produce redacted, region-addressed capsules for local files and browser pages with consistent normalization.; A durable owner-facing index of 'last seen' capsules that records viewing, not merely system generation or briefing delivery.

### "Before you do this, tell me exactly what data will leave my Mac, which model or service will see it, and what will remain local; after it finishes, show me what actually left."
- **useful because:** The owner has browser sessions, mail, files, and a relay, but cannot get a truthful per-action data-flow explanation. A permission prompt says whether an action is allowed, not whether page text, screenshots, or private metadata crossed the Mac boundary. This makes powerful multi-surface automation understandable and reversible.
- **path:** pendant → mac-planner → mac-vision → browser-extension → relay → unified
- **model tier:** Deterministic policy/data-flow analysis for the preflight and postflight receipt; a small model only compresses the receipt into one spoken sentence.
- **latency:** Preflight under 300 ms for known actions; postflight under 1 second after the action receipt arrives.
- **cost:** Near-zero model cost for structured actions; $0.001–$0.01 only when summarizing an unstructured payload classification.
- **security:** The audit itself must not reproduce secrets. Classify fields (credentials, page text, screenshot, metadata, audio) and retain hashes, destinations, policy decisions, and byte counts rather than raw payloads. Confirmation is required for new destinations, sensitive classes, or screenshots.
- **missing:** A mandatory egress manifest on every Mac, browser, and relay action describing payload classes, destination, model, retention, and redaction.; A post-action receipt that records actual bytes/classes sent rather than the intended plan alone.; A policy evaluator that compares intended and actual egress and blocks or flags mismatches.; A spoken pendant-friendly summary plus a durable local audit view.

### "Save this exact moment so I can resume later—restore the right tab or document, show me what I was looking at, and tell me what changed before I continue."
- **useful because:** The owner currently has separate browser history, Mac files, jobs, and spoken context, but no cross-surface resumption point. A real checkpoint would preserve the source, region, tab/document identity, unsaved local state, relevant action intent, and a safe return path instead of making the owner reconstruct the task from memory.
- **path:** pendant → browser-extension → mac-planner → mac-vision → relay → unified
- **model tier:** Deterministic checkpoint assembly and restoration; background model summarizes the checkpoint and changes; realtime only handles the spoken save/resume interaction.
- **latency:** Save in under 2 seconds; resume in under 5 seconds with a bounded fallback if a tab, file, or session no longer exists.
- **cost:** About $0.001–$0.02 per checkpoint, mostly local storage and optional changed-region summarization.
- **security:** Checkpoints can preserve authenticated URLs, drafts, and sensitive screen context. Store redacted capsules and opaque references locally, encrypt at rest, expire them by policy, and require confirmation before reopening a sensitive page or restoring unsaved edits.
- **missing:** A first-class cross-surface checkpoint object joining browser tab/window, evidence capsule, local file/document state, action/job/session IDs, and spoken intent.; Atomic capture of browser and Mac state so the checkpoint cannot claim a document was saved when only the tab was recorded.; A restore planner with explicit safe modes: reopen read-only, restore focus only, or restore editable state after confirmation.; Relay synchronization of checkpoint metadata for reconnecting the pendant, without uploading private bodies.


## Changes it proposed to its own stack

### `context` — Add a live-fact reconciliation pass before every context projection: compare machine-origin preferences and cached device/browser claims against fresh /ops/status, /machine-context, filesystem timezone, browser heartbeat, and relay health. Emit a signed observation with observedAt, source, freshness, and contradiction links; demote (never delete) a cached fact when live evidence disagrees, and make the model see the contradiction explicitly.
- **owner gets:** The owner stops receiving answers based on a pinned but wrong machine preference (for example America/Chicago while the Mac is America/New_York), or on a browser/device state that went stale minutes ago. Corrections happen automatically without rewriting the owner's memory.
- effort: Medium: deterministic comparator plus projection metadata and a small set of source adapters; no new model training.  ·  risk: A transient outage could demote a good fact. Require two consecutive contradictory observations or a freshness timeout, preserve the old row with provenance, and show 'live check unavailable' rather than treating missing data as false.
- cost: Negligible API cost; one local status read per projection, optionally cached for 30–60 seconds.  ·  latency: Adds roughly 50–200 ms locally when cache is warm; bounded parallel reads otherwise.
- security: The model receives more operational metadata. Keep URLs, mail subjects, and device identifiers redacted unless the user asks; never export raw secrets from memory.
- depends on: A mounted, bounded live-observation adapter for /ops/status and filesystem timezone; Projection support for source, observedAt, freshness, and contradiction metadata; A policy that distinguishes source.origin:'owner' from source.origin:'machine'

### `routines` — Make every scheduled brief a freshness-graded bundle rather than a single completed string: at fire time, collect per-source observedAt/age, timezone used, permission state, and retrieval result; refuse to present stale or missing sections as current, and attach a compact machine-readable receipt that the pendant/relay can later quote.
- **owner gets:** A 'completed' morning brief would finally mean the calendar, mail, files, and news were each checked—or the owner would hear exactly which section was unavailable or stale. It prevents a polished three-sentence lie when one source silently timed out.
- effort: Medium: add source-level receipt fields to routine runs and change the brief composer to enforce freshness thresholds; existing routine scheduler and Mac automation remain usable.  ·  risk: Freshness thresholds may make a brief feel incomplete during outages. Use explicit labels ('calendar checked 2m ago', 'mail unavailable') and let the owner override thresholds per routine.
- cost: Small extra reads; no additional model call if the composer uses deterministic status labels. News/browser retrieval may add normal search cost.  ·  latency: Adds parallel source checks, typically under 1 second; cap the routine at a fixed deadline and preserve partial results with warnings.
- security: Receipts must store metadata and hashes, not mail bodies or private file contents; spoken output should never expose URLs or subjects unless requested.
- depends on: Per-source observation schema with observedAt, age, status, and redaction class; Routine-run receipt support beyond one aggregate completed flag; Live Mac permission and timezone observations (currently available: permissions.ready=true and America/New_York); Relay/browser source result IDs for cloud-fetched material


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: the Mac agent is healthy, Accessibility and Screen Recording are now granted, Safari bridge is online with two tabs and no pending commands, relay is reachable on D1, and no pendant is registered. Proposed three distinct improvements: an evidence-chain verdict for 'did that really happen?', automatic contradiction reconciliation of stale machine facts, and freshness-graded scheduled briefs; also proposed a screen-grounded context handoff. I no longer need TCC access. What I still need for end-to-end perception is a real pendant registration/heartbeat and device-originated playback telemetry; until then all owner-heard claims remain unknown. The system also needs a stable relay browser-read ID/hash bridge and source-level routine receipts.

**Biggest unknown:** Whether the absent pendant is merely not deployed or unavailable; no live observation can distinguish those states, and the relay cannot verify receipt or playback without the device.

