# Harness derivation — relay-realtime — round 140

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Open my project dashboard and summarize what changed since yesterday."
- **useful because:** A daily “what’s new” view saves time and reduces context switching; the owner can decide quickly what matters.
- **path:** relay → browser → mac-bridge
- **model tier:** cheaper summarization model after extraction; realtime only for conversational steering.
- **latency:** A few seconds; most time is page load and extraction.
- **cost:** Moderate; browser automation and content extraction dominate.
- **security:** Authenticated pages may contain sensitive data. Use least extraction, cite sources, and avoid storing content longer than needed.
- **missing:** Implement server_browser_actions; currently only a schema exists; A browser-run environment with auth/session support or a handoff to mac-planner if not available

### "If I stop talking, keep listening for a few seconds in case I add something."
- **useful because:** Natural voice interactions often come in bursts; a short grace period reduces frustration and prevents accidental cutoffs.
- **path:** pendant → relay
- **model tier:** realtime for voice handling; no planner needed.
- **latency:** Immediate; it changes session behavior, not external work.
- **cost:** Low; a small buffer and timer; audio storage dominates if retained.
- **security:** Capturing extra audio risks recording unintended speech. Make the buffer short, local-first, and discard if no follow-up occurs.
- **missing:** A relay event push mechanism to extend session state; A device skill to buffer audio locally and mark end-of-speech consistently

### "“I’m heading out—hand me the exact work I was doing on my Mac, and let me continue it by voice from the pendant.”"
- **useful because:** Today leaving the desk strands the owner’s in-progress browser tabs, editor state, and pending actions. This would make the wearable a true continuation surface rather than a separate chatbot: it packages the active task, exposes only the relevant next decisions, and can hand the result back to the Mac when the owner returns.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles the short spoken handoff and disambiguation; a cheaper background model builds a compact task snapshot from Mac/browser state and maintains it while the owner is away.
- **latency:** A spoken handoff should begin within 1.5 seconds; snapshot generation may take 5–15 seconds after the owner leaves and must not block voice.
- **cost:** About $0.01–$0.05 per handoff, dominated by snapshot summarization and any repeated state diffs; incremental diffs should keep routine updates cheap.
- **security:** The snapshot can contain private tabs, source code, and authenticated page text. Keep it encrypted, expire it after the task closes, expose provenance and a one-button ‘discard handoff’ control, and never read unrelated tabs.
- **missing:** A Mac presence/away transition signal tied to the pendant; A task-snapshot schema that can represent browser tab, editor, and pending action state; A resumable voice-to-task command channel and a Mac-side reattachment endpoint

### "“When I press the pendant at a meeting, keep a private running record of decisions and commitments, then give me only my follow-ups when I leave.”"
- **useful because:** The owner currently has to remember decisions, identify their own commitments, and reconstruct context across calendar, browser, and Mac afterward. A physical pendant trigger makes capture intentional, while the relay can produce a useful follow-up list without making the owner manage another app.
- **path:** pendant → audio → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a small background transcription/structuring model during capture; reserve realtime for the owner’s spoken corrections and the final concise readout.
- **latency:** Start capture confirmation in under 500 ms; rolling segments can finalize asynchronously. The post-meeting follow-up should be ready within 30 seconds of stop.
- **cost:** Roughly $0.03–$0.20 per hour of audio depending on transcription length; summarization is a small additional fraction and should run once per meeting.
- **security:** Meeting audio and names are highly sensitive. Show an unmistakable LED/audio recording indicator, encrypt segments, retain only the derived commitments by default, let the owner delete the entire session from the pendant/dashboard, and do not send audio to browser sessions unless explicitly linked.
- **missing:** A device-local capture toggle and recording indicator; Streaming audio segment upload with resumable storage; Calendar/event association and speaker/commitment extraction; A durable per-meeting record with correction and deletion semantics

### "“Tell me what changed across my open work tabs and local project since yesterday, cite the exact evidence, and let me ask follow-up questions hands-free.”"
- **useful because:** A daily change brief that joins authenticated browser state with local project activity would replace manually reopening tabs and hunting through diffs. The important novelty is evidence-linked conversational comparison: the owner can challenge a claim from the pendant and receive the underlying tab/file source rather than an opaque summary.
- **path:** pendant → relay → browser-extension → mac-planner → mac-terminal → dashboard
- **model tier:** A cheaper background model computes incremental summaries and indexes citations; realtime only answers the owner’s follow-up question and routes any requested inspection to the correct surface.
- **latency:** Precompute in under two minutes after the chosen baseline; first spoken answer under 2 seconds, with cited detail fetched asynchronously if needed.
- **cost:** Approximately $0.02–$0.10 per daily brief, dominated by changed-page/file extraction; hash-based unchanged-content skipping keeps it low.
- **security:** Authenticated browser pages and source code must remain scoped to explicitly selected tabs/projects. Store hashes and redacted excerpts where possible, keep full evidence local to the Mac/browser, and require an explicit selection before adding a new source.
- **missing:** A baseline-and-diff store spanning browser pages and local project files; Stable evidence IDs that can be opened back on the originating Mac/browser surface; A citation-aware summarizer and voice follow-up retrieval path; A user-visible source-selection and retention control

