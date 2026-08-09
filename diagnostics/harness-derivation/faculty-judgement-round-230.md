# Harness derivation — faculty-judgement — round 230

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Did I actually hear everything important today?”"
- **useful because:** The system currently treats a relay/Mac job being completed as if the owner received it. A delivery-aware daily answer would reconcile generated, downloaded, started, finished, interrupted, checksum-error, and no-audio states, then tell the owner only what still needs attention. It would eliminate the most dangerous kind of automation success: work done but never heard.
- **path:** relay → mac → pendant → dashboard
- **model tier:** background for reconciliation and ranking; realtime only for the short spoken answer
- **latency:** Under 5 seconds on demand; no polling model calls. Read receipts and delivery ACKs, then one cheap ranking pass.
- **cost:** Usually <$0.01 per invocation; dominated by a small background ranking call, with receipt/ACK reads effectively free.
- **security:** Speak titles/statuses, not source content, unless the existing owner policy permits it. An ACK proves device delivery/playback state, not that the owner understood the content. Require provenance links for every missing-item claim and show the raw reason (offline, checksum error, interrupted, never downloaded).
- **missing:** A durable query joining relay job IDs, Mac job IDs, audio artifact IDs, and pendant delivery events (the current IDs are not a shared foreign key); A scheduled reconciliation job that reads record_pendant_delivery_event data and job receipts; A policy field distinguishing 'finished playback' from 'owner acknowledged'

### "“Give me the three things in the world I should know, and tell me what actually changed since yesterday.”"
- **useful because:** The owner repeatedly asks for short world/US headlines, but a headline list is not a personal brief: it can repeat yesterday, collapse disagreement, or sound current when a source is stale. This capability would maintain a source-linked change ledger, separate genuinely new developments from continuing stories, expose disagreement instead of inventing certainty, and deliver exactly three short spoken sentences with a reviewable source trail.
- **path:** browser → mac → relay → pendant
- **model tier:** background model for clustering, novelty and disagreement; realtime only to answer follow-up questions about one cited item
- **latency:** Run on the existing morning schedule in 20–60 seconds; the spoken result should begin within 3 seconds after the owner asks, using the latest completed ledger and clearly saying when refresh is still running.
- **cost:** Roughly $0.03–$0.15 per scheduled brief depending on source count; web fetches and long article extraction dominate, not the short synthesis.
- **security:** Public sources may contain prompt injection and untrusted instructions; treat page text as evidence only. Never imply a source was read if the browser was offline. Preserve URL, capture time, source excerpt digest, and model confidence. Do not read private browser tabs unless the owner explicitly asks for them.
- **missing:** A durable per-story change ledger keyed by canonical story identity and source capture time; A freshness/novelty evaluator that can say unchanged, updated, contradicted, or unresolved; A single scheduled run that coalesces the existing duplicate 07:00/07:30 brief jobs before speaking; An owner-facing correction path that records 'that was wrong/not useful' without silently changing news policy

### "“Can you check that my pendant is actually understandable before you rely on it for an important briefing?”"
- **useful because:** A downloaded-and-finished artifact is not proof that speech was intelligible. This gives the owner a one-minute, privacy-safe audio health check: relay sends a known short sentence, the pendant plays it, the owner presses the existing auxiliary marker button if it was clear, and the Mac/bridge records codec latency, underruns, packet loss, and the owner's result. Important briefings can then fall back to the Mac or remain queued when the audio path is degraded.
- **path:** relay → pendant → mac → dashboard
- **model tier:** No expensive model for the test; use deterministic test vectors and metrics. Use the background model only to summarize repeated failures and recommend a fallback.
- **latency:** Interactive test completes in 10–20 seconds; metrics are emitted immediately and the result is available before a scheduled briefing is released.
- **cost:** Near-zero model cost; a small generated test artifact and a few signed events. Hardware cost is $0 on the current board.
- **security:** Use synthetic text or a fixed non-sensitive phrase, never replay owner speech. The owner confirmation is a usability signal, not biometric evidence. Do not mark the path healthy from a delivery ACK alone; require an explicit confirmation or label the result unconfirmed.
- **missing:** A signed audio-health test artifact type and a release gate that can hold or reroute a briefing; Firmware handling for the auxiliary sw1 press as 'heard clearly' during a test without creating a normal moment marker; A relay/Mac result record joining test artifact, device metrics, and owner confirmation; A deterministic fallback action that sends the briefing to the Mac or leaves it in the existing alert inbox

### "“What important things did you know about but not tell me today, and why?”"
- **useful because:** Today silence is ambiguous: an item may have been intentionally deferred, suppressed by attention policy, blocked by permissions, missed because a browser was offline, or never observed at all. This gives the owner an omission audit rather than making them guess whether the system failed. It reports only item IDs, source, decision, policy rule, and recovery option until the owner asks for content.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic aggregation first; use the background model only to group related omissions and produce a concise spoken summary.
- **latency:** Under 3 seconds from durable decision logs; no live browser crawl unless the owner explicitly requests a recheck.
- **cost:** Near-zero API cost for normal use; one small background summarization call when there are many omitted items.
- **security:** The audit itself can reveal sensitive subject matter, so default spoken output must use opaque titles or counts and obey the existing sensitivity/redaction path. It must distinguish 'not observed' from 'observed and suppressed' and never claim an absence from a source that was unreadable. Opening a deferred item's content requires the existing owner confirmation rules for external effects.
- **missing:** A durable record for every attention decision, including suppress/defer/coalesce and the named policy rule; A first-class 'not observed because source unavailable' outcome, separate from empty source results; A cross-surface query joining briefing triage, browser-watch reports, routine/job failures, permissions, and pendant delivery state; A spoken/dashboard view that offers retry, queue, or inspect without silently changing the original decision

