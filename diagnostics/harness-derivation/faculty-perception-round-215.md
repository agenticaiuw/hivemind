# Harness derivation — faculty-perception — round 215

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-perception** — At 2026-08-09T00:19Z the Mac local agent is fully ready: Accessibility and Screen Recording are granted, all required permissions are present, computer-use loop is enabled, and the Safari browser extension is online with two tabs and zero pending commands. The relay is reachable and D1-backed; the registered fleet still contains no nRF9160 pendant, only the online Mac bridge and offline contract-test mobile.
  - evidence: read_continuity_snapshot(include=['relay','pipeline'], since='2026-08-08T23:00:00Z', maxItems=20): /ops/snapshot HTTP 200; status.permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser online=true, relay.store='d1', relay.macBridgeOnline=true; devices discovery lists Safari on MacIntel, home-macbook-bridge, cloudflare-contract-test and no pendant.

## Capabilities it proposed

### "When I ask “what happened while I was away?” give me a causal timeline, not a pile of statuses: what I asked, which surface received it, what actually ran, what the browser or Mac changed, whether audio reached the pendant, and the exact gap if the answer is unknowable."
- **useful because:** The current snapshot can show live components and pipeline traces, but it cannot explain causality or distinguish relay acceptance, Mac completion, and owner-heard playback. This would turn an opaque morning into an honest, checkable account and explicitly preserve unknowns instead of inventing success.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** background for reconstruction; realtime only for the one-sentence spoken answer
- **latency:** Under 5 seconds for a recent event; up to 20 seconds for a multi-day reconstruction
- **cost:** Usually one cheap text-model call over bounded event records; roughly $0.01–$0.05, dominated by context extraction rather than generation
- **security:** Include only the owner's authenticated event records and redacted browser claims. Never quote secret page text or infer that audio was heard without a device playback event. Require confirmation before replaying or acting on a proposed recovery.
- **missing:** A normalized event join keyed by run/job/announcement/capsule IDs across relay, Mac, browser, and future pendant playback events; A causal reducer that labels evidence as observed, reported by another surface, or unknown; A durable owner-facing reconstruction endpoint rather than separately scraping snapshot, pipeline, jobs, and browser spool

### "What exactly did that web page say when you told me about it? Show me the source, the captured passage, what was redacted, and whether the page changed before I acted on it."
- **useful because:** Relay browser reads currently return transient untrusted text, while Mac capsules and grounded claims exist only for extension reads. This gives the owner a verifiable answer instead of an untraceable paraphrase, especially for logged-in or fast-changing pages.
- **path:** browser-extension → relay-realtime → mac-planner → dashboard
- **model tier:** background for capture/hash/redaction; realtime only to summarize an already-grounded capsule
- **latency:** Capture within 1 second of the read; replay under 2 seconds; comparison can take 5 seconds
- **cost:** One local SHA-256/redaction pass and bounded storage; <$0.01 per capture, with model cost only if the owner asks for comparison or summarization
- **security:** Keep bodies local and redacted; never send passwords, tokens, or private page regions to the relay. Mark relay-origin text untrusted until the Mac validates its source and hash. Require confirmation before acting on a changed page.
- **missing:** The relay read result must return a stable read ID and content hash, and the Mac must mint an existing evidence capsule from it; Mount the existing browserProvenance routes and connect the capsule to the voice turn, job, and action receipt; A browser re-read comparator that reports changed/unchanged/unknown rather than silently refreshing

### "Tell me only when the system's own facts contradict each other—for example, a routine says completed while no device could have played it, a browser result refers to a tab that vanished, or a stored preference conflicts with the machine's authoritative timezone—and explain which source wins."
- **useful because:** The system currently exposes many individually plausible facts with different provenance and freshness. Contradictions are the dangerous perceptual failures: they cause confident wrong action while every single status looks healthy. A low-noise alarm lets the owner correct bad memory or stale completion claims before they matter.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard → pendant
- **model tier:** cheap background rule engine for detection and ranking; realtime model only when the owner asks for an explanation
- **latency:** Evaluate after each job/routine/browser result and within 60 seconds of a state change; explanation under 2 seconds
- **cost:** Near-zero for typed rules and hashes; <$0.01 for an occasional compact explanation
- **security:** Keep alerts local to the owner's account; include source provenance and timestamps, not secret content. Never auto-delete or rewrite a conflicting fact. Require owner confirmation to repair pinned memory or retry an action.
- **missing:** A provenance-aware contradiction schema with authority, freshness, and scope fields on every cross-surface observation; Rules for known hazards: Mac timezone authority versus machine-origin memory, Mac-side completion versus missing device_playback, browser tab/session identity drift, and stale device registry rows; A deduplicated alert store with suppression windows and a dashboard/voice route

