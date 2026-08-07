# Harness derivation — faculty-perception — round 119

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-input-reachability** — At 2026-08-07T17:57:31Z, AI Pendant Agent is running but Accessibility is false, Screen Recording false, input probe failed, and ui_click/ui_menu/type_text/press_keys may report success while doing nothing; AppleScript automation grants remain present.
  - evidence: GET /observe 200: accessibility.trusted=false, screenRecording=false, inputReachability.status=failed, uiActionsWillReachTheScreen=false, consequence explicitly warns receipts cannot be trusted; GET /ops/status confirms same.
- **browser-live-state** — Safari browser bridge is online with extension v1.2.0, three tabs, and zero pending commands, but its current heartbeat tab is https://example.com titled 'Failed to open page'; durable sessions include Gmail inbox and two probe tabs.
  - evidence: GET /browser/status and GET /ops/status at 2026-08-07T17:57:26-31Z.
- **pendant-registration** — The Mac agent's live route table has no /v1/devices/status route; current discover(devices) shows only online home-macbook-bridge and offline cloudflare-contract-test, with no registered nRF9160 pendant.
  - evidence: discover(devices) and authenticated GET /v1/devices/status returned 404 No such route.
- **timezone-conflict** — Machine context reports timezone America/New_York while owner memory previously reports America/Chicago; timezone is unresolved and must not be silently selected for scheduling or spoken relative times.
  - evidence: GET /machine-context 200 reports America/New_York; mac-terminal independently reported owner memory America/Chicago.

## Capabilities it proposed

### "Before you do anything consequential, tell me plainly which parts of my system are reachable and trustworthy right now—what you can read, what you can change, and what may silently fail—and then use only the trustworthy path."
- **useful because:** Today the agent can claim a click succeeded even when Accessibility is absent, and can treat an online browser bridge with a failed tab as healthy. A single preflight gives the owner an honest answer before wasted or dangerous actions, with a spoken reason and a safer fallback (AppleScript, browser extraction, or draft-only).
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for routine preflight; realtime only when the owner is waiting for the answer
- **latency:** Under 2 seconds for cached state; under 5 seconds if fresh Mac/browser/relay probes are needed
- **cost:** Low: deterministic aggregation of /observe, /ops/status, /browser/status and relay device state; occasional background model only to phrase ambiguity
- **security:** Never expose tab contents in the preflight unless requested. Treat missing Accessibility as a hard no for GUI input, and distinguish automation grants from screen-control grants. Require confirmation before selecting a fallback that changes state.
- **missing:** A unified signed perception snapshot joining Mac permissions, browser heartbeat/tab health, relay registration, and pendant telemetry; Action router support that consumes capability/trust verdicts instead of trusting optimistic receipts

### "When I say “today,” “tonight,” or give a meeting time, ask only if it is genuinely ambiguous; otherwise show me the timezone you used and keep every reminder, briefing, and spoken countdown consistent with it."
- **useful because:** The live Mac says America/New_York while owner memory says America/Chicago. Silent choice can shift reminders and meeting preparation by an hour. A perception-backed timezone contract makes relative time dependable across pendant speech, relay jobs, Mac Calendar, and browser accounts.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic for conversion and conflict detection; background model only for a concise clarification question
- **latency:** Immediate for known zones; one short turn only when sources conflict
- **cost:** Negligible compute; one background completion only on an unresolved conflict
- **security:** Timezone is metadata, but calendar and travel pages are private. Show source and effective date; never infer location from browser/IP without consent. Require explicit confirmation before changing the authority.
- **missing:** An authoritative timezone record with source, validity interval, and owner-confirmation state; Timezone propagation into relay scheduling, spoken relative-time rendering, and Mac/browser job payloads

### "If a page or device is broken, say exactly what failed, recover what you safely can, and leave me an evidence-backed partial result instead of pretending the task completed."
- **useful because:** The browser is online but its current tab is a failed page, while private Gmail is available in another session; the Mac GUI path is also nonfunctional. The owner should receive a useful partial answer (for example, “Gmail inspected, example.com unavailable, no action sent”) and a repair option, not an optimistic success receipt.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for failure classification and partial-result summarization; realtime only for interactive recovery approval
- **latency:** Initial diagnosis under 3 seconds; recovery may continue as a background job
- **cost:** Low-to-moderate: deterministic health probes first, then one small background synthesis; browser reads dominate latency
- **security:** Never retry a form submission or message send automatically. Preserve source URL/tab/session and failure evidence. Any fallback from GUI to browser or AppleScript must be disclosed and confirmed when effects differ.
- **missing:** A cross-surface failure taxonomy and provenance-preserving partial receipt; Recovery policy that routes around failed GUI input, stale tabs, and absent pendant registration without treating optimistic acknowledgements as proof