### "“Before you change anything, show me what you would have done under a different situation.”"
- **useful because:** The owner cannot safely tune interruption and autonomy behavior by trial and error. A counterfactual run would replay a real event against an alternate attention/autonomy policy or surface state—pendant offline, owner busy, source unreadable—without sending mail, clicking, speaking, or mutating state. It exposes which rule changes the outcome and lets the owner adopt the policy deliberately.
- **path:** dashboard → relay → mac → browser → pendant
- **model tier:** Deterministic policy replay; no realtime model required. Use a background model only to phrase the comparison after the rule-level diff is computed.
- **latency:** Under 2 seconds for a stored event; never perform a live recheck unless separately requested.
- **cost:** Effectively zero for stored replay; small background summarization cost only for a multi-event comparison.
- **security:** Replay must be side-effect free and operate on redacted evidence by default. Label stale or hypothetical inputs clearly. Never let a counterfactual approval token become executable; any real action still requires the normal policy and confirmation path.
- **missing:** An immutable decision receipt containing inputs, matched rules, policy version, and the alternatives considered; A pure replay endpoint that accepts an event plus alternate context/policy without invoking action executors; A dashboard diff showing ACT/PREPARE/QUEUE/ASK changes and source freshness; Owner storage for named policy scenarios, separate from the active policy

### "“What rules about me changed, who changed them, and can I undo just that change?”"
- **useful because:** Policies, memory facts, briefing settings, and permissions can influence behavior, but the owner has no single change history. A scoped policy-diff view would show the old and new value, source, timestamp, affected surfaces, and the exact behaviors changed; undo would revert only that version rather than wiping unrelated memory or preferences.
- **path:** dashboard → relay → mac → browser → pendant
- **model tier:** Deterministic diff and provenance lookup; no expensive model needed except optional plain-language narration.
- **latency:** Under 2 seconds for history and rollback preview; rollback requires explicit owner confirmation and should apply atomically.
- **cost:** Negligible API cost; durable append-only policy records are the main storage cost.
- **security:** Policy history may expose sensitive preferences and must remain local/dashboard-readable by default; the pendant should speak only a redacted summary. Rollback must be scoped, idempotent, and blocked if the current version no longer matches the version being reverted. Never allow a spoken transcript alone to rewrite a policy.
- **missing:** Versioned durable storage for briefing, attention, autonomy, disclosure, and routing policy changes; A provenance link from each decision receipt to the policy version it used; A preview-and-confirm rollback endpoint with optimistic concurrency; A clear distinction between owner-authored policy, system default, and inferred recommendation


## Changes it proposed to its own stack

### `integration` — Add a delivery-aware release controller for important audio. Before enqueueing, it attaches one stable artifact/brief-item ID; after generation it waits for a bounded pendant delivery window. On no_audio, checksum_error, repeated interruption, or stale device ACK, it stops retrying blindly, invokes cross-surface preflight, and offers the owner a short Mac-speaker fallback or leaves the item in the durable pendant inbox. A single receipt records the exact branch and never counts server generation as owner delivery.
- **owner gets:** Important information will not silently disappear just because the server succeeded. The owner gets one honest fallback instead of duplicate speech, endless retries, or a false 'done.'
- effort: Medium: join IDs across the relay/Mac pipeline, add a small release state machine, and wire the existing ACK/event and Mac audio actions.  ·  risk: A transient LTE outage could delay a briefing or cause an unwanted Mac fallback. Recover with a conservative timeout, owner-visible 'queued/not heard' state, idempotency key, and explicit disable switch; never auto-send the same audio twice.
- cost: Negligible API cost; one small state record and existing event writes. Mac fallback uses local TTS/audio resources.  ·  latency: Adds up to the configured delivery wait for important items; ordinary low-priority items remain queue-only.
- security: Fallback must pass the same spoken-content redaction policy as pendant audio. Do not expose raw error payloads or private briefing text in relay logs.
- depends on: A durable relay-job/Mac-job/artifact join (currently only telemetry localJobId exists); The accepted audio_delivery_ack_queue firmware behavior; A policy value defining which items are important enough to wait or fall back; A safe Mac audio executor path


## What it asked for

_Nothing._
## Its own summary

Produced four owner-facing proposals: (1) a delivery-aware answer to “did I actually hear everything important?”, (2) a source-linked “what changed since yesterday?” news brief, (3) a privacy-safe pendant intelligibility test using the existing auxiliary button, and (4) a delivery-aware release controller with Mac fallback for failed audio. The recorder accepted all four; the first three are intentionally connective capabilities, and the fourth makes the owner-visible behavior concrete.

**Biggest unknown:** The owner’s explicit release policy is still unknown: which briefings are important enough to wait for pendant delivery or fall back to Mac audio, and whether a failed pendant delivery should interrupt immediately or remain queued. Implementation also still needs a durable relay-job/Mac-job/artifact join; current ACK and receipt primitives exist but do not share a queryable foreign key.

