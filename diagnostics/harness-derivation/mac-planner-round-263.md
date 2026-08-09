# Harness derivation — mac-planner — round 263

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-observation-2026-08-09** — The live Mac is currently controllable by AI Pendant Agent: Accessibility trusted, synthesized events posting, Screen Recording true, secure input false; Safari is foreground with four durable browser sessions/tabs. The granted mac_readonly_inspect browser_tabs operation is currently ambiguous between action:browser_inspect and POST /browser/inspect and did not invoke either.
  - evidence: mac_readonly_inspect running_apps and foreground_app both invoked GET /observe at 2026-08-09T00:51:47Z and returned accessibility.trusted=true, eventsPost=true, screenRecording=true; browser_tabs call returned unresolved ambiguity.

## Capabilities it proposed

### "When I come back to my Mac, say a 90-second handoff of what changed since I left: calendar, unread mail, and the browser work I had open, with only items that need action."
- **useful because:** The owner currently has to reconstruct state across Safari, Mail, Calendar, and the pendant. A return-to-desk handoff turns the Mac's durable sources and the browser's live sessions into one spoken, time-bounded answer, while the pendant supplies the moment of return and the relay remembers the last handoff checkpoint. This is the single most useful daily behavior: useful without opening an app and genuinely cross-node.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Cheap background model composes and ranks the diff; realtime model speaks only the final brief if requested from the pendant.
- **latency:** Capture checkpoint under 1 s; source reads 3-8 s; speech begins within 5 s of the return request.
- **cost:** Usually <$0.01 per handoff; dominated by one small summarization call, not source reads.
- **security:** Mail snippets and authenticated tab URLs leave the Mac only as redacted, ranked deltas; never transmit page bodies by default. Require an owner-configured policy entry for which browser sessions and mail account may be included.
- **missing:** A durable leave/return checkpoint keyed to the pendant bookmark or Mac idle/active transition; A browser-inspection resolver that disambiguates action:browser_inspect from POST /browser/inspect; A relay endpoint that merges checkpointed source diffs into a spoken payload

### "Run a bench health check on the pendant and audio bridge, then leave me a dated pass/fail report on the Mac and tell me over the pendant exactly which stage failed."
- **useful because:** The chips are physically attached to this Mac today, and audio failures have previously been found only after subjective listening. A one-command, cross-node acceptance run would turn the USB-connected hardware from a hidden engineering dependency into something the owner can trust before a call. It exercises both directions, records numbers, and makes failure actionable instead of silently degrading a conversation.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Background/cheap model parses the fixed fixture counters and writes the report; realtime is used only to announce a failure during an active call.
- **latency:** 2-5 minutes for the fixture and report; no impact on normal calls because it is explicitly on-demand.
- **cost:** Near-zero API cost; dominated by local fixture execution and serial log collection.
- **security:** The fixture must never capture microphone content. Store only sequence numbers, timing, packet-loss, decode, clipping, and underrun counters. USB execution must be an explicit owner-invoked bench routine, with a clearly labelled report and no modem credentials or audio payloads.
- **missing:** A bounded bench runner that can arm audio_path_diagnostic_fixture over the currently connected USB serial devices and collect its completion marker; A parser/validator implementing the shipped acceptance thresholds (alias rejection, CPU, mic drops, tx_starved, and silent preamble); A durable report receipt linked to the relay job and surfaced through the pendant inbox

### "Package what I am looking at into a dated research packet: the relevant browser pages, a concise source summary, and next actions saved in my workspace, then tell me on the pendant where it was saved."
- **useful because:** The owner can read and browse, but turning a live authenticated session into a durable, navigable artifact still requires several surfaces. This captures the exact tabs he chose, preserves URLs and access time without copying secrets by default, produces a useful summary, and leaves a file he can reopen or hand to another agent. It is more reliable than asking the owner to remember which tab mattered.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model extracts and summarizes page text; realtime is unnecessary unless the owner dictates the packet request conversationally.
- **latency:** 10-30 s for 1-5 pages; acknowledge immediately on the pendant and report completion asynchronously.
- **cost:** <$0.03 per packet for five modest pages; page extraction and summarization dominate.
- **security:** Respect authenticated-session boundaries: include only explicitly selected tabs, redact tokens/forms/password fields, and never upload page bodies unless the owner has enabled it. Write atomically to a configured workspace and return a receipt, not an arbitrary path. Saving or sharing outside the workspace requires explicit owner policy.
- **missing:** A deterministic browser snapshot/read action that resolves without the current inspect-route ambiguity and returns selected-tab content with redaction metadata; A relay orchestration route that binds the pendant's current bookmark/request to browser command IDs and a Mac workbench transaction; A citation-preserving summarizer that records source URL, title, timestamp, and extraction confidence alongside the prose

