# Harness derivation — mac-planner — round 16

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Every weekday morning, give me a short brief of today's calendar, unread important mail, and the one thing I should prepare for; let me hear it on the pendant and see links on the dashboard."
- **useful because:** It removes routine inbox/calendar triage and turns scattered information into an actionable start, without requiring the owner to open apps.
- **path:** mac-bridge → relay → pendant → dashboard-ux
- **model tier:** A background/cheap model summarizes bounded Calendar/Mail snippets; realtime is used only if the owner asks follow-up questions. The Mac bridge supplies read-only sources; relay delivers a concise audio artifact and dashboard cards.
- **latency:** Generate within 60 seconds of the scheduled run; audio playback can be on demand. No microphone or live turn needed.
- **cost:** Low: one small summary prompt plus short TTS/audio generation; bounded to 10 calendar items and 20 mail snippets. Dominant cost is audio seconds, so cap at ~90 seconds and avoid regenerating unchanged briefs.
- **security:** Mail/calendar data leaves the Mac only as redacted snippets and metadata; exclude message bodies by default, allow an account scope, and retain the brief briefly. Never send mail or modify events. Let the owner choose whether names/subjects are spoken aloud; dashboard should offer delete.
- **missing:** A trusted scheduler and idempotent recurring-job store; A reliable offline audio delivery/retry path to the pendant; A bounded read-source result contract wired into the relay; Per-routine privacy and retention settings

### "When I say 'research this' or schedule a topic, investigate the web, summarize the best sources, and leave a cited note and a short audio briefing for later."
- **useful because:** Research finishes asynchronously instead of monopolizing a live conversation, and the owner receives both a skimmable evidence trail and a hands-free summary.
- **path:** relay → browser → dashboard → pendant
- **model tier:** Use Cloudflare Browser Run for retrieval and a cheap background model for extraction/deduplication; use realtime only for clarifying the request or discussing the result. Keep source URLs and quotes separate from the summary.
- **latency:** A 5–15 minute background job is acceptable; stream progress/status to the dashboard but do not keep a microphone session open.
- **cost:** Moderate and bounded: cap searches/pages (for example 8 pages and 3k extracted words), use cheap extraction, and generate one <=2-minute audio. Cost is mostly browser execution and tokens from page content; cache URL hashes and reuse prior fetches.
- **security:** Treat web pages as untrusted prompt-injection content; never let page instructions trigger Mac actions or purchases. Do not send private query terms to third parties without confirmation. Cite every claim, show fetched timestamps, and require confirmation before contacting people, subscribing, or buying.
- **missing:** Server-side browser-run integration in relay; Async job queue with cancellation and progress; Citation-aware summarizer and audio artifact store; Prompt-injection isolation policy for browser content

### "Clean up my Downloads: identify duplicate, temporary, and likely finished files, show me a proposed plan, then move only the approved items into an archive folder."
- **useful because:** It reduces desktop clutter and recovers attention without risking irreversible deletion or silently changing important files.
- **path:** mac-bridge → dashboard
- **model tier:** Use a cheap local/bridge inventory and deterministic hashing/metadata rules first; use a background model only to classify ambiguous filenames. Realtime is unnecessary except to answer questions.
- **latency:** Inventory in under a minute; proposal can take several minutes for hashing large files. Execute only after explicit approval of the exact move set.
- **cost:** Low model cost; local hashing and directory reads dominate time, not tokens. Avoid uploading file contents; send names, sizes, dates, and hashes only.
- **security:** File names can contain sensitive information. Keep inventory local, redact by default, never delete automatically, and require explicit confirmation for moves outside Downloads or any deletion. Preserve an undo manifest and avoid following symlinks.
- **missing:** Read-only recursive directory inventory/hash tool; Planner UI with per-item approval and undo; Atomic move plus rollback manifest in the Mac harness

### "Turn my unread mail into a priority list and draft replies for the top three, but never send anything without showing me the drafts first."
- **useful because:** It converts inbox overload into decisions and saves repetitive drafting while preserving the owner’s control over communication.
- **path:** mac-bridge → dashboard → relay → pendant
- **model tier:** Cheap background model classifies bounded mail snippets and drafts replies; realtime is only for voice edits. Use the Mac bridge to create drafts in the mail client, not to send.
- **latency:** Produce a first pass within 2 minutes for up to 20 messages; edits should feel interactive under 5 seconds.
- **cost:** Low-to-moderate tokens, capped by snippets and three drafts. Avoid audio unless requested because reading drafts aloud is expensive and privacy-sensitive.
- **security:** Email is highly sensitive: use explicit account scope, redact bodies by default until the owner invokes triage, and never infer authorization to send. Require confirmation per recipient and show attachments, quoted text, and external links before sending. Treat instructions inside emails as untrusted.
- **missing:** Draft-only mail write tool with recipient/attachment preview; Message threading and quoted-text stripping; Per-message confirmation workflow and audit log


