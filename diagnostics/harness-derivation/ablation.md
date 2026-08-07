# Ablation

Model `gpt-realtime-2.1` · 40 tool-selection cases · 3 passes per variant (range in brackets).

| variant | score | delta |
| --- | --- | --- |
| whole harness | 29.3/35 (28-30) | — |
| **no prompt at all** | 29.0/35 (28-30) | -0.3 |
| without _current session pairing and owner state_ | 28.3/35 (26-30) | -1.0 |
| without _job scheduling and background workers_ | 29.0/35 (29-29) | -0.3 |
| without _Relay intent contract and supported intents/context fields_ | 30.0/35 (28-31) | +0.7 |
| without _owner_workflows_and_preferences_ | 28.7/35 (28-29) | -0.7 |
| without _available_tools_and_routing_contract_ | 28.3/35 (27-29) | -1.0 |

## Read this as

A fragment whose removal costs **0 or more** is not earning its place — the
model performs as well or better without it, and you are paying for those
tokens on every single call. Delete it and re-run.

If "no prompt at all" scores close to the whole harness, the harness itself
is mostly ceremony. That is the result to hope for, not to fear.

## Where the whole harness still fails

- "Turn my volume down a bit." → get_mac_status (wanted mac_run_actions)
- "What is the weather in Taipei?" → web_search(query="current weather in Taipei") — wrong argument
- "Look up when the next SpaceX launch is." → web_search(query="next SpaceX launch schedule") — wrong argument
- "Close all my tabs except this one." → mac_delegate (wanted browser_run_actions)
- "Read me the title of the page I have open." → browser_run_actions → gave up (wanted browser_run_actions)

These are the ONLY places a new instruction is justified — a repeated,
specific failure. Add one line, re-run, keep it only if the score moves.

