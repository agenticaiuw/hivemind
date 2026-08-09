# Harness derivation — faculty-judgement — round 267

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Every morning, give me one brief I can trust. Tell me what matters, say explicitly what you could not read, and never replay an item the pendant already confirmed I heard."
- **useful because:** The current system can produce a plausible all-clear from an unauthorised calendar, has no briefing scheduler, and cannot join generated audio to actual pendant playback. This would make the brief honest about blind spots and genuinely stateful instead of repeating or silently losing important items.
- **path:** relay → mac → pendant
- **model tier:** background model for collection/ranking; realtime model only for the owner's follow-up questions
- **latency:** Prepare within 30 seconds of the configured morning time; spoken delivery starts only after the Mac-side evidence and attention decision are complete.
- **cost:** Roughly $0.01–$0.05 per brief, dominated by one background synthesis call; reads and delivery receipts are local/relay I/O.
- **security:** Calendar/mail content must pass the existing redaction boundary before TTS. Permission failures must be spoken as uncertainty, never as 'nothing'. Default to headlines and deadlines, with private details requiring the owner's later request. No external mutation occurs.
- **missing:** A real scheduler for runBriefingTriage/briefing delivery (the existing 07:00 policy only ranks; it does not fire).; A permission-aware calendar/reminder adapter that treats the corroborated empty-pair result as unreadable, not clear.; A durable join from briefing item ID to audio artifact and pendant playback ACK, using the granted delivery-event and audio-item primitives.; A policy-controlled handoff from the Mac result to attention arbitration; the current briefing policy is still a placeholder until the owner sets it.

### "If my Mac or the browser bridge dies halfway through something I asked, recover it and tell me exactly whether it finished, was safely retried, or needs me—without running a duplicate action."
- **useful because:** Today an in-flight relay job can remain stuck in processing for up to its TTL after a Mac crash, while browser command leases can also expire without a single owner-facing conclusion. The owner should not have to guess whether an email draft, file change, or browser step happened.
- **path:** relay → mac → browser → pendant
- **model tier:** Cheap deterministic recovery worker for lease/receipt reconciliation; realtime model only to explain an ambiguous outcome to the owner.
- **latency:** Detect an orphan within 1–2 minutes, reconcile receipts immediately on reconnect, and speak a compact result on the next available attention window.
- **cost:** Near-zero model cost for normal recovery; occasional $0.01–$0.03 explanation call when receipts conflict or the action is ambiguous.
- **security:** Fail closed when an external side effect may have happened but lacks a receipt. Retry only idempotent/reversible steps with the existing action identity; never auto-retry sends, purchases, deletion, or other destructive work. Expose evidence and require physical approval for a fresh irreversible attempt.
- **missing:** Relay job leases (lease_until/heartbeat), an expiry sweep, and a durable relay-job ↔ Mac-job mapping; the current localJobId is only telemetry.; A recovery state machine that distinguishes no-start, completed, interrupted, and unknown rather than treating processing as terminal.; A browser-bridge supervisor that actually starts; today its stale-command sweep is imported but never invoked.; One owner-facing reconciliation record that joins relay job, Mac receipt, browser command, and pendant delivery ACK.

### "Forget everything you know about [a person, project, or topic]—show me every copy you found, then erase or retract it everywhere you control."
- **useful because:** There is currently no global forget operation. Deleting a capture leaves its context-graph copy; revoking evidence leaves derived facts; the graph has no TTL; and fleet-memory retractions are designed but never written. A person should be able to revoke a topic, not hunt through unrelated stores and hope.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic local matcher and cascade executor; use the realtime model only to resolve an ambiguous topic match after presenting candidates.
- **latency:** Show a reviewable inventory in under 10 seconds for local stores; execute only after explicit confirmation, then return per-store completion and any unerasable tombstones.
- **cost:** Usually no model cost; $0.01–$0.05 only when natural-language topic resolution needs model help. Storage and relay writes dominate, not inference.
- **security:** Default to preview-only and exact/strong matches; never delete based on a vague name collision. Preserve minimal audit tombstones and hashes where required, but remove raw text and invalidate downstream prompt projections. Propagate revocations to relay, Mac, browser provenance, context graph, facts, evidence capsules, voice-note audio, and queued brief items. A spoken request cannot erase secrets without a confirmation/readback that does not repeat them.
- **missing:** A durable cross-store provenance link (especially capsuleId/source IDs on derived facts and graph entities).; A global topic index and cascade implementation spanning facts.json, context_graph.json, evidence capsules, browser provenance, voice notes/audio, fleet memory, and relay context.; A relay writer for fleet-memory retraction events and a durable revocation epoch that offline pendant queues honor on reconnect.; A review endpoint that reports matched records, deletion versus tombstone semantics, and failures before mutation.

