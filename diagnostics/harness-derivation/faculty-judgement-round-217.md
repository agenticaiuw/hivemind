# Harness derivation — faculty-judgement — round 217

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask for today's news, give me three short spoken sentences that are genuinely from the last 12 hours, with the source time and a one-tap/one-press way to hear the citations later; if freshness or source agreement is insufficient, say that instead of filling the gap."
- **useful because:** The owner has repeatedly asked for this and the system has repeatedly returned failed or empty results. This would make a daily high-value answer trustworthy rather than merely fluent.
- **path:** relay → browser → mac → pendant
- **model tier:** Use the slower background model for source collection and deduplication; use realtime only to answer the spoken request and announce the compact result. Browser reads source pages; relay enforces freshness and source diversity; Mac stores the cited draft; pendant receives the short audio and a queued citation item.
- **latency:** First spoken answer within 5 seconds from cached sources; otherwise say 'still gathering' and deliver within 2 minutes. Source collection may run in the background.
- **cost:** About $0.03-$0.15 per brief depending on article extraction; realtime cost is limited to the three-sentence rendering. Browser and relay I/O dominate, not model tokens.
- **security:** Only public URLs leave the device. Never treat a search snippet as evidence. Require two independent sources for a headline, record publication and retrieval timestamps, and redact any accidental personal content before speech. No external posting or account login.
- **missing:** freshness-bounded news collector with source timestamps; article identity/deduplication and independent-source check; citation audio item schema linked to the spoken brief; scheduled delivery that uses the existing attention arbiter instead of duplicate routines

### "Tell me the real battery state of both the Mac and the pendant, and warn me before either one will interrupt a conversation or fail to deliver audio—not just when I ask 'what is the battery percentage'."
- **useful because:** The owner has already asked for battery percentage, but the pendant currently has no battery gauge and Mac and pendant health are separate. A single forecast prevents silent loss of conversations and queued replies.
- **path:** pendant → relay → mac → dashboard
- **model tier:** No expensive model for telemetry; a deterministic relay rule computes remaining-runtime risk. Use realtime only for the one-sentence spoken warning and background model only if it must explain an unusual drain pattern.
- **latency:** Telemetry update every 60 seconds while connected; warning within 10 seconds of crossing a policy threshold. Dashboard can show the last-known value and its age.
- **cost:** Negligible API cost; a small authenticated telemetry packet and one relay decision per interval. Hardware addition is roughly $1-$3 BOM and under 1 mA quiescent draw.
- **security:** Battery telemetry is low sensitivity but must be authenticated to prevent false emergency warnings. Show 'unknown/stale' rather than extrapolating after link loss. Never claim a pendant percentage until hardware measurement exists.
- **missing:** fuel-gauge IC or calibrated ADC path on the pendant and firmware telemetry packet; relay model of audio minutes remaining from measured codec/radio load; Mac bridge adapter that reports Mac battery and charging state; cross-surface warning policy and dashboard age/unknown presentation

### "When something I asked for fails, tell me exactly what failed, which surface was unavailable or returned no actions, whether retrying is safe, and offer the smallest corrected retry—without pretending it succeeded."
- **useful because:** The owner's history contains many indistinguishable 'failed' and 'No actions provided' outcomes. Turning those into a clear, safe recovery path saves repeated commands and makes the hive feel like one reliable assistant.
- **path:** relay → mac → browser → pendant
- **model tier:** Deterministic classification first using receipts, preflight, and route status; invoke the slower model only to summarize ambiguous evidence into one owner-facing sentence. Realtime should not infer a success that receipts do not show.
- **latency:** Under 2 seconds for an existing job failure; no new action is issued automatically. A corrected retry is prepared immediately and runs only after owner confirmation when side effects are possible.
- **cost:** Usually under $0.01 because it is receipt/status joins; ambiguous failures may cost a small model call. No new recurring spend.
- **security:** Read-only diagnosis by default. Retry tokens must be idempotent and bound to the original intent, never replay destructive or externally visible actions silently. Include evidence references and distinguish transport failure, permission denial, empty plan, and target-side rejection.
- **missing:** stable relay-job to Mac/browser-job correlation (currently only telemetry localJobId); structured failure taxonomy populated at each executor boundary; receipt-backed retry planner that feeds autonomy_policy_evaluate; owner-facing failure inbox with deduplication

