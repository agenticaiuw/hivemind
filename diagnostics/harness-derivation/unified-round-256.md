# Harness derivation — unified — round 256

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser readiness** — The Mac agent and relay are healthy; Accessibility and Screen Recording are currently granted for AI Pendant Agent, browser extension is online with one Safari tab and zero pending/spooled commands, and the relay reports macBridgeOnline=true.
  - evidence: GET /ops/snapshot returned agent.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser.online=true, pendingCommands=0, spool.spooled=0, relay.reachable=true.

## Capabilities it proposed

### "When I say “continue that conversation,” resume the last interrupted turn from the exact point it stopped, without making me repeat myself."
- **useful because:** A dropped LTE session currently turns a real conversation into a cold restart. The relay can retain a bounded turn handoff, the Mac can provide the last local transcript/state, and the pendant can identify the next deliberate press; together they restore continuity no single surface can.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background for turn summarization and handoff indexing; realtime only for the resumed spoken reply
- **latency:** Acknowledge the resume press within 300 ms; reconstruct the handoff in under 2 s; never block on browser or Mac if relay context is sufficient.
- **cost:** ~$0.002–$0.01 per interrupted turn depending on whether summarization is needed; storage and relay reads dominate less than model context.
- **security:** Store only a bounded redacted handoff, not an open microphone buffer. Bind it to conversation/session and expire after 24 h; require the pendant's next deliberate press, and never replay an action merely because a conversation resumed.
- **missing:** A production turn-handoff record with sequence, last spoken/recognized spans, pending response state, and expiry; A resume trigger that the pendant emits after reconnect or next press; A deterministic deduplication rule so the same interrupted turn cannot be answered twice

### "Before you carry out a staged action, tell me exactly what changed since I approved it, and let me approve only the changed parts from the pendant."
- **useful because:** An approval that was valid when prepared can become misleading when a browser page, file, or calendar changes. A cross-surface delta lets the owner make a narrow informed decision instead of blindly rerunning or discarding the whole plan.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background/deterministic hashing for world comparison; realtime only to read the concise delta aloud
- **latency:** Compute the delta in under 1 s for local files and browser snapshots; speak a three-line summary within 2 s; no model call for unchanged plans.
- **cost:** Usually <$0.001 per check; occasional small realtime summary, with browser snapshot and hashing latency dominant.
- **security:** The pendant receives only opaque plan IDs, field labels, and redacted before/after summaries—not secrets or page contents. Invalidate the old approval on any unclassified change; require a fresh physical approval nonce for changed irreversible steps.
- **missing:** A typed world-delta schema shared by Mac and browser evidence; Partial re-approval semantics for changed steps, rather than all-or-nothing plan approval; Relay persistence for the delta and its expiry across a disconnected pendant

### "At the end of the day, ask “what did I start but not finish?” and let me close, defer, or hand off each item from the pendant."
- **useful because:** The system can currently execute jobs, create reminders, and record commitments, but those are separate worlds. A daily unfinished-work pass would join interrupted Mac/browser jobs, pending physical approvals, and spoken commitments into one owner-visible queue, reducing silent half-done work.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model for clustering and phrasing; deterministic joins and expiry first; realtime only when the owner asks for an item
- **latency:** Precompute in the background before the configured evening window; first spoken item under 500 ms; each close/defer action gets a receipt within 2 s.
- **cost:** ~$0.01–$0.05 per daily digest depending on item count; most work is deterministic joins over existing receipts and evidence.
- **security:** Only include items explicitly initiated by the owner or bound to an owner utterance; do not infer private obligations from ambient audio. Show provenance and source surface for every item, require physical approval for external/irreversible handoffs, and expire stale items rather than nagging forever.
- **missing:** A unified unfinished-item projection with provenance, owner-visible status, and expiry; A reliable distinction between completed, failed, abandoned, and awaiting-owner items across job/commitment records; Pendant actions for close/defer/hand-off that return an idempotent receipt

### "Never let a sensitive browser or Mac action run unless my pendant is physically nearby and I have just confirmed on it."
- **useful because:** A stolen or unattended Mac session should not be enough to send a message, approve a purchase, or alter an account. The worn device becomes a presence-and-intent boundary that the browser, Mac, and relay can all enforce.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic cryptographic checks; no model required except optional owner-facing explanation
- **latency:** Presence check under 150 ms for an already paired session; fail closed on timeout or link ambiguity.
- **cost:** Negligible per action; hardware pairing and relay verification dominate engineering cost.
- **security:** BLE proximity alone is not proof of possession and can be relayed, so combine rotating proximity attestations with a fresh physical approval nonce and short expiry. Never expose the device key or account secrets to the browser. Safe fallback is refusal, not execution.
- **missing:** A real paired-device identity and rotating proximity-attestation protocol; Mac and browser enforcement hooks that refuse high-risk actions when the attestation is absent or stale; A relay-verifiable binding between the physical approval latch and the exact staged action; Product pendant radio/antenna design that supports low-power proximity while LTE is idle