### "Why didn’t you tell me about that? Show me the exact reason an item was spoken, queued, deferred, suppressed, or never seen—and let me change only the rule that caused it."
- **useful because:** An assistant that stays silent is currently indistinguishable from one that never checked, lost a source, misclassified urgency, hit quiet hours, or failed to deliver audio. The owner needs an auditable explanation of absence, not only receipts for actions that happened.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic explanation over stored policy matches, source-health results, attention decisions, and delivery events; use the realtime model only to turn the trace into a short spoken answer.
- **latency:** Answer a recent 'why not?' in under 3 seconds from durable traces; older investigations may take 10 seconds to gather cross-surface evidence.
- **cost:** Near-zero for the trace query; at most $0.01 for a natural-language explanation when many causes conflict.
- **security:** Do not read private suppressed content aloud merely to explain suppression. Speak the category and rule name, with sensitive details available only in the local dashboard after confirmation. Every explanation must distinguish 'not observed' from 'observed and suppressed'. Policy edits require explicit owner confirmation and must not retroactively replay a backlog without a second decision.
- **missing:** A durable attention-decision journal: each candidate needs source freshness, policy version, matched rule, disposition, expiry, and delivery outcome.; A negative-evidence record for unavailable or unauthorised sources, so 'not seen' cannot be confused with 'clear'.; A stable join across briefing item, attention event, audio artifact, pendant ACK, and policy evaluation; current namespaces do not provide this.; A narrow policy-edit operation that changes one named rule and previews the consequences before taking effect.


## Changes it proposed to its own stack

### `interaction` — Make every path into synthesizePendantSpeech pass through one mandatory delivery firewall: classify the text, apply the safe sentence-level withholding routine, consult the owner-configurable speak/do-not-speak policy, and attach the source/evidence IDs to the resulting audio artifact. Reject or downgrade any secret/private content that bypasses the briefing path instead of trusting callers to redact first.
- **owner gets:** A private email, credential-like note, or browser result should never be read aloud merely because it came through a different route. Today pendantSpeech and audioBrief have no confidentiality gate; the owner gets safety consistently across ordinary answers, confirmations, and briefs.
- effort: Medium: centralize the gate, update all speech call sites, add adversarial tests for sentence-shaped secrets and unclassified browser/mail text, then verify with real pendant playback.  ·  risk: False positives could make useful confirmations vague; recover with a screen/dashboard detail view and an explicit owner policy override. A fail-open caller must be treated as a bug, not a reason to bypass the gate.
- cost: No meaningful API cost; small local CPU/latency for classification and redaction, likely under tens of milliseconds.  ·  latency: Adds one local pass before synthesis; no extra model round trip.
- security: Strongly improves least-disclosure behavior, but does not itself authorize outbound destinations. Keep originFanOut/httpPolicy and the existing redaction classifier as separate controls.
- depends on: The owner-configurable disclosure policy must remain unset/conservative until the owner decides what may be spoken.; Fix or consistently use withheldOrEmpty rather than the known-broken sentence path in maskSecretValue.; Attach audio artifact IDs so delivery ACKs and provenance can prove what was actually spoken.


## What it asked for

_Nothing._
## Its own summary

This round produced four owner-facing changes: a truthful, delivery-confirmed morning brief (the highest-value one), crash-safe cross-surface job recovery without duplicate actions, global topic erasure with reviewable propagation, and a universal spoken-content privacy firewall. I also established that the granted autonomy evaluator is still only a schema and not a callable implementation, so proposals must not claim it is enforcing decisions.

**Biggest unknown:** The owner still has not specified the actual disclosure and interruption policy: which content may be spoken aloud, quiet windows, and what qualifies as an emergency. Until they do, all new briefing and speech behavior must ship conservative, policy-driven defaults and clearly label uncertainty rather than inventing those preferences.

