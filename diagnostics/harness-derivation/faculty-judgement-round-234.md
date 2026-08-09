# Harness derivation — faculty-judgement — round 234

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make my morning brief dependable: resolve duplicate schedules, read only sources that are actually accessible, tell me what changed, and don't repeat it if I already heard it."
- **useful because:** Today the owner has two daily 07:00 briefs plus a 07:30 brief, and an apparently successful job is not proof that the calendar/mail were readable or that audio was delivered. This would produce one concise, source-honest brief, suppress duplicates, and retry only when the pendant did not receive or finish playback.
- **path:** relay → mac → browser → pendant
- **model tier:** Use the cheap deterministic policy/reconciliation path for schedule, permissions, freshness, deduplication, and attention; invoke the realtime model only to compress the already-verified findings into the owner's one-sentence spoken format.
- **latency:** Prepare in under 10 seconds before the scheduled window; speak immediately when a valid artifact is available, otherwise queue it without producing a false 'all clear'.
- **cost:** Usually <$0.01 per run; the dominant cost is one short realtime generation only when there is novel content.
- **security:** Calendar/mail/browser content must remain on the Mac unless the owner-approved briefing path permits it; secrets and sensitive subjects must be redacted before TTS. Never claim delivery from server completion: require the pendant downloaded/playback ACK, and keep a reviewable receipt.
- **missing:** A single owner-confirmed routine replacing the duplicate morning routines (the owner has not stated the desired brief time).; A writer from the Mac bridge into fleet memory or a durable deduplication record; the existing fleet-memory schema and routes have no production writer.; A scheduled invocation of briefing triage and a verified EventKit permission/empty-result check in every morning run.; A production join between relay job IDs and Mac job IDs, plus use of the accepted pendant delivery ACK queue.

### "Finish this browser task for me, but stop at the exact moment you need my login or two-factor code; tell me which site and what I must do, then continue automatically after I finish."
- **useful because:** The browser can already hold authenticated sessions that the Mac and relay cannot, but a task currently has no honest, user-centered handoff at a login wall. This turns a brittle failure into one short, contextual interruption and prevents the agent from guessing, asking for credentials, or abandoning the workflow.
- **path:** relay → mac → browser → pendant
- **model tier:** Use deterministic page-state and session-need classification for ordinary navigation and login-wall detection; use the realtime model only to phrase the short spoken request and interpret the owner's completion acknowledgement.
- **latency:** Detect a login wall within one browser poll (under 30 seconds today); after the owner completes it, resume within 2 seconds of the extension heartbeat and preserve the prior step idempotently.
- **cost:** <$0.01 for most tasks; model cost occurs only at the handoff and resume summary, not on every poll.
- **security:** Never transmit passwords, OTPs, page secrets, or form contents to the relay or pendant. The pendant should receive only site name, required interaction, expiry, and an opaque resume token. Require explicit owner confirmation before any external side effect after resumption, and expire the token when the browser session changes.
- **missing:** Activate the existing sessionNeedSignal/browserJobRunner island: its routes and scheduler are currently unreachable.; A typed browser-job state machine that distinguishes login required, MFA required, CAPTCHA, and ordinary failure, with a durable resume token and step idempotency.; A browser-extension event or heartbeat carrying only the handoff state; the current browser heartbeat does not expose semantic login completion.; A cross-surface job-id join so relay status, browser command, and Mac receipt can be shown as one task.

### "If you start something for me and the Mac, browser, or link dies, recover it safely or tell me exactly what remains—never leave me with a task that looks accepted but is silently stuck."
- **useful because:** A queued relay job can remain processing forever when the Mac dies, while browser commands have leases that are not swept automatically. The owner currently cannot distinguish 'still working' from 'orphaned' without inspecting several surfaces. This gives every delegated task a truthful outcome and a safe recovery path.
- **path:** relay → mac → browser → pendant
- **model tier:** Use a deterministic lease/recovery controller and autonomy policy for timeout, idempotency, reversibility, and retry decisions; use the expensive model only to summarize the final state when the failure is ambiguous or the next step needs judgment.
- **latency:** Detect a dead worker within 60 seconds, attempt only idempotent/reversible recovery automatically, and give the owner a concise status within 5 seconds of asking.
- **cost:** <$0.005 for ordinary lease checks; model cost only for an ambiguous recovery explanation.
- **security:** Never replay an external side effect merely because a worker disappeared. Revalidate the pending plan and receipts first, require owner confirmation for non-idempotent or destructive retry, and preserve a provenance chain from original request through each retry/cancel/undo.
- **missing:** Add lease_until and a requeue/expiry sweep to relay_jobs, using the working routine lease pattern.; Actually start the browser bridge supervisor so stale command leases are swept without a manual POST /browser/sweep.; Persist relay-job-id to Mac-job-id and browser-command joins; today localJobId is telemetry, not a queryable foreign key.; Expose a typed recovery outcome (recovered, already-completed, cancelled, needs-owner, permanently-failed) to the pendant inbox and status route.

