<!-- mcp-name: io.github.xDarkzx/obs-mcp -->
<h1 align="center">OBS-MCP</h1>

<p align="center">
  <strong>AI-powered stream and recording control for OBS Studio through the Model Context Protocol</strong>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-green.svg" alt="License" /></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple.svg" alt="MCP Compatible" /></a>
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/version-0.2.0-orange.svg" alt="v0.2.0" /></a>
  <a href="https://pypi.org/project/obs-mcp/"><img src="https://img.shields.io/pypi/v/obs-mcp.svg?color=blue" alt="PyPI" /></a>
  <a href="https://github.com/xDarkzx/OBS_MCP/actions/workflows/ci.yml"><img src="https://github.com/xDarkzx/OBS_MCP/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://obsproject.com/"><img src="https://img.shields.io/badge/OBS%20Studio-28%2B-red.svg" alt="OBS Studio 28+" /></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#new-here-what-this-actually-is">New Here?</a> &bull;
  <a href="#why-obs-mcp">Why OBS-MCP?</a> &bull;
  <a href="#features">Features</a> &bull;
  <a href="docs/TOOLS.md">Tools Reference</a> &bull;
  <a href="docs/ARCHITECTURE.md">Architecture</a> &bull;
  <a href="#troubleshooting">Troubleshooting</a>
</p>

---

