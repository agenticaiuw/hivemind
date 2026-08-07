# Harness derivation — faculty-perception — round 49

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-input-reachability** — At 2026-08-07T11:38:40Z, AI Pendant Agent is running from /Users/evanliu/Applications/AI Pendant Agent.app, but Accessibility is not trusted for that exact binary; screen recording is also not granted. inputReachability.status=failed and uiActionsWillReachTheScreen=false, so UI actions cannot be trusted despite success receipts.
  - evidence: GET /observe response: accessibility.trusted=false, screenRecording=false, inputReachability.status=failed, consequence says synthesized events are not accepted.
- **system-connectivity** — At 2026-08-07T11:38:40Z, the Mac bridge is online and relay reachable, but the Chrome browser extension is offline with 4 pending commands and 3 durable browser sessions/tabs visible only in local state.
  - evidence: GET /ops/status and GET /browser/status: macBridgeOnline=true; browser.online=false; pendingCommands=4; observe lists 3 sessions/tabs.
- **computer-use-safety-state** — Computer-use loop is disabled; a vision model is configured but vision upload consent is false, maxSteps=25. Foreground app is Claude (com.anthropic.claudefordesktop), and secure input is inactive.
  - evidence: GET /ops/status computerUse.loopEnabled=false, visionModelConfigured=true, visionUploadConsented=false; GET /observe foregroundApp and secureInputActive=false.
- **timezone-conflict** — Owner memory says timezone America/Chicago, while live Mac machine-context reports America/New_York. Do not infer local time or schedule against the Mac timezone without resolving this conflict.
  - evidence: discover owner remembered timezone America/Chicago; GET /machine-context reports timezone America/New_York.

## Capabilities it proposed

### "Before you act, tell me what each device can actually see right now—and stop if any view is stale, disconnected, or only pretending an action succeeded."
- **useful because:** The owner currently gets false confidence: Mac UI receipts can report success while events do nothing, and browser commands can queue while Chrome is offline. A live, cited preflight makes the system honest before it changes anything.
- **path:** pendant: owner says 'check state' or hears a brief warning; relay: gathers timestamped observations and preserves the preflight receipt; mac-planner: requests read-only /observe, /ops/status, and machine-context; browser-extension: reports heartbeat, tab/session freshness, and pending command count; unified: reconciles conflicts and speaks one short sentence; faculty-perception: assigns freshness and confidence, never claims reachability from intent alone; faculty-judgement: blocks plans whose required surface is stale or untrusted; faculty-action: executes only after the preflight passes
- **model tier:** Use a cheap background/text model to normalize typed observations; reserve realtime only for the spoken warning or interactive follow-up.
- **latency:** Under 1 second when Mac and relay are online; if a surface is offline, return the stale evidence in under 2 seconds rather than waiting for it.
- **cost:** Low: mostly local JSON reads and one small normalization call; realtime cost only when the owner asks verbally.
- **security:** Observations may expose foreground app names, URLs, and account state; redact page contents by default, retain short-lived receipts, and require confirmation before uploading screenshots or private page text. Never treat a success receipt as proof when inputReachability is failed.
- **missing:** A typed /perception/preflight endpoint or shared schema with source timestamps, TTLs, and confidence; A hard judgement gate that consumes the preflight and refuses actions requiring untrusted UI reachability; Browser heartbeat recovery/notification so queued commands cannot look completed; Exact-binary Accessibility and Screen Recording grants for AI Pendant Agent, then a fresh reachability probe

### "When something I asked for does not happen, say exactly where it broke—what I said, what the relay heard, which device was selected, what command was sent, what the device reported, and whether the outside world changed—then give me the smallest safe recovery."
- **useful because:** Today failures collapse into a vague 'failed' even when different links disagree. This would let the owner distinguish mishearing, stale browser state, unreachable Mac input, planner refusal, and an action that completed but was not observed, without manually searching logs.
- **path:** pendant: captures the request and any correction the owner speaks; relay: correlates audio, transcript, pipeline events, and durable job IDs; mac-planner: contributes plan/route decisions and preconditions; browser-extension: contributes command IDs, tab/session identity, heartbeat state, and page evidence; mac-terminal: contributes allowlisted command output and local logs; faculty-perception: builds a timestamped causal graph and labels each edge observed, inferred, or unknown; faculty-judgement: chooses a reversible recovery and asks only for confirmation where needed; faculty-action: performs that recovery and appends an outcome receipt
- **model tier:** Use deterministic correlation and a cheap text model for classification/summarization; use realtime only if the owner asks aloud for the diagnosis.
- **latency:** A first diagnosis within 3 seconds for local history, with deeper cross-device reconstruction continuing in the background and a notification on the pendant.
- **cost:** Low API cost: mostly indexed event joins and short summaries; storage/indexing and redaction dominate rather than model tokens.
- **security:** Failure traces can contain private URLs, mail subjects, transcripts, and command arguments. Store encrypted, redact secrets and page bodies by default, enforce per-owner retention, and require explicit confirmation before replaying any recovery that could send, delete, purchase, or submit.
- **missing:** A shared causality/event schema spanning pendant audio, relay pipelines, Mac jobs, terminal runs, and browser commands; A durable correlation ID propagated from spoken request through every delegated step; A read-only event index with redaction, retention, and confidence labels; Recovery planners that consume the diagnosis without treating an untrusted success receipt as proof


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: Mac bridge and relay are online, but Chrome extension is offline with 4 queued commands; computer-use is disabled; vision upload consent is false; and the exact running AI Pendant Agent binary still lacks Accessibility and Screen Recording, making inputReachability failed and GUI receipts untrustworthy. Also found an unresolved timezone conflict (owner memory America/Chicago vs live Mac America/New_York). Recorded all four findings, warned mac-vision/judgement/unified, and proposed a cross-device perception preflight that blocks stale or untrusted actions.

**Biggest unknown:** Whether the owner has actually granted Accessibility and Screen Recording to the exact running AI Pendant Agent binary and restarted it; live probes still say no. Authoritative timezone also remains unresolved.

