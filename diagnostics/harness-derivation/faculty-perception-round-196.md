# Harness derivation — faculty-perception — round 196

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac perception and browser reachability** — At 2026-08-08T22:51Z, the exact AI Pendant Agent binary has Accessibility and Screen Recording granted; /observe reports inputReachability.status=verified, uiActionsWillReachTheScreen=true, secureInput=false, and browser/status reports Safari extension online with 5 tabs and zero pending commands. The relay is reachable, D1-backed, and reports macBridgeOnline=true. This removes the prior TCC blocker, but no pendant is registered.
  - evidence: GET /observe HTTP 200; GET /browser/status HTTP 200; GET /ops/status HTTP 200 at 2026-08-08T22:51Z

## Capabilities it proposed

### "When I come back to my Mac, tell me what I was in the middle of and give me the one best next step."
- **useful because:** This is a perceptual handoff, not another event digest: it fuses the currently focused app and screen, the active browser tab/session, recent Mac jobs/pipeline state, and relay history into one grounded answer. It prevents the owner from reopening five contexts just to reconstruct what they were doing.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** Use a cheap background model to rank and summarize evidence; use realtime only when the owner asks by voice. Perception should attach timestamps, source surfaces, and confidence before judgement sees it.
- **latency:** 2-4 seconds on demand; screen/browser capture and local state reads in parallel, then one small ranking call.
- **cost:** About $0.002-$0.01 per on-demand handoff, dominated by the ranking model; local capture and route calls are negligible.
- **security:** Screen and browser content may contain secrets. Redact passwords, payment fields, and private messages before leaving the Mac; never send raw screenshots to the relay unless explicitly requested. Action recommendations are suggestions only and require the existing confirmation policy.
- **missing:** A perception endpoint that atomically captures foreground screen, active browser tab/DOM, Mac job/pipeline snapshot, and relay continuity with per-source timestamps; A local redaction/classification pass for screen regions and a stable handoff record; A ranking prompt that distinguishes an unfinished task from incidental foreground content

### "Save exactly what I'm looking at so I can ask about it later, even if the page changes."
- **useful because:** A normal bookmark loses the selected passage and the reason it mattered. This creates a durable, redacted, content-addressed reading snapshot from the browser, lets the Mac keep the evidence locally, and lets the relay announce or retrieve the saved item later. The owner can return to the same factual context instead of trusting a mutable URL.
- **path:** browser-extension → mac-planner → relay-realtime → relay → faculty-perception → faculty-judgement
- **model tier:** Use local code for capture, hashing, redaction, and storage; use a cheap model only to produce a short title/why-it-matters. Realtime is only for the save/retrieve voice interaction.
- **latency:** Under 1 second to capture and acknowledge locally; under 3 seconds to summarize and optionally queue a spoken confirmation.
- **cost:** $0.001-$0.005 per save when summarization is requested; zero model cost for raw capture, hashing, and later retrieval.
- **security:** Never persist passwords, payment data, private-message bodies, or form values. Keep the full capsule on the Mac; send only a redacted excerpt and capsule ID to relay. Require confirmation before sharing a saved capsule or opening its URL in a different context.
- **missing:** A voice-addressable capsule index and retrieval route on the relay or Mac; A browser command that captures the user's current selection plus surrounding DOM and hands it to the existing evidence capsule store; A join record linking the voice turn, browser command, capsuleId, and any later answer

### "Give me only the important world and US news that changed since the last brief, in three short spoken sentences, and save the sources."
- **useful because:** The owner has repeatedly asked for this exact brief. A delta brief avoids repeating yesterday's headlines, separates genuinely new developments from recycled coverage, and leaves a source-backed record the owner can inspect later. It is useful both as a scheduled routine and as a one-line pendant request.
- **path:** relay-realtime → browser-extension → mac-planner → mac-terminal → relay → faculty-perception → faculty-judgement
- **model tier:** Run collection, URL fetching, timestamps, and story fingerprinting in the background with a cheap model; use realtime only to compress the already-grounded delta into the owner's requested three spoken sentences.
- **latency:** Scheduled generation can take 30-90 seconds; an on-demand answer should target under 8 seconds, with a short spoken progress response if collection is still running.
- **cost:** Roughly $0.01-$0.05 per brief, dominated by fetching and summarization; incremental briefs are cheaper because unchanged story fingerprints are skipped.
- **security:** Web content is untrusted and must not become instructions. Store source URLs, publication times, and redacted excerpts—not arbitrary page text or credentials. Do not post, subscribe, or navigate authenticated pages without confirmation.
- **missing:** A persistent story-fingerprint ledger with publication-time and source provenance, separate from the unbounded relay announcement store; A collector that merges web_search, read_web_page, and browser-extension results while preserving source URLs and content hashes; A routine output that writes a cited Mac note/audio artifact and a relay announcement without claiming the owner heard it