### "Fact-check that for me before I repeat it: compare the public web with any relevant source I already have open, tell me what agrees or conflicts, and give me a confidence-labeled one-sentence answer with the sources I can ask to hear."
- **useful because:** The owner encounters claims while moving between conversations, browser pages, and research. Today the system can search or read a page, but it cannot perform a bounded, provenance-preserving comparison across public and authenticated context and expose disagreement rather than laundering one source into certainty. This would prevent confident repetition of stale or contradicted information without forcing the owner to open a laptop.
- **path:** pendant → relay → browser → mac
- **model tier:** Use a cheap deterministic evidence collector and contradiction detector first; call the expensive model only to normalize claims, judge whether two passages answer the same proposition, and produce the short spoken synthesis.
- **latency:** Return a provisional answer in 15 seconds and a cited final answer in 45 seconds; if sources remain contradictory, say so rather than extending the search indefinitely.
- **cost:** About $0.02–$0.08 per fact check, dominated by fetching and one synthesis call; cache content-addressed sources so a repeated claim is nearly free.
- **security:** Authenticated pages and private mail must never be sent to public search or an untrusted model. The owner must see which source classes were used, and a claim derived from private material must be marked before it can be spoken or used in an external action. Preserve raw evidence only under the existing retention/redaction policy and allow source revocation to invalidate the verdict.
- **missing:** A reachable, durable cross-check service: the existing crossCheck module is in-memory and unmounted, so it cannot survive a restart or be invoked by the pendant.; A typed claim/evidence model that links each conclusion to capsule IDs, URLs, capture times, and independent-source groups; browser provenance exists but its HTTP routes are also unmounted.; A source-boundary policy that explicitly separates public web, authenticated browser pages, local files, and mail before any model call.; An owner-facing spoken citation format and a follow-up action that can replay the disagreement without rereading sensitive excerpts.; A freshness and independence evaluator that detects syndicated copies, not merely two URLs repeating one wire story.

### "When I come back to my desk, tell me only what changed while I was away and restore the exact work context I left—open task, relevant browser page, unfinished job, and the next safe action."
- **useful because:** The owner should not have to reconstruct a half-finished thought after a walk, meeting, or disconnected pendant session. The system has separate Mac jobs, browser sessions, context handoff, and physical moment markers, but no owner-facing return brief that compares before/after state and refuses to resurrect stale actions.
- **path:** pendant → relay → mac → browser
- **model tier:** Use deterministic snapshots, timestamps, job receipts, browser session state, and stale-plan revalidation for the delta; use the realtime model only to compress the delta into one spoken sentence and rank the next safe action.
- **latency:** Capture a departure snapshot in under 1 second, build the return delta within 5 seconds of reconnection, and restore only after a fresh state check.
- **cost:** <$0.01 when no model synthesis is needed; one short generation for a nontrivial multi-surface delta.
- **security:** Snapshots must exclude passwords, page bodies, microphone audio, and private content unless explicitly requested. Never auto-resubmit a stale browser or Mac action; require policy evaluation and physical confirmation for external effects. A return summary must cite which state was observed and which was merely inferred.
- **missing:** A real cross-surface snapshot record joining the existing offline moment bookmark to relay, Mac, and browser state.; A departure/return event consumer on the relay; moment markers currently do not trigger a comparison.; A typed delta schema for opened context, unfinished jobs, changed pages, and safe next actions, with expiry.; A restore adapter that can reopen harmless context while leaving mutations staged for owner approval.

### "Warn me before the pendant becomes unreliable: turn its link, audio, and delivery measurements into a simple health trend, explain what is degrading, and prepare the smallest fix or bug report before it fails during a conversation."
- **useful because:** A UART anomaly is useful only after the owner has already experienced a bad call. The owner should get an early, measured warning—such as rising underruns, packet loss, decode saturation, or repeated checksum errors—with a reviewable diagnosis and an actionable fix, not a vague 'device offline' alert.
- **path:** pendant → relay → mac → browser
- **model tier:** Use deterministic rolling thresholds and trend detection for audio/link health; invoke the realtime model only to summarize correlated symptoms and choose between a local fix, a staged firmware change, or a draft issue.
- **latency:** Update health after each authenticated delivery/diagnostic batch; alert only after a sustained trend (for example three windows), and produce the owner summary in under 3 seconds.
- **cost:** <$0.01 per health window; model cost only when an anomaly crosses the configured warning threshold.
- **security:** Send opaque metrics and firmware/build identifiers, not microphone PCM or transcript, to the relay. A proposed firmware or configuration change must be reversible and require confirmation; bug drafts must be local/reviewable and never auto-file externally.
- **missing:** A durable time-series reducer for authenticated pendant diagnostics; the current UART parser can draft a report but does not maintain health baselines.; A relay-side join between diagnostic windows, audio delivery ACKs, and the originating pipeline artifact.; A signed device/build identity and monotonic metric sequence so offline replay and resets cannot create false trends.; A safe remediation catalog with measured rollback and acceptance tests for the already-shipped 24 kHz path.


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-visible capabilities: (1) a dependable, source-honest morning brief that deduplicates the four overlapping routines and counts pendant playback—not server completion—as delivery; (2) browser work that pauses at the exact login/MFA boundary without exposing credentials, then resumes safely; and (3) delegated work that detects orphaned Mac/browser/relay jobs, retries only after revalidation, and tells the owner exactly what remains. All three were recorded. The first and third are connective implementations over existing primitives, not new standalone routes.

**Biggest unknown:** I still need one owner decision before the morning brief can be made truthful as a promise: which single local schedule should survive (07:00, 07:30, or another time). Technically, the highest-value missing pieces are relay job leases/requeue, automatic browser-lease sweeping, cross-surface job-ID joins, and activation of the currently unreachable browser login-handoff runner. I do not need another permission request this round; calendar/mail readability and audio playback must remain explicit evidence rather than assumed success.

