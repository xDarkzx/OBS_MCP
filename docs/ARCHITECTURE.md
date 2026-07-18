# Architecture

## Overview

OBS-MCP is a thin, async Python layer over OBS Studio's built-in
[obs-websocket v5](https://github.com/obsproject/obs-websocket) protocol.
Unlike REAPER (which needed a custom file-based IPC bridge built from
scratch — see the sibling [Reaper-MCP](https://github.com/xDarkzx/Reaper-MCP)
project), OBS already ships a real-time WebSocket server with a fully
specified request/response protocol. There's no custom transport to build —
just a faithful, complete Python wrapper around it.

```
obs_mcp/
├── main.py             # FastMCP server entry point, registers all tools
├── obs_client.py       # Async wrapper over obsws-python's sync ReqClient
├── error_codes.py      # Typed error taxonomy (OBSMCPError)
├── tool_registry.py    # Auto-discovers tools/*.py modules, fail-loud on gaps
└── tools/
    ├── general_tools.py        # Version/stats, hotkeys, custom events
    ├── config_tools.py         # Scene collections, profiles, video settings
    ├── source_tools.py         # Active-state, screenshots
    ├── scene_tools.py          # Scenes, canvases, groups, program/preview
    ├── input_tools.py          # Inputs + full audio mixer + deinterlace
    ├── transition_tools.py     # Transitions, T-bar, triggering
    ├── filter_tools.py         # Source filter chain CRUD
    ├── scene_item_tools.py     # Transform, enabled/locked, z-order, blend
    ├── output_tools.py         # Virtual cam, replay buffer, generic outputs
    ├── stream_record_tools.py  # Start/stop/pause/split/chapters
    ├── media_tools.py          # Media source playback control
    ├── ui_tools.py             # Studio mode, dialogs, projectors
    └── pipeline_tools.py       # Composite tools — clean_audio_input, etc.
```

## Connection layer

`obs_client.py`'s `OBSClient` wraps [`obsws-python`](https://pypi.org/project/obsws-python/)'s
synchronous `ReqClient`. Every FastMCP tool is an `async def`, but the
underlying WebSocket client blocks — so every call runs in a thread-pool
executor (`loop.run_in_executor`) instead of on the event loop, the same
pattern Reaper-MCP uses for its blocking file I/O.

`OBSClient.execute(request_type, **data)` is a thin, generic dispatcher —
it calls `obsws-python`'s own generic escape hatch (`client.send(request_type,
data, raw=True)`) rather than relying on `obsws-python`'s convenience
methods, which don't cover 100% of the protocol. This is what makes full
147-request coverage possible without waiting on an upstream library update
for newer protocol additions (like Canvases, added in obs-websocket v5.7.0).

Connection is lazy — the first tool call triggers a connect. Every call
(connect included) is serialized through a single `asyncio.Lock`: `obsws-python`'s
request layer does a bare send-then-recv with no request-ID matching, so two
tool calls running concurrently could each read the other's response off the
socket. A real connection failure (no reply at all) resets state so the
*next* call reconnects instead of failing forever — but an ordinary
OBS-side error (bad scene name, out-of-range value) leaves the connection
alone, since the socket is still healthy and the AI will hit that case
routinely while exploring scene/source names.

## Tool registry

`tool_registry.py` follows the same auto-discovery pattern as Reaper-MCP:
`pkgutil.iter_modules()` finds every `tools/*.py` module, imports it, and
calls its `register(mcp)` function if it has one.

**`_EXPECTED_MODULES` is present from this project's first commit**, not
added after a bug was found. On a sibling project (Reaper-MCP), an overbroad
`.gitignore` rule silently excluded four tool modules from every published
copy of the repo for an extended period, with zero startup error — the
registry had nothing to compare "what's registered" against for the default
profile. This project's registry checks the registered set against a known-
good module list on every startup, for every profile, so that class of bug
fails loud instead of shipping quiet.

## Pipeline tools vs. raw requests

146 of the 147 tools are direct 1:1 wrappers over an obs-websocket request —
faithful, unopinionated, complete. `pipeline_tools.py` is the exception: it
composes several raw requests into the outcome a user actually wants.

`clean_audio_input` is the first of these — it builds a Noise Gate → Noise
Suppression → Compressor filter chain in the correct signal order, using
setting keys verified against OBS Studio's actual filter source
(`plugins/obs-filters/{noise-gate,noise-suppress,compressor}-filter.c`) —
not guessed from the UI labels, which don't match the underlying JSON keys.
It also queries `GetSourceFilterKindList` before creating the noise-
suppression stage, since which noise-suppress filter kind is registered
(`noise_suppress_filter` vs. the newer RNNoise-based
`noise_suppress_filter_v2`) depends on the platform and OBS build — assuming
one would silently fail on builds that only have the other.

It skips any stage whose filter *kind* already exists on the input instead
of duplicating it — but a pre-existing stage could be anywhere in the
chain, and a newly created one always lands at the end. After creating and
skipping, it does one more pass to anchor its three managed stages as an
adjacent, correctly-ordered group (at the earliest position any of them
occupies), so a mic that already had e.g. a Compressor from before doesn't
end up with the new Gate appended after it — which would invert the whole
point of gate-first ordering.

More pipelines belong here as they're built: anything that would otherwise
make the calling AI hand-assemble several raw requests and guess at
parameter names to get one real-world outcome.

## Protocol reference

Every tool's request name and field names are verified against the
[official obs-websocket v5 protocol spec](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md).
When adding a tool, check field names there — not from a blog post or the
OBS UI's display labels, which frequently differ from the underlying JSON
keys (e.g. the UI's "Suppression Level" slider is JSON key `suppress_level`
on the `speex` method only).
