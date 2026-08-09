# Harness derivation — relay-realtime — round 265

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Run a quick hardware check while I’m plugged in."
- **useful because:** While the pendant is physically connected to the Mac, the system can diagnose audio, storage, and link health in seconds, saving tedious manual troubleshooting.
- **path:** mac-bridge → relay → pendant
- **model tier:** Cheaper tier; this is deterministic diagnostics, not reasoning-heavy.
- **latency:** A few seconds to run and report.
- **cost:** Low; dominated by device I/O and logging, not model tokens.
- **security:** Diagnostics should be read-only where possible and clearly labeled. Any mutation (like firmware test modes) needs explicit confirmation.
- **missing:** A stable bridge command interface exposed to the relay for diagnostics; A standard schema for test reports and thresholds; Permissioned access to run tests without disrupting active recording

### "Remember my preferences and use them without me repeating them."
- **useful because:** It makes the pendant feel personal and reduces friction. The owner shouldn’t have to restate editor choice, reply length, or safety preferences every time.
- **path:** relay → mac-bridge
- **model tier:** Realtime uses a small projected memory slice; heavier memory management happens on the Mac.
- **latency:** No noticeable delay; memory should already be projected into the prompt.
- **cost:** Lower token cost over time if projection replaces bulky legacy context.
- **security:** Only relevant, scoped facts should be projected; sensitive facts must require explicit reveal.
- **missing:** Wiring the live prompt to use the existing memory projection route; A task-aware projection for voice surface; Telemetry to ensure stable head caching works

### "When I say “what changed since I left?”, compare the Mac, the browser tabs, and my mirrored iPhone with the last known checkpoint, then tell me only the meaningful changes and offer to continue the interrupted task."
- **useful because:** A worn pendant normally cannot know what happened while its owner was away. This turns returning to the desk into an immediate, cross-device re-entry point instead of forcing the owner to inspect three surfaces manually.
- **path:** pendant → relay → mac-planner → browser → iOS
- **model tier:** Use relay-realtime only to classify the short request and speak the result; use mac-planner for Mac/iPhone observations, browser harness for authenticated tabs, and a background model to rank changes and suppress noise.
- **latency:** Initial spoken acknowledgement under 500 ms; collect available snapshots within 10 s and stream a short result as each surface completes. If a surface is offline, say exactly which comparison is unavailable.
- **cost:** Roughly $0.01–$0.08 per invocation depending on page/screenshot volume; browser and vision extraction dominate, not the relay turn.
- **security:** Snapshots can contain private mail, documents, and authenticated pages. Keep raw captures on the owner's devices, send only extracted diffs to the relay, label source and timestamp, and never infer that an unchanged unavailable surface is unchanged.
- **missing:** A durable per-surface checkpoint store with explicit capture timestamps and expiry; Mac and browser snapshot adapters that expose current state without requiring a foreground action; A cross-surface diff/ranking worker and streaming result channel to the pendant

### "When I ask “what am I looking at?”, read the currently focused thing on my Mac or in my browser, identify the exact item and its source, and speak a useful one-sentence summary with a follow-up action such as copy the link, save it, or open it on my phone."
- **useful because:** The pendant has no display and the owner may be moving around. It would make the wearable a hands-free index into the precise object already in front of them, rather than forcing them to dictate titles or navigate menus.
- **path:** pendant → relay → mac-planner → mac-vision → browser → iOS
- **model tier:** Relay-realtime handles the utterance; mac-planner obtains focused-app metadata, browser harness obtains DOM/URL context, and mac-vision is used only when accessibility metadata is insufficient. A cheaper model summarizes extracted text.
- **latency:** Acknowledge immediately; return a one-sentence identity/summary in 2–4 s for accessible content and under 8 s for vision fallback. Actions must report their job receipt.
- **cost:** About $0.005–$0.04 per request; vision fallback and large-page extraction dominate.
- **security:** Focused content may be confidential. Redact passwords and secure fields, avoid uploading full pages when title/selection/accessibility text suffices, and speak only a bounded excerpt. Explicitly identify when the result came from visual inference rather than page metadata.
- **missing:** A unified focused-object contract across macOS accessibility, browser DOM, and iPhone Mirroring; A relay route that can return a spoken result while retaining an actionable object reference; Mac-vision fallback that can target the identified object without losing the originating surface

