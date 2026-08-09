# Harness derivation — relay-realtime — round 178

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Remember this as a personal rule and apply it next time: when I’m in a meeting, keep replies to one sentence unless I say otherwise."
- **useful because:** The owner can set voice interaction preferences in the moment, hands-free, and have them persist across sessions. That makes the pendant feel like a real assistant instead of a stateless demo.
- **path:** relay → memory → model-routing
- **model tier:** realtime to capture the rule quickly; a cheaper tier to persist and retrieve it later
- **latency:** A couple seconds to confirm it was saved; retrieval must be fast during conversation.
- **cost:** Low per invocation, dominated by a small write/read to a preference store.
- **security:** Store only what’s needed (preference text, scope, timestamp). Avoid storing sensitive content from meetings.
- **missing:** A shared preference store accessible to relay and used by routing/response shaping; A lightweight policy interpreter for applying preferences to response generation

### "If I say a task, then say “follow up when it’s done,” keep listening for completion and let me know even after we stop talking."
- **useful because:** This would be a standout feature: the owner can offload a task and trust the system to report back asynchronously, without polling or staying in a session.
- **path:** relay → mac-bridge → pendant
- **model tier:** realtime to capture the follow-up intent; cheaper background to watch the job and prepare the notification
- **latency:** Immediate confirmation of the watch; completion notice whenever it happens, even if the Mac is asleep.
- **cost:** Low ongoing cost if backed by job receipts; occasional notification events dominate.
- **security:** Only notify about the specific job the owner asked to watch. Keep messages short and avoid leaking details.
- **missing:** A working event delivery path from relay to pendant/paired device; Reliable job completion watch or receipt subscription; Persistence for watches across relay restarts

### "When I say 'take care of this' about something on my Mac or in a browser, carry it through end-to-end and tell me the truth: inspect the relevant state, perform the smallest complete action, verify the resulting state independently, and give me a spoken result with a receipt I can challenge later."
- **useful because:** Today the owner can hand off actions or get plans, but cannot reliably distinguish 'the agent tried' from 'the world changed.' This would make the pendant a dependable delegate rather than a voice-controlled launcher. It deliberately spans the worn microphone, always-awake relay, Mac planner/terminal, authenticated browser, and a second verification pass.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime only for intent extraction and a short spoken acknowledgement; gpt-5.6-luna for planning; gpt-4.1-mini or faculty-perception for independent visual/state verification; a cheap background model to compress the evidence receipt.
- **latency:** Acknowledge in under 1.5 s; ordinary completion within 30 s; long workflows may finish asynchronously and surface through the existing pendant inbox.
- **cost:** Roughly $0.02-$0.15 per ordinary invocation, dominated by planner and verification calls; browser screenshots and repeated retries dominate long jobs.
- **security:** The action may touch authenticated accounts and send or mutate external data. The system must retain a compact before/after evidence record, redact secrets from spoken output and receipts, and stop on an unverifiable result rather than claiming success. Owner policy allows execution without an extra gate when the utterance is explicit.
- **missing:** A durable transaction record linking plan, each action, independent observation, and final claim; A verifier that is required to observe postconditions through a different path than the executor; Rollback/compensation recipes for common reversible Mac and browser mutations; A relay-to-pendant delivery path for the final receipt when the voice session has ended

### "If my Mac is asleep or offline, let me explicitly hand the pendant a browser task such as 'open the insurance portal, download the renewal notice, and tell me the deadline,' using a session I previously paired, then return the result without exposing my cookies or asking me to leave the Mac awake."
- **useful because:** The pendant is worn away from the Mac, while the browser is currently the only place some accounts can be reached. This gives the owner useful remote continuity instead of silently failing whenever the Mac disappears. It is not a morning briefing: it is an on-demand, owner-initiated authenticated session with bounded data retrieval and a downloadable artifact.
- **path:** pendant → relay → browser-extension → browser → dashboard
- **model tier:** Realtime for the spoken request and a short status; a cheaper planner for browser actions; a sandboxed browser worker for navigation and extraction; realtime only again for the final spoken answer.
- **latency:** Acknowledge within 2 s; return text in 10-45 s; downloads and multi-page workflows can complete asynchronously.
- **cost:** About $0.01-$0.10 per invocation, dominated by sandbox browser minutes, screenshots, and document extraction.
- **security:** This is access to authenticated accounts. Pairing must be explicit and revocable, with per-origin session isolation, no cookie/token transcription into model context, encrypted short-lived storage, an audit trail, and a hard rule that extracted secrets are spoken only when directly requested. Mutating actions should be a separate explicit command from read/download tasks.
- **missing:** A Cloudflare Browser Rendering/Browser Run execution surface on the relay; A secure session-pairing and encrypted cookie vault that never enters model prompts; A relay-side artifact store with expiry and pendant-safe summaries; A browser action policy distinguishing retrieval from mutation without blocking the owner's stated maximum-access preference

