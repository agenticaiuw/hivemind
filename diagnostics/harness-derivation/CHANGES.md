# Changes the agents proposed

Written by `scripts/harness-ledger.mjs`. Status is owned by this file and
survives re-runs — refreshing adds new proposals, it never resets what you
have already marked done.

**38 open · 20 implemented · 46 other**

The `×` column counts how many times a proposal was made. Anything above 1
was arrived at independently more than once, which is the strongest signal
in here.

## Open

| id | layer | proposed by | × | change |
| --- | --- | --- | --- | --- |
| `chg-a813b918` | relay | mac-planner | 5 | Enable a bounded audio-retention sweeper and per-job deletion controls: default to short retention for generated briefings, delete expired R2 objects  |
| `chg-16bc5dee` | browser-harness | browser-extension | 4 | Add a durable browser job runner with two backends: the authenticated Safari bridge for owner-private pages and Cloudflare Browser Run for public page |
| `cap-bff5f829` | capability | browser-extension | 4 | Check my logged-in web accounts for anything urgent, summarize it, and draft (but do not send) any replies that need my attention. |
| `cap-8c36c70a` | capability | browser-extension | 4 | Every weekday morning, check my logged-in calendar, task board, and travel reservations, then tell me the three things I need to know and prepare a su |
| `cap-9a41624d` | capability | browser-extension | 4 | Watch this logged-in page for a meaningful change and tell me when it happens, with the before-and-after evidence. |
| `cap-dde88711` | capability | mac-planner | 4 | Every weekday at 8:30, prepare a concise workday brief: today's calendar, unread mail grouped by urgency, and the top three actions; save it as an aud |
| `cap-c5c14868` | capability | mac-planner | 4 | When I say 'triage my inbox', classify unread mail into urgent, reply soon, reference, and noise, draft replies for the first two categories, and show |
| `cap-60031093` | capability | mac-planner | 4 | Keep a daily 'closeout' routine: at 5:30 PM, summarize unfinished calendar items and the notes/files I touched today, then create a short checklist fo |
| `cap-5bd640c5` | capability | mac-planner | 4 | Watch my chosen logged-in web pages once a day and tell me only what changed; prepare drafts for any follow-up forms, but stop before submitting. |
| `cap-2a78a3d7` | capability | relay-realtime | 4 | “Check the weather and read the highlights to me.” |
| `chg-30c6ee4e` | dashboard-ux | browser-extension | 4 | Add a Jobs inbox shared by web, menubar, and iOS: each job shows status, source links, last update, evidence snippets, sensitivity, proposed actions,  |
| `chg-b453effa` | dashboard-ux | mac-planner | 4 | Add a unified Jobs inbox shared by web, menubar, and iOS: queued/running/completed/failed jobs, source timestamps, concise result, audio-play button,  |
| `chg-c3788e7b` | interaction | browser-extension | 4 | Make browser work explicitly two-phase: 'inspect' returns a concise result with citations and a proposed action; 'apply' repeats the exact destination |
| `chg-aace6694` | mac-harness | mac-planner | 4 | Add typed, read-only observability endpoints for job execution: running apps, foreground app, accessibility state, browser tabs, and allowlisted direc |
| `chg-e4ff3197` | memory | browser-extension | 4 | Replace raw browser-page insertion into context with expiring, source-backed facts: store only normalized facts plus source URL, observedAt, confidenc |
| `chg-a82e0b13` | memory | mac-planner | 4 | Replace per-surface hand-written fleetContext prompt sections with a compact, typed context service that returns only task-relevant facts, each with s |
| `chg-e567ac6a` | model-routing | mac-planner | 4 | Add an asynchronous job router: realtime handles only immediate conversational acknowledgement and dispatch; a cheaper background model handles calend |
| `chg-5b887962` | routines | relay-realtime | 4 | Add a Worker-side scheduler using Cron Triggers and Durable Object alarms to run routines even when the Mac is asleep, with a simple queue that delega |
| `cap-2fb3dd01` | capability | mac-planner | 3 | Every weekday morning, give me a short audio brief of today's calendar, unread important mail, weather, and any browser jobs that finished overnight. |
| `cap-4f5af34d` | capability | mac-planner | 3 | Check my authenticated browser accounts for anything that needs my attention, then put findings in a review queue instead of changing anything. |
| `cap-2eef696b` | capability | mac-planner | 3 | When I say 'clean up my desktop', group obvious screenshots and downloads into dated folders, but show me the proposed moves first. |
| `cap-d90ef7f1` | capability | mac-planner | 3 | Before my next meeting, prepare a one-page brief from the calendar invite, recent related mail, and approved web sources, save it to my Mac, and tell  |
| `cap-817211fc` | capability | mac-planner | 3 | Every weekday morning, give me a short brief of today's calendar, unread important mail, and the one thing I should prepare for; let me hear it on the |
| `cap-511245d4` | capability | mac-planner | 3 | When I say 'research this' or schedule a topic, investigate the web, summarize the best sources, and leave a cited note and a short audio briefing for |
| `cap-2b03a27d` | capability | mac-planner | 3 | Clean up my Downloads: identify duplicate, temporary, and likely finished files, show me a proposed plan, then move only the approved items into an ar |
| `cap-a5a9a6a9` | capability | mac-planner | 3 | Turn my unread mail into a priority list and draft replies for the top three, but never send anything without showing me the drafts first. |
| `cap-64c3562b` | capability | relay-realtime | 3 | “When I get back to my desk, summarize what happened while I was away and queue anything urgent.” |
| `cap-d5ef6ea9` | capability | relay-realtime | 3 | “Remind me every weekday at 5 to shut down and summarize what I did today.” |
| `cap-6bbef5ec` | capability | relay-realtime | 3 | “Read me the top three things I should care about right now.” |
| `chg-a649e91c` | dashboard-ux | mac-planner | 3 | Ship a unified Jobs inbox across web, menubar, and iOS showing queued/running/completed/failed work, source account, evidence links, data sensitivity, |
| `chg-05a523e6` | interaction | mac-planner | 3 | Make every Mac plan two-phase by default: first return a concise preview with affected app/files/URLs and expected side effects, then execute only the |
| `chg-75156244` | mac-harness | mac-planner | 3 | Add a mandatory server-side confirmation broker around POST /execute: classify each action batch, require a short-lived token for external side effect |
| `chg-85f818f7` | mac-harness | mac-planner | 3 | Add a real policy gate around POST /execute even when FULL_CONTROL_MODE is enabled: classify actions into read-only, reversible, and consequential; re |
| `chg-18a9c60f` | memory | mac-planner | 3 | Replace hand-written per-surface fleetContext prompt sections with a single typed context service that stores compact facts, provenance, sensitivity,  |
| `chg-0096a2b3` | memory | mac-planner | 3 | Replace per-surface hand-written fleetContext prompt sections with a shared, typed context compiler: retrieve only task-relevant entities/relations, a |
| `chg-38c86bb7` | model-routing | mac-planner | 3 | Split work into a cheap asynchronous planner/classifier, deterministic Mac/browser executors, and realtime only for live dialogue and ambiguous confir |
| `chg-f79dcdb8` | routines | relay-realtime | 3 | Add a first-class scheduler/queue for delayed and recurring work in the relay, backed by Durable Objects (alarms) or Worker Cron. Provide a routine st |
| `skill-ba1d5d1a` | firmware | mac-vision | 1 | computer_vision.screenshot |