### "Let me say, 'I have ten minutes—what is the one thing I should do now?' and receive a single defensible recommendation that weighs deadlines, unfinished work, current location/app context, and the cost of switching; if the evidence is incomplete, tell me which missing fact would change the recommendation."
- **useful because:** The system can currently list tasks, plans, reminders, mail, and browser state, but it cannot make a time-bounded judgement about the best next action in the owner's actual life. This is the core value of a judgement agent: reducing competing obligations to one honest next move rather than producing another dashboard.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use a background model to maintain compact candidate summaries from durable facts and receipts; use realtime only for the final spoken recommendation when the owner asks. Deterministic policy ranks deadlines, reversibility, travel/context fit, and estimated duration before the model explains the choice.
- **latency:** Under 3 seconds for a spoken answer using recent state; if a source is stale, answer with a bounded recommendation and identify the stale source rather than waiting indefinitely.
- **cost:** Roughly $0.01-$0.05 per request when summaries are cached; the expensive part is refreshing mail/browser/calendar evidence, not the final judgement.
- **security:** The recommendation may expose sensitive obligations aloud, so the spoken result must contain only the selected action and a safe rationale unless the owner requests detail. Never execute the action automatically. Every candidate and exclusion needs source references, freshness, and an explanation of uncertainty.
- **missing:** a read-capable unified obligation view covering reminders, calendar, mail, browser work, and active jobs; duration and context metadata for candidate tasks; a deterministic time-budget ranking policy with owner-editable weights; a compact recommendation record that can be audited after the fact

### "After I finish something, learn whether your time estimate and recommendation were actually useful, and gradually personalize future 'what should I do now?' answers without silently changing priorities."
- **useful because:** A judgement assistant that never learns the owner's actual task durations, energy patterns, or rejected recommendations will remain generic. This turns outcomes into explicit calibration rather than hidden profiling.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Use deterministic outcome matching and a cheap background model to summarize corrections. Realtime is only for an occasional concise question such as 'Was that estimate useful?' and never for silently rewriting policy.
- **latency:** No added latency to normal actions; calibration can happen asynchronously. The owner should see a proposed preference change before it affects recommendations.
- **cost:** Under $0.01 per completed task for aggregation; occasional background summarization is the dominant cost.
- **security:** Store only derived duration/error preferences with source and expiry, not raw conversations. Separate observed facts from inferred preferences. The owner can inspect, correct, or delete each learned weight; no learning may override explicit deadlines or safety policy.
- **missing:** an outcome link from recommendation to completion or rejection; owner-confirmed calibration event schema; durable cross-surface memory writer and retraction path; dashboard showing learned weights and their evidence

### "At any time, let me ask, 'What did the pendant hear, save, send, and play today?' and get a complete, source-linked privacy ledger with missing acknowledgements and a one-step way to revoke or forget each item."
- **useful because:** The owner cannot currently distinguish microphone capture, uploaded audio, generated speech, playback, and durable notes. A daily accounting would make the wearable trustworthy instead of opaque, especially across dropped links and offline queues.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Use deterministic joins over device delivery ACKs, pipeline receipts, audio-retention records, notes, and provenance. Use realtime only to summarize the ledger into one short spoken answer; never infer an ACK that is absent.
- **latency:** Under 2 seconds for a day-sized local ledger; reconcile delayed pendant events in the background and visibly mark the ledger incomplete until they arrive.
- **cost:** Negligible for local joins; a small model cost only when the owner requests a natural-language summary. Storage grows with compact event metadata, not PCM.
- **security:** The ledger itself is sensitive and must be local-first, redacted in spoken output, and protected behind explicit dashboard detail. Revocation must distinguish deleting local audio, retracting derived claims, and invalidating remote copies; no silent promise of deletion where propagation is unavailable.
- **missing:** a unified audio lineage record from capture through upload, transcription, synthesis, and playback; durable cross-surface event correlation and offline replay reconciliation; global forget propagation across facts, graph, capsules, relay, and device queues; dashboard and spoken-safe privacy-ledger views


## What it asked for

_Nothing._