### "When I say “make this safe to share,” inspect the document or page I am currently focused on, detect secrets and personal data, create a redacted copy with a review summary, and stage it for sending or saving wherever I specify."
- **useful because:** Sharing from a small wearable is dangerous because the owner cannot inspect every field. This gives them a practical voice-first redaction pass over the exact browser/Mac object they are viewing, without pretending the relay can see it by itself.
- **path:** pendant → relay → mac-planner → mac-vision → browser → iOS
- **model tier:** Use relay-realtime only for intent and status. Extract content locally through Mac/browser agents, run a cheaper structured PII/secrets detector first, use a stronger model only for ambiguous entities, then let mac-planner stage the artifact.
- **latency:** Preview findings in 5–10 s for ordinary text and under 30 s for PDFs/images. Never auto-send; stage the result and speak the count and categories of redactions.
- **cost:** Approximately $0.02–$0.20 per artifact, dominated by OCR/vision and document size; local regex/entropy scans should handle common keys cheaply.
- **security:** The redaction model itself sees sensitive material. Prefer local extraction and deterministic detectors, keep originals untouched, store the redacted artifact with provenance, make irreversible sending a separate explicit command, and expose every redaction for review on the Mac.
- **missing:** A focused-object capture and artifact staging API spanning Mac and browser; Deterministic secret/PII detector plus reviewable redaction format for text, PDFs, and images; A non-destructive artifact store with provenance and a send/save handoff to existing Mac/browser actions


## Changes it proposed to its own stack

### `integration` — Build a focused-object broker shared by the relay, Mac planner, Mac vision, browser extension, and iPhone-mirroring facet. On request it captures a bounded object reference (surface, app/tab, URL, accessibility role, selected text, screenshot hash, timestamp) rather than an unbounded screen dump; it supports read, summarize, redact, copy-link, save, and stage-for-send operations, and emits a provenance receipt tying the result to the exact source object. Add a short-lived encrypted object cache so a follow-up pendant utterance can refer to “that” without recapturing or guessing.
- **owner gets:** The owner can point at anything on any screen and operate it by voice from the pendant, including safely preparing a shareable version. Today each surface can act, but the relay cannot refer to one exact object consistently across turns or explain what it acted on.
- effort: High: a new cross-surface contract, adapters for macOS accessibility/browser DOM/iPhone Mirroring, Mac-vision fallback, encrypted short-lived cache, and receipt plumbing. Prototype on Safari and one native app first, then expand.  ·  risk: A stale or visually misidentified object could cause the wrong mutation. Default to read/preview and require a separate explicit send/delete/purchase utterance; expire references quickly, show source and confidence in the spoken response, and retain undo/provenance where available.
- cost: Low recurring relay cost; extraction is mostly local. Vision fallback and OCR may add $0.01–$0.10 per request, and the cache needs modest encrypted disk storage on the Mac/relay.  ·  latency: Accessible-object reads 1–3 seconds; browser extraction 2–5 seconds; vision fallback 5–15 seconds. Immediate acknowledgement and a short completion event are required.
- security: High-value private-content boundary. Keep raw object data on the Mac whenever possible, transmit bounded fields, encrypt the cache, expire it within minutes, omit password/payment fields, and log only hashes plus provenance.
- depends on: A real relay-to-Mac job/result stream rather than only fire-and-forget action lists; Adapters exposing focused accessibility/DOM context and iPhone Mirroring state; A short-lived encrypted object-reference cache and receipt schema


## What it asked for

_Nothing._
## Its own summary

Recorded four new items. The strongest is a cross-surface focused-object broker: “what am I looking at?”, safe redaction/staging, and exact provenance across Mac, browser, iPhone Mirroring, relay, and pendant. Also recorded a return-from-away change digest and the integration work needed to make follow-up references like “that” reliable. The owner still cannot have these today because there is no shared focused-object identity, cross-surface checkpoint/diff store, bounded capture contract, or encrypted short-lived object cache; those are the concrete missing pieces.

**Biggest unknown:** Whether the Mac planner and browser harness can expose focused accessibility/DOM objects without full screenshots; that determines whether these features are low-latency and privacy-preserving or require the slower vision fallback.