### "“Draft the reply from the page and files I’m looking at, then tell me exactly which private facts and attachments would leave my devices before I send it.”"
- **useful because:** The owner can currently ask an agent to act across Mac and authenticated browser surfaces, but cannot get a trustworthy, human-readable account of the assembled outbound payload. This capability turns the pendant into a data-boundary assistant: it gathers only explicitly referenced material, identifies secrets and personal data, and produces a spoken diff before any send action.
- **path:** pendant → relay → mac-planner → browser-extension → mac-terminal → dashboard
- **model tier:** Use a cheaper background model to assemble and classify the draft and payload; realtime only narrates the short risk summary and handles corrections. Sending remains an explicit downstream action after the owner hears the preview, without adding a blanket policy gate to unrelated actions.
- **latency:** Read the first concise preview within 3 seconds; full attachment and sensitive-span analysis may continue for up to 15 seconds with progress surfaced to the pendant.
- **cost:** About $0.03–$0.15 per composed message, dominated by extracting referenced page/file contents and classification; hashes and cached local scans reduce repeat cost.
- **security:** The analyzer itself sees exactly the sensitive material it is protecting. Keep raw files on the Mac whenever possible, send only spans/hashes to the relay, redact credentials and tokens in logs, show destination/account/attachments in the spoken and dashboard preview, and retain no draft after completion unless requested.
- **missing:** A cross-surface outbound-payload builder with explicit source selection; Local secret/PII classification and redaction that returns spans rather than uploading full files; A typed preview receipt that downstream send actions must reference; A pendant-friendly spoken diff for destination, recipients, attachments, and sensitive fields


## Changes it proposed to its own stack

### `relay` — Implement relay_route_intent as the canonical routing path from speech to downstream agents, with structured fields for intent, utterance, and target, plus a mapping to existing tool calls.
- **owner gets:** More reliable, faster routing means fewer misfires and less repetition when they ask for something by voice.
- effort: Medium; map intents to existing mac_run_actions/mac_delegate/browser_run_actions and record routing decisions for debugging.  ·  risk: Misrouting could trigger the wrong action. Mitigate with conservative defaults and a safe fallback to clarification.
- cost: Low; a small routing layer. Main cost is logging/telemetry.  ·  latency: Improves latency by reducing planning overhead and retries.
- security: Routing metadata may include sensitive text; log minimally and protect records.
- depends on: A defined intent taxonomy and mapping to existing tool calls; Implementing the relay_route_intent backend handler

### `model-routing` — Add a tiered summarization path: relay extracts minimal content, then a cheaper model summarizes, and only complex decisions escalate to a more capable model.
- **owner gets:** They get fast summaries without paying the latency cost of a top-tier model for routine tasks.
- effort: Low to medium; requires a summarization service and clear escalation rules.  ·  risk: Over-summarization could omit important details. Provide a way to ask for more detail or source quotes.
- cost: Reduces per-task cost by defaulting to cheaper models.  ·  latency: Improves average response time; keeps realtime free for conversation.
- security: Summaries may expose sensitive content; keep citations and avoid storing raw data unnecessarily.
- depends on: A summarization endpoint/service and policy for escalation thresholds


## What it asked for

### `s20-2ac2` (skill) — short_grace_audio_buffer
- does: After end-of-speech or button release, keep a short rolling buffer (e.g., 2–5 seconds) and append it if the user resumes, otherwise discard.
- must be on-device because: It must work even if the link drops and should avoid uploading unnecessary audio.
- trigger: speech end detected; optionally button state
- storage: RAM ring buffer; optional transient SD cache if RAM is tight
- RAM budget: ~32–96 KB for compressed audio and bookkeeping; exact size depends on codec and sample rate

## Its own summary

Recorded four non-identical owner capabilities: voice continuation handoff when leaving the Mac, intentional meeting commitments capture, evidence-linked cross-surface change briefs, and outbound-payload privacy preview before sending. The haptic hardware proposal was correctly rejected as already present in the backlog, so I did not rephrase it. The most important is voice continuation handoff: it would make the worn pendant a continuation of unfinished work rather than a separate interface.

**Biggest unknown:** The remaining implementation gap is not the individual Mac/browser routes; it is the missing cross-surface state contracts: resumable task snapshots, durable meeting records, baseline/evidence IDs, and an outbound payload/redaction receipt. I could not discover further this round as instructed.

