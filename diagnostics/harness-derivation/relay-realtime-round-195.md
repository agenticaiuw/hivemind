# Harness derivation — relay-realtime — round 195

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“I may have exposed a secret—find where it appeared across my Mac and signed-in browser, tell me exactly what is at risk, and contain it.”"
- **useful because:** Today the owner must remember which app, terminal, document, and browser tab contained the secret and manually coordinate containment. This would turn a panic-level incident into one spoken request: locate likely exposures, stop further propagation, and present only high-confidence actions needing a decision.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** Realtime relay only for intent and concise risk questions; mac-planner performs the multi-step investigation; browser-extension supplies authenticated page/session evidence; mac-terminal searches local files, shell history, clipboard and recent logs; dashboard shows an auditable incident timeline.
- **latency:** A first risk statement within 5 seconds; investigation and containment may take 1–3 minutes with spoken progress and a final digest.
- **cost:** About $0.05–$0.30 per incident depending on planner turns; browser and local evidence collection dominate latency, not speech.
- **security:** This handles extremely sensitive data. Evidence should remain on the Mac/browser where possible, with only hashes, locations, and minimal excerpts sent to the relay. Revocation, deletion, or external notification must be explicitly confirmed; read-only discovery can be proactive.
- **missing:** A secret-detection and correlation engine spanning local files, clipboard/history, browser DOM and network-visible pages; A containment adapter for common credentials and a transactional plan with rollback; An evidence-redaction protocol and incident-specific retention policy; A dashboard incident view and pendant progress vocabulary

### "“Keep me from losing the thread while I move between places: when I leave my Mac, preserve the exact next step and let me resume it from the pendant later.”"
- **useful because:** Current jobs and spoken sessions are separate from the owner's physical context. The owner can walk away mid-debugging or mid-form and later has to reconstruct what was open, what was decided, and what remains. A portable handoff would make the worn device a true continuation of the Mac rather than a second inbox.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay captures the handoff phrase and gives a two-sentence resume prompt; a cheaper background planner snapshots the active task state, open app/tab identifiers, unsent drafts, blockers, and safe next action. mac-vision contributes a visual checkpoint only when needed.
- **latency:** Capture confirmation under 1 second; checkpoint under 10 seconds; resume answer under 3 seconds when the owner asks later.
- **cost:** Roughly $0.01–$0.08 per checkpoint, dominated by visual/page summarization. Most checkpoints can use structured state without a model call.
- **security:** Do not upload full screens or document contents by default. Store encrypted local references and redacted summaries, expire checkpoints automatically, and require confirmation before reopening or transmitting an unsent draft.
- **missing:** A durable task-handoff object with versioned checkpoints and expiry; Mac hooks for active app/window/tab and unsaved-document metadata; A pendant-to-relay handoff gesture and resume query path; Cross-device encrypted keying and a dashboard to inspect/delete checkpoints

### "“Before I send this, compare it with the source I was looking at, flag claims that changed or are unsupported, and read me only the risky differences.”"
- **useful because:** The owner currently has separate browser reading, Mac editing, and voice interaction, but no cross-surface preflight that checks a draft against its actual source. This catches stale numbers, accidental recipients, and unsupported claims while the owner is away from the keyboard.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime relay handles the short spoken request; browser-extension extracts the source page and recipient context; mac-planner reads the draft and computes structured diffs; a background model classifies factual, privacy, and tone risks. Relay speaks only high-severity findings and can queue a fuller report.
- **latency:** High-level risk verdict within 8 seconds, with a detailed report within 30 seconds. No external send should occur until the owner explicitly chooses to proceed.
- **cost:** About $0.03–$0.15 per preflight; extraction and comparison dominate tokens, while the relay response is small.
- **security:** Drafts and authenticated pages are sensitive. Keep raw content local, send redacted spans or hashes when possible, distinguish source evidence from model inference, and never silently alter or send the draft.
- **missing:** A cross-surface source/draft binding that survives tab and app changes; Structured claim extraction with citations and change timestamps; Recipient/privacy analysis across Mail and browser forms; A compact pendant confirmation vocabulary plus dashboard diff view

### "“Why did that fail? Trace the request from what I said through the relay, Mac, and browser, identify the first real fault, and tell me the one fix that will prevent a repeat.”"
- **useful because:** Today a failure is fragmented across spoken history, queued jobs, Mac receipts, browser command state, and pipeline health. The owner gets a vague failure message and must debug the hive manually. A causal trace would make the system self-diagnosing instead of merely self-reporting.
- **path:** pendant → relay → mac-planner → mac-terminal → browser-extension → dashboard
- **model tier:** The relay asks one concise follow-up only when the job reference is ambiguous. A background diagnostic model correlates structured events and logs, then produces a causal graph and confidence-ranked fix; the dashboard exposes raw evidence for inspection.
- **latency:** A preliminary cause in 5 seconds from existing receipts; deep trace in under 60 seconds. The pendant should speak the first fault and queue the evidence graph rather than read logs aloud.
- **cost:** About $0.02–$0.12 per trace. Correlation over structured events is cheap; long logs and screenshots dominate cost.
- **security:** Logs may contain transcripts, page contents, credentials, or personal data. Redact secrets before model submission, retain only a bounded trace keyed to the job, and label hypotheses versus observed facts. Fixes should be proposed first; automatic repair must be separately selectable.
- **missing:** A shared causality/event schema carrying session, job, action, surface, timestamps and parent IDs; Mac and browser adapters that emit redacted failure evidence, not just final receipts; A trace assembler and root-cause evaluator; A dashboard graph view and a pendant vocabulary for confidence and uncertainty


## What it asked for

_Nothing._