### "Tell me what materially changed in my logged-in accounts since I last checked, with the exact site and evidence, without taking any action."
- **useful because:** The browser can reach sessions nobody else can, while the pendant is the fastest way to ask. A read-only change digest could surface unexpected orders, messages, subscriptions, or security settings before they become emergencies, without granting the system permission to fix anything.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model for summarizing already-collected diffs; deterministic DOM/structured-data extraction and hashing first
- **latency:** Precompute on a user schedule; answer a targeted site query in under 5 s, with no model call when nothing changed.
- **cost:** ~$0.01–$0.10 per digest depending on sites and snapshot size; browser reads and storage are the main costs.
- **security:** This is exceptionally sensitive. Bind each monitored site explicitly, redact secrets and message bodies by default, retain hashes/field-level diffs rather than full pages, and require a fresh spoken/physical confirmation before opening or reading protected content aloud. No auto-remediation.
- **missing:** Explicit per-site watch declarations and a baseline snapshot store; A privacy-preserving structured diff extractor for browser pages; A redacted evidence viewer and pendant speech policy that never reads sensitive fields by accident

### "When I say “I’m driving” or press the safety control, put every surface into a distraction-free travel mode and prove it stayed that way until I release it."
- **useful because:** A single spoken intent should stop the Mac and browser from surfacing nonessential notifications, prevent the relay from pushing queued audio, and leave the pendant with only essential safety cues. Today those surfaces have separate focus and queue behavior, so the owner must police each one.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic policy/state machine; realtime only to acknowledge the owner's command
- **latency:** Pendant mute and local cue under 100 ms; Mac/browser/relay convergence receipt within 2 s, with any unconfirmed surface reported rather than claimed stopped.
- **cost:** Near-zero model cost; engineering is in cross-surface state propagation and convergence receipts.
- **security:** Do not infer driving from ambient audio or location. Require an explicit spoken phrase or physical control, persist the mode across link loss, and make emergency/owner-selected allowlisted alerts the only exception. The owner must be able to inspect and clear the mode locally.
- **missing:** A shared travel-mode state with monotonic version and expiry/clear semantics; Mac notification/focus and browser queue enforcement; Relay suppression of nonessential pending speech plus a convergence receipt; A dedicated physical safety control or reuse of the accepted privacy latch without conflating their meanings


## Changes it proposed to its own stack

### `hardware` — Add a tiny low-power haptic actuator and driver to the production pendant, with firmware-defined short patterns for privacy-latch enter/exit, staged-transaction pending/approved/cancelled, and offline outbox acknowledged. Keep patterns local and deterministic; do not use it as a second data channel.
- **owner gets:** The owner gets unmistakable private confirmation while wearing the device in a noisy room or when audio is muted. Today a single LED is hard to see and spoken confirmation can itself disclose that a sensitive action occurred.
- effort: Small PCB/mechanical addition plus a compact driver and pattern table; validate skin-contact comfort and button/LED interaction. The current DK remains a software/LED prototype.  ·  risk: An overly strong or frequent vibration is annoying and can expose device presence. Enforce bounded pulse energy, rate-limit noncritical patterns, and provide a firmware setting to disable all but privacy and approval safety cues.
- cost: Approximately $0.30–$1.50 BOM and brief pulse power (tens of mW while active); negligible average draw with under-200 ms patterns.  ·  latency: Immediate local feedback, under 20 ms after the button/state transition; no relay or model latency.
- security: Improves confirmation clarity but is not authentication; preserve the existing physical approval nonce and privacy latch semantics. Patterns must not encode secrets or account details.
- depends on: local_privacy_latch firmware behavior; physical_transaction_approval_latch firmware behavior; a product pendant PCB/enclosure rather than the current development kit; owner choice of whether haptics are acceptable during quiet or sleep periods


## What it asked for

_Nothing._
## Its own summary

Round 256 produced three owner-facing capabilities: exact interrupted-conversation continuation, world-delta narration with partial re-approval, and a daily unfinished-work pass; plus a hardware proposal for private haptic confirmation. Live discovery also found the Mac agent, relay, browser, Accessibility, and Screen Recording all healthy/granted, with zero pending browser commands. The single most useful is conversation continuation: a dropped turn should resume at the exact boundary instead of forcing repetition.

**Biggest unknown:** The pendant itself is still offline/unregistered, so the remaining product-critical unknown is the real LTE-M reconnect/resume path and its event schema. I also still need the owner's explicit policy for which unfinished items may be auto-deferred versus which must wait for physical approval; I did not invent that policy.