OBS-MCP connects any MCP-compatible AI assistant to [OBS Studio](https://obsproject.com/), giving it full control over your stream and recordings. Say *"clean up my mic"* or *"switch to my starting soon scene"* and it just happens — no clicking through menus yourself.

**148 tools** cover the entire [obs-websocket v5](https://github.com/obsproject/obs-websocket) protocol — scenes, sources, the full audio mixer, filters, transitions, streaming, recording, virtual camera, replay buffer, studio mode, and output stats. On top of raw control, **pipeline tools** do the actual job in one call instead of making the AI hand-assemble a filter chain: `clean_audio_input` builds a verified Noise Gate → Noise Suppression → Compressor chain instead of guessing at OBS's internal filter parameter names, and `diagnose_av_health` tells you *why* your frames are dropping instead of handing back raw numbers.

**No cloud. Nothing leaves your machine.** OBS-MCP is a local WebSocket client that talks directly to OBS Studio's built-in `obs-websocket` server — your stream, recordings, and scene setup stay on your computer. Bring whatever AI client you already use (Claude Desktop, Claude Code, Cursor, any MCP client) — OBS-MCP handles OBS.

**If this is useful to you, a star helps other people find it** — that's the whole marketing budget for this project.

### Works With

OBS-MCP works with any AI client that supports the [Model Context Protocol](https://modelcontextprotocol.io):

- [Claude Desktop](https://claude.ai/download) — Anthropic's desktop app
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — CLI agent
- [Cursor](https://www.cursor.com/) — AI code editor with MCP support
- Any other [MCP-compatible client](https://modelcontextprotocol.io/clients)

---

## Why OBS-MCP?

- **Pipeline tools, not just raw API access.** Most OBS automation stops at "call obs-websocket." OBS-MCP goes further — `clean_audio_input`, `diagnose_av_health`, and other pipelines encode the actual expertise (the right filter chain order, what a dropped-frame stat actually means) so the AI gets it right instead of guessing at parameter names.
- **100% local.** No cloud calls, no API keys, nothing leaves your machine — OBS-MCP talks to OBS Studio's own built-in WebSocket server on disk-and-loopback only.
- **Full protocol coverage.** All of obs-websocket v5 is exposed — scenes, audio mixer, filters, transitions, streaming, recording, virtual camera, replay buffer, studio mode — not a curated subset.
- **Composable with companion tools.** Pairs with [Reaper-MCP](https://github.com/xDarkzx/Reaper-MCP) and [Audacity-MCP](https://github.com/xDarkzx/Audacity-MCP) if your stream setup also touches music production or audio cleanup — same AI conversation, different tool for each job.

---

## New here? What this actually is

If you've never used Claude Desktop or heard of "MCP" before, here's the whole idea in plain terms:

- **Claude Desktop** is Anthropic's free AI chat app (like ChatGPT, but made by Anthropic) — you download it, sign in, and type messages to it like a chatbot.
- **MCP (Model Context Protocol)** is a plug-in system that lets that chat app actually *do things* on your computer, not just talk. Without MCP, Claude can only give you instructions ("go to Tools menu, click..."). With MCP, Claude can just do it directly.
- **OBS-MCP is the plug-in for OBS Studio specifically.** Once it's installed, you can type things like *"clean up my mic"* or *"switch to my starting soon scene"* into Claude, and it actually happens in OBS — no clicking through menus yourself.

You don't need to know any code to use this. The installer below handles everything except two things only you can do: telling OBS to allow the connection, and telling your AI app to use this plug-in. Both are explained step by step.

---

## Quick Start

### 1. Get OBS-MCP

**Option A:** Click the green **Code** button above → **Download ZIP** → extract it to a folder somewhere easy to find (like your Desktop) — works with nothing pre-installed, easiest on a brand new machine.

**Option B:** Clone with git (lets you `git pull` for updates later):

A fresh Windows install doesn't ship with git — check first:
```powershell
git --version
```
If that says "not recognized", install it, then close and reopen your terminal:
```powershell
winget install --id Git.Git -e --source winget
```
(`winget` itself ships with Windows 11 and up-to-date Windows 10. If `winget` isn't found either, grab the installer directly from [git-scm.com](https://git-scm.com/download/win).)

macOS/Linux almost always have git already — `git --version` to check, or `brew install git` / `sudo apt install git` if not.

```bash
git clone https://github.com/xDarkzx/OBS_MCP.git
```

### 2. Run the installer (installs OBS-MCP *and* sets up your AI client, automatically)

**Windows:** either double-click `install.bat` in File Explorer, or — if you're already in a terminal from the `git clone` step above — just keep going in the same PowerShell/Command Prompt window (copy-paste both lines):
```powershell
cd OBS_MCP
.\install.bat
```

**macOS / Linux:**
```bash
cd OBS_MCP
bash install.sh
```

The installer checks you have Python (offers to install it if not), installs the `obs-mcp` command, and — if you say yes when it asks — automatically writes the config for Claude Desktop and/or LM Studio. No manual JSON editing required. Once it finishes, skip straight to [step 3](#3-enable-the-websocket-server-in-obs).

<details>
<summary>I don't use Claude Desktop or LM Studio, or want to install manually</summary>

**Don't even want to clone the repo?** OBS-MCP is on PyPI:

```bash
pip install obs-mcp
```

(or `pip install -e .` from inside the folder if you already have the repo cloned/extracted). Either way, this puts an `obs-mcp` command on your PATH — find where it landed with `where obs-mcp` (Windows) or `which obs-mcp` (macOS/Linux) if you ever need the exact file path. Add this to your client's MCP config:

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

**Or for zero footprint** (same idea as `npx` in Node.js — nothing stays installed, `uvx` runs it fresh each time from its own cache): since there's no permanent `obs-mcp` binary in this case, point the config at `uvx` itself instead:

```json
{
  "mcpServers": {
    "obs": {
      "command": "uvx",
      "args": ["obs-mcp"],
      "env": {
        "OBS_HOST": "localhost",
        "OBS_PORT": "4455",
        "OBS_PASSWORD": "your_password_here"
      }
    }
  }
}
```

**If you'd rather not install anything at all**, point your client straight at the source file instead of a command — `obs_mcp/main.py` inside the folder you cloned/extracted is the actual MCP server entry point:

```json
{
  "mcpServers": {
    "obs": {
      "command": "python",
      "args": ["-m", "obs_mcp.main"],
      "cwd": "/absolute/path/to/the/OBS_MCP/folder/you/extracted",
      "env": {
        "OBS_HOST": "localhost",
        "OBS_PORT": "4455",
        "OBS_PASSWORD": "your_password_here"
      }
    }
  }
}
```

Either way: leave `OBS_PASSWORD` empty (`""`) if you didn't set one in OBS. If your password has a `"` or `\` in it, escape it for JSON (`\"` / `\\`) — everything else can go in as-is. Check your client's own MCP documentation for where its config file lives. Full detail, including exact config-file paths per OS: [Installation Guide](docs/INSTALLATION.md).

</details>

### 3. Enable the WebSocket server in OBS

This is the one thing the installer genuinely can't do for you — OBS itself has to allow the connection.

OBS Studio ships this built in since v28 — there's nothing to download or install for this part.

1. Open OBS Studio.
2. **Tools → WebSocket Server Settings**.
3. Check **Enable WebSocket server**.
4. Note the **Server Port** (default `4455`, you usually don't need to change this).

**No password set yet?** Leave it blank — that's fine for a normal single-PC setup.

**Already have a password** (from a Stream Deck integration, chatbot, or earlier setup)? Don't retype it from memory — click **Show Connect Info** in that same settings window, which reveals the exact password OBS has stored.

Full walkthrough with screenshots-worth of detail if you get stuck: [Installation Guide](docs/INSTALLATION.md).

### 4. Talk to your AI

Restart Claude Desktop if it was already open, then just talk to it normally — for example:

```
"What OBS scenes do I have?"
"Clean up my mic audio"
"Why are my frames dropping?"
"Switch to my Starting Soon scene"
```

If OBS is running with the WebSocket server enabled, it just works — no special syntax, ask like you'd ask a person.

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