### "If I say “when the price on this logged-in page drops below the number I saw, buy it only if the page still shows the same seller and shipping terms,” hold that commitment, re-check the browser evidence, ask me only when every condition is still true, and otherwise tell me exactly which condition changed."
- **useful because:** Today the system can observe a page and can act through the Mac or browser, but it cannot preserve the owner's exact evidence conditions as a durable safety boundary. This prevents stale-page purchases and makes conditional intent useful without turning a vague watch into an unsafe automation.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** background rule/evidence evaluator; realtime model only for the owner's spoken confirmation
- **latency:** Re-check on the requested schedule or page mutation; under 3 seconds to present a confirmation, with no action until conditions validate
- **cost:** Mostly local hashing and typed predicates; <$0.02 per recheck, with browser/model cost proportional to the watch frequency
- **security:** Logged-in page contents stay on the browser/Mac. Buying, sending, or other irreversible actions always require explicit confirmation. Conditions must be content-hash- and locator-bound, expire by default, and fail closed on login walls, tab changes, or missing evidence.
- **missing:** A durable evidence-condition object linking an existing browser capsule to typed predicates and an expiry; Browser-side change notifications or scheduled authenticated re-reads with stable tab/session identity; An action gate that refuses POST /execute or browser mutations unless the condition receipt is valid and confirmation is present

### "When I get interrupted mid-thought, let me press once later and continue from the exact unfinished point: recover the locally buffered words and audio-quality verdict, show which parts were heard versus missing, and resume with the right browser tab or Mac document without pretending the sentence was complete."
- **useful because:** A dropped link or unusable capture currently turns an interrupted thought into a lost or ambiguous command. This would make the wearable genuinely resilient: the pendant preserves only the minimal unfinished utterance, while the Mac restores the work context and the relay explains uncertainty.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** small background model for reconstruction and redaction; realtime model only when the owner resumes speaking
- **latency:** Local interruption marker immediately; resume context under 4 seconds after reconnection
- **cost:** A few kilobytes of bounded local metadata/audio; <$0.02 per recovery, dominated by transcription only when needed
- **security:** Store encrypted, bounded utterance fragments locally and expire them quickly. Do not replay private audio into the relay unless the owner resumes. Require confirmation before reopening a sensitive page or editing a document.
- **missing:** A pendant-side unfinished-utterance journal that is distinct from routine SD fallback recording; A reconnect protocol carrying sequence ranges and capture-integrity verdicts to the relay; A Mac context bookmark tying the utterance to the active browser tab/document and restoring it through reversible actions

### "Use my logged-in browser to complete a task without sending the page contents or credentials to the cloud: let the relay describe the goal, let the Mac/browser evaluate the page locally, and return only a redacted fact, a proof of the exact tab and mutation, and a confirmation request before anything irreversible."
- **useful because:** The browser is the one surface holding sessions nobody else can reach, yet cloud planning and browser reads can currently expose more page text than the task needs. This gives the owner private-by-construction browser assistance while retaining enough evidence to audit what happened.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** local Mac model/rules for DOM interpretation and redaction; cheap relay model for goal decomposition; realtime only for spoken confirmation
- **latency:** Simple local checks under 2 seconds; multi-step tasks under 10 seconds before confirmation
- **cost:** <$0.02 per task when handled locally; cloud token use falls because only typed/redacted claims cross the boundary
- **security:** Credentials, DOM bodies, screenshots, and secrets never leave the Mac. Use capability-scoped opaque handles, redact before relay transmission, bind receipts to tab/session identity, and require confirmation for sends, purchases, deletes, or permission changes.
- **missing:** A relay planner protocol that can issue typed predicates and browser action intents without requesting raw page text; A local browser privacy executor that evaluates predicates and returns redacted claims plus mutation receipts; A policy-enforced boundary proving that cloud tools cannot bypass the local executor by calling read_web_page directly


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: evidence-gated conditional commitments, interruption-safe unfinished-thought recovery, and private-by-construction browser delegation. Each requires new cross-surface contracts rather than a refactor, and each names concrete missing dependencies.

**Biggest unknown:** Whether any of these collide with an unseen backlog entry; the recorder accepted all three, so none matched strongly enough to reject.

