<h1 align="center">OBS-MCP</h1>

<p align="center">
  <strong>AI-powered stream and recording control for OBS Studio through the Model Context Protocol</strong>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-green.svg" alt="License" /></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple.svg" alt="MCP Compatible" /></a>
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/version-0.1.0-orange.svg" alt="v0.1.0" /></a>
  <a href="#development"><img src="https://img.shields.io/badge/tests-pytest-0A9EDC.svg" alt="pytest" /></a>
  <a href="https://obsproject.com/"><img src="https://img.shields.io/badge/OBS%20Studio-28%2B-red.svg" alt="OBS Studio 28+" /></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#features">Features</a> &bull;
  <a href="docs/TOOLS.md">Tools Reference</a> &bull;
  <a href="docs/ARCHITECTURE.md">Architecture</a> &bull;
  <a href="#troubleshooting">Troubleshooting</a>
</p>

---

OBS-MCP connects any MCP-compatible AI assistant to [OBS Studio](https://obsproject.com/), giving it full control over your stream and recordings through **147 tools** covering the entire [obs-websocket v5](https://github.com/obsproject/obs-websocket) protocol — scenes, sources, scene items, inputs and the full audio mixer, filters, transitions, streaming, recording, virtual camera, replay buffer, media playback, studio mode, and objective output stats. On top of raw control, it ships **pipeline tools** that do the actual job in one call instead of making the AI hand-assemble a filter chain — `clean_audio_input` builds a verified Noise Gate → Noise Suppression → Compressor chain instead of guessing at OBS's internal filter parameter names.

**OBS-MCP itself runs entirely on your machine.** It's a local WebSocket client that talks directly to OBS Studio's built-in `obs-websocket` server — your stream, recordings, and scene setup never leave your computer. The AI "brain" lives wherever you already run it: Claude Desktop / Claude Code / Cursor / any MCP client. You bring the AI, OBS-MCP handles OBS.

### Works With

OBS-MCP works with any AI client that supports the [Model Context Protocol](https://modelcontextprotocol.io):

- [Claude Desktop](https://claude.ai/download) — Anthropic's desktop app
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — CLI agent
- [Cursor](https://www.cursor.com/) — AI code editor with MCP support
- Any other [MCP-compatible client](https://modelcontextprotocol.io/clients)

---

## Quick Start

### 1. Get OBS-MCP

**Option A:** Click the green **Code** button above → **Download ZIP** → extract to a folder

**Option B:** Clone with git:
```bash
git clone https://github.com/xDarkzx/OBS_MCP.git
```

### 2. Install

```bash
cd OBS_MCP
pip install -e .
```

This gives you the `obs-mcp` command.

### 3. Enable the WebSocket server in OBS

OBS Studio ships `obs-websocket` built in since v28 — nothing to install.

1. Open OBS Studio.
2. **Tools → WebSocket Server Settings**.
3. Check **Enable WebSocket server**.
4. Note the **Server Port** (default `4455`).

**No password set yet?** Leave it blank and skip to step 4 — `OBS_PASSWORD` stays empty.

**Already have a password** (from a Stream Deck integration, chatbot, or earlier setup)? Don't retype it from memory — click **Show Connect Info** in that same settings window, which reveals the exact password OBS has stored. Copy it from there.

### 4. Add OBS-MCP to your AI client

```json
{
  "mcpServers": {
    "obs": {
      "command": "obs-mcp",
      "env": {
        "OBS_HOST": "localhost",
        "OBS_PORT": "4455",
        "OBS_PASSWORD": "your_password_here"
      }
    }
  }
}
```

Leave `OBS_PASSWORD` empty (`""`) if you didn't set one in OBS. If your password contains a `"` or `\`, escape it for JSON (`\"` / `\\`) — everything else can go in as-is. Check your client's MCP documentation for the config file location. Full walkthrough with more detail: [Installation Guide](docs/INSTALLATION.md).

### 5. Talk to your AI

With OBS running and the WebSocket server enabled, ask your AI assistant to switch scenes, start streaming, clean up your mic audio, or check your dropped-frame stats — it now has real tools to do it.

---

## Features

| Category | Tools | What it does |
|----------|:-----:|---------------|
| **General** | 9 | Version/stats, hotkeys, custom events, vendor requests, persistent data storage |
| **Config** | 15 | Scene collections, profiles, video/canvas settings, stream service destination, record directory |
| **Sources** | 3 | Active-state check and screenshots — works for both inputs and scenes |
| **Scenes** | 12 | List/create/remove/rename scenes, program/preview control, per-scene transition overrides, canvases, groups |
| **Inputs & Audio** | 28 | Create/configure inputs; full mixer — mute, volume, balance, sync offset, monitor type, audio track routing, deinterlace mode |
| **Transitions** | 9 | List/set transitions, duration, settings, T-bar scrubbing, trigger transitions (including studio mode) |
| **Filters** | 10 | Full CRUD on source filter chains — audio and video effects, any order |
| **Scene Items** | 17 | Transform (position/scale/crop), enabled/locked state, z-order, blend mode |
| **Outputs** | 17 | Virtual camera, replay buffer, and any generic named output |
| **Stream & Record** | 14 | Start/stop/toggle, captions, pause/resume, file splitting, chapter markers |
| **Media** | 4 | Playback control for media sources — status, seek, play/pause/stop/restart/next/previous |
| **UI** | 8 | Studio mode, property/filter/interact dialogs, monitor list, projectors |
| **Pipelines** | 2 | `clean_audio_input` — one-call Noise Gate → Suppression → Compressor chain with verified OBS filter parameters. `diagnose_av_health` — one-call frame-drop/congestion/disk-space diagnosis instead of raw stats |

**148 tools total** — full coverage of the obs-websocket v5 protocol (the one intentional omission, `Sleep`, only functions inside request batches, which this version doesn't implement yet) plus the two composite pipeline tools above.

### `clean_audio_input` — the pipeline tool

Every other tool here is a thin, faithful wrapper over one obs-websocket request. This one isn't — it's the actual thing a streamer wants ("make my mic sound clean") instead of the mechanism ("create three filters with the right internal parameter names in the right order"):

```
clean_audio_input(input_name="Mic/Aux")
```

Builds a Noise Gate → Noise Suppression (RNNoise) → Compressor chain in the correct signal order, using parameter keys verified against OBS Studio's actual filter source (`plugins/obs-filters/*.c`) — not guessed from the UI. Skips any stage that's already present instead of duplicating it.

### `diagnose_av_health` — "why is my stream dropping frames?"

```
diagnose_av_health()
```

Pulls `GetStats` + `GetStreamStatus` + `GetRecordStatus` in one call and interprets them instead of handing back raw numbers: render-thread skip rate points at a GPU/scene bottleneck, output-thread skips with low network congestion point at the encoder, high congestion points at your upload/bitrate, and low disk space gets flagged before it silently kills a recording. Ask your AI "why are my frames dropping" or "is my stream healthy" and it has real numbers to reason from instead of guessing.

---

## Requirements

- **OBS Studio 28+** (obs-websocket v5 ships built in from v28 onward)
- **Python 3.10+**
- An MCP-compatible AI client

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Could not connect to OBS" | Make sure OBS Studio is running and Tools → WebSocket Server Settings → Enable WebSocket server is checked. |
| "Authentication failed" | Your `OBS_PASSWORD` env var doesn't match the password set in OBS's WebSocket Server Settings — or you set a password in OBS but left the env var empty. Don't retype the password from memory: Tools → WebSocket Server Settings → **Show Connect Info** shows the exact value OBS has stored. |
| Tool calls hang | Check OBS itself isn't showing a blocking dialog (e.g. a "scene collection changed" prompt) — some requests block until the user dismisses OBS-side UI. |
| Scene/input "not found" errors | Names are case-sensitive and must match exactly what's shown in OBS. Call `get_scene_list` / `get_input_list` first. |

---

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -x -q
```

### Adding New Tools

1. Create a module in `obs_mcp/tools/` (or add to an existing one).
2. Export a `register(mcp: FastMCP)` function.
3. Define your tools with `@mcp.tool()` decorators, calling `client.execute("RequestType", **params)`.
4. Add the module name to `_EXPECTED_MODULES` in `tool_registry.py`.
5. That's it — the tool registry auto-discovers it on startup.

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## Support

Found a bug or want a feature? [Open an issue](https://github.com/xDarkzx/OBS_MCP/issues).

If OBS-MCP has helped your stream, consider buying me a coffee:

<p align="center">
  <a href="https://buymeacoffee.com/xdarkzx">
    <img src="https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee" />
  </a>
</p>

Your support helps keep this project maintained and free for everyone.

---

## Documentation

- **[Installation Guide](docs/INSTALLATION.md)** — Detailed setup for Windows, macOS, Linux and every supported MCP client
- **[Tools Reference](docs/TOOLS.md)** — Every tool grouped by domain, with a one-line description and signature
- **[Architecture](docs/ARCHITECTURE.md)** — Connection layer, tool registry, pipeline tools, protocol reference
- **[Contributing](CONTRIBUTING.md)** — How to add tools and contribute
- **[Changelog](CHANGELOG.md)** — Version history and release notes

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.

Built by [Daniel Hodgetts](https://github.com/xDarkzx) &bull; [𝕏 @daehonz1](https://x.com/daehonz1)