### "When I ask 'why did you do that?' or 'what exactly happened?', replay the specific voice turn as a compact timeline: what the pendant heard, what the relay inferred, which Mac/browser actions ran, what each surface observed, and where uncertainty entered—then let me correct the mistaken interpretation by voice."
- **useful because:** A wearable assistant can act faster than the owner can inspect it, so a wrong action is otherwise opaque. This gives the owner a practical way to diagnose and correct failures without opening logs or remembering a job ID. It combines the pendant's session identity, relay transcript, planner actions, browser observations, and a human-sized spoken explanation rather than dumping telemetry.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheap background summarization over structured logs; realtime only to resolve 'that action' to a session and speak the explanation. Use a deterministic formatter for action names, timestamps, and evidence so the model cannot invent a narrative.
- **latency:** Resolve the referenced turn in under 2 s and speak a first three-sentence explanation within 5 s; offer deeper timeline details on button presses or follow-up questions.
- **cost:** Typically under $0.01 because most of the timeline is structured; cost rises to $0.03-$0.08 only when raw audio/transcript redaction or screenshot summarization is needed.
- **security:** Receipts can contain private page text, typed values, and audio. Keep raw evidence encrypted with short retention, redact secrets before model use, scope retrieval to the owner's session, and distinguish observed facts from inferred intent. Voice correction must create a new action rather than silently rewriting history.
- **missing:** A stable voice-turn/action correlation ID propagated from pendant through relay, planner, execute, and browser commands; A structured immutable event ledger with redacted before/after observations; A spoken query resolver for references like 'that' and 'the last thing'; A correction endpoint that records an amended intent while preserving the original evidence

### "While I am away from the Mac, let me ask 'what is on my screen?' or 'is that dialog safe to dismiss?', have the Mac capture the current display, and hear a concise visual answer; if I then say 'dismiss it' or 'click the blue button', execute exactly that on the still-matching screen."
- **useful because:** The owner cannot see the Mac while wearing the pendant, and application lists or DOM inspection cannot answer visual questions about canvas apps, dialogs, Ableton, or a stalled workflow. This would make the wearable a remote pair of eyes and hands, with a useful guard against acting on a screen that changed between observation and command.
- **path:** pendant → relay → mac-vision → mac-planner → dashboard
- **model tier:** gpt-4.1-mini computer-use loop for screenshot grounding and target selection; realtime relay only for low-latency speech; gpt-5.6-luna only when the visual question requires multi-step interpretation.
- **latency:** First visual answer in 3-6 s; an approved single click within 2 s after the follow-up; stale screenshots must fail closed rather than click.
- **cost:** About $0.02-$0.12 per question, dominated by screenshot vision and any repeated capture after a screen change.
- **security:** Screens may contain passwords, private messages, or financial data. Images need ephemeral encrypted handling and aggressive redaction from logs. Actions require a screen hash plus coordinate/target revalidation immediately before execution; never describe a visual guess as certainty.
- **missing:** The currently disabled Mac computer-use loop, with a screenshot capture and screen-hash API; A relay voice protocol carrying a visual observation reference into the next turn; Pre-action revalidation that rejects clicks against a changed display; A pendant-friendly spoken vocabulary for uncertainty and target disambiguation


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing capabilities: end-to-end delegated actions with independently verified postconditions; explicit authenticated-browser continuity while the Mac is offline; voice-queryable forensic timelines and correction; and remote screen vision with stale-screen-safe control. The common missing pieces are not more routing labels: durable correlation across pendant/relay/Mac/browser, immutable redacted evidence, independent postcondition verification, secure browser-session custody, and the currently disabled Mac computer-use/screenshot loop. The owner cannot have these today because existing plan/execute/browser routes stop at disconnected jobs and do not provide those cross-surface guarantees.

**Biggest unknown:** Whether /v1/ops/voice-runs/latest, /v1/ops/history, and /v1/ops/memory are sufficiently rich and correlated in the live relay; the proposal explicitly treats them as possible sources, not assumed implementations.

