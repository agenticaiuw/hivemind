# Harness derivation — faculty-judgement — round 23

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **audio-end-to-end** — The current prototype cannot honestly claim native 24 kHz end-to-end playback: pendant capture is 15,625 Hz, uplink is Opus 16 kHz, decode is 24 kHz but bridge resamples 31,250→44,100 and sends SBC-only A2DP; simultaneous codec work consumes ~87% of one core.
  - evidence: get_hardware_spec(audio) and get_hardware_spec(bridge): audio prototype specifies 15,625 Hz capture/16 kHz uplink and 24 kHz decode; HUZZAH32 bridge is SBC-only at fixed 44.1 kHz and has tight RAM.

## Capabilities it proposed

### "“Help me decide this.” Then give me the best option, what could change the answer, and let me choose it from the pendant without reopening all the tabs."
- **useful because:** The owner currently gets either raw account reads or an action attempt; nothing turns scattered private context into an explicit, revisable decision. This would make the judgement layer useful: gather evidence across calendar, mail, files, and logged-in pages, separate facts from assumptions, recommend an option, and preserve the decision so later work stays consistent.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action → dashboard
- **model tier:** Use a cheaper background model for evidence extraction and option comparison; use realtime only for the owner's spoken clarification and final one-sentence recommendation. Use the action model only after the owner selects an option.
- **latency:** First spoken acknowledgement under 1 s; evidence collection 5–20 s in background with progressive updates; final recommendation under 3 s after sources arrive. Pendant button: short press cycle options, long press select, second long press cancel.
- **cost:** Roughly $0.02–$0.10 per decision depending on number of private pages and transcript length; dominant cost is re-sending extracted context, so cache cited page fingerprints and pass only changed evidence.
- **security:** Private mail, calendar, files, and authenticated browser content leave the Mac/extension only as bounded extracted evidence, with source URL/tab, timestamp, and sensitivity labels. Never send, delete, purchase, or submit from a recommendation; require explicit spoken/button confirmation for those. Show uncertainty and stale evidence rather than inventing confidence. Current Accessibility/Screen Recording=false and browser offline must produce a truthful 'cannot verify' result, not a success claim.
- **missing:** A durable decision object containing question, options, evidence citations, assumptions, chosen option, expiry, and follow-up date; A cross-surface evidence merger that de-duplicates the same fact from Mac and browser and marks freshness; Pendant option browsing/selection and spoken replay of the recommendation; A permission/device-health preflight that blocks unverified GUI actions; A review queue/dashboard for changing or reopening decisions

### "“That’s wrong—fix it everywhere.” Then show me what future briefs, plans, reminders, and pending browser/Mac actions relied on the wrong fact, let me choose the replacements, and prevent the stale version from resurfacing."
- **useful because:** Today a correction in conversation does not reliably repair already-created plans or derived context. The owner needs a way to correct the mind once and have that correction propagate safely, instead of repeatedly fighting stale assumptions. This is a distinct capability from ordinary memory or action history: it traces dependency impact and repairs downstream artifacts.
- **path:** pendant → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Use a cheap background model to trace fact dependencies, compare replacement candidates, and generate repair patches. Use realtime only to ask for disambiguation and read the concise impact summary. Use the action tier only for explicitly approved repairs.
- **latency:** Acknowledge the correction in under 1 second; produce an impact list in 5–15 seconds; apply selected reversible repairs in the background and report completion. The pendant should be able to replay the affected-item count and pause the repair with its button.
- **cost:** Approximately $0.03–$0.15 per correction, dominated by dependency tracing over stored artifacts and changed-source rechecks. Avoid resending full context by retaining typed fact IDs, source hashes, and compact diffs.
- **security:** Corrections may involve sensitive personal data. Keep source content on the originating Mac/browser where possible and send only IDs, hashes, and bounded snippets to the relay. Never silently modify mail, purchases, deletes, or external submissions. Require confirmation for any irreversible repair and preserve before/after values with provenance.
- **missing:** A typed dependency graph linking facts to briefs, reminders, schedules, decisions, and queued Mac/browser actions; Fact supersession semantics with provenance, confidence, sensitivity, and effective time; A repair planner that produces reversible patches rather than rewriting history; Cross-surface invalidation events so relay, Mac, browser, and pendant stop using superseded facts; A review UI and pendant interaction for approving, skipping, or reopening individual repairs


