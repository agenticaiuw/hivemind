# Harness derivation — mac-planner — round 240

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What should I do next?” — use what is happening on my Mac and in my day, then set up the next focused step for me."
- **useful because:** This would be the system's most useful everyday behavior: not a generic briefing, but a live decision made from Calendar/Mail, the authenticated browser tabs I actually have open, foreground/running apps, and the pendant's recent moment bookmarks. It returns one ranked next action and can stage the relevant document or tab on the Mac, rather than making the owner translate a summary into work.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use the realtime model only to understand the spoken request and resolve ambiguity; use a cheaper background planner to rank candidates and generate the compact action plan. No model is needed for deterministic calendar/mail/tab joins.
- **latency:** 3–6 seconds for the answer; another 1–3 seconds to stage the chosen app/tab. If sources are unavailable, say exactly which source was omitted instead of guessing.
- **cost:** Usually one short realtime turn plus a small background ranking call; roughly $0.01–$0.05 depending on transcript/context size. The dominant cost is resending selected snippets, so send hashes and titles first and fetch bodies only for the chosen candidate.
- **security:** Mail snippets and authenticated tab titles/URLs leave the Mac only to the relay/model. Redact bodies by default and never transmit cookies or page screenshots unless explicitly requested. Staging an app/tab is a local mutation and should be recorded in the action journal; the owner must configure which domains/apps are eligible for unattended opening.
- **missing:** A source-joiner that correlates calendar/mail/tab/app/bookmark records by time and project instead of treating briefing output as a static report; A runtime policy entry declaring which browser domains and Mac apps may be opened by this routine; A compact pendant response format for ranked choice plus a Mac action receipt

### "“Privacy now.” — immediately stop capture and playback on the pendant, stop Mac/browser capture surfaces, and tell me what was actually shut down."
- **useful because:** The existing pendant privacy latch protects the wearable, but the owner can still have a browser meeting, screen recorder, dictation process, or audio application capturing on the Mac. A single physical latch event should create a verifiable privacy boundary across the whole hive, not merely mute one node. The owner gets a clear spoken/LED acknowledgement and an honest list of any surface that could not be stopped.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** No expensive model for the safety path. The relay executes a deterministic allowlisted shutdown graph and a cheap summarizer turns receipts into a short spoken acknowledgement; realtime is used only if the owner asks a follow-up question.
- **latency:** Local pendant mute is immediate. Relay-to-Mac/browser shutdown and verification should complete within 2 seconds; if disconnected, the pendant remains latched and queues the command until the link returns.
- **cost:** Near-zero model cost for normal operation; a small receipt summarization call only when needed. Engineering cost is in reliable event delivery and enumerating capture surfaces, not inference.
- **security:** This must fail closed for capture, but must not silently kill unrelated work. The owner needs an explicit, editable policy mapping (known microphone/camera apps, browser bridge, meeting tabs) and a local audit receipt. No audio or page content should be sent while latched. Releasing the latch must be local on the pendant; remote confirmation cannot be required.
- **missing:** A relay fan-out event with delivery/ack deadlines to Mac and browser surfaces; A Mac-side allowlisted privacy shutdown routine that reports process/app state before and after; A browser command that pauses page capture and confirms the extension is no longer forwarding content; A durable redacted privacy receipt visible on the dashboard and playable from the pendant inbox

### "“Make me a source packet on this.” — research the question, use my existing browser context when relevant, save a reproducible packet on the Mac, and give me the short answer on the pendant."
- **useful because:** A spoken request should produce more than an ephemeral answer. The relay can search and read public sources, the browser can contribute an authenticated page only when the owner explicitly names it, and the Mac can atomically save a dated packet containing the question, claims, URLs, excerpts, timestamps, and uncertainty. The owner gets an answer while walking and a durable artifact they can audit or share later.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use a cheaper background model for source selection, extraction, and citation checking; reserve realtime for interpreting the spoken request and delivering the concise spoken result. Do not send full authenticated page bodies unless the owner explicitly opts in.
- **latency:** Return a useful first answer in 8–15 seconds, then finish the packet asynchronously within 60 seconds. The pendant should receive a completion alert and a link/path receipt rather than waiting through the whole research run.
- **cost:** Typically 2–5 small web-read/search calls plus one background synthesis, approximately $0.03–$0.15 depending on source count. Most cost is source text, so cap excerpts and deduplicate URLs.
- **security:** Public research may leave the device through search/read services; authenticated browser material must be opt-in, redacted by default, and marked clearly in the packet. Preserve source URLs and retrieval times, never claim verification when a page was blocked, and require owner policy for which local directories can receive generated files.
- **missing:** A research orchestrator that can combine public web sources with an explicitly selected authenticated browser page while preserving provenance; A packet schema and citation/contradiction checker rather than a free-form note; A safe handoff from the background job to mac_workbench_transaction with idempotent job identity and a pendant completion alert

