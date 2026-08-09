# Harness derivation — faculty-judgement — round 198

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **cross_surface_preflight availability** — The granted cross_surface_preflight schema is unresolved in the live inventory; a call returns no implementation and nearest matches are GET /origins/budget, POST /research/briefings/:id/speech, and action:browser_read_page.
  - evidence: Live tool call in round 198 returned resolution=unresolved.
- **autonomy policy availability** — The granted autonomy_policy_evaluate schema is unresolved in the live inventory; it cannot currently evaluate or explain a proposed action.
  - evidence: Live tool call in round 198 returned resolution=unresolved; nearest routes were GET/POST /briefing/policy.
- **briefing reconciliation confidence** — A request to reconcile timezone, permissions, scheduled briefings, browser connectivity, audio queue, and goals resolved ambiguously to POST /briefing with low confidence 0.458 and was not invoked because it has side effects.
  - evidence: Live reconcile_personal_state call returned resolvedTo POST /briefing, invoked=false, confidence band low.

## Capabilities it proposed

### "Did I actually hear that, and did you actually finish it?"
- **useful because:** Today generation, relay acceptance, download, and playback are easy to conflate. The owner needs one answer that distinguishes 'the model produced it', 'the Mac/relay accepted the action', 'the pendant downloaded it', and 'the owner heard it', including an interruption or checksum failure. This is the single most useful trust feature for a wearable assistant: it prevents both false reassurance and needless repetition.
- **path:** relay-realtime → pendant → mac-planner → dashboard
- **model tier:** background for receipt reconciliation; realtime only for the short spoken answer
- **latency:** Under 500 ms when receipts are already indexed; up to 3 s to reconcile a fresh pendant ACK
- **cost:** Usually <$0.001 per query; dominated by no model call, with occasional cheap summarization for a long history
- **security:** Speak only the status and artifact label, never raw audio or transcript. Require provenance for every transition and show 'unknown' rather than infer playback from download. External actions still use the existing physical-consent policy.
- **missing:** A durable join key from relay job/audio artifact to Mac action and pendant event; An indexed read endpoint that folds generated/accepted/downloaded/played/interrupted states; A spoken status formatter that consumes record_pendant_delivery_event and job receipts

### "Remember this decision across the whole hive—and forget it everywhere when I say so."
- **useful because:** A preference or decision currently becomes a Mac-local fact, graph copy, browser residue, or inherited text with no reliable cross-node writer or deletion cascade. The owner should be able to state it once, have every body use the same version, inspect its sources, and revoke it without stale copies silently steering future actions.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background model only when normalizing an utterance into a typed fact; deterministic storage, projection, and revocation thereafter
- **latency:** Acknowledge the capture in under 1 s; cross-node projection under 5 s; revocation must return a per-surface completion report, not pretend instant deletion
- **cost:** <$0.002 per new decision if normalization needs a model; reads/revocations are storage calls
- **security:** Never persist raw secret text in a normalized claim. Keep source links and sensitivity, require explicit confirmation before a claim influences an external mutation, and fail closed if one surface cannot acknowledge revocation. Dashboard may reveal provenance; spoken relay gets a redacted explanation.
- **missing:** A writer from Mac/extension/relay into the existing fleet-memory event route; capsuleId/source linkage on local facts and graph entities; A fan-out revocation worker spanning facts, graph, browser provenance, inherited fleet memory, and cached context; Durable cross-surface correlation and an owner-facing partial-failure report

### "Give me the best answer now, then check it on the Mac and browser and correct me only if it changes."
- **useful because:** A wearable should not force the owner to choose between instant help and trustworthy help. The relay can speak a clearly-labelled provisional answer immediately, while the Mac and authenticated browser gather evidence; the pendant then delivers a concise correction or confirmation tied to the same utterance. This makes low-latency conversation useful without laundering an unverified guess into fact.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** realtime for the provisional sentence; background for evidence gathering and comparison; no expensive model when the verified result is unchanged
- **latency:** First spoken sentence in 1 s; verification target 10 s; correction must interrupt only when materially changed and otherwise join the next brief
- **cost:** <$0.01 typical; realtime first pass plus cheap background extraction, with browser/Mac work dominating time rather than tokens
- **security:** Provisional content must be explicitly marked uncertain and cannot authorize mutations. Evidence snippets are redacted before TTS; corrections carry source/provenance and expire with the question. A dropped link leaves the provisional state as unverified rather than silently upgrading it.
- **missing:** A durable utterance-level correlation ID spanning relay, Mac, browser, and audio artifact; A typed provisional/verified/corrected state with expiry and supersession; A background verifier and a policy hook into attention_arbitrate so only material corrections interrupt; A pendant playback control path that binds a correction to the currently spoken item