## Changes it proposed to its own stack

### `hardware` — Replace the provisional ESP32-class HUZZAH32 audio bridge for the product with a BLE Audio-capable bridge (nRF5340 Audio or equivalent) that accepts negotiated 24 kHz mono PCM/LC3 from the relay path and presents a native 24/48 kHz headphone stream. Keep the current ESP32 as a compatibility fixture, but add a wire-format capability handshake and a 16 kHz fallback. Validate with long-run packet-loss, reconnect, and latency tests before calling a run successful.
- **owner gets:** Speech will remain intelligible and natural instead of being resampled through the bridge's fixed 31,250→44,100→SBC chain, and reconnects will not silently turn into missing audio. The owner gets the promised superwideband voice path in real use, not only in the relay logs.
- effort: Hardware redesign and board bring-up; LC3/A2DP dual-mode firmware; relay negotiation; pendant and headphone interoperability matrix; 3–5 engineering weeks plus prototype spins.  ·  risk: BLE Audio/headphone compatibility may be incomplete, and a new radio stack can introduce dropouts. Recover with the existing ESP32/SBC bridge and explicit 16 kHz fallback; gate every spoken quality claim on an end-to-end probe receipt containing negotiated codec, sample rates, packet-loss, and playout latency.
- cost: Approximately $15–$35 per bridge in low volume, plus prototype/PCB cost; roughly 20–80 mA active depending radio and codec. API cost is unchanged; fewer retransmitted or re-generated audio packets may reduce it slightly.  ·  latency: Expected 20–60 ms lower playout latency by removing the extra resampling/buffering stages; BLE Audio connection setup may add 0.5–2 s on reconnect.
- security: No new cloud data if the bridge only transports already-encrypted audio; pairings and keys remain on the bridge. Require authenticated firmware updates and erase keys on factory reset.
- depends on: Define and implement a versioned audio capability handshake across pendant, relay, and bridge; End-to-end 24 kHz acceptance tests, including packet loss and reconnect behavior; A truthful audio receipt that distinguishes encoded, delivered, decoded, and actually played frames

### `memory` — Add an append-only supersession and impact-tracing layer: every derived artifact stores the fact IDs and source snapshots it depended on; a correction creates a new fact version, marks affected artifacts stale, and emits repair candidates rather than mutating prior history. Require each consumer (relay prompts, scheduled routines, Mac jobs, browser watches, audio queue) to reject superseded facts unless explicitly pinned to the historical version.
- **owner gets:** When the owner corrects a date, preference, plan, or identity detail once, stale versions will stop leaking into later spoken briefs and computer actions. They can see exactly what was affected and repair only the pieces they approve.
- effort: Medium-to-large schema and integration change: fact-version storage, dependency edges, invalidation events, repair-plan API, and adapters for routines, jobs, browser watches, and audio items; add migration for existing artifacts.  ·  risk: Incomplete dependency capture could leave one stale artifact active, while over-invalidation could create noise. Recover with conservative default blocking for high-impact actions, explicit provenance on every artifact, and a rebuild job that audits unlinked consumers.
- cost: Small storage/indexing increase; roughly 1–5% additional background model cost for impact summaries, with no realtime cost unless the owner asks. No hardware cost.  ·  latency: Normal responses gain a small lookup cost; correction impact analysis should complete in seconds asynchronously. High-risk actions may wait for freshness verification.
- security: The graph must inherit each fact's sensitivity and access scope; do not expose private source text merely because an artifact depends on it. Audit all supersession and repair decisions.
- depends on: A durable typed fact store with provenance and sensitivity labels; Cross-surface event delivery and job cancellation/invalidation; Reversible repair operations and truthful completion receipts


## What it asked for

_Nothing._