### "Tell me when one of your memories is contradicted by live evidence, show me both sources, and ask which one to keep."
- **useful because:** The system currently injects machine-derived facts into context as if they were reliable preferences; a stale value such as the wrong timezone can silently distort every later answer. The owner should be able to catch and resolve these contradictions before they become invisible behavior.
- **path:** faculty-perception → mac-planner → browser-extension → relay-realtime → relay → faculty-judgement
- **model tier:** Use deterministic comparisons for timestamps, timezone, device state, and source provenance; use a cheap model only to explain the conflict in one sentence. Realtime is appropriate only for the owner's confirmation conversation.
- **latency:** Run opportunistically after machine/browser state changes and before context projection; under 2 seconds for a single conflict and no perceptible cost when there is no conflict.
- **cost:** Near-zero for typed comparisons; under $0.002 when explanation needs a model.
- **security:** Show provenance and confidence without exposing secret fact values. Never overwrite an owner-origin fact automatically. Machine observations may be retained only as short-lived conflict evidence.
- **missing:** A contradiction detector joining projected memory facts to fresh Mac/browser/relay observations; A provenance-aware owner resolution flow that can retire or correct the selected fact; A context projection rule that quarantines unresolved contradictions instead of silently choosing the highest-confidence value

### "Where did I see or hear that? Search my recent browser pages, notes, spoken conversations, and saved evidence, then show me the exact source and the surrounding context."
- **useful because:** The owner should not have to remember whether an idea came from Safari, a voice exchange, a note, or a page that later changed. A cross-surface provenance search would answer with an exact excerpt, source, timestamp, and confidence instead of an ungrounded recollection.
- **path:** browser-extension → mac-planner → relay-realtime → relay → faculty-perception → faculty-judgement
- **model tier:** Use local lexical/content-hash retrieval first; use a cheaper model to rerank and summarize only the top matches. Realtime only handles the spoken query and concise answer.
- **latency:** 2-5 seconds for a recent search, with progressive results if browser or relay stores are slow.
- **cost:** $0.001-$0.01 per query, dominated by reranking; local retrieval and capsule lookup are negligible.
- **security:** Search must enforce sensitivity labels and source permissions. Do not return secret or private-message content merely because it matches; display a redacted hit and ask for confirmation before revealing sensitive context.
- **missing:** A single indexed search surface spanning evidence capsules, browser provenance, notes, pipeline transcripts/audio metadata, and relay records; A common provenance envelope with source URL or conversation ID, timestamp, content hash, and redaction state; A retention-aware result policy that clearly says when a source was evicted or never captured

### "Know when I am talking to another person, stay quiet unless it is genuinely urgent, and give me everything I missed when the conversation ends."
- **useful because:** Calendar quiet hours are not enough: an unplanned hallway conversation, phone call, or meeting can begin while the Mac and browser remain active. Combining pendant audio cues, Mac foreground/call state, calendar, and relay announcements would prevent socially disruptive interruptions while preserving urgent information and a trustworthy post-conversation handoff.
- **path:** pendant → relay-realtime → mac-vision → mac-planner → browser-extension → relay → faculty-perception → faculty-judgement
- **model tier:** Run a tiny on-device classifier for speech overlap and acoustic context; fuse it with deterministic Mac/browser/call signals locally. Use a cheap background model to rank deferred items. Realtime speaks only after a locally detected conversation boundary or an explicit owner request.
- **latency:** Silence decision under 300 ms; urgent-alert classification under 1 second; post-conversation digest within 3 seconds of the boundary.
- **cost:** Low recurring API cost because detection and queuing are local; roughly $0.001-$0.01 for a deferred-item summary.
- **security:** Do not record or transcribe bystanders. Keep acoustic features, not raw audio, on the pendant. Urgency policy must be owner-configurable; emergency-like alerts should require a conservative threshold and an audible escalation path.
- **missing:** A pendant-local conversation/overlap classifier that emits only bounded context signals; A cross-surface interruptibility state machine shared by pendant, relay, Mac, and browser; A deferred-announcement queue keyed to the interruptibility interval and a reliable boundary event; A policy editor for what counts as urgent


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: contradiction-aware memory repair, cross-surface provenance search, and conversation-safe interruption handling with post-conversation recovery. Each requires joining existing readers plus missing perception/state-machine logic; none assumes the pendant is currently registered.

**Biggest unknown:** Whether the backlog already contains a sufficiently similar proposal for conversation-aware interruption or provenance search; the recorder accepted all three as non-duplicates this round.