### "Learn from the decisions I correct—but show me exactly what you learned before it changes how you act."
- **useful because:** The system currently has static policy knobs and scattered receipts, so every correction disappears as a one-off event. The owner should be able to turn repeated approvals, rejections, edits, and undos into an inspectable calibration profile: for example, 'you usually want drafts without asking, but never send messages automatically.' The profile must be proposed, not silently adopted, and should explain which observed outcomes support each suggested change.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background model for clustering repeated corrections; deterministic counters and policy evaluation for enforcement; realtime only to acknowledge a correction.
- **latency:** Record each correction immediately; produce a suggested calibration after 5–20 relevant outcomes or on request; no added latency to the original action.
- **cost:** Usually <$0.005 per calibration suggestion; storage and deterministic aggregation dominate, with occasional background classification.
- **security:** Corrections can reveal sensitive work habits and must remain owner-visible only by default. Never infer permission for destructive, financial, public, or credential-bearing actions. A suggestion requires explicit owner approval, has an expiry, and carries the exact evidence events behind it.
- **missing:** A durable event schema joining owner corrections, approvals, edits, undos, and action outcomes across surfaces; A calibration store separate from factual memory, with versioning and expiry; A deterministic diff showing how a proposed policy version would change future decisions; An owner approval flow that updates autonomy policy only after explicit confirmation

### "Show me what you would have done last week under a different rule, without actually doing any of it."
- **useful because:** Policy changes are currently abstract knobs. The owner needs a safe counterfactual replay: compare the current policy with a proposed one over real historical jobs, approvals, refusals, and pending items, and show which actions would have been acted on, queued, or blocked. This turns autonomy settings into something the owner can understand before trusting them.
- **path:** dashboard → relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** Deterministic replay and policy evaluation first; background model only to summarize a large diff; realtime for a short spoken result.
- **latency:** Under 3 s for a week of receipts; under 15 s for a month; strictly read-only and never blocks live work.
- **cost:** <$0.003 per replay; primarily local/relay receipt scans, with optional cheap summarization.
- **security:** Historical records may contain private targets or snippets. Dashboard can reveal full provenance only after local authentication; spoken output exposes counts and categories, not content. Simulation must use immutable snapshots and reject any executor call.
- **missing:** A normalized historical action/event log with policy inputs and outcomes; A pure replay mode that cannot reach Mac, browser, relay mutation, or pendant delivery paths; Stable policy-version snapshots and a structured diff of decisions; A redacted owner-facing report with links to the evidence for each changed decision

### "Give me a visible daily risk budget for autonomous work, and stop before I cross it."
- **useful because:** A yes/no permission model cannot express that the owner is comfortable with many harmless drafts but only a small number of externally visible, costly, or hard-to-undo actions. A risk budget would let the owner delegate routine work while guaranteeing a bounded blast radius. Every action would reserve and then settle budget based on its actual effect; failed or undone actions would be visible rather than silently consuming trust.
- **path:** dashboard → relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** Deterministic accounting and autonomy policy evaluation; background model only for classifying ambiguous actions; realtime for warnings and budget exhaustion.
- **latency:** Budget check under 100 ms before an action; settlement immediately after its receipt; no model call on ordinary actions.
- **cost:** Negligible API cost; dominated by durable ledger writes and occasional classification.
- **security:** The budget is a safety limit, never permission to bypass physical consent for irreversible actions. Spend, audience, reversibility, and uncertainty must be explicit. Budget state is private, owner-editable, versioned, and fail-closed if settlement is ambiguous or a surface disappears.
- **missing:** A typed risk-cost taxonomy and owner-configurable budget dimensions; Atomic reservation/settlement/refund ledger across relay, Mac, and browser; Policy integration that refuses or queues actions when a budget is exhausted; A dashboard and pendant warning that identify the action class and remaining budget without exposing private targets


## What it asked for

_Nothing._