## Implemented

| id | layer | proposed by | × | change |
| --- | --- | --- | --- | --- |
| `cap-d65785c8` | capability | browser-extension | 6 | “Read the relevant pages in my open browser tabs, compare the options, and give me a short brief with links and any deadlines.” |
| `cap-9764ec65` | capability | browser-extension | 6 | “Research this topic across the public web, check the sources, and send me a cited answer later.” |
| `cap-2a60c5ba` | capability | mac-planner | 6 | “Research this topic and leave me a concise source-linked briefing on my Mac, with an audio version I can play later.” |
| `cap-d9af189b` | capability | relay-realtime | 6 | “Summarize the key points from this page and read them to me later.” |
| `chg-43804606` | dashboard-ux | browser-extension | 6 | Add a Browser Jobs view shared by web, menubar, and iOS: active/queued/completed jobs, per-site permission scope, source evidence, extracted result, p |
| `chg-56aa1998` | dashboard-ux | mac-planner | 6 | Add a unified Jobs and Approvals view shared by web, menubar, and iOS: each job shows purpose, sources accessed, files/apps touched, risk level, estim |
| `chg-12222176` | firmware | relay-realtime | 6 | Implement adaptive duplex behavior: when downlink audio is playing, reduce or pause uplink capture/encoding to avoid LTE contention; resume capture af |
| `chg-075869de` | integration | mac-planner | 6 | Make FULL_CONTROL_MODE execute through a capability-scoped confirmation broker instead of bypassing actionRisk. Classify every action (read, reversibl |
| `chg-81e5c92d` | integration | relay-realtime | 6 | Add a server-side browser harness (Cloudflare Browser Run) so the relay can perform read-only web tasks without requiring the Mac to be online, with s |
| `chg-5fc73ce3` | mac-harness | mac-planner | 6 | Add transactional desktop jobs: each plan has a preview, stable job/action IDs, preconditions (expected app/path/hash), checkpoints, result receipts,  |
| `chg-5415e046` | memory | browser-extension | 6 | Create a browser-job memory tier separate from conversational context: retain only normalized facts, source URLs, retrieval timestamps, consent scope, |
| `chg-a18cc4f0` | memory | browser-extension | 6 | Add a browser-site capability registry in the knowledge graph: per origin, allowed paths, login/session status (never credentials), extraction recipe, |
| `chg-96771ece` | memory | mac-planner | 6 | Unify fleetContext and the knowledge graph behind a scoped memory service that stores facts with provenance, sensitivity, confidence, expiry, and last |
| `chg-fa7c3587` | model-routing | mac-planner | 6 | Route deterministic Mac requests (open app/URL, list a directory, create a standard reminder, read a known file) through a typed intent parser and loc |
| `chg-cd89301b` | model-routing | mac-planner | 6 | Introduce a policy router that classifies requests into realtime dialogue, deterministic Mac/browser execution, cheap background summarization, or hig |
| `chg-ea640c81` | model-routing | relay-realtime | 6 | Introduce a clear tiering rule: realtime relay model only handles conversational intent capture, clarification, and short confirmations. Any task that |
| `chg-324de76f` | stack | relay-realtime | 6 | Align the stack spec and orchestrator tool registry for the realtime agent, and publish a single authoritative capability manifest (tools, endpoints,  |
| `cap-e49fb28e` | capability | mac-planner | 5 | “Research this topic, compare the best options, and leave me a short audio recommendation—don’t buy anything.” |
| `chg-0aa257d0` | dashboard-ux | browser-extension | 5 | Add a unified Jobs inbox across web, menubar, and iOS showing running/blocked/completed browser and Mac jobs, compact evidence, sensitive-field redact |
| `chg-6360d815` | memory | mac-planner | 5 | Replace per-surface hand-written fleetContext sections with a compact, typed context projection: stable preferences and permissions, current tasks, an |

## Rejected / duplicate

| id | layer | proposed by | × | change |
| --- | --- | --- | --- | --- |
| `chg-bc35ae04` | browser-harness | browser-extension | 6 | Add a first-class browser session API: list tabs with stable tab IDs, select a tab explicitly, bootstrap navigation only after confirmation, capture a |
| `chg-2fffc681` | browser-harness | browser-extension | 6 | Add a durable browser-task runner: bootstrap a tab via navigate, maintain task-scoped tab IDs, execute read/click/type/wait sequences with timeouts, c |
| `chg-086a6904` | browser-harness | browser-extension | 6 | Replace generic browser action results with a typed, policy-enforcing runner: classify commands as read-only or mutating; enforce origin/path allowlis |
| `cap-fc6643a7` | capability | browser-extension | 6 | “Every weekday morning, check my authenticated work portal for new high-priority items and tell me only what needs my attention.” |
| `cap-1e04349c` | capability | browser-extension | 6 | “Fill out this web form from the information I give you, stop before submission, and show me exactly what will be sent.” |
| `cap-daaf6d3e` | capability | browser-extension | 6 | Research this topic across my logged-in websites, compare the results, and send me a concise audio brief later. |
| `cap-c18a0fce` | capability | browser-extension | 6 | Watch this logged-in page or price/availability page and tell me only when the specified condition changes. |
| `cap-75ee1730` | capability | browser-extension | 6 | Fill out this online form using the details we discussed, stop before the final submit, and show me exactly what will be sent. |
| `cap-eb3ab088` | capability | browser-extension | 6 | “Check my authenticated work sites and inboxes for anything urgent, summarize it, and leave me a short audio briefing.” |
| `cap-28eaa582` | capability | browser-extension | 6 | “Fill out this web form from my notes, but stop before submitting and show me exactly what will be sent.” |
| `cap-ea762950` | capability | browser-extension | 6 | “Watch this authenticated page and tell me when the status, price, or availability changes.” |
| `cap-fb442a50` | capability | mac-planner | 6 | “Every morning, check my calendar, unread email, and today’s files, then give me a short spoken brief with the meetings that need preparation and a pr |
| `cap-b4dfb9ea` | capability | mac-planner | 6 | “Clean up my Downloads every Friday: group files by project, rename obvious duplicates, and show me a review list before anything is deleted.” |
| `cap-c071fa0a` | capability | mac-planner | 6 | “Every morning, give me a concise briefing of today’s calendar, unread priority messages, weather, and the files I need for my first meeting; let me a |
| `cap-0fee609c` | capability | mac-planner | 6 | “Prepare me for my next meeting: find the agenda and related local documents, summarize the open decisions and prior action items, and put the three m |
| `cap-70db8ef3` | capability | mac-planner | 6 | “When I say ‘prepare my workday’, check my calendar and inbox, make a concise brief, and put it in a note on my Mac; don't send anything.” |
| `cap-026858ec` | capability | mac-planner | 6 | “Find the best flight options for next Thursday, compare total price and duration, and leave me a shortlist; do not book.” |
| `cap-0e0b8d35` | capability | mac-planner | 6 | “Clean up my Downloads: group files by type into folders and show me what will be moved before doing it.” |
| `cap-23af3e85` | capability | mac-planner | 6 | “Every weekday at 5 pm, summarize the notes I created today into three next actions and put them in my task app; never send messages.” |
| `cap-5dbbe6df` | capability | relay-realtime | 6 | “Summarize what I missed in my email today.” |
| `cap-0e994cfb` | capability | relay-realtime | 6 | “Read my upcoming schedule for the day.” |
| `cap-2d29628a` | capability | relay-realtime | 6 | “Save this idea for later.” |
| `cap-1634d96f` | capability | relay-realtime | 6 | “Plan my day. Pull my calendar, summarize critical tasks and travel time, and give me a 30-second briefing.” |
| `cap-f66f7f6e` | capability | relay-realtime | 6 | “Read my notifications and tell me only what’s important.” |
| `cap-b5796f52` | capability | relay-realtime | 6 | “Start a focus session for 25 minutes. Block distractions and let me know when time’s up.” |
| `cap-fb73a1d0` | capability | relay-realtime | 6 | “Remember this: my bike lock code is 4829.” |
| `cap-7e779dac` | capability | relay-realtime | 6 | "Summarize this webpage" or "Check the price on this product" |
| `cap-37804d89` | capability | relay-realtime | 6 | "Remind me to do X at 6 pm" or "Every weekday at 9, remind me to stand up" |
| `chg-71ae0f60` | mac-harness | mac-planner | 6 | Replace FULL_CONTROL_MODE's undifferentiated execution path with a typed action broker: structured read/open/search actions by default, and separate m |
| `chg-e0d96401` | mac-harness | mac-planner | 6 | Put a typed capability broker in front of the existing FULL_CONTROL computer loop. Accept structured argv/files/app/UI operations with per-capability  |
| `chg-5dced2e2` | memory | mac-planner | 6 | Replace hand-written per-surface fleetContext prompt sections with a shared, typed context service: store facts with source, confidence, sensitivity,  |
| `chg-a05b2515` | memory | mac-planner | 6 | Replace per-surface prompt hand-written fleetContext with a compact, typed context API: stable owner preferences and permissions, task-local facts, an |
| `chg-54408a62` | model-routing | browser-extension | 6 | Introduce a browser-specific low-cost pipeline: deterministic command planner for navigation/extraction, small model for selector repair and page summ |
| `chg-67e2a397` | model-routing | mac-planner | 6 | Introduce an asynchronous job router with cheap background models for extraction, summarization, monitoring, and retries; reserve realtime for short v |
| `chg-1bd50c67` | model-routing | relay-realtime | 6 | Introduce a clear tiering policy: relay-realtime handles only intent capture, brief clarification, and immediate safety checks; everything else become |
| `chg-7f6f0131` | model-routing | relay-realtime | 6 | Add explicit, cheap tiers: relay captures intent and hands off to mac_delegate or server_browser_actions. Introduce job creation, status, cancellation |
| `chg-b3826cae` | browser-harness | browser-extension | 5 | Add a typed browser-job protocol with origin allowlists, tab bootstrap via navigate, structured extract selectors, per-action risk labels, screenshot/ |
| `cap-bc260bea` | capability | browser-extension | 5 | Every weekday morning, check my logged-in work dashboard, calendar, and inbox, then give me a short audio briefing with only what needs my attention. |
| `cap-b15b17f9` | capability | browser-extension | 5 | Open this website, fill out the form with the information we discussed, and show me exactly what is ready before you submit it. |
| `cap-cb69fbe6` | capability | browser-extension | 5 | Watch this logged-in page and tell me when the status changes, but don't click anything or send anything. |
| `cap-2fc364ed` | capability | mac-planner | 5 | “Give me a workday brief at 8:30, and let me play it from the pendant when I’m ready.” |
| `cap-d91c8266` | capability | mac-planner | 5 | “Before my next meeting, prepare me: open the agenda, summarize relevant email, and put a private briefing on the pendant.” |
| `cap-52dcc328` | capability | mac-planner | 5 | “Every Friday, tidy my Downloads into dated folders, show me a preview, and only then apply it.” |
| `chg-6a6fa4b6` | mac-harness | mac-planner | 5 | Add a typed action policy in front of FULL_CONTROL_MODE: classify every action as read-only, reversible local mutation, or high-impact mutation; requi |
| `chg-9206eec2` | memory | browser-extension | 5 | Store browser task definitions as versioned, user-owned recipes (origin, allowed paths, selectors, extracted fields, cadence, privacy/retention, and c |
| `chg-e5bfe9ad` | model-routing | mac-planner | 5 | Route all non-conversational work through an asynchronous job planner: realtime handles intent capture and confirmation only; a cheaper background mod |