### "Save this exact browser task for tomorrow. Preserve where I am, what I was trying to do, and the safe next step, then resume it later without making me log in again or lose the authenticated session."
- **useful because:** Today an interrupted authenticated workflow is either left in a tab, forgotten, or restarted from scratch. This would let the owner safely defer work across sleep, travel, and link loss while preserving intent rather than merely saving a URL. The pendant supplies the defer command, the relay keeps an encrypted continuation record, the browser retains the session boundary, and the Mac resumes only the explicitly recorded next step.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model extracts task state and proposes a bounded next step; realtime is used only for the owner's spoken defer/resume interaction.
- **latency:** Checkpoint in under 3 seconds; resume preview within 10 seconds after the Mac and browser reconnect.
- **cost:** Under $0.02 per checkpoint/resume, dominated by state summarization; storage and browser command traffic are negligible.
- **security:** Never copy cookies, passwords, tokens, or full page bodies into relay storage. The browser extension must retain session material locally and expose only an encrypted opaque session handle, redacted task state, URL origin, and expiry. Resumption must stop at the recorded safe step if page structure or authorization changed; submission, purchase, sending, deletion, or other external effects require the owner's existing policy decision.
- **missing:** A browser-side encrypted session escrow primitive that stores a local opaque handle plus an expiring, resumable task state; A relay continuation record with lease, origin binding, schema version, and interruption-safe checkpoint semantics; A Mac/browser resume coordinator that can revalidate the page and return a deterministic preview before taking the next action; A pendant command and durable inbox receipt for checkpointed tasks, including expiry and failure states

### "If I lose my Mac or think an authenticated session is exposed, revoke the browser sessions everywhere, preserve an incident record, and tell me on the pendant what was successfully locked down."
- **useful because:** The owner currently has no single action that spans the wearable, always-awake relay, browser-held sessions, and Mac receipts. A pendant-originated lockdown would turn a stressful security incident into one bounded command, while preserving enough evidence to distinguish requested, attempted, and confirmed revocations.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Realtime handles the short emergency interaction; a cheap background worker reconciles revocation receipts and retries only idempotent operations.
- **latency:** Acknowledge locally within 1 second; issue revocation commands within 5 seconds; final confirmed/unknown report within 30 seconds.
- **cost:** Usually under $0.02 per incident; dominated by browser-provider API calls and receipt reconciliation.
- **security:** The command must be authenticated by the pendant's local privacy/security state and relay identity, not by a browser page. Do not expose tokens to the relay or Mac. Revocation should be origin/session scoped when requested, with an unmistakable 'all sessions' option; failures must be reported rather than claimed as success. The owner must configure which providers may be revoked unattended.
- **missing:** A relay emergency-control route with replay protection and a short-lived incident identifier; Browser-extension/provider adapters that revoke or invalidate sessions without exporting cookies; A pendant-resident emergency acknowledgment path that works while the LTE link is unavailable and queues the request safely; A receipt reconciler that reports confirmed, attempted, and unreachable providers separately

### "Undo the whole thing I just asked you to do, across the Mac and browser, and show me exactly what was restored and what could not be undone."
- **useful because:** Today a multi-step request can leave a mixture of files, browser mutations, and external effects with no owner-level answer to 'put it back.' A cross-node transaction would make delegated work comprehensible: the owner gets one receipt describing completed, compensated, and irreversible steps instead of manually hunting through apps and tabs.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime interprets the short undo request and reads the receipt; a background worker executes compensation plans and reconciles results.
- **latency:** Immediate acknowledgment; preview of the compensation plan within 3 seconds; completion typically under 30 seconds, with long-running items reported asynchronously.
- **cost:** Under $0.03 for ordinary jobs; dominated by browser revalidation and any model-generated compensation plan.
- **security:** Never pretend an external send, purchase, deletion, or third-party mutation was undone. Each action needs an explicit compensation or 'irreversible' status, with before-state hashes where safe and no secret contents in receipts. The owner must configure whether compensation may run unattended; otherwise produce a precise plan.
- **missing:** A cross-surface transaction manifest linking relay jobs, Mac action receipts, browser command IDs, and resource versions; Compensation handlers for reversible Mac and browser mutations, with stale-state checks before restoring; A durable owner-facing receipt format that distinguishes restored, skipped, failed, and irreversible effects; A pendant command path that can target the most recent job unambiguously


## What it asked for

_Nothing._
