# Harness derivation — faculty-judgement — round 147

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **granted orchestration tools are not live routes** — reconcile_personal_state, cross_surface_preflight, and pendant_diagnostics_and_bug_draft were granted in policy but all three resolved as unavailable against the live inventory; each call returned no implementation. The system therefore cannot honestly claim it performed reconciliation, preflight, or UART diagnostics.
  - evidence: Live tool calls in round 147 returned resolution:'unresolved' with nearest routes POST /briefing, POST /origins/read, and GET /watches/drafts.
- **timezone conflict** — Owner memory says America/Chicago, while the authoritative Mac routine zone is America/New_York and the pendant has no zone. Any briefing or schedule that says 'today', 'morning', or 'at 07:00' must label which clock it uses until owner location is explicitly resolved.
  - evidence: Owner projection from discover:owner says timezone America/Chicago; established authoritative routine timezone says America/New_York; pendant NITZ/GNSS absent.

## Capabilities it proposed

### "When I reconnect the pendant, tell me what I missed and what still needs me—one short, trustworthy recovery briefing, not five separate alerts."
- **useful because:** Today catch-up has empty pendant sources, scheduled jobs can be orphaned, and audio delivery is not reconciled. This would turn a dropped-link morning into a single actionable account: completed, unheard, failed, stale, and requiring owner attention, with no false all-clear.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Background model composes the recovery digest; realtime model speaks only the final short sentence and handles follow-up questions.
- **latency:** Under 5 seconds after USB/LTE reconnect for the first spoken summary; detailed evidence can load asynchronously.
- **cost:** About $0.01–$0.04 per reconnect, dominated by one background synthesis; reads and ACK reconciliation are local/cheap.
- **security:** Never read message bodies or page contents into the first sentence. Include only opaque job/artifact IDs and redacted summaries unless the owner asks. Mutations (retry, reminder, draft) remain separate and require autonomy_policy_evaluate.
- **missing:** A real reconnect event from the pendant/bridge into relay catch-up; Durable relay-job lease/requeue and relay↔Mac job-id mapping; Writers for fleet memory or an equivalent durable cross-surface recovery record; A mounted delivery-ACK ingestion path and a populated pendant catch-up source

### "Before you tell me my calendar is clear, inbox is empty, or a task is done, say exactly what you were able to verify and what you could not access."
- **useful because:** The live system can confidently report an all-clear when EventKit is unauthorized, and GUI actions are untrusted without Accessibility/Screen Recording. An owner should never mistake missing evidence for a quiet day or an unverified click for completion.
- **path:** relay → mac-planner → browser-extension → pendant
- **model tier:** Deterministic policy and evidence checks decide the wording; use the realtime model only to compress the verified result into one spoken sentence.
- **latency:** Add no more than 300 ms to a normal read or action; if verification is unavailable, return immediately with a precise refusal and an offered next step.
- **cost:** Negligible model cost for normal calls; occasional realtime compression under $0.005.
- **security:** Do not expose sensitive snippets merely to explain a failure. Provenance should include source, permission state, timestamp, and postcondition fields, with secrets withheld. Never claim a mutation succeeded from an intent receipt alone.
- **missing:** A unified negative-evidence/postcondition envelope used by calendar, mail, Mac, and browser actions; EventKit Calendar/Reminders permission probes distinct from Automation-TCC probes; A reachable browser/Mac observation verifier that can report GUI uncertainty; A route that exposes owner-idle/focus signals for interruption wording

### "Run a two-minute pendant bench rehearsal over USB: speak a test phrase, play it back, measure the link and audio path, and tell me whether today's conversation is safe to use."
- **useful because:** The pendant and ESP32 bridge are physically connected now even though LTE is unregistered. The owner can get a real go/no-go answer today instead of discovering during a conversation that audio is clipped, queued, or silent. It would exercise the exact 24 kHz path and preserve measured evidence.
- **path:** pendant → relay → mac-planner
- **model tier:** No expensive model for the test; deterministic firmware probes and a cheap background summarizer produce the report. Realtime speaks only the result.
- **latency:** Two minutes wall clock including a short capture/playback loop; report within 2 seconds of completion.
- **cost:** Near-zero API cost; local serial and audio probes dominate. Optional synthesis under $0.002.
- **security:** Use a generated phrase with no owner speech or retained recording. Store metrics, hashes, and opaque run ID only; delete test audio after verification. Require confirmation before changing firmware or audio profiles.
- **missing:** A safe USB-serial command/route that coordinates nRF9160 capture, ESP32 playback, and Mac-side recording; Automated acceptance checks for alias rejection, codec CPU, mic drops, tx starvation, and pre-speech silence; A signed bench-run receipt linked to pipeline and pendant delivery events; A local hardware health endpoint that does not imply LTE registration

