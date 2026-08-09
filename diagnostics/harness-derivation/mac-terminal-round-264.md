# Harness derivation — mac-terminal — round 264

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device reachability round 264** — Safari on MacIntel and home-macbook-bridge are online; nrf9160-pendant is currently reported offline despite USB bench hardware being physically attached. iOS pairing probe is also offline.
  - evidence: discover(devices) returned Safari online, home-macbook-bridge online, nrf9160-pendant offline, ios-brain-pairing-probe offline.

## Capabilities it proposed

### "I was interrupted. Tell me what I was doing on the Mac, what the browser had open, which action (if any) was in flight, and give me the shortest safe way to resume."
- **useful because:** The system currently knows these facts in separate places, but the owner must reconstruct them manually. A single spoken resumption card would turn an interruption into a 20-second recovery instead of lost context. It is genuinely hive-level: the pendant supplies the interruption request, the Mac supplies foreground/project/job state, the browser supplies authenticated-tab context and provenance, and the relay compresses it into speech.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for assembling the state card; realtime only to read it aloud and answer follow-up questions
- **latency:** First spoken answer within 3 seconds; state collection should be bounded to 1 second and use cached snapshots where possible.
- **cost:** Usually one cheap synthesis/context pass, roughly $0.005-$0.03; no screenshot or large page body should be sent unless the owner explicitly asks.
- **security:** Do not speak secrets, tokens, or full page contents by default. Browser output must be limited to title/origin/task status, with provenance links available on request. Require confirmation before replaying a pending mutation; merely reporting state is safe.
- **missing:** A durable interruption/resumption record joining a pendant request timestamp to the Mac job, ledger, active project, and browser session.; A relay formatter that ranks active work over stale tabs and says when its evidence is old.; A browser summary endpoint returning tab title/origin/task status without page secrets.

### "Before you tell me an important answer, check whether it is still true on my Mac and in the browser; if something changed, say what changed and fix only the stale part."
- **useful because:** This prevents the most damaging hive failure: a cloud answer based on an old Mac state or an expired authenticated page. The relay can reason over the last known context, the Mac can re-read local state, and the browser can re-snapshot the live session. The owner gets answers that distinguish remembered facts from current facts, plus narrowly targeted repair instead of blindly repeating a whole workflow.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** cheap/background verifier for routine freshness checks; realtime only when the owner is waiting or the discrepancy needs conversation
- **latency:** Under 2 seconds for a normal status/answer check; under 8 seconds when a browser snapshot is needed. Never block on a full page crawl.
- **cost:** $0.003-$0.02 per verification, dominated by browser snapshot/page text; local Mac checks should be zero model cost.
- **security:** Only access the specific host/tab/app named or implied by the answer. Do not upload arbitrary page text to the relay; send extracted claims plus URL/time/provenance. Any repair that changes a document, sends a message, or submits a form requires the existing action semantics and an explicit owner confirmation.
- **missing:** A freshness ledger that stores claim timestamp, source node, URL/app identity, and a cheap revalidation recipe.; A planner that can issue read-only probes first and produce a minimal repair plan when one claim is stale.; A consistent spoken distinction between current, cached, and unverifiable facts.

### "When I walk away from the Mac, keep working privately: pause sensitive spoken output, finish only safe background work, and give me a compact catch-up when the pendant is back."
- **useful because:** A worn assistant should not broadcast authenticated work or personal data into a room after the owner has left. This uses physical reachability as an actual privacy boundary rather than a cosmetic online indicator: the pendant/bridge observes link truth, the Mac classifies queued work, the browser holds sessions without reading them aloud, and the relay queues a redacted digest until return.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** cheap policy/routing model for classifying work and redacting the digest; realtime only for the return-time catch-up conversation
- **latency:** Mute or divert output within 500 ms of verified pendant loss; return catch-up within 2 seconds after reconnection.
- **cost:** Near-zero while idle; about $0.005-$0.02 for a return digest. Local link state and job classification should not invoke the expensive model.
- **security:** Treat link loss as ambiguous for a short debounce window, never as proof of owner absence. Default to withholding sensitive speech, not deleting work. Store only encrypted, bounded summaries; expire them after delivery. The owner must be able to override the policy from the pendant or dashboard.
- **missing:** A signed presence/absence lease shared by pendant, Mac bridge, and relay, with debounce and stale-age semantics.; A sensitivity label on jobs, browser commands, and pending speech so safe work can continue without content leakage.; A reconnect digest queue that reports completed/failed/stale work without replaying private page text.