### "“Do this even if I lose signal.” — preserve my spoken intent, continue it across the relay, Mac, and browser exactly once, and tell me what happened when I reconnect."
- **useful because:** Today a dropped pendant link can preserve audio or a bookmark, but not the meaning of an in-flight multi-surface request. The owner should be able to say something consequential such as “prepare the report and stage the portal form,” walk away, and later receive one unambiguous result rather than a duplicate action, a silent loss, or an uncertain partial state.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime only transcribes and confirms the intent boundary. A cheap background worker resolves and executes the durable intent; deterministic idempotency keys and state transitions, not a model, decide whether a step may run again.
- **latency:** Capture and local acknowledgement under 500 ms; resume when any required node returns. Reconciliation should complete within 10 seconds of reconnection, with a pending/partial/complete state spoken or shown rather than guessed.
- **cost:** Low routine model cost, roughly $0.01–$0.04 for intent extraction and final explanation. Storage, receipts, and reconciliation dominate engineering cost; no audio needs to remain after transcription is acknowledged.
- **security:** A lost-link request must never silently perform a high-impact action later. Store a redacted intent summary and a step-level authorization policy, not raw audio by default. Authenticated browser operations need expiry checks, and every mutation needs a before/after receipt plus a durable reason if it was withheld.
- **missing:** A cross-node durable-intent protocol with a single idempotency key and explicit state machine for captured, staged, executing, partially-complete, and reconciled; A relay coordinator that can resume a Mac job and browser command without replaying acknowledged steps; A pendant result format for partial completion and an owner-configurable expiry/authorization policy

### "“Why did you do that, and what did you rely on?” — give me a compact, honest explanation spanning the pendant, relay, Mac, and browser, with the exact evidence and any omitted sources."
- **useful because:** The owner cannot currently audit a result that crosses surfaces: a spoken answer may have used a calendar item, a browser page, a local file, and a stale relay job, while each node keeps a different fragment of the story. A single evidence ledger would make the system trustworthy: it would distinguish observed facts from model inference, show timestamps and freshness, and expose actions that were planned but not executed.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Evidence collection and freshness checks are deterministic. Use a small background model to verbalize the already-structured evidence; realtime is needed only for a spoken follow-up. Never let the explanation model invent citations absent from the ledger.
- **latency:** A normal answer should carry a compact evidence token immediately; a full audit should render in under 5 seconds from receipts and cached metadata. It must remain available after the original job finishes.
- **cost:** Near-zero for ordinary ledger storage and deterministic joins; under $0.01 for a short natural-language explanation. The main cost is bounded metadata retention, not model tokens.
- **security:** Evidence must be redacted by field and source class, especially mail bodies, authenticated URLs, and local filenames. The owner should be able to inspect hashes/titles without exporting content. Explanations must say “not observed” rather than reveal secrets or fabricate certainty.
- **missing:** A common evidence-envelope schema with source, timestamp, freshness, content hash, observation versus inference, and redaction class; A cross-node ledger joiner that links relay decisions to Mac/browser receipts and pendant events; A user-facing audit view and pendant-friendly evidence token with retention and deletion controls

### "“Learn this routine without doing anything risky yet.” — observe the steps I take across my browser and Mac, simulate the routine for several days, show me the differences, then let me enable it as one named automation."
- **useful because:** Today the owner can run actions or create a routine, but cannot safely teach a cross-surface routine by comparing intended outcomes with real observations before it gains authority. A shadow mode would turn repeated work into a trustworthy automation: it records structure and outcomes, not secrets, produces dry-run diffs, and only becomes active after the owner sees what it would have changed.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Use deterministic event normalization and diffing for the shadow run. A cheaper background model can infer stable step labels from repeated traces; realtime is only for the owner's spoken setup and final explanation.
- **latency:** Setup in under a minute; shadow observations are asynchronous. Produce a daily or on-demand diff in under 10 seconds and make activation immediate once explicitly enabled.
- **cost:** Low recurring model cost, roughly $0.02–$0.10 per day depending on trace volume. The dominant cost is bounded local event storage and redaction, not inference.
- **security:** Shadow mode must not capture passwords, page contents, microphone audio, or arbitrary keystrokes. Store selectors, app/domain classes, outcome hashes, and timing rather than sensitive values. Activation must be a named owner policy with scope, expiry, and a visible dry-run diff; an empty policy means observation only.
- **missing:** A cross-surface trace format that joins browser commands, Mac actions, source reads, and pendant intent without retaining sensitive payloads; A shadow executor that can replay against snapshots or preflight results and calculate intended-versus-observed diffs; A routine lifecycle with learn, shadow, review, enable, pause, and expire states exposed in the dashboard and pendant inbox


## What it asked for

_Nothing._
## Its own summary

This round I recorded three non-identical capabilities: (1) a live “what should I do next?” navigator joining calendar/mail, current Mac apps, authenticated browser tabs, and pendant bookmarks before staging one focused action; (2) a physical privacy latch that propagates to Mac/browser capture surfaces and returns a verifiable shutdown receipt; and (3) a spoken, provenance-preserving research packet that saves an auditable artifact through the workbench and reports completion to the pendant. I also confirmed the new grants are live: bounded Mac inspection, preflight, read sources, and atomic workbench transactions. I still need the source-joiner/ranking layer, a relay privacy fan-out plus explicit owner-configured capture policy, and a research orchestrator with citation/provenance handling. I do not need another generic serial-health proposal: the recorder identified that as existing.

**Biggest unknown:** Which Mac/browser capture processes the owner actually wants included in the privacy policy, and which authenticated browser domains may be used as research sources. Those are owner policy decisions, not gaps I should guess.

