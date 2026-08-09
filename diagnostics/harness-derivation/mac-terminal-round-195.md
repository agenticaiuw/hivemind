# Harness derivation — mac-terminal — round 195

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “handle what’s in front of me,” use the active Safari tab and visible Mac screen as context, explain the important state in two spoken sentences, and—only if my request is unambiguous—carry out the obvious next step and tell me exactly what changed."
- **useful because:** The owner can act on a web page without narrating URLs, copying text, or switching attention to the laptop. It uniquely combines the pendant’s immediate voice intent, browser-held authenticated state, and Mac vision/action reach; a browser or Mac alone cannot provide the hands-free, context-aware handoff.
- **path:** relay-realtime → pendant → mac-vision → browser-extension → mac-planner → mac-terminal
- **model tier:** Realtime for the short spoken interpretation; a cheaper background planner for extracting page state and selecting/validating the next action; vision only when DOM inspection is insufficient.
- **latency:** Acknowledge on the pendant within 500 ms, speak the summary within 4 s, and complete a simple action within 8 s. Long tasks should stream truthful progress rather than hold the voice turn open.
- **cost:** Typically one realtime turn plus a small text-planner call; vision is the dominant variable cost and should be invoked only when browser inspection cannot establish state.
- **security:** Authenticated page text, screenshots, and the requested action leave Safari/Mac for the local agent and relay planner. Never read hidden page fields or passwords by default; preserve the existing trusted maximum-access policy, but speak the target, scope, and receipt after mutations so mistakes are discoverable.
- **missing:** A single cross-surface intent that atomically snapshots active-tab metadata, DOM text, and current screenshot under one turn ID; A planner contract that distinguishes explanation-only from execute-next-step and returns evidence plus a post-action observation; A compact spoken result/receipt path from local Mac execution back to the pendant

### "While I’m walking, let me say “get me there” or “what’s next?” and have the pendant give the next turn or place-specific instruction from the route currently open in Safari, refresh the route on the Mac if traffic or closures change, and recover cleanly if the laptop, browser, or wearable link drops."
- **useful because:** This turns the currently authenticated Maps session into a genuinely hands-free travel instrument: the wearable is the only interface the owner needs, while the Mac/browser can see and refresh a route that the pendant cannot. It is useful precisely because it continues across link loss instead of pretending the last instruction is current.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Realtime only for short turn requests and speech; a low-cost background route monitor compares browser observations and traffic/closure changes, escalating to vision for map canvas content.
- **latency:** Button/voice acknowledgement under 500 ms; next instruction under 3 s; route-change warning within 30 s of a changed browser observation. Offline mode should immediately replay the last confirmed instruction with its age, never fabricate a new turn.
- **cost:** Low steady cost for browser observation and local diffing; realtime usage is only per spoken request. Vision and external map lookups dominate when the route is rendered as a canvas or changes materially.
- **security:** Location and authenticated Maps URLs are sensitive. Keep route snapshots local to the Mac by default, send only the minimum next-turn text to the relay, and require an explicit spoken request before starting navigation or opening a destination. Never expose the full route in the pendant’s public status.
- **missing:** A route-state adapter that extracts ordered turns, current position, ETA, and freshness from the active Maps tab rather than treating it as generic page text; A durable, age-stamped navigation cursor stored on the pendant and reconciled exactly once after reconnect; A link-aware route monitor that can distinguish stale browser state from a genuine route change

### "When I reconnect after sleep, travel, or a crash, tell me “you were in the middle of X,” show me the exact browser/Mac state it recovered, and let me say “continue” to resume only the unfinished part—without repeating completed side effects."
- **useful because:** The owner should never have to remember whether a command, browser submission, or research task actually finished. This is a user-facing continuity guarantee across the worn device, always-awake relay, Mac job store, and authenticated browser—not merely a nicer job log—and it prevents both silent abandonment and duplicate real-world actions.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Cheap background reconciliation on reconnect; realtime only to speak the compact interruption summary and accept “continue.” Use the judgement/action faculties for resumability classification, not the expensive voice model.
- **latency:** Reconnect summary within 2 s of the Mac bridge becoming healthy; resume confirmation spoken in under 1 s; first safe resumed step within 5 s. Long-running work reports progress via the existing status beacon and relay events.
- **cost:** Small background model call per interrupted job and a lightweight state diff; realtime cost is one short turn. Browser re-observation or vision is invoked only for steps whose post-state is unknown.
- **security:** The summary may contain private browser titles, file paths, or command output, so keep full evidence on the Mac and send a redacted spoken capsule. Resuming shell/browser mutations must use the owner’s existing maximum-access policy, but never claim completion unless a post-state observation or receipt proves it.
- **missing:** Boot-time reconciliation that marks stale processing jobs and open ledgers as interrupted, joins every ledger to its job ID, and emits a resumable cursor; Exactly-once action execution using the existing idempotency engine, with explicit unknown-post-state rather than blind replay; A cross-surface reconnect event carrying bridge health, pendant turn ID, browser session, and the interruption capsule to the pendant

### "When I say “send this to the right place,” take the useful content from the page or document I’m looking at, identify the intended person/project from my current Mac and authenticated browser context, draft it in the right app, and let me review the exact excerpt, recipient, and source from the pendant before it is sent."
- **useful because:** The owner loses time and makes errors moving information between browser tabs, Mail, Notes, project folders, and reminders. This would turn a spoken intent plus the thing currently in view into a provenance-preserving cross-application handoff; no single browser session or Mac action knows both what the owner is looking at and where it belongs.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap text planner for extraction, entity matching, and destination ranking; use vision only for content that has no accessible text; use realtime solely for the short spoken review and correction loop.
- **latency:** Identify source and proposed destination within 4 seconds, speak a review capsule in under 2 seconds after planning, and complete the approved send/save within 5 seconds. If extraction is long, stream only stage changes, not raw private content.
- **cost:** Usually one small planner call and local app/browser actions; vision and large-page extraction dominate cost and should be bounded to the selected region or relevant text.
- **security:** Content, recipient identities, and authenticated page state are highly private. Keep full source and draft on the Mac; send only a redacted review capsule to the relay; attach a source URL/document identity and field-level provenance to the draft. The owner’s review must cover recipient, destination app, and quoted content, with no silent substitution after review.
- **missing:** A cross-surface handoff object containing source snapshot, extracted excerpt, destination candidate, provenance, and draft revision ID; Entity resolution across active browser sessions, Mac projects, Contacts/Mail/Notes, and the owner’s context graph; A pendant review protocol that can present a compact diff and accept corrections without reopening the laptop; Post-send verification that observes the destination app and records exactly what was committed


## What it asked for

_Nothing._
## Its own summary

This round established the Mac bridge and Safari extension are online, with two tabs (active Google Maps) and full control, browser, vision, accessibility, and screen-recording permissions. I recorded three distinct owner-facing capabilities: (1) a hands-free active-page explanation/action handoff, (2) link-resilient spoken route guidance from the live Maps tab, and (3) reconnect-time interruption recovery with exactly-once resume. The third is the highest-value continuity feature: it turns stale jobs and browser state into a truthful wearable summary and resumable work instead of duplicate side effects.

**Biggest unknown:** The system still lacks the connective contracts rather than the individual surfaces: one atomic active-tab+screen snapshot, a Maps route-state adapter, and boot-time job/ledger reconciliation with job IDs, post-state classification, and exactly-once resume. The newly granted Mac diagnostics schemas still do not resolve live (the actual GET /machine-context and GET /health routes do), and the already-queued USB serial diagnostics request remains unanswered; I did not re-ask for either.