### "Keep this objective alive until it is actually achieved: work through the authenticated browser and Mac, notice when a human decision or a changed page blocks you, ask me one precise question through the pendant, then continue from the same point without restarting."
- **useful because:** Today the owner can ask for a browser action or a Mac job, but not hand over an outcome that survives page changes, interruptions, relay restarts, or a missing decision. This would make the hive an accountable delegate rather than a sequence of disposable commands: it would maintain a bounded objective, preserve evidence of what has already happened, and escalate only the smallest unresolved choice.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** A cheap background planner and browser verifier should own the long-lived objective; use the realtime model only for the short clarification conversation on the pendant.
- **latency:** Accept an objective immediately and acknowledge within 2 seconds. Resume polling or browser work within 30 seconds of a relevant event. A clarification should reach the pendant within 3 seconds of detecting a genuine blocker.
- **cost:** Approximately $0.01-$0.10 per objective depending on page changes; most polling and state comparison should be deterministic, with model calls only for changed content or ambiguity.
- **security:** The objective must have an explicit scope, expiry, and action budget. Never infer permission to send, purchase, delete, or submit from the objective alone. Store browser provenance and a complete action/evidence trail; redact credentials and page secrets from relay prompts. The pendant question must identify the exact decision and the consequence of each choice.
- **missing:** A durable objective state machine with checkpoint, expiry, retry budget, blocker classification, and escalation state.; Exactly-once continuation across Mac jobs, browser commands, relay restarts, and changed authenticated pages.; A pendant-addressable clarification queue that binds the owner's answer to one objective and rejects stale answers.; A verifier that can distinguish successful outcome from merely completed clicks or a page that looks similar.

### "For the next hour, you may handle routine replies and scheduling for this project, but never send, buy, delete, or expose private content without asking; show me what authority is active and let me revoke it from the pendant."
- **useful because:** The owner currently has either one-off commands or broad agent trust, not a visible, temporary authority they can grant across the relay, Mac, and authenticated browser. A spoken, expiring delegation lease would make autonomy practical without forcing the owner to repeat the same boundary on every step. It is a user-facing control over what the hive may do, not a narrow execution gate.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap deterministic policy evaluation should enforce the lease; use the realtime model only to parse the initial spoken scope and resolve ambiguity.
- **latency:** A grant or revocation should be acknowledged locally within 500 ms and propagated within 2 seconds. Every action should evaluate the current lease without an extra model round trip.
- **cost:** Under $0.01 per grant, dominated by one parsing call; enforcement is local and effectively free.
- **security:** The lease must be signed, scoped by surface, action class, project/host, and expiry, with fail-closed behavior after clock or link uncertainty. Never let a browser page expand the lease. The dashboard and pendant must show active scope, last use, and revocation status. Revocation must cancel queued work where possible and mark already-running work clearly.
- **missing:** A cross-node signed delegation lease and revocation protocol.; A common action vocabulary mapping Mac shell, browser commands, relay jobs, and pendant requests to effects without blocking the owner's maximum-access mode by default.; A pendant-readable authority summary and an audit view showing exactly which action consumed the lease.

### "While I am speaking with someone, quietly keep a factual side-channel: look up only what I ask about, signal uncertainty in my ear, and after the conversation give me a sourced list of commitments and follow-ups without broadcasting any of it."
- **useful because:** This is a genuinely combined wearable/browser/Mac capability: the pendant provides a private audio channel and turn boundary, the relay handles low-latency conversation, the browser reaches authenticated sources the relay cannot reach, and the Mac turns agreed follow-ups into local work. The owner gets help in a live situation without handing the other person their screen or hearing private synthesized speech.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime for the private low-latency side-channel; a cheaper background model extracts commitments and drafts follow-ups after the conversation.
- **latency:** Private answer or uncertainty cue within 1.5 seconds of the owner's question. Post-conversation commitment list within 30 seconds of ending the session.
- **cost:** Roughly $0.05-$0.50 per conversation depending on duration; browser lookups and post-session extraction dominate, not local Mac operations.
- **security:** Only the pendant microphone is used; never open the Mac microphone. The other participant must not be silently recorded or attributed without an explicit mode and applicable consent. Default to ephemeral audio, retain only owner-confirmed commitments, and cite source URLs for lookups. Creating reminders or sending follow-ups must be separately confirmed.
- **missing:** A private side-channel session mode with strict audio-retention and participant-consent state.; A browser lookup broker that accepts a narrowly scoped question and returns sourced claims rather than raw page text.; A commitment extractor that separates the owner's own promises from the other person's statements and asks for confirmation before persistence.; A post-session handoff from confirmed commitments to Mac reminders or browser drafts.


## What it asked for

_Nothing._
