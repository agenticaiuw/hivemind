# Cloud-relay domain-memory agent — COMPLETE

Rewired the CLOUD RELAY around capability-domain memory (owner's 2026-08-12 design: no generic prompt memories; tools combined with memories; explicit memory_lookup/memory_save; clarify only on real ambiguity).

Changed:
- cloud-relay/fleetContext.js (+test): all generic memory splicing removed from the voice prompt; fleet.domainMemory normalized as data; buildFleetPayloadFromLocal now takes {machine, browser, permissions, speaker, domainMemory}.
- cloud-relay/server.js: PUT /v1/state/fleet merges the domainMemory hive block (two-writer safety); new GET/POST /v1/memory/domains; HTTP voice session wired with domainMemory.
- cloud-relay/relayScopes.js (+test): memory:domains:read / memory:domains:write rules.
- cloud-relay/deviceAuth.js (+test coverage via relayScopes): scopes granted to mobile, mac_bridge, browser_node; NOT nrf_pendant.
- cloud-relay/openaiRealtimeVoice.js (+test): memory_lookup/memory_save tools from shared MEMORY_TOOL_SPECS; fetch-on-tool-selection attach (domainMemory lines in tool results for get_mac_status / mac_run_actions / browser_run_actions); clarification gate refuses dispatch and speaks the question; openSocket test seam + fake-socket harness.
- cloud-relay/pendantConverse.js: spokenMemory capture deleted; domainMemory relay wired.
- NEW cloud-relay/domainMemoryRelay.js (+test): readDomainMemory / saveDomainMemory / createDomainMemoryRelay.
- Stores: memory-event log removed from memoryStore.js and d1Store.js (schema tables left alone).
- DELETED: shared/fleetMemory.js(+test), shared/spokenMemory.js(+test). Stale comment refs fixed in shared/capabilityRegistry.js(+test) (comment-only).

Tests: fleetContext 9, openaiRealtimeVoice 36, relayScopes+deviceAuth 34, domainMemoryRelay 8; full cloud-relay 457/457, shared 168/168, store 33/33. Residue grep clean except sanctioned schema.sql/fleet-memory-migration.sql comments.

Not committed, not deployed (per task).

## Independent verification (continuation agent, read-only) — PASS

Context: spawned as a continuation on the belief the worker was killed; the worker (relay-voice) was alive, so this agent stood down from edits, deconflicted via messages, and verified instead. Zero edits made to any source file by the verifier.

- Full suite: `node --test cloud-relay/*.test.js cloud-relay/store/*.test.js shared/*.test.js shared/domains/*.test.js` → 658/658 pass, 0 fail, run twice (bare `node --test cloud-relay/ shared/` is a Node 22 harness artifact — it fails on directory args; use the glob form).
- Residue grep (`fleetMemory|listMemoryEvents|appendMemoryEvents|spokenMemory` over cloud-relay, shared, cloudflare-worker): zero JS hits; only the sanctioned schema.sql/fleet-memory-migration.sql comments remain (spec: leave schema files alone).
- Spec line-items read and confirmed in source: prompt carries no memory section (fleetContext.js); PUT /v1/state/fleet merges the hive block via mergeDomainMemory with the merged block in the response for the Mac's write-back; GET/POST /v1/memory/domains behind memory:domains:read/write (relayScopes.js) granted to mobile/mac_bridge/browser_node with WHY comments, nrf_pendant excluded with rationale (deviceAuth.js); voice loop derives memory_lookup/memory_save from shared MEMORY_TOOL_SPECS, answers them in-turn null-safely, fetches domains via domainsForActions before dispatch (browser fallback for browser_run_actions), attaches rendered lines as `domainMemory` in function_call_output (8/domain cap), and the clarification gate refuses dispatch (state.actions stays empty) sending {ok:false, needs_clarification, question, options} + spoken question; pendantConverse.js drops createSpokenMemoryWriter and the onTurn capture, wires `domainMemory: createDomainMemoryRelay({store})`; both stores dropped the memory-event methods.
- Coordinator's added check — extension contract drift: `toolCatalogueDrift()` executed → {undescribed:[], unknown:[]}; brain.js and the relay both derive memory tool schemas from the one shared MEMORY_TOOL_SPECS; memoryLookupRequest/memorySaveRequest (brain.js) match the relay routes exactly (GET /v1/memory/domains?domain&query&limit; POST {node, facts:[{domain,name,value,scope:'hive'}]}); local-agent/bridge.js already calls the new buildFleetPayloadFromLocal signature with `domainMemory:{facts}` and mirrors the merged write-back.
- Non-memory work observed riding the same files from parallel workstreams (NOT part of this spec, not judged here): pendant hardware-control frames (approval_decision blue button, rotary menu) in pendantConverse.js + decideNextPendingApproval in approvalDelivery.js(+test).
- Minor follow-up candidates (comment-only, no action taken): local-agent/contextGraphRetention.js:17 and cloudflare-worker/schema.sql:249 / fleet-memory-migration.sql:1 still name the deleted shared/fleetMemory.js in comments.