### "“What is actually true right now?” Give me one synchronized, spoken situation report across my Mac, browser, relay, and wearable—what each can see, what each can do, when it was last witnessed, and every contradiction between them."
- **useful because:** Today the owner must mentally reconcile separate optimistic job receipts, browser heartbeats, Mac permissions, and a missing pendant. A cross-surface witness report would expose stale or contradictory state before it becomes a false belief, especially when one node has gone offline.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic evidence aggregation first; background model only to compress contradictions into speech
- **latency:** Fresh report within 3 seconds when all surfaces respond; explicitly mark any source that times out
- **cost:** Low: parallel authenticated probes and compact evidence records; model cost only for natural-language compression
- **security:** Do not include private tab contents by default—only health, capability, timestamps, and source identifiers. Sign snapshots and prevent one stale source from overwriting newer contradictory evidence.
- **missing:** A cross-surface witness protocol with synchronized timestamps, freshness windows, source identity, and contradiction records; Relay endpoint exposing authoritative device registration and delivery acknowledgements; A spoken/dashboard view that distinguishes observed, inferred, and unknown

### "When you answer me about something you saw or did, let me tap “show me the proof” and hear or see the exact source, timestamp, and unambiguous reason you believe it—without making me trust a green success receipt."
- **useful because:** The current system can report success for GUI input that never reached the screen, and a browser can be online while a tab is a failed page. The owner needs inspectable evidence attached to each claim, not just an outcome string, so they can catch silent failures and decide whether to retry.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** deterministic provenance lookup; no expensive model unless the owner asks for a plain-language explanation
- **latency:** Under 1 second for stored evidence; under 4 seconds for a fresh read-only verification
- **cost:** Low storage and lookup cost; verification may add one Mac/browser probe
- **security:** Redact secrets, message bodies, tokens, and unrelated tabs. Proof must be read-only and must never replay an action. Retain only hashes/snippets by default with explicit owner expansion.
- **missing:** A claim-level evidence object linking every spoken assertion and action receipt to source observations and freshness; Adapters that refuse to call optimistic UI receipts proof; Pendant gesture and dashboard affordance for proof-on-demand

### "If I lose connection, switch machines, or put the pendant away, keep a small ‘what changed while I was away’ envelope: only confirmed events, with the exact gap in observation, and let me ask for it when I return."
- **useful because:** The owner currently has no registered pendant and disconnected or stale surfaces can make an absence look like no change. A bounded return envelope would preserve meaningful, confirmed changes across relay sleep, Mac/browser downtime, and wearable absence without inventing continuity.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background event normalization; deterministic retention and gap marking; realtime only when the owner asks on return
- **latency:** Events captured asynchronously; return summary in under 2 seconds from durable state
- **cost:** Low-to-moderate D1/storage cost for compact event envelopes; background summarization only when multiple events need grouping
- **security:** Encrypt private event metadata, honor per-source retention, and clearly label unobserved intervals. Never infer that nothing happened during a gap; require confirmation before turning an event into an action.
- **missing:** A durable cross-surface event envelope with explicit observation gaps and acknowledgement semantics; Per-source privacy/retention policy and replay-safe deduplication; Reconnect hook from pendant/relay and browser/Mac heartbeat recovery


## What it asked for

_Nothing._
## Its own summary

Round 119 established fresh live truth: Mac bridge and Safari extension are online, but the browser heartbeat tab is a failed example.com page; Accessibility and Screen Recording are absent, input reachability failed, and GUI actions may silently no-op despite optimistic receipts. No pendant is registered, and machine timezone America/New_York conflicts owner memory America/Chicago. I recorded all four findings, notified judgement/terminal, and proposed three owner-facing capabilities: trust-aware preflight routing, an explicit timezone contract, and evidence-backed partial failure/recovery. Hardware inspection also confirms the pendant is prototype-only (one button/LED, one shared full-duplex I2S) and SD is failure-buffer-only.

**Biggest unknown:** Which timezone the owner authoritatively wants, and whether/when they will manually grant Accessibility and Screen Recording to the exact AI Pendant Agent binary. The system still lacks a unified, signed perception snapshot and a live relay device-registry route; those are what I still need to make trust verdicts authoritative rather than assembled from separate probes.