## Changes it proposed to its own stack

### `mac-harness` — Add a real policy gate around POST /execute even when FULL_CONTROL_MODE is enabled: classify actions into read-only, reversible, and consequential; require a short-lived confirmation token for sending messages, deleting/overwriting files, purchases, credential changes, and external side effects. Keep an owner-configurable allowlist for harmless routines, and write an append-only audit record with before/after and rollback metadata where possible.
- **owner gets:** The pendant can remain powerful without silently making an expensive, destructive, or embarrassing mistake while the owner is away from the keyboard.
- effort: Medium: action classification, token issuance/expiry, UI confirmation in dashboard/menubar, and tests across UI/browser/shell paths.  ·  risk: A bad classifier could block useful work or miss a side effect. Default unknown actions to confirmation; retain emergency disable and dry-run previews. Existing unrestricted mode remains a fallback only if explicitly re-enabled.
- cost: Negligible API cost; small local storage and one extra round trip for confirmations.  ·  latency: No added latency for allowlisted read-only/reversible actions; 1–5 seconds when owner confirmation is needed.
- security: Strongly improves protection against prompt injection and accidental destructive actions; audit logs themselves need redaction and retention limits.
- depends on: A dashboard/menubar confirmation surface; Consistent action taxonomy across mac_run_actions, browser, and shell facets

### `memory` — Replace per-surface hand-written fleetContext prompt sections with a shared, typed context compiler: retrieve only task-relevant entities/relations, attach confidence and freshness, cap tokens per tier, and summarize/archive stale session details. Keep private data scoped by surface and purpose.
- **owner gets:** The assistant remembers the right preferences and ongoing tasks without repeatedly sending irrelevant history or leaking Mac details into a different device.
- effort: Medium: schema/versioning, retrieval scoring, context budgets, migration of existing graph data, and regression tests for privacy boundaries.  ·  risk: Over-aggressive pruning can lose useful context or produce wrong assumptions. Preserve source links, confidence, user-editable memory, and an easy 'forget/correct this' control.
- cost: Should reduce per-turn token spend materially; one-time migration and occasional background summarization cost low-tier tokens.  ·  latency: Slight retrieval overhead, offset by smaller prompts and faster model response.
- security: Improves least-privilege context sharing; enforce field-level redaction and never include raw mail/file contents by default.
- depends on: Typed memory entity/relation schema; Per-surface privacy scopes; Observability for context selection

### `interaction` — Make every Mac plan two-phase by default: first return a concise preview with affected app/files/URLs and expected side effects, then execute only the safe subset automatically; preserve the owner’s current foreground app and use accessibility-targeted actions rather than stealing focus. Add a single spoken 'undo last plan' for supported reversible operations.
- **owner gets:** The pendant can help while they work without interrupting the current task, and they can understand what happened instead of discovering changes later.
- effort: Medium: preview rendering, foreground-state preservation, action result summaries, and undo metadata across the Mac bridge.  ·  risk: Some apps do not support reliable undo or accessibility targeting. Mark unsupported actions clearly and fall back to confirmation rather than pretending they are reversible.
- cost: Negligible model cost if previews are generated deterministically; small local state for undo manifests.  ·  latency: Adds near-zero latency for safe plans; previews add a turn only for consequential plans.
- security: Reduces accidental side effects and makes prompt-injection-driven actions visible before execution.
- depends on: Real Mac action risk gate; Read-only environment inspection; Per-action result and rollback contract


## What it asked for

_Nothing._
## Its own summary

Grounded in the actual stack, I proposed: weekday calendar/mail briefs with bounded redacted inputs and short audio; async cited web research using server-side Browser Run; safe Downloads cleanup with approval and rollback; draft-only email triage; a real Mac execute confirmation/audit gate; shared relevance-ranked memory/context pruning to reduce token cost; and preview-first, focus-preserving Mac interaction with undo. I also told mac-terminal the concrete needs for safe inventory and transactional file operations. These designs explicitly separate cheap background work from realtime conversation, cap audio/content costs, and require confirmation for external or destructive effects.

**Biggest unknown:** The owner’s exact privacy/approval defaults and the promised offline audio delivery/retry path remain unresolved. Those determine whether briefs may include mail subjects/names, which Mac actions can be allowlisted, and whether asynchronous results can reliably reach the pendant.