### "Where did I see or say that? Search my open browser tabs, authenticated mail, Mac notes, and recent pendant captures, then give me the answer with citations and tell me which places you could not search."
- **useful because:** The owner currently has to remember which body saw a fact. A single query would join the browser session nobody else can reach, local notes, mail, and voice captures while preserving the crucial distinction between not found and not accessible.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Cheap retrieval and deterministic ranking first; use the realtime model only to synthesize a short answer from returned, cited snippets.
- **latency:** First spoken result in 3 seconds for local/open-tab sources; authenticated mail or broad history may continue asynchronously with a second result.
- **cost:** Roughly $0.005–$0.03 per query; retrieval dominates, with model spend limited to cited snippets.
- **security:** Search results must remain on-device unless the owner explicitly asks for cloud synthesis. Secret and sensitive snippets are masked before relay use; every citation carries source, freshness, and access scope. Never imply a source was searched if its permission or session was unavailable.
- **missing:** A single read-only federated-search route over local facts/captures, mail, and browser sessions; Stable source IDs and freshness metadata shared across Mac, browser, and relay; A result contract that separates not_found, inaccessible, stale, and found; A bounded snippet/redaction layer for cross-surface synthesis

### "If the pendant link or audio degrades while we are talking, keep me in the conversation: switch to a safe shorter mode, show me what was missed on the Mac, and resume without making me repeat myself."
- **useful because:** A wearable conversation should fail gracefully rather than silently lose an answer. The relay, Mac, and pendant can preserve the interaction at different fidelity: spoken audio when healthy, a concise Mac/browser fallback when not, and resumable delivery when the link returns.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Deterministic health thresholds choose the transport and verbosity; a background model compacts the missed response. Realtime is used only for the live utterance when the audio path is healthy.
- **latency:** Detect degradation within one audio artifact or 2 seconds; publish a Mac fallback within 5 seconds; resume spoken delivery at the next safe boundary.
- **cost:** Usually negligible; one compacting call costs about $0.002–$0.01 only when audio fallback is needed.
- **security:** Fallback text must obey the same sensitivity policy as speech. Never duplicate a side effect merely because delivery was uncertain; bind every retry to an artifact/request ID and show the owner whether the response was generated, delivered, or merely queued.
- **missing:** A live health-to-routing adapter consuming pendant delivery ACKs and audio metrics; A durable response checkpoint joining relay interaction, Mac job, and audio artifact; A Mac/browser fallback surface for an answer that has not been heard; Idempotent resume semantics at utterance/item boundaries


## Changes it proposed to its own stack

### `hardware` — Add a normally-closed, firmware-controlled microphone power/load switch between the SPH0645 microphone and its supply/data path, with the existing privacy latch driving the safe state and a boot-time default that keeps capture physically off until the latch is cleared. Report only switch-state transitions and a tamper/open fault; do not buffer audio.
- **owner gets:** When the owner invokes privacy mode, a compromised or wedged application cannot keep listening merely by ignoring a software mute. The pendant gains a physical guarantee that the microphone is actually disconnected, including during a dropped link or reboot.
- effort: Moderate board revision: select a low-leakage audio-rated load switch or analog FET, reroute the mic supply/control, update the nRF9160 overlay and firmware latch path, and validate noise, boot behavior, and current draw on the live USB setup.  ·  risk: Added switch resistance or supply noise could reduce mic quality; a boot fault could leave capture unavailable. Recover with a hardware bypass/test pad, explicit self-test, and fail-closed diagnostics. This is a privacy cutoff, not a claim that the radio or already-buffered samples are erased.
- cost: Approximately $0.10–$0.80 in components and under a few mW when active; board spin and validation dominate.  ·  latency: No conversational latency; capture starts only after a GPIO-controlled power-settle delay, target under 5 ms.
- security: Strongly improves the local privacy boundary by making the mute physical and fail-closed. It does not replace offline panic wipe, auth revocation, or the existing no-audio-retention rule.
- depends on: Existing local privacy latch firmware behavior; SPH0645 microphone electrical characterization and board schematic access; A GPIO/overlay reservation and measured audio-quality regression test


## What it asked for

_Nothing._
## Its own summary

Round 147 produced three new owner-facing capabilities: reconnect recovery briefing, truthful verification/all-clear language, and a USB pendant bench rehearsal. Live testing exposed that three newly granted tools (personal reconciliation, cross-surface preflight, UART diagnostics) are policy grants without implementations and cannot currently run. I also recorded the unresolved America/Chicago owner-memory versus America/New_York Mac-clock conflict. What I still need is not another model grant: I need the orchestrator to wire those tools to real routes, a reconnect signal/ACK ingestion path, and a deterministic USB serial bench harness; until then I will not claim those checks happened.

**Biggest unknown:** Whether any agent has already inventoried a live USB serial command path and whether the owner intends America/Chicago as their personal timezone or only as stale memory.

